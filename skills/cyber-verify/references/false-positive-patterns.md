# False Positive Patterns Catalog

A comprehensive catalog of common false positive patterns encountered in automated security scanning. Use this reference to quickly identify and filter out non-findings from scan results.

---

## Table of Contents

1. [Generic 404/403 Page Matches](#generic-404403-page-matches)
2. [Version Banner Spoofing](#version-banner-spoofing)
3. [Default Credentials False Positives](#default-credentials-false-positives)
4. [SSL/TLS Configuration False Positives](#ssltls-configuration-false-positives)
5. [Information Disclosure False Positives](#information-disclosure-false-positives)
6. [XSS False Positives](#xss-false-positives)
7. [SQL Injection False Positives](#sql-injection-false-positives)
8. [Open Port False Positives (Masscan)](#open-port-false-positives-masscan)

---

## Generic 404/403 Page Matches

Scanners often flag generic error pages as vulnerabilities. These are almost always false positives.

### Pattern: 404 Page Detection

| Field | Value |
|-------|-------|
| **Template** | `http-misc/404-page.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~95% |

**Indicators of False Positive:**
- Response body contains standard "404 Not Found" text
- No unique application logic in the error page
- Response is a static HTML page
- Status code is actually 404 (not 200 with 404 content)

**Example False Positive:**
```
[INFO] http-misc/404-page - Target: https://example.com/nonexistent
Response: <html><body><h1>404 Not Found</h1></body></html>
```

**How to Verify:**
```bash
# Check if the page is a real 404
curl -s -o /dev/null -w "%{http_code}" https://example.com/random-path-12345
# If it returns 404, this is expected behavior, not a vulnerability
```

**When It's NOT a False Positive:**
- The 404 page leaks stack traces, internal paths, or version information
- The 404 page reflects user input without sanitization (XSS)
- The 404 page is actually a 200 OK (soft 404) used for cloaking

### Pattern: 403 Page Detection

| Field | Value |
|-------|-------|
| **Template** | `http-misc/403-page.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~90% |

**Indicators of False Positive:**
- Standard "403 Forbidden" response from web server
- Proper access control is working as intended
- No bypass is demonstrated

**Example False Positive:**
```
[INFO] http-misc/403-page - Target: https://example.com/admin
Response: <html><body><h1>403 Forbidden</h1></body></html>
```

**When It's NOT a False Positive:**
- The 403 can be bypassed with header manipulation (e.g., `X-Forwarded-For: 127.0.0.1`)
- The 403 page reveals sensitive information about the protected resource
- The 403 is inconsistent (some paths return 403, others return 200 for same resource)

---

## Version Banner Spoofing

Servers may intentionally or unintentionally disclose version information. Not all version disclosures are vulnerabilities.

### Pattern: Server Header Disclosure

| Field | Value |
|-------|-------|
| **Template** | `http-misc/server-header.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~80% |

**Indicators of False Positive:**
- Server header shows generic value (e.g., `Server: nginx`)
- No specific version number disclosed
- Header is expected behavior for the server type

**Example False Positive:**
```
[INFO] http-misc/server-header - Target: https://example.com
Server: nginx
```

**When It's NOT a False Positive:**
- Specific version with known CVEs: `Server: Apache/2.4.49` (CVE-2021-41773)
- Version reveals end-of-life software: `Server: Microsoft-IIS/6.0`
- Version combined with other findings increases attack surface

### Pattern: X-Powered-By Header

| Field | Value |
|-------|-------|
| **Template** | `http-misc/x-powered-by.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~85% |

**Indicators of False Positive:**
- Generic framework disclosure without version
- Common in development environments

**Example False Positive:**
```
[INFO] http-misc/x-powered-by - Target: https://example.com
X-Powered-By: PHP
```

**When It's NOT a False Positive:**
- Specific version: `X-Powered-By: PHP/7.4.3` (check for known CVEs)
- Combined with other technology disclosures for fingerprinting

---

## Default Credentials False Positives

Automated tools often report default credentials that have been changed or are not actually default.

### Pattern: Default Admin Credentials

| Field | Value |
|-------|-------|
| **Template** | `http-misc/default-login.yaml` |
| **Severity** | High |
| **False Positive Rate** | ~60% |

**Indicators of False Positive:**
- Login page exists but credentials don't work
- Login page is a decoy/honeypot
- Default credentials have been changed but page remains
- Login requires additional factors (CAPTCHA, 2FA)

**Example False Positive:**
```
[HIGH] http-misc/default-login - Target: https://example.com/admin
Attempted: admin/admin, admin/password, admin/123456
Result: All failed
```

**How to Verify:**
```bash
# Manually test default credentials
curl -s -X POST https://example.com/login \
  -d "username=admin&password=admin" \
  -w "\n%{http_code}" | tail -1
# If login fails (401/403), this is a false positive
```

**When It's NOT a False Positive:**
- Default credentials actually work
- Login page reveals valid username in error messages
- Password reset uses default credentials

### Pattern: Default Database Credentials

| Field | Value |
|-------|-------|
| **Template** | `network-misc/default-db-credentials.yaml` |
| **Severity** | Critical |
| **False Positive Rate** | ~50% |

**Indicators of False Positive:**
- Database port is open but requires authentication
- Default credentials don't work
- Database is behind a firewall

---

## SSL/TLS Configuration False Positives

SSL/TLS scanning can produce many informational findings that are not actual vulnerabilities.

### Pattern: TLS Version Detection

| Field | Value |
|-------|-------|
| **Template** | `ssl-misc/tls-version.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~70% |

**Indicators of False Positive:**
- TLS 1.2 is flagged as "outdated" (it's still acceptable)
- TLS 1.3 is available but TLS 1.2 is also supported (normal)
- Certificate is valid and properly configured

**Example False Positive:**
```
[INFO] ssl-misc/tls-version - Target: example.com:443
Supported: TLSv1.2, TLSv1.3
```

**When It's NOT a False Positive:**
- TLS 1.0 or 1.1 is supported (deprecated)
- SSLv3 is supported (POODLE attack)
- Weak cipher suites are enabled (RC4, DES, 3DES)
- Certificate is self-signed in production
- Certificate has expired or is misconfigured

### Pattern: Certificate Information Disclosure

| Field | Value |
|-------|-------|
| **Template** | `ssl-misc/cert-info.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~90% |

**Indicators of False Positive:**
- Certificate contains organization name (standard)
- Certificate has SAN entries (normal)
- Certificate chain is valid

**When It's NOT a False Positive:**
- Certificate contains internal hostnames or IP addresses
- Certificate reveals internal domain structure
- Wildcard certificate is overly broad (`*.internal.example.com`)

---

## Information Disclosure False Positives

Information disclosure findings often flag publicly available information that is not sensitive.

### Pattern: Directory Listing

| Field | Value |
|-------|-------|
| **Template** | `http-misc/directory-listing.yaml` |
| **Severity** | Low |
| **False Positive Rate** | ~75% |

**Indicators of False Positive:**
- Directory listing on static asset directories (e.g., `/images/`, `/css/`)
- No sensitive files in the directory
- Directory listing is intentional (e.g., file browser)

**Example False Positive:**
```
[LOW] http-misc/directory-listing - Target: https://example.com/images/
Files: logo.png, banner.jpg, icons.svg
```

**When It's NOT a False Positive:**
- Directory listing on sensitive paths (`/backup/`, `/config/`, `/admin/`)
- Source code files are visible (`.php`, `.bak`, `.sql`)
- Configuration files are accessible (`.env`, `config.php`, `web.config`)
- Backup files are accessible (`.zip`, `.tar.gz`, `.bak`)

### Pattern: robots.txt Discovery

| Field | Value |
|-------|-------|
| **Template** | `http-misc/robots-txt.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~95% |

**Indicators of False Positive:**
- Standard robots.txt with `User-agent: *`
- No sensitive paths in Disallow directives
- robots.txt is publicly intended

**When It's NOT a False Positive:**
- robots.txt reveals sensitive admin paths
- robots.txt contains credentials or tokens
- robots.txt reveals internal application structure

### Pattern: Security Headers Missing

| Field | Value |
|-------|-------|
| **Template** | `http-misc/missing-headers.yaml` |
| **Severity** | Info |
| **False Positive Rate** | ~65% |

**Indicators of False Positive:**
- Missing `X-Powered-By` header (not a security risk)
- Missing `X-AspNet-Version` header (informational)
- Missing headers on static content (lower risk)

**When It's NOT a False Positive:**
- Missing `Content-Security-Policy` on dynamic pages
- Missing `X-Frame-Options` or `frame-ancestors` (clickjacking risk)
- Missing `Strict-Transport-Security` on HTTPS sites
- Missing `X-Content-Type-Options` (MIME sniffing risk)

---

## XSS False Positives

Cross-Site Scripting findings are notoriously prone to false positives.

### Pattern: Reflected XSS

| Field | Value |
|-------|-------|
| **Template** | `http-misc/reflected-xss.yaml` |
| **Severity** | Medium |
| **False Positive Rate** | ~70% |

**Indicators of False Positive:**
- Input is reflected but properly encoded
- Reflection is in a non-executable context (e.g., inside a `<title>` tag)
- Payload is reflected but browser doesn't execute it
- CSP header prevents execution

**Example False Positive:**
```
[MEDIUM] http-misc/reflected-xss - Target: https://example.com/search?q=<script>alert(1)</script>
Response: <title>Search: &lt;script&gt;alert(1)&lt;/script&gt;</title>
```

**How to Verify:**
```bash
# Check if the payload is properly encoded
curl -s "https://example.com/search?q=<script>alert(1)</script>" | grep -o '<script>alert(1)</script>'
# If the payload appears unencoded in the response, it might be vulnerable
# If it appears as &lt;script&gt;, it's properly encoded (false positive)
```

**When It's NOT a False Positive:**
- Payload is reflected unencoded in HTML context
- Payload is reflected in JavaScript context without sanitization
- Payload is reflected in attribute context without quoting
- CSP is missing or misconfigured

### Pattern: DOM-based XSS

| Field | Value |
|-------|-------|
| **Template** | `http-misc/dom-xss.yaml` |
| **Severity** | Medium |
| **False Positive Rate** | ~80% |

**Indicators of False Positive:**
- Sink is not actually dangerous (e.g., `console.log`)
- Source is not user-controllable
- Data is sanitized before reaching the sink

---

## SQL Injection False Positives

SQL injection findings require careful verification to avoid false positives.

### Pattern: Error-based SQL Injection

| Field | Value |
|-------|-------|
| **Template** | `http-misc/sqli-error.yaml` |
| **Severity** | High |
| **False Positive Rate** | ~60% |

**Indicators of False Positive:**
- SQL error is from a different cause (e.g., malformed request)
- Error message is generic and doesn't reveal database structure
- Error is not triggered by SQL-specific payloads
- Application uses parameterized queries but has verbose error handling

**Example False Positive:**
```
[HIGH] http-misc/sqli-error - Target: https://example.com/product?id=1'
Response: Error: You have an error in your SQL syntax...
```

**How to Verify:**
```bash
# Test with a known SQL injection payload
curl -s "https://example.com/product?id=1' OR '1'='1" | grep -i "error\|warning\|mysql\|sql"
# If the payload doesn't change the response, it's likely a false positive
# Test with a benign payload for comparison
curl -s "https://example.com/product?id=1" | wc -c
curl -s "https://example.com/product?id=1' OR '1'='1" | wc -c
# If response sizes are identical, likely a false positive
```

**When It's NOT a False Positive:**
- SQL error messages reveal database type and structure
- Payloads produce different responses (time-based, boolean-based)
- UNION-based injection extracts data
- Error messages differ between valid and invalid SQL syntax

### Pattern: Blind SQL Injection

| Field | Value |
|-------|-------|
| **Template** | `http-misc/sqli-blind.yaml` |
| **Severity** | High |
| **False Positive Rate** | ~75% |

**Indicators of False Positive:**
- Response time variation is within normal network jitter
- Boolean-based responses are inconsistent
- No clear difference between true and false conditions

---

## Open Port False Positives (Masscan)

Masscan is extremely fast but can produce false positives due to its SYN scanning technique.

### Pattern: Masscan Open Port Detection

| Field | Value |
|-------|-------|
| **Tool** | masscan |
| **Severity** | Info |
| **False Positive Rate** | ~40% |

**Indicators of False Positive:**
- Port appears open in masscan but closed in nmap
- Port is a common false positive (e.g., 111, 135, 139, 445 on Windows)
- No actual service responds on the port
- Firewall or IDS is responding to SYN packets

**Example False Positive:**
```
[INFO] masscan - Target: 192.168.1.1
Open ports: 22, 80, 443, 3389, 8080
# nmap shows only 22, 80, 443 are actually open
```

**How to Verify:**
```bash
# Always verify masscan results with nmap
nmap -sV -sC -p <masscan-ports> <target>
# Compare results - only report ports confirmed by nmap
```

**Common Masscan False Positive Ports:**
| Port | Service | Reason |
|------|---------|--------|
| 111 | rpcbind | Often shows open due to firewall responses |
| 135 | msrpc | Windows firewall responds to SYN |
| 139 | netbios | Windows firewall responds to SYN |
| 445 | smb | Windows firewall responds to SYN |
| 3389 | rdp | Sometimes shows open when filtered |
| 8080 | http-proxy | Common honeypot or firewall response |

**When It's NOT a False Positive:**
- nmap confirms the port is open
- A service banner is captured
- The port responds to actual connections

---

## Quick Reference: False Positive Decision Tree

```
Is the finding from an automated scanner?
├── YES → Is the severity "info" or "low"?
│   ├── YES → Likely false positive (verify manually)
│   └── NO → Continue evaluation
└── NO → Trust the finding (manual verification)

Does the finding include proof-of-concept?
├── YES → Is the PoC reliable and repeatable?
│   ├── YES → Likely true positive
│   └── NO → Likely false positive
└── NO → Requires manual verification

Is the finding consistent across multiple tools?
├── YES → Higher confidence in true positive
└── NO → Investigate discrepancies
```

---

## Reporting False Positives

When reporting false positives, include:

1. **Finding ID**: The original finding identifier
2. **Tool**: Which tool generated the false positive
3. **Pattern Matched**: Which false positive pattern was matched
4. **Evidence**: Why this is a false positive
5. **Verification Method**: How you confirmed it's a false positive
6. **Recommendation**: Whether to suppress this pattern in future scans

Example:
```json
{
  "finding_id": "VULN-0042",
  "tool": "nuclei",
  "pattern": "generic-404-detection",
  "reason": "Standard 404 page with no sensitive information disclosure",
  "verification": "Manually confirmed response is standard nginx 404 page",
  "recommendation": "Suppress http-misc/404-page for this target"
}
```
