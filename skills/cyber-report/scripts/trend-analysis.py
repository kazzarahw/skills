#!/usr/bin/env python3
"""
Trend Analysis Script for Penetration Testing Engagements

Analyzes findings across multiple engagement reports to identify trends,
patterns, and improvement areas.

Usage:
    python trend-analysis.py --input reports/ --output trend-report.html
    python trend-analysis.py --input reports/ --format json
    python trend-analysis.py --input reports/ --start-date 2024-01-01 --end-date 2024-12-31
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import csv
import html


@dataclass
class Finding:
    """Represents a single finding from an engagement report."""
    finding_id: str
    title: str
    severity: str
    category: str
    cvss_score: float
    status: str = "open"
    date_identified: str = ""
    date_remediated: str = ""
    engagement_id: str = ""
    target: str = ""
    cve_ids: List[str] = field(default_factory=list)
    description: str = ""
    remediation: str = ""


@dataclass
class Engagement:
    """Represents a penetration testing engagement."""
    engagement_id: str
    name: str
    start_date: str
    end_date: str
    target_scope: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    tester: str = ""
    classification: str = "CONFIDENTIAL"


class TrendAnalyzer:
    """Analyzes findings across multiple engagements to identify trends."""

    SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0}

    def __init__(self, engagements: List[Engagement]):
        self.engagements = engagements
        self.all_findings: List[Finding] = []
        for eng in engagements:
            self.all_findings.extend(eng.findings)

    def severity_trend(self) -> Dict[str, Any]:
        """
        Analyze severity distribution trend across engagements.

        Returns:
            Dictionary with severity counts, percentages, and trend data.
        """
        severity_by_engagement = {}
        overall_counts = Counter()

        for eng in self.engagements:
            eng_severities = Counter(f.severity.lower() for f in eng.findings)
            severity_by_engagement[eng.engagement_id] = dict(eng_severities)
            overall_counts.update(eng_severities)

        total = sum(overall_counts.values())
        percentages = {
            sev: round((count / total) * 100, 2) if total > 0 else 0
            for sev, count in overall_counts.items()
        }

        # Calculate trend (increasing/decreasing/stable)
        trend = self._calculate_severity_trend(severity_by_engagement)

        return {
            "total_findings": total,
            "severity_counts": dict(overall_counts),
            "severity_percentages": percentages,
            "by_engagement": severity_by_engagement,
            "trend": trend,
        }

    def _calculate_severity_trend(self, severity_by_engagement: Dict) -> str:
        """Calculate if severity trend is increasing, decreasing, or stable."""
        if len(self.engagements) < 2:
            return "insufficient_data"

        sorted_engs = sorted(self.engagements, key=lambda e: e.start_date)
        first_eng = sorted_engs[0]
        last_eng = sorted_engs[-1]

        first_high = sum(
            1 for f in first_eng.findings
            if f.severity.lower() in ("critical", "high")
        )
        last_high = sum(
            1 for f in last_eng.findings
            if f.severity.lower() in ("critical", "high")
        )

        first_total = len(first_eng.findings)
        last_total = len(last_eng.findings)

        if first_total == 0 or last_total == 0:
            return "insufficient_data"

        first_ratio = first_high / first_total
        last_ratio = last_high / last_total

        if last_ratio > first_ratio * 1.1:
            return "increasing"
        elif last_ratio < first_ratio * 0.9:
            return "decreasing"
        else:
            return "stable"

    def category_trend(self) -> Dict[str, Any]:
        """
        Analyze category distribution trend across engagements.

        Returns:
            Dictionary with category counts, percentages, and trend data.
        """
        category_by_engagement = {}
        overall_counts = Counter()

        for eng in self.engagements:
            eng_categories = Counter(f.category for f in eng.findings)
            category_by_engagement[eng.engagement_id] = dict(eng_categories)
            overall_counts.update(eng_categories)

        total = sum(overall_counts.values())
        percentages = {
            cat: round((count / total) * 100, 2) if total > 0 else 0
            for cat, count in overall_counts.items()
        }

        # Find most common categories
        most_common = overall_counts.most_common(5)

        return {
            "total_findings": total,
            "category_counts": dict(overall_counts),
            "category_percentages": percentages,
            "by_engagement": category_by_engagement,
            "most_common": most_common,
        }

    def remediation_rate(self) -> Dict[str, Any]:
        """
        Analyze remediation rate across engagements.

        Returns:
            Dictionary with remediation statistics.
        """
        total_findings = len(self.all_findings)
        remediated = sum(1 for f in self.all_findings if f.status.lower() == "remediated")
        open_findings = sum(1 for f in self.all_findings if f.status.lower() == "open")
        in_progress = sum(1 for f in self.all_findings if f.status.lower() == "in_progress")

        remediation_rate = (remediated / total_findings * 100) if total_findings > 0 else 0

        # Calculate average remediation time
        remediation_times = []
        for f in self.all_findings:
            if f.status.lower() == "remediated" and f.date_identified and f.date_remediated:
                try:
                    identified = datetime.strptime(f.date_identified, "%Y-%m-%d")
                    remediated_date = datetime.strptime(f.date_remediated, "%Y-%m-%d")
                    days = (remediated_date - identified).days
                    remediation_times.append(days)
                except ValueError:
                    continue

        avg_remediation_time = (
            sum(remediation_times) / len(remediation_times) if remediation_times else 0
        )

        # Remediation rate by severity
        severity_remediation = {}
        for severity in self.SEVERITY_ORDER:
            sev_findings = [f for f in self.all_findings if f.severity.lower() == severity]
            sev_remediated = sum(1 for f in sev_findings if f.status.lower() == "remediated")
            sev_rate = (sev_remediated / len(sev_findings) * 100) if sev_findings else 0
            severity_remediation[severity] = {
                "total": len(sev_findings),
                "remediated": sev_remediated,
                "rate": round(sev_rate, 2),
            }

        return {
            "total_findings": total_findings,
            "remediated": remediated,
            "open": open_findings,
            "in_progress": in_progress,
            "remediation_rate": round(remediation_rate, 2),
            "average_remediation_days": round(avg_remediation_time, 1),
            "by_severity": severity_remediation,
        }

    def recurring_findings(self) -> Dict[str, Any]:
        """
        Identify recurring findings across engagements.

        Returns:
            Dictionary with recurring finding patterns.
        """
        # Group findings by title similarity
        title_groups = defaultdict(list)
        for f in self.all_findings:
            # Normalize title for comparison
            normalized = f.title.lower().strip()
            title_groups[normalized].append(f)

        # Find recurring findings (appearing in multiple engagements)
        recurring = {}
        for title, findings in title_groups.items():
            engagements_affected = set(f.engagement_id for f in findings)
            if len(engagements_affected) > 1:
                recurring[title] = {
                    "count": len(findings),
                    "engagements": list(engagements_affected),
                    "severity": findings[0].severity,
                    "category": findings[0].category,
                    "finding_ids": [f.finding_id for f in findings],
                }

        # Sort by count (most recurring first)
        sorted_recurring = dict(
            sorted(recurring.items(), key=lambda x: x[1]["count"], reverse=True)
        )

        return {
            "total_recurring": len(recurring),
            "recurring_findings": sorted_recurring,
        }

    def generate_report(self, output_format: str = "html") -> str:
        """
        Generate a trend analysis report.

        Args:
            output_format: Output format (html, json, csv, markdown)

        Returns:
            Report content as string.
        """
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "csv":
            return self._generate_csv_report()
        elif output_format == "markdown":
            return self._generate_markdown_report()
        else:
            return self._generate_html_report()

    def _generate_json_report(self) -> str:
        """Generate JSON format report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_engagements": len(self.engagements),
            "total_findings": len(self.all_findings),
            "severity_trend": self.severity_trend(),
            "category_trend": self.category_trend(),
            "remediation_rate": self.remediation_rate(),
            "recurring_findings": self.recurring_findings(),
        }
        return json.dumps(report, indent=2, default=str)

    def _generate_csv_report(self) -> str:
        """Generate CSV format report."""
        output = []
        output.append("Metric,Value,Details")

        sev_trend = self.severity_trend()
        for sev, count in sev_trend["severity_counts"].items():
            output.append(f"Severity {sev},{count},{sev_trend['severity_percentages'][sev]}%")

        cat_trend = self.category_trend()
        for cat, count in cat_trend["category_counts"].items():
            output.append(f"Category {cat},{count},{cat_trend['category_percentages'][cat]}%")

        rem_rate = self.remediation_rate()
        output.append(f"Remediation Rate,{rem_rate['remediation_rate']}%,")
        output.append(f"Avg Remediation Days,{rem_rate['average_remediation_days']},")

        return "\n".join(output)

    def _generate_markdown_report(self) -> str:
        """Generate Markdown format report."""
        lines = []
        lines.append("# Trend Analysis Report")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\nTotal Engagements: {len(self.engagements)}")
        lines.append(f"Total Findings: {len(self.all_findings)}")

        # Severity Trend
        lines.append("\n## Severity Trend")
        sev_trend = self.severity_trend()
        lines.append(f"\nTrend: {sev_trend['trend']}")
        lines.append("\n| Severity | Count | Percentage |")
        lines.append("|----------|-------|------------|")
        for sev, count in sev_trend["severity_counts"].items():
            pct = sev_trend["severity_percentages"][sev]
            lines.append(f"| {sev.upper()} | {count} | {pct}% |")

        # Category Trend
        lines.append("\n## Category Trend")
        cat_trend = self.category_trend()
        lines.append("\n| Category | Count | Percentage |")
        lines.append("|----------|-------|------------|")
        for cat, count in cat_trend["category_counts"].items():
            pct = cat_trend["category_percentages"][cat]
            lines.append(f"| {cat} | {count} | {pct}% |")

        # Remediation Rate
        lines.append("\n## Remediation Rate")
        rem_rate = self.remediation_rate()
        lines.append(f"\nOverall Rate: {rem_rate['remediation_rate']}%")
        lines.append(f"Average Remediation Time: {rem_rate['average_remediation_days']} days")
        lines.append("\n| Severity | Total | Remediated | Rate |")
        lines.append("|----------|-------|------------|------|")
        for sev, data in rem_rate["by_severity"].items():
            lines.append(f"| {sev.upper()} | {data['total']} | {data['remediated']} | {data['rate']}% |")

        # Recurring Findings
        lines.append("\n## Recurring Findings")
        recurring = self.recurring_findings()
        lines.append(f"\nTotal Recurring: {recurring['total_recurring']}")
        if recurring["recurring_findings"]:
            lines.append("\n| Finding | Count | Engagements | Severity |")
            lines.append("|---------|-------|-------------|----------|")
            for title, data in list(recurring["recurring_findings"].items())[:10]:
                lines.append(f"| {title} | {data['count']} | {len(data['engagements'])} | {data['severity']} |")

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        """Generate HTML format report."""
        sev_trend = self.severity_trend()
        cat_trend = self.category_trend()
        rem_rate = self.remediation_rate()
        recurring = self.recurring_findings()

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trend Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007bff; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .severity-critical {{ color: #dc3545; font-weight: bold; }}
        .severity-high {{ color: #fd7e14; font-weight: bold; }}
        .severity-medium {{ color: #ffc107; font-weight: bold; }}
        .severity-low {{ color: #28a745; font-weight: bold; }}
        .severity-informational {{ color: #6c757d; }}
        .trend-up {{ color: #dc3545; }}
        .trend-down {{ color: #28a745; }}
        .trend-stable {{ color: #6c757d; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Trend Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{len(self.engagements)}</div>
                <div class="metric-label">Engagements</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(self.all_findings)}</div>
                <div class="metric-label">Total Findings</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{rem_rate['remediation_rate']}%</div>
                <div class="metric-label">Remediation Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{rem_rate['average_remediation_days']}</div>
                <div class="metric-label">Avg Remediation Days</div>
            </div>
        </div>

        <h2>Severity Distribution</h2>
        <p>Trend: <span class="trend-{sev_trend['trend']}">{sev_trend['trend'].upper()}</span></p>
        <table>
            <tr><th>Severity</th><th>Count</th><th>Percentage</th></tr>
"""

        for sev, count in sev_trend["severity_counts"].items():
            pct = sev_trend["severity_percentages"][sev]
            html_content += f"""            <tr>
                <td class="severity-{sev}">{sev.upper()}</td>
                <td>{count}</td>
                <td>{pct}%</td>
            </tr>
"""

        html_content += """        </table>

        <h2>Category Distribution</h2>
        <table>
            <tr><th>Category</th><th>Count</th><th>Percentage</th></tr>
"""

        for cat, count in cat_trend["category_counts"].items():
            pct = cat_trend["category_percentages"][cat]
            html_content += f"""            <tr>
                <td>{html.escape(cat)}</td>
                <td>{count}</td>
                <td>{pct}%</td>
            </tr>
"""

        html_content += """        </table>

        <h2>Remediation by Severity</h2>
        <table>
            <tr><th>Severity</th><th>Total</th><th>Remediated</th><th>Rate</th></tr>
"""

        for sev, data in rem_rate["by_severity"].items():
            html_content += f"""            <tr>
                <td class="severity-{sev}">{sev.upper()}</td>
                <td>{data['total']}</td>
                <td>{data['remediated']}</td>
                <td>{data['rate']}%</td>
            </tr>
"""

        html_content += f"""        </table>

        <h2>Recurring Findings</h2>
        <p>Total Recurring: {recurring['total_recurring']}</p>
"""

        if recurring["recurring_findings"]:
            html_content += """        <table>
            <tr><th>Finding</th><th>Count</th><th>Engagements</th><th>Severity</th></tr>
"""
            for title, data in list(recurring["recurring_findings"].items())[:10]:
                html_content += f"""            <tr>
                <td>{html.escape(title)}</td>
                <td>{data['count']}</td>
                <td>{len(data['engagements'])}</td>
                <td class="severity-{data['severity'].lower()}">{data['severity']}</td>
            </tr>
"""
            html_content += "        </table>\n"

        html_content += f"""
        <div class="footer">
            <p>Report generated by TrendAnalyzer | Classification: CONFIDENTIAL</p>
        </div>
    </div>
</body>
</html>
"""

        return html_content


def load_engagements_from_directory(directory: str) -> List[Engagement]:
    """Load engagement data from JSON files in directory."""
    engagements = []
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for json_file in dir_path.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            findings = []
            for f_data in data.get("findings", []):
                finding = Finding(
                    finding_id=f_data.get("finding_id", ""),
                    title=f_data.get("title", ""),
                    severity=f_data.get("severity", "informational"),
                    category=f_data.get("category", "unknown"),
                    cvss_score=f_data.get("cvss_score", 0.0),
                    status=f_data.get("status", "open"),
                    date_identified=f_data.get("date_identified", ""),
                    date_remediated=f_data.get("date_remediated", ""),
                    engagement_id=data.get("engagement_id", ""),
                    target=f_data.get("target", ""),
                    cve_ids=f_data.get("cve_ids", []),
                    description=f_data.get("description", ""),
                    remediation=f_data.get("remediation", ""),
                )
                findings.append(finding)

            engagement = Engagement(
                engagement_id=data.get("engagement_id", ""),
                name=data.get("name", ""),
                start_date=data.get("start_date", ""),
                end_date=data.get("end_date", ""),
                target_scope=data.get("target_scope", []),
                findings=findings,
                tester=data.get("tester", ""),
                classification=data.get("classification", "CONFIDENTIAL"),
            )
            engagements.append(engagement)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse {json_file}: {e}", file=sys.stderr)
            continue

    return engagements


def main():
    """Main entry point for the trend analysis script."""
    parser = argparse.ArgumentParser(
        description="Analyze findings across multiple penetration testing engagements."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Directory containing engagement JSON files"
    )
    parser.add_argument(
        "--output", "-o",
        default="trend-report.html",
        help="Output file path (default: trend-report.html)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["html", "json", "csv", "markdown"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--start-date",
        help="Filter engagements from this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        help="Filter engagements until this date (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    try:
        # Load engagements
        engagements = load_engagements_from_directory(args.input)

        if not engagements:
            print("Error: No valid engagement files found.", file=sys.stderr)
            sys.exit(1)

        # Filter by date if specified
        if args.start_date or args.end_date:
            filtered = []
            for eng in engagements:
                try:
                    eng_date = datetime.strptime(eng.start_date, "%Y-%m-%d").date()
                    if args.start_date:
                        start = datetime.strptime(args.start_date, "%Y-%m-%d").date()
                        if eng_date < start:
                            continue
                    if args.end_date:
                        end = datetime.strptime(args.end_date, "%Y-%m-%d").date()
                        if eng_date > end:
                            continue
                    filtered.append(eng)
                except ValueError:
                    continue
            engagements = filtered

        # Analyze trends
        analyzer = TrendAnalyzer(engagements)
        report = analyzer.generate_report(args.format)

        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(report)

        print(f"Report generated: {args.output}")
        print(f"Engagements analyzed: {len(engagements)}")
        print(f"Total findings: {len(analyzer.all_findings)}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
