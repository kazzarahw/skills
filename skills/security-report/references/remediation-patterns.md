# Remediation Patterns

Remediation guidance by vulnerability type with code examples.

---

## Table of Contents

1. [Web2: OWASP Top 10 Remediation](#web2-owasp-top-10-remediation)
2. [Web2: Authentication Remediation](#web2-authentication-remediation)
3. [Web2: Authorization Remediation](#web2-authorization-remediation)
4. [Web2: Input Validation Remediation](#web2-input-validation-remediation)
5. [Web2: Cryptography Remediation](#web2-cryptography-remediation)
6. [Web3: Reentrancy Remediation](#web3-reentrancy-remediation)
7. [Web3: Oracle Manipulation Remediation](#web3-oracle-manipulation-remediation)
8. [Web3: Access Control Remediation](#web3-access-control-remediation)
9. [Web3: Upgrade Safety Remediation](#web3-upgrade-safety-remediation)
10. [Web3: Flash Loan Attack Remediation](#web3-flash-loan-attack-remediation)
11. [Web3: Governance Attack Remediation](#web3-governance-attack-remediation)
12. [Web3: Economic Attack Remediation](#web3-economic-attack-remediation)
13. [Secure Design Patterns](#secure-design-patterns)

---

## Web2: OWASP Top 10 Remediation

### A01:2021 — Broken Access Control

**Remediation:**
- Deny by default — explicitly grant access, never assume.
- Implement role-based access control (RBAC) or attribute-based access control (ABAC).
- Validate authorization on every request, not just at login.
- Use server-side authorization checks; never rely on client-side controls.
- Implement rate limiting on API endpoints.

**Code Example (Express.js):**
```javascript
// BAD: No authorization check
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});

// GOOD: Authorization check
app.get('/api/users/:id', authenticate, authorize('read:users'), async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});
```

### A02:2021 — Cryptographic Failures

**Remediation:**
- Use strong, industry-standard encryption algorithms (AES-256-GCM, ChaCha20-Poly1305).
- Never roll your own crypto.
- Use TLS 1.2+ for all data in transit.
- Hash passwords with bcrypt, scrypt, or Argon2 (never MD5 or SHA1).
- Store encryption keys in a dedicated key management service (KMS).

**Code Example (Python):**
```python
# BAD: Weak hashing
import hashlib
hashlib.md5(password.encode()).hexdigest()

# GOOD: Strong hashing
import bcrypt
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode(), salt)
```

### A03:2021 — Injection

**Remediation:**
- Use parameterized queries / prepared statements.
- Validate and sanitize all input.
- Use ORM frameworks that handle escaping.
- Implement allowlist input validation.
- Apply least privilege to database accounts.

**Code Example (Python/SQLAlchemy):**
```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE id = {user_input}"
db.execute(query)

# GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = :user_id"
db.execute(query, {"user_id": user_input})
```

### A04:2021 — Insecure Design

**Remediation:**
- Integrate threat modeling into the design phase.
- Use secure design patterns (see below).
- Implement defense in depth.
- Apply the principle of least privilege.
- Use secure defaults.

### A05:2021 — Security Misconfiguration

**Remediation:**
- Harden all configurations (disable default accounts, change default passwords).
- Remove unnecessary features and services.
- Implement automated configuration scanning.
- Use secure headers (CSP, HSTS, X-Frame-Options).
- Regularly patch and update all components.

**Code Example (Express.js security headers):**
```javascript
const helmet = require('helmet');
app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
  }
}));
```

### A06:2021 — Vulnerable and Outdated Components

**Remediation:**
- Maintain a software bill of materials (SBOM).
- Regularly scan for vulnerabilities (Snyk, Dependabot, OWASP Dependency-Check).
- Establish a patch management process.
- Remove unused dependencies.
- Monitor vulnerability databases (NVD, CVE).

### A07:2021 — Identification and Authentication Failures

**Remediation:**
- Implement multi-factor authentication (MFA).
- Enforce strong password policies.
- Implement account lockout after failed attempts.
- Use secure session management (random session IDs, secure cookies).
- Never store passwords in plaintext.

### A08:2021 — Software and Data Integrity Failures

**Remediation:**
- Verify integrity of software updates (code signing).
- Use CI/CD pipelines with integrity checks.
- Implement integrity verification for data in transit and at rest.
- Use digital signatures for critical data.

### A09:2021 — Security Logging and Monitoring Failures

**Remediation:**
- Log all authentication events, access control failures, and input validation errors.
- Implement real-time alerting for suspicious activity.
- Protect log integrity (append-only, centralized storage).
- Establish incident response procedures.
- Retain logs for at least 90 days.

### A10:2021 — Server-Side Request Forgery (SSRF)

**Remediation:**
- Validate and sanitize all user-supplied URLs.
- Implement allowlists for allowed domains/IPs.
- Disable unnecessary URL schemas (file://, gopher://, etc.).
- Use network segmentation to limit access.
- Implement egress filtering.

---

## Web2: Authentication Remediation

### Password Storage

```python
# Use Argon2 (winner of Password Hashing Competition)
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,      # iterations
    memory_cost=65536, # 64 MB
    parallelism=4,     # parallel threads
    hash_len=32,
    salt_len=16
)

# Hash password
hash = ph.hash(password)

# Verify password
try:
    ph.verify(hash, password)
except VerifyMismatchError:
    # Invalid password
    pass
```

### Session Management

```javascript
// Secure session configuration (Express.js)
app.use(session({
  secret: process.env.SESSION_SECRET,
  name: '__Host-sessionId',  // __Host- prefix for cookie security
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,      // HTTPS only
    httpOnly: true,    // No JavaScript access
    sameSite: 'strict', // CSRF protection
    maxAge: 3600000    // 1 hour
  }
}));
```

### Multi-Factor Authentication

```python
# TOTP-based MFA (Python)
import pyotp

# Generate secret
secret = pyotp.random_base32()

# Generate QR code URI
uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name=user.email,
    issuer_name="YourApp"
)

# Verify token
totp = pyotp.TOTP(secret)
if totp.verify(user_provided_token):
    # MFA successful
    pass
```

---

## Web2: Authorization Remediation

### Role-Based Access Control (RBAC)

```python
# RBAC implementation
from enum import Enum
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

def require_role(role: Role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/admin/users")
@require_role(Role.ADMIN)
def admin_users():
    return render_template("admin/users.html")
```

### Attribute-Based Access Control (ABAC)

```python
# ABAC implementation
def check_permission(user, resource, action):
    # Check user attributes
    if user.department == resource.department:
        return True
    if user.role == "admin":
        return True
    if resource.owner == user.id:
        return True
    return False
```

---

## Web2: Input Validation Remediation

### Allowlist Validation

```python
import re
from typing import Optional

def validate_username(username: str) -> Optional[str]:
    """Validate username against allowlist pattern."""
    if not username:
        return "Username is required"
    if len(username) < 3 or len(username) > 32:
        return "Username must be 3-32 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return "Username can only contain letters, numbers, and underscores"
    return None  # Valid

def validate_email(email: str) -> Optional[str]:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "Invalid email format"
    return None
```

### Output Encoding

```python
import html

def render_user_content(user_input: str) -> str:
    """Encode user input before rendering in HTML."""
    return html.escape(user_input)

# For JavaScript context
import json

def render_for_js(user_input: str) -> str:
    """Encode user input for JavaScript context."""
    return json.dumps(user_input)[1:-1]  # Remove quotes
```

---

## Web2: Cryptography Remediation

### Symmetric Encryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt using AES-256-GCM."""
    nonce = os.urandom(12)  # 96-bit nonce
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext  # Prepend nonce for decryption

def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt using AES-256-GCM."""
    nonce = ciphertext[:12]
    encrypted_data = ciphertext[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_data, None)
```

### TLS Configuration

```nginx
# nginx TLS configuration
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

---

## Web3: Reentrancy Remediation

### Checks-Effects-Interactions Pattern

```solidity
// BAD: Vulnerable to reentrancy
function withdraw() external {
    uint256 balance = balances[msg.sender];
    require(balance > 0, "No balance");

    (bool success, ) = msg.sender.call{value: balance}("");
    require(success, "Transfer failed");

    balances[msg.sender] = 0;
}

// GOOD: Checks-Effects-Interactions
function withdraw() external {
    uint256 balance = balances[msg.sender];
    require(balance > 0, "No balance");

    balances[msg.sender] = 0;  // Effects first

    (bool success, ) = msg.sender.call{value: balance}("");  // Interactions last
    require(success, "Transfer failed");
}
```

### Reentrancy Guard

```solidity
// Reentrancy guard using OpenZeppelin
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SecureVault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function withdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");

        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
    }
}
```

### Pull Over Push Pattern

```solidity
// GOOD: Pull over push
contract PullPayment {
    mapping(address => uint256) public balances;

    function withdraw() external {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");

        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
    }
}
```

---

## Web3: Oracle Manipulation Remediation

### Use Decentralized Oracles

```solidity
// BAD: Single source oracle
uint256 price = getPriceFromSingleSource();

// GOOD: Chainlink decentralized oracle
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function getLatestPrice() public view returns (int256) {
        (
            uint80 roundID,
            int256 price,
            uint256 startedAt,
            uint256 timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        return price;
    }
}
```

### TWAP (Time-Weighted Average Price)

```solidity
// Use TWAP instead of spot price
contract TWAPOracle {
    uint256 public period = 300; // 5 minutes
    uint256 public lastPrice;
    uint256 public lastUpdate;

    function update(uint256 currentPrice) external {
        uint256 timeElapsed = block.timestamp - lastUpdate;
        if (timeElapsed >= period) {
            lastPrice = currentPrice;
            lastUpdate = block.timestamp;
        }
    }

    function getPrice() external view returns (uint256) {
        return lastPrice;
    }
}
```

### Price Deviation Checks

```solidity
contract PriceCheck {
    uint256 public maxDeviation = 5; // 5%

    function validatePrice(uint256 newPrice, uint256 oldPrice) internal pure {
        uint256 deviation = newPrice > oldPrice
            ? ((newPrice - oldPrice) * 100) / oldPrice
            : ((oldPrice - newPrice) * 100) / oldPrice;
        require(deviation <= maxDeviation, "Price deviation too high");
    }
}
```

---

## Web3: Access Control Remediation

### Role-Based Access Control

```solidity
// OpenZeppelin AccessControl
import "@openzeppelin/contracts/access/AccessControl.sol";

contract SecureContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    constructor() {
        _setupRole(ADMIN_ROLE, msg.sender);
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function sensitiveFunction() external onlyRole(OPERATOR_ROLE) {
        // Only operators can call this
    }
}
```

### Ownable Pattern

```solidity
// OpenZeppelin Ownable
import "@openzeppelin/contracts/access/Ownable.sol";

contract OwnedContract is Ownable {
    function adminFunction() external onlyOwner {
        // Only owner can call this
    }
}
```

### Timelock for Critical Operations

```solidity
// OpenZeppelin TimelockController
import "@openzeppelin/contracts/governance/TimelockController.sol";

contract TimelockedAdmin is TimelockController {
    constructor(
        uint256 minDelay,
        address[] memory proposers,
        address[] memory executors
    ) TimelockController(minDelay, proposers, executors) {}
}
```

---

## Web3: Upgrade Safety Remediation

### Use Proxy Patterns

```solidity
// OpenZeppelin Transparent Upgradeable Proxy
import "@openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol";

// Implementation contract
contract MyContractV1 {
    uint256 public value;

    function setValue(uint256 _value) external {
        value = _value;
    }
}

// Proxy contract
contract MyContractProxy is TransparentUpgradeableProxy {
    constructor(
        address _logic,
        address admin_,
        bytes memory _data
    ) TransparentUpgradeableProxy(_logic, admin_, _data) {}
}
```

### Storage Layout Safety

```solidity
// BAD: Changing storage layout in upgrade
contract V1 {
    uint256 public value;
    address public owner;
}

contract V2 {
    address public owner;  // BAD: Changed order
    uint256 public value;
}

// GOOD: Append only
contract V1 {
    uint256 public value;
    address public owner;
}

contract V2 {
    uint256 public value;
    address public owner;
    uint256 public newValue;  // GOOD: Appended
}
```

### Initialization Safety

```solidity
// OpenZeppelin Initializable
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract MyContract is Initializable {
    uint256 public value;
    bool private initialized;

    function initialize(uint256 _value) external initializer {
        value = _value;
    }
}
```

---

## Web3: Flash Loan Attack Remediation

### Use TWAP Instead of Spot Price

```solidity
// BAD: Using spot price for collateral
uint256 collateralValue = getSpotPrice() * collateralAmount;

// GOOD: Using TWAP
uint256 collateralValue = getTWAP(300) * collateralAmount; // 5-minute TWAP
```

### Implement Circuit Breakers

```solidity
contract CircuitBreaker {
    uint256 public maxPriceChange = 10; // 10%
    uint256 public lastPrice;
    bool public paused;

    modifier whenNotPaused() {
        require(!paused, "Contract paused");
        _;
    }

    function checkPrice(uint256 currentPrice) internal {
        uint256 change = currentPrice > lastPrice
            ? ((currentPrice - lastPrice) * 100) / lastPrice
            : ((lastPrice - currentPrice) * 100) / lastPrice;
        if (change > maxPriceChange) {
            paused = true;
        }
        lastPrice = currentPrice;
    }
}
```

### Rate Limiting

```solidity
contract RateLimiter {
    uint256 public maxDeposit = 1000 ether;
    uint256 public maxWithdrawal = 1000 ether;
    uint256 public lastDepositTime;
    uint256 public lastWithdrawalTime;
    uint256 public cooldown = 1 hours;

    function deposit() external payable {
        require(block.timestamp >= lastDepositTime + cooldown, "Deposit cooldown");
        require(msg.value <= maxDeposit, "Exceeds max deposit");
        lastDepositTime = block.timestamp;
    }
}
```

---

## Web3: Governance Attack Remediation

### Quorum Requirements

```solidity
contract Governance {
    uint256 public quorum = 4; // 4% of total supply
    uint256 public proposalThreshold = 1000 ether;

    function propose(address[] memory targets, uint256[] memory values, bytes[] memory calldatas) external {
        require(getVotes(msg.sender) >= proposalThreshold, "Below proposal threshold");
        // Create proposal
    }
}

### Timelock for Governance

```solidity
contract TimelockedGovernance {
    uint256 public votingDelay = 1; // 1 block
    uint256 public votingPeriod = 40320; // ~7 days
    uint256 public timelockDelay = 2 days;

    function execute(uint256 proposalId) external {
        require(block.timestamp >= proposalEta, "Timelock active");
        // Execute proposal
    }
}
```

### Vote Snapshotting

```solidity
contract SnapshotGovernance {
    mapping(uint256 => mapping(address => uint256)) public snapshots;

    function getVotes(address account, uint256 blockNumber) public view returns (uint256) {
        return snapshots[blockNumber][account];
    }
}
```

---

## Web3: Economic Attack Remediation

### Slippage Protection

```solidity
contract AMM {
    uint256 public slippageTolerance = 50; // 0.5%

    function swap(uint256 amountIn, uint256 minAmountOut) external {
        uint256 amountOut = getAmountOut(amountIn);
        require(amountOut >= minAmountOut, "Slippage too high");
        // Execute swap
    }
}
```

### Deadline Protection

```solidity
contract DEX {
    function swap(uint256 amountIn, uint256 minAmountOut, uint256 deadline) external {
        require(block.timestamp <= deadline, "Transaction expired");
        // Execute swap
    }
}
```

### Reentrancy Protection for Swaps

```solidity
contract SecureSwap is ReentrancyGuard {
    function swap(uint256 amountIn, uint256 minAmountOut) external nonReentrant {
        // Swap logic
    }
}
```

---

## Secure Design Patterns

### Checks-Effects-Interactions

Always follow this order in smart contract functions:
1. **Checks** — Validate all conditions and inputs
2. **Effects** — Update contract state
3. **Interactions** — Make external calls

```solidity
function secureFunction() external {
    // 1. Checks
    require(condition, "Condition not met");

    // 2. Effects
    stateVariable = newValue;

    // 3. Interactions
    (bool success, ) = externalContract.call{value: amount}("");
    require(success, "Call failed");
}
```

### Pull Over Push

Prefer users withdrawing funds rather than the contract sending funds:

```solidity
// GOOD: Pull over push
mapping(address => uint256) public pendingWithdrawals;

function withdraw() external {
    uint256 amount = pendingWithdrawals[msg.sender];
    require(amount > 0, "No pending withdrawal");
    pendingWithdrawals[msg.sender] = 0;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### Circuit Breakers

Implement emergency pause functionality:

```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract PausableContract is Pausable, Ownable {
    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function criticalFunction() external whenNotPaused {
        // Function logic
    }
}
```

### Rate Limiting

Implement rate limiting for sensitive operations:

```solidity
contract RateLimited {
    mapping(address => uint256) public lastActionTime;
    uint256 public cooldown = 1 hours;

    modifier rateLimited() {
        require(block.timestamp >= lastActionTime[msg.sender] + cooldown, "Rate limited");
        _;
        lastActionTime[msg.sender] = block.timestamp;
    }

    function sensitiveAction() external rateLimited {
        // Action logic
    }
}
```

### Access Control

Implement proper access control:

```solidity
import "@openzeppelin/contracts/access/AccessControl.sol";

contract AccessControlled is AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external onlyRole(BURNER_ROLE) {
        _burn(from, amount);
    }
}
```

### Safe Math

Use SafeMath or Solidity 0.8+ built-in overflow checks:

```solidity
// Solidity 0.8+ has built-in overflow checks
pragma solidity ^0.8.0;

contract SafeMathExample {
    function add(uint256 a, uint256 b) external pure returns (uint256) {
        return a + b; // Reverts on overflow
    }
}
```

### Event Emission

Emit events for all state changes:

```solidity
contract EventEmitting {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function transfer(address to, uint256 amount) external {
        // Transfer logic
        emit Transfer(msg.sender, to, amount);
    }
}
```

---

## Quick Reference

| Vulnerability | Primary Remediation | Secondary Remediation |
|---------------|--------------------|-----------------------|
| SQL Injection | Parameterized queries | ORM, input validation |
| XSS | Output encoding | CSP headers |
| CSRF | SameSite cookies | CSRF tokens |
| Auth Bypass | Server-side validation | MFA |
| IDOR | Authorization checks | Object-level permissions |
| Reentrancy | Checks-Effects-Interactions | Reentrancy guard |
| Oracle Manipulation | Decentralized oracles | TWAP, deviation checks |
| Access Control | RBAC/ABAC | Timelock |
| Flash Loan | TWAP | Circuit breakers |
| Governance | Quorum | Timelock, snapshots |
