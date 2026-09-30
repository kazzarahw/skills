---
title: "ArtBlock"
type: entity
tags: [web3, nft, marketplace, defi, artblock, client-artblock, active]
sources: ["raw/2026-09-29-artblock-audit.md"]
created: 2026-09-29
updated: 2026-09-29
confidence: high
provenance: tool-proven
status: active
domain: web3
chain: ethereum
related:
  - "Reentrancy"
  - "Flash Loan Attack"
  - "Oracle Manipulation"
---

# ArtBlock

## Summary
ArtBlock is an NFT marketplace on Ethereum. Audited in September 2026, the platform had critical vulnerabilities in its withdraw function and oracle pricing mechanism that could be combined to drain contract funds.

## Attributes
- **Type:** NFT Marketplace
- **Chain:** Ethereum
- **Domain:** Web3

## Findings
- [[Reentrancy]] — Critical, tool-proven (withdraw function)
- [[Flash Loan Attack]] — High, tool-proven (oracle manipulation)
- [[Oracle Manipulation]] — High, tool-proven (NFT pricing oracle)

## Related Pages
- [[Reentrancy]]
- [[Flash Loan Attack]]
- [[Oracle Manipulation]]
- [[ArtBlock Combined Attack Path: Reentrancy + Oracle Manipulation]]
- [[ArtBlock Attack Path: Flash Loan to Drain]]
