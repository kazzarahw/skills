# MEV Patterns Reference

Detailed MEV extraction patterns with detection and mitigation guidance.

## Sandwich Attacks

### Mechanism

1. **Frontrun:** Attacker buys token X before victim, moving price up
2. **Victim:** Victim buys token X at inflated price (receives less than expected)
3. **Backrun:** Attacker sells token X after victim, capturing price difference

The attacker profits from the price impact of the victim's own transaction. The victim receives worse execution than the pre-attack market price.

### Step-by-Step

```
Block N:
  Tx 1 (Attacker): Buy 100 ETH of TokenX  → Price moves from 1.00 to 1.05
  Tx 2 (Victim):   Buy 50 ETH of TokenX   → Receives less than expected at 1.05
  Tx 3 (Attacker): Sell 100 ETH of TokenX → Price returns to ~1.00, profit = 5 ETH
```

### Detection

- **Same-block correlation:** Frontrun and backrun txs in same block as victim
- **Builder correlation:** All three txs built by same block builder
- **Token flow analysis:** Attacker address buys before, sells after, net positive
- **Price deviation:** Victim execution price significantly worse than pre-block market price
- **Profit consistency:** Attacker address consistently profitable on similar patterns

### Mitigation

- **Slippage protection:** Minimum output amount prevents worst-case slippage
- **Private mempool:** Flashbots Protect prevents mempool visibility
- **Batch auctions:** Uniform clearing price eliminates ordering advantage
- **TWAP oracles:** Time-weighted prices reduce single-block manipulation

## Backrunning

### Mechanism

1. **Target transaction:** Creates a state change (oracle update, large swap, governance action)
2. **Backrun transaction:** Exploits the state change for profit

Unlike sandwiching, backrunning does not require a frontrun. The attacker profits from the target's state change without harming the target.

### Common Patterns

**Oracle backrunning:**
```
Target: Oracle updates TokenX price from 1.00 to 1.05
Backrun: Buy TokenX on other DEX at 1.00, sell on updated DEX at 1.05
```

**Liquidation backrunning:**
```
Target: Large price drop triggers liquidation threshold
Backrun: Liquidate undercollateralized position, capture bonus
```

**Governance backrunning:**
```
Target: Governance proposal creates arbitrage opportunity
Backrun: Execute arbitrage before market adjusts
```

### Detection

- **Same-block or next-block execution:** Backrun tx immediately follows target
- **State dependency:** Backrun tx reads state written by target tx
- **No frontrun component:** Only backrun, no preceding transaction from same address
- **Consistent timing:** Attacker address consistently follows specific tx types

### Mitigation

- **Commit-reveal schemes:** Hide transaction contents until inclusion
- **Batch auctions:** Eliminate ordering advantage
- **Oracle update delays:** Time delay between oracle update and availability
- **Access restrictions:** Limit who can act on state changes

## Arbitrage Extraction

### Mechanism

Exploiting price differences between venues within a single block. Arbitrage is generally benign — it improves price alignment — but can be harmful when combined with other MEV strategies.

### Patterns

**Cross-DEX arbitrage:**
```
TokenX price on Uniswap: 1.00
TokenX price on SushiSwap: 1.05
Arbitrage: Buy on Uniswap, sell on SushiSwap, profit = 0.05 per unit
```

**Triangular arbitrage:**
```
ETH/USDC: 2000
USDC/DAI: 1.00
DAI/ETH: 0.00048
Path: ETH → USDC → DAI → ETH, profit = 0.04 ETH per cycle
```

**Flash loan arbitrage:**
```
Flash borrow 1000 ETH
Buy TokenX on Uniswap (moves price to 1.05)
Sell TokenX on SushiSwap (price still 1.00)
Repay flash loan + fee
Profit = price difference - flash loan fee - gas
```

### Detection

- **Circular token flows:** Transaction starts and ends with same token
- **Multiple DEX interactions:** Single tx touches multiple DEXs
- **Net positive:** Attacker ends with more of starting token than started
- **No victim:** No other user harmed by the transaction

### Mitigation

- **Arbitrage is benign:** Generally should not be mitigated
- **Protocol-level arbitrage:** If protocol loses revenue, adjust fee structure
- **Flash loan fees:** Ensure flash loan fees exceed arbitrage profit for harmful cases

## Liquidation MEV

### Mechanism

Competing to liquidate undercollateralized lending positions. Liquidators earn a bonus (typically 5-15%) for liquidating bad debt. High competition leads to gas wars and priority fee spikes.

### Patterns

**Standard liquidation:**
```
Position health factor drops below 1.0
Liquidator repays debt, receives collateral + bonus
Liquidator sells collateral for profit
```

**Cascading liquidation:**
```
Market crash → many positions undercollateralized
Liquidators compete for gas priority
Gas prices spike → some liquidations fail
Protocol accumulates bad debt
```

**Liquidation front-running:**
```
Attacker monitors mempool for liquidation txs
Frontruns with higher gas to liquidate first
Captures liquidation bonus
```

### Detection

- **Gas price spikes:** Priority fees significantly above base fee during volatility
- **Failed liquidations:** Transactions that fail due to gas competition
- **Liquidation clustering:** Multiple liquidations in same block from different addresses
- **Bad debt accumulation:** Protocol bad debt increases during volatility

### Mitigation

- **Liquidation optimization:** Use flash loans to reduce capital requirement
- **Dynamic liquidation bonus:** Adjust bonus based on competition
- **Liquidation throttling:** Limit liquidations per block to reduce gas wars
- **Private liquidation:** Route liquidations through private mempool

## Priority Gas Auctions

### Mechanism

Searchers compete for transaction inclusion by bidding increasingly high gas prices. The highest bidder wins inclusion, but all bidders pay gas on failed transactions.

### Dynamics

```
Searcher A: gas price 100 gwei
Searcher B: gas price 150 gwei (outbids A)
Searcher C: gas price 200 gwei (outbids B)
Result: C wins, A and B lose gas on failed transactions
```

### Detection

- **Gas price distribution:** Bimodal distribution with spike at priority fee level
- **Failed transaction rate:** High rate of failed transactions from gas competition
- **Priority fee variance:** High variance in priority fees for similar transactions
- **Block builder profit:** Builders extract priority fees from competing searchers

### Mitigation

- **EIP-1559 base fee:** Reduces gas price volatility
- **Private mempool:** Reduces competition visibility
- **Batch auctions:** Eliminates gas competition
- **Intent-based execution:** Solvers compete on price, not gas

## Validator Front-Running

### Mechanism

Block proposers reorder, insert, or censor transactions for profit. This is a consensus-layer threat that can lead to censorship and centralization.

### Patterns

**Proposer reordering:**
```
Block contains: [Victim buy, Attacker buy, Attacker sell]
Proposer reorders to: [Attacker buy, Victacker sell, Victim buy]
Attacker profits from victim's price impact
```

**Transaction censorship:**
```
Proposer excludes specific transactions from block
Target transaction delayed or never included
Used for censorship or to extract MEV later
```

**Proposer-builder collusion:**
```
Builder offers block with MEV extraction
Proposer accepts block, shares MEV profit
Both profit at expense of users
```

### Detection

- **Validator-specific patterns:** Specific validators consistently extract MEV
- **Transaction reordering:** Transactions reordered within blocks by specific validators
- **Censorship patterns:** Specific transaction types excluded by specific validators
- **MEV-Boost relay correlation:** Blocks from specific relays show MEV patterns

### Mitigation

- **Proposer-builder separation (PBS):** Builders produce blocks, validators select
- **MEV-Boost:** Competitive block building market
- **Encrypted mempool:** Hide transaction contents until inclusion
- **Proposer rotation:** Frequent validator rotation reduces individual impact
- **Slashing conditions:** Penalize validators for censorship or reordering

## Cross-Chain MEV

### Mechanism

MEV extraction that spans multiple chains, including cross-chain arbitrage, bridge MEV, and shared sequencer MEV.

### Patterns

**Cross-chain arbitrage:**
```
TokenX price on Ethereum: 1.00
TokenX price on Arbitrum: 1.05
Bridge TokenX from Ethereum to Arbitrum
Sell on Arbitrum for profit
```

**Bridge MEV:**
```
Bridge transaction creates price discrepancy
Attacker backruns bridge on destination chain
Profits from price difference
```

**Shared sequencer MEV:**
```
Shared sequencer orders transactions across chains
Attacker observes cross-chain state
Extracts MEV from cross-chain arbitrage
```

### Detection

- **Cross-chain correlation:** Related transactions on multiple chains in same time window
- **Bridge transaction analysis:** Bridge txs followed by arbitrage on destination chain
- **Shared sequencer analysis:** Transaction ordering across chains by shared sequencer

### Mitigation

- **Cross-chain batch auctions:** Uniform clearing price across chains
- **Intent-based cross-chain:** Solvers compete for cross-chain execution
- **Shared sequencer PBS:** Proposer-builder separation for shared sequencer
