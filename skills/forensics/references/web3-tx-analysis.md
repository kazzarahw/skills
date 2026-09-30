# Web3 Transaction Analysis

Techniques for analyzing blockchain transactions during incident response.

## Table of Contents

- [Transaction Decoding](#transaction-decoding)
- [Event Log Analysis](#event-log-analysis)
- [Internal Transaction Analysis](#internal-transaction-analysis)
- [Gas Analysis](#gas-analysis)
- [MEV Detection](#mev-detection)
- [Tools](#tools)
- [Best Practices](#best-practices)

## Transaction Decoding

### Calldata Decoding

```bash
# Decode transaction input data
cast tx <tx_hash> --rpc-url <rpc_url> --json | jq -r '.input' | cast calldata-decode "transfer(address,uint256)"

# Decode function signature
cast 4byte 0xa9059cbb  # transfer(address,uint256)

# Decode calldata with signature
cast calldata-decode "transfer(address,uint256)" 0xa9059cbb000000000000000000000000...

# Get function selector
cast sig "transfer(address,uint256)"
# Output: 0xa9059cbb
```

### Function Identification

```bash
# Look up function signature
cast 4byte 0xa9059cbb
# Output: transfer(address,uint256)

# Look up function signature by hash
cast 4byte 0x23b872dd
# Output: transferFrom(address,address,uint256)

# Get function signature from contract
cast abi-encode "transfer(address,uint256)" <address> <amount>
```

### Event Log Decoding

```bash
# Get transaction receipt with logs
cast receipt <tx_hash> --rpc-url <rpc_url> --json

# Decode event logs
cast logs --from-block <start_block> --to-block <end_block> \
  --address <contract> --rpc-url <rpc_url> \
  "Transfer(address,address,uint256)"

# Decode specific event
cast keccak "Transfer(address,address,uint256)"
# Output: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
```

## Event Log Analysis

### Event Emission

```bash
# Get all events from a transaction
cast receipt <tx_hash> --rpc-url <rpc_url> --json | jq '.logs'

# Get events from a specific contract
cast logs --from-block <start_block> --to-block <end_block> \
  --address <contract> --rpc-url <rpc_url>

# Get events by topic
cast logs --from-block <start_block> --to-block <end_block> \
  --rpc-url <rpc_url> \
  --topic0 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
```

### Parameter Decoding

```bash
# Decode event parameters
# Transfer event: Transfer(address indexed from, address indexed to, uint256 value)
# Topics: [event_signature, from, to]
# Data: [value]

cast receipt <tx_hash> --rpc-url <rpc_url> --json | jq '.logs[] | {
  address: .address,
  topics: .topics,
  data: .data
}'

# Decode indexed parameters (from topics)
cast --to-address 0x000000000000000000000000<address>

# Decode non-indexed parameters (from data)
cast --to-dec 0x<hex_value>
```

### Common Event Signatures

| Event | Signature | Topic Hash |
|-------|-----------|------------|
| Transfer | Transfer(address,address,uint256) | 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef |
| Approval | Approval(address,address,uint256) | 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925 |
| Swap | Swap(address,uint256,uint256,uint256,uint256,address) | 0xc42079f94a6350d7e6235f2b175474a392040f37ea37bd855af0625086345896 |
| Deposit | Deposit(address,uint256) | 0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c |
| Withdrawal | Withdrawal(address,uint256) | 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65 |

## Internal Transaction Analysis

### Contract-to-Contract Calls

```bash
# Get internal transactions (debug_traceTransaction)
# Note: Requires archive node or specific RPC support

# Using cast (with debug API)
cast rpc debug_traceTransaction <tx_hash> --rpc-url <rpc_url>

# Using ethers.js
# const tx = await provider.send('debug_traceTransaction', [txHash, {}]);

# Analyze internal calls
# Look for:
# - Contract-to-contract transfers
# - Flash loan patterns
# - Reentrancy patterns
# - Proxy contract interactions
```

### Internal Transaction Patterns

**Flash Loan Pattern:**
1. Borrow tokens from lending protocol
2. Perform operations (swap, liquidate, etc.)
3. Repay loan + fee
4. Keep profit

**Reentrancy Pattern:**
1. Attacker calls vulnerable function
2. Vulnerable function sends tokens to attacker
3. Attacker's fallback function re-enters vulnerable function
4. Repeat until drained

**Proxy Pattern:**
1. Attacker calls proxy contract
2. Proxy delegates to implementation contract
3. Implementation executes logic
4. Results returned through proxy

## Gas Analysis

### Gas Price Patterns

```bash
# Get transaction gas details
cast tx <tx_hash> --rpc-url <rpc_url> --json | jq '{
  gas_price: .gas_price,
  gas_limit: .gas,
  max_fee_per_gas: .maxFeePerGas,
  max_priority_fee_per_gas: .maxPriorityFeePerGas
}'

# Analyze gas price patterns
# High gas price = urgency (front-running, arbitrage)
# Low gas price = non-urgent (regular transfer)
# Very high gas price = potential MEV
```

### Gas Limit Analysis

```bash
# Get gas used
cast receipt <tx_hash> --rpc-url <rpc_url> --json | jq '{
  gas_used: .gasUsed,
  gas_limit: .gasLimit,
  gas_used_ratio: (.gasUsed / .gasLimit)
}'

# Analyze gas usage
# High gas usage = complex contract interaction
# Low gas usage = simple transfer
# Gas limit >> gas used = potential DoS attempt
```

### Gas Anomaly Detection

```python
# Pseudo-code for gas anomaly detection
def detect_gas_anomaly(tx, rpc_url):
    gas_price = tx['gasPrice']
    gas_used = tx['gasUsed']
    gas_limit = tx['gas']
    
    # Check for unusually high gas price
    avg_gas_price = get_average_gas_price(tx['blockNumber'])
    if gas_price > avg_gas_price * 10:
        return "Unusually high gas price"
    
    # Check for gas limit manipulation
    if gas_limit > gas_used * 10:
        return "Gas limit much higher than gas used"
    
    # Check for failed transactions with high gas
    if tx['status'] == 0 and gas_used > gas_limit * 0.9:
        return "Failed transaction with high gas usage"
    
    return "Normal"
```

## MEV Detection

### Sandwich Attacks

**Pattern:**
1. Attacker buys tokens before victim (front-run)
2. Victim buys tokens (pushes price up)
3. Attacker sells tokens after victim (back-run)

**Detection:**
```bash
# Look for transactions in the same block with:
# 1. Similar token pairs
# 2. Opposite directions (buy/sell)
# 3. Same attacker address
# 4. Victim transaction in between

# Using Dune Analytics
SELECT
  block_number,
  block_time,
  hash,
  "from",
  "to",
  value
FROM ethereum.transactions
WHERE block_number = <block_number>
  AND "to" = '<dex_contract>'
ORDER BY transaction_index
```

### Backrunning

**Pattern:**
1. Attacker monitors mempool for profitable transactions
2. Attacker submits transaction with higher gas price
3. Attacker's transaction executes immediately after target transaction
4. Attacker profits from price movement

**Detection:**
```bash
# Look for transactions that:
# 1. Execute immediately after a large trade
# 2. Have similar token pairs
# 3. Have higher gas price than target transaction
# 4. Are from the same address repeatedly
```

### Arbitrage

**Pattern:**
1. Attacker identifies price difference between DEXs
2. Attacker buys on cheaper DEX
3. Attacker sells on more expensive DEX
4. Attacker profits from price difference

**Detection:**
```bash
# Look for transactions that:
# 1. Interact with multiple DEXs in same transaction
# 2. Have similar token amounts
# 3. Execute in same block
# 4. Are from smart contracts (arbitrage bots)
```

## Tools

### Tenderly

```bash
# Tenderly API
curl "https://api.tenderly.co/api/v1/public/transaction/<tx_hash>" \
  -H "X-Access-Key: <api_key>"

# Tenderly provides:
# - Transaction simulation
# - State diff analysis
# - Gas analysis
# - Internal transaction tracing
# - Debugging tools
```

### Phalcon

```bash
# Phalcon (BlockSec)
# Transaction analysis platform
# Provides:
# - Transaction decoding
# - Fund flow analysis
# - MEV detection
# - Attack detection
```

### BlockSec

```bash
# BlockSec tools
# - Phalcon: Transaction analysis
# - Phalcon Explorer: Fund flow visualization
# - Attack detection and alerting
```

### Dune Analytics

```sql
-- Example Dune query for transaction analysis
SELECT
  block_time,
  hash,
  "from",
  "to",
  value,
  gas_price,
  gas_used
FROM ethereum.transactions
WHERE hash = '<tx_hash>'
```

### Etherscan

```bash
# Etherscan API
curl "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=<tx_hash>&apikey=<api_key>"

# Etherscan provides:
# - Transaction details
# - Internal transactions
# - Event logs
# - Contract verification
# - Token transfers
```

## Best Practices

1. **Decode all calldata** — Understand what functions were called
2. **Analyze all event logs** — Events reveal contract state changes
3. **Trace internal transactions** — Contract-to-contract calls reveal attack paths
4. **Analyze gas patterns** — Gas reveals intent and urgency
5. **Detect MEV** — MEV can indicate attack sophistication
6. **Use multiple tools** — Cross-validate findings
7. **Document everything** — Record all queries and findings
8. **Preserve evidence** — Export and hash all data
