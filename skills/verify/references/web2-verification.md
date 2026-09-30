# Web2-Specific Verification Procedures

## Table of Contents

- [1. Network Findings](#1-network-findings)
- [1.1 Nmap Verification](#11-nmap-verification)
- [1.2 Banner Grabbing](#12-banner-grabbing)
- [1.3 Service Confirmation](#13-service-confirmation)
- [2. Web Findings](#2-web-findings)
- [2.1 Curl Verification](#21-curl-verification)
- [2.2 Burp Suite Verification](#22-burp-suite-verification)
- [2.3 Browser Verification](#23-browser-verification)
- [3. Authentication Findings](#3-authentication-findings)
- [3.1 Credential Testing](#31-credential-testing)
- [3.2 Session Testing](#32-session-testing)
- [4. Authorization Findings](#4-authorization-findings)
- [4.1 Access Control Testing](#41-access-control-testing)
- [4.2 Privilege Escalation Testing](#42-privilege-escalation-testing)
- [5. Exploit Verification](#5-exploit-verification)
- [5.1 Multiple Indicators](#51-multiple-indicators)
- [5.2 Side-Effect Assertions](#52-side-effect-assertions)
- [5.3 Reproducibility](#53-reproducibility)
- [6. Evidence Capture](#6-evidence-capture)
- [6.1 Screenshots](#61-screenshots)
- [6.2 Command Output](#62-command-output)
- [6.3 HTTP Requests/Responses](#63-http-requestsresponses)
- [7. Verification Checklist](#7-verification-checklist)
- [Network Findings](#network-findings)
- [Web Findings](#web-findings)
- [Authentication Findings](#authentication-findings)
- [Authorization Findings](#authorization-findings)
- [Exploit Verification](#exploit-verification)

Detailed verification procedures for web2 findings. Each procedure includes the exact commands, expected output, and pass/fail criteria.

---

## 1. Network Findings

### 1.1 Nmap Verification

**Purpose**: Verify that a port is actually open and identify the service running on it.

**Procedure**:
```bash
# Basic port scan
nmap -p <port> <host> --reason -oN evidence/nmap-basic.txt

# Service version detection
nmap -sV -p <port> <host> --version-intensity 9 -oN evidence/nmap-version.txt

# OS detection (if needed)
nmap -O -p <port> <host> -oN evidence/nmap-os.txt

# Full scan (all ports)
nmap -p- <host> --reason -oN evidence/nmap-full.txt
```

**Pass criteria**:
- Port state is `open` (not `open|filtered`)
- Service version is detected and matches expected service
- Result is consistent across multiple runs

**Fail criteria**:
- Port state is `filtered` or `closed`
- Service version does not match expected service
- Result varies across runs

---

### 1.2 Banner Grabbing

**Purpose**: Verify the service banner and confirm the service is real.

**Procedure**:
```bash
# Raw banner capture
nc -w 5 <host> <port> < /dev/null 2>&1 | tee evidence/banner-raw.txt

# HTTP banner
curl -v http://<host>:<port>/ 2>&1 | tee evidence/banner-http.txt

# HTTPS banner
openssl s_client -connect <host>:<port> -servername <host> </dev/null 2>&1 | tee evidence/banner-https.txt

# SMTP banner
nc -w 5 <host> 25 < /dev/null 2>&1 | tee evidence/banner-smtp.txt

# FTP banner
nc -w 5 <host> 21 < /dev/null 2>&1 | tee evidence/banner-ftp.txt
```

**Pass criteria**:
- Banner matches expected service fingerprint
- Banner is consistent across multiple runs
- Service responds correctly to protocol-specific probes

**Fail criteria**:
- Banner does not match expected service fingerprint
- Banner varies across runs
- Service does not respond to protocol-specific probes

---

### 1.3 Service Confirmation

**Purpose**: Confirm the service is actually running and responding as expected.

**Procedure**:
```bash
# HTTP service confirmation
curl -s -o /dev/null -w "HTTP %{http_code} | Size: %{size_download} | Time: %{time_total}s\n" http://<host>:<port>/

# DNS service confirmation
dig @<host> <domain> +short

# SMTP service confirmation
swaks --to test@example.com --from test@example.com --server <host> --port 25

# Database service confirmation
mysql -h <host> -P <port> -u root -e "SELECT 1" 2>&1
psql -h <host> -p <port> -U postgres -c "SELECT 1" 2>&1
```

**Pass criteria**:
- Service responds correctly to protocol-specific commands
- Response is consistent with expected service behavior
- Response is consistent across multiple runs

**Fail criteria**:
- Service does not respond to protocol-specific commands
- Response is inconsistent with expected service behavior
- Response varies across runs

---

## 2. Web Findings

### 2.1 Curl Verification

**Purpose**: Verify web vulnerabilities using curl.

**Procedure**:
```bash
# Basic request
curl -v -X POST <url> -d '<payload>' 2>&1 | tee evidence/curl-basic.txt

# Request with headers
curl -v -X POST <url> -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '<payload>' 2>&1 | tee evidence/curl-headers.txt

# Request with cookies
curl -v -X POST <url> -b "session=<session_cookie>" -d '<payload>' 2>&1 | tee evidence/curl-cookies.txt

# Request with file upload
curl -v -X POST <url> -F "file=@/path/to/file" 2>&1 | tee evidence/curl-upload.txt

# Request with proxy
curl -v -X POST <url> -x http://proxy:8080 -d '<payload>' 2>&1 | tee evidence/curl-proxy.txt
```

**Pass criteria**:
- Response matches expected vulnerability behavior
- Response is consistent across multiple runs
- Side-effect assertions pass

**Fail criteria**:
- Response does not match expected vulnerability behavior
- Response varies across runs
- Side-effect assertions fail

---

### 2.2 Burp Suite Verification

**Purpose**: Verify web vulnerabilities using Burp Suite.

**Procedure**:
```bash
# Start Burp Suite in headless mode (if available)
# Or use Burp Suite API

# Send request to Burp Suite
curl -s -X POST "http://localhost:8080/v0.1/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["<url>"],
    "scope": {
      "include": [{"rule": "<url>"}]
    }
  }' | tee evidence/burp-scan.txt

# Get scan results
curl -s "http://localhost:8080/v0.1/scan/<scan_id>" | tee evidence/burp-results.txt
```

**Pass criteria**:
- Burp Suite confirms the vulnerability
- Burp Suite results match expected vulnerability behavior
- Results are consistent across multiple runs

**Fail criteria**:
- Burp Suite does not confirm the vulnerability
- Burp Suite results do not match expected vulnerability behavior
- Results vary across runs

---

### 2.3 Browser Verification

**Purpose**: Verify web vulnerabilities using a real browser.

**Procedure**:
```bash
# Using Puppeteer (Node.js)
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({headless: true});
  const page = await browser.newPage();
  
  // Capture console logs
  page.on('console', msg => console.log('CONSOLE:', msg.text()));
  
  // Capture dialogs (alert, confirm, prompt)
  page.on('dialog', async dialog => {
    console.log('DIALOG:', dialog.type(), dialog.message());
    await dialog.accept();
  });
  
  // Navigate to target
  await page.goto('<url>', {waitUntil: 'networkidle0'});
  
  // Execute payload
  await page.evaluate(() => {
    // Payload execution
  });
  
  // Capture screenshot
  await page.screenshot({path: 'evidence/browser-screenshot.png'});
  
  await browser.close();
})();
" 2>&1 | tee evidence/browser-verification.txt

# Using Playwright (Python)
python3 -c "
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Capture console logs
    page.on('console', lambda msg: print(f'CONSOLE: {msg.text}'))
    
    # Capture dialogs
    page.on('dialog', lambda dialog: print(f'DIALOG: {dialog.type} {dialog.message}'))
    
    # Navigate to target
    page.goto('<url>')
    
    # Execute payload
    page.evaluate('() => { /* payload */ }')
    
    # Capture screenshot
    page.screenshot(path='evidence/browser-screenshot.png')
    
    browser.close()
" 2>&1 | tee evidence/browser-verification.txt
```

**Pass criteria**:
- Browser confirms the vulnerability (e.g., alert fires, DOM is modified)
- Browser behavior matches expected vulnerability behavior
- Behavior is consistent across multiple runs

**Fail criteria**:
- Browser does not confirm the vulnerability
- Browser behavior does not match expected vulnerability behavior
- Behavior varies across runs

---

## 3. Authentication Findings

### 3.1 Credential Testing

**Purpose**: Verify that credentials are valid and work as expected.

**Procedure**:
```bash
# Test default credentials
curl -s -X POST "<url>/login" -d "username=admin&password=admin" | tee evidence/creds-default.txt

# Test weak credentials
curl -s -X POST "<url>/login" -d "username=admin&password=password123" | tee evidence/creds-weak.txt

# Test SQL injection in login
curl -s -X POST "<url>/login" -d "username=admin'--&password=anything" | tee evidence/creds-sqli.txt

# Test brute force (with rate limiting)
for i in $(seq 1 100); do
  curl -s -X POST "<url>/login" -d "username=admin&password=guess$i" -o /dev/null -w "%{http_code}\n"
  sleep 0.5
done | tee evidence/creds-bruteforce.txt
```

**Pass criteria**:
- Credentials work as expected
- Response is consistent with expected behavior
- Response is consistent across multiple runs

**Fail criteria**:
- Credentials do not work
- Response is inconsistent with expected behavior
- Response varies across runs

---

### 3.2 Session Testing

**Purpose**: Verify session management vulnerabilities.

**Procedure**:
```bash
# Session fixation test
curl -s -c cookies.txt "<url>/login" -o /dev/null
curl -s -b cookies.txt -X POST "<url>/login" -d "username=admin&password=admin" -o /dev/null
curl -s -b cookies.txt "<url>/api/profile" | tee evidence/session-fixation.txt

# Session expiration test
sleep 3600  # Wait for timeout
curl -s -b cookies.txt "<url>/api/profile" | tee evidence/session-expired.txt

# Session invalidation test
curl -s -b cookies.txt -X POST "<url>/logout" -o /dev/null
curl -s -b cookies.txt "<url>/api/profile" | tee evidence/session-invalidated.txt

# Session token analysis
cat cookies.txt | awk '{print $7}' | tee evidence/session-token.txt
```

**Pass criteria**:
- Session vulnerability is confirmed
- Behavior is consistent with expected vulnerability behavior
- Behavior is consistent across multiple runs

**Fail criteria**:
- Session vulnerability is not confirmed
- Behavior is inconsistent with expected vulnerability behavior
- Behavior varies across runs

---

## 4. Authorization Findings

### 4.1 Access Control Testing

**Purpose**: Verify access control vulnerabilities.

**Procedure**:
```bash
# Horizontal access control test
curl -s -H "Cookie: session=<user1>" "<url>/api/user/1/profile" | tee evidence/access-user1.txt
curl -s -H "Cookie: session=<user1>" "<url>/api/user/2/profile" | tee evidence/access-user2.txt

# Vertical access control test
curl -s -H "Cookie: session=<user1>" "<url>/api/admin/users" | tee evidence/access-admin.txt

# Function-level access control test
curl -s -H "Cookie: session=<user1>" -X POST "<url>/api/admin/delete-user" -d "id=2" | tee evidence/access-function.txt

# Object-level access control test
curl -s -H "Cookie: session=<user1>" "<url>/api/documents/2" | tee evidence/access-object.txt
```

**Pass criteria**:
- Access control vulnerability is confirmed
- Behavior is consistent with expected vulnerability behavior
- Behavior is consistent across multiple runs

**Fail criteria**:
- Access control vulnerability is not confirmed
- Behavior is inconsistent with expected vulnerability behavior
- Behavior varies across runs

---

### 4.2 Privilege Escalation Testing

**Purpose**: Verify privilege escalation vulnerabilities.

**Procedure**:
```bash
# Role modification test
curl -s -H "Cookie: session=<user>" -H "X-Role: admin" "<url>/api/admin/users" | tee evidence/privesc-role.txt

# Client-side role bypass test
curl -s -H "Cookie: session=<user>" "<url>/api/profile" -d "role=admin" | tee evidence/privesc-client.txt

# Missing role check test
curl -s -H "Cookie: session=<user>" "<url>/api/admin/config" | tee evidence/privesc-missing.txt

# Privilege escalation persistence test
curl -s -H "Cookie: session=<user>" "<url>/api/profile" | tee evidence/privesc-persist.txt
```

**Pass criteria**:
- Privilege escalation vulnerability is confirmed
- Behavior is consistent with expected vulnerability behavior
- Behavior is consistent across multiple runs

**Fail criteria**:
- Privilege escalation vulnerability is not confirmed
- Behavior is inconsistent with expected vulnerability behavior
- Behavior varies across runs

---

## 5. Exploit Verification

### 5.1 Multiple Indicators

**Purpose**: Verify exploit success using multiple independent indicators.

**Procedure**:
```bash
# Indicator 1: Command output
<exploit-command> 2>&1 | tee evidence/indicator-1.txt

# Indicator 2: File creation
ls -la /path/to/created/file 2>&1 | tee evidence/indicator-2.txt

# Indicator 3: Network callback
# Start listener
nc -l -p 4444 > evidence/indicator-3.txt &
# Run exploit
<exploit-command> 2>&1 | tee evidence/indicator-3-exploit.txt
# Wait for callback
sleep 5
cat evidence/indicator-3.txt

# Indicator 4: Process creation
ps aux | grep <process-name> | tee evidence/indicator-4.txt

# Indicator 5: Database change
mysql -h <host> -u root -e "SELECT * FROM <table>" | tee evidence/indicator-5.txt
```

**Pass criteria**:
- Multiple independent indicators confirm exploit success
- Indicators are consistent with expected exploit behavior
- Indicators are consistent across multiple runs

**Fail criteria**:
- Indicators do not confirm exploit success
- Indicators are inconsistent with expected exploit behavior
- Indicators vary across runs

---

### 5.2 Side-Effect Assertions

**Purpose**: Verify exploit success using side-effect assertions.

**Procedure**:
```bash
# File existence assertion
if [ -f /path/to/created/file ]; then
  echo "PASS: File exists"
  ls -la /path/to/created/file | tee evidence/assertion-file.txt
else
  echo "FAIL: File does not exist"
fi

# Command output assertion
output=$(<command>)
if echo "$output" | grep -q "expected_string"; then
  echo "PASS: Output matches"
  echo "$output" | tee evidence/assertion-output.txt
else
  echo "FAIL: Output does not match"
fi

# Network callback assertion
# Start listener
nc -l -p 4444 > evidence/assertion-callback.txt &
# Run exploit
<exploit-command> 2>&1 | tee evidence/assertion-exploit.txt
# Wait for callback
sleep 5
if [ -s evidence/assertion-callback.txt ]; then
  echo "PASS: Callback received"
  cat evidence/assertion-callback.txt
else
  echo "FAIL: No callback received"
fi
```

**Pass criteria**:
- Side-effect assertions pass
- Assertions are consistent with expected exploit behavior
- Assertions are consistent across multiple runs

**Fail criteria**:
- Side-effect assertions fail
- Assertions are inconsistent with expected exploit behavior
- Assertions vary across runs

---

### 5.3 Reproducibility

**Purpose**: Verify that the exploit is reproducible.

**Procedure**:
```bash
# Run 1
<exploit-command> 2>&1 | tee evidence/repro-run-1.txt
# Side-effect check
ls -la /path/to/created/file 2>&1 | tee evidence/repro-run-1-assertion.txt

# Run 2
<exploit-command> 2>&1 | tee evidence/repro-run-2.txt
# Side-effect check
ls -la /path/to/created/file 2>&1 | tee evidence/repro-run-2-assertion.txt

# Run 3
<exploit-command> 2>&1 | tee evidence/repro-run-3.txt
# Side-effect check
ls -la /path/to/created/file 2>&1 | tee evidence/repro-run-3-assertion.txt

# Compare results
diff evidence/repro-run-1.txt evidence/repro-run-2.txt | tee evidence/repro-diff-1-2.txt
diff evidence/repro-run-2.txt evidence/repro-run-3.txt | tee evidence/repro-diff-2-3.txt
```

**Pass criteria**:
- Exploit produces the same result every run
- Side-effect assertions pass every run
- Results are consistent across all runs

**Fail criteria**:
- Exploit produces different results across runs
- Side-effect assertions fail on any run
- Results vary across runs

---

## 6. Evidence Capture

### 6.1 Screenshots

**Purpose**: Capture visual evidence of the vulnerability.

**Procedure**:
```bash
# Using Puppeteer
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({headless: true});
  const page = await browser.newPage();
  await page.goto('<url>');
  await page.screenshot({path: 'evidence/screenshot.png', fullPage: true});
  await browser.close();
})();
" 2>&1 | tee evidence/screenshot.txt

# Using Playwright
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('<url>')
    page.screenshot(path='evidence/screenshot.png', full_page=True)
    browser.close()
" 2>&1 | tee evidence/screenshot.txt
```

---

### 6.2 Command Output

**Purpose**: Capture raw command output as evidence.

**Procedure**:
```bash
# Capture stdout and stderr
<command> > evidence/command-stdout.txt 2> evidence/command-stderr.txt

# Capture with exit code
<command> > evidence/command-output.txt 2>&1
echo "Exit code: $?" | tee evidence/command-exit-code.txt

# Capture with timestamp
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" | tee evidence/command-timestamp.txt
<command> 2>&1 | tee evidence/command-output.txt
```

---

### 6.3 HTTP Requests/Responses

**Purpose**: Capture HTTP requests and responses as evidence.

**Procedure**:
```bash
# Using curl
curl -v -X POST <url> -d '<payload>' 2>&1 | tee evidence/http-curl.txt

# Using Burp Suite
# Configure Burp Suite to save requests/responses
# Or use Burp Suite API

# Using mitmproxy
mitmproxy -w evidence/http-mitmproxy.flow &
# Run exploit
<exploit-command> 2>&1 | tee evidence/http-exploit.txt
# Stop mitmproxy
kill %1
```

---

## 7. Verification Checklist

### Network Findings

- [ ] Port is open (not filtered)
- [ ] Service banner is real (not spoofed)
- [ ] Service responds correctly to protocol-specific probes
- [ ] Vulnerability is exploitable
- [ ] Vulnerability is not patched
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (nmap output, banner, protocol check)

### Web Findings

- [ ] Payload is reflected/executed
- [ ] Payload is not sanitized
- [ ] Payload bypasses WAF (if applicable)
- [ ] Context is appropriate
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (curl output, browser screenshot)

### Authentication Findings

- [ ] Credentials work
- [ ] Session vulnerability is confirmed
- [ ] MFA bypass works (if applicable)
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (login response, session token)

### Authorization Findings

- [ ] Privilege escalation works
- [ ] Access control vulnerability is confirmed
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (access response, role modification)

### Exploit Verification

- [ ] Multiple indicators confirm success
- [ ] Side-effect assertions pass
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (command output, file existence, network callback)
