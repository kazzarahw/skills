# False Positive Patterns and Mitigations

## Table of Contents

- [Web2 False Positive Patterns](#web2-false-positive-patterns)
- [1. Version Mismatch](#1-version-mismatch)
- [2. Configuration-Dependent](#2-configuration-dependent)
- [3. Authentication Required](#3-authentication-required)
- [4. Rate Limiting](#4-rate-limiting)
- [5. False Banner](#5-false-banner)
- [6. Default Page](#6-default-page)
- [7. Error Message Disclosure](#7-error-message-disclosure)
- [Web3 False Positive Patterns](#web3-false-positive-patterns)
- [1. Compiler Version](#1-compiler-version)
- [2. Proxy Implementation](#2-proxy-implementation)
- [3. Oracle Dependency](#3-oracle-dependency)
- [4. Access Control](#4-access-control)
- [5. Reorg](#5-reorg)
- [6. Test Coverage](#6-test-coverage)
- [7. Gas Optimization](#7-gas-optimization)
- [Cross-Domain False Positive Patterns](#cross-domain-false-positive-patterns)
- [1. Mixed Findings](#1-mixed-findings)
- [2. Chain Confusion](#2-chain-confusion)
- [Mitigation Strategies](#mitigation-strategies)
- [General Mitigation Strategies](#general-mitigation-strategies)
- [Web2 Mitigation Strategies](#web2-mitigation-strategies)
- [Web3 Mitigation Strategies](#web3-mitigation-strategies)
- [False Positive Rate Tracking](#false-positive-rate-tracking)
- [Tracking Format](#tracking-format)
- [Tracking Procedure](#tracking-procedure)
- [Target False Positive Rates](#target-false-positive-rates)

Common false positive patterns in security verification and their mitigations. Every finding must be checked against these patterns before receiving a VERIFIED verdict.

---

## Web2 False Positive Patterns

### 1. Version Mismatch

**Pattern**: The CVE or vulnerability applies to a different version of the software than what is running on the target.

**Description**: The scanner or tool reports a vulnerability based on version detection, but the target is running a different version that is not affected.

**Detection**:
```bash
# Check exact version
nmap -sV -p <port> <host> --version-intensity 9
curl -sI http://<host>:<port>/ | grep -i "server\|x-powered-by"
```

**Mitigation**:
- Verify the exact version of the target software
- Cross-reference the CVE with the target version
- Test the vulnerability directly, not just version-based detection

**Frequency**: Common

---

### 2. Configuration-Dependent

**Pattern**: The vulnerability only exists in a specific configuration that is not present on the target.

**Description**: The vulnerability requires a specific configuration (e.g., debug mode enabled, specific header, specific setting) that is not present on the target.

**Detection**:
```bash
# Check configuration
curl -s http://<host>:<port>/ | grep -i "debug\|verbose\|test"
curl -sI http://<host>:<port>/ | grep -i "x-debug\|x-environment"
```

**Mitigation**:
- Test the vulnerability in the target's actual configuration
- Verify the configuration matches the vulnerability requirements
- Do not assume default configuration

**Frequency**: Common

---

### 3. Authentication Required

**Pattern**: The vulnerability requires authentication, but the test was performed without valid credentials.

**Description**: The vulnerability is only accessible to authenticated users, but the test was performed anonymously or with invalid credentials.

**Detection**:
```bash
# Test without authentication
curl -s -o /dev/null -w "%{http_code}" http://<host>:<port>/api/endpoint

# Test with authentication
curl -s -o /dev/null -w "%{http_code}" -H "Cookie: session=<valid>" http://<host>:<port>/api/endpoint
```

**Mitigation**:
- Test with valid credentials
- Verify the vulnerability is accessible with the credentials used
- Document the authentication requirements

**Frequency**: Frequent

---

### 4. Rate Limiting

**Pattern**: The scan or test was blocked by rate limiting or WAF, producing a false positive.

**Description**: The target has rate limiting or WAF that blocks the test, but the block is interpreted as a vulnerability.

**Detection**:
```bash
# Check for rate limiting
curl -sI http://<host>:<port>/ | grep -i "retry-after\|x-ratelimit\|x-waf"

# Test with delays
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code}\n" http://<host>:<port>/
  sleep 1
done
```

**Mitigation**:
- Use rate limiting in tests
- Add delays between requests
- Identify and bypass WAF (if authorized)
- Verify the response is not a WAF block page

**Frequency**: Common

---

### 5. False Banner

**Pattern**: The service banner is spoofed or misleading, leading to incorrect version or service identification.

**Description**: The service returns a false banner that does not match the actual service, leading to incorrect vulnerability identification.

**Detection**:
```bash
# Compare banner with actual behavior
nc -w 5 <host> <port> < /dev/null
curl -v http://<host>:<port>/ 2>&1 | head -20

# Protocol-specific probe
openssl s_client -connect <host>:443 -servername <host> </dev/null 2>&1 | openssl x509 -noout -text
```

**Mitigation**:
- Use protocol-specific probes to verify the service
- Compare banner with actual behavior
- Use multiple detection methods
- Do not rely solely on banner grabbing

**Frequency**: Common

---

### 6. Default Page

**Pattern**: The response is a default page (e.g., Apache default page, Tomcat default page) that is misidentified as a vulnerability.

**Description**: The target returns a default page that is misidentified as a vulnerability or sensitive information.

**Detection**:
```bash
# Check for default pages
curl -s http://<host>:<port>/ | grep -i "apache\|tomcat\|nginx\|iis\|default"

# Compare with known default pages
curl -s http://<host>:<port>/ | diff - <(curl -s http://<known-default-page>/)
```

**Mitigation**:
- Compare response with known default pages
- Verify the content is actually sensitive or vulnerable
- Do not report default pages as vulnerabilities

**Frequency**: Common

---

### 7. Error Message Disclosure

**Pattern**: The error message is misidentified as a vulnerability, but it is actually expected behavior.

**Description**: The target returns an error message that is misidentified as information disclosure, but it is actually expected behavior for the input.

**Detection**:
```bash
# Test with valid input
curl -s http://<host>:<port>/api/endpoint?param=valid

# Test with invalid input
curl -s http://<host>:<port>/api/endpoint?param=invalid

# Compare
diff <(curl -s http://<host>:<port>/api/endpoint?param=valid) <(curl -s http://<host>:<port>/api/endpoint?param=invalid)
```

**Mitigation**:
- Compare error messages with valid input
- Verify the error message is not expected behavior
- Do not report standard error messages as vulnerabilities

**Frequency**: Common

---

## Web3 False Positive Patterns

### 1. Compiler Version

**Pattern**: The vulnerability only exists in a specific Solidity compiler version that is not used by the target.

**Description**: The vulnerability is specific to a certain compiler version (e.g., `solc 0.4.x`) but the target uses a different version.

**Detection**:
```bash
# Check compiler version
cast interface <contract> --rpc-url $RPC_URL | grep "compiler"
# Or check on block explorer
```

**Mitigation**:
- Verify the compiler version of the target contract
- Cross-reference the vulnerability with the compiler version
- Test the vulnerability directly, not just version-based detection

**Frequency**: Common

---

### 2. Proxy Implementation

**Pattern**: The vulnerability is in the implementation contract, not the proxy contract that is actually used.

**Description**: The target is a proxy contract that delegates to an implementation contract. The vulnerability may be in the implementation, not the proxy.

**Detection**:
```bash
# Check if contract is a proxy
cast code <contract> --rpc-url $RPC_URL | grep -i "delegatecall\|proxy"

# Check implementation slot
cast storage <contract> 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc --rpc-url $RPC_URL
```

**Mitigation**:
- Verify both the proxy and implementation contracts
- Test the vulnerability on the actual implementation
- Document the proxy-implementation relationship

**Frequency**: Common

---

### 3. Oracle Dependency

**Pattern**: The vulnerability requires a specific oracle state that is not present on the target chain.

**Description**: The vulnerability depends on a specific oracle price or state that is not present on the target chain.

**Detection**:
```bash
# Check oracle state
cast call <oracle_contract> "latestAnswer()(int256)" --rpc-url $RPC_URL

# Check if oracle is manipulated
cast call <oracle_contract> "getAnswer()(int256)" --rpc-url $RPC_URL
```

**Mitigation**:
- Verify the oracle state on the target chain
- Test with the actual oracle state
- Simulate the oracle state in a fork test

**Frequency**: Common

---

### 4. Access Control

**Pattern**: The function requires a specific role or permission that is not available to the test account.

**Description**: The vulnerability is in a function that requires a specific role, but the test account does not have that role.

**Detection**:
```bash
# Check access control
cast call <contract> "hasRole(bytes32,address)(bool)" <role> <test_address> --rpc-url $RPC_URL

# Check function requirements
cast call <contract> "<function>()" --from <test_address> --rpc-url $RPC_URL
```

**Mitigation**:
- Verify the access control requirements
- Test with an account that has the required role
- Document the access control requirements

**Frequency**: Frequent

---

### 5. Reorg

**Pattern**: The state change is due to a chain reorg, not the vulnerability.

**Description**: The observed state change is due to a chain reorganization, not the vulnerability being tested.

**Detection**:
```bash
# Wait for finality
cast block-number --rpc-url $RPC_URL
# Wait for 12+ blocks (Ethereum) or appropriate finality for target chain

# Verify state after finality
cast storage <contract> <slot> --rpc-url $RPC_URL
```

**Mitigation**:
- Wait for sufficient finality before verifying
- Verify state after finality
- Do not verify state changes that are not finalized

**Frequency**: Common

---

### 6. Test Coverage

**Pattern**: The vulnerability is covered by tests, but the tests do not actually verify the vulnerability.

**Description**: The contract has tests that appear to cover the vulnerability, but the tests do not actually verify the vulnerability.

**Detection**:
```bash
# Run tests
forge test --match-contract <Contract> --fork-url $RPC_URL

# Check test coverage
forge coverage --match-contract <Contract> --fork-url $RPC_URL
```

**Mitigation**:
- Review the tests to verify they actually test the vulnerability
- Write additional tests if needed
- Do not rely solely on existing tests

**Frequency**: Common

---

### 7. Gas Optimization

**Pattern**: The vulnerability is a gas optimization issue, not a security vulnerability.

**Description**: The finding is a gas optimization issue that does not affect the security of the contract.

**Detection**:
```bash
# Check if the issue affects security
# Gas optimization issues are not security vulnerabilities
```

**Mitigation**:
- Verify the issue affects security, not just gas
- Do not report gas optimization issues as security vulnerabilities
- Document the difference between gas and security issues

**Frequency**: Common

---

## Cross-Domain False Positive Patterns

### 1. Mixed Findings

**Pattern**: The finding mixes web2 and web3 components, but only one component is actually vulnerable.

**Description**: The finding claims a cross-domain vulnerability, but only the web2 or web3 component is actually vulnerable.

**Detection**:
```bash
# Verify web2 component
curl -s "<web2_url>" | tee evidence/web2.txt

# Verify web3 component
cast call <contract> "<function>()" --rpc-url $RPC_URL | tee evidence/web3.txt

# Verify interaction
curl -s -X POST "<web2_url>/api/web3" -d "action=exploit" | tee evidence/interaction.txt
```

**Mitigation**:
- Verify each component independently
- Verify the interaction between components
- Do not assume cross-domain vulnerability without evidence

**Frequency**: Common

---

### 2. Chain Confusion

**Pattern**: The finding confuses different chains or networks.

**Description**: The finding claims a vulnerability on one chain, but the evidence is from a different chain.

**Detection**:
```bash
# Verify chain ID
cast chain-id --rpc-url $RPC_URL

# Verify contract address
cast code <contract> --rpc-url $RPC_URL

# Verify transaction
cast tx <tx_hash> --rpc-url $RPC_URL
```

**Mitigation**:
- Verify the chain ID
- Verify the contract address on the correct chain
- Verify the transaction on the correct chain
- Do not confuse different chains or networks

**Frequency**: Common

---

## Mitigation Strategies

### General Mitigation Strategies

1. **Verify directly**: Test the vulnerability directly, not just based on version or banner
2. **Use multiple methods**: Use multiple detection methods to confirm the finding
3. **Check configuration**: Verify the target's actual configuration
4. **Test with valid credentials**: Test with valid credentials when authentication is required
5. **Wait for finality**: Wait for sufficient finality before verifying on-chain findings
6. **Review evidence**: Review all evidence before declaring a finding VERIFIED

### Web2 Mitigation Strategies

1. **Version verification**: Verify the exact version of the target software
2. **Configuration testing**: Test in the target's actual configuration
3. **Authentication testing**: Test with valid credentials
4. **Rate limiting**: Use rate limiting in tests
5. **Banner verification**: Use protocol-specific probes to verify the service

### Web3 Mitigation Strategies

1. **Compiler version**: Verify the compiler version of the target contract
2. **Proxy verification**: Verify both proxy and implementation contracts
3. **Oracle state**: Verify the oracle state on the target chain
4. **Access control**: Verify the access control requirements
5. **Finality**: Wait for sufficient finality before verifying

---

## False Positive Rate Tracking

### Tracking Format

```yaml
false_positive_tracking:
  total_findings: 100
  true_positives: 75
  false_positives: 25
  false_positive_rate: 25%
  by_pattern:
    version_mismatch: 5
    configuration_dependent: 3
    authentication_required: 4
    rate_limiting: 2
    false_banner: 1
    default_page: 1
    error_message_disclosure: 2
    compiler_version: 1
    proxy_implementation: 2
    oracle_dependency: 1
    access_control: 2
    reorg: 1
```

### Tracking Procedure

1. Record every finding and its verdict
2. For each false positive, record the pattern
3. Calculate the false positive rate
4. Identify patterns with high false positive rates
5. Adjust verification procedures to reduce false positive rates

### Target False Positive Rates

| Finding Type | Target FP Rate |
|--------------|----------------|
| Network findings | Low |
| Web findings | Low |
| Authentication findings | Low |
| Authorization findings | Low |
| Cryptography findings | Very low |
| Web3 findings | Low |
| Cross-domain findings | Low |
