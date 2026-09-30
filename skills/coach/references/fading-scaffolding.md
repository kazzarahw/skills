# Fading Scaffolding

## Table of Contents

- [Overview](#overview)
- [Level Progression Rules](#level-progression-rules)
- [Level Regression Rules](#level-regression-rules)
- [State Tracking](#state-tracking)
- [Fading Schedule Algorithm](#fading-schedule-algorithm)
- [Examples of Fading in Practice](#examples-of-fading-in-practice)
- [When to Escalate to User](#when-to-escalate-to-user)
- [State Persistence](#state-persistence)
- [Integration with Trigger Detector](#integration-with-trigger-detector)

This file details the fading scaffolding system used by the security coach to gradually reduce guidance as the agent demonstrates competence.

---

## Overview

Fading scaffolding is a pedagogical technique where interventions start with **specific** guidance and progressively fade to **minimal** prompts as the agent demonstrates the ability to self-correct. The goal is to build the agent's independence over time.

### Three Levels

| Level | Name | Description | When Used |
|-------|------|-------------|-----------|
| 1 | **Specific** | Exact command, technique, or detailed step-by-step guidance | First intervention for a pattern |
| 2 | **General** | Direction or category suggestion | Second intervention for same pattern |
| 3 | **Minimal** | Question or prompt to stimulate self-correction | Third+ intervention for same pattern |

### Level Progression Example

```
Intervention 1 (Specific):
  COACH: You've tried nmap SYN scan 3 times without success. Try a UDP scan instead.

Intervention 2 (General):
  COACH: The current approach isn't working. Consider a different scanning technique.

Intervention 3 (Minimal):
  COACH: What fundamentally different approach haven't you tried yet?
```

---

## Level Progression Rules

### When to Progress (Fade Out)

Progress to the next level (less specific) when:

1. **Agent demonstrates understanding** — The agent acknowledges the intervention and changes approach
2. **Agent self-corrects** — The agent identifies and fixes the issue without further intervention
3. **Agent produces output** — The agent generates a candidate output after the intervention
4. **Agent asks a clarifying question** — The agent engages with the intervention constructively

### Progression Algorithm

```
function should_progress(state):
    if state.intervention_count == 0:
        return False  # First intervention is always specific

    if state.last_outcome == "success":
        state.consecutive_successes += 1
        if state.consecutive_successes >= 2:
            return True  # Agent has shown they can self-correct

    if state.intervention_count >= 2 and state.last_outcome != "failure":
        return True  # Default progression after 2 interventions

    return False
```

### Progression Triggers

| Trigger | Action |
|---------|--------|
| Agent changes approach after intervention | Progress to next level |
| Agent produces candidate output | Progress to next level |
| Agent self-corrects without intervention | Progress to next level |
| 2 interventions with no regression | Progress to next level |
| Agent explicitly says "I understand" | Progress to next level |

---

## Level Regression Rules

### When to Regress (Fade In)

Regress to the previous level (more specific) when:

1. **Agent ignores the intervention** — The agent continues the same behavior
2. **Agent fails to change approach** — The agent acknowledges but doesn't act
3. **Agent regresses to previous behavior** — The agent returns to the problematic pattern
4. **Agent produces incorrect output** — The agent's output is wrong or incomplete
5. **Agent expresses confusion** — The agent doesn't understand the intervention

### Regression Algorithm

```
function should_regress(state):
    if state.last_outcome == "failure":
        state.consecutive_failures += 1
        if state.consecutive_failures >= 2:
            return True  # Agent needs more specific guidance

    if state.intervention_count >= 3 and state.last_outcome == "failure":
        return True  # Agent hasn't responded to minimal guidance

    return False
```

### Regression Triggers

| Trigger | Action |
|---------|--------|
| Agent continues same behavior after intervention | Regress to previous level |
| Agent produces incorrect output | Regress to previous level |
| Agent expresses confusion | Regress to previous level |
| 2 consecutive failures after intervention | Regress to previous level |
| Agent returns to problematic pattern | Regress to previous level |

---

## State Tracking

### Pattern History

For each trigger pattern, maintain:

```python
@dataclass
class PatternState:
    pattern_type: str           # e.g., "repeated_failure"
    intervention_count: int = 0  # Total interventions for this pattern
    current_level: int = 1       # 1=specific, 2=general, 3=minimal
    last_intervention: float = 0.0  # Timestamp
    last_outcome: str = ""       # "success", "failure", "neutral"
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    history: List[Dict] = []     # Full intervention history
```

### Intervention History

Each intervention record contains:

```python
@dataclass
class InterventionRecord:
    timestamp: float
    pattern_type: str
    level: int
    directive: str
    outcome: str          # "success", "failure", "neutral"
    context: Dict         # Tool calls, agent state, etc.
```

### Success/Failure Tracking

**Success indicators:**
- Agent changes approach after intervention
- Agent produces candidate output within 5 tool calls
- Agent self-corrects the behavior
- Agent acknowledges and acts on the intervention

**Failure indicators:**
- Agent continues same behavior after intervention
- Agent produces incorrect or no output
- Agent expresses confusion or ignores the intervention
- Agent regresses to the problematic pattern

---

## Fading Schedule Algorithm

### Main Algorithm

```
function get_intervention(pattern_type, context):
    state = get_or_create_state(pattern_type)

    # Check minimum interval (5 minutes between interventions)
    if now() - state.last_intervention < 300:
        return None  # Too soon

    # Determine level based on state
    level = state.current_level

    # Get directive for this level
    directive = generate_directive(pattern_type, level, context)

    # Update state
    state.intervention_count += 1
    state.last_intervention = now()
    state.history.append({
        "timestamp": now(),
        "level": level,
        "directive": directive,
        "outcome": "pending"
    })

    return directive

function record_outcome(pattern_type, outcome):
    state = get_state(pattern_type)
    state.last_outcome = outcome

    # Update consecutive counters
    if outcome == "success":
        state.consecutive_successes += 1
        state.consecutive_failures = 0
    elif outcome == "failure":
        state.consecutive_failures += 1
        state.consecutive_successes = 0

    # Check for progression
    if should_progress(state):
        if state.current_level < 3:
            state.current_level += 1
            state.consecutive_successes = 0

    # Check for regression
    if should_regress(state):
        if state.current_level > 1:
            state.current_level -= 1
            state.consecutive_failures = 0

    # Update history
    state.history[-1]["outcome"] = outcome
```

### Fading Schedule Table

| Intervention # | Default Level | Progression Condition | Regression Condition |
|----------------|---------------|----------------------|---------------------|
| 1 | Specific (1) | Agent changes approach | Agent ignores intervention |
| 2 | Specific or General (1-2) | Agent produces output | Agent continues same behavior |
| 3 | General or Minimal (2-3) | Agent self-corrects | Agent produces incorrect output |
| 4+ | Minimal (3) | Agent demonstrates independence | Agent returns to pattern |

---

## Examples of Fading in Practice

### Example 1: Repeated Failure (Successful Fading)

```
Intervention 1 (Specific):
  COACH: You've tried sqlmap 3 times without success. Try manual SQL injection with crafted payloads instead.
  Outcome: Agent switches to manual testing → SUCCESS

Intervention 2 (General):
  COACH: The current approach isn't working. Consider a different injection technique.
  Outcome: Agent tries a new technique → SUCCESS

Intervention 3 (Minimal):
  COACH: What other attack vectors haven't you tried?
  Outcome: Agent identifies and tests new vector → SUCCESS

Result: Agent has learned to self-correct. No further intervention needed.
```

### Example 2: No Progress (Regression Needed)

```
Intervention 1 (Specific):
  COACH: You've made 12 calls without producing output. Form a hypothesis and test it with a targeted scan.
  Outcome: Agent continues reading code → FAILURE

Intervention 2 (General):
  COACH: Step back and map the attack surface before diving deeper.
  Outcome: Agent continues reading code → FAILURE

Intervention 3 (Minimal):
  COACH: What hypothesis can you test right now?
  Outcome: Agent finally forms a hypothesis → SUCCESS

Intervention 4 (Specific — regression):
  COACH: Test your hypothesis by running [specific_tool] against [specific_target].
  Outcome: Agent runs the test → SUCCESS

Result: Agent needed more specific guidance after minimal failed.
```

### Example 3: Scope Drift (Immediate Escalation)

```
Intervention 1 (Specific):
  COACH: You're outside the engagement scope. Return to the in-scope targets: www.example.com.
  Outcome: Agent continues testing out-of-scope target → FAILURE

Intervention 2 (General):
  COACH: Verify your target is in scope before proceeding.
  Outcome: Agent acknowledges and returns to scope → SUCCESS

Result: Agent corrected after 2 interventions. Monitor for recurrence.
```

---

## When to Escalate to User

Escalate to the user when:

1. **3+ interventions for the same pattern** — The agent is not self-correcting
2. **Regression to specific level twice** — The agent cannot maintain independence
3. **Scope drift persists** — The agent continues out-of-scope after intervention
4. **Reward hacking detected** — Integrity violations require user attention
5. **30+ minutes without progress** — The agent may be fundamentally stuck
6. **Multiple patterns co-occur** — The agent may need comprehensive guidance

### Escalation Format

```
COACH: The agent has been stuck on [pattern] for [duration] with [N] interventions.
Consider providing additional guidance or switching to a different approach.
```

---

## State Persistence

### Across Sessions

Fading state should persist across sessions to maintain continuity:

```python
def save_state(state, filepath):
    """Save fading state to disk."""
    with open(filepath, 'w') as f:
        json.dump({
            "pattern_type": state.pattern_type,
            "intervention_count": state.intervention_count,
            "current_level": state.current_level,
            "last_intervention": state.last_intervention,
            "consecutive_successes": state.consecutive_successes,
            "consecutive_failures": state.consecutive_failures,
            "history": state.history,
        }, f, indent=2)

def load_state(filepath):
    """Load fading state from disk."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return PatternState(**data)
```

### State Reset

Reset fading state when:
- A new engagement begins
- The agent demonstrates sustained independence (5+ successful self-corrections)
- The user explicitly requests a reset
- The pattern has not been triggered for 30+ minutes

---

## Integration with Trigger Detector

The fading scaffolding system integrates with the trigger detector as follows:

```
1. Trigger detector identifies a pattern
2. Fading schedule determines the appropriate level
3. Intervention is generated at that level
4. Agent acts on the intervention
5. Outcome is recorded
6. Fading schedule updates state (progression or regression)
7. Next intervention uses updated level
```

This creates a feedback loop that adapts to the agent's needs over time.
