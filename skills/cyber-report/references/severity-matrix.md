# Severity Matrix

## CVSS v3.1 Score Ranges

| Severity | Score Range | Label |
|----------|-------------|-------|
| Critical | 9.0 — 10.0 | Immediate action required; active exploitation likely or confirmed |
| High | 7.0 — 8.9 | Urgent action required; significant risk of exploitation |
| Medium | 4.0 — 6.9 | Action required; moderate risk; exploitation requires specific conditions |
| Low | 0.1 — 3.9 | Action recommended; limited risk; exploitation is difficult or impact is minimal |
| Informational | 0.0 | No direct risk; best practice deviation or hardening opportunity |

## CVSS v3.1 Base Metrics

### Attack Vector (AV)

| Value | Score | Description |
|-------|-------|-------------|
| Network (N) | 0.85 | Exploitable remotely over the network |
| Adjacent (A) | 0.62 | Exploitable from the same shared physical or logical network |
| Local (L) | 0.55 | Exploitable only with local access to the system |
| Physical (P) | 0.20 | Requires physical access to the system |

### Attack Complexity (AC)

| Value | Score | Description |
|-------|-------|-------------|
| Low (L) | 0.77 | No special conditions; reliable reproduction |
| High (H) | 0.44 | Depends on conditions outside attacker's control |

### Privileges Required (PR)

| Value | Score | Description |
|-------|-------|-------------|
| None (N) | 0.85 | No authentication required |
| Low (L) | 0.62 | Basic user privileges required |
| High (H) | 0.27 | Administrative privileges required |

### User Interaction (UI)

| Value | Score | Description |
|-------|-------|-------------|
| None (N) | 0.85 | No user interaction required |
| Required (R) | 0.62 | User must take some action |

### Scope (S)

| Value | Score | Description |
|-------|-------|-------------|
| Unchanged (U) | — | Vulnerability affects only the vulnerable component |
| Changed (C) | — | Vulnerability affects components beyond the vulnerable component |

### Confidentiality (C), Integrity (I), Availability (A)

| Value | Score | Description |
|-------|-------|-------------|
| High (H) | 0.56 | Total loss of the affected component |
| Low (L) | 0.22 | Limited loss; some impact |
| None (N) | 0.0 | No impact |

## Risk Rating Methodology

### Step 1: Determine Base Score

Use the CVSS v3.1 calculator with the metrics above. Document the full vector string.

### Step 2: Apply Temporal Metrics (if applicable)

| Metric | When to Apply |
|--------|---------------|
| Exploit Code Maturity | Known exploits exist |
| Remediation Level | Official fix, workaround, or unavailable |
| Report Confidence | Confirmed, reasonable, or unknown |

### Step 3: Apply Environmental Metrics (if applicable)

| Metric | When to Apply |
|--------|---------------|
| Confidentiality Requirement | Business impact of data exposure |
| Integrity Requirement | Business impact of data modification |
| Availability Requirement | Business impact of service disruption |

### Step 4: Map to Severity

Use the score ranges above. Always round to one decimal place.

## Business Impact Assessment

### Confidentiality Impact

| Level | Business Impact |
|-------|-----------------|
| High | Exposure of regulated data (PII, PHI, financial), trade secrets, or credentials |
| Medium | Exposure of internal data, configuration details, or non-sensitive user data |
| Low | Exposure of publicly available or non-sensitive information |

### Integrity Impact

| Level | Business Impact |
|-------|-----------------|
| High | Unauthorized modification of financial records, configurations, or code |
| Medium | Limited modification of non-critical data or settings |
| Low | Modification of cosmetic or easily reversible data |

### Availability Impact

| Level | Business Impact |
|-------|-----------------|
| High | Complete outage of revenue-critical or safety-critical systems |
| Medium | Degraded performance or partial outage of business systems |
| Low | Minor inconvenience or redundancy absorbs the impact |

## Severity Assignment Rules

1. **Always calculate, never guess.** Use the CVSS v3.1 calculator with documented vectors.
2. **When in doubt, round up.** If a finding falls on a boundary, assign the higher severity.
3. **Consider business context.** A technically Medium finding on a revenue-critical system may warrant a higher priority in the remediation roadmap.
4. **Document the rationale.** If severity is adjusted from the CVSS base score, explain why.
5. **Be consistent.** The same type of vulnerability on similar assets should receive the same severity.

## Quick Reference: Common Vulnerability Types

| Vulnerability | Typical CVSS Range | Typical Severity |
|---------------|-------------------|------------------|
| Remote Code Execution (unauthenticated) | 9.0-10.0 | Critical |
| SQL Injection (authenticated, data exfiltration) | 7.0-8.9 | High |
| Cross-Site Scripting (stored, authenticated) | 5.0-6.9 | Medium |
| Cross-Site Scripting (reflected, unauthenticated) | 4.0-6.9 | Medium |
| Missing security headers | 3.0-4.0 | Low |
| Information disclosure (version banners) | 2.0-3.0 | Low |
| Weak TLS configuration | 3.0-5.0 | Low-Medium |
| Default credentials | 8.0-10.0 | Critical-High |
| CSRF (state-changing action) | 5.0-7.0 | Medium-High |
| Open redirect | 3.0-4.0 | Low |
