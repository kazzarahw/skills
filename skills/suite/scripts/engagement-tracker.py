#!/usr/bin/env python3
"""
Engagement Tracker — Track security testing engagement state across phases.

Supports web2, web3, and mixed engagements. Records phase transitions,
tracks findings by severity, generates engagement summaries, and persists
state to JSON.

Usage:
    python engagement-tracker.py init --type web2 --target "example.com"
    python engagement-tracker.py transition --to audit
    python engagement-tracker.py finding --severity high --title "SQL injection" --provenance tool-proven
    python engagement-tracker.py summary
    python engagement-tracker.py export --format json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATE_FILE = ".engagement-state.json"

ENGAGEMENT_TYPES = ("web2", "web3", "mixed", "incident", "advisory")

PHASES = ("recon", "audit", "exploit", "verify", "forensics", "report")

SEVERITIES = ("critical", "high", "medium", "low", "informational")

PROVENANCE_LABELS = ("tool-proven", "model-asserted")

# Phase ordering per engagement type
PHASE_ORDER = {
    "web2":       ["recon", "audit", "exploit", "verify", "report"],
    "web3":       ["recon", "audit", "exploit", "verify", "report"],
    "mixed":      ["recon", "audit", "exploit", "verify", "report"],
    "incident":   ["forensics", "verify", "report"],
    "advisory":   ["audit", "report"],
}


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """Represents a single security finding."""
    id: str
    title: str
    severity: str
    provenance: str
    phase: str
    timestamp: str
    description: str = ""
    evidence: str = ""
    reproduction_steps: str = ""
    remediation: str = ""
    cvss_score: float | None = None
    immunefi_impact: str | None = None
    verified: bool = False
    false_positive: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        return cls(**data)


@dataclass
class PhaseTransition:
    """Records a transition from one phase to another."""
    from_phase: str
    to_phase: str
    timestamp: str
    exit_criteria_met: bool
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PhaseTransition":
        return cls(**data)


@dataclass
class EngagementState:
    """Complete engagement state."""
    engagement_id: str
    engagement_type: str
    target: str
    status: str  # active | complete | paused
    current_phase: str
    started: str
    updated: str
    phases_completed: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    transitions: list[PhaseTransition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engagement_id": self.engagement_id,
            "engagement_type": self.engagement_type,
            "target": self.target,
            "status": self.status,
            "current_phase": self.current_phase,
            "started": self.started,
            "updated": self.updated,
            "phases_completed": self.phases_completed,
            "findings": [f.to_dict() for f in self.findings],
            "transitions": [t.to_dict() for t in self.transitions],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EngagementState":
        findings = [Finding.from_dict(f) for f in data.get("findings", [])]
        transitions = [PhaseTransition.from_dict(t) for t in data.get("transitions", [])]
        return cls(
            engagement_id=data["engagement_id"],
            engagement_type=data["engagement_type"],
            target=data["target"],
            status=data["status"],
            current_phase=data["current_phase"],
            started=data["started"],
            updated=data["updated"],
            phases_completed=data.get("phases_completed", []),
            findings=findings,
            transitions=transitions,
            metadata=data.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _generate_id(prefix: str = "F") -> str:
    """Generate a unique finding ID."""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _load_state(path: Path) -> EngagementState | None:
    """Load engagement state from JSON file."""
    if not path.exists():
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return EngagementState.from_dict(data)


def _save_state(path: Path, state: EngagementState) -> None:
    """Persist engagement state to JSON file."""
    with open(path, "w") as f:
        json.dump(state.to_dict(), f, indent=2)


def _severity_counts(findings: list[Finding]) -> dict[str, int]:
    """Count findings by severity."""
    counts = defaultdict(int)
    for f in findings:
        counts[f.severity] += 1
    return dict(counts)


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a simple ASCII table."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(cell.ljust(w) for cell, w in zip(row, col_widths)))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a new engagement."""
    state_path = Path(args.state_file)

    if state_path.exists() and not args.force:
        print(f"ERROR: Engagement state already exists at {state_path}", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1

    eng_type = args.type
    if eng_type not in ENGAGEMENT_TYPES:
        print(f"ERROR: Invalid engagement type '{eng_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(ENGAGEMENT_TYPES)}", file=sys.stderr)
        return 1

    # Determine starting phase
    starting_phase = PHASE_ORDER[eng_type][0]

    now = _now()
    state = EngagementState(
        engagement_id=_generate_id("ENG"),
        engagement_type=eng_type,
        target=args.target,
        status="active",
        current_phase=starting_phase,
        started=now,
        updated=now,
        phases_completed=[],
        findings=[],
        transitions=[],
        metadata={
            "description": args.description or "",
            "client": args.client or "",
            "tester": args.tester or "",
        },
    )

    _save_state(state_path, state)
    print(f"Engagement initialized: {state.engagement_id}")
    print(f"  Type:   {eng_type}")
    print(f"  Target: {args.target}")
    print(f"  Phase:  {starting_phase}")
    print(f"  State:  {state_path}")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    """Transition to a new phase."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    if state.status != "active":
        print(f"ERROR: Engagement is {state.status}, not active", file=sys.stderr)
        return 1

    target_phase = args.to_phase
    if target_phase not in PHASES:
        print(f"ERROR: Invalid phase '{target_phase}'", file=sys.stderr)
        print(f"Valid phases: {', '.join(PHASES)}", file=sys.stderr)
        return 1

    # Validate phase order
    expected_phases = PHASE_ORDER[state.engagement_type]
    current_idx = expected_phases.index(state.current_phase) if state.current_phase in expected_phases else -1
    target_idx = expected_phases.index(target_phase) if target_phase in expected_phases else -1

    if target_idx <= current_idx and not args.allow_backtrack:
        print(f"ERROR: Cannot transition from '{state.current_phase}' to '{target_phase}'", file=sys.stderr)
        print("Use --allow-backtrack to override.", file=sys.stderr)
        return 1

    now = _now()
    transition = PhaseTransition(
        from_phase=state.current_phase,
        to_phase=target_phase,
        timestamp=now,
        exit_criteria_met=not args.exit_criteria_unmet,
        notes=args.notes or "",
    )

    # Mark previous phase as completed
    if state.current_phase not in state.phases_completed:
        state.phases_completed.append(state.current_phase)

    state.transitions.append(transition)
    state.current_phase = target_phase
    state.updated = now

    _save_state(state_path, state)
    print(f"Transitioned: {transition.from_phase} → {target_phase}")
    if args.notes:
        print(f"  Notes: {args.notes}")
    return 0


def cmd_finding(args: argparse.Namespace) -> int:
    """Add a finding to the engagement."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    severity = args.severity.lower()
    if severity not in SEVERITIES:
        print(f"ERROR: Invalid severity '{severity}'", file=sys.stderr)
        print(f"Valid severities: {', '.join(SEVERITIES)}", file=sys.stderr)
        return 1

    provenance = args.provenance
    if provenance not in PROVENANCE_LABELS:
        print(f"ERROR: Invalid provenance '{provenance}'", file=sys.stderr)
        print(f"Valid provenance: {', '.join(PROVENANCE_LABELS)}", file=sys.stderr)
        return 1

    finding = Finding(
        id=_generate_id(),
        title=args.title,
        severity=severity,
        provenance=provenance,
        phase=state.current_phase,
        timestamp=_now(),
        description=args.description or "",
        evidence=args.evidence or "",
        reproduction_steps=args.reproduction_steps or "",
        remediation=args.remediation or "",
        cvss_score=args.cvss_score,
        immunefi_impact=args.immunefi_impact,
        verified=args.verified,
        false_positive=args.false_positive,
    )

    state.findings.append(finding)
    state.updated = _now()

    _save_state(state_path, state)
    print(f"Finding added: {finding.id}")
    print(f"  Title:       {finding.title}")
    print(f"  Severity:    {finding.severity}")
    print(f"  Provenance:  {finding.provenance}")
    print(f"  Phase:       {finding.phase}")
    return 0


def cmd_verify_finding(args: argparse.Namespace) -> int:
    """Mark a finding as verified or false positive."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    finding_id = args.finding_id
    finding = next((f for f in state.findings if f.id == finding_id), None)

    if finding is None:
        print(f"ERROR: Finding '{finding_id}' not found", file=sys.stderr)
        return 1

    finding.verified = not args.unverify
    finding.false_positive = args.false_positive
    state.updated = _now()

    _save_state(state_path, state)
    status = "verified" if finding.verified else "unverified"
    if finding.false_positive:
        status += " (false positive)"
    print(f"Finding {finding_id}: {status}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """Display engagement summary."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    print("=" * 60)
    print("ENGAGEMENT SUMMARY")
    print("=" * 60)
    print(f"  ID:          {state.engagement_id}")
    print(f"  Type:        {state.engagement_type}")
    print(f"  Target:      {state.target}")
    print(f"  Status:      {state.status}")
    print(f"  Phase:       {state.current_phase}")
    print(f"  Started:     {state.started}")
    print(f"  Updated:     {state.updated}")
    print()

    # Phases completed
    print("Phases Completed:")
    for phase in PHASE_ORDER[state.engagement_type]:
        marker = "✓" if phase in state.phases_completed else " "
        current = " ← current" if phase == state.current_phase else ""
        print(f"  [{marker}] {phase}{current}")
    print()

    # Findings by severity
    counts = _severity_counts(state.findings)
    print("Findings by Severity:")
    for sev in SEVERITIES:
        count = counts.get(sev, 0)
        print(f"  {sev:15s} {count}")
    print(f"  {'Total':15s} {len(state.findings)}")
    print()

    # Findings by provenance
    provenance_counts = defaultdict(int)
    for f in state.findings:
        provenance_counts[f.provenance] += 1
    print("Findings by Provenance:")
    for prov in PROVENANCE_LABELS:
        count = provenance_counts.get(prov, 0)
        print(f"  {prov:15s} {count}")
    print()

    # Verified findings
    verified = sum(1 for f in state.findings if f.verified)
    false_pos = sum(1 for f in state.findings if f.false_positive)
    print(f"Verified:       {verified}")
    print(f"False Positives: {false_pos}")
    print(f"Unverified:     {len(state.findings) - verified - false_pos}")
    print()

    # Recent findings
    if state.findings:
        print("Recent Findings:")
        recent = sorted(state.findings, key=lambda f: f.timestamp, reverse=True)[:5]
        rows = []
        for f in recent:
            rows.append([f.id, f.severity, f.provenance, f.title[:40]])
        _print_table(["ID", "Severity", "Provenance", "Title"], rows)

    return 0


def cmd_list_findings(args: argparse.Namespace) -> int:
    """List all findings with optional filtering."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    findings = state.findings

    # Apply filters
    if args.severity:
        findings = [f for f in findings if f.severity == args.severity]
    if args.provenance:
        findings = [f for f in findings if f.provenance == args.provenance]
    if args.phase:
        findings = [f for f in findings if f.phase == args.phase]
    if args.verified_only:
        findings = [f for f in findings if f.verified]
    if args.false_positives:
        findings = [f for f in findings if f.false_positive]

    if not findings:
        print("No findings match the specified filters.")
        return 0

    rows = []
    for f in findings:
        status = "✓" if f.verified else "✗"
        if f.false_positive:
            status = "FP"
        rows.append([f.id, f.severity, f.provenance, f.phase, status, f.title[:35]])

    _print_table(["ID", "Severity", "Provenance", "Phase", "Status", "Title"], rows)
    print(f"\nTotal: {len(findings)} findings")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export engagement state to JSON or Markdown."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else None

    if args.format == "json":
        output = json.dumps(state.to_dict(), indent=2)
    elif args.format == "markdown":
        output = _generate_markdown_report(state)
    else:
        print(f"ERROR: Unsupported format '{args.format}'", file=sys.stderr)
        return 1

    if output_path:
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Exported to {output_path}")
    else:
        print(output)

    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    """Mark engagement as complete."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    state.status = "complete"
    state.updated = _now()

    _save_state(state_path, state)
    print(f"Engagement {state.engagement_id} marked as complete.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Quick status display."""
    state_path = Path(args.state_file)
    state = _load_state(state_path)

    if state is None:
        print(f"ERROR: No engagement state found at {state_path}", file=sys.stderr)
        return 1

    counts = _severity_counts(state.findings)
    print(f"Engagement: {state.engagement_id} ({state.engagement_type})")
    print(f"Target:     {state.target}")
    print(f"Status:     {state.status}")
    print(f"Phase:      {state.current_phase}")
    print(f"Findings:   {len(state.findings)} total")
    for sev in SEVERITIES:
        if counts.get(sev, 0) > 0:
            print(f"  {sev}: {counts[sev]}")
    return 0


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def _generate_markdown_report(state: EngagementState) -> str:
    """Generate a Markdown engagement report."""
    lines = []
    lines.append(f"# Engagement Report: {state.engagement_id}")
    lines.append("")
    lines.append(f"**Type:** {state.engagement_type}")
    lines.append(f"**Target:** {state.target}")
    lines.append(f"**Status:** {state.status}")
    lines.append(f"**Started:** {state.started}")
    lines.append(f"**Updated:** {state.updated}")
    lines.append("")

    # Phases
    lines.append("## Phases")
    lines.append("")
    for phase in PHASE_ORDER[state.engagement_type]:
        marker = "✓" if phase in state.phases_completed else " "
        current = " (current)" if phase == state.current_phase else ""
        lines.append(f"- [{marker}] {phase}{current}")
    lines.append("")

    # Findings summary
    counts = _severity_counts(state.findings)
    lines.append("## Findings Summary")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in SEVERITIES:
        lines.append(f"| {sev} | {counts.get(sev, 0)} |")
    lines.append(f"| **Total** | **{len(state.findings)}** |")
    lines.append("")

    # Detailed findings
    if state.findings:
        lines.append("## Detailed Findings")
        lines.append("")
        for f in sorted(state.findings, key=lambda x: SEVERITIES.index(x.severity)):
            status = "✓ Verified" if f.verified else "✗ Unverified"
            if f.false_positive:
                status = "False Positive"
            lines.append(f"### {f.id}: {f.title}")
            lines.append("")
            lines.append(f"- **Severity:** {f.severity}")
            lines.append(f"- **Provenance:** {f.provenance}")
            lines.append(f"- **Phase:** {f.phase}")
            lines.append(f"- **Status:** {status}")
            if f.cvss_score is not None:
                lines.append(f"- **CVSS Score:** {f.cvss_score}")
            if f.immunefi_impact:
                lines.append(f"- **Immunefi Impact:** {f.immunefi_impact}")
            if f.description:
                lines.append(f"- **Description:** {f.description}")
            if f.evidence:
                lines.append(f"- **Evidence:** {f.evidence}")
            if f.reproduction_steps:
                lines.append(f"- **Reproduction Steps:** {f.reproduction_steps}")
            if f.remediation:
                lines.append(f"- **Remediation:** {f.remediation}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Track security testing engagement state across phases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--state-file",
        default=STATE_FILE,
        help=f"Path to state file (default: {STATE_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new engagement")
    init_parser.add_argument("--type", required=True, choices=ENGAGEMENT_TYPES, help="Engagement type")
    init_parser.add_argument("--target", required=True, help="Engagement target")
    init_parser.add_argument("--description", help="Engagement description")
    init_parser.add_argument("--client", help="Client name")
    init_parser.add_argument("--tester", help="Tester name")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing state")

    # transition
    trans_parser = subparsers.add_parser("transition", help="Transition to a new phase")
    trans_parser.add_argument("--to", dest="to_phase", required=True, choices=PHASES, help="Target phase")
    trans_parser.add_argument("--notes", help="Transition notes")
    trans_parser.add_argument("--exit-criteria-unmet", action="store_true", help="Mark exit criteria as unmet")
    trans_parser.add_argument("--allow-backtrack", action="store_true", help="Allow backward phase transitions")

    # finding
    finding_parser = subparsers.add_parser("finding", help="Add a finding")
    finding_parser.add_argument("--title", required=True, help="Finding title")
    finding_parser.add_argument("--severity", required=True, choices=SEVERITIES, help="Finding severity")
    finding_parser.add_argument("--provenance", default="tool-proven", choices=PROVENANCE_LABELS, help="Provenance label")
    finding_parser.add_argument("--description", help="Finding description")
    finding_parser.add_argument("--evidence", help="Evidence reference")
    finding_parser.add_argument("--reproduction-steps", help="Reproduction steps")
    finding_parser.add_argument("--remediation", help="Remediation guidance")
    finding_parser.add_argument("--cvss-score", type=float, help="CVSS v3.1 score")
    finding_parser.add_argument("--immunefi-impact", help="Immunefi impact description")
    finding_parser.add_argument("--verified", action="store_true", help="Mark as verified")
    finding_parser.add_argument("--false-positive", action="store_true", help="Mark as false positive")

    # verify-finding
    verify_parser = subparsers.add_parser("verify-finding", help="Mark a finding as verified or false positive")
    verify_parser.add_argument("finding_id", help="Finding ID")
    verify_parser.add_argument("--unverify", action="store_true", help="Mark as unverified")
    verify_parser.add_argument("--false-positive", action="store_true", help="Mark as false positive")

    # summary
    subparsers.add_parser("summary", help="Display engagement summary")

    # list-findings
    list_parser = subparsers.add_parser("list-findings", help="List findings with optional filters")
    list_parser.add_argument("--severity", choices=SEVERITIES, help="Filter by severity")
    list_parser.add_argument("--provenance", choices=PROVENANCE_LABELS, help="Filter by provenance")
    list_parser.add_argument("--phase", choices=PHASES, help="Filter by phase")
    list_parser.add_argument("--verified-only", action="store_true", help="Show only verified findings")
    list_parser.add_argument("--false-positives", action="store_true", help="Show only false positives")

    # export
    export_parser = subparsers.add_parser("export", help="Export engagement state")
    export_parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Export format")
    export_parser.add_argument("--output", help="Output file path")

    # complete
    subparsers.add_parser("complete", help="Mark engagement as complete")

    # status
    subparsers.add_parser("status", help="Quick status display")

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    commands = {
        "init": cmd_init,
        "transition": cmd_transition,
        "finding": cmd_finding,
        "verify-finding": cmd_verify_finding,
        "summary": cmd_summary,
        "list-findings": cmd_list_findings,
        "export": cmd_export,
        "complete": cmd_complete,
        "status": cmd_status,
    }

    handler = commands.get(args.command)
    if handler is None:
        print(f"ERROR: Unknown command '{args.command}'", file=sys.stderr)
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
