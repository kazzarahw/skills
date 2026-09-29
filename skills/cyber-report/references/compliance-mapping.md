# Compliance Mapping

> **Priority**: Medium | **Skill**: cyber-report | **Last Updated**: 2026-09-28

A mapping of findings to compliance frameworks for penetration testing reports.

---

## PCI DSS 4.0 Mapping

### Requirement 1: Install and Maintain Network Security Controls

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 1.2.1 | WSTG-CONF-01 | Network segmentation issues |
| 1.2.2 | WSTG-CONF-01 | Firewall rule misconfigurations |
| 1.2.3 | WSTG-CONF-01 | Insecure network protocols |
| 1.2.4 | WSTG-CONF-01 | Wireless network vulnerabilities |
| 1.3.1 | WSTG-CONF-01 | Missing network security controls |
| 1.4.1 | WSTG-CONF-01 | Insecure remote access |
| 1.5.1 | WSTG-CONF-01 | Missing network documentation |

### Requirement 2: Apply Secure Configurations to All System Components

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 2.2.1 | WSTG-CONF-02 | Default credentials |
| 2.2.2 | WSTG-CONF-02 | Unnecessary services enabled |
| 2.2.3 | WSTG-CONF-02 | Insecure configuration |
| 2.2.4 | WSTG-CONF-02 | Missing security patches |
| 2.2.5 | WSTG-CONF-02 | Insecure protocols enabled |
| 2.2.6 | WSTG-CONF-02 | Unnecessary functionality enabled |
| 2.2.7 | WSTG-CONF-02 | Insecure default settings |

### Requirement 3: Protect Stored Account Data

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 3.5.1 | WSTG-CRYP-01 | Weak cryptographic algorithms |
| 3.5.2 | WSTG-CRYP-01 | Insecure key management |
| 3.6.1 | WSTG-CRYP-01 | Cleartext storage of PAN |
| 3.7.1 | WSTG-CRYP-01 | Insecure data storage |

### Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 4.1.1 | WSTG-CRYP-02 | Cleartext transmission of PAN |
| 4.2.1 | WSTG-CRYP-02 | Weak SSL/TLS configuration |
| 4.2.2 | WSTG-CRYP-02 | Insecure cryptographic protocols |

### Requirement 5: Protect All Systems and Networks from Malicious Software

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 5.2.1 | WSTG-MAL-01 | Missing antivirus/anti-malware |
| 5.2.2 | WSTG-MAL-01 | Outdated malware protection |
| 5.3.1 | WSTG-MAL-01 | Insecure malware protection config |

### Requirement 6: Develop and Maintain Secure Systems and Software

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 6.2.1 | WSTG-INFO-01 | Missing security patches |
| 6.2.2 | WSTG-INFO-01 | Outdated software versions |
| 6.3.1 | WSTG-INFO-01 | Insecure coding practices |
| 6.3.2 | WSTG-INFO-01 | Missing security controls |
| 6.3.3 | WSTG-INFO-01 | Insecure software development |
| 6.4.1 | WSTG-INFO-01 | Insecure third-party software |
| 6.4.2 | WSTG-INFO-01 | Insecure payment page scripts |
| 6.5.1 | WSTG-INPV-01 | Injection vulnerabilities |
| 6.5.2 | WSTG-INPV-01 | SQL injection |
| 6.5.3 | WSTG-INPV-01 | OS command injection |
| 6.5.4 | WSTG-INPV-01 | Buffer overflow |
| 6.5.5 | WSTG-INPV-01 | Cross-site scripting (XSS) |
| 6.5.6 | WSTG-INPV-01 | Cross-site request forgery (CSRF) |
| 6.5.7 | WSTG-INPV-01 | File upload vulnerabilities |
| 6.5.8 | WSTG-INPV-01 | Insecure deserialization |
| 6.5.9 | WSTG-INPV-01 | Insecure API usage |
| 6.5.10 | WSTG-INPV-01 | Insecure cryptographic usage |

### Requirement 7: Restrict Access to System Components and Cardholder Data

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 7.1.1 | WSTG-ATHN-01 | Missing access controls |
| 7.1.2 | WSTG-ATHN-01 | Insecure access control implementation |
| 7.2.1 | WSTG-ATHN-01 | Missing authorization checks |
| 7.2.2 | WSTG-ATHN-01 | Insecure authorization implementation |
| 7.3.1 | WSTG-ATHN-01 | Excessive privileges |

### Requirement 8: Identify Users and Authenticate Access to System Components

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 8.2.1 | WSTG-ATHN-02 | Weak authentication mechanisms |
| 8.2.2 | WSTG-ATHN-02 | Insecure password policies |
| 8.2.3 | WSTG-ATHN-02 | Insecure credential storage |
| 8.2.4 | WSTG-ATHN-02 | Insecure credential transmission |
| 8.2.5 | WSTG-ATHN-02 | Insecure multi-factor authentication |
| 8.3.1 | WSTG-ATHN-02 | Missing multi-factor authentication |
| 8.3.2 | WSTG-ATHN-02 | Insecure multi-factor authentication |
| 8.4.1 | WSTG-ATHN-02 | Insecure authentication bypass |

### Requirement 9: Restrict Physical Access to Cardholder Data

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 9.1.1 | WSTG-INFO-01 | Physical security controls |
| 9.2.1 | WSTG-INFO-01 | Physical access controls |
| 9.3.1 | WSTG-INFO-01 | Physical security monitoring |
| 9.4.1 | WSTG-INFO-01 | Physical media security |
| 9.5.1 | WSTG-INFO-01 | Physical media destruction |

### Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 10.2.1 | WSTG-ERRH-01 | Missing audit logging |
| 10.2.2 | WSTG-ERRH-01 | Insecure audit logging |
| 10.3.1 | WSTG-ERRH-01 | Missing log protection |
| 10.3.2 | WSTG-ERRH-01 | Insecure log protection |
| 10.4.1 | WSTG-ERRH-01 | Missing log monitoring |
| 10.4.2 | WSTG-ERRH-01 | Insecure log monitoring |
| 10.5.1 | WSTG-ERRH-01 | Missing log review |
| 10.6.1 | WSTG-ERRH-01 | Missing intrusion detection |
| 10.7.1 | WSTG-ERRH-01 | Missing log retention |

### Requirement 11: Test Security of Systems and Networks Regularly

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 11.3.1 | WSTG-INFO-01 | Missing vulnerability scanning |
| 11.3.2 | WSTG-INFO-01 | Missing penetration testing |
| 11.3.3 | WSTG-INFO-01 | Missing intrusion detection testing |
| 11.4.1 | WSTG-INFO-01 | Missing intrusion prevention testing |
| 11.5.1 | WSTG-INFO-01 | Missing file integrity monitoring |

### Requirement 12: Support Security Policies with Organizational Policies and Programs

| PCI DSS 4.0 | WSTG Category | Finding Types |
|-------------|---------------|---------------|
| 12.1.1 | WSTG-INFO-01 | Missing security policies |
| 12.2.1 | WSTG-INFO-01 | Insecure security policies |
| 12.3.1 | WSTG-INFO-01 | Missing risk assessment |
| 12.4.1 | WSTG-INFO-01 | Missing security awareness training |
| 12.5.1 | WSTG-INFO-01 | Missing incident response plan |
| 12.6.1 | WSTG-INFO-01 | Missing security procedures |
| 12.7.1 | WSTG-INFO-01 | Missing vendor management |
| 12.8.1 | WSTG-INFO-01 | Missing third-party security |
| 12.9.1 | WSTG-INFO-01 | Missing change management |
| 12.10.1 | WSTG-INFO-01 | Missing incident response testing |

---

## HIPAA Security Rule Mapping

### Administrative Safeguards

| HIPAA Section | WSTG Category | Finding Types |
|--------------|---------------|---------------|
| 164.308(a)(1) | WSTG-INFO-01 | Security management process |
| 164.308(a)(2) | WSTG-INFO-01 | Assigned security responsibility |
| 164.308(a)(3) | WSTG-ATHN-01 | Workforce security |
| 164.308(a)(4) | WSTG-ATHN-01 | Information access management |
| 164.308(a)(5) | WSTG-INFO-01 | Security awareness training |
| 164.308(a)(6) | WSTG-INFO-01 | Security incident procedures |
| 164.308(a)(7) | WSTG-INFO-01 | Contingency plan |
| 164.308(a)(8) | WSTG-INFO-01 | Evaluation |
| 164.308(b)(1) | WSTG-INFO-01 | Business associate contracts |

### Physical Safeguards

| HIPAA Section | WSTG Category | Finding Types |
|--------------|---------------|---------------|
| 164.310(a)(1) | WSTG-INFO-01 | Facility access controls |
| 164.310(a)(2)(i) | WSTG-INFO-01 | Contingency operations |
| 164.310(a)(2)(ii) | WSTG-INFO-01 | Facility security plan |
| 164.310(a)(2)(iii) | WSTG-INFO-01 | Access control and validation |
| 164.310(a)(2)(iv) | WSTG-INFO-01 | Maintenance records |
| 164.310(b)(1) | WSTG-INFO-01 | Workstation use |
| 164.310(b)(2) | WSTG-INFO-01 | Workstation security |
| 164.310(c)(1) | WSTG-INFO-01 | Device and media controls |
| 164.310(c)(2) | WSTG-INFO-01 | Media re-use |
| 164.310(d)(1) | WSTG-INFO-01 | Data backup and storage |

### Technical Safeguards

| HIPAA Section | WSTG Category | Finding Types |
|--------------|---------------|---------------|
| 164.312(a)(1) | WSTG-ATHN-01 | Access control |
| 164.312(a)(2)(i) | WSTG-ATHN-01 | Unique user identification |
| 164.312(a)(2)(ii) | WSTG-ATHN-01 | Emergency access procedure |
| 164.312(a)(2)(iii) | WSTG-ATHN-01 | Automatic logoff |
| 164.312(a)(2)(iv) | WSTG-ATHN-01 | Encryption and decryption |
| 164.312(b)(1) | WSTG-ERRH-01 | Audit controls |
| 164.312(c)(1) | WSTG-CRYP-01 | Integrity controls |
| 164.312(c)(2) | WSTG-CRYP-01 | Mechanism to authenticate ePHI |
| 164.312(d)(1) | WSTG-ATHN-02 | Person or entity authentication |
| 164.312(e)(1) | WSTG-CRYP-02 | Transmission security |
| 164.312(e)(2)(i) | WSTG-CRYP-02 | Integrity controls |
| 164.312(e)(2)(ii) | WSTG-CRYP-02 | Encryption |

### Organizational Requirements

| HIPAA Section | WSTG Category | Finding Types |
|--------------|---------------|---------------|
| 164.314(a)(1) | WSTG-INFO-01 | Business associate contracts |
| 164.314(b)(1) | WSTG-INFO-01 | Requirements for group health plans |

### Policies, Procedures, and Documentation

| HIPAA Section | WSTG Category | Finding Types |
|--------------|---------------|---------------|
| 164.316(a)(1) | WSTG-INFO-01 | Policies and procedures |
| 164.316(b)(1) | WSTG-INFO-01 | Documentation |

---

## ISO 27001:2022 Mapping

### Annex A.5: Organizational Controls

| ISO 27001:2022 | WSTG Category | Finding Types |
|---------------|---------------|---------------|
| A.5.1 | WSTG-INFO-01 | Policies for information security |
| A.5.2 | WSTG-INFO-01 | Information security roles and responsibilities |
| A.5.3 | WSTG-INFO-01 | Segregation of duties |
| A.5.4 | WSTG-INFO-01 | Management responsibilities |
| A.5.5 | WSTG-INFO-01 | Contact with authorities |
| A.5.6 | WSTG-INFO-01 | Contact with special interest groups |
| A.5.7 | WSTG-INFO-01 | Threat intelligence |
| A.5.8 | WSTG-INFO-01 | Information security in project management |
| A.5.9 | WSTG-INFO-01 | Inventory of information and other associated assets |
| A.5.10 | WSTG-INFO-01 | Acceptable use of information and other associated assets |
| A.5.11 | WSTG-INFO-01 | Return of assets |
| A.5.12 | WSTG-INFO-01 | Classification of information |
| A.5.13 | WSTG-INFO-01 | Labelling of information |
| A.5.14 | WSTG-INFO-01 | Information transfer |
| A.5.15 | WSTG-INFO-01 | Access control |
| A.5.16 | WSTG-INFO-01 | Identity management |
| A.5.17 | WSTG-INFO-01 | Authentication information |
| A.5.18 | WSTG-INFO-01 | Access rights |
| A.5.19 | WSTG-INFO-01 | Information security in supplier relationships |
| A.5.20 | WSTG-INFO-01 | Addressing information security within supplier agreements |
| A.5.21 | WSTG-INFO-01 | Managing information security in the ICT supply chain |
| A.5.22 | WSTG-INFO-01 | Monitoring, review and change management of supplier services |
| A.5.23 | WSTG-INFO-01 | Information security for use of cloud services |
| A.5.24 | WSTG-INFO-01 | Information security incident management planning and preparation |
| A.5.25 | WSTG-INFO-01 | Assessment and decision on information security events |
| A.5.26 | WSTG-INFO-01 | Response to information security incidents |
| A.5.27 | WSTG-INFO-01 | Learning from information security incidents |
| A.5.28 | WSTG-INFO-01 | Collection of evidence |
| A.5.29 | WSTG-INFO-01 | Information security during disruption |
| A.5.30 | WSTG-INFO-01 | ICT readiness for business continuity |
| A.5.31 | WSTG-INFO-01 | Legal, statutory, regulatory and contractual requirements |
| A.5.32 | WSTG-INFO-01 | Intellectual property rights |
| A.5.33 | WSTG-INFO-01 | Protection of records |
| A.5.34 | WSTG-INFO-01 | Privacy and protection of PII |
| A.5.35 | WSTG-INFO-01 | Independent review of information security |
| A.5.36 | WSTG-INFO-01 | Compliance with policies, rules and standards for information security |
| A.5.37 | WSTG-INFO-01 | Documented operating procedures |

### Annex A.6: People Controls

| ISO 27001:2022 | WSTG Category | Finding Types |
|---------------|---------------|---------------|
| A.6.1 | WSTG-INFO-01 | Screening |
| A.6.2 | WSTG-INFO-01 | Terms and conditions of employment |
| A.6.3 | WSTG-INFO-01 | Information security awareness, education and training |
| A.6.4 | WSTG-INFO-01 | Disciplinary process |
| A.6.5 | WSTG-INFO-01 | Responsibilities after termination or change of employment |
| A.6.6 | WSTG-INFO-01 | Confidentiality or non-disclosure agreements |
| A.6.7 | WSTG-INFO-01 | Remote working |
| A.6.8 | WSTG-INFO-01 | Information security event reporting |

### Annex A.7: Technological Controls

| ISO 27001:2022 | WSTG Category | Finding Types |
|---------------|---------------|---------------|
| A.7.1 | WSTG-INFO-01 | Physical entry controls |
| A.7.2 | WSTG-INFO-01 | Securing offices, rooms and facilities |
| A.7.3 | WSTG-INFO-01 | Physical security monitoring |
| A.7.4 | WSTG-INFO-01 | Physical and environmental threat protection |
| A.7.5 | WSTG-INFO-01 | Working in secure areas |
| A.7.6 | WSTG-INFO-01 | Clear desk and clear screen |
| A.7.7 | WSTG-INFO-01 | Equipment siting and protection |
| A.7.8 | WSTG-INFO-01 | Security of assets off-premises |
| A.7.9 | WSTG-INFO-01 | Storage media |
| A.7.10 | WSTG-INFO-01 | Supporting utilities |
| A.7.11 | WSTG-INFO-01 | Cabling security |
| A.7.12 | WSTG-INFO-01 | Equipment maintenance |
| A.7.13 | WSTG-INFO-01 | Secure disposal or re-use of equipment |
| A.7.14 | WSTG-INFO-01 | Unattended user equipment |
| A.7.15 | WSTG-INFO-01 | Clear desk and clear screen |
| A.7.16 | WSTG-INFO-01 | Equipment siting and protection |
| A.7.17 | WSTG-INFO-01 | Security of assets off-premises |
| A.7.18 | WSTG-INFO-01 | Storage media |
| A.7.19 | WSTG-INFO-01 | Supporting utilities |
| A.7.20 | WSTG-INFO-01 | Cabling security |
| A.7.21 | WSTG-INFO-01 | Equipment maintenance |
| A.7.22 | WSTG-INFO-01 | Secure disposal or re-use of equipment |
| A.7.23 | WSTG-INFO-01 | Unattended user equipment |
| A.7.24 | WSTG-INFO-01 | Information security event reporting |
| A.7.25 | WSTG-INFO-01 | Assessment and decision on information security events |
| A.7.26 | WSTG-INFO-01 | Response to information security incidents |
| A.7.27 | WSTG-INFO-01 | Learning from information security incidents |
| A.7.28 | WSTG-INFO-01 | Collection of evidence |
| A.7.29 | WSTG-INFO-01 | Information security during disruption |
| A.7.30 | WSTG-INFO-01 | ICT readiness for business continuity |
| A.7.31 | WSTG-INFO-01 | Legal, statutory, regulatory and contractual requirements |
| A.7.32 | WSTG-INFO-01 | Intellectual property rights |
| A.7.33 | WSTG-INFO-01 | Protection of records |
| A.7.34 | WSTG-INFO-01 | Privacy and protection of PII |
| A.7.35 | WSTG-INFO-01 | Independent review of information security |
| A.7.36 | WSTG-INFO-01 | Compliance with policies, rules and standards for information security |
| A.7.37 | WSTG-INFO-01 | Documented operating procedures |

### Annex A.8: Technological Controls

| ISO 27001:2022 | WSTG Category | Finding Types |
|---------------|---------------|---------------|
| A.8.1 | WSTG-INFO-01 | User endpoint devices |
| A.8.2 | WSTG-INFO-01 | Privileged access rights |
| A.8.3 | WSTG-INFO-01 | Information access restriction |
| A.8.4 | WSTG-INFO-01 | Access to source code |
| A.8.5 | WSTG-INFO-01 | Secure authentication |
| A.8.6 | WSTG-INFO-01 | Capacity management |
| A.8.7 | WSTG-INFO-01 | Protection against malware |
| A.8.8 | WSTG-INFO-01 | Management of technical vulnerabilities |
| A.8.9 | WSTG-INFO-01 | Configuration management |
| A.8.10 | WSTG-INFO-01 | Information deletion |
| A.8.11 | WSTG-INFO-01 | Data masking |
| A.8.12 | WSTG-INFO-01 | Data leakage prevention |
| A.8.13 | WSTG-INFO-01 | Information backup |
| A.8.14 | WSTG-INFO-01 | Redundancy of information processing facilities |
| A.8.15 | WSTG-INFO-01 | Logging |
| A.8.16 | WSTG-INFO-01 | Monitoring activities |
| A.8.17 | WSTG-INFO-01 | Clock synchronization |
| A.8.18 | WSTG-INFO-01 | Use of privileged utility programs |
| A.8.19 | WSTG-INFO-01 | Software installation on operational systems |
| A.8.20 | WSTG-INFO-01 | Networks security |
| A.8.21 | WSTG-INFO-01 | Security of network services |
| A.8.22 | WSTG-INFO-01 | Segregation of networks |
| A.8.23 | WSTG-INFO-01 | Web filtering |
| A.8.24 | WSTG-INFO-01 | Use of cryptography |
| A.8.25 | WSTG-INFO-01 | Secure development life cycle |
| A.8.26 | WSTG-INFO-01 | Application security requirements |
| A.8.27 | WSTG-INFO-01 | Secure architecture and engineering principles |
| A.8.28 | WSTG-INFO-01 | Secure coding |
| A.8.29 | WSTG-INFO-01 | Security testing in development and acceptance |
| A.8.30 | WSTG-INFO-01 | Outsourced development |
| A.8.31 | WSTG-INFO-01 | Separation of development, test and production environments |
| A.8.32 | WSTG-INFO-01 | Change management |
| A.8.33 | WSTG-INFO-01 | Test information |
| A.8.34 | WSTG-INFO-01 | Protection of information systems during audit testing |

---

## How to Use the Mapping in Reports

### Step 1: Identify Finding Categories

For each finding, identify the relevant WSTG category:
- WSTG-INFO-01: Information Gathering
- WSTG-CONF-01: Configuration and Deploy Management
- WSTG-ATHN-01: Authentication
- WSTG-ATHN-02: Authorization
- WSTG-INPV-01: Input Validation
- WSTG-CRYP-01: Cryptography
- WSTG-ERRH-01: Error Handling
- WSTG-MAL-01: Malware

### Step 2: Map to Compliance Frameworks

Use the tables above to map each finding to relevant compliance requirements.

### Step 3: Generate Compliance Section

For each compliance framework, list:
- Applicable requirements
- Related findings
- Compliance status (Compliant/Non-Compliant/Partial)
- Remediation recommendations

### Step 4: Create Compliance Summary

Generate a summary table:

| Framework | Total Requirements | Compliant | Non-Compliant | Partial | Compliance Rate |
|-----------|-------------------|-----------|---------------|---------|-----------------|
| PCI DSS 4.0 | 78 | 45 | 20 | 13 | 57.7% |
| HIPAA | 42 | 28 | 10 | 4 | 66.7% |
| ISO 27001:2022 | 93 | 60 | 25 | 8 | 64.5% |

### Step 5: Provide Remediation Roadmap

For each non-compliant requirement:
- Priority (Critical/High/Medium/Low)
- Remediation steps
- Estimated effort
- Responsible party
- Target completion date

---

## References

- [PCI DSS v4.0](https://www.pcisecuritystandards.org/document_library/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [ISO 27001:2022](https://www.iso.org/standard/27001)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
