#!/usr/bin/env python3
"""
On-Chain Transaction Tracer
Traces transactions, identifies fund flows, and collects evidence
for on-chain incident investigation.

Usage:
    python tx-tracer.py --tx 0xabc123... --chain ethereum
    python tx-tracer.py --address 0xattacker... --chain ethereum
    python tx-tracer.py --tx 0xabc123... --cross-chain
    python tx-tracer.py --interactive
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Chain(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BSC = "bsc"
    SOLANA = "solana"
    AVALANCHE = "avalanche"


class FundStatus(Enum):
    ACTIVE = "Active"
    FROZEN = "Frozen"
    RECOVERED = "Recovered"
    MIXED = "Mixed"
    AT_LARGE = "At Large"
    UNKNOWN = "Unknown"


@dataclass
class Transaction:
    hash: str
    chain: Chain
    from_address: str
    to_address: str
    value: float
    token: str
    timestamp: str
    block_number: int
    status: str = "success"
    internal_txs: list[dict[str, Any]] = field(default_factory=list)
    input_data: str = ""
    gas_used: int = 0
    gas_price: int = 0

    @property
    def value_usd(self) -> float:
        """Approximate USD value (would need price oracle in production)."""
        return 0.0  # Placeholder


@dataclass
class FundFlow:
    source: str
    destination: str
    amount: float
    token: str
    tx_hash: str
    chain: Chain
    timestamp: str
    via: str = "direct"  # direct, bridge, dex, mixer
    status: FundStatus = FundStatus.ACTIVE


@dataclass
class AttackerProfile:
    primary_address: str
    clustered_addresses: list[str] = field(default_factory=list)
    funding_source: str = "unknown"
    attribution_confidence: str = "speculative"
    known_affiliation: str = "none"
    total_stolen: float = 0.0
    current_holdings: float = 0.0
    fund_status: FundStatus = FundStatus.UNKNOWN


@dataclass
class EvidenceItem:
    tx_hash: str
    chain: Chain
    data_type: str  # transaction, internal_tx, event_log, state_diff
    data: dict[str, Any]
    timestamp: str
    sha256_hash: str = ""

    def __post_init__(self):
        if not self.sha256_hash:
            self.sha256_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class Investigation:
    incident_name: str
    incident_type: str
    start_date: str
    chains: list[Chain]
    transactions: list[Transaction] = field(default_factory=list)
    fund_flows: list[FundFlow] = field(default_factory=list)
    attacker: AttackerProfile | None = None
    evidence: list[EvidenceItem] = field(default_factory=list)
    total_loss: float = 0.0
    funds_recovered: float = 0.0
    status: str = "active"


class TransactionTracer:
    """Main tracer class for on-chain investigation."""

    KNOWN_MIXERS = {
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash 0.1 ETH",
        "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c0c2bd7d": "Tornado Cash 1 ETH",
        "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash 10 ETH",
        "0xa160cdab225685da1d56aa342ad8841c3b53f291d": "Tornado Cash 100 ETH",
        "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash 1000 ETH",
    }

    KNOWN_BRIDGES = {
        "0x3ee18B2214CAffA074b92A38e496A38d46CC5e9": "Wormhole",
        "0x32400084c286cf3e17e7b677ea9583e60a000324": "Ronin Bridge",
        "0x8898b472c54c31894e3b9bb83cea802a0b097e": "Multichain",
        "0x88A69C43Af0bf26Ed6F7245DBE7C1E0C1E4E3A4b": "Nomad Bridge",
    }

    KNOWN_EXCHANGES = {
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
        "0x71660c4005ba85c37ccec55d0c4493e66fe775d": "Coinbase",
        "0x28c6c06298d514db089934071355e5743bf21d60": "Kraken",
        "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": "OKX",
        "0x5041ed759dd4afc3a72b8192c143f72f4724081a": "Huobi",
        "0x859a95b2b58fd8d9d07c62840b6469744c2d29": "KuCoin",
    }

    def __init__(self, chain: Chain = Chain.ETHEREUM):
        self.chain = chain
        self.investigation = Investigation(
            incident_name="",
            incident_type="",
            start_date="",
            chains=[chain],
        )

    def analyze_transaction(self, tx_hash: str) -> Transaction:
        """Analyze a single transaction."""
        # In production, this would query Etherscan/Blockscout API
        # For now, create a placeholder transaction
        tx = Transaction(
            hash=tx_hash,
            chain=self.chain,
            from_address="0x0000000000000000000000000000000000000000",
            to_address="0x0000000000000000000000000000000000000000",
            value=0.0,
            token="ETH",
            timestamp=datetime.now(timezone.utc).isoformat(),
            block_number=0,
        )
        self.investigation.transactions.append(tx)
        return tx

    def trace_funds(self, source_address: str, depth: int = 3) -> list[FundFlow]:
        """Trace fund flows from a source address."""
        flows = []
        visited = set()

        def _trace(address: str, current_depth: int):
            if current_depth > depth or address in visited:
                return
            visited.add(address)

            # In production, this would query token transfer events
            # For now, create placeholder flows
            flow = FundFlow(
                source=address,
                destination="0x0000000000000000000000000000000000000000",
                amount=0.0,
                token="ETH",
                tx_hash="0x0000000000000000000000000000000000000000000000000000000000000000",
                chain=self.chain,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            flows.append(flow)
            self.investigation.fund_flows.append(flow)

            # Recurse to next hop
            _trace(flow.destination, current_depth + 1)

        _trace(source_address, 0)
        return flows

    def identify_attacker(self, addresses: list[str]) -> AttackerProfile:
        """Identify and cluster attacker addresses."""
        profile = AttackerProfile(primary_address=addresses[0] if addresses else "")

        # Clustering heuristics
        for addr in addresses:
            if addr not in profile.clustered_addresses:
                profile.clustered_addresses.append(addr)

        # Check funding sources
        for addr in addresses:
            if addr in self.KNOWN_EXCHANGES:
                profile.funding_source = "CEX"
            elif addr in self.KNOWN_MIXERS:
                profile.funding_source = "Mixer"

        # Attribution confidence
        if len(profile.clustered_addresses) > 5:
            profile.attribution_confidence = "moderate"
        if profile.funding_source != "unknown":
            profile.attribution_confidence = "high"

        self.investigation.attacker = profile
        return profile

    def detect_mixer_usage(self, address: str) -> bool:
        """Detect if funds passed through a mixer."""
        return address.lower() in {k.lower() for k in self.KNOWN_MIXERS}

    def detect_bridge_usage(self, address: str) -> str | None:
        """Detect if funds passed through a bridge."""
        for bridge_addr, bridge_name in self.KNOWN_BRIDGES.items():
            if address.lower() == bridge_addr.lower():
                return bridge_name
        return None

    def detect_exchange_deposit(self, address: str) -> str | None:
        """Detect if funds were deposited to an exchange."""
        for exchange_addr, exchange_name in self.KNOWN_EXCHANGES.items():
            if address.lower() == exchange_addr.lower():
                return exchange_name
        return None

    def cross_chain_trace(self, tx_hash: str, source_chain: Chain, dest_chain: Chain) -> list[FundFlow]:
        """Trace funds across chains through bridges."""
        flows = []

        # Identify bridge contract
        bridge_name = None
        for addr, name in self.KNOWN_BRIDGES.items():
            bridge_name = name
            break

        if bridge_name:
            flow = FundFlow(
                source=tx_hash,
                destination=f"bridged_to_{dest_chain.value}",
                amount=0.0,
                token="ETH",
                tx_hash=tx_hash,
                chain=source_chain,
                timestamp=datetime.now(timezone.utc).isoformat(),
                via="bridge",
            )
            flows.append(flow)
            self.investigation.fund_flows.append(flow)

            # Add destination chain flow
            dest_flow = FundFlow(
                source=f"bridged_from_{source_chain.value}",
                destination="unknown",
                amount=0.0,
                token="ETH",
                tx_hash="0x0000000000000000000000000000000000000000000000000000000000000000",
                chain=dest_chain,
                timestamp=datetime.now(timezone.utc).isoformat(),
                via="bridge",
            )
            flows.append(dest_flow)
            self.investigation.fund_flows.append(dest_flow)

        return flows

    def collect_evidence(self, tx_hash: str) -> EvidenceItem:
        """Collect and hash evidence for a transaction."""
        tx = self.analyze_transaction(tx_hash)

        evidence = EvidenceItem(
            tx_hash=tx_hash,
            chain=self.chain,
            data_type="transaction",
            data={
                "hash": tx.hash,
                "from": tx.from_address,
                "to": tx.to_address,
                "value": tx.value,
                "token": tx.token,
                "timestamp": tx.timestamp,
                "block_number": tx.block_number,
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.investigation.evidence.append(evidence)
        return evidence

    def calculate_loss(self) -> dict[str, float]:
        """Calculate total loss and recovery."""
        total = 0.0
        recovered = 0.0

        for flow in self.investigation.fund_flows:
            total += flow.amount
            if flow.status == FundStatus.RECOVERED:
                recovered += flow.amount

        self.investigation.total_loss = total
        self.investigation.funds_recovered = recovered

        return {
            "total_loss": total,
            "funds_recovered": recovered,
            "net_loss": total - recovered,
            "recovery_rate": (recovered / total * 100) if total > 0 else 0,
        }

    def generate_report(self) -> str:
        """Generate investigation report."""
        report = []
        report.append(f"# Investigation Report: {self.investigation.incident_name}")
        report.append("")
        report.append("## Executive Summary")
        report.append(f"- **Incident Type:** {self.investigation.incident_type}")
        report.append(f"- **Start Date:** {self.investigation.start_date}")
        report.append(f"- **Chains Affected:** {', '.join(c.value for c in self.investigation.chains)}")
        report.append(f"- **Status:** {self.investigation.status}")
        report.append("")

        loss_info = self.calculate_loss()
        report.append("## Loss Summary")
        report.append(f"- **Total Loss:** ${loss_info['total_loss']:,.2f}")
        report.append(f"- **Funds Recovered:** ${loss_info['funds_recovered']:,.2f}")
        report.append(f"- **Net Loss:** ${loss_info['net_loss']:,.2f}")
        report.append(f"- **Recovery Rate:** {loss_info['recovery_rate']:.1f}%")
        report.append("")

        if self.investigation.attacker:
            attacker = self.investigation.attacker
            report.append("## Attacker Analysis")
            report.append(f"- **Primary Address:** `{attacker.primary_address}`")
            report.append(f"- **Clustered Addresses:** {len(attacker.clustered_addresses)}")
            report.append(f"- **Funding Source:** {attacker.funding_source}")
            report.append(f"- **Attribution Confidence:** {attacker.attribution_confidence}")
            report.append(f"- **Known Affiliation:** {attacker.known_affiliation}")
            report.append("")

        if self.investigation.fund_flows:
            report.append("## Fund Flow Analysis")
            report.append("")
            report.append("| Source | Destination | Amount | Token | Via | Status |")
            report.append("|--------|-------------|--------|-------|-----|--------|")
            for flow in self.investigation.fund_flows:
                report.append(
                    f"| `{flow.source[:20]}...` | `{flow.destination[:20]}...` | "
                    f"{flow.amount:,.2f} | {flow.token} | {flow.via} | {flow.status.value} |"
                )
            report.append("")

        if self.investigation.evidence:
            report.append("## Evidence Package")
            report.append("")
            for ev in self.investigation.evidence:
                report.append(f"- **Tx:** `{ev.tx_hash}`")
                report.append(f"  - Type: {ev.data_type}")
                report.append(f"  - Chain: {ev.chain.value}")
                report.append(f"  - SHA-256: `{ev.sha256_hash}`")
                report.append("")

        report.append("## Recommendations")
        report.append("1. Continue real-time fund tracing while funds are moving.")
        report.append("2. Contact exchanges where funds have been deposited.")
        report.append("3. Engage law enforcement for legal action.")
        report.append("4. Monitor mixer usage and cross-chain bridges.")
        report.append("5. Document all findings for legal proceedings.")

        return "\n".join(report)


def interactive_mode():
    """Run tracer in interactive mode."""
    print("=" * 60)
    print("On-Chain Transaction Tracer - Interactive Mode")
    print("=" * 60)
    print()

    incident_name = input("Incident name: ").strip()
    incident_type = input("Incident type (exploit/hack/bridge/oracle): ").strip()

    print("\nAvailable chains:")
    for i, chain in enumerate(Chain, 1):
        print(f"  {i}. {chain.value}")
    chain_idx = int(input("Select chain (number): ").strip()) - 1
    chain = list(Chain)[chain_idx]

    tracer = TransactionTracer(chain)
    tracer.investigation.incident_name = incident_name
    tracer.investigation.incident_type = incident_type
    tracer.investigation.start_date = datetime.now(timezone.utc).isoformat()

    while True:
        print("\n--- Actions ---")
        print("1. Analyze transaction")
        print("2. Trace funds from address")
        print("3. Identify attacker")
        print("4. Cross-chain trace")
        print("5. Collect evidence")
        print("6. Generate report")
        print("7. Exit")

        choice = input("\nSelect action: ").strip()

        if choice == "1":
            tx_hash = input("Transaction hash: ").strip()
            tx = tracer.analyze_transaction(tx_hash)
            print(f"Analyzed transaction: {tx.hash}")

        elif choice == "2":
            address = input("Source address: ").strip()
            depth = int(input("Trace depth (default 3): ").strip() or "3")
            flows = tracer.trace_funds(address, depth)
            print(f"Found {len(flows)} fund flows")

        elif choice == "3":
            addresses = input("Attacker addresses (comma-separated): ").strip()
            addr_list = [a.strip() for a in addresses.split(",") if a.strip()]
            profile = tracer.identify_attacker(addr_list)
            print(f"Identified attacker: {profile.primary_address}")
            print(f"Clustered addresses: {len(profile.clustered_addresses)}")
            print(f"Attribution confidence: {profile.attribution_confidence}")

        elif choice == "4":
            tx_hash = input("Source transaction hash: ").strip()
            print("Available destination chains:")
            for i, c in enumerate(Chain, 1):
                if c != chain:
                    print(f"  {i}. {c.value}")
            dest_idx = int(input("Select destination chain: ").strip()) - 1
            dest_chain = [c for c in Chain if c != chain][dest_idx]
            flows = tracer.cross_chain_trace(tx_hash, chain, dest_chain)
            print(f"Cross-chain trace: {len(flows)} flows")

        elif choice == "5":
            tx_hash = input("Transaction hash: ").strip()
            evidence = tracer.collect_evidence(tx_hash)
            print(f"Evidence collected: {evidence.sha256_hash}")

        elif choice == "6":
            report = tracer.generate_report()
            print("\n" + "=" * 60)
            print(report)

        elif choice == "7":
            break


def main():
    parser = argparse.ArgumentParser(
        description="On-Chain Transaction Tracer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tx-tracer.py --tx 0xabc123... --chain ethereum
  python tx-tracer.py --address 0xattacker... --chain ethereum
  python tx-tracer.py --tx 0xabc123... --cross-chain --dest-chain polygon
  python tx-tracer.py --interactive
        """,
    )
    parser.add_argument("--tx", "-t", help="Transaction hash to analyze")
    parser.add_argument("--address", "-a", help="Address to trace funds from")
    parser.add_argument("--chain", "-c", default="ethereum", help="Blockchain (default: ethereum)")
    parser.add_argument("--cross-chain", action="store_true", help="Enable cross-chain tracing")
    parser.add_argument("--dest-chain", help="Destination chain for cross-chain tracing")
    parser.add_argument("--depth", "-d", type=int, default=3, help="Fund tracing depth (default: 3)")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--incident-name", help="Incident name for report")
    parser.add_argument("--incident-type", help="Incident type (exploit/hack/bridge/oracle)")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    try:
        chain = Chain(args.chain)
    except ValueError:
        print(f"Invalid chain: {args.chain}", file=sys.stderr)
        sys.exit(1)

    tracer = TransactionTracer(chain)

    if args.incident_name:
        tracer.investigation.incident_name = args.incident_name
    if args.incident_type:
        tracer.investigation.incident_type = args.incident_type

    if args.tx:
        tracer.analyze_transaction(args.tx)
        tracer.collect_evidence(args.tx)

    if args.address:
        tracer.trace_funds(args.address, args.depth)
        tracer.identify_attacker([args.address])

    if args.cross_chain and args.tx and args.dest_chain:
        try:
            dest_chain = Chain(args.dest_chain)
            tracer.cross_chain_trace(args.tx, chain, dest_chain)
        except ValueError:
            print(f"Invalid destination chain: {args.dest_chain}", file=sys.stderr)
            sys.exit(1)

    report = tracer.generate_report()

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
