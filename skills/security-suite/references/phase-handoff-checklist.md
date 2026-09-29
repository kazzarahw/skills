# Phase Handoff Checklist

Checklist for transitioning between phases. Each handoff defines required inputs, required outputs, quality checks, and common failure modes.

## Table of Contents

- [1. Recon → Audit Handoff](#1-recon--audit-handoff)
  - [Required Inputs](#required-inputs)
  - [Required Outputs](#required-outputs)
  - [Quality Checks](#quality-checks)
  - [Common Handoff Failures](#common-handoff-failures)
- [2. Audit → Exploit Handoff](#2-audit--exploit-handoff)
  - [Required Inputs](#required-inputs-1)
  - [Required Outputs](#required-outputs-1)
  - [Quality Checks](#quality-checks-1)
  - [Common Handoff Failures](#common-handoff-failures-1)
- [3. Exploit → Verify Handoff](#3-exploit--verify-handoff)
  - [Required Inputs](#required-inputs-2)
  - [Required Outputs](#required-outputs-2)
  - [Quality Checks](#quality-checks-2)
  - [Common Handoff Failures](#common-handoff-failures-2)
- [4. Verify → Forensics Handoff](#4-verify--forensics-handoff)
  - [Required Inputs](#required-inputs-3)
  - [Required Outputs](#required-outputs-3)
  - [Quality Checks](#quality-checks-3)
  - [Common Handoff Failures](#common-handoff-failures-3)
- [5. Forensics → Report Handoff](#5-forensics--report-handoff)
  - [Required Inputs](#required-inputs-4)
  - [Required Outputs](#required-outputs-4)
  - [Quality Checks](#quality-checks-4)
  - [Common Handoff Failures](#common-handoff-failures-4)
- [6. Report → Complete Handoff](#6-report--complete-handoff)
  - [Required Inputs](#required-inputs-5)
  - [Required Outputs](#required-outputs-5)
  - [Quality Checks](#quality-checks-5)
  - [Common Handoff Failures](#common-handoff-failures-5)
- [Universal Handoff Quality Checks](#universal-handoff-quality-checks)

---

## 1. Recon → Audit Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Attack surface map | Complete map of all discovered targets | Diagram + structured data |
| Target list | Enumerated list of all in-scope targets | CSV/JSON |
| Service inventory | All discovered services with versions | CSV/JSON |
| OSINT findings | Publicly available intelligence | Report |
| Risk indicators | Initial risk assessment per target | Structured data |
| Scope validation | Confirmation all targets are in-scope | Checklist |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Handoff document | Summary of recon phase findings | Markdown |
| Target priority list | Targets ranked by risk/impact | Structured data |
| Attack surface diagram | Visual representation of attack surface | Diagram |
| Evidence package | All raw recon data | Archive |

### Quality Checks

- [ ] All in-scope targets have been enumerated
- [ ] All discovered services are fingerprinted (type, version, banner)
- [ ] All subdomains have been discovered and catalogued
- [ ] All open ports have been identified and mapped to services
- [ ] All web technologies have been identified
- [ ] All cloud assets have been identified (if applicable)
- [ ] All API endpoints have been discovered (if applicable)
- [ ] All smart contracts have been identified and verified (if applicable)
- [ ] Risk indicators are documented for each target
- [ ] Evidence is captured for all findings (screenshots, scan output)
- [ ] Out-of-scope targets have been flagged and excluded
- [ ] Handoff document is complete and reviewed

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Incomplete enumeration | Missed attack surface | Multiple recon tools, cross-validation |
| Unfingerprinted services | Inaccurate vulnerability assessment | Manual verification, banner grabbing |
| Missing subdomains | Incomplete scope coverage | Multiple subdomain sources, brute force |
| Unvalidated scope | Testing out-of-scope targets | Scope validation before handoff |
| Missing evidence | Unverifiable findings | Automated evidence capture |
| Poor documentation | Context loss for audit phase | Structured handoff template |

---

## 2. Audit → Exploit Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Findings list | All identified vulnerabilities | Structured data |
| Severity ratings | CVSS/Immunefi severity per finding | Structured data |
| Exploitability assessment | Theoretical exploitability per finding | Structured data |
| Affected targets | Targets affected by each finding | Structured data |
| Evidence | Supporting evidence for each finding | Screenshots, scan output |
| Reproduction steps | Steps to reproduce each finding | Documented steps |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Exploit plan | Prioritized list of findings to exploit | Structured data |
| Exploit feasibility | Assessment of which findings are exploitable | Structured data |
| Risk assessment | Risk of exploitation per finding | Structured data |
| Handoff document | Summary of audit phase findings | Markdown |
| Evidence package | All raw audit data | Archive |

### Quality Checks

- [ ] All findings have severity ratings
- [ ] All findings have exploitability assessments
- [ ] All findings have documented evidence
- [ ] All findings have reproduction steps
- [ ] Findings are prioritized by risk/impact
- [ ] Exploitable findings are clearly marked
- [ ] Non-exploitable findings are documented with rationale
- [ ] Exploit risk is assessed for each finding
- [ ] Authorization for exploitation is confirmed
- [ ] Rollback/recovery plan is documented
- [ ] Handoff document is complete and reviewed

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Missing severity ratings | Incorrect prioritization | Mandatory severity assessment |
| No exploitability assessment | Wasted effort on non-exploitable findings | Theoretical analysis before handoff |
| Incomplete evidence | Unverifiable findings | Evidence capture during audit |
| Missing reproduction steps | Cannot validate findings | Document during discovery |
| No authorization | Legal/ethical violation | Explicit authorization check |
| No rollback plan | Production impact | Pre-exploitation planning |

---

## 3. Exploit → Verify Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Exploit evidence | Captured evidence of successful exploitation | Screenshots, logs, transaction hashes |
| Exploit code | Code used for exploitation | Source code |
| Success criteria | Defined criteria for successful exploitation | Structured data |
| Side effects | Observed side effects of exploitation | Documented observations |
| Impact assessment | Assessed impact of exploitation | Structured data |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Verification results | Results of verification attempts | Structured data |
| False positive list | Findings that could not be reproduced | Structured data |
| Verified findings | Findings confirmed with evidence | Structured data |
| Evidence package | All exploitation evidence | Archive |
| Handoff document | Summary of exploitation phase | Markdown |

### Quality Checks

- [ ] All exploitable findings have been attempted
- [ ] All successful exploitations have captured evidence
- [ ] All failed exploitations have documented rationale
- [ ] All findings have been verified or marked unverifiable
- [ ] All verified findings have deterministic reproduction steps
- [ ] All side effects have been documented
- [ ] All impact assessments are complete
- [ ] All evidence is preserved and organized
- [ ] False positives are clearly marked with rationale
- [ ] Handoff document is complete and reviewed

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Missing evidence | Unverifiable exploitation | Automated evidence capture |
| Non-deterministic reproduction | Unreliable findings | Multiple verification attempts |
| Incomplete side effect documentation | Incomplete impact assessment | Comprehensive side effect checklist |
| False positives not filtered | Inflated findings count | Adversarial verification |
| Evidence corruption | Lost findings | Backup and integrity checks |

---

## 4. Verify → Forensics Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Verified findings | All findings confirmed through verification | Structured data |
| Evidence package | Complete evidence for all verified findings | Archive |
| Investigation scope | Scope of forensic investigation | Structured data |
| Timeline | Timeline of verified exploitation | Structured data |
| Impact assessment | Quantified impact of verified findings | Structured data |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Investigation plan | Plan for forensic investigation | Structured data |
| Evidence handoff | Transfer of evidence to forensics | Archive |
| Investigation scope | Defined scope for forensics | Document |
| Handoff document | Summary of verification phase | Markdown |

### Quality Checks

- [ ] All verified findings are documented with evidence
- [ ] All evidence is preserved and organized
- [ ] Investigation scope is clearly defined
- [ ] Timeline of events is established
- [ ] Impact is quantified where possible
- [ ] Evidence chain of custody is maintained
- [ ] All findings are reproducible
- [ ] Handoff document is complete and reviewed

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Incomplete evidence transfer | Lost context for forensics | Structured evidence package |
| Undefined investigation scope | Unfocused investigation | Explicit scope definition |
| Missing timeline | Incomplete incident reconstruction | Timeline construction during verification |
| Broken chain of custody | Inadmissible evidence | Evidence handling procedures |
| Unreliable findings | Wasted forensic effort | Thorough verification before handoff |

---

## 5. Forensics → Report Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Investigation findings | All forensic findings | Structured data |
| Root cause analysis | Identified root cause of incident | Document |
| Attack timeline | Complete timeline of attack | Structured data |
| Impact assessment | Quantified impact (financial, data, reputational) | Structured data |
| Evidence package | All forensic evidence | Archive |
| Indicators of compromise | All identified IoCs | Structured data |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Incident report | Complete incident report | PDF/Word |
| Executive summary | High-level summary for leadership | Document |
| Technical findings | Detailed technical findings | Document |
| Remediation roadmap | Prioritized remediation steps | Spreadsheet |
| Evidence package | All evidence organized for delivery | Archive |
| Lessons learned | Key lessons from incident | Document |

### Quality Checks

- [ ] Root cause is identified and documented
- [ ] Attack timeline is complete and accurate
- [ ] Impact is quantified (financial, data, reputational)
- [ ] All IoCs are documented
- [ ] All evidence is preserved and organized
- [ ] Chain of custody is maintained
- [ ] Remediation steps are prioritized and actionable
- [ ] Executive summary is clear and concise
- [ ] Technical findings are detailed and accurate
- [ ] Lessons learned are documented
- [ ] Report is client-ready

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Incomplete root cause | Ineffective remediation | Thorough investigation |
| Inaccurate timeline | Misleading report | Multiple evidence sources |
| Unquantified impact | Inability to prioritize remediation | Impact assessment framework |
| Missing IoCs | Inability to detect future attacks | Comprehensive IoC collection |
| Poor organization | Unusable report | Structured report template |
| Missing lessons learned | Repeated incidents | Post-incident review process |

---

## 6. Report → Complete Handoff

### Required Inputs

| Input | Description | Format |
|-------|-------------|--------|
| Final report | Complete client-ready report | PDF/Word |
| Remediation roadmap | Prioritized remediation steps | Spreadsheet |
| Evidence package | All evidence organized for delivery | Archive |
| Lessons learned | Key lessons from engagement | Document |
| Client feedback | Feedback on draft report | Document |

### Required Outputs

| Output | Description | Format |
|--------|-------------|--------|
| Final deliverable package | All deliverables packaged for client | Archive |
| Engagement summary | Summary of engagement for internal use | Document |
| Lessons learned (internal) | Internal lessons for skill improvement | Document |
| Engagement closure | Formal closure of engagement | Checklist |

### Quality Checks

- [ ] Final report is delivered and accepted
- [ ] Remediation roadmap is delivered
- [ ] Evidence package is delivered
- [ ] All deliverables meet quality standards
- [ ] Client feedback is addressed
- [ ] Lessons learned are documented
- [ ] Engagement state is updated to "Complete"
- [ ] All evidence is archived
- [ ] Engagement metrics are recorded
- [ ] Follow-up actions are scheduled

### Common Handoff Failures

| Failure | Impact | Prevention |
|---------|--------|------------|
| Incomplete deliverables | Client dissatisfaction | Deliverable checklist |
| Unaddressed feedback | Client relationship damage | Feedback review process |
| Missing lessons learned | Repeated mistakes | Post-engagement review |
| Poor evidence organization | Inability to audit findings | Structured evidence package |
| No follow-up | Incomplete remediation | Scheduled follow-up actions |

---

## Universal Handoff Quality Checks

These checks apply to **every** phase transition:

- [ ] Required inputs are complete and validated
- [ ] Required outputs are complete and validated
- [ ] Evidence is preserved and organized
- [ ] Handoff document is complete and reviewed
- [ ] Next phase team has context to proceed
- [ ] No critical information is lost in transition
- [ ] Scope is re-validated at each transition
- [ ] Authorization is re-confirmed at each transition
- [ ] Timeline is updated and communicated
- [ ] Risks are re-assessed for next phase
