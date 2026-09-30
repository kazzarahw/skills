# Lint Rules Reference

Detailed lint check rules and procedures for maintaining wiki quality.

---

## Table of Contents

- [Lint Check Overview](#lint-check-overview)
- [1. Link Validation](#1-link-validation)
- [2. Orphan Detection](#2-orphan-detection)
- [3. Stale Claim Detection](#3-stale-claim-detection)
- [4. Duplicate Detection](#4-duplicate-detection)
- [5. Frontmatter Completeness](#5-frontmatter-completeness)
- [6. Index Coverage](#6-index-coverage)
- [7. Provenance Completeness](#7-provenance-completeness)
- [8. Tag Validity](#8-tag-validity)
- [9. Page Type Validity](#9-page-type-validity)
- [10. Cross-Domain Contamination](#10-cross-domain-contamination)
- [Lint Execution](#lint-execution)
  - [Running Lint Checks](#running-lint-checks)
  - [Exit Codes](#exit-codes)
  - [Automation](#automation)

---

## Lint Check Overview

| Check | Severity | Automated | Description |
|-------|----------|-----------|-------------|
| Link validation | Critical | Yes | All wikilinks resolve to existing pages |
| Orphan detection | Warning | Yes | Pages with no incoming links |
| Stale claim detection | Warning | Yes | Claims contradicted by newer evidence |
| Duplicate detection | Warning | Yes | Similar titles, overlapping tags |
| Frontmatter completeness | Critical | Yes | All required fields present |
| Index coverage | Critical | Yes | All pages listed in Index.md |
| Provenance completeness | Warning | Yes | All claims have provenance labels |
| Tag validity | Critical | Yes | All tags in taxonomy |
| Page type validity | Warning | Yes | Correct type for content |
| Cross-domain contamination | Critical | Yes | Web2/web3 findings properly separated |

---

## 1. Link Validation

**Severity:** Critical

### Check Procedure

1. Parse all wiki pages for `[[wikilinks]]`
2. Extract link targets (text before `|` or `]]`)
3. Normalize link targets (lowercase, trim whitespace)
4. Compare against existing page titles
5. Report broken links with source page and line number

### Detection Rules

```python
# Pseudocode
for page in wiki_pages:
    for link in extract_wikilinks(page.content):
        target = normalize(link.target)
        if target not in existing_titles:
            report_broken_link(page, link, target)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Link target does not exist | Critical |
| Link target exists but is invalidated | Warning |
| Link uses non-standard format | Info |

### Remediation

1. Create the missing page (if it should exist)
2. Update the link to point to the correct page
3. Remove the link if the target is no longer relevant
4. For invalidated targets, link to the superseding page

### Example Output

```
[CRITICAL] Broken link in entity-targetcorp.md:42
  [[SQL Injection in Login]] → Page not found
  Suggested fix: Create page or update link to [[SQL Injection]]
```

---

## 2. Orphan Detection

**Severity:** Warning

### Check Procedure

1. Build incoming link graph from all pages
2. Identify pages with zero incoming links
3. Exclude `Index.md` (root node, no incoming links expected)
4. Report orphan pages

### Detection Rules

```python
# Pseudocode
incoming_links = defaultdict(list)
for page in wiki_pages:
    for link in extract_wikilinks(page.content):
        incoming_links[link.target].append(page.title)

for page in wiki_pages:
    if page.title != "Index" and len(incoming_links[page.title]) == 0:
        report_orphan(page)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Orphan page (no incoming links) | Warning |
| Orphan page with status: draft | Info |
| Orphan page with status: invalidated | Info |

### Remediation

1. Add a link from a related page (e.g., Index.md, timeline, overview)
2. If the page is genuinely standalone, add it to Index.md
3. If the page is no longer relevant, mark as `archived`

### Example Output

```
[WARNING] Orphan page: concept-advanced-persistence.md
  No incoming links found
  Suggested fix: Add link from [[Index]] or related concept page
```

---

## 3. Stale Claim Detection

**Severity:** Warning

### Check Procedure

1. Extract all claims with dates from page content
2. Identify claims marked as `status: invalidated`
3. Check if newer evidence exists that contradicts active claims
4. Flag claims where `updated` date is significantly older than `created` date with no activity
5. Cross-reference with contradiction pages

### Detection Rules

```python
# Pseudocode
for page in wiki_pages:
    if page.status == "invalidated":
        # Check if any active page still references this as valid
        for other_page in wiki_pages:
            if other_page.status == "active" and references(other_page, page):
                report_stale_reference(other_page, page)
    
    # Check for outdated tool versions
    for tool in page.tools:
        if is_outdated_version(tool):
            report_outdated_tool(page, tool)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Active page references invalidated page | Warning |
| Tool version is >2 major versions behind | Info |
| Page not updated in >90 days with status: active | Info |
| Contradiction page exists but no resolution | Warning |

### Remediation

1. Update the stale page with current information
2. Mark as `invalidated` if no longer relevant
3. Create a `contradiction` page if sources conflict
4. Update tool versions in frontmatter

### Example Output

```
[WARNING] Stale reference in synthesis-ad-vulnerability.md:15
  References [[Old Password Policy]] which is invalidated
  Suggested fix: Update reference to [[Password Policy 2026-09]]

[INFO] Outdated tool in entity-targetcorp.md
  nmap 7.94 → Current: 7.95
  Suggested fix: Update tool version in frontmatter
```

---

## 4. Duplicate Detection

**Severity:** Warning

### Check Procedure

1. Extract all page titles
2. Compute similarity scores between titles (Levenshtein distance, Jaccard similarity)
3. Identify pages with overlapping tag sets (>70% shared tags)
4. Report potential duplicates

### Detection Rules

```python
# Pseudocode
for page_a, page_b in combinations(wiki_pages, 2):
    title_similarity = levenshtein_ratio(page_a.title, page_b.title)
    tag_overlap = jaccard_similarity(set(page_a.tags), set(page_b.tags))
    
    if title_similarity > 0.8:
        report_similar_title(page_a, page_b, title_similarity)
    
    if tag_overlap > 0.7 and title_similarity > 0.5:
        report_potential_duplicate(page_a, page_b, tag_overlap)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Title similarity >90% | Warning |
| Title similarity >80% AND tag overlap >70% | Warning |
| Identical titles (case-insensitive) | Critical |
| Tag overlap >90% | Info |

### Remediation

1. Merge duplicate pages (preserve both, add cross-references)
2. Differentiate titles to be more specific
3. Consolidate tags to reduce overlap
4. Add `related` field in frontmatter to link similar pages

### Example Output

```
[WARNING] Potential duplicate: concept-sql-injection.md and concept-sqli.md
  Title similarity: 85%
  Tag overlap: 80%
  Suggested fix: Merge or differentiate titles

[CRITICAL] Duplicate title: "TargetCorp" and "targetcorp"
  Identical titles (case-insensitive)
  Suggested fix: Rename one page
```

---

## 5. Frontmatter Completeness

**Severity:** Critical

### Check Procedure

1. Parse YAML frontmatter from all pages
2. Validate all required fields are present
3. Validate field types and constraints
4. Report missing or invalid fields

### Detection Rules

```python
# Pseudocode
REQUIRED_FIELDS = {
    'title': str,
    'type': ['entity', 'concept', 'synthesis', 'trail', 'timeline', 'overview', 'contradiction'],
    'tags': list,
    'sources': list,
    'created': date,
    'updated': date,
    'confidence': ['high', 'medium', 'low'],
    'provenance': ['tool-proven', 'model-asserted', 'unreviewed'],
    'status': ['active', 'invalidated', 'draft'],
}

for page in wiki_pages:
    frontmatter = parse_frontmatter(page.content)
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in frontmatter:
            report_missing_field(page, field)
        elif not validate_type(frontmatter[field], expected_type):
            report_invalid_field(page, field, expected_type)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Missing required field | Critical |
| Invalid field type | Critical |
| Invalid enum value | Critical |
| Missing optional field | Info |
| Date in future | Warning |
| `updated` < `created` | Critical |

### Remediation

1. Add missing required fields
2. Correct invalid field values
3. Update dates to valid ISO 8601 format
4. Ensure `updated` >= `created`

### Example Output

```
[CRITICAL] Missing required field in concept-sqli.md
  Field: 'provenance'
  Suggested fix: Add provenance: tool-proven

[CRITICAL] Invalid date in entity-targetcorp.md
  Field: 'created'
  Value: '2026-13-45'
  Suggested fix: Use ISO 8601 format (YYYY-MM-DD)
```

---

## 6. Index Coverage

**Severity:** Critical

### Check Procedure

1. Parse `Index.md` for all wikilinks
2. Compare against existing wiki pages
3. Report pages not listed in Index.md
4. Report Index.md entries that don't exist

### Detection Rules

```python
# Pseudocode
index_links = extract_wikilinks(index_page.content)
existing_pages = get_all_page_titles()

for page in existing_pages:
    if page.title != "Index" and page.title not in index_links:
        report_missing_from_index(page)

for link in index_links:
    if link.target not in existing_pages:
        report_broken_index_link(link)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Page not in Index.md | Critical |
| Index.md links to non-existent page | Critical |
| Index.md not found | Critical |
| Page in Index.md but not linked from any other page | Warning |

### Remediation

1. Add missing pages to Index.md
2. Remove or fix broken Index.md links
3. Organize Index.md by category for readability

### Example Output

```
[CRITICAL] Page not in Index.md: concept-advanced-persistence.md
  Suggested fix: Add to Index.md under Concepts section

[CRITICAL] Broken link in Index.md: [[Non-Existent Page]]
  Suggested fix: Remove or create the missing page
```

---

## 7. Provenance Completeness

**Severity:** Warning

### Check Procedure

1. Extract all claims from page content
2. Check if claims have provenance labels
3. Verify frontmatter provenance matches content claims
4. Flag `model-asserted` claims that could be upgraded

### Detection Rules

```python
# Pseudocode
for page in wiki_pages:
    claims = extract_claims(page.content)
    for claim in claims:
        if not has_provenance_label(claim):
            report_missing_provenance(page, claim)
    
    # Check for upgradeable model-asserted claims
    if page.provenance == "model-asserted":
        if has_tool_evidence(page):
            report_upgradeable_provenance(page)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Claim without provenance label | Warning |
| Frontmatter provenance mismatch | Warning |
| `model-asserted` with available tool evidence | Info |
| `unreviewed` pages older than 30 days | Warning |

### Remediation

1. Add provenance labels to all claims
2. Upgrade `model-asserted` to `tool-proven` when evidence available
3. Review and validate `unreviewed` pages
4. Ensure frontmatter provenance reflects highest confidence claim

### Example Output

```
[WARNING] Missing provenance in synthesis-ad-vulnerability.md:23
  Claim: "47 users in Domain Admins"
  Suggested fix: Add [tool-proven] or [model-asserted] label

[INFO] Upgradeable provenance in concept-sqli.md
  Current: model-asserted
  Evidence available in: raw/2026-09-15-burp-sqli.md
  Suggested fix: Update to tool-proven
```

---

## 8. Tag Validity

**Severity:** Critical

### Check Procedure

1. Extract all tags from all pages
2. Compare against approved taxonomy
3. Report invalid tags
4. Suggest valid alternatives

### Detection Rules

```python
# Pseudocode
VALID_TAGS = load_taxonomy("references/tagging-taxonomy.md")

for page in wiki_pages:
    for tag in page.tags:
        if tag not in VALID_TAGS:
            report_invalid_tag(page, tag)
            suggest = find_similar_tag(tag, VALID_TAGS)
            if suggest:
                report_suggestion(page, tag, suggest)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Tag not in taxonomy | Critical |
| Tag is deprecated | Warning |
| Tag is similar to valid tag | Info |
| Missing domain tag | Warning |
| Missing severity tag (for findings) | Warning |

### Remediation

1. Replace invalid tags with valid alternatives
2. Update taxonomy if new tag is needed
3. Add missing domain and severity tags
4. Remove deprecated tags

### Example Output

```
[CRITICAL] Invalid tag in entity-targetcorp.md: 'web-2'
  Not in taxonomy
  Suggested fix: Use 'web2'

[WARNING] Missing domain tag in concept-sqli.md
  Suggested fix: Add 'web2' or 'web3'
```

---

## 9. Page Type Validity

**Severity:** Warning

### Check Procedure

1. Analyze page content structure
2. Compare against expected structure for declared type
3. Report mismatches

### Detection Rules

```python
# Pseudocode
TYPE_INDICATORS = {
    'entity': ['Summary', 'Attributes', 'Findings'],
    'concept': ['Definition', 'Impact', 'Mitigation'],
    'synthesis': ['Question', 'Answer', 'Evidence'],
    'trail': ['Entry Point', 'Attack Chain', 'Impact'],
    'timeline': ['Metadata', 'Phase', 'Findings'],
    'overview': ['Surface', 'Findings', 'Paths'],
    'contradiction': ['Conflict', 'Source A', 'Source B', 'Resolution'],
}

for page in wiki_pages:
    expected_sections = TYPE_INDICATORS.get(page.type, [])
    actual_sections = extract_headings(page.content)
    
    missing = set(expected_sections) - set(actual_sections)
    if missing:
        report_type_mismatch(page, missing)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Missing expected sections for type | Warning |
| Content structure doesn't match type | Warning |
| Type is valid but unusual for content | Info |

### Remediation

1. Add missing sections to match page type
2. Change page type if content doesn't match
3. Restructure content to fit type template

### Example Output

```
[WARNING] Type mismatch in synthesis-ad-vulnerability.md
  Declared type: synthesis
  Missing sections: ['Question', 'Evidence']
  Suggested fix: Add missing sections or change type to 'concept'
```

---

## 10. Cross-Domain Contamination

**Severity:** Critical

### Check Procedure

1. Identify pages with `domain: web2` or `domain: web3`
2. Check for cross-domain references without `cross-domain` tag
3. Verify web2 pages don't contain web3-specific terminology without proper tagging
4. Verify web3 pages don't contain web2-specific terminology without proper tagging

### Detection Rules

```python
# Pseudocode
WEB2_TERMS = ['sql injection', 'xss', 'csrf', 'active directory', 'ldap', 'kerberos']
WEB3_TERMS = ['smart contract', 'solidity', 'evm', 'defi', 'flash loan', 'oracle']

for page in wiki_pages:
    if page.domain == 'web2':
        web3_matches = find_terms(page.content, WEB3_TERMS)
        if web3_matches and 'cross-domain' not in page.tags:
            report_contamination(page, 'web3', web3_matches)
    
    elif page.domain == 'web3':
        web2_matches = find_terms(page.content, WEB2_TERMS)
        if web2_matches and 'cross-domain' not in page.tags:
            report_contamination(page, 'web2', web2_matches)
```

### Severity Levels

| Condition | Severity |
|-----------|----------|
| Web2 page with web3 terms, no cross-domain tag | Critical |
| Web3 page with web2 terms, no cross-domain tag | Critical |
| Cross-domain page without proper tagging | Warning |
| Mixed findings without separation | Warning |

### Remediation

1. Add `cross-domain` tag if page legitimately spans both domains
2. Split page into separate web2 and web3 pages
3. Add explicit cross-reference links between domains
4. Ensure domain tag is accurate

### Example Output

```
[CRITICAL] Cross-domain contamination in concept-sqli.md
  Domain: web2
  Found web3 terms: ['smart contract', 'evm']
  Suggested fix: Add 'cross-domain' tag or remove web3 references
```

---

## Lint Execution

### Running Lint Checks

```bash
# Run all checks
python scripts/wiki-lint.py /path/to/wiki

# Run specific check
python scripts/wiki-lint.py /path/to/wiki --check link-validation

# Output format
python scripts/wiki-lint.py /path/to/wiki --format json
python scripts/wiki-lint.py /path/to/wiki --format markdown
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Warnings found |
| 2 | Critical issues found |
| 3 | Error running lint |

### Automation

Run lint checks:
- Before committing changes
- After ingesting new material
- Weekly during active engagements
- Before generating reports
