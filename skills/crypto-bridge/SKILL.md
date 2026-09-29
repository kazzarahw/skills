---
name: crypto-bridge
description: Analyzes cross-chain bridge security. Use when auditing bridge contracts, assessing validator sets, or evaluating cross-chain message verification. Covers lock-and-mint, burn-and-mint, and liquidity pool bridge architectures.
---

# Crypto Bridge

Cross-chain bridge security analysis skill. Audits bridge contracts, assesses validator sets, evaluates message verification, and identifies attack vectors across bridge architectures.

## Constitutional Rules

1. **Bridge exploits are the largest in crypto.** Ronin ($625M), Wormhole ($326M), Nomad ($190M), Harmony ($100M). Apply maximum scrutiny to all bridge components.
2. **Validator set security is paramount.** A bridge is only as secure as its validator set. Assess decentralization, key management, and collusion resistance before any other component.
3. **Message verification must be end-to-end.** Verify the complete message flow from source chain to destination chain. A vulnerability at any point compromises the entire bridge.
4. **Liquidity solvency is a security requirement.** Insolvent bridges cannot honor withdrawals. Always verify that locked assets exceed minted assets.
5. **Upgrade mechanisms are attack surfaces.** Proxy patterns, admin keys, and upgrade delays must be assessed. A compromised upgrade can drain any bridge.
6. **Trust assumptions must be explicit.** Every bridge makes trust assumptions (validators, oracles, relayers). Document all assumptions and assess their failure modes.
7. **Cross-chain composability amplifies risk.** Bridge vulnerabilities can cascade across chains. Assess cross-chain contagion risk.

## Bridge Analysis Process

### Phase 1: Architecture Review

Map the bridge architecture before any security analysis.

1. **Architecture classification** — Identify bridge type (lock-and-mint, burn-and-mint, liquidity pool, light client, optimistic)
2. **Contract inventory** — Identify all contracts on source and destination chains
3. **Message flow mapping** — Trace how messages travel from source to destination
4. **Asset flow analysis** — Trace how assets are locked, minted, burned, and released
5. **Trust boundary identification** — Map all trust assumptions (validators, oracles, relayers, admins)

**Exit criteria:** Complete architecture map with message and asset flows documented.

### Phase 2: Validator Set Analysis

Assess the security of the validator set that secures the bridge.

1. **Validator count and distribution** — Number of validators, geographic distribution, client diversity
2. **Collusion threshold** — Minimum validators required to compromise the bridge (m-of-n)
3. **Key management** — How validator keys are generated, stored, and rotated
4. **Slashing conditions** — Economic incentives against malicious validation
5. **Validator set updates** — How validators are added/removed, who controls changes

**Exit criteria:** Validator set security assessment with collusion resistance quantified.

### Phase 3: Message Verification Audit

Audit the message verification mechanism end-to-end.

1. **Signature scheme assessment** — ECDSA, BLS, Schnorr, MPC; threshold requirements
2. **Message replay protection** — Nonce, chain ID, contract address binding
3. **Message integrity** — Hash commitments, merkle proofs, data availability
4. **Verification contract audit** — Source and destination chain verification logic
5. **Upgrade and pause mechanisms** — Emergency controls and their security

**Exit criteria:** Message verification audit with all vulnerabilities documented.

### Phase 4: Liquidity Analysis

Verify bridge solvency and assess liquidity risks.

1. **Asset backing verification** — Locked assets on source chain vs. minted assets on destination
2. **Liquidity pool depth** — Sufficient liquidity for expected withdrawal volume
3. **Impermanent loss assessment** — For liquidity pool bridges, assess IL risk
4. **Withdrawal queue analysis** — Can the bridge honor all withdrawal requests?
5. **Cross-chain liquidity fragmentation** — Assess liquidity isolation risks

**Exit criteria:** Solvency verified with liquidity depth and withdrawal capacity assessed.

### Phase 5: Upgrade and Admin Security

Assess upgrade mechanisms and admin key security.

1. **Proxy pattern review** — Storage layout compatibility, implementation contract security
2. **Admin key management** — Multisig, timelock, DAO control
3. **Upgrade delay assessment** — Time between proposal and execution
4. **Emergency pause security** — Who can pause, under what conditions, how to unpause
5. **Implementation contract security** — Uninitialized contracts, storage collisions

**Exit criteria:** Upgrade and admin security assessed with all risks documented.

## Bridge Architecture Patterns

### Lock-and-Mint (Wormhole, Ronin)

**Mechanism:** Assets locked on source chain, equivalent assets minted on destination chain.

**Contracts:**
- Source: Bridge contract locks assets, emits message
- Destination: Bridge contract mints assets upon valid message

**Key risks:**
- Locked asset draining (source chain compromise)
- Unauthorized minting (destination chain compromise)
- Validator set compromise (both chains)

**Focus areas:**
- Lock contract access control
- Mint authorization (only valid messages)
- Validator set security
- Asset backing ratio

### Burn-and-Mint (Multichain, Synapse)

**Mechanism:** Assets burned on source chain, equivalent assets minted on destination chain.

**Contracts:**
- Source: Bridge contract burns assets, emits message
- Destination: Bridge contract mints assets upon valid message

**Key risks:**
- Unauthorized burning (source chain compromise)
- Unauthorized minting (destination chain compromise)
- Replay attacks (burn message reused)

**Focus areas:**
- Burn authorization
- Mint authorization
- Replay protection (nonce, chain ID)
- Message uniqueness

### Liquidity Pool (Stargate, Hop)

**Mechanism:** Liquidity providers deposit assets on both chains. Users deposit on source, receive on destination from pool.

**Contracts:**
- Source: Router contract accepts deposits, coordinates with destination
- Destination: Router contract releases assets from pool
- Pool contracts on both chains

**Key risks:**
- Liquidity pool insolvency
- Pool manipulation (price impact on pool)
- Cross-chain message verification
- LP token accounting errors

**Focus areas:**
- Pool solvency (deposits vs. withdrawals)
- Fee mechanism security
- Message verification
- LP token mint/burn accounting

### Light Client (IBC, Rainbow)

**Mechanism:** Light client on destination chain verifies source chain consensus.

**Contracts:**
- Source: Relayer submits block headers
- Destination: Light client contract verifies headers and processes messages

**Key risks:**
- Light client compromise (fake block headers)
- Consensus attack on source chain
- Relayer censorship
- Light client upgrade security

**Focus areas:**
- Light client verification logic
- Consensus verification (BFT, PoW, PoS)
- Relayer decentralization
- Light client upgrade mechanism

### Optimistic Verification (Nomad)

**Mechanism:** Messages accepted optimistically, challenged during dispute window.

**Contracts:**
- Source: Bridge contract emits message
- Destination: Optimistic bridge accepts message, allows challenge
- Dispute resolution contract

**Key risks:**
- Invalid message accepted during dispute window
- Challenge mechanism failure
- Dispute resolution compromise
- Message delay (must wait for dispute window)

**Focus areas:**
- Dispute window duration
- Challenge bond economics
- Dispute resolution security
- Message finality delay

## Attack Vectors

### Signature Verification Bypass

**Mechanism:** Exploiting flaws in signature verification to forge valid messages.

**Known exploits:**
- Wormhole ($326M): Signature verification bug allowed fake message validation
- Ronin ($625M): Compromised validator keys allowed fake withdrawals

**Detection:**
- Review signature verification logic for edge cases
- Check for missing signature count validation
- Verify signature malleability protection
- Test with invalid signatures

**Prevention:**
- Use battle-tested signature libraries
- Implement strict signature count validation
- Add signature malleability protection
- Use formal verification for critical paths

### Message Replay

**Mechanism:** Reusing a valid message on the same or different chain to mint assets multiple times.

**Known exploits:**
- Multichain ($130M): Replay of messages across chains
- Poly Network ($610M): Cross-chain message replay

**Detection:**
- Check for nonce implementation
- Verify chain ID binding in signed messages
- Test cross-chain replay scenarios
- Review message uniqueness guarantees

**Prevention:**
- Include chain ID and contract address in signed payload
- Implement per-chain nonce tracking
- Use message hash commitments
- Add replay protection at contract level

### Validator Collusion

**Mechanism:** Validators collude to approve fraudulent messages or censor legitimate ones.

**Known exploits:**
- Ronin ($625M): 5-of-9 validators compromised
- Harmony ($100M): 2-of-5 validators compromised

**Detection:**
- Assess validator set size and distribution
- Evaluate collusion threshold (m-of-n)
- Check for validator diversity (geographic, client, entity)
- Review slashing conditions

**Prevention:**
- Increase validator set size
- Require higher collusion threshold (e.g., 2/3 instead of 1/2)
- Implement slashing for malicious validation
- Diversify validator set (geographic, client, entity)
- Use decentralized validator sets (e.g., native staking)

### Improper Initialization

**Mechanism:** Uninitialized implementation contracts or proxy storage left writable by anyone.

**Known exploits:**
- Various proxy exploits: Uninitialized implementation allows takeover

**Detection:**
- Check for initialization functions
- Verify initialization status before use
- Review proxy storage layout
- Test with uninitialized contracts

**Prevention:**
- Use initialize pattern with reentrancy guard
- Verify initialization status in all functions
- Use transparent proxy pattern
- Implement storage layout checks

### Liquidity Pool Manipulation

**Mechanism:** Manipulating liquidity pool prices to extract value from bridge users.

**Known exploits:**
- Various pool exploits: Price manipulation for unfair exchange rates

**Detection:**
- Analyze pool depth and slippage
- Check for price oracle dependencies
- Review fee mechanism
- Test with large transactions

**Prevention:**
- Use TWAP oracles for pricing
- Implement slippage protection
- Add circuit breakers for large price deviations
- Use multiple liquidity sources

## Cross-References

| Skill | When to Use |
|-------|-------------|
| **cyber-recon** | Traditional reconnaissance methodology for infrastructure mapping |
| **cyber-exploit** | Exploitation methodology for bridge attack development |
| **cyber-verify** | Verification discipline for confirming bridge vulnerability exploitability |
| **cyber-coach** | Course correction when analysis stalls |
| **cyber-report** | Reporting format for bridge audit findings |
| **crypto-recon** | Blockchain reconnaissance for bridge contract identification |
| **crypto-audit** | Smart contract audit for bridge contract vulnerabilities |
| **crypto-defi** | DeFi protocol analysis for bridge-specific risks |
| **crypto-exploit** | Exploit development for bridge attack execution |
| **crypto-forensics** | Post-incident investigation of bridge exploits |
| **crypto-mev** | MEV analysis for bridge transaction ordering risks |

**Workflow:** `crypto-recon` → `crypto-bridge` → `crypto-audit` → `crypto-defi` → `crypto-exploit` → `crypto-forensics`

## Gotchas

- **Bridge exploits are the largest in crypto.** Ronin ($625M), Wormhole ($326M), Nomad ($190M), Harmony ($100M), Multichain ($130M). Always apply maximum scrutiny.
- **Validator set compromise is the #1 bridge attack vector.** Most major bridge exploits involved compromised validator keys or collusion. Assess validator set security first.
- **Message replay spans chains.** A message valid on one chain may be replayed on another. Always include chain ID and contract address in signed payloads.
- **Liquidity pool bridges have insolvency risk.** If pooled assets are drained or manipulated, the bridge cannot honor withdrawals. Always verify solvency.
- **Upgrade mechanisms are critical attack surfaces.** A compromised upgrade can drain any bridge regardless of other security measures. Assess upgrade security carefully.
- **Cross-chain composability amplifies risk.** A bridge exploit can cascade across multiple chains and protocols. Assess cross-chain contagion risk.
- **Optimistic verification has a delay trade-off.** Messages are not final until the dispute window passes. This delay can be exploited if the dispute mechanism fails.
- **Light client bridges depend on source chain security.** If the source chain consensus is compromised, the light client accepts fraudulent blocks.
- **Admin keys are a single point of failure.** Compromised admin keys can upgrade or pause any bridge. Assess admin key security and timelock duration.
- **Bridge TVL is a proxy for attack incentive.** Higher TVL attracts more attackers. Assess bridge security proportional to TVL.

## Output Format

```markdown
# Bridge Security Report: [Bridge Name]

## Executive Summary
- Overall Risk Rating: [Critical/High/Medium/Low]
- Architecture: [Lock-and-Mint/Burn-and-Mint/Liquidity Pool/Light Client/Optimistic]
- TVL: $[amount]
- Validator Set: [N validators, M-of-N threshold]
- Findings: [Critical: N, High: N, Medium: N, Low: N]

## Architecture Analysis
- Source Chain Contracts: [list]
- Destination Chain Contracts: [list]
- Message Flow: [description]
- Asset Flow: [description]
- Trust Assumptions: [list]

## Validator Set Security
- Validator Count: N
- Collusion Threshold: M-of-N
- Decentralization: [Low/Medium/High]
- Key Management: [description]
- Slashing Conditions: [Present/Absent]

## Message Verification
- Signature Scheme: [ECDSA/BLS/MPC]
- Replay Protection: [Present/Absent]
- Verification Logic: [Secure/Vulnerable]
- Upgrade Mechanism: [description]

## Liquidity Analysis
- Total Locked: $[amount]
- Total Minted: $[amount]
- Solvency Ratio: [X%]
- Liquidity Depth: [sufficient/insufficient]
- Withdrawal Capacity: [sufficient/insufficient]

## Findings

### [CRITICAL] Finding Title
- **Description:** [What is the vulnerability]
- **Root Cause:** [Why it exists]
- **Exploitability:** [How it can be exploited]
- **Impact:** [Potential loss]
- **Recommendation:** [How to fix]

## Risk Scoring
| Category | Risk Level | Score (1-10) |
|----------|-----------|--------------|
| Validator Set | [level] | [score] |
| Message Verification | [level] | [score] |
| Liquidity | [level] | [score] |
| Upgrade Security | [level] | [score] |
| **Overall** | **[level]** | **[score]** |

## Recommendations
1. [Highest priority recommendation]
2. [Next priority]
3. [Continue...]
```

## Quick Start

1. Run bridge analyzer: `python3 scripts/bridge-analyzer.py --bridge-config config.json`
2. Review `references/bridge-patterns.md` for detailed architecture patterns
3. Follow Bridge Analysis Process (Architecture → Validators → Messages → Liquidity → Upgrade)
4. Write report using Output Format above
