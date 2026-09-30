# Severity Matrix

CVSS v3.1 and Immunefi severity scales with cross-domain mapping.

---

## Table of Contents

1. [CVSS v3.1 Base Metrics](#cvss-v31-base-metrics)
2. [CVSS v3.1 Temporal Metrics](#cvss-v31-temporal-metrics)
3. [CVSS v3.1 Environmental Metrics](#cvss-v31-environmental-metrics)
4. [CVSS v3.1 Vector String Format](#cvss-v31-vector-string-format)
5. [CVSS v3.1 Calculation Procedure](#cvss-v31-calculation-procedure)
6. [CVSS v3.1 Qualitative Severity Rating](#cvss-v31-qualitative-severity-rating)
7. [Immunefi Severity Scale](#immunefi-severity-scale)
8. [Cross-Domain Mapping: CVSS ↔ Immunefi](#cross-domain-mapping)
9. [Severity Calculation Examples](#severity-calculation-examples)

---

## CVSS v3.1 Base Metrics

### Attack Vector (AV)

| Value | Description | Weight |
|-------|-------------|--------|
| **N** (Network) | Exploitable remotely over the network | 0.85 |
| **A** (Adjacent) | Exploitable from the same physical or logical network | 0.62 |
| **L** (Local) | Exploitable only with local access | 0.55 |
| **P** (Physical) | Exploitable only with physical access | 0.20 |

### Attack Complexity (AC)

| Value | Description | Weight |
|-------|-------------|--------|
| **L** (Low) | No special conditions required | 0.77 |
| **H** (High) | Depends on conditions beyond attacker control | 0.44 |

### Privileges Required (PR)

| Value | Description | Weight (S=U) | Weight (S=C) |
|-------|-------------|--------------|--------------|
| **N** (None) | No privileges required | 0.85 | 0.85 |
| **L** (Low) | Basic user privileges | 0.62 | 0.68 |
| **H** (High) | Administrative privileges | 0.27 | 0.50 |

### User Interaction (UI)

| Value | Description | Weight |
|-------|-------------|--------|
| **N** (None) | No user interaction required | 0.85 |
| **R** (Required) | User interaction required | 0.62 |

### Scope (S)

| Value | Description |
|-------|-------------|
| **U** (Unchanged) | Vulnerable component only |
| **C** (Changed) | Impact extends beyond the vulnerable component |

### Confidentiality (C)

| Value | Description | Weight |
|-------|-------------|--------|
| **N** (None) | No impact | 0.00 |
| **L** (Low) | Some information disclosure | 0.22 |
| **H** (High) | Total information disclosure | 0.56 |

### Integrity (I)

| Value | Description | Weight |
|-------|-------------|--------|
| **N** (None) | No impact | 0.00 |
| **L** (Low) | Some data modification | 0.22 |
| **H** (High) | Total data modification | 0.56 |

### Availability (A)

| Value | Description | Weight |
|-------|-------------|--------|
| **N** (None) | No impact | 0.00 |
| **L** (Low) | Some service degradation | 0.22 |
| **H** (High) | Total service loss | 0.56 |

---

## CVSS v3.1 Temporal Metrics

| Metric | Values | Description |
|--------|--------|-------------|
| **Exploit Code Maturity (E)** | X (Not Defined), U (Unproven), P (Proof-of-Concept), F (Functional), H (High) | Likelihood of exploitation |
| **Remediation Level (RL)** | X (Not Defined), O (Official Fix), T (Temporary Fix), W (Workaround), U (Unavailable) | Remediation status |
| **Report Confidence (RC)** | X (Not Defined), U (Unknown), R (Reasonable), C (Confirmed) | Confidence in the finding |

---

## CVSS v3.1 Environmental Metrics

| Metric | Description |
|--------|-------------|
| **Confidentiality Requirement (CR)** | Low / Medium / High / Not Defined |
| **Integrity Requirement (IR)** | Low / Medium / High / Not Defined |
| **Availability Requirement (AR)** | Low / Medium / High / Not Defined |
| **Modified Base Metrics** | Adjusted base metrics for the specific environment |

---

## CVSS v3.1 Vector String Format

```
CVSS:3.1/AV:[N|A|L|P]/AC:[L|H]/PR:[N|L|H]/UI:[N|R]/S:[U|C]/C:[N|L|H]/I:[N|L|H]/A:[N|L|H]
```

### Example

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

This represents: Network attack vector, low complexity, no privileges, no user interaction, unchanged scope, high confidentiality/integrity/availability impact.

---

## CVSS v3.1 Calculation Procedure

### Step 1: Calculate Base Score

```
Impact = 1 - [(1 - C) × (1 - I) × (1 - A)]
```

If Scope is Unchanged:
```
Impact = 6.42 × Impact
```

If Scope is Changed:
```
Impact = 7.52 × (Impact - 0.029) - 3.25 × (Impact - 0.02)^15
```

```
Exploitability = 8.22 × AV × AC × PR × UI
```

If Impact ≤ 0:
```
Base Score = 0
```

If Scope is Unchanged:
```
Base Score = RoundUp(min(Impact + Exploitability, 10))
```

If Scope is Changed:
```
Base Score = RoundUp(min(1.08 × (Impact + Exploitability), 10))
```

### Step 2: Calculate Temporal Score

```
Temporal Score = RoundUp(Base Score × E × RL × RC)
```

### Step 3: Calculate Environmental Score

```
Modified Impact = 1 - [(1 - C × CR) × (1 - I × IR) × (1 - A × AR)]
```

If Scope is Unchanged:
```
Modified Impact = 6.42 × Modified Impact
```

If Scope is Changed:
```
Modified Impact = 7.52 × (Modified Impact - 0.029) - 3.25 × (Modified Impact - 0.02)^15
```

```
Modified Exploitability = 8.22 × MAV × MAC × MPR × MUI
```

If Modified Impact ≤ 0:
```
Environmental Score = 0
```

If Scope is Unchanged:
```
Environmental Score = RoundUp(RoundUp(min(Modified Impact + Modified Exploitability, 10)) × E × RL × RC)
```

If Scope is Changed:
```
Environmental Score = RoundUp(RoundUp(min(1.08 × (Modified Impact + Modified Exploitability), 10)) × E × RL × RC)
```

---

## CVSS v3.1 Qualitative Severity Rating

| Score Range | Rating |
|-------------|--------|
| 0.0 | None |
| 0.1 – 3.9 | Low |
| 4.0 – 6.9 | Medium |
| 7.0 – 8.9 | High |
| 9.0 – 10.0 | Critical |

---

## Immunefi Severity Scale

### Critical

| Criterion | Description |
|-----------|-------------|
| **Impact** | Loss of funds > 10% of TVL, or complete protocol insolvency |
| **Likelihood** | High — easily exploitable with minimal conditions |
| **Examples** | Direct theft of user funds, unlimited minting, complete draining of protocol |

### High

| Criterion | Description |
|-----------|-------------|
| **Impact** | Loss of funds < 10% of TVL, or significant protocol disruption |
| **Likelihood** | Medium — exploitable with specific conditions |
| **Examples** | Partial fund drainage, temporary fund lock, governance takeover |

### Medium

| Criterion | Description |
|-----------|-------------|
| **Impact** | Temporary fund lock, or degradation of protocol functionality |
| **Likelihood** | Low — requires specific preconditions |
| **Examples** | Denial of service, temporary unavailability of core functions |

### Low

| Criterion | Description |
|-----------|-------------|
| **Impact** | No direct fund loss, minor protocol degradation |
| **Likelihood** | Very low — requires unlikely conditions |
| **Examples** | Gas optimization issues, minor information disclosure |

### Informational

| Criterion | Description |
|-----------|-------------|
| **Impact** | No direct impact on funds or protocol functionality |
| **Likelihood** | N/A — best practice recommendations |
| **Examples** | Code quality improvements, gas optimizations, documentation issues |

---

## Cross-Domain Mapping

| CVSS v3.1 Score | CVSS Rating | Immunefi Rating | Notes |
|-----------------|-------------|-----------------|-------|
| 9.0 – 10.0 | Critical | Critical | Direct fund loss or complete compromise |
| 7.0 – 8.9 | High | High | Significant fund loss or protocol disruption |
| 4.0 – 6.9 | Medium | Medium | Temporary impact or specific conditions |
| 0.1 – 3.9 | Low | Low | Minor impact, no direct fund loss |
| 0.0 | None | Informational | Best practice recommendations |

### Mapping Notes

- CVSS is used for **web2** findings; Immunefi is used for **web3** findings.
- When a finding spans both domains, use the **higher** severity rating.
- The mapping is approximate; use professional judgment for edge cases.
- Always document the rationale when deviating from the standard mapping.

---

## Severity Calculation Examples

### Example 1: SQL Injection (Web2)

**Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`

**Calculation:**
```
Impact = 1 - [(1 - 0.56) × (1 - 0.56) × (1 - 0.56)] = 1 - 0.085 = 0.915
Impact = 6.42 × 0.915 = 5.874
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.89
Base Score = RoundUp(min(5.874 + 3.89, 10)) = RoundUp(9.764) = 10.0
```

**Result:** Critical (10.0)

### Example 2: Stored XSS (Web2)

**Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`

**Calculation:**
```
Impact = 1 - [(1 - 0.22) × (1 - 0.22) × (1 - 0)] = 1 - 0.608 = 0.392
Impact = 7.52 × (0.392 - 0.029) - 3.25 × (0.392 - 0.02)^15 = 2.715 - 0.000 = 2.715
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.78
Base Score = RoundUp(min(1.08 × (2.715 + 2.78), 10)) = RoundUp(5.93) = 6.0
```

**Result:** Medium (6.0)

### Example 3: Reentrancy (Web3)

**Impact:** Direct theft of user funds
**Likelihood:** High — easily exploitable

**Immunefi Rating:** Critical

### Example 4: Missing Access Control (Web3)

**Impact:** Unauthorized function access, potential fund loss
**Likelihood:** Medium — requires specific conditions

**Immunefi Rating:** High

---

## Quick Reference

### CVSS v3.1 Base Score Ranges

| Rating | Score Range |
|--------|-------------|
| Critical | 9.0 – 10.0 |
| High | 7.0 – 8.9 |
| Medium | 4.0 – 6.9 |
| Low | 0.1 – 3.9 |
| None | 0.0 |

### Immunefi Severity Levels

| Level | Impact |
|-------|--------|
| Critical | Loss of funds > 10% TVL |
| High | Loss of funds < 10% TVL |
| Medium | Temporary fund lock |
| Low | No direct fund loss |
| Informational | No direct impact |
