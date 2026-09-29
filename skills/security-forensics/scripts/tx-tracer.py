#!/usr/bin/env python3
"""
Transaction Tracer for Web3 Forensics
=====================================

Traces fund movement through multiple hops on EVM-compatible chains.
Identifies source and sink addresses, generates fund flow graph,
and outputs structured JSON with evidence.

Usage:
    python tx-tracer.py --tx-hash <hash> --rpc-url <url> [--max-hops 10] [--output <file>]

Requirements:
    - Python 3.8+
    - web3.py
    - requests

Author: Security Forensics Team
License: MIT
"""

import argparse
import json
import hashlib
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Constants
# ============================================================================

ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ERC20_APPROVAL_TOPIC = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"

KNOWN_EXCHANGES = {
    "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
    "0x21a31ee1afc51d94c2efccaa2a02320a174f2b34": "Binance",
    "0x71660c4005ba85c37ccec55d0c4493e66677f2d5": "Coinbase",
    "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase",
    "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken",
    "0x0a869d79a7052c7f1b55eb89ae7e106b229e31c5": "Kraken",
}

KNOWN_MIXERS = {
    "0x910cbd523d972eb0a6f4ca48623c0b6617fe36e5": "Tornado Cash (ETH)",
    "0xd2135cfb216b74109775236e36d4b433f12d0964": "Tornado Cash (DAI)",
    "0x4736dcf1b7a3d580672cce6e6c65045c148a6967": "Tornado Cash (USDC)",
    "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash (USDT)",
}

KNOWN_BRIDGES = {
    "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Multichain (Anyswap)",
    "0x3ee18b22143aff074b92a38e490238d3608961f4": "Wormhole",
    "0x150f94b44927f0787375629fc68c4c56517e935e": "Stargate",
    "0x8898b472c54c31894e3b9bb83f8a8676d087894f": "Hop Protocol",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TransferEvent:
    """Represents a token transfer event."""
    tx_hash: str
    block_number: int
    timestamp: int
    from_address: str
    to_address: str
    value: int
    token_address: str
    token_symbol: str = "UNKNOWN"
    token_decimals: int = 18
    log_index: int = 0

    @property
    def value_human(self) -> float:
        """Return human-readable token value."""
        return self.value / (10 ** self.token_decimals)


@dataclass
class TransactionData:
    """Represents a blockchain transaction."""
    tx_hash: str
    block_number: int
    timestamp: int
    from_address: str
    to_address: str
    value: int
    gas_price: int
    gas_used: int
    input_data: str
    status: int
    transfers: List[TransferEvent] = field(default_factory=list)
    internal_calls: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FundFlowNode:
    """Represents a node in the fund flow graph."""
    address: str
    label: str
    node_type: str  # "source", "intermediate", "sink", "exchange", "mixer", "bridge"
    first_seen: int
    last_seen: int
    total_in: int = 0
    total_out: int = 0
    transactions: List[str] = field(default_factory=list)


@dataclass
class FundFlowEdge:
    """Represents an edge in the fund flow graph."""
    from_address: str
    to_address: str
    value: int
    token_address: str
    token_symbol: str
    tx_hash: str
    block_number: int
    timestamp: int
    hop_number: int


@dataclass
class TraceResult:
    """Represents the complete trace result."""
    start_tx_hash: str
    start_block: int
    start_timestamp: int
    attacker_address: str
    max_hops: int
    nodes: List[FundFlowNode]
    edges: List[FundFlowEdge]
    sinks: List[FundFlowNode]
    total_value_traced: int
    evidence_hashes: Dict[str, str]
    metadata: Dict[str, Any]


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

    def is_contract(self, address: str) -> bool:
        """Check if address is a contract."""
        code = self.get_code(address)
        return code != "0x" and len(code) > 2

    def get_token_info(self, token_address: str) -> Tuple[str, int]:
        """Get token symbol and decimals."""
        # Try symbol()
        try:
            result = self.call("eth_call", [{
                "to": token_address,
                "data": "0x95d89b41"  # symbol()
            }, "latest"])
            if result and result != "0x":
                symbol = self._decode_string(result)
            else:
                symbol = "UNKNOWN"
        except RPCError:
            symbol = "UNKNOWN"

        # Try decimals()
        try:
            result = self.call("eth_call", [{
                "to": token_address,
                "data": "0x313ce567"  # decimals()
            }, "latest"])
            if result and result != "0x":
                decimals = int(result, 16)
            else:
                decimals = 18
        except RPCError:
            decimals = 18

        return symbol, decimals

    def _decode_string(self, hex_data: str) -> str:
        """Decode ABI-encoded string."""
        if hex_data == "0x" or len(hex_data) < 66:
            return "UNKNOWN"
        try:
            # Remove 0x prefix
            data = hex_data[2:]
            # First 32 bytes = offset, next 32 bytes = length, then data
            offset = int(data[:64], 16) * 2
            length = int(data[offset:offset + 64], 16) * 2
            string_data = data[offset + 64:offset + 64 + length]
            return bytes.fromhex(string_data).decode("utf-8", errors="replace")
        except (ValueError, IndexError):
            return "UNKNOWN"


class RPCError(Exception):
    """RPC error exception."""
    pass


# ============================================================================
# Transaction Tracer
# ============================================================================

class TransactionTracer:
    """Traces fund movement through multiple hops."""

    def __init__(self, rpc_url: str, max_hops: int = 10, rate_limit_delay: float = 0.1):
        self.rpc = RPCClient(rpc_url)
        self.max_hops = max_hops
        self.rate_limit_delay = rate_limit_delay
        self.visited_txs: Set[str] = set()
        self.visited_addresses: Set[str] = set()
        self.nodes: Dict[str, FundFlowNode] = {}
        self.edges: List[FundFlowEdge] = []
        self.sinks: List[FundFlowNode] = []
        self.evidence: Dict[str, str] = {}

    def trace(self, start_tx_hash: str) -> TraceResult:
        """Trace funds starting from a transaction."""
        # Get the starting transaction
        tx = self.rpc.get_transaction(start_tx_hash)
        if not tx:
            raise ValueError(f"Transaction not found: {start_tx_hash}")

        receipt = self.rpc.get_transaction_receipt(start_tx_hash)
        block = self.rpc.get_block(int(tx["blockNumber"], 16))

        start_block = int(tx["blockNumber"], 16)
        start_timestamp = int(block["timestamp"], 16) if block else 0
        attacker_address = tx["from"].lower()

        # Store evidence
        self.evidence[f"tx_{start_tx_hash}"] = self._hash_json({
            "tx": tx,
            "receipt": receipt,
            "block": block
        })

        # Create initial node
        self._get_or_create_node(attacker_address, start_timestamp)

        # Trace transfers from this transaction
        transfers = self._extract_transfers(receipt, start_block, start_timestamp, start_tx_hash)
        for transfer in transfers:
            self._trace_transfer(transfer, hop=1)

        # Build result
        return TraceResult(
            start_tx_hash=start_tx_hash,
            start_block=start_block,
            start_timestamp=start_timestamp,
            attacker_address=attacker_address,
            max_hops=self.max_hops,
            nodes=list(self.nodes.values()),
            edges=self.edges,
            sinks=self.sinks,
            total_value_traced=sum(e.value for e in self.edges),
            evidence_hashes=self.evidence,
            metadata={
                "trace_timestamp": datetime.now(timezone.utc).isoformat(),
                "rpc_url": self.rpc.rpc_url,
                "total_hops": max((e.hop_number for e in self.edges), default=0),
                "total_transfers": len(self.edges),
                "unique_addresses": len(self.nodes),
            }
        )

    def _trace_transfer(self, transfer: TransferEvent, hop: int) -> None:
        """Trace a single transfer and follow the funds."""
        if hop > self.max_hops:
            return

        # Add edge
        self.edges.append(FundFlowEdge(
            from_address=transfer.from_address,
            to_address=transfer.to_address,
            value=transfer.value,
            token_address=transfer.token_address,
            token_symbol=transfer.token_symbol,
            tx_hash=transfer.tx_hash,
            block_number=transfer.block_number,
            timestamp=transfer.timestamp,
            hop_number=hop
        ))

        # Update nodes
        from_node = self._get_or_create_node(transfer.from_address, transfer.timestamp)
        from_node.total_out += transfer.value
        from_node.last_seen = max(from_node.last_seen, transfer.timestamp)
        if transfer.tx_hash not in from_node.transactions:
            from_node.transactions.append(transfer.tx_hash)

        to_node = self._get_or_create_node(transfer.to_address, transfer.timestamp)
        to_node.total_in += transfer.value
        to_node.last_seen = max(to_node.last_seen, transfer.timestamp)
        if transfer.tx_hash not in to_node.transactions:
            to_node.transactions.append(transfer.tx_hash)

        # Classify destination
        self._classify_node(transfer.to_address, to_node)

        # If destination is a contract, follow the funds
        if self.rpc.is_contract(transfer.to_address):
            time.sleep(self.rate_limit_delay)
            next_txs = self._find_next_transactions(transfer.to_address, transfer.block_number)
            for next_tx in next_txs:
                if next_tx["hash"] not in self.visited_txs:
                    self.visited_txs.add(next_tx["hash"])
                    next_receipt = self.rpc.get_transaction_receipt(next_tx["hash"])
                    if next_receipt:
                        next_transfers = self._extract_transfers(
                            next_receipt,
                            int(next_tx["blockNumber"], 16),
                            transfer.timestamp,
                            next_tx["hash"]
                        )
                        for next_transfer in next_transfers:
                            if next_transfer.from_address.lower() == transfer.to_address.lower():
                                self._trace_transfer(next_transfer, hop + 1)
        else:
            # Destination is an EOA - potential sink
            if to_node not in self.sinks:
                self.sinks.append(to_node)

    def _extract_transfers(self, receipt: Dict[str, Any], block_number: int,
                          timestamp: int, tx_hash: str) -> List[TransferEvent]:
        """Extract ERC-20 transfer events from transaction receipt."""
        transfers = []

        for log in receipt.get("logs", []):
            topics = log.get("topics", [])
            if not topics or topics[0] != ERC20_TRANSFER_TOPIC:
                continue

            # Decode transfer event
            # Transfer(address indexed from, address indexed to, uint256 value)
            from_address = "0x" + topics[1][-40:] if len(topics) > 1 else "0x0"
            to_address = "0x" + topics[2][-40:] if len(topics) > 2 else "0x0"
            value = int(log["data"], 16) if log["data"] != "0x" else 0
            token_address = log["address"].lower()

            # Get token info
            symbol, decimals = self.rpc.get_token_info(token_address)

            transfers.append(TransferEvent(
                tx_hash=tx_hash,
                block_number=block_number,
                timestamp=timestamp,
                from_address=from_address.lower(),
                to_address=to_address.lower(),
                value=value,
                token_address=token_address,
                token_symbol=symbol,
                token_decimals=decimals,
                log_index=int(log.get("logIndex", "0x0"), 16)
            ))

        return transfers

    def _find_next_transactions(self, address: str, after_block: int) -> List[Dict[str, Any]]:
        """Find transactions from an address after a given block."""
        # Get logs for token transfers from this address
        logs = self.rpc.get_logs(
            from_block=after_block + 1,
            to_block=after_block + 100,  # Look ahead 100 blocks
            topics=[ERC20_TRANSFER_TOPIC, "0x" + "0" * 24 + address[2:].lower()]
        )

        # Extract unique transaction hashes
        tx_hashes = list(set(log["transactionHash"] for log in logs))

        # Get transaction data
        transactions = []
        for tx_hash in tx_hashes[:10]:  # Limit to 10 transactions
            tx = self.rpc.get_transaction(tx_hash)
            if tx:
                transactions.append(tx)
            time.sleep(self.rate_limit_delay)

        return transactions

    def _get_or_create_node(self, address: str, timestamp: int) -> FundFlowNode:
        """Get existing node or create new one."""
        address = address.lower()
        if address not in self.nodes:
            self.nodes[address] = FundFlowNode(
                address=address,
                label=self._get_label(address),
                node_type=self._get_node_type(address),
                first_seen=timestamp,
                last_seen=timestamp
            )
        return self.nodes[address]

    def _classify_node(self, address: str, node: FundFlowNode) -> None:
        """Classify a node based on known addresses."""
        address_lower = address.lower()
        if address_lower in KNOWN_EXCHANGES:
            node.node_type = "exchange"
            node.label = KNOWN_EXCHANGES[address_lower]
        elif address_lower in KNOWN_MIXERS:
            node.node_type = "mixer"
            node.label = KNOWN_MIXERS[address_lower]
        elif address_lower in KNOWN_BRIDGES:
            node.node_type = "bridge"
            node.label = KNOWN_BRIDGES[address_lower]

    def _get_label(self, address: str) -> str:
        """Get a label for an address."""
        address_lower = address.lower()
        if address_lower in KNOWN_EXCHANGES:
            return KNOWN_EXCHANGES[address_lower]
        elif address_lower in KNOWN_MIXERS:
            return KNOWN_MIXERS[address_lower]
        elif address_lower in KNOWN_BRIDGES:
            return KNOWN_BRIDGES[address_lower]
        return f"{address[:6]}...{address[-4:]}"

    def _get_node_type(self, address: str) -> str:
        """Get the type of a node."""
        address_lower = address.lower()
        if address_lower in KNOWN_EXCHANGES:
            return "exchange"
        elif address_lower in KNOWN_MIXERS:
            return "mixer"
        elif address_lower in KNOWN_BRIDGES:
            return "bridge"
        return "unknown"

    def _hash_json(self, data: Any) -> str:
        """Generate SHA-256 hash of JSON data."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


# ============================================================================
# Output Formatters
# ============================================================================

def format_trace_result(result: TraceResult) -> Dict[str, Any]:
    """Format trace result as structured JSON."""
    return {
        "trace_info": {
            "start_transaction": result.start_tx_hash,
            "start_block": result.start_block,
            "start_timestamp": result.start_timestamp,
            "start_timestamp_utc": datetime.fromtimestamp(
                result.start_timestamp, tz=timezone.utc
            ).isoformat() if result.start_timestamp else None,
            "attacker_address": result.attacker_address,
            "max_hops": result.max_hops,
            "trace_timestamp": result.metadata.get("trace_timestamp"),
        },
        "summary": {
            "total_hops": result.metadata.get("total_hops", 0),
            "total_transfers": result.metadata.get("total_transfers", 0),
            "unique_addresses": result.metadata.get("unique_addresses", 0),
            "total_value_traced": result.total_value_traced,
            "sink_count": len(result.sinks),
        },
        "nodes": [asdict(node) for node in result.nodes],
        "edges": [asdict(edge) for edge in result.edges],
        "sinks": [asdict(sink) for sink in result.sinks],
        "evidence_hashes": result.evidence_hashes,
        "metadata": result.metadata,
    }


def generate_fund_flow_graph(result: TraceResult) -> str:
    """Generate a Mermaid graph of the fund flow."""
    lines = ["```mermaid", "graph LR"]

    # Add nodes
    for node in result.nodes:
        node_id = node.address[:10]
        label = node.label
        if node.node_type == "exchange":
            lines.append(f'    {node_id}["{label}"]:::exchange')
        elif node.node_type == "mixer":
            lines.append(f'    {node_id}["{label}"]:::mixer')
        elif node.node_type == "bridge":
            lines.append(f'    {node_id}["{label}"]:::bridge')
        else:
            lines.append(f'    {node_id}["{label}"]')

    # Add edges
    for edge in result.edges:
        from_id = edge.from_address[:10]
        to_id = edge.to_address[:10]
        value = edge.value / (10 ** 18)  # Simplified
        lines.append(f'    {from_id} -->|"{edge.token_symbol}: {value:.2f}"| {to_id}')

    # Add class definitions
    lines.append("    classDef exchange fill:#f96,stroke:#333,stroke-width:2px")
    lines.append("    classDef mixer fill:#f9f,stroke:#333,stroke-width:2px")
    lines.append("    classDef bridge fill:#99f,stroke:#333,stroke-width:2px")
    lines.append("```")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Trace fund movement through multiple hops on EVM chains",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tx-tracer.py --tx-hash 0xabc123... --rpc-url https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
  python tx-tracer.py --tx-hash 0xabc123... --rpc-url https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY --max-hops 5 --output trace.json
        """
    )
    parser.add_argument("--tx-hash", required=True, help="Transaction hash to trace")
    parser.add_argument("--rpc-url", required=True, help="RPC endpoint URL")
    parser.add_argument("--max-hops", type=int, default=10, help="Maximum hops to trace (default: 10)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["json", "graph", "both"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--rate-limit", type=float, default=0.1,
                       help="Delay between RPC calls in seconds (default: 0.1)")

    args = parser.parse_args()

    # Validate inputs
    if not args.tx_hash.startswith("0x") or len(args.tx_hash) != 66:
        print("Error: Invalid transaction hash format", file=sys.stderr)
        sys.exit(1)

    # Create tracer
    tracer = TransactionTracer(
        rpc_url=args.rpc_url,
        max_hops=args.max_hops,
        rate_limit_delay=args.rate_limit
    )

    # Run trace
    print(f"Tracing transaction: {args.tx_hash}", file=sys.stderr)
    print(f"RPC URL: {args.rpc_url}", file=sys.stderr)
    print(f"Max hops: {args.max_hops}", file=sys.stderr)
    print("", file=sys.stderr)

    try:
        result = tracer.trace(args.tx_hash)
    except (RPCError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.format in ("json", "both"):
        json_output = json.dumps(format_trace_result(result), indent=2, default=str)
        if args.output:
            Path(args.output).write_text(json_output)
            print(f"JSON output written to: {args.output}", file=sys.stderr)
        else:
            print(json_output)

    if args.format in ("graph", "both"):
        graph_output = generate_fund_flow_graph(result)
        if args.format == "both":
            print("\n" + graph_output)
        else:
            print(graph_output)

    # Print summary
    print("", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("TRACE SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total transfers found: {len(result.edges)}", file=sys.stderr)
    print(f"Unique addresses: {len(result.nodes)}", file=sys.stderr)
    print(f"Sink addresses: {len(result.sinks)}", file=sys.stderr)
    print(f"Max hops: {max((e.hop_number for e in result.edges), default=0)}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Sink addresses:", file=sys.stderr)
    for sink in result.sinks:
        print(f"  - {sink.address} ({sink.label})", file=sys.stderr)


if __name__ == "__main__":
    main()
