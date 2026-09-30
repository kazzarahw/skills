#!/usr/bin/env python3
"""
address-analyzer.py - Blockchain address classification and risk scoring

Usage: python3 address-analyzer.py -a <address> -c <chain> [-o output.json]

This script analyzes blockchain addresses:
  - Classifies address type (EOA/contract)
  - Retrieves transaction summary
  - Identifies contract interactions
  - Calculates risk score
  - Outputs structured JSON

Constitutional rules enforced:
  - Chain context confirmation
  - Evidence-based findings
  - Structured output format
"""

import argparse
import json
import sys
import re
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AddressInfo:
    """Blockchain address information."""
    address: str
    chain: str
    address_type: str = "unknown"
    is_contract: bool = False
    is_verified: bool = False
    contract_name: str = ""
    balance: str = "0"
    transaction_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    risk_score: int = 0
    risk_factors: List[str] = field(default_factory=list)
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskIndicator:
    """Risk indicator for an address."""
    category: str
    severity: str
    description: str
    score: int
    evidence: str


# ============================================================================
# Chain Configurations
# ============================================================================

CHAIN_CONFIGS = {
    "ethereum": {
        "name": "Ethereum",
        "explorer": "etherscan.io",
        "api_url": "https://api.etherscan.io/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 1,
    },
    "bsc": {
        "name": "BNB Smart Chain",
        "explorer": "bscscan.com",
        "api_url": "https://api.bscscan.com/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 56,
    },
    "polygon": {
        "name": "Polygon",
        "explorer": "polygonscan.com",
        "api_url": "https://api.polygonscan.com/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 137,
    },
    "arbitrum": {
        "name": "Arbitrum",
        "explorer": "arbiscan.io",
        "api_url": "https://api.arbiscan.io/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 42161,
    },
    "optimism": {
        "name": "Optimism",
        "explorer": "optimistic.etherscan.io",
        "api_url": "https://api-optimistic.etherscan.io/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 10,
    },
    "avalanche": {
        "name": "Avalanche",
        "explorer": "snowtrace.io",
        "api_url": "https://api.snowtrace.io/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 43114,
    },
    "fantom": {
        "name": "Fantom",
        "explorer": "ftmscan.com",
        "api_url": "https://api.ftmscan.com/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 250,
    },
    "base": {
        "name": "Base",
        "explorer": "basescan.org",
        "api_url": "https://api.basescan.org/api",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "chain_id": 8453,
    },
    "solana": {
        "name": "Solana",
        "explorer": "solscan.io",
        "api_url": "https://api.solscan.io/v2",
        "address_pattern": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
        "chain_id": None,
    },
    "bitcoin": {
        "name": "Bitcoin",
        "explorer": "mempool.space",
        "api_url": "https://mempool.space/api",
        "address_pattern": r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{25,39}$",
        "chain_id": None,
    },
}

# Known mixer addresses (EVM)
KNOWN_MIXERS = {
    "0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF": "Tornado Cash",
    "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c0c3d7f9": "Tornado Cash",
    "0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc": "Tornado Cash Router",
}

# Known exchange addresses (EVM)
KNOWN_EXCHANGES = {
    "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE": "Binance",
    "0x71660c4005BA85c37ccec55d0C4493E66Fe775d3": "Coinbase",
    "0x2910543Af39abA0Cd09dBb2D50200B3E8A000B66": "Kraken",
    "0xA910f92ACd497d1CAC917a2183C79C90cBf09e27": "Binance",
    "0x5a52e96bacdabb82fd05763e25335261b270efcb": "Coinbase",
}

# Known protocol addresses (EVM)
KNOWN_PROTOCOLS = {
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D": "Uniswap V2 Router",
    "0xE592427A0AEce92De3Edee1F18E0157C05861564": "Uniswap V3 Router",
    "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9": "Aave V2 Lending Pool",
    "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2": "Aave V3 Pool",
    "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B": "Compound Comptroller",
    "0x5ef30b9986345249bc32d8928B7ee64DE9435E39": "MakerDAO CDP Manager",
    "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1c7": "Curve",
    "0xBA12222222228d8Ba445958a75a0704d566BF2C8": "Balancer Vault",
    "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1": "Yearn",
    "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84": "Lido stETH",
    "0x59244D83DC15d36847C35209b1B5c9E19d26Bf5d": "Rocket Pool",
}


# ============================================================================
# Utility Functions
# ============================================================================

def validate_address(address: str, chain: str) -> bool:
    """Validate address format for the given chain."""
    if chain not in CHAIN_CONFIGS:
        return False
    pattern = CHAIN_CONFIGS[chain]["address_pattern"]
    return bool(re.match(pattern, address))


def get_chain_config(chain: str) -> Dict[str, Any]:
    """Get chain configuration."""
    return CHAIN_CONFIGS.get(chain, {})


def calculate_risk_score(info: AddressInfo) -> int:
    """Calculate risk score based on various factors."""
    score = 0

    # Unverified contract
    if info.is_contract and not info.is_verified:
        score += 20
        info.risk_factors.append("Unverified contract")

    # High transaction count
    if info.transaction_count > 10000:
        score += 5
        info.risk_factors.append("High transaction volume")

    # Mixer interaction
    for interaction in info.interactions:
        counterparty = interaction.get("counterparty", "")
        if counterparty in KNOWN_MIXERS:
            score += 50
            info.risk_factors.append(f"Mixer interaction: {KNOWN_MIXERS[counterparty]}")
            break

    # Sanctions exposure (placeholder - would need API call)
    # score += 100
    # info.risk_factors.append("Sanctions exposure")

    # New address (less than 30 days)
    if info.first_seen:
        try:
            first_seen = datetime.fromisoformat(info.first_seen.replace("Z", "+00:00"))
            days_old = (datetime.now() - first_seen).days
            if days_old < 30:
                score += 10
                info.risk_factors.append(f"New address ({days_old} days old)")
        except (ValueError, TypeError):
            pass

    # Known exchange interaction (reduces risk)
    for interaction in info.interactions:
        counterparty = interaction.get("counterparty", "")
        if counterparty in KNOWN_EXCHANGES:
            score -= 10
            info.risk_factors.append(f"Exchange interaction: {KNOWN_EXCHANGES[counterparty]}")
            break

    # Known protocol interaction (reduces risk)
    for interaction in info.interactions:
        counterparty = interaction.get("counterparty", "")
        if counterparty in KNOWN_PROTOCOLS:
            score -= 5
            info.risk_factors.append(f"Protocol interaction: {KNOWN_PROTOCOLS[counterparty]}")
            break

    # Clamp score to 0-100
    score = max(0, min(100, score))

    return score


def get_risk_level(score: int) -> str:
    """Get risk level from score."""
    if score >= 80:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 20:
        return "medium"
    else:
        return "low"


# ============================================================================
# HTTP Helper
# ============================================================================

def _http_get(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """Make an HTTP GET request and return JSON response."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "address-analyzer/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None


def _http_post(url: str, payload: Dict[str, Any], timeout: int = 30) -> Optional[Dict[str, Any]]:
    """Make an HTTP POST request with JSON payload and return JSON response."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "address-analyzer/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None


# ============================================================================
# EVM Analysis
# ============================================================================

def analyze_evm_address(address: str, chain: str, api_key: Optional[str] = None) -> AddressInfo:
    """Analyze an EVM address."""
    info = AddressInfo(address=address, chain=chain)

    # Determine if contract by checking if address has code
    info.is_contract = _check_if_contract_evm(address, chain, api_key)

    if info.is_contract:
        info.address_type = "contract"
        info.is_verified, info.contract_name = _check_contract_verification_evm(address, chain, api_key)
    else:
        info.address_type = "eoa"

    # Get balance
    info.balance = _get_balance_evm(address, chain, api_key)

    # Get transaction count
    info.transaction_count = _get_transaction_count_evm(address, chain, api_key)

    # Get interactions
    info.interactions = _get_interactions_evm(address, chain, api_key)

    # Get labels
    info.labels = _get_labels_evm(address)

    # Calculate risk score
    info.risk_score = calculate_risk_score(info)

    return info


def _get_api_url(chain: str, params: Dict[str, str], api_key: Optional[str] = None) -> str:
    """Build API URL with parameters."""
    config = CHAIN_CONFIGS[chain]
    params["apikey"] = api_key or ""
    query = urllib.parse.urlencode(params)
    return f"{config['api_url']}?{query}"


def _check_if_contract_evm(address: str, chain: str, api_key: Optional[str] = None) -> bool:
    """Check if EVM address is a contract using Etherscan API."""
    url = _get_api_url(chain, {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
    }, api_key)
    data = _http_get(url)
    if data and data.get("result"):
        result = data["result"]
        if isinstance(result, list) and len(result) > 0:
            # If there's source code or bytecode, it's a contract
            return bool(result[0].get("SourceCode") or result[0].get("Bytecode"))
    return False


def _check_contract_verification_evm(address: str, chain: str, api_key: Optional[str] = None) -> tuple:
    """Check if EVM contract is verified using Etherscan API."""
    url = _get_api_url(chain, {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
    }, api_key)
    data = _http_get(url)
    if data and data.get("result"):
        result = data["result"]
        if isinstance(result, list) and len(result) > 0:
            entry = result[0]
            is_verified = bool(entry.get("SourceCode"))
            contract_name = entry.get("ContractName", "")
            return is_verified, contract_name
    return False, ""


def _get_balance_evm(address: str, chain: str, api_key: Optional[str] = None) -> str:
    """Get EVM address balance using Etherscan API."""
    url = _get_api_url(chain, {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
    }, api_key)
    data = _http_get(url)
    if data and data.get("result") is not None:
        return str(data["result"])
    return "0"


def _get_transaction_count_evm(address: str, chain: str, api_key: Optional[str] = None) -> int:
    """Get EVM address transaction count using Etherscan API."""
    url = _get_api_url(chain, {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": "0",
        "endblock": "99999999",
        "page": "1",
        "offset": "1",
        "sort": "asc",
    }, api_key)
    data = _http_get(url)
    if data and data.get("result"):
        if isinstance(data["result"], list):
            # Etherscan returns up to 10000 records; if we got 10000, there are more
            if len(data["result"]) == 10000:
                return 10000  # At least 10000
            return len(data["result"])
    return 0


def _get_interactions_evm(address: str, chain: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get EVM address interactions using Etherscan API."""
    url = _get_api_url(chain, {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": "0",
        "endblock": "99999999",
        "page": "1",
        "offset": "100",
        "sort": "desc",
    }, api_key)
    data = _http_get(url)
    interactions = []
    if data and data.get("result") and isinstance(data["result"], list):
        for tx in data["result"]:
            counterparty = tx.get("to", "") if tx.get("from", "").lower() == address.lower() else tx.get("from", "")
            interactions.append({
                "counterparty": counterparty,
                "type": "contract_call" if tx.get("input", "0x") != "0x" else "transfer",
                "value": str(int(tx.get("value", "0")) / 10**18),
                "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))).isoformat() if tx.get("timeStamp") else "",
                "hash": tx.get("hash", ""),
            })
    return interactions


def _get_labels_evm(address: str) -> List[str]:
    """Get labels for EVM address."""
    labels = []
    if address in KNOWN_MIXERS:
        labels.append(f"Mixer: {KNOWN_MIXERS[address]}")
    if address in KNOWN_EXCHANGES:
        labels.append(f"Exchange: {KNOWN_EXCHANGES[address]}")
    if address in KNOWN_PROTOCOLS:
        labels.append(f"Protocol: {KNOWN_PROTOCOLS[address]}")
    return labels


# ============================================================================
# Solana Analysis
# ============================================================================

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"


def analyze_solana_address(address: str, chain: str, api_key: Optional[str] = None) -> AddressInfo:
    """Analyze a Solana address."""
    info = AddressInfo(address=address, chain=chain)

    # Determine if program (contract) by checking if executable
    info.is_contract = _check_if_program_solana(address, api_key)

    if info.is_contract:
        info.address_type = "program"
        info.is_verified, info.contract_name = _check_program_verification_solana(address, api_key)
    else:
        info.address_type = "account"

    # Get balance
    info.balance = _get_balance_solana(address, api_key)

    # Get transaction count
    info.transaction_count = _get_transaction_count_solana(address, api_key)

    # Get interactions
    info.interactions = _get_interactions_solana(address, api_key)

    # Calculate risk score
    info.risk_score = calculate_risk_score(info)

    return info


def _check_if_program_solana(address: str, api_key: Optional[str] = None) -> bool:
    """Check if Solana address is a program using Solana RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [address, {"encoding": "base64"}],
    }
    data = _http_post(SOLANA_RPC_URL, payload)
    if data and data.get("result") and data["result"].get("value"):
        return data["result"]["value"].get("executable", False)
    return False


def _check_program_verification_solana(address: str, api_key: Optional[str] = None) -> tuple:
    """Check if Solana program is verified using Solscan API."""
    url = f"https://api.solscan.io/v2/account/detail?address={address}"
    data = _http_get(url)
    if data and data.get("data"):
        entry = data["data"]
        is_verified = bool(entry.get("verified"))
        contract_name = entry.get("name", "")
        return is_verified, contract_name
    return False, ""


def _get_balance_solana(address: str, api_key: Optional[str] = None) -> str:
    """Get Solana address balance using Solana RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address],
    }
    data = _http_post(SOLANA_RPC_URL, payload)
    if data and data.get("result") and data["result"].get("value") is not None:
        # Convert lamports to SOL
        lamports = data["result"]["value"]
        return str(lamports / 10**9)
    return "0"


def _get_transaction_count_solana(address: str, api_key: Optional[str] = None) -> int:
    """Get Solana address transaction count using Solana RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [address, {"limit": 1000}],
    }
    data = _http_post(SOLANA_RPC_URL, payload)
    if data and data.get("result") and isinstance(data["result"], list):
        return len(data["result"])
    return 0


def _get_interactions_solana(address: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get Solana address interactions using Solana RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [address, {"limit": 100}],
    }
    data = _http_post(SOLANA_RPC_URL, payload)
    interactions = []
    if data and data.get("result") and isinstance(data["result"], list):
        for sig in data["result"]:
            interactions.append({
                "counterparty": "",
                "type": "transaction",
                "value": "0",
                "timestamp": datetime.fromtimestamp(sig.get("blockTime", 0)).isoformat() if sig.get("blockTime") else "",
                "hash": sig.get("signature", ""),
            })
    return interactions


# ============================================================================
# Bitcoin Analysis
# ============================================================================

def analyze_bitcoin_address(address: str, chain: str, api_key: Optional[str] = None) -> AddressInfo:
    """Analyze a Bitcoin address."""
    info = AddressInfo(address=address, chain=chain)
    info.address_type = "eoa"

    # Get balance
    info.balance = _get_balance_bitcoin(address)

    # Get transaction count
    info.transaction_count = _get_transaction_count_bitcoin(address)

    # Calculate risk score
    info.risk_score = calculate_risk_score(info)

    return info


def _get_balance_bitcoin(address: str) -> str:
    """Get Bitcoin address balance using mempool.space API."""
    url = f"https://mempool.space/api/address/{address}"
    data = _http_get(url)
    if data:
        # Balance is in satoshis
        funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
        spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
        balance_sat = funded - spent
        return str(balance_sat / 10**8)  # Convert to BTC
    return "0"


def _get_transaction_count_bitcoin(address: str) -> int:
    """Get Bitcoin address transaction count using mempool.space API."""
    url = f"https://mempool.space/api/address/{address}"
    data = _http_get(url)
    if data:
        stats = data.get("chain_stats", {})
        return stats.get("tx_count", 0)
    return 0


# ============================================================================
# Output Formatting
# ============================================================================

def format_output(info: AddressInfo, output_format: str = "json") -> str:
    """Format output in the specified format."""
    if output_format == "json":
        return json.dumps(asdict(info), indent=2, default=str)
    elif output_format == "markdown":
        return _format_markdown(info)
    else:
        return json.dumps(asdict(info), indent=2, default=str)


def _format_markdown(info: AddressInfo) -> str:
    """Format output as markdown."""
    risk_level = get_risk_level(info.risk_score)

    md = f"""# Address Analysis: {info.address}

**Chain:** {info.chain}
**Type:** {info.address_type}
**Risk Score:** {info.risk_score}/100 ({risk_level.upper()})

## Address Information

| Property | Value |
|----------|-------|
| Address | `{info.address}` |
| Chain | {info.chain} |
| Type | {info.address_type} |
| Contract | {info.is_contract} |
| Verified | {info.is_verified} |
| Contract Name | {info.contract_name or "N/A"} |
| Balance | {info.balance} |
| Transaction Count | {info.transaction_count} |
| First Seen | {info.first_seen or "N/A"} |
| Last Seen | {info.last_seen or "N/A"} |

## Risk Assessment

**Risk Score:** {info.risk_score}/100
**Risk Level:** {risk_level.upper()}

### Risk Factors
"""

    if info.risk_factors:
        for factor in info.risk_factors:
            md += f"- {factor}\n"
    else:
        md += "- No risk factors identified\n"

    md += "\n## Labels\n"
    if info.labels:
        for label in info.labels:
            md += f"- {label}\n"
    else:
        md += "- No labels\n"

    md += "\n## Interactions\n"
    if info.interactions:
        md += "| Counterparty | Type | Value | Timestamp |\n"
        md += "|-------------|------|-------|----------|\n"
        for interaction in info.interactions:
            md += f"| `{interaction.get('counterparty', 'N/A')}` | {interaction.get('type', 'N/A')} | {interaction.get('value', 'N/A')} | {interaction.get('timestamp', 'N/A')} |\n"
    else:
        md += "No interactions found\n"

    return md


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Blockchain address classification and risk scoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 address-analyzer.py -a 0x1234... -c ethereum
  python3 address-analyzer.py -a 0x1234... -c ethereum -o output.json
  python3 address-analyzer.py -a 0x1234... -c ethereum -f markdown
  python3 address-analyzer.py -a SolanaAddress... -c solana
        """
    )

    parser.add_argument("-a", "--address", required=True, help="Blockchain address to analyze")
    parser.add_argument("-c", "--chain", required=True, choices=list(CHAIN_CONFIGS.keys()), help="Blockchain network")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-f", "--format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("-k", "--api-key", help="API key for block explorer")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Validate address
    if not validate_address(args.address, args.chain):
        print(f"Error: Invalid address format for {args.chain}", file=sys.stderr)
        print(f"Address: {args.address}", file=sys.stderr)
        sys.exit(1)

    # Analyze address
    if args.chain in ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche", "fantom", "base"]:
        info = analyze_evm_address(args.address, args.chain, args.api_key)
    elif args.chain == "solana":
        info = analyze_solana_address(args.address, args.chain, args.api_key)
    elif args.chain == "bitcoin":
        info = analyze_bitcoin_address(args.address, args.chain, args.api_key)
    else:
        print(f"Error: Unsupported chain: {args.chain}", file=sys.stderr)
        sys.exit(1)

    # Format output
    output = format_output(info, args.format)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
