# Intervention Templates

## Table of Contents

- [Usage](#usage)
- [1. Repeated Failure Interventions](#1-repeated-failure-interventions)
- [2. No Progress Interventions](#2-no-progress-interventions)
- [3. Rabbit Hole Interventions](#3-rabbit-hole-interventions)
- [4. Known-Bad Approach Interventions](#4-known-bad-approach-interventions)
- [5. Scope Drift Interventions](#5-scope-drift-interventions)
- [6. Reward Hacking Interventions](#6-reward-hacking-interventions)
- [7. Overthinking Interventions](#7-overthinking-interventions)
- [8. Perfectionism Bias Interventions](#8-perfectionism-bias-interventions)
- [9. Confirmation Bias Interventions](#9-confirmation-bias-interventions)
- [10. Tool Fixation Interventions](#10-tool-fixation-interventions)
- [Intervention Delivery Rules](#intervention-delivery-rules)

This file provides intervention templates organized by pattern type. Each pattern has three specificity levels: **specific**, **general**, and **minimal**.

---

## Usage

Interventions follow the format:

```
COACH: [one directive]
```

**Rules:**
- One directive per intervention
- Specific, actionable, and short
- Never reveal answers or vulnerability details
- Meta-guidance only — suggest *how* to approach, not *what* the answer is

---

## 1. Repeated Failure Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You've tried [technique] [N] times without success. Try [specific_alternative] instead.
```

**Example:**
```
COACH: You've tried nmap SYN scan 3 times without success. Try a UDP scan or connect scan instead.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: The current approach isn't working. Consider a different [technique_category] technique.
```

**Example:**
```
COACH: The current approach isn't working. Consider a different network enumeration technique.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What fundamentally different approach haven't you tried yet?
```

**Example:**
```
COACH: What fundamentally different approach haven't you tried yet?
```

### Escalation Procedure

If the agent continues after 3 interventions for the same pattern:
1. Escalate to user: "The agent has tried [N] approaches for [pattern]. Consider providing additional guidance."
2. Suggest model switch if the agent appears unable to self-correct.
3. Document the pattern for future reference.

---

## 2. No Progress Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You've made [N] calls without producing a candidate output. Form a hypothesis and test it with [specific_action].
```

**Example:**
```
COACH: You've made 12 calls without producing a candidate output. Form a hypothesis about the vulnerability class and test it with a targeted scan.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Step back and map the attack surface. Identify the most likely entry point and test it.
```

**Example:**
```
COACH: Step back and map the attack surface. Identify the most likely entry point and test it.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What hypothesis can you test right now?
```

**Example:**
```
COACH: What hypothesis can you test right now?
```

### Escalation Procedure

If the agent continues without producing output after 3 interventions:
1. Suggest a structured approach: "Try the [skill_name] methodology for a systematic approach."
2. Recommend breaking the problem into smaller steps.
3. Escalate to user if no progress after 30+ minutes.

---

## 3. Rabbit Hole Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You're analyzing [out_of_scope_component] which is outside the attack surface. Return to [in_scope_target].
```

**Example:**
```
COACH: You're analyzing the ORM library internals which is outside the attack surface. Return to the application query construction code.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Focus on code paths reachable from the attacker-controlled input. The vulnerability is likely in application logic, not dependencies.
```

**Example:**
```
COACH: Focus on code paths reachable from the attacker-controlled input. The vulnerability is likely in application logic, not dependencies.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: Is the code you're reading reachable from the attack surface?
```

**Example:**
```
COACH: Is the code you're reading reachable from the attack surface?
```

### Escalation Procedure

If the agent continues reading irrelevant code after 3 interventions:
1. Strongly redirect: "Return to the in-scope attack surface immediately."
2. Suggest reviewing the engagement parameters to re-establish scope.
3. Escalate to user if the agent cannot self-correct.

---

## 4. Known-Bad Approach Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: [Technique] is incompatible with [target_type]. Try [specific_alternative] instead.
```

**Example:**
```
COACH: SQL injection is incompatible with a NoSQL database. Try NoSQL-specific injection techniques or command injection instead.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: This technique cannot succeed against this target type. Consider [alternative_category] instead.
```

**Example:**
```
COACH: This technique cannot succeed against this target type. Consider client-side attack vectors instead.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What attack vectors are viable against this target type?
```

**Example:**
```
COACH: What attack vectors are viable against this target type?
```

### Escalation Procedure

If the agent continues with the incompatible approach after 2 interventions:
1. Strongly redirect: "This approach cannot work. Switch to a viable technique immediately."
2. Explain why the technique is incompatible (without revealing the answer).
3. Escalate to user if the agent cannot identify a viable alternative.

---

## 5. Scope Drift Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You're outside the engagement scope. Return to the in-scope targets: [scope_summary].
```

**Example:**
```
COACH: You're outside the engagement scope. Return to the in-scope targets: www.example.com and 192.168.1.0/24.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Verify your target is in scope before proceeding. The engagement only authorizes [scope_category].
```

**Example:**
```
COACH: Verify your target is in scope before proceeding. The engagement only authorizes the production web application.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: Is your current target in scope?
```

**Example:**
```
COACH: Is your current target in scope?
```

### Escalation Procedure

If the agent continues out-of-scope after 2 interventions:
1. Immediate halt: "STOP. Return to in-scope targets immediately."
2. Remind of engagement boundaries and authorization.
3. Escalate to user — scope violations are serious engagement risks.

---

## 6. Reward Hacking Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: Verify your findings before reporting. Demonstrate that [specific_claim] actually works.
```

**Example:**
```
COACH: Verify your findings before reporting. Demonstrate that the SQL injection actually extracts data.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Claims without evidence are not findings. Follow proper methodology and verify each step.
```

**Example:**
```
COACH: Claims without evidence are not findings. Follow proper methodology and verify each step.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: Have you verified this finding?
```

**Example:**
```
COACH: Have you verified this finding?
```

### Escalation Procedure

If reward hacking is detected:
1. Immediate intervention — integrity violations are highest priority.
2. Require verification before any findings are accepted.
3. Escalate to user immediately — reward hacking undermines engagement integrity.
4. Document the incident for review.

---

## 7. Overthinking Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You have enough information to act. Try [specific_action] now and adjust based on results.
```

**Example:**
```
COACH: You have enough information to act. Try the most likely attack vector now and adjust based on results.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Set a 5-minute timer and commit to an approach. You can gather more data later if needed.
```

**Example:**
```
COACH: Set a 5-minute timer and commit to an approach. You can gather more data later if needed.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What's the next action you can take right now?
```

**Example:**
```
COACH: What's the next action you can take right now?
```

### Escalation Procedure

If overthinking persists after 3 interventions:
1. Strongly encourage action: "Take the next step now, even if imperfect."
2. Suggest a structured decision-making framework.
3. Escalate to user if the agent remains paralyzed.

---

## 8. Perfectionism Bias Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: Your current approach is sufficient. Move to the next objective instead of refining.
```

**Example:**
```
COACH: Your current approach is sufficient. Move to the next objective instead of refining.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: Good enough is sufficient. You can refine later if needed — focus on completing the task.
```

**Example:**
```
COACH: Good enough is sufficient. You can refine later if needed — focus on completing the task.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: Is this refinement necessary for the objective?
```

**Example:**
```
COACH: Is this refinement necessary for the objective?
```

### Escalation Procedure

If perfectionism blocks progress after 3 interventions:
1. Redirect to the primary objective.
2. Set a time limit for the current task.
3. Escalate to user if the agent cannot move forward.

---

## 9. Confirmation Bias Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: Try to disprove your hypothesis. What evidence would show that [hypothesis] is wrong?
```

**Example:**
```
COACH: Try to disprove your hypothesis. What evidence would show that the vulnerability is NOT in the authentication module?
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: You've only run confirming tests. Try a test that could fail and see what happens.
```

**Example:**
```
COACH: You've only run confirming tests. Try a test that could fail and see what happens.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What would prove your hypothesis wrong?
```

**Example:**
```
COACH: What would prove your hypothesis wrong?
```

### Escalation Procedure

If confirmation bias persists after 3 interventions:
1. Require the agent to test alternative hypotheses.
2. Suggest a structured hypothesis-testing approach.
3. Escalate to user if the agent cannot consider alternatives.

---

## 10. Tool Fixation Interventions

### Specific (Level 1 — First Intervention)

**Template:**
```
COACH: You've tried [tool] [N] times without success. Try [specific_alternative_tool] instead.
```

**Example:**
```
COACH: You've tried gobuster 6 times without success. Try ffuf with a different wordlist instead.
```

### General (Level 2 — Second Intervention)

**Template:**
```
COACH: This tool may not be effective for this target. Consider a different [tool_category] approach.
```

**Example:**
```
COACH: This tool may not be effective for this target. Consider a different directory enumeration approach.
```

### Minimal (Level 3 — Third+ Intervention)

**Template:**
```
COACH: What other tools could achieve the same objective?
```

**Example:**
```
COACH: What other tools could achieve the same objective?
```

### Escalation Procedure

If tool fixation persists after 3 interventions:
1. Strongly suggest alternative tools.
2. Explain why the current tool may not be effective.
3. Escalate to user if the agent cannot switch tools.

---

## Intervention Delivery Rules

### Timing
- Wait for a natural pause in agent activity (between tool calls)
- Do not interrupt mid-execution
- Allow the agent to complete the current thought before intervening

### Frequency
- Maximum one intervention per pattern per 5-minute window
- Do not stack multiple interventions
- If multiple patterns are detected, address only the highest-priority one

### Tone
- Direct but not hostile
- Helpful, not condescending
- Actionable, not vague
- Respectful of the agent's autonomy

### Format
- Always prefix with `COACH:`
- One sentence, one action
- No essays or multi-paragraph explanations
- No follow-up questions unless at minimal level
