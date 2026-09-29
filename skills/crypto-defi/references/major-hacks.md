# Major DeFi Hacks Reference

## 1. Ronin Bridge — $625M (March 2022)

**Protocol:** Ronin Bridge (Axie Infinity)
**Chain:** Ronin (Ethereum sidechain)
**Loss:** $625M (173,600 ETH + 25.5M USDC)

### Root Cause
The Ronin Bridge used a 5-of-9 multisig validator set. An attacker compromised 4 Ronin validators and 1 Axie DAO validator (via gas-free RPC node), achieving the 5-of-9 threshold needed to authorize withdrawals.

### Attack Steps
1. Attacker gained access to 4 Ronin validator private keys
2. Attacker compromised Axie DAO validator (shared with Ronin)
3. Attacker forged withdrawal signatures (5-of-9 threshold met)
4. Attacker withdrew 173,600 ETH and 25.5M USDC in two transactions
5. Funds were mixed through Tornado Cash

### Lessons Learned
- 5-of-9 multisig is insufficient for bridges holding >$100M
- Validator key management must use HSMs and geographic distribution
- Shared validator sets across protocols create correlated risk
- Bridge monitoring should detect large withdrawals in real-time
- The 6-day detection delay (discovered by user withdrawal failure) is unacceptable

---

## 2. Wormhole — $326M (February 2022)

**Protocol:** Wormhole Bridge
**Chain:** Solana → Ethereum
**Loss:** $326M (120,000 wETH)

### Root Cause
The Wormhole bridge's Solana verifier contract had a signature verification bug. The `verify_signatures` function allowed an attacker to forge a valid signature for a message that was never actually signed by the guardian set.

### Attack Steps
1. Attacker identified signature verification bug in Solana verifier
2. Attacker forged a valid signature for a mint message
3. Attacker minted 120,000 wETH on Solana without locking ETH on Ethereum
4. Attacker bridged wETH to Ethereum, redeemed for ETH
5. Attacker laundered funds through DEXs and mixers

### Lessons Learned
- Signature verification must be exhaustive and tested against edge cases
- Bridge contracts should use battle-tested libraries (e.g., OpenZeppelin)
- Guardian/validator sets need diversity and monitoring
- Bridge contracts should have daily withdrawal limits
- The bug was in a deprecated code path that was still accessible

---

## 3. Nomad — $190M (August 2022)

**Protocol:** Nomad Bridge
**Chain:** Multi-chain
**Loss:** $190M

### Root Cause
A routine upgrade initialized the trusted root to `0x00`, making all messages valid by default. This allowed anyone to call `process()` and mint tokens on the destination chain without a corresponding lock on the source chain.

### Attack Steps
1. Attacker noticed that `0x00` was a valid trusted root
2. Attacker called `process()` with arbitrary message
3. Contract accepted message as valid (trusted root was `0x00`)
4. Attacker minted tokens on destination chain
5. Copycat attacks followed, amplifying losses

### Lessons Learned
- Initialization values must be validated (never default to zero)
- Upgrade procedures need comprehensive testing
- Bridge contracts should have message replay protection
- The "first mover" advantage meant the attacker profited most; copycats followed
- Optimistic verification with challenge period would have prevented this

---

## 4. Euler — $197M (March 2023)

**Protocol:** Euler Finance
**Chain:** Ethereum
**Loss:** $197M (various tokens)

### Root Cause
Euler's donation mechanism allowed direct token transfers to lending pools, corrupting the share/asset ratio. Combined with a self-liquidation bug, this allowed the attacker to drain funds.

### Attack Steps
1. Attacker flash borrowed 30M DAI from Aave
2. Deposited 20M DAI into Euler, received eDAI
3. Donated 10M DAI directly to Euler pool (inflation attack)
4. Self-liquidated position, receiving collateral discount
5. Repeated process across multiple pools
6. Attacker profited ~$197M after repaying flash loan

### Lessons Learned
- Donation attacks are a critical risk for lending protocols
- Self-liquidation mechanisms need careful design
- Share/asset ratio must be protected against direct transfers
- The attacker returned funds after negotiations (90% returned)

---

## 5. Beanstalk — $182M (April 2022)

**Protocol:** Beanstalk (stablecoin)
**Chain:** Ethereum
**Loss:** $182M

### Root Cause
Beanstalk's governance used a DAO where voting power was proportional to staked BEAN tokens. An attacker used a flash loan to acquire majority voting power and passed a malicious proposal that drained funds.

### Attack Steps
1. Attacker flash loaned large amount of BEAN and other tokens
2. Attacker deposited tokens into Beanstalk DAO, acquiring >50% voting power
3. Attacker submitted proposal to transfer funds to attacker address
4. Attacker voted for proposal with borrowed tokens (passed immediately)
5. Attacker executed proposal, drained $182M
6. Attacker repaid flash loan, kept profit

### Lessons Learned
- Flash loan voting is a critical governance risk
- Governance power snapshots must use historical balances
- Timelocks are essential for governance execution
- DAO treasuries should have spending limits
- The attacker used two proposals to avoid detection

---

## 6. Mango — $114M (October 2022)

**Protocol:** Mango Markets (perpetuals)
**Chain:** Solana
**Loss:** $114M

### Root Cause
Mango's oracle used spot prices from low-liquidity pairs. An attacker manipulated the MNGO token price, then borrowed against inflated collateral.

### Attack Steps
1. Attacker bought MNGO on spot market, inflating price
2. Mango oracle reported inflated MNGO price
3. Attacker borrowed against MNGO collateral at inflated value
4. MNGO price crashed, position was underwater
5. Attacker kept borrowed funds, left bad debt

### Lessons Learned
- Spot price oracles are insufficient for lending
- Low-liquidity tokens should not be used as collateral
- Oracle manipulation resistance is critical
- The attacker (Avraham Eisenberg) was identified and later arrested

---

## 7. Cream — $130M (October 2021)

**Protocol:** Cream Finance
**Chain:** Ethereum, BSC
**Loss:** $130M

### Root Cause
Cream's price oracle used spot prices from AMMs. An attacker manipulated the price of a low-liquidity token (yUSD) and borrowed against it.

### Attack Steps
1. Attacker flash borrowed large amount of ETH
2. Manipulated yUSD price on AMM
3. Cream oracle reported inflated yUSD price
4. Attacker deposited yUSD as collateral, borrowed ETH
5. yUSD price returned to normal, position was underwater
6. Attacker kept borrowed ETH

### Lessons Learned
- Spot price oracles are vulnerable to flash loan manipulation
- Low-liquidity collateral tokens are dangerous
- Oracle diversity and TWAP are essential

---

## 8. BadgerDAO — $120M (December 2021)

**Protocol:** BadgerDAO
**Chain:** Ethereum
**Loss:** $120M

### Root Cause
A compromised Cloudflare API key allowed an attacker to inject malicious JavaScript into the BadgerDAO frontend. The script approved token transfers to the attacker's address.

### Attack Steps
1. Attacker compromised Cloudflare API key
2. Attacker injected malicious JavaScript into BadgerDAO frontend
3. Script triggered token approval to attacker address when users interacted
4. Attacker drained approved tokens from users
5. Attacker laundered funds through DEXs

### Lessons Learned
- Frontend security is as important as smart contract security
- API keys must be rotated and monitored
- Users should verify contract interactions before signing
- The attack was detected by a user who noticed unusual approvals

---

## 9. Harvest — $34M (October 2020)

**Protocol:** Harvest Finance
**Chain:** Ethereum
**Loss:** $34M

### Root Cause
Harvest's Curve pool strategy used spot prices. An attacker manipulated the Curve pool price and deposited/withdrew from Harvest vaults for profit.

### Attack Steps
1. Attacker flash borrowed USDT and USDC
2. Manipulated Curve pool price (USDT/USDC ratio)
3. Deposited into Harvest vault at favorable rate
4. Withdrew from Harvest vault at favorable rate
5. Repaid flash loan, kept profit

### Lessons Learned
- Curve pool spot prices can be manipulated with sufficient capital
- Vault deposit/withdrawal should use TWAP or oracle prices
- Flash loan resistance is essential for yield protocols

---

## 10. bZx — $35M (February 2020)

**Protocol:** bZx (Fulcrum)
**Chain:** Ethereum
**Loss:** $35M (two attacks)

### Root Cause
bZx allowed flash loans to be used as collateral. An attacker used a flash loan to manipulate the price of WBTC on Kyber, then borrowed against the manipulated price.

### Attack Steps
1. Attacker flash borrowed ETH from dYdX
2. Swapped ETH for WBTC on Kyber, inflating WBTC price
3. Deposited WBTC as collateral on bZx
4. Borrowed ETH against inflated WBTC collateral
5. WBTC price returned to normal, position was underwater
6. Attacker kept borrowed ETH

### Lessons Learned
- Flash loans should not be usable as collateral
- Oracle manipulation resistance is critical
- The second attack exploited a different oracle vulnerability

---

## 11. Poly Network — $611M (August 2021)

**Protocol:** Poly Network
**Chain:** Multi-chain (Ethereum, BSC, Polygon)
**Loss:** $611M (largest at the time)

### Root Cause
Poly Network's cross-chain contract had a bug in the `EthCrossChainManager` contract that allowed an attacker to bypass the `verifyHeaderAndExecuteTx` function and call `putCurEpochConPubKeyBytes` to replace the keeper public key.

### Attack Steps
1. Attacker identified bug in cross-chain manager
2. Attacker called `putCurEpochConPubKeyBytes` to replace keeper key
3. Attacker forged cross-chain messages with new keeper key
4. Attacker minted tokens on multiple chains
5. Attacker bridged tokens to Ethereum

### Lessons Learned
- Cross-chain message validation must be exhaustive
- Keeper key management must be secure
- The attacker returned all funds after negotiations
- Bridge contracts need comprehensive testing

---

## 12. Wintermute — $160M (September 2022)

**Protocol:** Wintermute (market maker)
**Chain:** Ethereum, Optimism, Polygon
**Loss:** $160M

### Root Cause
Wintermute used a vulnerable key generation tool (Profanity) that generated predictable private keys. An attacker brute-forced the key and drained funds.

### Attack Steps
1. Attacker identified Wintermute's Profanity-generated address
2. Attacker brute-forced the private key (predictable generation)
3. Attacker accessed Wintermute's hot wallet
4. Attacker drained $160M across multiple chains
5. Attacker laundered funds through Tornado Cash

### Lessons Learned
- Key generation must use cryptographically secure random number generators
- Profanity addresses are vulnerable to brute-force attacks
- Hot wallet limits and monitoring are essential
- The attacker was identified through clustering analysis

---

## 13. Harmony Bridge — $100M (June 2022)

**Protocol:** Harmony Bridge
**Chain:** Ethereum, BSC
**Loss:** $100M

### Root Cause
The Harmony Bridge used a 2-of-5 multisig validator set. An attacker compromised 2 validator keys and forged withdrawal signatures.

### Attack Steps
1. Attacker compromised 2 validator private keys
2. Attacker forged withdrawal signatures (2-of-5 threshold met)
3. Attacker withdrew tokens from bridge
4. Attacker laundered funds through Tornado Cash and DEXs

### Lessons Learned
- 2-of-5 multisig is insufficient for bridges
- Validator key management must use HSMs
- Bridge monitoring should detect large withdrawals
- The attacker was identified as Lazarus Group (North Korea)

---

## 14. Qubit Bridge — $80M (January 2022)

**Protocol:** Qubit Bridge
**Chain:** Ethereum, BSC
**Loss:** $80M

### Root Cause
The Qubit Bridge's `deposit` function had a bug that allowed an attacker to deposit 0 ETH and receive xETH (wrapped ETH) in return.

### Attack Steps
1. Attacker identified deposit function bug
2. Attacker called `deposit` with 0 ETH
3. Contract minted xETH to attacker
4. Attacker redeemed xETH for ETH on BSC
5. Attacker repeated process, draining bridge

### Lessons Learned
- Deposit functions must validate input amounts
- Bridge contracts need comprehensive testing
- Zero-value transactions should be rejected

---

## 15. Multichain — $126M (July 2023)

**Protocol:** Multichain (Anyswap)
**Chain:** Multi-chain
**Loss:** $126M

### Root Cause
Multichain's CEO was arrested by Chinese police, and the private keys were compromised. The attacker used the compromised keys to drain funds from bridge contracts.

### Attack Steps
1. CEO arrested, private keys compromised
2. Attacker used keys to authorize fraudulent withdrawals
3. Attacker drained $126M across multiple chains
4. Attacker bridged funds to Ethereum
5. Attacker laundered funds through mixers

### Lessons Learned
- Centralized key management is a single point of failure
- Bridge protocols need decentralized key management
- CEO arrest highlights jurisdictional risk
- The protocol was effectively rug-pulled after CEO arrest

---

## Summary Statistics

| Year | Total Loss | # of Major Hacks | Largest Hack |
|------|-----------|-------------------|--------------|
| 2020 | ~$100M | 5 | Harvest ($34M) |
| 2021 | ~$1.2B | 8 | Poly Network ($611M) |
| 2022 | ~$3.5B | 12 | Ronin ($625M) |
| 2023 | ~$1.5B | 8 | Euler ($197M) |
| 2024 | ~$800M | 5 | Various |
| 2025 | ~$600M | 3 | Various |
| 2026 | ~$400M | 2 | Various |

## Common Attack Patterns

1. **Oracle manipulation** — Most common, affects lending and perpetuals
2. **Bridge validator compromise** — Largest losses, affects bridges
3. **Flash loan governance** — Affects DAOs and governance protocols
4. **Inflation/donation attacks** — Affects yield and AMM protocols
5. **Private key compromise** — Affects all protocols with admin keys
6. **Frontend attacks** — Affects all protocols with web interfaces
7. **Reentrancy** — Classic but still occurs in poorly written contracts
8. **Access control bugs** — Missing or incorrect permission checks
