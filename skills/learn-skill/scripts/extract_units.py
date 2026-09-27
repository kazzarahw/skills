#!/usr/bin/env python3
"""Split a skill's markdown into small, citable units (steps, rules, gotchas, code, tables, ...).

Used for two jobs:
  - harvesting: triage another skill's content unit by unit when cherry-picking or merging;
  - coverage:   list your own skill's instructions so each can be mapped to an eval.

Usage:
  python3 extract_units.py <skill-dir | SKILL.md | file.md> [--source-id A] [--include-references]
                           [--format json|md] [--kinds step,rule,gotcha] [--min-words 3]

Each unit has: id (source-id + counter, e.g. A12), file, start/end line, section (heading path),
kind, flags, words, text. Kinds: frontmatter, step, rule, gotcha, point, code, command, template,
table, example, prose. Flags: imperative, emphatic (MUST/NEVER/...), conditional (if/when/unless),
rationale (because/so that), command (inline code or a path), dynamic-cmd (Claude Code
!`command` injection, which executes if copied into a SKILL.md).

Output goes to stdout: JSON (default) or a markdown ledger with an empty Verdict column.
Exit codes: 0 ok, 1 no input found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

GOTCHA_HEAD = re.compile(r"gotcha|pitfall|mistake|caveat|warning|anti-?pattern|red flag|trap|don't|avoid", re.I)
EXAMPLE_HEAD = re.compile(r"example", re.I)
TEMPLATE_HEAD = re.compile(r"template|format|structure|skeleton", re.I)
EMPHATIC = re.compile(r"\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|REQUIRED)\b")
DIRECTIVE = re.compile(r"\b(must|never|always|avoid|don't|do not|prefer|should|make sure|ensure|only)\b", re.I)
CONDITIONAL = re.compile(r"\b(if|when|unless|whenever|otherwise)\b", re.I)
RATIONALE = re.compile(r"\b(because|so that|since|otherwise|which means|why)\b", re.I)
COMMAND = re.compile(r"`[^`]*[/.$-][^`]*`")
IMPERATIVE_VERBS = {
    "aggregate", "capture", "clarify", "consider", "convert", "decide", "exclude", "expand", "focus",
    "generalize", "help", "identify", "install", "kill", "limit", "map", "package", "prompt", "provide",
    "rank", "repeat", "respond", "return", "scan", "select", "spawn", "specify", "store", "submit",
    "summarize", "trim", "wrap",
    "add", "apply", "ask", "avoid", "build", "call", "check", "choose", "collect", "compare", "confirm",
    "copy", "create", "cut", "decide", "define", "delete", "describe", "do", "don't", "draft", "ensure",
    "explain", "extract", "fetch", "fill", "find", "fix", "follow", "give", "grade", "include", "keep",
    "launch", "list", "load", "look", "make", "mark", "merge", "move", "name", "never", "note", "open",
    "pick", "pin", "place", "prefer", "present", "put", "read", "record", "remove", "replace", "report",
    "review", "rewrite", "run", "save", "say", "search", "set", "show", "skip", "split", "start", "state",
    "stop", "tell", "test", "treat", "try", "update", "use", "validate", "verify", "wait", "write",
}
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")


def flags_for(text: str) -> list[str]:
    flags = []
    lead = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", text.strip())   # list marker
    lead = re.sub(r"^\*\*[^*]+\*\*[:.]?\s*", "", lead) if re.match(r"^\*\*[^*]+\*\*[:.]\s", lead) else lead
    first = re.sub(r"^[*_`\[\]]+", "", lead).split(" ", 1)[0].lower().strip(":,.*")
    if first in IMPERATIVE_VERBS:
        flags.append("imperative")
    if EMPHATIC.search(text):
        flags.append("emphatic")
    if CONDITIONAL.search(text):
        flags.append("conditional")
    if RATIONALE.search(text):
        flags.append("rationale")
    if COMMAND.search(text):
        flags.append("command")
    if re.search(r"(^|\s)!`[^`]+`|^```!", text, re.M):
        flags.append("dynamic-cmd")  # runs in the shell if it ends up in a SKILL.md: strip or justify
    return flags


def split_frontmatter(lines: list[str]) -> tuple[list[str], int]:
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[1:i], i + 1
    return [], 0


def parse_file(path: Path, rel: str) -> list[dict]:
    lines = path.read_text(errors="replace").split("\n")
    units: list[dict] = []
    fm, start = split_frontmatter(lines)
    if fm:
        units.append({"file": rel, "start": 1, "end": start, "section": "(frontmatter)", "kind": "frontmatter",
                      "text": "\n".join(fm)})

    heads: list[tuple[int, str]] = []
    i = start
    n = len(lines)

    def section() -> str:
        return " > ".join(h for _, h in heads) or "(top)"

    def add(kind: str, s: int, e: int, text: str) -> None:
        text = text.strip("\n")
        if text.strip():
            units.append({"file": rel, "start": s + 1, "end": e + 1, "section": section(), "kind": kind, "text": text})

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = HEADING.match(line)
        if m:
            level = len(m.group(1))
            heads = [(lv, h) for lv, h in heads if lv < level] + [(level, m.group(2).strip())]
            i += 1
            continue

        m = FENCE.match(line)
        if m:
            marker, info = m.group(1), m.group(2).strip().lower()
            j = i + 1
            while j < n:
                mm = FENCE.match(lines[j])
                if mm and mm.group(1)[0] == marker[0] and len(mm.group(1)) >= len(marker) and not mm.group(2).strip():
                    break
                j += 1
            body = "\n".join(lines[i:j + 1])
            sec = section()
            if info.startswith(("bash", "sh", "shell", "zsh", "console", "powershell")):
                kind = "command"
            elif info.startswith(("markdown", "md")) or TEMPLATE_HEAD.search(sec):
                kind = "template"
            elif EXAMPLE_HEAD.search(sec):
                kind = "example"
            else:
                kind = "code"
            add(kind, i, min(j, n - 1), body)
            i = j + 1
            continue

        if line.lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            add("table", i, j - 1, "\n".join(lines[i:j]))
            i = j
            continue

        m = LIST_ITEM.match(line)
        if m and len(m.group(1)) == 0:
            numbered = m.group(2)[0].isdigit()
            j = i + 1
            # continuation: indented lines, or nested list items, until blank + non-indented or next top item
            while j < n:
                nxt = lines[j]
                if not nxt.strip():
                    # a blank line continues the item only if the next line is indented under it
                    if j + 1 < n and lines[j + 1].startswith((" ", "\t")):
                        j += 1
                        continue
                    break
                if LIST_ITEM.match(nxt) and not nxt.startswith((" ", "\t")):
                    break
                if HEADING.match(nxt) or (FENCE.match(nxt) and not nxt.startswith((" ", "\t"))):
                    break
                j += 1
            text = "\n".join(lines[i:j])
            sec = section()
            if numbered:
                kind = "step"
            elif GOTCHA_HEAD.search(sec):
                kind = "gotcha"
            elif "imperative" in flags_for(m.group(3)) or DIRECTIVE.search(m.group(3)):
                kind = "rule"
            elif EXAMPLE_HEAD.search(sec):
                kind = "example"
            else:
                kind = "point"
            add(kind, i, j - 1, text)
            i = j
            continue

        # paragraph
        j = i + 1
        while j < n and lines[j].strip() and not (HEADING.match(lines[j]) or FENCE.match(lines[j])
                                                  or LIST_ITEM.match(lines[j]) or lines[j].lstrip().startswith("|")):
            j += 1
        text = "\n".join(lines[i:j])
        sec = section()
        if GOTCHA_HEAD.search(sec) and DIRECTIVE.search(text):
            kind = "gotcha"
        elif EXAMPLE_HEAD.search(sec):
            kind = "example"
        elif DIRECTIVE.search(text) or "imperative" in flags_for(text) or re.match(r"^\*\*[^*]+\*\*[:.]", text.strip()):
            kind = "rule"
        else:
            kind = "prose"
        add(kind, i, j - 1, text)
        i = j
    return units


def collect_files(target: Path, include_refs: bool) -> tuple[Path, list[Path]]:
    if target.is_file():
        root = target.parent
        files = [target]
        if include_refs and target.name == "SKILL.md":
            files += sorted(p for p in root.rglob("*.md") if p != target and "evals" not in p.relative_to(root).parts
                            and ".repos" not in p.parts and not p.name.endswith(".provenance.json"))
        return root, files
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: no SKILL.md in {target}", file=sys.stderr)
        sys.exit(1)
    return collect_files(skill_md, include_refs)


def to_markdown(units: list[dict], source_label: str) -> str:
    out = [f"# Units: {source_label}", "",
           "| ID | Kind | From | Section | Summary | Flags | Verdict | Target | Notes |",
           "|---|---|---|---|---|---|---|---|---|"]
    for u in units:
        summary = re.sub(r"\s+", " ", u["text"]).strip()
        summary = summary[:110] + ("..." if len(summary) > 110 else "")
        summary = summary.replace("|", "\\|")
        sec = u["section"][-50:].replace("|", "\\|")
        out.append(f"| {u['id']} | {u['kind']} | {u['file']}:{u['start']}-{u['end']} | {sec} | {summary} | "
                   f"{','.join(u['flags'])} |  |  |  |")
    out += ["", "## Unit text", ""]
    for u in units:
        out += [f"### {u['id']} ({u['kind']}, {u['file']}:{u['start']}-{u['end']})", "", "````text", u["text"], "````", ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Split a skill's markdown into citable units for harvesting or coverage mapping.",
        epilog="Example: extract_units.py sources/anthropics__skills__skill-creator --source-id A --format md",
    )
    ap.add_argument("target", type=Path, help="Skill folder, SKILL.md, or any markdown file")
    ap.add_argument("--source-id", default="U", help="Prefix for unit IDs, one letter per source (default U)")
    ap.add_argument("--include-references", action="store_true", help="Also split the skill's other .md files")
    ap.add_argument("--format", choices=["json", "md"], default="json")
    ap.add_argument("--kinds", default="", help="Comma-separated kinds to keep, e.g. step,rule,gotcha")
    ap.add_argument("--min-words", type=int, default=3, help="Drop units shorter than this (default 3)")
    args = ap.parse_args()

    target = args.target.expanduser().resolve()
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)
    root, files = collect_files(target, args.include_references)
    kinds = {k.strip() for k in args.kinds.split(",") if k.strip()}

    units: list[dict] = []
    for f in files:
        units += parse_file(f, f.relative_to(root).as_posix())
    kept = []
    for u in units:
        u["words"] = len(u["text"].split())
        if u["kind"] != "frontmatter" and u["words"] < args.min_words:
            continue
        if kinds and u["kind"] not in kinds:
            continue
        u["flags"] = flags_for(u["text"]) if u["kind"] != "frontmatter" else []
        kept.append(u)
    for idx, u in enumerate(kept, start=1):
        u["id"] = f"{args.source_id}{idx}"
        # stable key order for readability
        kept[idx - 1] = {k: u[k] for k in ("id", "file", "start", "end", "section", "kind", "flags", "words", "text")}

    if args.format == "md":
        print(to_markdown(kept, str(target)))
    else:
        counts: dict[str, int] = {}
        for u in kept:
            counts[u["kind"]] = counts.get(u["kind"], 0) + 1
        print(json.dumps({"source": str(target), "source_id": args.source_id, "counts": counts, "units": kept},
                         indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
