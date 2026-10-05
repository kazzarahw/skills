#!/usr/bin/env python3
"""Append-only claim ledger: what was asserted, what backs it, and what it is worth.

A claim is graded the moment it is written, not at the end when the conclusion is already
formed. Two rules make the ledger worth keeping:

  * **Append-only.** A claim is never edited and never deleted. `grade` and `verdict` append a
    new line carrying `{"merge": true, ...}`; folding happens on read. That means the reasoning
    that led to a verdict survives even after the verdict is overturned, which is the only way to
    audit how confident the investigation was at each step.
  * **Refuse the impossible combinations.** `confirmed` on a D-grade source is a contradiction
    the machine can catch, so the machine catches it.

Standard library only, Python 3.9+. No network calls.

Usage:
    claimlog.py add     --case DIR --claim "TEXT" --source S --evidence raw/x.json
                        [--reliability A] [--credibility 3] [--probability likely]
    claimlog.py grade   --case DIR --id C0001 --reliability B --credibility 2
    claimlog.py verdict --case DIR --id C0001 --verdict probable --note "why"
    claimlog.py show    --case DIR --id C0001 [--json]
    claimlog.py list    --case DIR [--status probable] [--limit N] [--offset N] [--json]
    claimlog.py stats   --case DIR [--json]

Exit codes:
    0  success
    1  usage error
    2  gate refused - empty claim, impossible grade/verdict combination, or unknown id
    3  environment error - missing or unreadable path
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK, EXIT_USAGE, EXIT_GATE, EXIT_ENV = 0, 1, 2, 3

VERDICTS = ("confirmed", "probable", "unverified", "refuted", "inconclusive")
RELIABILITY = ("A", "B", "C", "D", "E")
CREDIBILITY = ("1", "2", "3", "4", "5", "6")
PROBABILITY = ("almost certainly", "highly likely", "likely", "roughly even chance",
               "unlikely", "highly unlikely", "remote")

# A verdict asserts the claim is true, so each has a minimum source grade. A stronger verdict on a
# weaker source is refused rather than accepted: it is always an error, never a judgement call.
FLOOR_RELIABILITY = {"confirmed": "B", "probable": "C", "unverified": "E", "refuted": "E",
                     "inconclusive": "E"}
ASSERTING = ("confirmed", "probable")


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on a bad flag, which would collide with "a gate refused".

    Keeping usage errors at 1 is what makes exit 2 mean exactly one thing: the script looked at
    your data and declined. An agent that cannot tell a mistyped flag from a detected credential
    will eventually report one as the other.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(EXIT_USAGE)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def die(msg: str, code: int):
    print(f"claimlog.py: {msg}", file=sys.stderr)
    raise SystemExit(code)


def read_lines(case: Path) -> list:
    path = case / "claims.jsonl"
    if not path.exists():
        return []
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((n, json.loads(line)))
        except json.JSONDecodeError as e:
            die(f"{path}:{n}: {e}. The ledger is append-only; repair the file by hand or start a "
                f"new ledger.", EXIT_ENV)
    return rows


def append(path: Path, record: dict) -> None:
    """Append one line. Nothing in this script ever truncates or rewrites the ledger."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def append_log(case: Path, verb: str, cid: str, clause: str) -> None:
    log = case / ".notes-log.md"
    if not log.exists():
        log.write_text("# Activity log\n\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"## [{utc_now()}] {verb} | {cid or '-'} | {clause}\n")


def fold(rows: list) -> dict:
    """Collapse append-only lines into the current view. Later explicit fields win; none are lost."""
    folded = {}
    for lineno, rec in rows:
        cid = rec.get("id")
        if not cid:
            continue
        cur = folded.setdefault(cid, {"id": cid, "revisions": [], "first_seen": rec.get("ts", "")})
        for k, v in rec.items():
            if k in ("merge", "id", "ts") or v is None:
                continue
            cur[k] = v
        cur.setdefault("ts", rec.get("ts", ""))
        cur["updated"] = rec.get("ts", cur.get("updated", ""))
        cur["revisions"].append({"line": lineno, "ts": rec.get("ts", ""),
                                 "op": "merge" if rec.get("merge") else "add",
                                 "changed": {k: v for k, v in rec.items()
                                             if k not in ("merge", "id", "ts") and v is not None}})
    return folded


def next_id(rows: list) -> str:
    used = {r.get("id") for _, r in rows if r.get("id")}
    n = 1
    while f"C{n:04d}" in used:
        n += 1
    return f"C{n:04d}"


def check_grade(reliability, credibility, verdict) -> str:
    """Return a message when the combination asserts more than the source can carry."""
    if not verdict:
        return ""
    if reliability in RELIABILITY and verdict in ASSERTING:
        floor = FLOOR_RELIABILITY[verdict]
        if reliability > floor:
            return (f"verdict {verdict!r} needs source grade {floor} or better, but the claim is "
                    f"graded {reliability}. A {reliability}-grade source cannot carry a "
                    f"{verdict!r} verdict.")
    if verdict == "confirmed" and str(credibility) in ("5", "6"):
        return (f"verdict 'confirmed' with credibility {credibility} contradicts itself: "
                f"credibility 5-6 means other sources have not confirmed the information.")
    if verdict == "confirmed" and not credibility:
        return ("verdict 'confirmed' needs an explicit --credibility. Credibility 1 means other "
                "sources confirm it; without the number the claim is asserting and measuring at "
                "the same time.")
    return ""


def known_evidence(case: Path) -> set:
    mf = case / "manifest.jsonl"
    out = set()
    if mf.exists():
        for line in mf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.add(json.loads(line).get("path", ""))
            except json.JSONDecodeError:
                continue
    return out


def cmd_add(a: argparse.Namespace) -> int:
    case = Path(a.case).expanduser()
    text = (a.claim or "").strip()
    if not text:
        die("--claim is required and must not be blank. An empty claim is not a claim.", EXIT_GATE)
    verdict = a.verdict or "unverified"

    bad = check_grade(a.reliability, a.credibility, verdict)
    if bad:
        die(bad, EXIT_GATE)
    if a.negative and not a.source:
        die("--negative needs --source naming what was searched and where. An absence with no "
            "stated coverage is indistinguishable from an unfinished search.", EXIT_GATE)
    if not a.source:
        print("claimlog.py: note: no --source given; this claim will stay unverified until one is.",
              file=sys.stderr)

    rows = read_lines(case)
    cid = next_id(rows)
    have = known_evidence(case)
    ev = []
    for e in (a.evidence or []):
        e = e.strip()
        if e and have and e not in have:
            print(f"claimlog.py: note: {e} is not in the manifest; capture it with evidence.py "
                  f"before citing it in a report.", file=sys.stderr)
        if e:
            ev.append(e)

    rec = {"id": cid, "claim": text, "verdict": verdict, "ts": utc_now(),
           "sources": [s for s in (a.source or []) if s], "evidence": ev}
    if a.reliability:
        rec["reliability"] = a.reliability
    if a.credibility:
        rec["credibility"] = a.credibility
    if a.probability:
        rec["probability"] = a.probability
    if a.theme:
        rec["theme"] = a.theme
    for flag in ("negative", "rejected", "gap"):
        if getattr(a, flag, False):
            rec[flag] = True
    if a.note:
        rec["note"] = a.note

    if a.dry_run:
        print(json.dumps({"status": "dry-run", **rec}, ensure_ascii=False))
        return EXIT_OK

    append(case / "claims.jsonl", rec)
    append_log(case, "create", cid, f"claim recorded ({verdict}); {len(rec['sources'])} source(s)")
    print(json.dumps({"status": "recorded", **rec}, ensure_ascii=False))
    return EXIT_OK


def merge_line(case: Path, a: argparse.Namespace, what: dict) -> dict:
    cid = a.id
    if cid not in fold(read_lines(case)):
        die(f"{cid} is not in this ledger. Ids are never reused or renumbered, so a gap in the "
            f"sequence is normal and is itself information.", EXIT_GATE)
    rec = {"id": cid, "merge": True, "ts": utc_now(), **what}
    if a.dry_run:
        return {"status": "dry-run", **rec}
    append(case / "claims.jsonl", rec)
    append_log(case, "update", cid, ", ".join(f"{k}={v}" for k, v in what.items()))
    return {"status": "updated", **rec}


def cmd_grade(a: argparse.Namespace) -> int:
    what = {}
    if a.reliability:
        what["reliability"] = a.reliability
    if a.credibility:
        what["credibility"] = a.credibility
    if a.probability:
        what["probability"] = a.probability
    if not what:
        die("grade needs at least one of --reliability, --credibility, --probability. "
            "Accepted reliability: " + ", ".join(RELIABILITY), EXIT_USAGE)
    out = merge_line(Path(a.case).expanduser(), a, what)
    print(json.dumps(out, ensure_ascii=False))
    return EXIT_OK


def cmd_verdict(a: argparse.Namespace) -> int:
    case = Path(a.case).expanduser()
    cur = fold(read_lines(case)).get(a.id)
    if cur is None:
        die(f"{a.id} is not in this ledger.", EXIT_GATE)
    what = {"verdict": a.verdict}
    if a.note:
        what["note"] = a.note
    bad = check_grade(cur.get("reliability"), cur.get("credibility"), a.verdict)
    if bad:
        die(bad, EXIT_GATE)
    if a.verdict == "confirmed" and not a.note:
        print("claimlog.py: note: a 'confirmed' verdict with no --note records that you checked "
              "for the null hypothesis. Be sure you did.", file=sys.stderr)
    out = merge_line(case, a, what)
    print(json.dumps(out, ensure_ascii=False))
    return EXIT_OK


def cmd_show(a: argparse.Namespace) -> int:
    rec = fold(read_lines(Path(a.case).expanduser())).get(a.id)
    if rec is None:
        die(f"{a.id} is not in this ledger.", EXIT_GATE)
    if a.json:
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        return EXIT_OK
    print(f"{rec['id']}  {rec.get('verdict', 'unverified')}  "
          f"{rec.get('probability') or '—'}")
    print(f"  claim      : {rec.get('claim', '')}")
    print(f"  grade      : reliability {rec.get('reliability', '—')} / "
          f"credibility {rec.get('credibility', '—')}")
    print(f"  sources    : {', '.join(rec.get('sources') or []) or 'NONE — ungraded'}")
    print(f"  evidence   : {', '.join(rec.get('evidence') or []) or 'NONE'}")
    if rec.get("note"):
        print(f"  note       : {rec['note']}")
    marks=[m for m in ("negative","rejected","gap") if rec.get(m)]
    if marks:
        print(f"  flags      : {', '.join(marks)}")
    print(f"  first_seen : {rec.get('first_seen', '')}   updated: {rec.get('updated', '')}")
    print(f"  revisions  : {len(rec.get('revisions', []))} (append-only; nothing was overwritten)")
    return EXIT_OK


def cmd_list(a: argparse.Namespace) -> int:
    folded = fold(read_lines(Path(a.case).expanduser()))
    items = [folded[k] for k in sorted(folded)]
    if a.status:
        items = [r for r in items if r.get("verdict") == a.status]
    total = len(items)
    window = items[a.offset:a.offset + a.limit]
    if a.json:
        print(json.dumps({"total": total, "offset": a.offset, "limit": a.limit,
                          "claims": [{k: v for k, v in r.items() if k != "revisions"}
                                     for r in window]}, indent=2, ensure_ascii=False))
        return EXIT_OK
    print(f"{total} claim(s); showing {len(window)} from offset {a.offset}\n")
    for r in window:
        grade = f"{r.get('reliability', '—')}/{r.get('credibility', '—')}"
        print(f"{r['id']}  {r.get('verdict', 'unverified'):<13} {grade:<5} "
              f"{(r.get('probability') or '—'):<21} {r.get('claim', '')[:58]}")
    return EXIT_OK


def cmd_stats(a: argparse.Namespace) -> int:
    folded = fold(read_lines(Path(a.case).expanduser()))
    by_verdict = {v: 0 for v in VERDICTS}
    by_prob = {}
    weak = unsourced = 0
    for r in folded.values():
        v = r.get("verdict", "unverified")
        by_verdict[v] = by_verdict.get(v, 0) + 1
        if r.get("probability"):
            by_prob[r["probability"]] = by_prob.get(r["probability"], 0) + 1
        if not r.get("sources"):
            unsourced += 1
        if r.get("reliability") in ("C", "D", "E") and v in ASSERTING:
            weak += 1
    out = {"total": len(folded), "by_verdict": by_verdict, "by_probability": by_prob,
           "unsourced": unsourced, "overstated_vs_grade": weak}
    if a.json:
        print(json.dumps(out, indent=2))
        return EXIT_OK
    print(f"{out['total']} claim(s) in the ledger\n")
    for v in VERDICTS:
        if by_verdict.get(v):
            print(f"  {v:<14} {by_verdict[v]}")
    if by_prob:
        print("\n  probability stated:")
        for p in PROBABILITY:
            if by_prob.get(p):
                print(f"    {p:<22} {by_prob[p]}")
    print(f"\n  claims with no source at all : {unsourced}")
    print(f"  verdicts stronger than grade  : {weak}")
    if weak:
        print("    ^ recorded with a weak source and an asserting verdict; check before shipping.")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(
        prog="claimlog.py",
        description="Append-only claim ledger. Grades and verdicts are recorded when the claim is "
                    "made and never edited afterwards.",
        epilog="Exit codes: 0 success | 1 usage error | 2 gate refused (empty claim, impossible "
               "grade/verdict combination, unknown id) | 3 environment error.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True, parser_class=_Parser)

    def common(sp):
        sp.add_argument("--case", default="case", help="case directory (default: case)")
        sp.add_argument("--dry-run", action="store_true", help="report what would be written")
        return sp

    c = common(sub.add_parser("add", help="record a new claim"))
    c.add_argument("--claim", required=True, help="the assertion, in one sentence")
    c.add_argument("--source", action="append", help="citation; repeatable")
    c.add_argument("--evidence", action="append",
                   help="manifest path backing it, e.g. raw/dns.json; repeatable")
    c.add_argument("--reliability", choices=RELIABILITY, help="source grade A (best) to E")
    c.add_argument("--credibility", choices=CREDIBILITY, help="information credibility 1-6")
    c.add_argument("--probability", choices=PROBABILITY, help="estimated likelihood of the claim")
    c.add_argument("--verdict", choices=VERDICTS, default="unverified", help="default unverified")
    c.add_argument("--note", help="reasoning, required in spirit for any inference")
    c.add_argument("--negative", action="store_true",
                   help="this claim records an ABSENCE: what was searched, where, in what "
                        "language, over what window. Required before a report can pass --strict")
    c.add_argument("--rejected", action="store_true",
                   help="a candidate examined and discarded; renders under Rejected candidates")
    c.add_argument("--gap", action="store_true",
                   help="an open question; renders under Gaps and limitations")
    c.add_argument("--theme", help="grouping heading for the findings section")
    c.set_defaults(fn=cmd_add)

    g = common(sub.add_parser("grade", help="append a new source grade"))
    g.add_argument("--id", required=True)
    g.add_argument("--reliability", choices=RELIABILITY)
    g.add_argument("--credibility", choices=CREDIBILITY)
    g.add_argument("--probability", choices=PROBABILITY)
    g.set_defaults(fn=cmd_grade)

    v = common(sub.add_parser("verdict", help="append a new verdict"))
    v.add_argument("--id", required=True)
    v.add_argument("--verdict", required=True, choices=VERDICTS)
    v.add_argument("--note", help="why")
    v.set_defaults(fn=cmd_verdict)

    s = common(sub.add_parser("show", help="print one folded claim"))
    s.add_argument("--id", required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_show)

    l = common(sub.add_parser("list", help="list folded claims"))
    l.add_argument("--status", choices=VERDICTS, help="filter by verdict")
    l.add_argument("--limit", type=int, default=20)
    l.add_argument("--offset", type=int, default=0)
    l.add_argument("--json", action="store_true")
    l.set_defaults(fn=cmd_list)

    st = common(sub.add_parser("stats", help="counts by verdict and probability"))
    st.add_argument("--json", action="store_true")
    st.set_defaults(fn=cmd_stats)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "limit", 1) == 0:
        die("--limit must be >= 1.", EXIT_USAGE)
    if getattr(args, "offset", 0) < 0:
        die("--offset must be >= 0.", EXIT_USAGE)
    try:
        return args.fn(args)
    except BrokenPipeError:
        return EXIT_OK
    except KeyboardInterrupt:
        die("interrupted", EXIT_ENV)


if __name__ == "__main__":
    raise SystemExit(main())
