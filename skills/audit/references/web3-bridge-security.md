# Bridge Security Audit Procedures

Comprehensive guide for auditing cross-chain bridge security, covering architecture analysis, validator sets, message verification, and known exploits.

---

## Table of Contents

- [Architecture Classification](#architecture-classification)
  - [Lock-and-Mint](#lock-and-mint)
  - [Burn-and-Mint](#burn-and-mint)
  - [Liquidity Pool](#liquidity-pool)
  - [Light Client](#light-client)
  - [Optimistic](#optimistic)
- [Validator Set Analysis](#validator-set-analysis)
  - [Validator Count and Distribution](#validator-count-and-distribution)
  - [Collusion Threshold](#collusion-threshold)
  - [Key Management](#key-management)
- [Message Verification](#message-verification)
  - [Signature Scheme](#signature-scheme)
  - [Replay Protection](#replay-protection)
  - [Message Integrity](#message-integrity)
- [Liquidity Analysis](#liquidity-analysis)
  - [Asset Backing](#asset-backing)
  - [Pool Depth](#pool-depth)
  - [Withdrawal Capacity](#withdrawal-capacity)
- [Upgrade and Admin Security](#upgrade-and-admin-security)
  - [Proxy Patterns](#proxy-patterns)
  - [Admin Keys](#admin-keys)
  - [Timelocks](#timelocks)
- [Known Bridge Exploits](#known-bridge-exploits)
  - [Wormhole (2022)](#wormhole-2022)
  - [Ronin Bridge (2022)](#ronin-bridge-2022)
  - [Nomad Bridge (2022)](#nomad-bridge-2022)
  - [Multichain (2023)](#multichain-2023)
  - [Poly Network (2021)](#poly-network-2021)
  - [Harmony Bridge (2022)](#harmony-bridge-2022)
- [Bridge Security Checklist](#bridge-security-checklist)
  - [Architecture](#architecture)
  - [Validator Set](#validator-set)
  - [Message Verification](#message-verification-1)
  - [Liquidity](#liquidity)
  - [Admin Security](#admin-security)
  - [Monitoring](#monitoring)

---

## Architecture Classification

### Lock-and-Mint

```
Source Chain                    Destination Chain
┌─────────────┐                ┌─────────────┐
│   User      │                │   User      │
│   Locks     │  ──────────►   │   Mints     │
│   Asset     │   Message      │   Asset     │
└─────────────┘                └─────────────┘
```

**Characteristics:**
- Asset locked on source chain
- Equivalent asset minted on destination chain
- Requires liquidity on destination chain
- Examples: Wormhole, Ronin

**Audit Focus:**
- Lock contract security
- Mint authorization
- Message verification
- Liquidity adequacy

### Burn-and-Mint

```
Source Chain                    Destination Chain
┌─────────────┐                ┌─────────────┐
│   User      │                │   User      │
│   Burns     │  ──────────►   │   Mints     │
│   Asset     │   Message      │   Asset     │
└─────────────┘                └─────────────┘
```

**Characteristics:**
- Asset burned on source chain
- Equivalent asset minted on destination chain
- No liquidity required
- Examples: Polygon PoS Bridge

**Audit Focus:**
- Burn authorization
- Mint authorization
- Message verification
- Replay protection

### Liquidity Pool

```
Source Chain                    Destination Chain
┌─────────────┐                ┌─────────────┐
│   User      │                │   User      │
│   Swaps     │  ──────────►   │   Receives  │
│   Asset     │   Message      │   Asset     │
└─────────────┘                └─────────────┘
       │                              │
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│   Liquidity │                │   Liquidity │
│   Pool      │                │   Pool      │
└─────────────┘                └─────────────┘
```

**Characteristics:**
- User swaps on source chain
- Liquidity pool on destination chain
- Requires deep liquidity
- Examples: Multichain, Synapse

**Audit Focus:**
- Liquidity pool security
- Price oracle security
- Slippage protection
- Liquidity adequacy

### Light Client

```
Source Chain                    Destination Chain
┌─────────────┐                ┌─────────────┐
│   User      │                │   User      │
│   Locks     │  ──────────►   │   Mints     │
│   Asset     │   Light Client │   Asset     │
└─────────────┘                └─────────────┘
       │                              │
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│   Consensus │◄──────────────►│   Consensus │
│   Proof     │   Verification │   Proof     │
└─────────────┘                └─────────────┘
```

**Characteristics:**
- Light client verifies consensus
- No trusted validators
- Most secure but expensive
- Examples: IBC (Cosmos)

**Audit Focus:**
- Light client security
- Consensus verification
- Proof validation
- Finality handling

### Optimistic

```
Source Chain                    Destination Chain
┌─────────────┐                ┌─────────────┐
│   User      │                │   User      │
│   Locks     │  ──────────►   │   Mints     │
│   Asset     │   Optimistic   │   Asset     │
└─────────────┘                └─────────────┘
       │                              │
       ▼                              ▼
┌─────────────┐                ┌─────────────┐
│   Challenge │                │   Challenge │
│   Period    │                │   Period    │
└─────────────┘                └─────────────┘
```

**Characteristics:**
- Optimistic verification
- Challenge period for fraud proofs
- Requires watchers
- Examples: Nomad (deprecated)

**Audit Focus:**
- Fraud proof mechanism
- Challenge period adequacy
- Watcher incentives
- Censorship resistance

---

## Validator Set Analysis

### Validator Count and Distribution

```solidity
// SECURE: Validator set analysis
contract Bridge {
    uint256 public constant TOTAL_VALIDATORS = 15;
    uint256 public constant REQUIRED_SIGNATURES = 8;
    
    mapping(address => bool) public validators;
    mapping(address => bool) public validatorJurisdictions;
    
    function addValidator(address validator, bytes32 jurisdiction) external onlyOwner {
        require(!validators[validator], "Already validator");
        validators[validator] = true;
        validatorJurisdictions[validator] = jurisdiction;
    }
    
    function getValidatorCount() external view returns (uint256) {
        return TOTAL_VALIDATORS;
    }
    
    function getRequiredSignatures() external view returns (uint256) {
        return REQUIRED_SIGNATURES;
    }
}
```

### Collusion Threshold

| Total Validators | Required Signatures | Collusion Threshold | Security Level |
|------------------|---------------------|---------------------|----------------|
| 9 | 5 | 4 | Low |
| 15 | 8 | 7 | Medium |
| 21 | 11 | 10 | High |
| 31 | 16 | 15 | Very High |

**Recommendation:** Use at least 8/15 for bridges holding > $100M.

### Key Management

```solidity
// SECURE: Key management
contract Bridge {
    // Use hardware wallets for validator keys
    // Distribute validators across jurisdictions
    // Implement key rotation
    
    mapping(address => uint256) public keyRotationBlock;
    uint256 public constant KEY_ROTATION_PERIOD = 90 days;
    
    function rotateKey(address newValidator) external onlyOwner {
        require(block.timestamp >= keyRotationBlock[msg.sender] + KEY_ROTATION_PERIOD, "Too early");
        validators[newValidator] = true;
        keyRotationBlock[newValidator] = block.timestamp;
    }
}
```

---

## Message Verification

### Signature Scheme

```solidity
// SECURE: ECDSA signature verification
function verifySignature(
    bytes32 messageHash,
    bytes memory signature,
    address expectedSigner
) internal pure returns (bool) {
    address signer = ECDSA.recover(messageHash, signature);
    return signer == expectedSigner;
}

// SECURE: Multi-signature verification
mapping(bytes32 => mapping(address => bool)) public signatures;
mapping(bytes32 => uint256) public signatureCount;

function submitSignature(bytes32 messageHash, bytes memory signature) external onlyValidator {
    require(!signatures[messageHash][msg.sender], "Already signed");
    require(verifySignature(messageHash, signature, msg.sender), "Invalid signature");
    signatures[messageHash][msg.sender] = true;
    signatureCount[messageHash]++;
}

function executeMessage(bytes32 messageHash, bytes memory message) external {
    require(signatureCount[messageHash] >= REQUIRED_SIGNATURES, "Insufficient signatures");
    // Execute message
}
```

### Replay Protection

```solidity
// SECURE: Replay protection
mapping(bytes32 => bool) public executedMessages;
mapping(uint256 => bool) public processedNonces;

function executeMessage(bytes memory message, uint256 nonce) external {
    bytes32 messageHash = keccak256(message);
    require(!executedMessages[messageHash], "Already executed");
    require(!processedNonces[nonce], "Nonce already used");
    
    executedMessages[messageHash] = true;
    processedNonces[nonce] = true;
    
    // Execute message
}
```

### Message Integrity

```solidity
// SECURE: Message integrity
function verifyMessageIntegrity(
    bytes memory message,
    bytes32 expectedHash
) internal pure returns (bool) {
    return keccak256(message) == expectedHash;
}

// SECURE: Include chain ID and contract address
function getMessageHash(
    uint256 sourceChainId,
    address sourceContract,
    uint256 destinationChainId,
    address destinationContract,
    bytes memory message
) internal pure returns (bytes32) {
    return keccak256(abi.encodePacked(
        sourceChainId,
        sourceContract,
        destinationChainId,
        destinationContract,
        message
    ));
}
```

---

## Liquidity Analysis

### Asset Backing

```solidity
// SECURE: Asset backing verification
mapping(address => uint256) public lockedAssets;
mapping(address => uint256) public mintedAssets;

function verifyBacking(address token) external view returns (bool) {
    return lockedAssets[token] >= mintedAssets[token];
}

function lockAsset(address token, uint256 amount) external {
    lockedAssets[token] += amount;
    // Lock tokens in contract
}

function mintAsset(address token, uint256 amount) external {
    require(verifyBacking(token), "Insufficient backing");
    mintedAssets[token] += amount;
    // Mint tokens to user
}
```

### Pool Depth

```solidity
// SECURE: Pool depth check
mapping(address => uint256) public poolDepth;
uint256 public constant MIN_POOL_DEPTH = 1000000 * 1e18; // $1M

function withdraw(address token, uint256 amount) external {
    require(poolDepth[token] >= amount, "Insufficient liquidity");
    require(poolDepth[token] - amount >= MIN_POOL_DEPTH, "Below minimum");
    // Process withdrawal
}
```

### Withdrawal Capacity

```solidity
// SECURE: Withdrawal capacity
mapping(address => uint256) public dailyWithdrawalLimit;
mapping(address => uint256) public dailyWithdrawn;
mapping(address => uint256) public lastWithdrawalDay;

function withdraw(address token, uint256 amount) external {
    uint256 currentDay = block.timestamp / 1 days;
    if (currentDay > lastWithdrawalDay[token]) {
        dailyWithdrawn[token] = 0;
        lastWithdrawalDay[token] = currentDay;
    }
    require(dailyWithdrawn[token] + amount <= dailyWithdrawalLimit[token], "Exceeds daily limit");
    dailyWithdrawn[token] += amount;
    // Process withdrawal
}
```

---

## Upgrade and Admin Security

### Proxy Patterns

```solidity
// SECURE: EIP-1967 proxy pattern
contract BridgeProxy {
    bytes32 private constant IMPLEMENTATION_SLOT = 
        bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1);
    bytes32 private constant ADMIN_SLOT = 
        bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1);
    
    constructor(address _implementation, address _admin) {
        assembly {
            sstore(IMPLEMENTATION_SLOT, _implementation)
            sstore(ADMIN_SLOT, _admin)
        }
    }
    
    function _implementation() internal view returns (address) {
        assembly {
            mstore(0, sload(IMPLEMENTATION_SLOT))
            return(0, 0x20)
        }
    }
    
    function _admin() internal view returns (address) {
        assembly {
            mstore(0, sload(ADMIN_SLOT))
            return(0, 0x20)
        }
    }
    
    fallback() external payable {
        address impl = _implementation();
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}
```

### Admin Keys

```solidity
// SECURE: Multi-sig admin
contract BridgeAdmin {
    address[] public admins;
    mapping(address => bool) public isAdmin;
    uint256 public constant REQUIRED_ADMINS = 3;
    
    mapping(bytes32 => mapping(address => bool)) public adminSignatures;
    mapping(bytes32 => uint256) public adminSignatureCount;
    
    function submitAdminAction(bytes32 actionHash, bytes memory signature) external onlyAdmin {
        require(!adminSignatures[actionHash][msg.sender], "Already signed");
        adminSignatures[actionHash][msg.sender] = true;
        adminSignatureCount[actionHash]++;
    }
    
    function executeAdminAction(bytes32 actionHash, bytes memory action) external {
        require(adminSignatureCount[actionHash] >= REQUIRED_ADMINS, "Insufficient signatures");
        // Execute admin action
    }
}
```

### Timelocks

```solidity
// SECURE: Timelock for admin operations
contract BridgeTimelock {
    uint256 public constant TIMELOCK_DURATION = 2 days;
    
    mapping(bytes32 => uint256) public queuedOperations;
    
    function queueOperation(bytes32 opHash) external onlyAdmin {
        queuedOperations[opHash] = block.timestamp + TIMELOCK_DURATION;
    }
    
    function executeOperation(bytes32 opHash) external onlyAdmin {
        require(block.timestamp >= queuedOperations[opHash], "Timelock active");
        // Execute operation
    }
}
```

---

## Known Bridge Exploits

### Wormhole (2022)

| Field | Value |
|-------|-------|
| **Loss** | $326M |
| **Root Cause** | Signature verification bug |
| **Category** | Authentication |

**Lessons:**
- Signature verification must be thorough
- Use well-audited libraries
- Implement comprehensive signature checks

### Ronin Bridge (2022)

| Field | Value |
|-------|-------|
| **Loss** | $625M |
| **Root Cause** | Access control (5/9 multisig) |
| **Category** | Access Control |

**Lessons:**
- 5/9 multisig is insufficient
- Use higher threshold (8/15)
- Distribute validators across jurisdictions

### Nomad Bridge (2022)

| Field | Value |
|-------|-------|
| **Loss** | $190M |
| **Root Cause** | Initialization bug |
| **Category** | Logic |

**Lessons:**
- Initialization bugs can be catastrophic
- Use well-tested bridge implementations
- Implement message replay protection

### Multichain (2023)

| Field | Value |
|-------|-------|
| **Loss** | $130M |
| **Root Cause** | Access control |
| **Category** | Access Control |

**Lessons:**
- Admin keys must be stored securely
- Use multi-signature wallets
- Implement timelocks for admin operations

### Poly Network (2021)

| Field | Value |
|-------|-------|
| **Loss** | $611M |
| **Root Cause** | Access control |
| **Category** | Access Control |

**Lessons:**
- Admin keys must be stored securely
- Use multi-signature wallets
- Implement timelocks for admin operations

### Harmony Bridge (2022)

| Field | Value |
|-------|-------|
| **Loss** | $100M |
| **Root Cause** | Access control (2/5 multisig) |
| **Category** | Access Control |

**Lessons:**
- 2/5 multisig is insufficient
- Use higher threshold (8/15)
- Distribute validators across jurisdictions

---

## Bridge Security Checklist

### Architecture
- [ ] Architecture type identified
- [ ] Trust boundaries mapped
- [ ] Asset flows documented
- [ ] Liquidity requirements assessed

### Validator Set
- [ ] Validator count adequate
- [ ] Collusion threshold appropriate
- [ ] Key management secure
- [ ] Jurisdiction distribution
- [ ] Key rotation implemented

### Message Verification
- [ ] Signature scheme secure
- [ ] Replay protection implemented
- [ ] Message integrity verified
- [ ] Chain ID included
- [ ] Contract address included

### Liquidity
- [ ] Asset backing verified
- [ ] Pool depth adequate
- [ ] Withdrawal capacity sufficient
- [ ] Daily limits implemented
- [ ] Emergency liquidity mechanisms

### Admin Security
- [ ] Multi-sig implemented
- [ ] Timelock implemented
- [ ] Admin keys secured
- [ ] Upgrade mechanism secure
- [ ] Emergency pause functionality

### Monitoring
- [ ] Real-time monitoring
- [ ] Alert thresholds configured
- [ ] Incident response plan
- [ ] Insurance fund adequate
