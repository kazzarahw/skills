## Contents

- [Three layers](#three-layers)
- [Frontmatter: nine fields, no others](#frontmatter-nine-fields-no-others)
- [Five page types](#five-page-types)
- [Naming and linking](#naming-and-linking)
- [Index-first discipline](#index-first-discipline)
- [Add-only: supersede, never overwrite](#add-only-supersede-never-overwrite)
- [Operation 1 — ingest](#operation-1--ingest)
- [Operation 2 — query](#operation-2--query)
- [Operation 3 — lint](#operation-3--lint)
- [When exploration compounds](#when-exploration-compounds)
- [Secrets](#secrets)

The wiki is the part of this skill that survives the session. Everything else — the pivots, the
queries, the intermediate dead ends — is spent to produce two durable things: curated pages under
`<wiki>/` and an audit trail of what was asked and what changed.

Root: `--wiki DIR`, default `./.osint-wiki`, overridable by environment variable `OSINT_WIKI`.
`wiki.py` resolves that order itself, so a `--wiki` flag always wins and the variable is the
fallback for agents that never pass flags.

## Three layers

| Layer | Where | Who owns it | Rule |
|---|---|---|---|
| Raw | `raw/` | `scripts/evidence.py` | Immutable. Hashed at capture, appended to the case manifest, never edited afterwards. A correction is a new file beside the old one. |
| Curated | `entities/` `concepts/` `syntheses/` `timelines/` `claims/` | you, the model, through `wiki.py add` | Derived knowledge. Rewritable while `status: active`, because a wrong belief that persists is the expensive failure. |
| Conventions | `SCHEMA.md` | `wiki.py init` | The field table, enums, naming rule and link rule, written to disk so a page written six months ago still has a schema beside it. |

Separating them prevents contamination and enables auditability: the raw layer keeps what the
source actually said, the curated layer keeps what you concluded, and a reader who disagrees with
the conclusion can still read the payload underneath it. Mixing the two is how an inference
quietly becomes an observation.

`index.md` and `log.md` sit at the root. Both are machine-maintained; neither is hand-edited.

## Frontmatter: nine fields, no others

`wiki.py lint` exits **2** on any unrecognised field, so the table is the whole schema. Declaring a
field that no page ever populates is not a design choice — it is a check that silently never runs.
Ship only what is written.

| Field | Type | Required | Constraint |
|---|---|---|---|
| `title` | string | yes | Unique wiki-wide. No `[`, `]` or `|` character — those break wikilink parsing. |
| `type` | enum | yes | `entity`, `concept`, `synthesis`, `timeline`, `claim`. |
| `sources` | list | yes | At least one path or URL. An unsourced page is an opinion with a filename. |
| `created` | date | yes | `YYYY-MM-DD`. Date filters read this field. |
| `updated` | date | yes | `YYYY-MM-DD`. |
| `confidence` | enum | no | `confirmed`, `probable`, `unverified`, `inferred`, `speculative`. |
| `provenance` | enum | no | `tool-proven` when a tool's output was observed, `model-asserted` when the model says so and no tool ran. |
| `status` | enum | no | `active`, `invalidated`, `draft`. |
| `tags` | list | no | Lowercase, kebab-case. |

`wiki.py add` defaults `confidence: unverified`, `provenance: model-asserted`, `status: active`. The
`model-asserted` default is deliberate: a page that does not say otherwise is assumed unproven.

`confidence` here is the same five-term vocabulary as the claim ledger in `references/grading.md`.
The words mean the same thing in both places; a page graded `probable` and a claim graded
`probable` are the same statement.

## Five page types

| Type | Directory | What it is for | One page per |
|---|---|---|---|
| `entity` | `entities/` | A real actor or asset: a domain, a registrant, a handle, a wallet, a person, a certificate. | Thing |
| `concept` | `concepts/` | A pattern or technique that recurs across cases: a registrar pattern, a document-forgery tell, a naming convention. | Pattern |
| `synthesis` | `syntheses/` | A conclusion drawn across several pages, with the inbound links that support it. | Question answered |
| `timeline` | `timelines/` | Ordered events for one subject, with the dates that anchor them. | Subject or incident |
| `claim` | `claims/` | One adjudicated assertion with its sources, mirroring a record in `<case>/claims.jsonl`. | Assertion |

There is no `trail`, `overview` or `contradiction` type. A contradiction is two `claim` pages and a
`synthesis` that adjudicates between them; that is what the links are for.

## Naming and linking

A page is `<type>-<kebab-of-title>.md` inside the directory for its type: `entity-acme-registrar.md`
in `entities/`. `wiki.py add` derives the name from `--type` and `--title` and refuses a `--filename`
whose prefix disagrees with `--type` (exit 2). `wiki.py lint` checks the same agreement from the
other direction and refuses to guess which of the two is right when they conflict.

**Links resolve against the `title:` field, never against a filename.** Write `[[ACME Registrar]]`
or `[[ACME Registrar|the registrar]]` in the body.

The hazard, stated plainly: there is no alias table and no redirect. Rename a title and every
inbound link silently becomes a dangling reference — the pages still read fine, the knowledge
graph is quietly severed, and the only symptom is a `broken-wikilink` finding nobody runs lint to
see. That is precisely why `wiki.py lint` exists, and why renaming is a lint event rather than a
one-line edit.

A link to a page marked `status: invalidated` is a critical finding, not a warning. If you still
need the historical link, say so in prose and link the superseding page instead.

## Index-first discipline

Read `index.md` before searching. It is the content-oriented catalog: one line per page, grouped
by type, each line a link and a one-line summary. At the scale of a wiki, it fits in one screen and
answers "what do I already know?" faster than any query, and it is the step that turns a second
investigation on a related subject into a continuation instead of a rediscovery.

`index.md` is **rewritten whole** by `python3 scripts/wiki.py index --wiki <wiki>`, from every page
in the tree. It is generated output; hand-edits are lost on the next run. `--fix` during lint
regenerates it and touches nothing else — no body, no title, no frontmatter value.

`log.md` is **chronological and append-only**: one line per action, never rewritten, never
reordered.

```
## [YYYY-MM-DD] verb | subject
```

`wiki.py log --verb ingest --subject "ACME Registrar"`. The prefix is fixed so the recent history
survives the obvious query:

```bash
grep "^## \[" <wiki>/log.md | tail -5
```

Verbs worth using: `ingest`, `query`, `supersede`, `refute`, `link`. The log answers "when did we
last look at this, and what changed since" — the two questions that decide whether a cached belief
is still worth anything.

## Add-only: supersede, never overwrite

Never overwrite a fact. When a page carries something that later evidence contradicts:

1. Write the new page (or the new section) with today's `created`/`updated` and its own sources.
2. Set the old page's `status: invalidated` and change its `updated` date. Leave its text in place.
3. Link the new page from the old one, and the old one from the new one.
4. `wiki.py log --verb supersede --subject "<old title> by <new title>"`.

The reasoning history survives, so a later investigation can see what was believed, when, and on
what basis — which is usually where the actual error is. Overwriting leaves a wiki that is
confidently right about a question nobody remembers asking.

## Operation 1 — ingest

Filing something new into the wiki.

1. Capture the payload to disk first, through `scripts/evidence.py capture`, so the page's `sources`
   entry points at a hashed file rather than a URL that may rot.
2. `python3 scripts/wiki.py search --wiki <wiki> --query "<name>"` — check whether the page already
   exists under a different title. A duplicate entity page is the failure this whole layer exists
   to prevent.
3. Choose the type. Person or asset → `entity`. Recurring pattern → `concept`. Conclusion spanning
   several pages → `synthesis`. Dated sequence → `timeline`. One adjudicated assertion → `claim`.
4. `python3 scripts/wiki.py add --wiki <wiki> --type <type> --title "<title>" --source "<path or
   url>" [--source <more>] [--tag <tag>] [--confidence <term>] [--provenance tool-proven] [--status
   active] [--summary "<one line>"] [--body-file <path>]`. Use `--body-file -` to read the body from
   stdin.
5. Add at least one `[[wikilink]]` in the body or summary to the related page, or the page lands as
   an orphan and the link graph never learns about it.
6. `python3 scripts/wiki.py index --wiki <wiki>`, then `python3 scripts/wiki.py log --wiki <wiki>
   --verb ingest --subject "<title>"`.

Exit criterion: the command exits 0 and prints `wrote <path>`, `index.md` lists the page, and
`log.md` carries the line. Exit 2 from `add` means a refused write — duplicate title, filename/type
mismatch, bad enum, or an existing page with different content (pass `--force` only when replacing
is genuinely intended, and prefer editing in place).

## Operation 2 — query

Reading prior knowledge.

1. Read `index.md` and `grep "^## \[" <wiki>/log.md | tail -20`. This is the index-first step; a
   direct search without it tends to re-derive what is already filed.
2. `python3 scripts/wiki.py search --wiki <wiki> --query "<terms>" [--tag t] [--type <type>]
   [--status <status>] [--date-from YYYY-MM-DD] [--date-to YYYY-MM-DD] [--limit 20] [--offset 0]
   [--json]`. `--limit` defaults to 20 and `--offset` pages through, because a wiki of a few hundred
   pages will otherwise flood the output.
3. Read the hits that matter in full: `python3 scripts/wiki.py show --wiki <wiki> --title "<exact
   title>"`.
4. Follow the outbound `[[links]]` on those pages. The graph, not the keyword, is what connects a
   registrar to a document tell to a prior claim about the same actor.

Two search behaviours worth knowing before you read a result as a fact. Scoring is additive per tag
(8.0 a tag, 10.0 a title), so two matching tags outrank a title hit — a page can surface above a
better match. And `--tag` is OR, not AND. `--date-from`/`--date-to` compare `created`, and a page
whose `created` is missing or malformed **fails** the filter and is named in the output; it is never
silently treated as in-window.

Exit criterion: you can name the page that answers the question, or state plainly that the wiki does
not hold it. `search` exits 0 on zero matches, so "no results" is a reading of the output, not of
the exit code.

## Operation 3 — lint

1. `python3 scripts/wiki.py lint --wiki <wiki>` — checks frontmatter completeness and recognised
   fields, enum values, unknown types, filename/type and directory/type agreement, duplicate titles,
   broken wikilinks, links to invalidated pages, orphans, pages with no outbound link, link text
   that looks like a stale title or a filename, and whether `index.md` is the generated form.
2. Read the exit code as the scheme, not as a boolean: **2** = at least one critical finding, **1**
   = warnings only, **0** = clean. Warnings alone exit 1, so 1 is not "fine".
3. `--fix` regenerates `index.md` and nothing else — never a body, a title or a frontmatter value.
   `--dry-run` reports without writing; `--json` emits the findings for a harness to branch on.
4. Work the criticals first. `broken-wikilink` after a rename is fixed by restoring the link text to
   the exact title, not by creating a stub page with the old name; `stale-link` names the nearest
   page, which is usually the one the link meant.

Exit criterion: exit 0. Exit 1 with only orphans and `no-outbound-wikilink` on a fresh wiki is
expected on the first page; a wiki of many pages where every page is an orphan means the links were
never written.

## When exploration compounds

File a result back when it satisfies one of these, not merely when it was interesting:

- it would save the next investigation a collection step (a working query, a registrar pattern, a
  document tell);
- it is a page the report cites more than once;
- it refutes something already filed — which is `supersede` plus a `refute` log line, and the most
  valuable thing to write down.

Keep the wiki thin enough to read. A page that only restates its own source belongs in `raw/` and
in the case folder; a page earns its place by linking two or more other pages.

## Secrets

No credential value — API key, token, session cookie, password — goes into a wiki page or into
`raw/`. Raw captures are hashed evidence and get read by people and by tools with wider access than
the investigation; a credential in either layer is an exfiltration with a provenance record.

Where correlation is the point, a truncated fingerprint is allowed: the first eight hex of a hash, a
key id, a domain without the subdomain. That answers "is this the same key?" without carrying the
key. `scripts/capabilities.py` reports whether a variable is set and never its value, length,
prefix or hash; the same discipline applies to anything you write by hand.

See also `references/collection.md` for what may be collected at all, and `references/grading.md`
for the `confidence` terms.