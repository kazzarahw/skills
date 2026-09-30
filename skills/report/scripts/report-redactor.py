#!/usr/bin/env python3
"""
Report Redactor
Redacts sensitive data from security reports.

Supports:
- Passwords and credentials
- API tokens and keys
- PII (Personally Identifiable Information)
- Cryptocurrency addresses
- Private keys
- Custom patterns

Usage:
    python report-redactor.py --input report.md --output report_redacted.md
    python report-redactor.py --input report.md --output report_redacted.md --patterns passwords,tokens,pii
    python report-redactor.py --input report.md --output report_redacted.md --custom-pattern "secret.*"
    python report-redactor.py --input report.md --output report_redacted.md --report redaction_report.md
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class RedactionMatch:
    """Represents a redaction match."""
    pattern_name: str
    line_number: int
    original: str
    redacted: str
    position: int


@dataclass
class RedactionReport:
    """Represents a redaction report."""
    input_file: str
    output_file: str
    timestamp: str
    total_redactions: int = 0
    matches: list = field(default_factory=list)
    patterns_used: list = field(default_factory=list)


# Redaction patterns
REDACTION_PATTERNS = {
    "passwords": [
        # password=..., password: ..., "password": "..."
        (r'(?i)(password\s*[=:]\s*["\']?)([^\s"\'&;]+)', r'\1[REDACTED]'),
        # passwd=..., pwd=...
        (r'(?i)(passwd|pwd)\s*[=:]\s*([^\s&;]+)', r'\1=[REDACTED]'),
        # --password=...
        (r'(?i)(--password[=\s]+)([^\s&;]+)', r'\1[REDACTED]'),
    ],
    "tokens": [
        # API tokens (generic)
        (r'(?i)(api[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9_\-]{16,})', r'\1[REDACTED]'),
        # Bearer tokens
        (r'(?i)(bearer\s+)([a-zA-Z0-9_\-\.]+)', r'\1[REDACTED]'),
        # JWT tokens
        (r'(eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+)', '[REDACTED]'),
        # GitHub tokens
        (r'(ghp_[a-zA-Z0-9]{36})', '[REDACTED]'),
        # Slack tokens
        (r'(xox[baprs]-[a-zA-Z0-9\-]+)', '[REDACTED]'),
    ],
    "credentials": [
        # Private keys
        (r'(-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----)', '[REDACTED]'),
        # AWS access keys
        (r'(AKIA[0-9A-Z]{16})', '[REDACTED]'),
        # AWS secret keys
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9/+=]{40})', r'\1[REDACTED]'),
        # Generic secrets
        (r'(?i)(secret[_-]?key\s*[=:]\s*["\']?)([a-zA-Z0-9_\-]{16,})', r'\1[REDACTED]'),
    ],
    "pii": [
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[REDACTED_EMAIL]'),
        # Phone numbers (US format)
        (r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', '[REDACTED_PHONE]'),
        # SSN
        (r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b', '[REDACTED_SSN]'),
        # Credit card numbers
        (r'\b(?:[0-9]{4}[- ]?){3}[0-9]{4}\b', '[REDACTED_CC]'),
    ],
    "addresses": [
        # Ethereum addresses
        (r'\b0x[a-fA-F0-9]{40}\b', '[REDACTED_ADDRESS]'),
        # Bitcoin addresses
        (r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', '[REDACTED_ADDRESS]'),
        # IP addresses
        (r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', '[REDACTED_IP]'),
    ],
    "database": [
        # Database connection strings
        (r'(?i)(mongodb(?:\+srv)?://[^\s]+)', '[REDACTED_DB_CONNECTION]'),
        (r'(?i)(postgres(?:ql)?://[^\s]+)', '[REDACTED_DB_CONNECTION]'),
        (r'(?i)(mysql://[^\s]+)', '[REDACTED_DB_CONNECTION]'),
        (r'(?i)(redis://[^\s]+)', '[REDACTED_DB_CONNECTION]'),
    ],
}


def redact_content(content: str, patterns: list, custom_patterns: list = None) -> tuple:
    """
    Redact sensitive content from text.

    Returns:
        tuple: (redacted_content, list of RedactionMatch objects)
    """
    matches = []
    redacted_content = content

    all_patterns = []

    # Add selected patterns
    for pattern_name in patterns:
        if pattern_name in REDACTION_PATTERNS:
            all_patterns.extend([(pattern_name, regex, replacement) for regex, replacement in REDACTION_PATTERNS[pattern_name]])

    # Add custom patterns
    if custom_patterns:
        for custom in custom_patterns:
            all_patterns.append(("custom", custom, "[REDACTED]"))

    # Apply patterns line by line for accurate line numbers
    lines = redacted_content.split("\n")
    redacted_lines = []

    for line_num, line in enumerate(lines, 1):
        redacted_line = line
        for pattern_name, regex, replacement in all_patterns:
            for match in re.finditer(regex, redacted_line):
                original = match.group(0)
                # Apply the replacement
                new_text = re.sub(regex, replacement, original)
                matches.append(RedactionMatch(
                    pattern_name=pattern_name,
                    line_number=line_num,
                    original=original,
                    redacted=new_text,
                    position=match.start(),
                ))
            redacted_line = re.sub(regex, replacement, redacted_line)
        redacted_lines.append(redacted_line)

    return "\n".join(redacted_lines), matches


def generate_redaction_report(report: RedactionReport, output_format: str = "markdown") -> str:
    """Generate a redaction report."""
    if output_format == "json":
        return json.dumps({
            "input_file": report.input_file,
            "output_file": report.output_file,
            "timestamp": report.timestamp,
            "total_redactions": report.total_redactions,
            "patterns_used": report.patterns_used,
            "matches": [
                {
                    "pattern_name": m.pattern_name,
                    "line_number": m.line_number,
                    "original": m.original,
                    "redacted": m.redacted,
                    "position": m.position,
                }
                for m in report.matches
            ],
        }, indent=2)

    lines = [
        "# Redaction Report",
        "",
        f"**Input File:** {report.input_file}",
        f"**Output File:** {report.output_file}",
        f"**Timestamp:** {report.timestamp}",
        f"**Total Redactions:** {report.total_redactions}",
        "",
        "## Patterns Used",
        "",
    ]

    for pattern in report.patterns_used:
        lines.append(f"- {pattern}")

    lines.extend([
        "",
        "## Redaction Details",
        "",
        "| # | Pattern | Line | Original | Redacted |",
        "|---|---------|------|----------|----------|",
    ])

    for i, match in enumerate(report.matches, 1):
        # Truncate long values for display
        original = match.original[:50] + "..." if len(match.original) > 50 else match.original
        redacted = match.redacted[:50] + "..." if len(match.redacted) > 50 else match.redacted
        lines.append(f"| {i} | {match.pattern_name} | {match.line_number} | `{original}` | `{redacted}` |")

    return "\n".join(lines)


def secure_delete(filepath: str, passes: int = 3) -> None:
    """Securely delete a file by overwriting it before deletion."""
    path = Path(filepath)
    if not path.exists():
        return

    file_size = path.stat().st_size

    with open(filepath, "ba+") as f:
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())

    path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redact sensitive data from security reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input report.md --output report_redacted.md
  %(prog)s --input report.md --output report_redacted.md --patterns passwords,tokens,pii
  %(prog)s --input report.md --output report_redacted.md --custom-pattern "secret.*"
  %(prog)s --input report.md --output report_redacted.md --report redaction_report.md
  %(prog)s --list-patterns
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        help="Input report file",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output redacted file",
    )
    parser.add_argument(
        "--patterns",
        help="Comma-separated list of pattern groups to apply",
    )
    parser.add_argument(
        "--custom-pattern",
        action="append",
        help="Custom regex pattern to redact (can be used multiple times)",
    )
    parser.add_argument(
        "--report",
        help="Output redaction report file",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Redaction report format (default: markdown)",
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List available pattern groups",
    )
    parser.add_argument(
        "--secure-delete",
        action="store_true",
        help="Securely delete the original file after redaction",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be redacted without writing files",
    )

    args = parser.parse_args()

    if args.list_patterns:
        print("Available pattern groups:")
        print()
        for name, patterns in REDACTION_PATTERNS.items():
            print(f"  {name:12s} - {len(patterns)} pattern(s)")
        print()
        print("Use --patterns to specify which groups to apply (comma-separated).")
        print("Use --all to apply all patterns.")
        return

    if not args.input or not args.output:
        parser.error("--input and --output are required (unless using --list-patterns)")

    # Read input file
    try:
        with open(args.input, "r") as f:
            content = f.read()
    except IOError as e:
        print(f"Error reading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine patterns to use
    if args.patterns:
        patterns = [p.strip() for p in args.patterns.split(",")]
    else:
        patterns = list(REDACTION_PATTERNS.keys())

    # Apply redactions
    redacted_content, matches = redact_content(content, patterns, args.custom_pattern)

    # Generate redaction report
    redaction_report = RedactionReport(
        input_file=args.input,
        output_file=args.output,
        timestamp=datetime.now().isoformat(),
        total_redactions=len(matches),
        matches=matches,
        patterns_used=patterns,
    )

    if args.dry_run:
        print(f"Dry run — would redact {len(matches)} items:")
        print()
        for i, match in enumerate(matches, 1):
            original = match.original[:50] + "..." if len(match.original) > 50 else match.original
            print(f"  {i}. Line {match.line_number} ({match.pattern_name}): {original}")
        print()
        print(f"Redacted content would be written to: {args.output}")
        return

    # Write redacted content
    try:
        with open(args.output, "w") as f:
            f.write(redacted_content)
        print(f"Redacted report written to {args.output}")
        print(f"Total redactions: {len(matches)}")
    except IOError as e:
        print(f"Error writing {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

    # Write redaction report
    if args.report:
        redaction_report_content = generate_redaction_report(redaction_report, args.format)
        try:
            with open(args.report, "w") as f:
                f.write(redaction_report_content)
            print(f"Redaction report written to {args.report}")
        except IOError as e:
            print(f"Error writing {args.report}: {e}", file=sys.stderr)

    # Securely delete original if requested
    if args.secure_delete:
        secure_delete(args.input)
        print(f"Original file securely deleted: {args.input}")


if __name__ == "__main__":
    main()
