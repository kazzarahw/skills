# Priority Resolution

## Table of Contents

- [Priority Order](#priority-order)
- [Resolution Rules](#resolution-rules)
- [Simultaneous Pattern Resolution](#simultaneous-pattern-resolution)
- [Priority Resolution Examples](#priority-resolution-examples)
- [Escalation Procedures](#escalation-procedures)
- [Priority Resolution Flowchart](#priority-resolution-flowchart)
- [Special Cases](#special-cases)

This file defines the priority resolution rules for when multiple trigger patterns are detected simultaneously.

---

## Priority Order

When multiple patterns are detected, resolve by the following priority (highest to lowest):

| Priority | Pattern | Rationale |
|----------|---------|-----------|
| 1 | **Scope drift** | Engagement violation — stop immediately |
| 2 | **Reward hacking** | Integrity violation — stop immediately |
| 3 | **Known-bad approach** | Prevent wasted effort — redirect to viable technique |
| 4 | **Repeated failure** | Active stuck state — suggest alternative approach |
| 5 | **Rabbit hole** | Misguided effort — redirect to attack surface |
| 6 | **No progress** | Passive stuck state — suggest structured approach |
| 7 | **Overthinking** | Analysis paralysis — encourage action |
| 8 | **Perfectionism bias** | Optimizing beyond constraints — encourage "good enough" |
| 9 | **Confirmation bias** | Only seeking confirming evidence — encourage disconfirming tests |
| 10 | **Tool fixation** | Using same tool despite failures — suggest alternative tool |

---

## Resolution Rules

### Rule 1: Integrity and Scope First

**Scope drift** and **reward hacking** always take precedence because they represent engagement violations that could have serious consequences.

```
IF scope_drift detected:
    INTERVENE immediately with scope redirect
    Do NOT address other patterns until scope is corrected

IF reward_hacking detected:
    INTERVENE immediately with verification demand
    Do NOT address other patterns until integrity is restored
```

### Rule 2: Prevention Before Correction

**Known-bad approach** takes precedence over active stuck states because preventing wasted effort is more efficient than correcting it.

```
IF known_bad_approach detected:
    INTERVENE to redirect to viable technique
    This may also resolve repeated_failure or tool_fixation
```

### Rule 3: Active Before Passive

**Repeated failure** (active stuck) takes precedence over **no progress** (passive stuck) because the agent is actively engaged but ineffective.

```
IF repeated_failure AND no_progress:
    ADDRESS repeated_failure first
    The alternative approach suggestion may also resolve no_progress
```

### Rule 4: Redirect Before Encourage

Patterns that require redirection (rabbit hole, scope drift) take precedence than patterns that require encouragement (overthinking, perfectionism).

```
IF rabbit_hole AND overthinking:
    ADDRESS rabbit_hole first
    Redirecting to attack surface may also resolve overthinking
```

### Rule 5: One Directive Per Intervention

Even when multiple patterns are detected, only the highest-priority pattern receives an intervention. Addressing multiple patterns simultaneously violates the "one directive per intervention" rule.

```
IF multiple_patterns detected:
    SELECT highest_priority(patterns)
    GENERATE intervention for that pattern ONLY
    DEFER other patterns to next intervention cycle
```

---

## Simultaneous Pattern Resolution

### Common Co-Occurrence Scenarios

#### Scenario 1: Scope Drift + Rabbit Hole

**Detection:** Agent is reading code outside the attack surface, and that code is also outside the engagement scope.

**Resolution:**
```
PRIORITY: Scope drift (1) > Rabbit hole (5)

INTERVENTION: "You're outside the engagement scope. Return to the in-scope targets: [scope]."

RATIONALE: Scope violation takes precedence. Correcting scope may also resolve the rabbit hole.
```

#### Scenario 2: Reward Hacking + Confirmation Bias

**Detection:** Agent is only running tests that confirm their hypothesis, and claiming success without verification.

**Resolution:**
```
PRIORITY: Reward hacking (2) > Confirmation bias (9)

INTERVENTION: "Verify your findings before reporting. Demonstrate that [claim] actually works."

RATIONALE: Integrity violation takes precedence. Enforcing verification may also resolve confirmation bias.
```

#### Scenario 3: Repeated Failure + Tool Fixation

**Detection:** Agent is using the same tool repeatedly, and each attempt fails.

**Resolution:**
```
PRIORITY: Repeated failure (4) > Tool fixation (10)

INTERVENTION: "You've tried [tool] [N] times without success. Try [alternative] instead."

RATIONALE: Addressing the failure with an alternative approach also resolves the tool fixation.
```

#### Scenario 4: No Progress + Overthinking

**Detection:** Agent has made many tool calls without producing output, and is writing long analysis paragraphs without acting.

**Resolution:**
```
PRIORITY: No progress (6) > Overthinking (7)

INTERVENTION: "You've made [N] calls without producing a candidate output. Form a hypothesis and test it now."

RATIONALE: Encouraging action to produce output also addresses the overthinking.
```

#### Scenario 5: Known-Bad Approach + Repeated Failure

**Detection:** Agent is using a technique incompatible with the target, and it keeps failing.

**Resolution:**
```
PRIORITY: Known-bad approach (3) > Repeated failure (4)

INTERVENTION: "[Technique] is incompatible with [target_type]. Try [alternative] instead."

RATIONALE: Redirecting to a viable technique also resolves the repeated failure.
```

#### Scenario 6: Perfectionism Bias + No Progress

**Detection:** Agent is polishing an existing artifact instead of producing new output.

**Resolution:**
```
PRIORITY: No progress (6) > Perfectionism bias (8)

INTERVENTION: "You've made [N] calls without producing a candidate output. Move to the next objective."

RATIONALE: Redirecting to produce output also addresses the perfectionism.
```

---

## Priority Resolution Examples

### Example 1: Multiple Patterns Detected

**Detected patterns:**
- Scope drift (agent testing staging.example.com)
- No progress (15 calls without output)
- Overthinking (6 analysis paragraphs)

**Resolution:**
```
ACTIVE: Scope drift (priority 1)
DEFERRED: No progress, Overthinking

INTERVENTION: "You're outside the engagement scope. Return to the in-scope targets: www.example.com."

NEXT CYCLE: If no progress persists after scope correction, address no progress.
```

### Example 2: Integrity + Stuck State

**Detected patterns:**
- Reward hacking (claiming success without verification)
- Repeated failure (4 failed exploit attempts)

**Resolution:**
```
ACTIVE: Reward hacking (priority 2)
DEFERRED: Repeated failure

INTERVENTION: "Verify your findings before reporting. Demonstrate that the exploit actually works."

NEXT CYCLE: If repeated failure persists after verification, address the failure.
```

### Example 3: Prevention + Active Stuck

**Detected patterns:**
- Known-bad approach (SQLi against NoSQL)
- Repeated failure (3 failed SQLi attempts)
- Tool fixation (using sqlmap 5 times)

**Resolution:**
```
ACTIVE: Known-bad approach (priority 3)
DEFERRED: Repeated failure, Tool fixation

INTERVENTION: "SQL injection is incompatible with a NoSQL database. Try NoSQL-specific injection techniques instead."

NEXT CYCLE: Monitor if agent switches to a viable technique.
```

---

## Escalation Procedures

### When Patterns Conflict

If two patterns suggest contradictory interventions:

1. **Always follow the priority order** — Higher priority pattern wins
2. **Do not combine interventions** — One directive per intervention
3. **Defer lower-priority patterns** — Address them in subsequent cycles
4. **Monitor for resolution** — Correcting a high-priority pattern may resolve lower-priority ones

### Escalation Triggers

Escalate to user when:

| Condition | Action |
|-----------|--------|
| 3+ interventions for same pattern | Escalate — agent cannot self-correct |
| Scope drift persists after 2 interventions | Escalate — engagement violation |
| Reward hacking detected | Escalate — integrity violation |
| Multiple high-priority patterns co-occur | Escalate — complex situation |
| 30+ minutes without progress | Escalate — agent fundamentally stuck |
| Regression to specific level twice | Escalate — agent cannot maintain independence |

### Escalation Format

```
COACH: [Pattern] has persisted for [duration] with [N] interventions.
The agent has tried [approaches] without success.
Consider providing additional guidance or switching to a different approach.
```

---

## Priority Resolution Flowchart

```
Multiple patterns detected
        │
        ▼
Extract all detected patterns
        │
        ▼
Sort by priority (1-10)
        │
        ▼
Select highest priority pattern
        │
        ▼
Generate intervention for that pattern
        │
        ▼
Output: COACH: [one directive]
        │
        ▼
Monitor agent response
        │
        ├── Success → Record outcome, check progression
        │
        └── Failure → Record outcome, check regression
                        │
                        ▼
                Next intervention cycle
                (address next highest priority pattern)
```

---

## Special Cases

### Case 1: All Patterns at Same Priority

If two patterns have the same priority (should not happen with the defined order), resolve by:
1. Which pattern was detected first
2. Which pattern has higher confidence
3. Which pattern is easier to address

### Case 2: Pattern Resolved by Another's Intervention

If addressing the highest-priority pattern also resolves a lower-priority pattern:
1. Note the resolution in the intervention record
2. Do not generate a separate intervention for the resolved pattern
3. Monitor for recurrence

### Case 3: New Pattern Emerges During Intervention

If a new pattern emerges while addressing an existing one:
1. Complete the current intervention
2. Assess the new pattern's priority
3. If higher priority, address it next
4. If lower priority, defer it to the next cycle
