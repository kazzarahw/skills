# Smart Contract Audit Guide

Comprehensive guide for auditing Solidity and Vyper smart contracts. Covers methodology, vulnerability patterns, and audit procedures.

## Table of Contents

- [Audit Methodology](#audit-methodology)
  - [Phase 1: Understand](#phase-1-understand)
  - [Phase 2: Automated Analysis](#phase-2-automated-analysis)
  - [Phase 3: Manual Review](#phase-3-manual-review)
  - [Phase 4: Dynamic Analysis](#phase-4-dynamic-analysis)
  - [Phase 5: Report](#phase-5-report)
- [Trust Boundary Mapping](#trust-boundary-mapping)
- [Invariant Documentation](#invariant-documentation)
  - [Example: Lending Protocol Invariants](#example-lending-protocol-invariants)
  - [Example: AMM Invariants](#example-amm-invariants)
- [Access Control Review](#access-control-review)
  - [Missing Modifiers](#missing-modifiers)
  - [tx.origin Authentication](#txorigin-authentication)
  - [delegatecall Risks](#delegatecall-risks)
- [Reentrancy](#reentrancy)
  - [Checks-Effects-Interactions Pattern](#checks-effects-interactions-pattern)
  - [Reentrancy Guard](#reentrancy-guard)
  - [Cross-Function Reentrancy](#cross-function-reentrancy)
- [Oracle Manipulation](#oracle-manipulation)
  - [Spot Price Dependency](#spot-price-dependency)
  - [Circuit Breakers](#circuit-breakers)
- [Integer Overflow/Underflow](#integer-overflowunderflow)
  - [Pre-0.8.0 Solidity](#pre-080-solidity)
  - [Unchecked Blocks](#unchecked-blocks)
- [Flash Loan Attacks](#flash-loan-attacks)
  - [Single-Transaction Manipulation](#single-transaction-manipulation)
  - [Governance Attack](#governance-attack)
- [Upgrade Safety](#upgrade-safety)
  - [Storage Collisions](#storage-collisions)
  - [Uninitialized Proxies](#uninitialized-proxies)
- [Gas Optimization & DoS](#gas-optimization--dos)
  - [Unbounded Loops](#unbounded-loops)
  - [Block Stuffing](#block-stuffing)
- [Formal Verification](#formal-verification)
  - [Certora](#certora)
  - [Halmos](#halmos)
- [Audit Checklist](#audit-checklist)
  - [Pre-Audit](#pre-audit)
  - [Automated Analysis](#automated-analysis)
  - [Manual Review](#manual-review)
  - [Dynamic Analysis](#dynamic-analysis)
  - [Reporting](#reporting)

---

## Audit Methodology

### Phase 1: Understand

```
1.1  Contract inventory       → all contracts, their roles, ownership
1.2  Architecture mapping     → contracts, actors, trust boundaries, asset flows
1.3  External integrations    → oracles, bridges, DEXs, tokens
1.4  Invariant documentation   → what must always be true
1.5  Documentation review      → specs, docs, intended behavior
1.6  Upgrade mechanism review  → proxy patterns, admin keys, timelocks
```

**Exit criteria:** Contract inventory complete, architecture mapped, invariants documented, upgrade mechanisms assessed.

### Phase 2: Automated Analysis

```bash
# Slither — comprehensive static analysis
slither . --json results.json --exclude-optimization

# Aderyn — Rust-based analyzer
aderyn . --json output.json

# Mythril — symbolic execution
myth analyze contract.sol --execution-timeout 300

# Solhint — linting
solhint "contracts/**/*.sol"

# Semgrep — pattern matching
semgrep --config=p/smart-contracts contracts/
```

**Exit criteria:** All automated tools executed, results triaged, false positives filtered.

### Phase 3: Manual Review

Line-by-line review focusing on:

| Category | What to Look For |
|----------|-----------------|
| **Access control** | Missing modifiers, tx.origin, delegatecall risks |
| **Reentrancy** | External calls before state updates, cross-function reentrancy |
| **Oracle manipulation** | Spot price dependency, short TWAP, no circuit breakers |
| **Integer overflow** | Pre-0.8.0 Solidity, unchecked blocks |
| **Flash loan attacks** | Single-transaction manipulation, governance attacks |
| **Upgrade safety** | Storage collisions, uninitialized proxies, admin key risks |
| **Economic attacks** | Inflation attacks, donation attacks, liquidation manipulation |
| **Gas optimization** | DoS via gas limits, unbounded loops |

**Exit criteria:** All in-scope code reviewed, findings documented with line numbers.

### Phase 4: Dynamic Analysis

```bash
# Foundry fuzzing
forge test --fuzz-runs 10000

# Echidna — property-based fuzzing
echidna contract.sol --contract TestContract

# Invariant testing
forge test --match-contract InvariantTest

# Fork testing
forge test --fork-url $RPC_URL --fork-block-number N
```

**Exit criteria:** Fuzzing executed, invariants tested, edge cases covered.

### Phase 5: Hand off to report

Compilation format below; the `report` skill owns delivery. Load `report` with verified findings — never deliver from here.

Compile findings with:
- Reference ID, Title, Severity, CVSS/Impact
- CVE/CWE/SWC classification
- Description, Evidence, Business impact, Remediation
- Provenance (tool-proven/model-asserted)

---

## Trust Boundary Mapping

Identify all trust boundaries before analyzing:

```
┌─────────────────────────────────────────────────────┐
│                    EOA (User)                        │
│  Trust: None — can call any public function          │
└──────────────────────┬──────────────────────────────┘
                       │ Transaction
┌──────────────────────▼──────────────────────────────┐
│              Contract A (Entry Point)                │
│  Trust: EOA — must validate all inputs               │
│  Boundary: msg.sender, msg.value, calldata           │
└──────────────────────┬──────────────────────────────┘
                       │ External call
┌──────────────────────▼──────────────────────────────┐
│              Contract B (Dependency)                 │
│  Trust: Contract A — assumes caller is authorized    │
│  Boundary: function parameters, return values        │
└──────────────────────┬──────────────────────────────┘
                       │ Oracle query
┌──────────────────────▼──────────────────────────────┐
│              Oracle (External)                       │
│  Trust: None — can return any value                  │
│  Boundary: price feeds, random numbers               │
└─────────────────────────────────────────────────────┘
```

**Key Principle:** Every external call, oracle, and user input is a trust boundary. Map them before analyzing.

---

## Invariant Documentation

Define invariants — properties that must always hold true:

### Example: Lending Protocol Invariants

```solidity
// INV-1: Total borrowed <= total supplied
assert(totalBorrowed <= totalSupplied);

// INV-2: Sum of user balances == contract token balance
assert(sumOfUserBalances == token.balanceOf(address(this)));

// INV-3: Health factor > 1 for all positions (if not being liquidated)
assert(healthFactor > 1e18);

// INV-4: Interest rate increases with utilization
assert(highUtilizationRate > lowUtilizationRate);

// INV-5: No user can have negative balance
assert(userBalance >= 0);
```

### Example: AMM Invariants

```solidity
// INV-1: Constant product formula (x * y = k)
assert(reserveA * reserveB >= initialK);

// INV-2: LP token supply is proportional to liquidity
assert(lpTokenSupply == sqrt(reserveA * reserveB));

// INV-3: No negative reserves
assert(reserveA >= 0 && reserveB >= 0);

// INV-4: Slippage protection
assert(amountOut >= minAmountOut);
```

---

## Access Control Review

### Missing Modifiers

```solidity
// VULNERABLE: No access control
function withdraw(uint256 amount) external {
    token.transfer(msg.sender, amount);
}

// SECURE: Owner-only modifier
function withdraw(uint256 amount) external onlyOwner {
    token.transfer(msg.sender, amount);
}
```

### tx.origin Authentication

```solidity
// VULNERABLE: tx.origin can be spoofed
function withdraw() external {
    require(msg.sender == tx.origin, "Only EOA");
    // Attacker can trick this via a malicious contract
    payable(msg.sender).transfer(address(this).balance);
}

// SECURE: Use msg.sender
function withdraw() external {
    require(msg.sender == owner, "Only owner");
    payable(msg.sender).transfer(address(this).balance);
}
```

### delegatecall Risks

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

---

## Reentrancy

### Checks-Effects-Interactions Pattern

```solidity
// VULNERABLE: External call before state update
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] -= amount;  // State update AFTER external call
}

// SECURE: Checks-Effects-Interactions
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);  // Check
    balances[msg.sender] -= amount;           // Effect
    (bool success, ) = msg.sender.call{value: amount}("");  // Interaction
    require(success);
}
```

### Reentrancy Guard

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

function withdraw(uint256 amount) external nonReentrant {
    // Safe from reentrancy
}
```

### Cross-Function Reentrancy

```solidity
// VULNERABLE: State shared across functions
mapping(address => uint256) public balances;

function transfer(address to, uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = to.call{value: amount}("");  // Reentrant call
    require(success);
    balances[msg.sender] -= amount;
}

function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] = 0;
}
// Attacker can reenter transfer() during withdraw()
```

---

## Oracle Manipulation

### Spot Price Dependency

```solidity
// VULNERABLE: Using spot price from DEX
function getPrice() public view returns (uint256) {
    returnuniswapPair.getReserves().reserve0 / 
           uniswapPair.getReserves().reserve1;
}

// SECURE: Use TWAP (Time-Weighted Average Price)
function getPrice() public view returns (uint256) {
    uint256[] memory prices = new uint256[](30);
    for (uint i = 0; i < 30; i++) {
        prices[i] = oracle.getPrice(block.timestamp - i * 12);
    }
    return median(prices);
}
```

### Circuit Breakers

```solidity
// SECURE: Circuit breaker for oracle deviation
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

## Integer Overflow/Underflow

### Pre-0.8.0 Solidity

```solidity
// VULNERABLE: Solidity < 0.8.0 — no built-in overflow checks
function transfer(address to, uint256 amount) external {
    balances[msg.sender] -= amount;  // Underflow if amount > balance
    balances[to] += amount;          // Overflow if sum > type(uint256).max
}

// SECURE: Use SafeMath
using SafeMath for uint256;

function transfer(address to, uint256 amount) external {
    balances[msg.sender] = balances[msg.sender].sub(amount);
    balances[to] = balances[to].add(amount);
}
```

### Unchecked Blocks

```solidity
// VULNERABLE: Unchecked block bypasses overflow checks
function transfer(address to, uint256 amount) external {
    unchecked {
        balances[msg.sender] -= amount;  // Can underflow!
        balances[to] += amount;
    }
}

// SECURE: Only use unchecked for gas optimization when safe
function transfer(address to, uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;  // Safe due to check above
    balances[to] += amount;
}
```

---

## Flash Loan Attacks

### Single-Transaction Manipulation

```solidity
// VULNERABLE: Price can be manipulated in single transaction
function borrow(uint256 amount) external {
    uint256 price = getSpotPrice();  // Can be manipulated
    uint256 collateralValue = amount * price;
    require(collateralValue >= minCollateral);
    // Issue loan
}

// SECURE: Use TWAP or oracle with delay
function borrow(uint256 amount) external {
    uint256 price = getTWAP(1 hours);  // Cannot be manipulated in single tx
    uint256 collateralValue = amount * price;
    require(collateralValue >= minCollateral);
    // Issue loan
}
```

### Governance Attack

```solidity
// VULNERABLE: Voting power from token balance
function propose(bytes memory data) external {
    uint256 votes = token.balanceOf(msg.sender);
    require(votes >= proposalThreshold);
    // Create proposal
}

// SECURE: Use snapshot or delegated voting
function propose(bytes memory data) external {
    uint256 votes = token.getPastVotes(msg.sender, block.number - 1);
    require(votes >= proposalThreshold);
    // Create proposal
}
```

---

## Upgrade Safety

### Storage Collisions

```solidity
// VULNERABLE: Storage layout mismatch between proxy and implementation
contract Proxy {
    address public implementation;  // Slot 0
    address public admin;           // Slot 1
}

contract ImplementationV1 {
    address public owner;    // Slot 0 — collides with implementation!
    uint256 public value;    // Slot 1 — collides with admin!
}

// SECURE: Use EIP-1967 storage slots
contract Proxy {
    bytes32 private constant IMPLEMENTATION_SLOT = 
        bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1);
    bytes32 private constant ADMIN_SLOT = 
        bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1);
}
```

### Uninitialized Proxies

```solidity
// VULNERABLE: Implementation can be initialized by anyone
contract Implementation {
    address public owner;
    bool public initialized;
    
    function initialize(address _owner) external {
        require(!initialized, "Already initialized");
        owner = _owner;
        initialized = true;
    }
}

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

## Gas Optimization & DoS

### Unbounded Loops

```solidity
// VULNERABLE: Unbounded loop can cause DoS
function distributeRewards(address[] memory users) external {
    for (uint i = 0; i < users.length; i++) {
        // If users array is too large, this will run out of gas
        _transferReward(users[i]);
    }
}

// SECURE: Pull over push pattern
mapping(address => uint256) public rewards;

function claimReward() external {
    uint256 amount = rewards[msg.sender];
    require(amount > 0, "No reward");
    rewards[msg.sender] = 0;
    token.transfer(msg.sender, amount);
}
```

### Block Stuffing

```solidity
// VULNERABLE: Can be blocked by large transactions
function finalize() external {
    require(block.number >= endBlock);
    // Process all pending operations
    for (uint i = 0; i < pendingOps.length; i++) {
        _process(pendingOps[i]);
    }
}

// SECURE: Process in batches
uint256 public processedIndex;

function finalize(uint256 batchSize) external {
    require(block.number >= endBlock);
    uint256 end = Math.min(processedIndex + batchSize, pendingOps.length);
    for (uint i = processedIndex; i < end; i++) {
        _process(pendingOps[i]);
    }
    processedIndex = end;
}
```

---

## Formal Verification

### Certora

```solidora
// Certora rule: Total supply is always equal to sum of balances
rule sumOfBalancesEqualsTotalSupply(address[] users) {
    uint256 sum = 0;
    foreach (address user in users) {
        sum += balanceOf(user);
    }
    assert sum == totalSupply();
}

// Certora rule: No one can transfer more than their balance
rule transferWithinBalance(address from, address to, uint256 amount) {
    uint256 balanceBefore = balanceOf(from);
    transfer(to, amount);
    assert balanceOf(from) == balanceBefore - amount;
}
```

### Halmos

```solidity
// Halmos invariant test
function test_Invariant_TotalSupply() public {
    assertEq(token.totalSupply(), token.balanceOf(address(this)));
}

function test_Invariant_NoNegativeBalance(address user) public {
    assertGe(token.balanceOf(user), 0);
}
```

---

## Audit Checklist

### Pre-Audit
- [ ] Contract inventory complete
- [ ] Architecture diagram reviewed
- [ ] Trust boundaries mapped
- [ ] Invariants documented
- [ ] Documentation reviewed
- [ ] Upgrade mechanisms assessed

### Automated Analysis
- [ ] Slither executed
- [ ] Aderyn executed
- [ ] Mythril executed
- [ ] Solhint executed
- [ ] Semgrep executed
- [ ] Results triaged

### Manual Review
- [ ] Access control reviewed
- [ ] Reentrancy checked
- [ ] Oracle dependencies assessed
- [ ] Integer overflow/underflow checked
- [ ] Flash loan attack vectors analyzed
- [ ] Governance mechanisms reviewed
- [ ] Upgrade safety verified
- [ ] Economic attack vectors analyzed
- [ ] Gas optimization/DoS checked

### Dynamic Analysis
- [ ] Unit tests executed
- [ ] Fuzzing executed
- [ ] Invariant tests executed
- [ ] Fork tests executed
- [ ] Edge cases covered

### Reporting
- [ ] All findings documented
- [ ] Severity assigned
- [ ] Remediation provided
- [ ] PoC included
- [ ] Report reviewed
