# Retrieval

## Contents

- [Index-first discipline](#index-first-discipline)
- [Query operation](#query-operation)
- [Search semantics worth knowing](#search-semantics-worth-knowing)

## Index-first discipline

Read `index.md` before searching. It is the content-oriented catalog: one line
per page, grouped by type, each a link and a one-line summary. At wiki scale
it fits on one screen and answers "what do I already know?" faster than any
query — and it is the step that turns a second session on a related subject
into a continuation instead of a rediscovery.

`index.md` is rewritten whole by `wiki.py index`, from every page in the tree.
It is generated output; hand-edits are lost on the next run. `log.md` is
chronological and append-only — `## [YYYY-MM-DD] verb | subject` — never
rewritten, never reordered, so the recent history survives a grep for the
`## [` prefix. It answers "when did we last look at this, and what changed
since": the two questions that decide whether a cached belief is still worth
anything. Conventional verbs (unenforced by the script): `ingest`,
`supersede`, `refute`, `link`. Log ingests and changes, never routine
queries.

A healthy wiki still goes unread mid-task. Consult it explicitly: after a
first failed hypothesis, before a second attempt, and whenever the task smells
like a solved problem.

## Query operation

1. Read `index.md` and the log tail (`grep "^## \[" <wiki>/log.md | tail -20`).
   A direct search without this step tends to re-derive what is already filed.
2. `python3 scripts/wiki.py search --wiki <wiki> --query "<terms>"` with
   `--tag`, `--type`, `--status`, `--date-from`/`--date-to`, `--limit`
   (default 20), `--offset` for paging, `--json` for harness use.
3. Read the hits that matter in full: `python3 scripts/wiki.py show --wiki
   <wiki> --title "<exact title>"` (case-insensitive; ambiguity reported).
4. Follow the outbound `[[links]]` on those pages. The graph, not the keyword,
   is what connects a decision to its context to the claim it rests on.

Done when you can name the page that answers the question, or state plainly
that the wiki does not hold it. `search` exits 0 on zero matches, so "no
results" is a reading of the output, not of the exit code.

## Search semantics worth knowing

Scoring is additive per tag (8.0 a tag, 10.0 a title hit), so two matching
tags outrank a title hit — a page can surface above a better match. `--tag`
is OR, not AND. `--date-from`/`--date-to` compare `created`, and a page whose
`created` is missing or malformed *fails* the filter and is named in the
output; it is never silently treated as in-window. Filters only see pages
that declare the key — a tag search never matches an untagged page, which is
correct behavior, not a miss.
