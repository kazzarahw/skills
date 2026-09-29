# Tool Selection Guide

When to use which tool across domains. Decision matrices and combination strategies for web2, web3, and cross-domain engagements.

## Table of Contents

- [Web2 Reconnaissance Tools](#web2-reconnaissance-tools)
  - [nmap vs masscan vs gobuster vs nuclei](#nmap-vs-masscan-vs-gobuster-vs-nuclei)
  - [Decision Matrix: Web2 Recon](#decision-matrix-web2-recon)
  - [Tool Combination Strategy: Web2 Recon](#tool-combination-strategy-web2-recon)
- [Web2 Audit Tools](#web2-audit-tools)
  - [semgrep vs bandit vs npm audit vs snyk](#semgrep-vs-bandit-vs-npm-audit-vs-snyk)
  - [Decision Matrix: Web2 Audit](#decision-matrix-web2-audit)
  - [Tool Combination Strategy: Web2 Audit](#tool-combination-strategy-web2-audit)
- [Web2 Exploitation Tools](#web2-exploitation-tools)
  - [Metasploit vs SQLmap vs Burp Suite vs Manual](#metasploit-vs-sqlmap-vs-burp-suite-vs-manual)
  - [Decision Matrix: Web2 Exploit](#decision-matrix-web2-exploit)
  - [Tool Combination Strategy: Web2 Exploit](#tool-combination-strategy-web2-exploit)
- [Web3 Reconnaissance Tools](#web3-reconnaissance-tools)
  - [Etherscan vs Solscan vs Blockscout vs Nansen](#etherscan-vs-solscan-vs-blockscout-vs-nansen)
  - [Decision Matrix: Web3 Recon](#decision-matrix-web3-recon)
  - [Tool Combination Strategy: Web3 Recon](#tool-combination-strategy-web3-recon)
- [Web3 Audit Tools](#web3-audit-tools)
  - [Slither vs Aderyn vs Mythril vs Echidna](#slither-vs-aderyn-vs-mythril-vs-echidna)
  - [Decision Matrix: Web3 Audit](#decision-matrix-web3-audit)
  - [Tool Combination Strategy: Web3 Audit](#tool-combination-strategy-web3-audit)
- [Web3 Exploitation Tools](#web3-exploitation-tools)
  - [Foundry vs Hardhat vs Tenderly vs Manual](#foundry-vs-hardhat-vs-tenderly-vs-manual)
  - [Decision Matrix: Web3 Exploit](#decision-matrix-web3-exploit)
  - [Tool Combination Strategy: Web3 Exploit](#tool-combination-strategy-web3-exploit)
- [Cross-Domain Tools](#cross-domain-tools)
  - [Tenderly vs Dune vs Chainalysis](#tenderly-vs-dune-vs-chainalysis)
  - [Decision Matrix: Cross-Domain](#decision-matrix-cross-domain)
- [Tool Selection Decision Matrix](#tool-selection-decision-matrix)
  - [By Engagement Phase](#by-engagement-phase)
  - [By Engagement Type](#by-engagement-type)
- [Tool Combination Strategies](#tool-combination-strategies)
  - [Strategy 1: Speed-First (Tight Timeline)](#strategy-1-speed-first-tight-timeline)
  - [Strategy 2: Thoroughness-First (Comprehensive)](#strategy-2-thoroughness-first-comprehensive)
  - [Strategy 3: Web3-Focused](#strategy-3-web3-focused)
  - [Strategy 4: Web2-Focused](#strategy-4-web2-focused)
  - [Strategy 5: Incident Response](#strategy-5-incident-response)
- [Tool Selection Best Practices](#tool-selection-best-practices)

---

## Web2 Reconnaissance Tools

### nmap vs masscan vs gobuster vs nuclei

| Tool | Best For | When to Use | When NOT to Use | Speed | Accuracy |
|------|----------|-------------|-----------------|-------|----------|
| **nmap** | Detailed port scanning, service detection, OS fingerprinting | Default choice for targeted scanning; when you need service versions and OS detection | Very large networks (slow); when stealth is required (noisy) | Medium | High |
| **masscan** | Internet-wide scanning, large network enumeration | Scanning large IP ranges quickly; when speed matters more than detail | When you need service detection or OS fingerprinting | Very Fast | Low-Medium |
| **gobuster** | Directory/file brute-forcing, virtual host discovery | Web application recon; finding hidden endpoints and content | When wordlists are poor; when stealth is required | Medium | Medium |
| **nuclei** | Vulnerability scanning with templates | Post-recon vulnerability identification; known CVE detection | For initial recon (not a recon tool); zero-day discovery | Fast | High |

### Decision Matrix: Web2 Recon

```
START: What are you scanning?
│
├─ Large IP range (>10,000 hosts)?
│  └─ YES → masscan (fast enumeration) → nmap (detailed scan of live hosts)
│
├─ Single host or small network?
│  └─ YES → nmap (comprehensive scan)
│
├─ Web application?
│  ├─ Need hidden directories/files? → gobuster
│  ├─ Need known vulnerabilities? → nuclei
│  └─ Need both? → gobuster → nuclei
│
└─ Need OSINT?
   └─ YES → theHarvester, Shodan, Censys
```

### Tool Combination Strategy: Web2 Recon

```
Phase 1: Enumeration
  masscan (large ranges) or nmap (targeted)
  → Identify live hosts and open ports

Phase 2: Service Detection
  nmap -sV -sC (service version and default scripts)
  → Identify services and versions

Phase 3: Web Content Discovery
  gobuster (directories, files, vhosts)
  → Find hidden web content

Phase 4: Vulnerability Identification
  nuclei (template-based scanning)
  → Identify known vulnerabilities

Phase 5: OSINT
  theHarvester, Shodan, Censys
  → Gather external intelligence
```

---

## Web2 Audit Tools

### semgrep vs bandit vs npm audit vs snyk

| Tool | Best For | When to Use | When NOT to Use | Language Support |
|------|----------|-------------|-----------------|------------------|
| **semgrep** | Lightweight static analysis, custom rules | Quick scans, custom pattern matching, CI/CD integration | Deep taint analysis, complex dataflow | 30+ languages |
| **bandit** | Python-specific security linting | Python code review; finding common Python security issues | Non-Python code | Python only |
| **npm audit** | Node.js dependency vulnerability scanning | Identifying known vulnerabilities in npm packages | Custom code vulnerabilities; non-npm ecosystems | Node.js/npm |
| **snyk** | Comprehensive dependency and container scanning | Enterprise environments; container image scanning; license compliance | Quick one-off scans; budget-constrained projects | Multi-language, multi-ecosystem |

### Decision Matrix: Web2 Audit

```
START: What are you auditing?
│
├─ Python code?
│  └─ YES → bandit (Python-specific) + semgrep (custom rules)
│
├─ Node.js project?
│  ├─ Need dependency audit? → npm audit or snyk
│  └─ Need code audit? → semgrep
│
├─ Multi-language codebase?
│  └─ YES → semgrep (broad language support)
│
├─ Container images?
│  └─ YES → snyk (container scanning)
│
├─ Need custom rules?
│  └─ YES → semgrep (custom rule support)
│
└─ Enterprise/CI-CD integration?
   └─ YES → snyk (enterprise features)
```

### Tool Combination Strategy: Web2 Audit

```
Phase 1: Dependency Audit
  npm audit / snyk (identify vulnerable dependencies)
  → Fix or flag vulnerable packages

Phase 2: Language-Specific Audit
  bandit (Python) / semgrep (other languages)
  → Identify language-specific security issues

Phase 3: Custom Rule Audit
  semgrep with custom rules
  → Identify project-specific security patterns

Phase 4: Container Audit
  snyk / trivy
  → Identify container image vulnerabilities
```

---

## Web2 Exploitation Tools

### Metasploit vs SQLmap vs Burp Suite vs Manual

| Tool | Best For | When to Use | When NOT to Use | Skill Required |
|------|----------|-------------|-----------------|----------------|
| **Metasploit** | Known exploit deployment, post-exploitation | Validating known CVEs; when public exploits exist | Custom attacks; when stealth is required | Medium |
| **SQLmap** | SQL injection detection and exploitation | Confirming SQL injection; extracting database content | Non-SQL injection vulnerabilities | Low-Medium |
| **Burp Suite** | Web application testing, manual exploitation | Web app exploitation; session manipulation; CSRF | Non-web vulnerabilities | Medium-High |
| **Custom/Manual** | Custom attacks, logic vulnerabilities, novel exploits | When no tools exist; logic bugs; business logic attacks | When known exploits exist (use tools first) | High |

### Decision Matrix: Web2 Exploit

```
START: What are you exploiting?
│
├─ Known CVE with public exploit?
│  └─ YES → Metasploit (deploy and validate)
│
├─ SQL injection?
│  └─ YES → SQLmap (automated extraction)
│
├─ Web application vulnerability?
│  └─ YES → Burp Suite (manual testing and exploitation)
│
├─ Business logic vulnerability?
│  └─ YES → Custom/Manual (no automation available)
│
├─ Custom/novel attack?
│  └─ YES → Custom/Manual (write custom exploit)
│
└─ Need post-exploitation?
   └─ YES → Metasploit (post-exploitation modules)
```

### Tool Combination Strategy: Web2 Exploit

```
Phase 1: Known Vulnerability Exploitation
  Metasploit (deploy known exploits)
  → Validate known CVEs

Phase 2: Web Application Exploitation
  Burp Suite (manual testing, session manipulation)
  → Exploit web vulnerabilities

Phase 3: Database Exploitation
  SQLmap (SQL injection)
  → Extract database content

Phase 4: Custom Exploitation
  Custom scripts (logic vulnerabilities, novel attacks)
  → Exploit unique vulnerabilities

Phase 5: Post-Exploitation
  Metasploit (privilege escalation, lateral movement)
  → Demonstrate full impact
```

---

## Web3 Reconnaissance Tools

### Etherscan vs Solscan vs Blockscout vs Nansen

| Tool | Best For | When to Use | When NOT to Use | Chain Support |
|------|----------|-------------|-----------------|---------------|
| **Etherscan** | Ethereum contract verification, transaction analysis | Ethereum mainnet and testnets; contract source verification | Non-EVM chains | Ethereum EVM |
| **Solscan** | Solana program analysis, transaction exploration | Solana ecosystem; program verification | Non-Solana chains | Solana |
| **Blockscout** | Self-hosted chain exploration, custom EVM chains | Custom EVM chains; self-hosted block explorers | Major chains (use native explorers) | EVM-compatible |
| **Nansen** | Wallet labeling, fund flow analysis, DeFi intelligence | Tracking fund flows; identifying smart money; protocol analysis | Basic contract analysis (use explorer) | Multi-chain |

### Decision Matrix: Web3 Recon

```
START: What chain are you analyzing?
│
├─ Ethereum/EVM?
│  ├─ Need contract verification? → Etherscan
│  ├─ Need fund flow analysis? → Nansen
│  └─ Need custom chain? → Blockscout
│
├─ Solana?
│  └─ YES → Solscan
│
├─ Need wallet intelligence?
│  └─ YES → Nansen (wallet labeling, fund flows)
│
└─ Need TVL/protocol data?
   └─ YES → DeFiLlama + Nansen
```

### Tool Combination Strategy: Web3 Recon

```
Phase 1: Chain Identification
  Etherscan / Solscan / Blockscout (identify chain and contracts)
  → Map all in-scope contracts

Phase 2: Contract Verification
  Etherscan (verify source code)
  → Confirm contract source matches deployment

Phase 3: Protocol Discovery
  DeFiLlama (TVL, protocol categories)
  → Understand protocol context

Phase 4: Fund Flow Analysis
  Nansen (wallet labeling, fund flows)
  → Identify key actors and fund sources

Phase 5: Historical Analysis
  Dune Analytics (custom queries)
  → Analyze historical transactions and patterns
```

---

## Web3 Audit Tools

### Slither vs Aderyn vs Mythril vs Echidna

| Tool | Best For | When to Use | When NOT to Use | Language Support |
|------|----------|-------------|-----------------|------------------|
| **Slither** | Static analysis, vulnerability detection, code quality | Comprehensive Solidity static analysis; CI/CD integration | Dynamic analysis; formal verification | Solidity/Vyper |
| **Aderyn** | Rust-based static analysis, Trail of Bits engine | Fast static analysis; when Slither is too slow | Non-Solidity code | Solidity |
| **Mythril** | Symbolic execution, bytecode analysis | Analyzing bytecode; when source unavailable | Quick static analysis (slower than Slither) | EVM bytecode |
| **Echidna** | Property-based fuzzing, invariant testing | Testing invariants; fuzzing custom properties | Static analysis (use Slither) | Solidity |

### Decision Matrix: Web3 Audit

```
START: What are you auditing?
│
├─ Solidity source code available?
│  ├─ Need comprehensive static analysis? → Slither
│  ├─ Need fast static analysis? → Aderyn
│  └─ Need both? → Slither + Aderyn (cross-validation)
│
├─ Only bytecode available?
│  └─ YES → Mythril (symbolic execution on bytecode)
│
├─ Need invariant testing?
│  └─ YES → Echidna (property-based fuzzing)
│
├─ Need formal verification?
│  └─ YES → Manticore / Certora Pro
│
└─ Need economic security analysis?
   └─ YES → Custom modeling + simulation
```

### Tool Combination Strategy: Web3 Audit

```
Phase 1: Static Analysis
  Slither (comprehensive) + Aderyn (fast)
  → Identify known vulnerability patterns

Phase 2: Symbolic Execution
  Mythril (bytecode analysis)
  → Identify deep vulnerabilities

Phase 3: Property-Based Testing
  Echidna (invariant fuzzing)
  → Test custom invariants and properties

Phase 4: Manual Review
  Manual code review
  → Identify logic vulnerabilities, economic attacks

Phase 5: Formal Verification
  Manticore / Certora Pro (if required)
  → Mathematically prove correctness
```

---

## Web3 Exploitation Tools

### Foundry vs Hardhat vs Tenderly vs Manual

| Tool | Best For | When to Use | When NOT to Use | Skill Required |
|------|----------|-------------|-----------------|----------------|
| **Foundry** | Fast testing, fuzzing, gas optimization | Writing and running PoC tests; fuzzing; gas analysis | Complex deployment scripts; frontend testing | Medium |
| **Hardhat** | Full-stack development, deployment, debugging | Complex deployment; debugging; frontend integration | Quick PoC (slower than Foundry) | Medium |
| **Tenderly** | Simulation, debugging, mainnet forking | Simulating transactions; debugging; mainnet forking | Local testing (use Foundry/Hardhat) | Low-Medium |
| **Custom/Manual** | Novel attacks, complex interactions | When frameworks don't support the attack; custom contract interactions | Standard attacks (use frameworks first) | High |

### Decision Matrix: Web3 Exploit

```
START: What are you exploiting?
│
├─ Need to write PoC tests?
│  ├─ Need speed? → Foundry (forge)
│  └─ Need debugging? → Hardhat
│
├─ Need to simulate on mainnet?
│  └─ YES → Tenderly (mainnet forking)
│
├─ Need to debug complex transactions?
│  └─ YES → Tenderly (transaction debugging)
│
├─ Need custom contract interactions?
│  └─ YES → Custom/Manual (write custom scripts)
│
└─ Need to deploy exploit contracts?
   ├─ Simple deployment? → Foundry
   └─ Complex deployment? → Hardhat
```

### Tool Combination Strategy: Web3 Exploit

```
Phase 1: Local Testing
  Foundry (forge test)
  → Write and run PoC tests locally

Phase 2: Testnet Validation
  Foundry / Hardhat (deploy to testnet)
  → Validate exploit on testnet

Phase 3: Mainnet Simulation
  Tenderly (mainnet forking)
  → Simulate exploit on mainnet state

Phase 4: Custom Exploitation
  Custom scripts (novel attacks)
  → Execute custom exploit logic

Phase 5: Evidence Capture
  Tenderly (transaction recording)
  → Capture evidence of successful exploitation
```

---

## Cross-Domain Tools

### Tenderly vs Dune vs Chainalysis

| Tool | Best For | When to Use | When NOT to Use | Domain |
|------|----------|-------------|-----------------|--------|
| **Tenderly** | Transaction simulation, debugging, mainnet forking | Simulating complex transactions; debugging failed transactions; mainnet forking | Basic block exploration (use explorer) | Web3 |
| **Dune Analytics** | On-chain data analysis, custom queries, dashboards | Analyzing on-chain data; creating custom queries; protocol analytics | Real-time monitoring (use Tenderly) | Web3 |
| **Chainalysis** | Fund tracing, compliance, investigation | Tracing fund flows; identifying illicit activity; compliance | Technical contract analysis | Web3 |

### Decision Matrix: Cross-Domain

```
START: What do you need?
│
├─ Simulate transactions?
│  └─ YES → Tenderly
│
├─ Analyze on-chain data?
│  └─ YES → Dune Analytics
│
├─ Trace funds?
│  └─ YES → Chainalysis / TRM Labs
│
├─ Need all three?
│  └─ YES → Tenderly + Dune + Chainalysis
│
└─ Need cross-component analysis?
   └─ YES → Custom scripts + Tenderly + Burp Suite
```

---

## Tool Selection Decision Matrix

### By Engagement Phase

| Phase | Web2 Primary | Web2 Secondary | Web3 Primary | Web3 Secondary |
|-------|-------------|----------------|-------------|----------------|
| Recon | nmap, gobuster | masscan, nuclei | Etherscan, DeFiLlama | Nansen, Dune |
| Audit | semgrep, bandit | snyk, trivy | Slither, Aderyn | Mythril, Echidna |
| Exploit | Metasploit, Burp | SQLmap | Foundry, Hardhat | Tenderly |
| Verify | curl, custom scripts | Burp Repeater | forge test, Anvil | Tenderly |
| Forensics | Volatility, Autopsy | Splunk, Velociraptor | Chainalysis, TRM | Dune, Tenderly |
| Report | custom templates | Dradis | custom templates | CVSS calculator |

### By Engagement Type

| Type | Recon | Audit | Exploit | Verify | Report |
|------|-------|-------|---------|--------|--------|
| Web2 pentest | nmap, gobuster | semgrep, bandit | Metasploit, Burp | curl, Burp | templates |
| Web3 audit | Etherscan, DeFiLlama | Slither, Aderyn | Foundry, Hardhat | forge test | templates |
| Mixed | nmap + Etherscan | semgrep + Slither | Burp + Foundry | curl + forge | templates |
| Incident response | Velociraptor | Splunk | N/A | Chainalysis | templates |
| Advisory | nmap, Shodan | semgrep, trivy | N/A | N/A | templates |

---

## Tool Combination Strategies

### Strategy 1: Speed-First (Tight Timeline)

```
Recon:     masscan → nmap (targeted) → nuclei
Audit:     semgrep → snyk
Exploit:   Metasploit → Burp Suite
Verify:    curl → forge test
Report:    templates
```

**Best for:** Short engagements (1-2 weeks), known vulnerability types

### Strategy 2: Thoroughness-First (Comprehensive)

```
Recon:     nmap → gobuster → nuclei → theHarvester → Shodan
Audit:     semgrep → bandit → snyk → trivy → Slither → Aderyn → Mythril → Echidna
Exploit:   Metasploit → Burp Suite → SQLmap → Foundry → Hardhat → Tenderly
Verify:    curl → Burp Repeater → forge test → Anvil → Tenderly
Report:    templates + CVSS calculator
```

**Best for:** Long engagements (3+ weeks), high-value targets, mixed engagements

### Strategy 3: Web3-Focused

```
Recon:     Etherscan → DeFiLlama → Nansen → Dune
Audit:     Slither → Aderyn → Mythril → Echidna → manual review
Exploit:   Foundry → Hardhat → Tenderly → custom scripts
Verify:    forge test → Anvil → Tenderly simulation
Report:    templates + Immunefi severity guide
```

**Best for:** Smart contract audits, DeFi protocol assessments

### Strategy 4: Web2-Focused

```
Recon:     nmap → gobuster → nuclei → theHarvester
Audit:     semgrep → bandit → snyk → OWASP ZAP
Exploit:   Metasploit → Burp Suite → SQLmap → custom scripts
Verify:    curl → Burp Repeater → custom reproduction
Report:    templates + CVSS calculator
```

**Best for:** Web application pentests, infrastructure assessments

### Strategy 5: Incident Response

```
Triage:    SIEM → Velociraptor → Etherscan
Forensics: Volatility → Autopsy → Splunk → Chainalysis → TRM Labs
Verify:    Cuckoo Sandbox → YARA → Tenderly simulation
Report:    templates + timeline visualization
```

**Best for:** Active incidents, post-breach investigations

---

## Tool Selection Best Practices

1. **Always use multiple tools** — No single tool catches everything. Cross-validate findings.
2. **Start with automated tools** — Use tools first, then manual review for what tools miss.
3. **Document tool versions** — Tool output varies by version. Record versions for reproducibility.
4. **Calibrate for false positives** — Every tool has false positive rates. Tune and filter.
5. **Keep tools updated** — New vulnerabilities and detection rules are added regularly.
6. **Understand tool limitations** — Know what each tool can and cannot detect.
7. **Combine static and dynamic** — Static analysis finds different issues than dynamic testing.
8. **Manual review is essential** — Tools augment but do not replace manual security review.
