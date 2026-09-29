# Incident Response Reference

## Incident Response Procedures

### Phase 1: Preparation

**Objective:** Establish capabilities before an incident occurs.

**Key Activities:**
1. **Incident response team** — Designate roles (incident commander, technical lead, communications lead, legal counsel)
2. **Contact list** — Maintain up-to-date contact information for all stakeholders
3. **Tool access** — Ensure access to block explorers, fund tracking tools, and communication channels
4. **Playbooks** — Develop incident response playbooks for common scenarios
5. **Retainers** — Establish relationships with forensic firms and legal counsel
6. **Insurance** — Maintain cyber insurance coverage
7. **Monitoring** — Deploy real-time monitoring and alerting

**Deliverables:**
- Incident response plan document
- Contact list with 24/7 access
- Tool access credentials
- Playbooks for common scenarios
- Insurance policy documentation

### Phase 2: Detection

**Objective:** Identify and classify security incidents.

**Key Activities:**
1. **Alert triage** — Assess alerts from monitoring tools
2. **Incident classification** — Classify incident type and severity
3. **Scope assessment** — Determine affected systems, funds, and users
4. **Evidence preservation** — Begin collecting and preserving evidence
5. **Stakeholder notification** — Notify internal stakeholders

**Incident Classification:**

| Severity | Criteria | Response Time |
|----------|----------|---------------|
| Critical | >$10M at risk, active exploit | Immediate |
| High | $1M-$10M at risk, potential exploit | 1 hour |
| Medium | <$1M at risk, suspicious activity | 4 hours |
| Low | No funds at risk, policy violation | 24 hours |

**Deliverables:**
- Incident classification report
- Initial scope assessment
- Evidence preservation log
- Stakeholder notification record

### Phase 3: Response

**Objective:** Contain the incident and prevent further loss.

**Key Activities:**
1. **Emergency shutdown** — Activate circuit breakers or pause contracts if available
2. **Fund tracing** — Begin real-time fund tracing
3. **Attacker identification** — Start clustering and identification
4. **Exchange notification** — Contact exchanges if funds are moving
5. **Law enforcement** — Notify law enforcement if appropriate
6. **Public communication** — Prepare public statement

**Emergency Shutdown Procedures:**
1. Identify pause/circuit breaker mechanism
2. Execute shutdown transaction
3. Verify shutdown effectiveness
4. Document shutdown transaction hash
5. Notify all stakeholders

**Deliverables:**
- Incident containment report
- Fund tracing report
- Attacker identification report
- Exchange notification records
- Law enforcement notification records
- Public communication draft

### Phase 4: Recovery

**Objective:** Restore operations and recover funds.

**Key Activities:**
1. **Vulnerability remediation** — Fix the exploited vulnerability
2. **Fund recovery** — Coordinate with exchanges and law enforcement
3. **System restoration** — Restore protocol operations
4. **User reimbursement** — Develop and execute reimbursement plan
5. **Post-incident review** — Conduct comprehensive review

**Fund Recovery Methods:**
1. **Exchange freeze** — Funds frozen at exchange
2. **Legal action** — Court orders for fund recovery
3. **Negotiation** — Direct negotiation with attacker
4. **Bounty payment** — Bug bounty for white-hat return
5. **Insurance claim** — Cyber insurance payout

**Deliverables:**
- Vulnerability remediation report
- Fund recovery report
- System restoration report
- User reimbursement plan
- Post-incident review report

---

## Post-Mortem Analysis Patterns

### Root Cause Analysis

**5 Whys Technique:**
1. Why did the exploit occur? → Vulnerability in contract
2. Why was the vulnerability present? → Missing input validation
3. Why was input validation missing? → Incomplete code review
4. Why was code review incomplete? → Time pressure and lack of audit
5. Why was there time pressure? → No security-focused development process

**Fishbone Diagram (Ishikawa):**
- **People:** Developer error, lack of training, insider threat
- **Process:** Incomplete testing, rushed deployment, no audit
- **Technology:** Compiler bugs, library vulnerabilities, tool limitations
- **Environment:** Market pressure, competitive dynamics, regulatory gaps

### Attack Timeline Reconstruction

**Template:**
```
Time (UTC) | Event | Tx Hash | Block | Details
-----------|-------|---------|-------|--------
T+0:00     | Initial exploit | 0x... | 12345678 | Attacker called vulnerable function
T+0:02     | Funds moved to... | 0x... | 12345679 | Funds transferred to intermediary
T+0:05     | Funds bridged to... | 0x... | 12345680 | Funds bridged to another chain
T+0:30     | Funds deposited to... | 0x... | 12345685 | Funds deposited to exchange
T+1:00     | Detection | N/A | N/A | Protocol team detected exploit
T+2:00     | Public disclosure | N/A | N/A | Incident publicly disclosed
```

### Loss Quantification

**Direct Losses:**
- Token value at time of exploit
- Gas costs for emergency operations
- Legal and forensic costs

**Indirect Losses:**
- Reputational damage
- User fund losses
- Token price impact
- TVL (Total Value Locked) loss
- Ecosystem impact

**Recovery Tracking:**
- Funds frozen at exchanges
- Funds recovered through negotiation
- Insurance payouts
- Net loss after recovery

---

## Evidence Preservation Techniques

### On-Chain Evidence

**Transaction Data:**
1. Export raw transaction data (JSON format)
2. Record transaction hash, block number, timestamp
3. Export internal transactions
4. Export event logs
5. Export state changes (if available)

**Contract Data:**
1. Export contract source code (if verified)
2. Export contract bytecode
3. Export contract storage (if possible)
4. Export contract creation transaction

**Address Data:**
1. Export address transaction history
2. Export address token balances
3. Export address labels and tags
4. Export address clustering data

### Off-Chain Evidence

**Communication Records:**
1. Save all email communications
2. Save all chat logs (Discord, Telegram, etc.)
3. Save all governance proposals
4. Save all on-chain messages

**Analysis Records:**
1. Save all queries and their results
2. Save all visualizations and diagrams
3. Save all reports and summaries
4. Save all tool outputs

### Evidence Integrity

**Hash Verification:**
1. Calculate SHA-256 hash of all exported data
2. Record hash values in evidence log
3. Store hashes in multiple locations
4. Verify hashes before any legal proceedings

**Chain of Custody:**
1. Document who collected each piece of evidence
2. Document when and how evidence was collected
3. Document who has accessed evidence
4. Document any transformations or modifications

---

## Legal Considerations

### Jurisdiction

**Key Questions:**
1. Which jurisdiction(s) apply to the incident?
2. Which jurisdiction(s) apply to the attacker?
3. Which jurisdiction(s) apply to the protocol?
4. Which jurisdiction(s) apply to the users?

**Common Jurisdictions:**
- **United States:** SEC, CFTC, FinCEN, DOJ
- **European Union:** MiCA, GDPR, national regulators
- **Singapore:** MAS
- **Japan:** FSA
- **UK:** FCA

### Regulatory Reporting

**When to Report:**
- Securities law violations (if tokens are securities)
- Money transmission violations
- Sanctions violations (OFAC)
- Data breach notification (if user data affected)

**How to Report:**
- SEC: Tip, Complaint, or Referral (TCR) system
- FinCEN: SAR (Suspicious Activity Report)
- OFAC: Voluntary self-disclosure
- Local regulators: Varies by jurisdiction

### Law Enforcement Engagement

**When to Engage:**
- Active exploit with funds still moving
- Attacker identified
- Funds at exchanges (for freezing)
- Large losses (>$1M)

**How to Engage:**
- FBI (US): Internet Crime Complaint Center (IC3)
- Secret Service (US): Cryptocurrency crimes
- Europol (EU): European Cybercrime Centre (EC3)
- Local police: Cyber crime unit

**What to Provide:**
- Complete evidence package
- Incident timeline
- Attacker identification
- Fund flow analysis
- Legal documentation

### Legal Actions

**Civil Lawsuits:**
- Against attacker (if identified)
- Against exchange (if negligent)
- Against auditor (if negligent)
- Against protocol team (if negligent)

**Criminal Prosecution:**
- Refer to law enforcement
- Provide evidence and testimony
- Cooperate with investigation

**Asset Recovery:**
- Court orders for fund freezing
- Subpoenas for exchange records
- International cooperation (MLAT)

---

## Communication Procedures

### Internal Communication

**Stakeholders:**
- Executive team
- Engineering team
- Legal team
- Communications team
- Board of directors

**Communication Channels:**
- Secure messaging (Signal, Wire)
- Email (encrypted)
- Video conference (encrypted)
- Incident management system

**Communication Schedule:**
- Initial notification: Within 1 hour of detection
- Status updates: Every 4 hours during active incident
- Resolution notification: Within 1 hour of resolution
- Post-incident review: Within 1 week of resolution

### External Communication

**Stakeholders:**
- Users
- Investors
- Partners
- Media
- Regulators
- Law Enforcement

**Communication Principles:**
1. **Timely:** Communicate as soon as possible
2. **Accurate:** Only communicate verified information
3. **Transparent:** Be honest about what happened
4. **Empathetic:** Show concern for affected users
5. **Actionable:** Tell users what they should do

**Communication Templates:**

**Initial Disclosure:**
```
We are aware of a security incident affecting [Protocol Name] on [Date].
We have engaged [Forensic Firm] and [Law Enforcement] to investigate.
We will provide updates every [N] hours.
We advise users to [specific action].
```

**Status Update:**
```
Update on [Protocol Name] incident:
- Funds at risk: $[amount]
- Funds recovered: $[amount]
- Attacker status: [Identified/Unknown]
- Next steps: [Description]
- Next update: [Time]
```

**Resolution Notice:**
```
The [Protocol Name] incident has been resolved.
- Total loss: $[amount]
- Funds recovered: $[amount]
- Net loss: $[amount]
- Remediation: [Description]
- Reimbursement: [Description]
```

### Media Communication

**Principles:**
1. Designate single spokesperson
2. Prepare talking points
3. Anticipate questions
4. Never speculate
5. Never blame individuals
6. Focus on facts and actions

**Common Questions:**
1. How much was lost?
2. Who is responsible?
3. What are you doing to recover funds?
4. How will you prevent this in the future?
5. Are user funds safe?
6. Will users be reimbursed?

---

## Fund Recovery Methods

### Exchange Freeze

**Process:**
1. Identify exchange where funds are deposited
2. Contact exchange compliance team
3. Provide evidence package
4. Exchange freezes funds
5. Law enforcement initiates legal process
6. Funds returned to protocol

**Timeline:** Weeks to months

**Success Rate:** Moderate (depends on jurisdiction and exchange cooperation)

### Legal Action

**Process:**
1. File civil lawsuit against attacker
2. Obtain court order for fund freezing
3. Serve order to exchanges and other parties
4. Enforce court order
5. Recover funds through legal process

**Timeline:** Months to years

**Success Rate:** Low to moderate (depends on attacker identification and jurisdiction)

### Negotiation

**Process:**
1. Identify attacker (through clustering or on-chain messages)
2. Open communication channel
3. Negotiate fund return terms
4. Execute fund return transaction
5. Provide agreed-upon compensation (if applicable)

**Timeline:** Days to weeks

**Success Rate:** Moderate (depends on attacker willingness)

### Bug Bounty

**Process:**
1. Identify attacker as potential white-hat
2. Offer bug bounty for fund return
3. Negotiate bounty amount
4. Execute fund return transaction
5. Pay bounty

**Timeline:** Days to weeks

**Success Rate:** High (if attacker is willing to negotiate)

### Insurance Claim

**Process:**
1. File claim with cyber insurance provider
2. Provide evidence package
3. Insurance provider investigates
4. Insurance provider approves or denies claim
5. Receive payout (if approved)

**Timeline:** Weeks to months

**Success Rate:** High (if policy covers the incident type)

---

## Post-Incident Checklist

### Immediate (0-24 hours)
- [ ] Incident classified and scoped
- [ ] Evidence preservation initiated
- [ ] Stakeholders notified
- [ ] Fund tracing started
- [ ] Exchange notifications sent (if applicable)
- [ ] Law enforcement notified (if applicable)
- [ ] Public statement prepared

### Short-term (1-7 days)
- [ ] Vulnerability identified and documented
- [ ] Emergency shutdown executed (if applicable)
- [ ] Attacker identification attempted
- [ ] Fund flow analysis completed
- [ ] Exchange cooperation established
- [ ] Legal counsel engaged
- [ ] Insurance claim filed

### Medium-term (1-4 weeks)
- [ ] Vulnerability remediated
- [ ] Fund recovery efforts underway
- [ ] User communication plan executed
- [ ] Post-mortem analysis initiated
- [ ] Regulatory reporting completed
- [ ] Law enforcement cooperation ongoing

### Long-term (1-6 months)
- [ ] Fund recovery completed
- [ ] User reimbursement completed
- [ ] Post-mortem report published
- [ ] Security improvements implemented
- [ ] Process improvements implemented
- [ ] Training and awareness programs updated
