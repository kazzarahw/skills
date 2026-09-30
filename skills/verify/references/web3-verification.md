# Web3-Specific Verification Procedures

## Table of Contents

- [1. Contract Findings](#1-contract-findings)
- [1.1 Storage Slot Verification](#11-storage-slot-verification)
- [1.2 Event Log Verification](#12-event-log-verification)
- [1.3 Balance Verification](#13-balance-verification)
- [2. Transaction Findings](#2-transaction-findings)
- [2.1 Transaction Verification](#21-transaction-verification)
- [2.2 Calldata Decoding](#22-calldata-decoding)
- [2.3 State Diff Verification](#23-state-diff-verification)
- [3. Exploit Verification](#3-exploit-verification)
- [3.1 Fork Testing](#31-fork-testing)
- [3.2 Simulation Validation](#32-simulation-validation)
- [3.3 Profit Assertion](#33-profit-assertion)
- [4. On-Chain Findings](#4-on-chain-findings)
- [4.1 Block Explorer Verification](#41-block-explorer-verification)
- [4.2 RPC Verification](#42-rpc-verification)
- [4.3 Event Verification](#43-event-verification)
- [5. Evidence Capture](#5-evidence-capture)
- [5.1 Transaction Hashes](#51-transaction-hashes)
- [5.2 State Diffs](#52-state-diffs)
- [5.3 Contract Interactions](#53-contract-interactions)
- [6. Verification Checklist](#6-verification-checklist)
- [Contract Findings](#contract-findings)
- [Transaction Findings](#transaction-findings)
- [Exploit Verification](#exploit-verification)
- [On-Chain Findings](#on-chain-findings)

Detailed verification procedures for web3 findings. Each procedure includes the exact commands, expected output, and pass/fail criteria.

---

## 1. Contract Findings

### 1.1 Storage Slot Verification

**Purpose**: Verify that a contract's storage slot has changed as expected.

**Procedure**:
```bash
# Before state
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/storage-before.txt

# Execute transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/exploit-tx.txt

# Wait for finality (12+ blocks for Ethereum)
sleep 15

# After state
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/storage-after.txt

# State diff
diff evidence/storage-before.txt evidence/storage-after.txt | tee evidence/storage-diff.txt

# Verify state change
if ! diff -q evidence/storage-before.txt evidence/storage-after.txt > /dev/null; then
  echo "PASS: State changed"
else
  echo "FAIL: State did not change"
fi
```

**Pass criteria**:
- Storage slot value changed
- State change is consistent with expected behavior
- State change persists after finality

**Fail criteria**:
- Storage slot value did not change
- State change is inconsistent with expected behavior
- State change does not persist after finality

---

### 1.2 Event Log Verification

**Purpose**: Verify that an event was emitted with the expected data.

**Procedure**:
```bash
# Get current block number
START_BLOCK=$(cast block-number --rpc-url $RPC_URL)
echo "Start block: $START_BLOCK" | tee evidence/event-start-block.txt

# Execute transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/event-tx.txt

# Wait for finality
sleep 15

# Get end block number
END_BLOCK=$(cast block-number --rpc-url $RPC_URL)
echo "End block: $END_BLOCK" | tee evidence/event-end-block.txt

# Get event logs
cast logs --from-block $START_BLOCK --to-block $END_BLOCK --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL | tee evidence/event-log.txt

# Decode event data
cast logs --from-block $START_BLOCK --to-block $END_BLOCK --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL --json | jq '.[] | .data' | tee evidence/event-data.txt

# Verify event was emitted
if [ -s evidence/event-log.txt ]; then
  echo "PASS: Event emitted"
else
  echo "FAIL: Event not emitted"
fi
```

**Pass criteria**:
- Event was emitted
- Event data matches expected values
- Event is consistent across multiple runs

**Fail criteria**:
- Event was not emitted
- Event data does not match expected values
- Event varies across runs

---

### 1.3 Balance Verification

**Purpose**: Verify that a balance has changed as expected.

**Procedure**:
```bash
# Before balance
cast balance <address> --rpc-url $RPC_URL | tee evidence/balance-before.txt

# Execute transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/balance-tx.txt

# Wait for finality
sleep 15

# After balance
cast balance <address> --rpc-url $RPC_URL | tee evidence/balance-after.txt

# Balance diff
BEFORE=$(cat evidence/balance-before.txt)
AFTER=$(cat evidence/balance-after.txt)
DIFF=$(echo "$AFTER - $BEFORE" | bc)
echo "Balance change: $DIFF" | tee evidence/balance-diff.txt

# Verify balance change
if [ "$DIFF" -gt 0 ]; then
  echo "PASS: Balance increased"
else
  echo "FAIL: Balance did not increase"
fi
```

**Pass criteria**:
- Balance changed as expected
- Balance change is consistent with expected behavior
- Balance change persists after finality

**Fail criteria**:
- Balance did not change
- Balance change is inconsistent with expected behavior
- Balance change does not persist after finality

---

## 2. Transaction Findings

### 2.1 Transaction Verification

**Purpose**: Verify that a transaction was executed successfully.

**Procedure**:
```bash
# Get transaction details
cast tx <tx_hash> --rpc-url $RPC_URL | tee evidence/tx-details.txt

# Get transaction receipt
cast receipt <tx_hash> --rpc-url $RPC_URL | tee evidence/tx-receipt.txt

# Verify transaction status
STATUS=$(cast receipt <tx_hash> --rpc-url $RPC_URL --json | jq -r '.status')
if [ "$STATUS" = "0x1" ]; then
  echo "PASS: Transaction succeeded"
else
  echo "FAIL: Transaction failed"
fi

# Verify transaction is not reverted
if cast tx <tx_hash> --rpc-url $RPC_URL | grep -q "reverted"; then
  echo "FAIL: Transaction reverted"
else
  echo "PASS: Transaction not reverted"
fi
```

**Pass criteria**:
- Transaction succeeded (status 0x1)
- Transaction is not reverted
- Transaction details match expected values

**Fail criteria**:
- Transaction failed (status 0x0)
- Transaction is reverted
- Transaction details do not match expected values

---

### 2.2 Calldata Decoding

**Purpose**: Decode and verify transaction calldata.

**Procedure**:
```bash
# Get transaction calldata
cast tx <tx_hash> --rpc-url $RPC_URL --json | jq -r '.input' | tee evidence/calldata-raw.txt

# Decode calldata
cast calldata-decode "<function_signature>" <calldata> | tee evidence/calldata-decoded.txt

# Verify calldata matches expected values
# Compare decoded values with expected values
```

**Pass criteria**:
- Calldata decodes correctly
- Decoded values match expected values
- Calldata is consistent with expected behavior

**Fail criteria**:
- Calldata does not decode correctly
- Decoded values do not match expected values
- Calldata is inconsistent with expected behavior

---

### 2.3 State Diff Verification

**Purpose**: Verify the state diff of a transaction.

**Procedure**:
```bash
# Get state diff using cast
# Note: cast does not have a direct state diff command
# Use forge or custom script to get state diff

# Using forge (if available)
forge inspect <contract> storage --rpc-url $RPC_URL | tee evidence/state-diff.txt

# Using custom script
# Get storage before and after transaction
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-before.txt
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL > /dev/null
sleep 15
cast storage <contract> <slot> --rpc-url $RPC_URL > evidence/state-after.txt
diff evidence/state-before.txt evidence/state-after.txt | tee evidence/state-diff.txt
```

**Pass criteria**:
- State diff matches expected values
- State diff is consistent with expected behavior
- State diff persists after finality

**Fail criteria**:
- State diff does not match expected values
- State diff is inconsistent with expected behavior
- State diff does not persist after finality

---

## 3. Exploit Verification

### 3.1 Fork Testing

**Purpose**: Verify exploit on a fork of the target chain.

**Procedure**:
```bash
# Run exploit on fork
forge test --match-contract ExploitTest --fork-url $RPC_URL -vvv | tee evidence/fork-test.txt

# Verify exploit succeeded
if grep -q "PASS\|success\|exploit" evidence/fork-test.txt; then
  echo "PASS: Exploit succeeded on fork"
else
  echo "FAIL: Exploit failed on fork"
fi

# Verify state change on fork
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/fork-state.txt
```

**Pass criteria**:
- Exploit succeeds on fork
- State change is confirmed on fork
- Exploit is reproducible on fork

**Fail criteria**:
- Exploit fails on fork
- State change is not confirmed on fork
- Exploit is not reproducible on fork

---

### 3.2 Simulation Validation

**Purpose**: Validate exploit using simulation.

**Procedure**:
```bash
# Simulate transaction
cast call <contract> "<function>()" --from <attacker_address> --rpc-url $RPC_URL | tee evidence/simulation.txt

# Simulate with state override
cast call <contract> "<function>()" --from <attacker_address> --rpc-url $RPC_URL --state-dict '{"<slot>":"<value>"}' | tee evidence/simulation-override.txt

# Verify simulation matches expected behavior
if grep -q "expected_value" evidence/simulation.txt; then
  echo "PASS: Simulation matches expected behavior"
else
  echo "FAIL: Simulation does not match expected behavior"
fi
```

**Pass criteria**:
- Simulation matches expected behavior
- Simulation is consistent across multiple runs
- Simulation confirms exploit feasibility

**Fail criteria**:
- Simulation does not match expected behavior
- Simulation varies across runs
- Simulation does not confirm exploit feasibility

---

### 3.3 Profit Assertion

**Purpose**: Verify that the exploit generates profit.

**Procedure**:
```bash
# Before balance
cast balance <attacker_address> --rpc-url $RPC_URL | tee evidence/profit-before.txt

# Execute exploit
cast send <contract> "<exploit_function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/profit-tx.txt

# Wait for finality
sleep 15

# After balance
cast balance <attacker_address> --rpc-url $RPC_URL | tee evidence/profit-after.txt

# Calculate profit
BEFORE=$(cast balance <attacker_address> --rpc-url $RPC_URL)
AFTER=$(cast balance <attacker_address> --rpc-url $RPC_URL)
PROFIT=$(echo "$AFTER - $BEFORE" | bc)
echo "Profit: $PROFIT" | tee evidence/profit-amount.txt

# Verify profit
if [ "$PROFIT" -gt 0 ]; then
  echo "PASS: Profit generated"
else
  echo "FAIL: No profit generated"
fi

# Verify profit is significant
TVL=$(cast call <contract> "totalLockedValue()(uint256)" --rpc-url $RPC_URL)
if [ "$PROFIT" -gt "$((TVL / 100))" ]; then
  echo "PASS: Profit is significant (>1% of TVL)"
else
  echo "FAIL: Profit is not significant"
fi
```

**Pass criteria**:
- Profit is generated
- Profit is significant relative to TVL
- Profit is reproducible across multiple runs

**Fail criteria**:
- No profit is generated
- Profit is not significant relative to TVL
- Profit varies across runs

---

## 4. On-Chain Findings

### 4.1 Block Explorer Verification

**Purpose**: Verify on-chain findings using a block explorer.

**Procedure**:
```bash
# Get transaction from block explorer
curl -s "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash=<tx_hash>&apikey=$ETHERSCAN_API_KEY" | tee evidence/blockexplorer-tx.json

# Get transaction receipt from block explorer
curl -s "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt&txhash=<tx_hash>&apikey=$ETHERSCAN_API_KEY" | tee evidence/blockexplorer-receipt.json

# Verify transaction status
STATUS=$(jq -r '.result.status' evidence/blockexplorer-receipt.json)
if [ "$STATUS" = "0x1" ]; then
  echo "PASS: Transaction succeeded"
else
  echo "FAIL: Transaction failed"
fi
```

**Pass criteria**:
- Block explorer confirms the finding
- Block explorer data matches expected values
- Block explorer data is consistent across multiple queries

**Fail criteria**:
- Block explorer does not confirm the finding
- Block explorer data does not match expected values
- Block explorer data varies across queries

---

### 4.2 RPC Verification

**Purpose**: Verify on-chain findings using RPC.

**Procedure**:
```bash
# Get transaction
cast tx <tx_hash> --rpc-url $RPC_URL | tee evidence/rpc-tx.txt

# Get transaction receipt
cast receipt <tx_hash> --rpc-url $RPC_URL | tee evidence/rpc-receipt.txt

# Get storage
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/rpc-storage.txt

# Get balance
cast balance <address> --rpc-url $RPC_URL | tee evidence/rpc-balance.txt

# Get code
cast code <contract> --rpc-url $RPC_URL | tee evidence/rpc-code.txt
```

**Pass criteria**:
- RPC confirms the finding
- RPC data matches expected values
- RPC data is consistent across multiple queries

**Fail criteria**:
- RPC does not confirm the finding
- RPC data does not match expected values
- RPC data varies across queries

---

### 4.3 Event Verification

**Purpose**: Verify on-chain events.

**Procedure**:
```bash
# Get event logs
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL | tee evidence/event-logs.txt

# Get event logs with JSON output
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL --json | tee evidence/event-logs.json

# Decode event data
cast logs --from-block <start> --to-block <end> --address <contract> "EventName(type1,type2)" --rpc-url $RPC_URL --json | jq '.[] | .data' | tee evidence/event-data.txt

# Verify event was emitted
if [ -s evidence/event-logs.txt ]; then
  echo "PASS: Event emitted"
else
  echo "FAIL: Event not emitted"
fi
```

**Pass criteria**:
- Event was emitted
- Event data matches expected values
- Event is consistent across multiple runs

**Fail criteria**:
- Event was not emitted
- Event data does not match expected values
- Event varies across runs

---

## 5. Evidence Capture

### 5.1 Transaction Hashes

**Purpose**: Capture transaction hashes as evidence.

**Procedure**:
```bash
# Capture transaction hash
TX_HASH=$(cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL --json | jq -r '.transactionHash')
echo "Transaction hash: $TX_HASH" | tee evidence/tx-hash.txt

# Capture transaction details
cast tx $TX_HASH --rpc-url $RPC_URL | tee evidence/tx-details.txt

# Capture transaction receipt
cast receipt $TX_HASH --rpc-url $RPC_URL | tee evidence/tx-receipt.txt
```

---

### 5.2 State Diffs

**Purpose**: Capture state diffs as evidence.

**Procedure**:
```bash
# Capture state before
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/state-before.txt

# Execute transaction
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/state-tx.txt

# Wait for finality
sleep 15

# Capture state after
cast storage <contract> <slot> --rpc-url $RPC_URL | tee evidence/state-after.txt

# Capture state diff
diff evidence/state-before.txt evidence/state-after.txt | tee evidence/state-diff.txt
```

---

### 5.3 Contract Interactions

**Purpose**: Capture contract interactions as evidence.

**Procedure**:
```bash
# Capture contract call
cast call <contract> "<function>()" --rpc-url $RPC_URL | tee evidence/contract-call.txt

# Capture contract send
cast send <contract> "<function>()" --private-key $PK --rpc-url $RPC_URL | tee evidence/contract-send.txt

# Capture contract code
cast code <contract> --rpc-url $RPC_URL | tee evidence/contract-code.txt

# Capture contract ABI
cast interface <contract> --rpc-url $RPC_URL | tee evidence/contract-abi.txt
```

---

## 6. Verification Checklist

### Contract Findings

- [ ] State change is observable
- [ ] State change is persistent
- [ ] State change is unauthorized
- [ ] State change is exploitable
- [ ] State change is not reverted
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (storage slot, state diff)

### Transaction Findings

- [ ] Transaction succeeded
- [ ] Transaction is not reverted
- [ ] Calldata decodes correctly
- [ ] State diff matches expected values
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (transaction hash, receipt, calldata)

### Exploit Verification

- [ ] Exploit succeeds on fork
- [ ] Simulation matches expected behavior
- [ ] Profit is generated
- [ ] Profit is significant
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (fork test, simulation, profit)

### On-Chain Findings

- [ ] Block explorer confirms finding
- [ ] RPC confirms finding
- [ ] Event was emitted
- [ ] Result is reproducible (3+ runs)
- [ ] Evidence is captured (transaction hash, event logs, storage)
