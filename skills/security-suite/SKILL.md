---
name: security-suite
description: >-
  Orchestrates security testing engagements across web2 and web3 targets.
  ALWAYS use this skill when starting a full security assessment, penetration
  test, smart contract audit, or incident response. Do NOT manually coordinate
  between phases when this skill is available. Load this skill before starting
  any multi-phase security engagement. Routes to the correct skill, manages
  phase handoffs, and maintains engagement state. For direct tool usage or
  single-phase tasks, use the specific skill directly.
---

# Security Suite

Orchestrates security testing engagements across web2 and web3 targets. Routes to the correct skill, manages phase handoffs, and maintains engagement state.

## Constitutional Rules

1. **Authorization required** — Verify written scope before any active testing. Refuse out-of-scope targets immediately.
2. **Evidence over assertion** — Every finding traces to captured tool output. No finding without a command log or transaction hash.
3. **Minimal blast radius** — Use least-intrusive techniques first. Aggressive modes require explicit authorization.
4. **Structured output** — All results use the skill's output template. No prose-only findings.
5. **Cross-skill consistency** — All skills in this suite share the same provenance rules, severity scales, and output conventions.

## Engagement Types

| Type | Description | Primary Skills |
|------|-------------|----------------|
| **Web2 pentest** | Network, web app, infrastructure testing | recon → audit → exploit → verify → report |
| **Web3 audit** | Smart contract, protocol, DeFi security | recon → audit → exploit → verify → report |
| **Mixed** | Web3 protocol with web2 components (frontend, API, infra) | recon → audit → exploit → verify → report |
| **Incident response** | Post-breach investigation and forensics | forensics → verify → report |
| **Advisory** | Security review, threat modeling, architecture assessment | audit → report |

## Engagement Phases

### Phase 1: Reconnaissance

**Skill:** `security-recon`

Map the attack surface before touching targets.

- **Web2:** Network scanning, OSINT, subdomain enumeration, service fingerprinting
- **Web3:** Chain identification, address profiling, contract verification, protocol discovery

**Exit criteria:** Attack surface mapped, targets enumerated, initial risk indicators identified.

### Phase 2: Security Audit

**Skill:** `security-audit`

Identify vulnerabilities through systematic analysis.

- **Web2:** Code review, configuration audit, threat modeling, OWASP Top 10
- **Web3:** Contract audit, protocol economic security, formal verification, known vulnerability patterns

**Exit criteria:** Vulnerabilities identified with severity ratings and exploitability assessments.

### Phase 3: Exploitation

**Skill:** `security-exploit`

Validate findings through controlled exploitation.

- **Web2:** Web exploitation, privilege escalation, lateral movement
- **Web3:** Contract exploitation, flash loan attacks, oracle manipulation

**Exit criteria:** Exploitability confirmed with evidence, impact demonstrated.

### Phase 4: Verification

**Skill:** `security-verify`

Filter false positives and verify findings.

- **Cross-domain:** Deterministic reproduction, adversarial review, side-effect assertions

**Exit criteria:** All findings verified with reproducible evidence or marked as unverifiable.

### Phase 5: Forensics

**Skill:** `security-forensics`

Investigate incidents and trace impact.

- **Web2:** Log analysis, malware analysis, disk/memory forensics
- **Web3:** On-chain tracing, fund tracking, transaction analysis

**Exit criteria:** Root cause identified, impact quantified, evidence preserved.

### Phase 6: Reporting

**Skill:** `security-report`

Generate professional deliverables.

- **Cross-domain:** Pentest reports, audit reports, incident reports, disclosure

**Exit criteria:** Client-ready report with executive summary, findings, and remediation.

## Orchestration Process

### Step 1: Classify Engagement

Determine the engagement type from the user's request:

1. **Explicit type** — User says "pentest", "audit", "incident response"
2. **Implicit type** — Infer from context (target type, tools mentioned, urgency)
3. **Mixed** — Web3 target with web2 components (frontend, API, infrastructure)

**Default:** If unclear, ask the user. Do not assume.

### Step 2: Determine Starting Phase

| Engagement Type | Starting Phase |
|-----------------|----------------|
| Web2 pentest | Recon |
| Web3 audit | Recon |
| Mixed | Recon |
| Incident response | Forensics |
| Advisory | Audit |

### Step 3: Route to Skill

Load the appropriate skill for the current phase. Each skill's SKILL.md contains the detailed process.

### Step 4: Manage Handoffs

When a phase completes:

1. Verify exit criteria are met
2. Summarize findings for the next phase
3. Route to the next skill
4. Carry forward evidence and context

### Step 5: Track Engagement State

Maintain a running engagement log:

```
Engagement: [Type] — [Target]
Started: [Timestamp]
Phase: [Current phase]
Findings: [Count by severity]
Status: [Active/Complete]
```

## Cross-Skill Navigation

| Skill | When to Use | Referenced By |
|-------|-------------|---------------|
| `security-recon` | Mapping attack surface, enumerating targets | suite, exploit, audit |
| `security-audit` | Identifying vulnerabilities, assessing risk | suite, recon, exploit |
| `security-exploit` | Validating findings, demonstrating impact | suite, audit, verify |
| `security-verify` | Filtering false positives, confirming findings | suite, exploit, audit |
| `security-forensics` | Investigating incidents, tracing funds | suite, exploit |
| `security-report` | Generating deliverables, documenting findings | suite, all skills |
| `security-coach` | Course correction, strategy guidance | suite, all skills |
| `security-wiki` | Knowledge persistence, cross-engagement learning | suite, all skills |

## Shared Conventions

### Provenance Labels

Every finding carries a provenance label:

- **`tool-proven`** — Backed by captured tool output (screenshot, scan result, command output, transaction hash)
- **`model-asserted`** — Hypothesis based on observed behavior but not directly captured. Must be labeled as unverified.

### Severity Scales

**Web2 (CVSS v3.1):**
| Score | Rating |
|-------|--------|
| 9.0-10.0 | Critical |
| 7.0-8.9 | High |
| 4.0-6.9 | Medium |
| 0.1-3.9 | Low |
| 0.0 | Informational |

**Web3 (Immunefi):**
| Impact | Rating |
|--------|--------|
| Loss of funds > 10% of TVL | Critical |
| Loss of funds < 10% of TVL | High |
| Temporary fund lock | Medium |
| No direct fund loss | Low |
| Informational | Informational |

### Output Formats

Each skill defines its own output format. All formats include:
- Executive summary
- Findings with severity and provenance
- Evidence with reproduction steps
- Recommendations

## Gotchas

- **Web3 engagements often have web2 components.** A DeFi protocol audit should include the frontend, API, and infrastructure, not just the smart contracts.
- **Chain context matters.** The same address on different chains is a different entity. Always confirm chain before analysis.
- **Tool output can be misleading.** A 200 OK from curl does not mean exploitation succeeded. Verify with side-effect assertions.
- **Scope creep is the #1 engagement risk.** Check authorization before every action. Document scope decisions.
- **Findings without evidence are worse than no findings.** Never fabricate evidence or present model-asserted findings as tool-proven.

## Scripts

- `scripts/engagement-tracker.py` — Track engagement state across phases
- `scripts/scope-checker.py` — Validate targets against scope

## References

- `references/engagement-templates.md` — Engagement plans for each type
- `references/phase-handoff-checklist.md` — Checklist for transitioning between phases
- `references/severity-mapping.md` — Cross-domain severity mapping table
- `references/tool-selection-guide.md` — When to use which tool across domains
