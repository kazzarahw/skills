---
name: security-report
description: Generates professional security reports across web2 and web3 engagements. Use after assessments, audits, or investigations to produce client-ready deliverables. Covers penetration test reports, audit reports, incident reports, and disclosure documentation with executive summaries, technical findings, severity ratings, and remediation guidance. Use when you need to produce a professional security report or deliverable.
---

# Security Report

Generates professional security reports across web2 and web3 engagements. Produces client-ready deliverables with executive summaries, technical findings, severity ratings, and remediation guidance.

## Constitutional Rules

1. **Never fabricate evidence.** Every claim must trace to captured tool output, a screenshot, or an explicit model-asserted hypothesis labeled as such.
2. **Severity is calculated, not guessed.** Use the appropriate severity scale (CVSS v3.1 for web2, Immunefi for web3) with documented vectors. Do not assign severity by intuition.
3. **Executive summary is written last.** It must reflect the final findings, not assumptions made before analysis.
4. **Deduplicate across tools.** Same host/address/vulnerability from multiple tools is one finding with multiple evidence sources.
5. **Redact sensitive data.** Passwords, tokens, PII, and credentials must be replaced with `[REDACTED]` before the report leaves the engagement environment.
6. **Scope and limitations are legal requirements.** Every report must explicitly state what was tested, what was not, and the constraints under which testing occurred.
7. **Use consistent terminology.** Define terms in the methodology section and use them uniformly throughout.

## Report Types

| Type | Audience | Format | Key Sections |
|------|----------|--------|--------------|
| **Web2 pentest** | C-suite, IT, developers | Markdown/PDF | Exec summary, findings, remediation |
| **Web3 audit** | Protocol team, investors | Markdown/PDF | Exec summary, findings, risk scoring |
| **Incident report** | Legal, PR, executives | Markdown/PDF | Timeline, root cause, impact |
| **Advisory** | Architecture, dev teams | Markdown | Threat model, recommendations |
| **Disclosure** | Protocol team, public | Markdown | Vulnerability, PoC, remediation |

## Report Structure

### Web2 Pentest Report Structure

1. **Title page** — Client name, engagement dates, report version, classification
2. **Executive summary** — Written last; 3-4 paragraphs for non-technical audience
3. **Scope and rules of engagement** — What was tested, constraints, authorization
4. **Methodology** — Testing approach, tools used, standards referenced
5. **Testing narrative** — Chronological account of the engagement
6. **Findings summary table** — At-a-glance view of all findings
7. **Detailed findings** — One section per finding (see Finding Format)
8. **Remediation roadmap** — Time-boxed prioritized recommendations
9. **Appendices** — Tool output, CVSS calculations, reproducible artifacts

### Web3 Audit Report Structure

1. **Title page** — Protocol name, audit dates, report version, classification
2. **Executive summary** — Scope, overall risk, key findings, recommendations
3. **Scope** — Contracts audited, commit hashes, dependencies, chains
4. **Methodology** — Audit approach, tools used, standards referenced
5. **Findings summary table** — At-a-glance view of all findings
6. **Detailed findings** — One section per finding (see Finding Format)
7. **Risk assessment** — Category-level risk scoring
8. **Recommendations** — Prioritized remediation guidance
9. **Appendices** — Tool output, test results, coverage metrics

### Incident Report Structure

1. **Title page** — Incident name, date, report version, classification
2. **Executive summary** — Incident type, impact, status, key findings
3. **Incident timeline** — Chronological reconstruction
4. **Root cause analysis** — Why the incident occurred
5. **Impact assessment** — Quantified impact across categories
6. **Attacker analysis** — Identification and attribution
7. **Evidence package** — Preserved evidence with hashes
8. **Recommendations** — Immediate, short-term, long-term
9. **Appendices** — Raw data, tool queries, chain of custody

## Finding Format

Each detailed finding MUST include all of the following fields:

| Field | Description |
|-------|-------------|
| Reference ID | Unique identifier (format varies by report type) |
| Title | Concise vulnerability name |
| Affected asset | Host, URL, port, contract, or component |
| Severity | Critical / High / Medium / Low / Informational |
| CVSS/Impact | Calculated score with vector string |
| CVE/CWE/SWC | Classification identifier if applicable |
| Description | What the vulnerability is, how it can be exploited, and potential damage |
| Evidence | Tool output, screenshots, or PoC — with provenance label |
| Business impact | What this means for the organization in business terms |
| Remediation | Specific, actionable steps to fix the issue |
| Provenance | `tool-proven` or `model-asserted` |

### Reference ID Formats

**Web2 (OWASP WSTG v4.2):**
```
WSTG-v42-<CATEGORY>-<NN>
```

| Code | Category |
|------|----------|
| INFO | Information Gathering |
| CONF | Configuration and Deployment Management |
| IDNT | Identity Management |
| AUTH | Authentication |
| AUTHZ | Authorization |
| SESS | Session Management |
| INPV | Input Validation |
| ERRH | Error Handling |
| CRYP | Cryptography |
| BUSL | Business Logic |
| CLNT | Client-side |
| API | API Testing |
| FILE | File Uploads |
| CODE | Code Quality |

**Web3 (SWC Registry):**
```
SWC-<NNN>
```

## Provenance Rules

Every finding carries a provenance label following the T3MP3ST pattern:

- **`provenance: tool-proven`** — Backed by captured tool output (screenshot, scan result, HTTP request/response, log entry, transaction hash). The evidence is reproducible.
- **`provenance: model-asserted`** — Hypothesis generated by the tester based on observed behavior but not directly captured in tool output. Must be clearly labeled as unverified.

**Rules:**
- Only `tool-proven` findings can be marked `verified: true`
- `model-asserted` findings must include a note explaining what evidence would be needed to confirm
- Never present a `model-asserted` finding as `tool-proven`
- When in doubt, label as `model-asserted`

## Deduplication Procedure

When multiple tools report the same issue:

1. **Identify duplicates** — Same host/address + port/function + vulnerability type = same finding
2. **Merge evidence** — Combine all tool outputs into a single evidence section, listing each source
3. **Keep highest severity** — If tools disagree on severity, use the highest (most conservative)
4. **Preserve all references** — Keep all CVE/CWE/SWC IDs from all sources
5. **Note the deduplication** — Add a "Also detected by" note listing other tools

## Executive Summary Procedure

Write this section LAST, after all findings are finalized.

**Structure (3-4 paragraphs):**

1. **Engagement overview** — What was tested, when, and at a high level what was found. Avoid specific vulnerability counts or severity labels here.
2. **Business impact** — What the findings mean for the organization. Focus on risk to operations, data, reputation, and compliance. Use plain language.
3. **Strategic recommendations** — 2-3 high-level recommendations that address the root causes rather than individual vulnerabilities.
4. **Positive observations** — What the organization is doing well. This builds trust and provides balance.

**Tone guidelines:**
- Write for a non-technical executive audience
- Avoid jargon, acronyms without explanation, and inflammatory language
- Be direct but not alarmist
- Focus on business risk, not technical detail

## Remediation Roadmap

Organize remediation into time-boxed phases:

| Phase | Timeframe | Focus |
|-------|-----------|-------|
| Immediate | 0-7 days | Critical and High findings; quick wins that block active attack paths |
| Short-term | 1-4 weeks | Medium findings; configuration changes and patching |
| Medium-term | 1-3 months | Low and Informational findings; architectural improvements |
| Strategic | 3+ months | Systemic issues; security program maturity |

Each remediation item must:
- Reference the finding ID(s) it addresses
- Be specific enough for an engineer to act on
- Include an estimated effort level (S/M/L)

## Severity Scales

### Web2: CVSS v3.1

| Score | Rating |
|-------|--------|
| 9.0-10.0 | Critical |
| 7.0-8.9 | High |
| 4.0-6.9 | Medium |
| 0.1-3.9 | Low |
| 0.0 | Informational |

### Web3: Immunefi

| Impact | Rating |
|--------|--------|
| Loss of funds > 10% of TVL | Critical |
| Loss of funds < 10% of TVL | High |
| Temporary fund lock | Medium |
| No direct fund loss | Low |
| Informational | Informational |

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `security-suite` | Orchestration and phase management |
| `security-recon` | Reconnaissance findings |
| `security-audit` | Audit findings |
| `security-exploit` | Exploit findings |
| `security-forensics` | Investigation findings |
| `security-verify` | Verification status |
| `security-coach` | Course correction |
| `security-wiki` | Knowledge persistence |

## Gotchas

- **Never fabricate evidence.** A finding without evidence is worse than no finding — it destroys credibility.
- **Severity is calculated, not guessed.** Always show the CVSS vector and calculation.
- **Executive summary is written last.** Writing it first leads to inconsistencies when findings change.
- **Deduplicate across tools.** Multiple tools finding the same issue is normal; presenting them as separate findings inflates the count and confuses the client.
- **Redact sensitive data.** Passwords, tokens, PII, and credentials must be replaced with `[REDACTED]`.
- **Include reproducible artifacts.** curl commands, HAR files, and PoC scripts allow the client to verify findings independently.
- **Scope and limitations are legal requirements.** Without them, the report has no legal standing and the client cannot verify what was actually tested.
- **Use the templates.** The reference files provide the exact structure. Deviating creates inconsistency across reports.
- **Web3 reports need proof-of-concepts.** Critical and high findings must include working PoCs.
- **Cross-domain findings need clear labeling.** When a finding spans web2 and web3, label both components clearly.

## Output Format

Default output is Markdown. If the client requests PDF or DOCX, convert the Markdown report using the appropriate tool (pandoc for PDF, python-docx for DOCX).

## Report Generation Procedure

1. **Collect findings** — Gather all tool outputs, scan results, and manual observations from the engagement
2. **Deduplicate** — Apply the deduplication procedure to merge overlapping findings
3. **Calculate severity** — For each finding, determine the severity vector and calculate the base score
4. **Assign provenance** — Label each finding as `tool-proven` or `model-asserted` based on available evidence
5. **Write detailed findings** — Populate the finding template for each deduplicated finding
6. **Build remediation roadmap** — Organize remediation steps into time-boxed phases
7. **Write executive summary** — Draft the executive summary based on the finalized findings
8. **Redact** — Scan the entire report for sensitive data and redact
9. **Review** — Verify all findings have complete fields, all evidence has provenance labels, and the report follows the template
10. **Deliver** — Output in the requested format

## Scripts

- `scripts/finding-id-generator.py` — Generate unique, sequential finding IDs
- `scripts/severity-calculator.py` — Calculate CVSS/Immunefi severity
- `scripts/trend-analysis.py` — Analyze findings across engagements
- `scripts/report-redactor.py` — Redact sensitive data from reports

## References

- `references/report-templates.md` — Full report skeletons for all report types
- `references/severity-matrix.md` — CVSS v3.1 and Immunefi score ranges
- `references/remediation-patterns.md` — Remediation guidance by vulnerability type
- `references/compliance-mapping.md` — PCI DSS, HIPAA, ISO 27001 mapping
- `references/executive-summary-guide.md` — Executive summary writing guide
- `references/finding-writing-guide.md` — How to write clear, actionable findings
- `references/web3-audit-report-template.md` — Web3-specific audit report template
- `references/web2-pentest-report-template.md` — Web2-specific pentest report template
- `references/incident-report-template.md` — Incident report template
- `references/disclosure-template.md` — Responsible disclosure template
