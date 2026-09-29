# Page Schema

Complete frontmatter schema, page templates, naming conventions, and tag taxonomy for the cyber-wiki.

## Frontmatter Schema

Every wiki page MUST include all required fields. Optional fields provide additional context.

### Required Fields

```yaml
---
title: "Page Title"                    # Human-readable title
type: entity | concept | synthesis | trail | timeline | overview | contradiction
tags: []                               # At least one tag
sources: []                            # Source file paths or references
created: YYYY-MM-DD                    # Creation date
updated: YYYY-MM-DD                    # Last update date
confidence: high | medium | low        # Confidence in page content
provenance: tool-proven | model-asserted | unreviewed
status: active | invalidated | draft   # Current validity
---
```

### Optional Fields

```yaml
---
# ... required fields above ...
engagement: "TargetCorp-2026-09"       # Engagement identifier
author: "agent-name"                   # Creating agent
related: []                            # Related page titles
supersedes: "Old Page Title"           # Page this replaces (if invalidated)
---
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable page title |
| `type` | enum | Page type (see below) |
| `tags` | array | Categorization tags |
| `sources` | array | Source file paths or references |
| `created` | date | Page creation date (YYYY-MM-DD) |
| `updated` | date | Last modification date (YYYY-MM-DD) |
| `confidence` | enum | Confidence level: high, medium, low |
| `provenance` | enum | Verification level: tool-proven, model-asserted, unreviewed |
| `status` | enum | Validity: active, invalidated, draft |
| `engagement` | string | Engagement identifier (optional) |
| `author` | string | Creating agent (optional) |
| `related` | array | Related page titles (optional) |
| `supersedes` | string | Invalidated page this replaces (optional) |

## Page Types

### entity

People, organizations, projects, targets.

```yaml
---
title: "TargetCorp"
type: entity
tags: [target, organization]
sources: []
created: 2026-09-28
updated: 2026-09-28
confidence: high
provenance: tool-proven
status: active
---
```

### concept

Vulnerability classes, techniques, methodologies.

```yaml
---
title: "SQL Injection"
type: concept
tags: [vulnerability, web, injection]
sources: []
created: 2026-09-28
updated: 2026-09-28
confidence: high
provenance: tool-proven
status: active
---
```

### synthesis

Saved query answers, analysis results.

```yaml
---
title: "Why TargetCorp's AD is vulnerable"
type: synthesis
tags: [analysis, ad, targetcorp]
sources: ["raw/nmap/2026-09-28-targetcorp-ad.md"]
created: 2026-09-28
updated: 2026-09-28
confidence: medium
provenance: model-asserted
status: active
---
```

### trail

Associative paths through related pages.

```yaml
---
title: "Web App Attack Path to DB Compromise"
type: trail
tags: [attack-path, web, database]
sources: []
created: 2026-09-28
updated: 2026-09-28
confidence: medium
provenance: model-asserted
status: active
---
```

### timeline

Chronological hubs for engagements.

```yaml
---
title: "Engagement: TargetCorp 2026-09"
type: timeline
tags: [engagement, targetcorp, timeline]
sources: []
created: 2026-09-28
updated: 2026-09-28
confidence: high
provenance: tool-proven
status: active
---
```

### overview

Cluster landscapes for domains.

```yaml
---
title: "TargetCorp Attack Surface"
type: overview
tags: [targetcorp, attack-surface, overview]
sources: []
created: 2026-09-28
updated: 2026-09-28
confidence: high
provenance: tool-proven
status: active
---
```

### contradiction

Conflict analysis between sources.

```yaml
---
title: "Port 443: HTTP vs HTTPS discrepancy"
type: contradiction
tags: [contradiction, network, targetcorp]
sources: ["raw/nmap/2026-09-28-targetcorp-443.md", "raw/burp/2026-09-28-targetcorp-443.md"]
created: 2026-09-28
updated: 2026-09-28
confidence: high
provenance: tool-proven
status: active
---
```

## Naming Conventions

### File Names

- Lowercase with hyphens: `targetcorp-overview.md`
- Date prefix for raw files: `2026-09-28-targetcorp-nmap.md`
- No spaces, no special characters except hyphens

### Page Titles

- Descriptive and specific: "TargetCorp Web Application" not "Web App"
- Include context when needed: "SQL Injection (TargetCorp Login)"
- Use consistent terminology across pages

### Tags

- Lowercase, hyphenated: `attack-surface`, `web-vulnerability`
- Hierarchical when useful: `targetcorp`, `targetcorp-web`, `targetcorp-network`
- Maximum 5 tags per page

## Tag Taxonomy

### Engagement Tags
- `engagement` — General engagement marker
- `targetcorp` — TargetCorp engagement
- `engagement-name` — Specific engagement identifier

### Domain Tags
- `network` — Network-related findings
- `web` — Web application findings
- `ad` — Active Directory findings
- `cloud` — Cloud infrastructure findings
- `physical` — Physical security findings
- `social` — Social engineering findings

### Type Tags
- `vulnerability` — Vulnerability findings
- `technique` — Attack techniques
- `tool` — Tool-related pages
- `methodology` — Methodology pages
- `analysis` — Analysis results
- `contradiction` — Contradiction pages

### Status Tags
- `validated` — Verified findings
- `unvalidated` — Unverified findings
- `deprecated` — Outdated but preserved
- `draft` — Work in progress

## Page Templates

### Entity Template

```markdown
---
title: "Entity Name"
type: entity
tags: [entity-type, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Entity Name

## Summary
Brief description of the entity.

## Attributes
- **Type**: Person | Organization | Project | Target
- **Domain**: Relevant domain
- **First Seen**: YYYY-MM-DD

## Observations
- [YYYY-MM-DD] Observation with provenance

## Relationships
- Links to related pages

## Sources
- List of source files
```

### Concept Template

```markdown
---
title: "Concept Name"
type: concept
tags: [concept-type, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Concept Name

## Definition
Clear definition of the concept.

## Characteristics
- Key characteristics

## Examples
- Real-world examples

## Mitigation
- How to mitigate or defend

## Related Concepts
- Links to related pages

## Sources
- List of source files
```

### Synthesis Template

```markdown
---
title: "Synthesis Title"
type: synthesis
tags: [analysis, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Synthesis Title

## Question
What question does this answer?

## Answer
Synthesized answer with evidence.

## Evidence
- Supporting evidence with provenance

## Confidence Assessment
Why this confidence level?

## Related Pages
- Links to related pages
```

### Trail Template

```markdown
---
title: "Trail Name"
type: trail
tags: [path, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Trail Name

## Purpose
What does this trail represent?

## Path
1. [[Page 1]] → [[Page 2]] → [[Page 3]]

## Observations
- Key observations along the trail

## Alternative Paths
- Other ways to traverse the same domain
```

### Timeline Template

```markdown
---
title: "Engagement: Name YYYY-MM"
type: timeline
tags: [engagement, timeline]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Engagement: Name YYYY-MM

## Overview
Brief engagement summary.

## Phases
### Phase 1: Discovery (YYYY-MM-DD)
- Activities and findings

### Phase 2: Exploitation (YYYY-MM-DD)
- Activities and findings

## Key Findings
- Summary of important findings

## Related Pages
- Links to related pages
```

### Overview Template

```markdown
---
title: "Domain Overview"
type: overview
tags: [overview, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Domain Overview

## Scope
What does this overview cover?

## Components
- List of components in the domain

## Relationships
- How components relate to each other

## Risk Assessment
- Overall risk posture

## Related Pages
- Links to related pages
```

### Contradiction Template

```markdown
---
title: "Contradiction: Brief Description"
type: contradiction
tags: [contradiction, domain]
sources: []
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
provenance: tool-proven | model-asserted | unreviewed
status: active
---

# Contradiction: Brief Description

## Conflict
Description of the conflicting information.

## Source A
- Claim from source A
- Evidence

## Source B
- Claim from source B
- Evidence

## Analysis
- Why the conflict exists
- Possible resolutions

## Resolution
- How it was resolved (if applicable)
- Or: Why it remains unresolved
```
