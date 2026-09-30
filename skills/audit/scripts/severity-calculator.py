#!/usr/bin/env python3
"""
severity-calculator.py

Calculates CVSS v3.1 scores from vector strings and maps to Immunefi severity
for web3. Outputs structured severity assessment.

Usage:
    python severity-calculator.py [OPTIONS] <command> [args]

Commands:
    calculate <vector>           Calculate CVSS score from vector string
    map <score>                  Map CVSS score to Immunefi severity
    batch <file>                 Process multiple vectors from file
    interactive                  Interactive mode

Options:
    -f, --format <json|text>     Output format (default: text)
    -v, --verbose                Verbose output
    -h, --help                   Show this help message

Examples:
    python severity-calculator.py calculate "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    python severity-calculator.py map 9.8
    python severity-calculator.py batch vectors.txt
    python severity-calculator.py interactive
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple


# ─── CVSS v3.1 Calculator ───────────────────────────────────────────────────

@dataclass
class CVSSMetrics:
    """CVSS v3.1 metrics."""
    # Base metrics
    av: str = "N"  # Attack Vector: N, A, L, P
    ac: str = "L"  # Attack Complexity: L, H
    pr: str = "N"  # Privileges Required: N, L, H
    ui: str = "N"  # User Interaction: N, R
    s: str = "U"   # Scope: U, C
    c: str = "N"   # Confidentiality: N, L, H
    i: str = "N"   # Integrity: N, L, H
    a: str = "N"   # Availability: N, L, H
    
    # Temporal metrics
    e: str = "X"   # Exploit Code Maturity: X, U, P, F, H
    rl: str = "X"  # Remediation Level: X, O, T, W, U
    rc: str = "X"  # Report Confidence: X, U, R, C
    
    # Environmental metrics
    cr: str = "X"  # Confidentiality Requirement: X, L, M, H
    ir: str = "X"  # Integrity Requirement: X, L, M, H
    ar: str = "X"  # Availability Requirement: X, L, M, H


# Metric values
AV_VALUES = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20}
AC_VALUES = {"L": 0.77, "H": 0.44}
PR_VALUES = {"N": 0.85, "L": 0.62, "H": 0.27}  # Scope Unchanged
PR_VALUES_SCOPED = {"N": 0.85, "L": 0.68, "H": 0.50}  # Scope Changed
UI_VALUES = {"N": 0.85, "R": 0.62}
CIA_VALUES = {"N": 0.0, "L": 0.22, "H": 0.56}

E_VALUES = {"X": 1.0, "U": 0.91, "P": 0.94, "F": 0.97, "H": 1.0}
RL_VALUES = {"X": 1.0, "O": 0.95, "T": 0.96, "W": 0.97, "U": 1.0}
RC_VALUES = {"X": 1.0, "U": 0.92, "R": 0.96, "C": 1.0}

CR_VALUES = {"X": 1.0, "L": 0.5, "M": 1.0, "H": 1.5}
IR_VALUES = {"X": 1.0, "L": 0.5, "M": 1.0, "H": 1.5}
AR_VALUES = {"X": 1.0, "L": 0.5, "M": 1.0, "H": 1.5}


def roundup(value: float) -> float:
    """Round up to 1 decimal place."""
    return math.ceil(value * 10) / 10


def parse_vector(vector: str) -> CVSSMetrics:
    """Parse CVSS vector string into metrics."""
    metrics = CVSSMetrics()
    
    # Remove prefix if present
    vector = vector.replace("CVSS:3.1/", "").replace("CVSS:3.0/", "")
    
    parts = vector.split("/")
    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        
        if key == "AV":
            metrics.av = value
        elif key == "AC":
            metrics.ac = value
        elif key == "PR":
            metrics.pr = value
        elif key == "UI":
            metrics.ui = value
        elif key == "S":
            metrics.s = value
        elif key == "C":
            metrics.c = value
        elif key == "I":
            metrics.i = value
        elif key == "A":
            metrics.a = value
        elif key == "E":
            metrics.e = value
        elif key == "RL":
            metrics.rl = value
        elif key == "RC":
            metrics.rc = value
        elif key == "CR":
            metrics.cr = value
        elif key == "IR":
            metrics.ir = value
        elif key == "AR":
            metrics.ar = value
    
    return metrics


def calculate_base_score(metrics: CVSSMetrics) -> float:
    """Calculate CVSS v3.1 base score."""
    # Get metric values
    av = AV_VALUES.get(metrics.av, 0.85)
    ac = AC_VALUES.get(metrics.ac, 0.77)
    
    if metrics.s == "C":
        pr = PR_VALUES_SCOPED.get(metrics.pr, 0.85)
    else:
        pr = PR_VALUES.get(metrics.pr, 0.85)
    
    ui = UI_VALUES.get(metrics.ui, 0.85)
    c = CIA_VALUES.get(metrics.c, 0.0)
    i = CIA_VALUES.get(metrics.i, 0.0)
    a = CIA_VALUES.get(metrics.a, 0.0)
    
    # Calculate impact
    impact = 1 - ((1 - c) * (1 - i) * (1 - a))
    
    if metrics.s == "U":
        impact = 6.42 * impact
    else:
        impact = 7.52 * (impact - 0.029) - 3.25 * (impact - 0.02) ** 15
    
    # Calculate exploitability
    exploitability = 8.22 * av * ac * pr * ui
    
    # Calculate base score
    if impact <= 0:
        return 0.0
    
    if metrics.s == "U":
        base_score = roundup(min(impact + exploitability, 10))
    else:
        base_score = roundup(min(1.08 * (impact + exploitability), 10))
    
    return base_score


def calculate_temporal_score(base_score: float, metrics: CVSSMetrics) -> float:
    """Calculate CVSS v3.1 temporal score."""
    e = E_VALUES.get(metrics.e, 1.0)
    rl = RL_VALUES.get(metrics.rl, 1.0)
    rc = RC_VALUES.get(metrics.rc, 1.0)
    
    temporal_score = roundup(base_score * e * rl * rc)
    return temporal_score


def calculate_environmental_score(metrics: CVSSMetrics) -> float:
    """Calculate CVSS v3.1 environmental score."""
    # Get metric values
    av = AV_VALUES.get(metrics.av, 0.85)
    ac = AC_VALUES.get(metrics.ac, 0.77)
    
    if metrics.s == "C":
        pr = PR_VALUES_SCOPED.get(metrics.pr, 0.85)
    else:
        pr = PR_VALUES.get(metrics.pr, 0.85)
    
    ui = UI_VALUES.get(metrics.ui, 0.85)
    c = CIA_VALUES.get(metrics.c, 0.0)
    i = CIA_VALUES.get(metrics.i, 0.0)
    a = CIA_VALUES.get(metrics.a, 0.0)
    
    cr = CR_VALUES.get(metrics.cr, 1.0)
    ir = IR_VALUES.get(metrics.ir, 1.0)
    ar = AR_VALUES.get(metrics.ar, 1.0)
    
    # Calculate modified impact
    modified_c = min(c * cr, 1.0)
    modified_i = min(i * ir, 1.0)
    modified_a = min(a * ar, 1.0)
    
    modified_impact = 1 - ((1 - modified_c) * (1 - modified_i) * (1 - modified_a))
    
    if metrics.s == "U":
        modified_impact = 6.42 * modified_impact
    else:
        modified_impact = 7.52 * (modified_impact - 0.029) - 3.25 * (modified_impact - 0.02) ** 15
    
    # Calculate modified exploitability
    modified_exploitability = 8.22 * av * ac * pr * ui
    
    # Calculate environmental score
    if modified_impact <= 0:
        return 0.0
    
    e = E_VALUES.get(metrics.e, 1.0)
    rl = RL_VALUES.get(metrics.rl, 1.0)
    rc = RC_VALUES.get(metrics.rc, 1.0)
    
    if metrics.s == "U":
        environmental_score = roundup(
            roundup(min(modified_impact + modified_exploitability, 10)) * e * rl * rc
        )
    else:
        environmental_score = roundup(
            roundup(min(1.08 * (modified_impact + modified_exploitability), 10)) * e * rl * rc
        )
    
    return environmental_score


def get_severity_rating(score: float) -> str:
    """Get severity rating from CVSS score."""
    if score == 0.0:
        return "None"
    elif score <= 3.9:
        return "Low"
    elif score <= 6.9:
        return "Medium"
    elif score <= 8.9:
        return "High"
    else:
        return "Critical"


def map_to_immunefi(score: float, is_web3: bool = True) -> str:
    """Map CVSS score to Immunefi severity."""
    if not is_web3:
        return get_severity_rating(score)
    
    # Immunefi mapping for web3
    if score >= 9.0:
        return "Critical"
    elif score >= 7.0:
        return "High"
    elif score >= 4.0:
        return "Medium"
    elif score >= 0.1:
        return "Low"
    else:
        return "Informational"


# ─── Severity Assessment ─────────────────────────────────────────────────────

@dataclass
class SeverityAssessment:
    """Complete severity assessment."""
    vector: str
    base_score: float
    temporal_score: Optional[float]
    environmental_score: Optional[float]
    severity_rating: str
    immunefi_severity: str
    metrics: Dict[str, str]
    rationale: str


def calculate_severity(vector: str, is_web3: bool = True) -> SeverityAssessment:
    """Calculate complete severity assessment from vector string."""
    metrics = parse_vector(vector)
    
    base_score = calculate_base_score(metrics)
    temporal_score = calculate_temporal_score(base_score, metrics)
    environmental_score = calculate_environmental_score(metrics)
    
    severity_rating = get_severity_rating(base_score)
    immunefi_severity = map_to_immunefi(base_score, is_web3)
    
    # Build rationale
    rationale_parts = []
    rationale_parts.append(f"Base Score: {base_score}")
    rationale_parts.append(f"Severity: {severity_rating}")
    if is_web3:
        rationale_parts.append(f"Immunefi: {immunefi_severity}")
    
    metrics_dict = {
        "Attack Vector": metrics.av,
        "Attack Complexity": metrics.ac,
        "Privileges Required": metrics.pr,
        "User Interaction": metrics.ui,
        "Scope": metrics.s,
        "Confidentiality": metrics.c,
        "Integrity": metrics.i,
        "Availability": metrics.a,
    }
    
    if metrics.e != "X":
        metrics_dict["Exploit Code Maturity"] = metrics.e
    if metrics.rl != "X":
        metrics_dict["Remediation Level"] = metrics.rl
    if metrics.rc != "X":
        metrics_dict["Report Confidence"] = metrics.rc
    
    return SeverityAssessment(
        vector=vector,
        base_score=base_score,
        temporal_score=temporal_score,
        environmental_score=environmental_score,
        severity_rating=severity_rating,
        immunefi_severity=immunefi_severity,
        metrics=metrics_dict,
        rationale=" | ".join(rationale_parts)
    )


# ─── Output Formatters ───────────────────────────────────────────────────────

def format_text(assessment: SeverityAssessment) -> str:
    """Format assessment as text."""
    lines = [
        "=" * 60,
        "SEVERITY ASSESSMENT",
        "=" * 60,
        "",
        f"Vector: {assessment.vector}",
        "",
        "Scores:",
        f"  Base Score:           {assessment.base_score}",
        f"  Temporal Score:       {assessment.temporal_score or 'N/A'}",
        f"  Environmental Score:  {assessment.environmental_score or 'N/A'}",
        "",
        "Severity:",
        f"  CVSS Rating:          {assessment.severity_rating}",
        f"  Immunefi Severity:    {assessment.immunefi_severity}",
        "",
        "Metrics:",
    ]
    
    for metric, value in assessment.metrics.items():
        lines.append(f"  {metric:<25} {value}")
    
    lines.extend([
        "",
        f"Rationale: {assessment.rationale}",
        "=" * 60,
    ])
    
    return "\n".join(lines)


def format_json(assessment: SeverityAssessment) -> str:
    """Format assessment as JSON."""
    data = {
        "vector": assessment.vector,
        "scores": {
            "base": assessment.base_score,
            "temporal": assessment.temporal_score,
            "environmental": assessment.environmental_score,
        },
        "severity": {
            "cvss_rating": assessment.severity_rating,
            "immunefi": assessment.immunefi_severity,
        },
        "metrics": assessment.metrics,
        "rationale": assessment.rationale,
    }
    return json.dumps(data, indent=2)


# ─── Interactive Mode ────────────────────────────────────────────────────────

def interactive_mode():
    """Run interactive severity calculator."""
    print("=" * 60)
    print("CVSS v3.1 Severity Calculator - Interactive Mode")
    print("=" * 60)
    print()
    print("Enter CVSS vector string (or 'quit' to exit):")
    print("Example: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    print()
    
    while True:
        try:
            vector = input("Vector: ").strip()
        except EOFError:
            break
        
        if vector.lower() in ("quit", "exit", "q"):
            break
        
        if not vector:
            continue
        
        try:
            assessment = calculate_severity(vector)
            print()
            print(format_text(assessment))
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()


# ─── Batch Processing ────────────────────────────────────────────────────────

def batch_process(filepath: str, output_format: str = "text"):
    """Process multiple vectors from file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    results = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        try:
            assessment = calculate_severity(line)
            results.append(assessment)
        except Exception as e:
            print(f"Error processing '{line}': {e}", file=sys.stderr)
    
    if output_format == "json":
        output = json.dumps([asdict(r) for r in results], indent=2)
        print(output)
    else:
        for assessment in results:
            print(format_text(assessment))
            print()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Calculate CVSS v3.1 scores and map to Immunefi severity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["calculate", "map", "batch", "interactive"],
        help="Command to execute"
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Command arguments"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "calculate":
        if not args.args:
            print("Error: 'calculate' command requires a vector string", file=sys.stderr)
            sys.exit(1)
        
        vector = args.args[0]
        assessment = calculate_severity(vector)
        
        if args.format == "json":
            print(format_json(assessment))
        else:
            print(format_text(assessment))
    
    elif args.command == "map":
        if not args.args:
            print("Error: 'map' command requires a score", file=sys.stderr)
            sys.exit(1)
        
        try:
            score = float(args.args[0])
        except ValueError:
            print("Error: Invalid score", file=sys.stderr)
            sys.exit(1)
        
        severity = get_severity_rating(score)
        immunefi = map_to_immunefi(score)
        
        if args.format == "json":
            print(json.dumps({
                "score": score,
                "cvss_rating": severity,
                "immunefi": immunefi
            }, indent=2))
        else:
            print(f"Score: {score}")
            print(f"CVSS Rating: {severity}")
            print(f"Immunefi Severity: {immunefi}")
    
    elif args.command == "batch":
        if not args.args:
            print("Error: 'batch' command requires a file path", file=sys.stderr)
            sys.exit(1)
        
        filepath = args.args[0]
        batch_process(filepath, args.format)
    
    elif args.command == "interactive":
        interactive_mode()


if __name__ == "__main__":
    main()
