# Designing a skill

Settle the design before writing prose; a well-worded skill with the wrong scope or invocation mode still fails.

## Contents
- Is a skill the right tool?
- Scope
- Skill types
- Invocation
- Degrees of freedom
- Information hierarchy
- Architecture patterns
- Spec template

## Is a skill the right tool?

| The need | Better home |
|---|---|
| A fact or preference that applies to almost every task | `CLAUDE.md` / `AGENTS.md` (always loaded) |
| Something that must happen every time, deterministically (format on save, block a command) | A hook; instructions can be ignored, hooks can't |
| A check that a regex or validator can enforce | A script or linter, run from a hook, CI, or a skill |
| Access to an external system with auth and state | An MCP server, optionally with a skill that teaches how to use it well |
| A long task that needs its own context window | A subagent, or a skill with `context: fork` (Claude Code) |
| A procedure or body of knowledge needed only for some tasks | **A skill** |
| Something done once | Nothing; just do it |

Signs a skill is warranted: the user keeps pasting the same instructions or checklist; a CLAUDE.md section has grown into a procedure rather than a fact; the baseline run fails in ways a written procedure would fix.

## Scope

A skill should cover one coherent unit of work, the way a good function does one thing.

- **Too narrow** and several skills must load for one task, adding overhead and conflicting instructions.
- **Too broad** and the description turns vague, so the skill triggers imprecisely, and the body fills with material irrelevant to any given run.
- Split when two parts have distinct trigger vocabulary, or when another skill needs to reach one part on its own.
- Keep things together when they share most steps, or when splitting would force both skills to load together anyway.
- Favor focus. In SkillsBench, focused skills with two or three modules outperformed exhaustive documentation bundles; comprehensive coverage is not the goal.

## Skill types

| Type | Example | Needs most | How to test |
|---|---|---|---|
| Technique | Filling PDF forms, debugging flaky tests | A clear procedure, a working example, gotchas | Apply it to new cases and variations |
| Reference | API conventions, schemas, a style guide | Findable structure, grep patterns, a table of contents | Can Claude retrieve and correctly apply facts? |
| Discipline | TDD, verify-before-claiming-done | Bright-line rules, a rationalization table, red flags | Pressure scenarios that tempt a violation |
| Task / workflow | Deploy, release, commit | Exact steps, validation gates; usually user-invoked | Run it end to end in a safe environment |
| Generator | Reports, decks, boilerplate | Templates in `assets/`, format rules | Output checks: structure, content, rendering |
| Integration | Wrapping a CLI or MCP server | Exact commands, auth, error handling, a script | Real calls, including the failure paths |

## Invocation

| Mode | Frontmatter (Claude Code) | Use for | Cost |
|---|---|---|---|
| Model-invoked (default) | none | Anything Claude should reach for by itself | The description sits in context every turn |
| User-invoked only | `disable-model-invocation: true` | Side effects or timing the user must control: deploy, send, publish, delete | The user has to remember the skill exists |
| Model-invoked only | `user-invocable: false` | Background knowledge that isn't a meaningful command | Hidden from the `/` menu |

For a user-invoked skill, the description becomes a one-line summary for humans; trigger lists add nothing because Claude never sees them. These fields are Claude Code extensions (`references/platform-reference.md`).

## Degrees of freedom

Match specificity to how fragile the operation is, part by part:

- **High freedom** (prose guidance) when many approaches work and context decides. Explain the goal and what good looks like.
- **Medium freedom** (a preferred pattern, pseudocode, a parameterized script) when one approach is preferred but variation is fine.
- **Low freedom** (an exact command or script, no deviations) when operations are fragile, the order matters, or consistency is critical: migrations, releases, anything destructive.

A narrow bridge with cliffs on both sides gets guardrails; an open field gets a direction. Most skills mix both.

## Information hierarchy

Place each piece of content by how immediately the running agent needs it:

1. **Steps in SKILL.md**: what every run does, in order.
2. **Reference in SKILL.md**: rules and facts every run may need, gotchas above all.
3. **Reference files**: material only some runs need, each behind a pointer that says when to read it ("Read `references/api-errors.md` if the API returns a non-200 status").

Rules of thumb:
- **The branching test**: inline what every branch needs; move behind a pointer what only some branches reach.
- **One level deep.** Reference files should link from SKILL.md, not from other reference files, because Claude may only preview a file reached through a chain.
- **Tables of contents** at the top of any reference file over about 100 lines, so a partial read still shows its scope.
- **Front-load SKILL.md.** After context compaction, Claude Code re-attaches only a skill's first 5,000 tokens.
- **Point, don't duplicate.** A pointer's wording decides whether Claude follows it. If a must-read file keeps being skipped, sharpen the pointer before inlining the content.

## Architecture patterns

| Pattern | Layout | Fits |
|---|---|---|
| Single file | `SKILL.md` | Short techniques and conventions |
| Router plus references | SKILL.md holds the workflow and routing; `references/<domain>.md` per domain or variant | Multiple domains, frameworks, or providers, where Claude reads only the relevant file |
| Workflow plus scripts | SKILL.md holds the steps; `scripts/` does deterministic work | File formats, validation, anything fragile |
| Template-driven | SKILL.md holds the rules; `assets/` holds templates copied into output | Documents, reports, boilerplate |
| Forked task | `context: fork` with an explicit task in the body | Self-contained jobs that don't need the conversation (Claude Code only) |

## Spec template

Write this to `<workspace>/spec.md` before drafting the skill.

```markdown
# Spec: <skill-name>

## Purpose
<One sentence: what the skill lets Claude do, for whom.>

## Triggers
- Should trigger: <5–8 representative user phrasings, including indirect ones>
- Should not trigger: <3–5 near-misses and where they belong instead>

## Targets
Platforms: <Claude Code | claude.ai | API | other agents>; allowed frontmatter accordingly.
Invocation: <model | user-only | model-only>. Why:

## Type and scope
Type: <technique | reference | discipline | task | generator | integration>
In scope: ...  Out of scope: ...

## Gaps this skill closes
| Baseline failure or missing knowledge | Skill content that fixes it | Location |
|---|---|---|

## File plan
| File | Purpose | Loaded when |
|---|---|---|
| SKILL.md | | always, on trigger |

## Freedom
<Which parts are exact commands, which are guidance, and why.>

## Borrowed content
<Units adopted from harvest.md, if any, with license notes.>

## Eval plan
<2–3 starter prompts (Standard) or 5–10 plus a coverage matrix (Deep); what the assertions will check; baseline configuration.>
```
