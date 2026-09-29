# Company Investigation

Corporate due-diligence workflow — resolve a brand or website to its registered legal entity, map group structure and beneficial ownership, profile officers and directors, enumerate the digital estate, and screen litigation, insolvency, procurement, sanctions, PEP and adverse media.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Resolve the Legal Entity First](#step-2--resolve-the-legal-entity-first)
- [Step 3 — Group Structure and Beneficial Ownership](#step-3--group-structure-and-beneficial-ownership)
- [Step 4 — People](#step-4--people)
- [Step 5 — Digital Estate](#step-5--digital-estate)
- [Step 6 — Litigation, Insolvency, Procurement, and Disclosure](#step-6--litigation-insolvency-procurement-and-disclosure)
- [Step 7 — Sanctions, PEP, and Adverse Media](#step-7--sanctions-pep-and-adverse-media)
- [Step 8 — Shell-Company Assessment](#step-8--shell-company-assessment)
- [Step 9 — Report](#step-9--report)
- [Key Tools](#key-tools)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

Write the target, the decision the work supports, the risk areas in scope, the jurisdictions involved, and what is out of bounds. Corporate research on public filings is broadly lawful and often mandatory, but two limits bite. Stay passive toward the company's own systems — reading DNS and certificate logs is OSINT, authenticating or probing is not. And named individuals inside the company are still data subjects: an officer's directorships are fair game, their family is not.

**Done when** the scope note names the decision, risk areas, and jurisdictions, and states that no interactive testing is authorised.

## Step 2 — Resolve the Legal Entity First

You are looking for a registration number in a named registry. Until you have one, you do not have a subject.

| What you hold | Route to the entity |
|---|---|
| A website | Footer, terms, and privacy policy — statutory disclosure rules in much of Europe force the legal name and number onto the site; then confirm in the registry |
| A brand or trading name | Trademark registers give the registered proprietor; national registries index trading names against the registrant |
| An invoice or contract | Company number, VAT/tax number, and registered office are usually on it; verify every one, do not trust the letterhead |
| A listed company | The securities regulator's filing system is richer than the company registry |
| A group name only | Find any one member entity, then walk the chain in both directions |

Record legal name, registration number, jurisdiction, incorporation date, status, registered office, officers, and share capital. Prefer the number over the name downstream — names change, numbers don't. Standard traps: an operating company and a holding company with near-identical names; a dissolved entity still trading under its old brand; a brand held by an IP entity in a different jurisdiction from the trading entity; a website run by a marketing entity that would not be liable for the product.

**Done when** you can name the entity that would be a party to your contract, with its registry and number, and have stated which other entities share the brand.

## Step 3 — Group Structure and Beneficial Ownership

Walk up to the ultimate parent and down to the subsidiaries. Sources: filed group accounts and subsidiary lists, listed-company exhibits enumerating subsidiaries, beneficial ownership registers, and the shared-officer and shared-address pivots. Cross-border chains are the norm, not a red flag. What matters is whether the chain ends in a named natural person or dissolves into a jurisdiction that publishes nothing. Record it as far as it goes and state where it stopped — "traced to a Cayman entity whose register is not public" is a finding, not a failure.

Beneficial ownership breaks down four predictable ways: nominees, legally recorded and economically irrelevant; trusts and foundations, which most registers do not pierce; layering, where no single register sees the whole chain; and thresholds, blind by construction to four people each holding just under the line.

**Done when** the ownership chain is drawn to its terminus or to a documented opacity point, and named beneficial owners are recorded with their source.

## Step 4 — People

Pull the officer list from the registry, not the website — the website shows who they promote, the registry shows who is legally responsible. For each person who matters to the decision run the people investigation workflow, and run the officer-name pivot for their other and prior directorships. A director with a trail of dissolved companies, or one on twenty unrelated boards, is a different risk profile from one with a coherent career.

Employee enumeration — headcount and function mix from professional networks, job postings, and the team page — tests whether the company is operationally what it claims. Platform counts include stale and duplicate profiles, exclude non-users, and skew hard by country and industry: use the shape of the workforce, not the number.

**Done when** every officer of record is listed with their other directorships checked, and the workforce claim is corroborated or flagged.

## Step 5 — Digital Estate

Run the domain investigation workflow as the entry point. What diligence wants from it, as opposed to security testing: registration dates contradicting the claimed founding date, infrastructure shared with unrelated brands under one operator, subdomains revealing unannounced products or partners, and job-posting evidence of the real stack. Check code hosting for public repositories and breach exposure for the email domain.

**Done when** the domain portfolio is enumerated, registration dates are compared to the corporate timeline, and discrepancies are written down.

## Step 6 — Litigation, Insolvency, Procurement, and Disclosure

- **Litigation.** Court dockets and judgment databases for the entity, its former names, and its subsidiaries. Read the disposition, not the filing — being sued is not liability, and a settlement tells you less than a judgment.
- **Insolvency.** Insolvency registers and statutory gazettes carry winding-up petitions, administration, and liquidation notices. Check the officers' prior companies; that is where the pattern shows.
- **Procurement.** Public tender and contract-award databases are third-party verified revenue — the strongest free evidence of real operations, and badly under-used. Debarment and exclusion lists sit alongside them.

Calibrate financial findings to the filing regime first. A listed company files audited statements, segment detail, related-party transactions, and risk factors. A small private company in most jurisdictions files an abridged, often unaudited balance sheet with no profit-and-loss and no turnover figure — so absence of revenue disclosure there is the legal norm, not evasion. What *is* meaningful: late filings, repeated auditor changes, auditor resignation, qualified opinions, charges registered against assets, and accounts that do not square with the claimed scale of operations.

**Done when** litigation, insolvency, and procurement each have a sourced finding or a recorded "searched these databases, nothing found", and financial findings are framed against what this entity type was required to disclose.

## Step 7 — Sanctions, PEP, and Adverse Media

Its own step with its own record, because it is the one a regulator or a court will ask you to evidence. Screen the entity, its parents and subsidiaries, and every named individual. Primary publishers: OFAC's sanctions list search, the EU consolidated list, the UK sanctions list, the UN consolidated list. OpenSanctions aggregates sanctions and PEP datasets across jurisdictions and is the practical start for a cross-jurisdiction sweep; OCCRP Aleph is a research index, for investigative rather than compliance screening. PEP status is a risk factor, not wrongdoing, and it extends to close associates and family — exactly where automated screening is weakest.

Adverse media means a structured search of news and regulatory announcements against the entity, its former names, and its principals, in the local language of every jurisdiction in the chain. An English-only search on a company with a foreign parent is close to worthless. Record search terms and date range so the negative is evidentially meaningful.

**Done when** every entity and person in the chain is screened against sanctions and PEP sources with sources and date recorded, and adverse media is searched in the relevant languages.

## Step 8 — Shell-Company Assessment

Score the profile; do not react to one indicator. Core cluster: an address shared by hundreds or thousands of entities; incorporation shortly before the transaction it is party to; no web presence, or a domain post-dating the pitch; nominee directors recurring across unrelated companies; no employees and no accounts showing activity; a name mimicking an established firm; bank details in a jurisdiction unconnected to the entity, the directors, or the work. Any one is common and innocent. Four together is the answer.

**Done when** the entity is scored against the catalogue with each indicator sourced, and the conclusion states which indicators drove it.

## Step 9 — Report

Hand to the reporting workflow. Lead with the entity chart — ultimate parent, intermediate holdings, contracting entity, subsidiaries, key people — then findings by risk area with source, date, and confidence. Gaps get their own section; a diligence report that hides what it could not check is worse than one that found nothing.

**Done when** the brief has an entity chart, per-risk-area findings, an explicit gaps section, and a stated overall confidence.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| OpenCorporates | Global corporate registries | Free |
| Companies House (UK) | UK company lookup and filings | Free |
| EDGAR Full Text Search | SEC filing search (US) | Free |
| OpenSanctions | Sanctions and PEP screening | Free |
| OCCRP Aleph | Investigative research index | Free |
| OpenSecrets | US political money and influence | Free |
| LittleSis | Power structure mapping | Free |
| DomainTools | Domain and IP investigation | Paid |
| WHOIS API | Domain registration data | Freemium |
| Wayback Machine | Historical web content | Free |
| Google Search | Advanced search operators | Free |

## Pivots

| Selector produced | Feed into |
|---|---|
| Registry number, officers, shareholders | Ownership investigation |
| Officer or director name | People investigation |
| Primary domain | Domain investigation |
| Officer addresses, phones, associates | Data brokers |
| Parent or subsidiary entity | Re-enter this workflow at Step 2 |
| Company email domain, public repositories | Breach investigation |
| Multi-entity ownership web | Link analysis |
| Finished evidence set | Reporting |
