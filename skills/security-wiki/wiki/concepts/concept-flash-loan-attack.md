---
title: "Flash Loan Attack"
type: concept
tags: [web3, defi, attack, flash-loan, active]
sources: ["raw/2026-08-10-flash-loan-analysis.md"]
created: 2026-08-10
updated: 2026-08-10
confidence: high
provenance: tool-proven
status: active
domain: web3
severity: high
---

# Flash Loan Attack

## Definition
A flash loan attack exploits uncollateralized borrowing in DeFi protocols to manipulate prices or drain funds. The attacker borrows a large sum, uses it to manipulate an oracle or market, exploits the price discrepancy for profit, and repays the loan — all within a single transaction.

## Common Patterns
1. Borrow large sum via flash loan
2. Manipulate oracle price
3. Exploit price discrepancy for profit
4. Repay loan in same transaction

## Impact
- Protocol fund drainage
- Oracle price manipulation
- Cascading liquidations
- Loss of user funds

## Mitigation
- Use TWAP oracles instead of spot prices
- Implement circuit breakers
- Rate-limit large transactions
- Use decentralized oracle networks (Chainlink)

## Observed In
- [[ProtoDAO]] — Oracle manipulation, August 2026
- [[ArtBlock]] — Oracle manipulation, September 2026

## Related Pages
- [[Oracle Manipulation]]
- [[Reentrancy]]
- [[DeFi Protocol Security]]
