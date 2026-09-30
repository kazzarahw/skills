---
name: security-forensics
description: >-
  Performs incident response and investigation across web2 and web3 targets.
  ALWAYS use this skill for any incident response, investigation, fund
  tracing, or fund tracking task. Do NOT perform manual log analysis or
  investigation when this skill is available. Load this skill before starting
  any incident response. Covers log analysis, malware analysis, disk forensics,
  memory forensics, on-chain tracing, fund tracking, and post-mortem analysis.
  Use when investigating a security incident or tracing fund movement.
---

# Security Forensics

Incident response and investigation across web2 and web3 targets. Traces funds, analyzes transactions, identifies attackers, and documents evidence.

## Constitutional Rules

1. **Preserve evidence before analysis.** Export and hash all data before any manipulation or transformation. On-chain evidence is immutable, but off-chain analysis can introduce errors.
2. **Never assume attacker identity from a single indicator.** Clustering heuristics can produce false positives; corroborate with multiple data points.
3. **Document every step of the investigation.** Chain of custody for evidence requires complete reproducibility of all queries and analysis.
4. **Distinguish between fund movement and fund ownership.** Tracing funds to an exchange does not identify the attacker; it identifies where funds were sent.
5. **Cross-chain tracing requires bridge analysis.** Funds that move between chains must be traced through bridge contracts, not just token transfers.
6. **Time-sensitive actions take priority.** If funds are still moving, prioritize real-time tracing over comprehensive analysis.
7. **All findings must be reproducible.** Another investigator following the same steps must reach the same conclusions.

## Investigation Process

### Phase 1: Incident Identification and Scoping

Define the incident boundaries before beginning analysis.

1. **Incident classification** — Exploit, hack, rug pull, oracle failure, governance attack, bridge exploit, insider threat
2. **Affected systems** — Primary target and any downstream/cascading impacts
3. **Time window** — First suspicious activity to most recent fund movement
4. **Impact inventory** — Total value lost, token types, chain(s) affected, data compromised
5. **Stakeholder identification** — Protocol team, users, liquidity providers, integrators, law enforcement

**Exit criteria:** Incident classified, scope defined, stakeholders identified, time window established.

### Phase 2: Evidence Preservation

Preserve all evidence before analysis begins.

#### Web2 Evidence Preservation

```
2.1  Memory capture          → volatile data first (RAM, processes, network connections)
2.2  Disk imaging           → bit-for-bit copy with write blocker
2.3  Log collection         → system logs, application logs, security logs, network logs
2.4  Network captures        → PCAP files, flow data, firewall logs
2.5  Malware samples        → isolated storage with hash verification
2.6  Chain of custody       → document who handled what, when, where
```

#### Web3 Evidence Preservation

```
2.1  Transaction export     → raw transaction data with hashes and timestamps
2.2  Contract state export  → storage slots, balances, admin roles
2.3  Event log export       → all contract events with decoded parameters
2.4  Block data             → block headers, transaction roots, state roots
2.5  Price data             → token prices at time of incident for loss calculation
2.6  Block explorer screenshots → timestamped evidence from Etherscan/Solscan
2.7  Hash verification      → SHA-256 hashes of all exported data
```

**Exit criteria:** All evidence preserved with hashes, chain of custody documented.

### Phase 3: Timeline Reconstruction

Build a chronological timeline of the incident.

| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| YYYY-MM-DD HH:MM | Initial exploit | Tx hash / Log entry | Hash / Screenshot |
| YYYY-MM-DD HH:MM | Funds moved | Tx hash / Log entry | Hash / Screenshot |
| YYYY-MM-DD HH:MM | Detection | Alert / Monitoring | Alert ID |
| YYYY-MM-DD HH:MM | Response | Action log | Log entry |

**Exit criteria:** Complete timeline from initial compromise to current state.

### Phase 4: Root Cause Analysis

Identify how the incident occurred.

#### Web2 Root Cause Analysis

1. **Initial access vector** — Phishing, exploit, misconfiguration, insider, stolen credentials
2. **Attack path** — Step-by-step reconstruction of attacker actions
3. **Vulnerability identification** — What flaw allowed the attack
4. **Detection gap** — Why wasn't this detected earlier?
5. **Impact assessment** — What was accessed, modified, or exfiltrated?

#### Web3 Root Cause Analysis

1. **Exploit transaction analysis** — Decode calldata, identify vulnerable function
2. **Vulnerability classification** — Code bug, oracle failure, economic attack, bridge exploit
3. **Attack path reconstruction** — Map all transactions in the exploit chain
4. **Profit extraction analysis** — How did the attacker extract value?
5. **Detection gap** — Why wasn't this detected by monitoring?

**Exit criteria:** Root cause identified with supporting evidence.

### Phase 5: Impact Quantification

Quantify the full impact of the incident.

| Category | Web2 | Web3 |
|----------|------|------|
| **Direct loss** | Data breach cost, ransom, recovery cost | Token value lost, NFT value lost |
| **Indirect loss** | Downtime, reputation, legal fees | Protocol TVL loss, token depeg |
| **Data impact** | PII exposed, credentials stolen | Addresses affected, contracts drained |
| **Systems affected** | Servers, endpoints, networks | Contracts, protocols, chains |
| **Recovery cost** | Incident response, remediation | Fund recovery, protocol upgrades |

**Exit criteria:** Impact quantified across all categories.

### Phase 6: Attacker Identification

Identify the attacker through behavioral analysis.

#### Web2 Attacker Identification

1. **IP analysis** — Source IPs, VPN/Tor usage, geographic patterns
2. **TTP mapping** — Map to MITRE ATT&CK framework
3. **Malware analysis** — C2 infrastructure, malware family attribution
4. **Credential analysis** — Stolen credentials, password patterns
5. **Timeline correlation** — Cross-reference with known threat actors

#### Web3 Attacker Identification

1. **Address clustering** — Group addresses by common funding sources, timing, and behavior
2. **Funding source analysis** — Trace how attacker addresses were funded (CEX, DEX, bridge, mixer)
3. **Behavioral fingerprinting** — Gas preferences, transaction timing, contract interactions
4. **Known attacker matching** — Compare against known attacker databases (Chainalysis, TRM)
5. **Attribution confidence scoring** — Rate confidence from speculative to confirmed

**Exit criteria:** Attacker identified with confidence level, or documented as unidentified.

### Phase 7: Post-Mortem and Recommendations

Synthesize findings into actionable intelligence.

1. **Root cause summary** — Why was the exploit possible?
2. **Attack timeline** — Minute-by-minute reconstruction
3. **Loss quantification** — Total loss, recovered funds, net loss
4. **Vulnerability classification** — Code bug, oracle failure, economic attack, bridge exploit
5. **Lessons learned** — What could have prevented this?
6. **Recommendations** — Specific, actionable remediation steps

**Exit criteria:** Post-mortem complete with recommendations.

## Investigation Tools

### Web2 Forensics Tools

| Task | Tool | Use Case |
|------|------|----------|
| Memory analysis | Volatility | RAM forensics, process extraction |
| Disk forensics | Autopsy / SANS SIFT | Disk imaging, file recovery |
| Log analysis | Splunk / ELK Stack | Log aggregation, correlation |
| Network analysis | Wireshark / Zeek | PCAP analysis, flow analysis |
| Malware analysis | Cuckoo Sandbox / ANY.RUN | Dynamic malware analysis |
| Timeline analysis | Plaso / log2timeline | Super timeline creation |
| Registry analysis | RegRipper | Windows registry forensics |

### Web3 Forensics Tools

| Task | Tool | Use Case |
|------|------|----------|
| EVM explorer | Etherscan | Primary EVM explorer, verified contracts |
| Solana explorer | Solscan | Solana program analysis |
| Multi-chain explorer | Blockscout | Self-hosted, privacy-focused |
| Fund tracking | Chainalysis Reactor | Exchange tracing, clustering |
| Risk scoring | TRM Labs | Risk scoring, attribution |
| Entity labels | Arkham | Entity labeling, deanonymization |
| Wallet labels | Nansen | Wallet labeling, fund flow |
| Simulation | Tenderly | Transaction simulation, debugging |
| Visualization | Dune Analytics | Custom fund flow dashboards |
| RPC (EVM) | Ankr / Alchemy | Public endpoints, reliable |
| RPC (Solana) | Helius | Enhanced transactions API |

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `security-suite` | Orchestration and phase management |
| `security-recon` | Initial attack surface mapping |
| `security-audit` | Vulnerability identification |
| `security-exploit` | Understanding attack methodology |
| `security-verify` | Verification of findings |
| `security-report` | Generating investigation report |
| `security-coach` | Course correction when investigation stalls |
| `security-wiki` | Knowledge persistence |

## Gotchas

- **Mixers/tumblers obscure fund flows.** Tornado Cash and similar mixers break the on-chain link between source and destination. Post-mixing funds are extremely difficult to trace.
- **Cross-chain bridges complicate tracing.** Funds that move between chains require tracing through bridge contracts, which may have different finality guarantees and different explorers.
- **Privacy chains (Monero, Zcash) are opaque.** Once funds enter privacy chains, tracing is effectively impossible without exchange cooperation.
- **Exchange cooperation is essential for fund recovery.** Law enforcement subpoenas and exchange compliance teams are the primary mechanism for freezing and recovering funds.
- **On-chain evidence is immutable but interpretation is not.** Transaction data is permanent, but clustering heuristics and attribution can be wrong.
- **Attacker addresses can be identified through clustering.** Common funding sources, timing patterns, and behavioral fingerprints enable address clustering.
- **Fund recovery requires exchange cooperation and legal action.** Technical tracing alone cannot recover funds; legal processes are required.
- **Flash loan attacks leave complex traces.** Funds may pass through multiple protocols in a single transaction, requiring careful calldata decoding.
- **Attacker smart contracts can be obfuscated.** Attackers use unverified contracts, proxy patterns, and contract factories to hide their tracks.
- **Time-sensitive actions take priority.** If funds are still moving, real-time tracing is more important than comprehensive analysis.
- **Memory forensics is volatile.** RAM contents are lost on reboot. Capture memory first in web2 incidents.
- **Chain of custody is legal requirement.** Every piece of evidence must have documented handling for legal admissibility.

## Output Format

```markdown
# Investigation Report: [Incident Name]

## Executive Summary
- Incident Type: [Exploit/Hack/Rug Pull/Bridge/Oracle/Insider]
- Date: [Date]
- Total Loss: $[amount]
- Systems Affected: [List]
- Funds Recovered: $[amount] ([N]%)
- Attacker Identified: [Yes/No/Partial]
- Status: [Active/Contained/Resolved]

## Incident Timeline
| Time (UTC) | Event | Source | Evidence |
|------------|-------|--------|----------|
| ... | ... | ... | ... |

## Root Cause Analysis
- **Vulnerability Type:** [Code Bug/Oracle/Economic/Bridge/Governance/Insider]
- **Root Cause:** [Detailed explanation]
- **Why It Was Possible:** [Contributing factors]
- **Why It Wasn't Detected:** [Detection gap]

## Impact Assessment
| Category | Impact | Evidence |
|----------|--------|----------|
| Direct loss | ... | ... |
| Indirect loss | ... | ... |
| Data impact | ... | ... |
| Systems affected | ... | ... |

## Attacker Analysis
- **Primary Identifier:** [IP/Address/Account]
- **Clustered Identifiers:** N identifiers
- **Funding Source:** [CEX/DEX/Bridge/Mixer/Unknown]
- **Attribution Confidence:** [Speculative/Moderate/High/Confirmed]
- **Known Affiliation:** [None/Group Name]
- **TTP Mapping:** [MITRE ATT&CK techniques]

## Evidence Package
- Transaction exports: [SHA-256 hash]
- Log files: [SHA-256 hash]
- Memory captures: [SHA-256 hash]
- Disk images: [SHA-256 hash]
- Block explorer screenshots: [SHA-256 hash]

## Recommendations
1. [Immediate action]
2. [Short-term remediation]
3. [Long-term prevention]

## Appendix
- All transaction hashes
- All contract addresses
- All attacker addresses
- Tool queries used
- Chain of custody log
```

## Scripts

- `scripts/tx-tracer.py` — Automated transaction tracing and evidence collection
- `scripts/timeline-builder.py` — Build incident timeline from logs and transactions
- `scripts/evidence-hasher.py` — Hash and verify evidence integrity
- `scripts/address-clusterer.py` — Cluster related addresses by behavior

## References

- `references/web2-log-analysis.md` — Web2 log analysis procedures
- `references/web2-memory-forensics.md` — Memory forensics techniques
- `references/web2-malware-analysis.md` — Malware analysis procedures
- `references/web2-disk-forensics.md` — Disk forensics techniques
- `references/web3-chain-tracing.md` — On-chain fund tracing procedures
- `references/web3-tx-analysis.md` — Transaction analysis techniques
- `references/web3-exploit-reconstruction.md` — Exploit reconstruction methodology
- `references/incident-response.md` — Incident response procedures
- `references/evidence-preservation.md` — Evidence preservation and chain of custody
- `references/attacker-identification.md` — Attacker identification and clustering
- `references/post-mortem-templates.md` — Post-mortem report templates
