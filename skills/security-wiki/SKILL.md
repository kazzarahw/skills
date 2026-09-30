---
name: security-wiki
description: >-
  Persistent knowledge base with provenance, for engagements and general research alike. Use when recording anything worth keeping — findings, decisions, techniques, patterns — or when prior knowledge applies. Security-report draws source material from it.
---

# Wiki

A structured, interlinked knowledge base that serves as the agent's persistent memory — the Karpathy llm-wiki pattern: raw sources stay immutable, the LLM owns a curated wiki layer, and everything compounds instead of re-deriving each session. Security engagements are the first domain profile; anything worth keeping (research, decisions, patterns, findings) belongs here. Designed for ADD-only growth with full provenance tracking.

## Three-Layer Architecture

```
wiki-base/
├── raw/              # Layer 1: Immutable source material (never edited)
│   ├── notes/        #   Manual observations, transcripts, clips
│   ├── docs/         #   Articles, papers, READMEs, advisories
│   ├── imports/      #   External reports, CVEs, data exports
│   └── security/     #   Domain profile: nmap, nuclei, burp, logs, PCAP, chain
├── wiki/             # Layer 2: LLM-maintained structured markdown
│   ├── Index.md      #   Master navigation hub (read first on every query)
│   ├── log.md        #   Append-only record: ingests, queries, lints
│   ├── entities/     #   People, orgs, projects, targets, contracts
│   ├── concepts/     #   Ideas, techniques, methodologies, vuln classes
│   ├── syntheses/    #   Query answers and analysis, filed back
│   ├── trails/       #   Associative paths through pages
│   ├── timelines/    #   Chronological hubs (engagements, projects)
│   ├── overviews/    #   Cluster landscapes for domains
│   └── contradictions/ # Conflict analysis between sources
└── SCHEMA.md         # Layer 3: Instructions for disciplined maintenance
```

**Why three layers**: Raw data is immutable evidence; wiki pages are curated knowledge; SCHEMA.md enforces discipline. Separating them prevents contamination and enables auditability.

## Page Types

| Type | Purpose | Example |
|------|---------|---------|
| `entity` | People, organizations, projects, targets, contracts | "TargetCorp", "Uniswap V3", "Metasploit Framework" |
| `concept` | Ideas, techniques, methodologies, vulnerability classes | "SQL Injection", "Flash Loan Attack", "Pass-the-Hash" |
| `synthesis` | Saved query answers, analysis results | "Why TargetCorp's AD is vulnerable" |
| `trail` | Associative paths through related pages | "Web App Attack Path → DB Compromise" |
| `timeline` | Chronological hubs for engagements or projects | "Engagement: TargetCorp 2026-09" |
| `overview` | Cluster landscapes for domains | "TargetCorp Attack Surface" |
| `contradiction` | Conflict analysis between sources | "Port 443: HTTP vs HTTPS discrepancy" |
| `log` | Append-only record (log.md): ingests, queries, lints | "## [2026-09-30] ingest \| TargetCorp nmap" |

## Core Operations

### 1. Ingest

Read new source material, extract key information, integrate into wiki.

**Procedure:**
1. Read source from `raw/`
2. Identify entities, concepts, and relationships
3. Create or update wiki pages (ADD-only — never overwrite)
4. Link to related pages via `[[wikilinks]]`
5. Update `Index.md` with new entries
6. Append to `wiki/log.md` with a parseable prefix (`## [YYYY-MM-DD] ingest | <source>`)
7. Tag with appropriate provenance level

**File naming**: `YYYY-MM-DD-source-briefdesc.md` in `raw/`

**Exit Criteria:**
- [ ] Source material read and key information extracted
- [ ] New wiki pages created with complete frontmatter
- [ ] All wikilinks resolve to existing pages
- [ ] Index.md updated with new entries
- [ ] Appropriate tags applied from taxonomy
- [ ] Provenance level assigned
- [ ] Lint passes with no new critical issues

### 2. Query

Search the wiki first, then raw sources. File valuable answers back.

**Procedure:**
1. Read `wiki/Index.md` first to find relevant pages, then drill in
2. Search `wiki/` for existing knowledge
3. If insufficient, search `raw/` for source material
4. Synthesize answer from available evidence
5. Save valuable answers as `synthesis` pages
6. Link synthesis to source entities/concepts
7. Append the query to `wiki/log.md` (`## [YYYY-MM-DD] query | <question>`)

**Why file answers back**: Prevents re-derivation, builds institutional knowledge, enables pattern recognition across engagements.

**Exit Criteria:**
- [ ] Wiki searched for existing knowledge
- [ ] Raw sources searched if wiki insufficient
- [ ] Answer synthesized from available evidence
- [ ] Valuable answers saved as synthesis pages
- [ ] Synthesis pages linked to source entities/concepts
- [ ] Confidence level assigned based on evidence quality

### 3. Lint

Check for broken links, orphans, stale claims, duplicates.

**Procedure:**
1. Validate all `[[wikilinks]]` resolve to existing pages
2. Identify orphan pages (no incoming links)
3. Flag stale claims (contradicted by newer evidence)
4. Detect duplicate content (similar titles, overlapping tags)
5. Verify frontmatter completeness
6. Check Index.md covers all pages

See `references/lint-rules.md` for detailed rules.

**Exit Criteria:**
- [ ] All wikilinks validated (no broken links)
- [ ] Orphan pages identified and addressed
- [ ] Stale claims flagged
- [ ] Duplicates detected and resolved
- [ ] Frontmatter completeness verified
- [ ] Index.md coverage confirmed
- [ ] Lint report generated with exit code 0 (no critical issues)

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

**Rules:**
- Every page links to at least one related page
- `Index.md` serves as master navigation hub
- Contradictions are flagged with `[[contradiction]]` links, not silently resolved
- Use descriptive link text: `[[SQL Injection|SQLi in login forms]]`

**Why wikilinks**: Enables graph traversal, supports trail pages, makes relationships explicit and auditable.

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `security-suite` | Orchestration and engagement tracking |
| `security-recon` | Store recon findings and attack surface maps |
| `security-audit` | Store audit findings and vulnerability analysis |
| `security-exploit` | Store exploit techniques and attack paths |
| `security-forensics` | Store investigation findings and evidence |
| `security-report` | Source material for reports |
| `security-verify` | Store verification results |
| `security-coach` | Store lessons learned and pattern recognition |
| `deep-research` | File cited reports as source material and syntheses |

## Handoffs

- Phase output from any lifecycle skill belongs here — record findings, techniques, and patterns with provenance at each phase end.
- Building a report → `security-report` draws source material from here.
- Background needed first → load `deep-research`, then file its report here.
- General knowledge (non-engagement) → ingest directly; no engagement required.

## Mid-Work Checkpoints

Periodically verify:
1. **Provenance on every entry?** No record without its source and verdict.
2. **ADD-only?** Never rewrite history; supersede with new entries.
3. **Phase ends recorded?** Each lifecycle phase leaves its output here.

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
| **Cross-domain contamination** | Web2 and web3 findings tagged by domain; never mix without explicit link |
| **Stale tool references** | Tool versions recorded in frontmatter; lint flags outdated versions |

## Quick Start

1. **First run**: Create directory structure, `Index.md`, `log.md`, and `SCHEMA.md`
2. **New engagement or topic**: Create `timeline` page (or `overview` for a topic), begin ingesting into `raw/`
3. **After each phase or source**: Run lint, update Index, file syntheses, append to log
4. **Cross-engagement**: Search wiki before querying raw; link related findings

## Scripts

- `scripts/wiki-search.py` — Search the wiki (title, tag, content matching with scoring)
- `scripts/wiki-backup.sh` — Backup and restore the wiki
- `scripts/wiki-lint.py` — Automated lint checks

## Backup and Restore

### Backup Procedure

**Full Backup:**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --full --verify
```

**Incremental Backup:**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --incremental --verify
```

**Encrypted Backup:**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --encrypt --recipient security@example.com
```

**With Rotation (keep 10 backups):**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --rotate 10
```

### Restore Procedure

**Restore Most Recent Backup:**
```bash
scripts/wiki-backup.sh /path/to/wiki /path/to/backups --restore
```

**Restore Specific Date:**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --restore --restore-date 2026-09-15
```

**List Available Backups:**
```bash
bash scripts/wiki-backup.sh /path/to/wiki /path/to/backups --list
```

### Backup Types

| Type | Description | File Pattern |
|------|-------------|--------------|
| Full | Complete backup of all files | `YYYY-MM-DD_full_TIMESTAMP/` |
| Incremental | Only changed files since last full | `YYYY-MM-DD_incremental_TIMESTAMP/` |
| Compressed | Gzipped tar archive | `*.tar.gz` |
| Encrypted | GPG encrypted archive | `*.tar.gz.gpg` |

### Backup Best Practices

1. **Schedule regular backups** — At least weekly during active engagements
2. **Verify backups** — Use `--verify` flag to check integrity
3. **Test restores** — Periodically test restore procedures
4. **Off-site storage** — Store backups in a separate location from the wiki
5. **Encryption** — Use `--encrypt` for sensitive engagement data
6. **Rotation** — Use `--rotate` to manage backup storage space

## References

- `references/page-schema.md` — Complete frontmatter schema, page templates, naming conventions, tag taxonomy
- `references/lint-rules.md` — Detailed lint check rules and procedures
- `references/tagging-taxonomy.md` — Tag taxonomy for web2, web3, and cross-domain findings
- `references/cross-engagement-patterns.md` — Pattern recognition across engagements
