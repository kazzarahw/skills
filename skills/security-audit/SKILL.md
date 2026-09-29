---
name: security-audit
description: Performs security assessments and vulnerability discovery across web2 and web3 targets. Use when reviewing code, auditing configurations, assessing protocol security, or identifying vulnerabilities. Covers static analysis, dynamic analysis, code review, threat modeling, contract auditing, protocol economic security, and formal verification.
---

# Security Audit

Security assessment and vulnerability discovery across web2 and web3 targets. Identifies vulnerabilities through systematic analysis.

## Constitutional Rules

1. **Never skip manual review.** Automated tools catch a significant portion of vulnerabilities, but manual review is still essential for comprehensive coverage. Manual line-by-line review is mandatory for every audit.
2. **Always verify exploitability.** A finding is only valid if you can demonstrate a concrete exploit path. Theoretical vulnerabilities are marked as informational.
3. **Trust boundaries define scope.** Every external call, oracle, and user input is a trust boundary. Map them before analyzing.
4. **Severity follows impact × likelihood.** Use the appropriate severity scale (CVSS for web2, Immunefi for web3). Never inflate severity.
5. **Report every finding.** Even if a vulnerability is mitigated, document it. Silence is worse than a false positive.
6. **Reproduce before reporting.** Every finding must include a proof-of-concept or test case that triggers the vulnerability.
7. **Stay within declared scope.** Do not audit contracts or systems outside the agreed scope without explicit approval.

## Audit Process

### Phase 0: Engagement

Establish the engagement framework before any analysis begins.

```
0.1  Scope confirmation       → in-scope components, exclusions, boundaries
0.2  Engagement letter/NDA    → signed authorization, legal agreement
0.3  Time estimation          → effort hours, milestones, delivery dates
0.4  Resource planning        → tools, environments, access requirements
0.5  Communication plan       → status updates, escalation contacts, reporting cadence
0.6  Data handling            → classification, storage, transmission, destruction
0.7  Legal/compliance         → regulatory requirements, responsible disclosure policy
```

**Exit criteria:** Scope confirmed in writing, engagement letter/NDA signed, time estimate approved, resources provisioned, communication plan agreed, data handling procedures documented, legal/compliance requirements satisfied.

### Phase 1: Understand

Map the system before analyzing it.

#### Web2 Understand

```
1.1  Architecture review      → components, data flows, trust boundaries
1.2  Tech stack identification → languages, frameworks, libraries, versions
1.3  Access control mapping    → who can access what, when, how
1.4  External dependencies     → APIs, CDNs, third-party services
1.5  Documentation review      → specs, READMEs, API docs
```

**Exit criteria:** All components documented with data flows and trust boundaries, tech stack identified.

#### Web3 Understand

```
1.1  Contract inventory       → all contracts, their roles, ownership
1.2  Architecture mapping     → contracts, actors, trust boundaries, asset flows
1.3  External integrations    → oracles, bridges, DEXs, tokens
1.4  Invariant documentation   → what must always be true
1.5  Documentation review      → specs, docs, intended behavior
1.6  Upgrade mechanism review  → proxy patterns, admin keys, timelocks
```

**Exit criteria:** Contract inventory complete, architecture mapped, invariants documented, upgrade mechanisms assessed.

### Phase 2: Automated Analysis

Run automated tools to identify known vulnerability patterns.

#### Web2 Automated Analysis

```bash
# Static analysis
semgrep --config=p/owasp-top-ten src/
npm audit                    # Node.js dependencies
safety check                 # Python dependencies
bandit -r src/               # Python security linting

# Dependency scanning
owasp-dependency-check --scan .
snyk test                    # SCA with vulnerability DB

# Infrastructure scanning
nuclei -u <target> -t exposures/
```

**Exit criteria:** All tool findings reviewed and marked as true positive, false positive, or needs investigation.

See `scripts/static-analysis-runner.sh` for automated execution.

#### Web3 Automated Analysis

```bash
# Slither — comprehensive static analysis
slither . --json results.json

# Aderyn — Rust-based analyzer for Solidity
aderyn . --json output.json

# Mythril — symbolic execution
myth analyze contract.sol

# Solhint — linting and style
solhint "contracts/**/*.sol"

# Semgrep — pattern matching
semgrep --config=p/smart-contracts contracts/
```

**Exit criteria:** All automated tools executed, results triaged, false positives filtered.

### Phase 3: Manual Review

Line-by-line review of in-scope code, focusing on:

#### Web2 Manual Review Focus Areas

| Category | What to Look For |
|----------|-----------------|
| **Input validation** | SQL injection, XSS, command injection, path traversal |
| **Authentication** | Weak auth, session management, credential handling |
| **Authorization** | IDOR, privilege escalation, missing access controls |
| **Cryptography** | Weak algorithms, hardcoded keys, improper random |
| **Business logic** | Race conditions, workflow bypass, price manipulation |
| **Error handling** | Verbose errors, information disclosure, DoS |

#### Web3 Manual Review Focus Areas

| Category | What to Look For |
|----------|-----------------|
| **Access control** | Missing modifiers, tx.origin, delegatecall risks |
| **Reentrancy** | External calls before state updates, cross-function reentrancy |
| **Oracle manipulation** | Spot price dependency, short TWAP, no circuit breakers |
| **Integer overflow** | Pre-0.8.0 Solidity, unchecked blocks |
| **Flash loan attacks** | Single-transaction manipulation, governance attacks |
| **Upgrade safety** | Storage collisions, uninitialized proxies, admin key risks |
| **Economic attacks** | Inflation attacks, donation attacks, liquidation manipulation |
| **Gas optimization** | DoS via gas limits, unbounded loops |

**Exit criteria:** 100% of in-scope files reviewed with line numbers documented.

See `references/web2-code-review.md` and `references/web3-contract-audit.md` for detailed review procedures.

### Phase 4: Dynamic Analysis

Execute tests and fuzzing to validate behavior under adversarial conditions.

#### Web2 Dynamic Analysis

```bash
# Fuzzing
ffuf -u <url>/FUZZ -w wordlist.txt
wfuzz -c -z file,wordlist.txt <url>

# API testing
postman / newman collections
burp suite intruder

# Authentication testing
hydra -l admin -P wordlist.txt <target> ssh
```

#### Web3 Dynamic Analysis

```bash
# Foundry fuzzing
forge test --fuzz-runs 10000

# Echidna — property-based fuzzing
echidna contract.sol --contract TestContract

# Invariant testing
forge test --match-contract InvariantTest

# Fork testing
forge test --fork-url $RPC_URL --fork-block-number N
```

**Exit criteria:** Fuzzing executed with minimum 10,000 runs, all invariants tested.

See `scripts/fuzz-test-generator.py` for generating fuzzing test cases.

### Phase 5: Threat Modeling

Systematically identify threats using STRIDE or similar methodology.

| Threat Category | Web2 Examples | Web3 Examples |
|-----------------|---------------|---------------|
| **Spoofing** | Session hijacking, credential theft | Signature replay, phishing |
| **Tampering** | Parameter tampering, input manipulation | Transaction manipulation, front-running |
| **Repudiation** | Missing audit logs | Missing events, anonymous actions |
| **Information disclosure** | Verbose errors, data exposure | Storage exposure, front-running |
| **Denial of service** | Resource exhaustion, DoS | Gas limit DoS, block stuffing |
| **Elevation of privilege** | Privilege escalation, IDOR | Admin key compromise, governance attacks |

**Exit criteria:** STRIDE analysis completed for all components, all threats mapped to mitigations.

See `references/threat-modeling.md` for the threat modeling methodology.

### Phase 6: Findings Compilation

Compile all findings into structured format.

Each finding must include:
- **Reference ID** — Unique identifier
- **Title** — Concise vulnerability name
- **Severity** — Critical / High / Medium / Low / Informational
- **CVSS/Impact** — Calculated score with vector
- **CVE/CWE/SWC** — Classification identifier
- **Description** — What the vulnerability is
- **Evidence** — Tool output, code excerpt, or PoC
- **Business impact** — What this means for the organization
- **Remediation** — Specific, actionable fix

**Exit criteria:** All findings have Reference ID, Title, Severity, CVSS/Impact, CVE/CWE/SWC, Description, Evidence, Business impact, Remediation.

See `scripts/finding-id-generator.py` and `scripts/severity-calculator.py` for finding management.

### Phase 7: Retest & Deliver

Verify remediations and deliver the final report.

```
7.1  Remediation verification  → retest all confirmed findings after fixes
7.2  Peer review process       → independent review of findings and report
7.3  Responsible disclosure    → coordinate disclosure timeline with client
7.4  Audit limitations          → document scope boundaries and limitations
7.5  Final report delivery     → executive summary, findings, remediation guidance
```

**Exit criteria:** All remediations verified, peer review completed, responsible disclosure timeline agreed, audit limitations documented, final report delivered.

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `security-suite` | Orchestration and phase management |
| `security-recon` | Attack surface mapping before audit |
| `security-exploit` | Validate findings through exploitation |
| `security-verify` | Verify findings before reporting |
| `security-report` | Generate audit report |
| `security-coach` | Course correction when audit stalls |
| `security-wiki` | Knowledge persistence |

## Gotchas

- **Automated tools produce false positives.** Always manually verify tool findings before reporting.
- **Slither misses business logic bugs.** Static analysis finds known patterns, not novel vulnerabilities.
- **Fuzzing finds crashes, not vulnerabilities.** A crash is only a finding if it has security impact.
- **Web3 invariants are critical.** Define invariants before fuzzing. Without invariants, fuzzing finds nothing.
- **Compiler version matters.** Solidity < 0.8.0 has different overflow behavior. Always check compiler version.
- **Proxy patterns hide vulnerabilities.** The implementation contract may have different vulnerabilities than the proxy.
- **Oracle dependencies are the #1 DeFi attack vector.** Always assess oracle manipulation risk.
- **Flash loan attacks are single-transaction.** No capital, no collateral, no credit check. If the attack fits in one transaction, it's free to attempt.
- **Gas optimization can introduce vulnerabilities.** Unbounded loops, complex computations, and storage-heavy operations can cause DoS.
- **Upgrade mechanisms are attack surfaces.** A compromised upgrade can drain any protocol.

## Output Format

```markdown
# Security Audit Report: [Target]

**Date:** YYYY-MM-DD
**Type:** [Web2/Web3/Mixed]
**Scope:** [In-scope components]
**Auditor:** [Name]
**Tools:** [Tool + versions]

## Executive Summary
- Overall risk: [Critical/High/Medium/Low]
- Findings: [Count by severity]
- Primary risk category: [Category]

## Scope and Methodology
- Components audited
- Standards referenced
- Tools used
- Time period

## Findings Summary
| ID | Title | Severity | Category |
|----|-------|----------|----------|
| ... | ... | ... | ... |

## Detailed Findings

### [SEVERITY] [ID]: [Title]
- **Description:** [What the vulnerability is]
- **Root cause:** [Why it exists]
- **Affected component:** [File/contract/line]
- **CVSS/Impact:** [Score with vector]
- **CVE/CWE/SWC:** [Identifier]
- **Evidence:** [Code excerpt, tool output, or PoC]
- **Business impact:** [Potential damage]
- **Remediation:** [Specific fix]
- **Provenance:** [tool-proven/model-asserted]

## Risk Assessment
| Category | Risk Level | Findings |
|----------|-----------|----------|
| ... | ... | ... |

## Recommendations
1. [Highest priority]
2. [Next priority]
3. [Continue...]

## Appendix
- Tool output logs
- Fuzzing results
- Threat model
```

## Scripts

- `scripts/static-analysis-runner.sh` — Automated static analysis execution
- `scripts/fuzz-test-generator.py` — Generate fuzzing test cases
- `scripts/finding-id-generator.py` — Generate unique finding IDs
- `scripts/severity-calculator.py` — Calculate CVSS/Immunefi severity

## References

- `references/web2-code-review.md` — Web2 code review procedures and checklists
- `references/web2-owasp-top10.md` — OWASP Top 10 vulnerability patterns
- `references/web3-contract-audit.md` — Smart contract audit procedures
- `references/web3-sw-registry.md` — SWC Registry vulnerability patterns
- `references/web3-known-hacks.md` — Major DeFi exploits and lessons learned
- `references/web3-defi-protocols.md` — DeFi protocol-specific audit guidance
- `references/web3-bridge-security.md` — Bridge security audit procedures
- `references/web3-mev-risks.md` — MEV risk assessment
- `references/threat-modeling.md` — Threat modeling methodology
- `references/severity-scales.md` — CVSS and Immunefi severity scales
