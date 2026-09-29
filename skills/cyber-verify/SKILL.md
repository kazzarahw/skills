---
name: cyber-verify
description: Verifies cybersecurity findings before submission. Use before reporting any vulnerability, PoC, or exploit to confirm validity, reproducibility, and target-specificity. Two-stage: deterministic reproduction + adversarial self-review.
---

# Cyber Verify

Verify cybersecurity findings before submission. Two stages: deterministic reproduction, then adversarial self-review.

## When to Use

- Before reporting any vulnerability, PoC, or exploit
- Before declaring a security test complete
- When a finding's validity is uncertain
- When reproducing a reported issue

## Constitutional Rules

1. **Raw output only** — Evidence is tool output, never model summaries
2. **Reproducibility is binary** — A finding either reproduces consistently or it does not
3. **Honest uncertainty** — UNVERIFIABLE is a valid outcome, not a failure
4. **No self-correction loops** — If reasoning is flawed, more reasoning will not fix it
5. **Information asymmetry** — The reviewer must not see the generator's reasoning
6. **Deterministic over interpretive** — Prefer observable assertions over judgment calls

## Stage 1: Deterministic Reproduction

Run the finding or PoC against the target. Minimum 3 runs.

### Procedure

1. Record the exact command or action
2. Execute against the target
3. Capture raw output (stdout, stderr, exit code)
4. Assert side-effect indicators (file exists, network callback, command output)
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

## Evidence Requirements

Every VERIFIED finding must include:

- [ ] Raw tool output (not model summaries)
- [ ] Exact commands run
- [ ] Timestamps for each run
- [ ] Side-effect assertions (file exists, command output, network callback)
- [ ] Multiple indicators for exploit success
- [ ] Reproducibility confirmation (N runs, same result)

## Convergence Detection

- If no improvement between iterations, HALT
- Maximum 3-5 iterations before escalating
- If feedback is not actionable, stop
- Document why convergence was not achieved

## Gotchas

### Hallucinated Success
75.8% of verification failures are false completions. The model believes it succeeded when it did not. **Mitigation:** Require side-effect assertions, not just output matching.

### Self-Correction Limitations
LLMs cannot reliably self-correction reasoning. If the initial reasoning is flawed, re-reasoning will likely reproduce the flaw. **Mitigation:** Use deterministic checks, not reasoning.

### Coherence Trap
Same-model verification is unreliable. The verifier shares the generator's blind spots. **Mitigation:** Use information asymmetry and deterministic oracles.

### Premature Completion
Declaring done after first visible progress. **Mitigation:** Require all runs to pass, not just the first.

### Structural Hallucinations
Hallucinated tool parameters, assumed data, or fabricated output. **Mitigation:** Verify tool parameters against documentation; never assume data exists.

### False Agreement in Adversarial Review
The critic gives in to confident rebuttals. **Mitigation:** Require evidence-grounded disagreement; confidence is not evidence.

### Verification Oracle Determines the Ceiling
The quality of verification is bounded by the oracle used. **Mitigation hierarchy:**
1. Deterministic (strongest) — file exists, command output, network callback
2. Specialist — domain-specific checker
3. Self-reflective (weakest) — model judgment

## Scripts

- `scripts/verify-runner.sh` — Automated deterministic reproduction runner
- `scripts/side_effect_assertions.py` — Library of side-effect assertions (file, command, callback, process, port, HTTP)

## Reference Files

- `references/verification-checklist.md` — Detailed verification criteria by finding type
- `references/adversarial-review.md` — Adversarial review patterns and protocols
- `references/false-positive-patterns.md` — Common false positive patterns and mitigations

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
