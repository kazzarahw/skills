# Breach Investigation

Find leaked or mentioned selectors circulating in pastes, leak forums, Telegram channels and dump markets, and judge whether a claimed leak is genuine or a recycled combolist.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Check Known Breach Databases](#step-2--check-known-breach-databases)
- [Step 3 — Search Paste Aggregators](#step-3--search-paste-aggregators)
- [Step 4 — Search Leak Forums and Markets](#step-4--search-leak-forums-and-markets)
- [Step 5 — Judge Whether the Leak Is Genuine](#step-5--judge-whether-the-leak-is-genuine)
- [Step 6 — Report](#step-6--report)
- [Key Tools](#key-tools)
- [Gotchas](#gotchas)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

Write down subject, objective, in-bounds selectors, out-of-bounds actions, and the governing jurisdiction. Breach data is among the most sensitive categories of personal data. In the EU and UK, processing breach data requires a lawful basis, and the data subject's rights apply regardless of how the data was obtained. In the US, using breach data for employment, tenancy, insurance, or credit decisions outside a regulated consumer reporting agency is a compliance violation however public the data feels.

**Done when** scope is written and the lawful basis is recorded.

## Step 2 — Check Known Breach Databases

Start with the established breach databases. These aggregate known breaches and allow you to check if an email, username, or phone number has been exposed.

Key tools:
- `Have I Been Pwned` — Email breach checking (free for basic searches; API requires subscription)
- `Dehashed` — Breach data search (paid)
- `IntelX` — Dark web and breach data search (freemium)
- `LeakCheck` — Breach data search (freemium)
- `BreachDirectory` — Breach data search (free)
- `Scylla.sh` — Breach data search (free)
- `Snusbase` — Breach data search (paid)
- `Hudson Rock` — Infostealer and malware intelligence (freemium)

**Done when** the selector is checked against at least three independent breach databases.

## Step 3 — Search Paste Aggregators

Paste sites are where breach data is often first shared. Search for the selector on these platforms.

Key tools:
- `Pastebin` — Paste aggregator (free)
- `Ghostbin` — Paste aggregator (free)
- `PrivateBin` — Paste aggregator (free)
- `0x0.st` — File and paste sharing (free)
- `Transfer.sh` — File sharing (free)

**Done when** paste aggregators are searched and results are recorded.

## Step 4 — Search Leak Forums and Markets

Leak forums and markets are where breach data is traded. Accessing these is generally legal (they are publicly available), but interacting with illegal marketplaces or accessing illegal content is not.

Key tools:
- `Ahmia` — Onion search engine (free)
- `DarkSearch` — Dark web search engine (free)
- `OnionLand Search` — Dark web search engine (free)
- `Tor` — Anonymous browsing (free)

**Done when** leak forums are searched and results are recorded.

## Step 5 — Judge Whether the Leak Is Genuine

Not all leaks are genuine. Signs of a genuine leak:
- The data is from a known, verifiable breach
- The data is consistent with other known breaches
- The data is not a recycled combolist
- The data has not been publicly available for a long time

Signs of a fake or recycled leak:
- The data is a combolist (a list of credentials compiled from multiple sources)
- The data has been publicly available for a long time
- The data is inconsistent with other known breaches
- The data is from an unknown or unverifiable source

**Done when** the leak is graded as genuine, fake, or unverifiable, with the evidence written next to it.

## Step 6 — Report

Run the reporting workflow. State what was found, where it was found, and the confidence grade. Do not publish full credentials or personal data from breach data; reference them by type and partial value.

**Done when** the report states what was found, where, and the confidence grade, and no full credentials or personal data are published.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| Have I Been Pwned | Email breach checking | Free (basic) |
| Dehashed | Breach data search | Paid |
| IntelX | Dark web and breach data search | Freemium |
| LeakCheck | Breach data search | Freemium |
| BreachDirectory | Breach data search | Free |
| Scylla.sh | Breach data search | Free |
| Snusbase | Breach data search | Paid |
| Hudson Rock | Infostealer intelligence | Freemium |
| Pastebin | Paste aggregator | Free |
| Ghostbin | Paste aggregator | Free |
| Ahmia | Onion search engine | Free |
| DarkSearch | Dark web search engine | Free |
| Tor | Anonymous browsing | Free |

## Gotchas

- **Breach data is personal data.** In the EU and UK, processing breach data requires a lawful basis, and the data subject's rights apply regardless of how the data was obtained. In the US, using breach data for employment, tenancy, insurance, or credit decisions outside a regulated consumer reporting agency is a compliance violation.
- **Combolists are not breaches.** A combolist is a list of credentials compiled from multiple sources. It is not a breach, and it is not evidence of a breach. Do not treat a combolist as a breach.
- **Recycled leaks are common.** Many "new" leaks are recycled combolist data that has been publicly available for a long time. Check the publication date and compare with known breaches.
- **Do not publish full credentials.** Publishing full credentials or personal data from breach data is unethical and potentially illegal. Reference them by type and partial value.
- **Do not interact with illegal marketplaces.** Accessing dark web content is generally legal (it is publicly available), but interacting with illegal marketplaces or accessing illegal content is not.
- **Breach data is not proof of current ownership.** Addresses get abandoned, recycled by providers, and reassigned to new staff at the same company.

## Pivots

| New selector | Goes to |
|---|---|
| Email address | Email investigation |
| Username | Username investigation |
| Phone number | Phone investigation |
| Password hash | Credential investigation |
| Domain | Domain investigation |
| Company name | Company investigation |
