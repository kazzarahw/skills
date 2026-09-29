---
title: "Reentrancy"
type: concept
tags: [web3, swc-registry, reentrancy, defi, active]
sources: ["raw/2026-08-10-reentrancy-analysis.md"]
created: 2026-08-10
updated: 2026-08-10
confidence: high
provenance: tool-proven
status: active
domain: web3
severity: critical
---

# Reentrancy

## Definition
Reentrancy is a smart contract vulnerability where an external call to an untrusted contract is made before state updates are finalized. The called contract can recursively call back into the original function, repeatedly executing logic (such as withdrawals) with stale state.

## Impact
- Draining of contract funds (ETH or tokens)
- Corruption of accounting state
- Recursive exploitation amplifying single-transaction impact

## Mitigation
- Checks-Effects-Interactions pattern
- Reentrancy guards (mutex locks)
- Pull over push payment patterns
- Gas limits on external calls

## Observed In
- [[ProtoDAO]] — Withdraw function, August 2026
- [[ArtBlock]] — Withdraw function, September 2026

## Related Pages
- [[Flash Loan Attack]]
- [[Oracle Manipulation]]
- [[DeFi Protocol Security]]
