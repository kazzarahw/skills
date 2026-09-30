# Responsible Disclosure Template

Vulnerability disclosure template for responsible disclosure to vendors/protocols.

---

## Table of Contents

- [Title Page](#title-page)
- [1. Vulnerability Summary](#1-vulnerability-summary)
- [2. Technical Details](#2-technical-details)
  - [2.1 Description](#21-description)
  - [2.2 Root Cause](#22-root-cause)
  - [2.3 Affected Code](#23-affected-code)
  - [2.4 Affected Components](#24-affected-components)
- [3. Proof of Concept](#3-proof-of-concept)
  - [3.1 Steps to Reproduce](#31-steps-to-reproduce)
  - [3.2 Evidence](#32-evidence)
  - [3.3 PoC Code](#33-poc-code)
- [4. Impact](#4-impact)
  - [4.1 Technical Impact](#41-technical-impact)
  - [4.2 Business Impact](#42-business-impact)
  - [4.3 Affected Users](#43-affected-users)
- [5. Remediation](#5-remediation)
  - [5.1 Recommended Fix](#51-recommended-fix)
  - [5.2 Alternative Fixes](#52-alternative-fixes)
  - [5.3 Verification Steps](#53-verification-steps)
- [6. Timeline](#6-timeline)
- [7. Contact Information](#7-contact-information)
- [8. Additional Information](#8-additional-information)
  - [8.1 References](#81-references)
  - [8.2 Acknowledgments](#82-acknowledgments)
  - [8.3 Disclosure Policy](#83-disclosure-policy)

---

## Title Page

```markdown
# Vulnerability Disclosure

## [VULNERABILITY_TITLE]

| Field | Value |
|-------|-------|
| **Vulnerability** | [VULNERABILITY_TITLE] |
| **Disclosure Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL — UNTIL DISCLOSURE DATE] |
| **Prepared by** | [RESEARCHER_NAME] |
| **Contact** | [EMAIL] |
| **PGP Key** | [KEY_ID] |
```

---

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Title** | [VULNERABILITY_TITLE] |
| **Severity** | [CRITICAL/HIGH/MEDIUM/LOW/INFO] |
| **Affected Component** | [COMPONENT_NAME] |
| **Affected Versions** | [VERSION_RANGE] |
| **CVE** | [CVE-ID or Pending] |
| **CWE** | [CWE-XXX] |
| **SWC** | [SWC-NNN] (if web3) |
| **CVSS v3.1** | [SCORE] — [VECTOR_STRING] (if web2) |

---

## 2. Technical Details

### 2.1 Description

[What the vulnerability is.]

[Provide a clear, concise description of the vulnerability. Explain what the issue is, where it exists, and why it is a security concern.]

### 2.2 Root Cause

[Why the vulnerability exists.]

[Explain the root cause of the vulnerability. This should be specific and technical, pointing to the exact code or configuration that causes the issue.]

### 2.3 Affected Code

[Code snippet showing the vulnerable code.]

```solidity
// Vulnerable code
function vulnerableFunction() external {
    // Vulnerable code here
}
```

### 2.4 Affected Components

| Component | Version | Impact |
|-----------|---------|--------|
| [COMPONENT] | [VERSION] | [IMPACT] |

---

## 3. Proof of Concept

### 3.1 Steps to Reproduce

1. [STEP_1]
2. [STEP_2]
3. [STEP_3]

### 3.2 Evidence

[Transaction hash, test output, or screenshot.]

**Transaction Hash:** [TX_HASH]
**Block Number:** [BLOCK_NUMBER]
**Timestamp:** [TIMESTAMP]

```
[TOOL_OUTPUT_OR_TRANSACTION_DETAILS]
```

### 3.3 PoC Code

[Working proof of concept code.]

```solidity
// PoC test
function testExploit() public {
    // Exploit code
}
```

---

## 4. Impact

[Potential damage if exploited.]

### 4.1 Technical Impact

[What an attacker can achieve: unauthorized access, data theft, fund loss, etc.]

### 4.2 Business Impact

[What this means for the organization: financial loss, reputational damage, regulatory fines, etc.]

### 4.3 Affected Users

[Who is affected and how many users.]

| User Group | Count | Impact |
|------------|-------|--------|
| [GROUP] | [N] | [IMPACT] |

---

## 5. Remediation

[Suggested fix.]

### 5.1 Recommended Fix

[Specific, actionable fix.]

```solidity
// Fixed code
function fixedFunction() external {
    // Fixed code here
}
```

### 5.2 Alternative Fixes

[If applicable, alternative remediation approaches.]

| Approach | Pros | Cons |
|----------|------|------|
| [APPROACH_1] | [PROS] | [CONS] |
| [APPROACH_2] | [PROS] | [CONS] |

### 5.3 Verification Steps

[How to verify the fix works.]

1. [VERIFICATION_STEP_1]
2. [VERIFICATION_STEP_2]

---

## 6. Timeline

| Date | Event | Notes |
|------|-------|-------|
| [DATE] | Discovered | [NOTES] |
| [DATE] | Disclosed to vendor | [NOTES] |
| [DATE] | Vendor acknowledged | [NOTES] |
| [DATE] | Fix developed | [NOTES] |
| [DATE] | Fix confirmed | [NOTES] |
| [DATE] | Public disclosure | [NOTES] |

---

## 7. Contact Information

| Field | Value |
|-------|-------|
| **Researcher** | [NAME] |
| **Email** | [EMAIL] |
| **PGP Key** | [KEY_ID] |
| **PGP Fingerprint** | [FINGERPRINT] |
| **Twitter** | [TWITTER_HANDLE] |
| **Website** | [WEBSITE] |

---

## 8. Additional Information

### 8.1 References

- [REFERENCE_1]
- [REFERENCE_2]

### 8.2 Acknowledgments

[If applicable, acknowledge any assistance received during research.]

### 8.3 Disclosure Policy

[Reference the vendor's disclosure policy, if applicable.]

---

## Usage Notes

- Replace all `[PLACEHOLDER]` values with actual data.
- Remove sections that do not apply.
- For web3 disclosures, include transaction hashes and contract addresses.
- For web2 disclosures, include CVSS scores and CWE IDs.
- Keep the tone professional and non-confrontational.
- Do not publicly disclose before the agreed disclosure date.
- Encrypt sensitive communications using the vendor's PGP key if available.
