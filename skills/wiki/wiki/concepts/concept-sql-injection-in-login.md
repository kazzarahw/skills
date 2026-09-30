---
title: "SQL Injection in Login"
type: concept
tags: [web2, owasp-top10, injection, broken-auth, active]
sources: ["raw/2026-09-15-burp-sqli.md"]
created: 2026-09-15
updated: 2026-09-15
confidence: high
provenance: tool-proven
status: active
domain: web2
severity: critical
---

# SQL Injection in Login

## Definition
SQL Injection in a login form is a specific variant of SQL injection where the attack targets authentication mechanisms. By injecting malicious SQL into username or password fields, attackers can bypass authentication entirely or extract credential data.

## Impact
- Authentication bypass without valid credentials
- Account takeover
- Credential extraction
- Lateral movement within the application
- Full system compromise (when combined with other vulnerabilities)

## Mitigation
- Parameterized queries for all database interactions
- Input validation on both client and server side
- Account lockout mechanisms
- Multi-factor authentication
- Web Application Firewall (WAF)

## Observed In
- [[TargetCorp]] — Login form at targetcorp.com/login, September 2026

## Related Pages
- [[TargetCorp]]
- [[SQL Injection]]
- [[OWASP Top 10]]
- [[Web App Attack Path to DB Compromise]]
