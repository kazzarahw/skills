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

## Validation

All skills pass the standard validation:

```bash
python3 skills/learn-skill/scripts/validate_skill.py skills/<skill-name>
```

The only warnings are intentional "emphatic word" warnings (ALWAYS, Do NOT)
that are specifically designed to help smaller models trigger correctly.
