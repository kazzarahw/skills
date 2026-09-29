# Compliance Mapping

Compliance framework mapping to security controls and testing procedures.

---

## Table of Contents

1. [PCI DSS v4.0](#pci-dss-v40)
2. [HIPAA Security Rule](#hipaa-security-rule)
3. [ISO 27001](#iso-27001)
4. [SOC 2](#soc-2)
5. [NIST CSF](#nist-csf)
6. [GDPR](#gdpr)

---

## PCI DSS v4.0

Payment Card Industry Data Security Standard v4.0

### Requirement 1: Install and Maintain Network Security Controls

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 1.1 | Network security controls (NSC) | Review firewall rules, verify segmentation | Firewall rule review, network diagrams |
| 1.2 | Network security configurations | Test default passwords, unnecessary services | Configuration review, vulnerability scan |
| 1.3 | Network access restrictions | Test inbound/outbound traffic rules | Penetration test results |
| 1.4 | Network security for mobile devices | Test mobile device security controls | Mobile device policy review |
| 1.5 | Network security for cloud environments | Test cloud security configurations | Cloud security assessment |

### Requirement 2: Apply Secure Configurations to All System Components

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 2.1 | Secure configurations for all systems | Review system configurations against baselines | Configuration compliance report |
| 2.2 | Default credentials | Test for default passwords | Vulnerability scan results |
| 2.3 | Unnecessary services | Test for unnecessary services | Service inventory, port scan |
| 2.4 | Insecure protocols | Test for SSLv3, TLS 1.0, etc. | Protocol scan results |

### Requirement 3: Protect Stored Account Data

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 3.1 | Data retention policies | Review data retention policies | Data retention policy document |
| 3.2 | Sensitive authentication data | Test for storage of full track data | Data discovery scan |
| 3.3 | PAN masking | Test PAN display masking | Screenshot evidence |
| 3.4 | PAN encryption | Test PAN storage encryption | Encryption configuration review |
| 3.5 | Key management | Test key management procedures | Key management policy review |

### Requirement 4: Protect Cardholder Data with Strong Cryptography

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 4.1 | Strong cryptography for transmission | Test TLS configuration | SSL/TLS scan results |
| 4.2 | End-to-end encryption | Test point-to-point encryption | P2PE configuration review |

### Requirement 5: Protect All Systems and Networks from Malicious Software

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 5.1 | Anti-malware solutions | Test anti-malware deployment | Anti-malware configuration review |
| 5.2 | Anti-malware updates | Test anti-malware update status | Update status report |
| 5.3 | Anti-malware scanning | Test anti-malware scanning | Scan results |

### Requirement 6: Develop and Maintain Secure Systems and Software

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 6.1 | Security patches | Test for missing patches | Patch management report |
| 6.2 | Software security patches | Test for critical patches | Patch compliance report |
| 6.3 | Secure development practices | Review SDLC practices | SDLC documentation |
| 6.4 | Web application security | Test for OWASP Top 10 | Web application scan results |
| 6.5 | Change management | Test change management process | Change management records |

### Requirement 7: Restrict Access to System Components and Cardholder Data

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 7.1 | Access control policies | Review access control policies | Access control policy document |
| 7.2 | Role-based access control | Test RBAC implementation | RBAC configuration review |
| 7.3 | Access control reviews | Test access control reviews | Access review records |

### Requirement 8: Identify Users and Authenticate Access to System Components

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 8.1 | User identification | Test user identification | User inventory |
| 8.2 | User authentication | Test authentication mechanisms | Authentication test results |
| 8.3 | Multi-factor authentication | Test MFA implementation | MFA configuration review |
| 8.4 | Password policies | Test password policies | Password policy review |

### Requirement 9: Restrict Physical Access to Cardholder Data

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 9.1 | Physical security controls | Test physical access controls | Physical security assessment |
| 9.2 | Physical access logs | Review physical access logs | Access log review |
| 9.3 | Physical access restrictions | Test physical access restrictions | Physical security review |

### Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 10.1 | Audit logs | Review audit log configuration | Audit log configuration review |
| 10.2 | Audit log content | Review audit log content | Audit log samples |
| 10.3 | Audit log retention | Test audit log retention | Retention policy review |
| 10.4 | Time synchronization | Test time synchronization | NTP configuration review |

### Requirement 11: Test Security of Systems and Networks Regularly

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 11.1 | Vulnerability scanning | Perform vulnerability scan | Vulnerability scan report |
| 11.2 | Penetration testing | Perform penetration test | Penetration test report |
| 11.3 | Intrusion detection/prevention | Test IDS/IPS | IDS/IPS configuration review |
| 11.4 | File integrity monitoring | Test FIM | FIM configuration review |

### Requirement 12: Support Security with Organizational Policies and Programs

| Sub-Requirement | Description | Testing Procedure | Evidence Required |
|----------------|-------------|-------------------|-------------------|
| 12.1 | Security policy | Review security policy | Security policy document |
| 12.2 | Security awareness program | Test security awareness | Training records |
| 12.3 | Risk assessment | Review risk assessment | Risk assessment report |
| 12.4 | Security testing program | Review security testing program | Testing program documentation |

---

## HIPAA Security Rule

Health Insurance Portability and Accountability Act — Security Rule

### Administrative Safeguards

| Section | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| 164.308(a)(1) | Security management process | Review risk analysis and management | Risk analysis report |
| 164.308(a)(2) | Assigned security responsibility | Review security officer designation | Security officer job description |
| 164.308(a)(3) | Workforce security | Review workforce security policies | Workforce security policy |
| 164.308(a)(4) | Information access management | Test access controls | Access control configuration review |
| 164.308(a)(5) | Security awareness and training | Review training program | Training records |
| 164.308(a)(6) | Security incident procedures | Test incident response | Incident response plan |
| 164.308(a)(7) | Contingency plan | Test contingency planning | Contingency plan document |
| 164.308(a)(8) | Evaluation | Review security evaluations | Evaluation reports |

### Physical Safeguards

| Section | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| 164.310(a)(1) | Facility access controls | Test facility access controls | Physical security assessment |
| 164.310(a)(2)(i) | Contingency operations | Test contingency operations | Contingency plan |
| 164.310(a)(2)(ii) | Facility security plan | Review facility security plan | Facility security plan |
| 164.310(a)(2)(iii) | Access control and validation | Test access controls | Access control review |
| 164.310(a)(2)(iv) | Maintenance records | Review maintenance records | Maintenance log review |
| 164.310(b) | Workstation use | Review workstation use policy | Workstation use policy |
| 164.310(c) | Workstation security | Test workstation security | Workstation security review |
| 164.310(d)(1) | Device and media controls | Test device and media controls | Device control policy |
| 164.310(d)(2)(i) | Disposal | Test media disposal | Disposal procedure review |
| 164.310(d)(2)(ii) | Media re-use | Test media re-use | Re-use procedure review |
| 164.310(d)(2)(iii) | Accountability | Test media tracking | Media tracking review |
| 164.310(d)(2)(iv) | Data backup and storage | Test data backup | Backup procedure review |

### Technical Safeguards

| Section | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| 164.312(a)(1) | Access control | Test access controls | Access control configuration review |
| 164.312(a)(2)(i) | Unique user identification | Test user identification | User inventory |
| 164.312(a)(2)(ii) | Emergency access procedure | Test emergency access | Emergency access procedure |
| 164.312(a)(2)(iii) | Automatic logoff | Test automatic logoff | Session timeout configuration |
| 164.312(a)(2)(iv) | Encryption and decryption | Test encryption | Encryption configuration review |
| 164.312(b) | Audit controls | Test audit controls | Audit log configuration review |
| 164.312(c)(1) | Integrity | Test data integrity | Integrity controls review |
| 164.312(c)(2) | Mechanism to authenticate ePHI | Test authentication | Authentication test results |
| 164.312(d) | Person or entity authentication | Test authentication | Authentication test results |
| 164.312(e)(1) | Transmission security | Test transmission security | TLS/SSL configuration review |
| 164.312(e)(2)(i) | Integrity controls | Test integrity controls | Integrity controls review |
| 164.312(e)(2)(ii) | Encryption | Test encryption | Encryption configuration review |

### Organizational Requirements

| Section | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| 164.314(a)(1) | Business associate contracts | Review BAAs | Business associate agreements |
| 164.314(a)(2)(i) | Group health plan requirements | Review group health plan | Group health plan documentation |

### Policies and Procedures and Documentation Requirements

| Section | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| 164.316(a) | Policies and procedures | Review security policies | Security policy documents |
| 164.316(b)(1) | Documentation | Review security documentation | Security documentation |
| 164.316(b)(2)(i) | Time limit | Test documentation retention | Retention policy review |
| 164.316(b)(2)(ii) | Availability | Test documentation availability | Documentation access review |
| 164.316(b)(2)(iii) | Updates | Test documentation updates | Documentation update records |

---

## ISO 27001

ISO/IEC 27001:2022 — Information Security Management System

### Annex A Controls

#### A.5: Organizational Controls

| Control | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| A.5.1 | Policies for information security | Review security policies | Security policy documents |
| A.5.2 | Information security roles and responsibilities | Review role definitions | Role responsibility matrix |
| A.5.3 | Segregation of duties | Test segregation of duties | SoD matrix review |
| A.5.4 | Management responsibilities | Review management responsibilities | Management review records |
| A.5.5 | Contact with authorities | Review authority contacts | Authority contact list |
| A.5.6 | Contact with special interest groups | Review special interest group contacts | SIG contact list |
| A.5.7 | Threat intelligence | Review threat intelligence program | Threat intelligence reports |
| A.5.8 | Information security in project management | Review project security | Project security documentation |
| A.5.9 | Inventory of information and other assets | Review asset inventory | Asset inventory |
| A.5.10 | Acceptable use of information and assets | Review acceptable use policy | Acceptable use policy |
| A.5.11 | Return of assets | Test asset return process | Asset return records |
| A.5.12 | Classification of information | Review information classification | Information classification policy |
| A.5.13 | Labelling of information | Review information labelling | Labelling procedure |
| A.5.14 | Information transfer | Test information transfer | Transfer procedure review |
| A.5.15 | Access control | Test access controls | Access control configuration review |
| A.5.16 | Identity management | Test identity management | Identity management review |
| A.5.17 | Authentication information | Test authentication information | Authentication review |
| A.5.18 | Access rights | Test access rights | Access rights review |
| A.5.19 | Information security in supplier relationships | Review supplier security | Supplier security assessment |
| A.5.20 | Addressing information security within supplier agreements | Review supplier agreements | Supplier agreement review |
| A.5.21 | Managing information security in the ICT supply chain | Review ICT supply chain security | Supply chain security review |
| A.5.22 | Monitoring, review and change management of supplier services | Review supplier monitoring | Supplier monitoring records |
| A.5.23 | Information security for use of cloud services | Review cloud security | Cloud security assessment |
| A.5.24 | Information security incident management planning and preparation | Review incident management | Incident management plan |
| A.5.25 | Assessment and decision on information security events | Review incident assessment | Incident assessment records |
| A.5.26 | Response to information security incidents | Test incident response | Incident response test results |
| A.5.27 | Learning from information security incidents | Review incident lessons learned | Lessons learned documentation |
| A.5.28 | Collection of evidence | Test evidence collection | Evidence collection procedure |
| A.5.29 | Information security during disruption | Test business continuity | Business continuity plan |
| A.5.30 | ICT readiness for business continuity | Test ICT continuity | ICT continuity plan |
| A.5.31 | Legal, statutory, regulatory and contractual requirements | Review legal requirements | Legal requirements register |
| A.5.32 | Intellectual property rights | Review IP protection | IP protection policy |
| A.5.33 | Protection of records | Test record protection | Record protection procedure |
| A.5.34 | Privacy and protection of PII | Test PII protection | PII protection assessment |
| A.5.35 | Independent review of information security | Review independent security reviews | Independent review reports |
| A.5.36 | Compliance with policies, rules and standards for information security | Test policy compliance | Policy compliance review |
| A.5.37 | Documented operating procedures | Review operating procedures | Operating procedure documents |

#### A.6: People Controls

| Control | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| A.6.1 | Screening | Test employee screening | Screening procedure review |
| A.6.2 | Terms and conditions of employment | Review employment terms | Employment contract review |
| A.6.3 | Information security awareness, education and training | Review security awareness program | Training records |
| A.6.4 | Disciplinary process | Review disciplinary process | Disciplinary procedure |
| A.6.5 | Responsibilities after termination or change of employment | Test offboarding process | Offboarding procedure |
| A.6.6 | Confidentiality or non-disclosure agreements | Review NDAs | NDA review |
| A.6.7 | Remote working | Test remote working security | Remote working policy |
| A.6.8 | Information security event reporting | Test event reporting | Event reporting procedure |

#### A.7: Technological Controls

| Control | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| A.7.1 | User endpoint devices | Test endpoint security | Endpoint security review |
| A.7.2 | Privileged access rights | Test privileged access | Privileged access review |
| A.7.3 | Information access restriction | Test access restriction | Access restriction review |
| A.7.4 | Access to source code | Test source code access | Source code access review |
| A.7.5 | Secure authentication | Test authentication | Authentication test results |
| A.7.6 | Capacity management | Test capacity management | Capacity management review |
| A.7.7 | Protection against malware | Test malware protection | Malware protection review |
| A.7.8 | Management of technical vulnerabilities | Test vulnerability management | Vulnerability management review |
| A.7.9 | Configuration management | Test configuration management | Configuration management review |
| A.7.10 | Information deletion | Test information deletion | Deletion procedure review |
| A.7.11 | Data masking | Test data masking | Data masking review |
| A.7.12 | Data leakage prevention | Test DLP | DLP configuration review |
| A.7.13 | Information backup | Test backup procedures | Backup procedure review |
| A.7.14 | Redundancy of information processing facilities | Test redundancy | Redundancy review |
| A.7.15 | Logging | Test logging | Logging configuration review |
| A.7.16 | Monitoring activities | Test monitoring | Monitoring configuration review |
| A.7.17 | Clock synchronization | Test clock synchronization | NTP configuration review |
| A.7.18 | Use of privileged utility programs | Test privileged utilities | Privileged utility review |
| A.7.19 | Software installation on operational systems | Test software installation | Software installation policy |
| A.7.20 | Networks security | Test network security | Network security assessment |
| A.7.21 | Security of network services | Test network services security | Network services review |
| A.7.22 | Segregation of networks | Test network segregation | Network segregation review |
| A.7.23 | Web filtering | Test web filtering | Web filtering configuration |
| A.7.24 | Use of cryptography | Test cryptography | Cryptography configuration review |
| A.7.25 | Secure development life cycle | Test SDLC | SDLC review |
| A.7.26 | Secure application architecture and engineering principles | Test secure architecture | Architecture review |
| A.7.27 | Secure coding | Test secure coding practices | Code review results |
| A.7.28 | Security testing in development and acceptance | Test security testing | Security testing review |
| A.7.29 | Outsourced development | Test outsourced development security | Outsourced development review |
| A.7.30 | Separation of development, test and production environments | Test environment separation | Environment separation review |
| A.7.31 | Change management | Test change management | Change management review |
| A.7.32 | Test information | Test test information protection | Test information review |
| A.7.33 | Protection of information systems during audit testing | Test audit protection | Audit protection review |

#### A.8: Physical Controls

| Control | Description | Testing Procedure | Evidence Required |
|---------|-------------|-------------------|-------------------|
| A.8.1 | Physical security perimeters | Test physical perimeters | Physical security assessment |
| A.8.2 | Physical entry | Test physical entry controls | Physical entry review |
| A.8.3 | Securing offices, rooms and facilities | Test facility security | Facility security review |
| A.8.4 | Physical security monitoring | Test physical monitoring | Physical monitoring review |
| A.8.5 | Protecting against physical and environmental threats | Test environmental controls | Environmental controls review |
| A.8.6 | Secure working areas | Test secure working areas | Secure area review |
| A.8.7 | Clear desk and clear screen | Test clear desk policy | Clear desk policy review |
| A.8.8 | Equipment siting and protection | Test equipment siting | Equipment siting review |
| A.8.9 | Security of assets off-premises | Test off-premises security | Off-premises security review |
| A.8.10 | Storage media | Test storage media security | Storage media review |
| A.8.11 | Supporting utilities | Test supporting utilities | Utilities review |
| A.8.12 | Cabling security | Test cabling security | Cabling security review |
| A.8.13 | Equipment maintenance | Test equipment maintenance | Maintenance records |
| A.8.14 | Secure disposal or re-use of equipment | Test equipment disposal | Disposal procedure review |

---

## SOC 2

System and Organization Controls 2 — Trust Service Criteria

### Security (Common Criteria)

| Criteria | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| CC1.1 | Control environment | Review governance structure | Governance documentation |
| CC1.2 | Communication and information | Review communication policies | Communication policy |
| CC1.3 | Risk assessment | Review risk assessment | Risk assessment report |
| CC1.4 | Monitoring activities | Review monitoring activities | Monitoring documentation |
| CC1.5 | Control activities | Review control activities | Control activity documentation |
| CC2.1 | Logical and physical access controls | Test access controls | Access control review |
| CC2.2 | System operations and monitoring | Test system monitoring | Monitoring configuration review |
| CC2.3 | Change management | Test change management | Change management review |
| CC2.4 | Risk mitigation | Test risk mitigation | Risk mitigation review |

### Availability

| Criteria | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| A1.1 | Availability monitoring | Test availability monitoring | Availability monitoring review |
| A1.2 | Capacity planning | Test capacity planning | Capacity planning review |
| A1.3 | Recovery procedures | Test recovery procedures | Recovery procedure review |

### Processing Integrity

| Criteria | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| PI1.1 | Processing integrity monitoring | Test processing integrity | Processing integrity review |
| PI1.2 | Data quality | Test data quality | Data quality review |
| PI1.3 | Error handling | Test error handling | Error handling review |

### Confidentiality

| Criteria | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| C1.1 | Confidentiality policies | Review confidentiality policies | Confidentiality policy |
| C1.2 | Confidentiality controls | Test confidentiality controls | Confidentiality control review |
| C1.3 | Data classification | Test data classification | Data classification review |
| C1.4 | Data retention | Test data retention | Data retention review |

### Privacy

| Criteria | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| P1.1 | Privacy policies | Review privacy policies | Privacy policy |
| P1.2 | Privacy controls | Test privacy controls | Privacy control review |
| P1.3 | Data subject rights | Test data subject rights | Data subject rights review |
| P1.4 | Consent management | Test consent management | Consent management review |

---

## NIST CSF

National Institute of Standards and Technology — Cybersecurity Framework

### Identify

| Category | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| ID.AM | Asset management | Review asset inventory | Asset inventory |
| ID.BE | Business environment | Review business environment | Business environment documentation |
| ID.GV | Governance | Review governance structure | Governance documentation |
| ID.RA | Risk assessment | Review risk assessment | Risk assessment report |
| ID.RM | Risk management strategy | Review risk management strategy | Risk management strategy |
| ID.SC | Supply chain risk management | Review supply chain risk | Supply chain risk assessment |

### Protect

| Category | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| PR.AC | Identity management and access control | Test access controls | Access control review |
| PR.AT | Awareness and training | Review training program | Training records |
| PR.DS | Data security | Test data security | Data security review |
| PR.IP | Information protection processes and procedures | Review protection processes | Protection process documentation |
| PR.MA | Maintenance | Test maintenance procedures | Maintenance records |
| PR.PT | Protective technology | Test protective technology | Protective technology review |

### Detect

| Category | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| DE.AE | Anomalies and events | Test anomaly detection | Anomaly detection review |
| DE.CM | Security continuous monitoring | Test continuous monitoring | Continuous monitoring review |
| DE.DP | Detection processes | Test detection processes | Detection process review |

### Respond

| Category | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| RS.RP | Response planning | Test response planning | Response plan |
| RS.CO | Communications | Test incident communications | Communication procedure |
| RS.AN | Analysis | Test incident analysis | Incident analysis procedure |
| RS.MI | Mitigation | Test incident mitigation | Mitigation procedure |
| RS.IM | Improvements | Test incident improvements | Improvement procedure |

### Recover

| Category | Description | Testing Procedure | Evidence Required |
|----------|-------------|-------------------|-------------------|
| RC.RP | Recovery planning | Test recovery planning | Recovery plan |
| RC.IM | Improvements | Test recovery improvements | Improvement procedure |
| RC.CO | Communications | Test recovery communications | Communication procedure |

---

## GDPR

General Data Protection Regulation — Security Requirements

### Article 5: Principles Relating to Processing of Personal Data

| Principle | Description | Testing Procedure | Evidence Required |
|-----------|-------------|-------------------|-------------------|
| 5(1)(a) | Lawfulness, fairness and transparency | Review data processing policies | Processing policy documentation |
| 5(1)(b) | Purpose limitation | Review purpose limitation | Purpose limitation documentation |
| 5(1)(c) | Data minimization | Test data minimization | Data minimization review |
| 5(1)(d) | Accuracy | Test data accuracy | Data accuracy review |
| 5(1)(e) | Storage limitation | Test storage limitation | Storage limitation review |
| 5(1)(f) | Integrity and confidentiality | Test security measures | Security measures review |

### Article 25: Data Protection by Design and by Default

| Requirement | Description | Testing Procedure | Evidence Required |
|-------------|-------------|-------------------|-------------------|
| 25(1) | Data protection by design | Review privacy by design | Privacy by design documentation |
| 25(2) | Data protection by default | Test default privacy settings | Default settings review |

### Article 32: Security of Processing

| Requirement | Description | Testing Procedure | Evidence Required |
|-------------|-------------|-------------------|-------------------|
| 32(1)(a) | Pseudonymization and encryption | Test encryption | Encryption configuration review |
| 32(1)(b) | Confidentiality, integrity, availability | Test CIA controls | CIA controls review |
| 32(1)(c) | Restore availability and access | Test recovery procedures | Recovery procedure review |
| 32(1)(d) | Regular testing and evaluation | Test security testing | Security testing review |
| 32(2) | Processor security | Test processor security | Processor security review |

### Article 33: Notification of a Personal Data Breach

| Requirement | Description | Testing Procedure | Evidence Required |
|-------------|-------------|-------------------|-------------------|
| 33(1) | Breach notification to supervisory authority | Test breach notification | Breach notification procedure |
| 33(2) | Processor notification to controller | Test processor notification | Processor notification procedure |
| 33(3) | Breach documentation | Test breach documentation | Breach documentation review |

### Article 34: Communication of a Personal Data Breach to the Data Subject

| Requirement | Description | Testing Procedure | Evidence Required |
|-------------|-------------|-------------------|-------------------|
| 34(1) | Breach communication | Test breach communication | Breach communication procedure |
| 34(2) | Exceptions to communication | Test communication exceptions | Exception procedure review |

### Article 35: Data Protection Impact Assessment

| Requirement | Description | Testing Procedure | Evidence Required |
|-------------|-------------|-------------------|-------------------|
| 35(1) | DPIA requirement | Review DPIA | DPIA documentation |
| 35(2) | DPIA content | Review DPIA content | DPIA content review |
| 35(3) | DPIA consultation | Test DPIA consultation | DPIA consultation records |

---

## Quick Reference

| Framework | Primary Focus | Key Testing Areas |
|-----------|--------------|-------------------|
| PCI DSS v4.0 | Payment card data | Network security, access control, encryption, vulnerability management |
| HIPAA | Healthcare data | Administrative, physical, technical safeguards |
| ISO 27001 | Information security management | Risk assessment, controls, continuous improvement |
| SOC 2 | Service organization controls | Security, availability, processing integrity, confidentiality, privacy |
| NIST CSF | Cybersecurity risk management | Identify, protect, detect, respond, recover |
| GDPR | Personal data protection | Data protection by design, breach notification, DPIA |
