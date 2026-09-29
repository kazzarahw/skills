# Remediation Patterns

## Remediation by Vulnerability Type

### Injection (SQL, Command, LDAP, XPath)

**Root cause:** Untrusted input concatenated into queries or commands without sanitization.

**Remediation:**
1. Use parameterized queries / prepared statements for all database interactions
2. Use allowlists for input validation (not denylists)
3. Apply the principle of least privilege to database accounts
4. Use ORM frameworks that handle escaping automatically
5. For command execution, avoid shell invocation; use language-specific APIs (e.g., `subprocess` with list args in Python)

**References:**
- OWASP SQL Injection Prevention Cheat Sheet
- OWASP Command Injection Prevention Cheat Sheet
- CWE-78, CWE-89, CWE-94

---

### Cross-Site Scripting (XSS)

**Root cause:** Untrusted input rendered in HTML without proper encoding.

**Remediation:**
1. Context-aware output encoding (HTML, JavaScript, URL, CSS contexts)
2. Use Content Security Policy (CSP) as defense-in-depth
3. Set `HttpOnly` and `Secure` flags on session cookies
4. Use modern frameworks that auto-escape by default (React, Vue, Angular)
5. Validate input against an allowlist of expected characters

**References:**
- OWASP XSS Prevention Cheat Sheet
- OWASP DOM-based XSS Prevention Cheat Sheet
- CWE-79

---

### Cross-Site Request Forgery (CSRF)

**Root cause:** State-changing actions rely solely on ambient credentials (cookies) without verifying user intent.

**Remediation:**
1. Implement anti-CSRF tokens (synchronizer token pattern)
2. Use `SameSite=Strict` or `SameSite=Lax` cookie attributes
3. Verify `Origin` and `Referer` headers for sensitive actions
4. Require re-authentication for high-risk operations

**References:**
- OWASP CSRF Prevention Cheat Sheet
- CWE-352

---

### Authentication Weaknesses

**Root cause:** Weak password policies, missing MFA, or flawed session management.

**Remediation:**
1. Enforce strong password policies (minimum 12 characters, complexity requirements)
2. Implement multi-factor authentication (TOTP or WebAuthn preferred)
3. Implement account lockout with exponential backoff
4. Use secure session management: random session IDs, timeout, regeneration on privilege change
5. Never store passwords in plaintext; use bcrypt, scrypt, or Argon2id

**References:**
- OWASP Authentication Cheat Sheet
- OWASP Password Storage Cheat Sheet
- CWE-287, CWE-307, CWE-916

---

### Authorization / Access Control

**Root cause:** Missing or inconsistent enforcement of access controls on every request.

**Remediation:**
1. Implement server-side authorization checks on every request
2. Use role-based access control (RBAC) or attribute-based access control (ABAC)
3. Deny by default; explicitly grant access
4. Test horizontal and vertical privilege escalation paths
5. Centralize authorization logic to avoid inconsistencies

**References:**
- OWASP Access Control Cheat Sheet
- CWE-639, CWE-862, CWE-863

---

### Security Misconfiguration

**Root cause:** Default configurations, unnecessary features enabled, or missing security headers.

**Remediation:**
1. Harden configurations per vendor security baselines (CIS Benchmarks)
2. Remove default accounts, sample applications, and unnecessary features
3. Implement security headers: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
4. Disable directory listing, HTTP TRACE, and unnecessary HTTP methods
5. Regularly scan for configuration drift

**References:**
- OWASP Security Headers Cheat Sheet
- CIS Benchmarks
- CWE-16, CWE-79

---

### Sensitive Data Exposure

**Root cause:** Data transmitted or stored without encryption, or with weak cryptography.

**Remediation:**
1. Encrypt data in transit using TLS 1.2+ (prefer TLS 1.3)
2. Encrypt data at rest using AES-256 or equivalent
3. Never store sensitive data unless absolutely necessary
4. Use strong, modern cryptographic algorithms (avoid MD5, SHA-1, DES, RC4)
5. Implement proper key management: rotation, secure storage, HSM where appropriate

**References:**
- OWASP Cryptographic Storage Cheat Sheet
- OWASP Transport Layer Security Cheat Sheet
- CWE-311, CWE-312, CWE-326, CWE-327

---

### Input Validation

**Root cause:** Insufficient validation of user-supplied input leading to unexpected behavior.

**Remediation:**
1. Validate all input on the server side (client-side validation is for UX only)
2. Use allowlists (accept known-good) rather than denylists (reject known-bad)
3. Validate type, length, format, and range
4. Use schema validation for structured data (JSON Schema, XML Schema)
5. Reject unexpected input; do not attempt to sanitize and continue

**References:**
- OWASP Input Validation Cheat Sheet
- CWE-20, CWE-116, CWE-1188

---

### File Upload Vulnerabilities

**Root cause:** Insufficient validation of uploaded files allowing execution or storage of malicious content.

**Remediation:**
1. Validate file type by content (magic bytes), not just extension
2. Store uploads outside the web root
3. Serve uploads with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`
4. Scan uploads with antivirus software
5. Rename uploaded files to prevent path traversal and execution
6. Set strict file size limits

**References:**
- OWASP File Upload Cheat Sheet
- CWE-434, CWE-435

---

### Server-Side Request Forgery (SSRF)

**Root cause:** Application fetches remote resources based on user-supplied URLs without validation.

**Remediation:**
1. Validate and allowlist URLs before fetching
2. Block requests to internal IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16)
3. Disable redirects or validate redirect targets
4. Use a dedicated egress proxy for outbound requests
5. Enforce URL scheme allowlist (http, https only)

**References:**
- OWASP SSRF Prevention Cheat Sheet
- CWE-918

---

### XML External Entity (XXE)

**Root cause:** XML parser processes external entity references, allowing file disclosure or SSRF.

**Remediation:**
1. Disable external entity processing in XML parsers
2. Use JSON instead of XML where possible
3. If XML is required, use a parser with secure defaults (e.g., `defusedxml` in Python)
4. Validate XML against a schema before processing

**References:**
- OWASP XXE Prevention Cheat Sheet
- CWE-611

---

### Insecure Deserialization

**Root cause:** Untrusted data deserialized without validation, leading to code execution.

**Remediation:**
1. Avoid deserializing data from untrusted sources
2. Use data-only formats (JSON, Protocol Buffers) instead of native serialization
3. If deserialization is necessary, implement integrity checks (HMAC) before deserializing
4. Run deserialization in a sandboxed environment with minimal privileges

**References:**
- OWASP Deserialization Prevention Cheat Sheet
- CWE-502

---

### API Security

**Root cause:** APIs lacking authentication, rate limiting, or input validation.

**Remediation:**
1. Require authentication on all API endpoints
2. Implement rate limiting per client/IP
3. Validate all input against a schema
4. Use OAuth 2.0 / OpenID Connect for authorization
5. Implement proper error handling that does not leak internal details
6. Log and monitor API access for anomalies

**References:**
- OWASP API Security Top 10
- OWASP REST Security Cheat Sheet
- CWE-284, CWE-285, CWE-639

---

## Configuration Hardening

### Web Server

```
# nginx example
server_tokens off;
add_header X-Content-Type-Options nosniff always;
add_header X-Frame-Options DENY always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

### TLS Configuration

```
# Minimum TLS 1.2, prefer TLS 1.3
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;
```

### Database

- Disable remote root access
- Use least-privilege application accounts
- Enable audit logging
- Encrypt connections (TLS)
- Regular patching schedule

---

## Effort Estimation Guide

| Level | Description | Example |
|-------|-------------|---------|
| S (Small) | < 4 hours; configuration change or single-line fix | Adding a security header, updating a dependency |
| M (Medium) | 4-40 hours; code change across multiple files or modules | Implementing parameterized queries, adding CSRF tokens |
| L (Large) | > 40 hours; architectural change or new system component | Implementing MFA, redesigning authorization system |
