# Cross-Engagement Patterns

Pattern recognition across security engagements for institutional learning.

---

## Table of Contents

- [Pattern Recognition Overview](#pattern-recognition-overview)
- [Pattern Categories](#pattern-categories)
  - [1. Recurring Vulnerability Patterns](#1-recurring-vulnerability-patterns)
  - [2. Recurring Attack Paths](#2-recurring-attack-paths)
  - [3. Recurring Misconfigurations](#3-recurring-misconfigurations)
  - [4. Recurring Tool Issues](#4-recurring-tool-issues)
  - [5. Recurring Process Issues](#5-recurring-process-issues)
- [Pattern Detection Approach](#pattern-detection-approach)
- [Pattern Reporting Format](#pattern-reporting-format)
- [Pattern-Based Recommendations](#pattern-based-recommendations)
- [Pattern Lifecycle](#pattern-lifecycle)
- [Integration with Wiki](#integration-with-wiki)

---

## Pattern Recognition Overview

Cross-engagement patterns identify recurring themes, vulnerabilities, and issues across multiple client engagements. This enables:

- **Proactive defense**: Address common issues before they're exploited
- **Efficiency**: Reuse successful techniques and tools
- **Quality**: Identify and fix recurring process issues
- **Knowledge building**: Develop institutional expertise

---

## Pattern Categories

### 1. Recurring Vulnerability Patterns

Same vulnerability type appearing across multiple clients.

#### Detection Approach

Pattern detection is performed by analyzing wiki pages for common vulnerability tags, similar titles, and overlapping content. The following pseudocode illustrates the approach:

```python
# Conceptual approach — not a production script
def find_recurring_vulnerabilities(wiki_pages):
    vuln_patterns = defaultdict(list)
    
    for page in wiki_pages:
        if has_vulnerability_tag(page):
            pattern = extract_vulnerability_pattern(page)
            vuln_patterns[pattern].append({
                'client': page.client,
                'engagement': page.engagement,
                'date': page.created,
                'severity': page.severity
            })
    
    return {k: v for k, v in vuln_patterns.items() if len(v) > 1}
```

#### Common Recurring Vulnerabilities

| Pattern | Typical Root Cause | Prevention |
|---------|-------------------|------------|
| SQL Injection | Lack of input validation | Parameterized queries, WAF |
| XSS | Output encoding gaps | CSP, output encoding |
| Weak Password Policy | Legacy AD policies | Password policy enforcement |
| Unpatched Systems | Patch management gaps | Automated patching |
| Hardcoded Credentials | Poor secret management | Secret scanning, vaults |
| Reentrancy | Unchecked external calls | Reentrancy guards |
| Oracle Manipulation | Spot price dependency | TWAP oracles |

#### Reporting Format

```markdown
## Recurring Pattern: SQL Injection

**Occurrences:** [To be determined from actual data]
**Clients:** [To be determined from actual data]
**Date Range:** [To be determined from actual data]

### Common Characteristics
- [To be determined from actual engagement data]

### Recommended Actions
1. Develop SQLi testing checklist
2. Create reusable detection payloads
3. Build client education material

### Related Pages
- [[SQL Injection]]
- [[OWASP Top 10]]
```

---

### 2. Recurring Attack Paths

Similar attack chains across engagements.

#### Detection Approach

```python
# Conceptual approach — not a production script
def find_recurring_attack_paths(wiki_pages):
    attack_chains = defaultdict(list)
    
    for page in wiki_pages:
        if page.type == 'trail':
            chain_signature = extract_chain_signature(page)
            attack_chains[chain_signature].append({
                'client': page.client,
                'engagement': page.engagement,
                'entry_point': extract_entry_point(page),
                'impact': extract_impact(page)
            })
    
    return {k: v for k, v in attack_chains.items() if len(v) > 1}
```

#### Common Recurring Attack Paths

| Path | Entry Point | Critical Step | Impact |
|------|-------------|---------------|--------|
| Web → DB | SQL Injection | Hardcoded credentials | Full DB compromise |
| Phish → Lateral | Credential theft | Pass-the-Hash | Domain admin |
| API → Data | Broken auth | IDOR | PII exposure |
| Contract → Drain | Reentrancy | Flash loan | Fund drainage |
| Bridge → Exploit | Validator compromise | Message forgery | Cross-chain theft |

#### Reporting Format

```markdown
## Recurring Attack Path: Web App → Database Compromise

**Occurrences:** [To be determined from actual data]
**Clients:** [To be determined from actual data]

### Attack Chain
1. SQL Injection in login form
2. Extract hardcoded credentials from config
3. SSH to database server
4. Full database compromise

### Key Enablers
- [To be determined from actual engagement data]

### Recommended Defenses
1. Implement secrets management
2. Network segmentation
3. Least privilege database access

### Related Pages
- [[SQL Injection]]
- [[Web App Attack Path to DB Compromise]]
```

---

### 3. Recurring Misconfigurations

Common configuration mistakes across engagements.

#### Detection Approach

```python
# Conceptual approach — not a production script
def find_recurring_misconfigurations(wiki_pages):
    misconfigs = defaultdict(list)
    
    for page in wiki_pages:
        if has_misconfiguration_indicator(page):
            config_type = classify_misconfiguration(page)
            misconfigs[config_type].append({
                'client': page.client,
                'engagement': page.engagement,
                'config': extract_config_details(page),
                'impact': page.severity
            })
    
    return {k: v for k, v in misconfigs.items() if len(v) > 1}
```

#### Common Recurring Misconfigurations

| Misconfiguration | Impact | Remediation |
|-----------------|--------|-------------|
| Default credentials | Critical | Credential scanning |
| Open S3 buckets | High | Bucket policy audit |
| Verbose error messages | Medium | Error handling review |
| Missing security headers | Medium | Header enforcement |
| Weak TLS configuration | High | TLS hardening |
| Excessive permissions | High | Permission audit |
| Unnecessary services | Medium | Attack surface reduction |

#### Reporting Format

```markdown
## Recurring Misconfiguration: Default Credentials

**Occurrences:** [To be determined from actual data]

### Affected Services
- [To be determined from actual engagement data]

### Recommended Actions
1. Implement credential scanning in recon phase
2. Create default credential database
3. Add to pre-engagement checklist

### Related Pages
- [[Security Misconfiguration]]
- [[Default Credentials]]
```

---

### 4. Recurring Tool Issues

Tools that consistently produce false positives or miss findings.

#### Detection Approach

```python
# Conceptual approach — not a production script
def find_recurring_tool_issues(wiki_pages):
    tool_issues = defaultdict(lambda: {'false_positives': [], 'misses': []})
    
    for page in wiki_pages:
        if has_tool_feedback(page):
            tool = extract_tool_name(page)
            issue_type = classify_tool_issue(page)
            tool_issues[tool][issue_type].append({
                'client': page.client,
                'engagement': page.engagement,
                'details': extract_issue_details(page)
            })
    
    return tool_issues
```

#### Common Tool Issues

| Tool | Issue Type | Workaround |
|------|------------|------------|
| Nuclei | False positives | Custom templates |
| Nmap | Misses services | Aggressive scan flags |
| Burp Suite | False positives | Manual verification |
| Slither | False positives | Custom detectors |
| Echidna | Misses invariants | Manual invariant review |

#### Reporting Format

```markdown
## Recurring Tool Issue: Nuclei False Positives

**Tool:** Nuclei [version]
**Issue Type:** False Positives

### Common False Positive Patterns
1. [To be determined from actual engagement data]

### Recommended Actions
1. Create custom template exclusions
2. Implement post-scan verification workflow
3. Contribute fixes to Nuclei project

### Related Pages
- [[Nuclei]]
- [[False Positive Management]]
```

---

### 5. Recurring Process Issues

Workflow problems across engagements.

#### Detection Approach

```python
# Conceptual approach — not a production script
def find_recurring_process_issues(wiki_pages):
    process_issues = defaultdict(list)
    
    for page in wiki_pages:
        if has_process_feedback(page):
            issue_type = classify_process_issue(page)
            process_issues[issue_type].append({
                'client': page.client,
                'engagement': page.engagement,
                'phase': extract_phase(page),
                'impact': extract_impact(page)
            })
    
    return process_issues
```

#### Common Recurring Process Issues

| Issue | Phase | Impact |
|-------|-------|--------|
| Incomplete scoping | Pre-engagement | Missed findings |
| Insufficient time for verification | Post-exploitation | False positives |
| Poor handoff between phases | All | Knowledge loss |
| Inconsistent reporting format | Reporting | Client confusion |
| Missing retesting | Post-remediation | Unverified fixes |

#### Reporting Format

```markdown
## Recurring Process Issue: Incomplete Scoping

**Phase:** Pre-engagement

### Common Symptoms
1. Assets discovered during engagement not in scope
2. Third-party integrations not assessed
3. Shadow IT infrastructure missed

### Root Causes
1. Client asset inventory incomplete
2. Scope definition too narrow
3. No pre-engagement recon

### Recommended Actions
1. Implement pre-engagement recon phase
2. Create comprehensive scoping questionnaire
3. Build asset discovery toolkit

### Related Pages
- [[Engagement Scoping]]
- [[Pre-Engagement Reconnaissance]]
```

---

## Pattern Detection Approach

### Similarity Scoring

Pattern detection uses similarity scoring between pages. The following pseudocode illustrates the approach:

```python
# Conceptual approach — not a production script
def calculate_pattern_similarity(page_a, page_b):
    """Calculate similarity score between two pages."""
    scores = {
        'title': levenshtein_ratio(page_a.title, page_b.title),
        'tags': jaccard_similarity(set(page_a.tags), set(page_b.tags)),
        'content': cosine_similarity(
            vectorize(page_a.content),
            vectorize(page_b.content)
        ),
        'type': 1.0 if page_a.type == page_b.type else 0.0,
        'domain': 1.0 if page_a.domain == page_b.domain else 0.0,
    }
    
    weights = {
        'title': 0.2,
        'tags': 0.3,
        'content': 0.3,
        'type': 0.1,
        'domain': 0.1,
    }
    
    return sum(scores[k] * weights[k] for k in scores)
```

### Clustering

```python
# Conceptual approach — not a production script
def cluster_pages(wiki_pages, threshold=0.7):
    """Group similar pages into clusters."""
    clusters = []
    
    for page in wiki_pages:
        assigned = False
        for cluster in clusters:
            if calculate_pattern_similarity(page, cluster['centroid']) > threshold:
                cluster['pages'].append(page)
                cluster['centroid'] = update_centroid(cluster)
                assigned = True
                break
        
        if not assigned:
            clusters.append({
                'centroid': page,
                'pages': [page]
            })
    
    return [c for c in clusters if len(c['pages']) > 1]
```

### Temporal Analysis

```python
# Conceptual approach — not a production script
def analyze_temporal_patterns(patterns):
    """Analyze how patterns evolve over time."""
    timeline = sorted(patterns, key=lambda p: p['date'])
    
    analysis = {
        'first_seen': timeline[0]['date'],
        'last_seen': timeline[-1]['date'],
        'frequency': len(timeline),
        'trend': calculate_trend(timeline),
        'seasonality': detect_seasonality(timeline),
    }
    
    return analysis
```

---

## Pattern Reporting Format

### Executive Summary

```markdown
# Cross-Engagement Pattern Report

**Report Date:** [Date]
**Engagements Analyzed:** [Count]
**Patterns Identified:** [Count]

## Key Findings

1. [To be determined from actual data]
2. [To be determined from actual data]

## Recommendations

1. [To be determined from actual data]
```

### Detailed Pattern Report

```markdown
## Pattern: [Pattern Name]

**Category:** Recurring Vulnerability
**Occurrences:** [Count]
**Confidence:** High
**Trend:** Stable

### Affected Engagements
| Client | Date | Severity | Status |
|--------|------|----------|--------|
| [Client] | [Date] | [Severity] | [Status] |

### Common Characteristics
- [To be determined from actual data]

### Recommended Mitigations
1. [To be determined from actual data]

### Related Pages
- [[Related Page]]
```

---

## Pattern-Based Recommendations

### Automatic Recommendations

When a pattern is detected, generate recommendations:

```python
# Conceptual approach — not a production script
def generate_recommendations(pattern):
    recommendations = []
    
    if pattern['frequency'] >= 3:
        recommendations.append({
            'priority': 'high',
            'action': f"Develop {pattern['name']} testing playbook",
            'rationale': f"Found in {pattern['frequency']} engagements"
        })
    
    if pattern['average_severity'] in ['critical', 'high']:
        recommendations.append({
            'priority': 'high',
            'action': f"Create {pattern['name']} detection signatures",
            'rationale': 'High severity pattern'
        })
    
    if pattern['trend'] == 'increasing':
        recommendations.append({
            'priority': 'medium',
            'action': f"Research {pattern['name']} root causes",
            'rationale': 'Increasing frequency'
        })
    
    return recommendations
```

### Recommendation Tracking

| Recommendation | Pattern | Status | Owner | Due Date |
|---------------|---------|--------|-------|----------|
| [Action] | [Pattern] | [Status] | [Owner] | [Date] |

---

## Pattern Lifecycle

### Pattern States

```
detected → validated → documented → mitigated → resolved
```

### State Transitions

| From | To | Trigger |
|------|----|---------|
| — | `detected` | Pattern first identified |
| `detected` | `validated` | Confirmed across 3+ engagements |
| `validated` | `documented` | Pattern report written |
| `documented` | `mitigated` | Recommendations implemented |
| `mitigated` | `resolved` | Pattern no longer observed |

---

## Integration with Wiki

### Pattern Pages

Create `concept` pages for significant patterns:

```markdown
---
title: "Recurring Pattern: SQL Injection"
type: concept
tags: [web2, pattern, injection, owasp-top10]
sources: ["raw/pattern-analysis-2026-09.md"]
created: 2026-09-29
updated: 2026-09-29
confidence: high
provenance: tool-proven
status: active
domain: web2
severity: critical
---

# Recurring Pattern: SQL Injection

## Pattern Summary
[To be determined from actual engagement data]

## Affected Engagements
- [[TargetCorp]] — 2026-09
- [Other clients to be determined]

## Recommendations
1. Develop SQLi testing playbook
2. Create detection signatures
3. Build client education material

## Related Pages
- [[SQL Injection]]
- [[OWASP Top 10]]
```

### Pattern Index

Add pattern index to `Index.md`:

```markdown
## Cross-Engagement Patterns

- [[Recurring Pattern: SQL Injection]] — [Count] engagements, Critical
- [[Recurring Pattern: Default Credentials]] — [Count] engagements, Critical
```

---

## Automation

### Pattern Detection Script

Pattern detection can be performed using the wiki-lint.py script with custom checks, or by writing a custom script that analyzes wiki pages for recurring patterns.

```bash
# Run lint checks to identify potential patterns
python scripts/wiki-lint.py /path/to/wiki --check duplicates

# Search for similar pages
python scripts/wiki-search.py /path/to/wiki -q "SQL injection" --search-raw
```

### Scheduled Tasks

| Task | Frequency | Command |
|------|-----------|---------|
| Pattern detection | Weekly | `wiki-lint.py --check duplicates` |
| Pattern report | Monthly | Manual review |
| Pattern validation | Quarterly | Manual review |
| Pattern cleanup | Annually | Manual review |
