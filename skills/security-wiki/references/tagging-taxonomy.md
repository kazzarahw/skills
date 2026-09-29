# Tagging Taxonomy

Complete tag taxonomy for web2, web3, and cross-domain security findings.

---

## Table of Contents

- [Tag Categories](#tag-categories)
- [Domain Tags](#domain-tags)
  - [Domain Tag Rules](#domain-tag-rules)
- [Technique Tags](#technique-tags)
  - [Technique Tag Rules](#technique-tag-rules)
- [Vulnerability Tags](#vulnerability-tags)
  - [OWASP Top 10 (Web2)](#owasp-top-10-web2)
  - [SWC Registry (Web3)](#swc-registry-web3)
  - [CVE Tags](#cve-tags)
  - [Custom Tags](#custom-tags)
  - [Vulnerability Tag Rules](#vulnerability-tag-rules)
- [Severity Tags](#severity-tags)
  - [Severity Tag Rules](#severity-tag-rules)
- [Engagement Tags](#engagement-tags)
  - [Engagement Tag Rules](#engagement-tag-rules)
  - [Examples](#examples)
- [Status Tags](#status-tags)
  - [Status Tag Rules](#status-tag-rules)
- [Tool Tags](#tool-tags)
  - [Common Tool Tags](#common-tool-tags)
  - [Tool Tag Rules](#tool-tag-rules)
- [Chain Tags (Web3 Only)](#chain-tags-web3-only)
  - [Chain Tag Rules](#chain-tag-rules)
- [Protocol Tags (Web3 Only)](#protocol-tags-web3-only)
  - [Protocol Tag Rules](#protocol-tag-rules)
- [Tag Combination Rules](#tag-combination-rules)
  - [Required Combinations](#required-combinations)
  - [Prohibited Combinations](#prohibited-combinations)
  - [Recommended Combinations](#recommended-combinations)
- [Tag Selection Guide](#tag-selection-guide)
  - [Step 1: Identify Domain](#step-1-identify-domain)
  - [Step 2: Identify Technique](#step-2-identify-technique)
  - [Step 3: Classify Vulnerability](#step-3-classify-vulnerability)
  - [Step 4: Assign Severity](#step-4-assign-severity)
  - [Step 5: Add Engagement Context](#step-5-add-engagement-context)
  - [Step 6: Add Status](#step-6-add-status)
  - [Step 7: Add Tool and Chain (if applicable)](#step-7-add-tool-and-chain-if-applicable)
- [Tag Validation](#tag-validation)
  - [Invalid Tag Examples](#invalid-tag-examples)
- [Taxonomy Maintenance](#taxonomy-maintenance)
  - [Adding New Tags](#adding-new-tags)
  - [Deprecating Tags](#deprecating-tags)
  - [Version Control](#version-control)

---

## Tag Categories

Tags are organized into the following categories:

1. **Domain Tags** — Which domain the finding belongs to
2. **Technique Tags** — What security activity produced the finding
3. **Vulnerability Tags** — Classification of the vulnerability
4. **Severity Tags** — Impact and urgency of the finding
5. **Engagement Tags** — Engagement and client identification
6. **Status Tags** — Current validity of the finding
7. **Tool Tags** — Tools used to produce the finding
8. **Chain Tags** — Blockchain chain (web3 only)
9. **Protocol Tags** — Protocol type (web3 only)

---

## Domain Tags

| Tag | Description | Usage |
|-----|-------------|-------|
| `web2` | Web application, network, infrastructure findings | Default for traditional security testing |
| `web3` | Blockchain, smart contract, DeFi findings | Default for blockchain security testing |
| `cross-domain` | Findings spanning both web2 and web3 | When a finding impacts both domains |

### Domain Tag Rules

- Every page MUST have exactly one domain tag
- Use `cross-domain` only when the finding genuinely spans both domains
- When in doubt, use the primary domain and add cross-references

---

## Technique Tags

| Tag | Description | Usage |
|-----|-------------|-------|
| `recon` | Reconnaissance and discovery | Information gathering, enumeration |
| `audit` | Security audit findings | Vulnerability assessment, code review |
| `exploit` | Exploitation techniques | Proof-of-concept, weaponized exploits |
| `forensics` | Investigation and analysis | Incident response, malware analysis |
| `report` | Reporting and documentation | Client reports, executive summaries |
| `verify` | Verification and validation | False positive verification, retesting |

### Technique Tag Rules

- Multiple technique tags allowed
- Use the primary technique that produced the finding
- Add secondary techniques if the finding spans multiple activities

---

## Vulnerability Tags

### OWASP Top 10 (Web2)

| Tag | Description |
|-----|-------------|
| `owasp-top10` | General OWASP Top 10 category |
| `injection` | SQL, NoSQL, OS command injection |
| `broken-auth` | Authentication and session management failures |
| `sensitive-data-exposure` | Data exposure vulnerabilities |
| `xxe` | XML External Entity vulnerabilities |
| `broken-access-control` | Authorization failures |
| `security-misconfig` | Default configs, incomplete configs |
| `xss` | Cross-site scripting |
| `insecure-deserialization` | Deserialization vulnerabilities |
| `vulnerable-components` | Outdated libraries and frameworks |
| `insufficient-logging` | Logging and monitoring gaps |

### SWC Registry (Web3)

| Tag | Description |
|-----|-------------|
| `swc-registry` | Smart Contract Weakness Classification |
| `reentrancy` | Reentrancy vulnerabilities |
| `access-control` | Smart contract access control issues |
| `arithmetic` | Integer overflow/underflow |
| `unprotected-ether` | Unprotected Ether withdrawal |
| `delegatecall` | Dangerous delegatecall usage |
| `tx-origin` | tx.origin authentication |
| `timestamp-dependence` | Block timestamp dependence |
| `short-address` | Short address attack |
| `default-visibility` | Default visibility issues |

### CVE Tags

| Tag | Description |
|-----|-------------|
| `cve` | CVE identifier present |
| `cve-critical` | CVE with critical severity |
| `cve-high` | CVE with high severity |

### Custom Tags

| Tag | Description |
|-----|-------------|
| `custom` | Custom vulnerability classification |
| `zero-day` | Previously unknown vulnerability |
| `n-day` | Known vulnerability, unpatched |
| `active-directory` | Active Directory related findings |
| `analysis` | Analysis and synthesis findings |
| `attack-path` | Attack path and chain analysis |
| `chain` | Chain-related findings |
| `marketplace` | Marketplace-related findings |
| `protocol` | Protocol-related findings |
| `target` | Target organization or entity |
| `timeline` | Timeline and chronological findings |
| `engagement` | Engagement-related findings |
| `overview` | Overview and landscape findings |
| `attack-surface` | Attack surface analysis |
| `attack` | General attack techniques |
| `flash-loan` | Flash loan specific findings |
| `artblock` | ArtBlock specific findings |
| `client-artblock` | ArtBlock client identification |
| `client-protodao` | ProtoDAO client identification |
| `eng-2026-001` | Engagement 2026-001 identifier |

### Vulnerability Tag Rules

- Use the most specific tag available
- Multiple vulnerability tags allowed
- Always use `owasp-top10` or `swc-registry` as parent category
- Add CVE tag if a CVE identifier exists

---

## Severity Tags

| Tag | Description | CVSS Range |
|-----|-------------|------------|
| `critical` | Immediate action required | 9.0-10.0 |
| `high` | Address in current sprint | 7.0-8.9 |
| `medium` | Address in next sprint | 4.0-6.9 |
| `low` | Address when convenient | 0.1-3.9 |
| `informational` | No action required | 0.0 |

### Severity Tag Rules

- Every finding MUST have exactly one severity tag
- Use CVSS score to determine severity level
- Severity can be upgraded or downgraded based on business context
- Document severity rationale in page content

---

## Engagement Tags

| Tag | Description | Format |
|-----|-------------|--------|
| `client-name` | Client or organization name | `client-{name}` |
| `engagement-id` | Engagement identifier | `eng-{YYYY-NNN}` |
| `date-range` | Engagement date range | `YYYY-MM` |

### Engagement Tag Rules

- Use `client-{name}` for client identification
- Use `eng-{YYYY-NNN}` for engagement tracking
- Use `YYYY-MM` for date-based filtering
- Multiple engagement tags allowed for cross-engagement findings

### Examples

```
tags: [client-targetcorp, eng-2026-001, 2026-09]
tags: [client-acme, eng-2026-002, 2026-08]
```

---

## Status Tags

| Tag | Description | Usage |
|-----|-------------|-------|
| `active` | Currently valid finding | Default for new findings |
| `invalidated` | Superseded by newer information | When finding is no longer valid |
| `draft` | Work in progress | Unreviewed content |
| `archived` | Historical reference only | Ended engagements |

### Status Tag Rules

- Every page MUST have exactly one status tag
- Default to `draft` for new pages
- Change to `active` after review
- Change to `invalidated` when superseded
- Change to `archived` when engagement ends

---

## Tool Tags

| Tag | Description | Format |
|-----|-------------|--------|
| `tool-name` | Tool used | `tool-{name}` |
| `tool-version` | Tool version | `tool-{name}-{version}` |

### Common Tool Tags

| Tag | Tool |
|-----|------|
| `tool-nmap` | Network mapper |
| `tool-nuclei` | Nuclei scanner |
| `tool-burp` | Burp Suite |
| `tool-metasploit` | Metasploit Framework |
| `tool-slither` | Slither analyzer |
| `tool-mythril` | Mythril analyzer |
| `tool-foundry` | Foundry (forge/cast) |
| `tool-hardhat` | Hardhat framework |
| `tool-echidna` | Echidna fuzzer |
| `tool-manticore` | Manticore symbolic executor |

### Tool Tag Rules

- Use `tool-{name}` for general tool reference
- Use `tool-{name}-{version}` for version-specific findings
- Multiple tool tags allowed
- Record tool version in frontmatter `tools` field

---

## Chain Tags (Web3 Only)

| Tag | Description |
|-----|-------------|
| `ethereum` | Ethereum mainnet or L2s |
| `solana` | Solana blockchain |
| `bitcoin` | Bitcoin blockchain |
| `cosmos` | Cosmos ecosystem |
| `multi-chain` | Multiple chains |
| `n/a` | Not applicable (web2) |

### Chain Tag Rules

- Required for all web3 pages
- Use `multi-chain` for cross-chain findings
- Use `n/a` for web2 pages
- Multiple chain tags allowed for multi-chain findings

---

## Protocol Tags (Web3 Only)

| Tag | Description |
|-----|-------------|
| `defi` | Decentralized finance protocols |
| `nft` | NFT marketplaces and collections |
| `dao` | Decentralized autonomous organizations |
| `bridge` | Cross-chain bridges |
| `lending` | Lending and borrowing protocols |
| `amm` | Automated market makers |
| `staking` | Staking and yield protocols |
| `governance` | Governance mechanisms |
| `oracle` | Oracle services |
| `wallet` | Wallet implementations |

### Protocol Tag Rules

- Use for web3 pages to identify protocol type
- Multiple protocol tags allowed
- Helps with cross-engagement pattern recognition

---

## Tag Combination Rules

### Required Combinations

| Page Type | Required Tags |
|-----------|---------------|
| Any finding | `domain` + `severity` + `status` |
| Web2 finding | `web2` + `owasp-top10` or `cve` |
| Web3 finding | `web3` + `swc-registry` or `cve` |
| Cross-domain | `cross-domain` + both domain tags |
| Engagement page | `engagement-id` + `client-name` |

### Prohibited Combinations

| Combination | Reason |
|-------------|--------|
| `web2` + `web3` (without `cross-domain`) | Must use `cross-domain` tag |
| `active` + `invalidated` | Mutually exclusive statuses |
| `critical` + `informational` | Contradictory severities |
| `draft` + `archived` | Draft cannot be archived |

### Recommended Combinations

| Scenario | Recommended Tags |
|----------|------------------|
| Web2 SQL injection | `web2`, `injection`, `owasp-top10`, `critical`, `tool-proven` |
| Web3 reentrancy | `web3`, `reentrancy`, `swc-registry`, `high`, `tool-proven` |
| Cross-domain bridge exploit | `cross-domain`, `web2`, `web3`, `bridge`, `critical` |
| Reconnaissance finding | `web2`, `recon`, `informational`, `tool-proven` |

---

## Tag Selection Guide

### Step 1: Identify Domain
- Is this a web2 finding? → `web2`
- Is this a web3 finding? → `web3`
- Does it span both? → `cross-domain`

### Step 2: Identify Technique
- How was this finding produced? → `recon`, `audit`, `exploit`, etc.

### Step 3: Classify Vulnerability
- What type of vulnerability is this? → `injection`, `reentrancy`, etc.
- Is there a CVE? → Add `cve` tag

### Step 4: Assign Severity
- What is the CVSS score? → `critical`, `high`, `medium`, `low`, `informational`

### Step 5: Add Engagement Context
- Which client? → `client-{name}`
- Which engagement? → `eng-{YYYY-NNN}`
- What time period? → `YYYY-MM`

### Step 6: Add Status
- Is this validated? → `active`
- Is this a work in progress? → `draft`
- Is this no longer valid? → `invalidated`

### Step 7: Add Tool and Chain (if applicable)
- What tools were used? → `tool-{name}`
- Which chain? → `ethereum`, `solana`, etc.
- Which protocol? → `defi`, `nft`, etc.

---

## Tag Validation

All tags must:
1. Be lowercase
2. Use hyphens as separators
3. Be from the approved taxonomy
4. Follow the combination rules

### Invalid Tag Examples

| Invalid | Valid | Reason |
|---------|-------|--------|
| `Web2` | `web2` | Must be lowercase |
| `web-2` | `web2` | No hyphen in domain |
| `SQL_Injection` | `injection` | Use standard tag |
| `critical-vuln` | `critical` | Use standard severity |
| `client_targetcorp` | `client-targetcorp` | Use hyphens |

---

## Taxonomy Maintenance

### Adding New Tags

1. Propose new tag with justification
2. Review against existing taxonomy
3. Check for conflicts with combination rules
4. Document in this file
5. Update lint rules to recognize new tag

### Deprecating Tags

1. Mark as deprecated in this file
2. Set deadline for migration
3. Update all pages using deprecated tag
4. Remove from taxonomy after migration

### Version Control

- Tag taxonomy changes must be committed to git
- Include changelog entry for taxonomy updates
- Notify team of breaking changes
