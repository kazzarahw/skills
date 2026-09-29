# Trigger Patterns — Detailed Detection Logic

This file provides detailed detection procedures for each trigger pattern referenced in SKILL.md.

---

## 1. Repeated Failure

**Threshold:** 3+ consecutive failed attempts using the same technique.

**Detection procedure:**

1. Maintain a rolling window of the last 10 tool calls.
2. For each tool call, extract the technique category (see [technique-taxonomy.md](technique-taxonomy.md)).
3. Check if the last 3+ tool calls share the same technique category.
4. Check if the outcomes of those calls indicate failure (error results, no output, or agent expressing frustration).
5. If both conditions are met, trigger.

**SHA-256 pattern detection for tool-call loops:**

```
For each tool call, compute:
    hash = SHA-256(tool_name + normalized_parameters)

Store hashes in a circular buffer of size 10.
If the last 3 hashes are identical → loop detected.
If the last 3 hashes share the same tool_name → technique repetition detected.
```

**Step counter implementation:**

```
consecutive_same_technique = 0
last_technique = None

for call in recent_tool_calls:
    technique = classify_technique(call)
    if technique == last_technique:
        consecutive_same_technique += 1
    else:
        consecutive_same_technique = 1
        last_technique = technique

if consecutive_same_technique >= 3:
    trigger("repeated_failure")
```

---

## 2. No Progress

**Threshold:** 10+ tool calls without producing a candidate output.

**Detection procedure:**

1. Count tool calls since the last candidate output (file written, finding reported, hypothesis stated).
2. If count >= 10, trigger.
3. Reset counter when a candidate output is produced.

**Candidate output definition:**
- A file written to disk (not a temp file)
- A finding reported in the agent's response
- A hypothesis explicitly stated and tested
- A PoC or proof-of-concept artifact

---

## 3. Rabbit Hole

**Threshold:** Agent reading code unrelated to the attack surface.

**Detection procedure:**

1. Identify the attack surface from the engagement parameters (in-scope files, endpoints, binaries).
2. For each tool call, check if the target (file path, URL, binary) is within the attack surface.
3. If 5+ consecutive tool calls target code outside the attack surface, trigger.
4. Exception: Reading library/dependency code that is directly called by in-scope code is NOT a rabbit hole.

**Indicators of rabbit hole behavior:**
- Reading test files when the target is production code
- Reading documentation for unrelated libraries
- Auditing dependency source when the vulnerability is in application logic
- Exploring features not exposed to the attacker

---

## 4. Known-Bad Approach

**Threshold:** Agent about to try a technique that cannot succeed.

**Detection procedure:**

1. Maintain a table of technique-to-target incompatibilities:

| Target Type | Incompatible Techniques |
|-------------|------------------------|
| NoSQL database | SQL injection |
| Static site (no backend) | Server-side request forgery |
| Compiled binary (no source) | Source code review |
| Encrypted protocol (no key) | Passive eavesdropping |
| Client-side only app | Server-side exploitation |

2. Before each tool call, check if the planned technique is incompatible with the target.
3. If incompatible, trigger immediately.

---

## 5. Scope Drift

**Threshold:** Agent working outside engagement boundaries.

**Detection procedure:**

1. Extract in-scope targets from engagement parameters (URLs, IP ranges, file paths, binaries).
2. For each tool call, check if the target is within scope.
3. If 3+ consecutive tool calls target out-of-scope resources, trigger.
4. Out-of-scope indicators:
   - Testing endpoints not listed in engagement parameters
   - Attacking infrastructure not owned by the target organization
   - Enumerating systems outside the defined IP range

---

## 6. Reward Hacking

**Threshold:** Skipping verification, hardcoding outputs, or gaming the scoring.

**Detection procedure:**

1. Check for hardcoded outputs: agent writes a file containing expected values without deriving them.
2. Check for skipped verification: agent claims success without running the exploit.
3. Check for output manipulation: agent modifies test results or scoring artifacts.
4. If any indicator is found, trigger immediately.

**Indicators:**
- Writing a "flag" file without executing the exploit
- Modifying test scripts to pass
- Claiming a vulnerability exists without demonstrating it
- Editing scoring or grading files

---

## 7. Overthinking

**Threshold:** Excessive reasoning without action.

**Detection procedure:**

1. Count consecutive analysis paragraphs (text blocks > 3 sentences) without an intervening tool call.
2. If 5+ consecutive analysis paragraphs occur without a tool call, trigger.
3. Exception: Initial reconnaissance phase (first 5 minutes) allows more analysis.

**Indicators:**
- Repeatedly restating the problem
- Enumerating possibilities without testing them
- Long chains of "if-then" reasoning without action
- Expressing uncertainty without resolving it through testing

---

## 8. Perfectionism Bias

**Threshold:** Optimizing beyond task constraints.

**Detection procedure:**

1. Check if the agent is refining an already-working solution.
2. Check if the refinement is necessary for the engagement objective.
3. If the agent is polishing beyond requirements, trigger.

**Indicators:**
- Refactoring exploit code when a rough PoC suffices
- Adding error handling to a one-shot exploit
- Optimizing payload size when no size constraint exists
- Adding features beyond the engagement scope

---

## Time-Per-Step Tracking

**Purpose:** Measure how long the agent spends on each approach.

**Implementation:**

```
approach_start_time = None
current_approach = None

for event in agent_events:
    if event.type == "tool_call":
        technique = classify_technique(event)
        if technique != current_approach:
            if current_approach is not None:
                duration = now() - approach_start_time
                log_approach_duration(current_approach, duration)
            current_approach = technique
            approach_start_time = now()
```

**Thresholds:**

| Duration | Action |
|----------|--------|
| 10+ minutes on one approach | Consider "no progress" trigger |
| 20+ minutes on one approach | Strong "no progress" trigger |
| 30+ minutes total stuck | Escalation criteria met |

---

## Priority Resolution

When multiple triggers fire simultaneously, resolve by priority:

1. **Reward hacking** (highest — integrity violation)
2. **Scope drift** (engagement violation)
3. **Known-bad approach** (prevent wasted effort)
4. **Repeated failure** (active stuck state)
5. **No progress** (passive stuck state)
6. **Rabbit hole** (misguided effort)
7. **Overthinking** (analysis paralysis)
8. **Perfectionism bias** (lowest — still making progress)

Output only the highest-priority trigger's directive.
