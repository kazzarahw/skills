#!/usr/bin/env python3
"""Copy third-party skills into a workspace for reading, vetting, or harvesting, without installing them.

Usage:
  python3 fetch_skill.py <source> --dest <dir> [--skill NAME ...] [--list] [--ref REF] [--refresh]

<source> forms:
  owner/repo                       GitHub shorthand (all skills, or filter with --skill)
  owner/repo@skill                 one skill from a GitHub repo
  https://github.com/o/r[/tree/<ref>/<path>]
  https://skills.sh/<owner>/<repo>/<skill>
  any git URL (https://.../*.git, git@host:o/r.git, GitLab, Azure Repos)
  https://.../SKILL.md             a single raw SKILL.md file
  ./local/path                     a skill folder, a SKILL.md, or a folder containing skills

What it does: shallow-clones git sources into <dest>/.repos/ (reused on later calls unless
--refresh), finds folders containing SKILL.md, and copies each selected skill to
<dest>/<source-slug>__<skill-name>/. Beside each copy it writes <copy>.provenance.json
(source, ref, commit, license). Symlinks are never followed or copied; they are listed as
warnings. Nothing fetched is executed, and nothing is installed into any agent.

Output: JSON on stdout. Exit codes: 0 ok, 1 bad source or nothing matched, 2 git/network failure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import NoReturn

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".repos"}
MAX_DEPTH = 8
RAW_MAX_BYTES = 1_000_000
GIT_TIMEOUT_S = 300  # large repos over slow links; shallow clones of typical skill repos take seconds
LICENSE_NAMES = ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENCE.txt", "COPYING", "COPYING.txt")
LICENSE_PATTERNS = [
    ("Apache-2.0", r"Apache License,?\s+Version 2\.0"),
    ("MIT", r"\bMIT License\b|Permission is hereby granted, free of charge"),
    ("BSD", r"Redistribution and use in source and binary forms"),
    ("ISC", r"\bISC License\b"),
    ("GPL", r"GNU GENERAL PUBLIC LICENSE"),
    ("LGPL", r"GNU LESSER GENERAL PUBLIC LICENSE"),
    ("MPL-2.0", r"Mozilla Public License,?\s+(Version|v\.)\s*2\.0"),
    ("CC", r"Creative Commons"),
    ("Unlicense", r"This is free and unencumbered software released into the public domain"),
]


def fail(msg: str, code: int = 1) -> NoReturn:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_frontmatter(text: str) -> dict:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}
    fm_text = "\n".join(lines[1:end])
    try:
        import yaml  # optional
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}
    except Exception:
        out = {}
        for key in ("name", "description", "license"):
            m = re.search(rf"^{key}:\s*(.+)$", fm_text, re.M)
            if m:
                out[key] = m.group(1).strip().strip("'\"")
        return out


def classify_license(text: str) -> str:
    for label, pat in LICENSE_PATTERNS:
        if re.search(pat, text, re.I):
            return label
    return "unrecognized"


def find_license(skill_dir: Path, repo_root: Path | None) -> dict:
    for base, scope in ((skill_dir, "skill"), (repo_root, "repo")):
        if base is None:
            continue
        for n in LICENSE_NAMES:
            p = base / n
            if p.is_file() and not p.is_symlink():
                text = p.read_text(errors="replace")[:20000]
                return {"file": n, "scope": scope, "detected": classify_license(text)}
    return {"file": None, "scope": None, "detected": "none found (all rights reserved by default)"}


def discover(root: Path) -> list[Path]:
    """Return skill folders (containing SKILL.md) under root, shallowest first."""
    found = []
    root_depth = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        d = Path(dirpath)
        dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS and not (d / x).is_symlink()]
        if len(d.parts) - root_depth > MAX_DEPTH:
            dirnames[:] = []
            continue
        if "SKILL.md" in filenames:
            found.append(d)
    found.sort(key=lambda p: (len(p.parts), str(p)))
    # A skill folder shadows SKILL.md files nested inside it (examples, test fixtures)
    kept: list[Path] = []
    for p in found:
        if not any(k in p.parents for k in kept):
            kept.append(p)
    return kept


def copy_skill(src: Path, dst: Path) -> list[str]:
    """Copy a skill folder without following or copying symlinks. Returns skipped symlink paths."""
    skipped = []
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        d = Path(dirpath)
        rel = d.relative_to(src)
        keep = []
        for x in dirnames:
            if x in SKIP_DIRS:
                continue
            if (d / x).is_symlink():
                skipped.append(str(rel / x))
                continue
            keep.append(x)
        dirnames[:] = keep
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for f in filenames:
            p = d / f
            if p.is_symlink():
                skipped.append(str(rel / f))
                continue
            shutil.copy2(p, dst / rel / f)
    return skipped


def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=GIT_TIMEOUT_S)


def clone(url: str, ref: str | None, dest: Path, refresh: bool) -> tuple[Path, str]:
    if shutil.which("git") is None:
        fail("git is not installed; install git or fetch the files another way.", 2)
    if dest.exists() and refresh:
        shutil.rmtree(dest)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        args = ["clone", "--depth", "1", "--single-branch", "--no-tags"]
        if ref:
            args += ["--branch", ref]
        r = run_git(args + [url, str(dest)])
        if r.returncode != 0 and ref:
            # ref may be a commit SHA, which --branch does not accept
            shutil.rmtree(dest, ignore_errors=True)
            r = run_git(["clone", "--depth", "1", "--no-tags", url, str(dest)])
            if r.returncode == 0:
                f = run_git(["fetch", "--depth", "1", "origin", ref], cwd=dest)
                c = run_git(["checkout", "--quiet", "FETCH_HEAD"], cwd=dest) if f.returncode == 0 else f
                if c.returncode != 0:
                    fail(f"could not check out ref {ref!r}: {c.stderr.strip()[:300]}", 2)
        if r.returncode != 0:
            shutil.rmtree(dest, ignore_errors=True)
            fail(f"git clone failed for {url}: {r.stderr.strip()[:400]}\n"
                 "Private repos need git credentials already configured (the clone never prompts).", 2)
    sha = run_git(["rev-parse", "HEAD"], cwd=dest).stdout.strip()
    return dest, sha


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "source"


def parse_source(source: str) -> dict:
    p = Path(source).expanduser()
    if p.exists():
        return {"kind": "local", "path": p.resolve(), "slug": "local"}

    m = re.match(r"^https?://(www\.)?skills\.sh/([^/]+)/([^/]+)/([^/?#]+)", source)
    if m:
        owner, repo, skill = m.group(2), m.group(3), m.group(4)
        if "." in owner and "/" not in owner:
            fail(f"{source} is published from a domain ({owner}), not a GitHub repo; "
                 "open the page to find its repository URL.")
        return {"kind": "git", "url": f"https://github.com/{owner}/{repo}.git", "ref": None, "subpath": None,
                "skill": skill, "slug": f"{owner}__{repo}"}

    m = re.match(r"^https?://github\.com/([^/]+)/([^/#?]+?)(?:\.git)?(?:/(tree|blob)/([^/]+)(?:/(.*))?)?/?$", source)
    if m:
        owner, repo, _, ref, sub = m.groups()
        if sub and sub.endswith("SKILL.md"):
            sub = sub[: -len("SKILL.md")].rstrip("/")
        return {"kind": "git", "url": f"https://github.com/{owner}/{repo}.git", "ref": ref, "subpath": sub or None,
                "skill": None, "slug": f"{owner}__{repo}"}

    if re.match(r"^https?://.*SKILL\.md(\?.*)?$", source) or "raw.githubusercontent.com" in source:
        return {"kind": "raw", "url": source, "slug": slugify(urllib.parse.urlparse(source).netloc)}

    if re.match(r"^(https?://|git@|ssh://)", source):
        tail = re.sub(r"\.git$", "", source.rstrip("/")).split("/")[-2:]
        return {"kind": "git", "url": source, "ref": None, "subpath": None, "skill": None,
                "slug": slugify("__".join(tail))}

    m = re.match(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:@(.+))?$", source)
    if m:
        owner, repo, skill = m.groups()
        return {"kind": "git", "url": f"https://github.com/{owner}/{repo}.git", "ref": None, "subpath": None,
                "skill": skill, "slug": f"{owner}__{repo}"}

    fail(f"Unrecognized source {source!r}. Use owner/repo[@skill], a GitHub/skills.sh/git URL, "
         "a raw SKILL.md URL, or a local path.")


def fetch_raw(url: str, dest_root: Path, slug: str, refresh: bool) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "learn-skill-fetch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read(RAW_MAX_BYTES + 1)
    except Exception as e:  # network errors vary widely
        fail(f"download failed for {url}: {e}", 2)
    if len(data) > RAW_MAX_BYTES:
        fail(f"{url} is larger than {RAW_MAX_BYTES} bytes; refusing to treat it as a SKILL.md.")
    text = data.decode("utf-8", errors="replace")
    fm = parse_frontmatter(text)
    name = slugify(str(fm.get("name") or "skill"))
    out = dest_root / f"{slug}__{name}"
    if out.exists() and not refresh:
        return {"name": name, "path": str(out), "status": "already fetched (use --refresh to replace)"}
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "SKILL.md").write_text(text)
    prov = {"source": url, "kind": "raw", "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "license": {"frontmatter": fm.get("license"), "detected": "unknown (single file; check the source)"},
            "name": fm.get("name"), "skipped_symlinks": []}
    Path(str(out) + ".provenance.json").write_text(json.dumps(prov, indent=2))
    return {"name": name, "path": str(out), "description": str(fm.get("description", ""))[:200],
            "license": prov["license"], "status": "fetched"}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Copy third-party skills into a workspace without installing or executing them.",
        epilog="Examples:\n  fetch_skill.py anthropics/skills@skill-creator --dest ws/sources\n"
               "  fetch_skill.py openai/skills --dest ws/sources --list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("source", help="owner/repo[@skill], GitHub/skills.sh/git URL, raw SKILL.md URL, or local path")
    ap.add_argument("--dest", required=True, type=Path, help="Destination folder, e.g. <workspace>/sources")
    ap.add_argument("--skill", action="append", default=[], help="Only these skills (frontmatter or folder name); repeatable")
    ap.add_argument("--list", action="store_true", help="List the skills found and copy nothing")
    ap.add_argument("--ref", default=None, help="Branch, tag, or commit to fetch (default: the default branch)")
    ap.add_argument("--refresh", action="store_true", help="Re-clone and replace earlier copies")
    args = ap.parse_args()

    dest_root = args.dest.expanduser().resolve()
    src = parse_source(args.source)

    if src["kind"] == "raw":
        if args.list:
            fail("--list needs a repository or folder, not a single file.")
        dest_root.mkdir(parents=True, exist_ok=True)
        print(json.dumps({"fetched": [fetch_raw(src["url"], dest_root, src["slug"], args.refresh)]}, indent=2))
        return

    repo_root: Path | None = None
    commit = None
    if src["kind"] == "git":
        repo_root, commit = clone(src["url"], args.ref or src["ref"], dest_root / ".repos" / src["slug"], args.refresh)
        search_root = repo_root / src["subpath"] if src.get("subpath") else repo_root
        if not search_root.exists():
            fail(f"path {src['subpath']!r} not found in {src['url']}")
    else:
        path = src["path"]
        search_root = path.parent if path.is_file() else path
        repo_root = None

    skills = discover(search_root)
    if (search_root / "SKILL.md").exists():
        skills = [search_root]  # the source points at one skill: don't pick up nested ones
    if not skills:
        fail(f"No SKILL.md found under {search_root}.")

    wanted = [s.lower() for s in args.skill + ([src["skill"]] if src.get("skill") else [])]
    entries = []
    for d in skills:
        fm = parse_frontmatter((d / "SKILL.md").read_text(errors="replace"))
        name = str(fm.get("name") or d.name)
        if wanted and name.lower() not in wanted and d.name.lower() not in wanted:
            continue
        entries.append((d, fm, name))

    if not entries:
        names = sorted({str(parse_frontmatter((d / 'SKILL.md').read_text(errors='replace')).get('name') or d.name)
                        for d in skills})
        fail(f"No skill matched {', '.join(wanted)}. Available: {', '.join(names)}")

    if args.list:
        base = repo_root or search_root
        print(json.dumps({"source": args.source, "commit": commit, "skills": [
            {"name": n, "path": str(d.relative_to(base)) if base in d.parents or d == base else str(d),
             "description": str(fm.get("description", ""))[:200]} for d, fm, n in entries]}, indent=2))
        return

    dest_root.mkdir(parents=True, exist_ok=True)
    results = []
    for d, fm, name in entries:
        out = dest_root / f"{src['slug']}__{slugify(name)}"
        if out.exists() and not args.refresh:
            results.append({"name": name, "path": str(out), "status": "already fetched (use --refresh to replace)"})
            continue
        if out.exists():
            shutil.rmtree(out)
        skipped = copy_skill(d, out)
        lic = find_license(d, repo_root)
        prov = {
            "source": args.source,
            "kind": src["kind"],
            "url": src.get("url"),
            "ref": args.ref or src.get("ref"),
            "commit": commit,
            "path_in_source": str(d.relative_to(repo_root)) if repo_root else str(d),
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "name": fm.get("name"),
            "license": {"frontmatter": fm.get("license"), **lic},
            "skipped_symlinks": skipped,
        }
        Path(str(out) + ".provenance.json").write_text(json.dumps(prov, indent=2))
        results.append({"name": name, "path": str(out), "description": str(fm.get("description", ""))[:200],
                        "license": prov["license"], "skipped_symlinks": skipped, "status": "fetched"})

    print(json.dumps({"source": args.source, "commit": commit, "fetched": results,
                      "next": "Vet each copy before reading it for content: vet_skill.py <path>"}, indent=2))


if __name__ == "__main__":
    main()
