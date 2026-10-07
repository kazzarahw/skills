# Lint

## Contents

- [Running lint](#running-lint)
- [The check set](#the-check-set)
- [Remediation ladder](#remediation-ladder)
- [Taxonomy maintenance](#taxonomy-maintenance)

## Running lint

`python3 scripts/wiki.py lint --wiki <wiki>`. Read the exit code as a scheme,
not a boolean: **2** means at least one critical finding, **1** warnings only,
**0** clean. Warnings alone exit 1, so 1 is not "fine". `--fix` regenerates
`index.md` and nothing else — never a body, a title, or a frontmatter value.
`--dry-run` reports without writing; `--json` emits findings for a harness.

Run lint after every ingest and before every commit. Work the criticals
first. Lint authority is split on purpose: deterministic safe fixes (index
regeneration, resolvable link targets) may be automatic; facts are never
auto-fixed — repair is a separate, reviewed edit.

## The check set

| Check | Severity | What it catches |
|---|---|---|
| frontmatter completeness | critical | Missing required field, unrecognised field, non-list `sources`/`tags`, scalar/list confusion, bad date, bad enum |
| filename/type agreement | critical | Prefix or directory disagreeing with declared `type:` (lint never guesses which is right) |
| broken wikilink | critical | `[[target]]` with no page; names the nearest title (usually a rename) |
| invalidated link | critical | Link to a `status: invalidated` page |
| duplicate titles | critical | Same title twice, including under different case; merge preserving both, never delete one side |
| title/heading agreement | warning | `title:` differing from the `# Heading` |
| tag format | warning | Non-lowercase or non-kebab tags; in-taxonomy membership is a manual check below |
| orphans | warning | No inbound links (`index.md` exempt); may be intentional — judge, don't auto-delete |
| no outbound link | warning | A fresh wiki's first page is expected; many pages with none means links were never written |
| stale link text | warning | Link matching no title but a near-miss (likely rename) or a filename instead of a title |
| index coverage | warning | Page missing from `index.md`, or index entry with no page — both directions; fixed by `--fix` |

Manual checks — judgment lint runs, not the script: provenance completeness
(body grade labels match frontmatter confidence), type validity (sections match
the declared type's template), unresolved contradictions (two claims with no
adjudicating synthesis), in-taxonomy tags, near-duplicate content above the
title threshold (merge preserving both).

## Remediation ladder

1. Restore, don't invent: a `broken-wikilink` after a rename is fixed by
   restoring the exact title, not by creating a stub page with the old name.
2. Redirect through supersede: point the link at the superseding page and say
   so in prose.
3. Merge preserving both: duplicates merge evidence and source lists under
   one title ("also detected by"), with the losing title kept as a
   `[[Canonical|old name]]` reference where linked.
4. Regenerate, don't hand-edit: index drift is fixed by `lint --fix`, never
   by editing `index.md`.
5. Record disputes: a contradiction that will not resolve becomes two claims
   plus an adjudicating synthesis marked contested — never a silent pick.

## Taxonomy maintenance

Tags stay lowercase kebab-case and inside a known taxonomy (`status`, `type`,
topic tags the wiki actually uses). Propose a new tag by using it on one page
and noting it in the log; check for conflicts (synonyms, scope overlap) before
it spreads; document it where the wiki lists its tags; from then on lint
recognises it. Deprecate by migrating every use, then removing. Version the
taxonomy in git like any schema change. One property, one type, everywhere: a
field that is a date on one page and text on another corrupts every filter
that reads it.
