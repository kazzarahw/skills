---
title: "Cross-Site Scripting"
type: concept
tags: [web2, owasp-top10, xss, active]
sources: ["raw/2026-09-15-burp-xss.md"]
created: 2026-09-15
updated: 2026-09-15
confidence: high
provenance: tool-proven
status: active
domain: web2
severity: high
---

# Cross-Site Scripting

## Definition
Cross-Site Scripting (XSS) is a code injection technique that exploits a security vulnerability in a web application's output encoding. Attackers inject malicious scripts into web pages viewed by other users, typically via input fields that are rendered without proper sanitization.

## Impact
- Session hijacking via cookie theft
- Credential harvesting via fake login forms
- Defacement of web pages
- Redirection to malicious sites
- Keylogging and screen capture

## Mitigation
- Output encoding (HTML entity encoding)
- Content Security Policy (CSP)
- Input validation and sanitization
- HttpOnly and Secure cookie flags
- X-XSS-Protection header (legacy browsers)

## Observed In
- [[TargetCorp]] — Login form, September 2026

## Related Pages
- [[TargetCorp]]
- [[OWASP Top 10]]
