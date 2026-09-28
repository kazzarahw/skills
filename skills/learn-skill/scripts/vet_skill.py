#!/usr/bin/env python3
"""Static red-flag scan of a skill before you reuse, install, or copy from it.

Usage:
  python3 vet_skill.py <skill-dir | file> [--json] [--min-severity low] [--fail-on high]

Scans every file for patterns associated with prompt injection, hidden text, secret and
environment access, outbound data transfer, remote code execution, persistence, writes to agent
memory or instruction files, destructive commands, broad tool grants, and client features that
run things without review (allowed-tools, and Claude Code's !`command` injection and hooks).

This is a high-recall first pass. It cannot judge intent: every finding needs a human or model
judgment (is it load-bearing for the skill's stated purpose?), and a clean scan does not prove a
skill is safe. Nothing is executed; files are only read.

Exit codes: 0 = scan completed (and nothing at or above --fail-on), 1 = findings at or above
--fail-on, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEVERITIES = ["info", "low", "medium", "high", "critical"]
RANK = {s: i for i, s in enumerate(SEVERITIES)}
CODE_EXT = {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".ps1", ".php", ".go", ".lua"}
COMPILED_EXT = {".exe", ".dll", ".so", ".dylib", ".bin", ".jar", ".pyc", ".class", ".wasm"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
MAX_BYTES = 1_000_000

# (id, severity, scope, pattern, message). scope: "any" = all text files, "code" = code files only,
# "md" = markdown only. Patterns are written so their own source text does not match them.
LINE_RULES = [
    # Instruction integrity
    ("PI-OVERRIDE", "high", "any",
     r"\b(ignore|disregard|forget)\s+(all\s+|any\s+)?(the\s+|your\s+)?(previous|prior|above|earlier|preceding|system)\s+"
     r"(instructions|prompts?|rules|messages|directions)",
     "Instruction-override language"),
    ("PI-IDENTITY", "medium", "any",
     r"\byou\s+are\s+now\s+(a|an|in)\b|\bnew\s+system\s+prompt\b|\bdeveloper\s+mode\s+(enabled|on)\b",
     "Attempts to redefine the agent's identity or mode"),
    ("PI-AUDIT", "critical", "any",
     r"\bthis\s+skill\s+is\s+(safe|trusted|verified|pre-?approved|harmless)\b"
     r"|\b(do\s+not|don't)\s+(flag|report|warn\s+about)\s+(this|these|it|any)\b"
     r"|\b(mark|classify|treat|rate)\s+(this|it)\s+as\s+(safe|benign|trusted|clean)\b"
     r"|\bif\s+you\s+are\s+(an?\s+)?(ai|llm|language\s+model|scanner|security\s+review|auditor|reviewer)\b",
     "Text aimed at a reviewer or scanner (audit manipulation)"),
    ("PI-SECRECY", "high", "any",
     r"\b(without|never|don't|do\s+not)\s+(telling|tell|informing|inform|notifying|notify|asking|ask|mentioning|mention)"
     r"\s+(it\s+to\s+)?(the\s+)?user\b",
     "Instructs the agent to hide actions from the user"),
    ("PI-COVERT", "low", "md",
     r"\b(secretly|covertly|surreptitiously)\b",
     "Covert-action wording"),
    ("PI-EXTRACT", "high", "any",
     r"\b(reveal|print|repeat|output|show|dump|leak)\s+(your\s+|the\s+)?(full\s+)?(system\s+prompt|hidden\s+instructions"
     r"|initial\s+instructions|developer\s+message)",
     "System-prompt extraction"),
    ("PI-EXFIL", "high", "any",
     r"\b(send|post|upload|transmit|forward|exfiltrate|report)\b.{0,80}(https?://|webhook|pastebin|requestbin|ngrok"
     r"|discord(app)?\.com/api/webhooks|hooks\.slack\.com)",
     "Instruction or code sending data to an external endpoint"),

    # Secrets and environment
    ("EX-SECRET-PATH", "high", "any",
     r"~/\.ssh\b|\.ssh/(id_|authorized_keys)|\bid_(rsa|ed25519|ecdsa)\b|~/\.aws\b|\.aws/credentials|\.config/gcloud"
     r"|\.npmrc\b|\.pypirc\b|\.netrc\b|\.docker/config\.json|\.kube/config|\.git-credentials|/etc/shadow"
     r"|login\.keychain|\.credentials\.json|\bwallet\.dat\b",
     "Reference to a credential or secret file"),
    ("EX-DOTENV", "low", "any",
     r"(open|read|cat|load|source)[^\n]{0,20}\.env\b",
     "Reads a .env file"),
    ("EX-ENV-BULK", "medium", "code",
     r"for\s+\w+(\s*,\s*\w+)?\s+in\s+os\.environ|dict\(os\.environ\)|os\.environ\.(copy|items)\(\)"
     r"|json\.dumps\(os\.environ|JSON\.stringify\(process\.env\)|Object\.(keys|entries|values)\(process\.env\)"
     r"|\bprintenv\b|^\s*env\s*(\||>)",
     "Bulk access to environment variables"),
    ("EX-NET-SEND", "medium", "any",
     r"\bcurl\s[^\n]*(\s-d\s|--data|\s-F\s|--form|\s-T\s|--upload-file|-X\s*POST)|\bwget\s[^\n]*--post-(data|file)"
     r"|requests\.(post|put|patch)\(|httpx\.(post|put|patch)\(|urlopen\([^)]*data=|method:\s*['\"](POST|PUT)"
     r"|axios\.(post|put|patch)\(|/dev/tcp/|\bnc\s+(-\w+\s+)*[\w.-]+\s+\d{2,5}\b",
     "Outbound data transfer"),

    # Remote code execution and supply chain
    ("SC-PIPE-SHELL", "critical", "any",
     r"\b(curl|wget)\s[^\n|]*\|\s*(sudo\s+)?(ba|z|da|k)?sh\b|\b(curl|wget)\s[^\n|]*\|\s*python[0-9.]*\b"
     r"|\biex\s*\(\s*(New-Object\s+Net\.WebClient|iwr|Invoke-WebRequest)|Invoke-Expression[^\n]*DownloadString",
     "Downloads and executes remote code"),
    ("SC-DECODE-EXEC", "critical", "any",
     r"base64\s+(-d|--decode)[^\n]*\|\s*(ba|z)?sh\b|exec\(\s*(base64|codecs|zlib|marshal)\.|exec\([^)\n]*b64decode"
     r"|eval\(\s*(atob|Buffer\.from)\(|(exec|eval)\(\s*(requests|urllib|httpx)\.",
     "Decodes or downloads content and executes it"),
    ("SC-DYN-EXEC", "medium", "code",
     r"\beval\(|\bexec\(|\bnew\s+Function\(|__import__\(|shell\s*=\s*True|\bos\.system\(|\bos\.popen\(|child_process",
     "Dynamic code or shell execution"),
    ("SC-REMOTE-INSTALL", "medium", "any",
     r"\bpip3?\s+install\s[^\n]*(git\+|https?://)|\bnpm\s+(i|install)\s[^\n]*https?://|\bgo\s+install\s[^\n]*@latest",
     "Installs a package from a URL or unpinned source"),

    # Persistence and memory
    ("PER-SCHEDULE", "high", "any",
     r"\bcrontab\s+-|/etc/cron|\bsystemctl\s+(--user\s+)?enable\b|\blaunchctl\s+(load|bootstrap)\b|/LaunchAgents/"
     r"|\bschtasks\b|CurrentVersion\\+Run\b",
     "Installs a scheduled task or startup item"),
    ("PER-SHELLRC", "high", "any",
     r"(>>|>|tee\s+-a)\s*[\"']?(~|\$HOME|/home/\w+|/Users/\w+)?/?[\w./-]*\.(bashrc|zshrc|profile|bash_profile|zprofile|zshenv)\b"
     r"|\.git/hooks/",
     "Modifies shell startup files or git hooks"),
    ("MEM-WRITE", "critical", "code",
     r"^(?=.*(CLAUDE\.md|AGENTS\.md|GEMINI\.md|copilot-instructions\.md|\.claude/settings|\.claude/(memory|projects)"
     r"|\.codex/(config|AGENTS)|MEMORY\.md|\.cursorrules|\.cursor/rules|\.windsurfrules|\.clinerules))"
     r"(?=.*(>>|\btee\b|write_text|writeFile|appendFile|\.write\(|open\(.*['\"][wa]\+?['\"]))",
     "Writes to agent memory or instruction files (persists after the skill is removed)"),
    ("MEM-INSTRUCT", "high", "md",
     r"\b(add|append|write|insert|save|copy)\s+(this|these|the\s+following|it|them)?\s*(line|rule|text|instructions?)?\s*"
     r"(to|into)\s+(your\s+|the\s+|the\s+user's\s+)?`?(CLAUDE\.md|AGENTS\.md|GEMINI\.md|copilot-instructions\.md|\.cursorrules|global\s+instructions|memory\s+files?"
     r"|settings\.json|config\.toml)",
     "Tells the agent to persist instructions into memory or settings"),

    # Destructive commands and permission bypass
    ("DAN-RM", "high", "any",
     r"\brm\s+-(?:[a-zA-Z]*r[a-zA-Z]*f|[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s+(?:/(?:\s|$|\*)|~/?(?:\s|$)|\$HOME/?(?:\s|$)|\*)",
     "Recursive forced delete of a broad path"),
    ("DAN-BYPASS", "high", "any",
     r"--dangerously-skip-permissions|\bbypassPermissions\b|dangerouslyDisableSandbox|--yolo\b|--no-sandbox\b",
     "Disables permission prompts or sandboxing"),
    ("DAN-SUDO", "medium", "any", r"\bsudo\s+\w", "Privilege escalation"),
    ("DAN-CHMOD", "medium", "any", r"\bchmod\s+(-R\s+)?(777|a\+w|\+s|u\+s)\b", "Unsafe permission change"),
    ("DAN-NO-VERIFY", "low", "any", r"\bgit\s+(commit|push)\s[^\n]*--no-verify\b", "Skips git hooks"),
]

ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\u180e]")
BIDI = re.compile("[\u202a-\u202e\u2066-\u2069]")
HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
COMMENT_INSTR = re.compile(r"\b(instruction|ignore|assistant|agent|ai|model|llm|claude|codex|gpt|gemini|execute|run|send"
                           r"|must|always|never|you)\b", re.I)
B64_BLOB = re.compile(r"[A-Za-z0-9+/]{200,}={0,2}")
DYNAMIC_CMD = re.compile(r"(^|\s)!`[^`]+`")
BROAD_TRIGGER = re.compile(
    r"\balways\s+use\b|\buse\s+(this|it)\s+for\s+(everything|all|any)\b|\bevery\s+(request|task|prompt|message|query)\b"
    r"|\bany\s+(request|task|question|prompt)\b", re.I)


def add(findings, rule_id, sev, file, line, evidence, message):
    findings.append({"id": rule_id, "severity": sev, "file": file, "line": line,
                     "evidence": evidence.strip()[:200], "message": message})


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan_frontmatter(text: str, rel: str, findings: list) -> None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return
    fm_lines = lines[1:end]
    fm = "\n".join(fm_lines)
    m = re.search(r"^allowed-tools:\s*(.*(?:\n\s+-.*)*)", fm, re.M)
    if m:
        tools = m.group(1).strip()
        ln = 1 + next(i for i, l in enumerate(fm_lines, start=1) if l.startswith("allowed-tools"))
        if re.search(r"(^|[\s,\[\"'-])(\*|Bash|Bash\(\*\)|Bash\(\s*\*\s*\))([\s,\]\"']|$)", tools):
            add(findings, "CC-TOOLS-BROAD", "high", rel, ln, f"allowed-tools: {tools}",
                "Pre-approves a very broad tool grant (runs without permission prompts, not gated by workspace trust)")
        else:
            add(findings, "CC-TOOLS", "info", rel, ln, f"allowed-tools: {tools}",
                "Pre-approved tools; check each is needed for the stated purpose")
    for key, sev, msg in (("hooks", "medium", "Registers hooks that run for the rest of the session"),
                          ("context", "info", "Runs in a forked subagent (check the agent type and tools)")):
        for i, l in enumerate(fm_lines, start=2):
            if re.match(rf"^{key}\s*:", l):
                if key == "context" and "fork" not in l:
                    continue
                add(findings, f"CC-{key.upper()}", sev, rel, i, l, msg)
    d = re.search(r"^description:\s*(.+(?:\n\s+.+)*)", fm, re.M)
    if d and BROAD_TRIGGER.search(d.group(1)):
        add(findings, "CT-BROAD-TRIGGER", "medium", rel, 2, d.group(1)[:200],
            "Description engineered to trigger on almost any request")
    n = re.search(r"^name:\s*(.+)$", fm, re.M)
    if n and re.search(r"official|anthropic|openai|claude|codex|gemini|google|microsoft|github", n.group(1), re.I):
        add(findings, "CT-IMPERSONATE", "low", rel, 2, n.group(0),
            "Name suggests an official or vendor origin; confirm the publisher")


def scan_text(text: str, rel: str, suffix: str, findings: list) -> None:
    is_code = suffix in CODE_EXT
    is_md = suffix in {".md", ".markdown", ".txt", ""}
    if rel.endswith("SKILL.md"):
        scan_frontmatter(text, rel, findings)
    for lineno, line in enumerate(text.split("\n"), start=1):
        for rule_id, sev, scope, pat, msg in COMPILED:
            if scope == "code" and not is_code:
                continue
            if scope == "md" and not is_md:
                continue
            m = pat.search(line)
            if m:
                add(findings, rule_id, sev, rel, lineno, line, msg)
        if ZERO_WIDTH.search(line) and not (lineno == 1 and line.startswith("\ufeff")):
            add(findings, "HID-ZERO-WIDTH", "high", rel, lineno, repr(line[:120]),
                "Zero-width characters (can hide text or spoof names)")
        if BIDI.search(line):
            add(findings, "HID-BIDI", "high", rel, lineno, repr(line[:120]),
                "Bidirectional override characters (can make text read differently than it executes)")
        if B64_BLOB.search(line) and not line.strip().startswith(("data:", "src=", "\"data:")) and "base64," not in line:
            add(findings, "HID-BLOB", "medium", rel, lineno, line[:120], "Long encoded blob")
        if suffix in {".md", ".markdown"} and (DYNAMIC_CMD.search(line) or line.strip().startswith("```!")):
            # Injection only executes in SKILL.md and command files; elsewhere it is a mention,
            # which matters only if someone moves the line into SKILL.md.
            live = rel.endswith("SKILL.md") or "/commands/" in f"/{rel}"
            add(findings, "CC-DYNAMIC-CMD", "medium" if live else "info", rel, lineno, line,
                "Dynamic context injection: runs in the shell when the skill loads, before anyone reads it"
                if live else "Dynamic-injection syntax outside SKILL.md (inert here; dangerous if moved into SKILL.md)")
    # HTML comments hide text only where markdown or HTML is rendered
    for m in (HTML_COMMENT.finditer(text) if suffix in {".md", ".markdown", ".html", ".htm", ".txt", ""} else ()):
        body = m.group(1)
        if COMMENT_INSTR.search(body) and len(body.strip()) > 20:
            add(findings, "HID-COMMENT", "high", rel, line_of(text, m.start()), body[:200],
                "HTML comment containing instruction-like text (invisible when rendered)")


def scan(target: Path) -> tuple[list, list]:
    findings: list = []
    scanned: list = []
    root = target if target.is_dir() else target.parent
    files = [target] if target.is_file() else sorted(p for p in target.rglob("*")
                                                      if not any(x in SKIP_DIRS for x in p.relative_to(target).parts))
    for p in files:
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            add(findings, "FILE-SYMLINK", "high", rel, 0, f"-> {p.readlink() if hasattr(p, 'readlink') else '?'}",
                "Symlink (can point outside the skill, e.g. at credentials)")
            continue
        if not p.is_file():
            continue
        if p.suffix.lower() in COMPILED_EXT:
            add(findings, "FILE-COMPILED", "medium", rel, 0, p.name, "Compiled or binary executable (cannot be reviewed)")
            continue
        size = p.stat().st_size
        if size > MAX_BYTES:
            add(findings, "FILE-LARGE", "info", rel, 0, f"{size} bytes", "Large file not scanned")
            continue
        raw = p.read_bytes()
        if raw == SELF_BYTES:
            # A byte-identical copy of this scanner: its rule table matches its own patterns.
            add(findings, "SELF", "info", rel, 0, p.name, "Copy of this scanner; its signature table was not scanned")
            continue
        if b"\x00" in raw[:8192]:
            add(findings, "FILE-BINARY", "info", rel, 0, p.name, "Binary file not scanned")
            continue
        text = raw.decode("utf-8", errors="replace")
        scanned.append(rel)
        if p.name.startswith(".") and p.name not in {".gitignore", ".gitattributes"}:
            sev = "medium" if re.search(r"^\s*[A-Z_]{3,}\s*=\s*\S", text, re.M) else "low"
            add(findings, "FILE-HIDDEN", sev, rel, 0, p.name, "Hidden file" + (" with KEY=value content" if sev == "medium" else ""))
        scan_text(text, rel, p.suffix.lower(), findings)
    return findings, scanned


COMPILED = [(rid, sev, scope, re.compile(pat, re.I if rid.startswith(("PI", "MEM-INSTRUCT")) else 0), msg)
            for rid, sev, scope, pat, msg in LINE_RULES]
SELF_BYTES = Path(__file__).resolve().read_bytes()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Static red-flag scan of a skill before reuse. Reads files only; executes nothing.",
        epilog="Example: python3 vet_skill.py ws/sources/owner__repo__my-skill --json",
    )
    ap.add_argument("target", type=Path, help="Skill folder or single file")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="info", help="Hide findings below this severity")
    ap.add_argument("--fail-on", choices=SEVERITIES, default=None,
                    help="Exit 1 if any finding is at or above this severity")
    args = ap.parse_args()

    target = args.target.expanduser().resolve()
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(2)

    findings, scanned = scan(target)
    findings = [f for f in findings if RANK[f["severity"]] >= RANK[args.min_severity]]
    findings.sort(key=lambda f: (-RANK[f["severity"]], f["file"], f["line"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in reversed(SEVERITIES)}
    top = next((s for s in reversed(SEVERITIES) if counts[s]), "none")
    advice = {
        "critical": "Do not reuse unless every critical finding is explained by the skill's stated purpose.",
        "high": "Review each high finding against the stated purpose (contract check) before reuse.",
        "medium": "Review flagged lines; most medium findings are benign in skills that clearly need them.",
        "low": "Minor flags only. Still read SKILL.md and every script before reuse.",
        "info": "No risky patterns found. Still read SKILL.md and every script before reuse.",
        "none": "No findings. A clean scan is not proof of safety: read SKILL.md and every script.",
    }[top]

    if args.json:
        print(json.dumps({"target": str(target), "files_scanned": len(scanned), "max_severity": top,
                          "counts": counts, "advice": advice, "findings": findings}, indent=2, ensure_ascii=False))
    else:
        print(f"Vetting {target} ({len(scanned)} text files scanned)")
        for f in findings:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
            print(f"  {f['severity'].upper():8} {f['id']:18} {loc}\n           {f['message']}\n           > {f['evidence']}")
        summary = ", ".join(f"{v} {k}" for k, v in counts.items() if v) or "no findings"
        print(f"Max severity: {top} ({summary})\n{advice}")

    if args.fail_on and top != "none" and RANK[top] >= RANK[args.fail_on]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
