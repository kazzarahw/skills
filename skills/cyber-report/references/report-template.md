# Penetration Test Report Template

## Title Page

```
[CLASSIFICATION]

Penetration Test Report

Client: [Client Name]
Engagement: [Engagement Name/ID]
Report Version: [X.Y]
Date: [Date]

Prepared by: [Tester Name / Team]
Contact: [Email]

[Company Logo]
```

---

## Table of Contents

1. Executive Summary
2. Scope and Rules of Engagement
3. Methodology
4. Testing Narrative
5. Findings Summary
6. Detailed Findings
7. Remediation Roadmap
8. Appendices

---

## 1. Executive Summary

*Written last. 3-4 paragraphs for non-technical audience.*

### Engagement Overview

[What was tested, when, and at a high level what was found. Avoid specific vulnerability counts or severity labels.]

### Business Impact

[What the findings mean for the organization. Focus on risk to operations, data, reputation, and compliance. Plain language.]

### Strategic Recommendations

[2-3 high-level recommendations addressing root causes rather than individual vulnerabilities.]

### Positive Observations

[What the organization is doing well. Builds trust and provides balance.]

---

## 2. Scope and Rules of Engagement

### 2.1 Scope

| Asset | IP/URL | In Scope | Notes |
|-------|--------|----------|-------|
| [Asset 1] | [IP/URL] | Yes/No | [Notes] |
| [Asset 2] | [IP/URL] | Yes/No | [Notes] |

### 2.2 Out of Scope

- [Explicitly excluded assets or test types]

### 2.3 Rules of Engagement

- **Authorization:** Written authorization obtained on [date] from [authorizing party]
- **Testing window:** [Start date] to [End date], [time constraints if any]
- **Data handling:** All client data handled per [NDA/agreement reference]
- **Escalation contact:** [Name, phone, email]
- **Constraints:** [Any limitations — e.g., no DoS testing, no social engineering, business hours only]

### 2.4 Limitations

- Testing was performed during a limited time window and may not cover all possible attack vectors
- [Any technical limitations — e.g., WAF interference, rate limiting, incomplete crawl]
- Findings represent a point-in-time assessment; the threat landscape evolves continuously

---

## 3. Methodology

### 3.1 Standards and Frameworks

- NIST SP 800-115: Technical Guide to Information Security Testing and Assessment
- OWASP Web Security Testing Guide (WSTG) v4.2
- PTES (Penetration Testing Execution Standard)
- CVSS v3.1 for severity scoring

### 3.2 Testing Approach

| Phase | Activities | Tools |
|-------|-----------|-------|
| Reconnaissance | Passive and active information gathering | [Tools] |
| Enumeration | Service identification, content discovery | [Tools] |
| Vulnerability Analysis | Automated scanning and manual verification | [Tools] |
| Exploitation | Controlled exploitation to validate findings | [Tools] |
| Post-Exploitation | Impact assessment, lateral movement testing | [Tools] |
| Reporting | Report compilation and review | — |

### 3.3 Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| [Tool 1] | [Version] | [Purpose] |
| [Tool 2] | [Version] | [Purpose] |

---

## 4. Testing Narrative

*Chronological account of the engagement.*

### Day 1 — [Date]

[What was done, what was found, key observations.]

### Day 2 — [Date]

[What was done, what was found, key observations.]

---

## 5. Findings Summary

| ID | Title | Asset | Severity | CVSS | Provenance |
|----|-------|-------|----------|------|------------|
| WSTG-v42-XXX-NN | [Title] | [Asset] | Critical/High/Medium/Low/Info | [Score] | tool-proven / model-asserted |

**Summary counts:**

| Severity | Count |
|----------|-------|
| Critical | [N] |
| High | [N] |
| Medium | [N] |
| Low | [N] |
| Informational | [N] |
| **Total** | **[N]** |

---

## 6. Detailed Findings

### Finding: [Title]

| Field | Value |
|-------|-------|
| **Reference ID** | WSTG-v42-[CATEGORY]-[NN] |
| **Affected Asset** | [Host/URL/Port] |
| **Severity** | [Critical/High/Medium/Low/Informational] |
| **CVSS v3.1** | [Score] — [Vector string] |
| **CVE** | [CVE-XXXX-XXXXX or N/A] |
| **CWE** | [CWE-XXX or N/A] |
| **Provenance** | tool-proven / model-asserted |
| **Verified** | true / false |

#### Description

[What the vulnerability is, how it can be exploited, and potential damage. Be specific and technical.]

#### Evidence

**Source:** [Tool name, version, date of capture]

```
[Tool output, HTTP request/response, screenshot reference, or scan result]
```

[Additional evidence sources if applicable]

#### Business Impact

[What this means for the organization in business terms. Connect the technical finding to operational, financial, reputational, or compliance risk.]

#### Remediation

1. [Specific, actionable step]
2. [Specific, actionable step]
3. [Specific, actionable step]

**Effort estimate:** S/M/L

**References:**
- [OWASP Cheat Sheet link]
- [Vendor documentation link]
- [CVE details link]

---

### Finding: [Title]

[Repeat structure for each finding]

---

## 7. Remediation Roadmap

### Immediate (0-7 days)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [Action] | S/M/L | [Role] |

### Short-term (1-4 weeks)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [Action] | S/M/L | [Role] |

### Medium-term (1-3 months)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [Action] | S/M/L | [Role] |

### Strategic (3+ months)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [Action] | S/M/L | [Role] |

---

## 8. Appendices

### Appendix A — CVSS Calculations

| Finding ID | Vector | Base Score | Temporal | Environmental |
|------------|--------|------------|----------|---------------|
| [ID] | [Vector] | [Score] | [Score] | [Score] |

### Appendix B — Reproducible Artifacts

#### [Finding ID] — [Title]

```bash
# Reproduction command
curl -v [URL] -H "[Header]"
```

```http
[Full HTTP request/response]
```

### Appendix C — Tool Output

[Raw tool output referenced in findings]

### Appendix D — Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Author] | Initial release |
