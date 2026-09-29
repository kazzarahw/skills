# Email Investigation

Investigate an email address — MX and syntactic validation, Gravatar lookup, corporate email-format inference, breach exposure, and full mail-header analysis covering the Received chain, Message-ID and SPF, DKIM and DMARC results.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Parse and Validate](#step-2--parse-and-validate)
- [Step 3 — Gravatar](#step-3--gravatar)
- [Step 4 — Where Is This Address Registered](#step-4--where-is-this-address-registered)
- [Step 5 — Read the Headers, If You Have the Message](#step-5--read-the-headers-if-you-have-the-message)
- [Key Tools](#key-tools)
- [Gotchas](#gotchas)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

Write down subject, objective, in-bounds selectors, out-of-bounds actions, and the governing jurisdiction. Decide in advance whether *interactive* probing — SMTP conversations, password-reset flows, signup-form enumeration — is authorized. It usually is not. Everything below is passive unless marked otherwise.

**Done when** scope is written and the interactive-probing decision is recorded.

## Step 2 — Parse and Validate

Three different things get called "email validation". They are not interchangeable.

| Method | What it proves | Cost |
|---|---|---|
| Syntactic | The string could be an address | Free, passive, proves nothing about the mailbox |
| Domain / MX | The domain exists and accepts mail | Free, passive, `dig MX example.com` |
| SMTP `RCPT TO` probe | The server claims the mailbox exists | Interactive, often blocked or lied to, and logged |

Do the first two. The third — opening an SMTP session and issuing `RCPT TO` to see whether the server accepts the recipient — is a live conversation with the subject's mail infrastructure from your IP. It gets logged, it gets your address range blocklisted, and against a **catch-all domain** it is worthless: a catch-all accepts every recipient, so every address "exists". Greylisting, tarpitting, and accept-then-bounce policies produce the same useless answer.

Then parse the local part. `first.last`, `flast`, `firstl`, `f.last` each imply a name and, on a corporate domain, a company-wide convention.

**Gmail normalisation matters.** Gmail ignores dots in the local part and everything after a `+`. `j.doe+news@gmail.com`, `jdoe@gmail.com` and `jd.oe@gmail.com` are one mailbox. Consequences: addresses that look different in two breaches may be the same person, and a `+tag` frequently names the service the address was given to, which is free intelligence about where the subject holds accounts. Not every provider behaves this way — check before assuming.

**Done when** the address is graded valid / invalid / unknown, the normalised form is recorded, and the name hypothesis is written down.

## Step 3 — Gravatar

Gravatar maps an address to a public avatar by MD5 hash of the lowercased, trimmed address. Compute the hash and request the avatar; a returned image means the address was registered with the service, and the associated public profile can carry a display name, a location, links to other accounts, and verified accounts on other platforms.

```bash
printf '%s' "jdoe@example.com" | tr 'A-Z' 'a-z' | md5sum
```

Free, passive, no key. Run the avatar through reverse image search. Treat a default fallback image as "no Gravatar", not as "address invalid".

**Done when** Gravatar presence is checked and any profile fields captured.

## Step 4 — Where Is This Address Registered

The honest position: reliable account enumeration by email is an *oracle* problem. Password-reset and signup forms disclose whether an address is registered, which is exactly why tools exist to automate them — and exactly why doing so is interactive, often against terms of service, and potentially notifying (a reset request can email the subject). Flag it, get it authorized explicitly, or don't do it.

Passive alternatives that cost you nothing:

- Search the full address in quotes, and the local part alone. Resumes, conference programmes, mailing-list archives, WHOIS history, and committed config files are full of addresses.
- Run breach investigation. Breach membership is the single best answer to "which services did this identity use", and it is retrospective rather than interactive.
- Push the local part into username enumeration as a username seed.
- Search code hosting for the address in commit metadata.

**Done when** the service list is assembled and each entry is marked passive or interactive in provenance.

## Step 5 — Read the Headers, If You Have the Message

Only applies when you legitimately possess the message. Headers are where an email stops being a selector and becomes evidence.

Read the `Received:` chain **bottom-up**: the bottom-most is the earliest hop, and the originating host is there unless the sending platform strips it. Everything below the first server you trust can be forged wholesale.

- `Message-ID` — the domain part and the ID's shape often identify the sending platform or mail client even when the visible headers are cosmetic.
- `Authentication-Results` — the receiving server's SPF, DKIM, and DMARC verdicts. A DKIM `pass` is the strongest thing in the header block: it is a cryptographic signature over content, so it survives forwarding claims.
- `X-Mailer` / `User-Agent` — client fingerprint, frequently left in place by bulk-mail tooling.
- `Return-Path` vs `From` — a mismatch is normal for mailing lists and suspicious in direct correspondence.

**Done when** the originating infrastructure is identified or explicitly stated as unrecoverable.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| `dig MX` | MX record lookup | Free |
| Epieos | Email lookup and breach checking | Free |
| GHunt | Google account investigation | Free |
| Have I Been Pwned | Breach exposure checking | Free |
| Dehashed | Breach data search | Paid |
| IntelX | Dark web and breach data search | Freemium |
| Gravatar | Avatar and profile lookup | Free |
| Google Search | Advanced search operators | Free |
| GitHub Code Search | Commit metadata search | Free |

## Gotchas

- **Catch-all domains defeat verification outright.** Everything validates. Detect one by testing an address you invented; if a random string validates, every result from that domain is meaningless.
- **Disposable and forwarding services.** Throwaway domains mean the address was never meant to persist; relay and alias services (including provider-issued private-relay addresses) mean the visible address is a wrapper around a mailbox you cannot see. Both cap how far the address can take you — recognise them early rather than burning hours.
- **Role addresses** (`info@`, `sales@`, `admin@`) belong to functions, not people. Attributing one to an individual is the most common serious error in email OSINT, and it survives into reports because it looks like a finding.
- **Inferred addresses are hypotheses.** Deriving `j.doe@company.com` from a company pattern gives a plausible address, not a real one. Label it inferred, permanently.
- **Breach data is not proof of current ownership.** Addresses get abandoned, recycled by providers, and reassigned to new staff at the same company.
- **Forwarding is indistinguishable from forgery** at a glance. Mailing lists and security gateways rewrite headers in ways that look like tampering.

## Pivots

| New selector | Goes to |
|---|---|
| Name from local part or Gravatar | People investigation |
| Local part as username | Username investigation |
| Email domain | Domain investigation |
| Employer from a corporate domain | Company investigation |
| Breach appearances | Breach investigation |
| Address in commits or config | Code investigation |
| Originating IP from headers | Infrastructure investigation |
| Gravatar or profile avatar | Image provenance |
| Address posted in dumps or channels | Leak investigation |
