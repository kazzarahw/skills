# Web3 Chain Analysis

Comprehensive on-chain analysis guide. Covers chain identification, address classification, transaction analysis, contract interaction mapping, fund flow tracing, cross-chain activity, entity clustering, risk scoring, and tool selection.

## Table of Contents

- [Chain Identification](#chain-identification)
- [Address Classification](#address-classification)
- [Transaction Analysis](#transaction-analysis)
- [Contract Interaction Mapping](#contract-interaction-mapping)
- [Fund Flow Tracing](#fund-flow-tracing)
- [Cross-Chain Activity](#cross-chain-activity)
- [Entity Clustering](#entity-clustering)
- [Risk Scoring](#risk-scoring)
- [Tool Selection](#tool-selection)

---

## Chain Identification

### EVM Chains

| Chain | Chain ID | Explorer | RPC Endpoint |
|-------|----------|----------|--------------|
| Ethereum | 1 | etherscan.io | https://eth.llamarpc.com |
| BSC | 56 | bscscan.com | https://bsc-dataseed.binance.org |
| Polygon | 137 | polygonscan.com | https://polygon-rpc.com |
| Arbitrum | 42161 | arbiscan.io | https://arb1.arbitrum.io/rpc |
| Optimism | 10 | optimistic.etherscan.io | https://mainnet.optimism.io |
| Avalanche | 43114 | snowtrace.io | https://api.avax.network/ext/bc/C/rpc |
| Fantom | 250 | ftmscan.com | https://rpc.ftm.tools |
| Base | 8453 | basescan.org | https://mainnet.base.org |
| Gnosis | 100 | gnosisscan.io | https://rpc.gnosischain.com |
| Celo | 42220 | celoscan.io | https://forno.celo.org |

### Solana

| Network | Explorer | RPC Endpoint |
|---------|----------|--------------|
| Mainnet | solscan.io | https://api.mainnet-beta.solana.com |
| Devnet | solscan.io | https://api.devnet.solana.com |

### Bitcoin

| Network | Explorer | API |
|---------|----------|-----|
| Mainnet | mempool.space | https://mempool.space/api |
| Testnet | mempool.space | https://mempool.space/testnet/api |

### Cosmos

| Chain | Explorer | RPC Endpoint |
|-------|----------|--------------|
| Cosmos Hub | mintscan.io | https://rpc.cosmos.network |
| Osmosis | mintscan.io | https://rpc.osmosis.zone |
| Juno | mintscan.io | https://rpc.juno.contracts |

### Other Chains

| Chain | Explorer | Notes |
|-------|----------|-------|
| Tron | tronscan.org | TVM compatible |
| Cardanoscan | cardanoscan.io | eUTXO model |
| Near | nearblocks.io | Account-based |
| Aptos | aptoscan.com | Move-based |
| Sui | suiscan.xyz | Move-based |

---

## Address Classification

### EOA vs Contract (EVM)

```bash
# Check if address is a contract
cast code 0xAddress --rpc-url https://eth.llamarpc.com

# If returns 0x, it's an EOA
# If returns bytecode, it's a contract

# Using Etherscan API
curl -s "https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0xAddress" | jq .

# Check contract verification
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq .
```

### EOA vs Contract (Solana)

```bash
# Check if account is a program (contract)
curl -s "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getAccountInfo","params":["0xAddress",{"encoding":"base64"}]}' | jq .

# If "executable": true, it's a program (contract)
# If "executable": false, it's an EOA
```

### Proxy Detection (EVM)

```bash
# EIP-1967 implementation slot
cast storage 0xProxyAddress 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url https://eth.llamarpc.com

# EIP-1967 admin slot
cast storage 0xProxyAddress 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url https://eth.llamarpc.com

# EIP-1967 beacon slot
cast storage 0xProxyAddress 0xa3f0ad74e5423aebfd80d3ef4346578335bb9a922d1d3e748223e92b6e5e5f5e --rpc-url https://eth.llamarpc.com

# Check if implementation address is a contract
cast code 0xImplementationAddress --rpc-url https://eth.llamarpc.com
```

### Address Type Reference

| Type | EVM | Solana | Bitcoin |
|------|-----|--------|---------|
| EOA | No code at address | executable: false | N/A |
| Contract | Code at address | executable: true | N/A |
| Proxy | EIP-1967 slots set | Program with authority | N/A |
| Token | ERC-20/721/1155 | SPL Token | N/A |
| Multisig | Gnosis Safe | Squads | P2SH/P2WSH |

---

## Transaction Analysis

### Transaction Enumeration (EVM)

```bash
# Get transaction count (nonce)
cast nonce 0xAddress --rpc-url https://eth.llamarpc.com

# Get balance
cast balance 0xAddress --rpc-url https://eth.llamarpc.com

# Get transaction receipt
cast receipt 0xTxHash --rpc-url https://eth.llamarpc.com

# Get transaction details
cast tx 0xTxHash --rpc-url https://eth.llamarpc.com

# Get block details
cast block latest --rpc-url https://eth.llamarpc.com

# List transactions (Etherscan API)
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=100&sort=asc" | jq .
```

### Transaction Enumeration (Solana)

```bash
# Get account info
curl -s "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getAccountInfo","params":["0xAddress",{"encoding":"base64"}]}' | jq .

# Get transaction signatures
curl -s "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":["0xAddress",{"limit":100}]}' | jq .

# Get transaction details
curl -s "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getTransaction","params":["0xSignature",{"encoding":"json"}]}' | jq .
```

### Temporal Patterns

```bash
# Analyze transaction timing (EVM)
# Get all transactions and analyze timestamps
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | {timeStamp, from, to, value}'

# Analyze hourly distribution
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | .timeStamp | tonumber | strftime("%Y-%m-%d %H:00")' | sort | uniq -c

# Analyze daily distribution
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | .timeStamp | tonumber | strftime("%Y-%m-%d")' | sort | uniq -c
```

### Value Flow Analysis

```bash
# Analyze incoming/outgoing value (EVM)
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | {from, to, value: (.value | tonumber)}'

# Calculate total inflow
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '[.result[] | select(.to == "0xAddress") | .value | tonumber] | add'

# Calculate total outflow
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '[.result[] | select(.from == "0xAddress") | .value | tonumber] | add'

# Top counterparties
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | {counterparty: (if .from == "0xAddress" then .to else .from end)}' | sort | uniq -c | sort -rn | head -20
```

---

## Contract Interaction Mapping

### Function Call Analysis

```bash
# Decode function calls (EVM)
cast calldata "0xa9059cbb000000000000000000000000..." 

# Get function signature
cast sig "transfer(address,uint256)"

# Get function selector
cast sig-event "Transfer(address,address,uint256)"

# Analyze function calls from transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | .input' | sort | uniq -c | sort -rn
```

### Dependency Mapping

```bash
# Identify token dependencies (EVM)
# Check ERC-20 token interactions
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .

# Check NFT interactions
curl -s "https://api.etherscan.io/api?module=account&action=token1155tx&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .

# Check internal transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlistinternal&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .
```

### Admin Role Enumeration

```bash
# Check owner (OpenZeppelin Ownable)
cast call 0xContractAddress "owner()(address)" --rpc-url https://eth.llamarpc.com

# Check admin roles
cast call 0xContractAddress "getAdmin()(address)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "getRoleAdmin(bytes32)(bytes32)" 0x0000000000000000000000000000000000000000000000000000000000000000 --rpc-url https://eth.llamarpc.com

# Check pause status
cast call 0xContractAddress "paused()(bool)" --rpc-url https://eth.llamarpc.com

# Check upgradeability
cast call 0xContractAddress "implementation()(address)" --rpc-url https://eth.llamarpc.com
```

---

## Fund Flow Tracing

### Source/Sink Identification

```bash
# Identify fund sources (EVM)
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.to == "0xAddress") | {from, value: (.value | tonumber)}'

# Identify fund sinks
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.from == "0xAddress") | {to, value: (.value | tonumber)}'

# Trace fund flow through multiple hops
# Hop 1: Source -> Address
# Hop 2: Address -> Destination
# Use Etherscan API or custom script
```

### Hop Analysis

```bash
# Trace fund flow (EVM)
# Step 1: Get all outgoing transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.from == "0xAddress") | {to, value: (.value | tonumber), hash: .hash}'

# Step 2: For each destination, get their outgoing transactions
# Repeat for N hops

# Using Etherscan API for internal transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlistinternal&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .
```

### Exchange Off-Ramp Detection

```bash
# Known exchange addresses (EVM)
# Binance: 0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE
# Coinbase: 0x71660c4005BA85c37ccec55d0C4493E66Fe775d3
# Kraken: 0x2910543Af39abA0Cd09dBb2D50200B3E8A000B66
# etc.

# Check if address has interacted with known exchanges
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.to == "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE" or .from == "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE")'

# Using Nansen API
curl -s "https://api.nansen.ai/v1/address/0xAddress" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .
```

---

## Cross-Chain Activity

### Bridge Interactions

```bash
# Known bridge contracts (EVM)
# Multichain: 0x3000000000000000000000000000000000000000
# Wormhole: 0x3ee18B221449A578A6453419727927055E1c7413
# etc.

# Check bridge interactions
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.to == "0x3000000000000000000000000000000000000000")'

# Using DeFiLlama API for cross-chain data
curl -s "https://api.llama.fi/protocols" | jq '.[] | select(.name == "Multichain")'
```

### Multi-Chain Address Matching

```bash
# Same address on different chains (EVM-compatible)
# Check if address exists on multiple chains
for chain in ethereum bsc polygon arbitrum optimism avalanche fantom; do
    echo "Checking $chain..."
    cast code 0xAddress --rpc-url https://$chain-rpc.com
done

# Using Etherscan API for multiple chains
curl -s "https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=0xAddress" | jq .
curl -s "https://api.bscscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xAddress" | jq .
curl -s "https://api.polygonscan.com/api?module=contract&action=getcontractcreation&contractaddresses=0xAddress" | jq .
```

---

## Entity Clustering

### Common-Input Clustering

```bash
# Identify addresses controlled by same entity
# If multiple addresses are inputs to same transaction, likely same controller

# Get transactions with multiple inputs
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | {hash, from, to}'

# Analyze common inputs
# If Address A and Address B both input to Transaction X, they may be same entity
```

### Behavioral Clustering

```bash
# Identify addresses with similar behavior
# Similar transaction patterns, timing, counterparties

# Get transaction patterns
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | {from, to, value: (.value | tonumber), timeStamp}'

# Compare with other addresses
# Similar patterns suggest same entity
```

### Label Propagation

```bash
# Use known labels to identify unknown addresses
# If Address A is labeled as "Exchange" and Address B interacts with Address A, Address B may be related

# Using Nansen API
curl -s "https://api.nansen.ai/v1/address/0xAddress" -H "Authorization: Bearer $NANSEN_API_KEY" | jq .

# Using TRM Labs API
curl -s "https://api.trmlabs.com/v1/address/0xAddress" -H "Authorization: Bearer $TRM_API_KEY" | jq .
```

---

## Risk Scoring

### Mixer Association

```bash
# Known mixer addresses (EVM)
# Tornado Cash: 0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF
# etc.

# Check if address has interacted with mixers
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.to == "0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF" or .from == "0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF")'

# Using TRM Labs API
curl -s "https://api.trmlabs.com/v1/address/0xAddress/risk" -H "Authorization: Bearer $TRM_API_KEY" | jq .
```

### Sanctions Exposure

```bash
# Check OFAC sanctions list
curl -s "https://api.treasury.gov/v1/sdn.json" | jq '.[] | select(.name | contains("example"))'

# Using Chainalysis API
curl -s "https://api.chainalysis.com/api/v1/address/0xAddress" -H "Authorization: Bearer $CHAINALYSIS_API_KEY" | jq .

# Using TRM Labs API
curl -s "https://api.trmlabs.com/v1/address/0xAddress/sanctions" -H "Authorization: Bearer $TRM_API_KEY" | jq .
```

### Exploit Involvement

```bash
# Check if address is involved in known exploits
# Use DeFiLlama API for exploit data
curl -s "https://api.llama.fi/exploits" | jq '.[] | select(.name == "example")'

# Check if address received funds from exploit
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | select(.from == "0xExploitAddress")'

# Using rekt.news (web only, no public API available)
# Visit https://rekt.news/ for exploit data and post-mortems
# Alternative: DeFiLlama API for exploit data
curl -s "https://api.llama.fi/exploits" | jq '.[] | select(.name == "example")'
```

### Risk Score Calculation

```bash
# Risk score factors:
# - Mixer interaction: +50 points
# - Sanctions exposure: +100 points
# - Exploit involvement: +30 points
# - Unverified contract: +10 points
# - High transaction volume: +5 points
# - Cross-chain activity: +5 points
# - New address (< 30 days): +10 points
# - Known exchange interaction: -10 points
# - Verified contract: -10 points

# Risk score interpretation:
# 0-20: Low risk
# 21-50: Medium risk
# 51-80: High risk
# 81-100: Critical risk
```

---

## Tool Selection

### Block Explorers

| Tool | Chains | Features | URL |
|------|--------|----------|-----|
| Etherscan | Ethereum | Most comprehensive labels | etherscan.io |
| BscScan | BSC | BSC-specific labels | bscscan.com |
| Polygonscan | Polygon | Polygon-specific labels | polygonscan.com |
| Arbiscan | Arbitrum | Arbitrum-specific labels | arbiscan.io |
| Solscan | Solana | Best program tagging | solscan.io |
| Blockscout | Multi-chain | Open-source, self-hostable | blockscout.com |
| Mempool.space | Bitcoin | Best Bitcoin explorer | mempool.space |
| Mintscan | Cosmos | Cosmos ecosystem | mintscan.io |

### Analytics Platforms

| Tool | Features | URL |
|------|----------|-----|
| Nansen | Best-in-class wallet labeling | nansen.ai |
| TRM Labs | Compliance-grade risk engine | trmlabs.com |
| Chainalysis | Investigation and compliance | chainalysis.com |
| Elliptic | Risk scoring and compliance | elliptic.co |
| DeFiLlama | TVL and protocol data | llama.fi |
| Dune Analytics | Custom SQL queries | dune.com |


### Development Tools

| Tool | Features | URL |
|------|----------|-----|
| Tenderly | Transaction simulation and tracing | tenderly.co |
| Heimdall | Fast EVM bytecode decompilation | heimdall-rs |
| Foundry | EVM development framework | foundry.rs |
| Hardhat | EVM development framework | hardhat.org |
| Anchor | Solana development framework | anchor-lang.com |

### RPC Providers

| Provider | Chains | Free Tier | URL |
|----------|--------|-----------|-----|
| Ankr | Multi-chain | Yes | ankr.com |
| Alchemy | EVM | Yes | alchemy.com |
| Infura | EVM | Yes | infura.io |
| Helius | Solana | Yes | helius.xyz |
| QuickNode | Multi-chain | Yes | quicknode.com |
| Public RPC | EVM | Yes | Various |

### Risk Intelligence

| Tool | Features | URL |
|------|----------|-----|
| TRM Labs | Risk scoring, sanctions | trmlabs.com |
| Chainalysis | Investigation, compliance | chainalysis.com |
| Elliptic | Risk scoring, compliance | elliptic.co |
| CipherTrace | Investigation, compliance | ciphertrace.com |
| Chainabuse | Scam reporting | chainabuse.com |
