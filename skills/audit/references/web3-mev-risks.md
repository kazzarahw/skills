# MEV Risk Assessment

Comprehensive guide for assessing Maximal Extractable Value (MEV) risks in DeFi protocols, covering detection, measurement, and mitigation strategies.

---

## Table of Contents

- [Sandwich Attacks](#sandwich-attacks)
  - [Description](#description)
  - [Detection](#detection)
  - [Measurement](#measurement)
  - [Mitigation](#mitigation)
- [Backrunning](#backrunning)
  - [Description](#description-1)
  - [Detection](#detection-1)
  - [Mitigation](#mitigation-1)
- [Arbitrage Extraction](#arbitrage-extraction)
  - [Description](#description-2)
  - [Types](#types)
  - [Mitigation](#mitigation-2)
- [Liquidation MEV](#liquidation-mev)
  - [Description](#description-3)
  - [Detection](#detection-2)
  - [Mitigation](#mitigation-3)
- [Priority Gas Auctions](#priority-gas-auctions)
  - [Description](#description-4)
  - [Detection](#detection-3)
  - [Mitigation](#mitigation-4)
- [Validator Front-Running](#validator-front-running)
  - [Description](#description-5)
  - [Detection](#detection-4)
  - [Mitigation](#mitigation-5)
- [Mitigation Patterns](#mitigation-patterns)
  - [Flashbots](#flashbots)
  - [Slippage Protection](#slippage-protection)
  - [Batch Auctions](#batch-auctions)
  - [MEV-Boost](#mev-boost)
  - [Intent-Based](#intent-based)
- [MEV Risk Assessment Checklist](#mev-risk-assessment-checklist)
  - [Detection](#detection-5)
  - [Measurement](#measurement-1)
  - [Mitigation](#mitigation-6)
  - [Monitoring](#monitoring)

---

## Sandwich Attacks

### Description

A sandwich attack occurs when an attacker places a transaction before and after a victim's transaction, profiting from the price movement caused by the victim's trade.

```
Block N:
  1. Attacker buys (front-run)
  2. Victim buys (price increases)
  3. Attacker sells (back-run, profit)
```

### Detection

```solidity
// Detection: Monitor for suspicious patterns
// - Large trades followed by immediate reversal
// - Same address on both sides of trade
// - Consistent profit pattern

// Example detection logic
mapping(address => uint256) public lastTradeBlock;
mapping(address => bool) public isAttacker;

function detectSandwich(address user, uint256 amount) internal {
    if (lastTradeBlock[user] == block.number - 1) {
        // Potential sandwich pattern
        emit SuspiciousActivity(user, amount, block.number);
    }
    lastTradeBlock[user] = block.number;
}
```

### Measurement

```python
# Python script to measure sandwich attacks
def measure_sandwich_impact(trades):
    """
    Calculate sandwich attack impact from trade data.
    
    Args:
        trades: List of trade records with timestamp, address, amount, price
    
    Returns:
        Dictionary with sandwich metrics
    """
    sandwich_count = 0
    total_impact = 0
    
    for i in range(1, len(trades) - 1):
        prev_trade = trades[i - 1]
        curr_trade = trades[i]
        next_trade = trades[i + 1]
        
        # Check for sandwich pattern
        if (prev_trade['address'] == next_trade['address'] and
            prev_trade['timestamp'] == curr_trade['timestamp'] - 1 and
            next_trade['timestamp'] == curr_trade['timestamp'] + 1):
            
            sandwich_count += 1
            impact = (next_trade['price'] - prev_trade['price']) * curr_trade['amount']
            total_impact += impact
    
    return {
        'sandwich_count': sandwich_count,
        'total_impact': total_impact,
        'average_impact': total_impact / sandwich_count if sandwich_count > 0 else 0
    }
```

### Mitigation

```solidity
// SECURE: Slippage protection
function swap(uint256 amountIn, uint256 minAmountOut) external {
    uint256 amountOut = getAmountOut(amountIn);
    require(amountOut >= minAmountOut, "Slippage too high");
    // Execute swap
}

// SECURE: Batch auctions
function batchAuction(Trade[] memory trades) external {
    // Clear all trades at same price
    // Prevents sandwich attacks
}

// SECURE: Commit-reveal scheme
function commit(bytes32 hash) external {
    commitments[msg.sender] = hash;
}

function reveal(uint256 amount, bytes32 salt) external {
    require(keccak256(abi.encodePacked(amount, salt)) == commitments[msg.sender]);
    // Execute trade
}
```

---

## Backrunning

### Description

Backrunning occurs when an attacker places a transaction immediately after a target transaction, profiting from the state change caused by the target.

```
Block N:
  1. Target transaction (e.g., oracle update)
  2. Attacker transaction (back-run, profit)
```

### Detection

```solidity
// Detection: Monitor for backrunning patterns
// - Transactions immediately after oracle updates
// - Consistent profit from state changes
// - Gas price spikes

mapping(uint256 => bool) public oracleUpdated;
mapping(address => uint256) public backrunCount;

function detectBackrun(address user) internal {
    if (oracleUpdated[block.number - 1]) {
        backrunCount[user]++;
        if (backrunCount[user] > THRESHOLD) {
            emit SuspiciousActivity(user, backrunCount[user]);
        }
    }
}
```

### Mitigation

```solidity
// SECURE: Oracle update delay
uint256 public constant ORACLE_DELAY = 1 hours;

function updateOracle(uint256 newPrice) external onlyOracle {
    pendingPrice = newPrice;
    oracleUpdateTime = block.timestamp;
}

function executeTrade() external {
    require(block.timestamp >= oracleUpdateTime + ORACLE_DELAY, "Oracle delay");
    // Use pendingPrice
}

// SECURE: Batch oracle updates
function updateOracleBatch(uint256[] memory prices) external onlyOracle {
    // Update multiple oracles in single transaction
    // Prevents backrunning
}
```

---

## Arbitrage Extraction

### Description

Arbitrage extraction occurs when an attacker exploits price differences between DEXs or within a single DEX.

### Types

#### Cross-DEX Arbitrage
```
DEX A: ETH/USDC = 2000
DEX B: ETH/USDC = 2010

Attacker:
1. Buy ETH on DEX A with USDC
2. Sell ETH on DEX B for USDC
3. Profit: 10 USDC per ETH
```

#### Triangular Arbitrage
```
ETH/USDC = 2000
ETH/BTC = 0.05
BTC/USDC = 41000

Implied: ETH/USDC = 0.05 * 41000 = 2050

Attacker:
1. Buy ETH with USDC at 2000
2. Sell ETH for BTC at 0.05
3. Sell BTC for USDC at 41000
4. Profit: 50 USDC per ETH
```

#### Flash Loan Arbitrage
```
1. Take flash loan of 1000 USDC
2. Buy ETH on DEX A at 2000 (get 0.5 ETH)
3. Sell ETH on DEX B at 2010 (get 1005 USDC)
4. Repay flash loan (1000 USDC + fee)
5. Profit: ~5 USDC
```

### Mitigation

```solidity
// SECURE: Use TWAP for pricing
function getPrice() public view returns (uint256) {
    uint256[] memory prices = new uint256[](30);
    for (uint i = 0; i < 30; i++) {
        prices[i] = oracle.getPrice(block.timestamp - i * 12);
    }
    return median(prices);
}

// SECURE: Slippage protection
function swap(uint256 amountIn, uint256 minAmountOut) external {
    uint256 amountOut = getAmountOut(amountIn);
    require(amountOut >= minAmountOut, "Slippage too high");
    // Execute swap
}
```

---

## Liquidation MEV

### Description

Liquidation MEV occurs when attackers compete to liquidate undercollateralized positions, often leading to gas price spikes and cascading liquidations.

### Detection

```solidity
// Detection: Monitor for liquidation patterns
// - Multiple liquidations in same block
// - Gas price spikes
// - Cascading liquidations

mapping(uint256 => uint256) public liquidationsPerBlock;
mapping(address => uint256) public liquidationCount;

function detectLiquidationCascade() internal {
    liquidationsPerBlock[block.number]++;
    if (liquidationsPerBlock[block.number] > MAX_LIQUIDATIONS_PER_BLOCK) {
        emit LiquidationCascade(block.number, liquidationsPerBlock[block.number]);
    }
}
```

### Mitigation

```solidity
// SECURE: Liquidation batching
function liquidateBatch(address[] memory users) external {
    // Process liquidations in batches
    // Prevents cascading liquidations
}

// SECURE: Liquidation incentive
function liquidate(address user) external {
    uint256 debt = getDebt(user);
    uint256 collateral = getCollateral(user);
    uint256 bonus = collateral * 5 / 100; // 5% bonus
    transferCollateral(msg.sender, collateral + bonus);
    repayDebt(debt);
}

// SECURE: Position size limits
uint256 public constant MAX_POSITION_SIZE = 1000000 * 1e18; // $1M

function openPosition(address token, uint256 size) external {
    require(size <= MAX_POSITION_SIZE, "Position too large");
    // Open position
}
```

---

## Priority Gas Auctions

### Description

Priority Gas Auctions (PGAs) occur when attackers bid high gas prices to have their transactions included before others, leading to gas wars.

### Detection

```solidity
// Detection: Monitor for gas price spikes
// - Sudden increase in gas prices
// - Failed transactions due to gas wars
// - MEV-Boost relay usage

uint256 public averageGasPrice;
uint256 public gasPriceSpikeThreshold = 2e9; // 2 Gwei

function detectGasSpike() internal {
    if (tx.gasprice > averageGasPrice * gasPriceSpikeThreshold) {
        emit GasPriceSpike(tx.gasprice, averageGasPrice);
    }
    // Update average
    averageGasPrice = (averageGasPrice * 99 + tx.gasprice) / 100;
}
```

### Mitigation

```solidity
// SECURE: Use Flashbots
// Submit transactions directly to miners/validators
// Prevents gas wars

// SECURE: Batch auctions
function batchAuction(Trade[] memory trades) external {
    // Clear all trades at same price
    // Prevents PGAs
}

// SECURE: Commit-reveal scheme
function commit(bytes32 hash) external {
    commitments[msg.sender] = hash;
}

function reveal(uint256 amount, bytes32 salt) external {
    require(keccak256(abi.encodePacked(amount, salt)) == commitments[msg.sender]);
    // Execute trade
}
```

---

## Validator Front-Running

### Description

Validator front-running occurs when validators reorder transactions to extract MEV, including reordering and censorship.

### Detection

```solidity
// Detection: Monitor for validator reordering
// - Transaction order changes
// - Censorship patterns
// - Validator profit from reordering

mapping(address => uint256) public validatorProfit;
mapping(address => uint256) public validatorReorders;

function detectValidatorFrontRun(address validator) internal {
    if (validatorProfit[validator] > THRESHOLD) {
        emit ValidatorFrontRun(validator, validatorProfit[validator]);
    }
}
```

### Mitigation

```solidity
// SECURE: Use MEV-Boost
// Distribute block building to multiple builders
// Prevents single validator front-running

// SECURE: Encrypted mempool
// Encrypt transactions until included
// Prevents front-running

// SECURE: Fair ordering
// Use fair ordering protocols
// Prevents reordering
```

---

## Mitigation Patterns

### Flashbots

```solidity
// Use Flashbots to submit transactions directly to miners
// Prevents front-running and gas wars

// Example: Flashbots bundle
// {
//   "jsonrpc": "2.0",
//   "method": "eth_sendBundle",
//   "params": [{
//     "txs": ["0x...", "0x..."],
//     "blockNumber": "0x...",
//     "minTimestamp": 0,
//     "maxTimestamp": 0
//   }]
// }
```

### Slippage Protection

```solidity
// SECURE: Slippage protection
function swap(uint256 amountIn, uint256 minAmountOut) external {
    uint256 amountOut = getAmountOut(amountIn);
    require(amountOut >= minAmountOut, "Slippage too high");
    // Execute swap
}
```

### Batch Auctions

```solidity
// SECURE: Batch auctions
function batchAuction(Trade[] memory trades) external {
    // Clear all trades at same price
    // Prevents sandwich attacks and PGAs
}
```

### MEV-Boost

```solidity
// SECURE: MEV-Boost
// Distribute block building to multiple builders
// Prevents single validator front-running

// Use MEV-Boost relay
// - Connect to multiple relays
// - Use fair ordering
// - Prevent censorship
```

### Intent-Based

```solidity
// SECURE: Intent-based architecture
// Users submit intents, not transactions
// Solvers compete to fulfill intents
// Prevents front-running

function submitIntent(Intent memory intent) external {
    intents[msg.sender] = intent;
}

function fulfillIntent(address user, bytes memory solution) external onlySolver {
    // Fulfill user intent
    // Prevents front-running
}
```

---

## MEV Risk Assessment Checklist

### Detection
- [ ] Sandwich attack detection
- [ ] Backrunning detection
- [ ] Arbitrage extraction monitoring
- [ ] Liquidation MEV detection
- [ ] Gas price spike detection
- [ ] Validator front-running detection

### Measurement
- [ ] Sandwich attack impact measured
- [ ] Backrunning profit measured
- [ ] Arbitrage extraction measured
- [ ] Liquidation MEV measured
- [ ] Gas war impact measured
- [ ] Validator front-running measured

### Mitigation
- [ ] Slippage protection implemented
- [ ] Batch auctions implemented
- [ ] Commit-reveal scheme implemented
- [ ] Flashbots integration
- [ ] MEV-Boost integration
- [ ] Intent-based architecture

### Monitoring
- [ ] Real-time MEV monitoring
- [ ] Alert thresholds configured
- [ ] Incident response plan
- [ ] Insurance fund for MEV losses
