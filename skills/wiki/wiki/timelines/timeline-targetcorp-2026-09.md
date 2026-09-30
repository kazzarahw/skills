---
title: "ENG-2026-001 Timeline"
type: timeline
tags: [web2, engagement, timeline, eng-2026-001, client-targetcorp]
sources: ["raw/2026-09-15-engagement-kickoff.md"]
created: 2026-09-15
updated: 2026-09-29
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# ENG-2026-001 Timeline

## Engagement Metadata
- **Client:** TargetCorp
- **Period:** 2026-09-15 to 2026-09-29
- **Scope:** Web application, internal network, AD environment
- **Team:** Red Team Alpha

## Phase 1: Reconnaissance (Sep 15-17)
- Subdomain enumeration — 47 subdomains discovered
- Technology stack — Apache 2.4.49, PHP 8.1, MySQL 8.0
- Attack surface map — 12 external entry points

## Phase 2: Vulnerability Discovery (Sep 18-22)
- [[SQL Injection in Login]] — Critical
- [[Exposed Admin Panel]] — High
- [[File Upload Vulnerability]] — Critical

## Phase 3: Exploitation (Sep 23-26)
- Web shell deployment — Successful
- Lateral movement — Via hardcoded credentials
- Database compromise — Full access achieved

## Phase 4: Reporting (Sep 27-29)
- [[TargetCorp Attack Surface]] — Overview page
- [[Web App Attack Path to DB Compromise]] — Trail page

## Findings
- SQL injection in login form (critical)
- Exposed admin panel (high)
- File upload vulnerability (critical)
- Hardcoded credentials in config
- Full database compromise achieved

## Related Pages
- [[TargetCorp]]
- [[TargetCorp Attack Surface]]
