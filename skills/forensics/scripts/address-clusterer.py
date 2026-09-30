#!/usr/bin/env python3
"""
Address Clusterer for Web3 Forensics
=====================================

Takes a list of addresses as input, clusters them by common funding
sources, timing, and behavior, and outputs cluster analysis with
confidence scores.

Usage:
    python address-clusterer.py --addresses <addresses_file> [--rpc-url <url>] [--output <file>]

Requirements:
    - Python 3.8+
    - requests

Author: Security Forensics Team
License: MIT
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AddressProfile:
    """Represents a blockchain address profile."""
    address: str
    first_seen: Optional[int] = None
    last_seen: Optional[int] = None
    transaction_count: int = 0
    unique_counterparties: Set[str] = field(default_factory=set)
    contract_interactions: Set[str] = field(default_factory=set)
    token_transfers: List[Dict[str, Any]] = field(default_factory=list)
    funding_sources: Set[str] = field(default_factory=set)
    gas_prices: List[int] = field(default_factory=list)
    total_value_in: int = 0
    total_value_out: int = 0
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AddressCluster:
    """Represents a cluster of related addresses."""
    cluster_id: str
    addresses: List[str]
    common_funding_sources: Set[str] = field(default_factory=set)
    timing_overlap: bool = False
    behavioral_similarity: float = 0.0
    confidence_score: float = 0.0
    confidence_level: str = "speculative"
    cluster_type: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusterAnalysisResult:
    """Represents the complete cluster analysis result."""
    input_addresses: List[str]
    clusters: List[AddressCluster]
    unclustered: List[str]
    analysis_timestamp: str
    total_addresses: int
    total_clusters: int
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# RPC Client
# ============================================================================

class RPCClient:
    """Simple JSON-RPC client for EVM chains."""

    def __init__(self, rpc_url: str, timeout: int = 30):
        self.rpc_url = rpc_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._request_id = 0

    def call(self, method: str, params: Optional[List[Any]] = None) -> Any:
        """Make a JSON-RPC call."""
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or []
        }

        try:
            response = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise RPCError(f"RPC error: {result['error']}")

            return result.get("result")
        except requests.exceptions.RequestException as e:
            raise RPCError(f"RPC request failed: {e}")

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash."""
        return self.call("eth_getTransactionByHash", [tx_hash])

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction receipt."""
        return self.call("eth_getTransactionReceipt", [tx_hash])

    def get_block(self, block_number: int) -> Optional[Dict[str, Any]]:
        """Get block by number."""
        return self.call("eth_getBlockByNumber", [hex(block_number), False])

    def get_code(self, address: str) -> str:
        """Get contract code at address."""
        return self.call("eth_getCode", [address, "latest"]) or "0x"

    def is_contract(self, address: str) -> bool:
        """Check if address is a contract."""
        code = self.get_code(address)
        return code != "0x" and len(code) > 2

    def get_logs(self, from_block: int, to_block: int, address: Optional[str] = None,
                 topics: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get logs matching filter."""
        filter_params: Dict[str, Any] = {
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
        }
        if address:
            filter_params["address"] = address
        if topics:
            filter_params["topics"] = topics

        return self.call("eth_getLogs", [filter_params]) or []


class RPCError(Exception):
    """RPC error exception."""
    pass


# ============================================================================
# Address Profiler
# ============================================================================

class AddressProfiler:
    """Profiles blockchain addresses."""

    def __init__(self, rpc_url: str, rate_limit_delay: float = 0.1):
        self.rpc = RPCClient(rpc_url)
        self.rate_limit_delay = rate_limit_delay

    def profile_address(self, address: str) -> AddressProfile:
        """Profile a single address."""
        profile = AddressProfile(address=address.lower())

        # Get all transactions involving this address
        # Note: This is a simplified approach. In production, use an indexer
        # or archive node with full transaction history.

        # Get recent transactions (last 1000 blocks)
        latest_block = int(self.rpc.call("eth_blockNumber", []), 16)
        from_block = max(0, latest_block - 1000)

        # Get transactions where address is sender
        # This requires an indexer or archive node
        # For now, we'll use a simplified approach

        # Get token transfers involving this address
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

        # Transfers from this address
        logs_from = self.rpc.get_logs(
            from_block=from_block,
            to_block=latest_block,
            topics=[transfer_topic, "0x" + "0" * 24 + address[2:].lower()]
        )

        # Transfers to this address
        logs_to = self.rpc.get_logs(
            from_block=from_block,
            to_block=latest_block,
            topics=[transfer_topic, None, "0x" + "0" * 24 + address[2:].lower()]
        )

        # Process transfers
        all_logs = logs_from + logs_to
        for log in all_logs:
            tx_hash = log["transactionHash"]
            tx = self.rpc.get_transaction(tx_hash)
            if not tx:
                continue

            block = self.rpc.get_block(int(tx["blockNumber"], 16))
            timestamp = int(block["timestamp"], 16) if block else 0

            # Update profile
            profile.transaction_count += 1
            profile.unique_counterparties.add(tx["from"].lower())
            profile.unique_counterparties.add(tx["to"].lower() if tx["to"] else "0x0")

            if profile.first_seen is None or timestamp < profile.first_seen:
                profile.first_seen = timestamp
            if profile.last_seen is None or timestamp > profile.last_seen:
                profile.last_seen = timestamp

            # Track gas prices
            profile.gas_prices.append(int(tx.get("gasPrice", "0x0"), 16))

            # Track contract interactions
            if tx["to"] and self.rpc.is_contract(tx["to"]):
                profile.contract_interactions.add(tx["to"].lower())

            # Track funding sources
            if tx["from"].lower() != address:
                profile.funding_sources.add(tx["from"].lower())

            # Track value
            value = int(tx.get("value", "0x0"), 16)
            if tx["from"].lower() == address:
                profile.total_value_out += value
            else:
                profile.total_value_in += value

            time.sleep(self.rate_limit_delay)

        # Remove self from counterparties
        profile.unique_counterparties.discard(address.lower())

        return profile


# ============================================================================
# Address Clusterer
# ============================================================================

class AddressClusterer:
    """Clusters addresses by common characteristics."""

    def __init__(self, rpc_url: str, rate_limit_delay: float = 0.1):
        self.profiler = AddressProfiler(rpc_url, rate_limit_delay)
        self.profiles: Dict[str, AddressProfile] = {}

    def cluster_addresses(self, addresses: List[str]) -> ClusterAnalysisResult:
        """Cluster a list of addresses."""
        # Profile all addresses
        print(f"Profiling {len(addresses)} addresses...", file=sys.stderr)
        for i, address in enumerate(addresses):
            print(f"  [{i + 1}/{len(addresses)}] Profiling {address}", file=sys.stderr)
            try:
                profile = self.profiler.profile_address(address)
                self.profiles[address.lower()] = profile
            except Exception as e:
                print(f"    Error: {e}", file=sys.stderr)

        # Cluster by common funding source
        print("Clustering by funding source...", file=sys.stderr)
        funding_clusters = self._cluster_by_funding_source()

        # Cluster by timing
        print("Clustering by timing...", file=sys.stderr)
        timing_clusters = self._cluster_by_timing()

        # Cluster by behavior
        print("Clustering by behavior...", file=sys.stderr)
        behavioral_clusters = self._cluster_by_behavior()

        # Merge clusters
        print("Merging clusters...", file=sys.stderr)
        merged_clusters = self._merge_clusters(funding_clusters, timing_clusters, behavioral_clusters)

        # Calculate confidence scores
        print("Calculating confidence scores...", file=sys.stderr)
        for cluster in merged_clusters:
            self._calculate_confidence(cluster)

        # Identify unclustered addresses
        clustered_addresses = set()
        for cluster in merged_clusters:
            clustered_addresses.update(cluster.addresses)
        unclustered = [addr for addr in addresses if addr.lower() not in clustered_addresses]

        return ClusterAnalysisResult(
            input_addresses=addresses,
            clusters=merged_clusters,
            unclustered=unclustered,
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            total_addresses=len(addresses),
            total_clusters=len(merged_clusters),
            metadata={
                "rpc_url": self.profiler.rpc.rpc_url,
                "profiles_generated": len(self.profiles),
            }
        )

    def _cluster_by_funding_source(self) -> List[AddressCluster]:
        """Cluster addresses by common funding source."""
        # Group addresses by funding source
        funding_groups: Dict[str, Set[str]] = defaultdict(set)

        for address, profile in self.profiles.items():
            for source in profile.funding_sources:
                funding_groups[source].add(address)

        clusters = []
        for source, addresses in funding_groups.items():
            if len(addresses) > 1:
                cluster = AddressCluster(
                    cluster_id=f"FUND-{source[:10]}",
                    addresses=list(addresses),
                    common_funding_sources={source},
                    cluster_type="common_funding"
                )
                clusters.append(cluster)

        return clusters

    def _cluster_by_timing(self) -> List[AddressCluster]:
        """Cluster addresses by timing overlap."""
        addresses = list(self.profiles.keys())
        clusters = []

        for i, addr1 in enumerate(addresses):
            profile1 = self.profiles[addr1]
            if profile1.first_seen is None:
                continue

            cluster_addresses = {addr1}

            for j, addr2 in enumerate(addresses):
                if i >= j:
                    continue

                profile2 = self.profiles[addr2]
                if profile2.first_seen is None:
                    continue

                # Check for timing overlap
                if self._timing_overlaps(profile1, profile2):
                    cluster_addresses.add(addr2)

            if len(cluster_addresses) > 1:
                cluster = AddressCluster(
                    cluster_id=f"TIME-{addr1[:10]}",
                    addresses=list(cluster_addresses),
                    timing_overlap=True,
                    cluster_type="timing_overlap"
                )
                clusters.append(cluster)

        return clusters

    def _cluster_by_behavior(self) -> List[AddressCluster]:
        """Cluster addresses by behavioral similarity."""
        addresses = list(self.profiles.keys())
        clusters = []

        for i, addr1 in enumerate(addresses):
            profile1 = self.profiles[addr1]
            cluster_addresses = {addr1}

            for j, addr2 in enumerate(addresses):
                if i >= j:
                    continue

                profile2 = self.profiles[addr2]
                similarity = self._behavioral_similarity(profile1, profile2)

                if similarity > 0.7:  # 70% similarity threshold
                    cluster_addresses.add(addr2)

            if len(cluster_addresses) > 1:
                cluster = AddressCluster(
                    cluster_id=f"BEHAVE-{addr1[:10]}",
                    addresses=list(cluster_addresses),
                    behavioral_similarity=0.7,
                    cluster_type="behavioral_similarity"
                )
                clusters.append(cluster)

        return clusters

    def _merge_clusters(self, *cluster_lists: List[AddressCluster]) -> List[AddressCluster]:
        """Merge overlapping clusters."""
        all_clusters = []
        for clusters in cluster_lists:
            all_clusters.extend(clusters)

        if not all_clusters:
            return []

        # Simple merge: combine clusters that share addresses
        merged = []
        used = set()

        for i, cluster1 in enumerate(all_clusters):
            if i in used:
                continue

            merged_addresses = set(cluster1.addresses)
            common_sources = set(cluster1.common_funding_sources)
            timing = cluster1.timing_overlap
            max_similarity = cluster1.behavioral_similarity

            for j, cluster2 in enumerate(all_clusters):
                if i >= j or j in used:
                    continue

                if merged_addresses & set(cluster2.addresses):
                    merged_addresses.update(cluster2.addresses)
                    common_sources.update(cluster2.common_funding_sources)
                    timing = timing or cluster2.timing_overlap
                    max_similarity = max(max_similarity, cluster2.behavioral_similarity)
                    used.add(j)

            merged.append(AddressCluster(
                cluster_id=f"CLUSTER-{len(merged) + 1:04d}",
                addresses=list(merged_addresses),
                common_funding_sources=common_sources,
                timing_overlap=timing,
                behavioral_similarity=max_similarity,
                cluster_type="merged"
            ))
            used.add(i)

        return merged

    def _timing_overlaps(self, profile1: AddressProfile, profile2: AddressProfile) -> bool:
        """Check if two profiles have overlapping timing."""
        if profile1.first_seen is None or profile2.first_seen is None:
            return False

        # Check if active periods overlap
        return not (
            profile1.last_seen < profile2.first_seen or
            profile2.last_seen < profile1.first_seen
        )

    def _behavioral_similarity(self, profile1: AddressProfile, profile2: AddressProfile) -> float:
        """Calculate behavioral similarity between two profiles."""
        scores = []

        # Contract interaction similarity
        if profile1.contract_interactions or profile2.contract_interactions:
            intersection = profile1.contract_interactions & profile2.contract_interactions
            union = profile1.contract_interactions | profile2.contract_interactions
            if union:
                scores.append(len(intersection) / len(union))

        # Counterparty similarity
        if profile1.unique_counterparties or profile2.unique_counterparties:
            intersection = profile1.unique_counterparties & profile2.unique_counterparties
            union = profile1.unique_counterparties | profile2.unique_counterparties
            if union:
                scores.append(len(intersection) / len(union))

        # Gas price similarity
        if profile1.gas_prices and profile2.gas_prices:
            avg1 = sum(profile1.gas_prices) / len(profile1.gas_prices)
            avg2 = sum(profile2.gas_prices) / len(profile2.gas_prices)
            if avg1 > 0 and avg2 > 0:
                ratio = min(avg1, avg2) / max(avg1, avg2)
                scores.append(ratio)

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_confidence(self, cluster: AddressCluster) -> None:
        """Calculate confidence score for a cluster."""
        score = 0.0

        # Funding source match (strong indicator)
        if cluster.common_funding_sources:
            score += 40.0

        # Timing overlap (moderate indicator)
        if cluster.timing_overlap:
            score += 20.0

        # Behavioral similarity (moderate indicator)
        score += cluster.behavioral_similarity * 30.0

        # Multiple addresses (weak indicator)
        if len(cluster.addresses) > 2:
            score += 10.0

        cluster.confidence_score = min(score, 100.0)

        # Determine confidence level
        if cluster.confidence_score >= 80:
            cluster.confidence_level = "confirmed"
        elif cluster.confidence_score >= 60:
            cluster.confidence_level = "high"
        elif cluster.confidence_score >= 40:
            cluster.confidence_level = "moderate"
        else:
            cluster.confidence_level = "speculative"


# ============================================================================
# Output Formatters
# ============================================================================

def format_cluster_json(result: ClusterAnalysisResult) -> str:
    """Format cluster analysis as JSON."""
    data = {
        "analysis_timestamp": result.analysis_timestamp,
        "summary": {
            "total_addresses": result.total_addresses,
            "total_clusters": result.total_clusters,
            "unclustered_addresses": len(result.unclustered),
        },
        "clusters": [
            {
                "cluster_id": cluster.cluster_id,
                "addresses": cluster.addresses,
                "address_count": len(cluster.addresses),
                "common_funding_sources": list(cluster.common_funding_sources),
                "timing_overlap": cluster.timing_overlap,
                "behavioral_similarity": cluster.behavioral_similarity,
                "confidence_score": cluster.confidence_score,
                "confidence_level": cluster.confidence_level,
                "cluster_type": cluster.cluster_type,
                "metadata": cluster.metadata,
            }
            for cluster in result.clusters
        ],
        "unclustered_addresses": result.unclustered,
        "metadata": result.metadata,
    }
    return json.dumps(data, indent=2, default=str)


def format_cluster_text(result: ClusterAnalysisResult) -> str:
    """Format cluster analysis as human-readable text."""
    lines = [
        "=" * 80,
        "ADDRESS CLUSTER ANALYSIS",
        "=" * 80,
        f"Analysis Time: {result.analysis_timestamp}",
        f"Total Addresses: {result.total_addresses}",
        f"Total Clusters: {result.total_clusters}",
        f"Unclustered: {len(result.unclustered)}",
        "=" * 80,
        "",
    ]

    for cluster in result.clusters:
        lines.extend([
            f"Cluster: {cluster.cluster_id}",
            "-" * 40,
            f"  Addresses: {len(cluster.addresses)}",
            f"  Confidence: {cluster.confidence_score:.1f}% ({cluster.confidence_level})",
            f"  Type: {cluster.cluster_type}",
            f"  Timing Overlap: {cluster.timing_overlap}",
            f"  Behavioral Similarity: {cluster.behavioral_similarity:.2f}",
        ])

        if cluster.common_funding_sources:
            lines.append(f"  Common Funding Sources:")
            for source in cluster.common_funding_sources:
                lines.append(f"    - {source}")

        lines.append(f"  Addresses:")
        for addr in cluster.addresses:
            lines.append(f"    - {addr}")

        lines.append("")

    if result.unclustered:
        lines.extend([
            "Unclustered Addresses:",
            "-" * 40,
        ])
        for addr in result.unclustered:
            lines.append(f"  - {addr}")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cluster related addresses by behavior",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Cluster addresses from file
  python address-clusterer.py --addresses addresses.txt --rpc-url https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

  # Cluster addresses from command line
  python address-clusterer.py --addresses 0xabc... 0xdef... --rpc-url https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

  # Output as text
  python address-clusterer.py --addresses addresses.txt --format text --output clusters.txt
        """
    )
    parser.add_argument("--addresses", nargs="+", help="Addresses to cluster (or file with one address per line)")
    parser.add_argument("--rpc-url", help="RPC endpoint URL")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--rate-limit", type=float, default=0.1,
                       help="Delay between RPC calls in seconds (default: 0.1)")

    args = parser.parse_args()

    # Parse addresses
    addresses = []
    if args.addresses:
        for addr in args.addresses:
            # Check if it's a file
            if Path(addr).exists():
                with open(addr) as f:
                    addresses.extend(line.strip() for line in f if line.strip())
            else:
                addresses.append(addr)

    if not addresses:
        print("Error: No addresses provided", file=sys.stderr)
        sys.exit(1)

    # Validate addresses
    valid_addresses = []
    for addr in addresses:
        if addr.startswith("0x") and len(addr) == 42:
            valid_addresses.append(addr)
        else:
            print(f"Warning: Invalid address format: {addr}", file=sys.stderr)

    if not valid_addresses:
        print("Error: No valid addresses", file=sys.stderr)
        sys.exit(1)

    # Create clusterer
    rpc_url = args.rpc_url or "https://eth-mainnet.g.alchemy.com/v2/demo"
    clusterer = AddressClusterer(rpc_url, rate_limit_delay=args.rate_limit)

    # Run clustering
    print(f"Clustering {len(valid_addresses)} addresses...", file=sys.stderr)
    result = clusterer.cluster_addresses(valid_addresses)

    # Format output
    if args.format == "json":
        output = format_cluster_json(result)
    else:
        output = format_cluster_text(result)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Cluster analysis written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    # Print summary
    print("", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("CLUSTER ANALYSIS SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total addresses: {result.total_addresses}", file=sys.stderr)
    print(f"Total clusters: {result.total_clusters}", file=sys.stderr)
    print(f"Unclustered: {len(result.unclustered)}", file=sys.stderr)
    print("", file=sys.stderr)
    for cluster in result.clusters:
        print(f"  {cluster.cluster_id}: {len(cluster.addresses)} addresses "
              f"({cluster.confidence_level}, {cluster.confidence_score:.1f}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
