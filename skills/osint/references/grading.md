# Grading — deciding what is true

Read this before the first claim is written down, not after the conclusion has formed. Grading
after the fact is how a hypothesis becomes a finding without ever being tested.

## Contents

- [The five-term vocabulary](#the-five-term-vocabulary)
- [Verbs carry the grade](#verbs-carry-the-grade)
- [Source grade: reliability × credibility](#source-grade-reliability--credibility)
- [Probability is a separate axis](#probability-is-a-separate-axis)
- [Evaluating a source](#evaluating-a-source)
- [Verifying user-generated content](#verifying-user-generated-content)
- [Manipulated media](#manipulated-media)
- [Red flags that downgrade a source](#red-flags-that-downgrade-a-source)
- [The oracle hierarchy](#the-oracle-hierarchy)
- [Structured analytic techniques](#structured-analytic-techniques)
- [Anti-fabrication](#anti-fabrication)

---

## The five-term vocabulary

Fixed, because a grade that means two things is worth nothing.

| Grade | Means | You are saying |
|---|---|---|
| `confirmed` | two independent sources, or one authoritative primary record | someone can check this and get the same answer |
| `probable` | one credible source, uncorroborated | this is probably right; I have not checked it twice |
| `unverified` | observed, reliability not assessed | I saw this, and I am not claiming it is true |
| `inferred` | derived from other observations, reasoning stated | I concluded this; here is the chain |
| `refuted` | re-derived from the primary record and found wrong | I checked, and it is not this |

`inconclusive` is a separate working state: the sources disagree and you did not resolve it. It is
not a weak `unverified`; it means the investigation has an open question, and it belongs in the
report's gaps section rather than in the findings.

**`confirmed` is the expensive one.** Reaching it is the whole job. A report where everything is
`confirmed` has been graded by enthusiasm, not by evidence.

## Verbs carry the grade

The verb is the grade. This is the cheapest defence against inference laundering — restating an
inference in observation's grammar until it reads like a fact.

| Grade | Verbs |
|---|---|
| Observation | *is, are, lists, shows, states, was registered to, filed on* |
| Inference | *indicates, implies, suggests, is consistent with, is likely* |
| Assessment | *we assess, we judge, we conclude, the most likely explanation is* |

**"Appears to be" is inference wearing observation's grammar.** So is "is believed to be", "seems
to indicate", and any past-tense verb applied to a source's *claim* rather than to the fact.

Two laundering moves to name explicitly:

- **Inference laundering** — an inference restated as an observation, usually by tense change.
  "The site shares a template ID with two other organisations" (observation) becomes "the site is
  operated by the same people" (inference) becomes "all three are one entity" (assessment). Each
  step is defensible; the chain is the claim, and the chain is what must be shown.
- **Confidence inflation from volume** — twenty weak sources do not make a strong claim. Five
  blogs restating one press release is one source. Count independent *origins*, not citations.

## Source grade: reliability × credibility

Two orthogonal axes, from the Admiralty system. Both are stated; neither implies the other.

**Reliability** — how much the *source* can be trusted to be accurate:

| | |
|---|---|
| **A** | completely reliable. Issued by the authoritative body; a filed record, a court document, a platform's own served data, a certificate transparency log. |
| **B** | usually reliable. A reputable secondary that cites its primary, or a well-established outlet with a corrections policy. |
| **C** | fairly reliable. A single secondary source, an aggregator, a trade blog with a named author. |
| **D** | not usually reliable. An anonymous blog, a forum, an unattributed claim, a vendor's marketing page. |
| **E** | unreliable. Content farms, SEO farms, undated reposts, a SaaS "social sentiment" product with no methodology. |

**Credibility** — how likely the *information* itself is to be true:

| | |
|---|---|
| **1** | confirmed by other sources |
| **2** | probably true |
| **3** | possibly true |
| **4** | doubtful |
| **5** | improbable |
| **6** | cannot be judged |

Inside a single finding, use the flat form that keeps source and information distinguishable:
`A1` (an official primary record, such as a filing), `B1` (a reputable secondary citing that
filing), `B2` (a reputable news aggregator), `C3` (not reproducible, aggregator-only), `D`
(circular or republished), `E` (unusable).

The pairing has a consequence worth stating: `A6` is a perfectly reliable source carrying
information you cannot judge. `E1` is a worthless source that other sources happen to repeat.
Neither is coherent, and both happen.

## Probability is a separate axis

"You can legitimately write *highly likely, low confidence*." Probability is about the world;
confidence is about the evidence. Collapsing them is how a hedged report becomes a false one.

| Term | Range |
|---|---|
| almost certainly | 93–99 % |
| highly likely | 75–92 % |
| likely | 55–74 % |
| roughly even chance | 45–55 % |
| unlikely | 25–44 % |
| highly unlikely | 6–24 % |
| remote | 0–5 % |

Rules:

- Never use a term off the ladder.
- Never put a numeric percentage and a word in the same sentence. Pick one. `"highly likely (80 %)"`
  is not a hedge, it is a contradiction — 80 % is "likely", not "highly likely".
- Never use "possible" as an estimate. It is not on the ladder.
- **Print the ladder in the report.** A reader who does not know your vocabulary is reading
  probability words as vibes.

## Evaluating a source

**CRAAP, adapted.** Score each axis in your head; the output is a reliability letter, not a number.

- **Currency** — when published, and separately, when the underlying data dates from. They are
  usually different and the second is what matters. A 2019 registry entry may be the most recent
  available and still be stale today.
- **Relevance** — does it actually address *this* claim? An article about a company's revenue does
  not support a claim about its ownership.
- **Authority** — who published it, and what is their track record? A registry has authority by
  being the issuing body; a blog does not, however confident the author sounds.
- **Accuracy** — can it be checked elsewhere? Does it cite its own sources? Are there errors that
  would undermine the whole?
- **Purpose** — why does it exist? Informing, persuading, selling, deceiving. A press release
  omits different things than a filing, and an activist blog omits different things again.

**Lateral reading.** Verify a source by leaving its page. Novices read the "About" section and the
author bio; both can be fabricated. Instead: search for the source or author on third-party sites
— encyclopedias, established outlets, fact-check registries, correction notices, funding
disclosures. A source with no third-party footprint is low-credibility by default.

**SIFT**, for the first encounter, before investing time:

1. **Stop** — do you trust this publisher at all? If not, pause.
2. **Investigate the source** — lateral reading, above.
3. **Find better coverage** — the same claim on a stronger source. Cite that instead.
4. **Trace to the original** — a quote lifted out of context can mean the opposite of what was
   meant. Find the original publication and read around it.

## Verifying user-generated content

Photos, video, and posts need three separate checks:

- **Provenance** — who posted it first, when, from where? Find the earliest known upload with a
  reverse image search or the platform API. A re-share has lost its metadata and usually its
  context; the original is the artefact of record.
- **Originality** — is this the original, or a repost? Re-shares strip EXIF and re-caption.
- **Context** — does the scene match the caption? Geolocate and chronolocate independently
  (shadow direction, weather, vegetation, event dates, terrain) rather than believing the caption.

Passes all three → a verified primary source for *what it depicts*. Fails any one → a lead, not
evidence, and it says so in the report.

## Manipulated media

Checks available without specialist tooling:

- **EXIF** — `exiftool FILE`. Software signatures (Photoshop, GIMP), timestamps, GPS. Absent EXIF
  is itself a signal: most platforms strip it, so its presence is informative.
- **Timestamp plausibility** — capture dates that predate the camera model's release.
- **GPS vs caption** — coordinates in a different country from the claimed location.
- **Reverse image search** — an image circulating with several different captions is being used
  deceptively.
- **Shadows** — all cast in a direction consistent with one light source. Inconsistent shadows are
  a compositing tell.
- **Edges** — zoom the boundary between subject and background; compositing leaves artefacts.

For anything going into a legal or journalistic product, these checks are necessary and not
sufficient. Say so rather than implying the check settled it.

## Red flags that downgrade a source

Any one of these drops the reliability grade, and the flag is recorded in the report so the reader
can see why the source was discounted:

- **Brand-new account.** Created days or hours before the relevant post, no history. Default:
  `unverified`, a lead only.
- **No archival history.** A site claiming to be long-established with no Wayback captures before
  the relevant event.
- **Stock avatar.** Reverse image search on the profile picture returns stock photography.
- **Inconsistent metadata.** EXIF that predates the device, or GPS in the wrong country.
- **Coordinated posting.** Several accounts posting identical content within minutes, with no
  organic engagement. Treat the cluster as one low-credibility source, not several.
- **Anonymous authorship on a contested claim.** No default credibility; requires corroboration
  from a named, authoritative source.

## The oracle hierarchy

The quality of verification is bounded by the oracle chosen. Ranked by determinism first.

**Tier 1 — deterministic.** File exists with the expected bytes. Command exits with the expected
status. A network callback arrives. A state change is visible on-chain. Rated: determinism yes,
independence yes, specificity high.

**Tier 2 — attributable.** A platform's own served record. An API response from the authoritative
service. A registry record. Rated: determinism yes, independence partial.

**Tier 3 — reasoned.** A human or a model judges consistency. Rated: determinism no.

Selection order: **Determinism → Independence → Specificity → Strength → Availability.** Use the
strongest available. An oracle you cannot reach is not an oracle.

**Every oracle carries this caveat: it verifies X, not the cause.** A callback proves the payload
executed. It does not prove who sent it, that they meant to, or that nothing else did. Confirming
the effect is not attributing it.

**Verdict discipline.** Three states, and one rule that does the work: **never collapse
UNVERIFIABLE into VERIFIED.**

| Verdict | Meaning | Action |
|---|---|---|
| `confirmed` | the oracle agreed, twice, independently | report it |
| `inconclusive` | the oracle could not decide — no access, rate limit, ambiguity | re-test with a different oracle, or escalate, or report as unresolved |
| `refuted` | the oracle disagreed | report the refutation |

**Hallucinated success is the single most common verification failure.** The agent believes it
succeeded when it did not. The defence is side-effect assertions, not output matching: assert on
the *effect* (the file exists, the callback arrived, the state changed), because output can be
produced without anything happening.

**Reflection is not execution.** A payload that comes back inside a response body has been
reflected, not executed. The distinguishing test is an effect outside the response — a dialog
handler firing, a callback arriving, a file written.

## Structured analytic techniques

From Richards J. Heuer, *Psychology of Intelligence Analysis*, CIA, 1999. These exist because
anchoring, confirmation bias, availability, and premature closure are not hypothetical for an
analyst — they are the default failure mode.

### Analysis of Competing Hypotheses

Run this whenever more than one explanation fits. Attribution and "is this the same actor?"
questions always qualify.

The core move: **evidence is evaluated against hypotheses, not hypotheses against evidence.** Do
not ask "does this support my theory?" — ask "how consistent is this with *each* hypothesis?"

1. **Generate hypotheses.** Include yours and at least two others. If you cannot produce three,
   you have not thought widely enough. They must be mutually exclusive and falsifiable.
2. **Include the null hypothesis** — shared hosting, coincidence, misconfiguration, a common
   vendor, an unrelated person with a common name. Most false attributions are a null hypothesis
   that was never written down.
3. **List the evidence.** Concrete observations only. An inference is not evidence.
4. **Build the matrix.** Rate each piece against each hypothesis: `+` consistent, `-` inconsistent,
   `0` neutral, `?` unknown.
5. **Look for diagnostic evidence.** The valuable evidence is what *discriminates* between
   hypotheses. Evidence consistent with all of them decides nothing. Focus on the `-` cells: one
   inconsistent item eliminates a hypothesis, ten consistent items do not confirm one.
6. **Eliminate, do not confirm.** The survivor is the **least inconsistent** hypothesis, not the
   most consistent one. That is a weaker and more honest claim.
7. **Sensitivity check.** For each load-bearing item: if this were wrong, stale, or planted, would
   the conclusion change? If yes, that item goes in the report's limitations.
8. **Document.** The matrix ships in the methodology appendix. The executive summary references
   its result.

### Key Assumptions Check

Before finalising. List every premise the conclusion rests on, rate each, and challenge it.

| Rating | Meaning |
|---|---|
| well-grounded | supported by multiple independent sources or by the nature of the data |
| plausible | reasonable, unverified — could be wrong and you have no evidence either way |
| speculative | assumed because the analysis cannot proceed without it, not because you have evidence |

Assumptions that commonly appear and are commonly wrong: that a passive-DNS source is complete;
that a registration date reflects the original registration rather than a transfer; that a
registrant is the operator rather than a proxy or a predecessor; that a resolver's answer is
authoritative rather than cached or filtered; that a target would not leave a deliberate false
trail; that the governing jurisdiction permits the technique you just used.

**Every speculative assumption is stated in the report's limitations section.** A conclusion that
requires one is a hypothesis, whatever the matrix says.

### Devil's Advocacy

Mandatory for any attribution claim, and for anything likely to be acted on legally.

1. Restate the conclusion in one sentence.
2. Build the strongest case against it: the second-best surviving hypothesis; single-source, stale,
   or tool-limited evidence; pivots that were authorised but not run; confounding factors (shared
   hosting, CDN behaviour, domain parking, privacy proxies, common registrars); and whether the
   evidence could have been planted.
3. Rate the counter-argument **Strong / Moderate / Weak**.
4. **Strong** downgrades confidence one full level. **Moderate** goes into limitations. **Weak** is
   noted and does not move the grade.

"Grinding produces volume, not severity" applies here too: a fourth pass over the same source adds
nothing. Escalate instead.

## Anti-fabrication

1. **Do not invent an identifier.** Every IP, address, handle, date, ASN, breach name, and phone
   number comes from output you observed or a source you can name. No identifier, no claim. If you
   have not run the lookup, say you have not run it.
2. **Do not describe a tool you did not run.** If it failed, errored, was rate-limited, or was
   never attempted, that is what the report says.
3. **Cite or retract.** Every factual sentence carries a source, or it does not ship. "Common
   knowledge" is not a source. The agent's training data is not a source.
4. **A failed source is not an empty one.** A lookup that errored, was rate-limited, or needed a
   credential you lack tells you nothing about whether records exist. Reporting "nothing found"
   from such a source is the most common false negative in this work, and it looks identical to a
   real negative in the finished report.
5. **No plausible interpolation.** A missing date stays missing. A missing country code stays
   missing. Filling a small gap makes the reader trust detail you do not have.
6. **State your knowledge limits.** Domains change hands, profiles are deleted, registries are
   amended. When a claim rests on data with a known lag, disclose the lag.
7. **Probabilistic matches stay probable.** A facial-recognition or fuzzy-match result is
   `probable` until a human confirms it with a second image or a documented record — whatever
   confidence score the algorithm reports.
8. **Self-audit before finalising.** Scan every factual sentence and ask whether a source can be
   attached. If not, the sentence is cut. Record the audit and its result in the methodology.
