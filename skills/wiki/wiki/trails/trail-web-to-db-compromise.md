---
title: "Web App Attack Path to DB Compromise"
type: trail
tags: [web2, attack-path, chain, eng-2026-001, client-targetcorp]
sources: ["raw/2026-09-15-attack-chain.md"]
created: 2026-09-15
updated: 2026-09-15
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# Web App Attack Path to DB Compromise

## Entry Point
[[SQL Injection in Login]] — Public-facing login form

## Attack Chain
1. [[SQL Injection in Login]] → Authentication bypass
2. [[Exposed Admin Panel]] → Administrative interface exposed
3. [[File Upload Vulnerability]] → Web shell deployment
4. Hardcoded credentials in config → Database access
5. Full database compromise → 2.3M customer records exposed

## Total Impact
Complete compromise of customer PII database (2.3M records)

## Mitigation Priority
1. Fix SQL injection (entry point)
2. Remove hardcoded credentials
3. Restrict admin panel access

## Related Pages
- [[TargetCorp]]
- [[SQL Injection]]
- [[ENG-2026-001 Timeline]]
