# Web2 Code Review Guide

Comprehensive code review procedures for web2 applications. Covers vulnerability patterns, detection techniques, and language-specific guidance.

## Table of Contents

- [OWASP Top 10 (2021)](#owasp-top-10-2021)
  - [A01: Broken Access Control](#a01-broken-access-control)
  - [A02: Cryptographic Failures](#a02-cryptographic-failures)
  - [A03: Injection](#a03-injection)
  - [A04: Insecure Design](#a04-insecure-design)
  - [A05: Security Misconfiguration](#a05-security-misconfiguration)
  - [A06: Vulnerable and Outdated Components](#a06-vulnerable-and-outdated-components)
  - [A07: Identification and Authentication Failures](#a07-identification-and-authentication-failures)
  - [A08: Software and Data Integrity Failures](#a08-software-and-data-integrity-failures)
  - [A09: Security Logging and Monitoring Failures](#a09-security-logging-and-monitoring-failures)
  - [A10: Server-Side Request Forgery (SSRF)](#a10-server-side-request-forgery-ssrf)
- [Input Validation](#input-validation)
  - [SQL Injection](#sql-injection)
  - [Cross-Site Scripting (XSS)](#cross-site-scripting-xss)
  - [Command Injection](#command-injection)
  - [Path Traversal](#path-traversal)
  - [XML External Entity (XXE)](#xml-external-entity-xxe)
- [Authentication](#authentication)
  - [Session Management](#session-management)
  - [Credential Handling](#credential-handling)
  - [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
- [Authorization](#authorization)
  - [IDOR (Insecure Direct Object Reference)](#idor-insecure-direct-object-reference)
  - [Privilege Escalation](#privilege-escalation)
- [Cryptography](#cryptography)
  - [Weak Algorithms](#weak-algorithms)
  - [Hardcoded Keys](#hardcoded-keys)
  - [Improper Random](#improper-random)
- [Business Logic](#business-logic)
  - [Race Conditions](#race-conditions)
  - [Workflow Bypass](#workflow-bypass)
  - [Price Manipulation](#price-manipulation)
- [Error Handling](#error-handling)
  - [Verbose Errors](#verbose-errors)
  - [Information Disclosure](#information-disclosure)
- [Dependency Vulnerabilities](#dependency-vulnerabilities)
  - [Scanning Commands](#scanning-commands)
  - [Remediation](#remediation)
- [Code Quality](#code-quality)
  - [Complexity Metrics](#complexity-metrics)
  - [Maintainability](#maintainability)
  - [Test Coverage](#test-coverage)
- [Language-Specific Guidance](#language-specific-guidance)
  - [Python](#python)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Java](#java)
  - [Go](#go)
  - [Rust](#rust)

---

## OWASP Top 10 (2021)

### A01: Broken Access Control

Access control enforces policy such that users cannot act outside their intended permissions. Failures lead to unauthorized information disclosure, modification, or destruction.

**Common Patterns:**
- IDOR (Insecure Direct Object Reference) — accessing objects by modifying IDs
- Missing function-level access control — endpoints lack authorization checks
- CORS misconfiguration — overly permissive cross-origin policy
- Metadata manipulation — tampering with JWTs, cookies, or hidden fields

**Code Example — IDOR:**
```python
# VULNERABLE: No ownership check
@app.route('/api/documents/<int:doc_id>')
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    return jsonify(doc.to_dict())  # Any authenticated user can access any document

# SECURE: Ownership verification
@app.route('/api/documents/<int:doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return jsonify(doc.to_dict())
```

**Code Example — CORS Misconfiguration:**
```javascript
// VULNERABLE: Wildcard origin with credentials
app.use(cors({
    origin: '*',
    credentials: true  // Dangerous combination
}));

// SECURE: Whitelist specific origins
app.use(cors({
    origin: ['https://app.example.com', 'https://admin.example.com'],
    credentials: true
}));
```

### A02: Cryptographic Failures

Failures related to cryptography often lead to exposure of sensitive data. Includes weak algorithms, improper key management, and lack of encryption.

**Common Patterns:**
- Hardcoded encryption keys or passwords in source code
- Use of deprecated algorithms (MD5, SHA1, DES, RC4)
- Improper random number generation for security tokens
- Missing TLS or using weak TLS configurations
- Sensitive data stored in plaintext

**Code Example — Hardcoded Key:**
```python
# VULNERABLE: Hardcoded encryption key
SECRET_KEY = "my-super-secret-key-12345"
cipher = AES.new(SECRET_KEY, AES.MODE_ECB)

# SECURE: Key from environment with proper mode
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = os.urandom(32)  # Generate or load from secure vault
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)
```

**Code Example — Weak Random:**
```python
# VULNERABLE: Predictable random for tokens
import random
token = random.randint(100000, 999999)  # Predictable

# SECURE: Cryptographically secure random
import secrets
token = secrets.token_urlsafe(32)
```

### A03: Injection

Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data can trick the interpreter into executing unintended commands.

**Common Patterns:**
- SQL injection — unsanitized input in database queries
- Cross-Site Scripting (XSS) — unescaped output in HTML
- OS command injection — unsanitized input in system commands
- LDAP injection — unsanitized input in LDAP queries
- XML External Entity (XXE) — external entity resolution in XML

**Code Example — SQL Injection:**
```python
# VULNERABLE: String concatenation in SQL
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)

# SECURE: Parameterized queries
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
```

**Code Example — XSS:**
```javascript
// VULNERABLE: Unescaped output
element.innerHTML = userInput;

// SECURE: Text content assignment
element.textContent = userInput;

// SECURE: If HTML is needed, sanitize first
element.innerHTML = DOMPurify.sanitize(userInput);
```

**Code Example — Command Injection:**
```python
# VULNERABLE: Shell command with user input
os.system(f"ping -c 1 {user_input}")

# SECURE: No shell, argument list
subprocess.run(["ping", "-c", "1", user_input], shell=False)
```

### A04: Insecure Design

Insecure design is a broad category representing different weaknesses expressed as "missing or ineffective control design." This is distinct from implementation flaws.

**Common Patterns:**
- Missing threat modeling during design
- No rate limiting on sensitive operations
- Missing workflow enforcement (skipping steps)
- No transaction integrity for multi-step operations
- Trusting client-side validation only

**Code Example — Missing Rate Limiting:**
```python
# VULNERABLE: No rate limit on password reset
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    email = request.json['email']
    send_reset_email(email)  # Can be abused for email bombing

# SECURE: Rate limiting with Flask-Limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/reset-password', methods=['POST'])
@limiter.limit("3 per hour")
def reset_password():
    email = request.json['email']
    send_reset_email(email)
```

### A05: Security Misconfiguration

The most commonly seen issue. Often caused by incomplete configurations, open cloud storage, misconfigured HTTP headers, and verbose error messages.

**Common Patterns:**
- Default credentials unchanged
- Verbose error messages exposing stack traces
- Unnecessary features enabled (ports, services, pages)
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Outdated software with known vulnerabilities

**Code Example — Verbose Errors:**
```python
# VULNERABLE: Detailed error exposure
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        'error': str(e),
        'traceback': traceback.format_exc(),
        'config': app.config  # Leaks secrets!
    }), 500

# SECURE: Generic error for production
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500
```

### A06: Vulnerable and Outdated Components

Components run with the same privileges as the application. Vulnerable components can lead to serious breaches.

**Detection Commands:**
```bash
# Node.js
npm audit
npm audit --json
npm audit fix

# Python
safety check
safety check --full-report
pip-audit

# Java
owasp-dependency-check --scan .

# Go
govulncheck ./...

# Rust
cargo audit

# Multi-language
snyk test
snyk monitor
```

### A07: Identification and Authentication Failures

Confirmation of user identity, authentication, and session management is critical to protect against authentication-related attacks.

**Common Patterns:**
- Weak password policy
- No MFA support
- Session fixation — session ID not regenerated after login
- Session timeout not enforced
- Credential stuffing protection missing
- Plaintext credential storage

**Code Example — Session Fixation:**
```python
# VULNERABLE: Session ID not regenerated
@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form)
    session['user_id'] = user.id  # Session ID unchanged!
    return redirect('/dashboard')

# SECURE: Regenerate session on login
@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form)
    session.clear()  # Clear old session
    session['user_id'] = user.id  # New session ID
    session.permanent = True
    return redirect('/dashboard')
```

### A08: Software and Data Integrity Failures

Relies on software updates, critical data, and CI/CD pipelines without verifying integrity. Insecure deserialization is a subset.

**Common Patterns:**
- Insecure deserialization of untrusted data
- CI/CD pipeline without integrity checks
- Unsigned or unverified software updates
- Missing integrity checks on cached data

**Code Example — Insecure Deserialization:**
```python
# VULNERABLE: Pickle deserialization of untrusted data
import pickle
data = pickle.loads(user_input)  # Remote code execution!

# SECURE: Use JSON for untrusted data
import json
data = json.loads(user_input)
```

### A09: Security Logging and Monitoring Failures

Without proper logging and monitoring, breaches can go undetected. The average time to identify a breach is 200+ days.

**Common Patterns:**
- No logging of authentication failures
- No logging of access control failures
- Logs not monitored or alerted
- Logs stored locally only (easily tampered)
- No audit trail for sensitive operations

**Code Example — Security Logging:**
```python
# SECURE: Comprehensive security logging
import structlog

logger = structlog.get_logger()

def login(username, password, ip_address):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning("auth_failed",
            username=username,
            ip=ip_address,
            user_agent=request.headers.get('User-Agent'),
            timestamp=datetime.utcnow().isoformat()
        )
        return False
    logger.info("auth_success", username=username, ip=ip_address)
    return True
```

### A10: Server-Side Request Forgery (SSRF)

SSRF flaws occur when a web application fetches a remote resource without validating the user-supplied URL.

**Common Patterns:**
- Fetching user-supplied URLs without validation
- Cloud metadata service access (169.254.169.254)
- Internal port scanning via URL manipulation
- Bypassing firewall via redirects

**Code Example — SSRF:**
```python
# VULNERABLE: Fetching user-supplied URL
@app.route('/api/fetch')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)  # Can access internal services!
    return response.text

# SECURE: URL validation and blocking internal ranges
import ipaddress
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
]

def is_safe_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        return not any(ip in net for net in BLOCKED_NETWORKS)
    except socket.gaierror:
        return False

@app.route('/api/fetch')
def fetch_url():
    url = request.args.get('url')
    if not is_safe_url(url):
        abort(400, description="URL not allowed")
    response = requests.get(url, timeout=5, allow_redirects=False)
    return response.text
```

---

## Input Validation

### SQL Injection

**Detection:**
- String concatenation in SQL queries
- Dynamic query building with user input
- ORM raw query methods with interpolation

**Exploitation:**
```sql
-- Authentication bypass
' OR '1'='1' --
' OR 1=1; DROP TABLE users; --

-- Data extraction
' UNION SELECT username, password FROM users; --
'; WAITFOR DELAY '0:0:5' --  (time-based blind)
```

**Remediation:**
- Use parameterized queries / prepared statements
- Use ORM query builders (not raw SQL with interpolation)
- Apply principle of least privilege to DB accounts
- Validate input type, length, and format

### Cross-Site Scripting (XSS)

**Types:**
- **Stored XSS** — malicious script stored in database
- **Reflected XSS** — script reflected in response
- **DOM-based XSS** — client-side script execution

**Detection:**
- Unescaped output in templates
- `innerHTML`, `document.write()` with user data
- Missing Content-Security-Policy header

**Remediation:**
- Context-aware output encoding (HTML, JavaScript, URL, CSS)
- Use `textContent` instead of `innerHTML`
- Implement CSP header
- Sanitize HTML with DOMPurify if rich content needed

### Command Injection

**Detection:**
- `os.system()`, `subprocess.call(shell=True)`, `eval()`, `exec()`
- User input in shell commands

**Remediation:**
- Avoid shell commands; use language-native APIs
- If shell needed, use `subprocess.run()` with `shell=False` and argument lists
- Validate and sanitize all input
- Use allowlists for commands

### Path Traversal

**Detection:**
- User input in file paths without sanitization
- `../` sequences in file operations

**Remediation:**
```python
# SECURE: Path validation
import os

def safe_read_file(base_dir, user_path):
    # Resolve to absolute path
    full_path = os.path.realpath(os.path.join(base_dir, user_path))
    # Ensure it's within base directory
    if not full_path.startswith(os.path.realpath(base_dir)):
        raise ValueError("Path traversal detected")
    with open(full_path, 'r') as f:
        return f.read()
```

### XML External Entity (XXE)

**Detection:**
- XML parsers with external entity resolution enabled
- User-supplied XML without validation

**Remediation:**
```python
# SECURE: Disable external entities
from defusedxml import ElementTree as ET

# defusedxml prevents XXE by default
tree = ET.parse(xml_file)

# For lxml:
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse(xml_file, parser)
```

---

## Authentication

### Session Management

**Best Practices:**
- Regenerate session ID after login (prevent fixation)
- Set secure, HttpOnly, SameSite cookies
- Implement absolute and idle session timeouts
- Store sessions server-side, not in cookies
- Invalidate sessions on logout

**Cookie Configuration:**
```python
# SECURE: Session cookie configuration
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

### Credential Handling

**Best Practices:**
- Hash passwords with bcrypt, scrypt, or Argon2 (never MD5/SHA1)
- Use unique salts per password
- Implement account lockout after failed attempts
- Never log credentials
- Use constant-time comparison for password verification

```python
# SECURE: Password hashing with bcrypt
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
```

### Multi-Factor Authentication (MFA)

**Implementation:**
- TOTP (Time-based One-Time Password) — RFC 6238
- WebAuthn/FIDO2 — hardware keys
- SMS fallback (weakest option)

```python
# SECURE: TOTP implementation
import pyotp

def setup_mfa(user):
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(user.email, issuer_name="MyApp")

def verify_mfa(user, token):
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(token, valid_window=1)
```

---

## Authorization

### IDOR (Insecure Direct Object Reference)

**Detection:**
- Object IDs in URLs/parameters without ownership checks
- Sequential IDs that can be enumerated
- Missing authorization checks on API endpoints

**Remediation:**
- Verify ownership before returning resources
- Use UUIDs instead of sequential IDs
- Implement authorization checks on every endpoint
- Use policy-based access control (PBAC)

### Privilege Escalation

**Detection:**
- Role changes without proper verification
- Client-side role determination
- Missing authorization on admin endpoints

**Remediation:**
```python
# SECURE: Role-based access control
from functools import wraps

def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/users')
@require_role('admin')
def admin_users():
    return User.query.all()
```

---

## Cryptography

### Weak Algorithms

**Never Use:**
- MD5, SHA1 (hashing)
- DES, 3DES, RC4 (encryption)
- RSA with < 2048-bit keys
- ECB mode (electronic codebook)

**Recommended:**
- Hashing: SHA-256, SHA-3, BLAKE2
- Encryption: AES-256-GCM, ChaCha20-Poly1305
- Key exchange: ECDH (Curve25519), RSA-4096
- Signatures: Ed25519, ECDSA (P-256)

### Hardcoded Keys

**Detection:**
- Search for `SECRET_KEY`, `API_KEY`, `PASSWORD` in source
- Check for base64-encoded strings in code
- Review configuration files committed to version control

**Remediation:**
- Store secrets in environment variables or vaults (HashiCorp Vault, AWS Secrets Manager)
- Rotate keys regularly
- Use separate keys for different environments
- Never commit secrets to version control

### Improper Random

**Detection:**
- `random.random()` or `Math.random()` for security tokens
- `rand()` in C/C++ for cryptographic purposes
- Predictable seed values

**Remediation:**
- Python: `secrets` module
- JavaScript: `crypto.getRandomValues()`
- Java: `SecureRandom`
- Go: `crypto/rand`

---

## Business Logic

### Race Conditions

**Detection:**
- Check-then-act patterns without locking
- Concurrent access to shared resources
- Time-of-check to time-of-use (TOCTOU) issues

**Remediation:**
```python
# SECURE: Atomic operations with optimistic locking
from sqlalchemy import func

def transfer_funds(from_account, to_account, amount):
    # Use database-level atomic operations
    result = db.session.execute(
        text("""
            UPDATE accounts 
            SET balance = balance - :amount 
            WHERE id = :from_id AND balance >= :amount
        """),
        {"amount": amount, "from_id": from_account}
    )
    if result.rowcount == 0:
        raise InsufficientFunds()
    
    db.session.execute(
        text("UPDATE accounts SET balance = balance + :amount WHERE id = :to_id"),
        {"amount": amount, "to_id": to_account}
    )
    db.session.commit()
```

### Workflow Bypass

**Detection:**
- Multi-step processes that can be skipped
- Client-side state management for workflow steps
- Missing server-side validation of step completion

**Remediation:**
- Enforce workflow state machine server-side
- Validate prerequisites for each step
- Use database transactions for multi-step operations

### Price Manipulation

**Detection:**
- Client-side price calculation
- Missing server-side price verification
- Discount/coupon logic that can be abused

**Remediation:**
```python
# SECURE: Server-side price calculation
def calculate_total(cart, coupon_code=None):
    total = 0
    for item in cart:
        # Always fetch price from database, never trust client
        product = Product.query.get(item.product_id)
        total += product.price * item.quantity
    
    if coupon_code:
        coupon = validate_coupon(coupon_code)  # Server-side validation
        total = apply_discount(total, coupon)
    
    return total
```

---

## Error Handling

### Verbose Errors

**Detection:**
- Stack traces shown to users
- Database error messages exposed
- Internal paths or configuration in error responses

**Remediation:**
- Generic error messages in production
- Detailed errors logged server-side only
- Custom error pages
- Error tracking (Sentry, etc.) for debugging

### Information Disclosure

**Detection:**
- Comments revealing internal details
- Debug mode enabled in production
- Directory listing enabled
- Unnecessary headers (Server, X-Powered-By)

**Remediation:**
```python
# SECURE: Remove identifying headers
@app.after_request
def remove_headers(response):
    response.headers.pop('Server', None)
    response.headers.pop('X-Powered-By', None)
    return response

# Disable debug mode in production
app.config['DEBUG'] = False
app.config['TESTING'] = False
```

---

## Dependency Vulnerabilities

### Scanning Commands

```bash
# Node.js
npm audit --audit-level=high
npm audit fix
npx auditjs ossi

# Python
safety check --full-report
pip-audit --desc

# Java
owasp-dependency-check --scan . --format JSON
mvn dependency:tree

# Go
govulncheck ./...
govulncheck -json ./...

# Rust
cargo audit
cargo audit --json

# Multi-language
snyk test --all-projects
snyk monitor
```

### Remediation

1. **Update** — Apply security patches immediately
2. **Replace** — Switch to maintained alternatives
3. **Mitigate** — Add compensating controls if patch unavailable
4. **Accept** — Document risk acceptance with justification

---

## Code Quality

### Complexity Metrics

| Metric | Tool | Threshold |
|--------|------|-----------|
| Cyclomatic Complexity | radon, lizard | < 10 per function |
| Cognitive Complexity | SonarQube | < 15 per function |
| Lines of Code | cloc | < 500 per file |
| Nesting Depth | ESLint, Pylint | < 4 levels |

### Maintainability

- **Single Responsibility** — Each function/class does one thing
- **DRY** — Don't repeat yourself; extract common logic
- **Meaningful names** — Variables and functions describe their purpose
- **Documentation** — Public APIs documented; complex logic commented
- **Test coverage** — Aim for > 80% coverage on security-critical code

### Test Coverage

```bash
# Python
pytest --cov=src --cov-report=html --cov-fail-under=80

# JavaScript
npm test -- --coverage --coverageThreshold=80

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

---

## Language-Specific Guidance

### Python

**Common Issues:**
- `pickle` deserialization of untrusted data
- `eval()` and `exec()` with user input
- `yaml.load()` without `SafeLoader`
- `subprocess` with `shell=True`
- `assert` statements for security checks (disabled with `-O`)

**Tools:**
```bash
bandit -r src/ -f json
pylint --load-plugins pylint_security
safety check
```

### JavaScript/TypeScript

**Common Issues:**
- `eval()` and `Function()` constructor
- Prototype pollution (`__proto__`, `constructor.prototype`)
- Insecure randomness (`Math.random()`)
- DOM-based XSS (`innerHTML`, `document.write`)
- Missing input validation on API endpoints

**Tools:**
```bash
eslint --ext .js,.ts src/
npm audit
npx semgrep --config=p/owasp-top-ten src/
```

### Java

**Common Issues:**
- Insecure deserialization (`ObjectInputStream`)
- XXE in XML parsers
- SQL injection in JDBC
- Hardcoded credentials
- Missing access controls

**Tools:**
```bash
spotbugs -textui .
owasp-dependency-check --scan .
```

### Go

**Common Issues:**
- SQL injection with string concatenation
- Insecure TLS configuration (`InsecureSkipVerify`)
- Path traversal in file operations
- Race conditions (use `go test -race`)
- Weak randomness (`math/rand` for security)

**Tools:**
```bash
gosec -fmt json -out results.json ./...
govulncheck ./...
go test -race ./...
```

### Rust

**Common Issues:**
- `unsafe` blocks with improper bounds checking
- Integer overflow in release mode (wraps by default)
- Unvalidated input in `std::process::Command`
- Weak randomness (`rand::thread_rng` for security)

**Tools:**
```bash
cargo audit
cargo clippy -- -W clippy::security
cargo fuzz run target_name
```
