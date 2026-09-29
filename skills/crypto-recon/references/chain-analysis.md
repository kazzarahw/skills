# Chain Analysis Reference

Detailed chain-specific analysis techniques for blockchain reconnaissance.

## EVM Chain Analysis

### Ethereum Mainnet

**Address Types:**
- EOA: 20-byte address, no bytecode, controlled by private key
- Contract: 20-byte address, has bytecode, executes on call
- Proxy: Contract that delegates to implementation (EIP-1967, EIP-1822, EIP-897)

**Key RPC Methods:**
```
eth_getCode          → bytecode (empty = EOA)
eth_getBalance       → native balance
eth_getTransactionCount → nonce
eth_getLogs           → event logs (token transfers, contract events)
eth_call              → read-only contract calls
debug_traceTransaction → execution trace (archive node required)
```

**Token Standards:**
- ERC-20: Fungible tokens. Check `balanceOf`, `transfer`, `approve`, `Transfer` events
- ERC-721: NFTs. Check `ownerOf`, `tokenURI`, `Transfer` events (single)
- ERC-1155: Multi-token. Check `balanceOfBatch`, `TransferBatch`, `TransferSingle`
- ERC-4626: Tokenized vaults. Check `asset`, `convertToShares`, `deposit`, `withdraw`

**Proxy Patterns:**
| Pattern | Storage Slot | Detection |
|---------|-------------|-----------|
| EIP-1967 | `0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc` | Implementation address |
| EIP-1967 Admin | `0xb53127740205c462e50a551533367715822234d53a18f31513cf5c67fa8cb3bc` | Admin address |
| EIP-1822 | `0xc5f16f0fcc639fa48a6947836d9850f504798523bf8c9a3a87d58ef68b5c9e7e` | Implementation address |
| EIP-897 | `0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ce0048b5cc966` | Delegate address |
| Transparent | `0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aea26cf4142e7bf64e8a4f900` | Admin address |

**Gas Analysis:**
- High gas limit → complex contract interactions
- Gas price spikes → MEV, front-running, or urgent transactions
- Out-of-gas reverts → failed attacks, logic errors, or griefing

### Layer 2 Chains

**Arbitrum:**
- Nitro architecture: WASM-based fraud proofs
- ArbSys precompile: `0x64` for L1→L2 info
- Delayed inbox: L1→L2 messages have delay
- ArbOS: System-level operations

**Optimism:**
- Bedrock architecture: EVM-equivalent
- L2OutputOracle: State root commitments
- Portal contracts: L1→L2 messaging
- Gas oracle: L1 fee tracking

**Base:**
- Built on OP Stack
- Same tooling as Optimism
- Coinbase ecosystem integration

**Polygon:**
- PoS chain: Checkpoint-based finality
- zkEVM: ZK-rollup with EVM equivalence
- Heimdall: Validator layer
- Bor: Block production layer

**L2-Specific Considerations:**
- Bridge contracts hold large asset reserves
- Sequencer centralization risk
- Different finality guarantees than L1
- Native token bridges vs third-party bridges

### EVM Sidechains

**BNB Smart Chain:**
- EVM-compatible, PoSA consensus
- Different validator set than Ethereum
- Lower gas costs, higher throughput

**Avalanche C-Chain:**
- EVM-compatible, Snowman consensus
- Subnet architecture for custom chains
- Different address format (same as EVM)

**Fantom:**
- EVM-compatible, Lachesis consensus
- Opera mainnet
- Different gas token (FTM)

## Solana Analysis

### Account Model

**Account Types:**
- Wallet (System Program): Holds SOL, controlled by keypair
- Program: Executable code, owned by BPF Loader
- PDA (Program Derived Address): No private key, derived from seeds + program ID
- Token Account: Holds SPL tokens, owned by Token Program
- Mint: Token metadata and supply
- Associated Token Account (ATA): PDA derived from wallet + mint

**Key RPC Methods:**
```
getAccountInfo          → account data, owner, lamports
getSignaturesForAddress → transaction history
getTransaction          → full transaction details
getProgramAccounts      → all accounts owned by program
getTokenAccountsByOwner → token balances
getMultipleAccounts      → batch account fetch
```

**PDA Derivation:**
```
PDA = findProgramAddress(seeds, program_id)
Seeds: [wallet_address, mint_address, ...]
Used for: ATAs, escrow accounts, governance accounts
```

**Program Verification:**
- Check program account for `upgradeable` flag
- Verify program ID against known registry
- Check upgrade authority (can modify program)
- Verify program data account

### SPL Token Analysis

**Token Program (TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA):**
- `mintTo`: Create new tokens
- `transfer`: Move tokens between accounts
- `approve`: Delegate spending authority
- `revoke`: Remove delegation
- `burn`: Destroy tokens
- `closeAccount`: Close token account

**Token-2022 (TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb):**
- Extended token standard
- Transfer fees, confidential tokens, metadata
- Same basic interface as Token Program

### Solana-Specific Risks

- **Rent exemption:** Accounts must hold minimum SOL or be closed
- **Priority fees:** Dynamic fee market for transaction inclusion
- **MEV:** Jito bundles, sandwich attacks on DEXes
- **Program upgrades:** Upgradeable programs can change behavior
- **Account confusion:** Similar account types can be mixed up

## Bitcoin Analysis

### Address Types

**P2PKH (Legacy):**
- Prefix: `1`
- Format: Base58Check
- Script: `OP_DUP OP_HASH160 <pubkey_hash> OP_EQUALVERIFY OP_CHECKSIG`
- Higher fees, less privacy

**P2SH (Script Hash):**
- Prefix: `3`
- Format: Base58Check
- Script: `OP_HASH160 <script_hash> OP_EQUAL`
- Used for multi-sig, SegWit compatibility

**P2WPKH (Native SegWit):**
- Prefix: `bc1q`
- Format: Bech32
- Script: `OP_0 <pubkey_hash>`
- Lower fees, better error detection

**P2TR (Taproot):**
- Prefix: `bc1p`
- Format: Bech32m
- Script: `OP_1 <x-only-pubkey>`
- Schnorr signatures, MAST, better privacy

**Testnet Addresses:**
- P2PKH: `m` or `n`
- P2SH: `2`
- P2WPKH: `tb1q`
- P2TR: `tb1p`

### UTXO Analysis

**Common-Input Heuristic:**
If multiple inputs are controlled by the same entity, they are clustered together. This is the primary clustering method for Bitcoin.

**Change Address Detection:**
- Output that is not the payment recipient
- Same address type as inputs
- Amount is "odd" (not round number)
- First output in transaction

**CoinJoin Detection:**
- Equal-value outputs
- Multiple unrelated inputs
- No change output
- Known Wasabi/Samourai patterns

### Lightning Network

**Channel Open:**
- Funding transaction: 2-of-2 multi-sig output
- Channel ID: derived from funding tx
- Capacity: sum of both parties' commitments

**Channel Close:**
- Cooperative: Both parties sign closing transaction
- Unilateral: One party broadcasts commitment transaction
- Breach remedy: Revocation key used if old state broadcast

**On-Chain Indicators:**
- Funding transactions to `3...` addresses (P2SH)
- Closing transactions with timelocks
- Large number of small channels = routing node

## Cosmos Ecosystem

### Address Format

**Bech32 Prefixes:**
| Chain | Prefix |
|-------|--------|
| Cosmos Hub | `cosmos` |
| Osmosis | `osmo` |
| Juno | `juno` |
| Secret | `secret` |
| Akash | `akash` |
| Regen | `regen` |
| Stargaze | `stars` |
| Evmos | `evmos` |

**Address Derivation:**
```
Address = bech32_encode(prefix, hash(pubkey))
Same pubkey → different address on each chain
```

### IBC (Inter-Blockchain Communication)

**Packet Lifecycle:**
```
1. Send: Source chain locks tokens, sends packet
2. Relay: Relayer forwards packet to destination
3. Recv: Destination chain mints vouchers
4. Ack: Acknowledgment returned to source
5. Timeout: If not received, tokens returned
```

**IBC Tracking:**
- `MsgSend`: Token transfer initiation
- `MsgRecv`: Token receipt on destination
- `MsgAcknowledgment`: Success confirmation
- `MsgTimeout`: Failed transfer recovery

**IBC Channels:**
- `channel-0`, `channel-1`, etc.
- Each channel connects two chains
- Channel state: OPEN, CLOSED, INIT

### Cosmos Modules

**Bank Module:**
- `MsgSend`: Native token transfer
- `MsgMultiSend`: Batch transfers
- `MsgSetSendEnabled`: Toggle transfers

**Staking Module:**
- `MsgDelegate`: Stake tokens to validator
- `MsgUndelegate`: Unstake (unbonding period)
- `MsgBeginRedelegate`: Move stake between validators

**Governance Module:**
- `MsgSubmitProposal`: Create proposal
- `MsgVote`: Vote on proposal
- `MsgDeposit`: Deposit tokens for proposal

**DEX Module (Osmosis):**
- `MsgSwapExactAmountIn`: Token swap
- `MsgJoinPool`: Add liquidity
- `MsgExitPool`: Remove liquidity

## Cross-Chain Analysis

### Bridge Types

**Lock-Mint Bridges:**
- Lock assets on source chain
- Mint wrapped assets on destination
- Examples: Polygon PoS Bridge, Arbitrum Bridge

**Burn-Mint Bridges:**
- Burn assets on source chain
- Mint native assets on destination
- Examples: Wormhole (some chains), LayerZero

**Liquidity Bridges:**
- Assets not locked, liquidity pools on both chains
- Examples: Stargate, Hop Protocol, Across

**Message Passing:**
- Generic message passing, not just token transfers
- Examples: LayerZero, Wormhole, Axelar, IBC

### Bridge Contract Identification

**EVM Bridge Contracts:**
- Large asset reserves
- `deposit`, `withdraw`, `lock`, `mint`, `burn` functions
- Governance-controlled parameters
- Emergency pause mechanisms

**Bridge Tracking:**
```
1. Identify bridge contract (known list or behavioral analysis)
2. Track deposit/lock transactions
3. Monitor relay/mint on destination chain
4. Track burn/release for return trips
5. Calculate bridge TVL and volume
```

### Cross-Chain Address Matching

**EVM Chains:**
- Same address across all EVM chains (same keypair)
- Check balance on multiple chains
- Track bridge transactions between chains

**Non-EVM Chains:**
- Different address formats
- Must use bridge transactions to link
- Track fund flow through bridges

**Multi-Chain Clustering:**
```
1. Start with known address on chain A
2. Find bridge transactions from chain A
3. Identify destination addresses on chain B
4. Repeat for chain B → chain C
5. Build multi-chain address graph
```

## Chain Identification Techniques

### Address Format Analysis

| Format | Prefix | Length | Chain |
|--------|--------|--------|-------|
| Hex (EVM) | `0x` | 42 chars | Ethereum, L2s, EVM sidechains |
| Base58 (Solana) | - | 32-44 chars | Solana |
| Bech32 (BTC) | `bc1` | 20-62 chars | Bitcoin |
| Bech32 (Cosmos) | `cosmos1` | 45 chars | Cosmos Hub |
| Bech32 (OsmO) | `osmo1` | 45 chars | Osmosis |

### RPC Chain ID

**EVM Chains:**
```
eth_chainId → chain_id
1: Ethereum
10: Optimism
42161: Arbitrum
8453: Base
137: Polygon
56: BSC
43114: Avalanche C-Chain
250: Fantom
```

**Non-EVM Chains:**
- Solana: `mainnet-beta`, `testnet`, `devnet`
- Bitcoin: `main`, `test`, `signet`
- Cosmos: chain ID in genesis file

## RPC Node Usage

### Public RPC Endpoints

**EVM:**
- Ankr: `https://rpc.ankr.com/eth`
- Alchemy: `https://eth-mainnet.g.alchemy.com/v2/<key>`
- Infura: `https://mainnet.infura.io/v3/<key>`
- Public: `https://ethereum.publicnode.com`

**Solana:**
- Helius: `https://mainnet.helius-rpc.com/?api-key=<key>`
- Triton: `https://rpc.triton.one`
- Public: `https://api.mainnet-beta.solana.com`

**Bitcoin:**
- mempool.space: `https://mempool.space/api`
- Blockchain.info: `https://blockchain.info`
- Electrum: Various public servers

### RPC Best Practices

1. **Rate limiting:** Respect provider rate limits
2. **Batch requests:** Use batch JSON-RPC for multiple calls
3. **Error handling:** Retry with exponential backoff
4. **Fallback nodes:** Have backup RPC endpoints
5. **Archive nodes:** Needed for historical state queries
6. **WebSocket:** Use for real-time monitoring

### RPC Security

- Never expose private keys in RPC calls
- Use read-only API keys when possible
- Validate RPC responses (man-in-the-middle protection)
- Use HTTPS for all RPC connections
- Rotate API keys regularly
