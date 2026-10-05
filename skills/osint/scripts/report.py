#!/usr/bin/env python3
"""Render the intelligence product from the claim ledger, and gate what is not sourced.

The ledger is the input: `<case>/claims.jsonl` (fold the append-only lines on read), the
hashed captures in `<case>/manifest.jsonl`, and the scope note. Nothing is fetched, and
nothing is invented — a claim the ledger does not carry does not reach the report, and a
capture that is not in the manifest is not evidence.

`--strict` collects every violation and exits 2 with the whole list. Reporting the first
one and stopping teaches nothing, because the next run finds the second one.

Grading vocabulary, fixed so a grade means one thing:
  verdict      confirmed | probable | unverified | inferred | inconclusive | refuted
  reliability  A (official primary) .. E (not usable), from `claimlog.py --reliability`
  credibility  1 confirmed by other sources .. 6 cannot be judged, `--credibility`
  probability  the seven-rung ladder, printed in the report body
Confidence is derived from the credibility digit and is a separate axis from probability:
"highly likely, low confidence" is a legitimate sentence. `claimlog.py` writes five of the
six verdict terms (it has no `inferred`); both are accepted here so a ledger written
either way renders, and an unrecognised term renders as itself rather than being dropped.

Where each section's content comes from, so nothing is silently invented:
  BLUF / Key judgements   claims, most-confirmed first. `key: true` on a claim promotes
                          it into Key judgements when any claim carries that flag.
  Findings by theme       claims grouped by their optional `theme` field, or "Ungrouped".
  Negative findings       claims carrying `negative: true` — what was searched and not
                          found. A report with none is a gate failure, not a shrug.
  Rejected candidates     claims with verdict `refuted`, or carrying `rejected: true`.
  Gaps and limitations    scope fields left `— NOT STATED —`, claims carrying `gap: true`,
                          and claims whose verdict is `unverified` or `inconclusive`.
  Methodology             counts read off the manifest, the ledger, the scope note and
                          the wiki index. No estimate.
  Sources                 every citation in the ledger, cross-checked against the manifest.
  Errors appendix         claims that supersede an earlier claim, and correction lines in
                          `<case>/.notes-log.md`.

Standard library only, Python 3.9+. No network calls.

Usage:
    report.py --case DIR --wiki DIR [-o FILE] [--strict] [--format md|json]
              [--limit N] [--offset N] [--dry-run]

Example:
    report.py --case cases/acme-phish --wiki ./.osint-wiki --strict
    OSINT_AUTHOR="A. Analyst" OSINT_CLASSIFICATION="TLP:AMBER" \\
        report.py --case cases/acme-phish --wiki ./.osint-wiki -o cases/acme-phish/report.md

Output is bounded: the claims table shows --limit claims (default 20) starting at
--offset, and the report says on its face how many it left out.

Template: `assets/report-template.md` is used when it carries at least one known section
placeholder. Otherwise the built-in skeleton in this module is used and the fallback is
reported on stderr — never silently.

Exit codes: 0 success | 1 usage error | 2 --strict found a violation | 3 environment error
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

# The ladder is printed verbatim inside the report: a reader who has not seen the key
# cannot check an estimate, and an estimate nobody can check is decoration.
LADDER = (
    "almost certainly 93-99% | highly likely 75-92% | likely 55-74% | "
    "roughly even chance 45-55% | unlikely 25-44% | highly unlikely 6-24% | remote 0-5%"
)

GRADE_TERMS = ("confirmed", "probable", "unverified", "inferred", "inconclusive", "refuted")
GRADE_RANK = {"confirmed": 0, "probable": 1, "inferred": 2, "unverified": 3,
              "inconclusive": 4, "refuted": 5}

# Confidence language, keyed on the Admiratory credibility digit. Named once, used
# everywhere: an adjective that means two things is worth nothing.
CREDIBILITY = {
    "1": "confirmed by other sources",
    "2": "probably true",
    "3": "possibly true",
    "4": "doubtful",
    "5": "improbable",
    "6": "cannot be judged",
}
UNGRADED = "— NOT GRADED —"

# A `confirmed` claim asserts the strongest thing the vocabulary allows, so the source
# under it has to be able to carry it. C is where a single uncorroborated reading lives.
WEAK_RELIABILITIES = ("C", "D", "E")

NOT_STATED = "— NOT STATED —"

# The ladder may sit inline or as a table; either counts as present. Every rung name has to
# be there, because one matching rung proves nothing.
LADDER_RUNGS = ("almost certainly", "highly likely", "likely", "roughly even chance",
                "unlikely", "highly unlikely", "remote")


def ladder_present(text: str) -> bool:
    return all(rung in text for rung in LADDER_RUNGS)

VIOLATION_RULES = {
    "unsourced-claim": "a claim with an empty sources list",
    "evidence-not-in-manifest": "a claim citing evidence the manifest does not hold",
    "grade-too-weak-for-confirmed": "a confirmed claim on a C, D or E source",
    "unresolved-citation": "a citation that resolves to no manifest entry",
    "empty-negative-findings": "a report with no negative findings",
}

SECTIONS = (
    "HEADER", "BLUF", "KEY_JUDGEMENTS", "FINDINGS", "NEGATIVE_FINDINGS",
    "REJECTED_CANDIDATES", "GAPS_AND_LIMITATIONS", "METHODOLOGY", "SOURCES",
    "ERRORS_APPENDIX",
)

SECTION_TITLES = {
    "HEADER": "Report header",
    "BLUF": "BLUF",
    "KEY_JUDGEMENTS": "Key judgements",
    "FINDINGS": "Findings by theme",
    "NEGATIVE_FINDINGS": "Negative findings",
    "REJECTED_CANDIDATES": "Rejected candidates",
    "GAPS_AND_LIMITATIONS": "Gaps and limitations",
    "METHODOLOGY": "Methodology",
    "SOURCES": "Sources",
    "ERRORS_APPENDIX": "Errors this investigation made, and how they were caught",
}

# A section may appear in a template under more than one name; every alias resolves to the
# one canonical section. A template the reader can edit is worth more than a strict one.
SECTION_ALIASES = {
    "GAPS": "GAPS_AND_LIMITATIONS",
    "ERRORS": "ERRORS_APPENDIX",
    "THEMES": "FINDINGS",
}

# Header fields a template may address individually instead of as one {{HEADER}} block.
HEADER_SCALARS = ("TITLE", "DATE", "SCOPE", "AUTHOR", "CLASSIFICATION", "WINDOW_NOTE")

CORRECTION_WORDS = ("correct", "wrong", "mistake", "mistaken", "overturn", "reversed",
                    "retracted", "initially", "earlier claim", "false positive",
                    "redone", "re-derived")


def die(msg: str, code: int):
    print(f"report.py: {msg}", file=sys.stderr)
    raise SystemExit(code)


def warn(msg: str):
    print(f"report.py: {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- input


def read_jsonl(path: Path, label: str) -> tuple[list[tuple[int, dict]], int]:
    """Read one JSON object per line. Returns (rows, malformed_line_count).

    A corrupt line is skipped and counted rather than aborting the render: one bad line
    should not cost an investigation its whole report. The count reaches Methodology, so
    the omission stays visible instead of being silent.
    """
    rows: list[tuple[int, dict]] = []
    malformed = 0
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        die(f"{label} not found: {path}", EXIT_ENV)
    except OSError as exc:
        die(f"{label} unreadable: {path} ({exc.strerror or exc})", EXIT_ENV)
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(obj, dict):
            rows.append((lineno, obj))
        else:
            malformed += 1
    return rows, malformed


def fold_claims(rows: list[tuple[int, dict]]) -> dict[str, dict]:
    """Collapse append-only ledger lines into the current view. Later explicit fields win.

    `revisions` counts how many lines touched each claim, so the report can show that a
    verdict was reasoned into rather than written once.
    """
    folded: dict[str, dict] = {}
    for lineno, rec in rows:
        cid = rec.get("id")
        if not cid:
            continue
        cur = folded.setdefault(cid, {"id": cid, "revisions": 0})
        for key, value in rec.items():
            if key in ("merge", "id"):
                continue
            cur[key] = value
        cur["revisions"] += 1
        cur["last_line"] = lineno
        cur.setdefault("claim", "")
    return folded


def load_manifest(case: Path) -> dict[str, dict]:
    """Capture records keyed by path. The manifest is the only definition of evidence."""
    path = case / "manifest.jsonl"
    if not path.exists():
        return {}
    by_path: dict[str, dict] = {}
    for _, rec in read_jsonl(path, "manifest.jsonl")[0]:
        p = rec.get("path")
        if isinstance(p, str) and p:
            by_path[p] = rec
    return by_path


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str) and v.strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def claim_grade(rec: dict) -> str:
    verdict = rec.get("verdict")
    return verdict if isinstance(verdict, str) and verdict.strip() else ""


def claim_confidence(rec: dict) -> str:
    digit = str(rec.get("credibility", "") or "").strip()
    return CREDIBILITY.get(digit, UNGRADED)


def flat_grade(rec: dict) -> str:
    """The A-E x 1-6 code, or the half of it that exists. Never invented."""
    rel = str(rec.get("reliability", "") or "").strip().upper() or "—"
    cred = str(rec.get("credibility", "") or "").strip() or "—"
    if rel == "—" and cred == "—":
        return UNGRADED
    return f"{rel}{cred}"


def claim_order(claims: dict[str, dict]) -> list[dict]:
    return sorted(
        claims.values(),
        key=lambda c: (GRADE_RANK.get(claim_grade(c), 9), c.get("id", "")),
    )


# ------------------------------------------------------------------- scope and wiki


def read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError:
        return None


def scope_section(scope_text: str | None, heading: str) -> str:
    """First paragraph under a `## Heading` in scope.md, or the empty string."""
    if not scope_text:
        return ""
    lines = scope_text.splitlines()
    pattern = re.compile(rf"^#{{1,3}}\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    for i, line in enumerate(lines):
        if not pattern.match(line):
            continue
        block: list[str] = []
        for rest in lines[i + 1:]:
            if rest.startswith("#"):
                break
            if rest.strip():
                block.append(rest.strip())
            elif block:
                break
        return " ".join(block).strip()
    return ""


def scope_gaps(scope_text: str | None) -> list[str]:
    """Named scope fields left unstated. A gap is a field, not a shrug."""
    if not scope_text:
        return []
    gaps = []
    for line in scope_text.splitlines():
        stripped = line.strip()
        if NOT_STATED in stripped:
            label = stripped.lstrip("-*").strip()
            label = label.split(":")[0].strip() or stripped
            gaps.append(label)
    seen, out = set(), []
    for g in gaps:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out


def wiki_state(wiki: Path) -> dict:
    """What the knowledge wiki already held. Read-only; a missing wiki is not an error."""
    state = {"path": str(wiki), "exists": wiki.is_dir(), "index_entries": 0,
             "pages_on_disk": 0, "dirs": {}, "log_entries": 0}
    index = read_text_or_none(wiki / "index.md")
    if index:
        state["index_entries"] = len(re.findall(r"\[\[([^\]]+)\]\]", index))
    log = read_text_or_none(wiki / "log.md")
    if log:
        state["log_entries"] = sum(
            1 for ln in log.splitlines() if ln.strip().startswith("## ["))
    for name in ("entities", "concepts", "syntheses", "timelines", "claims"):
        d = wiki / name
        if d.is_dir():
            state["dirs"][name] = sum(1 for p in d.iterdir()
                                      if p.suffix.lower() == ".md")
    state["pages_on_disk"] = sum(state["dirs"].values())
    return state


# ------------------------------------------------------------------- source registry


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())

# Shortest manifest field allowed to satisfy a citation by containment. Below this, a
# match is coincidence rather than a reference.
MIN_CONTAINMENT_LEN = 12


def matches(record: dict, citation: str) -> bool:
    """Does this capture answer to this citation?

    Exact normalised equality on source, url or path first. Then containment on source
    and url only, and only for a field of real length: a ledger line is often a full URL
    and the manifest's `source` field a shorter form of it, but a two-character fragment
    "resolving" a citation is worse than an unresolved one.
    """
    for key in ("source", "url", "path"):
        field = record.get(key)
        if not isinstance(field, str) or not field:
            continue
        if normalise(field) == normalise(citation):
            return True
    for key in ("source", "url"):
        field = record.get(key)
        if not isinstance(field, str) or len(field) < MIN_CONTAINMENT_LEN:
            continue
        if citation in field or field in citation:
            return True
    return False


def build_sources(claims: list[dict], manifest: dict[str, dict]) -> list[dict]:
    """One row per distinct citation, with its grade and where it was retrieved.

    A source is graded by the best reliability among the claims that cite it: the grade
    describes the evidence, not the weakest reader who relied on it. The claim-level grade
    is printed next to every claim, so nothing is hidden by this roll-up.
    """
    order: list[str] = []
    rows: dict[str, dict] = {}
    for claim in claims:
        for citation in as_list(claim.get("sources")):
            if citation not in rows:
                rows[citation] = {"citation": citation, "claims": [], "reliability": None,
                                  "retrieved_utc": "", "capture": ""}
                order.append(citation)
            row = rows[citation]
            row["claims"].append(claim.get("id", "?"))
            rel = str(claim.get("reliability", "") or "").strip().upper()
            if rel and (row["reliability"] is None or rel < row["reliability"]):
                row["reliability"] = rel
            for path, record in manifest.items():
                if matches(record, citation):
                    if not row["retrieved_utc"]:
                        row["retrieved_utc"] = str(record.get("retrieved_utc", "") or "")
                        row["capture"] = path
                    break
    out = []
    for n, citation in enumerate(order, start=1):
        row = rows[citation]
        row["number"] = f"S{n}"
        out.append(row)
    return out


# ------------------------------------------------------------------------ violations


class Report:
    def __init__(self, case: Path, wiki: Path, limit: int, offset: int):
        self.case = case
        self.wiki = wiki
        self.limit = limit
        self.offset = offset
        self.violations: list[dict] = []

    def violation(self, kind: str, where: str, detail: str, fix: str) -> None:
        self.violations.append({"rule": kind, "where": where, "detail": detail, "fix": fix})

    # -- inputs

    def load(self) -> None:
        self.claim_rows, self.malformed = read_jsonl(self.case / "claims.jsonl",
                                                    "claims.jsonl")
        self.claims = fold_claims(self.claim_rows)
        self.manifest = load_manifest(self.case)
        self.scope_text = read_text_or_none(self.case / "scope.md")
        self.notes = read_text_or_none(self.case / ".notes-log.md")
        self.wiki_state = wiki_state(self.wiki)
        self.ordered = claim_order(self.claims)
        self.window = self.ordered[self.offset:self.offset + self.limit]
        self.shown = len(self.window)
        self.total = len(self.ordered)
        self.sources = build_sources(self.window, self.manifest)
        self.source_numbers = {row["citation"]: row["number"] for row in self.sources}

    # -- gate

    def check(self) -> None:
        for claim in self.window:
            cid = claim.get("id", "?")
            sources = as_list(claim.get("sources"))
            evidence = as_list(claim.get("evidence"))
            reliability = str(claim.get("reliability", "") or "").strip().upper()

            if not sources:
                self.violation(
                    "unsourced-claim", cid,
                    f"{cid} has no sources.",
                    "Record the citation with `claimlog.py add --source`, or drop the claim.")

            for path in evidence:
                if path not in self.manifest:
                    self.violation(
                        "evidence-not-in-manifest", cid,
                        f"{cid} cites evidence `{path}`, which manifest.jsonl does not hold.",
                        "Capture the payload with `evidence.py capture`, then re-file the claim.")

            verdict = claim_grade(claim)
            if verdict == "confirmed" and reliability in WEAK_RELIABILITIES:
                self.violation(
                    "grade-too-weak-for-confirmed", cid,
                    f"{cid} is confirmed on a {reliability}-grade source.",
                    "A confirmed verdict needs an A or B source; otherwise set the verdict to "
                    "probable or unverified with `claimlog.py verdict`.")

        # An absence-shaped claim has nothing to capture. "Searched X, found nothing" and an open
        # question are both defined by the absence of a record; demanding a manifest entry would
        # mean capturing an empty result, which is not evidence of anything. The requirement that
        # a negative finding states *where it looked* is enforced instead by claimlog.py, which
        # refuses `--negative` without a --source.
        absence_ids = {c.get("id") for c in self.window
                       if c.get("negative") is True or c.get("gap") is True
                       or c.get("rejected") is True}

        for row in self.sources:
            if row["claims"] and all(cid in absence_ids for cid in row["claims"]):
                continue
            if not row["capture"]:
                self.violation(
                    "unresolved-citation", row["number"],
                    f"citation {row['number']} (`{row['citation']}`) resolves to no capture "
                    f"in manifest.jsonl.",
                    "Capture the page, or remove the citation from the claim that carries it.")


        if not self.negative_findings():
            self.violation(
                "empty-negative-findings", "Negative findings",
                "the report has no negative findings.",
                "Record what was searched and not found with `claimlog.py add "
                "--claim \"<absence>\"` and flag it `negative`; an unstated absence is "
                "indistinguishable from an unfinished search.")

    def flags(self) -> dict[str, list[str]]:
        """The same rules as `check`, keyed by claim id, for inline marking without --strict."""
        marks: dict[str, list[str]] = {}
        for claim in self.window:
            cid = claim.get("id", "?")
            if not as_list(claim.get("sources")):
                marks[cid] = [f"{cid} carries no source. A sentence with nothing behind it "
                              "is an assertion, not a finding."]
            for path in as_list(claim.get("evidence")):
                if path not in self.manifest:
                    marks.setdefault(cid, []).append(
                        f"{cid} cites `{path}`, which no capture backs; treat the claim as "
                        "unevidenced until the payload is on disk.")
            reliability = str(claim.get("reliability", "") or "").strip().upper()
            if claim_grade(claim) == "confirmed" and reliability in WEAK_RELIABILITIES:
                marks.setdefault(cid, []).append(
                    f"{cid} is marked confirmed on a {reliability}-grade source, which cannot "
                    "carry that verdict; read it as probable.")
        return marks

    def source_marks(self) -> dict[str, str]:
        return {row["number"]: f"citation {row['number']} (`{row['citation']}`) resolves to no "
                               "capture in the manifest; this citation is not evidence."
                for row in self.sources if not row["capture"]}

    # -- section content

    def key_judgements(self) -> list[dict]:
        flagged = [c for c in self.window if c.get("key") is True]
        if flagged:
            return flagged
        return [c for c in self.window if claim_grade(c) in ("confirmed", "probable")]

    def findings(self) -> list[tuple[str, list[dict]]]:
        themes: dict[str, list[dict]] = {}
        for claim in self.window:
            theme = claim.get("theme")
            name = str(theme).strip() if isinstance(theme, str) and theme.strip() else "Ungrouped"
            themes.setdefault(name, []).append(claim)
        return [(name, themes[name]) for name in sorted(themes)]

    def negative_findings(self) -> list[dict]:
        return [c for c in self.window if c.get("negative") is True]

    def rejected(self) -> list[dict]:
        out = [c for c in self.window
               if claim_grade(c) == "refuted" or c.get("rejected") is True]
        return out

    def gaps(self) -> list[str]:
        out = [f"Scope field left unstated in `scope.md`: {name}."
               for name in scope_gaps(self.scope_text)]
        out.extend(f"{c.get('id', '?')}: stated as {claim_grade(c) or 'ungraded'} — "
                   f"{str(c.get('claim', '')).strip()[:160]}"
                   for c in self.window
                   if c.get("gap") is True
                   or claim_grade(c) in ("unverified", "inconclusive"))
        if not out:
            out.append("No unstated scope field and no ungraded claim in the window "
                       "rendered. That is the state of this ledger, not a guarantee that "
                       "the investigation had no gaps.")
        return out

    def correction_lines(self) -> list[str]:
        if not self.notes:
            return []
        out = []
        for line in self.notes.splitlines():
            stripped = line.strip()
            if not stripped.startswith("## ["):
                continue
            low = stripped.lower()
            if any(word in low for word in CORRECTION_WORDS):
                out.append(stripped.lstrip("# ").strip())
        return out

    def errors_made(self) -> list[str]:
        out = []
        for claim in self.window:
            superseded = claim.get("supersedes")
            if superseded:
                out.append(f"{claim.get('id', '?')} supersedes {superseded}: "
                           f"{str(claim.get('note') or claim.get('claim') or '').strip()}")
        out.extend(self.correction_lines())
        if not out:
            out.append("No correction is recorded in this case. That is an absence of "
                       "records, not evidence that the investigation made no error — a "
                       "reader should treat it as untested.")
        return out


# ------------------------------------------------------------------------ rendering


def cite(claim: dict, rep: Report) -> str:
    nums = [rep.source_numbers[s] for s in as_list(claim.get("sources"))
            if s in rep.source_numbers]
    evidence = as_list(claim.get("evidence"))
    bits = []
    if nums:
        bits.append("sources " + ", ".join(nums))
    if evidence:
        bits.append("evidence " + ", ".join(f"`{e}`" for e in evidence))
    return "; ".join(bits) if bits else "no citation"


def claim_line(claim: dict, rep: Report) -> str:
    verdict = claim_grade(claim) or "ungraded"
    probability = str(claim.get("probability", "") or "").strip() or "not estimated"
    text = " ".join(str(claim.get("claim", "")).split())
    return (f"- **{claim.get('id', '?')}** — {text}\n"
            f"  verdict: {verdict} · grade: {flat_grade(claim)} · "
            f"probability: {probability} · confidence: {claim_confidence(claim)} · "
            f"{cite(claim, rep)}")



def section_body(name: str, rep: Report, marks: dict[str, list[str]],
                 smarks: dict[str, str]) -> str:
    if name == "HEADER":
        return header_block(rep)

    if name == "BLUF":
        lines = ["Every graded claim, strongest verdict first. A claim with no citation is "
                 "not evidence and is marked inline.", ""]
        if not rep.window:
            lines.append("_The window rendered no claims._")
        for claim in rep.window:
            lines.append(claim_line(claim, rep))
            for mark in marks.get(claim.get("id", "?"), []):
                lines.append(f"  UNVERIFIED: {mark}")

    elif name == "KEY_JUDGEMENTS":
        kj = rep.key_judgements()
        if not kj:
            lines = ["_No claim is confirmed or probable in the window rendered._"]
        else:
            lines = []
            for n, claim in enumerate(kj, start=1):
                probability = str(claim.get("probability", "") or "").strip()
                lines.append(f"{n}. **{claim.get('id', '?')}** "
                             f"{' '.join(str(claim.get('claim', '')).split())} "
                             f"— probability {probability or 'not estimated'}, "
                             f"confidence {claim_confidence(claim)}, "
                             f"grade {flat_grade(claim)}.")

    elif name == "FINDINGS":
        themes = rep.findings()
        if not themes:
            lines = ["_No claim in the window rendered._"]
        else:
            lines = []
            for theme, claims in themes:
                lines.append(f"### {theme}")
                lines.append("")
                for claim in claims:
                    lines.append(claim_line(claim, rep))
                    for mark in marks.get(claim.get("id", "?"), []):
                        lines.append(f"  UNVERIFIED: {mark}")
                lines.append("")

    elif name == "NEGATIVE_FINDINGS":
        negatives = rep.negative_findings()
        if not negatives:
            lines = [
                "_None recorded. This is a gate failure, not a statement that nothing was "
                "absent: it says the investigation did not write down what it looked for "
                "and did not find._",
            ]
        else:
            lines = ["Each entry names what was searched, against which source, and what the "
                     "source returned. An absence from a source that worked is a finding; an "
                     "absence from a source that failed is not.", ""]
            for claim in negatives:
                lines.append(claim_line(claim, rep))
                for mark in marks.get(claim.get("id", "?"), []):
                    lines.append(f"  UNVERIFIED: {mark}")

    elif name == "REJECTED_CANDIDATES":
        rejected = rep.rejected()
        if not rejected:
            lines = ["_No candidate was rejected._"]
        else:
            lines = ["Candidates examined and set aside, with the reason. A dropped candidate "
                     "is a result; a candidate nobody recorded is a repeat of the same work.",
                     ""]
            for claim in rejected:
                reason = str(claim.get("note") or "").strip() or "no reason recorded"
                lines.append(f"- **{claim.get('id', '?')}** — rejected. "
                             f"{' '.join(str(claim.get('claim', '')).split())} "
                             f"*Reason:* {reason} *Grade:* {flat_grade(claim)}.")

    elif name == "GAPS_AND_LIMITATIONS":
        lines = rep.gaps()

    elif name == "METHODOLOGY":
        lines = methodology(rep)

    elif name == "SOURCES":
        lines = sources_table(rep)
        for row in rep.sources:
            if row["number"] in smarks:
                lines.append(f"UNVERIFIED: {smarks[row['number']]}")

    elif name == "ERRORS_APPENDIX":
        lines = ["Each entry names the error and the check that surfaced it. An appendix "
                 "with no entries means the errors were not recorded, not that there were "
                 "none.", ""]
        lines.extend(rep.errors_made())

    else:
        lines = [""]

    return "\n".join(lines)


def header_scalars(rep: Report) -> dict:
    """The four header fields the case carries, plus the title the caller chose.

    Author, classification and date are not derivable from a ledger, so they come from the
    environment and render as NOT STATED when unset. A header nobody filled in is a gap
    the reader can see, which is the point of writing it down at all.
    """
    subject = scope_section(rep.scope_text, "Subject")
    objective = scope_section(rep.scope_text, "Objective")
    scope_bits = [b for b in (subject, objective) if b]
    window_note = (f"Claims rendered: {rep.shown} of {rep.total} "
                   f"(window starts at --offset {rep.offset}, width --limit {rep.limit}). "
                   f"Captures: {len(rep.manifest)}. Citations: {len(rep.sources)}."
                   if rep.total else
                   "No claims are recorded in this ledger.")
    return {
        # A report with no name is hard to file. The scope subject is the one thing the case
        # states that is actually a name for the product, so use it rather than a gap marker.
        "TITLE": os.environ.get("OSINT_REPORT_TITLE") or subject or NOT_STATED,
        "DATE": os.environ.get("OSINT_REPORT_DATE")
        or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "SCOPE": " — ".join(scope_bits) if scope_bits else NOT_STATED,
        "AUTHOR": os.environ.get("OSINT_AUTHOR") or NOT_STATED,
        "CLASSIFICATION": os.environ.get("OSINT_CLASSIFICATION") or NOT_STATED,
        "WINDOW_NOTE": window_note,
    }


def header_block(rep: Report) -> str:
    """The header as one block, for templates that carry a single {{HEADER}} slot."""
    fields = header_scalars(rep)
    ladder_note = ("Every probability below is one of these seven terms. Confidence is the "
                   "separate credibility axis (1 confirmed by other sources to 6 cannot be "
                   "judged); a claim can carry a high probability and a low confidence at "
                   "the same time.")
    return "\n".join([
        f"- **Date**: {fields['DATE']}",
        f"- **Scope**: {fields['SCOPE']}",
        f"- **Author**: {fields['AUTHOR']}",
        f"- **Classification**: {fields['CLASSIFICATION']}",
        "",
        fields["WINDOW_NOTE"],
        "",
        "### Probability ladder",
        "",
        LADDER,
        "",
        ladder_note,
    ])


def methodology(rep: Report) -> list[str]:
    state = rep.wiki_state
    lines = [
        "Counts are read off the case files; nothing here is estimated.", "",
        f"- Case: `{rep.case}`",
        f"- Ledger: {rep.total} claim(s) in `claims.jsonl`; "
        f"{rep.shown} rendered by this window; {malformed_note(rep.malformed)}",
        f"- Captures: {len(rep.manifest)} path(s) in `manifest.jsonl`",
        f"- Distinct citations: {len(rep.sources)}",
        f"- Scope note: {scope_note_line(rep)}",
        f"- Notes log: {log_lines(rep.notes)} line(s)",
        f"- Wiki `{state['path']}`: {'present' if state['exists'] else 'absent'}; "
        f"{state['index_entries']} index entr(ies); {state['pages_on_disk']} page(s) on disk",
        f"- Wiki log: {state['log_entries']} log entr(ies) in `log.md`",
        "",
        "Grading: reliability A-E and credibility 1-6 are printed per claim; a source's grade "
        "in the table below is the best reliability among the claims citing it. Verdicts "
        f"come from the fixed vocabulary ({', '.join(GRADE_TERMS)}).",
    ]
    if rep.window and rep.shown < rep.total:
        lines += ["",
                  f"The remaining {rep.total - rep.shown} claim(s) are outside this window. "
                  f"Raise `--limit` or move `--offset` to render them; a report that hides "
                  "claims behind a default width is a partial report."]
    return lines


def malformed_note(malformed: int) -> str:
    return (f"{malformed} malformed line(s) skipped and not rendered"
            if malformed else "no malformed lines")


def log_lines(notes: str | None) -> int:
    if not notes:
        return 0
    return sum(1 for ln in notes.splitlines() if ln.strip().startswith("## ["))


def scope_note_line(rep: Report) -> str:
    """Say plainly whether the scope gate ran. An absent scope note is a gate skipped."""
    return "present" if rep.scope_text is not None else "absent (scope gate not run)"


def sources_table(rep: Report) -> list[str]:
    lines = ["| # | URL | Retrieval UTC | Grade |", "|---|---|---|---|"]
    if not rep.sources:
        lines.append("| — | _no citation in the ledger_ | — | — |")
        return lines
    for row in rep.sources:
        grade = row["reliability"] or "—"
        if not row["capture"]:
            grade += " (unresolved)"
        lines.append(f"| {row['number']} | {row['citation']} | "
                     f"{row['retrieved_utc'] or '— NOT RECORDED —'} | {grade} |")
    lines += ["", "A blank retrieval time means the capture never recorded one; a citation "
                  "with no capture behind it is an assertion, not evidence."]
    return lines





# ---------------------------------------------------------------------- the template


DEFAULT_TEMPLATE = """# {{TITLE}}

Date: {{DATE}}
Scope: {{SCOPE}}
Author: {{AUTHOR}}
Classification: {{CLASSIFICATION}}

{{WINDOW_NOTE}}

## BLUF

{{BLUF}}

## Key judgements

{{KEY_JUDGEMENTS}}

Probability ladder, used verbatim and never reworded:

| Probability | Numeric range |
|---|---|
| almost certainly | 93-99% |
| highly likely | 75-92% |
| likely | 55-74% |
| roughly even chance | 45-55% |
| unlikely | 25-44% |
| highly unlikely | 6-24% |
| remote | 0-5% |

## Findings by theme

{{FINDINGS}}

## Negative findings

{{NEGATIVE_FINDINGS}}

## Rejected candidates

{{REJECTED_CANDIDATES}}

## Gaps and limitations

{{GAPS}}

## Methodology

{{METHODOLOGY}}

## Sources

{{SOURCES}}

## Errors this investigation made, and how they were caught

{{ERRORS}}
"""


def template_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "report-template.md"



def load_template() -> tuple[str, str]:
    """Return (template text, which one). Never fail because the asset is missing.

    A template is usable when it carries at least one known section slot; without one
    there is nowhere to put a section, and a report with no findings is not a report.
    """
    path = template_path()
    text = read_text_or_none(path)
    if text is None:
        return DEFAULT_TEMPLATE, "built-in (asset not found)"
    found = set(re.findall(r"\{\{([A-Z_]+)\}\}", text))
    if found & (set(SECTIONS) | set(SECTION_ALIASES) | {"BODY"}):
        return text, str(path)
    warn(f"{path} carries no known section placeholder "
         f"({', '.join(sorted(found)) or 'none found'}); using the built-in template.")
    return DEFAULT_TEMPLATE, "built-in (asset carries no section placeholder)"


def apply_template(template: str, sections: dict[str, str],
                   scalars: dict[str, str]) -> str:
    """Fill the template. A section with no slot is appended, never dropped.

    Aliases resolve to their canonical section, and the header can arrive either as one
    {{HEADER}} block or as individual {{DATE}} / {{SCOPE}} / {{AUTHOR}} /
    {{CLASSIFICATION}} fields, because a template someone can hand-edit is worth more than
    a strict one. The ladder is appended when the template omitted it: a reader who has
    not seen the key cannot check an estimate.
    """
    pending = dict(sections)
    uses_scalars = any("{{" + s + "}}" in template for s in HEADER_SCALARS)
    for name, value in scalars.items():
        template = template.replace("{{" + name + "}}", value)

    if uses_scalars and "{{HEADER}}" not in template:
        # The scalars already placed the header fields; drop the combined block so the
        # date is not printed twice.
        pending.pop("HEADER", None)

    for alias, canonical in SECTION_ALIASES.items():
        if "{{" + alias + "}}" in template and canonical in pending:
            template = template.replace("{{" + alias + "}}", pending[canonical])
            pending.pop(canonical, None)


    if re.search(r"\{\{BODY\}\}", template):
        joined = "\n\n".join(
            f"## {SECTION_TITLES[name]}\n\n{pending[name]}"
            for name in SECTIONS
            if name in pending and name != "HEADER")
        template = re.sub(r"\{\{BODY\}\}", joined, template)

    for name, value in pending.items():
        placeholder = "{{" + name + "}}"
        if placeholder in template:
            template = template.replace(placeholder, value)
        elif value.strip():
            template += (f"\n\n{name} was rendered but the template has no {placeholder} "
                         f"slot; the section is appended here.\n\n{value}")

    if not ladder_present(template):
        template += ("\n\n### Probability ladder\n\n" + LADDER + "\n")
    leftover = sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", template)))
    if leftover:
        warn("template placeholder(s) with no value: " + ", ".join(leftover))
    return template.rstrip() + "\n"


# ------------------------------------------------------------------------- commands


def build_model(rep: Report) -> dict:
    """The rendered content as data, for --format json and for reuse by other scripts."""
    marks = rep.flags()
    smarks = rep.source_marks()
    sections = {name: section_body(name, rep, marks, smarks) for name in SECTIONS}
    return {
        "case": str(rep.case),
        "wiki": rep.wiki_state,
        "ladder": LADDER,
        "header": header_scalars(rep),
        "sections": sections,
        "sources": rep.sources,
        "claims": [
            {"id": c.get("id"), "claim": c.get("claim"), "verdict": claim_grade(c),
             "reliability": c.get("reliability"), "credibility": c.get("credibility"),
             "probability": c.get("probability"), "grade": flat_grade(c),
             "confidence": claim_confidence(c), "sources": as_list(c.get("sources")),
             "evidence": as_list(c.get("evidence"))}
            for c in rep.window
        ],
        "window": {"total": rep.total, "shown": rep.shown,
                   "offset": rep.offset, "limit": rep.limit},
        "malformed_lines": rep.malformed,
        "violations": rep.violations,
    }


def report_violations(rep: Report) -> int:
    if not rep.violations:
        return EXIT_OK
    warn(f"--strict found {len(rep.violations)} violation(s); every one is listed.")
    for n, v in enumerate(rep.violations, start=1):
        print(f"{n}. [{v['rule']}] {v['where']}: {v['detail']}")
        print(f"   {VIOLATION_RULES.get(v['rule'], '')}")
        print(f"   fix: {v['fix']}", file=sys.stderr)
    print("", file=sys.stderr)
    print("The report was not delivered as clean. Fix every item above, then re-run.",
          file=sys.stderr)
    return EXIT_GATE


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="report.py",
        description="Render the intelligence product from the claim ledger, and gate what "
                    "is not sourced. --strict collects every violation and exits 2.",
        epilog=(
            "Examples:\n"
            "  report.py --case cases/acme --wiki ./.osint-wiki --strict\n"
            "  report.py --case cases/acme --wiki ./.osint-wiki --format json --limit 5\n"
            "\n"
            "Output is bounded: the claims table shows --limit claims (default 20) from "
            "--offset,\n"
            "and the report states on its face how many it left out.\n"
            "OSINT_AUTHOR, OSINT_CLASSIFICATION and OSINT_REPORT_DATE fill the header;\n"
            "each renders as - NOT STATED - when unset.\n"
            "\n"
            "Exit codes:\n"
            "  0  success\n"
            "  1  usage error\n"
            "  2  --strict found at least one violation\n"
            "  3  environment error - missing or unreadable case path\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--case", default="case", help="case directory (default: case)")
    p.add_argument("--wiki", default=os.environ.get("OSINT_WIKI", "./.osint-wiki"),
                   help="knowledge wiki root (default: $OSINT_WIKI, else ./.osint-wiki)")
    p.add_argument("-o", "--out", help="output file (default: <case>/report.md)")
    p.add_argument("--strict", action="store_true",
                   help="collect every violation, list them all, exit 2")
    p.add_argument("--format", choices=("md", "json"), default="md",
                   help="markdown report, or the same content as JSON (default: md)")
    p.add_argument("--limit", type=int, default=20,
                   help="claims to render in the window (default: 20)")
    p.add_argument("--offset", type=int, default=0,
                   help="index of the first claim in the window (default: 0)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the report and write nothing")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.limit < 1:
        die("--limit must be >= 1.", EXIT_USAGE)
    if args.offset < 0:
        die("--offset must be >= 0.", EXIT_USAGE)
    if args.format not in ("md", "json"):
        die(f"--format must be md or json, not {args.format!r}.", EXIT_USAGE)

    case = Path(args.case).expanduser()
    wiki = Path(args.wiki).expanduser()
    if not case.is_dir():
        die(f"case directory not found: {case}", EXIT_ENV)

    rep = Report(case, wiki, args.limit, args.offset)
    rep.load()
    rep.check()

    model = build_model(rep)
    template, origin = load_template()
    model["template"] = origin

    if args.format == "json":
        print(json.dumps(model, ensure_ascii=False, indent=2, sort_keys=False))
        return report_violations(rep) if args.strict else EXIT_OK

    text = apply_template(template, model["sections"], model["header"])
    out = Path(args.out).expanduser() if args.out else case / "report.md"

    if args.strict and rep.violations:
        # Rendered so the violations can be read in context, but not written: a file at
        # the default path is what a later step would pick up and treat as delivered.
        warn(f"--strict found {len(rep.violations)} violation(s); not writing {out}.")
        return report_violations(rep)

    if args.dry_run:
        print(text)
        warn(f"--dry-run: nothing written. Would write {out} "
             f"({len(text)} bytes, template: {origin}).")
        return EXIT_OK

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        die(f"cannot write {out}: {exc.strerror or exc}", EXIT_ENV)

    print(f"{out} — {rep.shown} of {rep.total} claim(s), "
          f"{len(rep.sources)} source(s), {len(rep.violations)} violation(s)")
    print(f"template: {origin}")
    return report_violations(rep) if args.strict else EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(EXIT_OK)
    except KeyboardInterrupt:
        die("interrupted", EXIT_ENV)