# Web3 Contract Discovery

Smart contract identification and verification guide. Covers contract verification status, proxy pattern detection, implementation contract analysis, dependency mapping, admin role enumeration, upgrade mechanism assessment, known protocol identification, and TVL/activity assessment.

## Table of Contents

- [Contract Verification Status](#contract-verification-status)
- [Proxy Pattern Detection](#proxy-pattern-detection)
- [Implementation Contract Analysis](#implementation-contract-analysis)
- [Dependency Mapping](#dependency-mapping)
- [Admin Role Enumeration](#admin-role-enumeration)
- [Upgrade Mechanism Assessment](#upgrade-mechanism-assessment)
- [Known Protocol Identification](#known-protocol-identification)
- [TVL & Activity Assessment](#tvl--activity-assessment)

---

## Contract Verification Status

### Verification Levels

| Level | Description | Risk |
|-------|-------------|------|
| Verified | Source code published and matches bytecode | Low |
| Partially Verified | Some source code published | Medium |
| Unverified | No source code published | High |
| Fake Verified | Source code doesn't match bytecode | Critical |

### Checking Verification Status (EVM)

```bash
# Etherscan API
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq .

# Check if verified
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq '.result[0].SourceCode'

# Check contract name
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq '.result[0].ContractName'

# Check compiler version
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq '.result[0].CompilerVersion'

# Check optimization
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0xAddress" | jq '.result[0].OptimizationUsed'
```

### Checking Verification Status (Solana)

```bash
# Solscan API
curl -s "https://api.solscan.io/v2/account/detail?address=0xAddress" | jq .

# Check if program is verified
curl -s "https://api.solscan.io/v2/account/detail?address=0xAddress" | jq '.data.verified'

# Check program name
curl -s "https://api.solscan.io/v2/account/detail?address=0xAddress" | jq '.data.name'
```

### Unverified Contract Analysis

```bash
# Decompile bytecode (EVM)
heimdall decompile 0xAddress --rpc-url https://eth.llamarpc.com

# Using Etherscan decompiler
# https://etherscan.io/address/0xAddress#code

# Using Dedaub
# https://app.dedaub.com/decompile

# Using Heimdall
heimdall decompile 0xAddress -o decompiled/

# Analyze bytecode
cast code 0xAddress --rpc-url https://eth.llamarpc.com | head -100

# Get bytecode size
cast codesize 0xAddress --rpc-url https://eth.llamarpc.com
```

---

## Proxy Pattern Detection

### EIP-1967 Storage Slots

```bash
# EIP-1967 Implementation Slot
# keccak256("eip1967.proxy.implementation") - 1
# 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
cast storage 0xProxyAddress 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url https://eth.llamarpc.com

# EIP-1967 Admin Slot
# keccak256("eip1967.proxy.admin") - 1
# 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103
cast storage 0xProxyAddress 0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103 --rpc-url https://eth.llamarpc.com

# EIP-1967 Beacon Slot
# keccak256("eip1967.proxy.beacon") - 1
# 0xa3f0ad74e5423aebfd80d3ef4346578335bb9a922d1d3e748223e92b6e5e5f5e
cast storage 0xProxyAddress 0xa3f0ad74e5423aebfd80d3ef4346578335bb9a922d1d3e748223e92b6e5e5f5e --rpc-url https://eth.llamarpc.com
```

### Transparent Proxy Pattern

```bash
# Check for Transparent Proxy
# 1. Check EIP-1967 implementation slot
# 2. Check if implementation is a contract
# 3. Check for admin functions in proxy

# Get implementation address
IMPL=$(cast storage 0xProxyAddress 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url https://eth.llamarpc.com)

# Check if implementation is a contract
cast code $IMPL --rpc-url https://eth.llamarpc.com

# Check for admin functions
cast sig "upgradeTo(address)"
cast sig "upgradeToAndCall(address,bytes)"
cast sig "changeAdmin(address)"
cast sig "admin()"
```

### UUPS Pattern

```bash
# Check for UUPS (Universal Upgradeable Proxy Standard)
# 1. Check for upgradeTo function in implementation
# 2. Check for authorizeUpgrade function

# Get implementation address
IMPL=$(cast storage 0xProxyAddress 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url https://eth.llamarpc.com)

# Check for UUPS functions
cast sig "upgradeTo(address)"
cast sig "upgradeToAndCall(address,bytes)"
cast sig "authorizeUpgrade(address)"
cast sig "proxiableUUID()"

# Check if implementation has upgradeTo function
cast call $IMPL "proxiableUUID()(bytes32)" --rpc-url https://eth.llamarpc.com
```

### Proxy Pattern Reference

| Pattern | Detection Method | Risk |
|---------|-----------------|------|
| EIP-1967 Transparent | Storage slot 0x3608... | Medium |
| EIP-1967 UUPS | Storage slot + upgradeTo in impl | Medium |
| EIP-1967 Beacon | Storage slot 0xa3f0... | Medium |
| Custom Proxy | Unknown storage slots | High |
| Diamond (EIP-2535) | Storage slot 0x4231... | High |
| No Proxy | No proxy patterns | Low |

---

## Implementation Contract Analysis

### Implementation Contract Identification

```bash
# Get implementation address from proxy
IMPL=$(cast storage 0xProxyAddress 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url https://eth.llamarpc.com)

# Check if implementation is verified
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$IMPL" | jq .

# Get implementation bytecode
cast code $IMPL --rpc-url https://eth.llamarpc.com

# Decompile implementation
heimdall decompile $IMPL --rpc-url https://eth.llamarpc.com
```

### Implementation Contract Analysis

```bash
# Check implementation contract name
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$IMPL" | jq '.result[0].ContractName'

# Check compiler version
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$IMPL" | jq '.result[0].CompilerVersion'

# Check optimization
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=$IMPL" | jq '.result[0].OptimizationUsed'

# Check for common patterns
# - Reentrancy guard
# - Pausable
# - Ownable
# - AccessControl
# - Upgradeable
```

### Implementation Risk Assessment

```bash
# Risk factors:
# - Unverified implementation: High risk
# - Old compiler version: Medium risk
# - No optimization: Low risk
# - No reentrancy guard: High risk
# - No pausable: Medium risk
# - No access control: High risk
# - Upgradeable: Medium risk
# - Proxy admin is EOA: High risk
# - Proxy admin is multisig: Low risk
```

---

## Dependency Mapping

### Token Dependencies

```bash
# Check ERC-20 token interactions
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .

# Check ERC-721 (NFT) interactions
curl -s "https://api.etherscan.io/api?module=account&action=token721tx&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .

# Check ERC-1155 interactions
curl -s "https://api.etherscan.io/api?module=account&action=token1155tx&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq .

# Get token balances
curl -s "https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=0xTokenAddress&address=0xContractAddress&tag=latest" | jq .
```

### Oracle Dependencies

```bash
# Check for Chainlink oracle interactions
# Chainlink Oracle: 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
cast call 0xContractAddress "oracle()(address)" --rpc-url https://eth.llamarpc.com

# Check for price feed
cast call 0xContractAddress "priceFeed()(address)" --rpc-url https://eth.llamarpc.com

# Check for latest answer
cast call 0xOracleAddress "latestAnswer()(int256)" --rpc-url https://eth.llamarpc.com

# Check for latest timestamp
cast call 0xOracleAddress "latestTimestamp()(uint256)" --rpc-url https://eth.llamarpc.com

# Check for decimals
cast call 0xOracleAddress "decimals()(uint8)" --rpc-url https://eth.llamarpc.com
```

### Protocol Dependencies

```bash
# Check for Uniswap interactions
# Uniswap V2 Router: 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
# Uniswap V3 Router: 0xE592427A0AEce92De3Edee1F18E0157C05861564

# Check for Aave interactions
# Aave V2 Lending Pool: 0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9
# Aave V3 Pool: 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2

# Check for Compound interactions
# Compound Comptroller: 0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B

# Check for MakerDAO interactions
# MakerDAO CDP Manager: 0x5ef30b9986345249bc32d8928B7ee64DE9435E39
```

---

## Admin Role Enumeration

### Ownable Pattern

```bash
# Check owner
cast call 0xContractAddress "owner()(address)" --rpc-url https://eth.llamarpc.com

# Check if owner is EOA or contract
OWNER=$(cast call 0xContractAddress "owner()(address)" --rpc-url https://eth.llamarpc.com)
cast code $OWNER --rpc-url https://eth.llamarpc.com

# If returns 0x, owner is EOA (higher risk)
# If returns bytecode, owner is contract (check if multisig)
```

### AccessControl Pattern

```bash
# Check admin role
cast call 0xContractAddress "getRoleAdmin(bytes32)(bytes32)" 0x0000000000000000000000000000000000000000000000000000000000000000 --rpc-url https://eth.llamarpc.com

# Check if address has admin role
cast call 0xContractAddress "hasRole(bytes32,address)(bool)" 0x0000000000000000000000000000000000000000000000000000000000000000 0xAddress --rpc-url https://eth.llamarpc.com

# Check role members
cast call 0xContractAddress "getRoleMemberCount(bytes32)(uint256)" 0x0000000000000000000000000000000000000000000000000000000000000000 --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "getRoleMember(bytes32,uint256)(address)" 0x0000000000000000000000000000000000000000000000000000000000000000 0 --rpc-url https://eth.llamarpc.com
```

### Pausable Pattern

```bash
# Check if contract is paused
cast call 0xContractAddress "paused()(bool)" --rpc-url https://eth.llamarpc.com

# Check pauser role
cast call 0xContractAddress "pauser()(address)" --rpc-url https://eth.llamarpc.com

# Check if address has pauser role
cast call 0xContractAddress "hasRole(bytes32,address)(bool)" 0x65d7a28e3265b37a6474929f336521b332cbe8169198e9a5a2fb157c6c5d5e5 0xAddress --rpc-url https://eth.llamarpc.com
```

### Admin Role Reference

| Role | Function | Risk if EOA | Risk if Multisig |
|------|----------|-------------|------------------|
| Owner | owner() | High | Low |
| Admin | getRoleAdmin() | High | Low |
| Pauser | paused() | Medium | Low |
| Minter | minter() | High | Low |
| Burner | burner() | Medium | Low |
| Upgrader | upgradeTo() | High | Low |

---

## Upgrade Mechanism Assessment

### Upgrade Function Analysis

```bash
# Check for upgrade functions
cast sig "upgradeTo(address)"
cast sig "upgradeToAndCall(address,bytes)"
cast sig "upgradeToAndCall(address,bytes,bool)"
cast sig "authorizeUpgrade(address)"

# Check if upgrade function is public
# Decompile and analyze
heimdall decompile 0xContractAddress --rpc-url https://eth.llamarpc.com

# Check for upgrade events
cast sig-event "Upgraded(address)"
cast sig-event "Upgrade(address,address)"
```

### Upgrade Risk Assessment

```bash
# Risk factors:
# - Upgrade function is public: Critical risk
# - Upgrade function is protected by owner: Medium risk
# - Upgrade function is protected by multisig: Low risk
# - Upgrade function is protected by timelock: Low risk
# - Upgrade function is protected by governance: Low risk
# - No upgrade mechanism: Low risk
# - Upgrade function has no access control: Critical risk
# - Upgrade function can be called by anyone: Critical risk
```

### Upgrade History

```bash
# Get upgrade events
curl -s "https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=0&toBlock=latest&address=0xContractAddress&topic0=0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b" | jq .

# Analyze upgrade history
# - Frequency of upgrades
# - Time between upgrades
# - Who triggered upgrades
# - What was upgraded
```

---

## Known Protocol Identification

### Protocol Detection

```bash
# Check for Uniswap
cast call 0xContractAddress "factory()(address)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "WETH()(address)" --rpc-url https://eth.llamarpc.com

# Check for Aave
cast call 0xContractAddress "POOL()(address)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "ADDRESSES_PROVIDER()(address)" --rpc-url https://eth.llamarpc.com

# Check for Compound
cast call 0xContractAddress "comptroller()(address)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "underlying()(address)" --rpc-url https://eth.llamarpc.com

# Check for MakerDAO
cast call 0xContractAddress "vat()(address)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "gem()(address)" --rpc-url https://eth.llamarpc.com

# Check for Curve
cast call 0xContractAddress "coins(uint256)(address)" 0 --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "A()(uint256)" --rpc-url https://eth.llamarpc.com
```

### Protocol Version Detection

```bash
# Check for version functions
cast call 0xContractAddress "version()(uint256)" --rpc-url https://eth.llamarpc.com
cast call 0xContractAddress "VERSION()(string)" --rpc-url https://eth.llamarpc.com

# Check for protocol-specific version indicators
# Uniswap V2: factory() returns address
# Uniswap V3: factory() returns address, but different interface
# Aave V2: POOL() returns address
# Aave V3: POOL() returns address, but different interface
```

### Protocol Reference

| Protocol | Chain | Detection Method | TVL |
|----------|-------|-----------------|-----|
| Uniswap | Ethereum | factory(), WETH() | $4B+ |
| Aave | Ethereum | POOL(), ADDRESSES_PROVIDER() | $10B+ |
| Compound | Ethereum | comptroller(), underlying() | $2B+ |
| MakerDAO | Ethereum | vat(), gem() | $5B+ |
| Curve | Ethereum | coins(), A() | $3B+ |
| Balancer | Ethereum | vault(), getPool() | $1B+ |
| Yearn | Ethereum | vault(), want() | $500M+ |
| Lido | Ethereum | stETH(), getSharesByPooledEth() | $15B+ |
| Rocket Pool | Ethereum | rocketDepositPool(), rocketTokenRETH() | $1B+ |

---

## TVL & Activity Assessment

### TVL Assessment

```bash
# Get contract balance
cast balance 0xContractAddress --rpc-url https://eth.llamarpc.com

# Get token balances
curl -s "https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=0xTokenAddress&address=0xContractAddress&tag=latest" | jq .

# Get TVL from DeFiLlama
curl -s "https://api.llama.fi/tvls/0xContractAddress" | jq .

# Get TVL from DefiPulse
curl -s "https://api.defipulse.com/v1/protocols" | jq '.[] | select(.name == "example")'
```

### Activity Assessment

```bash
# Get transaction count
cast nonce 0xContractAddress --rpc-url https://eth.llamarpc.com

# Get recent transactions
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=100&sort=desc" | jq .

# Get unique users
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '[.result[].from] | unique | length'

# Get activity over time
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0xContractAddress&startblock=0&endblock=99999999&page=1&offset=1000&sort=asc" | jq '.result[] | .timeStamp | tonumber | strftime("%Y-%m")' | sort | uniq -c
```

### Activity Metrics

| Metric | Low | Medium | High |
|--------|-----|--------|------|
| Daily transactions | < 10 | 10-100 | > 100 |
| Unique users | < 5 | 5-50 | > 50 |
| TVL | < $1M | $1M-$10M | > $10M |
| Contract age | < 30 days | 30-365 days | > 365 days |
| Upgrade frequency | < 1/month | 1-4/month | > 4/month |
