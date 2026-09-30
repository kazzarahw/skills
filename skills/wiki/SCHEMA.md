# SCHEMA.md — Disciplined Maintenance Instructions

This document provides the authoritative instructions for maintaining the security wiki. All contributors MUST follow these procedures.

---

## Table of Contents

- [Overview](#overview)
- [Page Type Definitions](#page-type-definitions)
- [Frontmatter Schema](#frontmatter-schema)
- [Naming Conventions](#naming-conventions)
- [Tag Taxonomy Reference](#tag-taxonomy-reference)
- [Lint Procedures](#lint-procedures)
- [ADD-Only Rule](#add-only-rule)
- [Page Lifecycle](#page-lifecycle)
- [Quality Gates](#quality-gates)

---

## Overview

The security wiki is a structured, interlinked knowledge base that serves as the agent's persistent memory. It follows a three-layer architecture:

1. **Raw Layer** (`raw/`) — Immutable source material (tool outputs, logs, captures)
2. **Wiki Layer** (`wiki/`) — LLM-maintained structured markdown pages
3. **Schema Layer** (`SCHEMA.md`) — Instructions for disciplined maintenance

**Core Principle**: Raw data is immutable evidence; wiki pages are curated knowledge; SCHEMA.md enforces discipline.

---

## Page Type Definitions

| Type | Purpose | Required Sections | Example |
|------|---------|-------------------|---------|
| `entity` | People, organizations, projects, targets, contracts | Summary, Attributes, Findings | "TargetCorp", "Uniswap V3" |
| `concept` | Vulnerability classes, techniques, methodologies | Definition, Impact, Mitigation | "SQL Injection", "Flash Loan Attack" |
| `synthesis` | Saved query answers, analysis results | Question, Answer, Evidence | "Why TargetCorp's AD is vulnerable" |
| `trail` | Associative paths through related pages | Entry Point, Attack Chain, Impact | "Web App Attack Path → DB Compromise" |
| `timeline` | Chronological hubs for engagements | Engagement Metadata, Phase, Findings | "Engagement: TargetCorp 2026-09" |
| `overview` | Cluster landscapes for domains | Surface, Findings, Paths | "TargetCorp Attack Surface" |
| `contradiction` | Conflict analysis between sources | Conflict, Source A, Source B, Resolution | "Port 443: HTTP vs HTTPS discrepancy" |

---

## Frontmatter Schema

Every wiki page MUST include YAML frontmatter with the following fields:

```yaml
---
# Required Fields
title: "Page Title"                    # string — Human-readable page title (1-200 chars)
type: entity                           # enum — One of: entity, concept, synthesis, trail, timeline, overview, contradiction
tags: []                               # list[string] — From approved taxonomy (see references/tagging-taxonomy.md)
sources: []                            # list[string] — Raw source file paths or external references
created: YYYY-MM-DD                    # date — Page creation date (ISO 8601)
updated: YYYY-MM-DD                    # date — Last modification date (ISO 8601)
confidence: high                       # enum — high | medium | low
provenance: tool-proven                # enum — tool-proven | model-asserted | unreviewed
status: active                          # enum — active | invalidated | draft

# Optional Fields
engagement: "ENG-2026-001"             # string — Engagement identifier (format: ENG-YYYY-NNN)
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

## Naming Conventions

### File Names

| Page Type | Format | Example |
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

## Tag Taxonomy Reference

Tags are organized into categories. See `references/tagging-taxonomy.md` for the complete taxonomy.

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

### Vulnerability Tags
- `owasp-top10` — General OWASP Top 10 category
- `swc-registry` — Smart Contract Weakness Classification
- `injection` — SQL, NoSQL, OS command injection
- `broken-auth` — Authentication and session management failures
- `xss` — Cross-site scripting
- `reentrancy` — Reentrancy vulnerabilities
- `access-control` — Smart contract access control issues
- `oracle` — Oracle-related vulnerabilities

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

### Engagement Tags
- `client-{name}` — Client identification (e.g., `client-targetcorp`)
- `eng-{YYYY-NNN}` — Engagement identifier (e.g., `eng-2026-001`)
- `YYYY-MM` — Date-based filtering (e.g., `2026-09`)

### Tool Tags
- `tool-{name}` — Tool used (e.g., `tool-nmap`, `tool-burp`)

### Chain Tags (Web3 Only)
- `ethereum`, `solana`, `bitcoin`, `cosmos`, `multi-chain`, `n/a`

### Protocol Tags (Web3 Only)
- `defi`, `nft`, `dao`, `bridge`, `lending`, `amm`, `staking`, `governance`, `oracle`, `wallet`

---

## Lint Procedures

### Running Lint Checks

```bash
# Run all checks
python scripts/wiki-lint.py /path/to/wiki

# Run specific check
python scripts/wiki-lint.py /path/to/wiki --check link-validation

# Output format
python scripts/wiki-lint.py /path/to/wiki --format json
python scripts/wiki-lint.py /path/to/wiki --format markdown

# Auto-fix issues
python scripts/wiki-lint.py /path/to/wiki --fix
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found |
| 2 | Critical issues found |
| 3 | Error running lint |

### Lint Schedule

Run lint checks:
- Before committing changes
- After ingesting new material
- Weekly during active engagements
- Before generating reports

---

## ADD-Only Rule

**Never overwrite. New facts are added alongside old ones.**

When information changes:
1. Add the new fact with current date and provenance
2. Mark the old entry as `status: invalidated` (do not delete)
3. Create a `contradiction` page if sources conflict
4. Git-backed version control provides audit trail

**Why ADD-only**: Preserves reasoning history, enables rollback, prevents knowledge loss from hasty edits, supports contradiction analysis.

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

---

## Quality Gates

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
