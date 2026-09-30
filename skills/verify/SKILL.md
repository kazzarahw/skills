---
name: verify
description: >-
  Gate before any report: confirms findings via deterministic reproduction plus adversarial review, verdicts VERIFIED / UNVERIFIABLE / BLOCKED. Use when reporting any vulnerability, PoC, or exploit — nothing ships without a verdict.
---

# Security Verify

Verifies security findings and filters false positives across web2 and web3. Two stages: deterministic reproduction, then adversarial self-review.

> **Note:** This skill is Phase 4 in the `engagement` engagement lifecycle.

## Prerequisites

This skill requires the following tools to be available on the system:

| Tool | Purpose | Verification |
|------|---------|--------------|
| `cast` | Web3 interaction (storage, balances, transactions) | `cast --version` |
| `forge` | Smart contract testing and forking | `forge --version` |
| `nmap` | Network scanning and service detection | `nmap --version` |
| `nc` | Network connections and banner grabbing | `nc -h` |
| `curl` | HTTP requests and web testing | `curl --version` |
| `jq` | JSON processing | `jq --version` |
| `bc` | Arithmetic calculations | `bc --version` |

Verify all required tools are installed before beginning verification:

```bash
for tool in cast forge nmap nc curl jq bc; do
  if command -v "$tool" &>/dev/null; then
    echo "[OK] $tool: $(command -v "$tool")"
  else
    echo "[MISSING] $tool — install before proceeding"
  fi
done
```

## Constitutional Rules

1. **Raw output only** — Evidence is tool output, never model summaries
2. **Reproducibility is binary** — A finding either reproduces consistently or it does not
3. **Honest uncertainty** — UNVERIFIABLE is a valid outcome, not a failure
4. **No self-correction loops** — If reasoning is flawed, more reasoning will not fix it
5. **Information asymmetry** — The reviewer must not see the generator's reasoning
6. **Deterministic over interpretive** — Prefer observable assertions over judgment calls

## Stage 1: Deterministic Reproduction

Run the finding or PoC against the target. Minimum 3 runs. Drive the loop with `scripts/verify-runner.sh` and assert with `scripts/side-effect-assertions.py` — do not hand-roll the repetition.

### Procedure

1. Record the exact command or action
2. Execute against the target
3. Capture raw output (stdout, stderr, exit code)
4. Assert side-effect indicators (file exists, network callback, command output, transaction state change)
5. Repeat N times (minimum 3)
6. Compare results across runs

### Pass Criteria

- Same result EVERY run
- Side-effect assertions confirm the claimed state change
- Output matches the vulnerability description

### Fail Criteria

- Any run produces a different result
- Side-effect assertions do not confirm
- Output contradicts the vulnerability description

### Recording Format

```
Run [N]: [timestamp]
Command: [exact command]
Exit code: [code]
Output: [raw output]
Assertions: [pass/fail with evidence]
```

## Stage 2: Adversarial Self-Review

Answer these questions honestly. The reviewer must NOT see the generator's reasoning (information asymmetry).

### Questions

1. **Specificity** — Does this exercise the SPECIFIC vulnerability path?
2. **Targeting** — Is this a broad crash or a targeted trigger?
3. **Patch resistance** — Would this also crash the patched/fixed version?
4. **Description match** — Does the result match the vulnerability description?

### Review Protocol

- Review the evidence only, not the generator's claims
- If any answer is "no" or "uncertain," the finding is not VERIFIED
- Document the disagreement with evidence
- See `references/adversarial-review.md` for detailed patterns

## Three-State Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| `VERIFIED` | Proof established, evidence attached | Submit with evidence |
| `UNVERIFIABLE` | Proof could not be established | Report honestly, do not submit as verified |
| `BLOCKED` | Policy or rule rejected the action | Stop, report blocker |

**Never collapse UNVERIFIABLE into VERIFIED.** Honest uncertainty is a valid signal.

## Post-Verdict Actions

After reaching a verdict, take the following actions:

| Verdict | Action |
|---------|--------|
| `VERIFIED` | Submit to `report` with full evidence attached |
| `UNVERIFIABLE` | Document the finding and either: re-test with a different oracle, escalate to a human reviewer, or mark as "inconclusive" in the report |
| `BLOCKED` | Stop immediately, document the blocker, notify the user |

## Evidence Requirements

Every VERIFIED finding must include:

- [ ] Raw tool output (not model summaries)
- [ ] Exact commands run
- [ ] Timestamps for each run
- [ ] Side-effect assertions (file exists, command output, network callback, transaction state change)
- [ ] Multiple indicators for exploit success
- [ ] Reproducibility confirmation (N runs, same result)

## Verification Oracles

The quality of verification is bounded by the oracle used. Mitigation hierarchy:

1. **Deterministic (strongest)** — file exists, command output, network callback, transaction state change
2. **Specialist** — domain-specific checker (e.g., on-chain balance check, storage slot verification)
3. **Self-reflective (weakest)** — model judgment

## Web2 Verification

### Network Findings

```bash
# Verify port is actually open
nmap -p <port> <host> --reason

# Verify service banner
nc -w 5 <host> <port>

# Verify vulnerability with curl
curl -v -X POST <url> -d '<payload>' 2>&1 | tee evidence.txt

# Verify file creation
ls -la /path/to/created/file
```

### Web Findings

```bash
# Verify XSS
curl -s "<url>?q=<script>alert(1)</script>" | grep "alert(1)"

# Verify SQL injection
curl -s "<url>' OR 1=1--" | diff - <(curl -s "<url>")

# Verify IDOR
curl -s -H "Cookie: session=<user1>" "<url>/api/user/2/profile"
```

## Web3 Verification

### Contract Findings

```bash
# Verify state change
cast storage <contract> <slot> --rpc-url $RPC_URL

# Verify event emission
cast logs --from-block <start> --to-block <end> --address <contract> <event_signature>

# Verify profit extraction
cast balance <attacker_address> --rpc-url $RPC_URL

# Verify exploit on fork
forge test --match-contract ExploitTest --fork-url $RPC_URL
```

### On-Chain Findings

```bash
# Verify transaction
cast tx <tx_hash> --rpc-url $RPC_URL

# Verify contract call
cast call <contract> "<function_signature>" <args> --rpc-url $RPC_URL

# Verify storage slot
cast storage <contract> <slot> --rpc-url $RPC_URL

# Verify balance change
cast balance <address> --rpc-url $RPC_URL
```

## Convergence Detection

- If no improvement between iterations, HALT
- Maximum 3-5 iterations before escalating
- If feedback is not actionable, stop
- Document why convergence was not achieved

## False Positive Patterns

### Web2 False Positive Patterns

| Pattern | Description | Mitigation |
|---------|-------------|------------|
| **Version mismatch** | CVE applies to different version | Verify exact version |
| **Configuration-dependent** | Vuln only in specific config | Test in target config |
| **Authentication required** | Vuln requires auth | Test with valid creds |
| **Rate limiting** | Scan blocked by WAF | Use rate limiting |
| **False banner** | Service spoofs version | Behavioral testing |

### Web3 False Positive Patterns

| Pattern | Description | Mitigation |
|---------|-------------|------------|
| **Compiler version** | Vuln only in specific compiler | Verify compiler version |
| **Proxy implementation** | Vuln in implementation, not proxy | Check implementation |
| **Oracle dependency** | Vuln requires specific oracle state | Test with oracle state |
| **Access control** | Function requires specific role | Test with authorized role |
| **Reorg** | State changed due to reorg | Wait for finality |

## Cross-References

| Skill | When to Use |
|-------|-------------|
| `engagement` | Orchestration and phase management |
| `recon` | Verify recon findings |
| `audit` | Verify audit findings |
| `exploit` | Verify exploit success |
| `forensics` | Verify investigation findings |
| `report` | Verification status in reports |
| `coach` | Course correction |
| `wiki` | Knowledge persistence |

## Handoffs

- `VERIFIED` → load `report` with the evidence pack.
- `UNVERIFIABLE` after re-test → load `coach` for a new oracle angle, or mark inconclusive — never upgrade it yourself.
- `BLOCKED` → stop and report the blocker; record it in `wiki`.
- Adversarial review needs fresh eyes (same-model critics share blind spots) → delegate Stage 2 to the `spark-reviewer` subagent with evidence only, no generator reasoning.

## Mid-Work Checkpoints

Periodically verify:
1. **Am I in the right skill?** If the work drifted into another phase, hand off via `## Handoffs` instead of continuing here.
2. **Am I routing verdicts?** VERIFIED, UNVERIFIABLE, and BLOCKED each have a next step — never collapse them.
3. **Evidence attached?** No verdict leaves this skill without raw output and assertions.

## Gotchas

- **Hallucinated success is the #1 verification failure.** A significant portion of verification failures are false completions. The model believes it succeeded when it did not. Mitigation: Require side-effect assertions, not just output matching.
- **Self-correction limitations.** LLMs cannot reliably self-correct reasoning. If the initial reasoning is flawed, re-reasoning will likely reproduce the flaw. Mitigation: Use deterministic checks, not reasoning.
- **Coherence trap.** Same-model verification is unreliable. The verifier shares the generator's blind spots. Mitigation: Use information asymmetry and deterministic oracles.
- **Premature completion.** Declaring done after first visible progress. Mitigation: Require all runs to pass, not just the first.
- **Structural hallucinations.** Hallucinated tool parameters, assumed data, or fabricated output. Mitigation: Verify tool parameters against documentation; never assume data exists.
- **False agreement in adversarial review.** The critic gives in to confident rebuttals. Mitigation: Require evidence-grounded disagreement; confidence is not evidence.
- **Verification oracle determines the ceiling.** The quality of verification is bounded by the oracle used. Mitigation hierarchy: deterministic > specialist > self-reflective.
- **Web3 reorgs can invalidate findings.** State can change due to chain reorgs. Always wait for sufficient finality before verifying.
- **Proxy contracts can hide vulnerabilities.** The implementation contract may have different vulnerabilities than the proxy. Verify both.
- **Test coverage does not mean security.** Passing tests do not mean the contract is secure. Tests only verify expected behavior, not unexpected behavior.

## Output Format

```yaml
verdict: VERIFIED | UNVERIFIABLE | BLOCKED
finding: [description]
evidence:
  runs: [N]
  reproducible: true | false
  assertions: [list of side-effect assertions]
  raw_output: [path or inline]
adversarial_review:
  specificity: yes | no | uncertain
  targeting: yes | no | uncertain
  patch_resistance: yes | no | uncertain
  description_match: yes | no | uncertain
  disagreements: [list]
convergence:
  iterations: [N]
  halted: true | false
  reason: [if halted]
```

## Scripts

- `scripts/verify-runner.sh` — Automated deterministic reproduction runner
- `scripts/side-effect-assertions.py` — Library of side-effect assertions (file, command, callback, process, port, HTTP, on-chain)
- `scripts/false-positive-filter.py` — Filter findings through false positive patterns

## References

- `references/verification-checklist.md` — Detailed verification criteria by finding type
- `references/adversarial-review.md` — Adversarial review patterns and protocols
- `references/false-positive-patterns.md` — Common false positive patterns and mitigations
- `references/web2-verification.md` — Web2-specific verification procedures
- `references/web3-verification.md` — Web3-specific verification procedures
- `references/oracle-hierarchy.md` — Verification oracle selection guide
