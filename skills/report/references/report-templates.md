# Report Templates

Full report skeletons for all report types. Copy the relevant template and replace all `[PLACEHOLDER]` values.

---

## Table of Contents

1. [Web2 Pentest Report Template](#web2-pentest-report-template)
2. [Web3 Audit Report Template](#web3-audit-report-template)
3. [Incident Report Template](#incident-report-template)
4. [Advisory Report Template](#advisory-report-template)
5. [Disclosure Template](#disclosure-template)

---

## Web2 Pentest Report Template

```markdown
# Penetration Test Report

## Title Page

| Field | Value |
|-------|-------|
| **Client** | [CLIENT_NAME] |
| **Engagement** | [ENGAGEMENT_NAME] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL / RESTRICTED / CLIENT CONFIDENTIAL] |
| **Prepared by** | [TESTER_NAME], [COMPANY] |
| **Engagement Dates** | [START_DATE] – [END_DATE] |

---

## 1. Executive Summary

[Written LAST — see executive-summary-guide.md]

### 1.1 Engagement Overview

[2-3 sentences: what was tested, when, high-level outcome. No vulnerability counts or severity labels.]

### 1.2 Business Impact

[2-3 sentences: what findings mean for operations, data, reputation, compliance. Plain language.]

### 1.3 Strategic Recommendations

[2-3 high-level recommendations addressing root causes, not individual vulnerabilities.]

### 1.4 Positive Observations

[1-2 sentences: what the organization is doing well.]

---

## 2. Scope and Rules of Engagement

### 2.1 In-Scope Targets

| Target | Type | Description |
|--------|------|-------------|
| [TARGET_1] | [Web App / API / Network / etc.] | [DESCRIPTION] |
| [TARGET_2] | [TYPE] | [DESCRIPTION] |

### 2.2 Out-of-Scope Targets

| Target | Reason |
|--------|--------|
| [TARGET] | [REASON] |

### 2.3 Rules of Engagement

- **Testing window:** [START_DATE] [START_TIME] – [END_DATE] [END_TIME] ([TIMEZONE])
- **Testing type:** [Black box / Gray box / White box]
- **Authorization:** Signed penetration testing agreement dated [DATE]
- **Constraints:** [Rate limiting, denial-of-service exclusions, etc.]
- **Data handling:** [How test data was handled and destroyed]

### 2.4 Limitations

- Testing was conducted during a limited time window and does not guarantee discovery of all vulnerabilities.
- [Any specific limitations: no social engineering, no physical testing, etc.]
- Findings represent a point-in-time assessment; the threat landscape evolves continuously.

---

## 3. Methodology

### 3.1 Standards Referenced

- OWASP Web Security Testing Guide (WSTG) v4.2
- NIST SP 800-115 Technical Guide to Information Security Testing
- PTES (Penetration Testing Execution Standard)

### 3.2 Testing Approach

| Phase | Activities | Tools |
|-------|-----------|-------|
| Reconnaissance | [DESCRIPTION] | [TOOL_NAMES] |
| Enumeration | [DESCRIPTION] | [TOOL_NAMES] |
| Vulnerability Discovery | [DESCRIPTION] | [TOOL_NAMES] |
| Exploitation | [DESCRIPTION] | [TOOL_NAMES] |
| Post-Exploitation | [DESCRIPTION] | [TOOL_NAMES] |
| Reporting | [DESCRIPTION] | [TOOL_NAMES] |

### 3.3 Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| [TOOL_NAME] | [VERSION] | [PURPOSE] |

### 3.4 Terminology

| Term | Definition |
|------|-----------|
| [TERM] | [DEFINITION] |

---

## 4. Testing Narrative

[Chronological account of the engagement. Include dates, key observations, and turning points.]

### Day 1 — [DATE]
- [Observation]
- [Observation]

### Day 2 — [DATE]
- [Observation]

---

## 5. Findings Summary

| ID | Title | Severity | CVSS | Asset | Status |
|----|-------|----------|------|-------|--------|
| [ID] | [TITLE] | [CRITICAL/HIGH/MEDIUM/LOW/INFO] | [SCORE] | [ASSET] | [STATUS] |

**Total findings:** [N] Critical, [N] High, [N] Medium, [N] Low, [N] Informational

---

## 6. Detailed Findings

### 6.1 [FINDING_TITLE]

| Field | Value |
|-------|-------|
| **Reference ID** | [WSTG-v42-CATEGORY-NN] |
| **Severity** | [CRITICAL/HIGH/MEDIUM/LOW/INFO] |
| **CVSS v3.1** | [SCORE] — [VECTOR_STRING] |
| **CWE** | [CWE-XXX] |
| **WSTG** | [WSTG-CATEGORY-NN] |
| **Affected Asset** | [HOST/URL/PORT] |
| **Provenance** | [tool-proven / model-asserted] |
| **Status** | [Open / Verified / Fixed / Accepted Risk] |

#### Description

[What the vulnerability is, how it can be exploited, and potential damage.]

#### Evidence

[Tool output, screenshots, HTTP request/response — with provenance label.]

```
[TOOL_OUTPUT]
```

#### Business Impact

[What this means for the organization in business terms.]

#### Remediation

[Specific, actionable steps to fix the issue.]

#### Also Detected By

[If deduplicated: list other tools that found this issue.]

---

## 7. Remediation Roadmap

### Phase 1: Immediate (0-7 days)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [ACTION] | [S/M/L] | [TEAM] |

### Phase 2: Short-term (1-4 weeks)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [ACTION] | [S/M/L] | [TEAM] |

### Phase 3: Medium-term (1-3 months)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [ACTION] | [S/M/L] | [TEAM] |

### Phase 4: Strategic (3+ months)

| Finding ID | Remediation Action | Effort | Owner |
|------------|-------------------|--------|-------|
| [ID] | [ACTION] | [S/M/L] | [TEAM] |

---

## 8. Appendices

### Appendix A: CVSS Calculations

| Finding ID | Vector String | Base Score | Temporal | Environmental |
|------------|--------------|------------|----------|---------------|
| [ID] | [VECTOR] | [SCORE] | [SCORE] | [SCORE] |

### Appendix B: Tool Output

[Raw tool output, scan results, etc.]

### Appendix C: Reproducible Artifacts

[curl commands, HAR files, PoC scripts]

### Appendix D: Glossary

| Term | Definition |
|------|-----------|
| [TERM] | [DEFINITION] |
```

---

## Web3 Audit Report Template

```markdown
# Smart Contract Security Audit Report

## Title Page

| Field | Value |
|-------|-------|
| **Protocol** | [PROTOCOL_NAME] |
| **Audit Type** | [Full Audit / Re-audit / Focused Review] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL / RESTRICTED] |
| **Prepared by** | [AUDITOR_NAME], [COMPANY] |
| **Audit Dates** | [START_DATE] – [END_DATE] |

---

## 1. Executive Summary

[Written LAST — see executive-summary-guide.md]

### 1.1 Scope Overview

[What was audited: number of contracts, lines of code, chains.]

### 1.2 Overall Risk Assessment

[High-level risk posture.]

### 1.3 Key Findings

[2-3 sentences on the most significant findings.]

### 1.4 Recommendations

[2-3 high-level recommendations.]

---

## 2. Scope

### 2.1 Contracts Audited

| Contract | Address | Lines of Code | Chain |
|----------|---------|---------------|-------|
| [CONTRACT_NAME] | [ADDRESS] | [LOC] | [CHAIN] |

### 2.2 Commit Hashes

| Repository | Commit Hash |
|------------|-------------|
| [REPO_NAME] | [COMMIT_HASH] |

### 2.3 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| [DEPENDENCY] | [VERSION] | [PURPOSE] |

### 2.4 Out of Scope

- [ITEM]
- [ITEM]

---

## 3. Methodology

### 3.1 Audit Approach

| Phase | Activities |
|-------|-----------|
| Manual Review | [DESCRIPTION] |
| Automated Analysis | [DESCRIPTION] |
| Testing | [DESCRIPTION] |
| Reporting | [DESCRIPTION] |

### 3.2 Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| [TOOL_NAME] | [VERSION] | [PURPOSE] |

### 3.3 Standards Referenced

- SWC Registry
- EIP Standards
- [OTHER_STANDARDS]

---

## 4. Findings Summary

| ID | Title | Severity | SWC | Contract | Status |
|----|-------|----------|-----|----------|--------|
| [ID] | [TITLE] | [CRITICAL/HIGH/MEDIUM/LOW/INFO] | [SWC-NNN] | [CONTRACT] | [STATUS] |

**Total findings:** [N] Critical, [N] High, [N] Medium, [N] Low, [N] Informational

---

## 5. Detailed Findings

### 5.1 [FINDING_TITLE]

| Field | Value |
|-------|-------|
| **Reference ID** | [SWC-NNN] |
| **Severity** | [CRITICAL/HIGH/MEDIUM/LOW/INFO] |
| **SWC** | [SWC-NNN] |
| **Contract** | [CONTRACT_NAME] |
| **Function** | [FUNCTION_NAME] |
| **Provenance** | [tool-proven / model-asserted] |
| **Status** | [Open / Verified / Fixed / Acknowledged] |

#### Description

[What the vulnerability is, how it can be exploited, and potential damage.]

#### Evidence

[Code snippet, transaction hash, tool output — with provenance label.]

```solidity
[CODE_SNIPPET]
```

#### Impact

[Potential damage in terms of funds, access, or protocol integrity.]

#### Remediation

[Specific, actionable steps to fix the issue.]

#### Proof of Concept

[For Critical/High findings: working PoC with transaction hash or test output.]

---

## 6. Risk Assessment

### 6.1 Category-Level Risk Scoring

| Category | Findings | Highest Severity | Risk Level |
|----------|----------|-----------------|------------|
| Access Control | [N] | [SEVERITY] | [RISK] |
| Reentrancy | [N] | [SEVERITY] | [RISK] |
| Oracle Manipulation | [N] | [SEVERITY] | [RISK] |
| [CATEGORY] | [N] | [SEVERITY] | [RISK] |

### 6.2 Overall Risk Rating

[LOW / MEDIUM / HIGH / CRITICAL]

---

## 7. Recommendations

### 7.1 Immediate Actions

| Finding ID | Recommendation | Priority |
|------------|---------------|----------|
| [ID] | [RECOMMENDATION] | [P0/P1/P2] |

### 7.2 Short-term Improvements

| Finding ID | Recommendation | Priority |
|------------|---------------|----------|
| [ID] | [RECOMMENDATION] | [P0/P1/P2] |

### 7.3 Long-term Recommendations

| Finding ID | Recommendation | Priority |
|------------|---------------|----------|
| [ID] | [RECOMMENDATION] | [P0/P1/P2] |

---

## 8. Appendices

### Appendix A: Tool Output

[Raw tool output, scanner results.]

### Appendix B: Test Results

[Unit test results, fuzzing results, coverage metrics.]

### Appendix C: Coverage Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | [N] |
| Functions | [N] |
| Branches Covered | [N%] |
| Lines Covered | [N%] |

### Appendix D: Glossary

| Term | Definition |
|------|-----------|
| [TERM] | [DEFINITION] |
```

---

## Incident Report Template

```markdown
# Security Incident Report

## Title Page

| Field | Value |
|-------|-------|
| **Incident Name** | [INCIDENT_NAME] |
| **Incident ID** | [INCIDENT_ID] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL / RESTRICTED] |
| **Prepared by** | [INVESTIGATOR_NAME], [COMPANY] |
| **Incident Dates** | [START_DATE] – [END_DATE] |

---

## 1. Executive Summary

### 1.1 Incident Type

[Data breach / Unauthorized access / Malware / DDoS / etc.]

### 1.2 Impact Summary

[Quantified impact: records affected, systems compromised, downtime duration.]

### 1.3 Current Status

[Contained / Eradicated / Recovered / Monitoring]

### 1.4 Key Findings

[2-3 sentences on the most significant findings.]

---

## 2. Incident Timeline

| Timestamp (UTC) | Event | Source |
|-----------------|-------|--------|
| [TIMESTAMP] | [EVENT] | [SOURCE] |
| [TIMESTAMP] | [EVENT] | [SOURCE] |

---

## 3. Root Cause Analysis

### 3.1 Root Cause

[Why the incident occurred.]

### 3.2 Contributing Factors

- [FACTOR]
- [FACTOR]

### 3.3 Attack Vector

[How the attacker gained access.]

---

## 4. Impact Assessment

### 4.1 Data Impact

| Category | Records Affected | Sensitivity |
|----------|-----------------|-------------|
| [CATEGORY] | [N] | [LEVEL] |

### 4.2 System Impact

| System | Downtime | Data Loss |
|--------|----------|-----------|
| [SYSTEM] | [DURATION] | [YES/NO] |

### 4.3 Business Impact

| Category | Impact |
|----------|--------|
| Financial | [DESCRIPTION] |
| Reputational | [DESCRIPTION] |
| Operational | [DESCRIPTION] |
| Regulatory | [DESCRIPTION] |

---

## 5. Attacker Analysis

### 5.1 Attribution

[Known / Suspected / Unknown]

### 5.2 TTPs

| Tactic | Technique | Tool |
|--------|-----------|------|
| [TACTIC] | [TECHNIQUE] | [TOOL] |

### 5.3 Indicators of Compromise

| Type | Value | Context |
|------|-------|---------|
| [IP/Hash/Domain] | [VALUE] | [CONTEXT] |

---

## 6. Evidence Package

### 6.1 Preserved Evidence

| Evidence ID | Description | Hash (SHA-256) | Location |
|-------------|-------------|-----------------|----------|
| [EVIDENCE_ID] | [DESCRIPTION] | [HASH] | [LOCATION] |

### 6.2 Chain of Custody

| Timestamp | Action | Performer | Notes |
|-----------|--------|-----------|-------|
| [TIMESTAMP] | [ACTION] | [NAME] | [NOTES] |

---

## 7. Recommendations

### 7.1 Immediate (0-7 days)

| ID | Recommendation | Owner | Status |
|----|---------------|-------|--------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] |

### 7.2 Short-term (1-4 weeks)

| ID | Recommendation | Owner | Status |
|----|---------------|-------|--------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] |

### 7.3 Long-term (1-3 months)

| ID | Recommendation | Owner | Status |
|----|---------------|-------|--------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] |

---

## 8. Appendices

### Appendix A: Raw Data

[Raw logs, packet captures, etc.]

### Appendix B: Tool Queries

[Queries used for investigation.]

### Appendix C: Chain of Custody Forms

[Detailed chain of custody documentation.]
```

---

## Advisory Report Template

```markdown
# Security Advisory Report

## Title Page

| Field | Value |
|-------|-------|
| **Client** | [CLIENT_NAME] |
| **Advisory Topic** | [TOPIC] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL] |
| **Prepared by** | [ADVISOR_NAME], [COMPANY] |

---

## 1. Executive Summary

### 1.1 Purpose

[Why this advisory was commissioned.]

### 1.2 Key Findings

[2-3 sentences on the most significant findings.]

### 1.3 Recommendations

[2-3 high-level recommendations.]

---

## 2. Background

[Context for the advisory.]

---

## 3. Threat Model

### 3.1 Assets

| Asset | Value | Criticality |
|-------|-------|-------------|
| [ASSET] | [VALUE] | [CRITICALITY] |

### 3.2 Threat Actors

| Actor | Motivation | Capability |
|-------|-----------|------------|
| [ACTOR] | [MOTIVATION] | [CAPABILITY] |

### 3.3 Attack Surface

| Vector | Exposure | Likelihood |
|--------|----------|------------|
| [VECTOR] | [EXPOSURE] | [LIKELIHOOD] |

---

## 4. Findings

### 4.1 [FINDING_TITLE]

| Field | Value |
|-------|-------|
| **Severity** | [HIGH/MEDIUM/LOW] |
| **Category** | [CATEGORY] |
| **Description** | [DESCRIPTION] |
| **Recommendation** | [RECOMMENDATION] |

---

## 5. Recommendations

### 5.1 Strategic Recommendations

| ID | Recommendation | Priority | Timeline |
|----|---------------|----------|----------|
| [ID] | [RECOMMENDATION] | [P0/P1/P2] | [TIMELINE] |

### 5.2 Tactical Recommendations

| ID | Recommendation | Priority | Timeline |
|----|---------------|----------|----------|
| [ID] | [RECOMMENDATION] | [P0/P1/P2] | [TIMELINE] |

---

## 6. Appendices

### Appendix A: References

[References to standards, frameworks, etc.]

### Appendix B: Glossary

| Term | Definition |
|------|-----------|
| [TERM] | [DEFINITION] |
```

---

## Disclosure Template

```markdown
# Vulnerability Disclosure

## Title Page

| Field | Value |
|-------|-------|
| **Vulnerability** | [VULNERABILITY_TITLE] |
| **Disclosure Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL — UNTIL DISCLOSURE DATE] |
| **Prepared by** | [RESEARCHER_NAME] |

---

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Title** | [VULNERABILITY_TITLE] |
| **Severity** | [CRITICAL/HIGH/MEDIUM/LOW/INFO] |
| **Affected Component** | [COMPONENT_NAME] |
| **Affected Versions** | [VERSION_RANGE] |
| **CVE** | [CVE-ID or Pending] |

---

## 2. Technical Details

### 2.1 Description

[What the vulnerability is.]

### 2.2 Root Cause

[Why the vulnerability exists.]

### 2.3 Affected Code

```solidity
[CODE_SNIPPET]
```

---

## 3. Proof of Concept

### 3.1 Steps to Reproduce

1. [STEP]
2. [STEP]

### 3.2 Evidence

[Transaction hash, test output, or screenshot.]

---

## 4. Impact

[Potential damage if exploited.]

---

## 5. Remediation

[Suggested fix.]

---

## 6. Timeline

| Date | Event |
|------|-------|
| [DATE] | Discovered |
| [DATE] | Disclosed to vendor |
| [DATE] | Fix confirmed |
| [DATE] | Public disclosure |

---

## 7. Contact Information

| Field | Value |
|-------|-------|
| **Researcher** | [NAME] |
| **Email** | [EMAIL] |
| **PGP Key** | [KEY_ID] |
```

---

## Usage Notes

- Replace all `[PLACEHOLDER]` values with actual data.
- Remove sections that do not apply to the engagement.
- Keep the structure consistent across reports for the same client.
- The executive summary is always written last.
- All findings must have provenance labels.
- All sensitive data must be redacted before delivery.
