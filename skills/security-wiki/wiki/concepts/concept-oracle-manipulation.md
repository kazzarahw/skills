---
title: "Oracle Manipulation"
type: concept
tags: [web3, defi, oracle, attack, active]
sources: ["raw/2026-08-10-oracle-analysis.md"]
created: 2026-08-10
updated: 2026-08-10
confidence: high
provenance: tool-proven
status: active
domain: web3
severity: high
---

# Oracle Manipulation

## Definition
Oracle manipulation is an attack on DeFi protocols that rely on external price feeds. An attacker artificially moves the price reported by an oracle (often via a flash loan on a DEX) to trigger favorable protocol behavior — such as borrowing against inflated collateral or liquidating positions at incorrect prices.

## Common Patterns
1. Identify protocol using spot price oracle
2. Use flash loan to move DEX price
3. Protocol reads manipulated price
4. Exploit price discrepancy (borrow, liquidate, arbitrage)
5. Repay flash loan, keep profit

## Impact
- Protocol insolvency
- Incorrect liquidations
- Arbitrage extraction from protocol reserves
- Cascading failures across integrated protocols

## Mitigation
- TWAP (Time-Weighted Average Price) oracles
- Decentralized oracle networks (Chainlink, Band)
- Circuit breakers on large price deviations
- Multi-source oracle aggregation

## Observed In
- [[ProtoDAO]] — Spot price oracle, August 2026
- [[ArtBlock]] — NFT pricing oracle, September 2026

## Related Pages
- [[Flash Loan Attack]]
- [[Reentrancy]]
- [[DeFi Protocol Security]]
