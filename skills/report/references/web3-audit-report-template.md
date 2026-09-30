# Web3 Audit Report Template

Web3-specific smart contract security audit report template.

---

## Table of Contents

- [Title Page](#title-page)
- [1. Executive Summary](#1-executive-summary)
  - [1.1 Scope Overview](#11-scope-overview)
  - [1.2 Overall Risk Assessment](#12-overall-risk-assessment)
  - [1.3 Key Findings](#13-key-findings)
  - [1.4 Recommendations](#14-recommendations)
- [2. Scope](#2-scope)
  - [2.1 Contracts Audited](#21-contracts-audited)
  - [2.2 Commit Hashes](#22-commit-hashes)
  - [2.3 Dependencies](#23-dependencies)
  - [2.4 Out of Scope](#24-out-of-scope)
  - [2.5 Assumptions](#25-assumptions)
- [3. Methodology](#3-methodology)
  - [3.1 Audit Approach](#31-audit-approach)
  - [3.2 Tools Used](#32-tools-used)
  - [3.3 Standards Referenced](#33-standards-referenced)
  - [3.4 Terminology](#34-terminology)
- [4. Findings Summary](#4-findings-summary)
  - [Severity Distribution](#severity-distribution)
- [5. Detailed Findings](#5-detailed-findings)
  - [5.1 [FINDING_TITLE]](#51-finding_title)
- [6. Risk Assessment](#6-risk-assessment)
  - [6.1 Category-Level Risk Scoring](#61-category-level-risk-scoring)
  - [6.2 Overall Risk Rating](#62-overall-risk-rating)
- [7. Recommendations](#7-recommendations)
  - [7.1 Immediate Actions (P0)](#71-immediate-actions-p0)
  - [7.2 Short-term Improvements (P1)](#72-short-term-improvements-p1)
  - [7.3 Long-term Recommendations (P2)](#73-long-term-recommendations-p2)
- [8. Appendices](#8-appendices)
  - [Appendix A: Tool Output](#appendix-a-tool-output)
  - [Appendix B: Test Results](#appendix-b-test-results)
  - [Appendix C: Coverage Metrics](#appendix-c-coverage-metrics)
  - [Appendix D: Glossary](#appendix-d-glossary)
  - [Appendix E: References](#appendix-e-references)

---

## Title Page

```markdown
# Smart Contract Security Audit Report

## [PROTOCOL_NAME]

| Field | Value |
|-------|-------|
| **Protocol** | [PROTOCOL_NAME] |
| **Protocol URL** | [URL] |
| **Audit Type** | [Full Audit / Re-audit / Focused Review / Code Review] |
| **Report Date** | [DATE] |
| **Report Version** | [VERSION] |
| **Classification** | [CONFIDENTIAL / RESTRICTED] |
| **Prepared by** | [AUDITOR_NAME], [COMPANY] |
| **Audit Dates** | [START_DATE] – [END_DATE] |
| **Commit Hash** | [COMMIT_HASH] |
| **Blockchain** | [Ethereum / Polygon / Arbitrum / etc.] |
```

---

## 1. Executive Summary

[Written LAST — see executive-summary-guide.md]

### 1.1 Scope Overview

[What was audited: number of contracts, lines of code, chains.]

This audit covered [N] smart contracts totaling approximately [N] lines of Solidity code. The contracts were audited at commit hash [COMMIT_HASH] on the [CHAIN] blockchain.

### 1.2 Overall Risk Assessment

[High-level risk posture.]

The audit identified [N] Critical, [N] High, [N] Medium, [N] Low, and [N] Informational findings. The overall risk rating for this protocol is [LOW / MEDIUM / HIGH / CRITICAL].

### 1.3 Key Findings

[2-3 sentences on the most significant findings.]

The most significant findings include [BRIEF_DESCRIPTION_OF_TOP_FINDINGS]. These issues could potentially allow [POTENTIAL_IMPACT].

### 1.4 Recommendations

[2-3 high-level recommendations.]

We recommend that the protocol team prioritize the following actions: (1) [RECOMMENDATION_1], (2) [RECOMMENDATION_2], and (3) [RECOMMENDATION_3].

---

## 2. Scope

### 2.1 Contracts Audited

| Contract | Address | Lines of Code | Chain | Description |
|----------|---------|---------------|-------|-------------|
| [CONTRACT_NAME] | [ADDRESS] | [LOC] | [CHAIN] | [DESCRIPTION] |
| [CONTRACT_NAME] | [ADDRESS] | [LOC] | [CHAIN] | [DESCRIPTION] |

### 2.2 Commit Hashes

| Repository | Commit Hash | Date |
|------------|-------------|------|
| [REPO_NAME] | [COMMIT_HASH] | [DATE] |

### 2.3 Dependencies

| Dependency | Version | Purpose | Audit Status |
|------------|---------|---------|--------------|
| [DEPENDENCY] | [VERSION] | [PURPOSE] | [Audited / Not Audited] |

### 2.4 Out of Scope

- [ITEM]
- [ITEM]

### 2.5 Assumptions

- The audit assumes the protocol operates on [CHAIN] blockchain.
- The audit assumes the dependencies listed above are secure.
- The audit does not cover [OUT_OF_SCOPE_ITEMS].

---

## 3. Methodology

### 3.1 Audit Approach

| Phase | Activities | Duration |
|-------|-----------|----------|
| Manual Review | Line-by-line code review, architecture analysis | [N] days |
| Automated Analysis | Static analysis, symbolic execution, fuzzing | [N] days |
| Testing | Unit tests, integration tests, PoC development | [N] days |
| Reporting | Finding documentation, remediation guidance | [N] days |

### 3.2 Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Slither | [VERSION] | Static analysis |
| Mythril | [VERSION] | Symbolic execution |
| Echidna | [VERSION] | Fuzzing |
| Foundry | [VERSION] | Unit testing |
| [TOOL_NAME] | [VERSION] | [PURPOSE] |

### 3.3 Standards Referenced

- SWC Registry
- EIP Standards
- [OTHER_STANDARDS]

### 3.4 Terminology

| Term | Definition |
|------|-----------|
| TVL | Total Value Locked |
| TWAP | Time-Weighted Average Price |
| [TERM] | [DEFINITION] |

---

## 4. Findings Summary

| ID | Title | Severity | SWC | Contract | Status |
|----|-------|----------|-----|----------|--------|
| [ID] | [TITLE] | [CRITICAL/HIGH/MEDIUM/LOW/INFO] | [SWC-NNN] | [CONTRACT] | [STATUS] |

**Total findings:** [N] Critical, [N] High, [N] Medium, [N] Low, [N] Informational

### Severity Distribution

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | [N] | [N%] |
| High | [N] | [N%] |
| Medium | [N] | [N%] |
| Low | [N] | [N%] |
| Informational | [N] | [N%] |

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
| **Lines** | [LINE_RANGE] |
| **Provenance** | [tool-proven / model-asserted] |
| **Status** | [Open / Verified / Fixed / Acknowledged] |

#### Description

[What the vulnerability is, how it can be exploited, and potential damage.]

#### Evidence

[Code snippet, transaction hash, tool output — with provenance label.]

```solidity
// Vulnerable code
function vulnerableFunction() external {
    // Vulnerable code here
}
```

#### Impact

[Potential damage in terms of funds, access, or protocol integrity.]

#### Remediation

[Specific, actionable steps to fix the issue.]

```solidity
// Fixed code
function fixedFunction() external {
    // Fixed code here
}
```

#### Proof of Concept

[For Critical/High findings: working PoC with transaction hash or test output.]

```solidity
// PoC test
function testExploit() public {
    // Exploit code
}
```

---

## 6. Risk Assessment

### 6.1 Category-Level Risk Scoring

| Category | Findings | Highest Severity | Risk Level |
|----------|----------|-----------------|------------|
| Access Control | [N] | [SEVERITY] | [RISK] |
| Reentrancy | [N] | [SEVERITY] | [RISK] |
| Oracle Manipulation | [N] | [SEVERITY] | [RISK] |
| Integer Overflow/Underflow | [N] | [SEVERITY] | [RISK] |
| Front-running | [N] | [SEVERITY] | [RISK] |
| Governance | [N] | [SEVERITY] | [RISK] |
| Economic | [N] | [SEVERITY] | [RISK] |
| [CATEGORY] | [N] | [SEVERITY] | [RISK] |

### 6.2 Overall Risk Rating

[LOW / MEDIUM / HIGH / CRITICAL]

**Rationale:** [Explanation of the overall risk rating based on findings.]

---

## 7. Recommendations

### 7.1 Immediate Actions (P0)

| Finding ID | Recommendation | Effort | Priority |
|------------|---------------|--------|----------|
| [ID] | [RECOMMENDATION] | [S/M/L] | P0 |

### 7.2 Short-term Improvements (P1)

| Finding ID | Recommendation | Effort | Priority |
|------------|---------------|--------|----------|
| [ID] | [RECOMMENDATION] | [S/M/L] | P1 |

### 7.3 Long-term Recommendations (P2)

| Finding ID | Recommendation | Effort | Priority |
|------------|---------------|--------|----------|
| [ID] | [RECOMMENDATION] | [S/M/L] | P2 |

---

## 8. Appendices

### Appendix A: Tool Output

[Raw tool output, scanner results.]

```
$ slither .
[INFO] ...
```

### Appendix B: Test Results

[Unit test results, fuzzing results, coverage metrics.]

```
$ forge test
[PASS] testWithdraw() (gas: 12345)
[PASS] testReentrancy() (gas: 23456)
```

### Appendix C: Coverage Metrics

| Metric | Value |
|--------|-------|
| Lines of Code | [N] |
| Functions | [N] |
| Branches Covered | [N%] |
| Lines Covered | [N%] |
| Functions Covered | [N%] |

### Appendix D: Glossary

| Term | Definition |
|------|-----------|
| TVL | Total Value Locked |
| TWAP | Time-Weighted Average Price |
| Reentrancy | A vulnerability where a function can be called recursively before the first call completes |
| Oracle | A service that provides external data to smart contracts |
| [TERM] | [DEFINITION] |

### Appendix E: References

- [SWC Registry](https://swcregistry.io/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [EIP Standards](https://eips.ethereum.org/)
- [OTHER_REFERENCES]
