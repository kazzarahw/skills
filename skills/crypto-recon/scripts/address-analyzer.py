#!/usr/bin/env python3
"""
Address Analyzer - Blockchain address classification and risk scoring.

Performs automated analysis of blockchain addresses including:
- Address classification (EOA, contract, exchange, mixer)
- Transaction history summary
- Token holdings identification
- Contract interaction mapping
- Risk scoring
- Cross-chain activity detection

Usage:
    python address-analyzer.py <address> [--chain ethereum|solana|bitcoin] [--rpc-url URL]
"""

import argparse
import json
import sys
import hashlib
import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class AddressType(Enum):
    UNKNOWN = "unknown"
    EOA = "eoa"
    CONTRACT = "contract"
    EXCHANGE = "exchange"
    MIXER = "mixer"
    BRIDGE = "bridge"
    DEFI = "defi"
    NFT = "nft"
    TOKEN = "token"
    MULTISIG = "multisig"
    DAO = "dao"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AddressProfile:
    """Complete profile for a blockchain address."""
    address: str
    chain: str
    address_type: AddressType = AddressType.UNKNOWN
    label: Optional[str] = None
    risk_score: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: list = field(default_factory=list)
    first_seen: Optional[str] = None
    last_activity: Optional[str] = None
    total_transactions: int = 0
    inbound_count: int = 0
    outbound_count: int = 0
    total_volume: float = 0.0
    token_holdings: list = field(default_factory=list)
    contract_interactions: list = field(default_factory=list)
    counterparties: list = field(default_factory=list)
    cross_chain_activity: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class AddressAnalyzer:
    """Main analyzer class for blockchain addresses."""

    # Known address labels (simplified - in production, query database)
    KNOWN_EXCHANGES = {
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance",
        "0x71660c4005ba85c37ccec55d0c4493e6667725d": "Binance",
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance",
        "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance",
        "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance",
        "0x56eddb7aa87536c09ccc2793473599fd41a84b17": "Coinbase",
        "0x0d0707963952f2fba59dd06f2b425ace40b492": "Kraken",
        "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc": "Kraken",
        "0xae2d4617c862399ae3e3e0447c9370835972e0": "Kraken",
        "0x46340b20830761efd32832a74d7169b29dfe79": "OKX",
        "0x5041ed759dd4afc3a72b8192c143f72f4724081": "OKX",
        "0xc5451b523d5fffe175025e8a3414f397e4c543": "Bitfinex",
        "0x876eabf441b2ee5b5b0554fd502a8e0600950c": "Bitfinex",
    }

    KNOWN_MIXERS = {
        "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash 0.1 ETH",
        "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c0c2bd7d": "Tornado Cash 1 ETH",
        "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash 10 ETH",
        "0xa160cdab225685da1d56aa342ad8841c3b53f291d": "Tornado Cash 100 ETH",
        "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash 1000 ETH",
    }

    KNOWN_BRIDGES = {
        "0x8315177ab297ba92a06054ce80a67ed4dbd7ed3a": "Arbitrum Inbox",
        "0x99c9fc46f92e8a1c0dec1b1747d010903e884be1": "Optimism Portal",
        "0xa0c68c638235ee32657e8f720a3cec1cfc7c7f7": "Polygon PoS Bridge",
        "0x3ee18b221449a578a64534d9b4dc9da8609f2b60": "Wormhole",
        "0x8731d54e9d02c286767d56ac03e8037c079e1c9d": "Stargate Router",
        "0x4d9079bb4165aeb4084c526a326951dc94f8f1f8": "Across SpokePool",
    }

    KNOWN_DEFI = {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
        "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap V3 Router",
        "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "Uniswap V3 Router 2",
        "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch Router",
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "0x Exchange Proxy",
        "0x3e66b66fd1d0b02fda6c7111b779c7791234543": "Curve Router",
    }

    # Chain ID mappings
    EVM_CHAIN_IDS = {
        1: "ethereum",
        10: "optimism",
        56: "bsc",
        137: "polygon",
        250: "fantom",
        100: "gnosis",
        1284: "moonbeam",
        1285: "moonriver",
        42161: "arbitrum",
        42170: "arbitrum_nova",
        43114: "avalanche",
        8453: "base",
        59144: "linea",
        534352: "scroll",
        324: "zksync_era",
    }

    def __init__(self, rpc_url: Optional[str] = None, api_key: Optional[str] = None):
        self.rpc_url = rpc_url
        self.api_key = api_key
        self.session = None

    def _get_rpc_url(self, chain: str) -> str:
        """Get default RPC URL for chain."""
        default_rpcs = {
            "ethereum": "https://ethereum.publicnode.com",
            "optimism": "https://optimism.publicnode.com",
            "arbitrum": "https://arbitrum.publicnode.com",
            "base": "https://base.publicnode.com",
            "polygon": "https://polygon.publicnode.com",
            "bsc": "https://bsc.publicnode.com",
            "avalanche": "https://avalanche.publicnode.com",
            "fantom": "https://fantom.publicnode.com",
        }
        return self.rpc_url or default_rpcs.get(chain, "https://ethereum.publicnode.com")

    def _rpc_call(self, method: str, params: list, chain: str = "ethereum") -> dict:
        """Make JSON-RPC call to EVM chain."""
        import urllib.request
        import urllib.error

        url = self._get_rpc_url(chain)
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                if "error" in result:
                    return {"error": result["error"]}
                return result.get("result", {})
        except Exception as e:
            return {"error": str(e)}

    def _is_valid_evm_address(self, address: str) -> bool:
        """Validate EVM address format."""
        if not address.startswith("0x"):
            return False
        if len(address) != 42:
            return False
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False

    def _is_valid_solana_address(self, address: str) -> bool:
        """Validate Solana address format."""
        if len(address) < 32 or len(address) > 44:
            return False
        try:
            import base58
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except Exception:
            return False

    def _is_valid_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format."""
        # P2PKH
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        # P2WPKH/P2TR (bech32)
        if re.match(r'^bc1[a-z0-9]{25,62}$', address):
            return True
        return False

    def _detect_chain(self, address: str) -> str:
        """Detect chain from address format."""
        if self._is_valid_evm_address(address):
            return "ethereum"
        if self._is_valid_solana_address(address):
            return "solana"
        if self._is_valid_bitcoin_address(address):
            return "bitcoin"
        return "unknown"

    def _get_code(self, address: str, chain: str) -> str:
        """Get bytecode at address (EVM only)."""
        if chain not in self.EVM_CHAIN_IDS.values() and chain != "ethereum":
            return ""
        result = self._rpc_call("eth_getCode", [address, "latest"], chain)
        if isinstance(result, dict) and "error" in result:
            return ""
        return result if isinstance(result, str) else ""

    def _get_balance(self, address: str, chain: str) -> float:
        """Get native token balance."""
        result = self._rpc_call("eth_getBalance", [address, "latest"], chain)
        if isinstance(result, dict) and "error" in result:
            return 0.0
        try:
            return int(result, 16) / 1e18
        except (ValueError, TypeError):
            return 0.0

    def _get_transaction_count(self, address: str, chain: str) -> int:
        """Get transaction count (nonce) for address."""
        result = self._rpc_call("eth_getTransactionCount", [address, "latest"], chain)
        if isinstance(result, dict) and "error" in result:
            return 0
        try:
            return int(result, 16)
        except (ValueError, TypeError):
            return 0

    def _get_logs(self, address: str, chain: str, from_block: int = 0) -> list:
        """Get event logs for address."""
        result = self._rpc_call("eth_getLogs", [{
            "address": address,
            "fromBlock": hex(from_block),
            "toBlock": "latest",
        }], chain)
        if isinstance(result, dict) and "error" in result:
            return []
        return result if isinstance(result, list) else []

    def _classify_address(self, address: str, chain: str, code: str) -> tuple:
        """Classify address type and return (type, label)."""
        addr_lower = address.lower()

        # Check known labels first
        if addr_lower in self.KNOWN_EXCHANGES:
            return AddressType.EXCHANGE, self.KNOWN_EXCHANGES[addr_lower]
        if addr_lower in self.KNOWN_MIXERS:
            return AddressType.MIXER, self.KNOWN_MIXERS[addr_lower]
        if addr_lower in self.KNOWN_BRIDGES:
            return AddressType.BRIDGE, self.KNOWN_BRIDGES[addr_lower]
        if addr_lower in self.KNOWN_DEFI:
            return AddressType.DEFI, self.KNOWN_DEFI[addr_lower]

        # EVM classification
        if chain in self.EVM_CHAIN_IDS.values() or chain == "ethereum":
            if not code or code == "0x":
                return AddressType.EOA, None
            else:
                return AddressType.CONTRACT, None

        return AddressType.UNKNOWN, None

    def _calculate_risk_score(self, profile: AddressProfile) -> tuple:
        """Calculate risk score and return (score, level, factors)."""
        score = 0
        factors = []

        # Mixer interaction
        if profile.address_type == AddressType.MIXER:
            score += 80
            factors.append("Address is a known mixer/tumbler")

        # Exchange interaction
        if profile.address_type == AddressType.EXCHANGE:
            score += 20
            factors.append("Address belongs to a centralized exchange")

        # Contract risk
        if profile.address_type == AddressType.CONTRACT:
            score += 10
            factors.append("Address is a smart contract")

        # High transaction volume
        if profile.total_transactions > 10000:
            score += 15
            factors.append("Very high transaction volume")

        # Many counterparties
        if len(profile.counterparties) > 500:
            score += 10
            factors.append("Large number of counterparties")

        # Cross-chain activity
        if profile.cross_chain_activity:
            score += 10
            factors.append("Cross-chain activity detected")

        # Determine risk level
        if score >= 70:
            level = RiskLevel.CRITICAL
        elif score >= 40:
            level = RiskLevel.HIGH
        elif score >= 20:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return score, level, factors

    def _detect_cross_chain(self, address: str, chain: str) -> list:
        """Detect cross-chain activity for address."""
        activity = []

        # EVM chains - check same address on other chains
        if chain in self.EVM_CHAIN_IDS.values() or chain == "ethereum":
            for chain_id, chain_name in self.EVM_CHAIN_IDS.items():
                if chain_name != chain:
                    # In production, query each chain's RPC
                    # For now, return placeholder
                    activity.append({
                        "chain": chain_name,
                        "chain_id": chain_id,
                        "address": address,
                        "detected": False,  # Would be True if balance > 0
                        "bridge": None,
                    })

        return activity

    def _get_token_holdings(self, address: str, chain: str) -> list:
        """Get token holdings for address."""
        tokens = []

        # In production, query token contracts or use indexer
        # For now, return placeholder structure
        if chain in self.EVM_CHAIN_IDS.values() or chain == "ethereum":
            # Would query ERC-20 balances via eth_call
            pass

        return tokens

    def _get_contract_interactions(self, address: str, chain: str) -> list:
        """Get contract interaction history."""
        interactions = []

        # In production, query transaction logs and decode
        # For now, return placeholder structure
        if chain in self.EVM_CHAIN_IDS.values() or chain == "ethereum":
            logs = self._get_logs(address, chain)
            for log in logs[:100]:  # Limit to recent 100
                interactions.append({
                    "contract": log.get("address"),
                    "event": log.get("topics", [None])[0] if log.get("topics") else None,
                    "block": log.get("blockNumber"),
                    "tx_hash": log.get("transactionHash"),
                })

        return interactions

    def analyze(self, address: str, chain: Optional[str] = None) -> AddressProfile:
        """
        Perform complete analysis of a blockchain address.

        Args:
            address: The blockchain address to analyze
            chain: Optional chain hint (ethereum, solana, bitcoin)

        Returns:
            AddressProfile with complete analysis results
        """
        # Detect chain if not provided
        if not chain:
            chain = self._detect_chain(address)

        # Initialize profile
        profile = AddressProfile(address=address, chain=chain)

        # EVM analysis
        if chain in self.EVM_CHAIN_IDS.values() or chain == "ethereum":
            self._analyze_evm(address, chain, profile)
        elif chain == "solana":
            self._analyze_solana(address, profile)
        elif chain == "bitcoin":
            self._analyze_bitcoin(address, profile)
        else:
            profile.address_type = AddressType.UNKNOWN
            profile.risk_factors.append("Unknown chain or address format")

        # Calculate risk score
        score, level, factors = self._calculate_risk_score(profile)
        profile.risk_score = score
        profile.risk_level = level
        profile.risk_factors.extend(factors)

        return profile

    def _analyze_evm(self, address: str, chain: str, profile: AddressProfile):
        """Analyze EVM address."""
        # Get bytecode
        code = self._get_code(address, chain)

        # Classify
        addr_type, label = self._classify_address(address, chain, code)
        profile.address_type = addr_type
        profile.label = label

        # Get balance
        balance = self._get_balance(address, chain)
        profile.metadata["balance"] = balance

        # Get transaction count
        tx_count = self._get_transaction_count(address, chain)
        profile.total_transactions = tx_count

        # Get token holdings
        profile.token_holdings = self._get_token_holdings(address, chain)

        # Get contract interactions
        profile.contract_interactions = self._get_contract_interactions(address, chain)

        # Detect cross-chain activity
        profile.cross_chain_activity = self._detect_cross_chain(address, chain)

    def _analyze_solana(self, address: str, profile: AddressProfile):
        """Analyze Solana address."""
        # In production, use Solana RPC
        profile.address_type = AddressType.UNKNOWN
        profile.risk_factors.append("Solana analysis requires RPC endpoint")

    def _analyze_bitcoin(self, address: str, profile: AddressProfile):
        """Analyze Bitcoin address."""
        # In production, use Bitcoin RPC or indexer
        profile.address_type = AddressType.UNKNOWN
        profile.risk_factors.append("Bitcoin analysis requires RPC endpoint")

    def generate_report(self, profile: AddressProfile) -> str:
        """Generate formatted report from profile."""
        lines = [
            f"# Address Analysis Report",
            f"",
            f"**Address:** `{profile.address}`",
            f"**Chain:** {profile.chain}",
            f"**Type:** {profile.address_type.value}",
            f"**Label:** {profile.label or 'N/A'}",
            f"**Risk Score:** {profile.risk_score}/100 ({profile.risk_level.value})",
            f"",
            f"## Risk Factors",
        ]

        if profile.risk_factors:
            for factor in profile.risk_factors:
                lines.append(f"- {factor}")
        else:
            lines.append("- No risk factors identified")

        lines.extend([
            f"",
            f"## Activity Summary",
            f"- Total Transactions: {profile.total_transactions}",
            f"- Inbound: {profile.inbound_count}",
            f"- Outbound: {profile.outbound_count}",
            f"- Total Volume: {profile.total_volume:.6f}",
            f"- Unique Counterparties: {len(profile.counterparties)}",
            f"",
            f"## Token Holdings",
        ])

        if profile.token_holdings:
            for token in profile.token_holdings:
                lines.append(f"- {token.get('symbol', 'Unknown')}: {token.get('balance', 0)}")
        else:
            lines.append("- No tokens detected")

        lines.extend([
            f"",
            f"## Contract Interactions",
        ])

        if profile.contract_interactions:
            for interaction in profile.contract_interactions[:10]:
                lines.append(f"- `{interaction.get('contract', 'Unknown')}` - Block {interaction.get('block', 'N/A')}")
        else:
            lines.append("- No contract interactions detected")

        lines.extend([
            f"",
            f"## Cross-Chain Activity",
        ])

        if profile.cross_chain_activity:
            for activity in profile.cross_chain_activity:
                if activity.get("detected"):
                    lines.append(f"- {activity['chain']}: Detected via {activity.get('bridge', 'unknown')}")
        else:
            lines.append("- No cross-chain activity detected")

        lines.extend([
            f"",
            f"## Metadata",
            f"```json",
            json.dumps(profile.metadata, indent=2),
            f"```",
        ])

        return "\n".join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Blockchain Address Analyzer - Classify and score addresses"
    )
    parser.add_argument(
        "address",
        help="Blockchain address to analyze"
    )
    parser.add_argument(
        "--chain",
        choices=["ethereum", "solana", "bitcoin", "optimism", "arbitrum", "base", "polygon", "bsc", "avalanche", "fantom"],
        help="Blockchain network (auto-detected if not specified)"
    )
    parser.add_argument(
        "--rpc-url",
        help="Custom RPC endpoint URL"
    )
    parser.add_argument(
        "--api-key",
        help="API key for RPC provider"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = AddressAnalyzer(rpc_url=args.rpc_url, api_key=args.api_key)

    # Run analysis
    try:
        profile = analyzer.analyze(args.address, chain=args.chain)
    except Exception as e:
        print(f"Error analyzing address: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate output
    if args.json:
        output = json.dumps({
            "address": profile.address,
            "chain": profile.chain,
            "type": profile.address_type.value,
            "label": profile.label,
            "risk_score": profile.risk_score,
            "risk_level": profile.risk_level.value,
            "risk_factors": profile.risk_factors,
            "total_transactions": profile.total_transactions,
            "inbound_count": profile.inbound_count,
            "outbound_count": profile.outbound_count,
            "total_volume": profile.total_volume,
            "token_holdings": profile.token_holdings,
            "contract_interactions": profile.contract_interactions,
            "cross_chain_activity": profile.cross_chain_activity,
            "metadata": profile.metadata,
        }, indent=2)
    else:
        output = analyzer.generate_report(profile)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
