# Pivots — if you found X, investigate Y

Read this once the scope note exists and you hold a seed identifier. Each pivot below has the same
four parts: **Trigger** (what finding activates it), **Steps** (with the command and what its output
looks like), **Anti-patterns** (how it goes wrong), and **Output** (the fields it must produce).

A pivot outside the written scope is a finding to report, not a workstream to start. Enumeration
yields neighbours forever; "not in the scope list" means record it and stop.

Every command below assumes Tier 0 (`python3`, `curl`, `dig`, `whois`). Run `capabilities.py`
first — anything needing a key has a documented free fallback in `collection.md`.

## Contents

- [domain → infrastructure](#domain--infrastructure)
- [email → reality](#email--reality)
- [username → identity](#username--identity)
- [phone → person](#phone--person)
- [company → registration](#company--registration)
- [wallet → entity](#wallet--entity)
- [image → origin](#image--origin)
- [document → author](#document--author)
- [breach record → every identifier it leaks](#breach-record--every-identifier-it-leaks)
- [sponsor → organisation](#sponsor--organisation)
- [person → everything else](#person--everything-else)

---

## domain → infrastructure

**Trigger.** A domain name, resolved or not.

**Steps.**

1. Resolve and record the answer. `dig +short A example.com`, `dig +short MX example.com`,
   `dig +short NS example.com`. Record the TTL and the timestamp; they matter later.
2. Registration, via RDAP rather than WHOIS where possible — WHOIS is increasingly rate-limited and
   often privacy-proxied. `curl -s https://rdap.org/domain/example.com | jq '{ldhName, status,
   events, entities: [.entities[]? | {roles, vcardArray}]}'`. Note the registrar, the creation
   date, and the last update date separately — a domain created in 2024 and updated weekly is a
   different object from one created in 2004.
3. Name servers and hosting. `dig +short NS example.com`, then resolve the registrar's own
   RDAP endpoint (`rdap.godaddy.com`, `rdap.nic.us`) for the registrar-side record, which often
   differs from the registry-side record.
4. Certificate transparency — subdomains you did not enumerate, from a log you did not guess.
   `curl -s 'https://crt.sh/?q=%25.example.com&output=json' | jq -r '.[].name_value' | sort -u`.
   The free keyless alternative is Cert Spotter:
   `curl -s 'https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true&expand=dns_names'`.
5. Subdomains by tool, if installed: `subfinder -d example.com -all -silent`. Without it, the CT
   logs above plus `gau --subs example.com` cover most of it.
6. Historical surface. Wayback CDX:
   `curl -s 'https://web.archive.org/cdx/search/cdx?url=example.com*&output=json&collapse=urlkey&fl=timestamp,original,statuscode'`.
   Subdomains that existed in 2019 and are gone now are often the interesting ones.
7. IP attribution, if you have an address: `whois <ip> | grep -iE 'orgname|netname|descr|abuse'`
   plus the RIR RDAP (`rdap.arin.net`, `rdap.db.ripe.net`, `rdap.apnic.net`).

**Anti-patterns.**

- **A shared host is not an operator.** Dozens of unrelated sites on one IP is the null hypothesis
  for any infrastructure claim, and it is right far more often than not. Check for a shared
  certificate, a shared CMS template, and a shared analytics ID before you infer anything.
- **Registration is not operation.** The registrant is often a privacy proxy, a registrar, or a
  predecessor. Cite the registrant as the registrant.
- **A subdomain from CT is not a live service.** The log records issuance, not deployment. Resolve
  it before claiming it exists.
- **Passive DNS is incomplete by nature.** Absence from a passive source is weak evidence. State
  the coverage.

**Output.** Domain, registration record with retrieval timestamp, nameservers, resolved addresses
with TTL, subdomain list with the source of each, historical snapshot range, hosting/ASN with the
RIR record as the citation, and an explicit list of what could not be checked.

## email → reality

**Trigger.** An email address from any source.

**Steps.**

1. **Three tiers, in order, and they prove different things.**
   - *Syntactic* — parse it. Proves nothing about whether the mailbox exists.
   - *Domain/MX* — `dig +short MX example.com`. An address at a domain with no MX cannot receive
     mail, which is a real finding about the domain even if not about the person.
   - *SMTP* — `RCPT TO` probe. **Interactive, frequently blocked, frequently lied to, and logged.**
     Never treat a silent `RCPT TO` as a deliverability result.
2. **Gravatar.** The service keys on the MD5 of the lowercased, trimmed address.
   `printf '%s' 'user@example.com' | tr 'A-Z' 'a-z' | md5sum` then request
   `https://www.gravatar.com/avatar/<hash>` — a returned image means the address was registered
   with Gravatar, nothing more. The associated public profile may carry a display name, a location,
   and links. That is a self-published claim by the account holder, not verified identity.
3. **Breach presence.** Where a credentialed source is available, query it; record the breach name,
   date, and the fields exposed. Without a key, say the check could not be run — do not report
   absence.
4. **Mail headers**, when you have a message. The `Received` chain gives the path; `Message-ID`
   gives the originating host; SPF/DKIM/DMARC results tell you whether the sending domain was
   authorised. A `From:` header is a self-asserted string.

**Anti-patterns.**

- **A Gravatar hit is not identity.** It proves an account exists, not who runs it, and the profile
  fields are self-published.
- **A breach hit is not proof of the person.** Shared and recycled addresses are common. Corroborate
  with a discriminator that only the subject would satisfy.
- **A deliverable address is not a person.** Never convert an address into a name without a
  separate, cited step.

**Output.** Address, validation tier reached and what each tier did and did not prove, Gravatar
result, breach matches with breach names and dates, header analysis if applicable, and the exact
lookup that could not be run.

## username → identity

**Trigger.** A handle from any source — an email local part, a forum, a breach record, a mention.

**Steps.**

1. Breadth: `sherlock handle --csv`. Existence only. Sherlock's default run covers roughly the
   highest-traffic sites and a large share of its hits are false positives from generic pages.
2. Fields: `maigret handle --json handle.json --html handle.html`. The `extracted_data` block is
   the value — profile picture URL, bio, declared location, declared name, and **explicit
   cross-links the account holder made to other accounts**. A self-declared cross-link is far
   stronger than a same-name hit.
3. Want to know *why* a hit fired: the WhatsMyName dataset behind both tools.
4. Direct lookups where they pay: GitHub
   `curl -s https://api.github.com/users/HANDLE | jq '{login,name,bio,location,company,blog,created_at,avatar_url}'`;
   Reddit `curl -s -A "osint/1.0" https://www.reddit.com/user/HANDLE/about.json`; Keybase, which
   cryptographically proves control of linked identities at proof time.
5. Reverse image search on any recovered avatar.
6. Archived versions: bios are edited. A 2019 bio that names an employer is often the most useful
   thing you will recover.

**Anti-patterns.**

- **Two accounts with the same handle are not one person.** `jsmith88` is a common pattern.
  Corroboration needs at least two of: identical avatar verified by perceptual hash rather than by
  eye, overlapping bio phrasing, account creation within a short window, mutual follows, or a
  shared breach record.
- **Do not probe at full scope unthrottled.** maigret touches ~2500 sites; that saturates a
  connection and trips abuse detection on several CDNs, and the result is a partial sweep you then
  mistake for a complete one.
- **Do not log in to view a profile.** Some platforms notify the subject that you viewed it. That
  converts passive collection into an interactive act with the subject.
- **Keybase proofs are point-in-time.** They prove control at proof time, not now.

**Output.** Handle, enumerator hits with a false-positive flag each, extracted metadata with the
self-declared cross-links marked as such, avatar inventory with hashes, archived snapshots with what
they reveal, the corroborating evidence for each claimed link, and the confidence for each
asserted identity claim.

## phone → person

**Trigger.** A phone number in E.164, ideally with country code.

**Steps.**

1. `python3 -c "import phonenumbers as p; print(p.is_valid_number(p.parse('+14155552671')))"` —
   validity only, never identity. A valid number is not a real subscriber.
2. Carrier and line type. VoIP numbers are portable and have no meaningful geographic attribution;
   a US country code on a VoIP number tells you nothing about where the holder is.
3. Messaging registration: a number registered on a platform is a registration, not a verified
   identity. Platforms do not verify names.

**Anti-patterns.**

- **A country code is not a location** when the number is VoIP or ported.
- **Registration is not identity** on any messaging platform.
- **Do not use reverse-lookup aggregators for a private individual.** They are for organisations.

**Output.** Number in E.164, validity, line type, carrier, platform registrations found, and an
explicit statement that no subscriber identity was established.

## company → registration

**Trigger.** An organisation name, from anywhere.

**Steps.**

1. **Entity resolution first.** *Until you have a registration number in a named registry, you do
   not have a subject — you have candidates.* Search the registry directly, not a name aggregator.
   For US: FEC (`docquery.fec.gov`), state Secretary of State, IRS Form 990 via ProPublica
   (`projects.propublica.org/nonprofits/api/v2/search.json?q=`), SEC EDGAR full-text.
2. Disambiguate using the discriminators in the scope note. Every near-match that fails a
   discriminator is a rejected candidate, recorded.
3. From the registration record, pivot to identifiers: registered domain, contact email, officer
   names, filing address.
4. Beneficial ownership where a jurisdiction mandates disclosure — the officers, the parent, the
   ultimate owner.

**Anti-patterns.**

- **A name match is not an entity.** Name collisions are the single most common false positive in
  company work, and the name-collision case is why the scope note demands discriminators.
- **A registered address is not an operating address.**
- **A filing is a point-in-time record.** Officers change.

**Output.** Legal name, registration number, registry and retrieval date, jurisdiction, officers
with dates, registered identifiers, ownership chain, and every rejected candidate with its reason.

## wallet → entity

**Trigger.** A blockchain address.

**Steps.**

1. Identify the chain and address type from the prefix: `1` P2PKH, `3` P2SH / wrapped SegWit,
   `bc1q` native bech32, `bc1p` Taproot, `0x` + 40 hex EVM (mixed case carries an EIP-55 checksum —
   a mixed-case address that fails the checksum is malformed, which is itself a finding).
2. First and last activity, balance, and counterparty set.
3. Interaction with labelled services. **Do not rely on a hardcoded list of exchange addresses** —
   they move, and a stale list produces a confident wrong attribution. Query a labelling source
   (a chain analytics API with a key, or an address-label service) and record its retrieval time.
   A public label database with no update date is weaker than no label at all.
4. Peel chains: a fresh address funded from an exchange, consolidations, and timing clusters.

**Anti-patterns.**

- **An exchange deposit is not a person's ownership.** It is a deposit to an exchange.
- **A transaction cluster is not an entity.** Several addresses in one transaction may be one
  person, one exchange hot wallet, or a payment splitter.
- **Funding-source labels decay.** Record the date of the label, not just the label.

**Output.** Chain, address with checksum status, activity window, labelled counterparties with the
label source and its date, cluster analysis, and — if no entity was established — that statement
plainly.

## image → origin

**Trigger.** Any image from any source.

**Steps.**

1. Extract metadata before anything else. `exiftool -a -u -g1 FILE`. Priority order, highest
   signal first: `GPSHPositioningError`, `GPSImgDirection`, `GPSDateStamp`/`GPSTimeStamp` (UTC),
   the original timestamp triplet, device make/model/**serial**, the software chain, and whether
   there is an embedded thumbnail that differs from the main image. The embedded thumbnail is
   frequently the pre-edit original — it is the most valuable field in the file.
2. Hash it: `sha256sum FILE`, recorded through `evidence.py`.
3. Reverse image search on the widest available engines — one engine's index is not "the internet".
4. Geolocate independently: terrain, signage, vegetation, sun position against the claimed time,
   weather. Chronolocate: does the claimed date fit the light, the weather, the events?
5. For video: `ffprobe -v error -show_format -show_streams FILE` for duration, codec, and
   creation time; `c2patool FILE --info` for content credentials.

**Anti-patterns.**

- **EXIF is absent from most platform uploads**, so its absence is not evidence of anything. Its
  presence is informative.
- **A timestamp that predates the camera model is not a camera timestamp.**
- **One reverse-image engine returning nothing is not absence.** Say which engines were searched.

**Output.** File hash, EXIF findings in priority order, earliest known appearance with URL and
date, geolocation reasoning and its confidence, chronolocation reasoning, and the engines searched.

## document → author

**Trigger.** A PDF, DOCX, or any file with authorship metadata.

**Steps.** `exiftool -a -u -g1 FILE` for author, creator application, and revision count. Revision
count is often the most telling field: a heavily revised document with a single stated author is
either a genuine redraft or a document assembled from several sources. Font and heading structure
give hints. Do not rely on metadata alone — it is trivially editable and often stripped.

**Anti-patterns.** **Metadata is self-asserted and trivially forged.** A stated author is a claim
by the document, cited as such, never as a fact about who wrote it.

**Output.** Stated author and application with the caveat, revision count, document creation and
modification timestamps, and the corroboration (or absence of it) from independent sources.

## breach record → every identifier it leaks

**Trigger.** Any breach corpus hit.

**Steps.** Extract every field the breach exposes, not just the obvious ones: secondary emails,
phone numbers, physical addresses, employer and job title, usernames, IP addresses, password
hashes, and past passwords. Each is a new pivot with its own scope question.

**Anti-patterns.**

- **A breach record is a claim about a record, not a fact about a person.** Corroborate the
  discriminator before acting on identity claims.
- **Data brokers resell each other.** The same record appearing in three sources is one origin.
- **Never attempt to use recovered credentials.** That is intrusion, not OSINT, and it is outside
  this skill entirely.

**Output.** Breach name, date, and verified provenance of the dataset; the fields exposed; and each
extracted identifier as a candidate pivot with its own scope status.

## sponsor → organisation

**Trigger.** An advert, a sponsorship, a named funder.

**Steps.** Ad libraries are legally mandated repositories in many jurisdictions, which makes them
the **highest-grade advertising source available** — treat them as primary records, not as leads.
Search by sponsor name; record the creative, the landing page, and the date range. Pivot to the
landing page's hosting, its analytics identifiers, and its registrant.

**Anti-patterns.**

- **A shared ad-tech vendor is not a relationship.** The same agency serving hundreds of
  advertisers is the null hypothesis.
- **A landing page's registrant is often the agency.**
- **Ad libraries lag and miss.** A creative absent from the library is not evidence it never ran.

**Output.** Advertiser as recorded by the library with retrieval date, creative and landing page,
date range, hosting and analytics identifiers, and the discriminator that distinguishes the
advertiser from its agency.

## person → everything else

**Trigger.** A name, from anywhere. The hardest pivot, because it starts with the least structured
identifier.

**Steps.**

1. **Discriminators before anything else.** Write down what would distinguish this person from
   others with the same name: employer, location, age band, role. A name alone is not a subject.
2. Entity resolution against the registries the person would appear in — corporate filings,
   professional registers, court records, and their own published pages.
3. From any identifier found — employer, handle, domain, address — run the relevant pivot above.
4. Record every rejected candidate explicitly.

**Anti-patterns.**

- **Common names generate false positives at a rate that makes unreviewed results worthless.**
  Name + employer + location is the minimum, and the rejection list is not optional.
- **Do not assemble a dossier on a private individual.** The stop conditions in the skill apply
  with full force: a private person's home, workplace, and family are not investigation targets.
  Business conduct and published professional records are.

**Output.** The discriminators used, the matches that survived them with citations, every rejected
candidate with its reason, and the identifiers found that justify the next pivot.
