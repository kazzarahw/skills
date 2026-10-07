# Pages

## Contents

- [Five page types](#five-page-types)
- [Frontmatter: nine fields, no others](#frontmatter-nine-fields-no-others)
- [Naming and linking](#naming-and-linking)
- [Lifecycle: add-only, supersede, current state](#lifecycle-add-only-supersede-current-state)

## Five page types

| Type | Directory | What it is for | One page per |
|---|---|---|---|
| `entity` | `entities/` | A real thing: a person, service, component, vendor, contract | Thing |
| `concept` | `concepts/` | A pattern that recurs: a failure mode, a convention, a technique | Pattern |
| `synthesis` | `syntheses/` | A conclusion drawn across several pages, with the inbound links that support it | Question answered |
| `timeline` | `timelines/` | Ordered events for one subject, with the dates that anchor them | Subject |
| `claim` | `claims/` | One adjudicated assertion with its sources | Assertion |

There is no trail, overview, or contradiction type. A contradiction is two
`claim` pages and a `synthesis` that adjudicates between them; that is what
the links are for. A landscape of a domain is a `synthesis` with inventory,
flow, dependency, and boundary sections — not a sixth type.

## Frontmatter: nine fields, no others

`wiki.py lint` exits 2 on any unrecognised field. A field no page populates is
a check that silently never runs — ship only what is written.

| Field | Type | Required | Constraint |
|---|---|---|---|
| `title` | string | yes | Unique wiki-wide. None of `[ ] \| # ^ : %` |
| `type` | enum | yes | `entity`, `concept`, `synthesis`, `timeline`, `claim` |
| `sources` | list | yes | At least one path or URL. An unsourced page is an opinion with a filename |
| `created` | date | yes | `YYYY-MM-DD`. Date filters read this field |
| `updated` | date | yes | `YYYY-MM-DD`. Knowledge-change date, never mtime |
| `confidence` | enum | no | `confirmed`, `probable`, `unverified`, `inferred`, `refuted` |
| `provenance` | enum | no | `observed`, `asserted` |
| `status` | enum | no | `active`, `invalidated`, `draft` |
| `tags` | list | no | Lowercase, kebab-case, in-taxonomy |

`add` defaults `confidence: unverified`, `provenance: asserted`,
`status: active`. A page that does not say otherwise is assumed unproven.
`confidence` is the same vocabulary as every claim grade; a page graded
`probable` and a claim graded `probable` are the same statement. `status` is
the only lifecycle field — review state is `confidence: unverified`, never a
second flag. `title:` must equal the page's `# Heading`: titles are graph
identifiers, and a mismatch forks the graph.

## Naming and linking

A page is `<type>-<kebab-of-title>.md` inside its type directory. `add`
derives the name and refuses a `--filename` whose prefix disagrees with
`--type` (exit 2); lint checks the agreement from the other direction and
refuses to guess which side is right.

Write `[[Page Title]]` or `[[Page Title|display text]]`. Links resolve against
`title:`, never filenames, matching case-insensitively; a link matching two
titles is ambiguous and reported, never guessed. There is no alias table and
no redirect: write `[[Canonical Title|alias]]`, never a bare `[[alias]]`, and
quote any `[[link]]` that appears inside a YAML value. Rename a title and every
inbound link silently dangles — which is why renaming is a lint event, not a
one-line edit. A link to an `invalidated` page is a critical finding; link the
superseding page instead and say so in prose.

Every page carries at least one outbound link, or the link graph never learns
about it. An orphan with no inbound links may still be intentional — lint
reports, the agent judges.

## Lifecycle: add-only, supersede, current state

States: `draft` (not yet reviewed) → `active` → `invalidated` (superseded or
shown false) or archived. Never overwrite a contradicted page:

1. Write the new page (or section) with today's date and its own sources.
2. Set the old page's `status: invalidated` and update its date. Leave its
   text in place.
3. Link the new page from the old one, and the old one from the new one.
4. `wiki.py log --verb supersede --subject "<old> by <new>"`.

The reasoning history survives, so a later session sees what was believed,
when, and on what basis — usually where the actual error is. Order supersedes
by ingest order, never by model-stated dates.

One exception: a page may hold a `## Current State` section for state facts
(one current value), which is *replaced* in place when the world changes.
Everything else — events, claims, history — is appended, never rewritten.
Appending a state creates two answers with the stale one reading first; that
is the rot the `Current State` section exists to prevent.
