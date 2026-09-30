---
name: engagement
description: >-
  Entry point for any multi-phase security engagement across web2 and web3. Use when starting an assessment, pentest, contract audit, or incident response. Routes phases to the right skill and manages handoffs and engagement state. Single-phase task with a known skill? Load that skill directly instead.
---

# Security Engagement

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

**Skill:** `recon`

Map the attack surface before touching targets.

- **Web2:** Network scanning, OSINT, subdomain enumeration, service fingerprinting
- **Web3:** Chain identification, address profiling, contract verification, protocol discovery

**Exit criteria:** Attack surface mapped, targets enumerated, initial risk indicators identified.

### Phase 2: Security Audit

**Skill:** `audit`

Identify vulnerabilities through systematic analysis.

- **Web2:** Code review, configuration audit, threat modeling, OWASP Top 10
- **Web3:** Contract audit, protocol economic security, formal verification, known vulnerability patterns

**Exit criteria:** Vulnerabilities identified with severity ratings and exploitability assessments.

### Phase 3: Exploitation

**Skill:** `exploit`

Validate findings through controlled exploitation.

- **Web2:** Web exploitation, privilege escalation, lateral movement
- **Web3:** Contract exploitation, flash loan attacks, oracle manipulation

**Exit criteria:** Exploitability confirmed with evidence, impact demonstrated.

### Phase 4: Verification

**Skill:** `verify`

Filter false positives and verify findings.

- **Cross-domain:** Deterministic reproduction, adversarial review, side-effect assertions

**Exit criteria:** All findings verified with reproducible evidence or marked as unverifiable.

### Phase 5: Forensics (incident branch only)

**Skill:** `forensics`

Investigate incidents and trace impact. The main pipeline runs 1 → 2 → 3 → 4 → 6; this phase applies only to incident-response engagements.

- **Web2:** Log analysis, malware analysis, disk/memory forensics
- **Web3:** On-chain tracing, fund tracking, transaction analysis

**Exit criteria:** Root cause identified, impact quantified, evidence preserved.

### Phase 6: Reporting

**Skill:** `report`

Generate professional deliverables.

- **Cross-domain:** Pentest reports, audit reports, incident reports, disclosure

**Exit criteria:** Client-ready report with executive summary, findings, and remediation.

## Orchestration Process

### Step 0: Establish Target

No target yet → select one before any enumeration (this is look-once work; hand-rolled trawling burns hundreds of calls):
1. Screen candidates (e.g. DeFiLlama TVL/rankings for web3) against: bounty or authorization exists, source code available, in-scope surface.
2. Source-first verification before chain work: docs site → repo search → clone → audit reports (scope + known issues) → bounty scope table. Chain calls verify source-vs-deployment, never discover blind.
3. Record the pick, its scope, and its repo in `wiki` + the engagement state file.
4. Validate every target against scope with `scripts/scope-checker.py` before active testing.

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
| `recon` | Mapping attack surface, enumerating targets | engagement, exploit, audit, verify, forensics, report |
| `osint` | Identity and selector investigation with verification standards | engagement, recon, research |
| `audit` | Identifying vulnerabilities, assessing risk | engagement, recon, exploit, verify, forensics, report |
| `exploit` | Validating findings, demonstrating impact | engagement, audit, verify, forensics, report |
| `verify` | Filtering false positives, confirming findings | engagement, exploit, audit |
| `forensics` | Investigating incidents, tracing funds | engagement, exploit |
| `report` | Generating deliverables, documenting findings | engagement, all skills |
| `coach` | Course correction, strategy guidance | engagement, all skills |
| `wiki` | Knowledge persistence, cross-engagement learning | engagement, all skills |

## Handoffs

- You are the entry point. A full engagement starts here — workers never self-orchestrate.
- At each phase boundary: verify exit criteria, summarize evidence, then load the next skill with the skill tool (recon → audit → exploit → verify → report; forensics branch for incidents).
- Intel gaps → `research`. Stall anywhere → `coach`. Phase ends → persist state to `wiki`.

## Shared Conventions

### Provenance Labels

Every finding carries a provenance label:

- **`tool-proven`** — Backed by captured tool output (screenshot, scan result, command output, transaction hash)
- **`model-asserted`** — Hypothesis based on observed behavior but not directly captured. Must be labeled as unverified.

### Severity Scales

Owned by `report` — use its scales, never redefine them here:

- **Web2:** CVSS v3.1 (Critical 9.0+, High 7.0+, Medium 4.0+, Low 0.1+, Informational 0.0)
- **Web3:** Immunefi impact scale (fund loss vs TVL)

### Output Formats

Each skill defines its own output format. All formats include:
- Executive summary
- Findings with severity and provenance
- Evidence with reproduction steps
- Recommendations

## Mid-Work Checkpoints

When orchestrating an engagement, periodically verify:

1. **Am I following the engagement lifecycle?** Check the current phase against the phase table.
2. **Have I met the current phase's exit criteria?** Do not transition until the current phase is complete.
3. **Am I routing to the correct skill?** Each phase has a designated skill — load it before continuing.
4. **Am I carrying forward context?** Summarize findings for the next phase before transitioning.
5. **Am I tracking engagement state?** Maintain the running engagement log.

## Phase Transition Reminders

When transitioning between phases, explicitly:
1. State the current phase and its exit criteria
2. Summarize findings from the completed phase
3. Name the next phase and its skill
4. Load the next skill with the skill tool
5. Carry forward evidence and context

## Goal Restatement at Phase Transitions

At each phase transition, restate the engagement context:

```markdown
## Phase Transition: [Current Phase] → [Next Phase]

**Engagement Goal:** [One sentence — what is the overall objective?]
**Current Phase:** [Phase name] — [Exit criteria status]
**Findings So Far:** [Count by severity]
**Evidence Captured:** [Yes/No — list any gaps]
**Next Phase:** [Phase name] — [What will it accomplish?]
**Next Skill:** [Skill name] — [What will it do?]
```

This combats attention decay and recency bias by re-injecting the goal into the conversation.

## Engagement State File

For long engagements, maintain a state file at `./engagement-state.md`:

```markdown
# Engagement State

**Started:** YYYY-MM-DD HH:MM
**Type:** [Web2 pentest / Web3 audit / Mixed / Incident response / Advisory]
**Target:** [Target identifier]
**Current Phase:** [Phase name]
**Phase Started:** YYYY-MM-DD HH:MM

## Findings

| Severity | Count | Last Updated |
|----------|-------|--------------|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 0 | — |
| Low | 0 | — |

## Evidence Log

- [YYYY-MM-DD HH:MM] [Tool] [Target] [Result summary]

## Phase History

| Phase | Started | Completed | Exit Criteria Met | Skill Used |
|-------|---------|-----------|-------------------|------------|
| Recon | YYYY-MM-DD HH:MM | YYYY-MM-DD HH:MM | Yes/No | recon |
| Audit | YYYY-MM-DD HH:MM | — | — | — |

## Next Steps

- [ ] [Next action]
- [ ] [Following action]
```

Update this file at each phase transition and every ~20 tool calls. This creates an external memory that survives context window pressure.

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
