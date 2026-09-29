---
name: cyber-wiki
description: Maintains a structured cybersecurity knowledge base as interlinked markdown files. Use to record findings, techniques, and patterns discovered during engagements. The wiki is the agent's persistent memory.
---

# Cyber Wiki

A structured, interlinked cybersecurity knowledge base that serves as the agent's persistent memory. Designed for ADD-only growth with full provenance tracking.

## Three-Layer Architecture

```
cyber-wiki/
├── raw/              # Layer 1: Immutable source material
│   ├── nmap/         #   Tool outputs (nmap, masscan, etc.)
│   ├── nuclei/       #   Scanner results
│   ├── burp/         #   Proxy captures
│   ├── notes/        #   Manual observations
│   └── imports/      #   External reports, CVEs
├── wiki/             # Layer 2: LLM-maintained structured markdown
│   ├── Index.md      #   Master navigation hub
│   ├── entities/     #   People, orgs, projects, targets
│   ├── concepts/     #   Vulnerability classes, techniques
│   ├── syntheses/    #   Query answers, analysis results
│   ├── trails/       #   Associative paths through pages
│   ├── timelines/    #   Chronological engagement hubs
│   ├── overviews/    #   Cluster landscapes for domains
│   └── contradictions/ # Conflict analysis between sources
└── SCHEMA.md         # Layer 3: Instructions for disciplined maintenance
```

**Why three layers**: Raw data is immutable evidence; wiki pages are curated knowledge; SCHEMA.md enforces discipline. Separating them prevents contamination and enables auditability.

## Page Types

| Type | Purpose | Example |
|------|---------|---------|
| `entity` | People, organizations, projects, targets | "TargetCorp", "Metasploit Framework" |
| `concept` | Vulnerability classes, techniques, methodologies | "SQL Injection", "Pass-the-Hash" |
| `synthesis` | Saved query answers, analysis results | "Why TargetCorp's AD is vulnerable" |
| `trail` | Associative paths through related pages | "Web App Attack Path → DB Compromise" |
| `timeline` | Chronological hubs for engagements | "Engagement: TargetCorp 2026-09" |
| `overview` | Cluster landscapes for domains | "TargetCorp Attack Surface" |
| `contradiction` | Conflict analysis between sources | "Port 443: HTTP vs HTTPS discrepancy" |

## Core Operations

### 1. Ingest

Read new source material, extract key information, integrate into wiki.

**Procedure**:
1. Read source from `raw/`
2. Identify entities, concepts, and relationships
3. Create or update wiki pages (ADD-only — never overwrite)
4. Link to related pages via `[[wikilinks]]`
5. Update `Index.md` with new entries
6. Tag with appropriate provenance level

**File naming**: `YYYY-MM-DD-source-briefdesc.md` in `raw/`

### 2. Query

Search the wiki first, then raw sources. File valuable answers back.

**Procedure**:
1. Search `wiki/` for existing knowledge
2. If insufficient, search `raw/` for source material
3. Synthesize answer from available evidence
4. Save valuable answers as `synthesis` pages
5. Link synthesis to source entities/concepts

**Why file answers back**: Prevents re-derivation, builds institutional knowledge, enables pattern recognition across engagements.

### 3. Lint

Check for broken links, orphans, stale claims, duplicates.

**Procedure**:
1. Validate all `[[wikilinks]]` resolve to existing pages
2. Identify orphan pages (no incoming links)
3. Flag stale claims (contradicted by newer evidence)
4. Detect duplicate content (similar titles, overlapping tags)
5. Verify frontmatter completeness
6. Check Index.md covers all pages

See `references/lint-rules.md` for detailed rules.

## ADD-Only Rule

**Never overwrite. New facts are added alongside old ones.**

When information changes:
- Add the new fact with current date and provenance
- Mark the old entry as `status: invalidated` (do not delete)
- Create a `contradiction` page if sources conflict
- Git-backed version control provides audit trail

**Why ADD-only**: Preserves reasoning history, enables rollback, prevents knowledge loss from hasty edits, supports contradiction analysis.

## Provenance Tracking

Every claim must indicate its verification level:

| Provenance | Meaning | Usage |
|------------|---------|-------|
| `tool-proven` | Backed by captured tool output | Scanner results, command output, verified observations |
| `model-asserted` | Hypothesis, not verified | Inferences, predictions, unconfirmed patterns |
| `unreviewed` | Not yet validated | Raw imports, unprocessed observations |

**Why provenance matters**: Prevents garbage-in-gospel-out, enables confidence weighting, supports contradiction detection.

## Frontmatter Schema

Every wiki page MUST include:

```yaml
---
title: "Page Title"
type: entity | concept | synthesis | trail | timeline | overview | contradiction
tags: []
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active | invalidated | draft
---
```

See `references/page-schema.md` for complete schema, templates, and naming conventions.

## Cross-Referencing

Use `[[wikilinks]]` for all internal references.

**Rules**:
- Every page links to at least one related page
- `Index.md` serves as master navigation hub
- Contradictions are flagged with `[[contradiction]]` links, not silently resolved
- Use descriptive link text: `[[SQL Injection|SQLi in login forms]]`

**Why wikilinks**: Enables graph traversal, supports trail pages, makes relationships explicit and auditable.

## Gotchas

| Gotcha | Mitigation |
|--------|------------|
| **Knowledge decay** | Regular lint cycles; confidence degrades over time |
| **Authoritative hallucinations** | Contradiction pages flag conflicts; agent must not silently pick sides |
| **Knowledge burial** | Index.md surfaces important pages; trails create multiple paths |
| **Garbage-in-gospel-out** | Provenance tracking; `model-asserted` never upgraded without evidence |
| **Consolidation errors** | ADD-only rule preserves original claims for comparison |
| **Context dilution** | Focused page types; trails prevent context loss across sessions |
| **Provenance failures** | Lint checks provenance fields; `unreviewed` flagged for review |
| **Memory scoping failures** | Tags include engagement/session identifiers; timelines isolate contexts |

## Quick Start

1. **First run**: Create directory structure, `Index.md`, and `SCHEMA.md`
2. **New engagement**: Create `timeline` page, begin ingesting into `raw/`
3. **After each phase**: Run lint, update Index, file syntheses
4. **Cross-engagement**: Search wiki before querying raw; link related findings

## Scripts

- `scripts/wiki-search.py` — Search the wiki (title, tag, content matching with scoring)
- `scripts/wiki-backup.sh` — Backup and restore the wiki

## File References

- `references/page-schema.md` — Complete frontmatter schema, page templates, naming conventions, tag taxonomy
- `references/lint-rules.md` — Detailed lint check rules and procedures
