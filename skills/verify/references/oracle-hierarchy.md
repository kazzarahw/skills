# Verification Oracle Selection Guide

## Table of Contents

- [Oracle Hierarchy](#oracle-hierarchy)
- [Tier 1: Deterministic Oracles (Strongest)](#tier-1-deterministic-oracles-strongest)
- [1.1 File Exists](#11-file-exists)
- [1.2 Command Output](#12-command-output)
- [1.3 Network Callback](#13-network-callback)
- [1.4 Transaction State Change](#14-transaction-state-change)
- [Tier 2: Specialist Oracles](#tier-2-specialist-oracles)
- [2.1 On-Chain Balance Check](#21-on-chain-balance-check)
- [2.2 Storage Slot Verification](#22-storage-slot-verification)
- [2.3 Event Log Verification](#23-event-log-verification)
- [2.4 HTTP Response Check](#24-http-response-check)
- [2.5 Process Check](#25-process-check)
- [2.6 Port Check](#26-port-check)
- [Tier 3: Self-Reflective Oracles (Weakest)](#tier-3-self-reflective-oracles-weakest)
- [3.1 Model Judgment](#31-model-judgment)
- [3.2 Output Matching](#32-output-matching)
- [3.3 Pattern Matching](#33-pattern-matching)
- [Oracle Selection Criteria](#oracle-selection-criteria)
- [1. Determinism](#1-determinism)
- [2. Independence](#2-independence)
- [3. Specificity](#3-specificity)
- [4. Strength](#4-strength)
- [5. Availability](#5-availability)
- [Oracle Combination Strategies](#oracle-combination-strategies)
- [Strategy 1: Multiple Deterministic Oracles](#strategy-1-multiple-deterministic-oracles)
- [Strategy 2: Deterministic + Specialist Oracles](#strategy-2-deterministic--specialist-oracles)
- [Strategy 3: Multiple Specialist Oracles](#strategy-3-multiple-specialist-oracles)
- [Strategy 4: Deterministic + Specialist + Self-Reflective Oracles](#strategy-4-deterministic--specialist--self-reflective-oracles)
- [Oracle Limitations and Failure Modes](#oracle-limitations-and-failure-modes)
- [Deterministic Oracle Limitations](#deterministic-oracle-limitations)
- [Specialist Oracle Limitations](#specialist-oracle-limitations)
- [Self-Reflective Oracle Limitations](#self-reflective-oracle-limitations)
- [Oracle Selection Decision Tree](#oracle-selection-decision-tree)
- [Oracle Strength Comparison](#oracle-strength-comparison)
- [Best Practices](#best-practices)

The quality of verification is bounded by the oracle used. This guide describes the oracle hierarchy, selection criteria, and combination strategies.

---

## Oracle Hierarchy

### Tier 1: Deterministic Oracles (Strongest)

Deterministic oracles produce the same result every time and can be independently verified. They are the strongest form of verification.

#### 1.1 File Exists

**Description**: Check if a file exists on the filesystem.

**Use case**: Verify that a file was created, modified, or deleted.

**Command**:
```bash
if [ -f /path/to/file ]; then
  echo "PASS: File exists"
  ls -la /path/to/file
else
  echo "FAIL: File does not exist"
fi
```

**Strength**: Very strong — filesystem state is deterministic.

**Limitations**: Only verifies file existence, not content or integrity.

---

#### 1.2 Command Output

**Description**: Check the output of a command.

**Use case**: Verify that a command produces the expected output.

**Command**:
```bash
output=$(<command>)
if echo "$output" | grep -q "expected_string"; then
  echo "PASS: Output matches"
  echo "$output"
else
  echo "FAIL: Output does not match"
fi
```

**Strength**: Very strong — command output is deterministic.

**Limitations**: Only verifies output, not side effects.

---

#### 1.3 Network Callback

**Description**: Check if a network callback was received.

**Use case**: Verify that a network request was made to a specific endpoint.

**Command**:
```bash
# Start listener
nc -l -p 4444 > evidence/callback.txt &
LISTENER_PID=$!

# Run exploit
<exploit-command>

# Wait for callback
sleep 5

# Check callback
if [ -s evidence/callback.txt ]; then
  echo "PASS: Callback received"
  cat evidence/callback.txt
else
  echo "FAIL: No callback received"
fi

# Stop listener
kill $LISTENER_PID
```

**Strength**: Very strong — network callback is deterministic.

**Limitations**: Only verifies that a callback was received, not the content.

---

#### 1.4 Transaction State Change

**Description**: Check if a transaction changed the state of a contract.

**Use case**: Verify that a transaction modified contract storage.

**Command**:
```bash
# Before state
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-before.txt

# Execute transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL

# Wait for finality
sleep 15

# After state
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-after.txt

# Verify state change
if ! diff -q evidence/state-before.txt evidence/state-after.txt > /dev/null; then
  echo "PASS: State changed"
  diff evidence/state-before.txt evidence/state-after.txt
else
  echo "FAIL: State did not change"
fi
```

**Strength**: Very strong — blockchain state is deterministic.

**Limitations**: Only verifies state change, not the cause.

---

### Tier 2: Specialist Oracles

Specialist oracles are domain-specific checkers that require specialized knowledge or tools.

#### 2.1 On-Chain Balance Check

**Description**: Check the balance of an address on-chain.

**Use case**: Verify that funds were transferred.

**Command**:
```bash
cast balance <address> --rpc-url $RPC_URL
```

**Strength**: Strong — blockchain state is deterministic.

**Limitations**: Only verifies balance change, not the cause.

---

#### 2.2 Storage Slot Verification

**Description**: Verify the value of a specific storage slot.

**Use case**: Verify that a specific storage slot was modified.

**Command**:
```bash
cast storage <contract> <slot> --rpc-url $RPC_URL
```

**Strength**: Strong — blockchain state is deterministic.

**Limitations**: Only verifies storage slot value, not the cause.

---

#### 2.3 Event Log Verification

**Description**: Verify that an event was emitted.

**Use case**: Verify that a specific event was emitted with expected data.

**Command**:
```bash
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL
```

**Strength**: Strong — blockchain state is deterministic.

**Limitations**: Only verifies event emission, not the cause.

---

#### 2.4 HTTP Response Check

**Description**: Check the HTTP response from a web server.

**Use case**: Verify that a web server returned the expected response.

**Command**:
```bash
curl -s -o /dev/null -w "%{http_code}" <url>
```

**Strength**: Strong — HTTP response is deterministic.

**Limitations**: Only verifies HTTP response, not the cause.

---

#### 2.5 Process Check

**Description**: Check if a process is running.

**Use case**: Verify that a process was started or is running.

**Command**:
```bash
ps aux | grep <process-name>
```

**Strength**: Medium — process state can vary.

**Limitations**: Only verifies process existence, not the cause.

---

#### 2.6 Port Check

**Description**: Check if a port is open.

**Use case**: Verify that a service is listening on a port.

**Command**:
```bash
nc -zv -w 5 <host> <port>
```

**Strength**: Medium — port state can vary.

**Limitations**: Only verifies port state, not the service.

---

### Tier 3: Self-Reflective Oracles (Weakest)

Self-reflective oracles rely on model judgment and are the weakest form of verification.

#### 3.1 Model Judgment

**Description**: Use a model to judge whether the finding is valid.

**Use case**: Verify findings that cannot be verified with deterministic or specialist oracles.

**Command**:
```bash
# Ask a model to evaluate the evidence
# This is the weakest form of verification
```

**Strength**: Weak — model judgment is subjective and can be biased.

**Limitations**: Subjective, can be biased, can be fooled by coherent but incorrect reasoning.

---

#### 3.2 Output Matching

**Description**: Check if the output matches the expected output.

**Use case**: Verify that the output matches the vulnerability description.

**Command**:
```bash
diff <(echo "expected output") <(echo "actual output")
```

**Strength**: Weak — output matching does not verify the cause.

**Limitations**: Only verifies output matching, not the cause.

---

#### 3.3 Pattern Matching

**Description**: Check if the output matches a known pattern.

**Use case**: Verify that the output matches a known vulnerability pattern.

**Command**:
```bash
echo "$output" | grep -q "known_pattern"
```

**Strength**: Weak — pattern matching does not verify the cause.

**Limitations**: Only verifies pattern matching, not the cause.

---

## Oracle Selection Criteria

### 1. Determinism

**Question**: Does the oracle produce the same result every time?

**Preference**: Prefer deterministic oracles over non-deterministic oracles.

### 2. Independence

**Question**: Can the oracle be independently verified?

**Preference**: Prefer oracles that can be independently verified.

### 3. Specificity

**Question**: Does the oracle verify the specific vulnerability?

**Preference**: Prefer oracles that verify the specific vulnerability over general oracles.

### 4. Strength

**Question**: How strong is the oracle?

**Preference**: Prefer stronger oracles over weaker oracles.

### 5. Availability

**Question**: Is the oracle available?

**Preference**: Prefer available oracles over unavailable oracles.

---

## Oracle Combination Strategies

### Strategy 1: Multiple Deterministic Oracles

**Description**: Use multiple deterministic oracles to verify the finding.

**Example**:
```bash
# Oracle 1: File exists
if [ -f /path/to/file ]; then
  echo "PASS: File exists"
fi

# Oracle 2: Command output
output=$(<command>)
if echo "$output" | grep -q "expected_string"; then
  echo "PASS: Output matches"
fi

# Oracle 3: Network callback
if [ -s evidence/callback.txt ]; then
  echo "PASS: Callback received"
fi
```

**Strength**: Very strong — multiple deterministic oracles provide strong verification.

---

### Strategy 2: Deterministic + Specialist Oracles

**Description**: Use a deterministic oracle and a specialist oracle to verify the finding.

**Example**:
```bash
# Deterministic oracle: Transaction state change
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-before.txt
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL
sleep 15
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-after.txt
if ! diff -q evidence/state-before.txt evidence/state-after.txt > /dev/null; then
  echo "PASS: State changed"
fi

# Specialist oracle: On-chain balance check
BALANCE=$(cast balance <address> --rpc-url $RPC_URL)
if [ "$BALANCE" -gt 0 ]; then
  echo "PASS: Balance is positive"
fi
```

**Strength**: Very strong — deterministic + specialist oracles provide strong verification.

---

### Strategy 3: Multiple Specialist Oracles

**Description**: Use multiple specialist oracles to verify the finding.

**Example**:
```bash
# Specialist oracle 1: On-chain balance check
BALANCE=$(cast balance <address> --rpc-url $RPC_URL)
if [ "$BALANCE" -gt 0 ]; then
  echo "PASS: Balance is positive"
fi

# Specialist oracle 2: Event log verification
if [ -s evidence/event-logs.txt ]; then
  echo "PASS: Event emitted"
fi

# Specialist oracle 3: Storage slot verification
VALUE=$(cast storage <contract> <slot> --rpc-url $RPC_URL)
if [ "$VALUE" = "expected_value" ]; then
  echo "PASS: Storage slot matches"
fi
```

**Strength**: Strong — multiple specialist oracles provide strong verification.

---

### Strategy 4: Deterministic + Specialist + Self-Reflective Oracles

**Description**: Use all three types of oracles to verify the finding.

**Example**:
```bash
# Deterministic oracle: File exists
if [ -f /path/to/file ]; then
  echo "PASS: File exists"
fi

# Specialist oracle: HTTP response check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" <url>)
if [ "$HTTP_CODE" = "200" ]; then
  echo "PASS: HTTP 200"
fi

# Self-reflective oracle: Output matching
output=$(<command>)
if echo "$output" | grep -q "expected_string"; then
  echo "PASS: Output matches"
fi
```

**Strength**: Very strong — all three types of oracles provide the strongest verification.

---

## Oracle Limitations and Failure Modes

### Deterministic Oracle Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| False negative | Oracle fails to detect a valid finding | Use multiple oracles |
| False positive | Oracle detects a finding that is not valid | Use multiple oracles |
| Scope | Oracle only verifies a specific aspect | Use multiple oracles |
| Availability | Oracle is not available | Use alternative oracles |

### Specialist Oracle Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| Domain-specific | Oracle only works for a specific domain | Use domain-appropriate oracles |
| Tool dependency | Oracle requires a specific tool | Ensure tool is available |
| Configuration | Oracle requires specific configuration | Verify configuration |
| False negative | Oracle fails to detect a valid finding | Use multiple oracles |
| False positive | Oracle detects a finding that is not valid | Use multiple oracles |

### Self-Reflective Oracle Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| Subjectivity | Oracle is subjective | Use deterministic oracles |
| Bias | Oracle can be biased | Use deterministic oracles |
| Coherence trap | Oracle can be fooled by coherent but incorrect reasoning | Use deterministic oracles |
| Hallucination | Oracle can hallucinate results | Use deterministic oracles |
| Inconsistency | Oracle can produce inconsistent results | Use deterministic oracles |

---

## Oracle Selection Decision Tree

```
Is a deterministic oracle available?
├── Yes → Use deterministic oracle
│   ├── Is the deterministic oracle sufficient?
│   │   ├── Yes → Use deterministic oracle only
│   │   └── No → Use deterministic + specialist oracles
│   └── Is the deterministic oracle reliable?
│       ├── Yes → Use deterministic oracle
│       └── No → Use multiple deterministic oracles
└── No → Is a specialist oracle available?
    ├── Yes → Use specialist oracle
    │   ├── Is the specialist oracle sufficient?
    │   │   ├── Yes → Use specialist oracle only
    │   │   └── No → Use multiple specialist oracles
    │   └── Is the specialist oracle reliable?
    │       ├── Yes → Use specialist oracle
    │       └── No → Use multiple specialist oracles
    └── No → Use self-reflective oracle (weakest)
        └── Document the limitation
```

---

## Oracle Strength Comparison

| Oracle | Type | Strength | Determinism | Independence | Specificity |
|--------|------|----------|-------------|--------------|-------------|
| File exists | Deterministic | Very strong | Yes | Yes | High |
| Command output | Deterministic | Very strong | Yes | Yes | High |
| Network callback | Deterministic | Very strong | Yes | Yes | High |
| Transaction state change | Deterministic | Very strong | Yes | Yes | High |
| On-chain balance check | Specialist | Strong | Yes | Yes | Medium |
| Storage slot verification | Specialist | Strong | Yes | Yes | High |
| Event log verification | Specialist | Strong | Yes | Yes | High |
| HTTP response check | Specialist | Strong | Yes | Yes | Medium |
| Process check | Specialist | Medium | No | Yes | Low |
| Port check | Specialist | Medium | No | Yes | Low |
| Model judgment | Self-reflective | Weak | No | No | Low |
| Output matching | Self-reflective | Weak | No | No | Low |
| Pattern matching | Self-reflective | Weak | No | No | Low |

---

## Best Practices

1. **Always prefer deterministic oracles** over specialist oracles, and specialist oracles over self-reflective oracles.
2. **Use multiple oracles** to verify a finding.
3. **Document the oracle used** and its limitations.
4. **Verify the oracle** is working correctly before relying on it.
5. **Use the strongest oracle available** for the finding.
6. **Document the oracle selection** and the reasoning behind it.
7. **Be honest about oracle limitations** and the impact on verification quality.
