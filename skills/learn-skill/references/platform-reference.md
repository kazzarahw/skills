# Platform reference

Facts about the skill format and the platforms that load it. Verified against the Agent Skills specification and the Claude Code and Claude platform docs in September 2026; platforms change, so if something behaves differently, re-check the pages listed in `references/sources.md`.

## Contents
- Frontmatter: the portable spec
- Frontmatter: Claude Code extensions
- Which fields each destination accepts
- Names
- Locations
- Claude Code body features
- Skill content lifecycle in Claude Code
- Platform runtime constraints
- Tools for checking skills

## Frontmatter: the portable spec

The Agent Skills specification (agentskills.io), accepted by Claude Code, claude.ai, the Claude API, and most other agents:

| Field | Required | Constraints |
|---|---|---|
| `name` | yes | 1–64 chars; lowercase `a-z`, `0-9`, `-`; no leading, trailing, or consecutive hyphens; must match the folder name |
| `description` | yes | 1–1,024 chars; what the skill does and when to use it; no XML tags |
| `license` | no | A license name or a reference to a bundled license file |
| `compatibility` | no | Up to 500 chars; environment requirements (product, packages, network). Most skills don't need it |
| `metadata` | no | A map of string keys to string values, for your own tooling |
| `allowed-tools` | no | Pre-approved tools, space-separated (experimental; support varies) |

The frontmatter must start on the file's first line with `---`.

## Frontmatter: Claude Code extensions

Claude Code accepts everything above plus the fields below. It silently ignores unknown field names, so a typo in a field name fails without an error.

| Field | Effect |
|---|---|
| `when_to_use` | Extra trigger text appended to the description in the listing; counts toward the 1,536-char cap |
| `disable-model-invocation: true` | Only the user can invoke it (`/name`); the description is removed from Claude's context |
| `user-invocable: false` | Only Claude can invoke it; hidden from the `/` menu |
| `allowed-tools` | Tools usable without a permission prompt during the turn that invokes the skill. Doesn't restrict other tools. Not gated by workspace trust |
| `disallowed-tools` | Tools removed while the skill is active |
| `argument-hint` | Autocomplete hint, such as `[issue-number]` |
| `arguments` | Named positional arguments for `$name` substitution |
| `model`, `effort` | Model or effort level while the skill is active |
| `context: fork` | Run the body as a task in a separate subagent that has no conversation history; the body must contain an explicit task |
| `agent` | Subagent type for `context: fork` (`Explore`, `Plan`, `general-purpose`, or a custom agent) |
| `background` | With `context: fork`, `false` waits for the result in the invoking turn |
| `hooks` | Hooks registered when the skill is invoked, lasting the rest of the session |
| `paths` | Glob patterns: auto-load only while working with matching files |
| `shell` | `bash` (default) or `powershell` for injected commands |

## Which fields each destination accepts

| Destination | Allowed fields |
|---|---|
| Claude Code (personal, project, plugin, enterprise skills) | All of the above |
| claude.ai upload, the Skills API, `package_skill.py`, and skills synced to Cowork or cloud sessions | Only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any other key is a hard error on upload |
| Other agents (Codex, Cursor, Copilot, ...) | The spec fields; support for `allowed-tools` varies. `context: fork` and hooks are Claude Code-specific |

For a skill meant for several destinations, keep to the spec fields and validate with `--target portable`.

## Names

- The folder name and `name` should match; the spec requires it.
- For the Claude API and claude.ai: `name` can't contain "anthropic" or "claude", and neither field can contain XML tags.
- Claude Code reserves the folder names `synced` and `anthropic-skills`, which don't load outside a plugin.
- Prefer short, specific names: a gerund or a verb-led phrase (`processing-pdfs`, `gh-address-comments`). Avoid vague names (`helper`, `utils`) and names that collide with installed skills.
- In Claude Code, `name` becomes the `/command`. Plugin skills are namespaced `/plugin:skill`; skills synced from claude.ai answer to `/anthropic-skills:name`, and lose their short name when a local skill has the same one.

## Locations

| Scope | Path | Loads in |
|---|---|---|
| Personal (Claude Code) | `~/.claude/skills/<name>/SKILL.md` | All local projects. Not in Cowork or cloud sessions |
| Project (Claude Code) | `.claude/skills/<name>/SKILL.md` | That repo, including cloud sessions of it. Also found in parent directories up to the repo root; nested `.claude/skills/` load once Claude works in that subdirectory |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled |
| Enterprise | Managed settings directory | All users of the organization |
| claude.ai account | Uploaded or enabled on claude.ai | claude.ai, Cowork, cloud sessions, and signed-in Claude Code sessions |
| Cross-agent convention | `.agents/skills/` (project) or `~/.agents/skills/` (user) | Agents that follow the convention; `npx skills add` manages these |

When names collide in Claude Code: enterprise beats personal beats project; a skill beats a same-named file in `.claude/commands/`; plugin skills are namespaced, so both load. Two skills with overlapping *descriptions* both stay listed and compete for the same prompts, whatever their names.

Claude Code watches skill folders, so edits to SKILL.md take effect in the running session. A newly created top-level skills folder needs `/reload-skills`.

## Claude Code body features

These don't work on claude.ai or through the API; they arrive there as literal text.

| Feature | Behavior |
|---|---|
| `$ARGUMENTS`, `$0`, `$1`, `$name` | Replaced with what the user typed after `/skill-name`. If nothing consumes the arguments, they are appended as `ARGUMENTS: ...` |
| `${CLAUDE_SKILL_DIR}` | The skill's folder. Use it to call bundled scripts from any working directory |
| `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Project root, session ID, current effort level |
| `` !`command` `` at line start, or a ```` ```! ```` block | Runs in the shell when the skill loads; the output replaces the line before Claude sees it. A non-zero exit aborts the whole skill (append `\|\| true` if non-zero is normal). Commands pass through permission rules; pre-approve them with `allowed-tools`. Not run for skills synced from claude.ai |
| `ultrathink` anywhere in the body | Requests deeper reasoning when the skill runs |

The pattern that lets a bundled script run without a permission prompt:

```yaml
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
```
with the body telling Claude to run `${CLAUDE_SKILL_DIR}/scripts/render.sh <file>`.

## Skill content lifecycle in Claude Code

- Only names and descriptions load at startup. The listing budget is about 1% of the context window; when it overflows, descriptions of the least-used skills are dropped first.
- On invocation, the rendered SKILL.md enters the conversation once and stays there; the file isn't re-read on later turns.
- After compaction, the most recent invocation of each skill is re-attached, keeping only its first 5,000 tokens, within a shared 25,000-token budget filled from the most recently used skill. Keep what matters most near the top.
- `allowed-tools` grants last only for the turn that invoked the skill.

## Platform runtime constraints

| Surface | Network | Packages |
|---|---|---|
| Claude API (code execution) | None | Preinstalled only; no runtime installs |
| claude.ai | Full, partial, or none, depending on user and admin settings | Can install from PyPI and npm when network is allowed |
| Claude Code | Same as any local program | Install into a local environment (a venv, `uv run`, `npx`), not globally |

Skills don't sync between surfaces: a skill uploaded to claude.ai must be uploaded separately to the API, and personal Claude Code skills don't reach claude.ai unless uploaded there. A skill that needs network access or particular packages should say so in `compatibility` and in its body.

## Tools for checking skills

- `python3 ${CLAUDE_SKILL_DIR}/scripts/validate_skill.py <dir> --target claude-code|portable`: this skill's linter.
- `claude plugin validate <skills-dir>`: Claude Code's own frontmatter parse check.
- `/skills` lists loaded skills; `/context` shows what the listing costs; `/skill-doctor` reports per-skill cost and usage; `--debug` shows frontmatter parse errors.
- `claude plugin eval`: with-and-without evals for skills shipped in a plugin, suitable for CI.
