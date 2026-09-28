# Writing guide

How to write the two parts of a skill that decide whether it works: the description, which decides whether the skill loads, and the body, which decides what the agent does once it has.

## Contents
- Part 1: The description
- Part 2: The body
- Match the form to the failure
- Discipline skills: resisting rationalization
- Anti-patterns

---

## Part 1: The description

The description is the only part of the skill the agent sees before deciding to load it, and it sits in context on every turn alongside every other skill's description. It carries the whole burden of triggering.

### The formula

> **[What it does: capabilities and outcomes, third person.] Use when [the situations and user intents that call for it, including indirect ones].** Optionally: [a boundary against the nearest neighbor].

```yaml
description: Extract text and tables from PDF files, fill PDF forms, and merge or split PDFs. Use when the user works with PDF files or mentions forms, document extraction, or combining documents, even if they don't say "PDF".
```

### Rules

- **What plus when.** The capability sentence tells the agent what the skill is good for; the "Use when" clause tells it when to reach for it. Both matter, and all the "when" information belongs here, not in the body, which only loads after the decision has been made.
- **Outcomes, not procedure.** Don't summarize the workflow steps. In testing, a description that summarized a two-stage review ("reviews code between tasks") led the agent to follow that one-line summary and skip the body's second stage. Name what the skill achieves and leave how to the body.
- **Third person.** The description is injected into the system prompt, where "I can help you..." or "You can use this to..." read inconsistently. "Processes X" and "Use when..." are both fine.
- **Cover indirect phrasings.** Real users describe the need without naming the domain ("my boss wants a chart from this data" for a CSV-analysis skill). Say so explicitly: "even if they don't mention CSV".
- **Assertive in coverage, calm in tone.** Agents tend to under-use skills, so list the contexts generously. But current frontier models respond strongly to aggressive wording (Anthropic documents this for Claude): "CRITICAL: you MUST use this skill" causes over-triggering. Write "Use when...", not "ALWAYS use when...".
- **Draw boundaries against near neighbors** when false triggers are likely: "For editing existing Word files, not creating PDFs." Keep it to one clause.
- **Lead with the main use case.** Clients truncate long entries in the skill listing, and some drop descriptions entirely when many skills are installed (Claude Code drops those of rarely used skills first). The first sentence has to stand on its own.
- **Length.** Aim for roughly 300–700 characters. The spec's hard limit is 1,024; Claude Code caps `description` plus `when_to_use` at 1,536 characters in its listing. Every character is paid for on every turn.
- **Format.** No angle brackets or XML tags (rejected on upload). If the text contains `: ` (colon-space), quote the whole value or use a `>-` block scalar, because an unquoted colon breaks YAML parsing, and in Claude Code a broken frontmatter means the skill loads with no description at all.
- **Distinct words.** The description competes with every other skill's. Use the specific nouns and verbs of this domain (file types, tool names, error messages users paste) rather than words every skill could claim ("help", "tasks", "data").
- **User-invoked skills** (`disable-model-invocation: true`) are never matched by the agent, so their description is just a one-line summary for the human reading the `/` menu.

### Examples

| Weak | Why | Stronger |
|---|---|---|
| `Helps with documents.` | No capability, no trigger | `Create and edit Word documents (.docx): tracked changes, comments, templates. Use when the user asks for a Word file or wants a .docx edited.` |
| `I can help you write commit messages.` | First person, no trigger conditions | `Generate commit messages from staged changes. Use when the user asks for a commit message or wants their diff summarized for a commit.` |
| `Use for TDD: write the test, watch it fail, write minimal code, refactor.` | Summarizes the workflow, which invites skipping the body | `Use when implementing any feature or bugfix, before writing implementation code.` |
| `ALWAYS use this skill for ANY data task.` | Aggressive and over-broad, so it triggers everywhere | `Analyze CSV and TSV files: summary statistics, derived columns, charts, cleaning. Use when the user has tabular data to explore, even if they don't say "CSV".` |

---

## Part 2: The body

### Principles

**Add what the agent lacks; cut what it knows.** For every line ask whether the agent would get this wrong without it. Explaining what a PDF is, how HTTP works, or that code should be readable costs tokens on every load and changes nothing. The test is relative to the model, not to a human reader, so settle disagreements by running the skill, not by debate.

**Be concrete.** "Handle errors appropriately" teaches nothing. "The API returns 200 with `{"error": ...}` on validation failures; check the body, not the status code" teaches everything.

**Give defaults, not menus.** Name the tool or approach to use and mention an alternative only for a specific case: "Use pdfplumber. For scanned PDFs, use pdf2image with pytesseract instead." A list of five equal options makes the agent spend effort choosing.

**Teach the procedure, not the answer.** A skill should work across the whole class of tasks. "Read the schema in `references/schema.yaml`, join on the `_id` foreign keys, apply the user's filters as WHERE clauses" generalizes; "join orders to customers where region = 'EMEA'" doesn't.

**Explain the why, briefly.** A reason lets the agent handle cases the rule didn't anticipate: "Use `--no-cache`, because the CI cache holds stale lockfiles." Keep it to a clause; don't narrate history ("in session 3 we discovered..."), which is a story, not an instruction.

**Say what to do.** State the target behavior ("write one-line comments") rather than prohibiting its opposite. A prohibition puts the unwanted behavior in front of the model and invites negotiation with it. Keep prohibitions for hard guardrails, and even then pair each with the behavior you want instead.

**Calibrate emphasis.** ALL-CAPS MUST, NEVER, ALWAYS, and CRITICAL are a yellow flag: usually a sign that a reason is missing. Current models follow plain instructions well and over-apply emphatic ones. Save emphasis for the few rules whose violation causes real damage, and give the reason alongside.

**End every step on a completion criterion**, a condition the agent can check to know the step is done. Vague bounds ("once you understand the codebase") invite stopping early. Demanding criteria drive thoroughness: "every modified model accounted for" produces more careful work than "produce a change list".

**One term per concept.** Pick "field" or "box" or "element", never all three. Consistent terms help the agent connect instructions to each other.

**Write standing instructions.** Once loaded, a skill's content usually stays in context for the rest of the session, and the agent doesn't re-read the file. Guidance meant to apply throughout a task should read as a standing rule, not a one-time step.

**Avoid time-sensitive statements** ("after August 2025, use the new API"). State the current method; if the old one still matters, put it under a collapsed "Old patterns" note.

**Use the platform's names.** Refer to other skills by name without force-loading them. Name MCP tools with their server (`ServerName:tool_name`). Use forward slashes in paths.

### Patterns worth reaching for

**Gotchas section.** Often the highest-value content in a skill: concrete, environment-specific facts that defy reasonable assumptions. Keep it in SKILL.md so the agent reads it before hitting the situation. When the agent makes a mistake you have to correct, add the correction here.

```markdown
## Gotchas
- The `users` table soft-deletes: add `WHERE deleted_at IS NULL` or results include deactivated accounts.
- `/health` returns 200 while the database is down; check `/ready` instead.
```

**Templates for output.** the agent matches concrete structures more reliably than prose descriptions of them. Say how strict the template is ("use exactly this structure" versus "a sensible default; adapt as needed"). Put short templates inline and long ones in `assets/`.

**Examples.** One excellent input/output example beats several mediocre ones. Make it realistic and complete; avoid fill-in-the-blank skeletons.

**Checklists** for multi-step workflows with dependencies, which the agent can copy and tick off as it goes.

**Validation loops**: do the work, run a validator (a script or a checklist), fix, repeat, and proceed only when it passes.

**Plan, validate, execute** for batch or destructive work: write the plan to a file (`changes.json`), validate it against the source of truth with a script, then apply it. Make the validator's errors name the valid options ("Field 'sig_date' not found; available: signature_date, ...").

**Conditional routing**: "Creating a new document? Follow 'Creation' below. Editing one? Follow 'Editing'." Move large branches into reference files.

**Leading words.** A single well-chosen word the model already understands ("tracer bullet", "red/green", "tight loop") can replace a sentence of explanation each time it recurs. Prefer existing vocabulary over coined terms, which must be defined before they help.

### Body skeleton

A reasonable default, not a mandate. Omit any section with nothing real to say.

```markdown
# <Skill title>

<One or two sentences: what this accomplishes and the approach.>

## Workflow (or Quick start)
1. <Step> — done when <checkable condition>.
2. ...

## Gotchas
- ...

## Output format
<Template, if output shape matters.>

## Resources
- `references/x.md`: read when <condition>.
- `scripts/y.py`: run to <purpose>; `python3 scripts/y.py --help` for options.
```

A "When to use this skill" section in the body usually wastes tokens, because the body loads only after the decision to use it has been made. Use the body for routing between cases instead.

---

## Match the form to the failure

Before writing guidance to fix a problem seen in a baseline or eval run, classify the failure. The form that fixes one kind of failure backfires on another.

| Observed failure | Form that works | Form that backfires |
|---|---|---|
| Knows the rule but breaks it under pressure | Bright-line rule, rationalization table, red flags (next section) | Soft guidance ("consider...") |
| Complies, but the output has the wrong shape (bloated, buried answer, restated input) | A positive recipe: what the output *is*, its parts, in order | A list of prohibitions ("don't restate...") |
| Leaves out a required element | A required slot in the template it fills in | A prose reminder near the template |
| Behavior should depend on a condition | A conditional on an observable fact ("if the brief exists, reference it") | An unconditional rule plus exceptions |
| Ignores an instruction that is present | Make that instruction clearer or more prominent, or sharpen its pointer | Adding a second, similar instruction |

Two traps: a nuance clause ("don't X unless it matters") reopens the negotiation the rule was meant to close, so write real exceptions as their own conditionals; and an exemption ("this limit doesn't apply to code blocks") tends to leak, so restructure so the rule can't reach what it shouldn't touch.

---

## Discipline skills: resisting rationalization

Only for skills that enforce a practice the agent knows but skips under pressure (test first, verify before claiming done). For other failures these techniques backfire; use the table above.

- **Close loopholes by name.** "Wrote code before the test? Delete it and start over. Don't keep it as reference, don't adapt it while writing tests."
- **State that the letter is the spirit.** "Violating the letter of this rule is violating its spirit" cuts off "I'm following the spirit" arguments.
- **Rationalization table.** Collect the excuses from baseline runs verbatim and answer each one.

  | Excuse | Reality |
  |---|---|
  | "Too simple to test" | Simple code breaks. The test takes 30 seconds. |

- **Red flags list**: thoughts that mean stop ("this case is different because...").
- **Put the moment of temptation in the description**: "Use when about to claim work is done, before committing."
- Test with pressure scenarios (`references/evaluation.md`).

---

## Anti-patterns

- **Generic best practices** that restate what the agent already does ("write clean, maintainable code").
- **Narrative**: "In our session on Oct 3 we found..." Extract the rule; drop the story.
- **Walls of options** with no default.
- **Deep reference chains**: SKILL.md → a.md → b.md → the actual information.
- **Duplication**: the same rule in SKILL.md and a reference file, drifting apart over time.
- **Sediment**: stale lines kept because deleting feels risky. Review every line on each revision.
- **Workflow summaries in the description.**
- **Extra docs inside the skill** (README, CHANGELOG, installation guides). The skill is for the agent; anything else is clutter it may read.
- **Multi-language dilution**: the same example in five languages. One good example is enough; the agent ports well.
- **Over-fitting to eval prompts**: special cases that fix a test while teaching nothing general.
