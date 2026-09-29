# Address Profiles Reference

Detailed identification techniques for different address types on blockchain.

## EOA (Externally Owned Account) Identification

### EVM EOA

**Characteristics:**
- 20-byte hex address (42 chars with `0x` prefix)
- No bytecode at address (`eth_getCode` returns `0x`)
- Can sign transactions directly
- Nonce increments with each transaction
- Controlled by private key

**Detection:**
```python
# Pseudocode
code = rpc.eth_getCode(address)
is_eoa = (code == "0x" or code == "")
```

**Subtypes:**
- **Standard EOA:** Single key, no special features
- **Multi-sig EOA:** Not possible (multi-sig requires contract)
- **Smart wallet EOA:** Not possible (smart wallets are contracts)

### Solana Wallet

**Characteristics:**
- Base58-encoded 32-byte public key
- Owned by System Program
- Holds SOL balance
- Can sign transactions
- No executable code

**Detection:**
```python
# Pseudocode
account = rpc.getAccountInfo(address)
is_wallet = (account.owner == "11111111111111111111111111111111" and
             not account.executable)
```

### Bitcoin Address

**Characteristics:**
- Not a UTXO address (those are scripts)
- Private key controls UTXOs
- Address is hash of public key
- No on-chain representation of "wallet"

**Detection:**
- Bitcoin addresses are always UTXO scripts, not accounts
- "Wallet" is an abstraction over UTXOs
- Cluster UTXOs by common-input heuristic

## Smart Contract Identification

### EVM Contract

**Characteristics:**
- Has bytecode at address
- Executes code when called
- Cannot initiate transactions (only respond)
- Can hold tokens and ETH
- Can be verified (source code published)

**Detection:**
```python
code = rpc.eth_getCode(address)
is_contract = (len(code) > 2)  # More than "0x"
```

**Verification Status:**
- **Verified:** Source code published on explorer
- **Unverified:** Bytecode only, no source
- **Partially verified:** Some contracts verified
- **Similar match:** Bytecode matches known contract

### Solana Program

**Characteristics:**
- Account with `executable = true`
- Owned by BPF Loader
- Contains program logic
- Can have upgrade authority

**Detection:**
```python
account = rpc.getAccountInfo(address)
is_program = account.executable
```

**Program Types:**
- **Native programs:** Built into Solana runtime
- **BPF programs:** User-deployed, upgradeable
- **Verified programs:** Source code published

## Exchange Hot Wallet Identification

### Characteristics

**Behavioral Indicators:**
- High transaction volume (1000+ tx/day)
- Many unique counterparties (100+ addresses)
- Frequent small deposits (user deposits)
- Periodic large withdrawals (batching)
- 24/7 activity (no downtime)
- Low failure rate

**On-Chain Indicators:**
- Labeled on Etherscan/Solscan as exchange
- Tagged by Nansen/Chainalysis
- Known deposit address patterns
- High token diversity (many tokens held)
- Stablecoin-heavy balances

### Known Exchange Wallet Patterns

**Centralized Exchanges:**
- Binance: Multiple hot wallets, frequent rotation
- Coinbase: Known wallet labels, high volume
- Kraken: Segregated wallets per user
- OKX: Multi-chain hot wallets
- Bitfinex: Known deposit patterns

**Detection Steps:**
1. Check explorer labels (Etherscan, Solscan)
2. Query Nansen/Chainalysis labels
3. Analyze transaction patterns
4. Cross-reference with known exchange addresses
5. Verify with deposit address patterns

### Exchange Deposit Addresses

**Characteristics:**
- Unique per user (HD wallet derivation)
- Only receive funds (no outbound)
- Funds swept to hot wallet periodically
- Short lifespan (address rotation)
- Low individual volume

**Detection:**
- Inbound-only transactions
- Funds moved to known hot wallet
- Address derived from exchange HD wallet
- No contract interactions

## Mixer/Tumbler Identification

### Known Mixers

**EVM Mixers:**
- Tornado Cash (ETH, DAI, USDC, USDT, WBTC, cDAI)
- Tornado Cash Nova (privacy pools)
- Aztec Network (zk.money)
- Railgun (privacy protocol)

**Bitcoin Mixers:**
- Wasabi Wallet (CoinJoin)
- Samourai Wallet (Whirlpool, Stonewall)
- ChipMixer (defunct)
- Tornado Cash (also on Bitcoin via bridges)

**Detection Indicators:**
- Equal-value outputs (Tornado Cash pattern)
- Time-delayed withdrawals
- Multiple unrelated depositors
- No on-chain link between deposit and withdrawal
- Known mixer contract addresses
- Privacy-focused transaction patterns

### Tornado Cash Detection

**Contract Addresses (Ethereum):**
- 0.1 ETH: `0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc`
- 1 ETH: `0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c0c2Bd7d`
- 10 ETH: `0x910Cbd523D972eb0a6f4cAe4618aD62622b39DbF`
- 100 ETH: `0xA160cdAB225685dA1d56aa342Ad8841c3b53f291D`

**Behavioral Pattern:**
1. Deposit: Send exact amount to mixer contract
2. Wait: Random time delay (hours to days)
3. Withdraw: Send to new address, prove deposit via ZK proof
4. No link: On-chain observer cannot link deposit to withdrawal

### Mixer Risk Scoring

**High Risk:**
- Direct interaction with known mixer
- Funds from mixer to CEX deposit
- Multiple mixer interactions
- Mixer interaction followed by bridging

**Medium Risk:**
- Indirect mixer interaction (funds passed through)
- Mixer interaction long ago (aged funds)
- Small mixer interaction relative to total volume

**Low Risk:**
- No mixer interaction
- Funds from verified protocols
- Clean transaction history

## Bridge Contract Identification

### EVM Bridge Contracts

**Native Bridges:**
- **Arbitrum Bridge:** `0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a` (Inbox)
- **Optimism Bridge:** `0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1` (Portal)
- **Polygon Bridge:** `0xA0c68C638235ee32657e8f720a23ceC1cFc7c7f7` (PoS Bridge)

**Third-Party Bridges:**
- **Wormhole:** `0x3ee18B221449A578A64534D9B4DC9DA8609f2B60`
- **LayerZero:** Various endpoint contracts
- **Stargate:** `0x8731d54E9D02c286767d56ac03e8037C079e1C9d` (Router)
- **Hop Protocol:** Various bridge contracts
- **Across Protocol:** `0x4D9079Bb4165aeb4084c526a326951dC94f8F1F8` (SpokePool)

**Detection:**
- Large asset reserves (TVL)
- `deposit`, `withdraw`, `lock`, `mint`, `burn` functions
- Governance-controlled parameters
- Emergency pause mechanisms
- Multi-sig or DAO governance

### Bridge Interaction Patterns

**Lock-Mint Pattern:**
```
1. User calls deposit() on source chain
2. Bridge locks tokens in contract
3. Relayer calls mint() on destination chain
4. User receives wrapped tokens
```

**Burn-Mint Pattern:**
```
1. User calls burn() on source chain
2. Bridge burns tokens
3. Relayer calls mint() on destination chain
4. User receives native tokens
```

**Liquidity Pattern:**
```
1. User calls swap() on source chain
2. Bridge swaps from liquidity pool
3. Relayer calls swap() on destination chain
4. User receives tokens from liquidity pool
```

## DeFi Protocol Identification

### DEX (Decentralized Exchange)

**Characteristics:**
- Token swap functions (`swap`, `exchange`, `trade`)
- Liquidity pool contracts
- Factory contract for pool creation
- Fee collection mechanisms
- Price oracle integration

**Known DEXes:**
- Uniswap (V2, V3): Factory + Router pattern
- SushiSwap: Fork of Uniswap
- Curve: Stablecoin-focused, low slippage
- Balancer: Weighted pools, multi-token
- PancakeSwap: BSC DEX
- Osmosis: Cosmos DEX

**Detection:**
- `swapExactTokensForTokens` function calls
- Liquidity pool token holdings
- Factory contract interactions
- LP token minting/burning

### Lending Protocol

**Characteristics:**
- Collateral deposit functions
- Borrow/repay functions
- Liquidation mechanisms
- Interest rate models
- Price oracle dependency

**Known Protocols:**
- Aave: Pool-based lending
- Compound: cToken model
- MakerDAO: CDP (Collateralized Debt Position)
- Venus: BSC lending
- Benqi: Avalanche lending

**Detection:**
- `deposit`, `borrow`, `repay`, `liquidate` functions
- Collateral token approvals
- Debt token minting
- Oracle price feed interactions

### Yield Aggregator

**Characteristics:**
- Vault contracts (ERC-4626)
- Strategy contracts for yield generation
- Auto-compounding mechanisms
- Performance fee collection

**Known Protocols:**
- Yearn Finance: Vaults V2
- Beefy Finance: Multi-chain aggregator
- Harvest Finance: Farm strategies
- Autofarm: BSC aggregator

**Detection:**
- `deposit`, `withdraw` with share minting
- Strategy contract interactions
- Reward token harvesting
- Vault share price increases

## NFT Contract Identification

### ERC-721 (NFT)

**Characteristics:**
- `ownerOf(tokenId)` function
- `tokenURI(tokenId)` function
- `Transfer` event with `tokenId`
- Non-fungible (each token unique)
- Metadata stored on-chain or IPFS

**Detection:**
- `safeTransferFrom` function calls
- `Transfer` event with single tokenId
- `tokenURI` returns metadata URL
- Contract implements ERC-721 interface

**Known NFT Collections:**
- Bored Ape Yacht Club (BAYC)
- CryptoPunks
- Azuki
- CloneX
- Doodles

### ERC-1155 (Multi-Token)

**Characteristics:**
- `balanceOfBatch` function
- `TransferBatch` event
- Fungible and non-fungible tokens
- Gas-efficient batch operations
- Semi-fungible tokens

**Detection:**
- `safeBatchTransferFrom` function calls
- `TransferBatch` event
- `uri(tokenId)` returns metadata
- Contract implements ERC-1155 interface

**Known ERC-1155 Projects:**
- Enjin Coin
- Axie Infinity
- Gods Unchained
- The Sandbox

### NFT Marketplace

**Characteristics:**
- Listing functions (`listItem`, `createOffer`)
- Auction mechanisms
- Royalty collection
- Escrow during trade
- Fee collection

**Known Marketplaces:**
- OpenSea: Seaport protocol
- Blur: Aggregator + marketplace
- LooksRare: Community-focused
- Magic Eden: Solana + multi-chain

## Token Contract Identification

### ERC-20 (Fungible Token)

**Characteristics:**
- `balanceOf(address)` function
- `transfer(to, amount)` function
- `approve(spender, amount)` function
- `Transfer` event (from, to, value)
- `Approval` event (owner, spender, value)
- Decimals, name, symbol

**Detection:**
- `Transfer` event signature: `Transfer(address,address,uint256)`
- `balanceOf` returns uint256
- `decimals()` returns uint8
- Contract implements ERC-20 interface

**Verification:**
- Check source code verification
- Verify contract name and symbol
- Check total supply
- Verify decimals (usually 6 or 18)

### Token Risk Scoring

**High Risk:**
- Unverified source code
- No liquidity
- Honeypot (cannot sell)
- Mint function (inflation risk)
- Blacklist function
- High owner concentration

**Medium Risk:**
- Low liquidity
- Recent deployment
- Few holders
- No audit
- Centralized control

**Low Risk:**
- Verified source code
- High liquidity
- Many holders
- Audited
- Decentralized governance
- Established track record

## Multi-Sig Wallet Identification

### EVM Multi-Sig

**Characteristics:**
- Gnosis Safe (formerly Gnosis Multi-Sig)
- Multiple owners required for transactions
- Threshold signature requirement
- Module system for extensibility
- Guard mechanisms

**Detection:**
- `setup` function called with owners and threshold
- `execTransaction` function calls
- `isOwner(address)` returns true
- Contract implements Gnosis Safe interface

**Known Multi-Sig Contracts:**
- Gnosis Safe Singleton: `0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552`
- Gnosis Safe Proxy Factory: `0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2`

**Analysis:**
- Count owners
- Check threshold
- Identify owner addresses
- Check modules (enabled contracts)
- Check guards (transaction restrictions)

### Bitcoin Multi-Sig

**Characteristics:**
- P2SH address (prefix `3`)
- P2WSH address (prefix `bc1q`)
- M-of-N signature requirement
- Redeem script reveals signers

**Detection:**
- Spending transaction reveals redeem script
- Count required signatures
- Identify signer addresses
- Check for known multi-sig services

**Known Multi-Sig Services:**
- Casa: Key management
- Unchained Capital: Collaborative custody
- Electrum: Software multi-sig
- Specter: DIY multi-sig

## DAO/Governance Contract Identification

### Governance Token

**Characteristics:**
- ERC-20 token with voting power
- Delegation mechanism
- Snapshot integration
- Voting escrow (veToken model)

**Known Governance Tokens:**
- UNI (Uniswap)
- AAVE (Aave)
- COMP (Compound)
- CRV (Curve)
- ENS (Ethereum Name Service)

### Governance Contract

**Characteristics:**
- Proposal creation functions
- Voting functions (`castVote`, `castVoteBySig`)
- Quorum requirements
- Execution timelock
- Delegation tracking

**Detection:**
- `propose` function calls
- `castVote` function calls
- `execute` function calls
- `queue` function calls
- Proposal state tracking

**Known Governance Systems:**
- Compound Governor Bravo
- OpenZeppelin Governor
- Aragon
- DAOhaus
- Snapshot (off-chain voting)

### Timelock Contract

**Characteristics:**
- Delayed execution of transactions
- Admin-controlled parameters
- Queue, execute, cancel functions
- Used by DAOs for security

**Detection:**
- `queueTransaction` function calls
- `executeTransaction` function calls
- `cancelTransaction` function calls
- Delay parameter (usually 24-48 hours)

**Analysis:**
- Check delay duration
- Identify admin (usually governance contract)
- Monitor queued transactions
- Check for emergency mechanisms
