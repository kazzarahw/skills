# Cherry-picking and merging skills

Use this when the user wants to combine skills, borrow specific rules or steps from other skills ("take the gotchas from X and the review checklist from Y"), or when Phase 2 found several skills that each cover part of the need.

The goal is a skill that reads as if one careful author wrote it, where every borrowed piece earns its place, and where you can say where each piece came from and whether you may use it.

## Contents
- 1. Collect the sources
- 2. Vet each source
- 3. Extract units
- 4. Triage
- 5. Let the user choose
- 6. Resolve conflicts
- 7. Integrate
- 8. Licensing and attribution
- 9. Verify that each borrowed piece helps
- Merging whole skills
- Ledger template

## 1. Collect the sources

Copy every source into `<workspace>/sources/`, including skills that are already installed. Work on copies so you never edit an installed skill in place.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_skill.py <owner/repo@skill | URL | path> --dest <workspace>/sources
```

A SKILL.md the user pasted into the chat counts as a source too: save it under `sources/pasted-<name>/SKILL.md` and note in the ledger that it has no verifiable provenance.

## 2. Vet each source

Follow `references/vetting-skills.md` before reading any source for content. Sources judged "do not reuse" contribute ideas at most, re-expressed in your own words, never text or code.

## 3. Extract units

Split each source into small, citable units: steps, rules, gotchas, templates, examples, code, tables.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_units.py <workspace>/sources/<copy> \
  --source-id A --include-references --format md > <workspace>/harvest-A.md
```

Give each source its own letter (`A`, `B`, ...), so unit IDs such as `A12` and `B3` stay unique across the whole harvest. Use `--format json` when you want to filter or sort the units programmatically. The script records each unit's file, line range, section path, kind, and flags such as `emphatic` (heavy MUST/NEVER wording) or `command` (contains a command or path).

## 4. Triage

Merge the per-source files into `<workspace>/harvest.md` (template below) and give every unit a verdict:

- **adopt**: use as is, apart from voice and terminology;
- **adapt**: the idea is right but it needs changing, so say what;
- **reject**: say why.

Adopt freely:
- gotchas and environment facts that defy reasonable assumptions;
- procedures that have clearly been exercised (specific commands, flags, orderings, validation steps);
- templates for output formats;
- scripts that do deterministic work and pass vetting.

Reject:
- **no-ops**: things Claude already does by default ("write clean code", "be thorough");
- generic advice with no specific action ("handle errors appropriately");
- details tied to the source author's environment that don't transfer (their paths, their team's conventions);
- duplicates of something you already adopted (keep the better-worded one);
- anything the vet flagged that you can't explain;
- content that conflicts with the target platform (for example Claude Code-only frontmatter in a skill meant for claude.ai).

## 5. Let the user choose

Present units grouped by theme rather than by source, with your recommended picks marked and a one-line reason for each. For a handful of choices, use AskUserQuestion with `multiSelect: true` (at most four options per question, four questions per call). For more, show a compact table and ask the user to reply with the IDs they want to add or drop. Record their decisions in the ledger.

## 6. Resolve conflicts

When sources disagree, settle it in this order and record each decision in the ledger:

1. the user's explicit preference;
2. the official spec and platform docs, for questions of format and platform behavior (`references/platform-reference.md`);
3. evidence from your own evals and transcripts;
4. primary-source research (`research.md`);
5. the more widely adopted and better-tested source.

If two sources disagree on approach and nothing above settles it, pick one and add an eval that would reveal the difference, then compare them head to head in Phase 7.

## 7. Integrate

- **Rewrite into one voice.** Pick one term per concept and use it everywhere; borrowed text arrives with other authors' vocabulary ("assertion" vs "expectation", "run" vs "execute"). Convert rules to the target skill's register, which should be calm, explain the why, and save emphasis for real guardrails.
- **One source of truth.** Each meaning lives in one place. Don't keep two versions of a rule "for emphasis".
- **Place by need.** Content every run needs goes in SKILL.md; content only some branches need goes in a reference file linked with when to read it (`references/design.md`, "Information hierarchy").
- **Strip hazards.** Remove `` !`command` `` lines, `allowed-tools` grants, and hooks unless the new skill needs them and the user agrees.
- **Keep provenance out of SKILL.md.** Attribution comments inside the skill cost tokens on every load. Keep provenance in `harvest.md`, and license notices in the skill's `LICENSE`/`NOTICE` files and in the headers of copied scripts.

## 8. Licensing and attribution

Check each source's license: its frontmatter `license` field, a LICENSE file in the skill folder, or the repo's root LICENSE (recorded by `fetch_skill.py` in `.provenance.json`).

| License | What you may do |
|---|---|
| MIT, BSD, ISC | Copy and modify; keep the copyright and license notice. |
| Apache-2.0 | Copy and modify; include the license, keep existing notices, and mark modified files as changed. |
| CC-BY | Copy and modify with attribution. |
| No license | All rights reserved by default. Re-express ideas in your own words; copy no text or code. |
| Proprietary or unclear | Copy nothing; ask the user. |

Ideas, techniques, and facts can generally be reused; specific text and code are what licenses govern. This is practical guidance, not legal advice. Tell the user when a license question affects what you can include.

## 9. Verify that each borrowed piece helps

A borrowed rule that changes nothing costs tokens on every load and buys nothing.

- Make sure at least one eval exercises each adopted unit. Running `extract_units.py` on the finished SKILL.md gives you a list to map evals against (`references/evaluation.md`, "Coverage matrix").
- If a borrowed rule shows no effect against the baseline, drop it.
- When merging whole skills, the merged skill should do at least as well as each original on that original's own intended prompts. Run a few of each original's prompts as regression evals.

## Merging whole skills

First decide whether to merge at all. If the originals trigger on different vocabulary and serve different tasks, keeping them separate (with sharper descriptions) usually beats one broad skill, since merging trades trigger precision for convenience. Merge when they serve the same task, share most steps, or compete for the same prompts.

To merge:
1. Inventory each original's units and triggers.
2. Choose an architecture. The usual shape is a SKILL.md that holds the shared workflow and routing, plus one reference file per former domain.
3. Write one description that covers the union of the triggers without becoming vague. Every clause in it is paid for on every turn.
4. Run the originals' prompts as regression evals.
5. Retire the originals only after the merged skill passes. Tell the user to disable them, because overlapping skills compete for the same prompts.

## Ledger template

```markdown
# Harvest ledger: <target skill>

## Sources
| ID | Source | Commit / version | License | Vet verdict |
|---|---|---|---|---|
| A | anthropics/skills@skill-creator | 1a2b3c4 | Apache-2.0 | safe to reuse |

## Units
| ID | Kind | From (file:lines) | Summary | Verdict | Target location | Notes |
|---|---|---|---|---|---|---|
| A12 | gotcha | SKILL.md:140-143 | eval dirs must start with `eval-` | adopt | references/evaluation.md | |
| B3 | rule | SKILL.md:88 | "always use TDD" | reject | | no-op for this domain |

## Conflicts
| Topic | Positions | Decision | Basis |
|---|---|---|---|

## User decisions
<What the user added or dropped, and when.>
```
