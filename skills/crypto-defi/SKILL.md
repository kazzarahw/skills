---
name: crypto-defi
description: Analyzes DeFi protocol security. Use when auditing AMMs, lending protocols, yield aggregators, stablecoins, or bridges. Covers oracle security, flash loan risks, governance attacks, and economic attack vectors.
---

# DeFi Protocol Security Analysis

## Constitutional Rules

1. **Never trust oracle prices without manipulation resistance analysis.** Every oracle dependency must be evaluated for price manipulation risk before any other assessment.
2. **Flash loan risk is always present.** Assume any protocol accepting on-chain price inputs is flash loan attackable until proven otherwise.
3. **Economic attack surface must be mapped before technical review.** Incentive misalignments cause more losses than code bugs.
4. **Composability is a liability, not just a feature.** Every external contract dependency introduces cascade risk that must be documented.
5. **Governance mechanisms are attack surfaces.** Voting power acquisition, proposal manipulation, and timelock bypass must be assessed.
6. **Bridge protocols require the highest scrutiny.** Bridge exploits account for the largest losses in DeFi history; validator sets, signature schemes, and message verification must be exhaustively reviewed.
7. **All findings must include exploitability assessment.** A vulnerability without a concrete exploit path is a theoretical risk, not a finding.

## Protocol Analysis Process

### Phase 1: Protocol Architecture Review

Map the protocol's contract architecture before any security analysis:

1. **Contract inventory** — Identify all contracts, their roles, and ownership
2. **Access control mapping** — Document who can call what, when, and with what constraints
3. **External dependency graph** — Map all oracle, token, and protocol dependencies
4. **Upgrade mechanism review** — Assess proxy patterns, admin keys, and upgrade delays
5. **Fund flow analysis** — Trace how assets enter, move through, and exit the protocol

**Why:** Architecture flaws (missing access controls, upgrade risks) are the root cause of most major exploits.

### Phase 2: Oracle Dependency Analysis

Oracle manipulation is the #1 DeFi attack vector. For each oracle dependency:

1. **Oracle type classification** — Spot price, TWAP, chainlink, custom, or hybrid
2. **Manipulation cost estimation** — Calculate capital required to move the oracle
3. **Flash loan amplification** — Assess whether flash loans reduce manipulation cost
4. **Staleness and heartbeat analysis** — Evaluate update frequency and deviation thresholds
5. **Circuit breaker assessment** — Check for emergency shutdown mechanisms

**Default:** If a protocol uses spot prices from AMMs without TWAP or circuit breakers, flag as critical risk.

### Phase 3: Flash Loan Risk Assessment

Flash loans enable single-transaction attacks with no capital requirements:

1. **Identify flash loan providers** — Aave, Uniswap, Balancer, dYdX (discontinued)
2. **Map attack surfaces** — Governance voting, oracle manipulation, liquidation, arbitrage
3. **Assess atomicity requirements** — Can the attack be executed in a single transaction?
4. **Evaluate mitigation effectiveness** — Timelocks, TWAP, quantity limits, reentrancy guards

**Why:** Flash loan attacks require no upfront capital, making them accessible to any attacker.

### Phase 4: Governance Mechanism Review

Governance attacks combine flash loans with voting mechanisms:

1. **Voting power analysis** — Token-weighted, delegated, or quadratic
2. **Proposal threshold assessment** — Minimum tokens required to submit proposals
3. **Timelock evaluation** — Delay between proposal approval and execution
4. **Flash loan voting risk** — Can voting power be borrowed within a single transaction?
5. **Quorum and participation analysis** — Low participation enables governance capture

**Default:** If governance tokens can be flash loaned and there is no timelock, flag as critical risk.

### Phase 5: Economic Attack Surface Mapping

Economic attacks exploit incentive misalignments rather than code bugs:

1. **Inflation attack assessment** — Share/asset ratio manipulation via donation
2. **Donation attack evaluation** — Direct balance inflation to corrupt accounting
3. **Liquidation incentive analysis** — Are liquidators properly incentivized?
4. **Interest rate model review** — Can rates be manipulated for insolvency?
5. **Peg mechanism stability** — For stablecoins, assess de-peg recovery mechanisms

**Why:** Economic attacks are often overlooked because they don't involve code exploits.

### Phase 6: Composability Risk Analysis

DeFi protocols integrate with other protocols, creating cascade risks:

1. **Integration dependency mapping** — Which protocols does this protocol depend on?
2. **Cascade failure analysis** — If a dependency fails, what happens to this protocol?
3. **ERC-20 token risk** — Deflationary tokens, rebasing tokens, fee-on-transfer tokens
4. **Cross-protocol contagion** — Can a failure in one protocol cascade to others?

## Protocol Categories

### AMMs (Uniswap, Curve, Balancer)

**Key risks:** Price manipulation, slippage exploitation, LP token accounting errors, impermanent loss amplification.

**Focus areas:**
- Constant product formula manipulation
- Stablecoin pool manipulation, Curve invariant exploitation
- Weighted pool ratio manipulation
- LP token mint/burn accounting
- Fee-on-transfer token handling

### Lending (Aave, Compound, MakerDAO)

**Key risks:** Oracle manipulation, liquidation failures, interest rate model exploits, collateral token risks.

**Focus areas:**
- Oracle price feed manipulation
- Liquidation threshold and bonus analysis
- Interest rate model stability
- Collateral factor calibration
- Flash loan liquidation risk
- Governance token collateral risk

### Yield Aggregators (Yearn, Harvest)

**Key risks:** Inflation attacks, donation attacks, strategy manipulation, vault share accounting.

**Focus areas:**
- Share/asset ratio manipulation
- Strategy deposit/withdrawal logic
- Harvest timing manipulation
- Vault token decimal handling
- Reward token distribution

### Stablecoins (DAI, FRAX, USDC)

**Key risks:** Oracle failure, peg manipulation, flash mint exploits, collateral insolvency.

**Focus areas:**
- Oracle dependency for peg maintenance
- Collateral quality and diversification
- Peg stability mechanism (Peg Stability Module)
- Flash mint availability
- Blacklist/freeze functionality risk
- Off-chain collateral counterparty risk

### Bridges (Wormhole, Ronin, Nomad)

**Key risks:** Signature verification failures, message replay, validator compromise, message validation bugs.

**Focus areas:**
- Validator set security and decentralization
- Signature scheme (MPC, multisig, light client)
- Message replay prevention
- Liquidity pool solvency
- Upgrade mechanism security
- Guardian/relayer trust assumptions

**Why:** Bridge exploits account for the largest losses in DeFi history ($625M Ronin, $326M Wormhole, $190M Nomad).

### Perpetuals (dYdX, GMX, GNS)

**Key risks:** Oracle latency exploitation, funding rate manipulation, liquidation cascades, liquidity depth.

**Focus areas:**
- Oracle update frequency and latency
- Funding rate calculation manipulation
- Liquidation engine robustness
- Liquidity pool depth analysis
- Position size limits
- ADL (Auto-Deleveraging) fairness

### Liquid Staking (Lido, Rocket Pool)

**Key risks:** Oracle manipulation, validator slashing, derivative token depeg.

**Focus areas:**
- Oracle price feed for staking rewards
- Validator slashing conditions and impact
- stETH/rETH depeg risk and recovery
- Withdrawal queue management
- Node operator collusion

### Restaking (EigenLayer)

**Key risks:** Slashing cascade, operator collusion, AVS security.

**Focus areas:**
- Slashing conditions and cascade risk
- Operator set diversity and collusion
- AVS (Actively Validated Service) security
- Withdrawal delay and queue management
- Token incentive alignment

### Options (Lyra, Premia)

**Key risks:** Oracle manipulation, liquidation, premium calculation errors.

**Focus areas:**
- Oracle price feed for underlying assets
- Liquidation engine for undercollateralized positions
- Premium calculation and Greeks
- Exercise and settlement logic
- Liquidity provider risk

### RWA (Centrifuge, Maple)

**Key risks:** Oracle failure, collateral default, legal compliance.

**Focus areas:**
- Oracle price feeds for real-world assets
- Collateral quality and default risk
- Legal compliance and regulatory risk
- Custody and asset verification
- Loan origination and underwriting

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `cyber-recon` | Traditional reconnaissance methodology for protocol infrastructure |
| `cyber-exploit` | Exploitation methodology for proof-of-concept development |
| `cyber-verify` | Verification discipline for confirming vulnerability exploitability |
| `cyber-coach` | Course correction when analysis stalls |
| `crypto-recon` | Blockchain reconnaissance for on-chain activity analysis |
| `crypto-audit` | Smart contract audit for code-level vulnerability discovery |
| `crypto-exploit` | Web3 exploitation for on-chain attack execution |
| `crypto-forensics` | Post-incident investigation and fund tracing |

**Workflow:** `crypto-recon` → `crypto-audit` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

- **Oracle manipulation is the #1 DeFi attack vector.** More funds are lost to oracle manipulation than any other category. Always assess oracle security first.
- **Flash loan attacks are single-transaction.** No capital, no collateral, no credit check. If the attack fits in one transaction, it's free to attempt.
- **Governance attacks need flash loan + no timelock.** The combination of borrowable voting power and immediate execution is lethal.
- **Bridge exploits are the largest by far.** Ronin ($625M), Wormhole ($326M), Nomad ($190M) — bridges hold the most funds and have the most complex trust assumptions.
- **Inflation attacks target share/asset ratios.** Donating assets directly to a pool corrupts LP token accounting, allowing attackers to drain funds.
- **Donation attacks inflate balances directly.** By sending tokens directly to a contract (not via deposit), accounting can be corrupted.
- **TWAP manipulation requires sustained capital.** Unlike spot price manipulation, TWAP manipulation requires maintaining price over time, increasing cost.
- **Composability risks are often overlooked.** A protocol can be secure in isolation but vulnerable when integrated with other protocols.
- **Admin keys are a single point of failure.** Compromised admin keys can drain any protocol, regardless of code quality.
- **Upgrade mechanisms introduce risk.** Proxy patterns and admin-controlled upgrades can change protocol behavior at any time.

## Output Format

```markdown
# Protocol Security Report: [Protocol Name]

## Executive Summary
- Overall Risk Rating: [Critical/High/Medium/Low]
- Total Findings: [N] (Critical: N, High: N, Medium: N, Low: N)
- Primary Risk Category: [Oracle/Governance/Economic/Composability/Bridge]

## Protocol Architecture
- Contract Count: N
- External Dependencies: N
- Upgrade Mechanism: [Description]
- Admin Key Risk: [Single/Multisig/Timelock/DAO]

## Oracle Security
- Oracle Type: [Spot/TWAP/Chainlink/Custom]
- Manipulation Cost: $[amount]
- Flash Loan Amplifiable: [Yes/No]
- Circuit Breakers: [Present/Absent]

## Flash Loan Risk
- Attack Surfaces Identified: N
- Mitigation Effectiveness: [Strong/Moderate/Weak]
- Atomicity Possible: [Yes/No]

## Governance Security
- Voting Mechanism: [Description]
- Flash Loan Voting Risk: [Yes/No]
- Timelock Duration: [N blocks/N hours/None]
- Proposal Threshold: [N tokens]

## Economic Attack Surface
- Inflation Attack Risk: [High/Medium/Low]
- Donation Attack Risk: [High/Medium/Low]
- Liquidation Incentive Alignment: [Aligned/Misaligned]

## Composability Risks
- Critical Dependencies: N
- Cascade Failure Risk: [High/Medium/Low]
- Token Standard Risks: [List]

## Findings

### [CRITICAL] Finding Title
- **Description:** [What is the vulnerability]
- **Root Cause:** [Why it exists]
- **Exploitability:** [How it can be exploited]
- **Impact:** [Potential loss]
- **Recommendation:** [How to fix]

## Risk Scoring
| Category | Risk Level | Score (1-10) |
|----------|-----------|--------------|
| Oracle Security | Critical | 9 |
| Flash Loan Risk | High | 7 |
| Governance | Medium | 5 |
| Economic | High | 7 |
| Composability | Medium | 5 |
| **Overall** | **High** | **6.6** |

## Recommendations
1. [Highest priority recommendation]
2. [Next priority]
3. [Continue...]
```

## Quick Reference

| Attack Vector | Protocol Type | Capital Required | Detection Difficulty |
|--------------|---------------|-----------------|---------------------|
| Oracle Manipulation | Lending, Perps | Low (flash loan) | Medium |
| Flash Loan Governance | Governance | None | Low |
| Inflation Attack | Yield, AMM | Low | High |
| Bridge Validator | Bridge | High (collusion) | Low |
| Liquidation Manipulation | Lending | Medium | Medium |
| Peg Manipulation | Stablecoin | High | Low |
| Composability Cascade | All | Varies | High |
