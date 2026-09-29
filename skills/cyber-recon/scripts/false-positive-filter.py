#!/usr/bin/env python3
"""
false-positive-filter.py - Filter Common False Positives from Scan Results

Filters out common false positive findings from nuclei, nikto, and nmap scan results.
Uses pattern matching, version-aware CVE validation, and contextual analysis.

Usage:
    python3 false-positive-filter.py --input results.json --output filtered.json
    python3 false-positive-filter.py --input nuclei.json --tool nuclei --severity-threshold low
    cat results.json | python3 false-positive-filter.py --tool nuclei

Exit Codes:
    0   Success
    1   Error processing input
    2   Invalid arguments
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """Represents a single finding from a scan."""
    id: str
    title: str
    severity: str
    host: str = ""
    port: Any = ""
    service: str = ""
    cve: str = ""
    cvss: Any = ""
    evidence: str = ""
    verification: str = "pending"
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Finding":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            severity=data.get("severity", "info").lower(),
            host=data.get("host", ""),
            port=data.get("port", ""),
            service=data.get("service", ""),
            cve=data.get("cve", ""),
            cvss=data.get("cvss", ""),
            evidence=data.get("evidence", ""),
            verification=data.get("verification", "pending"),
            raw=data,
        )

    def to_dict(self) -> dict:
        result = dict(self.raw)
        result["verification"] = self.verification
        return result


# =============================================================================
# FALSE POSITIVE PATTERNS
# =============================================================================

# Nuclei false positive patterns
NUCLEI_FALSE_POSITIVE_PATTERNS = [
    # Generic 404/403 page matches
    {
        "name": "generic-404-detection",
        "pattern": r"(?i)(404|not found).*(page|error|response)",
        "severity_filter": ["info", "low"],
        "description": "Generic 404 page detection - not a vulnerability",
    },
    {
        "name": "generic-403-detection",
        "pattern": r"(?i)(403|forbidden).*(page|error|response)",
        "severity_filter": ["info", "low"],
        "description": "Generic 403 page detection - not a vulnerability",
    },
    # Version banner spoofing
    {
        "name": "version-banner-info",
        "pattern": r"(?i)(server.*banner|version.*disclosure|header.*exposure)",
        "severity_filter": ["info"],
        "description": "Version banner disclosure - informational only",
    },
    # SSL/TLS configuration false positives
    {
        "name": "tls-ssl-info",
        "pattern": r"(?i)(ssl|tls).*(certificate|protocol|cipher).*(info|disclosure)",
        "severity_filter": ["info", "low"],
        "description": "SSL/TLS informational findings",
    },
    # Default credentials false positives
    {
        "name": "default-credentials-info",
        "pattern": r"(?i)default.*(credentials|password|login).*(info|check)",
        "severity_filter": ["info"],
        "description": "Default credentials check - informational",
    },
    # Information disclosure false positives
    {
        "name": "info-disclosure-generic",
        "pattern": r"(?i)(information|info).*(disclosure|exposure|leak).*(generic|potential)",
        "severity_filter": ["info", "low"],
        "description": "Generic information disclosure - needs manual verification",
    },
    # XSS false positives
    {
        "name": "xss-reflected-generic",
        "pattern": r"(?i)(reflected|xss).*(potential|possible|generic|detected)",
        "severity_filter": ["info", "low"],
        "description": "Potential XSS - requires manual confirmation",
    },
    # SQL injection false positives
    {
        "name": "sqli-generic",
        "pattern": r"(?i)(sql|injection).*(potential|possible|generic|detected)",
        "severity_filter": ["info", "low"],
        "description": "Potential SQL injection - requires manual confirmation",
    },
    # Open port false positives
    {
        "name": "open-port-info",
        "pattern": r"(?i)(open.*port|port.*open).*(info|detection)",
        "severity_filter": ["info"],
        "description": "Open port detection - informational only",
    },
    # Technology detection
    {
        "name": "tech-detection",
        "pattern": r"(?i)(technology|framework|cms).*(detection|identification)",
        "severity_filter": ["info"],
        "description": "Technology detection - informational only",
    },
    # Missing headers
    {
        "name": "missing-header-info",
        "pattern": r"(?i)missing.*(header|security).*(info)",
        "severity_filter": ["info"],
        "description": "Missing security header - informational",
    },
    # CORS misconfiguration info
    {
        "name": "cors-info",
        "pattern": r"(?i)cors.*(info|detection|configuration)",
        "severity_filter": ["info"],
        "description": "CORS configuration info - informational",
    },
]

# Nikto false positive patterns
NIKTO_FALSE_POSITIVE_PATTERNS = [
    {
        "name": "nikto-directory-listing-info",
        "pattern": r"(?i)directory.*(listing|index).*(enabled|found|info)",
        "severity_filter": ["info", "low"],
        "description": "Directory listing - informational",
    },
    {
        "name": "nikto-server-header",
        "pattern": r"(?i)server.*header.*(disclosure|exposure)",
        "severity_filter": ["info"],
        "description": "Server header disclosure - informational",
    },
    {
        "name": "nikto-options-method",
        "pattern": r"(?i)http.*options.*method.*(enabled|allowed)",
        "severity_filter": ["info", "low"],
        "description": "HTTP OPTIONS method enabled - informational",
    },
    {
        "name": "nikto-trace-method",
        "pattern": r"(?i)(trace|track).*method.*(enabled|allowed)",
        "severity_filter": ["info", "low"],
        "description": "HTTP TRACE/TRACK method - informational",
    },
    {
        "name": "nikto-default-page",
        "pattern": r"(?i)default.*(page|index|welcome).*(found|detected)",
        "severity_filter": ["info"],
        "description": "Default page found - informational",
    },
    {
        "name": "nikto-cgi-scripts",
        "pattern": r"(?i)(cgi|script).*(found|detected|exists)",
        "severity_filter": ["info", "low"],
        "description": "CGI scripts found - informational",
    },
    {
        "name": "nikto-robots-txt",
        "pattern": r"(?i)robots\.txt.*(found|exists|disclosure)",
        "severity_filter": ["info"],
        "description": "robots.txt found - informational",
    },
    {
        "name": "nikto-backup-files",
        "pattern": r"(?i)(backup|bak|old|copy).*(file|found|exists)",
        "severity_filter": ["info", "low"],
        "description": "Potential backup files - needs verification",
    },
]

# Nmap false positive patterns
NMAP_FALSE_POSITIVE_PATTERNS = [
    {
        "name": "nmap-os-guess",
        "pattern": r"(?i)(os.*guess|os.*detection|aggressive.*os)",
        "severity_filter": ["info"],
        "description": "OS guess from nmap - not always accurate",
    },
    {
        "name": "nmap-service-info",
        "pattern": r"(?i)(service.*info|version.*detection)",
        "severity_filter": ["info"],
        "description": "Service version info - informational",
    },
]

# Combined patterns for all tools
ALL_FALSE_POSITIVE_PATTERNS = {
    "nuclei": NUCLEI_FALSE_POSITIVE_PATTERNS,
    "nikto": NIKTO_FALSE_POSITIVE_PATTERNS,
    "nmap": NMAP_FALSE_POSITIVE_PATTERNS,
    "masscan": NMAP_FALSE_POSITIVE_PATTERNS,
}


# =============================================================================
# VERSION-AWARE CVE VALIDATION
# =============================================================================

def cve_applies_to_version(cve_id: str, detected_version: str, product: str = "") -> bool:
    """
    Check if a CVE applies to a detected version of a product.
    
    Uses CPE (Common Platform Enumeration) data and version ranges to determine
    if a CVE is relevant to the detected software version.
    
    Args:
        cve_id: The CVE identifier (e.g., "CVE-2021-44228")
        detected_version: The version string detected by the scanner
        product: The product name (e.g., "Apache httpd", "OpenSSH")
    
    Returns:
        True if the CVE likely applies, False if it's a false positive,
        None if unable to determine (requires manual review)
    """
    if not cve_id or not detected_version:
        return None
    
    # CVE version database (simplified - in production, use NVD API or local CVE database)
    # Format: CVE_ID -> {product: [(min_version, max_version, inclusive_min, inclusive_max)]}
    CVE_VERSION_DB = {
        "CVE-2021-44228": {  # Log4Shell
            "log4j": [("2.0", "2.14.1", True, True)],
            "log4j2": [("2.0", "2.14.1", True, True)],
        },
        "CVE-2021-45046": {  # Log4Shell follow-up
            "log4j": [("2.0", "2.15.0", True, True)],
            "log4j2": [("2.0", "2.15.0", True, True)],
        },
        "CVE-2014-0160": {  # Heartbleed
            "openssl": [("1.0.1", "1.0.1f", True, True)],
        },
        "CVE-2017-5638": {  # Struts2 RCE
            "struts": [("2.3.5", "2.3.31", True, True), ("2.5.0", "2.5.10", True, True)],
        },
        "CVE-2019-0708": {  # BlueKeep
            "rdp": [("any", "any", True, True)],  # All versions vulnerable
        },
        "CVE-2020-1472": {  # Zerologon
            "netlogon": [("any", "any", True, True)],
        },
    }
    
    cve_data = CVE_VERSION_DB.get(cve_id)
    if not cve_data:
        # Unknown CVE - cannot determine, requires manual review
        return None
    
    # Find matching product
    product_lower = product.lower() if product else ""
    version_ranges = None
    for db_product, ranges in cve_data.items():
        if db_product in product_lower or product_lower in db_product:
            version_ranges = ranges
            break
    
    if not version_ranges:
        # Product doesn't match - likely false positive
        return False
    
    # Check version against ranges
    for min_ver, max_ver, inclusive_min, inclusive_max in version_ranges:
        if min_ver == "any" and max_ver == "any":
            return True
        
        try:
            # Simple version comparison (for production, use packaging.version)
            detected_parts = _parse_version(detected_version)
            min_parts = _parse_version(min_ver)
            max_parts = _parse_version(max_ver)
            
            ge_min = _version_gte(detected_parts, min_parts) if inclusive_min else _version_gt(detected_parts, min_parts)
            le_max = _version_lte(detected_parts, max_parts) if inclusive_max else _version_lt(detected_parts, max_parts)
            
            if ge_min and le_max:
                return True
        except (ValueError, TypeError):
            continue
    
    # Version not in vulnerable range
    return False


def _parse_version(version_str: str) -> list:
    """Parse version string into comparable components."""
    if not version_str:
        return [0]
    # Remove common prefixes
    version_str = re.sub(r'^[vV]', '', version_str)
    # Split by dots and non-numeric separators
    parts = re.split(r'[.\-_+]', version_str)
    result = []
    for part in parts:
        try:
            result.append(int(part))
        except ValueError:
            # Non-numeric part, try to extract numbers
            nums = re.findall(r'\d+', part)
            if nums:
                result.append(int(nums[0]))
            else:
                result.append(0)
    return result


def _version_gte(a: list, b: list) -> bool:
    """Check if version a >= version b."""
    return _compare_versions(a, b) >= 0


def _version_gt(a: list, b: list) -> bool:
    """Check if version a > version b."""
    return _compare_versions(a, b) > 0


def _version_lte(a: list, b: list) -> bool:
    """Check if version a <= version b."""
    return _compare_versions(a, b) <= 0


def _version_lt(a: list, b: list) -> bool:
    """Check if version a < version b."""
    return _compare_versions(a, b) < 0


def _compare_versions(a: list, b: list) -> int:
    """Compare two version lists. Returns -1, 0, or 1."""
    max_len = max(len(a), len(b))
    a = a + [0] * (max_len - len(a))
    b = b + [0] * (max_len - len(b))
    for x, y in zip(a, b):
        if x < y:
            return -1
        if x > y:
            return 1
    return 0


# =============================================================================
# FILTERING LOGIC
# =============================================================================

def filter_finding(finding: Finding, tool: str = "nuclei", 
                   severity_threshold: str = "info",
                   enable_version_check: bool = True) -> tuple:
    """
    Determine if a finding is a false positive.
    
    Args:
        finding: The finding to evaluate
        tool: The tool that generated the finding (nuclei, nikto, nmap)
        severity_threshold: Minimum severity to keep (filters below this)
        enable_version_check: Whether to perform CVE version checking
    
    Returns:
        Tuple of (is_false_positive: bool, reason: str)
    """
    # Check severity threshold
    severity_order = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    finding_sev = severity_order.get(finding.severity, 0)
    threshold_sev = severity_order.get(severity_threshold, 0)
    
    if finding_sev < threshold_sev:
        return (True, f"Below severity threshold ({finding.severity} < {severity_threshold})")
    
    # Get patterns for this tool
    patterns = ALL_FALSE_POSITIVE_PATTERNS.get(tool, [])
    
    # Check against false positive patterns
    for fp_pattern in patterns:
        pattern = fp_pattern["pattern"]
        severity_filter = fp_pattern.get("severity_filter", [])
        
        # Only apply pattern if finding severity is in the filter list
        if severity_filter and finding.severity not in severity_filter:
            continue
        
        # Check title and evidence against pattern
        text_to_check = f"{finding.title} {finding.evidence}"
        if re.search(pattern, text_to_check, re.IGNORECASE):
            return (True, f"Matched false positive pattern: {fp_pattern['name']} - {fp_pattern['description']}")
    
    # CVE version check
    if enable_version_check and finding.cve:
        # Try to extract version from evidence or raw data
        detected_version = _extract_version_from_finding(finding)
        product = finding.raw.get("product", "") or finding.service
        
        if detected_version:
            applies = cve_applies_to_version(finding.cve, detected_version, product)
            if applies is False:
                return (True, f"CVE {finding.cve} does not apply to detected version {detected_version}")
            elif applies is None:
                # Unable to determine - flag for manual review but don't filter
                pass
    
    return (False, "No false positive patterns matched")


def _extract_version_from_finding(finding: Finding) -> str:
    """Extract version information from finding data."""
    # Check raw data for version fields
    for key in ["version", "product_version", "service_version"]:
        if key in finding.raw and finding.raw[key]:
            return str(finding.raw[key])
    
    # Try to extract from evidence using regex
    version_patterns = [
        r'(\d+\.\d+\.\d+[\w.\-]*)',
        r'(\d+\.\d+[\w.\-]*)',
        r'v(\d+\.\d+[\w.\-]*)',
    ]
    for pattern in version_patterns:
        match = re.search(pattern, finding.evidence)
        if match:
            return match.group(1)
    
    return ""


def filter_findings(findings: list, tool: str = "nuclei",
                    severity_threshold: str = "info",
                    enable_version_check: bool = True) -> dict:
    """
    Filter a list of findings, separating true and false positives.
    
    Returns:
        Dictionary with 'true_positives', 'false_positives', and 'summary' keys.
    """
    true_positives = []
    false_positives = []
    
    for finding in findings:
        is_fp, reason = filter_finding(finding, tool, severity_threshold, enable_version_check)
        
        if is_fp:
            finding.verification = "false_positive"
            finding.raw["false_positive_reason"] = reason
            false_positives.append(finding)
        else:
            true_positives.append(finding)
    
    return {
        "true_positives": [f.to_dict() for f in true_positives],
        "false_positives": [f.to_dict() for f in false_positives],
        "summary": {
            "total": len(findings),
            "true_positives": len(true_positives),
            "false_positives": len(false_positives),
            "filter_rate": f"{len(false_positives) / len(findings) * 100:.1f}%" if findings else "0%",
        }
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Filter common false positives from security scan results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input nuclei-results.json --tool nuclei --output filtered.json
  %(prog)s --input results.json --tool nikto --severity-threshold medium
  %(prog)s --input results.json --tool nuclei --no-version-check
  cat results.json | %(prog)s --tool nuclei --output -
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input JSON file (reads from stdin if not specified)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="-",
        help="Output file (default: stdout, use '-' for stdout)"
    )
    parser.add_argument(
        "--tool", "-t",
        type=str,
        choices=["nuclei", "nikto", "nmap", "masscan", "auto"],
        default="auto",
        help="Tool that generated the results (default: auto-detect)"
    )
    parser.add_argument(
        "--severity-threshold",
        type=str,
        choices=["info", "low", "medium", "high", "critical"],
        default="info",
        help="Minimum severity to keep (default: info)"
    )
    parser.add_argument(
        "--no-version-check",
        action="store_true",
        help="Disable CVE version checking"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed filtering decisions"
    )
    
    args = parser.parse_args()
    
    # Read input
    try:
        if args.input:
            with open(args.input, 'r') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Extract findings from various input formats
    findings = []
    if isinstance(data, list):
        findings = [Finding.from_dict(item) for item in data]
    elif isinstance(data, dict):
        if "findings" in data:
            findings = [Finding.from_dict(item) for item in data["findings"]]
        elif "results" in data:
            findings = [Finding.from_dict(item) for item in data["results"]]
        else:
            # Single finding
            findings = [Finding.from_dict(data)]
    
    if not findings:
        print("Warning: No findings found in input", file=sys.stderr)
        sys.exit(0)
    
    # Auto-detect tool if needed
    tool = args.tool
    if tool == "auto":
        if isinstance(data, dict) and "tool" in data:
            tool = data["tool"]
        else:
            tool = "nuclei"  # Default assumption
    
    # Filter findings
    result = filter_findings(
        findings,
        tool=tool,
        severity_threshold=args.severity_threshold,
        enable_version_check=not args.no_version_check
    )
    
    # Output results
    output = json.dumps(result, indent=2)
    
    if args.output == "-":
        print(output)
    else:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Filtered results written to: {args.output}", file=sys.stderr)
        print(f"  Total: {result['summary']['total']}", file=sys.stderr)
        print(f"  True positives: {result['summary']['true_positives']}", file=sys.stderr)
        print(f"  False positives: {result['summary']['false_positives']}", file=sys.stderr)
        print(f"  Filter rate: {result['summary']['filter_rate']}", file=sys.stderr)
    
    # Verbose output
    if args.verbose:
        print("\n--- Filtering Details ---", file=sys.stderr)
        for fp in result["false_positives"]:
            reason = fp.get("false_positive_reason", "unknown")
            print(f"  [FP] {fp['id']}: {fp['title']} - {reason}", file=sys.stderr)


if __name__ == "__main__":
    main()
