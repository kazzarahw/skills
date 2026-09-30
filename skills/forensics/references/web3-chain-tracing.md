# Web3 Chain Tracing

On-chain fund tracing procedures for tracking stolen or exploited funds across blockchain networks.

## Table of Contents

- [Transaction Tracing](#transaction-tracing)
- [Bridge Tracing](#bridge-tracing)
- [Mixer Detection](#mixer-detection)
- [Exchange Identification](#exchange-identification)
- [Cross-Chain Tracing](#cross-chain-tracing)
- [Fund Flow Visualization](#fund-flow-visualization)
- [Evidence Collection](#evidence-collection)
- [Best Practices](#best-practices)

## Transaction Tracing

### Following Token Transfers Through Multiple Hops

```bash
# Get transaction details
cast tx <tx_hash> --rpc-url <rpc_url>

# Get transaction receipt with logs
cast receipt <tx_hash> --rpc-url <rpc_url>

# Decode transfer events
cast logs --from-block <start_block> --to-block <end_block> \
  --address <token_contract> --rpc-url <rpc_url> \
  "Transfer(address,address,uint256)"

# Trace token transfers for an address
cast logs --from-block <start_block> --to-block <end_block> \
  --rpc-url <rpc_url> \
  "Transfer(address,address,uint256)" \
  --address <token_contract>
```

### Multi-Hop Tracing Methodology

1. **Identify the source transaction** — The exploit transaction where funds were extracted
2. **Extract all outgoing transfers** — All token transfers from the attacker address
3. **Follow each transfer** — For each recipient, check if they forward funds
4. **Identify sinks** — Exchanges, mixers, bridges, or final destinations
5. **Document each hop** — Record transaction hashes, amounts, timestamps

```python
# Pseudo-code for multi-hop tracing
def trace_funds(tx_hash, rpc_url, max_hops=10):
    hops = []
    current_tx = tx_hash
    
    for hop in range(max_hops):
        tx = get_transaction(current_tx, rpc_url)
        transfers = extract_transfers(tx)
        
        for transfer in transfers:
            hops.append({
                'hop': hop,
                'tx_hash': current_tx,
                'from': transfer['from'],
                'to': transfer['to'],
                'amount': transfer['amount'],
                'token': transfer['token'],
                'timestamp': tx['timestamp']
            })
            
            # Check if recipient is a contract (forwarding)
            if is_contract(transfer['to'], rpc_url):
                current_tx = find_next_tx(transfer['to'], rpc_url)
            else:
                # Reached a sink (EOA or exchange)
                break
    
    return hops
```

## Bridge Tracing

### Lock/Mint Patterns

**Ethereum → Other Chain:**
1. User calls `lock()` on bridge contract (Ethereum)
2. Bridge contract emits `Lock` event
3. Validator/mint contract on destination chain mints tokens
4. Track the mint transaction on destination chain

**Other Chain → Ethereum:**
1. User calls `burn()` on bridge contract (source chain)
2. Bridge contract emits `Burn` event
3. Validator/release contract on Ethereum releases tokens
4. Track the release transaction on Ethereum

### Bridge Tracing Steps

```bash
# 1. Identify bridge contract interaction
cast tx <tx_hash> --rpc-url <rpc_url>

# 2. Find bridge contract address
# Look for known bridge contracts or decode calldata

# 3. Get bridge event logs
cast logs --from-block <start_block> --to-block <end_block> \
  --address <bridge_contract> --rpc-url <rpc_url> \
  "Lock(address,address,uint256)"  # or "Burn(address,address,uint256)"

# 4. Find corresponding mint/release on destination chain
# Use bridge documentation or known contract addresses

# 5. Track funds on destination chain
cast logs --from-block <start_block> --to-block <end_block> \
  --address <destination_token> --rpc-url <destination_rpc> \
  "Transfer(address,address,uint256)"
```

### Known Bridge Contracts

| Bridge | Chains | Contract Pattern |
|--------|--------|------------------|
| Multichain (Anyswap) | Multiple | Lock/Burn → Mint/Release |
| Wormhole | Multiple | Lock → Attest → Mint |
| LayerZero | Multiple | OFT (Omnichain Fungible Token) |
| Stargate | Multiple | Pool-based bridging |
| Hop Protocol | L1 → L2 | Bonding curve + AMM |
| Across Protocol | L1 → L2 | Relayer-based |
| Synapse | Multiple | Lock/Burn → Mint/Release |
| Celer Bridge | Multiple | Lock/Burn → Mint/Release |

## Mixer Detection

### Tornado Cash

```bash
# Tornado Cash contract addresses (Ethereum)
# ETH: 0x910Cbd523D972eb0a6f4cA48623c0B6617fe36e5
# DAI: 0xD2135CfB216b74109775236E36d4b433F12D0964
# USDC: 0x4736dCf1b7A3d580672CcE6E6c65045c148A6967
# USDT: 0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc

# Detect Tornado Cash deposits
cast logs --from-block <start_block> --to-block <end_block> \
  --address <tornado_contract> --rpc-url <rpc_url> \
  "Deposit(bytes32,address,uint256)"

# Detect Tornado Cash withdrawals
cast logs --from-block <start_block> --to-block <end_block> \
  --address <tornado_contract> --rpc-url <rpc_url> \
  "Withdrawal(address,bytes32,address,uint256)"
```

### Samourai Wallet

```bash
# Samourai Whirlpool (Bitcoin)
# Detect by analyzing Bitcoin transactions for Whirlpool patterns
# Whirlpool uses CoinJoin with specific denomination patterns

# Using Whirlpool API
curl "https://whirlpool.cyclops.wh/api/v0.5/whirlpool/tx0?txid=<tx_hash>"
```

### ChipMixer

```bash
# ChipMixer (Bitcoin)
# Detect by analyzing Bitcoin transactions for ChipMixer patterns
# ChipMixer uses a chip-based mixing system

# Using blockchain analysis tools
# Chainalysis, TRM Labs, or Elliptic can identify ChipMixer transactions
```

## Exchange Identification

### Known Exchange Wallet Lists

```bash
# Binance hot wallets
# 0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE (Ethereum)
# 0x28C6c06298d514Db089934071355E5743bf21d60 (Ethereum)
# 0x21a31Ee1afC51d94C2eFcCaA2a02320a174f2b34 (Ethereum)

# Coinbase hot wallets
# 0x71660c4005BA85c37ccec55d0C4493E66677f2d5 (Ethereum)
# 0x503828976D22510aad0201ac7EC88293211D23Da (Ethereum)

# Kraken hot wallets
# 0x2910543Af39abA0Cd09dBb2D50200b3E800A63D2 (Ethereum)
# 0x0A869d79a7052C7f1b55eB89Ae7e106B229E31C5 (Ethereum)

# Use Etherscan API to check if address is labeled
curl "https://api.etherscan.io/api?module=account&action=balance&address=<address>&tag=latest&apikey=<api_key>"
```

### Exchange Identification Methodology

1. **Check known wallet lists** — Compare against published exchange wallets
2. **Analyze transaction patterns** — High volume, many small deposits, regular withdrawals
3. **Check contract labels** — Use Etherscan, Etherscan labels, or Arkham
4. **Analyze gas patterns** — Exchanges often use specific gas strategies
5. **Check funding sources** — Exchanges fund from known hot wallets

```python
# Pseudo-code for exchange identification
def identify_exchange(address, rpc_url):
    # Check known exchange wallets
    if address in KNOWN_EXCHANGE_WALLETS:
        return KNOWN_EXCHANGE_WALLETS[address]
    
    # Analyze transaction patterns
    txs = get_transactions(address, rpc_url)
    
    # High transaction volume
    if len(txs) > 1000:
        # Many unique counterparties
        counterparties = set(tx['from'] for tx in txs)
        if len(counterparties) > 500:
            return "Likely Exchange"
    
    # Check contract labels
    label = get_contract_label(address)
    if label and "exchange" in label.lower():
        return label
    
    return "Unknown"
```

## Cross-Chain Tracing

### Following Funds Across Multiple Chains

1. **Identify the bridge transaction** — Find where funds left the source chain
2. **Identify the bridge contract** — Determine which bridge was used
3. **Find the destination chain** — Determine where funds were sent
4. **Track the mint/release transaction** — Find the corresponding transaction on the destination chain
5. **Continue tracing on destination chain** — Follow funds as they move

### Cross-Chain Tracing Tools

```bash
# DeBank (multi-chain portfolio tracker
curl "https://api.debank.com/user/total_balance?id=<address>"

# Zapper (multi-chain portfolio tracker)
curl "https://api.zapper.fi/v2/balances?addresses[]=<address>"

# Nansen (wallet labeling)
# Requires API access

# Arkham (entity labeling)
# Requires API access
```

## Fund Flow Visualization

### Dune Analytics

```sql
-- Example Dune query for fund flow
WITH transfers AS (
  SELECT
    "from" as sender,
    "to" as receiver,
    value as amount,
    block_time as timestamp
  FROM erc20."ERC20_evt_Transfer"
  WHERE contract_address = '<token_address>'
    AND block_time >= '<start_time>'
    AND block_time <= '<end_time>'
)
SELECT * FROM transfers
WHERE sender IN (<attacker_addresses>)
   OR receiver IN (<attacker_addresses>)
ORDER BY timestamp
```

### Nansen

```bash
# Nansen API
curl "https://api.nansen.ai/v1/address/<address>/transactions" \
  -H "Authorization: Bearer <api_key>"

# Nansen provides:
# - Wallet labels
# - Fund flow visualization
# - Smart money tracking
# - Exchange identification
```

### Chainalysis Reactor

```bash
# Chainalysis Reactor (commercial tool)
# 1. Enter transaction hash or address
# 2. Reactor automatically traces fund flow
# 3. Generates visual graph
# 4. Identifies exchanges and services
# 5. Exports evidence package
```

## Evidence Collection

### Transaction Exports

```bash
# Export transaction data
cast tx <tx_hash> --rpc-url <rpc_url> --json > /evidence/tx-<hash>.json

# Export transaction receipt
cast receipt <tx_hash> --rpc-url <rpc_url> --json > /evidence/receipt-<hash>.json

# Export event logs
cast logs --from-block <start_block> --to-block <end_block> \
  --address <contract> --rpc-url <rpc_url> --json > /evidence/logs-<contract>.json

# Export block data
cast block <block_number> --rpc-url <rpc_url> --json > /evidence/block-<number>.json
```

### Block Explorer Screenshots

```bash
# Etherscan
# 1. Navigate to transaction page
# 2. Take screenshot with timestamp
# 3. Save to evidence folder

# Using Playwright (automated screenshots)
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://etherscan.io/tx/<tx_hash>')
    page.screenshot(path='/evidence/etherscan-tx-<hash>.png', full_page=True)
    browser.close()
"
```

### Hash Verification

```bash
# Generate SHA-256 hash of evidence
sha256sum /evidence/tx-<hash>.json > /evidence/tx-<hash>.json.sha256

# Verify integrity
sha256sum -c /evidence/tx-<hash>.json.sha256

# Create evidence manifest
find /evidence -type f -exec sha256sum {} \; > /evidence/MANIFEST.sha256
```

## Best Practices

1. **Start from the exploit transaction** — Always begin tracing from the known exploit
2. **Follow the money** — Track every transfer, no matter how small
3. **Document every hop** — Record transaction hashes, amounts, timestamps
4. **Identify sinks** — Exchanges, mixers, bridges are critical endpoints
5. **Use multiple tools** — Cross-validate findings with different tools
6. **Preserve evidence** — Export and hash all data immediately
7. **Consider privacy chains** — Funds entering Monero/Zcash are effectively untraceable
8. **Monitor in real-time** — If funds are still moving, prioritize live tracing
