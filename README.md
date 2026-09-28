# skills

Custom [Agent Skills](https://agentskills.io), written to the open spec so they work in any skills-compatible agent (Codex, Claude Code, Cursor, Copilot, Gemini CLI, OpenCode, and others).

| Skill | What it does |
|---|---|
| [learn-skill](skills/learn-skill/) | Creates, improves, merges, and tests skills: finds existing skills before building, vets third-party skills, cherry-picks rules from them, grounds new skills in research, and benchmarks them against no skill. |

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add kazzarahw/skills@learn-skill -g -a codex -a claude-code
```

List every agent you use with `-a`; the CLI installs into each agent's skills folder from one shared copy. Drop `-g` to install into the current project only.

Or manually, keeping the clone as the source of truth so `git pull` updates the skill:

```bash
git clone https://github.com/kazzarahw/skills.git ~/dev/skills
ln -s ~/dev/skills/skills/learn-skill ~/.agents/skills/learn-skill   # agents that read ~/.agents/skills
ln -s ~/dev/skills/skills/learn-skill ~/.claude/skills/learn-skill   # Claude Code
```

Other agents use their own user folders (for example `~/.codex/skills`, `~/.config/opencode/skills`); see `skills/learn-skill/references/platform-reference.md`. Replace any existing copy before linking.

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

Ask your agent to use `learn-skill` (for example, "turn this workflow into a skill"), or scaffold one directly:

```bash
python3 skills/learn-skill/scripts/init_skill.py <name> --path skills
```

Check it before committing:

```bash
python3 skills/learn-skill/scripts/validate_skill.py skills/<name>                          # open spec (any agent)
python3 skills/learn-skill/scripts/validate_skill.py skills/<name> --target claude-code      # Claude Code-only skills
python3 skills/learn-skill/scripts/validate_skill.py skills/<name> --target claude-upload    # before uploading to claude.ai or the Claude API
```

`validate_skill.py` needs PyYAML (`pip install pyyaml`, or run it with `uv run`).

## Licenses

Everything here is Apache-2.0 (see [LICENSE](LICENSE)) unless a skill's own folder says otherwise. `learn-skill` is derived from Anthropic's skill-creator and includes material from MIT-licensed projects; see its `LICENSE.txt` and `NOTICE`.
