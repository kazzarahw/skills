---
name: recon
description: >-
  Maps attack surface: network scanning, OSINT, subdomain enumeration, service fingerprinting, blockchain analysis, address profiling, contract discovery. Use when opening the recon phase or doing a standalone recon task. Full engagement? Start with engagement. Intel gaps needing cited depth go to research.
---

# Security Recon

Reconnaissance and enumeration across web2 and web3 targets. Maps attack surface before active testing.

## Constitutional Rules

1. **Authorization required** — Verify written scope before any active scanning. Refuse out-of-scope targets immediately.
2. **Evidence over assertion** — Every finding traces to captured tool output or on-chain data. No finding without a command log or transaction hash.
3. **Passive before active** — Start with passive techniques that do not touch the target. Escalate to active only when necessary.
4. **Rate limiting by default** — Use rate limiting on all active scans. Aggressive modes require explicit authorization.
5. **Structured output** — All results use the output template. No prose-only findings.
6. **Chain context** — Address formats overlap across chains. Always confirm chain before drawing conclusions.

## Recon Process

### Phase 1: Passive Reconnaissance

Gather intelligence without touching the target.

#### Web2 Passive Recon

```
1.1  Selector intelligence   → people, emails, employees, breach data: load `osint` (it owns verification standards and OPSEC); recon consumes its output
1.2  DNS enumeration         → records, zone transfer attempts, DNSSEC
1.3  Certificate transparency → crt.sh, certspotter
1.4  Exposure search          → dorks for exposed documents and credentials (identity/breach questions go to `osint`)
1.5  Social media recon       → tech stack only (people questions go to `osint`)
1.6  Wayback Machine          → historical endpoints, deleted pages
```

**Exit criteria:** Subdomain list compiled, tech stack identified, employee emails collected, historical endpoints documented.

#### Web3 Passive Recon

```
1.1  Chain identification    → determine target chain(s)
1.2  Address identification   → contract addresses, EOA addresses, token addresses
1.3  Label lookup             → exchange, mixer, protocol tags
1.4  Contract verification    → Etherscan/Solscan verification status
1.5  Protocol discovery      → identify protocol type, version, dependencies
1.6  Historical activity      → first deployment, upgrade history, known incidents
```

**Exit criteria:** Chain(s) identified, addresses classified, contract verification status confirmed, protocol type determined.

### Phase 2: Active Reconnaissance

Direct interaction with in-scope targets.

#### Web2 Active Recon

```
2.1  Host discovery          → masscan (fast sweep)
2.2  Port scanning           → nmap (detailed enumeration)
2.3  Service enumeration      → nmap -sV -sC on open ports
2.4  Web fingerprinting       → whatweb (level 1 default)
2.5  Directory enumeration    → gobuster (medium wordlist)
2.6  Vulnerability scanning   → nuclei (cves/ + exposure/)
```

**Exit criteria:** All open ports identified, services versioned, web tech fingerprinted, directories enumerated.

#### Web3 Active Recon

```
2.1  Contract interaction     → call view functions to map protocol state
2.2  Event log analysis       → query event logs for activity patterns
2.3  Token flow mapping       → trace token movements through protocol
2.4  Oracle dependency check  → identify oracle contracts and update frequency
2.5  Admin role enumeration   → identify owner, admin, pause roles
2.6  Upgrade mechanism scan   → proxy patterns, implementation addresses
```

**Exit criteria:** Protocol state mapped, dependencies identified, admin roles documented, upgrade mechanisms assessed.

### Phase 3: Attack Surface Mapping

Compile findings into an attack surface map.

| Category | Web2 | Web3 |
|----------|------|------|
| **Entry points** | URLs, APIs, services | Contracts, functions, oracles |
| **Trust boundaries** | Auth, sessions, roles | Access control, upgrade keys |
| **Data flows** | User input → processing → storage | User tx → contract → state change |
| **Dependencies** | Libraries, APIs, CDNs | Oracles, tokens, other protocols |
| **Exposure** | Public, internal, authenticated | Public, owner, governance |

**Exit criteria:** Attack surface map complete with all categories populated.

### Phase 4: Risk Indicators

Identify initial risk indicators for prioritization.

| Indicator | Web2 | Web3 |
|-----------|------|------|
| **Outdated software** | Version banners, CVE matching | Old compiler version, deprecated patterns |
| **Misconfigurations** | Default creds, open ports, permissive CORS | Uninitialized proxies, public admin functions |
| **Sensitive data exposure** | Debug endpoints, verbose errors | Unverified contracts, exposed storage |
| **Known vulnerabilities** | CVE databases, exploit-db | Known hack patterns, SWC registry |

**Exit criteria:** Risk indicators documented with severity hints.

## Tool Selection

### Web2 Tools

| Task | Default Tool | Command | Why |
|------|-------------|---------|-----|
| Fast port scan | masscan | `masscan -p1-65535 <target> --rate=10000` | Fastest for large ranges |
| Detailed port scan | nmap | `nmap -sV -sC -p- <target>` | Service detection + scripts |
| Subdomain enum | subfinder | `subfinder -d <domain>` | Passive, fast |
| Directory enum | gobuster | `gobuster dir -u <url> -w <wordlist>` | Reliable, configurable |
| Web fingerprint | whatweb | `whatweb -a 1 <url>` | Quick tech identification |
| Vuln scan | nuclei | `nuclei -u <url> -t cves/` | Template-based, comprehensive |
| OSINT | theHarvester | `theHarvester -d <domain> -b all` | Multi-source OSINT |

### Web3 Tools

| Task | Default Tool | Command/URL | Why |
|------|-------------|-------------|-----|
| EVM explorer | Etherscan | `etherscan.io/address/<addr>` | Most comprehensive labels |
| Solana explorer | Solscan | `solscan.io/account/<addr>` | Best program tagging |
| Multi-chain explorer | Blockscout | `blockscout.com` | Open-source, self-hostable |
| EVM decompilation | Heimdall | `heimdall-rs` | Fast EVM bytecode decompilation |
| Entity labels | Nansen | `nansen.ai` | Best-in-class wallet labeling |
| Risk scoring | TRM Labs | `trmlabs.com` | Compliance-grade risk engine |
| Simulation | Tenderly | `tenderly.co` | Transaction simulation and tracing |
| RPC (EVM) | Ankr/Alchemy | Public endpoints | Free tier, reliable |
| RPC (Solana) | Helius | `helius.xyz` | Enhanced transactions API |

**Deviation rule:** If a default tool is unavailable or rate-limited, substitute the next tool in the chain and log the substitution.

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `engagement` | Orchestration and phase management |
| `audit` | Vulnerability identification from recon findings |
| `exploit` | Target selection for exploitation |
| `verify` | Verification of recon findings |
| `coach` | Course correction when recon stalls |
| `wiki` | Knowledge persistence across engagements |

## Handoffs

Act on these transitions immediately — load the named skill with the skill tool, do not continue by hand:
- Recon complete → load `audit` with the attack surface map.
- Target intel needs cited depth (vendor, protocol) → load `research`.
- People, company, or actor question → load `osint`, not `research`.
- A finding needs confirmation before it leaves recon → load `verify`.
- Stuck, looping, or off-track → load `coach`.
- Phase done → record the map and indicators in `wiki`.

## Mid-Work Checkpoints

Periodically verify:
1. **Am I in the right skill?** If the work drifted into another phase, hand off via `## Handoffs` instead of continuing here.
2. **Am I routing phase ends?** Findings and maps move to other skills — never absorb them.
3. **Evidence attached?** No finding leaves this skill without captured output.

## Gotchas

- **Version banners can be spoofed.** Always confirm with behavioral testing before relying on version-specific exploits.
- **Subdomain takeovers are common.** Check for dangling CNAMES pointing to cloud services (S3, GitHub Pages, Heroku).
- **Web3 contracts can be unverified.** Unverified contracts require bytecode analysis. Do not assume functionality from ABI alone.
- **Proxy contracts hide implementation.** Check EIP-1967 storage slots before analyzing contract behavior.
- **Same address, different chains.** EVM-compatible chains use the same address format. Always confirm chain context.
- **Rate limiting is essential.** Aggressive scanning can trigger WAFs, block IPs, and alert defenders. Use rate limiting by default.
- **Passive recon is not risk-free.** Some passive techniques (DNS queries, certificate transparency) can be detected by sophisticated defenders.
- **Web3 recon is read-only.** Never send transactions during recon. Use view functions and event logs only.

## Output Format

```markdown
# Reconnaissance Report: [Target]

**Date:** YYYY-MM-DD
**Type:** [Web2/Web3/Mixed]
**Scope:** [In-scope targets]
**Tools:** [Tool + versions]

## Executive Summary
- Attack surface: [size and complexity]
- Key findings: [top 3-5 findings]
- Risk indicators: [count by severity]

## Attack Surface Map

### Entry Points
| Type | Target | Exposure | Notes |
|------|--------|----------|-------|
| ... | ... | ... | ... |

### Trust Boundaries
| Boundary | Mechanism | Strength | Notes |
|----------|-----------|----------|-------|
| ... | ... | ... | ... |

### Dependencies
| Dependency | Type | Risk | Notes |
|------------|------|------|-------|
| ... | ... | ... | ... |

## Findings

### [SEVERITY] Finding Title
- **Category:** [Web2/Web3]
- **Target:** [host/address/URL]
- **Description:** [What was found]
- **Evidence:** [Tool output or on-chain data]
- **Risk:** [Potential impact]

## Risk Indicators
| Indicator | Severity | Evidence |
|-----------|----------|----------|
| ... | ... | ... |

## Methodology
- Commands/queries executed (full list)
- Tools and versions
- Time window analyzed
- Scope decision log
```

## Scripts

- `scripts/recon-pipeline.sh` — Automated web2 recon pipeline
- `scripts/address-analyzer.py` — Automated web3 address classification and risk scoring
- `scripts/subdomain-monitor.py` — Monitor for new subdomains

## References

- `references/web2-network-recon.md` — Detailed web2 network scanning procedures
- `references/web2-osint-techniques.md` — OSINT collection techniques
- `references/web3-chain-analysis.md` — On-chain analysis procedures
- `references/web3-contract-discovery.md` — Contract identification and verification
- `references/attack-surface-templates.md` — Attack surface map templates
- `references/tool-cheatsheet.md` — Quick reference for all recon tools
