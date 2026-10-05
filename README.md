# skills

Custom [Agent Skills](https://agentskills.io), written to the open spec so they work in any skills-compatible agent (Codex, Claude Code, Cursor, Copilot, Gemini CLI, OpenCode, and others).

> **Status: mid-refactor.** The previous skill set has been removed and `skills/` is being rebuilt from scratch on the `refactor` branch. Nothing is installed from this repo yet.

## Layout

One directory per skill, under `skills/`:

```
skills/<skill-name>/
├── SKILL.md       # frontmatter (name, description) + instructions
├── references/    # docs loaded on demand
├── scripts/       # executable helpers
├── assets/        # templates and files used in output
└── evals/         # test prompts (not included in packaged skills)
```

`SKILL.md` is the only required file: YAML frontmatter carrying `name` and `description`, then the instructions. Everything else is optional and loaded on demand.

`.claude/skills` and `.opencode/skills` are symlinks to `skills/`, so Claude Code and OpenCode resolve the same copy the repo tracks. Add an equivalent symlink for any other agent.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add kazzarahw/skills@<skill-name> -g -a codex -a claude-code
```

List every agent you use with `-a`; the CLI installs into each agent's skills folder from one shared copy. Drop `-g` to install into the current project only.

Or manually, keeping the clone as the source of truth so `git pull` updates the skill:

```bash
git clone https://github.com/kazzarahw/skills.git ~/dev/skills
ln -s ~/dev/skills/skills/<skill-name> ~/.agents/skills/<skill-name>   # agents that read ~/.agents/skills
ln -s ~/dev/skills/skills/<skill-name> ~/.claude/skills/<skill-name>   # Claude Code
```

Other agents use their own user folders (for example `~/.codex/skills`, `~/.config/opencode/skills`). Replace any existing copy before linking.

## Adding a skill

Create `skills/<skill-name>/` and write its `SKILL.md`: a `name` and `description` in frontmatter, then the instructions. The `description` is what agents match on to decide whether to load the skill, so it should state what the skill does and when to reach for it.

## Licenses

Everything here is Apache-2.0 (see [LICENSE](LICENSE)) unless a skill's own folder says otherwise.