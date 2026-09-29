#!/usr/bin/env python3
"""
false-positive-filter.py — Filter findings through false positive patterns
Part of the security-verify skill

Filters security findings through known false positive patterns and outputs
filtered findings with false positive analysis.

Usage:
    python3 false_positive_filter.py --input findings.json --output filtered.json
    python3 false_positive_filter.py --input findings.json --type web2
    python3 false-positive-filter.py --input findings.json --type web3
    python3 false-positive-filter.py --input findings.json --type all --verbose

Input format (JSON):
    [
        {
            "id": "finding-1",
            "type": "web2|web3|cross-domain",
            "title": "SQL Injection in login form",
            "description": "...",
            "target": "http://example.com/login",
            "evidence": {...},
            "metadata": {
                "version": "1.2.3",
                "configuration": "default",
                "authentication": "required",
                "rate_limiting": false,
                "compiler_version": null,
                "proxy_address": null,
                "oracle_dependency": false,
                "access_control": "none",
                "chain_id": null
            }
        }
    ]

Output format (JSON):
    {
        "findings": [...],
        "filtered_findings": [...],
        "false_positive_analysis": [...],
        "statistics": {
            "total": 100,
            "filtered": 25,
            "remaining": 75,
            "false_positive_rate": 0.25
        }
    }
"""

import json
import argparse
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class FindingType(Enum):
    WEB2 = "web2"
    WEB3 = "web3"
    CROSS_DOMAIN = "cross-domain"


class FalsePositivePattern(Enum):
    # Web2 patterns
    VERSION_MISMATCH = "version_mismatch"
    CONFIGURATION_DEPENDENT = "configuration_dependent"
    AUTHENTICATION_REQUIRED = "authentication_required"
    RATE_LIMITING = "rate_limiting"
    FALSE_BANNER = "false_banner"
    DEFAULT_PAGE = "default_page"
    ERROR_MESSAGE_DISCLOSURE = "error_message_disclosure"

    # Web3 patterns
    COMPILER_VERSION = "compiler_version"
    PROXY_IMPLEMENTATION = "proxy_implementation"
    ORACLE_DEPENDENCY = "oracle_dependency"
    ACCESS_CONTROL = "access_control"
    REORG = "reorg"
    TEST_COVERAGE = "test_coverage"
    GAS_OPTIMIZATION = "gas_optimization"

    # Cross-domain patterns
    MIXED_FINDINGS = "mixed_findings"
    CHAIN_CONFUSION = "chain_confusion"


@dataclass
class FalsePositiveCheck:
    """Result of a false positive pattern check."""
    pattern: str
    is_false_positive: bool
    reason: str
    mitigation: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilteredFinding:
    """A finding with false positive analysis."""
    finding: Dict[str, Any]
    false_positive_checks: List[FalsePositiveCheck] = field(default_factory=list)
    is_false_positive: bool = False
    false_positive_patterns: List[str] = field(default_factory=list)
    recommendation: str = ""


# ============================================================================
# Web2 False Positive Checks
# ============================================================================

def check_version_mismatch(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is a version mismatch false positive."""
    metadata = finding.get("metadata", {})
    version = metadata.get("version")
    target_version = metadata.get("target_version")

    if version and target_version and version != target_version:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.VERSION_MISMATCH.value,
            is_false_positive=True,
            reason=f"Finding applies to version {version} but target is version {target_version}",
            mitigation="Verify the exact version of the target software",
            evidence={"finding_version": version, "target_version": target_version},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.VERSION_MISMATCH.value,
        is_false_positive=False,
        reason="No version mismatch detected",
        mitigation="",
        evidence={},
    )


def check_configuration_dependent(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is configuration-dependent false positive."""
    metadata = finding.get("metadata", {})
    configuration = metadata.get("configuration", "default")
    required_configuration = metadata.get("required_configuration")

    if required_configuration and configuration != required_configuration:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.CONFIGURATION_DEPENDENT.value,
            is_false_positive=True,
            reason=f"Finding requires configuration '{required_configuration}' but target uses '{configuration}'",
            mitigation="Test the vulnerability in the target's actual configuration",
            evidence={"target_configuration": configuration, "required_configuration": required_configuration},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.CONFIGURATION_DEPENDENT.value,
        is_false_positive=False,
        reason="No configuration dependency detected",
        mitigation="",
        evidence={},
    )


def check_authentication_required(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding requires authentication that was not provided."""
    metadata = finding.get("metadata", {})
    authentication = metadata.get("authentication", "none")
    credentials_provided = metadata.get("credentials_provided", False)

    if authentication == "required" and not credentials_provided:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.AUTHENTICATION_REQUIRED.value,
            is_false_positive=True,
            reason="Finding requires authentication but no credentials were provided",
            mitigation="Test with valid credentials",
            evidence={"authentication": authentication, "credentials_provided": credentials_provided},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.AUTHENTICATION_REQUIRED.value,
        is_false_positive=False,
        reason="No authentication issue detected",
        mitigation="",
        evidence={},
    )


def check_rate_limiting(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is affected by rate limiting."""
    metadata = finding.get("metadata", {})
    rate_limiting = metadata.get("rate_limiting", False)
    waf_detected = metadata.get("waf_detected", False)

    if rate_limiting or waf_detected:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.RATE_LIMITING.value,
            is_false_positive=False,
            reason="Test was blocked by rate limiting or WAF — not a false positive, but a blocked test",
            mitigation="Re-test with rate limiting",
            evidence={"rate_limiting": rate_limiting, "waf_detected": waf_detected},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.RATE_LIMITING.value,
        is_false_positive=False,
        reason="No rate limiting detected",
        mitigation="",
        evidence={},
    )


def check_false_banner(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is based on a false banner."""
    metadata = finding.get("metadata", {})
    banner_verified = metadata.get("banner_verified", True)
    behavioral_test_passed = metadata.get("behavioral_test_passed", True)

    if not banner_verified or not behavioral_test_passed:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.FALSE_BANNER.value,
            is_false_positive=True,
            reason="Service banner may be spoofed or misleading",
            mitigation="Use protocol-specific probes to verify the service",
            evidence={"banner_verified": banner_verified, "behavioral_test_passed": behavioral_test_passed},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.FALSE_BANNER.value,
        is_false_positive=False,
        reason="Banner verified",
        mitigation="",
        evidence={},
    )


def check_default_page(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is based on a default page."""
    metadata = finding.get("metadata", {})
    is_default_page = metadata.get("is_default_page", False)

    if is_default_page:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.DEFAULT_PAGE.value,
            is_false_positive=True,
            reason="Response is a default page, not a vulnerability",
            mitigation="Compare response with known default pages",
            evidence={"is_default_page": is_default_page},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.DEFAULT_PAGE.value,
        is_false_positive=False,
        reason="Not a default page",
        mitigation="",
        evidence={},
    )


def check_error_message_disclosure(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is based on an error message that is expected behavior."""
    metadata = finding.get("metadata", {})
    error_is_expected = metadata.get("error_is_expected", False)

    if error_is_expected:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.ERROR_MESSAGE_DISCLOSURE.value,
            is_false_positive=True,
            reason="Error message is expected behavior for the input",
            mitigation="Compare error messages with valid input",
            evidence={"error_is_expected": error_is_expected},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.ERROR_MESSAGE_DISCLOSURE.value,
        is_false_positive=False,
        reason="Error message is not expected behavior",
        mitigation="",
        evidence={},
    )


# ============================================================================
# Web3 False Positive Checks
# ============================================================================

def check_compiler_version(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is specific to a compiler version."""
    metadata = finding.get("metadata", {})
    compiler_version = metadata.get("compiler_version")
    target_compiler_version = metadata.get("target_compiler_version")

    if compiler_version and target_compiler_version and compiler_version != target_compiler_version:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.COMPILER_VERSION.value,
            is_false_positive=True,
            reason=f"Finding applies to compiler {compiler_version} but target uses {target_compiler_version}",
            mitigation="Verify the compiler version of the target contract",
            evidence={"finding_compiler": compiler_version, "target_compiler": target_compiler_version},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.COMPILER_VERSION.value,
        is_false_positive=False,
        reason="No compiler version mismatch detected",
        mitigation="",
        evidence={},
    )


def check_proxy_implementation(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is in the implementation, not the proxy."""
    metadata = finding.get("metadata", {})
    is_proxy = metadata.get("is_proxy", False)
    implementation_verified = metadata.get("implementation_verified", True)

    if is_proxy and not implementation_verified:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.PROXY_IMPLEMENTATION.value,
            is_false_positive=True,
            reason="Finding may be in the implementation contract, not the proxy",
            mitigation="Verify both the proxy and implementation contracts",
            evidence={"is_proxy": is_proxy, "implementation_verified": implementation_verified},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.PROXY_IMPLEMENTATION.value,
        is_false_positive=False,
        reason="No proxy-implementation issue detected",
        mitigation="",
        evidence={},
    )


def check_oracle_dependency(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding depends on a specific oracle state."""
    metadata = finding.get("metadata", {})
    oracle_dependency = metadata.get("oracle_dependency", False)
    oracle_state_verified = metadata.get("oracle_state_verified", True)

    if oracle_dependency and not oracle_state_verified:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.ORACLE_DEPENDENCY.value,
            is_false_positive=True,
            reason="Finding depends on a specific oracle state that was not verified",
            mitigation="Verify the oracle state on the target chain",
            evidence={"oracle_dependency": oracle_dependency, "oracle_state_verified": oracle_state_verified},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.ORACLE_DEPENDENCY.value,
        is_false_positive=False,
        reason="No oracle dependency detected",
        mitigation="",
        evidence={},
    )


def check_access_control(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is affected by access control."""
    metadata = finding.get("metadata", {})
    access_control = metadata.get("access_control", "none")
    required_role = metadata.get("required_role")
    test_account_has_role = metadata.get("test_account_has_role", True)

    if access_control != "none" and required_role and not test_account_has_role:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.ACCESS_CONTROL.value,
            is_false_positive=True,
            reason=f"Finding requires role '{required_role}' but test account does not have it",
            mitigation="Test with an account that has the required role",
            evidence={"access_control": access_control, "required_role": required_role, "test_account_has_role": test_account_has_role},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.ACCESS_CONTROL.value,
        is_false_positive=False,
        reason="No access control issue detected",
        mitigation="",
        evidence={},
    )


def check_reorg(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is affected by a chain reorg."""
    metadata = finding.get("metadata", {})
    chain_id = metadata.get("chain_id")
    finality_reached = metadata.get("finality_reached", True)

    if not finality_reached:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.REORG.value,
            is_false_positive=True,
            reason="State change may be due to a chain reorg",
            mitigation="Wait for sufficient finality before verifying",
            evidence={"chain_id": chain_id, "finality_reached": finality_reached},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.REORG.value,
        is_false_positive=False,
        reason="Finality reached",
        mitigation="",
        evidence={},
    )


def check_test_coverage(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is covered by tests that do not actually verify it."""
    metadata = finding.get("metadata", {})
    has_tests = metadata.get("has_tests", False)
    tests_verify_vulnerability = metadata.get("tests_verify_vulnerability", True)

    if has_tests and not tests_verify_vulnerability:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.TEST_COVERAGE.value,
            is_false_positive=True,
            reason="Tests exist but do not actually verify the vulnerability",
            mitigation="Review the tests to verify they actually test the vulnerability",
            evidence={"has_tests": has_tests, "tests_verify_vulnerability": tests_verify_vulnerability},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.TEST_COVERAGE.value,
        is_false_positive=False,
        reason="No test coverage issue detected",
        mitigation="",
        evidence={},
    )


def check_gas_optimization(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding is a gas optimization issue, not a security vulnerability."""
    metadata = finding.get("metadata", {})
    is_gas_optimization = metadata.get("is_gas_optimization", False)

    if is_gas_optimization:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.GAS_OPTIMIZATION.value,
            is_false_positive=True,
            reason="Finding is a gas optimization issue, not a security vulnerability",
            mitigation="Verify the issue affects security, not just gas",
            evidence={"is_gas_optimization": is_gas_optimization},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.GAS_OPTIMIZATION.value,
        is_false_positive=False,
        reason="Not a gas optimization issue",
        mitigation="",
        evidence={},
    )


# ============================================================================
# Cross-Domain False Positive Checks
# ============================================================================

def check_mixed_findings(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding mixes web2 and web3 components incorrectly."""
    metadata = finding.get("metadata", {})
    web2_verified = metadata.get("web2_verified", True)
    web3_verified = metadata.get("web3_verified", True)

    if not web2_verified or not web3_verified:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.MIXED_FINDINGS.value,
            is_false_positive=True,
            reason="Finding mixes web2 and web3 components but not all are verified",
            mitigation="Verify each component independently",
            evidence={"web2_verified": web2_verified, "web3_verified": web3_verified},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.MIXED_FINDINGS.value,
        is_false_positive=False,
        reason="All components verified",
        mitigation="",
        evidence={},
    )


def check_chain_confusion(finding: Dict[str, Any]) -> FalsePositiveCheck:
    """Check if the finding confuses different chains or networks."""
    metadata = finding.get("metadata", {})
    chain_id = metadata.get("chain_id")
    target_chain_id = metadata.get("target_chain_id")

    if chain_id and target_chain_id and chain_id != target_chain_id:
        return FalsePositiveCheck(
            pattern=FalsePositivePattern.CHAIN_CONFUSION.value,
            is_false_positive=True,
            reason=f"Finding is for chain {chain_id} but target is chain {target_chain_id}",
            mitigation="Verify the chain ID and contract address on the correct chain",
            evidence={"finding_chain": chain_id, "target_chain": target_chain_id},
        )

    return FalsePositiveCheck(
        pattern=FalsePositivePattern.CHAIN_CONFUSION.value,
        is_false_positive=False,
        reason="No chain confusion detected",
        mitigation="",
        evidence={},
    )


# ============================================================================
# Filter Engine
# ============================================================================

WEB2_CHECKS = [
    check_version_mismatch,
    check_configuration_dependent,
    check_authentication_required,
    check_rate_limiting,
    check_false_banner,
    check_default_page,
    check_error_message_disclosure,
]

WEB3_CHECKS = [
    check_compiler_version,
    check_proxy_implementation,
    check_oracle_dependency,
    check_access_control,
    check_reorg,
    check_test_coverage,
    check_gas_optimization,
]

CROSS_DOMAIN_CHECKS = [
    check_mixed_findings,
    check_chain_confusion,
]


def filter_finding(finding: Dict[str, Any]) -> FilteredFinding:
    """Filter a single finding through all applicable false positive checks."""
    finding_type = finding.get("type", "web2")

    # Select applicable checks
    checks = []
    if finding_type == "web2":
        checks = WEB2_CHECKS
    elif finding_type == "web3":
        checks = WEB3_CHECKS
    elif finding_type == "cross-domain":
        checks = CROSS_DOMAIN_CHECKS + WEB2_CHECKS + WEB3_CHECKS

    # Run all checks
    false_positive_checks = []
    for check_func in checks:
        result = check_func(finding)
        false_positive_checks.append(result)

    # Determine if finding is a false positive
    fp_patterns = [c.pattern for c in false_positive_checks if c.is_false_positive]
    is_false_positive = len(fp_patterns) > 0

    # Generate recommendation
    if is_false_positive:
        mitigations = [c.mitigation for c in false_positive_checks if c.is_false_positive and c.mitigation]
        recommendation = "Apply mitigations: " + "; ".join(mitigations)
    else:
        recommendation = "No false positive patterns detected. Proceed with verification."

    return FilteredFinding(
        finding=finding,
        false_positive_checks=false_positive_checks,
        is_false_positive=is_false_positive,
        false_positive_patterns=fp_patterns,
        recommendation=recommendation,
    )


def filter_findings(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Filter all findings through false positive patterns."""
    filtered = [filter_finding(f) for f in findings]

    true_positives = [f for f in filtered if not f.is_false_positive]
    false_positives = [f for f in filtered if f.is_false_positive]

    total = len(findings)
    fp_count = len(false_positives)
    fp_rate = fp_count / total if total > 0 else 0.0

    return {
        "findings": [f.finding for f in true_positives],
        "filtered_findings": [f.finding for f in false_positives],
        "false_positive_analysis": [
            {
                "finding_id": f.finding.get("id", "unknown"),
                "finding_title": f.finding.get("title", "unknown"),
                "is_false_positive": f.is_false_positive,
                "false_positive_patterns": f.false_positive_patterns,
                "recommendation": f.recommendation,
                "checks": [asdict(c) for c in f.false_positive_checks],
            }
            for f in filtered
        ],
        "statistics": {
            "total": total,
            "filtered": fp_count,
            "remaining": total - fp_count,
            "false_positive_rate": round(fp_rate, 4),
        },
    }


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Filter findings through false positive patterns")
    parser.add_argument("--input", required=True, help="Input JSON file with findings")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--type", choices=["web2", "web3", "cross-domain", "all"],
                        default="all", help="Finding type filter")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load findings
    try:
        with open(args.input, "r") as f:
            findings = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(findings, list):
        print("Error: Input must be a JSON array of findings", file=sys.stderr)
        sys.exit(1)

    # Filter by type if specified
    if args.type != "all":
        findings = [f for f in findings if f.get("type") == args.type]

    # Run filter
    result = filter_findings(findings)

    # Output
    output_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Output written to: {args.output}")
    else:
        print(output_json)

    # Print summary
    stats = result["statistics"]
    print(f"\n--- Summary ---", file=sys.stderr)
    print(f"Total findings: {stats['total']}", file=sys.stderr)
    print(f"False positives: {stats['filtered']}", file=sys.stderr)
    print(f"Remaining: {stats['remaining']}", file=sys.stderr)
    print(f"False positive rate: {stats['false_positive_rate']:.1%}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
