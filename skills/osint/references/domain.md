# Domain Investigation

End-to-end passive reconnaissance for a domain, website or IP — builds an asset inventory covering registration, DNS, subdomains, infrastructure, tech stack, history and ownership without sending a single packet to the target.

## Contents
- [Ordering Logic](#ordering-logic)
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Registration and DNS Baseline](#step-2--registration-and-dns-baseline)
- [Step 3 — Expand the Name Space](#step-3--expand-the-name-space)
- [Step 4 — Resolve and Start the Inventory](#step-4--resolve-and-start-the-inventory)
- [Step 5 — Infrastructure and Services](#step-5--infrastructure-and-services)
- [Step 6 — Content, History, Code and Tech Stack](#step-6--content-history-code-and-tech-stack)
- [Step 7 — Decide Whether the Map Is Done](#step-7--decide-whether-the-map-is-done)
- [Step 8 — Hand Off the Owner](#step-8--hand-off-the-owner)
- [Step 9 — Report](#step-9--report)
- [Confidence Grading](#confidence-grading)
- [Gotchas](#gotchas)
- [Pivots](#pivots)

## Ordering Logic

Each stage feeds the next, and the sequence is cheapest-and-quietest first:

| Order | Stage | Why here |
|---|---|---|
| 1 | Registration and DNS | Defines the perimeter. Without the apex set and the registrant you do not know what is in scope |
| 2 | Name expansion | Archival sources only. Costs nothing, touches nothing, produces the candidate list everything else consumes |
| 3 | Resolution and inventory | Converts names to addresses, which is what infrastructure lookups take as input |
| 4 | Infrastructure and services | Needs stage 3's addresses. Third-party scan data only |
| 5 | Content, history, code, tech stack | Needs hostnames and org names from earlier stages as search terms, and reuses artifacts already collected |
| 6 | Owner attribution | The registrant, tenant and organization names surfaced above are the input |

Run stages 1–5 as a loop, not a line. Every stage produces new selectors that belong back at stage 1 or 2. Stop looping when the stopping rule is met.

## Step 1 — Authorized Scope

State in writing: the subject (which domains and netblocks, and which adjacent ones are explicitly excluded), the objective, the jurisdictions involved, and the passive boundary — specifically whether DNS resolution, wordlist brute-forcing and any HTTP contact with the target are permitted. If being noticed matters, set up attribution hygiene before querying anything.

**Done when** subject, objective, out-of-bounds list, jurisdiction and passive boundary are written down, and you know which of the three grey activities you may perform.

## Step 2 — Registration and DNS Baseline

Run WHOIS/RDAP on every in-scope apex. You want registrar, dates and status, nameservers, the full record set, and the mail and SaaS fingerprints TXT, MX, DKIM and CAA give up. Where registration is redacted, pull historical WHOIS in the same pass.

Key tools:
- `whois example.com` — Command-line WHOIS lookup
- `dig MX example.com` — DNS record queries
- `dig TXT example.com` — TXT records (SPF, DKIM, verification)
- `crt.sh` — Certificate Transparency search
- `DNS Dumpster` — DNS reconnaissance and subdomain mapping
- `urlscan.io` — Website scanner and analyzer
- `Host.io` — Domain data and subdomain finder

**Done when** every apex has a registration record with a retrieval timestamp, a complete record set, and a list of named third-party vendors extracted from its DNS.

## Step 3 — Expand the Name Space

Certificate Transparency and passive DNS first, because they are free, historical and invisible. Feed it the organization names from step 2 as well as the domains — a certificate-subject search finds sibling and acquired domains nobody put in the brief.

Key tools:
- `crt.sh` — Certificate Transparency log search
- `DNS Dumpster` — Subdomain enumeration
- `Subfinder` — Passive subdomain discovery
- `Amass` — In-depth attack surface mapping
- `SecurityTrails` — DNS history and passive DNS
- `FullHunt` — Attack surface intelligence

**Done when** you have a deduplicated candidate hostname list with the source and first-seen date recorded per name, and any newly discovered apex domains have been pushed back through step 2.

## Step 4 — Resolve and Start the Inventory

Classify each candidate: resolves to an address, resolves to a third-party CNAME, or does not resolve. Build the inventory now rather than at the end — retrofitting provenance onto a list you already collected is how findings lose their timestamps.

Key tools:
- `dig A example.com` — DNS resolution
- `dig CNAME example.com` — CNAME records
- `IPinfo` — IP geolocation and ASN data
- `ARIN` — IP and ASN registration lookup
- `BGP.he.net` — BGP routing information

**Done when** every candidate is in one of the three buckets with a resolution timestamp, every resolving host has an IP and an ASN, and every third-party CNAME is attributed to a named vendor.

## Step 5 — Infrastructure and Services

Run over the addresses and netblocks from step 4. Query scan platforms only — no port scanning, no service probing. Use the certificate and favicon pivots to catch hosts that share the target's infrastructure without sharing its DNS, and note anything that looks unintentionally exposed.

Key tools:
- `Shodan` — Search engine for internet-connected devices
- `Censys` — Internet-wide scanning and certificate search
- `FOFA` — Cyberspace search engine
- `Netlas` — Internet intelligence platform
- `urlscan.io` — Website behavior analysis
- `BuiltWith` — Technology stack identification
- `Wappalyzer` — Web technology profiler

**Done when** each in-scope IP has its observed ports and services with scan dates, each netblock has an owner from its RIR record, and any infrastructure found only through cert or favicon pivots has been added to the inventory and attribution-graded.

## Step 6 — Content, History, Code and Tech Stack

Three sources, in this order:

1. **Archives** for the estate as it used to be: retired hostnames, old staff pages, exposed paths, pre-CDN infrastructure references.
2. **Search engines** for what is indexed now on the hosts you found — documents, directory listings, configs, forgotten portals.
3. **Code hosting** for the org names, GitHub organization slugs, cloud tenant labels and project IDs surfaced in steps 2 to 5.

If imagery matters — a logo reused across a network of sites, a stock photo posing as an office — run reverse image search. Shared images tie sites together when DNS and registration do not.

Then assemble the tech stack from what you now hold: headers and cookies in archived copies and scan records, certificate issuers, CNAME targets, JavaScript and asset paths, CSP directives, favicon hashes, and the SaaS fingerprints from step 2. Where you need a live page, read a third-party scan of it instead of fetching it.

Key tools:
- `Wayback Machine` — Historical web content
- `Google Search` — Advanced search operators
- `GitHub Code Search` — Public repository search
- `grep.app` — Code search across hosts
- `Grayhat Warfare` — Open cloud storage buckets
- `ExifTool` — Metadata extraction

**Done when** archived and indexed content is reviewed for the top-priority hostnames, code exposure is documented or ruled out, new hostnames have gone back through step 4, and the stack is documented per host with the artifact each conclusion rests on and versions marked claimed rather than verified.

## Step 7 — Decide Whether the Map Is Done

Completeness is a judgement, so make it against criteria:

- Two consecutive new sources produced no new assets. Saturation, not exhaustion, is the signal.
- Every discovered name is resolved or classified, and every resolving host has an owner and an attribution grade.
- Naming conventions have no unexplained gaps: if `web01` and `web03` are in the inventory, you have accounted for `web02`.
- Every named vendor and tenant from step 2 has yielded assets or been ruled out.
- The objective from step 1 can be answered from the inventory.

A failing criterion tells you exactly which stage to re-enter.

**Done when** all five pass, or the remaining gaps are written up as stated limitations rather than left implicit.

## Step 8 — Hand Off the Owner

If the registrant, certificate subject, RIR reassignment or tenant label resolves to a legal entity rather than an individual, the domain work is finished and a corporate investigation starts: hand the entity name and jurisdiction to the company investigation workflow, take registry and beneficial-ownership questions to the ownership workflow, and send recovered emails to the email investigation workflow. Do not attempt corporate structure from DNS artifacts — DNS shows operators, not shareholders.

**Done when** every owner-side selector is routed to the right workflow or recorded as a dead end with the reason.

## Step 9 — Report

Run the reporting workflow. Lead with the asset inventory, then the attribution chain, then anything that appears unintentionally exposed, then the limitations from step 7. **Done when** every claim traces to an inventory row with a source and timestamp, and every finding carries a confidence grade.

## Confidence Grading

Grade the **inventory** and the **attribution** separately. A host can be a confirmed live service and an unconfirmed asset of your target at once, and conflating the two is the most common reporting error in domain recon.

- **Confirmed asset** — under a domain whose registration you verified, or on a netblock reassigned to the target by name, or serving a certificate the target demonstrably controls, and corroborated by a second independent source.
- **Probable asset** — one strong infrastructure fingerprint (shared DKIM key, same mail tenant label, same provider-assigned nameserver pair, distinctive favicon or body string) with nothing contradicting it.
- **Unconfirmed** — shared-hosting or CDN addresses, bundled-certificate names, `org:`-only attribution, or an aggregator result whose underlying record you have not seen.

## Gotchas

- **Scope creep through pivots.** Enumeration produces sibling domains endlessly and each looks like the next target. If it is not in the step 1 subject list it is a finding to report, not a workstream to start.
- **Silent drift into active.** Resolution, brute-forcing and HTTP probing sit on a spectrum, and tools blur it — passive collectors have active modes one flag away, and one careless flag ends the passive claim for the engagement.
- **Inventory without attribution.** Shared hosting, CDN addresses and bundled certs attach assets to your target that are not the target's, and an ungraded inventory row is a liability. Relatedly, a vulnerable SaaS tenant the target merely uses is a supply-chain finding and must be phrased as one.
- **Stale data presented as current.** Archives, CT and scan records are all historical, and undated findings are not findings.
- **Stopping at the first quiet moment.** No new results usually means one source saturated, not the estate mapped — which is what step 7 catches.
- **Over-collection.** Staff names from archived pages and SNMP contacts are personal data. Collect what the objective needs, nothing more.

## Pivots

| Selector | Goes to |
|---|---|
| Legal entity, group name, jurisdiction | Company investigation, ownership investigation |
| Emails and phone numbers | Email investigation, phone investigation |
| Named employees from archives or metadata | People investigation |
| Developer handles from repositories | Username investigation |
| Documents pulled from the estate | Metadata investigation |
| Breach exposure for the domain's mailboxes | Breach investigation |
| The whole asset and entity set, for structure | Link analysis |
