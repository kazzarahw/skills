# Nanobot Configuration

This directory contains configuration files and tools for optimizing
Nanobot's behavior with smaller language models (e.g., OrcaSAQ 2 Cyber 27B).

## Files

| File | Purpose |
|------|---------|
| `SOUL.md` | Customized SOUL.md with skill-first behavioral instructions |
| `trigger_test.py` | Reusable test script for verifying skill description triggers |

## Deployment

### 1. Install SOUL.md

Copy the customized SOUL.md to your Nanobot workspace:

```bash
cp nanobot/SOUL.md ~/.nanobot/workspace/SOUL.md
```

This adds "Skill Usage" instructions that tell the model to:
- Always check available skills before starting work
- Load the full SKILL.md when a skill matches
- Not perform manual work when a skill covers the domain

### 2. Install Skills

Symlink or copy the repo skills into Nanobot's skill directory:

```bash
# Symlink (recommended - keeps repo as source of truth)
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(realpath "$skill")" ~/.nanobot/workspace/skills/"$name"
done

# Or copy (independent from repo)
cp -r skills/* ~/.nanobot/workspace/skills/
```

### 3. Verify Trigger Quality

Run the trigger test to verify skill descriptions match common task phrases:

```bash
python3 nanobot/trigger_test.py
```

## Why These Changes Help Smaller Models

Smaller models (27B parameter class) are less adept at implicit skill recognition
than frontier models. The optimizations include:

1. **Explicit directives** — "ALWAYS use this skill" leaves no ambiguity
2. **Negative triggers** — "Do NOT perform manual X" prevents the common failure
   mode of the model trying to do everything itself
3. **Action-oriented language** — "Load this skill before starting" tells the
   model exactly what to do
4. **SOUL.md behavioral instructions** — creates a system-level expectation
   that skills should be checked first
5. **Mid-Work Checkpoints** — every skill now has a "Mid-Work Checkpoints" section
   that reminds the model to re-read the skill if drifting, check progress against
   phase exit criteria, and maintain output format requirements
6. **Phase transition reminders** — the security-suite orchestrator explicitly
   reminds the model to route to the next skill at phase boundaries
7. **Periodic self-audit** — SOUL.md instructs the model to pause every ~20 tool
   calls and verify it's following the skill's process
8. **Progress checkpoints** — the model writes engagement state to a file,
   creating external memory that survives context window pressure
9. **Goal restatement** — at each phase transition, the model restates the
   engagement goal, combating attention decay and recency bias

## Research Basis

These techniques are based on research into AI agent skill adherence:

- **Periodic Constraint Injection (PCI)** — re-injecting constraints at fixed
  intervals can reduce drift by up to 77% when combined with other techniques
- **Goal reminders** — explicit restatements at fixed turns reduce divergence
  by up to 30%
- **File-based checkpoints** — writing state to markdown files creates
  durable external memory
- **Self-audit** — periodic self-verification catches drift before it compounds

No single technique eliminates drift entirely, but the combination of
explicit descriptions, mid-work checkpoints, periodic self-audit, and
external state files provides defense in depth against the multiple
causes of drift (attention decay, recency bias, compaction loss).

## Validation

All skills pass the standard validation:

```bash
python3 skills/learn-skill/scripts/validate_skill.py skills/<skill-name>
```

The only warnings are intentional "emphatic word" warnings (ALWAYS, Do NOT)
that are specifically designed to help smaller models trigger correctly.
