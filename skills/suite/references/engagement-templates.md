# Engagement Templates

Professional engagement plans for each engagement type. Each template defines scope, phases, timeline, deliverables, tools, and risk assessment.

## Table of Contents

- [1. Web2 Penetration Test Engagement](#1-web2-penetration-test-engagement)
  - [Scope Definition](#scope-definition)
  - [Pre-Engagement Checklist](#pre-engagement-checklist)
  - [Phase Definitions](#phase-definitions)
  - [Timeline (Typical 2-Week Engagement)](#timeline-typical-2-week-engagement)
  - [Deliverables](#deliverables)
  - [Tools](#tools)
  - [Risk Assessment](#risk-assessment)
  - [Handoff Procedures](#handoff-procedures)
- [2. Web3 Smart Contract Audit Engagement](#2-web3-smart-contract-audit-engagement)
  - [Scope Definition](#scope-definition-1)
  - [Pre-Engagement Checklist](#pre-engagement-checklist-1)
  - [Phase Definitions](#phase-definitions-1)
  - [Timeline (Typical 2-Week Engagement)](#timeline-typical-2-week-engagement-1)
  - [Deliverables](#deliverables-1)
  - [Tools](#tools-1)
  - [Risk Assessment](#risk-assessment-1)
  - [Handoff Procedures](#handoff-procedures-1)
- [3. Mixed Engagement (Web3 + Web2)](#3-mixed-engagement-web3--web2)
  - [Scope Definition](#scope-definition-2)
  - [Pre-Engagement Checklist](#pre-engagement-checklist-2)
  - [Phase Definitions](#phase-definitions-2)
  - [Timeline (Typical 3-Week Engagement)](#timeline-typical-3-week-engagement)
  - [Deliverables](#deliverables-2)
  - [Tools](#tools-2)
  - [Risk Assessment](#risk-assessment-2)
  - [Handoff Procedures](#handoff-procedures-2)
- [4. Incident Response Engagement](#4-incident-response-engagement)
  - [Scope Definition](#scope-definition-3)
  - [Pre-Engagement Checklist](#pre-engagement-checklist-3)
  - [Phase Definitions](#phase-definitions-3)
  - [Timeline (Typical 1-Week Response)](#timeline-typical-1-week-response)
  - [Deliverables](#deliverables-3)
  - [Tools](#tools-3)
  - [Risk Assessment](#risk-assessment-3)
  - [Handoff Procedures](#handoff-procedures-3)
- [5. Advisory Engagement](#5-advisory-engagement)
  - [Scope Definition](#scope-definition-4)
  - [Pre-Engagement Checklist](#pre-engagement-checklist-4)
  - [Phase Definitions](#phase-definitions-4)
  - [Timeline (Typical 1-Week Engagement)](#timeline-typical-1-week-engagement)
  - [Deliverables](#deliverables-4)
  - [Tools](#tools-4)
  - [Risk Assessment](#risk-assessment-4)
  - [Handoff Procedures](#handoff-procedures-4)
- [Universal Exit Criteria](#universal-exit-criteria)

---

## 1. Web2 Penetration Test Engagement

### Scope Definition

| Attribute | Description |
|-----------|-------------|
| **Target types** | Network infrastructure, web applications, APIs, cloud resources |
| **In-scope** | Explicitly listed IP ranges, domains, subdomains, API endpoints |
| **Out-of-scope** | Production customer data, third-party services, DDoS testing, social engineering |
| **Testing window** | Defined time window (e.g., 02:00-06:00 UTC) for intrusive testing |
| **Authorization** | Signed Rules of Engagement (RoE) document |

### Pre-Engagement Checklist

- [ ] Signed RoE received and countersigned
- [ ] Scope document reviewed and acknowledged
- [ ] Emergency contacts identified (primary + secondary)
- [ ] Testing window confirmed with client
- [ ] VPN/credentials provisioned for remote access
- [ ] Backup and rollback procedures confirmed
- [ ] Data handling agreement signed (NDA, DPA)
- [ ] Insurance/liability documentation verified
- [ ] Communication channel established (Slack/Teams/email)
- [ ] Escalation path defined for critical findings

### Phase Definitions

| Phase | Duration | Activities | Exit Criteria |
|-------|----------|------------|---------------|
| **Recon** | 2-3 days | Network scanning, OSINT, subdomain enumeration, service fingerprinting | Attack surface map complete, all live hosts and services catalogued |
| **Audit** | 3-5 days | Vulnerability scanning, code review, configuration audit, threat modeling | Vulnerabilities identified with severity ratings |
| **Exploit** | 3-5 days | Controlled exploitation, privilege escalation, lateral movement | Exploitability confirmed with evidence |
| **Verify** | 1-2 days | False positive filtering, deterministic reproduction | All findings verified or marked unverifiable |
| **Report** | 2-3 days | Report writing, remediation guidance, executive summary | Client-ready report delivered |

### Timeline (Typical 2-Week Engagement)

```
Week 1:
  Mon-Tue:   Recon (scanning, enumeration, OSINT)
  Wed-Fri:   Audit (vuln identification, code review)
Week 2:
  Mon-Wed:   Exploit (validation, escalation, lateral movement)
  Thu:       Verify (false positive filtering, reproduction)
  Fri:       Report (draft delivery, debrief scheduling)
```

### Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| Daily status updates | Email/Slack | End of each day |
| Interim critical findings | Encrypted email + call | Within 1 hour of discovery |
| Draft report | PDF/Word | Day 10 |
| Final report | PDF/Word | Day 12 |
| Remediation roadmap | Spreadsheet | With final report |
| Raw evidence package | Encrypted archive | With final report |
| Executive presentation | Slide deck | Day 13 (optional) |

### Tools

| Phase | Primary Tools | Supporting Tools |
|-------|---------------|------------------|
| Recon | nmap, masscan, gobuster, sublist3r, amass | theHarvester, Shodan, Censys |
| Audit | nuclei, semgrep, bandit, OWASP ZAP | nikto, testssl.sh, trivy |
| Exploit | Metasploit, Burp Suite, SQLmap | custom scripts, pwntools |
| Verify | curl, custom reproduction scripts | Burp Repeater, browser devtools |
| Report | custom templates | CVSS calculator, Dradis |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Production outage during testing | Low | Critical | Maintenance window, rate limiting, rollback plan |
| Data exfiltration | Low | Critical | Encryption at rest, access logging, DPA |
| Scope creep | Medium | High | Pre-defined scope, change request process |
| False positive fatigue | Medium | Medium | Automated verification, severity calibration |
| Tool malfunction | Low | Medium | Manual fallback procedures, redundant tools |

### Handoff Procedures

1. **Recon → Audit:** Deliver attack surface map, target list, service inventory
2. **Audit → Exploit:** Deliver findings list with severity, exploitability assessment
3. **Exploit → Verify:** Deliver exploit evidence, reproduction steps, success criteria
4. **Verify → Report:** Deliver verified findings, evidence package, impact assessment

---

## 2. Web3 Smart Contract Audit Engagement

### Scope Definition

| Attribute | Description |
|-----------|-------------|
| **Target types** | Smart contracts, protocol logic, DeFi mechanisms, bridge contracts |
| **In-scope** | Explicitly listed contract addresses, repositories, commit hashes |
| **Out-of-scope** | Frontend (unless specified), off-chain infrastructure, governance decisions |
| **Chain(s)** | Explicitly listed (Ethereum, BSC, Arbitrum, etc.) |
| **Audit type** | Full audit / focused review / re-audit |

### Pre-Engagement Checklist

- [ ] Contract addresses and chain(s) confirmed
- [ ] Source code access granted (GitHub repo or flattened files)
- [ ] Commit hash or version tag specified
- [ ] Documentation reviewed (whitepaper, docs, specs)
- [ ] Previous audit reports obtained (if re-audit)
- [ ] Bug bounty program parameters understood (if applicable)
- [ ] Communication channel established
- [ ] Timeline agreed upon
- [ ] Emergency contact for critical vulnerabilities identified

### Phase Definitions

| Phase | Duration | Activities | Exit Criteria |
|-------|----------|------------|---------------|
| **Recon** | 1-2 days | Chain identification, contract verification, protocol discovery, TVL assessment | All in-scope contracts identified and verified |
| **Audit** | 5-10 days | Static analysis, manual review, economic security, formal verification | Vulnerabilities identified with severity ratings |
| **Exploit** | 2-3 days | Proof-of-concept development, testnet deployment, attack simulation | Exploitability demonstrated with evidence |
| **Verify** | 1-2 days | False positive filtering, deterministic reproduction on testnet | All findings verified or marked unverifiable |
| **Report** | 2-3 days | Report writing, remediation guidance, severity justification | Client-ready report delivered |

### Timeline (Typical 2-Week Engagement)

```
Week 1:
  Mon:       Recon (chain ID, contract verification, protocol mapping)
  Tue-Thu:   Audit (static analysis, manual review, economic analysis)
  Fri:       Audit continued, initial findings compilation
Week 2:
  Mon-Tue:   Exploit (PoC development, testnet validation)
  Wed:       Verify (reproduction, false positive filtering)
  Thu-Fri:   Report (draft delivery, remediation guidance)
```

### Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| Daily status updates | Encrypted message | End of each day |
| Critical vulnerability alert | Encrypted call + message | Within 1 hour |
| Draft findings | Markdown/PDF | Day 8 |
| Final report | PDF | Day 10 |
| PoC code | GitHub repo | With final report |
| Remediation guidance | Markdown | With final report |

### Tools

| Phase | Primary Tools | Supporting Tools |
|-------|---------------|------------------|
| Recon | Etherscan, Blockscout, DeFiLlama | Nansen, Dune Analytics |
| Audit | Slither, Aderyn, Mythril | Echidna, Manticore, 4naly3er |
| Exploit | Foundry, Hardhat | Tenderly, custom scripts |
| Verify | Foundry (forge test), Anvil | Tenderly simulation, mainnet forking |
| Report | custom templates | CVSS calculator, Immunefi severity guide |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positive on mainnet | Medium | High | Testnet validation before mainnet claims |
| Incomplete scope definition | Medium | High | Explicit contract list, commit hash pinning |
| Economic attack complexity | Medium | High | Economic modeling, simulation |
| Re-audit scope confusion | Low | Medium | Clear diff from previous audit |
| Tool false negatives | Medium | High | Manual review supplements automated tools |

### Handoff Procedures

1. **Recon → Audit:** Deliver contract inventory, protocol map, TVL/risk indicators
2. **Audit → Exploit:** Deliver findings with severity, exploitability assessment
3. **Exploit → Verify:** Deliver PoC code, testnet evidence, reproduction steps
4. **Verify → Report:** Deliver verified findings, evidence package, impact assessment

---

## 3. Mixed Engagement (Web3 + Web2)

### Scope Definition

| Attribute | Description |
|-----------|-------------|
| **Target types** | Smart contracts + frontend + API + infrastructure |
| **In-scope** | Contract addresses, frontend domains, API endpoints, infrastructure IPs |
| **Out-of-scope** | Third-party integrations, production customer data |
| **Chain(s)** | Explicitly listed |
| **Integration points** | Contract-frontend, contract-API, API-infrastructure |

### Pre-Engagement Checklist

- [ ] All web2 and web3 scope items explicitly listed
- [ ] Integration points between web2 and web3 identified
- [ ] Frontend source code access granted
- [ ] API documentation reviewed
- [ ] Infrastructure access credentials provisioned
- [ ] Contract addresses and chain(s) confirmed
- [ ] Testing environment availability confirmed (testnet + staging)
- [ ] Emergency contacts for both web2 and web3 components
- [ ] Data handling agreement signed

### Phase Definitions

| Phase | Duration | Activities | Exit Criteria |
|-------|----------|------------|---------------|
| **Recon** | 2-3 days | Full attack surface mapping (contracts + infra + frontend + API) | Complete attack surface map with all components |
| **Audit** | 5-7 days | Contract audit + web2 audit (parallel tracks) | Vulnerabilities identified across all components |
| **Exploit** | 3-5 days | Cross-component exploitation, integration attack chains | Exploitability confirmed with evidence |
| **Verify** | 1-2 days | False positive filtering, cross-component reproduction | All findings verified |
| **Report** | 2-3 days | Unified report with cross-component findings | Client-ready report delivered |

### Timeline (Typical 3-Week Engagement)

```
Week 1:
  Mon-Wed:   Recon (full attack surface: contracts, frontend, API, infra)
Week 2:
  Mon-Fri:   Audit (parallel: contract audit + web2 audit)
Week 3:
  Mon-Wed:   Exploit (cross-component chains, integration attacks)
  Thu:       Verify (reproduction, false positive filtering)
  Fri:       Report (draft delivery)
```

### Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| Daily status updates | Email/Slack | End of each day |
| Critical findings | Encrypted call + email | Within 1 hour |
| Draft report | PDF/Word | Day 15 |
| Final report | PDF/Word | Day 18 |
| PoC code | GitHub repo | With final report |
| Remediation roadmap | Spreadsheet | With final report |

### Tools

| Phase | Web3 Tools | Web2 Tools |
|-------|------------|------------|
| Recon | Etherscan, Blockscout | nmap, gobuster, sublist3r |
| Audit | Slither, Aderyn, Mythril | nuclei, semgrep, OWASP ZAP |
| Exploit | Foundry, Hardhat | Metasploit, Burp Suite, SQLmap |
| Verify | forge test, Anvil | curl, Burp Repeater |
| Report | custom templates | custom templates |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cross-component attack chains missed | Medium | High | Integration point mapping, chain analysis |
| Scope boundary confusion | Medium | High | Explicit component labeling, scope matrix |
| Testnet/mainnet divergence | Medium | High | Mainnet forking for verification |
| Resource contention (parallel tracks) | Low | Medium | Dedicated resources per track |
| Frontend-backend trust assumptions | Medium | High | API security review, auth testing |

### Handoff Procedures

1. **Recon → Audit:** Deliver unified attack surface map, component inventory, integration points
2. **Audit → Exploit:** Deliver cross-component findings, severity ratings, chain analysis
3. **Exploit → Verify:** Deliver exploit evidence, cross-component reproduction
4. **Verify → Report:** Deliver verified findings, unified evidence package

---

## 4. Incident Response Engagement

### Scope Definition

| Attribute | Description |
|-----------|-------------|
| **Target systems** | Compromised infrastructure, contracts, accounts |
| **Trigger** | Confirmed or suspected security incident |
| **In-scope** | Systems related to the incident, logs, artifacts |
| **Out-of-scope** | Unrelated systems, unrelated investigations |
| **Priority** | P1 — Immediate response required |

### Pre-Engagement Checklist

- [ ] Incident declared by client
- [ ] Emergency contacts activated
- [ ] Evidence preservation procedures initiated
- [ ] Legal/compliance team notified
- [ ] Communication protocol established (secure channel)
- [ ] Access credentials provisioned (read-only where possible)
- [ ] Timeline of known events established
- [ ] Indicators of compromise (IoCs) collected
- [ ] Chain of custody procedures understood

### Phase Definitions

| Phase | Duration | Activities | Exit Criteria |
|-------|----------|------------|---------------|
| **Triage** | 0-4 hours | Incident classification, severity assessment, initial containment | Incident classified, containment initiated |
| **Forensics** | 1-5 days | Log analysis, artifact collection, malware analysis, on-chain tracing | Root cause identified, attack vector documented |
| **Verify** | 1-2 days | Attack reproduction, impact quantification, evidence validation | Attack chain verified, impact quantified |
| **Report** | 1-3 days | Incident report, remediation guidance, lessons learned | Client-ready incident report |

### Timeline (Typical 1-Week Response)

```
Hour 0-4:   Triage (classification, containment, evidence preservation)
Day 1-3:    Forensics (log analysis, artifact collection, tracing)
Day 4:      Verify (reproduction, impact quantification)
Day 5:      Report (incident report, remediation guidance)
```

### Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| Initial assessment | Encrypted message | Within 4 hours |
| Daily updates | Encrypted message | Every 4 hours during active response |
| Interim findings | Encrypted message | As discovered |
| Final incident report | PDF | Day 5-7 |
| Evidence package | Encrypted archive | With final report |
| Remediation roadmap | Spreadsheet | With final report |
| Lessons learned document | Markdown | Day 7 |

### Tools

| Phase | Web2 Tools | Web3 Tools |
|-------|------------|------------|
| Triage | SIEM, Velociraptor | Etherscan, Tenderly |
| Forensics | Volatility, Autopsy, Splunk | Chainalysis, TRM Labs, Dune |
| Verify | Cuckoo Sandbox, YARA | Foundry, Tenderly simulation |
| Report | custom templates | custom templates |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Evidence destruction | High | Critical | Immediate preservation, read-only access |
| Attacker still present | Medium | Critical | Continuous monitoring, credential rotation |
| Legal/compliance violation | Medium | Critical | Legal team involvement, chain of custody |
| Incomplete timeline | Medium | High | Multiple log sources, correlation |
| False attribution | Low | High | Multiple evidence sources, peer review |

### Handoff Procedures

1. **Triage → Forensics:** Deliver incident classification, initial IoCs, containment status
2. **Forensics → Verify:** Deliver root cause analysis, attack timeline, evidence package
3. **Verify → Report:** Deliver verified attack chain, impact assessment, evidence validation
4. **Report → Complete:** Deliver final report, remediation roadmap, lessons learned

---

## 5. Advisory Engagement

### Scope Definition

| Attribute | Description |
|-----------|-------------|
| **Target types** | Architecture, code, infrastructure, processes |
| **In-scope** | Systems, codebases, architectures under review |
| **Out-of-scope** | Exploitation, active testing, production changes |
| **Deliverable** | Assessment report with recommendations |
| **Urgency** | Standard (non-emergency) |

### Pre-Engagement Checklist

- [ ] Advisory scope defined (architecture review, code review, threat modeling)
- [ ] Documentation access granted
- [ ] Stakeholder interviews scheduled
- [ ] Previous assessments obtained (if any)
- [ ] Communication channel established
- [ ] Timeline agreed upon
- [ ] Deliverable format confirmed

### Phase Definitions

| Phase | Duration | Activities | Exit Criteria |
|-------|----------|------------|---------------|
| **Discovery** | 1-2 days | Documentation review, stakeholder interviews, architecture mapping | Architecture and threat model understood |
| **Audit** | 3-5 days | Code review, architecture assessment, threat modeling, best practice comparison | Findings identified with severity ratings |
| **Report** | 2-3 days | Report writing, recommendations, roadmap | Client-ready assessment report |

### Timeline (Typical 1-Week Engagement)

```
Mon:       Discovery (documentation review, interviews)
Tue-Thu:   Audit (code review, architecture assessment, threat modeling)
Fri:       Report (draft delivery, recommendations)
```

### Deliverables

| Deliverable | Format | Timing |
|-------------|--------|--------|
| Daily updates | Email | End of each day |
| Draft report | PDF/Word | Day 4 |
| Final report | PDF/Word | Day 5 |
| Recommendations roadmap | Spreadsheet | With final report |
| Presentation | Slide deck | Day 6 (optional) |

### Tools

| Phase | Primary Tools | Supporting Tools |
|-------|---------------|------------------|
| Discovery | Architecture diagrams, documentation | Lucidchart, draw.io |
| Audit | semgrep, bandit, trivy | OWASP ASVS, NIST CSF |
| Report | custom templates | CVSS calculator |

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Incomplete documentation | Medium | High | Stakeholder interviews, code analysis |
| Scope ambiguity | Medium | High | Explicit scope document, regular check-ins |
| Recommendation feasibility | Medium | High | Client constraint analysis, prioritization |
| Stakeholder availability | Medium | Medium | Scheduled interviews, async communication |

### Handoff Procedures

1. **Discovery → Audit:** Deliver architecture map, threat model, documentation gaps
2. **Audit → Report:** Deliver findings with severity, recommendations, roadmap
3. **Report → Complete:** Deliver final report, recommendations, presentation

---

## Universal Exit Criteria

Every engagement must meet these criteria before closure:

- [ ] All in-scope targets assessed
- [ ] All findings documented with evidence
- [ ] All findings verified or marked unverifiable
- [ ] Final report delivered and accepted
- [ ] Remediation guidance provided
- [ ] Evidence package delivered
- [ ] Lessons learned documented
- [ ] Engagement state updated to "Complete"
