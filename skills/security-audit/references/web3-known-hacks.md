# Major DeFi Exploits and Lessons Learned

> **Last updated: 2024.** For the most recent exploits, consult current security news sources.

Comprehensive reference of major DeFi exploits, their root causes, attack paths, and prevention measures.

## Table of Contents

- [The DAO (2016)](#the-dao-2016)
  - [Attack Path](#attack-path)
  - [Lessons Learned](#lessons-learned)
  - [Prevention](#prevention)
- [Parity Wallet (2017)](#parity-wallet-2017)
  - [Attack Path](#attack-path-1)
  - [Lessons Learned](#lessons-learned-1)
  - [Prevention](#prevention-1)
- [Parity Wallet 2 (2017)](#parity-wallet-2-2017)
  - [Attack Path](#attack-path-2)
  - [Lessons Learned](#lessons-learned-2)
  - [Prevention](#prevention-2)
- [Bancor (2018)](#bancor-2018)
  - [Attack Path](#attack-path-3)
  - [Lessons Learned](#lessons-learned-3)
  - [Prevention](#prevention-3)
- [SpankChain (2018)](#spankchain-2018)
  - [Attack Path](#attack-path-4)
  - [Lessons Learned](#lessons-learned-4)
  - [Prevention](#prevention-4)
- [EOSBet (2018)](#eosbet-2018)
  - [Attack Path](#attack-path-5)
  - [Lessons Learned](#lessons-learned-5)
  - [Prevention](#prevention-5)
- [ChainSwap (2020)](#chainswap-2020)
  - [Attack Path](#attack-path-6)
  - [Lessons Learned](#lessons-learned-6)
  - [Prevention](#prevention-6)
- [Akropolis (2020)](#akropolis-2020)
  - [Attack Path](#attack-path-7)
  - [Lessons Learned](#lessons-learned-7)
  - [Prevention](#prevention-7)
- [Harvest Finance (2020)](#harvest-finance-2020)
  - [Attack Path](#attack-path-8)
  - [Lessons Learned](#lessons-learned-8)
  - [Prevention](#prevention-8)
- [CREAM Finance (2021)](#cream-finance-2021)
  - [Attack Path](#attack-path-9)
  - [Lessons Learned](#lessons-learned-9)
  - [Prevention](#prevention-9)
- [Compound (2021)](#compound-2021)
  - [Attack Path](#attack-path-10)
  - [Lessons Learned](#lessons-learned-10)
  - [Prevention](#prevention-10)
- [Beanstalk (2022)](#beanstalk-2022)
  - [Attack Path](#attack-path-11)
  - [Lessons Learned](#lessons-learned-11)
  - [Prevention](#prevention-11)
- [Wormhole (2022)](#wormhole-2022)
  - [Attack Path](#attack-path-12)
  - [Lessons Learned](#lessons-learned-12)
  - [Prevention](#prevention-12)
- [Ronin Bridge (2022)](#ronin-bridge-2022)
  - [Attack Path](#attack-path-13)
  - [Lessons Learned](#lessons-learned-13)
  - [Prevention](#prevention-13)
- [Nomad Bridge (2022)](#nomad-bridge-2022)
  - [Attack Path](#attack-path-14)
  - [Lessons Learned](#lessons-learned-14)
  - [Prevention](#prevention-14)
- [Mango Markets (2022)](#mango-markets-2022)
  - [Attack Path](#attack-path-15)
  - [Lessons Learned](#lessons-learned-15)
  - [Prevention](#prevention-15)
- [BNB Chain (2022)](#bnb-chain-2022)
  - [Attack Path](#attack-path-16)
  - [Lessons Learned](#lessons-learned-16)
  - [Prevention](#prevention-16)
- [Curve (2023)](#curve-2023)
  - [Attack Path](#attack-path-17)
  - [Lessons Learned](#lessons-learned-17)
  - [Prevention](#prevention-17)
- [Summary Table](#summary-table)
- [Common Attack Patterns](#common-attack-patterns)
  - [Reentrancy](#reentrancy)
  - [Oracle Manipulation](#oracle-manipulation)
  - [Access Control](#access-control)
  - [Flash Loan Attacks](#flash-loan-attacks)
  - [Signature Verification](#signature-verification)
  - [Initialization Bugs](#initialization-bugs)

---

## The DAO (2016)

| Field | Value |
|-------|-------|
| **Date** | June 2016 |
| **Loss** | $60M (3.6M ETH) |
| **Root Cause** | Reentrancy |
| **Category** | Access Control |

### Attack Path

1. Attacker called `splitDAO()` function
2. Function sent ETH via `call.value()` before updating balance
3. Attacker's fallback function reentered `splitDAO()`
4. Repeated withdrawal drained funds

### Lessons Learned

- Always follow checks-effects-interactions pattern
- External calls can reenter your contract
- State updates must happen before external calls

### Prevention

```solidity
// SECURE: Checks-Effects-Interactions
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount);  // Check
    balances[msg.sender] -= amount;           // Effect
    (bool success, ) = msg.sender.call{value: amount}("");  // Interaction
    require(success);
}
```

---

## Parity Wallet (2017)

| Field | Value |
|-------|-------|
| **Date** | July 2017 |
| **Loss** | $150M (150K ETH) |
| **Root Cause** | Unprotected delegatecall |
| **Category** | Access Control |

### Attack Path

1. Attacker called `initWallet()` on library contract
2. Library used `delegatecall` to execute code in wallet context
3. Attacker became owner of wallet
4. Attacker drained funds

### Lessons Learned

- `delegatecall` executes code in caller's context
- Never use `delegatecall` to untrusted contracts
- Library contracts must have proper access control

### Prevention

```solidity
// SECURE: Whitelist for delegatecall targets
mapping(address => bool) public approvedTargets;

function execute(address target, bytes memory data) external onlyOwner {
    require(approvedTargets[target], "Target not approved");
    (bool success, ) = target.delegatecall(data);
    require(success);
}
```

---

## Parity Wallet 2 (2017)

| Field | Value |
|-------|-------|
| **Date** | November 2017 |
| **Loss** | $30M (513K ETH) |
| **Root Cause** | Uninitialized storage pointer |
| **Category** | Logic |

### Attack Path

1. Attacker called `initWallet()` on uninitialized proxy
2. Proxy had no owner set
3. Attacker became owner
4. Attacker called `selfdestruct()` and drained funds

### Lessons Learned

- Always initialize contracts in constructor
- Use `constructor` to set initial state
- Disable implementation contract initialization

### Prevention

```solidity
// SECURE: Disable initializer in constructor
contract Implementation {
    address public owner;
    bool public initialized;
    
    constructor() {
        initialized = true;  // Disable implementation initialization
    }
    
    function initialize(address _owner) external {
        require(!initialized, "Already initialized");
        owner = _owner;
        initialized = true;
    }
}
```

---

## Bancor (2018)

| Field | Value |
|-------|-------|
| **Date** | July 2018 |
| **Loss** | $23.5M |
| **Root Cause** | Access control |
| **Category** | Access Control |

### Attack Path

1. Attacker compromised a Bancor team wallet
2. Used compromised key to call `withdrawToken()`
3. Drained tokens from exchange contract

### Lessons Learned

- Admin keys must be stored in hardware wallets
- Use multi-signature wallets for admin operations
- Implement timelocks for sensitive operations

### Prevention

```solidity
// SECURE: Multi-sig + timelock
contract AdminOperations {
    uint256 public constant TIMELOCK_DURATION = 2 days;
    
    mapping(bytes32 => uint256) public queuedOperations;
    
    function queueOperation(bytes32 opHash) external onlyMultiSig {
        queuedOperations[opHash] = block.timestamp + TIMELOCK_DURATION;
    }
    
    function executeOperation(bytes32 opHash) external onlyMultiSig {
        require(block.timestamp >= queuedOperations[opHash], "Timelock active");
        // Execute operation
    }
}
```

---

## SpankChain (2018)

| Field | Value |
|-------|-------|
| **Date** | October 2018 |
| **Loss** | $38K |
| **Root Cause** | Reentrancy |
| **Category** | Access Control |

### Attack Path

1. Attacker called `withdraw()` on payment channel
2. Function sent ETH before updating state
3. Attacker's fallback reentered `withdraw()`
4. Repeated withdrawal drained funds

### Lessons Learned

- Reentrancy is a recurring vulnerability
- Always use checks-effects-interactions
- Use reentrancy guards

### Prevention

```solidity
// SECURE: Reentrancy guard
contract ReentrancyGuard {
    bool private locked;
    
    modifier nonReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
}
```

---

## EOSBet (2018)

| Field | Value |
|-------|-------|
| **Date** | September 2018 |
| **Loss** | $200K |
| **Root Cause** | Randomness manipulation |
| **Category** | Authentication |

### Attack Path

1. Attacker predicted random number from block hash
2. Used prediction to win bets repeatedly
3. Drained contract funds

### Lessons Learned

- Block hashes are predictable
- Never use chain attributes for randomness
- Use oracle-based randomness (Chainlink VRF)

### Prevention

```solidity
// SECURE: Chainlink VRF
function requestRandomness() external {
    requestId = COORDINATOR.requestRandomness(
        keyHash,
        subscriptionId,
        requestConfirmations,
        callbackGasLimit,
        numWords
    );
}

function fulfillRandomness(uint256 requestId, uint256[] memory randomWords) internal override {
    // Use randomWords[0] for randomness
}
```

---

## ChainSwap (2020)

| Field | Value |
|-------|-------|
| **Date** | July 2020 |
| **Loss** | $800K |
| **Root Cause** | Access control |
| **Category** | Access Control |

### Attack Path

1. Attacker compromised private key
2. Used key to call admin functions
3. Drained funds from bridge contract

### Lessons Learned

- Private keys must be stored securely
- Use multi-signature wallets
- Implement timelocks for admin operations

### Prevention

```bash
# Use hardware wallets for admin keys
# Use Gnosis Safe for multi-sig
# Implement timelock contracts
```

---

## Akropolis (2020)

| Field | Value |
|-------|-------|
| **Date** | November 2020 |
| **Loss** | $2M |
| **Root Cause** | Flash loan + reentrancy |
| **Category** | Access Control |

### Attack Path

1. Attacker took flash loan
2. Used funds to manipulate pool
3. Reentered during withdrawal
4. Drained funds

### Lessons Learned

- Flash loans enable single-transaction attacks
- Reentrancy + flash loans = dangerous combination
- Use reentrancy guards on all external calls

### Prevention

```solidity
// SECURE: Reentrancy guard + checks-effects-interactions
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}
```

---

## Harvest Finance (2020)

| Field | Value |
|-------|-------|
| **Date** | October 2020 |
| **Loss** | $24M |
| **Root Cause** | Flash loan oracle manipulation |
| **Category** | Oracle |

### Attack Path

1. Attacker took flash loan
2. Manipulated Curve pool spot price
3. Harvest used spot price for valuation
4. Attacker deposited, withdrew profit, repaid loan

### Lessons Learned

- Spot prices can be manipulated with flash loans
- Use TWAP or oracle with delay
- Implement circuit breakers

### Prevention

```solidity
// SECURE: Use TWAP
function getPrice() public view returns (uint256) {
    uint256[] memory prices = new uint256[](30);
    for (uint i = 0; i < 30; i++) {
        prices[i] = oracle.getPrice(block.timestamp - i * 12);
    }
    return median(prices);
}
```

---

## CREAM Finance (2021)

| Field | Value |
|-------|-------|
| **Date** | October 2021 |
| **Loss** | $130M |
| **Root Cause** | Flash loan + price manipulation |
| **Category** | Oracle |

### Attack Path

1. Attacker took flash loan
2. Manipulated price oracle
3. Borrowed against inflated collateral
4. Repaid loan, kept profit

### Lessons Learned

- Oracle manipulation is the #1 DeFi attack vector
- Use multiple oracle sources
- Implement price deviation checks

### Prevention

```solidity
// SECURE: Oracle deviation check
uint256 public constant MAX_DEVIATION = 5e16; // 5%

function checkOracleHealth() internal view {
    uint256 oraclePrice = getOraclePrice();
    uint256 internalPrice = getInternalPrice();
    
    uint256 deviation = oraclePrice > internalPrice 
        ? (oraclePrice - internalPrice) * 1e18 / oraclePrice
        : (internalPrice - oraclePrice) * 1e18 / internalPrice;
    
    require(deviation <= MAX_DEVIATION, "Oracle deviation too high");
}
```

---

## Compound (2021)

| Field | Value |
|-------|-------|
| **Date** | September 2021 |
| **Loss** | $140M |
| **Root Cause** | Oracle manipulation |
| **Category** | Oracle |

### Attack Path

1. Attacker manipulated COMP price oracle
2. Borrowed against inflated collateral
3. Oracle corrected, position underwater
4. Bad debt accumulated

### Lessons Learned

- Oracle manipulation can create bad debt
- Use TWAP for collateral valuation
- Implement liquidation incentives

### Prevention

```solidity
// SECURE: TWAP for collateral valuation
function getCollateralValue(address user) public view returns (uint256) {
    uint256 twapPrice = getTWAP(collateralToken, 1 hours);
    uint256 collateralAmount = getCollateralBalance(user);
    return collateralAmount * twapPrice / 1e18;
}
```

---

## Beanstalk (2022)

| Field | Value |
|-------|-------|
| **Date** | April 2022 |
| **Loss** | $182M |
| **Root Cause** | Governance attack |
| **Category** | Governance |

### Attack Path

1. Attacker took flash loan
2. Used funds to gain voting majority
3. Passed malicious proposal
4. Drained funds, repaid loan

### Lessons Learned

- Flash loans can enable governance attacks
- Use snapshot voting or delegated voting
- Implement timelock for governance

### Prevention

```solidity
// SECURE: Snapshot voting
function propose(bytes memory data) external {
    uint256 votes = token.getPastVotes(msg.sender, block.number - 1);
    require(votes >= proposalThreshold);
    // Create proposal
}
```

---

## Wormhole (2022)

| Field | Value |
|-------|-------|
| **Date** | February 2022 |
| **Loss** | $326M |
| **Root Cause** | Signature verification bug |
| **Category** | Authentication |

### Attack Path

1. Attacker exploited signature verification bug
2. Forged signature for mint function
3. Minted 120K wETH without backing
4. Bridged to Ethereum, redeemed for ETH

### Lessons Learned

- Signature verification must be thorough
- Use well-audited libraries (OpenZeppelin)
- Implement comprehensive signature checks

### Prevention

```solidity
// SECURE: Use OpenZeppelin ECDSA
function verifySignature(bytes32 hash, bytes memory signature) internal view returns (bool) {
    return ECDSA.recover(hash, signature) == owner;
}
```

---

## Ronin Bridge (2022)

| Field | Value |
|-------|-------|
| **Date** | March 2022 |
| **Loss** | $625M |
| **Root Cause** | Access control (5/9 multisig) |
| **Category** | Access Control |

### Attack Path

1. Attacker compromised 5 of 9 validator keys
2. Used compromised keys to approve withdrawals
3. Drained 173,600 ETH and 25.5M USDC

### Lessons Learned

- 5/9 multisig is insufficient for large bridges
- Use higher threshold (e.g., 8/15)
- Distribute validators across jurisdictions

### Prevention

```solidity
// SECURE: Higher threshold multisig
contract Bridge {
    uint256 public constant REQUIRED_SIGNATURES = 8;
    uint256 public constant TOTAL_VALIDATORS = 15;
    
    mapping(bytes32 => mapping(address => bool)) public signatures;
    mapping(bytes32 => uint256) public signatureCount;
    
    function submitSignature(bytes32 txHash, bytes memory signature) external onlyValidator {
        require(!signatures[txHash][msg.sender], "Already signed");
        signatures[txHash][msg.sender] = true;
        signatureCount[txHash]++;
    }
    
    function executeWithdrawal(bytes32 txHash) external {
        require(signatureCount[txHash] >= REQUIRED_SIGNATURES, "Insufficient signatures");
        // Execute withdrawal
    }
}
```

---

## Nomad Bridge (2022)

| Field | Value |
|-------|-------|
| **Date** | August 2022 |
| **Loss** | $190M |
| **Root Cause** | Initialization bug |
| **Category** | Logic |

### Attack Path

1. Attacker found uninitialized storage slot
2. Used slot to bypass message verification
3. Forged withdrawal messages
4. Drained funds

### Lessons Learned

- Initialization bugs can be catastrophic
- Use well-tested bridge implementations
- Implement message replay protection

### Prevention

```solidity
// SECURE: Proper initialization
contract Bridge {
    bytes32 public constant INITIALIZED_SLOT = 
        bytes32(uint256(keccak256('bridge.initialized')) - 1);
    
    modifier initialized() {
        require(initialized(), "Not initialized");
        _;
    }
    
    function initialize() external {
        require(!initialized(), "Already initialized");
        assembly {
            sstore(INITIALIZED_SLOT, 1)
        }
    }
}
```

---

## Mango Markets (2022)

| Field | Value |
|-------|-------|
| **Date** | October 2022 |
| **Loss** | $114M |
| **Root Cause** | Oracle manipulation |
| **Category** | Oracle |

### Attack Path

1. Attacker manipulated MNGO price oracle
2. Borrowed against inflated collateral
3. Oracle corrected, position underwater
4. Bad debt accumulated

### Lessons Learned

- Oracle manipulation can create bad debt
- Use TWAP for collateral valuation
- Implement position size limits

### Prevention

```solidity
// SECURE: Position size limits
uint256 public constant MAX_POSITION_SIZE = 1000000 * 1e18; // $1M

function openPosition(address token, uint256 size) external {
    require(size <= MAX_POSITION_SIZE, "Position too large");
    // Open position
}
```

---

## BNB Chain (2022)

| Field | Value |
|-------|-------|
| **Date** | October 2022 |
| **Loss** | $570M |
| **Root Cause** | Bridge validation bug |
| **Category** | Authentication |

### Attack Path

1. Attacker exploited bridge validation bug
2. Forged Merkle proof for withdrawal
3. Minted 2M BNB without backing
4. Bridged to other chains

### Lessons Learned

- Bridge validation must be thorough
- Use well-audited bridge implementations
- Implement Merkle proof verification

### Prevention

```solidity
// SECURE: Merkle proof verification
function verifyMerkleProof(
    bytes32 root,
    bytes32 leaf,
    bytes32[] memory proof
) internal pure returns (bool) {
    bytes32 computedHash = leaf;
    for (uint i = 0; i < proof.length; i++) {
        bytes32 proofElement = proof[i];
        if (computedHash <= proofElement) {
            computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
        } else {
            computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
        }
    }
    return computedHash == root;
}
```

---

## Curve (2023)

| Field | Value |
|-------|-------|
| **Date** | July 2023 |
| **Loss** | $62M |
| **Root Cause** | Compiler bug (Vyper) |
| **Category** | Logic |

### Attack Path

1. Attacker exploited Vyper compiler bug
2. Bug affected certain Vyper versions
3. Attacker manipulated pool state
4. Drained funds

### Lessons Learned

- Compiler bugs can affect many contracts
- Use well-tested compiler versions
- Implement emergency pause mechanisms

### Prevention

```solidity
// SECURE: Emergency pause
contract Pausable {
    bool public paused;
    
    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }
    
    function pause() external onlyOwner {
        paused = true;
    }
    
    function unpause() external onlyOwner {
        paused = false;
    }
}
```

---

## Summary Table

| Exploit | Year | Loss | Root Cause | Category |
|---------|------|------|------------|----------|
| The DAO | 2016 | $60M | Reentrancy | Access Control |
| Parity Wallet | 2017 | $150M | Unprotected delegatecall | Access Control |
| Parity Wallet 2 | 2017 | $30M | Uninitialized storage pointer | Logic |
| Bancor | 2018 | $23.5M | Access control | Access Control |
| SpankChain | 2018 | $38K | Reentrancy | Access Control |
| EOSBet | 2018 | $200K | Randomness manipulation | Authentication |
| ChainSwap | 2020 | $800K | Access control | Access Control |
| Akropolis | 2020 | $2M | Flash loan + reentrancy | Access Control |
| Harvest Finance | 2020 | $24M | Flash loan oracle manipulation | Oracle |
| CREAM Finance | 2021 | $130M | Flash loan + price manipulation | Oracle |
| Compound | 2021 | $140M | Oracle manipulation | Oracle |
| Beanstalk | 2022 | $182M | Governance attack | Governance |
| Wormhole | 2022 | $326M | Signature verification bug | Authentication |
| Ronin Bridge | 2022 | $625M | Access control (5/9 multisig) | Access Control |
| Nomad Bridge | 2022 | $190M | Initialization bug | Logic |
| Mango Markets | 2022 | $114M | Oracle manipulation | Oracle |
| BNB Chain | 2022 | $570M | Bridge validation bug | Authentication |
| Curve | 2023 | $62M | Compiler bug (Vyper) | Logic |

---

## Common Attack Patterns

### Reentrancy
- The DAO, SpankChain, Akropolis
- **Prevention:** Checks-effects-interactions, reentrancy guards

### Oracle Manipulation
- Harvest Finance, CREAM Finance, Compound, Mango Markets
- **Prevention:** TWAP, circuit breakers, multiple oracle sources

### Access Control
- Bancor, ChainSwap, Ronin Bridge
- **Prevention:** Multi-sig, timelocks, hardware wallets

### Flash Loan Attacks
- Akropolis, Harvest Finance, CREAM Finance, Beanstalk
- **Prevention:** TWAP, commit-reveal, snapshot voting

### Signature Verification
- Wormhole, BNB Chain
- **Prevention:** Use OpenZeppelin ECDSA, thorough verification

### Initialization Bugs
- Parity Wallet 2, Nomad Bridge
- **Prevention:** Constructor initialization, disable implementation init
