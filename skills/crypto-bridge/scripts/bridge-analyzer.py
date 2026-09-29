#!/usr/bin/env python3
"""
Bridge Security Analyzer

Analyzes cross-chain bridge security by assessing architecture, validator sets,
signature schemes, message replay risk, and liquidity solvency.

Usage:
    python3 bridge-analyzer.py --bridge-config config.json
    python3 bridge-analyzer.py --source 0x... --destination 0x... --rpc-url $RPC_URL
    python3 bridge-analyzer.py --tvl 100000000 --validators 9 --threshold 5
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class BridgeArchitecture(Enum):
    """Bridge architecture types."""
    LOCK_AND_MINT = "lock-and-mint"
    BURN_AND_MINT = "burn-and-mint"
    LIQUIDITY_POOL = "liquidity-pool"
    LIGHT_CLIENT = "light-client"
    OPTIMISTIC = "optimistic"
    UNKNOWN = "unknown"


class SignatureScheme(Enum):
    """Signature schemes used by bridges."""
    ECDSA = "ecdsa"
    BLS = "bls"
    SCHNORR = "schnorr"
    MPC = "mpc"
    MULTISIG = "multisig"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ValidatorSet:
    """Represents a bridge validator set."""
    total_validators: int
    threshold: int
    validators: list = field(default_factory=list)
    is_decentralized: bool = False
    has_slashing: bool = False
    key_rotation_period: int = 0  # days

    @property
    def collusion_resistance(self) -> float:
        """Calculate collusion resistance score (0.0 to 1.0)."""
        if self.total_validators == 0:
            return 0.0

        # Higher threshold ratio = better
        threshold_ratio = self.threshold / self.total_validators

        # More validators = better (diminishing returns)
        count_score = min(1.0, self.total_validators / 20)

        # Decentralization bonus
        decentralization_bonus = 0.2 if self.is_decentralized else 0.0

        # Slashing bonus
        slashing_bonus = 0.1 if self.has_slashing else 0.0

        score = (threshold_ratio * 0.5) + (count_score * 0.2) + decentralization_bonus + slashing_bonus
        return min(1.0, score)

    @property
    def risk_level(self) -> RiskLevel:
        """Determine risk level based on validator set security."""
        if self.total_validators < 4:
            return RiskLevel.CRITICAL
        elif self.threshold / self.total_validators < 0.5:
            return RiskLevel.HIGH
        elif self.total_validators < 10:
            return RiskLevel.MEDIUM
        elif not self.is_decentralized:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


@dataclass
class SignatureConfig:
    """Represents signature verification configuration."""
    scheme: SignatureScheme
    threshold: int
    total_signers: int
    has_replay_protection: bool = False
    has_chain_id_binding: bool = False
    has_nonce_tracking: bool = False
    is_formally_verified: bool = False

    @property
    def security_score(self) -> float:
        """Calculate signature security score (0.0 to 1.0)."""
        score = 0.0

        # Scheme security
        if self.scheme == SignatureScheme.BLS:
            score += 0.3
        elif self.scheme == SignatureScheme.ECDSA:
            score += 0.25
        elif self.scheme == SignatureScheme.MPC:
            score += 0.25
        elif self.scheme == SignatureScheme.MULTISIG:
            score += 0.2
        else:
            score += 0.1

        # Threshold ratio
        if self.total_signers > 0:
            threshold_ratio = self.threshold / self.total_signers
            score += threshold_ratio * 0.3

        # Replay protection
        if self.has_replay_protection:
            score += 0.15
        if self.has_chain_id_binding:
            score += 0.1
        if self.has_nonce_tracking:
            score += 0.1

        # Formal verification
        if self.is_formally_verified:
            score += 0.1

        return min(1.0, score)

    @property
    def risk_level(self) -> RiskLevel:
        """Determine risk level based on signature security."""
        if not self.has_replay_protection:
            return RiskLevel.CRITICAL
        elif not self.has_chain_id_binding:
            return RiskLevel.HIGH
        elif self.security_score < 0.4:
            return RiskLevel.HIGH
        elif self.security_score < 0.6:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


@dataclass
class LiquidityStatus:
    """Represents bridge liquidity status."""
    total_locked: float  # USD
    total_minted: float  # USD
    pool_depth: float  # USD
    withdrawal_capacity: float  # USD

    @property
    def solvency_ratio(self) -> float:
        """Calculate solvency ratio (locked / minted)."""
        if self.total_minted == 0:
            return float("inf")
        return self.total_locked / self.total_minted

    @property
    def is_solvent(self) -> bool:
        """Check if bridge is solvent."""
        return self.solvency_ratio >= 1.0

    @property
    def risk_level(self) -> RiskLevel:
        """Determine risk level based on liquidity."""
        if self.solvency_ratio < 0.8:
            return RiskLevel.CRITICAL
        elif self.solvency_ratio < 1.0:
            return RiskLevel.HIGH
        elif self.solvency_ratio < 1.2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


@dataclass
class BridgeConfig:
    """Represents a bridge configuration for analysis."""
    name: str
    architecture: BridgeArchitecture
    source_chain: str
    destination_chain: str
    validator_set: ValidatorSet
    signature_config: SignatureConfig
    liquidity: LiquidityStatus
    has_upgrade_timelock: bool = False
    upgrade_timelock_hours: int = 0
    has_admin_multisig: bool = False
    admin_threshold: int = 0
    admin_total: int = 0
    has_emergency_pause: bool = False
    has_rate_limits: bool = False


class BridgeAnalyzer:
    """Analyzes bridge security configuration."""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.findings: list[dict] = []

    def analyze(self) -> dict:
        """Run complete bridge security analysis."""
        self.findings = []

        # Architecture analysis
        self._analyze_architecture()

        # Validator set analysis
        self._analyze_validator_set()

        # Signature scheme analysis
        self._analyze_signature_scheme()

        # Message replay analysis
        self._analyze_message_replay()

        # Liquidity analysis
        self._analyze_liquidity()

        # Upgrade security analysis
        self._analyze_upgrade_security()

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk()

        return {
            "bridge_name": self.config.name,
            "architecture": self.config.architecture.value,
            "overall_risk": overall_risk.value,
            "risk_score": self._calculate_risk_score(),
            "findings": self.findings,
            "validator_set": {
                "total": self.config.validator_set.total_validators,
                "threshold": self.config.validator_set.threshold,
                "collusion_resistance": self.config.validator_set.collusion_resistance,
                "risk_level": self.config.validator_set.risk_level.value,
            },
            "signature": {
                "scheme": self.config.signature_config.scheme.value,
                "security_score": self.config.signature_config.security_score,
                "risk_level": self.config.signature_config.risk_level.value,
            },
            "liquidity": {
                "total_locked": self.config.liquidity.total_locked,
                "total_minted": self.config.liquidity.total_minted,
                "solvency_ratio": self.config.liquidity.solvency_ratio,
                "is_solvent": self.config.liquidity.is_solvent,
                "risk_level": self.config.liquidity.risk_level.value,
            },
        }

    def _analyze_architecture(self):
        """Analyze bridge architecture risks."""
        arch = self.config.architecture

        if arch == BridgeArchitecture.UNKNOWN:
            self._add_finding(
                RiskLevel.HIGH,
                "Unknown architecture",
                "Bridge architecture could not be determined. Manual review required.",
            )
        elif arch == BridgeArchitecture.OPTIMISTIC:
            self._add_finding(
                RiskLevel.MEDIUM,
                "Optimistic verification delay",
                "Optimistic bridges have a dispute window delay. Ensure dispute mechanism is secure.",
            )
        elif arch == BridgeArchitecture.LIGHT_CLIENT:
            self._add_finding(
                RiskLevel.MEDIUM,
                "Light client dependency",
                "Light client bridges depend on source chain consensus security. Assess source chain attack cost.",
            )

    def _analyze_validator_set(self):
        """Analyze validator set security."""
        vs = self.config.validator_set

        if vs.total_validators < 4:
            self._add_finding(
                RiskLevel.CRITICAL,
                "Insufficient validator count",
                f"Only {vs.total_validators} validators. Minimum recommended: 10+.",
            )

        if vs.threshold / vs.total_validators < 0.5:
            self._add_finding(
                RiskLevel.HIGH,
                "Low collusion threshold",
                f"Threshold is {vs.threshold}/{vs.total_validators}. Recommended: 2/3 or higher.",
            )

        if not vs.is_decentralized:
            self._add_finding(
                RiskLevel.HIGH,
                "Centralized validator set",
                "Validator set is not decentralized. Single entity control risk.",
            )

        if not vs.has_slashing:
            self._add_finding(
                RiskLevel.MEDIUM,
                "No slashing conditions",
                "No economic penalties for malicious validation. Implement slashing.",
            )

    def _analyze_signature_scheme(self):
        """Analyze signature scheme security."""
        sig = self.config.signature_config

        if sig.scheme == SignatureScheme.UNKNOWN:
            self._add_finding(
                RiskLevel.HIGH,
                "Unknown signature scheme",
                "Signature scheme could not be determined. Manual review required.",
            )

        if not sig.has_replay_protection:
            self._add_finding(
                RiskLevel.CRITICAL,
                "No replay protection",
                "Messages can be replayed to mint assets multiple times. Implement nonce tracking.",
            )

        if not sig.has_chain_id_binding:
            self._add_finding(
                RiskLevel.HIGH,
                "No chain ID binding",
                "Messages not bound to specific chains. Cross-chain replay possible.",
            )

        if not sig.is_formally_verified:
            self._add_finding(
                RiskLevel.MEDIUM,
                "Signature verification not formally verified",
                "Critical signature verification logic should be formally verified.",
            )

    def _analyze_message_replay(self):
        """Analyze message replay risk."""
        sig = self.config.signature_config

        replay_risk = 0
        if not sig.has_replay_protection:
            replay_risk += 3
        if not sig.has_chain_id_binding:
            replay_risk += 2
        if not sig.has_nonce_tracking:
            replay_risk += 2

        if replay_risk >= 5:
            self._add_finding(
                RiskLevel.CRITICAL,
                "High message replay risk",
                "Multiple replay vulnerabilities detected. Immediate remediation required.",
            )
        elif replay_risk >= 3:
            self._add_finding(
                RiskLevel.HIGH,
                "Medium message replay risk",
                "Some replay protections missing. Review and implement missing protections.",
            )

    def _analyze_liquidity(self):
        """Analyze liquidity solvency."""
        liq = self.config.liquidity

        if not liq.is_solvent:
            self._add_finding(
                RiskLevel.CRITICAL,
                "Bridge insolvent",
                f"Solvency ratio: {liq.solvency_ratio:.2f}. Locked assets do not cover minted assets.",
            )
        elif liq.solvency_ratio < 1.2:
            self._add_finding(
                RiskLevel.MEDIUM,
                "Low liquidity buffer",
                f"Solvency ratio: {liq.solvency_ratio:.2f}. Recommended: 1.5+ for safety buffer.",
            )

        if liq.pool_depth < liq.total_minted * 0.1:
            self._add_finding(
                RiskLevel.HIGH,
                "Insufficient pool depth",
                "Pool depth is less than 10% of minted assets. Large withdrawals may fail.",
            )

    def _analyze_upgrade_security(self):
        """Analyze upgrade and admin security."""
        if not self.config.has_upgrade_timelock:
            self._add_finding(
                RiskLevel.HIGH,
                "No upgrade timelock",
                "Bridge can be upgraded without delay. Implement 48+ hour timelock.",
            )
        elif self.config.upgrade_timelock_hours < 48:
            self._add_finding(
                RiskLevel.MEDIUM,
                "Short upgrade timelock",
                f"Upgrade timelock is {self.config.upgrade_timelock_hours}h. Recommended: 48+h.",
            )

        if not self.config.has_admin_multisig:
            self._add_finding(
                RiskLevel.CRITICAL,
                "No admin multisig",
                "Single admin key can upgrade or drain bridge. Implement multisig immediately.",
            )
        elif self.config.admin_threshold / self.config.admin_total < 0.5:
            self._add_finding(
                RiskLevel.HIGH,
                "Low admin threshold",
                f"Admin threshold is {self.config.admin_threshold}/{self.config.admin_total}. Recommended: 2/3 or higher.",
            )

        if not self.config.has_emergency_pause:
            self._add_finding(
                RiskLevel.MEDIUM,
                "No emergency pause",
                "No mechanism to pause bridge during incidents. Implement circuit breaker.",
            )

    def _add_finding(self, severity: RiskLevel, title: str, description: str):
        """Add a finding to the report."""
        self.findings.append({
            "severity": severity.value,
            "title": title,
            "description": description,
        })

    def _calculate_overall_risk(self) -> RiskLevel:
        """Calculate overall risk level."""
        critical_count = sum(1 for f in self.findings if f["severity"] == "critical")
        high_count = sum(1 for f in self.findings if f["severity"] == "high")

        if critical_count > 0:
            return RiskLevel.CRITICAL
        elif high_count >= 3:
            return RiskLevel.HIGH
        elif high_count > 0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_risk_score(self) -> float:
        """Calculate overall risk score (0-10, higher = more risky)."""
        score = 0.0

        for finding in self.findings:
            if finding["severity"] == "critical":
                score += 3.0
            elif finding["severity"] == "high":
                score += 2.0
            elif finding["severity"] == "medium":
                score += 1.0
            elif finding["severity"] == "low":
                score += 0.5

        return min(10.0, score)


def load_config(config_path: str) -> BridgeConfig:
    """Load bridge configuration from JSON file."""
    with open(config_path, "r") as f:
        data = json.load(f)

    return BridgeConfig(
        name=data.get("name", "Unknown Bridge"),
        architecture=BridgeArchitecture(data.get("architecture", "unknown")),
        source_chain=data.get("source_chain", "unknown"),
        destination_chain=data.get("destination_chain", "unknown"),
        validator_set=ValidatorSet(
            total_validators=data.get("validator_set", {}).get("total", 0),
            threshold=data.get("validator_set", {}).get("threshold", 0),
            validators=data.get("validator_set", {}).get("validators", []),
            is_decentralized=data.get("validator_set", {}).get("is_decentralized", False),
            has_slashing=data.get("validator_set", {}).get("has_slashing", False),
            key_rotation_period=data.get("validator_set", {}).get("key_rotation_period", 0),
        ),
        signature_config=SignatureConfig(
            scheme=SignatureScheme(data.get("signature", {}).get("scheme", "unknown")),
            threshold=data.get("signature", {}).get("threshold", 0),
            total_signers=data.get("signature", {}).get("total_signers", 0),
            has_replay_protection=data.get("signature", {}).get("has_replay_protection", False),
            has_chain_id_binding=data.get("signature", {}).get("has_chain_id_binding", False),
            has_nonce_tracking=data.get("signature", {}).get("has_nonce_tracking", False),
            is_formally_verified=data.get("signature", {}).get("is_formally_verified", False),
        ),
        liquidity=LiquidityStatus(
            total_locked=data.get("liquidity", {}).get("total_locked", 0),
            total_minted=data.get("liquidity", {}).get("total_minted", 0),
            pool_depth=data.get("liquidity", {}).get("pool_depth", 0),
            withdrawal_capacity=data.get("liquidity", {}).get("withdrawal_capacity", 0),
        ),
        has_upgrade_timelock=data.get("upgrade", {}).get("has_timelock", False),
        upgrade_timelock_hours=data.get("upgrade", {}).get("timelock_hours", 0),
        has_admin_multisig=data.get("admin", {}).get("has_multisig", False),
        admin_threshold=data.get("admin", {}).get("threshold", 0),
        admin_total=data.get("admin", {}).get("total", 0),
        has_emergency_pause=data.get("admin", {}).get("has_emergency_pause", False),
        has_rate_limits=data.get("admin", {}).get("has_rate_limits", False),
    )


def create_sample_config() -> dict:
    """Create a sample bridge configuration."""
    return {
        "name": "Sample Bridge",
        "architecture": "lock-and-mint",
        "source_chain": "ethereum",
        "destination_chain": "polygon",
        "validator_set": {
            "total_validators": 13,
            "threshold": 9,
            "validators": [],
            "is_decentralized": True,
            "has_slashing": True,
            "key_rotation_period": 30,
        },
        "signature": {
            "scheme": "ecdsa",
            "threshold": 9,
            "total_signers": 13,
            "has_replay_protection": True,
            "has_chain_id_binding": True,
            "has_nonce_tracking": True,
            "is_formally_verified": False,
        },
        "liquidity": {
            "total_locked": 100000000,
            "total_minted": 95000000,
            "pool_depth": 10000000,
            "withdrawal_capacity": 5000000,
        },
        "upgrade": {
            "has_timelock": True,
            "timelock_hours": 72,
        },
        "admin": {
            "has_multisig": True,
            "threshold": 3,
            "total": 5,
            "has_emergency_pause": True,
            "has_rate_limits": True,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze cross-chain bridge security"
    )
    parser.add_argument(
        "--bridge-config",
        help="Path to bridge configuration JSON file",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run analysis on sample configuration",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.sample:
        config_data = create_sample_config()
        config = BridgeConfig(
            name=config_data["name"],
            architecture=BridgeArchitecture(config_data["architecture"]),
            source_chain=config_data["source_chain"],
            destination_chain=config_data["destination_chain"],
            validator_set=ValidatorSet(**config_data["validator_set"]),
            signature_config=SignatureConfig(
                scheme=SignatureScheme(config_data["signature"]["scheme"]),
                **{k: v for k, v in config_data["signature"].items() if k != "scheme"},
            ),
            liquidity=LiquidityStatus(**config_data["liquidity"]),
            has_upgrade_timelock=config_data["upgrade"]["has_timelock"],
            upgrade_timelock_hours=config_data["upgrade"]["timelock_hours"],
            has_admin_multisig=config_data["admin"]["has_multisig"],
            admin_threshold=config_data["admin"]["threshold"],
            admin_total=config_data["admin"]["total"],
            has_emergency_pause=config_data["admin"]["has_emergency_pause"],
            has_rate_limits=config_data["admin"]["has_rate_limits"],
        )
    elif args.bridge_config:
        config = load_config(args.bridge_config)
    else:
        print("Error: Specify --bridge-config or --sample")
        sys.exit(1)

    analyzer = BridgeAnalyzer(config)
    result = analyzer.analyze()

    if args.format == "json":
        output = json.dumps(result, indent=2)
    else:
        output = format_text_report(result)

    if args.output != "-":
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


def format_text_report(result: dict) -> str:
    """Format analysis result as text report."""
    lines = [
        f"\n{'='*60}",
        f"Bridge Security Analysis: {result['bridge_name']}",
        f"{'='*60}",
        f"",
        f"Architecture: {result['architecture']}",
        f"Overall Risk: {result['overall_risk'].upper()}",
        f"Risk Score: {result['risk_score']:.1f}/10",
        f"",
        f"Validator Set:",
        f"  Total: {result['validator_set']['total']}",
        f"  Threshold: {result['validator_set']['threshold']}",
        f"  Collusion Resistance: {result['validator_set']['collusion_resistance']:.0%}",
        f"  Risk Level: {result['validator_set']['risk_level'].upper()}",
        f"",
        f"Signature Scheme:",
        f"  Scheme: {result['signature']['scheme']}",
        f"  Security Score: {result['signature']['security_score']:.0%}",
        f"  Risk Level: {result['signature']['risk_level'].upper()}",
        f"",
        f"Liquidity:",
        f"  Total Locked: ${result['liquidity']['total_locked']:,.0f}",
        f"  Total Minted: ${result['liquidity']['total_minted']:,.0f}",
        f"  Solvency Ratio: {result['liquidity']['solvency_ratio']:.2f}",
        f"  Solvent: {'Yes' if result['liquidity']['is_solvent'] else 'No'}",
        f"  Risk Level: {result['liquidity']['risk_level'].upper()}",
        f"",
        f"Findings ({len(result['findings'])}):",
    ]

    for finding in result["findings"]:
        lines.append(f"")
        lines.append(f"  [{finding['severity'].upper()}] {finding['title']}")
        lines.append(f"    {finding['description']}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
