#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""Lint a skill folder against the Agent Skills spec, client-specific rules, and authoring practice.

Usage:
  python3 validate_skill.py <skill-dir> [--target spec|claude-code|claude-upload] [--json] [--strict]

Targets are entries in the CLIENTS registry, not branches in the checks. Each entry says which
frontmatter fields the destination accepts, which body substitutions it expands, which names it
rejects, how strict it is, and what the checks should print about it. The check functions read
those fields and stay client-neutral: supporting another destination means adding an entry, not
editing the checks. Facts that are only true of one client (its extension fields, its listing cap,
its truncation behavior) live in that client's entry.

  spec           (default) The open Agent Skills spec (agentskills.io), read by any compatible
                 agent. Client-specific fields and syntax are warnings.
  claude-code    Claude Code skills: its extension fields are allowed.
  claude-upload  claude.ai uploads, the Claude Skills API, and package_skill.py: only the six
                 spec fields, and names can't contain "anthropic" or "claude".

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
from dataclasses import dataclass
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
# Authoring budget, not a client fact: what a body should stay under before a client may drop it.
BODY_TOKEN_BUDGET = 5000
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
TABLE_ROW_RE = re.compile(r"^\s*\|")
# Verbs that make a mention an instruction to open a file rather than a citation. Inflections
# and re- prefixes count ("reads", "following", "reusing"); the noun "user" does not.
DIRECTIVE_RE = re.compile(
    r"\b(?:re-?)?(?:"
    r"reads?|reader|reading|"
    r"follows?|followed|following|"
    r"us(?:e|es|ed|ing|eful|eless|able)|"
    r"runs?|running|"
    r"appl(?:y|ies|ied|ying)|"
    r"consults?|consulted|consulting|"
    r"opens?|opened|opening|"
    r"checks?|checked|checking"
    r")\b",
    re.I,
)


@dataclass(frozen=True)
class Substitution:
    """A body placeholder some clients expand and other clients leave as literal text."""

    token: str
    pattern: re.Pattern


@dataclass(frozen=True)
class FieldNote:
    """An info note about a client extension field. `value` gates it (None: any value)."""

    field: str
    code: str
    note: str
    value: str | None = None

    def matches(self, fm: dict) -> bool:
        return self.field in fm and (self.value is None or str(fm[self.field]).lower() == self.value)


@dataclass(frozen=True)
class Client:
    """One destination a skill is written for: the data every check below reads.

    Only set what actually differs between destinations; the defaults describe "no client
    extensions, spec-level strictness", which is what the open-spec target does.
    """

    label: str                     # human name, used in the messages the checks print
    summary: str                   # one line for --help
    extra_fields: tuple[str, ...] = ()          # accepted frontmatter fields beyond SPEC_FIELDS
    invocation_fields: tuple[str, ...] = ()     # fields that can hide the skill from the agent
    substitutions: tuple[str, ...] = ()         # Substitution.token values this client expands
    dynamic_cmd_severity: str = "warning"
    dynamic_cmd_note: str = ("some clients run it in the shell when the skill loads; elsewhere it stays "
                             "literal text, and a non-zero exit aborts the skill.")
    substitution_severity: str = "warning"
    reserved_name_words: tuple[str, ...] = ()  # name words this destination refuses
    reserved_name_note: str = ""
    reserved_folder_names: tuple[str, ...] = ()
    reserved_folder_note: str = ""
    unknown_field_severity: str = "warning"
    unknown_field_note: str = ""
    list_allowed_fields: bool = False           # print the accepted field list in the message
    missing_name_severity: str = "error"
    missing_name_note: str = ""                # what the client does instead of reading `name`
    name_dir_severity: str = "error"
    name_reserved_severity: str = "warning"
    description_cap: int = 0                    # chars of listing text the client shows
    description_cap_fields: tuple[str, ...] = ()
    description_cap_note: str = ""
    body_token_note: str = "Long skills can be truncated by clients."
    extension_notes: tuple[FieldNote, ...] = ()
    nested_skill_severity: str = "warning"
    nested_skill_note: str = "Packaged uploads accept exactly one; rename supporting docs."


# The registry. Spec-neutral baseline first, then one entry per real client destination.
CLIENTS: dict[str, Client] = {
    "spec": Client(
        label="the Agent Skills spec",
        summary="The open Agent Skills spec (agentskills.io), read by any compatible agent",
        unknown_field_note="Other agents ignore them and some upload targets reject them.",
        reserved_name_words=("anthropic", "claude"),
        reserved_name_note="claude.ai and the Claude API reject these names.",
    ),
    "claude-code": Client(
        label="Claude Code",
        summary="Claude Code skills; its extension fields are allowed",
        extra_fields=("when_to_use", "argument-hint", "arguments", "disable-model-invocation",
                      "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
                      "background", "hooks", "paths", "shell"),
        invocation_fields=("disable-model-invocation", "user-invocable"),
        substitutions=("$ARGUMENTS", "${CLAUDE_...}"),
        dynamic_cmd_severity="info",
        dynamic_cmd_note="Claude Code runs it in the shell when the skill loads; a non-zero exit "
                         "aborts the skill.",
        reserved_name_words=("anthropic", "claude"),
        reserved_name_note="claude.ai and the Claude API reject these names.",
        reserved_folder_names=("synced", "anthropic-skills"),
        reserved_folder_note="is reserved by Claude Code, which will not load it.",
        unknown_field_note="Claude Code silently ignores them; check spelling.",
        missing_name_severity="info",
        missing_name_note="Claude Code will use the folder name.",
        name_dir_severity="warning",
        description_cap=1536,
        description_cap_fields=("description", "when_to_use"),
        description_cap_note="Claude Code truncates at 1536 in the listing.",
        body_token_note="Claude Code keeps only the first 5000 tokens after compaction.",
        extension_notes=(
            FieldNote("hooks", "HOOKS",
                      "Skill registers hooks that keep running for the rest of the session."),
            FieldNote("context", "FORK",
                      "`context: fork` runs the body as a task in a subagent without conversation "
                      "history; make sure the body contains an explicit task.", value="fork"),
        ),
    ),
    "claude-upload": Client(
        label="claude.ai / the Claude API",
        summary="claude.ai uploads, the Claude Skills API, and package_skill.py",
        unknown_field_severity="error",
        unknown_field_note="Upload fails with a hard error.",
        list_allowed_fields=True,
        reserved_name_words=("anthropic", "claude"),
        reserved_name_note="claude.ai and the Claude API reject these names, and this target uploads there.",
        name_reserved_severity="error",
        nested_skill_severity="error",
    ),
}

# Substitutions any client may declare; a client expands the ones its entry lists.
KNOWN_SUBSTITUTIONS = (
    Substitution("$ARGUMENTS", re.compile(r"\$ARGUMENTS")),
    Substitution("${CLAUDE_...}", re.compile(r"\$\{CLAUDE_[A-Z_]+\}")),
)

# Which client owns which frontmatter extension, for messages that name the client behind a field.
EXTENSION_OWNERS: dict[str, list[str]] = {}
for _client in CLIENTS.values():
    for _field in _client.extra_fields:
        EXTENSION_OWNERS.setdefault(_field, []).append(_client.label)

# Extension notes from every entry, each paired with the client that declares it.
DECLARED_NOTES = tuple((c, n) for c in CLIENTS.values() for n in c.extension_notes)


def get_client(key: str) -> Client:
    """Look up a registry entry by --target key."""
    try:
        return CLIENTS[key]
    except KeyError:
        print(f"Error: unknown target {key!r}. Choose one of: {', '.join(CLIENTS)}.", file=sys.stderr)
        raise SystemExit(2)


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


def check_frontmatter(fm: dict, skill_dir: Path, client: Client, rep: Report) -> None:
    allowed = SPEC_FIELDS | set(client.extra_fields)
    unknown = sorted(set(fm) - allowed)
    if unknown:
        ext = [f for f in unknown if f in EXTENSION_OWNERS]
        owners = "/".join(sorted({o for f in ext for o in EXTENSION_OWNERS[f]}))
        if not ext:
            ext_note = ""
        elif len(ext) == 1:
            ext_note = f" ({ext[0]} is a {owners} extension)"
        else:
            ext_note = f" ({', '.join(ext)} are {owners} extensions)"
        rep.add(client.unknown_field_severity, "FM-UNKNOWN",
                f"Fields outside {client.label}: {', '.join(unknown)}"
                + ext_note
                + f". {client.unknown_field_note}"
                + (f" Allowed: {', '.join(sorted(SPEC_FIELDS))}." if client.list_allowed_fields else ""),
                "SKILL.md")

    # name
    name = fm.get("name")
    if name is None:
        msg = f"No `name`; {client.missing_name_note}" if client.missing_name_note else "Missing required `name`."
        rep.add(client.missing_name_severity, "NAME-MISSING", msg, "SKILL.md")
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
            rep.add(client.name_dir_severity, "NAME-DIR",
                    f"`name` '{n}' does not match folder name '{skill_dir.name}' (the spec requires a match).",
                    "SKILL.md")
        hit = [w for w in client.reserved_name_words if w in n]
        if hit:
            rep.add(client.name_reserved_severity, "NAME-RESERVED",
                    f"`name` '{n}' contains reserved word(s) ({', '.join(repr(w) for w in hit)}); "
                    f"{client.reserved_name_note}", "SKILL.md")
    if skill_dir.name.lower() in client.reserved_folder_names:
        rep.add("error", "DIR-RESERVED",
                f"Folder name '{skill_dir.name}' {client.reserved_folder_note}", "")

    # description
    desc = fm.get("description")
    dmi = str(fm.get("disable-model-invocation", "")).lower() in {"true", "yes", "on", "1"}
    if desc is None or (isinstance(desc, str) and not desc.strip()):
        if not (client.invocation_fields and dmi):
            rep.add("error", "DESC-MISSING",
                    "Missing `description`; the agent decides whether to load the skill from it.", "SKILL.md")
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
        if client.description_cap:
            cap_parts = {f: fm.get(f) for f in client.description_cap_fields}
            combined = sum(len(str(v)) for v in cap_parts.values() if v)
            if combined > client.description_cap:
                names = " + ".join(f"`{f}`" for f in client.description_cap_fields)
                rep.add("warning", "DESC-LISTING-CAP",
                        f"{names} is {combined} chars; {client.description_cap_note}", "SKILL.md")
        if dmi and len(d) > 300:
            rep.add("info", "DESC-USER-ONLY",
                    "Skill is user-invoked only, so the agent never sees the description; a one-line summary is enough.",
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
    # Client extension fields, reported from whichever registry entry declares them.
    for owner, note in DECLARED_NOTES:
        if note.matches(fm):
            elsewhere = "" if owner is client else f" Only {owner.label} acts on it."
            rep.add("info", note.code, note.note + elsewhere, "SKILL.md")


def check_body(body: str, body_start: int, skill_dir: Path, client: Client, rep: Report) -> None:
    lines = body.split("\n")
    n_lines = len(lines)
    words = len(body.split())
    approx_tokens = int(len(body) / 4)
    if n_lines > 500:
        rep.add("warning", "BODY-LINES",
                f"SKILL.md body is {n_lines} lines; keep it under 500 and move detail to reference files.", "SKILL.md")
    if approx_tokens > BODY_TOKEN_BUDGET:
        rep.add("warning", "BODY-TOKENS",
                f"SKILL.md body is ~{approx_tokens} tokens; aim under {BODY_TOKEN_BUDGET}. "
                f"{client.body_token_note}", "SKILL.md")

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
        rep.add(client.dynamic_cmd_severity, "DYNAMIC-CMD",
                f"Body contains !`command` dynamic context injection: {client.dynamic_cmd_note}", "SKILL.md")
    unsupported = [s for s in KNOWN_SUBSTITUTIONS
                   if s.pattern.search(body) and s.token not in client.substitutions]
    if unsupported:
        expanders = sorted({c.label for c in CLIENTS.values()
                            if any(s.token in c.substitutions for s in unsupported)})
        if len(expanders) == 1:
            who = f"which only {expanders[0]} expands"
        elif expanders:
            who = f"which {' / '.join(expanders)} expand"
        else:
            who = "which no client in the registry expands"
        rep.add(client.substitution_severity, "CLIENT-SUBST",
                f"Body uses client substitutions ({', '.join(s.token for s in unsupported)}), "
                f"{who}; elsewhere they stay literal.", "SKILL.md")

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


def check_doc_gating(annotated: list[tuple[int, str, bool]], rel_s: str, doc_name: str, rep: Report) -> None:
    """Warn when SKILL.md names a doc but never tells the agent to open it.

    Mentioning a file is not routing to it. ORPHAN-DOC only sees whether a doc is named at
    all, so a skill that indexes its reference docs in a catalog table at the bottom, or
    cites them in parentheses, passes that check while every agent that loads the skill
    reads the body and opens none of them. A name gates a doc when the line also carries a
    directive verb; a table row never gates, because a table is a list, not an instruction.
    A doc named only inside a fenced code block is not a mention at all.
    """
    first_mention = 0
    gated = False
    for n, line, fenced in annotated:
        if fenced or (rel_s not in line and doc_name not in line):
            continue
        if not first_mention:
            first_mention = n
        if not TABLE_ROW_RE.match(line) and DIRECTIVE_RE.search(line):
            gated = True
            break
    if first_mention and not gated:
        rep.add("warning", "REF-PASSIVE",
                f"{rel_s} is named in SKILL.md but never with an instruction to open it, so an agent will not "
                f'read it; add a "Read {rel_s} first." line at the phase that needs it.',
                f"SKILL.md:{first_mention}")


def check_files(skill_dir: Path, skill_md_text: str, client: Client, rep: Report) -> None:
    all_files = list(iter_skill_files(skill_dir))
    md_texts = {}
    for f in all_files:
        if f.suffix in {".md", ".py", ".sh", ".js", ".ts", ".html"}:
            try:
                md_texts[f] = f.read_text(errors="replace")
            except OSError:
                pass

    # Doc mentions are judged on how SKILL.md names them, so the scan is done once and shared.
    skill_md_lines = strip_fenced_code(skill_md_text)

    # Nested SKILL.md files (portable uploads accept exactly one)
    skill_mds = [f for f in all_files if f.name == "SKILL.md"
                 and not (f.relative_to(skill_dir).parts and f.relative_to(skill_dir).parts[0] == "evals")]
    if len(skill_mds) > 1:
        extras = [str(f.relative_to(skill_dir)) for f in skill_mds if f.parent != skill_dir]
        rep.add(client.nested_skill_severity, "NESTED-SKILL-MD",
                f"Extra SKILL.md files: {', '.join(extras)}. {client.nested_skill_note}", "")

    for f in all_files:
        rel = f.relative_to(skill_dir)
        rel_s = rel.as_posix()
        if len(rel.parts) == 1 and f.name in EXTRA_DOCS:
            rep.add("warning", "EXTRA-DOC",
                    f"{rel_s} is documentation for humans; skills should hold only what the agent needs.", rel_s)
        if f.name.lower() == "skill.md" and f.name != "SKILL.md" and f.parent == skill_dir:
            rep.add("error", "SKILL-MD-CASE", f"Found {f.name}; the file must be named exactly SKILL.md.", rel_s)

        # Orphans: reference docs not mentioned in SKILL.md, and mentioned but never gated
        if rel.parts[0] in RESOURCE_DIRS and f.suffix == ".md":
            if rel_s not in skill_md_text and f.name not in skill_md_text:
                rep.add("warning", "ORPHAN-DOC",
                        f"{rel_s} is never mentioned in SKILL.md, so the agent won't know when to read it.", rel_s)
            check_doc_gating(skill_md_lines, rel_s, f.name, rep)
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
    client = get_client(target)
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
                    f"Frontmatter is not valid YAML ({str(e).splitlines()[0]}).{hint} Some clients (e.g. Claude Code) "
                    "then load the skill with no description.", "SKILL.md")
            fm = {}
    if fm:
        check_frontmatter(fm, skill_dir, client, rep)
    check_body(body, body_start, skill_dir, client, rep)
    check_files(skill_dir, text, client, rep)
    return rep


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Lint a skill folder against the Agent Skills spec, client-specific rules, and authoring practice.",
        epilog="Example: python3 validate_skill.py skills/my-skill   (add --target claude-code for Claude Code-only skills)",
    )
    ap.add_argument("skill_dir", type=Path, help="Path to the skill folder (the one containing SKILL.md)")
    ap.add_argument("--target", choices=list(CLIENTS), default="spec", metavar="spec|claude-code|claude-upload",
                    help="; ".join(f"{k}: {c.summary}" for k, c in CLIENTS.items()))
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
