# People Investigation

Build a sourced, corroborated profile of a named individual from public records, social platforms, professional networks, court and property filings, licensing boards, patents, papers and obituaries — anchoring the name to a second selector first so you never fuse two people into one dossier.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Bind the Name to a Second Selector](#step-2--bind-the-name-to-a-second-selector)
- [Step 3 — Order of Operations](#step-3--order-of-operations)
- [Step 4 — Record Provenance as You Collect](#step-4--record-provenance-as-you-collect)
- [Step 5 — Back Out When It Is a Different Person](#step-5--back-out-when-it-is-a-different-person)
- [Step 6 — Family and Associate Structure](#step-6--family-and-associate-structure)
- [Step 7 — Report](#step-7--report)
- [Key Tools](#key-tools)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

Write down, before searching: the subject, the objective, what is in bounds, what is out of bounds, and which jurisdiction's law governs you and the subject.

Built for: counterparty and investor due diligence, fraud and asset investigation, journalism, skip tracing and debt recovery, missing persons, pre-employment integrity checks on senior or fiduciary roles, and personal self-defense — running yourself to see what an attacker would find.

Out of bounds, always: establishing a private individual's home address, routine movements, children, medical status, immigration status, or sexuality for any purpose other than a documented lawful one; anything that puts you in contact with the subject; and any use a reasonable person would call surveillance. If your objective is to confront, embarrass, or reach the subject in person, stop.

**Done when** the scope note exists in the case file, names a lawful objective, and states an explicit out-of-bounds list.

## Step 2 — Bind the Name to a Second Selector

Never search on a name alone. Pick an anchor and carry it into every query.

| What you hold | First move | Why |
|---|---|---|
| Name + employer | Professional network, company bios, press releases | Employment is the strongest cheap anchor; it dates the person and gives a city |
| Name + city/region | Local records — property, court, voter file where public, local press | Geography prunes namesakes fastest |
| Name + a photo | Reverse image search, then metadata extraction | A face survives name changes and transliteration |
| Name + email or handle | Email investigation, username enumeration | Machine-unique selectors; skip disambiguation almost entirely |
| Name + approximate age | Genealogy, obituaries, licensing records | Age bands split same-name clusters cleanly |
| Name only | Stop. Go back to the requester | A bare common name is not an investigable selector |

Common-name subjects need two anchors, not one. Non-Latin-script names need the native-script spelling plus the transliterations actually used in your sources — search all of them, because registries, papers, and press each pick a different romanisation.

**Done when** you can state a discriminating test — "my subject is the one who worked at X in Y" — that you will apply to every candidate record.

## Step 3 — Order of Operations

Cheapest, highest-yield, lowest-noise first. Do not start with data brokers; they will hand you plausible wrong answers before you have a way to reject them.

1. **Structured professional record.** Professional networks, employer team pages and bios, press releases, conference programmes and speaker pages. Self-published, so accurate about role and affiliation and unreliable about achievement.
2. **Published output.** Bylines, papers, patents, standards contributions. Use search operators with `site:` and exact-phrase. Papers carry an institutional affiliation and often an ORCID, which exists specifically to solve name ambiguity; patents carry an inventor city and an assignee company.
3. **Regulated-role registers.** Licensing and professional boards publish name, licence number, jurisdiction, status, and often disciplinary history. If your subject claims a regulated role, this both confirms and dates it.
4. **Corporate record.** Company registries for directorships and shareholdings. The officer-name pivot is the highest-yield single step for anyone with business involvement.
5. **Public legal and property records.** Court dockets, judgments, insolvency, and land registers — where and only where public in that jurisdiction.
6. **Social and behavioural.** Username enumeration to enumerate accounts, then social media analysis. Deliberately late: noisiest layer, easiest to misattribute.
7. **Aggregators.** People-search sites, data brokers, last, and only for leads you then confirm against a layer above.
8. **Historical.** Wayback Machine for removed bios and old team pages — often the richest single source, because people scrub current pages and forget the archive.

**Done when** each layer has been worked or explicitly recorded as not-applicable, with a reason.

## Step 4 — Record Provenance as You Collect

Every claim gets, at capture time: the claim, the source URL, the access date, a saved copy or archive snapshot, and which anchor let you attribute it to your subject. Reconstructing citations at the end always fails — the page will have changed, and you will no longer remember why you believed record 14 was the right person.

Corroboration standard: **two independent sources per claim.** Independent means different origin, not different website. Three brokers agreeing is one source, because they buy from each other. A company bio and a press release from the same communications team is one source. A registry filing and a bylined news article are two.

**Done when** every claim in the case file carries a source, a date, and an attribution basis.

## Step 5 — Back Out When It Is a Different Person

Actively hunt the disconfirming detail. Signals you have crossed onto a namesake:
- An age or graduation year off your band by more than a few years
- A location with no plausible bridge to a known one
- A career discontinuity requiring two full-time roles at once
- A middle initial that conflicts rather than merely being absent
- A relatives cluster sharing no member with the one you already had

Do not quietly drop the record. Split the file: maintain a candidate set, and record for each candidate what would confirm or eliminate it. Fusing two people destroys the whole product, and it is invisible in the finished brief unless you tracked candidates explicitly.

**Done when** every collected record is assigned to a named candidate, and the non-subject candidates are documented rather than deleted.

## Step 6 — Family and Associate Structure

Only when the objective requires it. Obituaries name survivors with relationships and cities and are the most efficient family-structure source there is; genealogy and civil-registration indexes give births, marriages, and deaths where published; co-directorships and co-authorship give professional associates. Treat relatives as context for disambiguation, not as targets — pivoting a full investigation onto an uninvolved family member is out of bounds.

**Done when** relationships used in the brief are sourced, and no uninvolved third party has been profiled.

## Step 7 — Report

Hand off to the reporting workflow. Separate confirmed facts from inference, state the disambiguation basis up front, list the candidates you eliminated, and cut anything collected that the objective does not need.

**Done when** the brief states its confidence grade per claim and its disambiguation basis, and the surplus collection has been deleted.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| Sherlock | Username enumeration across 500+ sites | Free |
| Maigret | Username enumeration with profile content | Free |
| WhatsMyName | Username detection list (500+ sites) | Free |
| OSINT Industries | Multi-platform people search | Freemium |
| BeenVerified | Comprehensive background checks | Paid |
| Spokeo | People search aggregator | Freemium |
| OpenCorporates | Corporate registries | Free |
| EDGAR | SEC filings (US) | Free |
| Professional licensing boards | License verification | Free |
| Court records databases | Litigation history | Varies |
| Wayback Machine | Historical web content | Free |
| Google Search | Advanced search operators | Free |

## Pivots

| Selector produced | Feed into |
|---|---|
| Username or display name | Username enumeration |
| Email address | Email investigation |
| Phone number | Phone investigation |
| Photograph | Image provenance, metadata |
| Photo with a location question | Geolocation workflow |
| Company name or registry number | Company investigation |
| Personal or vanity domain | Domain investigation |
| Confirmed social accounts | Social media analysis |
| Address, relatives, prior cities | Data brokers |
| Deleted bio or old page | Archive recovery |
| Finished evidence set | Reporting |
