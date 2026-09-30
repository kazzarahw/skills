# Threat Modeling Methodology

Comprehensive guide to threat modeling for security audits, covering STRIDE, PASTA, DREAD, attack trees, and trust boundary identification.

---

## Table of Contents

- [STRIDE](#stride)
  - [STRIDE by Asset](#stride-by-asset)
  - [STRIDE Examples](#stride-examples)
- [PASTA](#pasta)
  - [Stage 1: Define Objectives](#stage-1-define-objectives)
  - [Stage 2: Define Technical Scope](#stage-2-define-technical-scope)
  - [Stage 3: Application Decomposition](#stage-3-application-decomposition)
  - [Stage 4: Threat Analysis](#stage-4-threat-analysis)
  - [Stage 5: Vulnerability Analysis](#stage-5-vulnerability-analysis)
  - [Stage 6: Attack Modeling](#stage-6-attack-modeling)
  - [Stage 7: Risk and Impact Analysis](#stage-7-risk-and-impact-analysis)
- [DREAD](#dread)
  - [DREAD Calculation](#dread-calculation)
  - [DREAD Example](#dread-example)
- [Attack Trees](#attack-trees)
  - [Structure](#structure)
  - [Attack Tree Notation](#attack-tree-notation)
  - [Web3 Attack Tree Example](#web3-attack-tree-example)
- [Trust Boundary Identification](#trust-boundary-identification)
  - [Definition](#definition)
  - [Web2 Trust Boundaries](#web2-trust-boundaries)
  - [Web3 Trust Boundaries](#web3-trust-boundaries)
  - [Trust Boundary Checklist](#trust-boundary-checklist)
- [Threat Agent Identification](#threat-agent-identification)
  - [External Threat Agents](#external-threat-agents)
  - [Web3-Specific Threat Agents](#web3-specific-threat-agents)
- [Mitigation Mapping](#mitigation-mapping)
  - [STRIDE to Mitigation](#stride-to-mitigation)
  - [Web2 Mitigations](#web2-mitigations)
  - [Web3 Mitigations](#web3-mitigations)
- [Threat Modeling Process](#threat-modeling-process)
  - [Step 1: Identify Assets](#step-1-identify-assets)
  - [Step 2: Identify Trust Boundaries](#step-2-identify-trust-boundaries)
  - [Step 3: Identify Threats](#step-3-identify-threats)
  - [Step 4: Assess Risk](#step-4-assess-risk)
  - [Step 5: Define Mitigations](#step-5-define-mitigations)
  - [Step 6: Validate](#step-6-validate)
- [Threat Modeling Tools](#threat-modeling-tools)
- [Threat Modeling Checklist](#threat-modeling-checklist)
  - [Preparation](#preparation)
  - [Analysis](#analysis)
  - [Assessment](#assessment)
  - [Mitigation](#mitigation)
  - [Documentation](#documentation)

---

## STRIDE

STRIDE is a threat modeling methodology developed by Microsoft. Each letter represents a threat category:

| Category | Threat | Description |
|----------|--------|-------------|
| **S** | Spoofing | Impersonating something or someone else |
| **T** | Tampering | Modifying data or code |
| **R** | Repudiation | Claiming to have not performed an action |
| **I** | Information Disclosure | Exposing information to unauthorized parties |
| **D** | Denial of Service | Denying service to legitimate users |
| **E** | Elevation of Privilege | Gaining capabilities without proper authorization |

### STRIDE by Asset

| Asset | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|-------|----------|-----------|-------------|-----------------|-----|-----------|
| **Data** | Fake data | Modify data | Deny action | Leak data | Corrupt data | Access restricted data |
| **Process** | Fake process | Modify process | Deny execution | Leak process info | Crash process | Execute with elevated privileges |
| **Communication** | Fake identity | Modify messages | Deny sending | Intercept messages | Block messages | Impersonate privileged user |

### STRIDE Examples

#### Spoofing
```
Web2: Session hijacking, credential theft, phishing
Web3: Signature replay, phishing, fake contracts
```

#### Tampering
```
Web2: Parameter tampering, input manipulation, MITM
Web3: Transaction manipulation, front-running, reentrancy
```

#### Repudiation
```
Web2: Missing audit logs, anonymous actions
Web3: Missing events, anonymous transactions
```

#### Information Disclosure
```
Web2: Verbose errors, data exposure, directory listing
Web3: Storage exposure, front-running, MEV
```

#### Denial of Service
```
Web2: Resource exhaustion, DDoS, slowloris
Web3: Gas limit DoS, block stuffing, unbounded loops
```

#### Elevation of Privilege
```
Web2: Privilege escalation, IDOR, admin bypass
Web3: Admin key compromise, governance attacks, flash loan voting
```

---

## PASTA

PASTA (Process for Attack Simulation and Threat Analysis) is a risk-centric threat modeling methodology with seven stages:

### Stage 1: Define Objectives

```
Business objectives:
- Protect user funds
- Ensure service availability
- Maintain data integrity
- Comply with regulations

Security objectives:
- Prevent unauthorized access
- Ensure data confidentiality
- Maintain system integrity
- Provide audit trail
```

### Stage 2: Define Technical Scope

```
Components:
- Web application
- API endpoints
- Database
- Authentication system
- External integrations

Technologies:
- Languages: Python, JavaScript
- Frameworks: Flask, React
- Infrastructure: AWS, Docker
```

### Stage 3: Application Decomposition

```
Data Flow Diagram:
┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────►│   Web   │────►│   API   │
│         │     │   App   │     │         │
└─────────┘     └─────────┘     └─────────┘
                     │               │
                     ▼               ▼
               ┌─────────┐     ┌─────────┐
               │  Auth   │     │   DB    │
               │ Service │     │         │
               └─────────┘     └─────────┘

Trust Boundaries:
- User ↔ Web App (HTTPS)
- Web App ↔ API (Internal)
- API ↔ DB (Internal)
- API ↔ External (HTTPS)
```

### Stage 4: Threat Analysis

```
Threat Agents:
- External attackers
- Malicious insiders
- Competitors
- Automated bots

Threat Intelligence:
- Known attack patterns
- Industry threat reports
- Vulnerability databases
```

### Stage 5: Vulnerability Analysis

```
Vulnerability Identification:
- Code review
- Automated scanning
- Penetration testing
- Configuration review

Vulnerability Classification:
- OWASP Top 10
- CWE/SANS Top 25
- SWC Registry (Web3)
```

### Stage 6: Attack Modeling

```
Attack Trees:
Root Goal: Steal user funds
├── Exploit authentication
│   ├── Brute force password
│   ├── Session hijacking
│   └── Credential stuffing
├── Exploit authorization
│   ├── IDOR
│   ├── Privilege escalation
│   └── Missing access control
└── Exploit business logic
    ├── Race condition
    ├── Price manipulation
    └── Workflow bypass
```

### Stage 7: Risk and Impact Analysis

```
Risk Assessment:
- Likelihood: High/Medium/Low
- Impact: Critical/High/Medium/Low
- Risk Score: Likelihood × Impact

Risk Matrix:
           Low    Medium    High
High       Medium  High      Critical
Medium     Low     Medium    High
Low        Low     Low       Medium
```

---

## DREAD

DREAD is a risk assessment model with five categories:

| Category | Description | Scale |
|----------|-------------|-------|
| **D**amage | How bad would an attack be? | 0-10 |
| **R**eproducibility | How easy is it to reproduce? | 0-10 |
| **E**xploitability | How easy is it to attack? | 0-10 |
| **A**ffected Users | How many users affected? | 0-10 |
| **D**iscoverability | How easy is it to discover? | 0-10 |

### DREAD Calculation

```
Risk Score = (Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5

Score Interpretation:
0-2: Low risk
2-4: Medium risk
4-6: High risk
6-8: Very high risk
8-10: Critical risk
```

### DREAD Example

```
Vulnerability: SQL Injection

Damage: 8 (Can access all data)
Reproducibility: 9 (Easy to reproduce)
Exploitability: 8 (Public exploits available)
Affected Users: 10 (All users)
Discoverability: 9 (Easy to find)

Risk Score = (8 + 9 + 8 + 10 + 9) / 5 = 8.8 (Critical)
```

---

## Attack Trees

Attack trees represent hierarchical decomposition of attack goals.

### Structure

```
Root Goal: Steal User Funds
│
├── OR: Exploit Authentication
│   ├── AND: Obtain Credentials
│   │   ├── Phishing
│   │   ├── Credential Stuffing
│   │   └── Brute Force
│   └── AND: Bypass MFA
│       ├── SIM Swapping
│       └── MFA Fatigue
│
├── OR: Exploit Authorization
│   ├── IDOR
│   ├── Privilege Escalation
│   └── Missing Access Control
│
└── OR: Exploit Business Logic
    ├── Race Condition
    ├── Price Manipulation
    └── Workflow Bypass
```

### Attack Tree Notation

```
OR Gate: Any child goal achieves parent goal
AND Gate: All child goals required to achieve parent goal

Example:
Root: Steal Funds
├── OR: Direct Theft
│   ├── AND: Access Account
│   │   ├── Obtain Credentials
│   │   └── Bypass 2FA
│   └── AND: Transfer Funds
│       └── Execute Transfer
└── OR: Indirect Theft
    ├── Exploit Smart Contract
    └── Social Engineering
```

### Web3 Attack Tree Example

```
Root Goal: Drain Protocol Funds
│
├── OR: Oracle Manipulation
│   ├── AND: Manipulate Price
│   │   ├── Flash Loan
│   │   └── Spot Price Dependency
│   └── AND: Exploit Valuation
│       ├── Inflate Collateral
│       └── Borrow Excess
│
├── OR: Reentrancy
│   ├── AND: External Call
│   │   └── Unprotected Function
│   └── AND: State Update
│       └── After External Call
│
└── OR: Governance Attack
    ├── AND: Acquire Voting Power
    │   ├── Flash Loan
    │   └── Token Accumulation
    └── AND: Pass Malicious Proposal
        └── Drain Funds
```

---

## Trust Boundary Identification

### Definition

A trust boundary is a point where data or execution changes trust level. Crossing a trust boundary requires validation.

### Web2 Trust Boundaries

```
┌─────────────────────────────────────────────────────┐
│                    Internet                          │
│  Trust: None                                         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│              Web Application                         │
│  Trust: User input must be validated                 │
│  Boundary: Request parameters, headers, cookies      │
└──────────────────────┬──────────────────────────────┘
                       │ Internal
┌──────────────────────▼──────────────────────────────┐
│              API Layer                               │
│  Trust: Web app is trusted                           │
│  Boundary: API parameters, authentication            │
└──────────────────────┬──────────────────────────────┘
                       │ Internal
┌──────────────────────▼──────────────────────────────┐
│              Database                                │
│  Trust: API layer is trusted                         │
│  Boundary: SQL queries, stored procedures            │
└─────────────────────────────────────────────────────┘
```

### Web3 Trust Boundaries

```
┌─────────────────────────────────────────────────────┐
│                    EOA (User)                        │
│  Trust: None — can call any public function          │
└──────────────────────┬──────────────────────────────┘
                       │ Transaction
┌──────────────────────▼──────────────────────────────┐
│              Contract A (Entry Point)                │
│  Trust: EOA — must validate all inputs               │
│  Boundary: msg.sender, msg.value, calldata           │
└──────────────────────┬──────────────────────────────┘
                       │ External call
┌──────────────────────▼──────────────────────────────┐
│              Contract B (Dependency)                 │
│  Trust: Contract A — assumes caller is authorized    │
│  Boundary: function parameters, return values        │
└──────────────────────┬──────────────────────────────┘
                       │ Oracle query
┌──────────────────────▼──────────────────────────────┐
│              Oracle (External)                       │
│  Trust: None — can return any value                  │
│  Boundary: price feeds, random numbers               │
└─────────────────────────────────────────────────────┘
```

### Trust Boundary Checklist

- [ ] All trust boundaries identified
- [ ] Data flows across boundaries documented
- [ ] Validation requirements defined
- [ ] Authentication requirements defined
- [ ] Authorization requirements defined

---

## Threat Agent Identification

### External Threat Agents

| Agent | Motivation | Capability | Likelihood |
|-------|-----------|------------|------------|
| **Script Kiddie** | Curiosity, reputation | Low | High |
| **Hacktivist** | Political, social | Medium | Medium |
| **Cybercriminal** | Financial gain | High | High |
| **Nation State** | Espionage, sabotage | Very High | Low |
| **Insider** | Financial, revenge | High | Medium |

### Web3-Specific Threat Agents

| Agent | Motivation | Capability | Likelihood |
|-------|-----------|------------|------------|
| **Flash Loan Attacker** | Financial gain | High | High |
| **MEV Searcher** | Financial gain | Medium | High |
| **Governance Attacker** | Control, financial | High | Medium |
| **Validator** | Financial gain | High | Low |
| **Bridge Validator** | Financial gain | Very High | Low |

---

## Mitigation Mapping

### STRIDE to Mitigation

| Threat | Mitigation |
|--------|-----------|
| **Spoofing** | Authentication, MFA, session management |
| **Tampering** | Input validation, integrity checks, signatures |
| **Repudiation** | Audit logging, digital signatures, non-repudiation |
| **Info Disclosure** | Encryption, access control, data minimization |
| **DoS** | Rate limiting, resource limits, redundancy |
| **Elevation** | Authorization, least privilege, access control |

### Web2 Mitigations

| Threat | Mitigation |
|--------|-----------|
| **SQL Injection** | Parameterized queries, ORM |
| **XSS** | Output encoding, CSP, sanitization |
| **CSRF** | CSRF tokens, SameSite cookies |
| **IDOR** | Ownership verification, authorization |
| **SSRF** | URL validation, network segmentation |

### Web3 Mitigations

| Threat | Mitigation |
|--------|-----------|
| **Reentrancy** | Checks-effects-interactions, reentrancy guards |
| **Oracle Manipulation** | TWAP, circuit breakers, multiple oracles |
| **Flash Loan Attacks** | TWAP, commit-reveal, snapshot voting |
| **Governance Attacks** | Snapshot voting, timelock, delegation |
| **Access Control** | Multi-sig, timelock, role-based access |

---

## Threat Modeling Process

### Step 1: Identify Assets

```
Web2 Assets:
- User data
- Credentials
- Financial data
- Intellectual property

Web3 Assets:
- Smart contract funds
- Governance tokens
- LP tokens
- Oracle data
```

### Step 2: Identify Trust Boundaries

```
- Map all trust boundaries
- Document data flows
- Identify validation points
```

### Step 3: Identify Threats

```
- Use STRIDE methodology
- Consider all threat agents
- Review known attack patterns
```

### Step 4: Assess Risk

```
- Use DREAD or PASTA
- Calculate risk scores
- Prioritize by risk
```

### Step 5: Define Mitigations

```
- Map threats to mitigations
- Prioritize by risk
- Document residual risk
```

### Step 6: Validate

```
- Test mitigations
- Verify effectiveness
- Update threat model
```

---

## Threat Modeling Tools

| Tool | Type | Use Case |
|------|------|----------|
| **Microsoft Threat Modeling Tool** | Desktop | STRIDE analysis |
| **OWASP Threat Dragon** | Web | Collaborative threat modeling |
| **IriusRisk** | Enterprise | Automated threat modeling |
| **pytm** | Python | Code-based threat modeling |
| **ThreatSpec** | Open Source | Threat modeling as code |

---

## Threat Modeling Checklist

### Preparation
- [ ] System architecture documented
- [ ] Data flow diagrams created
- [ ] Trust boundaries identified
- [ ] Assets inventoried

### Analysis
- [ ] STRIDE analysis completed
- [ ] Threat agents identified
- [ ] Attack trees created
- [ ] Vulnerabilities identified

### Assessment
- [ ] Risk scores calculated
- [ ] Risk matrix completed
- [ ] Prioritization defined

### Mitigation
- [ ] Mitigations mapped to threats
- [ ] Residual risk documented
- [ ] Validation plan defined

### Documentation
- [ ] Threat model documented
- [ ] Findings reported
- [ ] Recommendations provided
