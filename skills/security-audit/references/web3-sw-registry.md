# SWC Registry Reference

Smart Contract Weakness Classification (SWC) Registry — comprehensive reference for all 37+ entries organized by category.

## Table of Contents

- [Access Control](#access-control)
  - [SWC-100: Function Default Visibility](#swc-100-function-default-visibility)
  - [SWC-105: Unprotected Ether Withdrawal](#swc-105-unprotected-ether-withdrawal)
  - [SWC-106: Unprotected SELFDESTRUCT Instruction](#swc-106-unprotected-selfdestruct-instruction)
  - [SWC-107: Reentrancy](#swc-107-reentrancy)
  - [SWC-108: State Variable Default Visibility](#swc-108-state-variable-default-visibility)
  - [SWC-115: Authorization through tx.origin](#swc-115-authorization-through-txorigin)
  - [SWC-120: Weak Sources of Randomness from Chain Attributes](#swc-120-weak-sources-of-randomness-from-chain-attributes)
- [Arithmetic](#arithmetic)
  - [SWC-101: Integer Overflow and Underflow](#swc-101-integer-overflow-and-underflow)
  - [SWC-134: Message call with hardcoded gas amount](#swc-134-message-call-with-hardcoded-gas-amount)
- [Authentication](#authentication)
  - [SWC-114: Transaction Order Dependence](#swc-114-transaction-order-dependence)
  - [SWC-121: Missing Protection against Signature Replay Attacks](#swc-121-missing-protection-against-signature-replay-attacks)
- [Logic](#logic)
  - [SWC-110: Assert Violation](#swc-110-assert-violation)
  - [SWC-112: Delegatecall to Untrusted Callee](#swc-112-delegatecall-to-untrusted-callee)
  - [SWC-113: DoS with Failed Call](#swc-113-dos-with-failed-call)
  - [SWC-116: Timestamp Dependence](#swc-116-timestamp-dependence)
  - [SWC-117: Signature Malleability](#swc-117-signature-malleability)
  - [SWC-118: Incorrect Constructor Name](#swc-118-incorrect-constructor-name)
  - [SWC-119: Shadowing State Variables](#swc-119-shadowing-state-variables)
  - [SWC-122: Lack of Proper Signature Verification](#swc-122-lack-of-proper-signature-verification)
  - [SWC-123: Requirement Violation](#swc-123-requirement-violation)
  - [SWC-124: Write to Arbitrary Storage Location](#swc-124-write-to-arbitrary-storage-location)
  - [SWC-125: Incorrect Inheritance Order](#swc-125-incorrect-inheritance-order)
  - [SWC-126: Insufficient Gas Griefing](#swc-126-insufficient-gas-griefing)
  - [SWC-127: Arbitrary Jump with Function Type Variable](#swc-127-arbitrary-jump-with-function-type-variable)
  - [SWC-128: DoS with Block Gas Limit](#swc-128-dos-with-block-gas-limit)
  - [SWC-129: Typographical Error](#swc-129-typographical-error)
  - [SWC-130: Right-To-Left-Override Control Character](#swc-130-right-to-left-override-control-character)
  - [SWC-131: Presence of Unused Variables](#swc-131-presence-of-unused-variables)
  - [SWC-132: Unexpected Ether Balance](#swc-132-unexpected-ether-balance)
  - [SWC-133: Hash Collisions with Multiple Variable Length Arguments](#swc-133-hash-collisions-with-multiple-variable-length-arguments)
  - [SWC-134: Message Call with Hardcoded Gas Amount](#swc-134-message-call-with-hardcoded-gas-amount-1)
  - [SWC-135: Code With No Effects](#swc-135-code-with-no-effects)
  - [SWC-136: Unencrypted Private Data On-Chain](#swc-136-unencrypted-private-data-on-chain)
- [Summary Table](#summary-table)

---

## Access Control

### SWC-100: Function Default Visibility

**Description:** Functions without explicit visibility specifiers default to `public` in Solidity, allowing anyone to call them.

**CWE Mapping:** CWE-749 (Exposed Dangerous Method or Function)

**Code Example:**
```solidity
// VULNERABLE: Function defaults to public
function setOwner(address _newOwner) {
    owner = _newOwner;
}

// SECURE: Explicit visibility
function setOwner(address _newOwner) external onlyOwner {
    owner = _newOwner;
}
```

**Remediation:** Always specify function visibility (`public`, `external`, `internal`, `private`).

---

### SWC-105: Unprotected Ether Withdrawal

**Description:** An unprotected function that withdraws Ether allows anyone to drain the contract's balance.

**CWE Mapping:** CWE-862 (Missing Authorization)

**Code Example:**
```solidity
// VULNERABLE: No access control on withdrawal
function withdraw() external {
    payable(msg.sender).transfer(address(this).balance);
}

// SECURE: Owner-only withdrawal
function withdraw() external onlyOwner {
    payable(msg.sender).transfer(address(this).balance);
}
```

**Remediation:** Use `onlyOwner` or role-based access control on all withdrawal functions.

---

### SWC-106: Unprotected SELFDESTRUCT Instruction

**Description:** An unprotected `selfdestruct` allows anyone to destroy the contract.

**CWE Mapping:** CWE-862 (Missing Authorization)

**Code Example:**
```solidity
// VULNERABLE: Anyone can destroy the contract
function kill() external {
    selfdestruct(payable(msg.sender));
}

// SECURE: Owner-only destruction
function kill() external onlyOwner {
    selfdestruct(payable(msg.sender));
}
```

**Remediation:** Protect `selfdestruct` with access control. Consider using `pause` instead.

---

### SWC-107: Reentrancy

**Description:** A function makes an external call to an untrusted contract before updating its state, allowing the callee to reenter the function.

**CWE Mapping:** CWE-841 (Improper Enforcement of Behavioral Workflow)

**Code Example:**
```solidity
// VULNERABLE: State update after external call
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] -= amount;  // Too late!
}

// SECURE: Checks-Effects-Interactions
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}
```

**Remediation:** Follow checks-effects-interactions pattern. Use `nonReentrant` modifier.

---

### SWC-108: State Variable Default Visibility

**Description:** State variables without explicit visibility default to `internal`, but explicit visibility is recommended for clarity.

**CWE Mapping:** CWE-749 (Exposed Dangerous Method or Function)

**Code Example:**
```solidity
// VULNERABLE: Implicit internal visibility
uint256 totalSupply;  // Defaults to internal

// SECURE: Explicit visibility
uint256 public totalSupply;
```

**Remediation:** Always specify state variable visibility explicitly.

---

### SWC-115: Authorization through tx.origin

**Description:** Using `tx.origin` for authorization is vulnerable to phishing attacks.

**CWE Mapping:** CWE-345 (Insufficient Verification of Data Authenticity)

**Code Example:**
```solidity
// VULNERABLE: tx.origin can be spoofed
function withdraw() external {
    require(msg.sender == tx.origin, "Only EOA");
    payable(msg.sender).transfer(address(this).balance);
}

// SECURE: Use msg.sender
function withdraw() external {
    require(msg.sender == owner, "Only owner");
    payable(msg.sender).transfer(address(this).balance);
}
```

**Remediation:** Never use `tx.origin` for authorization. Use `msg.sender`.

---

### SWC-120: Weak Sources of Randomness from Chain Attributes

**Description:** Using block timestamps, block numbers, or other chain attributes for randomness is predictable by miners/validators.

**CWE Mapping:** CWE-330 (Use of Insufficiently Random Values)

**Code Example:**
```solidity
// VULNERABLE: Predictable randomness
function getRandom() external view returns (uint256) {
    return uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));
}

// SECURE: Use Chainlink VRF
function requestRandomness() external {
    requestId = COORDINATOR.requestRandomness(
        keyHash,
        subscriptionId,
        requestConfirmations,
        callbackGasLimit,
        numWords
    );
}
```

**Remediation:** Use Chainlink VRF or commit-reveal schemes for randomness.

---

## Arithmetic

### SWC-101: Integer Overflow and Underflow

**Description:** Arithmetic operations can overflow or underflow in Solidity < 0.8.0, leading to unexpected behavior.

**CWE Mapping:** CWE-190 (Integer Overflow or Wraparound)

**Code Example:**
```solidity
// VULNERABLE: No overflow protection (Solidity < 0.8.0)
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;  // Underflow
    balances[to] += amount;          // Overflow
}

// SECURE: Use Solidity >= 0.8.0 or SafeMath
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;  // Reverts on underflow
    balances[to] += amount;          // Reverts on overflow
}
```

**Remediation:** Use Solidity >= 0.8.0 (built-in overflow checks) or OpenZeppelin SafeMath.

---

### SWC-134: Message call with hardcoded gas amount

**Description:** Using hardcoded gas amounts for external calls can lead to out-of-gas errors.

**CWE Mapping:** CWE-670 (Always-Incorrect Control Flow Implementation)

**Code Example:**
```solidity
// VULNERABLE: Hardcoded gas
(bool success, ) = msg.sender.call{value: amount, gas: 2300}("");

// SECURE: Forward all gas
(bool success, ) = msg.sender.call{value: amount}("");
```

**Remediation:** Avoid hardcoded gas amounts. Forward all gas or use `call` with appropriate gas.

---

## Authentication

### SWC-114: Transaction Order Dependence

**Description:** The outcome of a transaction depends on the order in which it is mined, leading to front-running vulnerabilities.

**CWE Mapping:** CWE-362 (Concurrent Execution using Shared Resource)

**Code Example:**
```solidity
// VULNERABLE: Front-running possible
function buyToken() external payable {
    uint256 tokenAmount = msg.value * tokenPrice;
    token.transfer(msg.sender, tokenAmount);
}

// SECURE: Commit-reveal scheme
function commit(bytes32 hash) external {
    commits[msg.sender] = hash;
}

function reveal(uint256 amount, bytes32 salt) external {
    require(keccak256(abi.encodePacked(amount, salt)) == commits[msg.sender]);
    // Process purchase
}
```

**Remediation:** Use commit-reveal schemes or batch auctions to prevent front-running.

---

### SWC-121: Missing Protection against Signature Replay Attacks

**Description:** Signatures can be replayed across different chains or contracts if not properly protected.

**CWE Mapping:** CWE-294 (Authentication Capture by Replay)

**Code Example:**
```solidity
// VULNERABLE: No replay protection
function transferWithSignature(address to, uint256 amount, bytes memory signature) external {
    bytes32 hash = keccak256(abi.encodePacked(to, amount));
    address signer = ECDSA.recover(hash, signature);
    require(signer == owner);
    // Transfer
}

// SECURE: Include chain ID and contract address
function transferWithSignature(address to, uint256 amount, bytes memory signature) external {
    bytes32 hash = keccak256(abi.encodePacked(
        block.chainid,
        address(this),
        to,
        amount,
        nonces[signer]++
    ));
    address signer = ECDSA.recover(hash, signature);
    require(signer == owner);
    // Transfer
}
```

**Remediation:** Include chain ID, contract address, and nonce in signature hash.

---

## Logic

### SWC-110: Assert Violation

**Description:** Using `assert()` for input validation can lead to unexpected behavior as it consumes all gas.

**CWE Mapping:** CWE-617 (Reachable Assertion)

**Code Example:**
```solidity
// VULNERABLE: assert consumes all gas
function transfer(address to, uint256 amount) external {
    assert(balances[msg.sender] >= amount);  // Consumes all gas on failure
    balances[msg.sender] -= amount;
    balances[to] += amount;
}

// SECURE: Use require for input validation
function transfer(address to, uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

**Remediation:** Use `require()` for input validation. Use `assert()` only for invariants.

---

### SWC-112: Delegatecall to Untrusted Callee

**Description:** Using `delegatecall` to an untrusted contract can lead to storage corruption.

**CWE Mapping:** CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

**Code Example:**
```solidity
// VULNERABLE: delegatecall to untrusted contract
function execute(address target, bytes memory data) external {
    (bool success, ) = target.delegatecall(data);
    require(success);
}

// SECURE: Whitelist allowed targets
mapping(address => bool) public approvedTargets;

function execute(address target, bytes memory data) external onlyOwner {
    require(approvedTargets[target], "Target not approved");
    (bool success, ) = target.delegatecall(data);
    require(success);
}
```

**Remediation:** Never `delegatecall` to untrusted contracts. Use a whitelist.

---

### SWC-113: DoS with Failed Call

**Description:** External calls that fail can cause denial of service if not handled properly.

**CWE Mapping:** CWE-703 (Improper Check or Handling of Exceptional Conditions)

**Code Example:**
```solidity
// VULNERABLE: Failed call causes DoS
function distribute(address[] memory recipients) external {
    for (uint i = 0; i < recipients.length; i++) {
        (bool success, ) = recipients[i].call{value: 1 ether}("");
        require(success);  // One failure blocks all
    }
}

// SECURE: Pull over push pattern
mapping(address => uint256) public pendingWithdrawals;

function distribute(address[] memory recipients) external {
    for (uint i = 0; i < recipients.length; i++) {
        pendingWithdrawals[recipients[i]] += 1 ether;
    }
}

function withdraw() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}
```

**Remediation:** Use pull-over-push pattern for external calls.

---

### SWC-116: Timestamp Dependence

**Description:** Using block timestamps for critical logic is vulnerable to miner manipulation.

**CWE Mapping:** CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

**Code Example:**
```solidity
// VULNERABLE: Timestamp-based logic
function isLockPeriodOver() public view returns (bool) {
    return block.timestamp > lockPeriod;  // Miner can manipulate
}

// SECURE: Use block numbers or oracle
function isLockPeriodOver() public view returns (bool) {
    return block.number > lockBlockNumber;  // Less manipulable
}
```

**Remediation:** Use block numbers instead of timestamps for critical logic.

---

### SWC-117: Signature Malleability

**Description:** ECDSA signatures can be malleated, allowing different valid signatures for the same message.

**CWE Mapping:** CWE-345 (Insufficient Verification of Data Authenticity)

**Code Example:**
```solidity
// VULNERABLE: No malleability check
function verifySignature(bytes32 hash, bytes memory signature) internal view returns (bool) {
    address signer = ECDSA.recover(hash, signature);
    return signer == owner;
}

// SECURE: Use OpenZeppelin ECDSA library
function verifySignature(bytes32 hash, bytes memory signature) internal view returns (bool) {
    return ECDSA.recover(hash, signature) == owner;
}
```

**Remediation:** Use OpenZeppelin's ECDSA library which handles malleability.

---

### SWC-118: Incorrect Constructor Name

**Description:** Constructor name mismatch in old Solidity versions can leave the contract uninitialized.

**CWE Mapping:** CWE-665 (Improper Initialization)

**Code Example:**
```solidity
// VULNERABLE: Constructor name mismatch (Solidity < 0.4.22)
contract Token {
    address public owner;
    
    function Token() public {  // Old constructor syntax
        owner = msg.sender;
    }
}

// SECURE: Use constructor keyword
contract Token {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
}
```

**Remediation:** Use `constructor` keyword. Ensure compiler version >= 0.4.22.

---

### SWC-119: Shadowing State Variables

**Description:** State variables can be shadowed by local variables or in inherited contracts.

**CWE Mapping:** CWE-710 (Improper Adherence to Coding Standards)

**Code Example:**
```solidity
// VULNERABLE: Shadowing in inherited contract
contract Base {
    uint256 public totalSupply;
}

contract Derived is Base {
    uint256 public totalSupply;  // Shadows Base.totalSupply!
}

// SECURE: Use different names or override
contract Derived is Base {
    uint256 public derivedTotalSupply;
}
```

**Remediation:** Avoid shadowing state variables. Use distinct names.

---

### SWC-122: Lack of Proper Signature Verification

**Description:** Missing or improper signature verification allows unauthorized actions.

**CWE Mapping:** CWE-345 (Insufficient Verification of Data Authenticity)

**Code Example:**
```solidity
// VULNERABLE: No signature verification
function execute(address to, uint256 amount) external {
    // No signature check!
    token.transfer(to, amount);
}

// SECURE: Verify signature
function execute(address to, uint256 amount, bytes memory signature) external {
    bytes32 hash = keccak256(abi.encodePacked(to, amount));
    address signer = ECDSA.recover(hash, signature);
    require(signer == owner, "Invalid signature");
    token.transfer(to, amount);
}
```

**Remediation:** Always verify signatures for sensitive operations.

---

### SWC-123: Requirement Violation

**Description:** Missing requirement checks can lead to unexpected behavior.

**CWE Mapping:** CWE-617 (Reachable Assertion)

**Code Example:**
```solidity
// VULNERABLE: Missing requirement
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;
    balances[to] += amount;
}

// SECURE: Add requirement checks
function transfer(address to, uint256 amount) external {
    require(to != address(0), "Invalid address");
    require(amount > 0, "Invalid amount");
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

**Remediation:** Add requirement checks for all critical operations.

---

### SWC-124: Write to Arbitrary Storage Location

**Description:** Writing to arbitrary storage locations can corrupt contract state.

**CWE Mapping:** CWE-787 (Out-of-bounds Write)

**Code Example:**
```solidity
// VULNERABLE: Arbitrary storage write
function writeStorage(uint256 slot, bytes32 value) external {
    assembly {
        sstore(slot, value)  // Can overwrite any storage!
    }
}

// SECURE: Use structured storage
mapping(uint256 => bytes32) public data;

function writeData(uint256 key, bytes32 value) external {
    data[key] = value;  // Controlled write
}
```

**Remediation:** Never allow arbitrary storage writes. Use structured storage.

---

### SWC-125: Incorrect Inheritance Order

**Description:** Incorrect inheritance order can lead to unexpected behavior in Solidity's linearization.

**CWE Mapping:** CWE-665 (Improper Initialization)

**Code Example:**
```solidity
// VULNERABLE: Wrong inheritance order
contract Token is ERC20, Ownable {
    // Ownable's constructor may not be called correctly
}

// SECURE: Correct inheritance order
contract Token is Ownable, ERC20 {
    // Ownable is initialized first
}
```

**Remediation:** Order inheritance from most base to most derived.

---

### SWC-126: Insufficient Gas Griefing

**Description:** An attacker can cause a transaction to run out of gas by providing insufficient gas.

**CWE Mapping:** CWE-400 (Uncontrolled Resource Consumption)

**Code Example:**
```solidity
// VULNERABLE: Gas griefing possible
function processBatch(address[] memory users) external {
    for (uint i = 0; i < users.length; i++) {
        _process(users[i]);  // Can be griefed
    }
}

// SECURE: Process in batches
function processBatch(address[] memory users, uint256 batchSize) external {
    uint256 end = Math.min(processedIndex + batchSize, users.length);
    for (uint i = processedIndex; i < end; i++) {
        _process(users[i]);
    }
    processedIndex = end;
}
```

**Remediation:** Process large operations in batches.

---

### SWC-127: Arbitrary Jump with Function Type Variable

**Description:** Using function type variables for jumps can lead to arbitrary code execution.

**CWE Mapping:** CWE-843 (Type Confusion)

**Code Example:**
```solidity
// VULNERABLE: Arbitrary jump
function execute(function() external callback) external {
    callback();  // Can call any function!
}

// SECURE: Use interface
function execute(IERC20 token) external {
    token.transfer(msg.sender, 100);  // Controlled call
}
```

**Remediation:** Use interfaces instead of function type variables.

---

### SWC-128: DoS with Block Gas Limit

**Description:** Transactions that exceed the block gas limit can cause denial of service.

**CWE Mapping:** CWE-400 (Uncontrolled Resource Consumption)

**Code Example:**
```solidity
// VULNERABLE: Can exceed block gas limit
function processAll() external {
    for (uint i = 0; i < allUsers.length; i++) {
        _process(allUsers[i]);  // May exceed gas limit
    }
}

// SECURE: Process in batches
function processBatch(uint256 start, uint256 end) external {
    for (uint i = start; i < end; i++) {
        _process(allUsers[i]);
    }
}
```

**Remediation:** Process large operations in batches.

---

### SWC-129: Typographical Error

**Description:** Typographical errors in variable names can lead to unexpected behavior.

**CWE Mapping:** CWE-670 (Always-Incorrect Control Flow Implementation)

**Code Example:**
```solidity
// VULNERABLE: Typo in variable name
uint256 public totalSupply;
uint256 public totalSuppply;  // Typo!

function mint(uint256 amount) external {
    totalSuppply += amount;  // Updates wrong variable!
}

// SECURE: Use consistent naming
uint256 public totalSupply;

function mint(uint256 amount) external {
    totalSupply += amount;
}
```

**Remediation:** Use consistent naming conventions. Enable compiler warnings.

---

### SWC-130: Right-To-Left-Override Control Character

**Description:** Unicode control characters can be used to hide malicious code.

**CWE Mapping:** CWE-102 (Stray Visual Text)

**Code Example:**
```solidity
// VULNERABLE: Hidden character
function transfer(address to, uint256 amount) external {
    // Hidden U+202E character reverses text direction
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    balances[to] += amount;
}

// SECURE: Use ASCII only
function transfer(address to, uint256 amount) external {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

**Remediation:** Use ASCII only. Enable linter warnings for non-ASCII characters.

---

### SWC-131: Presence of Unused Variables

**Description:** Unused variables can indicate bugs or dead code.

**CWE Mapping:** CWE-563 (Assignment to Variable without Use)

**Code Example:**
```solidity
// VULNERABLE: Unused variable
function transfer(address to, uint256 amount) external {
    uint256 unusedVar = 100;  // Never used
    balances[msg.sender] -= amount;
    balances[to] += amount;
}

// SECURE: Remove unused variables
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

**Remediation:** Remove unused variables. Enable compiler warnings.

---

### SWC-132: Unexpected Ether Balance

**Description:** Contracts that can receive Ether without proper handling can lead to locked funds.

**CWE Mapping:** CWE-843 (Type Confusion)

**Code Example:**
```solidity
// VULNERABLE: No way to receive Ether
contract Token {
    // No receive() or fallback() function
    // Ether sent to this contract is locked
}

// SECURE: Handle Ether properly
contract Token {
    receive() external payable {
        // Handle incoming Ether
    }
    
    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
```

**Remediation:** Implement `receive()` or `fallback()` functions. Provide withdrawal mechanism.

---

### SWC-133: Hash Collisions with Multiple Variable Length Arguments

**Description:** abi.encodePacked can produce hash collisions with multiple variable-length arguments.

**CWE Mapping:** CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)

**Code Example:**
```solidity
// VULNERABLE: Hash collision possible
function hashData(string memory a, string memory b) external pure returns (bytes32) {
    return keccak256(abi.encodePacked(a, b));
    // "ab" + "c" == "a" + "bc" — same hash!
}

// SECURE: Use abi.encode
function hashData(string memory a, string memory b) external pure returns (bytes32) {
    return keccak256(abi.encode(a, b));
}
```

**Remediation:** Use `abi.encode` instead of `abi.encodePacked` for multiple arguments.

---

### SWC-134: Message Call with Hardcoded Gas Amount

**Description:** Using hardcoded gas amounts for external calls can lead to out-of-gas errors.

**CWE Mapping:** CWE-670 (Always-Incorrect Control Flow Implementation)

**Code Example:**
```solidity
// VULNERABLE: Hardcoded gas
(bool success, ) = msg.sender.call{value: amount, gas: 2300}("");

// SECURE: Forward all gas
(bool success, ) = msg.sender.call{value: amount}("");
```

**Remediation:** Avoid hardcoded gas amounts.

---

### SWC-135: Code With No Effects

**Description:** Code that has no effects can indicate bugs or dead code.

**CWE Mapping:** CWE-1059 (Incomplete Documentation)

**Code Example:**
```solidity
// VULNERABLE: No effect
function transfer(address to, uint256 amount) external {
    balances[msg.sender] - amount;  // Missing assignment!
    balances[to] + amount;          // Missing assignment!
}

// SECURE: Proper assignment
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

**Remediation:** Ensure all operations have effects. Enable compiler warnings.

---

### SWC-136: Unencrypted Private Data On-Chain

**Description:** Private data stored on-chain is publicly visible.

**CWE Mapping:** CWE-311 (Missing Encryption of Sensitive Data)

**Code Example:**
```solidity
// VULNERABLE: Private data on-chain
contract Voting {
    mapping(address => bool) public hasVoted;  // Publicly visible!
    mapping(address => uint256) public votes;   // Publicly visible!
}

// SECURE: Use commit-reveal or off-chain storage
contract Voting {
    mapping(address => bytes32) public commitments;
    
    function commit(bytes32 hash) external {
        commitments[msg.sender] = hash;
    }
    
    function reveal(uint256 vote, bytes32 salt) external {
        require(keccak256(abi.encodePacked(vote, salt)) == commitments[msg.sender]);
        // Process vote
    }
}
```

**Remediation:** Use commit-reveal schemes or off-chain storage for private data.

---

## Summary Table

| SWC ID | Title | Category | CWE |
|--------|-------|----------|-----|
| SWC-100 | Function Default Visibility | Access Control | CWE-749 |
| SWC-101 | Integer Overflow and Underflow | Arithmetic | CWE-190 |
| SWC-105 | Unprotected Ether Withdrawal | Access Control | CWE-862 |
| SWC-106 | Unprotected SELFDESTRUCT | Access Control | CWE-862 |
| SWC-107 | Reentrancy | Access Control | CWE-841 |
| SWC-108 | State Variable Default Visibility | Access Control | CWE-749 |
| SWC-110 | Assert Violation | Logic | CWE-617 |
| SWC-112 | Delegatecall to Untrusted Callee | Logic | CWE-829 |
| SWC-113 | DoS with Failed Call | Logic | CWE-703 |
| SWC-114 | Transaction Order Dependence | Authentication | CWE-362 |
| SWC-115 | Authorization through tx.origin | Access Control | CWE-345 |
| SWC-116 | Timestamp Dependence | Logic | CWE-829 |
| SWC-117 | Signature Malleability | Logic | CWE-345 |
| SWC-118 | Incorrect Constructor Name | Logic | CWE-665 |
| SWC-119 | Shadowing State Variables | Logic | CWE-710 |
| SWC-120 | Weak Sources of Randomness | Access Control | CWE-330 |
| SWC-121 | Missing Protection against Signature Replay | Authentication | CWE-294 |
| SWC-122 | Lack of Proper Signature Verification | Authentication | CWE-345 |
| SWC-123 | Requirement Violation | Logic | CWE-617 |
| SWC-124 | Write to Arbitrary Storage Location | Logic | CWE-787 |
| SWC-125 | Incorrect Inheritance Order | Logic | CWE-665 |
| SWC-126 | Insufficient Gas Griefing | Logic | CWE-400 |
| SWC-127 | Arbitrary Jump with Function Type Variable | Logic | CWE-843 |
| SWC-128 | DoS with Block Gas Limit | Logic | CWE-400 |
| SWC-129 | Typographical Error | Logic | CWE-670 |
| SWC-130 | Right-To-Left-Override Control Character | Logic | CWE-102 |
| SWC-131 | Presence of Unused Variables | Logic | CWE-563 |
| SWC-132 | Unexpected Ether Balance | Logic | CWE-843 |
| SWC-133 | Hash Collisions with Multiple Variable Length Arguments | Logic | CWE-327 |
| SWC-134 | Message Call with Hardcoded Gas Amount | Arithmetic | CWE-670 |
| SWC-135 | Code With No Effects | Logic | CWE-1059 |
| SWC-136 | Unencrypted Private Data On-Chain | Logic | CWE-311 |
