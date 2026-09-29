# Incident Report Template

Security incident report template.

---

## Table of Contents

- [Title Page](#title-page)
- [1. Executive Summary](#1-executive-summary)
  - [1.1 Incident Type](#11-incident-type)
  - [1.2 Impact Summary](#12-impact-summary)
  - [1.3 Current Status](#13-current-status)
  - [1.4 Key Findings](#14-key-findings)
- [2. Incident Timeline](#2-incident-timeline)
  - [Timeline Notes](#timeline-notes)
- [3. Root Cause Analysis](#3-root-cause-analysis)
  - [3.1 Root Cause](#31-root-cause)
  - [3.2 Contributing Factors](#32-contributing-factors)
  - [3.3 Attack Vector](#33-attack-vector)
  - [3.4 5 Whys Analysis](#34-5-whys-analysis)
- [4. Impact Assessment](#4-impact-assessment)
  - [4.1 Data Impact](#41-data-impact)
  - [4.2 System Impact](#42-system-impact)
  - [4.3 Business Impact](#43-business-impact)
  - [4.4 Affected Parties](#44-affected-parties)
- [5. Attacker Analysis](#5-attacker-analysis)
  - [5.1 Attribution](#51-attribution)
  - [5.2 TTPs (Tactics, Techniques, and Procedures)](#52-ttps-tactics-techniques-and-procedures)
  - [5.3 Indicators of Compromise (IOCs)](#53-indicators-of-compromise-iocs)
  - [5.4 Attack Chain](#54-attack-chain)
- [6. Evidence Package](#6-evidence-package)
  - [6.1 Preserved Evidence](#61-preserved-evidence)
  - [6.2 Chain of Custody](#62-chain-of-custody)
  - [6.3 Evidence Handling](#63-evidence-handling)
- [7. Recommendations](#7-recommendations)
  - [7.1 Immediate (0-7 days)](#71-immediate-0-7-days)
  - [7.2 Short-term (1-4 weeks)](#72-short-term-1-4-weeks)
  - [7.3 Long-term (1-3 months)](#73-long-term-1-3-months)
  - [7.4 Strategic (3+ months)](#74-strategic-3-months)
- [8. Appendices](#8-appendices)
  - [Appendix A: Raw Data](#appendix-a-raw-data)
  - [Appendix B: Tool Queries](#appendix-b-tool-queries)
  - [Appendix C: Chain of Custody Forms](#appendix-c-chain-of-custody-forms)
  - [Appendix D: Glossary](#appendix-d-glossary)
  - [Appendix E: References](#appendix-e-references)

---

## Title Page

```markdown
# Security Incident Report

## [INCIDENT_NAME]

| Field | Value |
|-------|-------|
| **Incident Name** | [INCIDENT_NAME] |
| **Incident ID** | [INCIDENT_ID] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL / RESTRICTED] |
| **Prepared by** | [INVESTIGATOR_NAME], [COMPANY] |
| **Incident Dates** | [START_DATE] – [END_DATE] |
| **Severity** | [CRITICAL/HIGH/MEDIUM/LOW] |
| **Status** | [OPEN / CONTAINED / ERADICATED / RECOVERED / CLOSED] |
```

---

## 1. Executive Summary

### 1.1 Incident Type

[Data breach / Unauthorized access / Malware / DDoS / Insider threat / etc.]

### 1.2 Impact Summary

[Quantified impact: records affected, systems compromised, downtime duration.]

On [DATE], [ORGANIZATION] experienced a [INCIDENT_TYPE] that affected [SYSTEMS_AFFECTED]. The incident resulted in [QUANTIFIED_IMPACT]. The total estimated impact is [FINANCIAL_IMPACT].

### 1.3 Current Status

[Contained / Eradicated / Recovered / Monitoring / Closed]

The incident was [CONTAINED/ERADICATED] on [DATE]. [CURRENT_STATUS_DETAILS].

### 1.4 Key Findings

[2-3 sentences on the most significant findings.]

The investigation revealed that [KEY_FINDING_1]. Additionally, [KEY_FINDING_2]. The root cause was identified as [ROOT_CAUSE].

---

## 2. Incident Timeline

| Timestamp (UTC) | Event | Source | Evidence |
|-----------------|-------|--------|----------|
| [TIMESTAMP] | [EVENT] | [SOURCE] | [EVIDENCE_ID] |
| [TIMESTAMP] | [EVENT] | [SOURCE] | [EVIDENCE_ID] |

### Timeline Notes

[Additional context for the timeline, if needed.]

---

## 3. Root Cause Analysis

### 3.1 Root Cause

[Why the incident occurred.]

The root cause of this incident was [ROOT_CAUSE]. This allowed the attacker to [WHAT_THEY_DID].

### 3.2 Contributing Factors

- [FACTOR_1]
- [FACTOR_2]
- [FACTOR_3]

### 3.3 Attack Vector

[How the attacker gained access.]

The attacker gained access through [ATTACK_VECTOR]. This involved [ATTACK_STEPS].

### 3.4 5 Whys Analysis

| Level | Question | Answer |
|-------|----------|--------|
| 1 | Why did the incident occur? | [ANSWER] |
| 2 | Why did that happen? | [ANSWER] |
| 3 | Why did that happen? | [ANSWER] |
| 4 | Why did that happen? | [ANSWER] |
| 5 | Why did that happen? | [ANSWER] |

---

## 4. Impact Assessment

### 4.1 Data Impact

| Category | Records Affected | Sensitivity | Regulatory Impact |
|----------|-----------------|-------------|-------------------|
| [CATEGORY] | [N] | [LEVEL] | [YES/NO] |

### 4.2 System Impact

| System | Downtime | Data Loss | Data Exposure |
|--------|----------|-----------|---------------|
| [SYSTEM] | [DURATION] | [YES/NO] | [YES/NO] |

### 4.3 Business Impact

| Category | Impact | Estimated Cost |
|----------|--------|----------------|
| Financial | [DESCRIPTION] | $[AMOUNT] |
| Reputational | [DESCRIPTION] | [DESCRIPTION] |
| Operational | [DESCRIPTION] | [DESCRIPTION] |
| Regulatory | [DESCRIPTION] | [DESCRIPTION] |
| Legal | [DESCRIPTION] | [DESCRIPTION] |

### 4.4 Affected Parties

| Party | Count | Notification Required | Notification Sent |
|-------|-------|----------------------|-------------------|
| Customers | [N] | [YES/NO] | [YES/NO] |
| Employees | [N] | [YES/NO] | [YES/NO] |
| Partners | [N] | [YES/NO] | [YES/NO] |
| Regulators | [N] | [YES/NO] | [YES/NO] |

---

## 5. Attacker Analysis

### 5.1 Attribution

[Known / Suspected / Unknown]

[ATTRIBUTION_DETAILS]

### 5.2 TTPs (Tactics, Techniques, and Procedures)

| Tactic | Technique | Tool | MITRE ATT&CK ID |
|--------|-----------|------|-----------------|
| [TACTIC] | [TECHNIQUE] | [TOOL] | [ID] |

### 5.3 Indicators of Compromise (IOCs)

| Type | Value | Context | First Seen |
|------|-------|---------|------------|
| IP | [IP_ADDRESS] | [CONTEXT] | [DATE] |
| Domain | [DOMAIN] | [CONTEXT] | [DATE] |
| Hash | [HASH] | [CONTEXT] | [DATE] |
| Email | [EMAIL] | [CONTEXT] | [DATE] |

### 5.4 Attack Chain

```
[RECONNAISSANCE] → [WEAPONIZATION] → [DELIVERY] → [EXPLOITATION] → [INSTALLATION] → [COMMAND_AND_CONTROL] → [ACTIONS_ON_OBJECTIVES]
```

---

## 6. Evidence Package

### 6.1 Preserved Evidence

| Evidence ID | Description | Type | Hash (SHA-256) | Size | Location |
|-------------|-------------|------|-----------------|------|----------|
| [EVIDENCE_ID] | [DESCRIPTION] | [TYPE] | [HASH] | [SIZE] | [LOCATION] |

### 6.2 Chain of Custody

| Timestamp | Action | Performer | Location | Notes |
|-----------|--------|-----------|----------|-------|
| [TIMESTAMP] | [ACTION] | [NAME] | [LOCATION] | [NOTES] |

### 6.3 Evidence Handling

- All evidence was collected following [EVIDENCE_PROCEDURE].
- Evidence was stored in [STORAGE_LOCATION] with [ACCESS_CONTROLS].
- Access to evidence is restricted to [AUTHORIZED_PERSONNEL].

---

## 7. Recommendations

### 7.1 Immediate (0-7 days)

| ID | Recommendation | Owner | Status | Due Date |
|----|---------------|-------|--------|----------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] | [DATE] |

### 7.2 Short-term (1-4 weeks)

| ID | Recommendation | Owner | Status | Due Date |
|----|---------------|-------|--------|----------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] | [DATE] |

### 7.3 Long-term (1-3 months)

| ID | Recommendation | Owner | Status | Due Date |
|----|---------------|-------|--------|----------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] | [DATE] |

### 7.4 Strategic (3+ months)

| ID | Recommendation | Owner | Status | Due Date |
|----|---------------|-------|--------|----------|
| [ID] | [RECOMMENDATION] | [OWNER] | [STATUS] | [DATE] |

---

## 8. Appendices

### Appendix A: Raw Data

[Raw logs, packet captures, etc.]

```
[RAW_DATA]
```

### Appendix B: Tool Queries

[Queries used for investigation.]

```sql
-- Example query
SELECT * FROM logs WHERE timestamp BETWEEN '[START]' AND '[END]' AND event_type = '[TYPE]';
```

### Appendix C: Chain of Custody Forms

[Detailed chain of custody documentation.]

### Appendix D: Glossary

| Term | Definition |
|------|-----------|
| IOC | Indicator of Compromise |
| TTP | Tactics, Techniques, and Procedures |
| [TERM] | [DEFINITION] |

### Appendix E: References

- [NIST SP 800-61](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [OTHER_REFERENCES]
