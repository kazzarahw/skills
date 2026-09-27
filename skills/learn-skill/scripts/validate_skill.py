#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""Lint a skill folder against the Agent Skills spec, Claude Code rules, and authoring practice.

Usage:
  python3 validate_skill.py <skill-dir> [--target claude-code|portable] [--json] [--strict]

Targets:
  claude-code  Claude Code personal/project/plugin skills (all Claude Code frontmatter fields allowed).
  portable     claude.ai uploads, the Skills API, package_skill.py, and other agents
               (only the six spec fields; stricter name rules).

Severities: error (must fix), warning (probably wrong), info (worth a look).
Exit codes: 0 = no errors, 1 = errors (or warnings with --strict), 2 = bad invocation or missing PyYAML.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment dependent
    print(
        "Error: PyYAML is required. Install it with `pip install pyyaml`, or run this "
        "script with `uv run <path>/validate_skill.py ...` to have it installed automatically.",
        file=sys.stderr,
    )
    sys.exit(2)

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_CODE_FIELDS = SPEC_FIELDS | {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
    "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell",
}
RESOURCE_DIRS = ("references", "scripts", "assets", "agents", "examples", "templates")
EXTRA_DOCS = {"README.md", "CHANGELOG.md", "INSTALL.md", "INSTALLATION.md", "INSTALLATION_GUIDE.md",
              "QUICK_REFERENCE.md", "CONTRIBUTING.md"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
EMPHATIC_RE = re.compile(r"\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|REQUIRED)\b")
FIRST_SECOND_PERSON_RE = re.compile(r"\b(I can|I will|I'll|I help|you can|you should|your )", re.I)
WHEN_CLAUSE_RE = re.compile(r"\b(use (this|it|when|for|whenever)|when (the )?user|whenever|trigger|invoke)", re.I)
TIME_SENSITIVE_RE = re.compile(
    r"\b(as of (january|february|march|april|may|june|july|august|september|october|november|december|\d{4})"
    r"|(before|after|until|since) (january|february|march|april|may|june|july|august|september|october|november|december) \d{4})",
    re.I,
)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BACKTICK_PATH_RE = re.compile(r"`((?:\$\{CLAUDE_SKILL_DIR\}/)?(?:" + "|".join(RESOURCE_DIRS) + r"|eval-viewer)/[^`\s]+)`")
TOC_RE = re.compile(r"^#+\s*(contents|table of contents)\b", re.I | re.M)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
DYNAMIC_CMD_RE = re.compile(r"(^|\s)!`[^`]+`|^```!", re.M)
CC_SUBST_RE = re.compile(r"\$ARGUMENTS|\$\{CLAUDE_[A-Z_]+\}")


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, severity: str, code: str, message: str, where: str = "") -> None:
        self.items.append({"severity": severity, "code": code, "message": message, "where": where})

    def count(self, severity: str) -> int:
        return sum(1 for i in self.items if i["severity"] == severity)


def split_frontmatter(text: str) -> tuple[str | None, str, int]:
    """Return (frontmatter_text, body, body_start_line). frontmatter_text is None if absent."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2
    return None, text, 1


def strip_fenced_code(body: str) -> list[tuple[int, str, bool]]:
    """Yield (line_no_in_body starting at 1, line, in_fence)."""
    out = []
    fence = None
    for n, line in enumerate(body.split("\n"), start=1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker[0] * len(marker)
                out.append((n, line, True))
                continue
            if marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
                out.append((n, line, True))
                continue
        out.append((n, line, fence is not None))
    return out


def iter_skill_files(root: Path):
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            yield p


def check_frontmatter(fm: dict, skill_dir: Path, target: str, rep: Report) -> None:
    allowed = SPEC_FIELDS if target == "portable" else CLAUDE_CODE_FIELDS
    unknown = sorted(set(fm) - allowed)
    if unknown:
        if target == "portable":
            rep.add("error", "FM-UNKNOWN",
                    f"Fields not allowed for portable targets (upload fails with a hard error): {', '.join(unknown)}. "
                    f"Allowed: {', '.join(sorted(SPEC_FIELDS))}.", "SKILL.md")
        else:
            rep.add("warning", "FM-UNKNOWN",
                    f"Unknown fields (Claude Code silently ignores them; check spelling): {', '.join(unknown)}.",
                    "SKILL.md")

    # name
    name = fm.get("name")
    if name is None:
        if target == "portable":
            rep.add("error", "NAME-MISSING", "Missing required `name`.", "SKILL.md")
        else:
            rep.add("info", "NAME-MISSING", "No `name`; Claude Code will use the folder name.", "SKILL.md")
    elif not isinstance(name, str):
        rep.add("error", "NAME-TYPE", f"`name` must be a string, got {type(name).__name__}.", "SKILL.md")
    else:
        n = name.strip()
        if not NAME_RE.match(n):
            rep.add("error", "NAME-FORMAT",
                    f"`name` '{n}' must be lowercase letters, digits, and single hyphens, "
                    "not starting or ending with a hyphen.", "SKILL.md")
        if len(n) > 64:
            rep.add("error", "NAME-LENGTH", f"`name` is {len(n)} chars; maximum is 64.", "SKILL.md")
        if n != skill_dir.name:
            sev = "error" if target == "portable" else "warning"
            rep.add(sev, "NAME-DIR",
                    f"`name` '{n}' does not match folder name '{skill_dir.name}' (the spec requires a match).",
                    "SKILL.md")
        if re.search(r"anthropic|claude", n):
            sev = "error" if target == "portable" else "warning"
            rep.add(sev, "NAME-RESERVED",
                    f"`name` '{n}' contains a reserved word ('anthropic' or 'claude'), rejected by claude.ai and the API.",
                    "SKILL.md")
    if target == "claude-code" and skill_dir.name.lower() in {"synced", "anthropic-skills"}:
        rep.add("error", "DIR-RESERVED", f"Folder name '{skill_dir.name}' is reserved by Claude Code and won't load.", "")

    # description
    desc = fm.get("description")
    dmi = str(fm.get("disable-model-invocation", "")).lower() in {"true", "yes", "on", "1"}
    if desc is None or (isinstance(desc, str) and not desc.strip()):
        if target == "portable" or not dmi:
            rep.add("error", "DESC-MISSING",
                    "Missing `description`; Claude decides whether to load the skill from it.", "SKILL.md")
    elif not isinstance(desc, str):
        rep.add("error", "DESC-TYPE", f"`description` must be a string, got {type(desc).__name__}.", "SKILL.md")
    else:
        d = desc.strip()
        if len(d) > 1024:
            rep.add("error", "DESC-LENGTH", f"`description` is {len(d)} chars; maximum is 1024.", "SKILL.md")
        elif len(d) > 700 and not dmi:
            rep.add("info", "DESC-LONG",
                    f"`description` is {len(d)} chars; it is paid for on every turn. Aim for roughly 300-700.",
                    "SKILL.md")
        elif len(d) < 80 and not dmi:
            rep.add("warning", "DESC-SHORT",
                    f"`description` is only {len(d)} chars; it probably lacks trigger contexts.", "SKILL.md")
        if re.search(r"\bTODO\b", d):
            rep.add("warning", "TODO", "`description` still contains a TODO placeholder.", "SKILL.md")
        if "<" in d or ">" in d:
            rep.add("error", "DESC-BRACKETS",
                    "`description` contains angle brackets, which uploads reject (no XML tags).", "SKILL.md")
        if FIRST_SECOND_PERSON_RE.search(d):
            rep.add("warning", "DESC-PERSON",
                    "`description` uses first or second person; write in third person "
                    "('Processes X. Use when...').", "SKILL.md")
        if not dmi and not WHEN_CLAUSE_RE.search(d):
            rep.add("warning", "DESC-NO-WHEN",
                    "`description` has no apparent 'when to use' clause (e.g. 'Use when...').", "SKILL.md")
        if EMPHATIC_RE.search(d):
            rep.add("warning", "DESC-EMPHATIC",
                    "`description` uses emphatic words (MUST/ALWAYS/CRITICAL...), which make current "
                    "models over-trigger. Use calm phrasing.", "SKILL.md")
        wtu = fm.get("when_to_use")
        combined = len(d) + (len(str(wtu)) if wtu else 0)
        if target == "claude-code" and combined > 1536:
            rep.add("warning", "DESC-LISTING-CAP",
                    f"`description` + `when_to_use` is {combined} chars; Claude Code truncates at 1536 in the listing.",
                    "SKILL.md")
        if dmi and len(d) > 300:
            rep.add("info", "DESC-USER-ONLY",
                    "Skill is user-invoked only, so Claude never sees the description; a one-line summary is enough.",
                    "SKILL.md")

    comp = fm.get("compatibility")
    if comp is not None:
        if not isinstance(comp, str):
            rep.add("error", "COMPAT-TYPE", "`compatibility` must be a string.", "SKILL.md")
        elif len(comp) > 500:
            rep.add("error", "COMPAT-LENGTH", f"`compatibility` is {len(comp)} chars; maximum is 500.", "SKILL.md")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            rep.add("error", "META-TYPE", "`metadata` must be a map of string keys to string values.", "SKILL.md")
        else:
            bad = [k for k, v in meta.items() if not isinstance(v, str)]
            if bad:
                rep.add("warning", "META-VALUES",
                        f"`metadata` values should be strings (quote them): {', '.join(map(str, bad))}.", "SKILL.md")

    tools = fm.get("allowed-tools")
    if tools:
        tool_text = " ".join(tools) if isinstance(tools, list) else str(tools)
        if re.search(r"(^|[\s,])(\*|Bash|Bash\(\*\))([\s,]|$)", tool_text):
            rep.add("warning", "TOOLS-BROAD",
                    f"`allowed-tools` grants a very broad permission ({tool_text!r}); scope it to specific commands.",
                    "SKILL.md")
    if "hooks" in fm:
        rep.add("info", "HOOKS", "Skill registers hooks that keep running for the rest of the session.", "SKILL.md")
    if str(fm.get("context", "")).lower() == "fork":
        rep.add("info", "FORK",
                "`context: fork` runs the body as a task in a subagent without conversation history; "
                "make sure the body contains an explicit task.", "SKILL.md")


def check_body(body: str, body_start: int, skill_dir: Path, target: str, rep: Report) -> None:
    lines = body.split("\n")
    n_lines = len(lines)
    words = len(body.split())
    approx_tokens = int(len(body) / 4)
    if n_lines > 500:
        rep.add("warning", "BODY-LINES",
                f"SKILL.md body is {n_lines} lines; keep it under 500 and move detail to reference files.", "SKILL.md")
    if approx_tokens > 5000:
        rep.add("warning", "BODY-TOKENS",
                f"SKILL.md body is ~{approx_tokens} tokens; aim under 5000. Claude Code keeps only the first "
                "5000 tokens of a skill after compaction.", "SKILL.md")

    annotated = strip_fenced_code(body)
    emphatic_lines = [body_start + n - 1 for n, l, fenced in annotated if not fenced and EMPHATIC_RE.search(l)]
    if len(emphatic_lines) > 5:
        rep.add("warning", "BODY-EMPHATIC",
                f"{len(emphatic_lines)} lines use ALL-CAPS directives (MUST/NEVER/ALWAYS/CRITICAL...). Usually a "
                f"missing reason; explain the why instead. Lines: {', '.join(map(str, emphatic_lines[:10]))}"
                + (" ..." if len(emphatic_lines) > 10 else ""), "SKILL.md")

    for n, l, fenced in annotated:
        if fenced:
            continue
        if re.match(r"^#+\s*when to use( this skill)?\s*$", l.strip(), re.I):
            rep.add("info", "BODY-WHEN-SECTION",
                    "Body has a 'When to use' section; the body loads only after triggering, so trigger "
                    "conditions belong in the description.", f"SKILL.md:{body_start + n - 1}")
        if TIME_SENSITIVE_RE.search(l):
            rep.add("info", "TIME-SENSITIVE", f"Possibly time-sensitive wording: {l.strip()[:100]!r}",
                    f"SKILL.md:{body_start + n - 1}")
        if re.search(r"\b(scripts|references|assets)\\[\w.-]+", l):
            rep.add("warning", "BACKSLASH-PATH", "Use forward slashes in paths.", f"SKILL.md:{body_start + n - 1}")
        if re.search(r"\bTODO\b", l):
            rep.add("warning", "TODO", f"Leftover TODO: {l.strip()[:100]!r}", f"SKILL.md:{body_start + n - 1}")

    # Bare script invocation inside shell code blocks
    for n, l, fenced in annotated:
        if fenced and re.match(r"^\s*(\./)?scripts/[\w./-]+\.(sh|py|js|ts|rb)\b", l):
            rep.add("warning", "BARE-SCRIPT",
                    "Script invoked by bare path; call it through its interpreter (e.g. `python3 scripts/x.py`) "
                    "since packagers can strip executable bits.", f"SKILL.md:{body_start + n - 1}")

    if DYNAMIC_CMD_RE.search(body):
        sev = "warning" if target == "portable" else "info"
        rep.add(sev, "DYNAMIC-CMD",
                "Body contains !`command` dynamic context injection: it runs in the shell when the skill loads "
                "(Claude Code only; literal text elsewhere; a non-zero exit aborts the skill).", "SKILL.md")
    if target == "portable" and CC_SUBST_RE.search(body):
        rep.add("warning", "CC-SUBST",
                "Body uses Claude Code substitutions ($ARGUMENTS or ${CLAUDE_...}), which stay literal outside Claude Code.",
                "SKILL.md")

    # Links and path references
    check_references(body, body_start, skill_dir, "SKILL.md", rep, strict_links=True)

    rep.add("info", "STATS",
            f"Body: {n_lines} lines, {words} words, ~{approx_tokens} tokens.", "SKILL.md")


def check_references(text: str, start: int, skill_dir: Path, rel_name: str, rep: Report, strict_links: bool) -> None:
    base = skill_dir / Path(rel_name).parent
    annotated = strip_fenced_code(text)
    for n, line, fenced in annotated:
        where = f"{rel_name}:{start + n - 1}"
        if not fenced:
            for target in MD_LINK_RE.findall(line):
                if re.match(r"^(https?:|mailto:|#|<)", target) or "{" in target:
                    continue
                path = target.split("#")[0]
                if path and not (base / path).exists():
                    rep.add("error" if strict_links else "warning", "LINK-BROKEN",
                            f"Link target does not exist: {target}", where)
        if rel_name == "SKILL.md":
            for raw in BACKTICK_PATH_RE.findall(line):
                if any(ch in raw for ch in "<>*[]{") and not raw.startswith("${CLAUDE_SKILL_DIR}"):
                    continue
                path = raw.replace("${CLAUDE_SKILL_DIR}/", "")
                if any(ch in path for ch in "<>*[]"):
                    continue
                if not (skill_dir / path).exists():
                    rep.add("warning", "PATH-MISSING", f"Referenced path not found in the skill: {path}", where)


def check_files(skill_dir: Path, skill_md_text: str, target: str, rep: Report) -> None:
    all_files = list(iter_skill_files(skill_dir))
    md_texts = {}
    for f in all_files:
        if f.suffix in {".md", ".py", ".sh", ".js", ".ts", ".html"}:
            try:
                md_texts[f] = f.read_text(errors="replace")
            except OSError:
                pass

    # Nested SKILL.md files (portable uploads accept exactly one)
    skill_mds = [f for f in all_files if f.name == "SKILL.md"
                 and not (f.relative_to(skill_dir).parts and f.relative_to(skill_dir).parts[0] == "evals")]
    if len(skill_mds) > 1:
        extras = [str(f.relative_to(skill_dir)) for f in skill_mds if f.parent != skill_dir]
        sev = "error" if target == "portable" else "warning"
        rep.add(sev, "NESTED-SKILL-MD",
                f"Extra SKILL.md files: {', '.join(extras)}. Uploads accept exactly one; rename supporting docs.", "")

    for f in all_files:
        rel = f.relative_to(skill_dir)
        rel_s = rel.as_posix()
        if len(rel.parts) == 1 and f.name in EXTRA_DOCS:
            rep.add("warning", "EXTRA-DOC",
                    f"{rel_s} is documentation for humans; skills should hold only what the agent needs.", rel_s)
        if f.name.lower() == "skill.md" and f.name != "SKILL.md" and f.parent == skill_dir:
            rep.add("error", "SKILL-MD-CASE", f"Found {f.name}; the file must be named exactly SKILL.md.", rel_s)

        # Orphans: reference docs not mentioned in SKILL.md
        if rel.parts[0] in RESOURCE_DIRS and f.suffix == ".md":
            if rel_s not in skill_md_text and f.name not in skill_md_text:
                rep.add("warning", "ORPHAN-DOC",
                        f"{rel_s} is never mentioned in SKILL.md, so Claude won't know when to read it.", rel_s)
        elif rel.parts[0] in RESOURCE_DIRS and f.suffix != ".md" and f.name != "__init__.py":
            mentioned = rel_s in skill_md_text or f.name in skill_md_text or f.stem in skill_md_text or any(
                (f.name in t or f.stem in t) for p, t in md_texts.items() if p != f)
            if not mentioned:
                rep.add("info", "ORPHAN-FILE", f"{rel_s} is not referenced anywhere in the skill.", rel_s)

        # Reference docs: TOC and nesting
        if f.suffix == ".md" and f != skill_dir / "SKILL.md" and rel.parts[0] != "evals":
            text = md_texts.get(f, "")
            n_lines = text.count("\n") + 1
            if n_lines > 100 and not TOC_RE.search(text) and rel.parts[0] == "references":
                rep.add("warning", "REF-NO-TOC",
                        f"{rel_s} has {n_lines} lines but no table of contents; partial reads miss its scope.", rel_s)
            check_references(text, 1, skill_dir, rel_s, rep, strict_links=False)

        # Syntax checks without executing anything (bytecode goes to a temp dir,
        # so the skill folder is never written to)
        if f.suffix == ".py":
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    py_compile.compile(str(f), cfile=str(Path(tmp) / "check.pyc"), doraise=True)
            except py_compile.PyCompileError as e:
                rep.add("error", "PY-SYNTAX", f"Python syntax error: {e.msg.strip().splitlines()[-1]}", rel_s)
        elif f.suffix == ".sh":
            try:
                r = subprocess.run(["bash", "-n", str(f)], capture_output=True, text=True, timeout=20)
                if r.returncode != 0:
                    rep.add("error", "SH-SYNTAX", f"Shell syntax error: {r.stderr.strip()[:200]}", rel_s)
            except (OSError, subprocess.TimeoutExpired):
                pass

    if not (skill_dir / "evals" / "evals.json").exists():
        rep.add("info", "NO-EVALS", "No evals/evals.json; the skill has not been tested against a baseline.", "")


def validate(skill_dir: Path, target: str) -> Report:
    rep = Report()
    if not skill_dir.is_dir():
        rep.add("error", "NOT-DIR", f"{skill_dir} is not a directory.")
        return rep
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        alt = [p.name for p in skill_dir.iterdir() if p.name.lower() == "skill.md"]
        hint = f" Found {alt[0]}; rename it to SKILL.md." if alt else ""
        rep.add("error", "NO-SKILL-MD", "SKILL.md not found." + hint)
        return rep

    text = skill_md.read_text(errors="replace")
    fm_text, body, body_start = split_frontmatter(text)
    if fm_text is None:
        rep.add("error", "FM-MISSING",
                "No YAML frontmatter: SKILL.md must start with '---' on line 1 and close with '---'.", "SKILL.md:1")
        fm = {}
    else:
        try:
            fm = yaml.safe_load(fm_text) or {}
            if not isinstance(fm, dict):
                rep.add("error", "FM-TYPE", "Frontmatter must be a YAML mapping.", "SKILL.md")
                fm = {}
        except yaml.YAMLError as e:
            hint = ""
            if re.search(r"^\s*description:\s*[^'\">|].*:\s", fm_text, re.M):
                hint = " The description contains ': ' - quote the value or use a '>-' block scalar."
            rep.add("error", "FM-YAML",
                    f"Frontmatter is not valid YAML ({str(e).splitlines()[0]}).{hint} In Claude Code the skill "
                    "would load with no description.", "SKILL.md")
            fm = {}
    if fm:
        check_frontmatter(fm, skill_dir, target, rep)
    check_body(body, body_start, skill_dir, target, rep)
    check_files(skill_dir, text, target, rep)
    return rep


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Lint a skill folder against the Agent Skills spec, Claude Code rules, and authoring practice.",
        epilog="Example: python3 validate_skill.py ~/.claude/skills/my-skill --target claude-code",
    )
    ap.add_argument("skill_dir", type=Path, help="Path to the skill folder (the one containing SKILL.md)")
    ap.add_argument("--target", choices=["claude-code", "portable"], default="claude-code",
                    help="claude-code (default) or portable (claude.ai upload, API, other agents)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero on warnings too")
    ap.add_argument("--quiet", action="store_true", help="Hide info items in text output")
    args = ap.parse_args()

    skill_dir = args.skill_dir.expanduser().resolve()
    rep = validate(skill_dir, args.target)
    errors, warnings = rep.count("error"), rep.count("warning")

    if args.json:
        print(json.dumps({"skill_dir": str(skill_dir), "target": args.target, "errors": errors,
                          "warnings": warnings, "items": rep.items}, indent=2))
    else:
        order = {"error": 0, "warning": 1, "info": 2}
        print(f"Validating {skill_dir} (target: {args.target})")
        for item in sorted(rep.items, key=lambda i: order[i["severity"]]):
            if args.quiet and item["severity"] == "info":
                continue
            loc = f" [{item['where']}]" if item["where"] else ""
            print(f"  {item['severity'].upper():7} {item['code']}{loc}: {item['message']}")
        verdict = "FAIL" if errors or (args.strict and warnings) else "PASS"
        print(f"{verdict}: {errors} error(s), {warnings} warning(s)")

    sys.exit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
