#!/usr/bin/env python3
"""
Scope Checker — Validate targets against engagement scope.

Validates IP ranges, domains, and blockchain addresses against defined scope.
Supports web2 and web3 scope formats. Generates scope validation report and
flags out-of-scope targets.

Usage:
    python scope-checker.py validate --scope scope.json --targets targets.txt
    python scope-checker.py check --scope scope.json --target 192.168.1.1
    python scope-checker.py report --scope scope.json --targets targets.txt --output report.md
"""

import argparse
import ipaddress
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Regex patterns
DOMAIN_PATTERN = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
)

ETH_ADDRESS_PATTERN = re.compile(r'^0x[a-fA-F0-9]{40}$')
SOL_ADDRESS_PATTERN = re.compile(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$')
BTC_ADDRESS_PATTERN = re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{25,39}$')

# EVM chain ID mappings
EVM_CHAINS = {
    1: "Ethereum Mainnet",
    5: "Goerli Testnet",
    11155111: "Sepolia Testnet",
    56: "BNB Smart Chain",
    137: "Polygon Mainnet",
    42161: "Arbitrum One",
    10: "Optimism",
    43114: "Avalanche C-Chain",
    250: "Fantom Opera",
    42220: "Celo Mainnet",
}


# ---------------------------------------------------------------------------
# Enums and Data Classes
# ---------------------------------------------------------------------------

class TargetType(Enum):
    """Type of target."""
    IP = "ip"
    CIDR = "cidr"
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    ETH_ADDRESS = "eth_address"
    SOL_ADDRESS = "sol_address"
    BTC_ADDRESS = "btc_address"
    URL = "url"
    UNKNOWN = "unknown"


class ScopeStatus(Enum):
    """Scope validation status."""
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    INVALID = "invalid"
    AMBIGUOUS = "ambiguous"


@dataclass
class ScopeEntry:
    """Represents a single scope entry."""
    value: str
    type: str
    description: str = ""
    chain_id: int | None = None  # For web3 addresses

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScopeEntry":
        return cls(**data)


@dataclass
class TargetValidation:
    """Result of validating a single target."""
    target: str
    target_type: str
    status: str
    matched_scope: str | None = None
    reason: str = ""
    chain_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScopeReport:
    """Complete scope validation report."""
    total_targets: int = 0
    in_scope: int = 0
    out_of_scope: int = 0
    invalid: int = 0
    ambiguous: int = 0
    validations: list[TargetValidation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_targets": self.total_targets,
            "in_scope": self.in_scope,
            "out_of_scope": self.out_of_scope,
            "invalid": self.invalid,
            "ambiguous": self.ambiguous,
            "validations": [v.to_dict() for v in self.validations],
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Target Classification
# ---------------------------------------------------------------------------

def classify_target(target: str) -> TargetType:
    """Classify a target string into a target type."""
    target = target.strip()

    # URL
    if target.startswith(("http://", "https://")):
        return TargetType.URL

    # Ethereum address
    if ETH_ADDRESS_PATTERN.match(target):
        return TargetType.ETH_ADDRESS

    # Solana address
    if SOL_ADDRESS_PATTERN.match(target):
        return TargetType.SOL_ADDRESS

    # Bitcoin address
    if BTC_ADDRESS_PATTERN.match(target):
        return TargetType.BTC_ADDRESS

    # CIDR notation
    if "/" in target:
        try:
            ipaddress.ip_network(target, strict=False)
            return TargetType.CIDR
        except ValueError:
            return TargetType.UNKNOWN

    # IP address
    try:
        ipaddress.ip_address(target)
        return TargetType.IP
    except ValueError:
        pass

    # Domain
    if DOMAIN_PATTERN.match(target):
        # Check if it's a subdomain (more than 2 labels)
        labels = target.split(".")
        if len(labels) > 2:
            return TargetType.SUBDOMAIN
        return TargetType.DOMAIN

    return TargetType.UNKNOWN


# ---------------------------------------------------------------------------
# Scope Validation
# ---------------------------------------------------------------------------

def _ip_in_scope(ip_str: str, scope_entries: list[ScopeEntry]) -> tuple[bool, str | None]:
    """Check if an IP address is within any scope entry."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False, None

    for entry in scope_entries:
        entry_type = classify_target(entry.value)

        if entry_type == TargetType.IP:
            if ip == ipaddress.ip_address(entry.value):
                return True, entry.value

        elif entry_type == TargetType.CIDR:
            try:
                network = ipaddress.ip_network(entry.value, strict=False)
                if ip in network:
                    return True, entry.value
            except ValueError:
                continue

    return False, None


def _domain_in_scope(domain: str, scope_entries: list[ScopeEntry]) -> tuple[bool, str | None]:
    """Check if a domain is within any scope entry (including subdomains)."""
    domain = domain.lower().rstrip(".")

    for entry in scope_entries:
        entry_value = entry.value.lower().rstrip(".")
        entry_type = classify_target(entry.value)

        if entry_type in (TargetType.DOMAIN, TargetType.SUBDOMAIN):
            # Exact match
            if domain == entry_value:
                return True, entry.value

            # Subdomain match (scope is parent domain)
            if domain.endswith("." + entry_value):
                return True, entry.value

    return False, None


def _address_in_scope(address: str, scope_entries: list[ScopeEntry], chain_id: int | None = None) -> tuple[bool, str | None]:
    """Check if a blockchain address is within any scope entry."""
    address_lower = address.lower()

    for entry in scope_entries:
        entry_value = entry.value.lower()
        entry_type = classify_target(entry.value)

        if entry_type in (TargetType.ETH_ADDRESS, TargetType.SOL_ADDRESS, TargetType.BTC_ADDRESS):
            if address_lower == entry_value:
                # If chain is specified, verify chain match
                if chain_id is not None and entry.chain_id is not None:
                    if chain_id == entry.chain_id:
                        return True, entry.value
                else:
                    return True, entry.value

    return False, None


def validate_target(target: str, scope_entries: list[ScopeEntry], chain_id: int | None = None) -> TargetValidation:
    """Validate a single target against scope entries."""
    target = target.strip()
    target_type = classify_target(target)

    if target_type == TargetType.UNKNOWN:
        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.INVALID.value,
            reason="Unrecognized target format",
        )

    if target_type == TargetType.URL:
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(target)
        domain = parsed.hostname or target
        in_scope, matched = _domain_in_scope(domain, scope_entries)
        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.IN_SCOPE.value if in_scope else ScopeStatus.OUT_OF_SCOPE.value,
            matched_scope=matched,
            reason=f"Domain '{domain}' {'in scope' if in_scope else 'out of scope'}",
        )

    if target_type == TargetType.IP:
        in_scope, matched = _ip_in_scope(target, scope_entries)
        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.IN_SCOPE.value if in_scope else ScopeStatus.OUT_OF_SCOPE.value,
            matched_scope=matched,
            reason=f"IP {'in scope' if in_scope else 'out of scope'}",
        )

    if target_type == TargetType.CIDR:
        # Check if CIDR overlaps with any scope entry
        try:
            target_net = ipaddress.ip_network(target, strict=False)
        except ValueError:
            return TargetValidation(
                target=target,
                target_type=target_type.value,
                status=ScopeStatus.INVALID.value,
                reason="Invalid CIDR notation",
            )

        for entry in scope_entries:
            entry_type = classify_target(entry.value)
            if entry_type == TargetType.CIDR:
                try:
                    entry_net = ipaddress.ip_network(entry.value, strict=False)
                    if target_net.overlaps(entry_net):
                        return TargetValidation(
                            target=target,
                            target_type=target_type.value,
                            status=ScopeStatus.IN_SCOPE.value,
                            matched_scope=entry.value,
                            reason=f"CIDR overlaps with scope entry {entry.value}",
                        )
                except ValueError:
                    continue
            elif entry_type == TargetType.IP:
                try:
                    if ipaddress.ip_address(entry.value) in target_net:
                        return TargetValidation(
                            target=target,
                            target_type=target_type.value,
                            status=ScopeStatus.IN_SCOPE.value,
                            matched_scope=entry.value,
                            reason=f"CIDR contains scope IP {entry.value}",
                        )
                except ValueError:
                    continue

        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.OUT_OF_SCOPE.value,
            reason="CIDR does not overlap with any scope entry",
        )

    if target_type in (TargetType.DOMAIN, TargetType.SUBDOMAIN):
        in_scope, matched = _domain_in_scope(target, scope_entries)
        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.IN_SCOPE.value if in_scope else ScopeStatus.OUT_OF_SCOPE.value,
            matched_scope=matched,
            reason=f"Domain {'in scope' if in_scope else 'out of scope'}",
        )

    if target_type in (TargetType.ETH_ADDRESS, TargetType.SOL_ADDRESS, TargetType.BTC_ADDRESS):
        in_scope, matched = _address_in_scope(target, scope_entries, chain_id)
        return TargetValidation(
            target=target,
            target_type=target_type.value,
            status=ScopeStatus.IN_SCOPE.value if in_scope else ScopeStatus.OUT_OF_SCOPE.value,
            matched_scope=matched,
            reason=f"Address {'in scope' if in_scope else 'out of scope'}",
            chain_id=chain_id,
        )

    return TargetValidation(
        target=target,
        target_type=target_type.value,
        status=ScopeStatus.AMBIGUOUS.value,
        reason="Unable to determine scope status",
    )


# ---------------------------------------------------------------------------
# Scope File Parsing
# ---------------------------------------------------------------------------

def load_scope(scope_path: str | Path) -> list[ScopeEntry]:
    """Load scope entries from a JSON file.

    Expected format:
    {
        "scope": [
            {"value": "192.168.1.0/24", "type": "cidr", "description": "Internal network"},
            {"value": "example.com", "type": "domain", "description": "Primary domain"},
            {"value": "0x1234...", "type": "eth_address", "chain_id": 1, "description": "Contract"}
        ]
    }
    """
    scope_path = Path(scope_path)
    if not scope_path.exists():
        raise FileNotFoundError(f"Scope file not found: {scope_path}")

    with open(scope_path, "r") as f:
        data = json.load(f)

    entries = []
    for item in data.get("scope", []):
        entries.append(ScopeEntry(
            value=item["value"],
            type=item.get("type", "unknown"),
            description=item.get("description", ""),
            chain_id=item.get("chain_id"),
        ))

    return entries


def load_targets(targets_path: str | Path) -> list[str]:
    """Load targets from a text file (one per line)."""
    targets_path = Path(targets_path)
    if not targets_path.exists():
        raise FileNotFoundError(f"Targets file not found: {targets_path}")

    targets = []
    with open(targets_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(line)

    return targets


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def generate_markdown_report(report: ScopeReport, scope_entries: list[ScopeEntry]) -> str:
    """Generate a Markdown scope validation report."""
    lines = []
    lines.append("# Scope Validation Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total targets | {report.total_targets} |")
    lines.append(f"| In scope | {report.in_scope} |")
    lines.append(f"| Out of scope | {report.out_of_scope} |")
    lines.append(f"| Invalid | {report.invalid} |")
    lines.append(f"| Ambiguous | {report.ambiguous} |")
    lines.append("")

    # Scope entries
    lines.append("## Scope Entries")
    lines.append("")
    lines.append("| Value | Type | Description |")
    lines.append("|-------|------|-------------|")
    for entry in scope_entries:
        lines.append(f"| `{entry.value}` | {entry.type} | {entry.description} |")
    lines.append("")

    # Validation results
    lines.append("## Validation Results")
    lines.append("")
    lines.append("| Target | Type | Status | Matched Scope | Reason |")
    lines.append("|--------|------|--------|---------------|--------|")
    for v in report.validations:
        matched = f"`{v.matched_scope}`" if v.matched_scope else "—"
        lines.append(f"| `{v.target}` | {v.target_type} | {v.status} | {matched} | {v.reason} |")
    lines.append("")

    # Out-of-scope targets (flagged)
    out_of_scope = [v for v in report.validations if v.status == ScopeStatus.OUT_OF_SCOPE.value]
    if out_of_scope:
        lines.append("## ⚠️ Out-of-Scope Targets")
        lines.append("")
        lines.append("The following targets are **out of scope** and must not be tested:")
        lines.append("")
        for v in out_of_scope:
            lines.append(f"- `{v.target}` ({v.target_type}) — {v.reason}")
        lines.append("")

    # Invalid targets
    invalid = [v for v in report.validations if v.status == ScopeStatus.INVALID.value]
    if invalid:
        lines.append("## ❌ Invalid Targets")
        lines.append("")
        lines.append("The following targets have **invalid format**:")
        lines.append("")
        for v in invalid:
            lines.append(f"- `{v.target}` — {v.reason}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_validate(args: argparse.Namespace) -> int:
    """Validate targets against scope."""
    try:
        scope_entries = load_scope(args.scope)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load scope: {e}", file=sys.stderr)
        return 1

    try:
        targets = load_targets(args.targets)
    except FileNotFoundError as e:
        print(f"ERROR: Failed to load targets: {e}", file=sys.stderr)
        return 1

    chain_id = args.chain_id

    report = ScopeReport()
    report.total_targets = len(targets)

    for target in targets:
        result = validate_target(target, scope_entries, chain_id)
        report.validations.append(result)

        if result.status == ScopeStatus.IN_SCOPE.value:
            report.in_scope += 1
        elif result.status == ScopeStatus.OUT_OF_SCOPE.value:
            report.out_of_scope += 1
        elif result.status == ScopeStatus.INVALID.value:
            report.invalid += 1
        elif result.status == ScopeStatus.AMBIGUOUS.value:
            report.ambiguous += 1

    # Output
    if args.output:
        md_report = generate_markdown_report(report, scope_entries)
        with open(args.output, "w") as f:
            f.write(md_report)
        print(f"Report written to {args.output}")
    else:
        # Console output
        print("=" * 60)
        print("SCOPE VALIDATION REPORT")
        print("=" * 60)
        print(f"Total targets:  {report.total_targets}")
        print(f"In scope:       {report.in_scope}")
        print(f"Out of scope:   {report.out_of_scope}")
        print(f"Invalid:        {report.invalid}")
        print(f"Ambiguous:      {report.ambiguous}")
        print()

        if report.out_of_scope > 0:
            print("⚠️  OUT-OF-SCOPE TARGETS:")
            for v in report.validations:
                if v.status == ScopeStatus.OUT_OF_SCOPE.value:
                    print(f"  - {v.target} ({v.target_type}): {v.reason}")
            print()

        if report.invalid > 0:
            print("❌ INVALID TARGETS:")
            for v in report.validations:
                if v.status == ScopeStatus.INVALID.value:
                    print(f"  - {v.target}: {v.reason}")
            print()

        if report.out_of_scope == 0 and report.invalid == 0:
            print("✅ All targets are in scope.")

    # Return non-zero if any out-of-scope or invalid targets found
    return 1 if (report.out_of_scope > 0 or report.invalid > 0) else 0


def cmd_check(args: argparse.Namespace) -> int:
    """Check a single target against scope."""
    try:
        scope_entries = load_scope(args.scope)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load scope: {e}", file=sys.stderr)
        return 1

    result = validate_target(args.target, scope_entries, args.chain_id)

    print(f"Target:   {result.target}")
    print(f"Type:     {result.target_type}")
    print(f"Status:   {result.status}")
    if result.matched_scope:
        print(f"Matched:  {result.matched_scope}")
    print(f"Reason:   {result.reason}")

    if result.status == ScopeStatus.OUT_OF_SCOPE.value:
        print("\n⚠️  WARNING: Target is OUT OF SCOPE. Do not test.")
        return 1
    elif result.status == ScopeStatus.INVALID.value:
        print("\n❌ ERROR: Target format is invalid.")
        return 1
    elif result.status == ScopeStatus.IN_SCOPE.value:
        print("\n✅ Target is in scope.")
        return 0
    else:
        print("\n❓ Target scope status is ambiguous.")
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Generate a scope validation report."""
    try:
        scope_entries = load_scope(args.scope)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load scope: {e}", file=sys.stderr)
        return 1

    try:
        targets = load_targets(args.targets)
    except FileNotFoundError as e:
        print(f"ERROR: Failed to load targets: {e}", file=sys.stderr)
        return 1

    report = ScopeReport()
    report.total_targets = len(targets)

    for target in targets:
        result = validate_target(target, scope_entries, args.chain_id)
        report.validations.append(result)

        if result.status == ScopeStatus.IN_SCOPE.value:
            report.in_scope += 1
        elif result.status == ScopeStatus.OUT_OF_SCOPE.value:
            report.out_of_scope += 1
        elif result.status == ScopeStatus.INVALID.value:
            report.invalid += 1
        elif result.status == ScopeStatus.AMBIGUOUS.value:
            report.ambiguous += 1

    md_report = generate_markdown_report(report, scope_entries)

    if args.output:
        with open(args.output, "w") as f:
            f.write(md_report)
        print(f"Report written to {args.output}")
    else:
        print(md_report)

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Validate targets against engagement scope.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate targets against scope")
    validate_parser.add_argument("--scope", required=True, help="Path to scope JSON file")
    validate_parser.add_argument("--targets", required=True, help="Path to targets text file")
    validate_parser.add_argument("--chain-id", type=int, help="EVM chain ID for address validation")
    validate_parser.add_argument("--output", help="Output file for Markdown report")

    # check
    check_parser = subparsers.add_parser("check", help="Check a single target against scope")
    check_parser.add_argument("--scope", required=True, help="Path to scope JSON file")
    check_parser.add_argument("--target", required=True, help="Target to check")
    check_parser.add_argument("--chain-id", type=int, help="EVM chain ID for address validation")

    # report
    report_parser = subparsers.add_parser("report", help="Generate scope validation report")
    report_parser.add_argument("--scope", required=True, help="Path to scope JSON file")
    report_parser.add_argument("--targets", required=True, help="Path to targets text file")
    report_parser.add_argument("--chain-id", type=int, help="EVM chain ID for address validation")
    report_parser.add_argument("--output", help="Output file for Markdown report")

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    commands = {
        "validate": cmd_validate,
        "check": cmd_check,
        "report": cmd_report,
    }

    handler = commands.get(args.command)
    if handler is None:
        print(f"ERROR: Unknown command '{args.command}'", file=sys.stderr)
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
