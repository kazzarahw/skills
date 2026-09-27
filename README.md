# skills

Custom [Agent Skills](https://agentskills.io) for Claude Code and other skills-compatible agents.

| Skill | What it does |
|---|---|
| [learn-skill](skills/learn-skill/) | Creates, improves, merges, and tests skills: finds existing skills before building, vets third-party skills, cherry-picks rules from them, grounds new skills in research, and benchmarks them against no skill. |

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add kazzarahw/skills@learn-skill -g -a claude-code
```

Drop `-g` to install into the current project only, or change `-a` to target another agent.

Or manually, keeping the clone as the source of truth so `git pull` updates the skill:

```bash
git clone https://github.com/kazzarahw/skills.git ~/dev/skills
ln -s ~/dev/skills/skills/learn-skill ~/.claude/skills/learn-skill
```

For claude.ai or the Claude API, build an uploadable `.skill` file:

```bash
cd skills/learn-skill && python3 -B -m scripts.package_skill "$PWD" "$PWD/../../dist"
```

## Layout

```
skills/<skill-name>/
├── SKILL.md       # frontmatter (name, description) + instructions
├── references/    # docs loaded on demand
├── scripts/       # executable helpers
├── assets/        # templates and files used in output
└── evals/         # test prompts (not included in packaged skills)
```

## Adding a skill

Ask Claude to use `learn-skill` (for example, "turn this workflow into a skill"), or scaffold one directly:

```bash
python3 skills/learn-skill/scripts/init_skill.py <name> --path skills
```

Check it before committing:

```bash
python3 skills/learn-skill/scripts/validate_skill.py skills/<name>             # Claude Code
python3 skills/learn-skill/scripts/validate_skill.py skills/<name> --target portable   # claude.ai, API, other agents
```

`validate_skill.py` needs PyYAML (`pip install pyyaml`, or run it with `uv run`).

## Licenses

Each skill carries its own license. `learn-skill` is Apache-2.0, derived from Anthropic's skill-creator; see its `LICENSE.txt` and `NOTICE`.
