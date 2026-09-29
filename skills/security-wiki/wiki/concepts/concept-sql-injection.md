---
title: "SQL Injection"
type: concept
tags: [web2, owasp-top10, injection, active]
sources: ["raw/2026-09-15-burp-sqli.md"]
created: 2026-09-15
updated: 2026-09-15
confidence: high
provenance: tool-proven
status: active
domain: web2
severity: critical
---

# SQL Injection

## Definition
SQL Injection is a code injection technique that exploits a security vulnerability in an application's database layer. Attackers insert malicious SQL statements into input fields, which are then executed by the database, allowing unauthorized data access, modification, or deletion.

## Impact
- Unauthorized data access (PII, credentials, financial data)
- Authentication bypass
- Data modification or deletion
- Remote code execution (in severe cases)
- Full database compromise

## Mitigation
- Parameterized queries (prepared statements)
- Input validation and sanitization
- Least privilege database accounts
- Web Application Firewall (WAF) rules
- Regular security testing

## Observed In
- [[TargetCorp]] — Login form, September 2026

## Related Pages
- [[TargetCorp]]
- [[OWASP Top 10]]
- [[SQL Injection in Login]]
