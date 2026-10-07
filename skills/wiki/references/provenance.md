# Provenance

## Contents

- [Two axes, never merged](#two-axes-never-merged)
- [Observation versus inference](#observation-versus-inference)
- [Citation format](#citation-format)
- [Negative findings and gaps](#negative-findings-and-gaps)
- [Artifact metadata](#artifact-metadata)

## Two axes, never merged

`confidence` (how strong) and `provenance` (where from) are orthogonal. A
`tool-proven`-style binary and a graded scale measure different things; merging
them into one label destroys both. State both, separately:

- `confidence`: `confirmed` (two independent sources, or one authoritative
  primary record), `probable` (one credible source, uncorroborated),
  `unverified` (observed, not assessed), `inferred` (derived, reasoning
  stated), `refuted` (re-checked against the primary record and found wrong).
- `provenance`: `observed` (seen in the source) or `asserted` (the model
  concluded it).

Grade at capture time, not reconstructed at the end. Independence means
different origin, not different website — three aggregators repeating one
record are one source. Trace a source's origin before claiming corroboration;
circular reporting is the classic false confirmation. probability and
confidence stay separate axes: "likely, low confidence" is legitimate, and a
bare percentage with no rung is not a grade.

## Observation versus inference

An observation is what a source says; an inference is what you concluded; an
assessment is what you recommend. They are never filed as the same thing. Test
every sentence by its verb: `is` / `shows` states an observation, `indicates`
an inference, `we assess` an assessment. A sentence that cannot say which it
is has smuggled a conclusion into the evidence.

Rules: never present inferred as observed. Inferred entries state what
evidence would confirm them. When in doubt, label down — `probable` over
`confirmed`, `inferred` over observed. A claim whose only support is a single
source stays `probable`; single-source claims are flagged, estimates and
opinions labeled inference, genuine conflicts left unsettled rather than
picked silently.

## Citation format

Cite inline as `Source Title (link), date/version` and close every page
with a Sources section: `Title (link) — one-line summary, date/version`.
Use the identical citation string everywhere a source is named, so a citation
resolves to exactly one captured record. Pin the version or date every claim
was checked against: library, document, or repo version for technical claims;
retrieval UTC for pages. "As cited in" chains decay — if the primary source
cannot be located, flag the chain rather than citing the intermediary as the
origin. Code-backed claims store `path:line` plus the repo version or commit.
Never cite a snippet: open the source, read it in full, then file.

Every stored claim carries its confidence and its gaps. A page header states
date, source count, confidence, and the verification boundary — what was
observed versus what was cited — so the reader tells verified from unverified
without reconstructing the investigation.

## Negative findings and gaps

Absence is a finding, but only from a source that worked: name what was
searched, where, over what window, in what language. Record the two shapes
exactly: `CHECKED, ABSENT` (the source worked and the thing was not there)
versus `COULD NOT CHECK` (the source failed — with its error or status text —
and the question stays open). A failed lookup described as an absence is the
most common false negative; report the failure as a failure.

Every synthesis carries a Gaps section, and "insufficient data found" is a
complete entry. Date-stamp anecdotes with year and version before presenting
them as current. Numbers ship with their cuts (date, scope, source) or as a
direction and range only.

## Artifact metadata

Where an artifact may be disputed, record the full row: ID, source, type,
time range, collection method, timestamp, collector, hash, storage. The
lightweight form — source path, retrieval timestamp, SHA-256 — suffices for
ordinary pages; reach for the full row when custody matters. Record the
collection method in provenance (passive reading versus interaction), and
treat labels applied by third parties (tags, tool verdicts) as claims by their
labeller: cite who labeled, not just the label.
