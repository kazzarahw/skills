---
name: crypto-forensics
description: Performs on-chain investigation and incident response. Use after security incidents to trace funds, analyze transactions, identify attackers, and document evidence. Covers transaction tracing, fund tracking, and post-mortem analysis.
---

# On-Chain Investigation and Incident Response

## Constitutional Rules

1. **Preserve evidence before analysis.** Export and hash all transaction data before any manipulation or transformation. On-chain evidence is immutable, but off-chain analysis can introduce errors.
2. **Never assume attacker identity from a single transaction.** Clustering heuristics can produce false positives; corroborate with multiple data points.
3. **Document every step of the investigation.** Chain of custody for on-chain evidence requires complete reproducibility of all queries and analysis.
4. **Distinguish between fund movement and fund ownership.** Tracing funds to an exchange does not identify the attacker; it identifies where funds were sent.
5. **Cross-chain tracing requires bridge analysis.** Funds that move between chains must be traced through bridge contracts, not just token transfers.
6. **Time-sensitive actions take priority.** If funds are still moving, prioritize real-time tracing over comprehensive analysis.
7. **All findings must be reproducible.** Another investigator following the same steps must reach the same conclusions.

## Investigation Process

### Phase 1: Incident Identification and Scoping

Define the incident boundaries before beginning analysis:

1. **Incident classification** — Exploit, hack, rug pull, oracle failure, governance attack, bridge exploit
2. **Affected protocols** — Primary protocol and any downstream/cascading impacts
3. **Time window** — First suspicious transaction to most recent fund movement
4. **Fund inventory** — Total value lost, token types, chain(s) affected
5. **Stakeholder identification** — Protocol team, users, liquidity providers, integrators

**Why:** Scoping prevents analysis paralysis and ensures resources focus on the actual incident.

### Phase 2: Transaction Tracing and Fund Flow Analysis

Trace fund movement from source to current location:

1. **Initial transaction analysis** — Identify the exploit transaction and its origin
2. **Direct fund tracing** — Follow token transfers from the exploit address
3. **Bridge tracing** — If funds crossed chains, trace through bridge contracts
4. **Mixer detection** — Identify if funds entered mixers (Tornado Cash, etc.)
5. **Exchange identification** — Determine if funds reached centralized exchanges
6. **Current fund status** — Frozen, liquidated, staked, bridged, or in attacker wallet

**Default:** Start with the exploit transaction and trace forward. Do not start from the protocol's stolen funds.

### Phase 3: Attacker Identification and Clustering

Identify attacker addresses through behavioral analysis:

1. **Address clustering** — Group addresses by common funding sources, timing, and behavior
2. **Funding source analysis** — Trace how attacker addresses were funded (CEX, DEX, bridge, mixer)
3. **Behavioral fingerprinting** — Gas preferences, transaction timing, contract interactions
4. **Known attacker matching** — Compare against known attacker databases (Chainalysis, TRM)
5. **Attribution confidence scoring** — Rate confidence from speculative to confirmed

**Why:** Attacker identification enables exchange cooperation, legal action, and fund recovery.

### Phase 4: Evidence Collection and Preserve

Build a defensible evidence package:

1. **Transaction export** — Raw transaction data with hashes and timestamps
2. **Fund flow diagrams** — Visual representation of fund movement
3. **Contract interaction logs** — All contract calls with decoded calldata
4. **Price data** — Token prices at time of incident for loss calculation
5. **Block explorer screenshots** — Timestamped evidence from Etherscan/Solscan
6. **Hash verification** — SHA-256 hashes of all exported data

**Why:** Evidence must withstand legal scrutiny and be verifiable by third parties.

### Phase 5: Post-Mortem Analysis and Reporting

Synthesize findings into actionable intelligence:

1. **Root cause analysis** — Why was the exploit possible?
2. **Attack timeline** — Minute-by-minute reconstruction
3. **Loss quantification** — Total loss, recovered funds, net loss
4. **Vulnerability classification** — Code bug, oracle failure, economic attack, bridge exploit
5. **Lessons learned** — What could have prevented this?
6. **Recommendations** — Specific, actionable remediation steps

## Investigation Tools

### Block Explorers

| Explorer | Chain | Best For |
|----------|-------|----------|
| Etherscan | Ethereum | Primary EVM explorer, verified contracts |
| Solscan | Solana | Solana program analysis |
| Blockscout | Multi-chain | Self-hosted, privacy-focused |
| Arbiscan | Arbitrum | L2 transaction tracing |
| Polygonscan | Polygon | Polygon PoS chain |
| BscScan | BSC | Binance Smart Chain |

### Fund Tracking

| Tool | Use Case | Access |
|------|----------|--------|
| Chainalysis Reactor | Exchange tracing, clustering | Enterprise |
| TRM Labs | Risk scoring, attribution | Enterprise |
| Elliptic | Wallet screening, compliance | Enterprise |
| Arkham | Entity labeling, deanonymization | Public/Private |
| Nansen | Wallet labeling, fund flow | Subscription |

### Transaction Analysis

| Tool | Use Case | Access |
|------|----------|--------|
| Tenderly | Transaction simulation, debugging | Public/Private |
| Phalcon | Transaction visualization, tracing | Enterprise |
| BlockSec | Attack detection, monitoring | Enterprise |
| Dune Analytics | Custom queries, aggregation | Public/Private |

### Visualization

| Tool | Use Case |
|------|----------|
| Dune Analytics | Custom fund flow dashboards |
| Nansen | Wallet labeling, money flow graphs |
| Chainalysis Reactor | Interactive fund flow visualization |
| Arkham | Entity relationship mapping |

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `cyber-report` | Report generation for investigation findings |
| `cyber-wiki` | Knowledge management for incident documentation |
| `cyber-verify` | Verification discipline for evidence validation |
| `cyber-coach` | Course correction when investigation stalls |
| `crypto-recon` | Blockchain reconnaissance for protocol analysis |
| `crypto-audit` | Smart contract audit for vulnerability identification |
| `crypto-defi` | Protocol security analysis for root cause |
| `crypto-exploit` | Understanding attack methodology |

**Workflow:** `crypto-recon` → `crypto-audit` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

- **Mixers/tumblers obscure fund flows.** Tornado Cash and similar mixers break the on-chain link between source and destination. Post-mixing funds are extremely difficult to trace.
- **Cross-chain bridges complicate tracing.** Funds that move between chains require tracing through bridge contracts, which may have different finality guarantees and different explorers.
- **Privacy chains (Monero, Zcash) are opaque.** Once funds enter privacy chains, tracing is effectively impossible without exchange cooperation.
- **Exchange cooperation is essential for fund recovery.** Law enforcement subpoenas and exchange compliance teams are the primary mechanism for freezing and recovering funds.
- **On-chain evidence is immutable but interpretation is not.** Transaction data is permanent, but clustering heuristics and attribution can be wrong.
- **Attacker addresses can be identified through clustering.** Common funding sources, timing patterns, and behavioral fingerprints enable address clustering.
- **Fund recovery requires exchange cooperation and legal action.** Technical tracing alone cannot recover funds; legal processes are required.
- **Flash loan attacks leave complex traces.** Funds may pass through multiple protocols in a single transaction, requiring careful calldata decoding.
- **Attacker smart contracts can be obfuscated.** Attackers use unverified contracts, proxy patterns, and contract factories to hide their tracks.
- **Time-sensitive actions take priority.** If funds are still moving, real-time tracing is more important than comprehensive analysis.

## Output Format

```markdown
# Investigation Report: [Incident Name]

## Executive Summary
- Incident Type: [Exploit/Hack/Rug Pull/Bridge/Oracle]
- Date: [Date]
- Total Loss: $[amount]
- Chains Affected: [List]
- Funds Recovered: $[amount] ([N]%)
- Attacker Identified: [Yes/No/Partial]
- Status: [Active/Contained/Resolved]

## Incident Timeline
| Time (UTC) | Event | Tx Hash |
|------------|-------|---------|
| 2024-01-01 12:00 | Initial exploit | 0x... |
| 2024-01-01 12:05 | Funds bridged to... | 0x... |
| 2024-01-01 12:30 | Funds deposited to... | 0x... |

## Fund Flow Analysis
- **Initial Theft:** [Amount] [Token] from [Protocol]
- **Bridge Movement:** [Amount] bridged via [Bridge] to [Chain]
- **Current Location:** [Exchange/Mixer/Staked/Attacker Wallet]
- **Recovery Status:** [Frozen/Recovered/At Large]

## Attacker Analysis
- **Primary Address:** 0x...
- **Clustered Addresses:** N addresses
- **Funding Source:** [CEX/DEX/Bridge/Mixer]
- **Attribution Confidence:** [Speculative/Moderate/High/Confirmed]
- **Known Affiliation:** [None/Group Name]

## Evidence Package
- Transaction exports: [SHA-256 hash]
- Fund flow diagrams: [SHA-256 hash]
- Contract interaction logs: [SHA-256 hash]
- Block explorer screenshots: [SHA-256 hash]

## Root Cause Analysis
- **Vulnerability Type:** [Code Bug/Oracle/Economic/Bridge/Governance]
- **Root Cause:** [Detailed explanation]
- **Why It Was Possible:** [Contributing factors]
- **Why It Wasn't Detected:** [Detection gap]

## Recommendations
1. [Immediate action]
2. [Short-term remediation]
3. [Long-term prevention]

## Appendix
- All transaction hashes
- All contract addresses
- All attacker addresses
- Tool queries used
```

## Quick Reference

| Phase | Priority | Time Sensitivity | Key Action |
|-------|----------|-----------------|------------|
| Incident ID | Critical | Immediate | Classify and scope |
| Fund Tracing | Critical | Immediate | Trace while funds move |
| Attacker ID | High | Hours | Cluster and identify |
| Evidence | High | Hours | Export and hash |
| Post-Mortem | Medium | Days | Analyze and report |
| Recovery | High | Weeks | Exchange cooperation |
