#!/usr/bin/env python3
"""
Severity Calculator
Calculates CVSS v3.1 scores from vector strings and maps to Immunefi severity.

Supports:
- CVSS v3.1 base score calculation
- CVSS v3.1 temporal score calculation
- CVSS v3.1 environmental score calculation
- Immunefi severity mapping for web3
- Batch processing from file

Usage:
    python severity-calculator.py --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    python severity-calculator.py --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" --temporal "E:F/RL:O/RC:C"
    python severity-calculator.py --batch vectors.txt
    python severity-calculator.py --immunefi --impact "Loss of funds > 10% TVL" --likelihood high
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from typing import Optional


# CVSS v3.1 metric weights
CVSS_WEIGHTS = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.20},
    "AC": {"L": 0.77, "H": 0.44},
    "PR": {"N": 0.85, "L": 0.62, "H": 0.27},  # Scope unchanged
    "PR_C": {"N": 0.85, "L": 0.68, "H": 0.50},  # Scope changed
    "UI": {"N": 0.85, "R": 0.62},
    "C": {"N": 0.00, "L": 0.22, "H": 0.56},
    "I": {"N": 0.00, "L": 0.22, "H": 0.56},
    "A": {"N": 0.00, "L": 0.22, "H": 0.56},
}

# Temporal metric weights
TEMPORAL_WEIGHTS = {
    "E": {"X": 1.0, "U": 0.91, "P": 0.94, "F": 0.97, "H": 1.0},
    "RL": {"X": 1.0, "O": 0.95, "T": 0.96, "W": 0.97, "U": 1.0},
    "RC": {"X": 1.0, "U": 0.92, "R": 0.96, "C": 1.0},
}

# Environmental requirement weights
ENV_WEIGHTS = {
    "CR": {"L": 0.5, "M": 1.0, "H": 1.5, "X": 1.0},
    "IR": {"L": 0.5, "M": 1.0, "H": 1.5, "X": 1.0},
    "AR": {"L": 0.5, "M": 1.0, "H": 1.5, "X": 1.0},
}


@dataclass
class CVSSVector:
    """Represents a CVSS v3.1 vector."""
    AV: str = "N"
    AC: str = "L"
    PR: str = "N"
    UI: str = "N"
    S: str = "U"
    C: str = "N"
    I: str = "N"
    A: str = "N"

    # Temporal metrics
    E: str = "X"
    RL: str = "X"
    RC: str = "X"

    # Environmental metrics
    MAV: str = "X"
    MAC: str = "X"
    MPR: str = "X"
    MUI: str = "X"
    MS: str = "X"
    MC: str = "X"
    MI: str = "X"
    MA: str = "X"
    CR: str = "X"
    IR: str = "X"
    AR: str = "X"


@dataclass
class CVSSResult:
    """Represents a CVSS calculation result."""
    vector: str
    base_score: float
    base_severity: str
    temporal_score: Optional[float] = None
    temporal_severity: Optional[str] = None
    environmental_score: Optional[float] = None
    environmental_severity: Optional[str] = None
    impact: float = 0.0
    exploitability: float = 0.0


def round_up(value: float) -> float:
    """Round up to 1 decimal place (CVSS standard)."""
    return math.ceil(value * 10) / 10


def parse_vector(vector_string: str) -> CVSSVector:
    """Parse a CVSS v3.1 vector string into a CVSSVector object."""
    # Remove prefix if present
    vector_string = vector_string.replace("CVSS:3.1/", "").replace("CVSS:3.0/", "")

    metrics = {}
    for part in vector_string.split("/"):
        if ":" in part:
            key, value = part.split(":", 1)
            metrics[key] = value

    return CVSSVector(**metrics)


def calculate_impact(vector: CVSSVector, scope_changed: bool = False) -> float:
    """Calculate the impact sub-score."""
    c = CVSS_WEIGHTS["C"][vector.C]
    i = CVSS_WEIGHTS["I"][vector.I]
    a = CVSS_WEIGHTS["A"][vector.A]

    impact = 1 - ((1 - c) * (1 - i) * (1 - a))

    if scope_changed:
        impact = 7.52 * (impact - 0.029) - 3.25 * (impact - 0.02) ** 15
    else:
        impact = 6.42 * impact

    return impact


def calculate_exploitability(vector: CVSSVector, scope_changed: bool = False) -> float:
    """Calculate the exploitability sub-score."""
    av = CVSS_WEIGHTS["AV"][vector.AV]
    ac = CVSS_WEIGHTS["AC"][vector.AC]

    if scope_changed:
        pr = CVSS_WEIGHTS["PR_C"][vector.PR]
    else:
        pr = CVSS_WEIGHTS["PR"][vector.PR]

    ui = CVSS_WEIGHTS["UI"][vector.UI]

    return 8.22 * av * ac * pr * ui


def get_severity_rating(score: float) -> str:
    """Get the qualitative severity rating from a score."""
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


def calculate_base_score(vector: CVSSVector) -> CVSSResult:
    """Calculate the CVSS v3.1 base score."""
    scope_changed = vector.S == "C"

    impact = calculate_impact(vector, scope_changed)
    exploitability = calculate_exploitability(vector, scope_changed)

    if impact <= 0:
        base_score = 0.0
    elif scope_changed:
        base_score = round_up(min(1.08 * (impact + exploitability), 10))
    else:
        base_score = round_up(min(impact + exploitability, 10))

    return CVSSResult(
        vector=f"CVSS:3.1/AV:{vector.AV}/AC:{vector.AC}/PR:{vector.PR}/UI:{vector.UI}/S:{vector.S}/C:{vector.C}/I:{vector.I}/A:{vector.A}",
        base_score=base_score,
        base_severity=get_severity_rating(base_score),
        impact=round(impact, 3),
        exploitability=round(exploitability, 3),
    )


def calculate_temporal_score(result: CVSSResult, vector: CVSSVector) -> CVSSResult:
    """Calculate the CVSS v3.1 temporal score."""
    e = TEMPORAL_WEIGHTS["E"][vector.E]
    rl = TEMPORAL_WEIGHTS["RL"][vector.RL]
    rc = TEMPORAL_WEIGHTS["RC"][vector.RC]

    temporal_score = round_up(result.base_score * e * rl * rc)

    result.temporal_score = temporal_score
    result.temporal_severity = get_severity_rating(temporal_score)

    return result


def calculate_environmental_score(result: CVSSResult, vector: CVSSVector) -> CVSSResult:
    """Calculate the CVSS v3.1 environmental score."""
    # Use modified metrics if defined, otherwise use base metrics
    mav = CVSS_WEIGHTS["AV"].get(vector.MAV, CVSS_WEIGHTS["AV"][vector.AV])
    mac = CVSS_WEIGHTS["AC"].get(vector.MAC, CVSS_WEIGHTS["AC"][vector.AC])

    ms = vector.MS if vector.MS != "X" else vector.S
    scope_changed = ms == "C"

    if scope_changed:
        mpr = CVSS_WEIGHTS["PR_C"].get(vector.MPR, CVSS_WEIGHTS["PR_C"][vector.PR])
    else:
        mpr = CVSS_WEIGHTS["PR"].get(vector.MPR, CVSS_WEIGHTS["PR"][vector.PR])

    mui = CVSS_WEIGHTS["UI"].get(vector.MUI, CVSS_WEIGHTS["UI"][vector.UI])

    mc = CVSS_WEIGHTS["C"].get(vector.MC, CVSS_WEIGHTS["C"][vector.C])
    mi = CVSS_WEIGHTS["I"].get(vector.MI, CVSS_WEIGHTS["I"][vector.I])
    ma = CVSS_WEIGHTS["A"].get(vector.MA, CVSS_WEIGHTS["A"][vector.A])

    cr = ENV_WEIGHTS["CR"][vector.CR]
    ir = ENV_WEIGHTS["IR"][vector.IR]
    ar = ENV_WEIGHTS["AR"][vector.AR]

    modified_impact = 1 - ((1 - mc * cr) * (1 - mi * ir) * (1 - ma * ar))

    if scope_changed:
        modified_impact = 7.52 * (modified_impact - 0.029) - 3.25 * (modified_impact - 0.02) ** 15
    else:
        modified_impact = 6.42 * modified_impact

    modified_exploitability = 8.22 * mav * mac * mpr * mui

    if modified_impact <= 0:
        environmental_score = 0.0
    elif scope_changed:
        environmental_score = round_up(
            round_up(min(1.08 * (modified_impact + modified_exploitability), 10))
            * TEMPORAL_WEIGHTS["E"][vector.E]
            * TEMPORAL_WEIGHTS["RL"][vector.RL]
            * TEMPORAL_WEIGHTS["RC"][vector.RC]
        )
    else:
        environmental_score = round_up(
            round_up(min(modified_impact + modified_exploitability, 10))
            * TEMPORAL_WEIGHTS["E"][vector.E]
            * TEMPORAL_WEIGHTS["RL"][vector.RL]
            * TEMPORAL_WEIGHTS["RC"][vector.RC]
        )

    result.environmental_score = environmental_score
    result.environmental_severity = get_severity_rating(environmental_score)

    return result


def calculate_cvss(vector_string: str, temporal: bool = False, environmental: bool = False) -> CVSSResult:
    """Calculate CVSS v3.1 scores from a vector string."""
    vector = parse_vector(vector_string)
    result = calculate_base_score(vector)

    if temporal:
        calculate_temporal_score(result, vector)

    if environmental:
        calculate_environmental_score(result, vector)

    return result


def map_to_immunefi(cvss_score: float, cvss_severity: str) -> str:
    """Map CVSS score to Immunefi severity."""
    if cvss_score >= 9.0:
        return "Critical"
    elif cvss_score >= 7.0:
        return "High"
    elif cvss_score >= 4.0:
        return "Medium"
    elif cvss_score >= 0.1:
        return "Low"
    else:
        return "Informational"


def get_immunefi_severity(impact: str, likelihood: str) -> str:
    """Determine Immunefi severity from impact and likelihood."""
    impact = impact.lower()
    likelihood = likelihood.lower()

    # Critical: Loss of funds > 10% TVL or complete protocol insolvency
    if "critical" in impact or "> 10%" in impact or "insolvency" in impact:
        return "Critical"

    # High: Loss of funds < 10% TVL or significant protocol disruption
    if "high" in impact or "< 10%" in impact or "disruption" in impact:
        return "High"

    # Medium: Temporary fund lock or degradation of protocol functionality
    if "medium" in impact or "lock" in impact or "degradation" in impact:
        return "Medium"

    # Low: No direct fund loss, minor protocol degradation
    if "low" in impact or "minor" in impact:
        return "Low"

    # Informational: No direct impact
    if "info" in impact or "none" in impact or "no direct" in impact:
        return "Informational"

    # Default based on likelihood
    if likelihood == "high":
        return "High"
    elif likelihood == "medium":
        return "Medium"
    elif likelihood == "low":
        return "Low"
    else:
        return "Informational"


def format_result(result: CVSSResult, json_output: bool = False) -> str:
    """Format the CVSS result for display."""
    if json_output:
        output = {
            "vector": result.vector,
            "base_score": result.base_score,
            "base_severity": result.base_severity,
            "impact": result.impact,
            "exploitability": result.exploitability,
        }
        if result.temporal_score is not None:
            output["temporal_score"] = result.temporal_score
            output["temporal_severity"] = result.temporal_severity
        if result.environmental_score is not None:
            output["environmental_score"] = result.environmental_score
            output["environmental_severity"] = result.environmental_severity
        output["immunefi_severity"] = map_to_immunefi(result.base_score, result.base_severity)
        return json.dumps(output, indent=2)

    lines = [
        f"Vector: {result.vector}",
        f"Base Score: {result.base_score} ({result.base_severity})",
        f"Impact: {result.impact}",
        f"Exploitability: {result.exploitability}",
    ]

    if result.temporal_score is not None:
        lines.append(f"Temporal Score: {result.temporal_score} ({result.temporal_severity})")

    if result.environmental_score is not None:
        lines.append(f"Environmental Score: {result.environmental_score} ({result.environmental_severity})")

    lines.append(f"Immunefi Severity: {map_to_immunefi(result.base_score, result.base_severity)}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate CVSS v3.1 scores and map to Immunefi severity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
  %(prog)s --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" --temporal
  %(prog)s --vector "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H" --environmental
  %(prog)s --batch vectors.txt
  %(prog)s --immunefi --impact "Loss of funds > 10% TVL" --likelihood high
        """,
    )

    parser.add_argument(
        "--vector",
        help="CVSS v3.1 vector string",
    )
    parser.add_argument(
        "--temporal",
        action="store_true",
        help="Calculate temporal score",
    )
    parser.add_argument(
        "--environmental",
        action="store_true",
        help="Calculate environmental score",
    )
    parser.add_argument(
        "--batch",
        help="File containing vector strings (one per line)",
    )
    parser.add_argument(
        "--immunefi",
        action="store_true",
        help="Calculate Immunefi severity from impact and likelihood",
    )
    parser.add_argument(
        "--impact",
        help="Impact description (for Immunefi)",
    )
    parser.add_argument(
        "--likelihood",
        choices=["high", "medium", "low"],
        help="Likelihood (for Immunefi)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()

    if args.immunefi:
        if not args.impact or not args.likelihood:
            parser.error("--impact and --likelihood are required for Immunefi calculation")
        severity = get_immunefi_severity(args.impact, args.likelihood)
        if args.json:
            print(json.dumps({"impact": args.impact, "likelihood": args.likelihood, "severity": severity}, indent=2))
        else:
            print(f"Impact: {args.impact}")
            print(f"Likelihood: {args.likelihood}")
            print(f"Immunefi Severity: {severity}")
        return

    if args.batch:
        with open(args.batch, "r") as f:
            vectors = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        results = []
        for vector_string in vectors:
            result = calculate_cvss(vector_string, args.temporal, args.environmental)
            results.append(result)
            if args.json:
                print(json.dumps({
                    "vector": result.vector,
                    "base_score": result.base_score,
                    "base_severity": result.base_severity,
                }))
            else:
                print(format_result(result))
                print()

        if args.json:
            print(json.dumps([{
                "vector": r.vector,
                "base_score": r.base_score,
                "base_severity": r.base_severity,
            } for r in results], indent=2))
        return

    if not args.vector:
        parser.error("--vector is required (unless using --batch or --immunefi)")

    result = calculate_cvss(args.vector, args.temporal, args.environmental)
    print(format_result(result, args.json))


if __name__ == "__main__":
    main()
