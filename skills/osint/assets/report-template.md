# {{TITLE}}

Date: {{DATE}}
Scope: {{SCOPE}}
Author: {{AUTHOR}}
Classification: {{CLASSIFICATION}}

<!-- Classification takes one of: UNCLASSIFIED // OPEN // CONFIDENTIAL // RESTRICTED. The header
     block is written once, by hand, and never regenerated from memory. -->

## BLUF

{{BLUF}}

Three to five sentences: the answer to the question the objective asked, the confidence behind
it, and the single fact that most changes the reader's action. Nothing here may be absent from the
sections below.

## Key Judgements

{{KEY_JUDGEMENTS}}

One bullet per judgement. Each bullet carries the judgement, then its probability, then the
source reliability grade, written as two separate things: "highly likely, low confidence" is a
legitimate pairing. Every bullet resolves to at least one numbered source and one raw artefact.

Probability ladder, used verbatim and never reworded:

| Probability | Numeric range |
|---|---|
| almost certainly | 93-99% |
| highly likely | 75-92% |
| likely | 55-74% |
| roughly even chance | 45-55% |
| unlikely | 25-44% |
| highly unlikely | 6-24% |
| remote | 0-5% |

A claim carries either a rung from this ladder or no probability at all. Never a number alone, and
never "possible" as an estimate.

## Findings by theme

{{FINDINGS}}

Organised by subject, not by source. A finding earns a place when it resolves or moves an
objective, or when it is the best available answer to the discriminator in the scope note.
Verbs distinguish the level of support: observation (is, lists, shows), inference (indicates,
implies), assessment (we assess, we judge). Each finding cites its source numbers and its raw
artefact paths.

## Negative findings

{{NEGATIVE_FINDINGS}}

The most useful part of this report, and the first thing a reader checks. Each entry names what
was searched, where, in what language, over what window, and what the search returned. A lookup
that failed is recorded as a failure with its status code or error text, never as an absence of
results; `CHECKED, ABSENT` and `COULD NOT CHECK` are different findings and are never merged.

## Rejected candidates

{{REJECTED_CANDIDATES}}

Every candidate entity or attribution that was considered and set aside, with the single piece
of evidence that killed it. A candidate is recorded here rather than dropped, so that the next
investigation does not re-derive it.

## Gaps and limitations

{{GAPS}}

What this investigation could not see: paywalls, deleted pages, languages not searched, archives
not reachable, sources that failed. Each gap states the finding it could have changed. A reader
must be able to tell what the report is not entitled to claim.

## Methodology

{{METHODOLOGY}}

The pivots run, the tools used, and the fallback taken when a tool was absent. Every retrieved
payload is hashed into the manifest and every claim resolves to a raw path. Where a source's
answer depends on the oracle behind it, state what the oracle verifies and that it does not
verify cause.

## Sources

{{SOURCES}}

| # | URL | Retrieval UTC | Grade |
|---|---|---|---|
| 1 | | | |

Grades are source reliability A-E, assigned per source: A is the primary record, E is an
undated unattributed repost. Every claim above cites numbers from this table; a claim citing
nothing here did not happen.

## Errors this investigation made, and how they were caught

{{ERRORS}}

The appendix of record. Each entry names the error, the positive control that exposed it, and
the correction. An investigation that reports no errors has not checked. This section is required
and is not optional prose.