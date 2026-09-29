# Adversarial Review Patterns and Protocols

## Table of Contents

- [Information Asymmetry](#information-asymmetry)
- [Principle](#principle)
- [Implementation](#implementation)
- [What the Reviewer Must NOT See](#what-the-reviewer-must-not-see)
- [What the Reviewer MUST See](#what-the-reviewer-must-see)
- [Review Questions](#review-questions)
- [1. Specificity](#1-specificity)
- [2. Targeting](#2-targeting)
- [3. Patch Resistance](#3-patch-resistance)
- [4. Description Match](#4-description-match)
- [Review Protocol](#review-protocol)
- [Step 1: Evidence Collection](#step-1-evidence-collection)
- [Step 2: Independent Evaluation](#step-2-independent-evaluation)
- [Step 3: Disagreement Documentation](#step-3-disagreement-documentation)
- [Step 4: Verdict](#step-4-verdict)
- [Common Adversarial Review Failures](#common-adversarial-review-failures)
- [1. False Agreement](#1-false-agreement)
- [2. Coherence Trap](#2-coherence-trap)
- [3. Premature Completion](#3-premature-completion)
- [4. Confirmation Bias](#4-confirmation-bias)
- [5. Authority Bias](#5-authority-bias)
- [Review Checklist by Finding Type](#review-checklist-by-finding-type)
- [Network Findings](#network-findings)
- [Web Findings](#web-findings)
- [Authentication Findings](#authentication-findings)
- [Authorization Findings](#authorization-findings)
- [Cryptography Findings](#cryptography-findings)
- [Web3 Findings](#web3-findings)
- [Escalation Procedures for Disagreements](#escalation-procedures-for-disagreements)
- [Level 1: Document Disagreement](#level-1-document-disagreement)
- [Level 2: Independent Re-verification](#level-2-independent-re-verification)
- [Level 3: Escalate to Human Review](#level-3-escalate-to-human-review)
- [Level 4: Accept UNVERIFIABLE](#level-4-accept-unverifiable)
- [Review Output Format](#review-output-format)

The adversarial review is the second stage of verification. It is designed to catch false positives, hallucinated successes, and reasoning errors that deterministic reproduction alone cannot detect.

---

## Information Asymmetry

### Principle

The reviewer must NOT see the generator's reasoning, claims, or self-assessment. The reviewer evaluates evidence independently.

### Implementation

1. **Generator produces**: Raw evidence (tool output, commands, timestamps, side-effect assertions)
2. **Reviewer receives**: Only the evidence, NOT the generator's claims or reasoning
3. **Reviewer evaluates**: Evidence against the four review questions
4. **Reviewer documents**: Disagreements with evidence

### What the Reviewer Must NOT See

- Generator's self-assessment ("I believe this is VERIFIED")
- Generator's reasoning ("This works because...")
- Generator's confidence level
- Generator's interpretation of results

### What the Reviewer MUST See

- Raw tool output (stdout, stderr, exit codes)
- Exact commands run
- Timestamps for each run
- Side-effect assertions and their results
- The vulnerability description being verified

---

## Review Questions

### 1. Specificity

**Question**: Does this exercise the SPECIFIC vulnerability path?

**Evaluation**:
- Does the PoC target the exact vulnerable code path?
- Does the PoC trigger the specific vulnerability described?
- Is the PoC a targeted trigger or a broad crash?

**Pass**: PoC exercises the specific vulnerability path described in the finding.

**Fail**: PoC triggers a different vulnerability, a broad crash, or an unrelated code path.

**Evidence required**:
```bash
# Show the specific code path exercised
# For web2: Show the specific parameter, endpoint, or function
# For web3: Show the specific function, storage slot, or contract
```

### 2. Targeting

**Question**: Is this a broad crash or a targeted trigger?

**Evaluation**:
- Does the PoC produce a specific, expected result?
- Does the PoC produce a generic error or crash?
- Is the result consistent with the vulnerability description?

**Pass**: PoC produces a specific, targeted result consistent with the vulnerability description.

**Fail**: PoC produces a generic error, crash, or unrelated result.

**Evidence required**:
```bash
# Show the specific result
# Compare to expected result from vulnerability description
diff <(echo "expected result") <(echo "actual result")
```

### 3. Patch Resistance

**Question**: Would this also crash the patched/fixed version?

**Evaluation**:
- Does the PoC rely on the specific vulnerability being present?
- Would the PoC fail on a patched version?
- Is the PoC testing for the presence of the vulnerability?

**Pass**: PoC would fail on a patched version (i.e., the PoC is specific to the vulnerability).

**Fail**: PoC would also crash a patched version (i.e., the PoC is not specific to the vulnerability).

**Evidence required**:
```bash
# Test against patched version (if available)
# Or: Analyze the code to determine if the PoC would fail on patched version
```

### 4. Description Match

**Question**: Does the result match the vulnerability description?

**Evaluation**:
- Does the observed behavior match the described vulnerability?
- Are the side-effect assertions consistent with the description?
- Is the impact consistent with the description?

**Pass**: Observed behavior matches the vulnerability description.

**Fail**: Observed behavior contradicts or is unrelated to the vulnerability description.

**Evidence required**:
```bash
# Show the vulnerability description
# Show the observed behavior
# Compare the two
```

---

## Review Protocol

### Step 1: Evidence Collection

The reviewer collects all evidence from the generator:
- Raw tool output
- Exact commands
- Timestamps
- Side-effect assertions
- Vulnerability description

### Step 2: Independent Evaluation

The reviewer evaluates the evidence against the four questions:
1. Specificity
2. Targeting
3. Patch resistance
4. Description match

### Step 3: Disagreement Documentation

If any answer is "no" or "uncertain":
- Document the disagreement with evidence
- Explain why the evidence does not support the finding
- Provide specific counter-evidence

### Step 4: Verdict

- If all four questions pass: VERIFIED
- If any question fails or is uncertain: UNVERIFIABLE
- If policy or rule blocks the action: BLOCKED

---

## Common Adversarial Review Failures

### 1. False Agreement

**Pattern**: The reviewer agrees with the generator without independent evaluation.

**Cause**: The reviewer is influenced by the generator's confidence or reasoning.

**Mitigation**: The reviewer must not see the generator's reasoning. The reviewer must evaluate evidence independently.

**Detection**: If the reviewer's verdict matches the generator's claim without independent evidence, it is likely false agreement.

### 2. Coherence Trap

**Pattern**: The reviewer is trapped by the coherence of the generator's narrative.

**Cause**: The generator's reasoning is internally consistent, so the reviewer assumes it is correct.

**Mitigation**: The reviewer must evaluate evidence, not reasoning. Coherent reasoning can still be wrong.

**Detection**: If the reviewer's verdict is based on the generator's reasoning rather than evidence, it is likely a coherence trap.

### 3. Premature Completion

**Pattern**: The reviewer declares the review complete after the first piece of evidence.

**Cause**: The reviewer sees one piece of supporting evidence and stops evaluating.

**Mitigation**: The reviewer must evaluate ALL evidence against ALL four questions.

**Detection**: If the reviewer's verdict is based on a single piece of evidence, it is likely premature completion.

### 4. Confirmation Bias

**Pattern**: The reviewer interprets ambiguous evidence as supporting the finding.

**Cause**: The reviewer wants to confirm the finding and interprets ambiguous evidence favorably.

**Mitigation**: The reviewer must interpret ambiguous evidence as UNVERIFIABLE, not as supporting.

**Detection**: If the reviewer's verdict is VERIFIED based on ambiguous evidence, it is likely confirmation bias.

### 5. Authority Bias

**Pattern**: The reviewer defers to the generator's authority or expertise.

**Cause**: The reviewer assumes the generator is correct because of their role or expertise.

**Mitigation**: The reviewer must evaluate evidence independently, regardless of the generator's authority.

**Detection**: If the reviewer's verdict is based on the generator's authority rather than evidence, it is likely authority bias.

---

## Review Checklist by Finding Type

### Network Findings

- [ ] Port is actually open (not filtered)
- [ ] Service banner is real (not spoofed)
- [ ] Vulnerability is exploitable (not just present)
- [ ] Vulnerability is not patched
- [ ] Result is reproducible (3+ runs)

### Web Findings

- [ ] Payload is reflected/executed (not just accepted)
- [ ] Payload is not sanitized
- [ ] Payload bypasses WAF (if applicable)
- [ ] Context is appropriate
- [ ] Result is reproducible (3+ runs)

### Authentication Findings

- [ ] Credentials actually work (not just accepted)
- [ ] Session token is actually predictable/fixable
- [ ] MFA bypass actually works
- [ ] Result is reproducible (3+ runs)

### Authorization Findings

- [ ] Privilege escalation actually works
- [ ] Access control is actually missing/flawed
- [ ] Result is reproducible (3+ runs)

### Cryptography Findings

- [ ] Algorithm is actually weak (not just deprecated)
- [ ] Key is actually hardcoded/predictable/exposed
- [ ] Result is reproducible (3+ runs)

### Web3 Findings

- [ ] State change is actually observable
- [ ] Event is actually emitted
- [ ] Profit is actually extracted
- [ ] Result is reproducible (3+ runs)

---

## Escalation Procedures for Disagreements

### Level 1: Document Disagreement

If the reviewer disagrees with the generator:
1. Document the disagreement with evidence
2. Explain why the evidence does not support the finding
3. Provide specific counter-evidence

### Level 2: Independent Re-verification

If the disagreement persists:
1. Have a third party independently verify the finding
2. The third party must not see either the generator's or reviewer's reasoning
3. The third party evaluates only the evidence

### Level 3: Escalate to Human Review

If the disagreement cannot be resolved:
1. Escalate to a human security engineer
2. Provide all evidence and documentation
3. The human engineer makes the final determination

### Level 4: Accept UNVERIFIABLE

If the disagreement cannot be resolved by any means:
1. Accept UNVERIFIABLE as the verdict
2. Document the disagreement and the reasons
3. Do not submit the finding as VERIFIED

---

## Review Output Format

```yaml
adversarial_review:
  reviewer: [reviewer ID or "self"]
  information_asymmetry: maintained | compromised
  questions:
    specificity:
      answer: yes | no | uncertain
      evidence: [evidence supporting the answer]
    targeting:
      answer: yes | no | uncertain
      evidence: [evidence supporting the answer]
    patch_resistance:
      answer: yes | no | uncertain
      evidence: [evidence supporting the answer]
    description_match:
      answer: yes | no | uncertain
      evidence: [evidence supporting the answer]
  disagreements:
    - question: [question name]
      issue: [description of disagreement]
      counter_evidence: [evidence contradicting the finding]
  verdict: VERIFIED | UNVERIFIABLE | BLOCKED
  confidence: high | medium | low
  notes: [additional notes]
```
