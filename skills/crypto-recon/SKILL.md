---
name: crypto-recon
description: Performs blockchain reconnaissance and address analysis. Use when investigating addresses, tracing transactions, identifying contracts, or analyzing on-chain activity. Covers EVM chains, Solana, Bitcoin, and cross-chain analysis.
---

# Crypto Recon

Blockchain reconnaissance and address analysis skill for authorized investigations.

## Constitutional Rules

1. **Authorization required** — Verify written scope before any active query. Refuse out-of-scope targets immediately.
2. **Evidence over assertion** — Every finding traces to captured tool output or on-chain data. No finding without a transaction hash or log reference.
3. **Read-only by default** — Use public explorers and RPC read calls. No transactions, no contract state changes, no signing.
4. **Structured output** — All results use the report template. No prose-only findings.
5. **Deterministic defaults** — Use the specified tool and parameters unless scope constraints require deviation. Log all deviations.
6. **Privacy preservation** — Do not link addresses to real-world identities without explicit authorization. Flag potential identity links as "unverified."
7. **Cross-chain awareness** — Address formats overlap across chains. Always confirm chain context before drawing conclusions.

## Reconnaissance Process

### Phase 1: Address Identification and Classification

Determine what you are looking at before analyzing it.

```
1.1  Address format validation  → chain identification
1.2  EOA vs contract detection  → bytecode check
1.3  Label lookup               → exchange, mixer, protocol tags
1.4  Initial risk scoring       → heuristic-based triage
```

**Exit criteria:** Address classified (EOA/contract/unknown), chain identified, initial risk score assigned.

### Phase 2: Transaction History Analysis

Map the address's on-chain activity.

```
2.1  Transaction enumeration   → inbound, outbound, internal
2.2  Temporal analysis         → first/last seen, activity bursts
2.3  Value flow analysis       → volume, frequency, counterparties
2.4  Failed transaction check  → out-of-gas, reverts, approvals
```

**Exit criteria:** Transaction graph summarized, activity patterns identified, counterparty list compiled.

### Phase 3: Contract Interaction Mapping

For contract addresses, map the protocol surface.

```
3.1  Contract source verification  → Etherscan/Solscan verification status
3.2  Function call frequency       → identify primary use case
3.3  Dependency mapping            → tokens, oracles, other contracts
3.4  Admin/privilege detection      → owner, proxy admin, pause roles
```

**Exit criteria:** Contract purpose identified, dependencies mapped, privileged roles documented.

### Phase 4: Fund Flow Tracing

Follow the money through the transaction graph.

```
4.1  Source identification       → originating addresses, funding sources
4.2  Sink identification          → destination addresses, cash-out points
4.3  Hop analysis                 → intermediary addresses, layering detection
4.4  Exchange off-ramp detection   → CEX deposit addresses, fiat off-ramps
```

**Exit criteria:** Fund flow graph constructed, source/sink identified, layering patterns documented.

### Phase 5: Cross-Chain Activity Analysis

Track assets and activity across chains.

```
5.1  Bridge interaction detection  → lock/mint, burn/release patterns
5.2  Multi-chain address matching  → same key, different chain
5.3  Cross-chain message tracking  → LayerZero, Wormhole, IBC
5.4  Chain-hop analysis            → rapid movement across chains
```

**Exit criteria:** Cross-chain activity mapped, bridge interactions documented, multi-chain profile compiled.

### Phase 6: Entity Identification and Cluster Analysis

Group related addresses into entity clusters.

```
6.1  Common-input clustering     → co-spending addresses (Bitcoin)
6.2  Behavioral clustering        → similar transaction patterns
6.3  Label propagation           → known entity associations
6.4  Entity attribution           → exchange, protocol, individual
```

**Exit criteria:** Address clusters identified, entity attribution proposed (with confidence level).

## Chain-Specific Analysis

### EVM Chains (Ethereum, Arbitrum, Optimism, Base, Polygon, BSC, Avalanche, Fantom)

| Aspect | Approach |
|--------|----------|
| Address type | Bytecode length > 0 → contract |
| Token detection | ERC-20/721/1155 balance checks |
| Proxy detection | EIP-1967 storage slots |
| Label source | Etherscan tags, Nansen labels |
| RPC | `eth_getCode`, `eth_getBalance`, `eth_getLogs` |

### Solana

| Aspect | Approach |
|--------|----------|
| Account type | Program account vs PDA vs wallet |
| Program ID | Verify against known program registry |
| PDA derivation | Seeds + program ID reconstruction |
| Label source | Solscan tags, Step Finance |
| RPC | `getAccountInfo`, `getSignaturesForAddress` |

### Bitcoin

| Aspect | Approach |
|--------|----------|
| Address type | P2PKH, P2SH, P2WPKH, P2TR (bech32) |
| UTXO analysis | Input/output clustering |
| Entity clustering | Common-input heuristic |
| Label source | WalletExplorer, OXT |
| Lightning | Channel open/close detection |

### Cosmos Ecosystem

| Aspect | Approach |
|--------|----------|
| Address format | Bech32 prefix (cosmos, osmo, etc.) |
| IBC tracking | Packet send/recv/acknowledge |
| Module interaction | Staking, governance, dex modules |
| Label source | Mintscan, Ping.pub |

## Tool Selection Defaults

| Task | Default Tool | Command/URL Pattern | Why |
|------|-------------|---------------------|-----|
| EVM explorer | Etherscan | `etherscan.io/address/<addr>` | Most comprehensive labels |
| Solana explorer | Solscan | `solscan.io/account/<addr>` | Best program tagging |
| Multi-chain explorer | Blockscout | `blockscout.com` | Open-source, self-hostable |
| EVM decompilation | Heimdall (decompiler) | `github.com/JoranHonig/Heimdall` | Fast EVM bytecode decompilation |
| Alternative decomp | Panoramix | `github.com/palkeo/panoramix` | Python-based, good for proxies |
| Entity labels | Nansen | `nansen.ai` | Best-in-class wallet labeling |
| Risk scoring | TRM Labs | `trmlabs.com` | Compliance-grade risk engine |
| Exchange labels | Chainalysis | `chainalysis.com` | Industry standard for attribution |
| Monitoring | Forta | `forta.org` | Real-time threat detection |
| Simulation | Tenderly | `tenderly.co` | Transaction simulation and tracing |
| RPC (EVM) | Ankr / Alchemy | Public endpoints | Free tier, reliable |
| RPC (Solana) | Helius | `helius.xyz` | Enhanced transactions API |
| RPC (Solana) | Triton | `triton.one` | Enhanced Solana RPC |
| RPC (Bitcoin) | mempool.space | `mempool.space/api` | No API key required |

**Deviation rule:** If a default tool is unavailable or rate-limited, substitute the next tool in the chain and log the substitution.

## Cross-References

| Skill | When to Use |
|-------|-------------|
| **cyber-recon** | Traditional recon methodology (OSINT, scanning, enumeration) |
| **cyber-wiki** | Knowledge management and report storage |
| **cyber-verify** | Verification discipline and false-positive filtering |
| **cyber-coach** | Course correction when recon stalls |
| **crypto-forensics** | Deep-dive forensic analysis and evidence handling |
| **crypto-exploit** | Vulnerability analysis and exploit development |
| **crypto-audit** | Smart contract security auditing |
| **crypto-defi** | DeFi protocol analysis and risk assessment |

**Workflow:** `crypto-recon` → `crypto-audit` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

### Address Reuse Across Chains
The same private key generates different addresses on different chains (except EVM-compatible chains where the address is identical). Always verify chain context before assuming address equivalence.

### Proxy Contract Identification
Proxy contracts delegate logic to an implementation contract. The proxy address is what users interact with, but the logic lives elsewhere. Check EIP-1967 storage slots (`0x360894...1003` for implementation, `0xb53127...bc79` for admin) before analyzing contract behavior.

### Mixer/Tumbler Detection
Mixer detection requires behavioral analysis, not just label lookup. Key indicators: equal-value outputs, time-delayed withdrawals, multiple unrelated depositors, no on-chain link between deposit and withdrawal. Known mixers: Tornado Cash, Samourai Wallet, ChipMixer.

### Exchange Hot Wallet Identification
Exchange wallets have high transaction volume, many counterparties, and frequent small deposits. Cross-reference with known exchange wallet lists (Nansen, Chainalysis). Do not assume an address belongs to an exchange without label verification.

### Smart Contract vs EOA Distinction
EOAs have no bytecode and can sign transactions directly. Contracts have bytecode and execute logic when called. Some contracts (Gnosis Safe, Argent) are wallet-like but are contracts. Check bytecode length before classification.

### Cross-Chain Bridge Tracking
Bridges lock assets on one chain and mint equivalents on another. Track the full lifecycle: lock → mint → transfer → burn → release. Bridge contracts are high-value targets and often hold large asset reserves.

### Token Approval Risks
Unlimited token approvals (`approve(type(uint256).max)`) are common but create risk. Check approval allowances when analyzing contract interactions. Revoked approvals may indicate security awareness or post-incident response.

### Reorg and Finality Considerations
EVM chains can experience reorgs. Bitcoin has probabilistic finality. Solana has optimistic confirmation. Always wait for sufficient finality before treating transactions as confirmed. Document the finality threshold used.

## Output Format

```markdown
# Blockchain Reconnaissance Report: [Address]

**Date:** YYYY-MM-DD
**Chain:** [chain name]
**Address:** [address]
**Scope:** [investigation scope]
**Tools:** [tool + versions]

## Executive Summary
- Address type: [EOA/contract/unknown]
- Primary activity: [description]
- Risk score: [0-100]
- Entity attribution: [label + confidence]
- Cross-chain activity: [yes/no + chains]

## Address Profile
| Field | Value |
|-------|-------|
| Address | ... |
| Chain | ... |
| Type | ... |
| First seen | ... |
| Last activity | ... |
| Total transactions | ... |
| Total volume | ... |

## Transaction Analysis
- Inbound: N transactions, X ETH
- Outbound: N transactions, X ETH
- Counterparties: N unique addresses
- Activity pattern: [description]

## Contract Interactions (if applicable)
| Contract | Label | Interaction Count | Primary Functions |
|----------|-------|-------------------|-------------------|
| ... | ... | ... | ... |

## Fund Flow
- Source: [addresses]
- Sink: [addresses]
- Hops: [intermediary addresses]
- Exchange off-ramp: [yes/no + exchange]

## Cross-Chain Activity
| Chain | Address | Activity | Bridge Used |
|-------|---------|----------|-------------|
| ... | ... | ... | ... |

## Risk Assessment
| Factor | Score | Evidence |
|--------|-------|----------|
| Mixer association | ... | ... |
| Sanctions exposure | ... | ... |
| Exploit involvement | ... | ... |
| Phishing association | ... | ... |
| Overall risk | ... | ... |

## Entity Clusters
- Cluster 1: [addresses] — [relationship]
- Cluster 2: [addresses] — [relationship]

## Methodology
- Commands/queries executed (full list)
- Tools and versions
- RPC endpoints used
- Time window analyzed

## Appendix
- Raw transaction data
- Label sources
- Scope decision log
```

## Scripts

- `scripts/address-analyzer.py` — Automated address classification, transaction summary, and risk scoring

## Reference Files

- **Chain analysis:** `references/chain-analysis.md`
- **Address profiles:** `references/address-profiles.md`
