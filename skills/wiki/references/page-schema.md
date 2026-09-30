# Page Schema Reference

Complete specification for wiki page structure, frontmatter, naming conventions, and lifecycle management.

---

## Table of Contents

- [Frontmatter Schema](#frontmatter-schema)
  - [Field Constraints](#field-constraints)
- [Page Templates](#page-templates)
  - [Entity Page](#entity-page)
  - [Concept Page](#concept-page)
  - [Synthesis Page](#synthesis-page)
  - [Trail Page](#trail-page)
  - [Timeline Page](#timeline-page)
  - [Overview Page](#overview-page)
  - [Contradiction Page](#contradiction-page)
- [Naming Conventions](#naming-conventions)
  - [File Names](#file-names)
  - [Page Titles](#page-titles)
  - [Wikilinks](#wikilinks)
- [Tag Taxonomy](#tag-taxonomy)
  - [Domain Tags](#domain-tags)
  - [Technique Tags](#technique-tags)
  - [Severity Tags](#severity-tags)
  - [Status Tags](#status-tags)
- [Page Type Selection Guide](#page-type-selection-guide)
- [Page Lifecycle](#page-lifecycle)
  - [States](#states)
  - [Transitions](#transitions)
  - [Lifecycle Rules](#lifecycle-rules)
- [Examples of Well-Formed Pages](#examples-of-well-formed-pages)
  - [Good Entity Page](#good-entity-page)
  - [Good Concept Page](#good-concept-page)
- [Validation Checklist](#validation-checklist)

---

## Frontmatter Schema

Every wiki page MUST include YAML frontmatter with the following fields:

```yaml
---
# Required Fields
title: "Page Title"                    # string — Human-readable page title
type: entity                           # enum — One of: entity, concept, synthesis, trail, timeline, overview, contradiction
tags: []                               # list[string] — From approved taxonomy (see tagging-taxonomy.md)
sources: []                            # list[string] — Raw source file paths or external references
created: YYYY-MM-DD                    # date — Page creation date (ISO 8601)
updated: YYYY-MM-DD                    # date — Last modification date (ISO 8601)
confidence: high                       # enum — high | medium | low
provenance: tool-proven                # enum — tool-proven | model-asserted | unreviewed
status: active                          # enum — active | invalidated | draft

# Optional Fields
engagement: "ENG-2026-001"             # string — Engagement identifier
client: "TargetCorp"                    # string — Client/organization name
severity: critical                      # enum — critical | high | medium | low | informational
domain: web2                           # enum — web2 | web3 | cross-domain
chain: ethereum                        # enum — ethereum | solana | bitcoin | cosmos | multi-chain | n/a
tools:                                 # list[string] — Tools used to produce findings
  - "nmap 7.94"
  - "nuclei 3.1.0"
related: []                            # list[string] — Related page titles for quick navigation
supersedes: "Old Page Title"           # string — Title of page this replaces (for invalidated pages)
---
```

### Field Constraints

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `title` | string | Yes | 1-200 chars, unique across wiki |
| `type` | enum | Yes | Must be one of 7 valid types |
| `tags` | list[string] | Yes | All tags must exist in taxonomy |
| `sources` | list[string] | Yes | At least one source required |
| `created` | date | Yes | ISO 8601 format, not in future |
| `updated` | date | Yes | ISO 8601 format, >= created |
| `confidence` | enum | Yes | high, medium, low |
| `provenance` | enum | Yes | tool-proven, model-asserted, unreviewed |
| `status` | enum | Yes | active, invalidated, draft |
| `engagement` | string | No | Format: `ENG-YYYY-NNN` |
| `client` | string | No | Organization name |
| `severity` | enum | No | critical, high, medium, low, informational |
| `domain` | enum | No | web2, web3, cross-domain |
| `chain` | enum | No | ethereum, solana, bitcoin, cosmos, multi-chain, n/a |
| `tools` | list[string] | No | Tool name with optional version |
| `related` | list[string] | No | Must reference existing pages |
| `supersedes` | string | No | Must reference existing page |

---

## Page Templates

### Entity Page

```markdown
---
title: "TargetCorp"
type: entity
tags: [web2, client-name, target]
sources: ["raw/2026-09-15-recon-targetcorp.md"]
created: 2026-09-15
updated: 2026-09-15
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# TargetCorp

## Summary
Brief description of the entity (1-3 sentences).

## Attributes
- **Type:** Organization
- **Industry:** Financial Services
- **Domain:** targetcorp.com
- **Engagement:** [[ENG-2026-001 Timeline]]

## Findings
- [[SQL Injection in Login]] — Critical, tool-proven (example — create page if needed)
- [[Exposed Admin Panel]] — High, tool-proven (example — create page if needed)

## Related Pages
- [[TargetCorp Attack Surface]]
- [[ENG-2026-001 Timeline]]
```

### Concept Page

```markdown
---
title: "SQL Injection"
type: concept
tags: [web2, owasp-top10, injection]
sources: ["raw/2026-09-15-burp-sqli.md", "raw/2026-09-16-nuclei-sqli.md"]
created: 2026-09-15
updated: 2026-09-16
confidence: high
provenance: tool-proven
status: active
domain: web2
severity: critical
---

# SQL Injection

## Definition
SQL Injection is a code injection technique that exploits a security vulnerability in an application's database layer...

## Impact
- Unauthorized data access
- Authentication bypass
- Remote code execution (in severe cases)

## Mitigation
- Parameterized queries
- Input validation
- Least privilege database accounts

## Observed In
- [[TargetCorp]] — Login form, September 2026
- [[OtherClient]] — Search endpoint, March 2026

## Related Pages
- [[OWASP Top 10]]
- [[Injection Attacks]]
```

### Synthesis Page

```markdown
---
title: "Why TargetCorp's AD is Vulnerable"
type: synthesis
tags: [web2, analysis, active-directory]
sources: ["raw/2026-09-15-ad-recon.md", "raw/2026-09-16-ldap-query.md"]
created: 2026-09-16
updated: 2026-09-16
confidence: medium
provenance: model-asserted
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# Why TargetCorp's AD is Vulnerable

## Question
Why is TargetCorp's Active Directory environment susceptible to lateral movement?

## Answer
TargetCorp's AD environment has three compounding factors:

1. **Weak password policy** — 8-character minimum, no complexity requirements
2. **Excessive privileges** — 47 users in Domain Admins who don't need it
3. **Unpatched systems** — 12 domain controllers missing KB5034441

## Evidence
- [[Password Policy Analysis]] — tool-proven
- [[Domain Admin Enumeration]] — tool-proven
- [[Patch Status Report]] — tool-proven

## Confidence Rationale
Medium confidence because the analysis is based on a single engagement's findings. Cross-engagement validation needed.

## Related Pages
- [[TargetCorp]]
- [[Active Directory Security]]
```

### Trail Page

```markdown
---
title: "Web App Attack Path to DB Compromise"
type: trail
tags: [web2, attack-path, chain]
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
2. [[Admin Panel Access]] → Administrative interface exposed
3. [[File Upload Vulnerability]] → Web shell deployment
4. [[Database Credentials]] → Hardcoded credentials in config
5. [[Database Compromise]] → Full database access

## Total Impact
Complete compromise of customer PII database (2.3M records)

## Mitigation Priority
1. Fix SQL injection (entry point)
2. Remove hardcoded credentials
3. Restrict admin panel access

## Related Pages
- [[TargetCorp]]
- [[SQL Injection]]
- [[Web Shell Detection]]
```

### Timeline Page

```markdown
---
title: "Engagement: TargetCorp 2026-09"
type: timeline
tags: [web2, engagement, timeline]
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

# Engagement: TargetCorp 2026-09

## Engagement Metadata
- **Client:** TargetCorp
- **Period:** 2026-09-15 to 2026-09-29
- **Scope:** Web application, internal network, AD environment
- **Team:** Red Team Alpha

## Phase 1: Reconnaissance (Sep 15-17)
- [[Subdomain Enumeration]] — 47 subdomains discovered
- [[Technology Stack]] — Apache 2.4.49, PHP 8.1, MySQL 8.0
- [[Attack Surface Map]] — 12 external entry points

## Phase 2: Vulnerability Discovery (Sep 18-22)
- [[SQL Injection in Login]] — Critical
- [[Exposed Admin Panel]] — High
- [[File Upload Vulnerability]] — Critical

## Phase 3: Exploitation (Sep 23-26)
- [[Web Shell Deployment]] — Successful
- [[Lateral Movement]] — Via hardcoded credentials
- [[Database Compromise]] — Full access achieved

## Phase 4: Reporting (Sep 27-29)
- [[TargetCorp Attack Surface]] — Overview page
- [[Web App Attack Path to DB Compromise]] — Trail page

## Related Pages
- [[TargetCorp]]
- [[TargetCorp Attack Surface]]
```

### Overview Page

```markdown
---
title: "TargetCorp Attack Surface"
type: overview
tags: [web2, attack-surface, overview]
sources: ["raw/2026-09-15-nmap.md", "raw/2026-09-16-nuclei.md"]
created: 2026-09-16
updated: 2026-09-29
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# TargetCorp Attack Surface

## External Attack Surface
| Host | Port | Service | Risk |
|------|------|---------|------|
| targetcorp.com | 443 | HTTPS | Medium |
| admin.targetcorp.com | 443 | HTTPS | High |
| api.targetcorp.com | 443 | HTTPS | Medium |
| mail.targetcorp.com | 993 | IMAPS | Low |

## Internal Attack Surface
| Segment | Host Count | Key Services | Risk |
|---------|-----------|--------------|------|
| DMZ | 8 | Web, Mail | High |
| App Tier | 12 | App servers | Medium |
| Data Tier | 4 | Databases | Critical |
| Management | 6 | AD, Jump hosts | Critical |

## Critical Findings
- [[SQL Injection in Login]] — Internet-facing
- [[Exposed Admin Panel]] — Internet-facing
- [[Unpatched Apache]] — CVE-2024-38475

## Attack Paths
- [[Web App Attack Path to DB Compromise]]

## Related Pages
- [[TargetCorp]]
- [[ENG-2026-001 Timeline]]
```

### Contradiction Page

```markdown
---
title: "Port 443: HTTP vs HTTPS Discrepancy"
type: contradiction
tags: [web2, contradiction, network]
sources: ["raw/2026-09-15-nmap.md", "raw/2026-09-16-curl.md"]
created: 2026-09-16
updated: 2026-09-16
confidence: high
provenance: tool-proven
status: active
engagement: "ENG-2026-001"
client: "TargetCorp"
domain: web2
---

# Port 443: HTTP vs HTTPS Discrepancy

## Conflict
Two tools report different protocols on port 443 of targetcorp.com.

## Source A: Nmap (2026-09-15)
- **Result:** `443/tcp open https`
- **Tool:** nmap 7.94
- **Provenance:** tool-proven

## Source B: curl (2026-09-16)
- **Result:** `HTTP/1.1 200 OK` (plain HTTP response)
- **Tool:** curl 8.5.0
- **Provenance:** tool-proven

## Analysis
The discrepancy may be caused by:
1. Nmap detecting TLS handshake but server falling back to HTTP
2. Load balancer terminating TLS and forwarding HTTP
3. Virtual host misconfiguration

## Resolution
**Unresolved.** Requires manual verification with browser and packet capture.

## Impact
If HTTP is served on 443, traffic may be interceptable.

## Related Pages
- [[TargetCorp]]
- [[TargetCorp Attack Surface]]
```

---

## Naming Conventions

### File Names

| Convention | Format | Example |
|-----------|--------|---------|
| Entity pages | `entity-{name}.md` | `entity-targetcorp.md` |
| Concept pages | `concept-{name}.md` | `concept-sql-injection.md` |
| Synthesis pages | `synthesis-{brief-desc}.md` | `synthesis-ad-vulnerability-analysis.md` |
| Trail pages | `trail-{brief-desc}.md` | `trail-web-to-db-compromise.md` |
| Timeline pages | `timeline-{client}-{YYYY-MM}.md` | `timeline-targetcorp-2026-09.md` |
| Overview pages | `overview-{brief-desc}.md` | `overview-targetcorp-attack-surface.md` |
| Contradiction pages | `contradiction-{brief-desc}.md` | `contradiction-port-443-protocol.md` |

### Page Titles

- Use descriptive, specific titles
- Include client/entity name when relevant
- Use title case for entities, sentence case for concepts
- Maximum 200 characters

### Wikilinks

- Format: `[[Page Title]]` or `[[Page Title|Display Text]]`
- Link text should be descriptive
- Every page must have at least one outgoing wikilink
- Index.md is the root — all pages should be reachable from it

---

## Tag Taxonomy

Tags are organized into categories. See `tagging-taxonomy.md` for the complete taxonomy.

### Domain Tags
- `web2` — Web application, network, infrastructure findings
- `web3` — Blockchain, smart contract, DeFi findings
- `cross-domain` — Findings spanning both domains

### Technique Tags
- `recon` — Reconnaissance and discovery
- `audit` — Security audit findings
- `exploit` — Exploitation techniques
- `forensics` — Investigation and analysis
- `report` — Reporting and documentation
- `verify` — Verification and validation

### Severity Tags
- `critical` — Immediate action required
- `high` — Address in current sprint
- `medium` — Address in next sprint
- `low` — Address when convenient
- `informational` — No action required

### Status Tags
- `active` — Currently valid
- `invalidated` — Superseded by newer information
- `draft` — Work in progress
- `archived` — Historical reference only

---

## Page Type Selection Guide

| Content | Type | Example |
|---------|------|---------|
| A person, org, project, target, or contract | `entity` | "TargetCorp", "Uniswap V3" |
| A vulnerability class, technique, or methodology | `concept` | "SQL Injection", "Flash Loan Attack" |
| A saved query answer or analysis result | `synthesis` | "Why TargetCorp's AD is vulnerable" |
| An associative path through related pages | `trail` | "Web App → DB Compromise" |
| A chronological engagement hub | `timeline` | "Engagement: TargetCorp 2026-09" |
| A cluster landscape for a domain | `overview` | "TargetCorp Attack Surface" |
| A conflict analysis between sources | `contradiction` | "Port 443: HTTP vs HTTPS" |

---

## Page Lifecycle

### States

```
draft → active → invalidated
           ↓
        archived
```

### Transitions

| From | To | Trigger | Action |
|------|----|---------|--------|
| — | `draft` | New page created | Add frontmatter, mark as draft |
| `draft` | `active` | Content reviewed and validated | Update status, add provenance |
| `active` | `invalidated` | New evidence contradicts | Add `supersedes` field, create contradiction page if needed |
| `active` | `archived` | Engagement ended, historical value only | Update status, preserve for reference |
| `invalidated` | `active` | Re-validated with new evidence | Update provenance, add new sources |

### Lifecycle Rules

1. **ADD-only**: Never delete or overwrite. New facts are added alongside old ones.
2. **Provenance preservation**: When invalidating, keep original content and add new section.
3. **Contradiction creation**: When sources conflict, create a `contradiction` page.
4. **Index updates**: All status changes must be reflected in `Index.md`.
5. **Git tracking**: All changes committed with descriptive messages.

---

## Examples of Well-Formed Pages

### Good Entity Page
```markdown
---
title: "Uniswap V3"
type: entity
tags: [web3, defi, protocol, ethereum]
sources: ["raw/2026-08-10-uniswap-audit.md"]
created: 2026-08-10
updated: 2026-08-10
confidence: high
provenance: tool-proven
status: active
domain: web3
chain: ethereum
---

# Uniswap V3

## Summary
Uniswap V3 is a decentralized exchange protocol on Ethereum, concentrated liquidity AMM.

## Key Contracts
- Factory: 0x1F98431c8aD98523631AE4a59f267346ea31F984
- Router: 0xE592427A0AEce92De3Edee1F18E0157C05861564

## Findings
- [[Reentrancy in Swap]] — Medium, tool-proven

## Related Pages
- [[Flash Loan Attack]]
- [[DeFi Protocol Security]]
```

### Good Concept Page
```markdown
---
title: "Flash Loan Attack"
type: concept
tags: [web3, defi, attack, flash-loan]
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
A flash loan attack exploits uncollateralized borrowing in DeFi protocols to manipulate prices or drain funds.

## Common Patterns
1. Borrow large sum via flash loan
2. Manipulate oracle price
3. Exploit price discrepancy for profit
4. Repay loan in same transaction

## Observed In
- [[Uniswap V3]] — Oracle manipulation
- [[Cream Finance]] — Price manipulation (2026-03)

## Mitigation
- Use TWAP oracles instead of spot prices
- Implement circuit breakers
- Rate-limit large transactions

## Related Pages
- [[Oracle Manipulation]]
- [[DeFi Protocol Security]]
```

---

## Validation Checklist

Before committing a new page, verify:

- [ ] All required frontmatter fields present
- [ ] `type` matches content
- [ ] All tags exist in taxonomy
- [ ] At least one source listed
- [ ] At least one outgoing wikilink
- [ ] Page added to `Index.md`
- [ ] File name follows convention
- [ ] Dates are valid ISO 8601
- [ ] `updated` >= `created`
- [ ] Provenance level is appropriate
