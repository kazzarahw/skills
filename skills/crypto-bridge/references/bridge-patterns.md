# Bridge Patterns Reference

Detailed bridge architecture patterns with known exploits, detection, and prevention.

## Lock-and-Mint Architecture

### Mechanism

1. User deposits assets into bridge contract on source chain
2. Bridge contract locks assets and emits a message
3. Validators observe and sign the message
4. Relayer submits signed message to destination chain
5. Destination bridge contract verifies signatures and mints equivalent assets
6. User receives minted assets on destination chain

### Contracts

**Source Chain:**
- `Bridge.sol` — Locks assets, emits deposit event
- `Token.sol` — ERC-20 token being bridged

**Destination Chain:**
- `Bridge.sol` — Verifies messages, mints assets
- `BridgeToken.sol` — Wrapped/minted token (e.g., "Ethereum USDC on Polygon")

### Known Exploits

**Ronin Bridge ($625M, March 2022):**
- 5-of-9 validator threshold compromised
- Attacker gained control of 5 validator keys
- Approved fraudulent withdrawal messages
- Root cause: Low validator threshold + compromised keys

**Wormhole ($326M, February 2022):**
- Signature verification bug in `verify_signatures`
- Attacker forged valid signature for fake message
- Minted 120,000 wETH without depositing ETH
- Root cause: Missing signature count validation

### Detection

- **Lock contract access control:** Verify only authorized contracts can lock assets
- **Mint authorization:** Verify only valid validator-signed messages can mint
- **Validator set monitoring:** Track validator set changes and key rotations
- **Asset backing ratio:** Monitor locked assets vs. minted assets
- **Unusual minting patterns:** Alert on large or frequent minting events

### Prevention

- **Increase validator threshold:** Use 2/3 or higher instead of 1/2
- **Diversify validator set:** Geographic, client, and entity diversity
- **Implement slashing:** Economic penalties for malicious validation
- **Use formal verification:** Prove signature verification correctness
- **Add rate limits:** Limit minting volume per time window
- **Implement circuit breakers:** Pause bridge on anomalous activity

## Burn-and-Mint Architecture

### Mechanism

1. User deposits assets into bridge contract on source chain
2. Bridge contract burns assets and emits a message
3. Validators observe and sign the message
4. Relayer submits signed message to destination chain
5. Destination bridge contract verifies signatures and mints equivalent assets
6. User receives minted assets on destination chain

### Contracts

**Source Chain:**
- `Bridge.sol` — Burns assets, emits burn event
- `Token.sol` — ERC-20 token being bridged

**Destination Chain:**
- `Bridge.sol` — Verifies messages, mints assets
- `BridgeToken.sol` — Minted token representing burned asset

### Known Exploits

**Multichain ($130M, July 2023):**
- Validator key compromise allowed fake message approval
- Attacker minted assets on destination without burning on source
- Root cause: Centralized validator set + key compromise

**Synapse (various incidents):**
- Replay attacks due to insufficient nonce tracking
- Cross-chain message reuse
- Root cause: Missing chain ID in signed payload

### Detection

- **Burn authorization:** Verify only authorized contracts can burn assets
- **Message uniqueness:** Track message nonces per chain
- **Cross-chain replay testing:** Test message replay on different chains
- **Validator set monitoring:** Track validator set changes
- **Burn/mint ratio:** Monitor burned assets vs. minted assets

### Prevention

- **Include chain ID in signed payload:** Bind messages to specific chains
- **Implement per-chain nonce tracking:** Prevent replay within and across chains
- **Use message hash commitments:** Track processed message hashes
- **Increase validator decentralization:** More validators, higher threshold
- **Add minting delays:** Time delay between message verification and minting

## Liquidity Pool Architecture

### Mechanism

1. Liquidity providers deposit assets into pool contracts on both chains
2. User deposits assets into pool on source chain
3. Bridge coordinates with destination chain pool
4. User receives assets from pool on destination chain
5. Pool rebalances over time (fees, arbitrage)

### Contracts

**Source Chain:**
- `Router.sol` — Accepts user deposits, coordinates with destination
- `Pool.sol` — Holds liquidity, manages deposits/withdrawals

**Destination Chain:**
- `Router.sol` — Releases assets to users, coordinates with source
- `Pool.sol` — Holds liquidity, manages deposits/withdrawals

### Known Exploits

**Stargate (various incidents):**
- Pool manipulation through large deposits/withdrawals
- Cross-chain message verification failures
- Root cause: Insufficient pool depth + message verification bugs

**Hop Protocol (various incidents):**
- Bonding curve manipulation
- Cross-chain arbitrage exploitation
- Root cause: AMM-based pricing vulnerable to manipulation

### Detection

- **Pool solvency monitoring:** Track deposits vs. withdrawals on both chains
- **Slippage analysis:** Monitor price impact of large transactions
- **Message verification audit:** Verify cross-chain message security
- **LP token accounting:** Verify mint/burn accounting matches deposits/withdrawals
- **Rebalancing monitoring:** Track pool rebalancing frequency and volume

### Prevention

- **Use TWAP oracles:** Time-weighted prices reduce manipulation
- **Implement slippage protection:** Maximum slippage for large transactions
- **Add circuit breakers:** Pause on large price deviations
- **Diversify liquidity sources:** Multiple pools or liquidity providers
- **Implement fee mechanisms:** Dynamic fees based on pool utilization

## Light Client Architecture

### Mechanism

1. Relayers submit source chain block headers to destination chain light client
2. Light client verifies block headers (consensus verification)
3. Once headers are verified, messages in those blocks are valid
4. Users submit proofs of messages to destination bridge contract
5. Bridge contract verifies proof against light client state and releases assets

### Contracts

**Source Chain:**
- `Bridge.sol` — Emits messages, manages deposits

**Destination Chain:**
- `LightClient.sol` — Verifies source chain block headers
- `Bridge.sol` — Verifies message proofs, releases assets

### Known Exploits

**Various light client exploits:**
- Fake block headers accepted by light client
- Consensus attack on source chain
- Light client upgrade vulnerabilities
- Root cause: Light client verification bugs + source chain consensus attacks

### Detection

- **Light client verification audit:** Verify consensus verification logic
- **Block header validation:** Check for proper signature verification
- **Relayer decentralization:** Assess relayer diversity and censorship resistance
- **Light client upgrade security:** Review upgrade mechanism
- **Source chain consensus security:** Assess source chain attack cost

### Prevention

- **Use battle-tested light client implementations:** IBC, Rainbow, etc.
- **Implement light client upgrades with timelock:** Delay between proposal and execution
- **Diversify relayers:** Multiple independent relayers
- **Monitor source chain consensus:** Alert on consensus anomalies
- **Use formal verification:** Prove light client verification correctness

## Optimistic Verification Architecture

### Mechanism

1. User deposits assets into bridge contract on source chain
2. Bridge contract emits message (optimistically accepted)
3. Message is relayed to destination chain
4. Destination bridge accepts message optimistically
5. Challenge window opens (e.g., 30 minutes)
6. Anyone can challenge invalid message by posting bond
7. If challenged, dispute resolution determines validity
8. If unchallenged, message is finalized and assets released

### Contracts

**Source Chain:**
- `Bridge.sol` — Accepts deposits, emits messages

**Destination Chain:**
- `OptimisticBridge.sol` — Accepts messages optimistically, manages challenges
- `DisputeResolution.sol` — Resolves challenges, determines message validity

### Known Exploits

**Nomad ($190M, August 2022):**
- Improper initialization of replica contract
- Attacker could approve any message as valid
- Root cause: Uninitialized contract + missing initialization check

### Detection

- **Initialization status check:** Verify all contracts are properly initialized
- **Challenge mechanism audit:** Verify challenge logic and bond economics
- **Dispute resolution security:** Assess dispute resolution contract security
- **Message delay analysis:** Evaluate dispute window duration
- **Challenge bond assessment:** Verify bond is sufficient to prevent spam

### Prevention

- **Use initialize pattern with reentrancy guard:** Prevent uninitialized contract usage
- **Verify initialization status in all functions:** Check before processing messages
- **Implement adequate dispute window:** Long enough for challenge, short enough for UX
- **Set appropriate challenge bond:** High enough to prevent spam, low enough for participation
- **Use decentralized dispute resolution:** Multiple independent disputers
- **Add message finality delay:** Wait for dispute window before considering message final

## Cross-Chain Message Verification Patterns

### Signature-Based Verification

**Mechanism:** Validators sign messages, destination contract verifies signatures.

**Security considerations:**
- Signature scheme (ECDSA, BLS, Schnorr, MPC)
- Threshold requirements (m-of-n)
- Signature malleability protection
- Key rotation and revocation

**Best practices:**
- Use battle-tested signature libraries (OpenZeppelin, etc.)
- Implement strict signature count validation
- Add signature malleability protection (EIP-2 for ECDSA)
- Use threshold signatures for efficiency
- Implement key rotation mechanism

### Merkle Proof Verification

**Mechanism:** Messages committed in merkle tree, users submit merkle proofs.

**Security considerations:**
- Merkle tree construction (sorted vs. unsorted)
- Proof verification logic
- Data availability (can users construct proofs?)
- Tree update mechanism

**Best practices:**
- Use sorted merkle trees (prevent second-preimage attacks)
- Verify proof path length matches tree depth
- Ensure data availability for proof construction
- Implement secure tree update mechanism

### Optimistic Verification

**Mechanism:** Messages accepted optimistically, challenged during dispute window.

**Security considerations:**
- Dispute window duration
- Challenge bond economics
- Dispute resolution mechanism
- Message finality delay

**Best practices:**
- Set dispute window long enough for challenge (30+ minutes)
- Set challenge bond high enough to prevent spam
- Use decentralized dispute resolution
- Implement message finality delay
- Add emergency pause mechanism

## Bridge Upgrade Security

### Proxy Patterns

**Transparent Proxy:**
- Admin can upgrade implementation
- Users cannot call admin functions
- Lower upgrade risk

**UUPS Proxy:**
- Implementation contract can upgrade itself
- More flexible but higher risk
- Requires careful implementation contract security

**Beacon Proxy:**
- Multiple proxies share implementation via beacon
- Efficient for many proxies
- Beacon compromise affects all proxies

### Upgrade Security Checklist

- [ ] Proxy pattern reviewed (transparent, UUPS, beacon)
- [ ] Storage layout compatibility verified
- [ ] Implementation contract initialized
- [ ] Admin key multisig (3-of-5 or higher)
- [ ] Upgrade timelock (48+ hours)
- [ ] Emergency pause mechanism
- [ ] Upgrade event logging
- [ ] Implementation contract audited
- [ ] Storage collision check
- [ ] Reentrancy guard on initialization
