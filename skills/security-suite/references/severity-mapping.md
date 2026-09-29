# Severity Mapping

Cross-domain severity mapping between CVSS v3.1 (web2) and Immunefi (web3) severity scales.

## Table of Contents

- [CVSS v3.1 ↔ Immunefi Mapping](#cvss-v31--immunefi-mapping)
- [Mapping Rationale](#mapping-rationale)
  - [Critical (CVSS 9.0-10.0 ↔ Immunefi Critical)](#critical-cvss-90-100--immunefi-critical)
  - [High (CVSS 7.0-8.9 ↔ Immunefi High)](#high-cvss-70-89--immunefi-high)
  - [Medium (CVSS 4.0-6.9 ↔ Immunefi Medium)](#medium-cvss-40-69--immunefi-medium)
  - [Low (CVSS 0.1-3.9 ↔ Immunefi Low)](#low-cvss-01-39--immunefi-low)
  - [Informational (CVSS 0.0 ↔ Immunefi Informational)](#informational-cvss-00--immunefi-informational)
- [Edge Cases and Conflicts](#edge-cases-and-conflicts)
  - [Edge Case 1: Web3 Vulnerability with No Direct Fund Loss](#edge-case-1-web3-vulnerability-with-no-direct-fund-loss)
  - [Edge Case 2: Web2 Vulnerability with Financial Impact](#edge-case-2-web2-vulnerability-with-financial-impact)
  - [Edge Case 3: Web3 Vulnerability with Indirect Fund Loss](#edge-case-3-web3-vulnerability-with-indirect-fund-loss)
  - [Edge Case 4: Mixed Engagement Cross-Component Vulnerabilities](#edge-case-4-mixed-engagement-cross-component-vulnerabilities)
  - [Edge Case 5: CVSS Score Boundary Cases](#edge-case-5-cvss-score-boundary-cases)
  - [Edge Case 6: Web3 Vulnerability with Governance Impact](#edge-case-6-web3-vulnerability-with-governance-impact)
- [Severity Escalation Rules](#severity-escalation-rules)
- [Severity De-escalation Rules](#severity-de-escalation-rules)
- [Severity Justification Template](#severity-justification-template)
- [Cross-Domain Severity Equivalence Table](#cross-domain-severity-equivalence-table)
- [Severity Calibration Guidelines](#severity-calibration-guidelines)
  - [For Web2 (CVSS v3.1)](#for-web2-cvss-v31)
  - [For Web3 (Immunefi)](#for-web3-immunefi)
  - [For Mixed Engagements](#for-mixed-engagements)

---

## CVSS v3.1 ↔ Immunefi Mapping

| CVSS v3.1 Score | CVSS Rating | Immunefi Rating | Immunefi Impact Description |
|-----------------|-------------|-----------------|------------------------------|
| 9.0 — 10.0 | Critical | Critical | Loss of funds > 10% of TVL, or complete system compromise |
| 7.0 — 8.9 | High | High | Loss of funds < 10% of TVL, or significant system impact |
| 4.0 — 6.9 | Medium | Medium | Temporary fund lock, or limited system impact |
| 0.1 — 3.9 | Low | Low | No direct fund loss, minor system impact |
| 0.0 | None | Informational | Informational, no security impact |

---

## Mapping Rationale

### Critical (CVSS 9.0-10.0 ↔ Immunefi Critical)

**CVSS criteria:** Network attack vector, low attack complexity, no privileges required, no user interaction, complete confidentiality/integrity/availability impact.

**Immunefi criteria:** Loss of funds exceeding 10% of TVL, or complete system compromise rendering protocol unusable.

**Rationale:** Both scales represent the most severe impact. In web2, this means complete system compromise. In web3, this means catastrophic fund loss or protocol failure. The 10% TVL threshold aligns with the "complete compromise" concept — losses above this threshold threaten protocol survival.

**Examples:**
- Web2: Unauthenticated remote code execution on production server
- Web3: Any vulnerability allowing drainage of >10% of protocol TVL

### High (CVSS 7.0-8.9 ↔ Immunefi High)

**CVSS criteria:** Network/adjacent attack vector, low/medium attack complexity, no/low privileges required, no/user interaction, high confidentiality/integrity/availability impact.

**Immunefi criteria:** Loss of funds below 10% of TVL, or significant system impact without complete compromise.

**Rationale:** Both scales represent serious but not catastrophic impact. In web2, this means significant data exposure or system compromise. In web3, this means meaningful fund loss that doesn't threaten protocol survival.

**Examples:**
- Web2: SQL injection exposing sensitive user data, authenticated RCE
- Web3: Vulnerability allowing drainage of <10% of TVL, or theft of specific user funds

### Medium (CVSS 4.0-6.9 ↔ Immunefi Medium)

**CVSS criteria:** Network/adjacent/local attack vector, medium attack complexity, low privileges required, no/user interaction, medium confidentiality/integrity/availability impact.

**Immunefi criteria:** Temporary fund lock, or limited system impact with no direct fund loss.

**Rationale:** Both scales represent moderate impact. In web2, this means limited data exposure or partial system compromise. In web3, this means temporary fund unavailability or griefing attacks.

**Examples:**
- Web2: Stored XSS, CSRF, information disclosure
- Web3: Temporary fund lock, griefing, gas griefing, front-running with limited impact

### Low (CVSS 0.1-3.9 ↔ Immunefi Low)

**CVSS criteria:** Local/physical attack vector, high attack complexity, high privileges required, user interaction required, low confidentiality/integrity/availability impact.

**Immunefi criteria:** No direct fund loss, minor system impact.

**Rationale:** Both scales represent minor impact. In web2, this means minimal data exposure or minor security issues. In web3, this means no fund loss but potential minor issues.

**Examples:**
- Web2: Clickjacking, missing security headers, verbose error messages
- Web3: Minor logic errors, gas optimization issues, minor DoS with limited impact

### Informational (CVSS 0.0 ↔ Immunefi Informational)

**CVSS criteria:** No impact on confidentiality, integrity, or availability.

**Immunefi criteria:** Informational, no security impact.

**Rationale:** Both scales represent findings with no direct security impact but potential defense-in-depth improvements.

**Examples:**
- Web2: Information disclosure of non-sensitive data, best practice violations
- Web3: Code quality issues, gas optimization suggestions, architecture observations

---

## Edge Cases and Conflicts

### Edge Case 1: Web3 Vulnerability with No Direct Fund Loss

**Scenario:** A vulnerability that allows griefing or temporary DoS but no fund loss.

**Conflict:** CVSS might rate this Medium (availability impact), but Immunefi might rate it Low (no fund loss).

**Resolution:** Use the **higher** severity. If CVSS says Medium, rate as Medium. The availability impact is real even without fund loss.

### Edge Case 2: Web2 Vulnerability with Financial Impact

**Scenario:** A web2 vulnerability (e.g., payment API flaw) that could lead to financial loss.

**Conflict:** CVSS rates based on CIA impact, but financial loss suggests higher severity.

**Resolution:** Apply **financial impact modifier**. If the vulnerability could cause financial loss >10% of revenue, escalate to Critical. If <10%, escalate to High.

### Edge Case 3: Web3 Vulnerability with Indirect Fund Loss

**Scenario:** A vulnerability that doesn't directly drain funds but could lead to fund loss through secondary effects (e.g., oracle manipulation enabling arbitrage).

**Conflict:** Direct impact is Medium (oracle manipulation), but indirect impact could be High (fund loss).

**Resolution:** Rate based on **realistic worst-case impact**. If the secondary effect is plausible and significant, rate as High.

### Edge Case 4: Mixed Engagement Cross-Component Vulnerabilities

**Scenario:** A vulnerability that spans web2 and web3 components (e.g., frontend vulnerability enabling contract exploitation).

**Conflict:** Different severity scales apply to different components.

**Resolution:** Rate based on **overall impact**. If the cross-component attack leads to fund loss, use Immunefi scale. If it leads to data breach, use CVSS scale. If both, use the **higher** severity.

### Edge Case 5: CVSS Score Boundary Cases

**Scenario:** A vulnerability with CVSS score exactly at a boundary (e.g., 8.9 vs 9.0).

**Conflict:** Small score changes lead to different severity ratings.

**Resolution:** Use **impact subscore** as tiebreaker. If the impact subscore is high, round up. If low, round down. Document the rationale.

### Edge Case 6: Web3 Vulnerability with Governance Impact

**Scenario:** A vulnerability that doesn't directly cause fund loss but compromises governance (e.g., governance takeover).

**Conflict:** No direct fund loss (Low/Informational), but governance compromise could lead to fund loss.

**Resolution:** Rate as **High** if governance compromise could plausibly lead to fund loss. Rate as **Medium** if governance impact is limited.

---

## Severity Escalation Rules

Escalate severity when any of the following conditions are met:

| Rule | Condition | Escalation |
|------|-----------|------------|
| **Financial impact** | Vulnerability could cause financial loss | +1 level |
| **Exploitability** | Exploit is publicly available or trivially exploitable | +1 level |
| **Scope** | Vulnerability affects multiple systems or components | +1 level |
| **Data sensitivity** | Vulnerability exposes highly sensitive data (PII, credentials) | +1 level |
| **Chain reaction** | Vulnerability enables secondary attacks | +1 level |
| **TVL threshold** | Web3 vulnerability approaches 10% TVL loss threshold | +1 level |
| **Regulatory** | Vulnerability has regulatory/compliance implications | +1 level |

**Maximum escalation:** 2 levels above base severity.

---

## Severity De-escalation Rules

De-escalate severity when any of the following conditions are met:

| Rule | Condition | De-escalation |
|------|-----------|---------------|
| **Mitigation exists** | Effective mitigation already in place | -1 level |
| **Exploit complexity** | Exploit requires unrealistic conditions | -1 level |
| **Limited scope** | Vulnerability affects only non-critical component | -1 level |
| **Transient** | Vulnerability is transient or time-limited | -1 level |
| **User interaction** | Exploit requires significant user interaction | -1 level |
| **Privilege requirement** | Exploit requires high-privilege access | -1 level |

**Maximum de-escalation:** 1 level below base severity. Never de-escalate below Informational.

---

## Severity Justification Template

Every severity rating must include this justification:

```
Finding: [Brief description]
Base severity: [CVSS/Immunefi rating]
Base score: [CVSS score or Immunefi impact description]

Escalation factors:
- [Factor 1]: [Explanation]
- [Factor 2]: [Explanation]

De-escalation factors:
- [Factor 1]: [Explanation]

Final severity: [Rating]
Justification: [Summary of rationale]
```

---

## Cross-Domain Severity Equivalence Table

For mixed engagements, use this equivalence table to ensure consistent severity across domains:

| Impact Description | CVSS v3.1 | Immunefi | Combined Rating |
|--------------------|-----------|----------|-----------------|
| Complete system compromise / >10% TVL loss | 9.0-10.0 | Critical | Critical |
| Significant compromise / <10% TVL loss | 7.0-8.9 | High | High |
| Limited compromise / temporary fund lock | 4.0-6.9 | Medium | Medium |
| Minor impact / no fund loss | 0.1-3.9 | Low | Low |
| No security impact | 0.0 | Informational | Informational |

---

## Severity Calibration Guidelines

### For Web2 (CVSS v3.1)

1. **Always use the CVSS v3.1 calculator** — Do not estimate scores manually
2. **Consider environmental metrics** — Adjust based on target environment
3. **Document all metric choices** — Justify each metric selection
4. **Use temporal metrics** — Adjust for available exploits and remediation

### For Web3 (Immunefi)

1. **Assess fund loss potential** — Estimate maximum plausible fund loss
2. **Consider TVL percentage** — Use TVL percentage as primary metric
3. **Evaluate exploitability** — Assess realistic exploit scenarios
4. **Consider protocol context** — Account for protocol-specific risks

### For Mixed Engagements

1. **Rate each component separately** — Use appropriate scale per component
2. **Assess cross-component impact** — Evaluate combined impact
3. **Use highest severity** — Overall finding severity is the highest component severity
4. **Document both ratings** — Include both CVSS and Immunefi ratings where applicable
