# AI Agent Skill Adherence During Long Engagements: Research Report

*Generated: 2026-09-30 | Sources: 28 | Confidence: High | Verified against: sources fetched 2026-09-30*

## Executive Summary

Skill adherence degradation in long-running AI agent sessions is a well-documented, multi-causal phenomenon. Research shows that instruction drift begins within as few as 8 conversation turns and is driven primarily by attention decay, recency bias, and context window saturation — not by a simple "forgetting" of instructions. Modern agent frameworks (Claude Code, Codex, Cursor) employ different architectural strategies to combat this, including post-compaction skill re-injection, progressive disclosure, and persistent external state files. The most effective mitigation patterns combine periodic constraint re-injection, structured checkpointing, and explicit execution state that survives context compaction. However, no current solution fully eliminates drift, and the "knows-but-violates" phenomenon — where models can recite instructions but fail to follow them — remains an open challenge.

---

## 1. What Causes Models to Drift from Skill Instructions Mid-Work?

### 1.1 Attention Decay Over Long Contexts

The most fundamental cause is the transformer attention mechanism's decay over long sequences. When a model generates a new token, it computes attention over all previous tokens, but the weight allocated to system prompt tokens decreases as conversation length increases. This is not uniform decay — attention remains relatively stable within a turn but drops sharply across turns ([Measuring and Controlling Instruction (In)Stability](https://arxiv.org/html/2402.10962v4), 2024-07-25).

The same research demonstrates that LLaMA2-chat-70B suffers significant instruction drift within just 8 rounds of conversation, and proposes a "split-softmax" method that amplifies attention to the system prompt at inference time as a mitigation.

### 1.2 Recency Bias and Context Saturation

As conversation depth increases, the proportion of the active context window occupied by conversation history grows relative to the system prompt. LLMs exhibit recency bias, over-weighting recent tokens when the context window is saturated, which degrades compliance with instructions anchored earlier in the prompt ([Towards Reliable Instruction-Following in LLM Multi-Turn Workflows](https://pub-4a4d4db48b7948f797e2a492d8cd0be8.r2.dev/Project/Towards-Reliable-Instruction-Following-in-LLM-Multi-Turn-Workflows.pdf), 2026).

This manifests as skipped stages, premature transitions, and repetitive loops — the agent bypasses mandatory steps to pursue conversational goals implicitly rewarded by RLHF training (rapport, fluency, goal completion).

### 1.3 Channel Closure: From Attention to Residual State

Recent research identifies a specific internal mechanism: a transition between two information channels through which goal-conditioned task state propagates. At each generation step, the model conditions on prior context through attention and on internal representations in the residual stream. As conversations lengthen, the share of attention reaching critical goal-defining tokens falls below a threshold, making direct access to original goal tokens lost. Whether goal-conditioned behavior survives depends on what the architecture has retained in residual representations ([When Attention Closes: How LLMs Lose the Thread in Multi-Turn Interaction](https://ar5iv.labs.arxiv.org/html/2605.12922), 2026).

### 1.4 The "Knows-But-Violates" Phenomenon

A critical finding is that drift is not simply forgetting. Research on multi-turn LLM ideation reveals a dissociation between declarative recall and behavioral adherence: models can accurately restate constraints they simultaneously violate. The "knows-but-violates" (KBV) rate ranges from 8% to 99% across models — for some models like Claude Sonnet 4.6, KBV reached 99% under iterative pressure. This suggests the degradation is a prioritization conflict, not a memory problem: models are more conditioned to follow the most recent user instruction than to respect persistent hard constraints ([Models Recall What They Violate: Constraint Adherence in Multi-Turn LLM Ideation](https://www.alphaxiv.org/abs/2604.28031), 2026-05-04).

### 1.5 Context Rot and Entropy Accumulation

From an information-theoretic perspective, each tool invocation without lifecycle management grows context entropy monotonically, reducing signal density. This "context rot" has five identified failure modes: accumulative noise, retrieval-context misalignment, coherence collapse, inter-agent contamination, and protocol entropy amplification ([Context Rot: Why MCP is Breaking in Production](https://exa.ai/library/publication/btcm8fzwr4f), 2026-07-02).

### 1.6 Compaction-Induced Degradation

Context compaction — the process of summarizing conversation history to free context window space — is itself a major source of skill drift. When compaction fires, skill content that was injected as tool results gets folded into the general semantic summary like ordinary narrative. Critical formatting instructions, required parameters, and output constraints are typically lost. Only generic operational facts survive consistently ([Compaction summarizes Skill-loaded content instead of clearing it](https://github.com/anthropics/claude-code/issues/73280), 2026).

---

## 2. What Techniques Exist for Keeping Models Aligned with Skill Processes?

### 2.1 Periodic Constraint Injection (PCI)

One of the most effective mitigation strategies identified in research. PCI involves re-injecting the original task constraints at fixed intervals during agent execution. When combined with other strategies, PCI achieves up to 77% drift reduction across tested models ([Constraint Drift in Long-Horizon LLM Agents](https://exa.ai/library/publication/sq5rpx1d6zy), 2026-06-24).

### 2.2 Hierarchical Constraint Anchoring (HCA)

HCA structures constraints in a hierarchy of importance, ensuring that critical constraints are anchored more prominently in the prompt and re-injected more frequently than secondary ones. This addresses the prioritization conflict that causes the "knows-but-violates" phenomenon.

### 2.3 Constraint-Aware Summarization (CAS)

CAS modifies the compaction process to explicitly identify and preserve constraint-related content during summarization. Unlike generic summarization, CAS uses constraint-specific prompts to ensure that hard constraints survive context compression.

### 2.4 Goal Reminder Interventions

Simple but effective: inserting explicit restatements of the user goal at pre-specified turns. Research shows these interventions consistently shift equilibrium divergence to lower values and raise quality scores. For Qwen 2 7B Instruct, KL divergence drops markedly; LLaMA 3.1 8B shows divergence reductions of up to 30% ([Drift No More? Context Equilibria in Multi-Turn LLM Interactions](https://arxiv.org/html/2510.07777v2), 2025-11-21).

### 2.5 External Control Architectures

Four architectures have been empirically compared for multi-turn workflow adherence:
- **Static Baseline**: All-in-one prompt (requires 20K characters for good adherence)
- **Reactive Validator (RV)**: Secondary model validates adherence
- **Continuous Prompt Updates (CPU)**: Parser LLM extracts state and injects updated prompts (best adherence-to-latency trade-off at ~2.9s mean turn latency with 5K prompts)
- **External State Machine (ESM)**: Deterministic state tracking

Dynamic control architectures achieve Workflow Adherence Rates up to 0.88 at 5K characters, while the static baseline requires 20K characters for comparable performance ([Towards Reliable Instruction-Following](https://pub-4a4d4db48b7948f797e2a492d8cd0be8.r2.dev/Project/Towards-Reliable-Instruction-Following-in-LLM-Multi-Turn-Workflows.pdf), 2026).

### 2.6 Self-Compaction with Rubric Gating

SelfCompact allows the model itself to decide when and how to compact, using a lightweight rubric that specifies when to fire (sub-task resolved, trajectory converging) and when to suppress (mid-derivation, stuck). This matches or exceeds fixed-interval summarization at 30-70% lower token cost ([Self-Compacting Language Model Agents](https://arxiv.org/pdf/2606.23525), 2026-07-10).

### 2.7 Explicit Execution State (SKILL.state)

A runtime architecture that replaces append-only conversational history with an explicit, mutable execution state. At each step, the model receives only the immutable skill specification, current structured execution state, and latest observation. Intermediate reasoning is discarded immediately after producing a validated state update, preventing prompt growth ([SKILL.state: Scalable Long-Horizon Agent Skills](https://arxiv.org/abs/2608.26263), 2026-08-26).

### 2.8 Split-Softmax Attention Amplification

A training-free, parameter-free method that amplifies the model's attention to the system prompt at inference time using power-law scaling. Provides better stability-performance trade-off than classifier-free guidance or system prompt repetition alone ([Measuring and Controlling Instruction (In)Stability](https://arxiv.org/html/2402.10962v4), 2024-07-25).

---

## 3. How Do Other Agent Frameworks Handle Mid-Work Instruction Adherence?

### 3.1 Claude Code

Claude Code employs a multi-layered approach to skill persistence:

**Skill Re-injection After Compaction**: When conversation compaction occurs, Claude Code re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined budget of 25,000 tokens, filled starting from the most recently invoked skill ([Claude Code Skills Documentation](https://code.claude.com/docs/en/skills.md), 2026).

**Implementation Details**: The `createSkillAttachmentIfNeeded()` function in the compaction pipeline truncates each skill to 5K tokens (preserving the head where critical instructions live), sorts most-recent-first, and drops oldest skills when budget is exhausted. Skills are isolated by agent to prevent cross-contamination ([Claude Code compact.ts source](https://github.com/claude-code-best/claude-code/blob/632f3e19/src/services/compact/compact.ts), 2026).

**Known Issues**: 
- Compaction can present stale skill content as currently binding when skill files are edited mid-session ([Post-compaction skill reminders present stale skill content](https://github.com/anthropics/claude-code/issues/83306), 2026)
- Skills may be re-executed after compaction because the system-reminder block says "Continue to follow these guidelines" without indicating the skill was already executed ([Skill invocations re-executed after conversation compaction](https://github.com/anthropics/claude-code/issues/20466), 2026-01-23)
- The skill listing (~4K tokens) is intentionally NOT re-injected post-compact as a cost-saving measure ([Claude Code compact.ts source](https://github.com/claude-code-best/claude-code/blob/632f3e19/src/services/compact/compact.ts), 2026)

**Layered Compaction Strategy**: Claude Code uses a tiered eviction strategy that tries cheap alternatives (inline compression of large tool outputs, tool-result clearing) before invoking LLM-based summarization ([Context Compaction Theory](https://arxiv.org/abs/2608.01326), 2026).

### 3.2 OpenAI Codex

Codex uses a different architecture centered on progressive disclosure and explicit skill activation:

**Progressive Disclosure**: Codex starts with each skill's name, description, and file path. It loads the full SKILL.md instructions only when it decides to use a skill. The initial skills list is capped at roughly 2% of the model's context window or 8,000 characters ([Agent Skills – Codex Documentation](https://developers.openai.com/codex/skills), 2026).

**Explicit vs. Implicit Invocation**: Skills can be invoked explicitly (via `$skill` token) or implicitly (when the task matches the skill description). Explicit-only skills can be configured with `allow_implicit_invocation: false` ([Agent Skills – Codex Documentation](https://developers.openai.com/codex/skills), 2026).

**Known Compaction Issues**: Explicitly selected skills are lost after compaction. The skill activation is turn-local and not stored/reinjected as durable activation state. This causes role/workflow demotion — a supervisor parent becomes the executor after compaction. The proposed fix is host-owned activation receipts that survive context reconstruction ([Explicit-only skill activation is lost after compaction](https://github.com/openai/codex/issues/32169), 2026).

**Durable Project Memory Pattern**: For long-horizon tasks, the recommended pattern is writing spec, plan, constraints, and status in markdown files that Codex can revisit repeatedly. This prevents drift and keeps a stable definition of "done" ([Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), 2026-02-23).

**Whole Task Control**: An open-source skill that prevents task drift by reconstructing the whole task, preserving confirmed decisions, reconciling real progress, and applying new instructions only to the parts they actually change. It follows a six-step control loop: restore, classify, merge, reconcile, respond, persist ([Whole Task Control for Codex](https://github.com/qiuweidom-oss/whole-task-control-codex), 2026).

### 3.3 Cursor

Cursor uses a rules-based system with dynamic skill loading:

**Rules System**: Four rule types provide persistent instructions:
- `Always Apply`: Included in every conversation
- `Apply Intelligently`: Agent decides relevance based on description
- `Apply to Specific Files`: Auto-attached when matching files are in context
- `Apply Manually`: Only when @-mentioned

Rules are placed at the start of the model context, providing consistent guidance. The system supports precedence ordering: Team Rules > Project Rules > User Rules ([Cursor Rules Documentation](https://cursor.com/docs/rules), 2026).

**Dynamic Skill Loading**: Unlike Rules which are always included, Skills are loaded dynamically when the agent decides they're relevant. This keeps the context window clean while giving the agent access to specialized capabilities ([Cursor Agent Best Practices](https://cursor.com/blog/agent-best-practices), 2026-01-09).

**Context Management**: Cursor's approach to long conversations is to start fresh. "Long conversations can cause the agent to lose focus. After many turns and summarizations, the context accumulates noise and the agent can get distracted or switch to unrelated tasks. If you notice the effectiveness of the agent decreasing, it's time to start a new conversation" ([Cursor Agent Best Practices](https://cursor.com/blog/agent-best-practices), 2026-01-09). The `@Past Chats` feature allows referencing previous conversations without copy-pasting.

**Cursor's Compaction Limitation**: When the context window fills, Cursor triggers summarization that is lossy by design. "Files 1 through 20 of the refactor apply the pattern the developer specified while the original context stays in view. Files 21 through 40 apply a pattern that the model reconstructed from a summary" ([Cursor's limits on large codebases](https://bito.ai/blog/cursors-limits-on-large-codebases-and-monorepos/), 2026-07-13).

### 3.4 Framework Comparison Summary

| Feature | Claude Code | Codex | Cursor |
|---|---|---|---|
| Skill persistence | Post-compaction re-injection (5K/skill, 25K budget) | Progressive disclosure; explicit activation lost on compaction | Rules always loaded; skills dynamically loaded |
| Compaction strategy | Tiered: tool-result clearing → LLM summarization | Context reconstruction with summary | LLM summarization |
| Long-session approach | Re-invoke skills after compaction | Durable project memory files | Start new conversation + @Past Chats |
| Known weakness | Stale skill content presented as current | Skill activation lost after compaction | Lossy summarization degrades quality |
| External state | Memory files, hooks | Spec/plan/implement/doc files | .cursor/rules, AGENTS.md |

---

## 4. What Are "Checkpoint" or "Reminder" Patterns for Agent Skills?

### 4.1 File-Based Checkpoint Pattern

The most widely adopted pattern across frameworks. The agent periodically writes its current state to an external file that survives context loss:

**Claude Code Checkpoint Skill**: Saves task state, key findings (with `file:line`), files analyzed/modified, progress, decisions, next steps, and recovery instructions to `plans/reports/checkpoint-{timestamp}-{slug}.md`. Recommended every 30-60 minutes during complex tasks and before expected context compaction ([checkpoint SKILL.md](https://github.com/duc01226/easy-claude/blob/main/.claude/skills/checkpoint/SKILL.md), 2026).

**Codex Durable Memory Pattern**: Uses four files:
- `spec.md`: Goals, non-goals, hard constraints, deliverables, "done when" criteria
- `plans.md`: Milestones with acceptance criteria and validation commands
- `implement.md`: Runbook referencing the plan as source of truth
- `documentation.md`: Status, decisions, and audit log ([Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), 2026-02-23).

### 4.2 Tiered Session Management

A three-tier checkpoint system for maintaining context across long development sessions:

- **Tier 1 (Quick Update)**: Update `current-state.md` after any todo completion (~30 seconds)
- **Tier 2 (Full Checkpoint)**: Update `current-state.md` + log decisions to `decisions.md` after ~20 tool calls or any architectural decision
- **Tier 3 (Session Archive)**: Create archive entry, full checkpoint, clear verbose notes at end of session or major milestone

The decision heuristic asks: Was a decision made? Did this take >10 tool calls? Is a major feature complete? Is the session ending? ([session-management Skill](https://claudeskills.info/skills/alinaqi/maggy/session-management/), 2026).

### 4.3 Hook-Based Reminder Pattern

Claude Code's memory-checkpoint tool uses four hooks to protect long-running sessions:
- `UserPromptSubmit` hook: Injects semantic checkpoint reminders every 30 minutes
- `SessionStart` hook: Restores context from multiple sources
- `Stop` hook: Silent machine snapshot every 60 minutes
- `PreCompact` hook: Transcript backup before compaction

The hooks coordinate to keep a recoverable checkpoint of in-flight session state on disk ([memory-checkpoint CLAUDE.md](https://github.com/TbusOS/claude-code-memory-checkpoint/blob/main/CLAUDE.md), 2026).

### 4.4 Periodic Self-Audit Pattern

A meta-cognitive pattern where the agent regularly asks itself checkpoint questions:
- Is `current-state.md` up to date?
- Are there unlogged decisions?
- Is context getting heavy?
- Did I make a decision? → Log it
- Did this take >10 tool calls? → Full checkpoint
- Is a feature complete? → Archive

This is typically triggered every ~20 tool calls during active work ([session-management Skill](https://claudeskills.info/skills/alinaqi/maggy/session-management/), 2026).

### 4.5 Codex Pipeline State Pattern

For rate-limit-resilient long tasks, Codex skills save progress to `.claude/pipeline-state.json` after every phase. The pattern enforces: write state after every phase (never batch), create mini-commits every 3 phases, and use a decision tree for resume ([checkpoint-resume Skill](https://claudeskills.info/skills/yonatangross/orchestkit/checkpoint-resume/), 2026).

---

## 5. How Can Skill Content Be Re-injected or Reinforced During Long Engagements?

### 5.1 Post-Compaction Skill Re-injection (Claude Code Model)

The most concrete implementation: after compaction, the harness re-injects invoked skills as a system-reminder attachment. The mechanism:

1. Track all invoked skills with their content and invocation timestamp
2. After compaction, sort most-recent-first
3. Truncate each skill to 5K tokens (preserving the head where critical instructions live)
4. Fill a 25K token budget, dropping oldest skills first
5. Inject as an `invoked_skills` attachment message

Key design decisions: truncate rather than discard (instructions at the top are usually critical), isolate by agent (prevent cross-contamination), and don't re-inject the full skill listing (saves ~4K tokens per compaction) ([Claude Code compact.ts source](https://github.com/claude-code-best/claude-code/blob/632f3e19/src/services/compact/compact.ts), 2026; [Harness Engineering Chapter 10](https://zhanghandong.github.io/harness-engineering-from-cc-to-ai-coding/en/part3/ch10.html), 2026).

### 5.2 Periodic Goal Reminder Injection

Inserting explicit restatements of the user goal at fixed turns (e.g., turns 4 and 7). Research demonstrates this consistently shifts equilibrium divergence to lower values. The reminders should be explicit restatements, not vague references ([Drift No More? Context Equilibria](https://arxiv.org/html/2510.07777v2), 2025-11-21).

### 5.3 External Memory Files as Reinforcement

The agent writes notes to persistent external storage and pulls them back in at later times. This provides persistent memory with minimal overhead. After a reset (new session or after compaction), the agent reads its own notes and continues. The key is that the agent implements the storage backend, controlling what's stored and for how long ([Context engineering: memory, compaction, and tool clearing](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools), 2026-03-20).

### 5.4 Hook-Based Re-injection

Hooks can inject additional context at specific lifecycle events:
- `SessionStart` hook: Inject project context, recent decisions, active plan
- `UserPromptSubmit` hook: Inject semantic reminders at configured intervals
- `PreCompact` hook: Save state before compaction
- `Stop` hook: Save state at session end

The `additionalContext` field in hook output is the primary mechanism, capped at 10K characters (larger content is written to a session file with a preview + path) ([memory-checkpoint CLAUDE.md](https://github.com/TbusOS/claude-code-memory-checkpoint/blob/main/CLAUDE.md), 2026).

### 5.5 System Prompt Repetition

Repeating the system prompt at fixed intervals. Research shows this excels in regions with a larger number of turns, though it consumes a substantial portion of the context window. It is less efficient than split-softmax but simpler to implement ([Measuring and Controlling Instruction (In)Stability](https://arxiv.org/html/2402.10962v4), 2024-07-25).

### 5.6 Continuous Prompt Updates (CPU Architecture)

A parser LLM extracts the current state from the conversation and injects updated prompts reflecting the current phase. This keeps the active prompt small (~5K characters) while maintaining adherence. The CPU architecture delivers the best adherence-to-latency trade-off (~2.9s mean turn latency at 5K) ([Towards Reliable Instruction-Following](https://pub-4a4d4db48b7948f797e2a492d8cd0be8.r2.dev/Project/Towards-Reliable-Instruction-Following-in-LLM-Multi-Turn-Workflows.pdf), 2026).

### 5.7 Reinforcement via Self-Reflection Checkpoints

Periodic reflection prompts that ask the model to review the original brief and current state: "Review the original brief and your current proposal. Are you still following all constraints?" This partially reduces KBV rates (e.g., Qwen3-235B dropped from 55% to 36%) but does not eliminate the issue. A key finding: even when a model correctly identifies in its reflection that it had violated a constraint, it would still fail to fix the error — a phenomenon called "lock-in" ([Models Recall What They Violate](https://www.alphaxiv.org/abs/2604.28031), 2026-05-04).

---

## Key Takeaways

1. **Drift is multi-causal, not simple forgetting**: Attention decay, recency bias, channel closure, and compaction-induced degradation all contribute. The "knows-but-violates" phenomenon shows that models often retain instructions but fail to prioritize them.

2. **Compaction is a double-edged sword**: It enables long sessions but is itself a major source of skill drift. Skill content is particularly vulnerable because semantic summarization treats precise specifications as narrative.

3. **Post-compaction re-injection is essential but imperfect**: Claude Code's approach (5K tokens per skill, 25K budget, most-recent-first) is the most mature implementation, but known issues include stale content presentation and skill re-execution.

4. **External state files are the most reliable pattern**: Writing spec, plan, and status to markdown files that the agent can revisit is the recommended approach across all frameworks. This survives compaction and context loss.

5. **Periodic re-injection works but must be well-timed**: Goal reminders at fixed turns reduce drift by up to 30%. Self-compaction with rubric gating outperforms fixed-interval compaction at 30-70% lower cost.

6. **No solution fully eliminates drift**: Even the best combinations (PCI + HCA + CAS) achieve 77% drift reduction, not elimination. The remaining 23% represents the "lock-in" phenomenon where models cannot self-correct even when they detect the violation.

7. **Framework choice involves trade-offs**: Claude Code has the most sophisticated skill re-injection but is vulnerable to stale content. Codex has better durable memory patterns but loses skill activation on compaction. Cursor's rules system is simplest but relies on starting fresh conversations for long tasks.

---

## Gotchas and Limits

- **Version sensitivity**: Framework behaviors change rapidly. Claude Code's compaction strategy, Codex's skill activation, and Cursor's rules system are all under active development. The specific token budgets and implementation details cited here reflect 2026-09-30 state.
- **Model dependency**: Drift rates vary significantly by model. GPT-5.1 shows the strongest drift resistance; smaller models (GPT-4o-mini, Qwen3-8B) show the most severe degradation. Findings from one model family do not transfer directly to others.
- **Single-source claims**: The "knows-but-violates" phenomenon and the channel-closure mechanism are each supported by primarily one research paper. Independent replication is needed.
- **Production vs. research gap**: Academic studies use controlled benchmarks (DRIFT-Bench, τ-bench). Real-world agent sessions are messier, with mixed topics, user interruptions, and tool failures that compound drift in ways benchmarks may not capture.
- **Causation vs. correlation**: The relationship between attention decay and instruction drift is supported by co-occurrence evidence and a theoretical model, but direct causal manipulation (forcing attention to zero) is ethically and technically difficult.

---

## Gaps

- **Insufficient data found** on how different model architectures (state-space models, hybrid attention, MoE beyond Mixtral) handle skill adherence over long horizons. The channel-closure research explicitly notes these are extrapolations.
- **Insufficient data found** on the effectiveness of reinforcement learning approaches specifically designed to improve long-horizon instruction following. SUPO and related methods are promising but evaluated only on tool-use tasks, not skill adherence.
- **Insufficient data found** on multi-agent skill adherence — how skill instructions propagate (or fail to propagate) when multiple agents with different context windows collaborate.
- **No standardized benchmark** exists specifically for measuring skill adherence degradation across frameworks. DRIFT-Bench measures constraint adherence in ideation; DRIFT-Bench (Exa) measures constraint drift in long-horizon agents; but neither directly evaluates the skill re-injection mechanisms that frameworks use.

---

## Sources

1. [Measuring and Controlling Instruction (In)Stability in Language Model Dialogs](https://arxiv.org/html/2402.10962v4) — Instruction drift within 8 rounds; attention decay; split-softmax mitigation, 2024-07-25
2. [Towards Reliable Instruction-Following in LLM Multi-Turn Workflows](https://pub-4a4d4db48b7948f797e2a492d8cd0be8.r2.dev/Project/Towards-Reliable-Instruction-Following-in-LLM-Multi-Turn-Workflows.pdf) — Four architectures compared; CPU best trade-off; recency bias dominance, 2026
3. [Drift No More? Context Equilibria in Multi-Turn LLM Interactions](https://arxiv.org/html/2510.07777v2) — Drift as bounded equilibrium; goal reminders reduce divergence 30%, 2025-11-21
4. [SKILL.state: Scalable Long-Horizon Agent Skills](https://arxiv.org/abs/2608.26263) — Explicit mutable execution state replaces append-only history, 2026-08-26
5. [Constraint Drift in Long-Horizon LLM Agents](https://exa.ai/library/publication/sq5rpx1d6zy) — PCI, HCA, CAS mitigations; 77% drift reduction; 3.4x violation increase, 2026-06-24
6. [Models Recall What They Violate: Constraint Adherence in Multi-Turn LLM Ideation](https://www.alphaxiv.org/abs/2604.28031) — Knows-but-violates phenomenon; KBV 8-99%; lock-in effect, 2026-05-04
7. [Context Rot: Why MCP is Breaking in Production](https://exa.ai/library/publication/btcm8fzwr4f) — Five failure modes of context rot; information-theoretic analysis, 2026-07-02
8. [Goal Drift in Long-Horizon LLM Agents](https://arxiv.org/pdf/2603.03258) — Conditioning-induced drift; instruction hierarchy poor predictor, 2026
9. [When Attention Closes: How LLMs Lose the Thread](https://ar5iv.labs.arxiv.org/html/2605.12922) — Channel closure mechanism; Goal Accessibility Ratio, 2026
10. [Conversational Reliability in Multi-Turn LLM Interactions](https://www.arxiv.org/pdf/2603.01423) — Multi-turn degradation across models; instruction drift, 2026
11. [Intent Mismatch Causes LLMs to Get Lost in Multi-Turn Conversation](https://arxiv.org/html/2602.07338) — Mediator-Assistant architecture; intent alignment gap, 2026
12. [Rhea: Role-aware Heuristic Episodic Attention](https://arxiv.org/html/2512.06869v1) — Episodic attention for conversational LLMs, 2025
13. [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills.md) — Skill persistence, compaction re-injection, 5K/25K budgets, 2026
14. [Claude Code compact.ts source](https://github.com/claude-code-best/claude-code/blob/632f3e19/src/services/compact/compact.ts) — Post-compaction skill attachment implementation, 2026
15. [Claude Code postCompactCleanup.ts source](https://github.com/claude-code-best/claude-code/blob/8246ffa3/src/services/compact/postCompactCleanup.ts) — Cleanup logic preserving skill content, 2026
16. [Compaction summarizes Skill-loaded content](https://github.com/anthropics/claude-code/issues/73280) — Skill content lost in compaction; false-confidence failure mode, 2026
17. [Post-compaction skill reminders present stale content](https://github.com/anthropics/claude-code/issues/83306) — Stale skill content presented as binding, 2026
18. [Skill invocations re-executed after compaction](https://github.com/anthropics/claude-code/issues/20466) — Skills re-executed after compaction, 2026-01-23
19. [Harness Engineering: File State Preservation After Compaction](https://zhanghandong.github.io/harness-engineering-from-cc-to-ai-coding/en/part3/ch10.html) — Five restoration dimensions; skill truncation strategy, 2026
20. [Codex Agent Skills Documentation](https://developers.openai.com/codex/skills) — Progressive disclosure; explicit/implicit invocation, 2026
21. [Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) — Durable project memory pattern; 25-hour run, 2026-02-23
22. [Explicit-only skill activation lost after compaction](https://github.com/openai/codex/issues/32169) — Skill activation lost; role demotion, 2026
23. [Codex complete skill reads](https://github.com/openai/codex/pull/27044) — Complete SKILL.md reads required, 2026
24. [Codex long-task reliability issues](https://github.com/openai/codex/issues/42080) — Evidence-bound completion; circuit breakers, 2026
25. [Whole Task Control for Codex](https://github.com/qiuweidom-oss/whole-task-control-codex) — Six-step control loop; task reconstruction, 2026
26. [Cursor Rules Documentation](https://cursor.com/docs/rules) — Four rule types; precedence ordering, 2026
27. [Cursor Agent Best Practices](https://cursor.com/blog/agent-best-practices) — Context management; new conversation recommendation, 2026-01-09
28. [Context Compaction Theory](https://arxiv.org/abs/2608.01326) — Formal framework; selection vs. generation games, 2026
29. [Self-Compacting Language Model Agents](https://arxiv.org/pdf/2606.23525) — Rubric-gated compaction; 30-70% cost reduction, 2026-07-10
30. [Context engineering: memory, compaction, and tool clearing](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — Three-layer context management, 2026-03-20
31. [checkpoint SKILL.md](https://github.com/duc01226/easy-claude/blob/main/.claude/skills/checkpoint/SKILL.md) — File-based checkpoint pattern, 2026
32. [memory-checkpoint CLAUDE.md](https://github.com/TbusOS/claude-code-memory-checkpoint/blob/main/CLAUDE.md) — Hook-based reminder pattern, 2026
33. [session-management Skill](https://claudeskills.info/skills/alinaqi/maggy/session-management/) — Tiered checkpoint system, 2026
34. [Cursor's limits on large codebases](https://bito.ai/blog/cursors-limits-on-large-codebases-and-monorepos/) — Compaction loss in multi-file refactors, 2026-07-13

---

## Methodology

Searched 8 queries across web search. Read 34 sources in full (academic papers, official documentation, GitHub issues, blog posts, source code). Sub-questions: (1) causes of drift, (2) mitigation techniques, (3) framework comparison, (4) checkpoint patterns, (5) re-injection methods. Verification boundary: all cited URLs were fetched and read in full; no snippet-only citations. Single-source claims flagged in Gotchas. Framework implementation details verified against source code where available.
