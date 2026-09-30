# Severity Scales Reference

Comprehensive reference for CVSS v3.1 and Immunefi severity scales, including calculation procedures and cross-domain mapping.

---

## Table of Contents

- [CVSS v3.1](#cvss-v31)
  - [Base Metrics](#base-metrics)
  - [Base Score Calculation](#base-score-calculation)
  - [Temporal Metrics](#temporal-metrics)
  - [Environmental Metrics](#environmental-metrics)
  - [CVSS Vector String Format](#cvss-vector-string-format)
  - [CVSS Severity Ratings](#cvss-severity-ratings)
- [Immunefi Severity](#immunefi-severity)
  - [Critical](#critical)
  - [High](#high)
  - [Medium](#medium)
  - [Low](#low)
  - [Informational](#informational)
- [Cross-Domain Mapping](#cross-domain-mapping)
  - [CVSS to Immunefi Mapping](#cvss-to-immunefi-mapping)
  - [Web2 to Web3 Mapping](#web2-to-web3-mapping)
- [Severity Calculation Procedures](#severity-calculation-procedures)
  - [Web2 Severity Calculation](#web2-severity-calculation)
  - [Web3 Severity Calculation](#web3-severity-calculation)
  - [Severity Calculation Example](#severity-calculation-example)
- [Severity Assessment Checklist](#severity-assessment-checklist)
  - [Web2](#web2)
  - [Web3](#web3)
  - [Cross-Domain](#cross-domain)

---

## CVSS v3.1

### Base Metrics

#### Attack Vector (AV)

| Value | Description | Score |
|-------|-------------|-------|
| **N** | Network | 0.85 |
| **A** | Adjacent network | 0.62 |
| **L** | Local | 0.55 |
| **P** | Physical | 0.20 |

#### Attack Complexity (AC)

| Value | Description | Score |
|-------|-------------|-------|
| **L** | Low | 0.77 |
| **H** | High | 0.44 |

#### Privileges Required (PR)

| Value | Description | Score (Scope Changed) | Score (Scope Unchanged) |
|-------|-------------|----------------------|------------------------|
| **N** | None | 0.85 | 0.85 |
| **L** | Low | 0.68 | 0.62 |
| **H** | High | 0.50 | 0.27 |

#### User Interaction (UI)

| Value | Description | Score |
|-------|-------------|-------|
| **N** | None | 0.85 |
| **R** | Required | 0.62 |

#### Scope (S)

| Value | Description |
|-------|-------------|
| **U** | Unchanged |
| **C** | Changed |

#### Confidentiality (C)

| Value | Description | Score |
|-------|-------------|-------|
| **N** | None | 0.00 |
| **L** | Low | 0.22 |
| **H** | High | 0.56 |

#### Integrity (I)

| Value | Description | Score |
|-------|-------------|-------|
| **N** | None | 0.00 |
| **L** | Low | 0.22 |
| **H** | High | 0.56 |

#### Availability (A)

| Value | Description | Score |
|-------|-------------|-------|
| **N** | None | 0.00 |
| **L** | Low | 0.22 |
| **H** | High | 0.56 |

### Base Score Calculation

```
Impact = 1 - [(1 - C) × (1 - I) × (1 - A)]

If Scope is Unchanged:
    Impact = 6.42 × Impact
If Scope is Changed:
    Impact = 7.52 × (Impact - 0.029) - 3.25 × (Impact - 0.02)^15

Exploitability = 8.22 × AV × AC × PR × UI

If Impact <= 0:
    Base Score = 0
If Scope is Unchanged:
    Base Score = RoundUp(min(Impact + Exploitability, 10))
If Scope is Changed:
    Base Score = RoundUp(min(1.08 × (Impact + Exploitability), 10))
```

### Temporal Metrics

#### Exploit Code Maturity (E)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **U** | Unproven | 0.91 |
| **P** | Proof-of-concept | 0.94 |
| **F** | Functional | 0.97 |
| **H** | High | 1.00 |

#### Remediation Level (RL)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **O** | Official fix | 0.95 |
| **T** | Temporary fix | 0.96 |
| **W** | Workaround | 0.97 |
| **U** | Unavailable | 1.00 |

#### Report Confidence (RC)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **U** | Unknown | 0.92 |
| **R** | Reasonable | 0.96 |
| **C** | Confirmed | 1.00 |

### Environmental Metrics

#### Confidentiality Requirement (CR)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **L** | Low | 0.50 |
| **M** | Medium | 1.00 |
| **H** | High | 1.50 |

#### Integrity Requirement (IR)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **L** | Low | 0.50 |
| **M** | Medium | 1.00 |
| **H** | High | 1.50 |

#### Availability Requirement (AR)

| Value | Description | Score |
|-------|-------------|-------|
| **X** | Not defined | 1.00 |
| **L** | Low | 0.50 |
| **M** | Medium | 1.00 |
| **H** | High | 1.50 |

### CVSS Vector String Format

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

Format:
CVSS:3.1/AV:[AV]/AC:[AC]/PR:[PR]/UI:[UI]/S:[S]/C:[C]/I:[I]/A:[A]

With Temporal:
CVSS:3.1/AV:[AV]/AC:[AC]/PR:[PR]/UI:[UI]/S:[S]/C:[C]/I:[I]/A:[A]/E:[E]/RL:[RL]/RC:[RC]

With Environmental:
CVSS:3.1/AV:[AV]/AC:[AC]/PR:[PR]/UI:[UI]/S:[S]/C:[C]/I:[I]/A:[A]/E:[E]/RL:[RL]/RC:[RC]/CR:[CR]/IR:[IR]/AR:[AR]/MAV:[MAV]/MAC:[MAC]/MPR:[MPR]/MUI:[MUI]/MS:[MS]/MC:[MC]/MI:[MI]/MA:[MA]
```

### CVSS Severity Ratings

| Score Range | Severity |
|-------------|----------|
| 0.0 | None |
| 0.1 - 3.9 | Low |
| 4.0 - 6.9 | Medium |
| 7.0 - 8.9 | High |
| 9.0 - 10.0 | Critical |

---

## Immunefi Severity

### Critical

**Impact:** Loss of funds, permanent freezing of funds, or complete compromise of the protocol.

**Criteria:**
- Direct theft of funds
- Permanent freezing of user funds
- Complete protocol compromise
- Governance takeover with fund drainage
- Oracle manipulation leading to massive loss

**Examples:**
- Reentrancy draining all funds
- Flash loan attack draining protocol
- Governance attack with fund drainage
- Private key compromise

### High

**Impact:** Loss of funds, temporary freezing of funds, or significant protocol disruption.

**Criteria:**
- Theft of a portion of funds
- Temporary freezing of funds
- Significant protocol disruption
- Oracle manipulation leading to moderate loss
- Access control bypass

**Examples:**
- IDOR accessing other users' funds
- Price manipulation affecting protocol
- Reentrancy on specific functions
- Missing access control on sensitive functions

### Medium

**Impact:** Limited loss of funds, minor protocol disruption, or degradation of service.

**Criteria:**
- Limited loss of funds
- Minor protocol disruption
- Degradation of service
- Information disclosure
- DoS on specific functions

**Examples:**
- Information disclosure
- DoS on non-critical functions
- Minor price manipulation
- Missing input validation

### Low

**Impact:** Minimal impact, no loss of funds, or very limited protocol disruption.

**Criteria:**
- Minimal impact
- No loss of funds
- Very limited protocol disruption
- Code quality issues
- Best practice violations

**Examples:**
- Code quality issues
- Best practice violations
- Minor gas optimization
- Missing events

### Informational

**Impact:** No direct security impact, but represents a potential risk or deviation from best practices.

**Criteria:**
- No direct security impact
- Potential risk
- Deviation from best practices
- Educational value

**Examples:**
- Potential future risks
- Best practice recommendations
- Code quality improvements
- Documentation issues

---

## Cross-Domain Mapping

### CVSS to Immunefi Mapping

| CVSS Score | CVSS Severity | Immunefi Severity | Notes |
|------------|---------------|-------------------|-------|
| 9.0 - 10.0 | Critical | Critical | Direct fund loss, complete compromise |
| 7.0 - 8.9 | High | High | Significant fund loss, major disruption |
| 4.0 - 6.9 | Medium | Medium | Limited fund loss, minor disruption |
| 0.1 - 3.9 | Low | Low | Minimal impact, no fund loss |
| 0.0 | None | Informational | No security impact |

### Web2 to Web3 Mapping

| Web2 Vulnerability | CVSS Range | Web3 Equivalent | Immunefi Severity |
|-------------------|------------|-----------------|-------------------|
| SQL Injection | 9.0 - 10.0 | Reentrancy | Critical |
| RCE | 9.0 - 10.0 | Flash Loan Attack | Critical |
| Auth Bypass | 7.0 - 8.9 | Access Control Bypass | High |
| IDOR | 7.0 - 8.9 | IDOR | High |
| XSS (Stored) | 6.1 - 8.0 | N/A | Medium |
| SSRF | 5.0 - 7.9 | Oracle Manipulation | Medium |
| CSRF | 4.0 - 6.9 | N/A | Medium |
| Information Disclosure | 2.0 - 4.9 | Information Disclosure | Low |
| Missing Headers | 0.1 - 3.9 | N/A | Low |

---

## Severity Calculation Procedures

### Web2 Severity Calculation

```
1. Identify vulnerability type
2. Determine CVSS base metrics:
   - Attack Vector (AV)
   - Attack Complexity (AC)
   - Privileges Required (PR)
   - User Interaction (UI)
   - Scope (S)
   - Confidentiality (C)
   - Integrity (I)
   - Availability (A)
3. Calculate base score
4. Apply temporal metrics (if applicable)
5. Apply environmental metrics (if applicable)
6. Map to severity rating
```

### Web3 Severity Calculation

```
1. Identify vulnerability type
2. Assess impact:
   - Can it lead to direct fund loss? → Critical
   - Can it lead to temporary fund freezing? → High
   - Can it lead to limited fund loss? → Medium
   - Is it a code quality issue? → Low
   - Is it informational? → Informational
3. Assess likelihood:
   - Is it easily exploitable? → Increase severity
   - Does it require specific conditions? → Decrease severity
4. Calculate final severity
5. Document rationale
```

### Severity Calculation Example

```
Vulnerability: Reentrancy in withdrawal function

Web2 CVSS Calculation:
- AV: Network (0.85)
- AC: Low (0.77)
- PR: None (0.85)
- UI: None (0.85)
- S: Unchanged (1.0)
- C: High (0.56)
- I: High (0.56)
- A: High (0.56)

Impact = 1 - [(1 - 0.56) × (1 - 0.56) × (1 - 0.56)] = 0.914
Impact = 6.42 × 0.914 = 5.87
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.89
Base Score = RoundUp(min(5.87 + 3.89, 10)) = 9.8 (Critical)

Web3 Immunefi Calculation:
- Impact: Direct fund loss → Critical
- Likelihood: Easily exploitable → Critical
- Final Severity: Critical
```

---

## Severity Assessment Checklist

### Web2
- [ ] CVSS base metrics determined
- [ ] Base score calculated
- [ ] Temporal metrics applied (if applicable)
- [ ] Environmental metrics applied (if applicable)
- [ ] Severity rating assigned
- [ ] Rationale documented

### Web3
- [ ] Impact assessed
- [ ] Likelihood assessed
- [ ] Severity assigned
- [ ] Rationale documented
- [ ] Examples provided

### Cross-Domain
- [ ] Web2 severity mapped to Web3 (if applicable)
- [ ] Web3 severity mapped to Web2 (if applicable)
- [ ] Mapping rationale documented
