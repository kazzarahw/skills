# Executive Summary Guide

How to write effective executive summaries for security reports.

---

## Table of Contents

1. [Purpose and Audience](#purpose-and-audience)
2. [Structure](#structure)
3. [Tone Guidelines](#tone-guidelines)
4. [Length](#length)
5. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
6. [Examples](#examples)

---

## Purpose and Audience

The executive summary is the most important section of the report. It is the only section that many readers will read in full. It must:

- Provide a clear, concise overview of the engagement and its findings
- Communicate business risk in non-technical terms
- Enable executives to make informed decisions about remediation priorities
- Build trust by demonstrating thoroughness and professionalism

**Primary audience:** C-suite executives, board members, and non-technical stakeholders.

**Secondary audience:** IT and security teams who need a high-level overview before diving into technical details.

---

## Structure

The executive summary should be 3-4 paragraphs, written in this order:

### Paragraph 1: Engagement Overview

- What was tested (systems, applications, contracts)
- When the testing occurred
- High-level outcome (e.g., "The assessment identified several areas of concern that require attention")
- **Do NOT** include specific vulnerability counts or severity labels in this paragraph

**Example:**
> Between [START_DATE] and [END_DATE], [COMPANY] conducted a comprehensive security assessment of [TARGET_SYSTEMS]. The assessment evaluated the security posture of [SCOPE_DESCRIPTION] and identified areas where security controls could be strengthened to better protect [ORGANIZATION]'s assets and data.

### Paragraph 2: Business Impact

- What the findings mean for the organization
- Focus on risk to operations, data, reputation, and compliance
- Use plain language — no jargon or technical terms
- Be direct but not alarmist

**Example:**
> The assessment revealed vulnerabilities that could potentially allow unauthorized access to sensitive customer data, disrupt business operations, or result in financial loss. Several of the identified issues are commonly exploited by attackers and could be leveraged as entry points for more extensive compromise. Addressing these findings will significantly reduce the organization's exposure to cyber threats and strengthen its overall security posture.

### Paragraph 3: Strategic Recommendations

- 2-3 high-level recommendations
- Address root causes, not individual vulnerabilities
- Focus on systemic improvements

**Example:**
> We recommend that [ORGANIZATION] prioritize the following actions: (1) implement a formal vulnerability management program with regular scanning and patching cycles, (2) enhance access controls across all systems to enforce the principle of least privilege, and (3) establish a security awareness training program to reduce the risk of social engineering attacks. These measures will address the underlying issues that contributed to the findings and provide long-term security benefits.

### Paragraph 4: Positive Observations

- What the organization is doing well
- Builds trust and provides balance
- Demonstrates that the assessment was fair and thorough

**Example:**
> [ORGANIZATION] has several security measures in place that demonstrate a commitment to security, including [POSITIVE_OBSERVATION_1] and [POSITIVE_OBSERVATION_2]. These controls provide a solid foundation upon which to build additional security capabilities.

---

## Tone Guidelines

### DO:
- Write for a non-technical executive audience
- Use clear, direct language
- Be honest about risks without being alarmist
- Focus on business impact, not technical detail
- Use active voice
- Be specific about recommendations

### DON'T:
- Use jargon, acronyms without explanation, or technical terms
- Use inflammatory language ("catastrophic," "disastrous," "negligent")
- Assign blame or make accusations
- Include specific vulnerability counts or severity labels
- Make recommendations that are too technical or vague
- Write more than 4 paragraphs

### Language Guidelines

| Instead of... | Use... |
|---------------|--------|
| "Critical vulnerability" | "Serious security issue" |
| "Exploitable" | "Could be used by an attacker" |
| "Attack surface" | "Entry points" |
| "Attack vector" | "Method of attack" |
| "Remediation" | "Fix" or "Address" |
| "Patch" | "Update" |
| "Exploit" | "Attack technique" |

---

## Length

- **Target:** 3-4 paragraphs, 300-500 words total
- **Maximum:** 1 page
- The executive summary should be readable in 2-3 minutes

---

## Common Mistakes to Avoid

### 1. Writing the Executive Summary First

The executive summary must be written **last**, after all findings are finalized. Writing it first leads to inconsistencies when findings change during the engagement.

### 2. Including Too Much Technical Detail

The executive summary is not the place for CVSS scores, CVE IDs, or technical explanations. Save those for the detailed findings section.

### 3. Using Alarmist Language

Phrases like "catastrophic failure" or "complete compromise" undermine credibility. Be direct and factual.

### 4. Vague Recommendations

"Improve security" is not a recommendation. "Implement multi-factor authentication for all remote access" is.

### 5. Ignoring Positive Observations

Every engagement finds things the organization is doing well. Acknowledging these builds trust and makes the report more credible.

### 6. Inconsistent with Findings

The executive summary must accurately reflect the findings. If the findings change during the engagement, update the executive summary.

### 7. Missing Business Impact

Executives care about business risk, not technical vulnerabilities. Always connect findings to business impact.

---

## Examples

### Good Executive Summary

> Between January 15 and January 26, 2024, Acme Security conducted a comprehensive penetration test of Example Corp's web applications, APIs, and network infrastructure. The assessment evaluated the security posture of systems that handle sensitive customer data and financial transactions, and identified several areas where security controls could be strengthened.
>
> The assessment revealed vulnerabilities that could potentially allow unauthorized access to customer data, disrupt business operations, or result in financial loss. Several of the identified issues are commonly exploited by attackers and could serve as entry points for more extensive compromise. Of particular concern were weaknesses in authentication mechanisms and access controls that could allow an attacker to gain unauthorized access to sensitive systems.
>
> We recommend that Example Corp prioritize the following actions: (1) implement multi-factor authentication for all user accounts, particularly those with administrative privileges, (2) enhance input validation across all web applications to prevent injection attacks, and (3) establish a formal vulnerability management program with regular scanning and patching cycles. These measures will address the underlying issues that contributed to the findings and provide long-term security benefits.
>
> Example Corp has several security measures in place that demonstrate a commitment to security, including network segmentation, regular security updates, and a dedicated security team. These controls provide a solid foundation upon which to build additional security capabilities.

### Bad Executive Summary

> We found 3 critical, 7 high, 12 medium, and 5 low vulnerabilities during our penetration test. The CVSS scores ranged from 4.2 to 9.8. The most critical finding was a SQL injection vulnerability (CWE-89) in the login form that could allow an attacker to extract the entire user database. We also found stored XSS (CWE-79), CSRF (CWE-352), and several authentication bypass issues. The attack surface was huge and the organization is basically negligent in their security practices. They need to fix everything immediately or they will get hacked.
>
> We recommend patching all vulnerabilities, implementing WAF rules, fixing the SDLC, and training developers. Also, they should do penetration tests more often and implement a bug bounty program.
>
> The organization has a firewall and antivirus.

**Why this is bad:**
- Too technical (CVSS scores, CWE IDs, vulnerability counts)
- Alarmist language ("negligent," "will get hacked")
- Vague recommendations ("fix everything")
- No business impact
- No positive observations
- Too long and unfocused

---

## Checklist

Before finalizing the executive summary, verify:

- [ ] Written last, after all findings are finalized
- [ ] 3-4 paragraphs, 300-500 words
- [ ] No jargon or unexplained acronyms
- [ ] No specific vulnerability counts or severity labels
- [ ] Business impact clearly stated
- [ ] 2-3 specific, actionable recommendations
- [ ] Positive observations included
- [ ] Tone is direct but not alarmist
- [ ] Consistent with detailed findings
- [ ] Readable in 2-3 minutes
