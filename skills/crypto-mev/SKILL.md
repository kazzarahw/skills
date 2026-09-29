---
name: crypto-mev
description: Analyzes MEV (Maximal Extractable Value) risks and attack vectors. Use when assessing sandwich attacks, backrunning, arbitrage extraction, liquidation MEV, and priority gas auctions. Covers detection, measurement, and mitigation.
---

# Crypto MEV

MEV risk analysis skill. Identifies, measures, and mitigates Maximal Extractable Value exposure across DeFi protocols, bridges, and application chains.

## Constitutional Rules

1. **MEV is not inherently malicious.** MEV is a structural property of block production. Analysis focuses on harmful extraction (sandwiching, liquidation theft) and protocol-level mitigation, not on eliminating all MEV.
2. **Distinguish searcher MEV from validator MEV.** Searcher MEV (arbitrage, backrunning) is competitive and benign. Validator MEV (proposer reordering, censorship) is a consensus-layer threat. Never conflate the two.
3. **Measure before mitigating.** Quantify extracted value, frequency, and cost to users before recommending mitigations. Unquantified MEV claims are speculation.
4. **Sandwich detection requires mempool data.** On-chain post-hoc detection has false positives. Mempool monitoring or block-builder data is required for definitive sandwich identification.
5. **Mitigations have trade-offs.** Private mempool reduces sandwiching but introduces builder centralization. Batch auctions reduce MEV but increase latency. Always document trade-offs.
6. **Profitability determines risk.** A MEV vector with negative expected profit after gas is not an attack vector. Always compute net profit after costs.
7. **Cross-chain MEV is underexplored.** Cross-chain arbitrage, bridge MEV, and shared-sequencer MEV are emerging vectors. Include them in scope.

## MEV Analysis Process

### Phase 1: Identify

Map all MEV extraction surfaces in the target system.

1. **Transaction flow mapping** — Identify all state-changing transactions that alter prices, liquidation thresholds, or reward distributions
2. **Actor identification** — Determine who can observe and act on pending transactions (searchers, builders, validators, users)
3. **Value flow analysis** — Trace where extractable value originates (slippage, liquidation bonuses, arbitrage spreads, oracle updates)
4. **Ordering dependency assessment** — Identify transactions whose profitability depends on execution order relative to others

**Exit criteria:** Complete inventory of MEV surfaces with associated actors and value sources.

### Phase 2: Measure

Quantify the extractable value for each identified surface.

1. **Historical extraction analysis** — Measure past MEV extraction using block data, mempool archives, or MEV-Explore datasets
2. **Theoretical maximum calculation** — Compute upper bound of extractable value given liquidity depth and slippage parameters
3. **Frequency assessment** — Determine how often each MEV opportunity arises (per block, per day, per event)
4. **Competition analysis** — Assess how many searchers compete for the same opportunities (affects net extraction)

**Exit criteria:** Quantified MEV extraction per surface with frequency and competition data.

### Phase 3: Assess

Evaluate the impact of identified MEV on protocol health and users.

1. **User cost calculation** — Compute total cost to users from harmful MEV (sandwich slippation, liquidation theft)
2. **Protocol revenue impact** — Determine if MEV extraction reduces protocol revenue or LP returns
3. **Centralization risk** — Assess if MEV extraction leads to builder centralization or validator capture
4. **Cascading risk** — Evaluate if MEV extraction can trigger cascading liquidations or insolvency

**Exit criteria:** Impact assessment with user cost, protocol revenue, and centralization metrics.

### Phase 4: Mitigate

Recommend and implement appropriate mitigations based on assessment.

1. **Mitigation selection** — Choose mitigations based on MEV category and protocol architecture (see Mitigation Patterns)
2. **Trade-off analysis** — Document latency, cost, centralization, and UX trade-offs for each mitigation
3. **Implementation guidance** — Provide concrete implementation steps with code references
4. **Residual risk assessment** — Evaluate remaining MEV exposure after mitigation

**Exit criteria:** Mitigation plan with trade-offs documented and residual risk quantified.

## MEV Categories

### Sandwich Attacks

**Mechanism:** Attacker frontruns a victim buy (or sell) transaction, executes the victim's transaction which moves the price, then backruns to capture the price difference.

**Key indicators:**
- Buy transaction immediately before victim tx from same block builder
- Sell transaction immediately after victim tx from same block builder
- Victim tx receives worse execution price than expected
- Attacker profit ≈ victim slippage minus gas costs

**Capital requirement:** Moderate (must hold inventory through victim tx). Flash loans reduce capital requirement to gas cost.

### Backrunning

**Mechanism:** Attacker submits a transaction immediately after a target transaction to exploit the state change it creates.

**Key indicators:**
- Tx submitted within same block or next block after target
- Profits from state change created by target (arbitrage, liquidation, oracle update)
- No frontrun component (unlike sandwich)

**Common targets:** Oracle updates, large swaps creating price discrepancies, governance actions.

### Arbitrage Extraction

**Mechanism:** Exploiting price differences between DEXs or between DEX and CEX within a single block.

**Key indicators:**
- Multiple DEX swaps in single transaction or block
- Net token flow returns to original asset (circular trade)
- Profit from price discrepancy, not from victim transaction
- Benign — improves price alignment across venues

**Sub-types:** Cross-DEX arbitrage, triangular arbitrage, flash loan arbitrage.

### Liquidation MEV

**Mechanism:** Competing to liquidate undercollateralized positions to capture liquidation bonuses.

**Key indicators:**
- Liquidation transactions clustered around specific collateral factors
- Gas price spikes during market volatility
- Liquidation bonus captured by searchers rather than protocol
- Cascading liquidations during market crashes

**Risk:** If liquidation bonus < gas cost, positions go underliquidated, creating bad debt.

### Priority Gas Auctions

**Mechanism:** Gas bidding wars where searchers compete for transaction inclusion by offering increasingly high gas prices.

**Key indicators:**
- Gas prices significantly above base fee for specific transactions
- Failed transactions from gas estimation errors
- Searchers losing gas on failed transactions
- Block builders extracting priority fees from competing searchers

**Impact:** Increases effective gas cost for all users; failed transactions waste gas.

### Validator Front-Running

**Mechanism:** Block proposers reorder, insert, or censor transactions for profit.

**Key indicators:**
- Transactions reordered within blocks by specific validators
- Consistent patterns of specific validators extracting MEV
- Censorship of specific transaction types
- Proposer-builder separation (PBS) bypass

**Risk:** Consensus-layer threat. Can lead to censorship, liveness failures, and centralization.

## Detection Techniques

### Mempool Monitoring

Monitor pending transactions to identify MEV patterns before inclusion.

```python
# See scripts/sandwich-detector.py for full implementation
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"))

def monitor_mempool():
    """Subscribe to pending transactions and detect sandwich patterns."""
    # Filter for DEX swap transactions
    # Group by token pair and block
    # Identify frontrun/backrun patterns
    pass
```

### Block Analysis

Post-hoc analysis of block data to identify MEV extraction.

1. **Same-block analysis** — Identify transactions in same block with correlated token flows
2. **Builder identification** — Map blocks to builders to identify builder-specific MEV strategies
3. **Profit tracing** — Trace token flows to identify MEV profit addresses
4. **Frequency analysis** — Identify addresses that consistently extract MEV

### Price Impact Analysis

Calculate expected vs. actual execution price to detect sandwich attacks.

```python
def calculate_price_impact(input_amount, reserve_in, reserve_out):
    """Calculate constant product AMM price impact."""
    return (input_amount * reserve_out) / (reserve_in + input_amount)

def detect_sandwich(victim_tx, frontrun_tx, backrun_tx):
    """Detect sandwich by comparing expected and actual execution prices."""
    # Compare victim execution price to pre-frontrun market price
    # If deviation exceeds threshold, flag as sandwich
    pass
```

## Mitigation Patterns

### Flashbots / Private Mempool

**Use when:** Sandwich attacks are the primary MEV risk.

**Mechanism:** Submit transactions directly to block builders, bypassing public mempool.

**Trade-offs:**
- Reduces sandwich attacks significantly
- Introduces builder centralization (builder knows tx contents)
- Requires trust in builder not to reorder
- Adds latency (builder inclusion delay)

**Implementation:** Flashbots Protect RPC, MEV-Boost relays, private transaction pools.

### Slippage Protection

**Use when:** Protocol users are vulnerable to sandwich-induced slippage.

**Mechanism:** Enforce maximum slippage on all swaps and trades.

**Trade-offs:**
- Protects users from worst-case slippage
- Does not prevent MEV extraction (attacker still profits)
- Can cause transaction failures during volatility
- Adds complexity to transaction flow

**Implementation:** Minimum output amount parameters, slippage oracles, dynamic slippage based on volatility.

### Batch Auctions

**Use when:** Protocol can tolerate increased latency for MEV elimination.

**Mechanism:** Collect orders over a time window and execute at uniform clearing price.

**Trade-offs:**
- Eliminates MEV entirely (no ordering advantage)
- Increases latency (wait for batch window)
- Requires liquidity provision during batch period
- Complex implementation

**Implementation:** CoW Swap (batch auctions with solver competition), UniswapX (Dutch auction with filler competition).

### MEV-Boost / PBS

**Use when:** Validator MEV extraction is the primary concern.

**Mechanism:** Separate block building from block proposal. Builders compete to produce blocks; validators select highest-paying block.

**Trade-offs:**
- Reduces validator MEV extraction
- Introduces builder centralization
- Relays become trust assumptions
- Does not reduce searcher MEV

**Implementation:** MEV-Boost, proposer-builder separation protocols.

### Intent-Based Architectures

**Use when:** Protocol can delegate execution to competitive solvers.

**Mechanism:** Users submit intents (desired outcome) rather than transactions. Solvers compete to fulfill intents optimally.

**Trade-offs:**
- Eliminates MEV (no transaction ordering to exploit)
- Requires solver competition to be robust
- Adds latency (solver competition period)
- Complex implementation

**Implementation:** UniswapX, CoW Swap, Anoma, SUAVE.

## Cross-References

| Skill | When to Use |
|-------|-------------|
| **cyber-recon** | Traditional reconnaissance methodology for infrastructure mapping |
| **cyber-exploit** | Exploitation methodology for MEV attack development |
| **cyber-verify** | Verification discipline for confirming MEV exploitability |
| **cyber-coach** | Course correction when analysis stalls |
| **cyber-report** | Reporting format for MEV analysis findings |
| **crypto-recon** | Blockchain reconnaissance for on-chain MEV activity |
| **crypto-audit** | Smart contract audit for MEV-related vulnerabilities |
| **crypto-defi** | DeFi protocol analysis for protocol-specific MEV risks |
| **crypto-exploit** | Exploit development for MEV attack execution |
| **crypto-forensics** | Post-incident investigation of MEV extraction |
| **crypto-bridge** | Cross-chain bridge MEV analysis |

**Workflow:** `crypto-recon` → `crypto-mev` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

- **MEV is not just profit.** MEV extraction can cause cascading liquidations, insolvency, and consensus instability. Always assess systemic impact.
- **Salmonella attacks are a variant.** Attackers use token transfer fees or rebasing to extract value from sandwich victims beyond slippage. Check for fee-on-transfer and rebasing tokens.
- **Sandwich detection has false positives.** Large trades naturally move prices. Require same-block-builder correlation for definitive identification.
- **MEV-Boost does not reduce searcher MEV.** PBS only addresses validator MEV. Searcher MEV (arbitrage, backrunning) continues unchanged.
- **Private mempool is not fully private.** Builders can still front-run. Trust assumptions shift from public mempool to builder.
- **Batch auctions require solver competition.** A single solver can extract MEV within the batch. Ensure multiple independent solvers.
- **Cross-chain MEV is underexplored.** Bridge transactions, shared sequencers, and cross-chain arbitrage create MEV vectors that span multiple chains.
- **MEV extraction is competitive.** High MEV opportunities attract more searchers, reducing individual profit. Net extraction may be lower than theoretical maximum.
- **Gas estimation fails under MEV competition.** Searchers overestimate gas to win priority, causing failed transactions that waste gas.
- **MEV-Boost relay centralization is a risk.** A few relays dominate block building. Relay failure or censorship threatens liveness.

## Output Format

```markdown
# MEV Analysis Report: [Protocol Name]

## Executive Summary
- Overall MEV Risk: [Low/Medium/High/Critical]
- Total MEV Extracted (30d): $[amount]
- Primary MEV Category: [Sandwich/Backrunning/Arbitrage/Liquidation/PGA/Validator]
- User Cost (30d): $[amount]

## MEV Surface Inventory
| Surface | Category | Frequency | Estimated Value | Competition |
|---------|----------|-----------|-----------------|-------------|
| [Surface 1] | [Category] | [per day] | $[amount] | [Low/Med/High] |

## Sandwich Attack Analysis
- Sandwiches Detected (30d): N
- Average Victim Slippage: X%
- Total User Cost: $[amount]
- Top Attacker Addresses: [list]

## Mitigation Assessment
| Mitigation | Effectiveness | Trade-offs | Recommendation |
|------------|--------------|------------|----------------|
| [Mitigation] | [High/Med/Low] | [Trade-offs] | [Adopt/Consider/Reject] |

## Residual Risk
- Post-Mitigation MEV Risk: [Low/Medium/High]
- Remaining Vulnerabilities: [list]

## Recommendations
1. [Highest priority mitigation]
2. [Next priority]
3. [Continue...]
```

## Quick Start

1. Run sandwich detector: `python3 scripts/sandwich-detector.py --rpc-url $RPC_URL --blocks 1000`
2. Review `references/mev-patterns.md` for detailed attack patterns
3. Follow MEV Analysis Process (Identify → Measure → Assess → Mitigate)
4. Write report using Output Format above
