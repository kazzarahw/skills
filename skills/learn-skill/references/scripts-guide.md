# Bundling scripts

Scripts turn fragile or repetitive work into one reliable command. Claude runs them without reading their source, so only their output costs context.

## Contents
- When to write a script
- One-off commands instead of scripts
- Self-contained dependencies
- Designing for an agent caller
- Referencing scripts from SKILL.md
- Before you ship

## When to write a script

- The same logic would otherwise be written from scratch on every run. Eval transcripts show this directly: if several runs each wrote a similar helper, bundle it.
- Correctness matters more than flexibility: validation, format conversion, anything destructive or order-sensitive.
- The work is deterministic and describing it in prose would take longer than the code.

Keep work in prose when it depends on judgment or context.

## One-off commands instead of scripts

When an existing tool already does the job, a pinned one-liner in SKILL.md is enough:

```bash
uvx ruff@0.8.0 check .
npx eslint@9.0.0 --fix .
```

Pin versions so the command behaves the same next month. Once a command grows complex enough that it's hard to get right the first time, move it into a tested script.

## Self-contained dependencies

Declare dependencies inside the script so it runs with one command and no setup step.

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11,<1"]
# ///
```

`uv run scripts/extract.py` reads this block (PEP 723), builds an isolated environment, and runs the script; `pipx run` supports it too. Deno (`npm:` and `jsr:` imports), Bun (versioned imports), and Ruby (`bundler/inline`) have equivalents. Prefer the standard library where it is enough. It removes the install step entirely, which matters on surfaces without network access.

## Designing for an agent caller

An agent reads stdout and stderr to decide its next step. Design for that reader:

- **No interactive prompts.** Agents run in non-interactive shells, and a prompt hangs forever. Take all input through flags, environment variables, or stdin. When a required input is missing, fail with an error that shows the usage.
- **`--help`** that states the purpose, the flags, and an example or two. It is how Claude learns the interface, so keep it short.
- **Errors that say what to do**: what went wrong, what was expected, and the valid options ("--format must be one of: json, csv, table; got 'xml'").
- **Structured output.** JSON or CSV on stdout; progress and warnings on stderr, so the data stays parseable.
- **Bounded output.** Harnesses truncate long tool output (often past 10–30K characters). Default to a summary, and offer `--limit`/`--offset` or `--output FILE` for more.
- **Meaningful exit codes**, documented in `--help`: 0 for success, and distinct codes for distinct failures.
- **Idempotent where possible.** Agents retry. "Create if missing" beats "fail if it exists".
- **Safe defaults.** Offer `--dry-run` for anything stateful, and require an explicit flag (`--force`) for destructive actions.
- **Solve, don't punt.** Handle the expected failures (missing file, permission denied, bad input) inside the script instead of crashing and leaving Claude to diagnose a traceback.
- **No unexplained constants.** `TIMEOUT = 30  # typical request completes in <5s; 30 covers slow links` rather than a bare 47.

## Referencing scripts from SKILL.md

- Say whether Claude should **run** a script ("Run `scripts/fill.py` to fill the form") or **read** it as reference ("See `scripts/fill.py` for the field-mapping algorithm"). Running is the norm.
- Call scripts through their interpreter (`python3 scripts/x.py`, `bash scripts/x.sh`). Some packagers strip executable bits, and a bare `scripts/x.sh` then fails with "Permission denied".
- Paths are relative to the skill folder. In Claude Code, `${CLAUDE_SKILL_DIR}/scripts/x.py` works from any working directory, and the same variable in `allowed-tools` lets the script run without a permission prompt (`references/platform-reference.md`).
- List each script with a one-line purpose and point to `--help` for its flags, rather than documenting every flag in SKILL.md.
- Use forward slashes, even on Windows.
- State what must already be installed ("requires Node.js 18+"), and use the `compatibility` field for runtime requirements.

## Before you ship

- Run every script at least once on realistic input, including a failure path. When there are many similar scripts, test a representative sample.
- Run `--help` and read it as a newcomer would.
- Check that the output is small enough to be useful and parseable.
- If the skill targets the Claude API, confirm the script needs no network and only preinstalled packages.
