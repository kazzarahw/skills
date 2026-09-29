# Adversarial Review

Patterns and protocols for Stage 2 adversarial self-review.

## Core Principle

The reviewer evaluates evidence without seeing the generator's reasoning. This information asymmetry prevents the reviewer from being anchored by the generator's conclusions.

## Review Prompt Patterns

### Pattern 1: Evidence-Only Review

```
You are reviewing a cybersecurity finding. You have the evidence but NOT the generator's reasoning or claims.

Evidence:
[raw output, commands, timestamps, assertions]

Answer these questions based ONLY on the evidence:
1. Does this exercise the SPECIFIC vulnerability path?
2. Is this a broad crash or a targeted trigger?
3. Would this also crash the patched/fixed version?
4. Does the result match the vulnerability description?

For each answer, cite specific evidence. If evidence is insufficient, answer "uncertain."
```

### Pattern 2: Red Team Review

```
You are a red team reviewer. Your job is to find flaws in this finding.

Evidence:
[raw output, commands, timestamps, assertions]

Attack the finding:
- What alternative explanations exist for the observed result?
- What evidence is missing that would strengthen the claim?
- What would falsify this finding?
- Is the evidence sufficient to support the claim?

Be specific. Cite evidence for every criticism.
```

### Pattern 3: Patch Diff Review

```
You are reviewing whether this finding would survive a patch.

Evidence:
[raw output, commands, timestamps, assertions]
Patch description: [if available]

Questions:
1. Does the patch address the root cause exercised by this finding?
2. Would the finding still produce the same result after the patch?
3. Is the finding dependent on behavior that the patch changes?

Answer with evidence. If the patch is unavailable, answer "uncertain" for questions 2 and 3.
```

## Information Asymmetry Implementation

### What the Reviewer Sees

- Raw tool output
- Exact commands run
- Timestamps
- Side-effect assertions
- Vulnerability description (for question 4 only)

### What the Reviewer Does NOT See

- Generator's reasoning or analysis
- Generator's confidence level
- Generator's intended verdict
- Generator's self-assessment

### Why This Matters

- Prevents anchoring bias
- Prevents false agreement
- Forces evidence-based evaluation
- Surfaces generator blind spots

## Evidence-Grounded Disagreement Protocol

When the reviewer disagrees with the generator's implied conclusion:

1. **State the disagreement clearly**
   ```
   DISAGREEMENT: [specific claim] is not supported by the evidence.
   ```

2. **Cite the specific evidence gap**
   ```
   EVIDENCE GAP: [what is missing or contradictory]
   ```

3. **Propose a resolution**
   ```
   RESOLUTION: [what evidence would resolve the disagreement]
   ```

4. **Classify the disagreement**
   - `FATAL` — The finding cannot be VERIFIED without resolution
   - `SIGNIFICANT` — The finding is weakened but may still be valid
   - `MINOR` — The finding is valid but could be stronger

## False Agreement Prevention

### Signs of False Agreement

- Reviewer agrees without citing specific evidence
- Reviewer uses the generator's terminology without verification
- Reviewer does not propose alternative explanations
- Reviewer does not identify missing evidence

### Prevention Techniques

1. **Require evidence citations** — Every answer must cite specific evidence
2. **Require alternative explanations** — Reviewer must propose at least one
3. **Require falsification test** — Reviewer must state what would disprove the finding
4. **Blind review** — Reviewer must not see generator's reasoning (information asymmetry)
5. **Structured output** — Use a format that forces specificity

### Reviewer Output Format

```
## Adversarial Review

### Specificity
Answer: [yes/no/uncertain]
Evidence: [specific citation]
Alternative explanation: [if any]

### Targeting
Answer: [yes/no/uncertain]
Evidence: [specific citation]
Alternative explanation: [if any]

### Patch Resistance
Answer: [yes/no/uncertain]
Evidence: [specific citation]
Alternative explanation: [if any]

### Description Match
Answer: [yes/no/uncertain]
Evidence: [specific citation]
Alternative explanation: [if any]

### Disagreements
1. [disagreement] — [classification: FATAL/SIGNIFICANT/MINOR]
   Evidence gap: [what is missing]
   Resolution: [what would resolve it]

### Missing Evidence
- [evidence that would strengthen the finding]

### Falsification Test
- [what would disprove this finding]
```

## Reviewer Mindset

### Do

- Assume the finding is false until proven otherwise
- Look for alternative explanations
- Identify missing evidence
- Propose falsification tests
- Cite specific evidence for every answer

### Do Not

- Accept claims without evidence
- Use the generator's terminology without verification
- Agree because the finding is plausible
- Skip the falsification test
- Let confidence substitute for evidence

## Escalation

If the reviewer identifies a FATAL disagreement:

1. Document the disagreement with evidence
2. Do not collapse into VERIFIED
3. Either:
   - Run additional experiments to resolve the disagreement
   - Change verdict to UNVERIFIABLE
   - Change verdict to BLOCKED (if policy prevents resolution)

If the reviewer identifies a SIGNIFICANT disagreement:

1. Document the disagreement
2. Note it in the final report
3. Verdict may still be VERIFIED if the core claim is supported

If the reviewer identifies only MINOR disagreements:

1. Document the disagreements
2. Verdict may be VERIFIED
3. Note improvements for future iterations
