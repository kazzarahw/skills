# Phone Number Investigation

Investigate a phone number — E.164 normalisation, carrier and line-type identification, VoIP and burner detection, messaging-app registration checks, and reverse lookup.

## Contents
- [Step 1 — Authorized Scope](#step-1--authorized-scope)
- [Step 2 — Normalise to E.164](#step-2--normalise-to-e164)
- [Step 3 — Carrier and Line Type](#step-3--carrier-and-line-type)
- [Step 4 — VoIP and Burner Detection](#step-4--voip-and-burner-detection)
- [Step 5 — Messaging App Registration](#step-5--messaging-app-registration)
- [Step 6 — Reverse Lookup](#step-6--reverse-lookup)
- [Key Tools](#key-tools)
- [Gotchas](#gotchas)
- [Pivots](#pivots)

## Step 1 — Authorized Scope

Write down subject, objective, in-bounds selectors, out-of-bounds actions, and the governing jurisdiction. Phone numbers are personal data in most jurisdictions. In the EU and UK, a phone number is personal data on its own — collect only what the objective needs, store it encrypted, and set a deletion date.

**Done when** scope is written and the lawful basis is recorded.

## Step 2 — Normalise to E.164

Convert the number to E.164 format: `+` followed by country code and national significant number, with no spaces, dashes, or parentheses. Use `libphonenumber` (available as a Python library, JavaScript library, or command-line tool) to parse and validate.

```bash
# Python
pip install phonenumbers
python3 -c "import phonenumbers; print(phonenumbers.format_number(phonenumbers.parse('+14155552671', 'US'), phonenumbers.PhoneNumberFormat.E164))"
```

**Done when** the number is in E.164 format and its validity is confirmed.

## Step 3 — Carrier and Line Type

Identify the carrier (mobile network operator) and line type (mobile, landline, VoIP). This tells you a lot about the number's nature:

- **Mobile** — Assigned to a person, can receive SMS
- **Landline** — Assigned to a location, often a business or residence
- **VoIP** — Internet-based, can be anywhere, often used for burners

Key tools:
- `libphonenumber` — Carrier and line type identification
- `Numverify` — Phone number validation and carrier lookup (freemium)
- `Truecaller` — Reverse phone lookup (freemium)
- `Sync.me` — Reverse phone lookup (freemium)
- `Phunter` — Phone number OSINT and validation (free)

**Done when** the carrier and line type are identified, or explicitly stated as unidentifiable.

## Step 4 — VoIP and Burner Detection

VoIP numbers are often used as burners because they can be created and discarded easily. Signs of a VoIP/burner number:
- Carrier is a VoIP provider (Twilio, Google Voice, etc.)
- Number was recently assigned
- Number has no social media presence
- Number is associated with multiple identities

Key tools:
- `libphonenumber` — Line type identification
- `Truecaller` — Reputation and spam detection
- `Sync.me` — Reputation and spam detection
- `Whocalld` — Reverse phone lookup

**Done when** the number is graded as mobile, landline, or VoIP, with confidence.

## Step 5 — Messaging App Registration

Check if the number is registered on messaging apps. This can reveal associated accounts and identities.

Key tools:
- `Telegram Phone Number Checker` — Checks if a number is on Telegram (free)
- `WhatsApp` — Check if a number is registered (manual)
- `Signal` — Check if a number is registered (manual)

**Done when** messaging app registration is checked for the major platforms.

## Step 6 — Reverse Lookup

Search for the number in public sources to find associated names, addresses, and accounts.

Key tools:
- `Truecaller` — Reverse phone lookup (freemium)
- `Sync.me` — Reverse phone lookup (freemium)
- `Phunter` — Reverse phone lookup (free)
- `Google Search` — Search the number in quotes (free)
- `Bing` — Search the number in quotes (free)
- `Yandex` — Search the number in quotes (free)

**Done when** reverse lookup is completed and associated identities are recorded with sources.

## Key Tools

| Tool | Purpose | Cost |
|---|---|---|
| `libphonenumber` | Phone number parsing and validation | Free |
| `Numverify` | Carrier and line type lookup | Freemium |
| `Truecaller` | Reverse phone lookup | Freemium |
| `Sync.me` | Reverse phone lookup | Freemium |
| `Phunter` | Phone number OSINT | Free |
| `Telegram Phone Number Checker` | Telegram registration check | Free |
| `Google Search` | Web search | Free |
| `Bing` | Web search | Free |
| `Yandex` | Web search | Free |

## Gotchas

- **Phone numbers are personal data.** In the EU and UK, a phone number is personal data on its own. Collect only what the objective needs, store it encrypted, and set a deletion date.
- **VoIP numbers can be anywhere.** A VoIP number with a US country code can be operated from anywhere in the line. Do not assume geographic location from the country code.
- **Burner numbers are common.** VoIP numbers are often used as burners because they can be created and discarded easily. A number with no social media presence and a recent assignment date is likely a burner.
- **Reverse lookup is not definitive.** Reverse phone lookup services aggregate data from many sources, and the data can be outdated or incorrect. Always corroborate with a second source.
- **Messaging app registration is not proof of identity.** A number can be registered on a messaging app without the owner's knowledge (e.g., someone else entered the number). Corroborate with other evidence.

## Pivots

| New selector | Goes to |
|---|---|
| Associated name | People investigation |
| Associated address | People investigation |
| Associated email | Email investigation |
| Associated username | Username investigation |
| Associated social media | Social media investigation |
| Associated company | Company investigation |
