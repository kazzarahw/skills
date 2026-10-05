# Reporting — the product

Open this when producing the intelligence product. The report is not a summary of the work; it is
an argument that a reader can check. Its job is to let someone pick any sentence, follow the
citation, and disagree with it on the evidence.

## Contents

- [The shape of the product](#the-shape-of-the-product)
- [Negative findings](#negative-findings)
- [Rejected candidates](#rejected-candidates)
- [Checked, absent vs could not check](#checked-absent-vs-could-not-check)
- [Methodology](#methodology)
- [Errors this investigation made](#errors-this-investigation-made)
- [Audiences](#audiences)
- [What sinks a report](#what-sinks-a-report)
- [Template tokens](#template-tokens)

---

## The shape of the product

Ten sections, in this order. Two of them are the ones people skip and should not.

**Header.** Date, Scope, Author, Classification. The scope line restates what was in bounds, so a
reader who receives this months later knows what it was about.

**BLUF.** Roughly thirty lines. Bottom line up front. Every claim carries its grade and its basis
in the same line: *"The domain has been registered to the same committee since 2023
(`confirmed`, FEC filing `C00634261`, retrieved 2026-10-04)."* No claim appears here that is not
developed below.

**Key judgements.** A short numbered list. Each judgement states its probability *and* its
confidence, separately, and names its scope. "Highly likely, low confidence" is a legitimate and
often correct thing to write.

**Findings by theme.** Grouped by what the reader wants to know, not by which tool produced the
data. Each claim in its graded form with its citations.

**Negative findings.** See below.

**Rejected candidates.** See below.

**Gaps and limitations.** Numbered. Each gap either names its resolution condition and, where one
exists, the date by which it will be known — *"the Q3 filing is due 2026-10-15"* — or states that
nothing will close it.

**Methodology.** What was run, with versions and dates. What was graded how. Which positive
controls were applied. Which credentials arrived late and what they were deliberately not used for.

**Sources.** Numbered. URL, retrieval timestamp in UTC, grade, and what each source contributed.

**Errors this investigation made, and how they were caught.** See below.

## Negative findings

**The most useful part of most reports, and the part most often left out.** A reader's decision
depends far more on what is *absent* than on what is present, because presence is what you went
looking for.

Each negative finding names:

- **what** was searched for;
- **where** — which sources, which endpoints, which platforms;
- **in what language** — non-English sources are the most common blind spot in this work;
- **over what window** — date range, and whether the archive coverage for that window is known to
  be complete or merely attempted.

Format: *"No corporate registry record for the operating entity. Searched: SEC EDGAR full-text,
state SOS for VA and DE, OpenCorporates (English only). Window: 2015-01-01 to 2026-10-04. Archive
coverage for the state SOS index is incomplete for 2020–2021, so absence there is weak evidence."*

Without the coverage caveat, the negative finding is itself an ungraded claim.

## Rejected candidates

Every near-match that was examined and discarded, recorded rather than silently dropped. This is
what stops the next investigation — and the next reader — from re-running a dead end, and it is
what distinguishes an investigation from a search.

Format: *candidate, why it was rejected, what would revive it.* For entity work the rejection
reason is usually a discriminator failure: a registration number, an address, a role, a date.

The rule from the scope note applies here too — until a registration number in a named registry
matches, you do not have a subject, and you have candidates.

## Checked, absent vs could not check

**The distinction the report must not blur.** These are different results and they lead to
opposite conclusions:

| | Meaning |
|---|---|
| `CHECKED, ABSENT` | the source was queried successfully and returned no record. A finding. |
| `COULD NOT CHECK` | the source failed, was rate-limited, needed a credential, was blocked, or was never queried. Not a finding. |

Collapsing them produces a report that asserts negatives nobody established, and it is
indistinguishable from a real negative once it ships. If a whole class of check was blocked, say
so once, prominently, and carry the consequence into the limitations.

## Methodology

Enough for a competent reader to repeat the work:

- the tools and versions, and the date the work was done;
- the grading scheme and how it was applied;
- bulk classification: if claims were classified in bulk, the classifier and how it was checked;
- **positive controls** — for each, what error it caught. *"A known-false lookup was run against the
  same endpoint and returned the known-false answer, confirming the query was not silently
  returning empty for everyone."* A surprising negative with no positive control is the thing to
  worry about: a claim about a system needs a case where the effect appears *and* a case where it
  does not, or you have measured nothing.
- late-arriving credentials and what they were **not** used for.

## Errors this investigation made

A required appendix, not a disclaimer. Each entry: what went wrong, how it was caught, what changed.

The entries that make a report trustworthy are the ones where a claim was wrong and got fixed —
the wrong payee, the misattributed domain, the certificate whose dates made the story impossible.
A report with no errors section, on a real investigation, is either lucky or not reporting.

A positive control that caught an error goes here too, which is why the two sections overlap.

## Audiences

Same evidence, different cut. Pick one; do not write all four into one document.

| Audience | Shape |
|---|---|
| **Client / decision-maker** | One page, BLUF only. No tool names in the body. Judgements with probability and confidence. What you want them to do. |
| **Incident responder** | Machine-usable indicator table: indicator, type, first seen, last seen, confidence, source. Minimal prose. |
| **Legal** | Observation-only body — what is recorded, not what it implies. Chain of custody and a hash per exhibit. Nothing redacted without a log entry saying what and why. |
| **Internal handover** | Link graph, every dead end, every open question, and the next actions. Assumes the reader picks this up cold. |

## What sinks a report

- **False precision.** A date you inferred, a count you rounded, a number with no unit. Leave the
  gap visible instead.
- **Probability and confidence merged.** "Probably certain" is not a grade.
- **A load-bearing adverse fact buried.** If the strongest evidence contradicts the conclusion,
  it goes in the BLUF, not in a footnote after three qualifications.
- **"It cannot be ruled out that."** True of everything. If that is the strength of your evidence,
  say the claim is not supported.
- **A completeness claim.** "No other exposure was found" is a claim about the whole world. Write
  what was covered and what was not, and let the reader weigh it.
- **Tool names as evidence.** The reader needs the source and the retrieval time, not which CLI
  produced it.
- **Numbers without cuts.** No funding figure, headcount, or traffic number without a date and a
  source. Give direction and range where the precision is not available.

## Template tokens

`scripts/report.py` substitutes exactly these and nothing else. `assets/report-template.md` is the
input; the section order above is the contract.

| Token | Section |
|---|---|
| `{{TITLE}}` | product name |
| `{{DATE}}` | date of the report |
| `{{SCOPE}}` | one-line scope restated from `scope.md` |
| `{{AUTHOR}}` | author |
| `{{CLASSIFICATION}}` | classification marking |
| `{{BLUF}}` | bottom line up front |
| `{{KEY_JUDGEMENTS}}` | numbered judgements |
| `{{FINDINGS}}` | findings by theme |
| `{{NEGATIVE_FINDINGS}}` | negative findings — `--strict` fails when empty |
| `{{REJECTED_CANDIDATES}}` | rejected candidates |
| `{{GAPS}}` | gaps and limitations |
| `{{METHODOLOGY}}` | methodology |
| `{{SOURCES}}` | numbered sources table |
| `{{ERRORS}}` | errors this investigation made — `--strict` fails when empty |

The probability ladder is printed inside the template body, not substituted:

```
almost certainly 93-99% | highly likely 75-92% | likely 55-74% | roughly even chance 45-55% |
unlikely 25-44% | highly unlikely 6-24% | remote 0-5%
```
