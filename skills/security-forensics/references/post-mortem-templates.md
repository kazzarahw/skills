# Post-Mortem Templates

Templates for documenting incident post-mortems and lessons learned.

## Table of Contents

- [Web2 Incident Post-Mortem Template](#web2-incident-post-mortem-template)
- [Web3 Exploit Post-Mortem Template](#web3-exploit-post-mortem-template)
- [Root Cause Analysis Template](#root-cause-analysis-template)
- [Timeline Template](#timeline-template)
- [Impact Assessment Template](#impact-assessment-template)
- [Recommendations Template](#recommendations-template)

## Web2 Incident Post-Mortem Template

```markdown
# Post-Mortem: [Incident Name]

## Incident Summary

| Field | Value |
|-------|-------|
| Incident ID | INC-2024-XXXX |
| Date | YYYY-MM-DD |
| Duration | X hours |
| Severity | Critical/High/Medium/Low |
| Type | Malware/Ransomware/Data Breach/Insider/Other |
| Status | Resolved/Contained/Active |

## Executive Summary

[2-3 sentence summary of the incident, impact, and resolution]

## Timeline

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | Initial compromise | [Log/Alert] | [Hash/Reference] |
| YYYY-MM-DD HH:MM | Detection | [Alert/Report] | [Alert ID] |
| YYYY-MM-DD HH:MM | Containment | [Action Log] | [Reference] |
| YYYY-MM-DD HH:MM | Eradication | [Action Log] | [Reference] |
| YYYY-MM-DD HH:MM | Recovery | [Action Log] | [Reference] |
| YYYY-MM-DD HH:MM | Resolution | [Action Log] | [Reference] |

## Root Cause Analysis

### What Happened?
[Detailed description of the incident]

### Why Did It Happen?
[Root cause explanation]

### Contributing Factors
- [Factor 1]
- [Factor 2]
- [Factor 3]

### 5 Whys Analysis
1. What happened? — [Answer]
2. Why? — [Answer]
3. Why? — [Answer]
4. Why? — [Answer]
5. Why? — [Answer]

## Impact Assessment

| Category | Impact | Evidence |
|----------|--------|----------|
| Data compromised | [Description] | [Reference] |
| Systems affected | [List] | [Reference] |
| Downtime | [Duration] | [Reference] |
| Financial impact | $[Amount] | [Reference] |
| Reputational impact | [Description] | [Reference] |
| Regulatory impact | [Description] | [Reference] |

## Response Evaluation

### What Went Well
- [Action 1]
- [Action 2]
- [Action 3]

### What Could Be Improved
- [Area 1]
- [Area 2]
- [Area 3]

### Detection Gap
[Why wasn't this detected earlier?]

### Response Time
| Phase | Target | Actual | Variance |
|-------|--------|--------|----------|
| Detection | X min | X min | X min |
| Containment | X min | X min | X min |
| Eradication | X hours | X hours | X hours |
| Recovery | X hours | X hours | X hours |

## Recommendations

### Immediate (0-7 days)
1. [Action item]
2. [Action item]

### Short-term (1-4 weeks)
1. [Action item]
2. [Action item]

### Long-term (1-6 months)
1. [Action item]
2. [Action item]

### Strategic (6+ months)
1. [Action item]
2. [Action item]

## Lessons Learned

### Technical Lessons
- [Lesson 1]
- [Lesson 2]

### Process Lessons
- [Lesson 1]
- [Lesson 2]

### Organizational Lessons
- [Lesson 1]
- [Lesson 2]

## Evidence Package

| Evidence | Hash | Location |
|----------|------|----------|
| Memory capture | [SHA-256] | [Path] |
| Disk image | [SHA-256] | [Path] |
| Log files | [SHA-256] | [Path] |
| Malware samples | [SHA-256] | [Path] |
| Network captures | [SHA-256] | [Path] |

## Appendix

- All commands used
- All tools used
- All queries used
- Chain of custody log
- Glossary of terms
```

## Web3 Exploit Post-Mortem Template

```markdown
# Post-Mortem: [Exploit Name]

## Exploit Summary

| Field | Value |
|-------|-------|
| Incident ID | EXP-2024-XXXX |
| Date | YYYY-MM-DD |
| Protocol | [Protocol Name] |
| Chain | [Chain Name] |
| Type | Reentrancy/Oracle/Flash Loan/Access Control/Other |
| Total Loss | $[Amount] |
| Funds Recovered | $[Amount] ([N]%) |
| Status | Resolved/Contained/Active |

## Executive Summary

[2-3 sentence summary of the exploit, impact, and resolution]

## Exploit Timeline

| Time (UTC) | Event | Tx Hash | Block |
|------------|-------|---------|-------|
| YYYY-MM-DD HH:MM | Initial funding | [Hash] | [Number] |
| YYYY-MM-DD HH:MM | Exploit transaction | [Hash] | [Number] |
| YYYY-MM-DD HH:MM | Fund movement | [Hash] | [Number] |
| YYYY-MM-DD HH:MM | Detection | N/A | N/A |
| YYYY-MM-DD HH:MM | Response | N/A | N/A |
| YYYY-MM-DD HH:MM | Resolution | N/A | N/A |

## Root Cause Analysis

### What Happened?
[Detailed description of the exploit]

### Why Did It Happen?
[Root cause explanation]

### Vulnerability Classification
- [ ] Code bug (logic error)
- [ ] Design flaw (architecture)
- [ ] Oracle manipulation
- [ ] Economic attack
- [ ] Access control
- [ ] Other: [Description]

### 5 Whys Analysis
1. What happened? — [Answer]
2. Why? — [Answer]
3. Why? — [Answer]
4. Why? — [Answer]
5. Why? — [Answer]

## Exploit Transaction Analysis

### Transaction Details
| Field | Value |
|-------|-------|
| Transaction Hash | [Hash] |
| Block Number | [Number] |
| From | [Address] |
| To | [Address] |
| Value | [Amount] |
| Gas Price | [Amount] |
| Gas Used | [Amount] |
| Input Data | [Calldata] |

### Function Called
- Function: [Function name]
- Parameters: [Decoded parameters]
- Calldata: [Raw calldata]

### Event Logs
| Event | Parameters | Decoded |
|-------|------------|---------|
| [Event name] | [Raw] | [Decoded] |

### Internal Transactions
| From | To | Value | Function |
|------|----|-------|----------|
| [Address] | [Address] | [Amount] | [Function] |

## Fund Flow Analysis

### Fund Movement
| Hop | From | To | Amount | Token | Tx Hash |
|-----|------|----|--------|-------|---------|
| 1 | [Address] | [Address] | [Amount] | [Token] | [Hash] |
| 2 | [Address] | [Address] | [Amount] | [Token] | [Hash] |
| 3 | [Address] | [Address] | [Amount] | [Token] | [Hash] |

### Fund Destinations
| Destination | Type | Amount | % of Total |
|-------------|------|--------|------------|
| [Address] | Exchange/Mixer/Bridge/Other | [Amount] | [N]% |
| [Address] | Exchange/Mixer/Bridge/Other | [Amount] | [N]% |

### Value at Time of Exploit
| Token | Amount | Price (USD) | Total (USD) |
|-------|--------|-------------|-------------|
| [Token] | [Amount] | $[Price] | $[Total] |

## Attacker Analysis

### Attacker Addresses
| Address | Role | First Seen | Last Seen |
|---------|------|------------|-----------|
| [Address] | Primary | [Date] | [Date] |
| [Address] | Intermediate | [Date] | [Date] |

### Funding Source
- Source: [CEX/DEX/Bridge/Mixer/Unknown]
- Details: [Description]

### Behavioral Analysis
- Gas pattern: [Description]
- Timing pattern: [Description]
- Contract interactions: [Description]

### Attribution
- Confidence: Speculative/Moderate/High/Confirmed
- Known affiliation: [None/Group name]
- Evidence: [Description]

## Impact Assessment

| Category | Impact | Evidence |
|----------|--------|----------|
| Direct loss | $[Amount] | [Tx hashes] |
| Indirect loss | [Description] | [Reference] |
| Data impact | [Description] | [Reference] |
| Systems affected | [List] | [Reference] |
| Users affected | [Number] | [Reference] |

## Response Evaluation

### What Went Well
- [Action 1]
- [Action 2]

### What Could Be Improved
- [Area 1]
- [Area 2]

### Detection Gap
[Why wasn't this detected by monitoring?]

### Response Time
| Phase | Target | Actual | Variance |
|-------|--------|--------|----------|
| Detection | X min | X min | X min |
| Containment | X min | X min | X min |
| Communication | X hours | X hours | X hours |

## Recommendations

### Immediate (0-7 days)
1. [Action item]
2. [Action item]

### Short-term (1-4 weeks)
1. [Action item]
2. [Action item]

### Long-term (1-6 months)
1. [Action item]
2. [Action item]

### Strategic (6+ months)
1. [Action item]
2. [Action item]

## Lessons Learned

### Technical Lessons
- [Lesson 1]
- [Lesson 2]

### Process Lessons
- [Lesson 1]
- [Lesson 2]

### Economic Lessons
- [Lesson 1]
- [Lesson 2]

## Evidence Package

| Evidence | Hash | Location |
|----------|------|----------|
| Exploit transaction | [SHA-256] | [Path] |
| Event logs | [SHA-256] | [Path] |
| Contract source | [SHA-256] | [Path] |
| Block explorer screenshots | [SHA-256] | [Path] |
| Fund flow analysis | [SHA-256] | [Path] |

## Appendix

- All transaction hashes
- All contract addresses
- All attacker addresses
- Tool queries used
- Chain of custody log
- Glossary of terms
```

## Root Cause Analysis Template

```markdown
# Root Cause Analysis: [Incident Name]

## Problem Statement
[Clear, concise statement of the problem]

## Root Cause

### Primary Root Cause
[The fundamental reason the incident occurred]

### Contributing Factors
1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

## 5 Whys Analysis

### Chain 1: [Aspect]
1. What happened? — [Answer]
2. Why? — [Answer]
3. Why? — [Answer]
4. Why? — [Answer]
5. Why? — [Answer]

### Chain 2: [Aspect]
1. What happened? — [Answer]
2. Why? — [Answer]
3. Why? — [Answer]
4. Why? — [Answer]
5. Why? — [Answer]

## Fishbone Diagram (Ishikawa)

### People
- [Factor]
- [Factor]

### Process
- [Factor]
- [Factor]

### Technology
- [Factor]
- [Factor]

### Environment
- [Factor]
- [Factor]

## Corrective Actions

| Action | Owner | Priority | Due Date | Status |
|--------|-------|----------|----------|--------|
| [Action] | [Name] | High/Medium/Low | [Date] | Open/In Progress/Complete |

## Preventive Measures

| Measure | Owner | Priority | Due Date | Status |
|---------|-------|----------|----------|--------|
| [Measure] | [Name] | High/Medium/Low | [Date] | Open/In Progress/Complete |
```

## Timeline Template

```markdown
# Incident Timeline: [Incident Name]

## Pre-Incident

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Initial Compromise

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Exploitation

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Detection

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Response

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Recovery

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |

## Resolution

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | [Event] | [Source] | [Evidence] |
```

## Impact Assessment Template

```markdown
# Impact Assessment: [Incident Name]

## Direct Impact

| Category | Impact | Evidence |
|----------|--------|----------|
| Financial loss | $[Amount] | [Reference] |
| Data compromised | [Description] | [Reference] |
| Systems affected | [List] | [Reference] |
| Downtime | [Duration] | [Reference] |

## Indirect Impact

| Category | Impact | Evidence |
|----------|--------|----------|
| Reputational damage | [Description] | [Reference] |
| Customer impact | [Description] | [Reference] |
| Regulatory impact | [Description] | [Reference] |
| Legal impact | [Description] | [Reference] |

## Affected Parties

| Party | Impact | Contact |
|-------|--------|---------|
| [Party] | [Description] | [Contact] |

## Recovery Cost

| Category | Cost | Evidence |
|----------|------|----------|
| Incident response | $[Amount] | [Reference] |
| Remediation | $[Amount] | [Reference] |
| Legal fees | $[Amount] | [Reference] |
| Other | $[Amount] | [Reference] |
| **Total** | **$[Amount]** | |

## Total Impact

| Category | Amount |
|----------|--------|
| Direct loss | $[Amount] |
| Indirect loss | $[Amount] |
| Recovery cost | $[Amount] |
| **Total impact** | **$[Amount]** |
```

## Recommendations Template

```markdown
# Recommendations: [Incident Name]

## Immediate Actions (0-7 days)

| # | Action | Owner | Priority | Due Date | Status |
|---|--------|-------|----------|----------|--------|
| 1 | [Action] | [Name] | Critical | [Date] | Open |
| 2 | [Action] | [Name] | Critical | [Date] | Open |

## Short-term Actions (1-4 weeks)

| # | Action | Owner | Priority | Due Date | Status |
|---|--------|-------|----------|----------|--------|
| 1 | [Action] | [Name] | High | [Date] | Open |
| 2 | [Action] | [Name] | High | [Date] | Open |

## Long-term Actions (1-6 months)

| # | Action | Owner | Priority | Due Date | Status |
|---|--------|-------|----------|----------|--------|
| 1 | [Action] | [Name] | Medium | [Date] | Open |
| 2 | [Action] | [Name] | Medium | [Date] | Open |

## Strategic Actions (6+ months)

| # | Action | Owner | Priority | Due Date | Status |
|---|--------|-------|----------|----------|--------|
| 1 | [Action] | [Name] | Low | [Date] | Open |
| 2 | [Action] | [Name] | Low | [Date] | Open |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| [Metric] | [Target] | [Current] | On Track/At Risk/Behind |
```
