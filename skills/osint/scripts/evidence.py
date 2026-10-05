#!/usr/bin/env python3
"""Capture a raw artefact, hash it, and record it in an append-only manifest.

Raw evidence is immutable: once a payload lands in `<case>/raw/` its bytes never change, so a
verdict written months later can still be recomputed against the artefact the verdict was based on.
That property is worth more than convenience, so `capture` refuses to overwrite and the manifest
is only ever opened in append mode.

Standard library only, Python 3.9+. No network calls. Reads nothing from the network: `capture`
takes a local file or stdin, because fetching is the agent's job and this script is the part that
must not lie about where a byte came from.

Usage:
    evidence.py capture --case DIR --file PATH --slug NAME --source "where it came from"
    evidence.py capture --case DIR --slug NAME --source "..." < payload.json
    evidence.py verify  --case DIR
    evidence.py list    --case DIR [--limit N] [--offset N] [--json]

Exit codes:
    0  success
    1  usage error
    2  gate refused - immutable file exists, credential detected, or verification found a mismatch
    3  environment error - missing or unreadable path
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys


class _Parser(argparse.ArgumentParser):
    """argparse exits 2 on a bad flag, which would collide with "a gate refused".

    Keeping usage errors at 1 is what makes exit 2 mean exactly one thing: the script looked at
    your data and declined. An agent that cannot tell a mistyped flag from a detected credential
    will eventually report one as the other.
    """

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(1)

from datetime import datetime, timezone
from pathlib import Path

EXIT_OK, EXIT_USAGE, EXIT_GATE, EXIT_ENV = 0, 1, 2, 3

# Credential shapes worth refusing before a payload reaches disk. Each is reported by line number
# and pattern name only: the matched text is never echoed, because echoing it would copy the
# secret into the transcript that this script exists to protect.
SECRET_PATTERNS = (
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("assigned-secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd)"
        r"\b\s*[:=]\s*[\"']?[^\s\"',]{12,}")),
    ("bearer-token", re.compile(r"(?i)\bauthorization\s*[:=]\s*[\"']?bearer\s+[A-Za-z0-9._\-]{16,}")),
)

# Extensions we accept on a slug. Kept small: raw evidence is json/txt/html/pdf/images/warc.
KNOWN_EXT = {".json", ".txt", ".html", ".htm", ".pdf", ".jpg", ".jpeg", ".png", ".gif",
             ".webp", ".xml", ".csv", ".warc", ".har", ".jsonl", ".yaml", ".yml", ".eml",
             ".pcap", ".pcapng", ".zip", ".gz", ".mp4", ".mp3", ".wav", ".svg", ".md"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def die(msg: str, code: int):
    print(f"evidence.py: {msg}", file=sys.stderr)
    raise SystemExit(code)


def read_manifest(case: Path) -> list[dict]:
    mf = case / "manifest.jsonl"
    if not mf.exists():
        return []
    rows = []
    for n, line in enumerate(mf.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            die(f"{mf}:{n}: {e}. The manifest is append-only; repair the file by hand "
                f"or start a new manifest.", EXIT_ENV)
    return rows


def append_jsonl(path: Path, record: dict) -> None:
    """Append one line. This is the only writer; nothing here truncates or rewrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def append_log(case: Path, verb: str, subject: str, clause: str) -> None:
    log = case / ".notes-log.md"
    if not log.exists():
        log.write_text("# Activity log\n\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"## [{utc_now()}] {verb} | {subject} | {clause}\n")


def scan_secrets(data: bytes) -> list[tuple[str, int]]:
    """Return [(pattern_name, line_number)] for each credential hit. Never returns the value."""
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return []
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in SECRET_PATTERNS:
            if rx.search(line):
                hits.append((name, lineno))
    return hits


def cmd_capture(a: argparse.Namespace) -> int:
    case = Path(a.case).expanduser()
    if not a.slug:
        die(f"--slug is required. Supply --slug NAME, and --ext when reading from stdin "
            f"(one of: {', '.join(sorted(KNOWN_EXT))}).", EXIT_USAGE)
    slug = re.sub(r"[^a-z0-9._-]+", "-", a.slug.lower()).strip("-.")
    if not slug:
        die(f"--slug {a.slug!r} contains no usable characters.", EXIT_USAGE)

    if a.file:
        src = Path(a.file).expanduser()
        if not src.is_file():
            die(f"--file {src} does not exist or is not a regular file.", EXIT_ENV)
        try:
            data = src.read_bytes()
        except OSError as e:
            die(f"cannot read {src}: {e}", EXIT_ENV)
        ext = src.suffix.lower()
    else:
        data = sys.stdin.buffer.read()
        ext = f".{a.ext.lstrip('.')}" if a.ext else ".txt"

    if ext and ext not in KNOWN_EXT:
        print(f"evidence.py: note: unusual extension {ext!r}; capturing anyway", file=sys.stderr)

    dest = case / "raw" / f"{slug}{ext}"
    if dest.exists() and not a.force:
        die(f"{dest} already exists and raw evidence is immutable. Use a new --slug, or "
            f"--force to write a second copy beside it (the original is never modified).", EXIT_GATE)

    hits = scan_secrets(data)
    if hits and not a.allow_secret:
        listed = ", ".join(f"{name} at line {ln}" for name, ln in hits[:5])
        more = f" (+{len(hits) - 5} more)" if len(hits) > 5 else ""
        die(f"payload looks like it contains a credential: {listed}{more}. The value is not "
            f"printed. Redact it, or re-run with --allow-secret, which records the escape in "
            f"the activity log.", EXIT_GATE)

    digest = hashlib.sha256(data).hexdigest()
    manifest = case / "manifest.jsonl"
    for row in read_manifest(case):
        if row.get("sha256") == digest:
            print(f"evidence.py: identical content already captured as {row['path']} "
                  f"(sha256 {digest[:12]}); nothing written.", file=sys.stderr)
            print(json.dumps({"status": "duplicate", "path": row["path"], "sha256": digest}))
            return EXIT_OK

    if a.dry_run:
        print(json.dumps({"status": "dry-run", "path": str(dest), "bytes": len(data),
                          "sha256": digest, "secrets": [h[0] for h in hits]}))
        return EXIT_OK

    dest.parent.mkdir(parents=True, exist_ok=True)
    # 'xb' would be ideal but the existence check above already ran; 'wb' here can only reach
    # this line for a fresh path or under --force with a distinct slug.
    dest.write_bytes(data)
    record = {"sha256": digest, "path": str(dest.relative_to(case)).replace(os.sep, "/"),
              "bytes": len(data), "source": a.source or "unstated",
              "retrieved_utc": utc_now()}
    append_jsonl(manifest, record)

    clause = f"captured {record['path']} sha256 {digest[:12]} from {record['source']}"
    if hits and a.allow_secret:
        clause += f" [ALLOWED SECRET: {'; '.join(f'{n} line {l}' for n, l in hits)}]"
    append_log(case, "research", "-", clause)

    print(json.dumps({"status": "captured", **record}, ensure_ascii=False))
    return EXIT_OK


def cmd_verify(a: argparse.Namespace) -> int:
    case = Path(a.case).expanduser()
    if not case.is_dir():
        die(f"case directory {case} does not exist.", EXIT_ENV)
    rows = read_manifest(case)
    raw_dir = case / "raw"
    problems: list[str] = []

    listed = set()
    for r in rows:
        rel = r.get("path", "")
        listed.add(rel)
        target = case / rel
        if not target.is_file():
            problems.append(f"manifest row has no file: {rel}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != r.get("sha256"):
            problems.append(f"HASH MISMATCH {rel}: manifest {r.get('sha256','')[:12]} "
                            f"on disk {actual[:12]}")

    if raw_dir.is_dir():
        for p in sorted(raw_dir.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(case)).replace(os.sep, "/")
                if rel not in listed:
                    problems.append(f"file has no manifest row: {rel}")

    checked = len(rows)
    if problems:
        print(f"{len(problems)} problem(s) across {checked} manifest row(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print(json.dumps({"status": "failed", "rows": checked, "problems": problems}))
        return EXIT_GATE
    print(json.dumps({"status": "ok", "rows": checked,
                      "message": f"{checked} artefact(s) hash-match the manifest"}))
    return EXIT_OK


def cmd_list(a: argparse.Namespace) -> int:
    case = Path(a.case).expanduser()
    rows = read_manifest(case)
    total = len(rows)
    window = rows[a.offset:a.offset + a.limit]
    if a.json:
        print(json.dumps({"total": total, "offset": a.offset, "limit": a.limit,
                          "entries": window}, indent=2))
        return EXIT_OK
    print(f"{total} artefact(s); showing {len(window)} from offset {a.offset}\n")
    print(f"{'sha256':14} {'bytes':>9}  {'retrieved':17} path")
    for r in window:
        print(f"{r.get('sha256','')[:12]:14} {r.get('bytes',0):9}  "
              f"{r.get('retrieved_utc',''):17} {r.get('path','')}")
        if r.get("source"):
            print(f"{'':14} {'':9}  {'':17}   from {r['source']}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(
        prog="evidence.py",
        description="Capture a raw artefact, hash it, and record it in an append-only manifest. "
                    "Raw is immutable; this is what lets an old verdict still be checked.",
        epilog="Exit codes: 0 success | 1 usage error | 2 gate refused (immutable file exists, "
               "credential detected, or verify found a mismatch) | 3 environment error.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(parser_class=_Parser, dest="cmd", required=True)

    c = sub.add_parser("capture", help="store a payload under raw/ and append to the manifest")
    c.add_argument("--case", default="case", help="case directory (default: case)")
    c.add_argument("--file", help="read the payload from this local file")
    c.add_argument("--ext", help="extension when reading from stdin (default: txt)")
    c.add_argument("--slug", help="name stem for the stored file; sanitised to [a-z0-9._-]")
    c.add_argument("--source", help="where this payload came from, as a citation")
    c.add_argument("--force", action="store_true",
                   help="capture a second copy beside an existing slug; never overwrites")
    c.add_argument("--allow-secret", action="store_true",
                   help="record a credential found in the payload and write it anyway")
    c.add_argument("--dry-run", action="store_true", help="report what would happen, write nothing")
    c.set_defaults(fn=cmd_capture)

    v = sub.add_parser("verify", help="re-hash every manifest row and find orphans")
    v.add_argument("--case", default="case", help="case directory (default: case)")
    v.set_defaults(fn=cmd_verify)

    l = sub.add_parser("list", help="list the manifest")
    l.add_argument("--case", default="case", help="case directory (default: case)")
    l.add_argument("--limit", type=int, default=20, help="max rows to print (default: 20)")
    l.add_argument("--offset", type=int, default=0, help="rows to skip (default: 0)")
    l.add_argument("--json", action="store_true", help="machine-readable output")
    l.set_defaults(fn=cmd_list)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "limit", 1) < 1 or getattr(args, "offset", 0) < 0:
        die("--limit must be >= 1 and --offset >= 0.", EXIT_USAGE)
    try:
        return args.fn(args)
    except BrokenPipeError:
        return EXIT_OK
    except KeyboardInterrupt:
        die("interrupted", EXIT_ENV)


if __name__ == "__main__":
    raise SystemExit(main())
