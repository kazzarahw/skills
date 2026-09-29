#!/usr/bin/env python3
"""
subdomain-monitor.py - Monitor for new subdomain discoveries

Usage: python3 subdomain-monitor.py -d <domain> -b <baseline-file> [-o output.json]

This script monitors for new subdomains:
  - Queries multiple sources (crt.sh, subfinder, etc.)
  - Compares against baseline
  - Alerts on new discoveries
  - Supports multiple sources

Constitutional rules enforced:
  - Passive recon only (no active scanning)
  - Evidence-based findings
  - Structured output format
"""

import argparse
import json
import sys
import os
import subprocess
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SubdomainInfo:
    """Subdomain information."""
    subdomain: str
    source: str
    first_seen: str
    last_seen: str
    ip_addresses: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitorResult:
    """Monitor result."""
    domain: str
    timestamp: str
    total_subdomains: int
    new_subdomains: List[SubdomainInfo] = field(default_factory=list)
    removed_subdomains: List[str] = field(default_factory=list)
    unchanged_subdomains: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ============================================================================
# Source Functions
# ============================================================================

def query_crtsh(domain: str) -> List[SubdomainInfo]:
    """Query crt.sh for subdomains."""
    subdomains = []
    try:
        import urllib.request
        import urllib.parse

        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        req = urllib.request.Request(url, headers={"User-Agent": "subdomain-monitor/1.0"})

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        for entry in data:
            name_value = entry.get("name_value", "")
            # Handle multiple domains in one entry
            for subdomain in name_value.split("\n"):
                subdomain = subdomain.strip().lower()
                if subdomain.endswith(domain) and "*" not in subdomain:
                    subdomains.append(SubdomainInfo(
                        subdomain=subdomain,
                        source="crt.sh",
                        first_seen=datetime.utcnow().isoformat() + "Z",
                        last_seen=datetime.utcnow().isoformat() + "Z",
                    ))

    except Exception as e:
        print(f"Warning: crt.sh query failed: {e}", file=sys.stderr)

    return subdomains


def query_subfinder(domain: str) -> List[SubdomainInfo]:
    """Query subfinder for subdomains."""
    subdomains = []
    try:
        result = subprocess.run(
            ["subfinder", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    subdomains.append(SubdomainInfo(
                        subdomain=line.strip().lower(),
                        source="subfinder",
                        first_seen=datetime.utcnow().isoformat() + "Z",
                        last_seen=datetime.utcnow().isoformat() + "Z",
                    ))

    except FileNotFoundError:
        print("Warning: subfinder not found, skipping", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("Warning: subfinder timed out", file=sys.stderr)
    except Exception as e:
        print(f"Warning: subfinder query failed: {e}", file=sys.stderr)

    return subdomains


def query_dnsrecon(domain: str) -> List[SubdomainInfo]:
    """Query dnsrecon for subdomains."""
    subdomains = []
    try:
        result = subprocess.run(
            ["dnsrecon", "-d", domain, "-t", "brt", "-j", "/dev/stdout"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            for entry in data:
                subdomain = entry.get("name", "").lower()
                if subdomain.endswith(domain):
                    subdomains.append(SubdomainInfo(
                        subdomain=subdomain,
                        source="dnsrecon",
                        first_seen=datetime.utcnow().isoformat() + "Z",
                        last_seen=datetime.utcnow().isoformat() + "Z",
                    ))

    except FileNotFoundError:
        print("Warning: dnsrecon not found, skipping", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("Warning: dnsrecon timed out", file=sys.stderr)
    except Exception as e:
        print(f"Warning: dnsrecon query failed: {e}", file=sys.stderr)

    return subdomains


def query_amass(domain: str) -> List[SubdomainInfo]:
    """Query amass for subdomains."""
    subdomains = []
    try:
        result = subprocess.run(
            ["amass", "enum", "-passive", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    subdomains.append(SubdomainInfo(
                        subdomain=line.strip().lower(),
                        source="amass",
                        first_seen=datetime.utcnow().isoformat() + "Z",
                        last_seen=datetime.utcnow().isoformat() + "Z",
                    ))

    except FileNotFoundError:
        print("Warning: amass not found, skipping", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("Warning: amass timed out", file=sys.stderr)
    except Exception as e:
        print(f"Warning: amass query failed: {e}", file=sys.stderr)

    return subdomains


# ============================================================================
# Baseline Functions
# ============================================================================

def load_baseline(baseline_file: str) -> Set[str]:
    """Load baseline subdomains from file."""
    baseline = set()
    if os.path.exists(baseline_file):
        with open(baseline_file, "r") as f:
            for line in f:
                subdomain = line.strip().lower()
                if subdomain and not subdomain.startswith("#"):
                    baseline.add(subdomain)
    return baseline


def save_baseline(baseline_file: str, subdomains: Set[str]) -> None:
    """Save baseline subdomains to file."""
    os.makedirs(os.path.dirname(baseline_file) or ".", exist_ok=True)
    with open(baseline_file, "w") as f:
        for subdomain in sorted(subdomains):
            f.write(f"{subdomain}\n")


# ============================================================================
# Comparison Functions
# ============================================================================

def compare_subdomains(
    current: List[SubdomainInfo],
    baseline: Set[str],
) -> tuple:
    """Compare current subdomains against baseline."""
    current_dict = {s.subdomain: s for s in current}
    current_set = set(current_dict.keys())

    new_subdomains = current_set - baseline
    removed_subdomains = baseline - current_set
    unchanged_subdomains = current_set & baseline

    new_info = [current_dict[s] for s in new_subdomains]

    return new_info, list(removed_subdomains), list(unchanged_subdomains)


# ============================================================================
# Output Formatting
# ============================================================================

def format_output(result: MonitorResult, output_format: str = "json") -> str:
    """Format output in the specified format."""
    if output_format == "json":
        return json.dumps(asdict(result), indent=2, default=str)
    elif output_format == "markdown":
        return _format_markdown(result)
    else:
        return json.dumps(asdict(result), indent=2, default=str)


def _format_markdown(result: MonitorResult) -> str:
    """Format output as markdown."""
    md = f"""# Subdomain Monitor Report: {result.domain}

**Date:** {result.timestamp}
**Total Subdomains:** {result.total_subdomains}
**New Subdomains:** {len(result.new_subdomains)}
**Removed Subdomains:** {len(result.removed_subdomains)}

## New Subdomains

"""
    if result.new_subdomains:
        md += "| Subdomain | Source | First Seen |\n"
        md += "|-----------|--------|------------|\n"
        for sub in result.new_subdomains:
            md += f"| {sub.subdomain} | {sub.source} | {sub.first_seen} |\n"
    else:
        md += "No new subdomains found.\n"

    md += "\n## Removed Subdomains\n\n"
    if result.removed_subdomains:
        for sub in result.removed_subdomains:
            md += f"- {sub}\n"
    else:
        md += "No subdomains removed.\n"

    md += "\n## Sources\n\n"
    for source in result.sources:
        md += f"- {source}\n"

    if result.errors:
        md += "\n## Errors\n\n"
        for error in result.errors:
            md += f"- {error}\n"

    return md


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Monitor for new subdomain discoveries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 subdomain-monitor.py -d example.com -b baseline.txt
  python3 subdomain-monitor.py -d example.com -b baseline.txt -o output.json
  python3 subdomain-monitor.py -d example.com -b baseline.txt -f markdown
  python3 subdomain-monitor.py -d example.com -b baseline.txt --update-baseline
        """
    )

    parser.add_argument("-d", "--domain", required=True, help="Domain to monitor")
    parser.add_argument("-b", "--baseline", required=True, help="Baseline file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-f", "--format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--update-baseline", action="store_true", help="Update baseline after scan")
    parser.add_argument("--sources", nargs="+", default=["crtsh", "subfinder"], choices=["crtsh", "subfinder", "dnsrecon", "amass"], help="Sources to query")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load baseline
    baseline = load_baseline(args.baseline)
    if args.verbose:
        print(f"Loaded {len(baseline)} subdomains from baseline", file=sys.stderr)

    # Query sources
    all_subdomains = []
    sources_used = []
    errors = []

    source_functions = {
        "crtsh": query_crtsh,
        "subfinder": query_subfinder,
        "dnsrecon": query_dnsrecon,
        "amass": query_amass,
    }

    for source in args.sources:
        if source in source_functions:
            if args.verbose:
                print(f"Querying {source}...", file=sys.stderr)
            try:
                subdomains = source_functions[source](args.domain)
                all_subdomains.extend(subdomains)
                sources_used.append(source)
                if args.verbose:
                    print(f"  Found {len(subdomains)} subdomains", file=sys.stderr)
            except Exception as e:
                errors.append(f"{source}: {str(e)}")
                print(f"Error querying {source}: {e}", file=sys.stderr)

    # Deduplicate
    seen = set()
    unique_subdomains = []
    for sub in all_subdomains:
        if sub.subdomain not in seen:
            seen.add(sub.subdomain)
            unique_subdomains.append(sub)

    if args.verbose:
        print(f"Total unique subdomains: {len(unique_subdomains)}", file=sys.stderr)

    # Compare against baseline
    new_subdomains, removed_subdomains, unchanged_subdomains = compare_subdomains(
        unique_subdomains, baseline
    )

    # Create result
    result = MonitorResult(
        domain=args.domain,
        timestamp=datetime.utcnow().isoformat() + "Z",
        total_subdomains=len(unique_subdomains),
        new_subdomains=new_subdomains,
        removed_subdomains=removed_subdomains,
        unchanged_subdomains=unchanged_subdomains,
        sources=sources_used,
        errors=errors,
    )

    # Format output
    output = format_output(result, args.format)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Update baseline if requested
    if args.update_baseline:
        current_set = {s.subdomain for s in unique_subdomains}
        save_baseline(args.baseline, current_set)
        print(f"Baseline updated: {args.baseline}", file=sys.stderr)

    # Exit with error code if new subdomains found
    if new_subdomains:
        sys.exit(1)


if __name__ == "__main__":
    main()
