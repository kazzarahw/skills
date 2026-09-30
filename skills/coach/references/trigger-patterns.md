# Trigger Patterns — Detailed Detection Logic

## Table of Contents

- [1. Repeated Failure](#1-repeated-failure)
- [2. No Progress](#2-no-progress)
- [3. Rabbit Hole](#3-rabbit-hole)
- [4. Known-Bad Approach](#4-known-bad-approach)
- [5. Scope Drift](#5-scope-drift)
- [6. Reward Hacking](#6-reward-hacking)
- [7. Overthinking](#7-overthinking)
- [8. Perfectionism Bias](#8-perfectionism-bias)
- [9. Confirmation Bias](#9-confirmation-bias)
- [10. Tool Fixation](#10-tool-fixation)
- [Time-Per-Step Tracking](#time-per-step-tracking)
- [Pattern Interaction Matrix](#pattern-interaction-matrix)

This file provides detailed detection procedures for each trigger pattern referenced in SKILL.md.

---

## 1. Repeated Failure

**Threshold:** 3+ consecutive failed attempts using the same technique.

**Detection signals:**
- Same tool called 3+ times with identical or near-identical parameters
- Each call returns an error, empty result, or explicit failure indicator
- Agent expresses frustration or acknowledges failure in text output
- No variation in approach between attempts

**Detection algorithm:**

```
Maintain a rolling window of the last 10 tool calls.
For each tool call, extract:
  - technique_category (static_analysis, dynamic_analysis, network, web, crypto)
  - normalized_parameters (sorted, deduplicated key-value pairs)
  - outcome (success, failure, empty)

Compute a technique fingerprint:
  fingerprint = SHA-256(technique_category + normalized_parameters)

Store fingerprints in a circular buffer of size 10.

Trigger condition:
  IF last 3 fingerprints are identical AND all 3 outcomes == failure
  THEN trigger("repeated_failure", confidence=0.85)

Escalation condition:
  IF last 5 fingerprints are identical AND all 5 outcomes == failure
  THEN trigger("repeated_failure", confidence=0.95, escalate=True)
```

**Confidence scoring:**

| Consecutive Failures | Confidence | Action |
|----------------------|------------|--------|
| 3 | 0.70 | Suggest alternative approach |
| 4 | 0.85 | Strong suggestion + technique switch |
| 5+ | 0.95 | Escalate to user |

**Examples:**
- Running `nmap -sS -sV` three times against the same target after each returns "host down"
- Calling `sqlmap` with identical parameters three times, each timing out
- Repeatedly attempting the same exploit payload that crashes without producing output

**Intervention suggestions:**
- "You've tried [technique] 3 times without success. Try a fundamentally different vector."
- "The current approach isn't working. Consider [alternative_category] instead."
- "Document what you've ruled out, then identify what attack surface remains."

---

## 2. No Progress

**Threshold:** 10+ tool calls without producing a candidate output.

**Detection signals:**
- Tool calls are executing successfully but not producing actionable results
- Agent is reading code, running scans, or gathering data without forming hypotheses
- No files written, no findings reported, no hypotheses stated
- Time spent without tangible output

**Detection algorithm:**

```
candidate_output_counter = 0

for each tool_call in history:
    if is_candidate_output(tool_call):
        candidate_output_counter = 0
    else:
        candidate_output_counter += 1

if candidate_output_counter >= 10:
    trigger("no_progress", confidence=min(0.5 + candidate_output_counter * 0.05, 0.95))

function is_candidate_output(tool_call):
    return (
        tool_call produces a file written to disk (not temp) OR
        tool_call result contains a stated hypothesis OR
        tool_call result contains a reported finding OR
        tool_call produces a PoC artifact OR
        tool_call result contains a testable claim
    )
```

**Confidence scoring:**

| Calls Without Output | Confidence | Action |
|----------------------|------------|--------|
| 10 | 0.60 | Suggest structured approach |
| 15 | 0.75 | Strong suggestion + hypothesis prompt |
| 20+ | 0.90 | Escalate — agent may be lost |

**Examples:**
- Reading source files for 30+ minutes without forming a single hypothesis
- Running reconnaissance tools repeatedly without analyzing results
- Browsing documentation without connecting it to the target

**Intervention suggestions:**
- "You've made [N] calls without producing a candidate output. Form a hypothesis and test it."
- "Step back and map the attack surface before diving deeper."
- "Document what you've ruled out so far, then identify what's left to try."

---

## 3. Rabbit Hole

**Threshold:** Agent reading code or analyzing components unrelated to the attack surface.

**Detection signals:**
- Tool calls target files/modules outside the defined attack surface
- Agent is auditing library code when the target is application logic
- Reading test files when production code is the target
- Exploring features not exposed to the attacker
- Deep-diving into dependency internals without justification

**Detection algorithm:**

```
attack_surface = extract_from_engagement_parameters(
    in_scope_files, in_scope_endpoints, in_scope_binaries
)

consecutive_out_of_surface = 0

for each tool_call in recent_history:
    target = extract_target(tool_call)  # file path, URL, binary name

    if target in attack_surface:
        consecutive_out_of_surface = 0
    elif is_dependency_of_attack_surface(target, attack_surface):
        # Reading library code called by in-scope code is acceptable
        consecutive_out_of_surface = 0
    else:
        consecutive_out_of_surface += 1

if consecutive_out_of_surface >= 5:
    trigger("rabbit_hole", confidence=min(0.5 + consecutive_out_of_surface * 0.08, 0.95))
```

**Confidence scoring:**

| Consecutive Out-of-Surface Calls | Confidence | Action |
|----------------------------------|------------|--------|
| 5 | 0.60 | Gentle redirect |
| 8 | 0.75 | Strong redirect to attack surface |
| 12+ | 0.90 | Escalate — agent is lost |

**Examples:**
- Auditing `node_modules` library code when the target is application business logic
- Reading database ORM internals when the vulnerability is in application-level query construction
- Exploring admin panel code when only the public-facing attack surface is in scope

**Intervention suggestions:**
- "You're analyzing code outside the attack surface. Return to the in-scope components."
- "Focus on code paths reachable from the attacker-controlled input."
- "The vulnerability is likely in application logic, not library internals."

---

## 4. Known-Bad Approach

**Threshold:** Agent about to try a technique that cannot succeed against the target.

**Detection signals:**
- Technique is fundamentally incompatible with the target type
- Agent is using a tool designed for a different technology stack
- Approach has been proven ineffective against this target class
- Agent is repeating a technique that has known limitations for the target

**Detection algorithm:**

```
INCOMPATIBILITY_TABLE = {
    "NoSQL database": ["sql_injection", "sqlmap"],
    "Static site (no backend)": ["ssrf", "rce", "file_inclusion"],
    "Compiled binary (no source)": ["source_code_review", "pattern_matching"],
    "Encrypted protocol (no key)": ["passive_eavesdropping", "traffic_analysis"],
    "Client-side only app": ["server_side_exploitation", "sqli", "command_injection"],
    "Read-only filesystem": ["file_write", "persistence"],
    "No network stack": ["network_exploitation", "reverse_shell"],
}

for each tool_call in planned_or_recent:
    technique = classify_technique(tool_call)
    target_type = classify_target(tool_call.target)

    if target_type in INCOMPATIBILITY_TABLE:
        incompatible_techniques = INCOMPATIBILITY_TABLE[target_type]
        if technique in incompatible_techniques:
            trigger("known_bad_approach", confidence=0.90)
```

**Confidence scoring:**

| Condition | Confidence | Action |
|-----------|------------|--------|
| Technique-target mismatch detected | 0.90 | Immediate redirect |
| Technique has known limitation for target | 0.75 | Suggest alternative |
| Agent ignores previous failure of same technique | 0.85 | Strong redirect |

**Examples:**
- Trying SQL injection against a MongoDB database
- Attempting SSRF against a static HTML site
- Using source code review techniques on a stripped binary
- Trying to capture traffic on a fully encrypted protocol without the key

**Intervention suggestions:**
- "This technique is incompatible with the target type. Try [alternative] instead."
- "The target doesn't support this attack vector. Consider [alternative_category]."
- "This approach cannot succeed against [target_type]. Redirect to [viable_vector]."

---

## 5. Scope Drift

**Threshold:** Agent working outside engagement boundaries.

**Detection signals:**
- Testing endpoints not listed in engagement parameters
- Attacking infrastructure not owned by the target organization
- Enumerating systems outside the defined IP range
- Accessing resources explicitly marked as out-of-scope
- Time spent on targets not mentioned in the engagement brief

**Detection algorithm:**

```
in_scope_targets = extract_from_engagement(
    urls, ip_ranges, file_paths, binaries, domains
)

out_of_scope_streak = 0

for each tool_call in recent_history:
    target = extract_target(tool_call)

    if is_in_scope(target, in_scope_targets):
        out_of_scope_streak = 0
    else:
        # Check if it's a related but out-of-scope target
        if is_related_but_out_of_scope(target, in_scope_targets):
            out_of_scope_streak += 1
        else:
            # Completely unrelated target — stronger signal
            out_of_scope_streak += 2

if out_of_scope_streak >= 3:
    trigger("scope_drift", confidence=min(0.6 + out_of_scope_streak * 0.1, 0.95))
```

**Confidence scoring:**

| Out-of-Scope Streak | Confidence | Action |
|---------------------|------------|--------|
| 3 | 0.70 | Immediate redirect to in-scope |
| 5 | 0.85 | Strong redirect + scope reminder |
| 8+ | 0.95 | Escalate — potential engagement violation |

**Examples:**
- Testing `staging.example.com` when only `www.example.com` is in scope
- Scanning `10.0.0.0/8` when only `192.168.1.0/24` is authorized
- Analyzing a third-party API not owned by the target organization

**Intervention suggestions:**
- "You're outside the engagement scope. Return to the in-scope attack surface."
- "Target [X] is not in the authorized scope. Focus on [in-scope target]."
- "Verify scope before proceeding. The authorized targets are [scope]."

---

## 6. Reward Hacking

**Threshold:** Skipping verification, hardcoding outputs, or gaming the scoring.

**Detection signals:**
- Writing a "found" flag or result file without executing the exploit
- Claiming success without running the verification step
- Modifying test scripts or scoring artifacts to pass
- Hardcoding expected outputs instead of deriving them
- Editing grading or evaluation files
- Claiming a vulnerability exists without demonstrating it

**Detection algorithm:**

```
for each tool_call in history:
    # Check for hardcoded outputs
    if tool_call writes_file and contains_expected_values(tool_call):
        if not preceded_by_execution(tool_call):
            trigger("reward_hacking", confidence=0.90)

    # Check for skipped verification
    if tool_call claims_success and not followed_by_verification(tool_call):
        trigger("reward_hacking", confidence=0.80)

    # Check for output manipulation
    if tool_call modifies_test_results or scoring_artifacts:
        trigger("reward_hacking", confidence=0.95)

    # Check for editing evaluation files
    if tool_call targets_grading_files:
        trigger("reward_hacking", confidence=0.95)
```

**Confidence scoring:**

| Condition | Confidence | Action |
|-----------|------------|--------|
| Hardcoded output detected | 0.90 | Immediate intervention |
| Skipped verification | 0.80 | Enforce verification |
| Modified test/scoring files | 0.95 | Escalate — integrity violation |

**Examples:**
- Writing a file containing the flag value without executing the exploit
- Claiming "SQL injection found" without showing the extracted data
- Modifying the test script to return a passing result
- Editing the scoring rubric to award points for unverified findings

**Intervention suggestions:**
- "Verify your findings before reporting. Demonstrate the exploit works."
- "Don't hardcode outputs — derive them from actual execution."
- "Claims without evidence are not findings. Show the proof."

---

## 7. Overthinking

**Threshold:** Excessive reasoning without action.

**Detection signals:**
- 5+ consecutive analysis paragraphs without an intervening tool call
- Repeatedly restating the problem without progressing
- Enumerating possibilities without testing them
- Long chains of "if-then" reasoning without resolution
- Expressing uncertainty without resolving it through testing

**Detection algorithm:**

```
consecutive_analysis_blocks = 0

for each event in agent_events:
    if event.type == "text" and is_analysis_paragraph(event):
        consecutive_analysis_blocks += 1
    elif event.type == "tool_call":
        consecutive_analysis_blocks = 0

if consecutive_analysis_blocks >= 5:
    trigger("overthinking", confidence=min(0.5 + consecutive_analysis_blocks * 0.08, 0.90))

function is_analysis_paragraph(event):
    text = event.content
    return (
        len(text) > 200 and  # Substantial text block
        count_sentences(text) >= 3 and
        contains_reasoning_patterns(text)  # "if", "then", "could", "might", "perhaps"
    )
```

**Confidence scoring:**

| Analysis Blocks Without Action | Confidence | Action |
|--------------------------------|------------|--------|
| 5 | 0.60 | Encourage action |
| 8 | 0.75 | Strong encouragement + time limit |
| 12+ | 0.90 | Escalate — analysis paralysis |

**Examples:**
- Writing 5+ paragraphs analyzing possible attack vectors without testing any
- Repeatedly listing "we could try X, or maybe Y, or possibly Z" without choosing
- Expressing uncertainty about approach without resolving it through experimentation

**Intervention suggestions:**
- "You have enough information to act. Take the next step now."
- "Set a 5-minute timer and commit to an approach."
- "Done is better than perfect. Try the highest-probability vector now."

---

## 8. Perfectionism Bias

**Threshold:** Optimizing beyond task constraints.

**Detection signals:**
- Refactoring working code when a rough PoC suffices
- Adding error handling to a one-shot exploit
- Optimizing payload size when no size constraint exists
- Adding features beyond the engagement scope
- Polishing output format when content matters more
- Re-running successful commands with minor variations

**Detection algorithm:**

```
for each tool_call in recent_history:
    if is_refinement_of_working_solution(tool_call):
        if not required_by_engagement(tool_call):
            trigger("perfectionism_bias", confidence=0.70)

function is_refinement_of_working_solution(tool_call):
    return (
        tool_call modifies_existing_artifact and
        previous_artifact_was_functional and
        change_is_cosmetic_or_optimization
    )

function required_by_engagement(tool_call):
    return (
        engagement_specifies_quality_requirements or
        refinement_addresses_security_concern or
        refinement_is_necessary_for_reliability
    )
```

**Confidence scoring:**

| Condition | Confidence | Action |
|-----------|------------|--------|
| Cosmetic refinement detected | 0.65 | Encourage "good enough" |
| Optimization beyond requirements | 0.75 | Redirect to next objective |
| Repeated polishing of same artifact | 0.85 | Strong redirect |

**Examples:**
- Refactoring exploit code to be "cleaner" when a rough PoC is sufficient
- Adding comprehensive error handling to a one-shot payload
- Optimizing payload size when there's no size constraint
- Reformatting report output when the content is already adequate

**Intervention suggestions:**
- "Good enough is sufficient. Move to the next objective."
- "You can refine later if needed. Focus on completing the task."
- "Don't let perfect be the enemy of good. Your current approach works."

---

## 9. Confirmation Bias

**Threshold:** Only seeking evidence that confirms the hypothesis.

**Detection signals:**
- Ignoring contradictory scan results or tool outputs
- Only running tests that would confirm the hypothesis
- Dismissing evidence that contradicts the current theory
- Not testing alternative hypotheses
- Interpreting ambiguous results as confirmation
- Seeking supporting evidence while avoiding disconfirming tests

**Detection algorithm:**

```
hypothesis = extract_current_hypothesis(agent_events)

confirming_tests = 0
disconfirming_tests = 0
ignored_contradictions = 0

for each tool_call in recent_history:
    if tests_hypothesis(tool_call, hypothesis):
        if would_confirm(tool_call, hypothesis):
            confirming_tests += 1
        else:
            disconfirming_tests += 1

    if contains_contradictory_evidence(tool_call) and not addressed_by_agent(tool_call):
        ignored_contradictions += 1

if confirming_tests >= 3 and disconfirming_tests == 0:
    trigger("confirmation_bias", confidence=0.70)

if ignored_contradictions >= 2:
    trigger("confirmation_bias", confidence=0.85)
```

**Confidence scoring:**

| Condition | Confidence | Action |
|-----------|------------|--------|
| Only confirming tests run | 0.70 | Suggest disconfirming tests |
| Contradictory evidence ignored | 0.85 | Strong redirect to evidence |
| Both conditions met | 0.90 | Escalate — hypothesis may be wrong |

**Examples:**
- Only running scans that would detect the suspected vulnerability type
- Ignoring a clean scan result that contradicts the hypothesis
- Not testing alternative vulnerability classes
- Interpreting a timeout as "the exploit is working" rather than "the exploit failed"

**Intervention suggestions:**
- "Try to disprove your hypothesis. What evidence would show you're wrong?"
- "You've only run confirming tests. Try a test that could fail."
- "Consider alternative explanations for the results you're seeing."

---

## 10. Tool Fixation

**Threshold:** Using the same tool despite consistent failures.

**Detection signals:**
- Same tool called 5+ times with different parameters, all failing
- Agent not switching tools after repeated failures
- Tool is being used outside its intended purpose
- Agent expresses attachment to a specific tool
- Alternative tools are available but not considered

**Detection algorithm:**

```
tool_usage = defaultdict(list)

for each tool_call in history:
    tool_usage[tool_call.tool_name].append(tool_call)

for tool, calls in tool_usage.items():
    if len(calls) >= 5:
        failure_rate = count_failures(calls) / len(calls)
        if failure_rate >= 0.6:
            # Check if agent has tried alternative tools
            alternative_tools = get_alternatives(tool)
            tried_alternatives = [t for t in alternative_tools if t in tool_usage]

            if not tried_alternatives:
                trigger("tool_fixation", confidence=0.75)
            else:
                trigger("tool_fixation", confidence=0.60)
```

**Confidence scoring:**

| Condition | Confidence | Action |
|-----------|------------|--------|
| 5+ calls, 60%+ failure rate, no alternatives tried | 0.75 | Suggest alternative tool |
| 8+ calls, 70%+ failure rate | 0.85 | Strong suggestion + rationale |
| 10+ calls, 80%+ failure rate | 0.95 | Escalate — tool is not working |

**Examples:**
- Running `nmap` with 8 different flag combinations, all returning no results
- Using `sqlmap` against a non-SQL database repeatedly
- Sticking with `gobuster` when `ffuf` is available and might work better
- Repeatedly using the same exploit framework module that keeps failing

**Intervention suggestions:**
- "You've tried [tool] [N] times without success. Try [alternative_tool] instead."
- "This tool may not be effective for this target. Consider [alternative_category]."
- "Diversify your toolkit. What other tools could achieve the same objective?"

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

## Pattern Interaction Matrix

Patterns frequently co-occur. Understanding interactions improves detection:

| Primary Pattern | Commonly Co-With | Interaction |
|----------------|------------------|-------------|
| Repeated failure | Tool fixation | Same technique failing repeatedly |
| No progress | Rabbit hole | Reading code without producing output |
| Rabbit hole | Confirmation bias | Only reading code that confirms hypothesis |
| Overthinking | No progress | Analyzing without acting |
| Perfectionism | No progress | Polishing instead of progressing |
| Scope drift | Rabbit hole | Exploring out-of-scope code |
| Known-bad approach | Repeated failure | Incompatible technique failing repeatedly |
| Reward hacking | Confirmation bias | Only running tests that "confirm" success |
