---
title: "ProtoDAO"
type: entity
tags: [web3, defi, lending, protocol, client-protodao]
sources: ["raw/2026-08-10-protodao-audit.md"]
created: 2026-08-10
updated: 2026-08-10
confidence: high
provenance: tool-proven
status: active
domain: web3
chain: ethereum
---

# ProtoDAO

## Summary
ProtoDAO is a DeFi lending protocol on Ethereum. Audited in August 2026, the protocol had critical vulnerabilities in its withdraw function and oracle pricing mechanism.

## Attributes
- **Type:** DeFi Lending Protocol
- **Chain:** Ethereum
- **Domain:** Web3

## Findings
- [[Reentrancy]] — Critical, tool-proven (withdraw function)
- [[Flash Loan Attack]] — High, tool-proven (oracle manipulation)
- [[Oracle Manipulation]] — High, tool-proven (spot price oracle)

## Related Pages
- [[Reentrancy]]
- [[Flash Loan Attack]]
- [[Oracle Manipulation]]
