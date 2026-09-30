# Incident Response

Incident response procedures for web2 and web3 security incidents.

## Table of Contents

- [IR Phases](#ir-phases)
- [Incident Classification](#incident-classification)
- [Evidence Preservation](#evidence-preservation)
- [Communication Procedures](#communication-procedures)
- [Fund Recovery Methods](#fund-recovery-methods)
- [Post-Mortem Patterns](#post-mortem-patterns)
- [Regulatory Considerations](#regulatory-considerations)
- [Best Practices](#best-practices)

## IR Phases

### Phase 1: Preparation

**Objectives:**
- Establish incident response team and roles
- Develop incident response plan and procedures
- Deploy monitoring and detection tools
- Conduct training and tabletop exercises
- Establish communication channels and escalation paths

**Key Activities:**
- Define incident classification and severity levels
- Establish chain of custody procedures
- Deploy EDR/XDR, SIEM, and log aggregation
- Create incident response playbooks
- Establish relationships with law enforcement and legal counsel
- Prepare evidence handling procedures

**Exit Criteria:** IR plan documented, team trained, tools deployed, communication channels established.

### Phase 2: Identification

**Objectives:**
- Detect and confirm security incidents
- Classify incident type and severity
- Determine scope and impact
- Preserve initial evidence

**Key Activities:**
- Monitor alerts and anomalies
- Triage and validate alerts
- Classify incident (exploit, hack, breach, etc.)
- Determine affected systems and data
- Document initial findings
- Escalate as needed

**Exit Criteria:** Incident confirmed, classified, and scoped. Initial evidence preserved.

### Phase 3: Containment

**Objectives:**
- Stop the attack from spreading
- Prevent further damage
- Preserve evidence for analysis
- Maintain business operations where possible

**Key Activities:**
- Isolate affected systems (network segmentation, account suspension)
- Block malicious IPs, domains, and addresses
- Revoke compromised credentials
- Deploy temporary fixes or workarounds
- Monitor for additional compromise
- Document all containment actions

**Exit Criteria:** Attack contained, no further damage occurring, evidence preserved.

### Phase 4: Eradication

**Objectives:**
- Remove attacker access and malware
- Patch vulnerabilities
- Clean affected systems
- Verify system integrity

**Key Activities:**
- Remove malware and backdoors
- Patch exploited vulnerabilities
- Reset compromised credentials
- Rebuild compromised systems from known-good images
- Verify no remaining attacker persistence
- Document all eradication actions

**Exit Criteria:** Attacker access removed, vulnerabilities patched, systems clean.

### Phase 5: Recovery

**Objectives:**
- Restore systems and services
- Verify system integrity
- Monitor for recurrence
- Return to normal operations

**Key Activities:**
- Restore systems from clean backups
- Verify data integrity
- Implement additional monitoring
- Gradual service restoration
- User communication and support
- Document all recovery actions

**Exit Criteria:** Systems restored, services operational, monitoring in place.

### Phase 6: Lessons Learned

**Objectives:**
- Analyze the incident
- Identify improvements
- Update procedures and controls
- Share knowledge with organization

**Key Activities:**
- Conduct post-incident review
- Identify root cause and contributing factors
- Document lessons learned
- Update incident response plan
- Implement additional controls
- Share findings with stakeholders
- Update training materials

**Exit Criteria:** Post-mortem complete, improvements implemented, knowledge shared.

## Incident Classification

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| Critical | Active attack, major data breach, ransomware | Immediate | C-Suite, Legal, Law Enforcement |
| High | Confirmed compromise, significant data exposure | 1 hour | Management, Legal |
| Medium | Suspicious activity, potential compromise | 4 hours | Security Team |
| Low | Policy violation, minor security event | 24 hours | Security Team |

### Incident Types

| Type | Description | Examples |
|------|-------------|----------|
| Exploit | Smart contract vulnerability exploited | Reentrancy, oracle manipulation, access control |
| Hack | Unauthorized system access | Phishing, credential theft, vulnerability exploitation |
| Breach | Unauthorized data access | Database exfiltration, API abuse, insider threat |
| Ransomware | Data encryption and ransom demand | File encryption, double extortion |
| DDoS | Service disruption | Volumetric, protocol, application layer |
| Insider | Malicious internal actor | Data theft, sabotage, privilege abuse |
| Supply Chain | Compromised third-party component | Malicious dependency, compromised update |

## Evidence Preservation

### Chain of Custody

**Requirements:**
- Document who handled what, when, where
- Maintain evidence integrity with hash verification
- Store evidence in access-controlled, encrypted storage
- Limit access to authorized personnel only
- Document all access and transfers

**Chain of Custody Form:**
```
Evidence ID: EVD-2024-0115-001
Description: [Description of evidence]
Source: [System/Address/Account]
Collected: [Timestamp]
Collector: [Name]
Method: [Collection method]
SHA-256: [Hash value]
Storage: [Location]

Access Log:
| Timestamp | Person | Action | Reason |
|-----------|--------|--------|--------|
| ... | ... | ... | ... |
```

### Legal Considerations

**Key Principles:**
- Evidence must be legally admissible
- Chain of custody must be documented
- Evidence handling must follow procedures
- Privacy laws must be respected
- Legal counsel should be consulted

**Common Legal Issues:**
- Data privacy (GDPR, CCPA)
- Breach notification requirements
- Law enforcement cooperation
- Cross-border data transfer
- Attorney-client privilege

## Communication Procedures

### Internal Communication

| Audience | Timing | Content | Channel |
|----------|--------|---------|---------|
| IR Team | Immediate | Technical details, action items | Secure chat |
| Management | 1 hour | Impact, status, resource needs | Email/Meeting |
| Legal | 1 hour | Legal obligations, liability | Email/Meeting |
| All Staff | 4 hours | General awareness, precautions | Email |
| Customers | 24 hours | Impact, remediation, support | Email/Status Page |

### External Communication

| Audience | Timing | Content | Channel |
|----------|--------|---------|---------|
| Law Enforcement | As needed | Technical details, evidence | Direct contact |
| Regulators | As required | Breach notification | Formal filing |
| Media | As needed | Public statement | Press release |
| Partners | As needed | Impact, coordination | Direct contact |
| Public | As needed | Transparency, updates | Website/Social |

### Communication Principles

1. **Be transparent** — Share what is known, acknowledge what is not
2. **Be timely** — Communicate quickly, even if incomplete
3. **Be accurate** — Verify information before sharing
4. **Be consistent** — Ensure all communications align
5. **Be empathetic** — Consider the impact on affected parties
6. **Be legal** — Consult legal counsel before external communications

## Fund Recovery Methods

### Exchange Cooperation

```bash
# 1. Identify exchange where funds were sent
# Use Chainalysis, TRM Labs, or Elliptic to identify exchange

# 2. Contact exchange compliance team
# Provide:
# - Transaction hashes
# - Attacker addresses
# - Evidence of theft
# - Law enforcement case number (if available)

# 3. Exchange may freeze funds
# - Requires legal process in most cases
# - Exchange compliance team can freeze pending investigation

# 4. Document all communications
# - Keep records of all interactions
# - Follow up regularly
```

### Legal Action

```bash
# 1. Engage legal counsel
# - Specialized in cybercrime and asset recovery
# - Experience with cryptocurrency tracing

# 2. Obtain court orders
# - Subpoena exchanges for account information
# - Freeze orders for exchange accounts
# - Disclosure orders for KYC information

# 3. Coordinate with law enforcement
# - FBI (US)
# - NCA (UK)
# - Europol (EU)
# - Local law enforcement

# 4. File civil lawsuits
# - Against identified attackers
# - Against negligent third parties
# - For asset recovery
```

### Insurance

```bash
# 1. Review insurance policies
# - Cyber insurance
# - Crime insurance
# - Directors and officers (D&O) insurance

# 2. File claims
# - Document all losses
# - Provide evidence of incident
# - Cooperate with investigation

# 3. Engage forensic accountants
# - Quantify losses
# - Document damages
# - Support insurance claims
```

## Post-Mortem Patterns

### Root Cause Analysis

**5 Whys Technique:**
1. What happened? — Exploit drained $10M from protocol
2. Why? — Reentrancy vulnerability in withdraw function
3. Why? — State update after external call
4. Why? — No reentrancy guard implemented
5. Why? — Code review process missed the pattern

**Root Cause Categories:**
- Code bug (logic error, missing check)
- Design flaw (architecture vulnerability)
- Configuration error (misconfigured access)
- Process failure (inadequate review/testing)
- Human error (mistake, oversight)
- External dependency (third-party vulnerability)

### Timeline Template

```
Incident Timeline
=================

[Date] [Time] UTC — [Event]
  Source: [Log/Transaction/Alert]
  Evidence: [Hash/Screenshot/Reference]

[Date] [Time] UTC — [Event]
  Source: [Log/Transaction/Alert]
  Evidence: [Hash/Screenshot/Reference]
```

### Recommendations Template

```
Recommendations
===============

Immediate (0-7 days):
1. [Action item]
2. [Action item]

Short-term (1-4 weeks):
1. [Action item]
2. [Action item]

Long-term (1-6 months):
1. [Action item]
2. [Action item]

Strategic (6+ months):
1. [Action item]
2. [Action item]
```

## Regulatory Considerations

### GDPR (General Data Protection Regulation)

**Applicability:** EU residents' personal data

**Requirements:**
- Breach notification within 72 hours
- Notify affected individuals if high risk
- Document breach and response
- Data Protection Officer (DPO) involvement

**Key Articles:**
- Article 33: Breach notification to authority
- Article 34: Communication to affected individuals
- Article 35: Data protection impact assessment

### CCPA (California Consumer Privacy Act)

**Applicability:** California residents' personal data

**Requirements:**
- Notify affected individuals
- Notify California Attorney General if >500 residents
- Provide credit monitoring if SSN/financial data exposed
- Document breach and response

### Breach Notification Laws

**United States:**
- All 50 states have breach notification laws
- Varies by state (timing, content, recipients)
- Sector-specific requirements (HIPAA, GLBA)

**European Union:**
- GDPR (general)
- NIS2 Directive (essential services)
- ePrivacy Directive (electronic communications)

**Other Jurisdictions:**
- PIPEDA (Canada)
- LGPD (Brazil)
- APPI (Japan)
- Privacy Act (Australia)

## Best Practices

1. **Have a plan** — Documented IR plan with clear roles and procedures
2. **Practice regularly** — Tabletop exercises and simulations
3. **Preserve evidence** — Chain of custody from the start
4. **Communicate clearly** — Timely, accurate, consistent messaging
5. **Coordinate with legal** — Early involvement of legal counsel
6. **Document everything** — Every action, decision, and finding
7. **Learn and improve** — Post-incident review and process improvement
8. **Monitor continuously** — Ongoing monitoring for recurrence
9. **Build relationships** — Law enforcement, exchanges, other organizations
10. **Stay current** — Keep up with evolving threats and regulations
