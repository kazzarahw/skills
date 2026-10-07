# Store

## Contents

- [Three layers](#three-layers)
- [Store root](#store-root)
- [Raw conventions](#raw-conventions)
- [Git discipline](#git-discipline)
- [Secrets](#secrets)

## Three layers

| Layer | Where | Who owns it | Rule |
|---|---|---|---|
| Raw | `raw/` | whatever captured it | Immutable. Never edited after capture; a correction is a new file beside the old one. |
| Curated | `entities/` `concepts/` `syntheses/` `timelines/` `claims/` | you, through `wiki.py add` | Rewritable while `status: active`, because a wrong belief that persists is the expensive failure. |
| Conventions | `SCHEMA.md` | `wiki.py init` | Field table, enums, naming and link rules on disk, so a page written months ago still has its schema beside it. |

Separating them keeps conclusions checkable: raw holds what the source said,
curated holds what you concluded, and a reader who disputes the conclusion can
still read the payload underneath. Mixing the two is how an inference quietly
becomes an observation.

`index.md` and `log.md` sit at the root. Both are machine-maintained; neither
is hand-edited (hand-edits are lost on the next regeneration, and lint reports
the drift).

## Store root

`--wiki DIR`, default `./.wiki`, overridable by the `WIKI_DIR` environment
variable. The flag always wins; the variable is the fallback for callers that
never pass flags. One store per project; point two projects at one directory
only deliberately, never by accident.

`wiki.py init --wiki <wiki>` creates `raw/`, the five type directories,
`SCHEMA.md`, `index.md`, and `log.md`. It never touches anything else.

## Raw conventions

Name captures `YYYY-MM-DD-source-briefdesc` (`2026-10-07-deploy-notes.md`), so
a listing already tells when and what. Capture the payload to disk *before*
curating, so every `sources` entry can point at a file that will still exist
tomorrow rather than a URL that may rot. Hash artifacts at capture
(`sha256sum`); record the hash beside the acquisition path when the artifact
may be disputed later. Work on copies; the original stays read-only.

Capture fails open: if a later stage (parse, curate, index) throws, the raw
file is already on disk. A single throwing filter must never silently discard
a session's evidence.

## Git discipline

Commit the store's changes with messages (`ingest: <title>`, `supersede: <old>
by <new>`), so `git blame` answers when a line was actually written — a fresh
`updated` date on a moved-but-unverified line is a false trust signal.
Pull before writing when several agents share the store; prefer append-mostly
commits. Before any bulk migration, branch first and stop on ambiguous consent;
never "back up" by copying the folder, because a copy is a second answer to
every question.

## Secrets

No credential value — key, token, cookie, password — goes into a page or into
`raw/`. Captures get read by people and tools with wider access than the
session; a credential in either layer is an exfiltration with a provenance
record. Where correlation is the point, a truncated fingerprint is allowed
(first eight hex of a hash, a key id, a name without the qualifier). That
answers "is this the same one?" without carrying the secret.
