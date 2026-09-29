# Lint Rules

Detailed lint check rules and procedures for maintaining wiki quality.

## Overview

Lint checks ensure wiki integrity, completeness, and accuracy. Run lint after each ingestion phase and before major operations.

## Check Categories

1. **Broken Wikilinks** — Verify all `[[links]]` resolve
2. **Orphan Pages** — Find pages with no incoming links
3. **Stale Claims** — Flag outdated or contradicted information
4. **Duplicate Content** — Detect similar or overlapping pages
5. **Frontmatter Validation** — Ensure all required fields present
6. **Index Completeness** — Verify Index.md covers all pages

## 1. Broken Wikilink Detection

### Rule
Every `[[wikilink]]` must resolve to an existing wiki page.

### Procedure
1. Extract all `[[...]]` patterns from all wiki pages
2. For each link, check if target page exists in `wiki/`
3. Report broken links with source page and line number

### Exceptions
- Links to external URLs (http://, https://) are ignored
- Links with display text `[[Target|Display]]` check `Target` only
- Links to `raw/` sources are checked but flagged as warnings

### Output Format
```
BROKEN LINKS:
- wiki/concepts/sqli.md:15 → [[SQL Injections]] (not found)
- wiki/entities/targetcorp.md:42 → [[TargetCorp AD]] (not found)
```

## 2. Orphan Page Detection

### Rule
Every wiki page (except Index.md) must have at least one incoming link from another wiki page.

### Procedure
1. Build link graph from all `[[wikilinks]]`
2. Identify pages with zero incoming links
3. Report orphans with suggestions for linking

### Exceptions
- `Index.md` is exempt (it is the root)
- Pages created in the last 24 hours are exempt (grace period)
- `timeline` pages are exempt if linked from Index.md

### Output Format
```
ORPHAN PAGES:
- wiki/concepts/kerberos.md (no incoming links)
  Suggested: Link from [[Active Directory]] or [[Authentication]]
```

## 3. Stale Claim Detection

### Rule
Claims marked as `status: invalidated` or contradicted by newer evidence must be flagged.

### Procedure
1. Find all pages with `status: invalidated`
2. Find all `contradiction` pages
3. Check if invalidated pages are still linked as active
4. Flag pages where invalidated content is presented as current

### Indicators of Stale Content
- `status: invalidated` in frontmatter
- Contradiction pages referencing the claim
- Claims older than 90 days with `provenance: model-asserted`
- Claims contradicted by `tool-proven` evidence

### Output Format
```
STALE CLAIMS:
- wiki/entities/targetcorp.md: "TargetCorp uses Windows 2016" (invalidated 2026-08-15)
  Contradicted by: wiki/contradictions/win2016-vs-win2022.md
```

## 4. Duplicate Content Detection

### Rule
Pages with highly similar content or overlapping scope should be merged or differentiated.

### Procedure
1. Compare page titles for similarity (Levenshtein distance < 3)
2. Compare tag overlap (> 70% shared tags)
3. Compare content similarity (first 500 characters)
4. Report potential duplicates with similarity score

### Exceptions
- `timeline` pages for different engagements
- `synthesis` pages answering different questions
- Pages with different `provenance` levels (raw vs. curated)

### Output Format
```
POTENTIAL DUPLICATES:
- wiki/concepts/sqli.md and wiki/concepts/sql-injection.md (similarity: 0.85)
  Action: Merge or differentiate scope
```

## 5. Frontmatter Validation

### Rule
Every wiki page must have complete, valid frontmatter.

### Required Fields
- `title` — Non-empty string
- `type` — One of: entity, concept, synthesis, trail, timeline, overview, contradiction
- `tags` — Non-empty array
- `sources` — Array (can be empty)
- `created` — Valid date (YYYY-MM-DD)
- `updated` — Valid date (YYYY-MM-DD)
- `confidence` — One of: high, medium, low
- `provenance` — One of: tool-proven, model-asserted, unreviewed
- `status` — One of: active, invalidated, draft

### Validation Rules
- `created` must not be in the future
- `updated` must not be before `created`
- `updated` should not be more than 30 days in the past (stale page)
- `type` must match directory location (e.g., `entity` pages in `entities/`)

### Output Format
```
FRONTMATTER ERRORS:
- wiki/concepts/sqli.md: Missing required field 'provenance'
- wiki/entities/targetcorp.md: 'updated' (2026-01-01) before 'created' (2026-09-28)
- wiki/syntheses/analysis.md: Invalid type 'analysis' (must be 'synthesis')
```

## 6. Index Completeness Check

### Rule
`Index.md` must list all active wiki pages.

### Procedure
1. List all `.md` files in `wiki/` subdirectories
2. Check each file is referenced in `Index.md`
3. Report missing entries

### Exceptions
- `Index.md` itself
- `SCHEMA.md`
- Pages with `status: draft` (optional inclusion)

### Output Format
```
INDEX MISSING ENTRIES:
- wiki/concepts/kerberos.md (not in Index.md)
- wiki/entities/targetcorp.md (not in Index.md)
```

## Lint Execution

### Manual Run
```bash
# Run all lint checks
# (Agent executes these checks procedurally)
```

### Automated Checks
1. Parse all wiki pages
2. Build link graph
3. Run each check category
4. Generate report
5. Suggest fixes

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| ERROR | Broken required field or link | Must fix immediately |
| WARNING | Potential issue (orphan, stale) | Should fix soon |
| INFO | Suggestion for improvement | Optional fix |

## Lint Report Template

```
WIKI LINT REPORT
Date: YYYY-MM-DD
Pages Checked: N

ERRORS (N):
- [ERROR] wiki/page.md: Description

WARNINGS (N):
- [WARNING] wiki/page.md: Description

INFO (N):
- [INFO] wiki/page.md: Description

SUMMARY:
- Broken Links: N
- Orphan Pages: N
- Stale Claims: N
- Potential Duplicates: N
- Frontmatter Errors: N
- Index Missing: N
```

## Post-Lint Actions

1. **Fix errors immediately** — Broken links and frontmatter errors
2. **Review warnings** — Orphans and stale claims need attention
3. **Schedule info fixes** — Duplicates and improvements can wait
4. **Update Index.md** — After adding new pages
5. **Re-run lint** — Verify all fixes applied
