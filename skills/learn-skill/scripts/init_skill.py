#!/usr/bin/env python3
"""Scaffold a new skill folder with a SKILL.md skeleton and an empty evals file.

Usage:
  python3 init_skill.py <name> --path <parent-dir> [--resources scripts,references,assets]
                        [--target spec|claude-code|claude-upload] [--invocation model|user|model-only]
                        [--description TEXT] [--force]

--target picks an entry from the CLIENTS registry below, which says which name words and folder
names the destination reserves, how it spells invocation control, and what to say about it. The
scaffolding reads those fields; adding a destination means adding an entry, not new branches.
(validate_skill.py holds the matching registry of accepted frontmatter fields and substitutions.)

  spec           (default) the open Agent Skills spec: spec fields only, no invocation control
  claude-code    Claude Code: its extension fields and invocation-control fields are allowed
  claude-upload  claude.ai / the Claude API: spec fields only, no client extensions

The name is normalized to the spec format ("Plan Mode" -> "plan-mode"). The folder is
created at <parent-dir>/<name>/. Existing folders are left untouched unless --force is given,
in which case only missing files are added (nothing is overwritten).

Output: a JSON summary on stdout (created paths, next steps). Exit 0 on success, 1 on error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VALID_RESOURCES = ("scripts", "references", "assets")
# Words reserved for claude.ai and the Claude API, not a coupling to one client.
RESERVED_WORDS = ("anthropic", "claude")


@dataclass(frozen=True)
class Client:
    """One destination a scaffolded skill is written for."""

    label: str                                       # human name used in messages
    summary: str                                     # one line for --help
    reserved_words: tuple[str, ...] = RESERVED_WORDS
    reserved_word_note: str = "claude.ai and the Claude API reject names like that"
    reserved_folder_names: tuple[str, ...] = ()
    reserved_folder_note: str = ""
    invocation_fields: tuple[tuple[str, str], ...] = ()  # (--invocation mode, "key: value")
    invocation_note: str = "invocation-control fields are a Claude Code extension"


# The registry: the spec-neutral baseline first, then one entry per real client destination.
CLIENTS: dict[str, Client] = {
    "spec": Client(
        label="the Agent Skills spec",
        summary="the open Agent Skills spec (agentskills.io); spec fields only",
    ),
    "claude-code": Client(
        label="Claude Code",
        summary="Claude Code; its extension and invocation-control fields are allowed",
        reserved_folder_names=("synced", "anthropic-skills"),
        reserved_folder_note="is reserved by Claude Code",
        invocation_fields=(("user", "disable-model-invocation: true"),
                           ("model-only", "user-invocable: false")),
        invocation_note="invocation-control fields are a Claude Code extension",
    ),
    "claude-upload": Client(
        label="claude.ai / the Claude API",
        summary="claude.ai uploads and the Claude Skills API; spec fields only",
        reserved_word_note="claude.ai and the Claude API reject names like that, and this target uploads there",
        invocation_note="invocation-control fields are a Claude Code extension that upload does not accept",
    ),
}


def normalize_name(raw: str) -> str:
    name = raw.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def skeleton(name: str, description: str | None, invocation: str, client: Client, title: str) -> str:
    desc = description or (
        "TODO: What this skill does, in third person. Use when TODO: the situations and user "
        "phrasings that should load it, including ones that never name the domain."
    )
    fm = [f"name: {name}"]
    if ": " in desc or desc.startswith(("'", '"', "[", "{", ">", "|", "*", "&", "!", "%", "@", "`")):
        fm.append("description: " + json.dumps(desc))
    else:
        fm.append(f"description: {desc}")
    invocation_line = dict(client.invocation_fields).get(invocation)
    if invocation_line:
        fm.append(invocation_line)
    return (
        "---\n" + "\n".join(fm) + "\n---\n\n"
        f"# {title}\n\n"
        "TODO: One or two sentences: what this skill accomplishes and the approach it takes.\n\n"
        "## Workflow\n\n"
        "1. TODO: First step. Done when <checkable condition>.\n"
        "2. TODO: Next step.\n\n"
        "## Gotchas\n\n"
        "- TODO: Environment-specific facts that defy reasonable assumptions (from research and baseline runs).\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Scaffold a new skill folder (SKILL.md skeleton + evals/evals.json).",
        epilog="Example: python3 init_skill.py pdf-forms --path skills --resources scripts,references",
    )
    ap.add_argument("name", help="Skill name; normalized to lowercase-hyphen form")
    ap.add_argument("--path", required=True, type=Path, help="Parent directory to create the skill folder in")
    ap.add_argument("--resources", default="", help=f"Comma-separated subfolders to create: {', '.join(VALID_RESOURCES)}")
    ap.add_argument("--target", choices=list(CLIENTS), default="spec", metavar="spec|claude-code|claude-upload",
                    help="; ".join(f"{k}: {c.summary}" for k, c in CLIENTS.items()))
    ap.add_argument("--invocation", choices=["model", "user", "model-only"], default="model",
                    help="model (default): the agent and the user can invoke; user: only /name; model-only: hidden from / (claude-code target only)")
    ap.add_argument("--description", default=None, help="Initial description text (can be refined later)")
    ap.add_argument("--force", action="store_true", help="Add missing files to an existing folder; never overwrites")
    args = ap.parse_args()

    client = CLIENTS[args.target]
    name = normalize_name(args.name)
    errors = []
    if not name:
        errors.append(f"Name {args.name!r} has no usable characters; use letters, digits, and hyphens.")
    elif len(name) > 64:
        errors.append(f"Name {name!r} is {len(name)} chars; the maximum is 64.")
    if any(w in name for w in client.reserved_words):
        print(f"Warning: Name {name!r} contains {'/'.join(client.reserved_words)}; {client.reserved_word_note}.",
              file=sys.stderr)
    if name.lower() in client.reserved_folder_names:
        errors.append(f"Name {name!r} {client.reserved_folder_note}.")
    resources = [r.strip() for r in args.resources.split(",") if r.strip()]
    bad = [r for r in resources if r not in VALID_RESOURCES]
    if bad:
        errors.append(f"Unknown --resources value(s): {', '.join(bad)}. Valid: {', '.join(VALID_RESOURCES)}.")
    if args.invocation != "model" and args.invocation not in dict(client.invocation_fields):
        print(f"Warning: {client.invocation_note}; ignoring --invocation for the {args.target} target.",
              file=sys.stderr)
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    parent = args.path.expanduser().resolve()
    skill_dir = parent / name
    if skill_dir.exists() and not args.force:
        print(f"Error: {skill_dir} already exists. Use --force to add missing files without overwriting.",
              file=sys.stderr)
        sys.exit(1)

    created = []
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        # Keep the user's own casing for the heading ("PDF Form Filler"); otherwise title-case the slug
        title = args.name.strip() if args.name.strip() != name else name.replace("-", " ").title()
        skill_md.write_text(skeleton(name, args.description, args.invocation, client, title))
        created.append(str(skill_md))
    for r in resources:
        d = skill_dir / r
        if not d.exists():
            d.mkdir()
            created.append(str(d) + "/")
    evals = skill_dir / "evals" / "evals.json"
    if not evals.exists():
        evals.parent.mkdir(exist_ok=True)
        evals.write_text(json.dumps({"skill_name": name, "evals": []}, indent=2) + "\n")
        created.append(str(evals))

    if name != normalize_name(args.name) or name != args.name:
        print(f"Note: normalized name {args.name!r} -> {name!r}", file=sys.stderr)
    print(json.dumps({
        "skill_dir": str(skill_dir),
        "name": name,
        "created": created,
        "next_steps": [
            "Replace every TODO in SKILL.md (description first).",
            "Add prompts to evals/evals.json.",
            f"Validate: python3 {Path(__file__).resolve().parent / 'validate_skill.py'} {skill_dir} --target {args.target}",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
