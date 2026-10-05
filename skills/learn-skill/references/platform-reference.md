# Platform reference

Facts about the skill format and the agents that load it. The open Agent Skills specification is the common ground; each client adds its own locations and extensions. Verified against the spec, the skills CLI's agent table, and the Claude Code and Claude platform docs in September 2026. Clients change quickly, so if something behaves differently, re-check the pages listed in `references/sources.md`.

## Contents
- The spec: fields every agent understands
- Locations
- How agents load skills
- Client extensions, and how to stay portable
- Client notes: Claude Code
- Client notes: Codex
- Client notes: OpenCode
- Client notes: oh-my-pi
- Hosted runtimes and packaged uploads
- Tools for checking skills

## The spec: fields every agent understands

From agentskills.io/specification:

| Field | Required | Constraints |
|---|---|---|
| `name` | yes | 1–64 chars; lowercase `a-z`, `0-9`, `-`; no leading, trailing, or consecutive hyphens; must match the folder name |
| `description` | yes | 1–1,024 chars; what the skill does and when to use it |
| `license` | no | A license name or a reference to a bundled license file |
| `compatibility` | no | Up to 500 chars; environment requirements (intended agents, packages, network) |
| `metadata` | no | A map of string keys to string values, for your own tooling |
| `allowed-tools` | no | Pre-approved tools, space-separated (experimental; support and syntax vary by client) |

- The frontmatter starts on the file's first line with `---`.
- Keep SKILL.md under about 500 lines and 5,000 tokens; put detail in `references/`, `scripts/`, and `assets/`, referenced by relative paths from the skill folder, one level deep.
- A skill that sticks to these fields and plain markdown loads the same way in every compliant agent. Anything else is a client extension: a client that doesn't implement one ignores its fields and shows its syntax as literal text.
- Clients parse leniently but inconsistently. An unquoted `: ` inside the description breaks strict YAML parsers, so quote such values or use a `>-` block scalar.

## Locations

The cross-agent convention is `.agents/skills/<name>/` in a project and `~/.agents/skills/<name>/` for the user; many agents read it, and more are adopting it. Per-agent folders, from the skills CLI's agent table:

| Agent | Project | User |
|---|---|---|
| Codex | `.agents/skills/` | `~/.codex/skills/` |
| Cursor | `.agents/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `.agents/skills/` | `~/.copilot/skills/` |
| Gemini CLI | `.agents/skills/` | `~/.gemini/skills/` |
| OpenCode | `.agents/skills/` | `~/.config/opencode/skills/` |
| Amp | `.agents/skills/` | `~/.config/agents/skills/` |
| Cline, Warp, Zed, and others | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| Goose | `.goose/skills/` | `~/.config/goose/skills/` |
| Kiro CLI | `.kiro/skills/` | `~/.kiro/skills/` |
| Roo Code | `.roo/skills/` | `~/.roo/skills/` |
| Continue | `.continue/skills/` | `~/.continue/skills/` |
| oh-my-pi (not in the CLI table; read from its installed source) | `.omp/skills/` (also `.agent/skills/`, `.agents/skills/`, `.claude/skills/`) | `~/.omp/agent/skills/`, `~/.omp/agent/managed-skills/`, `~/.agent/skills/`, `~/.agents/skills/` |

`npx skills add <source> -a <agent> [-a <agent>...]` installs into the right folder for each agent, symlinked from one canonical copy; `npx skills list` shows what is installed where. When one skill should reach several agents, prefer this over hand-copying, so the copies can't drift apart.

Collisions: agents generally let project skills override user skills with the same name. Two skills with overlapping *descriptions* both stay listed and compete for the same prompts, whatever their names. Some agents ship their own built-in skills (Codex, for example, includes a system skill-creator), which compete too.

## How agents load skills

The same three tiers everywhere:
1. **Catalog**: the name and description of every skill, loaded at session start (roughly 50–100 tokens each). This is all the agent sees when deciding whether to use a skill.
2. **Instructions**: the SKILL.md body, loaded when the agent (or the user) activates the skill, either by reading the file or through a dedicated skill tool.
3. **Resources**: files the body points to, read or run only when needed.

Consequences for authors: all triggering information belongs in the description; the body should put what every run needs first; and a large catalog can crowd out descriptions (Claude Code, for example, drops descriptions of rarely used skills when its listing budget overflows).

## Client extensions, and how to stay portable

Every client layers its own frontmatter fields, substitutions, and invocation rules on top of the spec, and no extension is portable. A skill meant for more than one agent should stay inside the spec and say in plain language what it needs.

| Need | Portable way to express it | Extension syntax some clients provide |
|---|---|---|
| Restrict who may invoke the skill | A line in the body: act only when the user asks by name | `disable-model-invocation`, `user-invocable` (Claude Code) |
| Take arguments from the user | Read the request out of the user's own message | `$ARGUMENTS`, `$1` substitutions (Claude Code) |
| Address the skill's own folder | "Run `scripts/x.py` from this skill's folder" | A skill-folder variable (`${CLAUDE_SKILL_DIR}` in Claude Code) and equivalents elsewhere |
| Pre-approve tools | Name the tool in the body and let the client ask for it | `allowed-tools`, `disallowed-tools` |
| Run something before the instructions | Make it the first step of the body, so the agent runs it under normal permissions | `` !`command` `` injection (Claude Code) |
| Load only for matching files | Check the paths in the body | `paths` globs (Claude Code) |
| Give the job its own context | Ask for a subagent if the client has one | `context: fork` (Claude Code) |

Check each target client's documentation for its own equivalents. Validate a skill meant for several agents with the default target (`validate_skill.py <dir>`, no `--target`); pass `--target <client>` only when that client is one of the targets.

How widely each extension is supported, from the skills CLI's compatibility table (a sample):

| Feature | Supported by |
|---|---|
| Basic skills (the spec) | Every agent listed above |
| `allowed-tools` | Most agents, including Claude Code, Codex, Cursor, OpenCode, Copilot; not Kiro CLI or Zencoder |
| `context: fork` | Claude Code only |
| Hooks | Claude Code, Cline, Kiro CLI |

The next sections are per-client notes, one section per client. Find yours and read it before relying on any extension; nothing in these sections is portable, and coverage tracks how much each client documents, not which client is preferred. Validate with the default target (`--target spec`) unless a named client is one of the targets.

For Gemini, Cursor, Copilot, Cline, Kiro CLI, and Zencoder, use the skills CLI's [Supported Agents](https://github.com/vercel-labs/skills) table for folders and feature support, then check that client's own documentation for extensions.

## Client notes: Claude Code

Claude Code extensions apply only to skills meant for Claude Code. Validate such a skill with `--target claude-code`.

| Field | Effect |
|---|---|
| `when_to_use` | Extra trigger text appended to the description; description plus this is capped at 1,536 chars in the listing |
| `disable-model-invocation: true` | Only the user can invoke it (`/name`); the description is removed from the agent's context |
| `user-invocable: false` | Only the agent can invoke it; hidden from the `/` menu |
| `allowed-tools` | Tools usable without a permission prompt during the invoking turn. Doesn't restrict other tools. Not gated by workspace trust |
| `disallowed-tools` | Tools removed while the skill is active |
| `argument-hint`, `arguments` | Autocomplete hint; named positional arguments for `$name` substitution |
| `model`, `effort` | Model or effort level while the skill is active |
| `context: fork`, `agent`, `background` | Run the body as a task in a separate subagent with no conversation history; the body must contain an explicit task |
| `hooks` | Hooks registered when the skill is invoked, lasting the rest of the session |
| `paths` | Glob patterns: auto-load only while working with matching files |
| `shell` | `bash` (default) or `powershell` for injected commands |

Body features, which a client without these extensions shows as literal text:

| Feature | Behavior |
|---|---|
| `$ARGUMENTS`, `$0`, `$1`, `$name` | Replaced with what the user typed after `/skill-name` |
| `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Skill folder, project root, session ID, effort level |
| `` !`command` `` at line start, or a ```` ```! ```` block | Runs in the shell when the skill loads; the output replaces the line. A non-zero exit aborts the skill (append `\|\| true` if non-zero is normal). Not run for skills synced from claude.ai |

Other Claude Code behavior worth knowing:
- After context compaction, a skill is re-attached with only its first 5,000 tokens, within a shared 25,000-token budget.
- Skills under `~/.claude/skills/synced/` come from the user's claude.ai account and are overwritten by the next sync; the names `synced` and `anthropic-skills` are reserved.
- Name precedence: enterprise over personal over project; plugin skills are namespaced `/plugin:skill`.
- Edits to SKILL.md take effect in the running session; a newly created top-level skills folder needs `/reload-skills`.
- Cloud and Cowork sessions don't read `~/.claude/skills/`; they load skills enabled on the claude.ai account, plus project skills committed to the repo.

## Client notes: Codex

Observed behavior of Codex CLI 0.156 (September 2026), not a documented extension set. Codex publishes no skill-specific frontmatter fields, so a skill written to the spec works as-is.

- Loads project skills from `.agents/skills/`.
- Reads the SKILL.md with a shell command; the read shows up in `codex exec --json` output, which is what `run_eval.py --runner command` matches on to detect a trigger.
- `codex exec -` reads a prompt on stdin, so it fits `--agent-cmd '{query}'` directly.
- Ships a built-in skill-creator, which competes with this skill for the same prompts.
- Supports `allowed-tools`.

For anything beyond this, check Codex's own documentation rather than assuming a Claude Code field exists.

## Client notes: OpenCode

Observed behavior of OpenCode 2.0 (September 2026), likewise not a documented extension set.

- Loads project skills from `.agents/skills/` through a `skill` tool; the call shows up in `opencode run --format json` output, which is what `run_eval.py --runner command` matches on.
- `opencode run` reads a prompt on stdin.
- Supports `allowed-tools`.

## Client notes: oh-my-pi

Observed behavior of oh-my-pi 18.4.9 (`@oh-my-pi/pi-coding-agent`, September 2026), read from the installed package source and `omp --help` rather than from a documented extension set.

- Loads project skills from `.agent/skills/` and `.agents/skills/`, walking up from the working directory to the repo root, and from `~/.agent/skills/` and `~/.agents/skills/` in the user's home. It also reads `.omp/skills/`, and `.claude/skills/*/SKILL.md`, so an existing Claude Code skill loads unchanged.
- User-level oh-my-pi skills live in its own agent directory: `~/.omp/agent/skills/` for skills you wrote or installed, and `~/.omp/agent/managed-skills/` for skills oh-my-pi generated itself. Both load like any other skill; don't edit managed ones in place, they get regenerated.
- Frontmatter is spec-only: `name`, `description`, `alwaysApply`. There are no client-specific extension fields, so a skill written to the spec loads as-is.
- The gotcha: `alwaysApply: true` on a SKILL.md does nothing. It parses into the skill object, but only rules (`RULES.md`) consult it. It is not a "always trigger this" switch.
- Skills are listed, not injected. The system prompt carries a catalog of names and descriptions plus an instruction to read `skill://<name>` first; the body arrives only when the agent reads that skill, so anything every run needs belongs in the description or the top of the body.
- Non-interactive: `omp -p "<prompt>"` processes a prompt and exits, and also takes one piped on stdin. `--mode=json` gives machine-readable output; `--model` picks the model and `--no-session` makes the run ephemeral. That fits the eval scripts as `--agent-cmd "omp -p --mode=json '{query}'"`.

## Hosted runtimes and packaged uploads

Some destinations take a packaged skill rather than a folder on disk:

| Destination | Notes |
|---|---|
| claude.ai and the Claude API | Upload a `.skill` file (`scripts/package_skill.py`). Only the six spec fields are accepted; any other key is a hard error. `name` can't contain "anthropic" or "claude"; no XML tags in either field. Exactly one SKILL.md per skill. Uploads don't sync between claude.ai and the API. Validate with `--target claude-upload` |
| Sandboxed code-execution runtimes | May have no network access and no runtime package installs (the Claude API's code execution has neither); claude.ai's network access depends on admin settings |
| Local agents (CLIs, IDEs) | Same network and filesystem access as any local program; install dependencies into a local environment (a venv, `uv run`, `npx`), not globally |

A skill that needs network access or particular packages should say so in `compatibility` and in its body.

## Tools for checking skills

- `python3 <skill-dir>/scripts/validate_skill.py <dir> [--target spec|claude-code|claude-upload]`: this skill's linter.
- `skills-ref validate <dir>`: the Agent Skills reference validator.
- `npx skills add <path> --list`: confirms the skills CLI can discover the skill.
- Claude Code: `claude plugin validate <skills-dir>` (frontmatter parse check), `/skills`, `/context`, `/skill-doctor`, and `claude plugin eval` for with-and-without evals in CI.
