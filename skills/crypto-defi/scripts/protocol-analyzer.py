#!/usr/bin/env python3
"""
DeFi Protocol Security Analyzer
Analyzes DeFi protocol security across multiple dimensions:
- Protocol architecture
- Oracle dependency mapping
- Flash loan risk assessment
- Governance mechanism review
- Economic attack surface mapping
- Risk scoring

Usage:
    python protocol-analyzer.py --protocol Aave --config protocol_config.json
    python protocol-analyzer.py --interactive
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


@dataclass
class Finding:
    title: str
    description: str
    root_cause: str
    exploitability: str
    impact: str
    recommendation: str
    risk_level: RiskLevel
    category: str


@dataclass
class ProtocolAnalysis:
    name: str
    category: str
    architecture: dict[str, Any] = field(default_factory=dict)
    oracle_security: dict[str, Any] = field(default_factory=dict)
    flash_loan_risk: dict[str, Any] = field(default_factory=dict)
    governance_security: dict[str, Any] = field(default_factory=dict)
    economic_surface: dict[str, Any] = field(default_factory=dict)
    composability_risks: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    risk_scores: dict[str, int] = field(default_factory=dict)

    @property
    def overall_risk(self) -> RiskLevel:
        if not self.risk_scores:
            return RiskLevel.INFO
        avg = sum(self.risk_scores.values()) / len(self.risk_scores)
        if avg >= 8:
            return RiskLevel.CRITICAL
        elif avg >= 6:
            return RiskLevel.HIGH
        elif avg >= 4:
            return RiskLevel.MEDIUM
        elif avg >= 2:
            return RiskLevel.LOW
        return RiskLevel.INFO


class ProtocolAnalyzer:
    """Main analyzer class for DeFi protocol security assessment."""

    PROTOCOL_CATEGORIES = {
        "aave": "lending",
        "compound": "lending",
        "makerdao": "lending",
        "uniswap": "amm",
        "curve": "amm",
        "balancer": "amm",
        "yearn": "yield",
        "harvest": "yield",
        "dai": "stablecoin",
        "frax": "stablecoin",
        "usdc": "stablecoin",
        "wormhole": "bridge",
        "ronin": "bridge",
        "nomad": "bridge",
        "dydx": "perpetuals",
        "gmx": "perpetuals",
        "gns": "perpetuals",
    }

    def __init__(self, protocol_name: str, config: dict[str, Any] | None = None):
        self.protocol_name = protocol_name
        self.config = config or {}
        self.category = self._classify_protocol(protocol_name)
        self.analysis = ProtocolAnalysis(name=protocol_name, category=self.category)

    def _classify_protocol(self, name: str) -> str:
        name_lower = name.lower()
        for key, category in self.PROTOCOL_CATEGORIES.items():
            if key in name_lower:
                return category
        return "unknown"

    def analyze_architecture(self) -> dict[str, Any]:
        """Phase 1: Protocol architecture review."""
        contracts = self.config.get("contracts", [])
        dependencies = self.config.get("dependencies", [])
        upgrade_mechanism = self.config.get("upgrade_mechanism", "unknown")
        admin_keys = self.config.get("admin_keys", "unknown")

        architecture = {
            "contract_count": len(contracts),
            "contracts": contracts,
            "external_dependencies": dependencies,
            "dependency_count": len(dependencies),
            "upgrade_mechanism": upgrade_mechanism,
            "admin_key_risk": self._assess_admin_key_risk(admin_keys),
            "fund_flow": self.config.get("fund_flow", "Not analyzed"),
        }

        self.analysis.architecture = architecture

        # Generate findings
        if admin_keys == "single":
            self.analysis.findings.append(Finding(
                title="Single Admin Key Risk",
                description="Protocol uses a single admin key, creating a single point of failure.",
                root_cause="Centralized key management without multi-signature or timelock.",
                exploitability="Compromised key can drain all funds immediately.",
                impact="Total protocol TVL at risk.",
                recommendation="Implement multi-signature (e.g., 4-of-7) with timelock for critical operations.",
                risk_level=RiskLevel.CRITICAL,
                category="Architecture",
            ))

        if upgrade_mechanism == "instant":
            self.analysis.findings.append(Finding(
                title="Instant Upgrade Mechanism",
                description="Protocol can be upgraded without timelock or delay.",
                root_cause="Admin-controlled upgrade mechanism without delay.",
                exploitability="Compromised key can upgrade to malicious contract instantly.",
                impact="Total protocol TVL at risk.",
                recommendation="Implement timelock (minimum 48 hours) for all upgrades.",
                risk_level=RiskLevel.CRITICAL,
                category="Architecture",
            ))

        return architecture

    def _assess_admin_key_risk(self, admin_keys: str) -> str:
        risk_map = {
            "single": "Critical",
            "multisig": "Medium",
            "timelock": "Low",
            "dao": "Low",
            "unknown": "Unknown",
        }
        return risk_map.get(admin_keys, "Unknown")

    def analyze_oracle_security(self) -> dict[str, Any]:
        """Phase 2: Oracle dependency analysis."""
        oracle_type = self.config.get("oracle_type", "unknown")
        oracle_sources = self.config.get("oracle_sources", [])
        twap_enabled = self.config.get("twap_enabled", False)
        circuit_breaker = self.config.get("circuit_breaker", False)
        heartbeat = self.config.get("heartbeat", "unknown")

        oracle_security = {
            "oracle_type": oracle_type,
            "oracle_sources": oracle_sources,
            "source_count": len(oracle_sources),
            "twap_enabled": twap_enabled,
            "circuit_breaker": circuit_breaker,
            "heartbeat": heartbeat,
            "manipulation_cost": self._estimate_manipulation_cost(oracle_type),
            "flash_loan_amplifiable": oracle_type in ("spot", "custom"),
        }

        self.analysis.oracle_security = oracle_security

        # Generate findings
        if oracle_type == "spot":
            self.analysis.findings.append(Finding(
                title="Spot Price Oracle Vulnerability",
                description="Protocol uses spot prices from AMMs, vulnerable to flash loan manipulation.",
                root_cause="Spot prices can be manipulated within a single transaction using flash loans.",
                exploitability="Attacker can flash loan large capital, manipulate price, exploit protocol, repay loan.",
                impact="All funds dependent on oracle price at risk.",
                recommendation="Use TWAP (Time-Weighted Average Price) or Chainlink decentralized oracle feeds.",
                risk_level=RiskLevel.CRITICAL,
                category="Oracle",
            ))

        if not twap_enabled and oracle_type in ("spot", "custom"):
            self.analysis.findings.append(Finding(
                title="No TWAP Protection",
                description="Protocol does not use TWAP for price averaging.",
                root_cause="Reliance on instantaneous price without time-weighted averaging.",
                exploitability="Single-transaction price manipulation is possible.",
                impact="Oracle-dependent operations are manipulable.",
                recommendation="Implement TWAP with appropriate window (e.g., 30 minutes).",
                risk_level=RiskLevel.HIGH,
                category="Oracle",
            ))

        if not circuit_breaker:
            self.analysis.findings.append(Finding(
                title="No Circuit Breaker",
                description="Protocol lacks emergency shutdown or circuit breaker mechanism.",
                root_cause="No mechanism to pause protocol during extreme price deviations.",
                exploitability="Attacker can exploit price manipulation without time limit.",
                impact="Losses can continue until manual intervention.",
                recommendation="Implement circuit breaker that pauses protocol on large price deviations.",
                risk_level=RiskLevel.HIGH,
                category="Oracle",
            ))

        return oracle_security

    def _estimate_manipulation_cost(self, oracle_type: str) -> str:
        cost_map = {
            "spot": "Low (flash loan)",
            "twap": "High (sustained capital)",
            "chainlink": "Very High (decentralized)",
            "custom": "Variable",
            "unknown": "Unknown",
        }
        return cost_map.get(oracle_type, "Unknown")

    def analyze_flash_loan_risk(self) -> dict[str, Any]:
        """Phase 3: Flash loan risk assessment."""
        flash_loan_providers = self.config.get("flash_loan_providers", [])
        attack_surfaces = self.config.get("attack_surfaces", [])
        mitigations = self.config.get("mitigations", [])

        flash_loan_risk = {
            "providers": flash_loan_providers,
            "provider_count": len(flash_loan_providers),
            "attack_surfaces": attack_surfaces,
            "surface_count": len(attack_surfaces),
            "mitigations": mitigations,
            "mitigation_count": len(mitigations),
            "atomicity_possible": len(attack_surfaces) > 0,
        }

        self.analysis.flash_loan_risk = flash_loan_risk

        # Generate findings
        if "governance" in attack_surfaces:
            self.analysis.findings.append(Finding(
                title="Flash Loan Governance Attack Surface",
                description="Governance voting power can be acquired via flash loans.",
                root_cause="Voting power is based on current token balance, not historical balance.",
                exploitability="Attacker flash loans governance tokens, votes on malicious proposal, repays loan.",
                impact="Governance can be captured and malicious proposals executed.",
                recommendation="Use voting power snapshots (historical balances) instead of current balances.",
                risk_level=RiskLevel.CRITICAL,
                category="Flash Loan",
            ))

        if "oracle" in attack_surfaces:
            self.analysis.findings.append(Finding(
                title="Flash Loan Oracle Manipulation Surface",
                description="Oracle prices can be manipulated using flash loans.",
                root_cause="Oracle relies on AMM spot prices that can be manipulated with borrowed capital.",
                exploitability="Attacker flash loans capital, manipulates AMM price, exploits oracle-dependent protocol.",
                impact="All oracle-dependent operations are vulnerable.",
                recommendation="Use TWAP or decentralized oracle feeds resistant to single-transaction manipulation.",
                risk_level=RiskLevel.CRITICAL,
                category="Flash Loan",
            ))

        if "liquidation" in attack_surfaces:
            self.analysis.findings.append(Finding(
                title="Flash Loan Liquidation Surface",
                description="Liquidation mechanisms can be exploited using flash loans.",
                root_cause="Liquidation can be triggered and executed within a single transaction.",
                exploitability="Attacker flash loans collateral, triggers own liquidation, profits from bonus.",
                impact="Protocol may incur bad debt from manipulated liquidations.",
                recommendation="Implement liquidation thresholds with buffer and fair liquidation mechanisms.",
                risk_level=RiskLevel.HIGH,
                category="Flash Loan",
            ))

        return flash_loan_risk

    def analyze_governance_security(self) -> dict[str, Any]:
        """Phase 4: Governance mechanism review."""
        voting_mechanism = self.config.get("voting_mechanism", "unknown")
        proposal_threshold = self.config.get("proposal_threshold", "unknown")
        timelock_duration = self.config.get("timelock_duration", "none")
        quorum_requirement = self.config.get("quorum_requirement", "unknown")

        governance_security = {
            "voting_mechanism": voting_mechanism,
            "proposal_threshold": proposal_threshold,
            "timelock_duration": timelock_duration,
            "quorum_requirement": quorum_requirement,
            "flash_loan_voting_risk": voting_mechanism in ("token_weighted", "delegated"),
        }

        self.analysis.governance_security = governance_security

        # Generate findings
        if timelock_duration == "none":
            self.analysis.findings.append(Finding(
                title="No Governance Timelock",
                description="Governance proposals can be executed immediately after passing.",
                root_cause="No delay between proposal approval and execution.",
                exploitability="Flash loan governance attack can execute within a single transaction.",
                impact="Malicious proposals can be executed before community can respond.",
                recommendation="Implement minimum 48-hour timelock for all governance actions.",
                risk_level=RiskLevel.CRITICAL,
                category="Governance",
            ))

        if voting_mechanism == "token_weighted":
            self.analysis.findings.append(Finding(
                title="Token-Weighted Voting Vulnerable to Flash Loans",
                description="Voting power is proportional to current token balance.",
                root_cause="No snapshot mechanism; voting power can be borrowed via flash loans.",
                exploitability="Attacker borrows tokens, votes, repays in same transaction.",
                impact="Governance capture is possible with zero capital.",
                recommendation="Implement voting power snapshots or use quadratic voting.",
                risk_level=RiskLevel.HIGH,
                category="Governance",
            ))

        return governance_security

    def analyze_economic_surface(self) -> dict[str, Any]:
        """Phase 5: Economic attack surface mapping."""
        inflation_attack_risk = self.config.get("inflation_attack_risk", "unknown")
        donation_attack_risk = self.config.get("donation_attack_risk", "unknown")
        liquidation_incentives = self.config.get("liquidation_incentives", "unknown")
        peg_mechanism = self.config.get("peg_mechanism", "unknown")

        economic_surface = {
            "inflation_attack_risk": inflation_attack_risk,
            "donation_attack_risk": donation_attack_risk,
            "liquidation_incentives": liquidation_incentives,
            "peg_mechanism": peg_mechanism,
        }

        self.analysis.economic_surface = economic_surface

        # Generate findings
        if inflation_attack_risk == "high":
            self.analysis.findings.append(Finding(
                title="High Inflation Attack Risk",
                description="Share/asset ratio can be corrupted via direct donations.",
                root_cause="Vault accounting does not protect against direct token transfers.",
                exploitability="Attacker donates tokens directly to vault, corrupts share price, drains funds.",
                impact="Other depositors lose funds due to corrupted share price.",
                recommendation="Use ERC-4626 with virtual shares or implement donation attack prevention.",
                risk_level=RiskLevel.CRITICAL,
                category="Economic",
            ))

        if donation_attack_risk == "high":
            self.analysis.findings.append(Finding(
                title="High Donation Attack Risk",
                description="Direct token transfers can corrupt internal accounting.",
                root_cause="Internal balance tracking does not account for direct transfers.",
                exploitability="Attacker sends tokens directly to contract, corrupts accounting.",
                impact="Accounting discrepancies can be exploited for profit.",
                recommendation="Use balanceOf for share calculations instead of internal accounting.",
                risk_level=RiskLevel.HIGH,
                category="Economic",
            ))

        return economic_surface

    def analyze_composability_risks(self) -> dict[str, Any]:
        """Phase 6: Composability risk analysis."""
        integrations = self.config.get("integrations", [])
        cascade_risk = self.config.get("cascade_risk", "unknown")
        token_standards = self.config.get("token_standards", [])

        composability_risks = {
            "integrations": integrations,
            "integration_count": len(integrations),
            "cascade_risk": cascade_risk,
            "token_standards": token_standards,
        }

        self.analysis.composability_risks = composability_risks

        # Generate findings
        if cascade_risk == "high":
            self.analysis.findings.append(Finding(
                title="High Cascade Failure Risk",
                description="Protocol failure could cascade to dependent protocols.",
                root_cause="Deep integration with other protocols without isolation mechanisms.",
                exploitability="Failure in one protocol triggers failures in dependent protocols.",
                impact="Systemic risk across multiple protocols and users.",
                recommendation="Implement exposure limits, circuit breakers, and emergency shutdown mechanisms.",
                risk_level=RiskLevel.HIGH,
                category="Composability",
            ))

        if "rebasing" in token_standards:
            self.analysis.findings.append(Finding(
                title="Rebasing Token Risk",
                description="Protocol integrates with rebasing tokens that change balance automatically.",
                root_cause="Rebasing tokens modify balances without explicit transfers.",
                exploitability="Share calculations may not account for rebasing correctly.",
                impact="Accounting errors can lead to fund loss.",
                recommendation="Use wrapped versions of rebasing tokens or implement rebasing-aware accounting.",
                risk_level=RiskLevel.MEDIUM,
                category="Composability",
            ))

        return composability_risks

    def calculate_risk_scores(self) -> dict[str, int]:
        """Calculate risk scores for each category (1-10 scale)."""
        scores = {}

        # Oracle security score
        oracle_score = 5
        if self.analysis.oracle_security.get("oracle_type") == "spot":
            oracle_score = 9
        elif self.analysis.oracle_security.get("oracle_type") == "twap":
            oracle_score = 4
        elif self.analysis.oracle_security.get("oracle_type") == "chainlink":
            oracle_score = 2
        if not self.analysis.oracle_security.get("twap_enabled"):
            oracle_score += 1
        if not self.analysis.oracle_security.get("circuit_breaker"):
            oracle_score += 1
        scores["oracle_security"] = min(oracle_score, 10)

        # Flash loan risk score
        flash_score = 3
        if self.analysis.flash_loan_risk.get("atomicity_possible"):
            flash_score += 3
        if "governance" in self.analysis.flash_loan_risk.get("attack_surfaces", []):
            flash_score += 2
        if "oracle" in self.analysis.flash_loan_risk.get("attack_surfaces", []):
            flash_score += 2
        scores["flash_loan_risk"] = min(flash_score, 10)

        # Governance security score
        gov_score = 3
        if self.analysis.governance_security.get("timelock_duration") == "none":
            gov_score += 4
        if self.analysis.governance_security.get("flash_loan_voting_risk"):
            gov_score += 2
        scores["governance_security"] = min(gov_score, 10)

        # Economic attack surface score
        econ_score = 3
        if self.analysis.economic_surface.get("inflation_attack_risk") == "high":
            econ_score += 4
        if self.analysis.economic_surface.get("donation_attack_risk") == "high":
            econ_score += 2
        scores["economic_surface"] = min(econ_score, 10)

        # Composability risk score
        comp_score = 3
        if self.analysis.composability_risks.get("cascade_risk") == "high":
            comp_score += 3
        if self.analysis.composability_risks.get("integration_count", 0) > 5:
            comp_score += 2
        scores["composability_risk"] = min(comp_score, 10)

        # Architecture risk score
        arch_score = 3
        if self.analysis.architecture.get("admin_key_risk") == "Critical":
            arch_score += 4
        if self.analysis.architecture.get("upgrade_mechanism") == "instant":
            arch_score += 3
        scores["architecture"] = min(arch_score, 10)

        self.analysis.risk_scores = scores
        return scores

    def run_full_analysis(self) -> ProtocolAnalysis:
        """Run all analysis phases."""
        self.analyze_architecture()
        self.analyze_oracle_security()
        self.analyze_flash_loan_risk()
        self.analyze_governance_security()
        self.analyze_economic_surface()
        self.analyze_composability_risks()
        self.calculate_risk_scores()
        return self.analysis

    def generate_report(self) -> str:
        """Generate a structured security report."""
        if not self.analysis.risk_scores:
            self.run_full_analysis()

        report = []
        report.append(f"# Protocol Security Report: {self.protocol_name}")
        report.append("")
        report.append("## Executive Summary")
        report.append(f"- **Overall Risk Rating:** {self.analysis.overall_risk.value}")
        report.append(f"- **Protocol Category:** {self.analysis.category}")
        report.append(f"- **Total Findings:** {len(self.analysis.findings)}")

        critical = sum(1 for f in self.analysis.findings if f.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for f in self.analysis.findings if f.risk_level == RiskLevel.HIGH)
        medium = sum(1 for f in self.analysis.findings if f.risk_level == RiskLevel.MEDIUM)
        low = sum(1 for f in self.analysis.findings if f.risk_level == RiskLevel.LOW)
        report.append(f"- **Findings Breakdown:** Critical: {critical}, High: {high}, Medium: {medium}, Low: {low}")
        report.append("")

        report.append("## Protocol Architecture")
        arch = self.analysis.architecture
        report.append(f"- **Contract Count:** {arch.get('contract_count', 'N/A')}")
        report.append(f"- **External Dependencies:** {arch.get('dependency_count', 'N/A')}")
        report.append(f"- **Upgrade Mechanism:** {arch.get('upgrade_mechanism', 'N/A')}")
        report.append(f"- **Admin Key Risk:** {arch.get('admin_key_risk', 'N/A')}")
        report.append("")

        report.append("## Oracle Security")
        oracle = self.analysis.oracle_security
        report.append(f"- **Oracle Type:** {oracle.get('oracle_type', 'N/A')}")
        report.append(f"- **TWAP Enabled:** {oracle.get('twap_enabled', 'N/A')}")
        report.append(f"- **Circuit Breaker:** {oracle.get('circuit_breaker', 'N/A')}")
        report.append(f"- **Manipulation Cost:** {oracle.get('manipulation_cost', 'N/A')}")
        report.append(f"- **Flash Loan Amplifiable:** {oracle.get('flash_loan_amplifiable', 'N/A')}")
        report.append("")

        report.append("## Flash Loan Risk")
        flash = self.analysis.flash_loan_risk
        report.append(f"- **Providers:** {', '.join(flash.get('providers', [])) or 'N/A'}")
        report.append(f"- **Attack Surfaces:** {flash.get('surface_count', 0)}")
        report.append(f"- **Atomicity Possible:** {flash.get('atomicity_possible', 'N/A')}")
        report.append("")

        report.append("## Governance Security")
        gov = self.analysis.governance_security
        report.append(f"- **Voting Mechanism:** {gov.get('voting_mechanism', 'N/A')}")
        report.append(f"- **Timelock Duration:** {gov.get('timelock_duration', 'N/A')}")
        report.append(f"- **Flash Loan Voting Risk:** {gov.get('flash_loan_voting_risk', 'N/A')}")
        report.append("")

        report.append("## Economic Attack Surface")
        econ = self.analysis.economic_surface
        report.append(f"- **Inflation Attack Risk:** {econ.get('inflation_attack_risk', 'N/A')}")
        report.append(f"- **Donation Attack Risk:** {econ.get('donation_attack_risk', 'N/A')}")
        report.append(f"- **Liquidation Incentives:** {econ.get('liquidation_incentives', 'N/A')}")
        report.append("")

        report.append("## Composability Risks")
        comp = self.analysis.composability_risks
        report.append(f"- **Integration Count:** {comp.get('integration_count', 'N/A')}")
        report.append(f"- **Cascade Risk:** {comp.get('cascade_risk', 'N/A')}")
        report.append("")

        report.append("## Risk Scoring")
        report.append("| Category | Risk Level | Score (1-10) |")
        report.append("|----------|-----------|--------------|")
        for category, score in self.analysis.risk_scores.items():
            level = RiskLevel.CRITICAL if score >= 8 else RiskLevel.HIGH if score >= 6 else RiskLevel.MEDIUM if score >= 4 else RiskLevel.LOW
            report.append(f"| {category.replace('_', ' ').title()} | {level.value} | {score} |")
        report.append("")

        if self.analysis.findings:
            report.append("## Findings")
            report.append("")
            for finding in sorted(self.analysis.findings, key=lambda f: f.risk_level.value):
                report.append(f"### [{finding.risk_level.value}] {finding.title}")
                report.append(f"- **Category:** {finding.category}")
                report.append(f"- **Description:** {finding.description}")
                report.append(f"- **Root Cause:** {finding.root_cause}")
                report.append(f"- **Exploitability:** {finding.exploitability}")
                report.append(f"- **Impact:** {finding.impact}")
                report.append(f"- **Recommendation:** {finding.recommendation}")
                report.append("")

        report.append("## Recommendations")
        report.append("1. Address all Critical findings before proceeding with audit.")
        report.append("2. Implement TWAP or decentralized oracle feeds for price-dependent operations.")
        report.append("3. Add timelock (minimum 48 hours) for governance and upgrade mechanisms.")
        report.append("4. Implement circuit breakers for emergency shutdown.")
        report.append("5. Use multi-signature wallets for admin key management.")
        report.append("6. Conduct comprehensive testing including flash loan attack scenarios.")
        report.append("7. Engage multiple independent audit firms for code review.")

        return "\n".join(report)


def interactive_mode():
    """Run analyzer in interactive mode."""
    print("=" * 60)
    print("DeFi Protocol Security Analyzer - Interactive Mode")
    print("=" * 60)
    print()

    protocol_name = input("Enter protocol name: ").strip()
    if not protocol_name:
        print("Protocol name is required.")
        sys.exit(1)

    config = {}

    print("\n--- Protocol Architecture ---")
    contracts = input("Contract names (comma-separated): ").strip()
    config["contracts"] = [c.strip() for c in contracts.split(",") if c.strip()]

    dependencies = input("External dependencies (comma-separated): ").strip()
    config["dependencies"] = [d.strip() for d in dependencies.split(",") if d.strip()]

    config["upgrade_mechanism"] = input("Upgrade mechanism (instant/timelock/proxy): ").strip() or "unknown"
    config["admin_keys"] = input("Admin keys (single/multisig/timelock/dao): ").strip() or "unknown"

    print("\n--- Oracle Security ---")
    config["oracle_type"] = input("Oracle type (spot/twap/chainlink/custom): ").strip() or "unknown"
    config["twap_enabled"] = input("TWAP enabled? (yes/no): ").strip().lower() == "yes"
    config["circuit_breaker"] = input("Circuit breaker? (yes/no): ").strip().lower() == "yes"

    print("\n--- Flash Loan Risk ---")
    providers = input("Flash loan providers (comma-separated): ").strip()
    config["flash_loan_providers"] = [p.strip() for p in providers.split(",") if p.strip()]

    surfaces = input("Attack surfaces (comma-separated, e.g., governance,oracle,liquidation): ").strip()
    config["attack_surfaces"] = [s.strip() for s in surfaces.split(",") if s.strip()]

    print("\n--- Governance Security ---")
    config["voting_mechanism"] = input("Voting mechanism (token_weighted/delegated/quadratic): ").strip() or "unknown"
    config["timelock_duration"] = input("Timelock duration (none/48h/7d): ").strip() or "none"

    print("\n--- Economic Attack Surface ---")
    config["inflation_attack_risk"] = input("Inflation attack risk (high/medium/low): ").strip() or "unknown"
    config["donation_attack_risk"] = input("Donation attack risk (high/medium/low): ").strip() or "unknown"

    print("\n--- Composability Risks ---")
    integrations = input("Integrations (comma-separated): ").strip()
    config["integrations"] = [i.strip() for i in integrations.split(",") if i.strip()]
    config["cascade_risk"] = input("Cascade risk (high/medium/low): ").strip() or "unknown"

    analyzer = ProtocolAnalyzer(protocol_name, config)
    analyzer.run_full_analysis()

    print("\n" + "=" * 60)
    print(analyzer.generate_report())


def main():
    parser = argparse.ArgumentParser(
        description="DeFi Protocol Security Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python protocol-analyzer.py --protocol Aave --config config.json
  python protocol-analyzer.py --interactive
  python protocol-analyzer.py --protocol Uniswap --category amm
        """,
    )
    parser.add_argument("--protocol", "-p", help="Protocol name to analyze")
    parser.add_argument("--config", "-c", help="Path to JSON configuration file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--category", help="Override protocol category")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.protocol:
        parser.error("--protocol is required (or use --interactive)")

    config = {}
    if args.config:
        try:
            with open(args.config) as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    analyzer = ProtocolAnalyzer(args.protocol, config)
    if args.category:
        analyzer.category = args.category
        analyzer.analysis.category = args.category

    analyzer.run_full_analysis()
    report = analyzer.generate_report()

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
