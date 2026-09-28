# Quality rubric

Use this to review a skill, your own or someone else's. Rate each finding **blocker** (the skill will misfire or cause harm), **major** (it will often underperform), or **minor** (polish). Run `scripts/validate_skill.py` first; it catches the mechanical issues, so this rubric can focus on judgment.

## A. Triggering

- [ ] The description says what the skill does *and* when to use it.
- [ ] It covers indirect phrasings, where users describe the need without naming the domain.
- [ ] It sets a boundary against the nearest neighbor if false triggers are likely.
- [ ] It doesn't summarize the workflow steps.
- [ ] It is written in third person, without "CRITICAL", "MUST", or "ALWAYS".
- [ ] The main use case comes first, and the whole description runs roughly 300–700 characters.
- [ ] Its vocabulary distinguishes it from the other installed skills.
- [ ] Invocation mode fits: side-effecting skills are user-invoked.

## B. Value

- [ ] Each section closes a gap seen in a baseline run, or encodes knowledge the agent couldn't infer.
- [ ] No no-ops: nothing the agent already does by default.
- [ ] Content is specific to this domain or environment, not generic best practice.
- [ ] Gotchas are present, concrete, and in SKILL.md.
- [ ] It is grounded in named sources, the user's material, or tested behavior rather than general knowledge.

## C. Structure

- [ ] What every run needs is near the top of SKILL.md.
- [ ] SKILL.md is under about 500 lines and 5,000 tokens.
- [ ] Reference files are one level deep, each linked with *when* to read it.
- [ ] Reference files over about 100 lines have a table of contents.
- [ ] Each meaning lives in one place, with no duplicated rules.
- [ ] Terminology is consistent: one term per concept.
- [ ] There are no extra docs (README, CHANGELOG) or leftover template placeholders.

## D. Instructions

- [ ] Defaults, not menus: one recommended approach per decision.
- [ ] It teaches procedures that generalize, not answers to one instance.
- [ ] Each step ends on a checkable completion condition.
- [ ] Freedom is calibrated: exact commands where operations are fragile, guidance where judgment is needed.
- [ ] Important rules carry a brief reason.
- [ ] It states the behavior wanted; prohibitions are reserved for guardrails and paired with the alternative.
- [ ] Strict output formats come with a template or a concrete example.
- [ ] Fragile or destructive work has a validation loop or plan-validate-execute.
- [ ] Nothing is time-sensitive ("after August 2025...").

## E. Scripts

- [ ] Every bundled script has been run, including a failure path.
- [ ] No interactive prompts; `--help` is useful; errors name the valid options.
- [ ] Data goes to stdout and diagnostics to stderr; output size is bounded.
- [ ] Dependencies are declared (PEP 723 or equivalent) and pinned where it matters.
- [ ] Scripts are invoked through their interpreter, with paths relative to the skill folder or `<skill-dir>`.

## F. Safety and trust

- [ ] Nothing in the skill would surprise the user given its description.
- [ ] `allowed-tools` is as narrow as the task allows; no wildcards.
- [ ] No `` !`command` `` injection with side effects, and none that could fail and abort the skill unexpectedly.
- [ ] No secrets, personal data, or machine-specific paths that shouldn't ship.
- [ ] Borrowed content is vetted, licensed for reuse, and attributed in LICENSE/NOTICE where required.

## G. Portability

- [ ] Frontmatter is valid for every target agent (`validate_skill.py` default spec target; `--target claude-code` or `claude-upload` where applicable).
- [ ] Client-specific features (Claude Code's substitutions, `!` injection, invocation fields) are absent from multi-agent skills, or degrade gracefully.
- [ ] Paths use forward slashes; runtime requirements are stated in the body or in `compatibility`.

## H. Evidence

- [ ] Evals exist, with realistic prompts, and include at least one edge case.
- [ ] The skill was compared against a baseline and beats it by more than it costs in time and tokens.
- [ ] The key instructions are exercised by at least one eval (coverage).
- [ ] Triggering has been checked against should-trigger and near-miss queries.
- [ ] What remains untested is written down and reported to the user.
