#!/usr/bin/env python3
"""
Trend Analysis
Analyzes findings across engagements to identify trends and track remediation progress.

Supports:
- Recurring vulnerability type identification
- Remediation progress tracking
- Trend report generation
- Cross-engagement comparison

Usage:
    python trend-analysis.py --engagement engagement1.json engagement2.json
    python trend-analysis.py --engagement engagement1.json engagement2.json --output trend_report.md
    python trend-analysis.py --engagement-dir ./engagements/ --output trend_report.md
    python trend-analysis.py --engagement engagement1.json engagement2.json --format json
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Finding:
    """Represents a security finding."""
    id: str
    title: str
    severity: str
    category: str
    status: str
    date: str
    engagement: str
    cvss_score: Optional[float] = None
    cwe: Optional[str] = None
    swc: Optional[str] = None


@dataclass
class Engagement:
    """Represents a security engagement."""
    name: str
    date: str
    client: str
    findings: list = field(default_factory=list)


def load_engagement(filepath: str) -> Engagement:
    """Load an engagement from a JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)

    engagement = Engagement(
        name=data.get("name", Path(filepath).stem),
        date=data.get("date", "Unknown"),
        client=data.get("client", "Unknown"),
    )

    for finding_data in data.get("findings", []):
        finding = Finding(
            id=finding_data.get("id", "Unknown"),
            title=finding_data.get("title", "Unknown"),
            severity=finding_data.get("severity", "Unknown"),
            category=finding_data.get("category", "Unknown"),
            status=finding_data.get("status", "Open"),
            date=finding_data.get("date", engagement.date),
            engagement=engagement.name,
            cvss_score=finding_data.get("cvss_score"),
            cwe=finding_data.get("cwe"),
            swc=finding_data.get("swc"),
        )
        engagement.findings.append(finding)

    return engagement


def load_engagement_dir(dirpath: str) -> list:
    """Load all engagements from a directory."""
    engagements = []
    path = Path(dirpath)

    for json_file in sorted(path.glob("*.json")):
        try:
            engagement = load_engagement(str(json_file))
            engagements.append(engagement)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {json_file}: {e}", file=sys.stderr)

    return engagements


def analyze_recurring_vulnerabilities(engagements: list) -> dict:
    """Identify recurring vulnerability types across engagements."""
    category_counter = Counter()
    cwe_counter = Counter()
    swc_counter = Counter()

    for engagement in engagements:
        for finding in engagement.findings:
            category_counter[finding.category] += 1
            if finding.cwe:
                cwe_counter[finding.cwe] += 1
            if finding.swc:
                swc_counter[finding.swc] += 1

    return {
        "categories": category_counter.most_common(),
        "cwes": cwe_counter.most_common(),
        "swcs": swc_counter.most_common(),
    }


def analyze_remediation_progress(engagements: list) -> dict:
    """Track remediation progress across engagements."""
    status_counter = Counter()
    severity_status = defaultdict(Counter)

    for engagement in engagements:
        for finding in engagement.findings:
            status_counter[finding.status] += 1
            severity_status[finding.severity][finding.status] += 1

    return {
        "overall_status": status_counter.most_common(),
        "severity_status": {sev: dict(counts) for sev, counts in severity_status.items()},
    }


def analyze_severity_trends(engagements: list) -> dict:
    """Analyze severity trends across engagements."""
    severity_by_engagement = {}

    for engagement in engagements:
        severity_counter = Counter()
        for finding in engagement.findings:
            severity_counter[finding.severity] += 1
        severity_by_engagement[engagement.name] = dict(severity_counter)

    return severity_by_engagement


def analyze_cvss_trends(engagements: list) -> dict:
    """Analyze CVSS score trends across engagements."""
    cvss_by_engagement = {}

    for engagement in engagements:
        scores = [f.cvss_score for f in engagement.findings if f.cvss_score is not None]
        if scores:
            cvss_by_engagement[engagement.name] = {
                "count": len(scores),
                "average": round(sum(scores) / len(scores), 2),
                "highest": max(scores),
                "lowest": min(scores),
            }

    return cvss_by_engagement


def generate_trend_report(engagements: list, output_format: str = "markdown") -> str:
    """Generate a trend report from engagement data."""
    recurring = analyze_recurring_vulnerabilities(engagements)
    remediation = analyze_remediation_progress(engagements)
    severity_trends = analyze_severity_trends(engagements)
    cvss_trends = analyze_cvss_trends(engagements)

    if output_format == "json":
        return json.dumps({
            "recurring_vulnerabilities": {
                "categories": recurring["categories"],
                "cwes": recurring["cwes"],
                "swcs": recurring["swcs"],
            },
            "remediation_progress": remediation,
            "severity_trends": severity_trends,
            "cvss_trends": cvss_trends,
        }, indent=2)

    # Markdown report
    lines = [
        "# Security Trend Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Engagements Analyzed:** {len(engagements)}",
        "",
        "---",
        "",
        "## 1. Recurring Vulnerability Types",
        "",
        "### 1.1 By Category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]

    for category, count in recurring["categories"]:
        lines.append(f"| {category} | {count} |")

    if recurring["cwes"]:
        lines.extend([
            "",
            "### 1.2 By CWE",
            "",
            "| CWE | Count |",
            "|-----|-------|",
        ])
        for cwe, count in recurring["cwes"]:
            lines.append(f"| {cwe} | {count} |")

    if recurring["swcs"]:
        lines.extend([
            "",
            "### 1.3 By SWC",
            "",
            "| SWC | Count |",
            "|-----|-------|",
        ])
        for swc, count in recurring["swcs"]:
            lines.append(f"| {swc} | {count} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Remediation Progress",
        "",
        "### 2.1 Overall Status",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ])

    for status, count in remediation["overall_status"]:
        lines.append(f"| {status} | {count} |")

    lines.extend([
        "",
        "### 2.2 Status by Severity",
        "",
        "| Severity | Open | Verified | Fixed | Acknowledged |",
        "|----------|------|----------|-------|-------------|",
    ])

    for severity in ["Critical", "High", "Medium", "Low", "Informational"]:
        if severity in remediation["severity_status"]:
            counts = remediation["severity_status"][severity]
            lines.append(
                f"| {severity} | {counts.get('Open', 0)} | {counts.get('Verified', 0)} | "
                f"{counts.get('Fixed', 0)} | {counts.get('Acknowledged', 0)} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Severity Trends",
        "",
        "| Engagement | Critical | High | Medium | Low | Informational |",
        "|------------|----------|------|--------|-----|---------------|",
    ])

    for engagement_name, severities in severity_trends.items():
        lines.append(
            f"| {engagement_name} | {severities.get('Critical', 0)} | "
            f"{severities.get('High', 0)} | {severities.get('Medium', 0)} | "
            f"{severities.get('Low', 0)} | {severities.get('Informational', 0)} |"
        )

    if cvss_trends:
        lines.extend([
            "",
            "---",
            "",
            "## 4. CVSS Score Trends",
            "",
            "| Engagement | Count | Average | Highest | Lowest |",
            "|------------|-------|---------|---------|--------|",
        ])
        for engagement_name, stats in cvss_trends.items():
            lines.append(
                f"| {engagement_name} | {stats['count']} | {stats['average']} | "
                f"{stats['highest']} | {stats['lowest']} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## 5. Recommendations",
        "",
    ])

    # Generate recommendations based on trends
    if recurring["categories"]:
        top_category = recurring["categories"][0]
        lines.append(f"1. **Address recurring {top_category[0]} issues:** This category appeared {top_category[1]} times across engagements. Consider implementing targeted controls and training.")

    if remediation["overall_status"]:
        open_count = next((c for s, c in remediation["overall_status"] if s == "Open"), 0)
        fixed_count = next((c for s, c in remediation["overall_status"] if s == "Fixed"), 0)
        if open_count > fixed_count:
            lines.append(f"2. **Improve remediation velocity:** {open_count} findings remain open while {fixed_count} have been fixed. Consider increasing remediation resources.")

    lines.append(f"3. **Continue monitoring:** Regular trend analysis helps identify systemic issues and measure security program effectiveness.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze findings across engagements to identify trends.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --engagement engagement1.json engagement2.json
  %(prog)s --engagement-dir ./engagements/ --output trend_report.md
  %(prog)s --engagement engagement1.json engagement2.json --format json
        """,
    )

    parser.add_argument(
        "--engagement",
        nargs="+",
        help="Engagement JSON files to analyze",
    )
    parser.add_argument(
        "--engagement-dir",
        help="Directory containing engagement JSON files",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    args = parser.parse_args()

    if not args.engagement and not args.engagement_dir:
        parser.error("Either --engagement or --engagement-dir is required")

    engagements = []

    if args.engagement:
        for filepath in args.engagement:
            try:
                engagement = load_engagement(filepath)
                engagements.append(engagement)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {filepath}: {e}", file=sys.stderr)
                sys.exit(1)

    if args.engagement_dir:
        engagements.extend(load_engagement_dir(args.engagement_dir))

    if not engagements:
        print("No engagements loaded.", file=sys.stderr)
        sys.exit(1)

    report = generate_trend_report(engagements, args.format)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Trend report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
