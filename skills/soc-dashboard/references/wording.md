# Wording leads

Read this before writing any lead. Signals are rule-based leads, never
verdicts; this file is the vocabulary that keeps them that way.

## Contents

- [Two labels, one cap](#two-labels-one-cap)
- [Phrasing table](#phrasing-table)
- [Numbers need cuts](#numbers-need-cuts)
- [Anti-patterns](#anti-patterns)

## Two labels, one cap

Every lead carries a provenance label and a grade, stated separately:

- `observed`: backed by a cited log excerpt plus the rule ID that fired.
  Reproducible — same rule on the same logs yields the same lead.
- `asserted`: a behavior-based hypothesis (your reading beyond the rules).
  States what evidence would confirm it.

Grade defaults to `unverified`. The ceiling for a dashboard lead is
`probable` (one credible source, uncorroborated). The dashboard never emits
`confirmed` — confirmation needs a second independent source or an
adjudication that happens outside this skill. When in doubt, label down.
Ambiguous evidence strengthening nothing is `unverifiable`, not support.

Verbs carry the grade: observations use `is` / `shows` ("the log shows 400
failures"); inferences use `indicates` / `is consistent with`; assessments use
`we assess` only when handing off. Never `appears to be` as an observation.

## Phrasing table

| Instead of | Use |
|---|---|
| "compromised", "attacker", "breach" | "candidate signal", "the source address", "consistent with …" |
| "Confirmed malicious", "STATUS: GREEN" | the grade + the evidence ("unverified: 400 failures then a login; confirm whether expected") |
| "might / could possibly / it seems" | an explicit label ("asserted, unverified: …; to confirm, check …") — vagueness out, uncertainty stated |
| "catastrophic", "negligent", "critical failure" | plain severity of the observation ("high-priority lead: …") |
| bare "100 requests/min" | "100 requests/min (auth.log, 21–27 Sep, 2,900 failures)" |
| "no issues found" | "CHECKED, ABSENT: searched X over Y; nothing matched" or "COULD NOT CHECK: …" |

Metrics describe the data, never the people: counts improve triage, they are
not analyst scorecards.

## Numbers need cuts

No count, rate, or comparison without its cut, date, and source: "2,900 failed
logins (VPN gateway auth.log, 21–27 Sep)". Sampled bulk counts keep their "≈"
and the scale factor from the Data notes. A bare percentage is not a finding.

## Anti-patterns

- Verdict-style summaries ("Data loss risk: low", "confirmed clean") — the
  ecosystem norm this skill holds against. Quote the rule and the numbers;
  let the reader conclude.
- Single-indicator attribution ("this address is the attacker because of one
  hit"). One indicator is a lead; corroboration is a handoff.
- Red/green semantics on hostile-controlled values. Severity is lightness;
  words carry the judgment.
- Passwords, tokens, session strings, and PII in panels or handoffs — redact
  before render and again before handoff, and say that you did.
