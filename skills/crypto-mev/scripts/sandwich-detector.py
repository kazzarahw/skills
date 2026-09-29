#!/usr/bin/env python3
"""
Sandwich Attack Detector

Detects sandwich attacks by analyzing mempool data and block transactions.
Identifies frontrun/backrun patterns, calculates price impact, and estimates
attacker profit.

Usage:
    python3 sandwich-detector.py --rpc-url $RPC_URL --blocks 1000
    python3 sandwich-detector.py --rpc-url $RPC_URL --tx-hash 0x...
    python3 sandwich-detector.py --rpc-url $RPC_URL --pair 0x... --blocks 500
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

try:
    from web3 import Web3
except ImportError:
    print("Error: web3 package required. Install with: pip install web3")
    sys.exit(1)


# Common DEX router addresses
DEX_ROUTERS = {
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D": "Uniswap V2 Router",
    "0xE592427A0AEce92De3Edee1F18E0157C05861564": "Uniswap V3 Router",
    "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F": "SushiSwap Router",
    "0x111111125421cA6dc452d289314280a0f8842A65": "1inch Router",
}

# ERC20 Transfer event signature
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# Common function selectors
SWAP_SELECTORS = {
    "0x38ed1739": "swapExactTokensForTokens",
    "0x8803dbee": "swapTokensForExactTokens",
    "0x7ff36ab5": "swapExactETHForTokens",
    "0x18cbafe5": "swapExactTokensForETH",
    "0x4a25d94a": "swapTokensForExactETH",
    "0xfb3bdb41": "swapETHForExactTokens",
    "0x5c11d795": "swapExactTokensForTokensSupportingFeeOnTransferTokens",
    "0x791ac947": "swapExactTokensForETHSupportingFeeOnTransferTokens",
    "0xb6f9de95": "swapExactETHForTokensSupportingFeeOnTransferTokens",
    "0x5f575529": "swap (Universal Router)",
}


@dataclass
class Transaction:
    """Represents a blockchain transaction."""
    hash: str
    block_number: int
    from_address: str
    to_address: str
    value: int
    gas_price: int
    input_data: str
    timestamp: int = 0

    @property
    def is_dex_swap(self) -> bool:
        """Check if transaction interacts with a known DEX router."""
        return self.to_address.lower() in [addr.lower() for addr in DEX_ROUTERS]

    @property
    def swap_type(self) -> Optional[str]:
        """Identify the swap function type."""
        selector = self.input_data[:10] if len(self.input_data) >= 10 else ""
        return SWAP_SELECTORS.get(selector)

    @property
    def function_selector(self) -> str:
        """Extract function selector from input data."""
        return self.input_data[:10] if len(self.input_data) >= 10 else ""


@dataclass
class TokenFlow:
    """Represents a token transfer within a transaction."""
    token_address: str
    from_address: str
    to_address: str
    amount: int
    log_index: int


@dataclass
class SandwichPattern:
    """Represents a detected sandwich attack pattern."""
    block_number: int
    victim_tx: Transaction
    frontrun_tx: Optional[Transaction]
    backrun_tx: Optional[Transaction]
    token_pair: tuple
    victim_slippage: float
    attacker_profit: float
    confidence: float  # 0.0 to 1.0
    evidence: list = field(default_factory=list)


class MempoolMonitor:
    """Monitors mempool for pending transactions and sandwich patterns."""

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.pending_txs: dict[str, Transaction] = {}
        self.sandwich_candidates: list[SandwichPattern] = []

    def subscribe_pending(self):
        """Subscribe to pending transactions (WebSocket only)."""
        # Note: This requires WebSocket provider
        # HTTP providers do not support subscriptions
        pass

    def add_pending_tx(self, tx_hash: str, tx_data: dict):
        """Add a pending transaction to monitoring."""
        tx = Transaction(
            hash=tx_hash,
            block_number=0,  # Not yet mined
            from_address=tx_data.get("from", ""),
            to_address=tx_data.get("to", ""),
            value=int(tx_data.get("value", "0x0"), 16),
            gas_price=int(tx_data.get("gasPrice", "0x0"), 16),
            input_data=tx_data.get("input", "0x"),
        )
        self.pending_txs[tx_hash] = tx

    def check_sandwich_pattern(self, tx_hash: str) -> Optional[SandwichPattern]:
        """Check if a newly mined transaction forms a sandwich pattern."""
        if tx_hash not in self.pending_txs:
            return None

        tx = self.pending_txs[tx_hash]
        if not tx.is_dex_swap:
            return None

        # Look for related transactions in the same block
        # This is a simplified check - full implementation would analyze
        # token flows and price impact
        return None


class PriceImpactCalculator:
    """Calculates price impact for AMM transactions."""

    @staticmethod
    def constant_product_impact(
        input_amount: int,
        reserve_in: int,
        reserve_out: int,
        fee_bps: int = 30,
    ) -> dict:
        """
        Calculate price impact for constant product AMM (x*y=k).

        Args:
            input_amount: Amount of input token
            reserve_in: Reserve of input token
            reserve_out: Reserve of output token
            fee_bps: Fee in basis points (default 30 = 0.3%)

        Returns:
            Dictionary with output amount, price impact, and execution price
        """
        if reserve_in == 0 or reserve_out == 0:
            return {"output": 0, "impact": 0.0, "execution_price": 0.0}

        # Apply fee
        input_with_fee = input_amount * (10000 - fee_bps)
        numerator = input_with_fee * reserve_out
        denominator = (reserve_in * 10000) + input_with_fee
        output_amount = numerator // denominator

        # Calculate price impact
        spot_price = reserve_out / reserve_in
        execution_price = output_amount / input_amount if input_amount > 0 else 0
        price_impact = (spot_price - execution_price) / spot_price if spot_price > 0 else 0

        return {
            "output": output_amount,
            "impact": price_impact,
            "execution_price": execution_price,
            "spot_price": spot_price,
        }

    @staticmethod
    def stable_swap_impact(
        input_amount: int,
        reserve_in: int,
        reserve_out: int,
        amplification: int = 100,
    ) -> dict:
        """
        Calculate price impact for stable swap invariant (Curve-style).

        Args:
            input_amount: Amount of input token
            reserve_in: Reserve of input token
            reserve_out: Reserve of output token
            amplification: Amplification coefficient (A)

        Returns:
            Dictionary with output amount and price impact
        """
        # Simplified stable swap calculation
        # Full implementation requires solving the invariant equation
        if reserve_in == 0 or reserve_out == 0:
            return {"output": 0, "impact": 0.0}

        # Approximation for small trades
        spot_price = reserve_out / reserve_in
        output_amount = int(input_amount * spot_price * 0.999)  # Approximate fee
        execution_price = output_amount / input_amount if input_amount > 0 else 0
        price_impact = (spot_price - execution_price) / spot_price if spot_price > 0 else 0

        return {
            "output": output_amount,
            "impact": price_impact,
            "execution_price": execution_price,
            "spot_price": spot_price,
        }


class SandwichDetector:
    """Detects sandwich attacks in block data."""

    def __init__(self, w3: Web3):
        self.w3 = w3
        self.price_calc = PriceImpactCalculator()
        self.detected_sandwiches: list[SandwichPattern] = []

    def analyze_block(self, block_number: int) -> list[SandwichPattern]:
        """
        Analyze a block for sandwich attack patterns.

        Args:
            block_number: Block number to analyze

        Returns:
            List of detected sandwich patterns
        """
        block = self.w3.eth.get_block(block_number, full_transactions=True)
        if not block or not block.transactions:
            return []

        sandwiches = []
        txs = block.transactions

        # Group transactions by DEX router
        dex_txs = [tx for tx in txs if self._is_dex_tx(tx)]

        # Look for sandwich patterns
        for i, victim_tx in enumerate(dex_txs):
            # Check for frontrun (tx before victim from different address)
            frontrun = self._find_frontrun(txs, victim_tx, i)
            # Check for backrun (tx after victim from same address as frontrun)
            backrun = self._find_backrun(txs, victim_tx, frontrun)

            if frontrun and backrun:
                pattern = self._build_sandwich_pattern(
                    block_number, victim_tx, frontrun, backrun
                )
                if pattern and pattern.confidence > 0.5:
                    sandwiches.append(pattern)

        self.detected_sandwiches.extend(sandwiches)
        return sandwiches

    def _is_dex_tx(self, tx) -> bool:
        """Check if transaction is a DEX swap."""
        to_addr = tx.get("to", "")
        if not to_addr:
            return False
        return to_addr.lower() in [addr.lower() for addr in DEX_ROUTERS]

    def _find_frontrun(self, txs: list, victim_tx, victim_index: int) -> Optional[dict]:
        """Find potential frontrun transaction."""
        victim_from = victim_tx.get("from", "").lower()

        # Look at transactions before victim in the same block
        for tx in reversed(txs[:victim_index]):
            tx_from = tx.get("from", "").lower()
            # Frontrun is from different address but same DEX
            if tx_from != victim_from and self._is_dex_tx(tx):
                return tx
        return None

    def _find_backrun(self, txs: list, victim_tx, frontrun_tx) -> Optional[dict]:
        """Find potential backrun transaction."""
        if not frontrun_tx:
            return None

        frontrun_from = frontrun_tx.get("from", "").lower()
        victim_index = next(
            (i for i, tx in enumerate(txs) if tx.get("hash") == victim_tx.get("hash")),
            0,
        )

        # Look at transactions after victim from same address as frontrun
        for tx in txs[victim_index + 1:]:
            tx_from = tx.get("from", "").lower()
            if tx_from == frontrun_from and self._is_dex_tx(tx):
                return tx
        return None

    def _build_sandwich_pattern(
        self,
        block_number: int,
        victim_tx: dict,
        frontrun_tx: dict,
        backrun_tx: dict,
    ) -> Optional[SandwichPattern]:
        """Build a sandwich pattern from detected transactions."""
        # Calculate confidence based on heuristics
        confidence = 0.0
        evidence = []

        # Same block
        confidence += 0.2
        evidence.append("Transactions in same block")

        # Same DEX
        if frontrun_tx.get("to") == victim_tx.get("to") == backrun_tx.get("to"):
            confidence += 0.2
            evidence.append("Same DEX router")

        # Frontrun and backrun from same address
        if frontrun_tx.get("from") == backrun_tx.get("from"):
            confidence += 0.3
            evidence.append("Frontrun and backrun from same address")

        # Victim from different address
        if victim_tx.get("from") != frontrun_tx.get("from"):
            confidence += 0.1
            evidence.append("Victim from different address")

        # Gas price similarity (searchers use similar gas)
        frontrun_gas = int(frontrun_tx.get("gasPrice", "0x0"), 16)
        backrun_gas = int(backrun_tx.get("gasPrice", "0x0"), 16)
        if frontrun_gas > 0 and backrun_gas > 0:
            gas_ratio = min(frontrun_gas, backrun_gas) / max(frontrun_gas, backrun_gas)
            if gas_ratio > 0.9:
                confidence += 0.2
                evidence.append("Similar gas prices")

        # Estimate slippage and profit (simplified)
        victim_slippage = 0.0
        attacker_profit = 0.0

        return SandwichPattern(
            block_number=block_number,
            victim_tx=self._tx_to_dataclass(victim_tx),
            frontrun_tx=self._tx_to_dataclass(frontrun_tx),
            backrun_tx=self._tx_to_dataclass(backrun_tx),
            token_pair=("TOKEN_A", "TOKEN_B"),  # Would be extracted from tx data
            victim_slippage=victim_slippage,
            attacker_profit=attacker_profit,
            confidence=confidence,
            evidence=evidence,
        )

    def _tx_to_dataclass(self, tx: dict) -> Transaction:
        """Convert transaction dict to Transaction dataclass."""
        return Transaction(
            hash=tx.get("hash", "").hex() if hasattr(tx.get("hash", ""), "hex") else str(tx.get("hash", "")),
            block_number=tx.get("blockNumber", 0),
            from_address=tx.get("from", ""),
            to_address=tx.get("to", "") or "",
            value=int(tx.get("value", "0x0"), 16) if isinstance(tx.get("value"), str) else tx.get("value", 0),
            gas_price=int(tx.get("gasPrice", "0x0"), 16) if isinstance(tx.get("gasPrice"), str) else tx.get("gasPrice", 0),
            input_data=tx.get("input", "0x"),
        )

    def analyze_transaction(self, tx_hash: str) -> Optional[SandwichPattern]:
        """
        Analyze a specific transaction for sandwich patterns.

        Args:
            tx_hash: Transaction hash to analyze

        Returns:
            SandwichPattern if detected, None otherwise
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            if not tx:
                return None

            block_number = tx.blockNumber
            return self.analyze_block(block_number)
        except Exception as e:
            print(f"Error analyzing transaction: {e}")
            return None

    def scan_blocks(self, start_block: int, num_blocks: int) -> list[SandwichPattern]:
        """
        Scan a range of blocks for sandwich patterns.

        Args:
            start_block: Starting block number
            num_blocks: Number of blocks to scan

        Returns:
            List of detected sandwich patterns
        """
        all_sandwiches = []
        for block_num in range(start_block, start_block + num_blocks):
            sandwiches = self.analyze_block(block_num)
            all_sandwiches.extend(sandwiches)
            if sandwiches:
                print(f"Block {block_num}: {len(sandwiches)} sandwich(es) detected")
        return all_sandwiches


class ProfitEstimator:
    """Estimates attacker profit from sandwich patterns."""

    @staticmethod
    def estimate_sandwich_profit(
        frontrun_amount: int,
        victim_amount: int,
        backrun_amount: int,
        gas_cost: int,
        fee_bps: int = 30,
    ) -> dict:
        """
        Estimate profit from a sandwich attack.

        Args:
            frontrun_amount: Amount attacker spends on frontrun
            victim_amount: Amount victim trades
            backrun_amount: Amount attacker sells on backrun
            gas_cost: Total gas cost for both transactions
            fee_bps: DEX fee in basis points

        Returns:
            Dictionary with profit breakdown
        """
        # Simplified profit calculation
        # Full implementation would simulate the AMM trades

        # Frontrun: attacker buys, price goes up
        # Victim: buys at higher price
        # Backrun: attacker sells, price returns

        # Gross profit = backrun_amount - frontrun_amount - fees
        gross_profit = backrun_amount - frontrun_amount
        fee_cost = (frontrun_amount + backrun_amount) * fee_bps / 10000
        net_profit = gross_profit - fee_cost - gas_cost

        return {
            "gross_profit": gross_profit,
            "fee_cost": fee_cost,
            "gas_cost": gas_cost,
            "net_profit": net_profit,
            "roi": net_profit / frontrun_amount if frontrun_amount > 0 else 0,
        }

    @staticmethod
    def calculate_breakeven_gas(
        frontrun_amount: int,
        expected_profit_pct: float,
        fee_bps: int = 30,
    ) -> int:
        """
        Calculate maximum gas cost for profitable sandwich.

        Args:
            frontrun_amount: Amount attacker spends on frontrun
            expected_profit_pct: Expected profit as percentage (e.g., 0.01 for 1%)
            fee_bps: DEX fee in basis points

        Returns:
            Maximum gas cost in wei
        """
        gross_profit = frontrun_amount * expected_profit_pct
        fee_cost = frontrun_amount * 2 * fee_bps / 10000  # Buy and sell
        max_gas = gross_profit - fee_cost
        return max(0, int(max_gas))


def main():
    parser = argparse.ArgumentParser(
        description="Detect sandwich attacks in Ethereum blocks"
    )
    parser.add_argument(
        "--rpc-url",
        required=True,
        help="Ethereum RPC URL (e.g., https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY)",
    )
    parser.add_argument(
        "--blocks",
        type=int,
        default=100,
        help="Number of blocks to scan (default: 100)",
    )
    parser.add_argument(
        "--tx-hash",
        help="Analyze specific transaction hash",
    )
    parser.add_argument(
        "--pair",
        help="Token pair address to filter (optional)",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (0.0-1.0, default: 0.5)",
    )

    args = parser.parse_args()

    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(args.rpc_url))
    if not w3.is_connected():
        print("Error: Cannot connect to Ethereum node")
        sys.exit(1)

    print(f"Connected to Ethereum node (chain ID: {w3.eth.chain_id})")

    detector = SandwichDetector(w3)

    if args.tx_hash:
        # Analyze specific transaction
        print(f"Analyzing transaction: {args.tx_hash}")
        sandwiches = detector.analyze_transaction(args.tx_hash)
        if sandwiches:
            for s in sandwiches:
                if s.confidence >= args.min_confidence:
                    print(format_sandwich(s))
        else:
            print("No sandwich pattern detected")
    else:
        # Scan recent blocks
        latest_block = w3.eth.block_number
        start_block = max(0, latest_block - args.blocks)
        print(f"Scanning blocks {start_block} to {latest_block}...")

        sandwiches = detector.scan_blocks(start_block, args.blocks)

        # Filter by confidence
        filtered = [s for s in sandwiches if s.confidence >= args.min_confidence]

        print(f"\nDetected {len(filtered)} sandwich pattern(s)")

        for s in filtered:
            print(format_sandwich(s))

        # Output JSON if requested
        if args.output != "-":
            output_data = [
                {
                    "block_number": s.block_number,
                    "victim_tx": s.victim_tx.hash,
                    "frontrun_tx": s.frontrun_tx.hash if s.frontrun_tx else None,
                    "backrun_tx": s.backrun_tx.hash if s.backrun_tx else None,
                    "confidence": s.confidence,
                    "victim_slippage": s.victim_slippage,
                    "attacker_profit": s.attacker_profit,
                    "evidence": s.evidence,
                }
                for s in filtered
            ]
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Results written to {args.output}")


def format_sandwich(s: SandwichPattern) -> str:
    """Format sandwich pattern for display."""
    lines = [
        f"\n{'='*60}",
        f"Sandwich Attack Detected - Block {s.block_number}",
        f"{'='*60}",
        f"Confidence: {s.confidence:.0%}",
        f"",
        f"Frontrun: {s.frontrun_tx.hash if s.frontrun_tx else 'N/A'}",
        f"  From: {s.frontrun_tx.from_address if s.frontrun_tx else 'N/A'}",
        f"",
        f"Victim:  {s.victim_tx.hash}",
        f"  From: {s.victim_tx.from_address}",
        f"",
        f"Backrun: {s.backrun_tx.hash if s.backrun_tx else 'N/A'}",
        f"  From: {s.backrun_tx.from_address if s.backrun_tx else 'N/A'}",
        f"",
        f"Evidence:",
    ]
    for e in s.evidence:
        lines.append(f"  - {e}")
    lines.append(f"{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
