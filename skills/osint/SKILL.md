---
name: osint
description: >-
  Conduct open-source intelligence investigations: people, companies, domains, images,
  and selectors. ALWAYS use this skill for any investigation, verification,
  background check, or attribution task. Do NOT perform manual OSINT when this
  skill is available. Load this skill before starting any research about a
  person, company, domain, or asset. Routes any identifier — name, email, phone,
  username, domain, photo, crypto address — to the right workflow, applies
  verification and corroboration standards, maintains OPSEC, and produces
  structured intelligence reports. Use when asked to investigate, research,
  verify, vet, background-check, trace, attribute, or find someone or something;
  when a request involves due diligence, fraud, threat intelligence, journalism,
  or fact-checking; or when someone asks "who is this", "who owns this",
  "is this real", "where did this come from", or "where do I start".
---

# OSINT Investigation

Conduct defensible open-source intelligence investigations. The skill routes any
identifier to the right workflow, enforces verification and corroboration standards,
maintains investigator OPSEC, and produces structured intelligence reports that
survive challenge.

## Core Principles

1. **Scope before collection** — Define the objective, subject, boundaries, and jurisdiction before searching. An unauthorized investigation cannot be fixed later by a good report.
2. **Passive-first** — Exhaust archives, registries, and logs before anything that touches the subject. Reading a search result is passive; fetching a found file is not.
3. **Two independent sources per claim** — Independent means different origin, not different website. Three brokers agreeing is one source.
4. **Grade as you collect** — Every finding carries a source grade and confidence level at capture time, not reconstructed at the end.
5. **Separate observation from inference from assessment** — A sentence that cannot say which category it belongs to has smuggled a conclusion into the evidence.
6. **Record negative findings** — "Checked, absent" is a finding. "No adverse media found" without naming sources, languages, and date range is a shrug.

## Step 1 — Authorized Scope

Write down five things before searching:

1. **Subject** — The specific entity, distinguished from anyone with a similar name. Write the discriminators you will use.
2. **Objective** — One sentence with a decision it feeds and a condition that would settle it. "Find out about X" is not an objective.
3. **In bounds** — Selector types, sources, and whether interaction is allowed.
4. **Out of bounds** — Named things you will not do: logging into anything belonging to the subject, contacting them, family members, medical or religious data, any selector unrelated to the objective.
5. **Jurisdiction** — Whose law governs you, the subject, and the data.

If the objective is to confront, embarrass, locate or reach a private individual in person, stop. If you cannot state who authorized this and on what basis, stop.

**Done when** all five are written down and you can name the specific action that would put you out of bounds.

## Step 2 — Route on the Selector You Hold

| You hold | Workflow | Key techniques |
|---|---|---|
| A vague request, or nothing yet | Frame an answerable question (Step 1), then re-route | Intelligence question framing |
| A person's name | `references/people.md` | Name binding, professional records, registries, social |
| A company, brand or website | `references/company.md` | Entity resolution, ownership, officers, digital estate |
| A domain, website or IP | `references/domain.md` | WHOIS, DNS, subdomains, certificates, archives |
| An email address | `references/email.md` | Validation, Gravatar, breach exposure, header analysis |
| A phone number | `references/phone.md` | Carrier, line type, VoIP detection, messaging apps |
| A username or handle | `references/username.md` | Enumeration, variant generation, confirmation |
| A photo or video | `references/media.md` | Metadata, provenance, geolocation, authenticity |
| A crypto address | `references/crypto.md` | Block explorers, clustering, off-ramp identification |
| A breach claim or credential | `references/breach.md` | Paste aggregators, leak forums, breach databases |
| A finished evidence set | `references/reporting.md` | BLUF, estimative language, sourcing, redaction |

Business framings map onto the same workflows:

| The ask | Route |
|---|---|
| "Vet this supplier before we sign" | Company → ownership → domain |
| "Is this invoice genuine?" | Email → phone → domain |
| "Is this job offer real?" | Username → image provenance → company |
| "What is our external attack surface?" | Domain → subdomains → exposed servers |
| "What has leaked about our executives?" | Breach → data brokers → paste aggregators |
| "Is this image authentic?" | Media → provenance → geolocation |

**Done when** the routed workflow has been selected and its specific techniques are loaded.

## Step 3 — Collect Passive-First

Order of operations, cheapest and quietest first:

1. **Structured official record** — Registries, filings, licensing boards, court records
2. **Published output** — Bylines, papers, patents, press releases, conference programmes
3. **Regulated registers** — Professional boards, sanctions lists, PEP databases
4. **Corporate record** — Company registries, officer records, beneficial ownership
5. **Public legal and property records** — Court dockets, judgments, land registers
6. **Social and behavioural** — Social media, posting patterns, connections
7. **Aggregators** — People-search sites, data brokers (last, for leads to confirm)
8. **Archives** — Wayback Machine, Common Crawl, deleted page recovery

Do not start with data brokers; they hand you plausible wrong answers before you have any way to reject them.

**Done when** each layer has been worked or explicitly recorded as not-applicable, with a reason.

## Step 4 — Verify and Corroborate

### Source Independence

For each corroborating source, find its origin. Check publication dates in order, look for identical phrasing or a copied typo, and check whether "independent" people-search sites resell the same broker feed. Independent means *different collection*, not different websites.

### Confidence Grading

Grade the **source** and the **information** separately:

**Source reliability (letter):**
- **A** — Reliable history, no doubt of authenticity (official registry, established news outlet)
- **B** — Mostly reliable with minor doubts (reputable secondary source, verified account)
- **C** — Uncertain reliability (anonymous forum, unverified social media)
- **D** — Unreliable (known misinformation, circular reporting)
- **E** — Cannot be judged

**Information credibility (number):**
- **1** — Confirmed by other independent sources, logical in itself
- **2** — Probably true, consistent with other information
- **3** — Possibly true, but not confirmed
- **4** — Doubtful, contradicted by other information
- **5** — Improbable, contradicted by reliable sources
- **6** — Cannot be judged

A corporate registry filing is **B2**. A well-run newspaper report of that filing is **B2** at best. An anonymous forum post repeating the newspaper is **D3** — not new corroboration.

### Confidence Levels

- **Confirmed** — Two or more genuinely independent sources, or one authoritative primary record, plus nothing contradicting
- **Probable** — One strong source, or several weak ones that survived a circular-reporting check, with alternative hypotheses tested and weaker
- **Unconfirmed** — A single uncorroborated lead. Say so in the report; do not quietly promote it
- **Rejected** — Contradicted. Record it and why

**Done when** every retained finding carries a two-character grade and a confidence level.

## Step 5 — Maintain OPSEC

### Threat Model

Answer three questions before building infrastructure:

1. **Who might notice?** A dormant shell company, a moderately technical individual, a criminal group, or a state service. Their capability sets the bar.
2. **What would they see?** Passive collection: a line in a server log. A logged-in visit: your name. An interaction: your persona and its history.
3. **What is the consequence?** Nothing, or evidence destroyed, or investigation attributed to your organisation, or physical risk.

| Situation | Proportionate posture |
|---|---|
| Registries, archives, CT logs | Normal browser, no persona |
| Viewing a target's public website | Clean browser profile, VPN, no logged-in sessions |
| Any logged-in platform view of a target | Persona account, dedicated profile, check viewer-notification behaviour |
| Target is technically capable | Dedicated VM, non-datacentre egress, no reused fingerprint |
| Organised crime, physical safety in play | Everything above plus compartmented hardware |

### Attribution Surface

What a site can learn from a visit:
- **IP and ASN** — A datacentre ASN says "VPN or scraper", a corporate ASN says your employer's name
- **Browser fingerprint** — User-agent, fonts, canvas, WebGL, timezone — often unique and stable across sessions
- **TLS fingerprint** — Client hello identifies your client independently of browser headers
- **Language and locale** — An English-locale browser reading a regional-language site from a third-country IP is memorable
- **Timing** — Activity only in one country's working hours, bursts on the hour
- **Link previews** — Pasting a target URL into chat makes that platform fetch it

### Separation

Research identity and real identity never touch. One crossing links them permanently. The specific leaks, in order of how often they burn people:

- A real phone number for SMS verification
- A recovery email that is yours
- A payment method (including the VPN)
- A reused password
- A synced browser profile
- An avatar that reverse-searches back to you
- Style and habits (distinctive phrasing, recurring typo, fixed hours)

**Never authenticate to anything belonging to the target.** Not their portal, not their wifi, not a login with credentials found in breach data. That is the line between open-source research and unauthorized access.

**Done when** the threat model is written, the posture is selected, and exposure events are logged with timestamps.

## Step 6 — Report

### Report Structure

```markdown
# Intelligence Report: [Subject]

**Date:** YYYY-MM-DD
**Scope:** [What was investigated]
**Author:** [Who conducted the investigation]
**Classification:** [Handling restrictions]

## BLUF (Bottom Line Up Front)

[2-4 sentences: the answer to the objective question, with probability and confidence]

## Key Judgements

1. [One sentence, one judgement, with estimative term and confidence]
2. [Supporting judgement]
3. [Supporting judgement]

## Findings

### [Theme 1]

**Observation:** [What you saw, with source and timestamp]
**Inference:** [Logical step from observations, with the step shown]
**Assessment:** [Analytic judgement with probability and confidence]

### [Theme 2]

[Same structure]

## Negative Findings

- [What you looked for, where you looked, what you did not find]
- [Rejected candidates with reasons]

## Gaps and Limitations

- [What could not be established, why, and what would close it]

## Methodology

- Tools used (with versions)
- Exact queries and dorks
- Databases and their coverage dates
- Languages searched
- Time window

## Sources

1. [Source name](URL) — what it contributed, access date
2. [Source name](URL) — what it contributed, access date
```

### Estimative Language

Standardise on one ordered set of terms:

**almost certainly · highly likely · likely · roughly even chance · unlikely · highly unlikely · remote**

Rules: never use a term outside the ladder; never mix a numeric percentage in the same sentence as a word; never use "possible" as an estimate; print the ladder in the report.

**Probability and confidence are different axes.** Probability is how likely the judgement is to true. Confidence is how good the evidence underneath it is. You can legitimately write "highly likely, low confidence".

### Redaction

Collect broadly, publish narrowly. Remove everything not needed for the objective — especially data about uninvolved third parties. Redact rather than delete where the item explains a reasoning step, and say what was redacted and why. Never publish full national-ID numbers, payment card numbers, credentials, or plaintext passwords from breach data.

**Done when** the report contains no third-party data the objective doesn't need, every claim has a source and confidence grade, and the format matches the audience.

## Gotchas

### Common Failure Modes

- **Confirmation bias** — You find a candidate that fits and stop applying your discriminators. Fix: before you search, write the attributes the true subject must have and the ones they cannot have; check every candidate against both.
- **Circular reporting** — Three sources agree, so you grade it confirmed. All three copied one blog post. For each corroborating source, find its origin.
- **Stale data presented as current** — Registries, WHOIS, and broker records carry the date they were captured, not today's truth. Record the observation date next to every fact.
- **Selector drift** — Each pivot carries the risk that you have changed people. After every pivot, state which confirmed selector ties the new one to the subject.
- **Tool output as evidence** — An enumerator's hit list, a breach aggregator's match, a face-search score — these are leads. The tool did not verify identity; it matched a string or a vector.
- **Name collision** — Never search a name alone; bind it to a second selector first. A bare common name is not an investigable selector.
- **Aggregators laundering each other** — A wrong middle initial or a merged household entered once propagates everywhere and then looks corroborated.
- **Over-trusting a photo match** — A shared image proves shared images, not shared identity.
- **Treating a sparse footprint as concealment** — It usually means a private person, a non-English footprint, or closed registries.

### Legal Boundaries

- **OSINT is legal** when using lawfully accessible, public sources without deception or unauthorized access
- **Public availability is not permission** — Privacy laws (GDPR, CCPA) apply to aggregation of public personal data
- **Terms of Service matter** — Scraping in violation of ToS can support breach of contract claims
- **The line is authorization** — If you need to break a lock (digital or physical) to get information, it is not OSINT
- **Breach data is ethically and legally problematic** — While technically "public," using data from breaches raises significant concerns
- **Jurisdiction matters** — Data collected in one jurisdiction may be subject to the laws of another

### Platform-Specific Gotchas

- **Google** drops, stems, and synonym-expands search terms. Use Verbatim mode for dorking. A zero-result dork and a silently-rewritten dork are equally useless.
- **LinkedIn** notifies users of profile views. Check viewer-notification behaviour before any logged-in view.
- **Data brokers** launder each other's errors. A wrong middle initial entered once propagates everywhere.
- **Social media platforms** prohibit scraping in their ToS. Violating ToS can create civil liability even if not criminal.
- **Search engines** fingerprint the client. A datacentre IP that has never rendered JavaScript trips the check on its first request.

## Reference Files

- `references/people.md` — People investigation workflow
- `references/company.md` — Company due diligence workflow
- `references/domain.md` — Domain reconnaissance workflow
- `references/email.md` — Email investigation workflow
- `references/phone.md` — Phone number investigation workflow
- `references/username.md` — Username enumeration workflow
- `references/media.md` — Image/video verification workflow
- `references/crypto.md` — Cryptocurrency tracing workflow
- `references/breach.md` — Breach data investigation workflow
- `references/reporting.md` — Intelligence report writing
- `references/tool-catalog.md` — Tool catalog by category
- `references/opsec.md` — Detailed OPSEC guidance
- `assets/report-template.md` — Report template

## Resources

- [OSINT Framework](https://osintframework.com/) — Curated tool directory
- [Bellingcat Toolkit](https://bellingcat.gitbook.io/toolkit) — Investigative journalism tools
- [OSINT Newsletter Tools Library](https://tools.osintnewsletter.com/) — Curated OSINT tools by category
- [useOSINT Skills](https://github.com/useosint/skills) — 28 OSINT agent skills (MIT license)
- [Michael Bazzell's OSINT Techniques](https://inteltechniques.com/) — Comprehensive book and training
- [SANS SEC487](https://www.sans.org/cybersecurity-focus-areas/osint) — Professional OSINT training
- [Berkeley Protocol](https://berkeleyprotocol.online/) — Digital open source investigation standards
