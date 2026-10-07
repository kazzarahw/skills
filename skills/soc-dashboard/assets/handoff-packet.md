# Lead packet: <LEAD-01 short name>

Provenance: observed | asserted. Grade: unverified | probable (never confirmed).
Rule: <rule ID and threshold, quoted>.

## Evidence

- <log excerpt> — <timestamp UTC> — <source file, line/offset>
- <further source lines for merged hits ("also detected by" as hit-count + rules)>
- Counts with cuts: <N failed logins (auth.log, 21 Sep, 02:00–04:35 UTC)>

## What this is not

<What the dashboard did not conclude; what was not tested.>

## Confirm or kill

- Confirms it: <evidence that would upgrade this lead>.
- Kills it: <evidence that would retire it>.

## Negative findings

<Checked and absent: source, scope, window — or "none applicable".>

## Gaps

<What remains unknown. "Insufficient data found" is a complete entry.>

## Redaction

<What was redacted (passwords, tokens, PII) before filing, or "nothing
sensitive present".>

---

# Incident slice: <candidate type> <YYYY-MM-DD>

Candidate type only — never an assigned type, severity, or response time.

## Scope and window

Hosts/services observed (counts, no verdicts). First–last timestamps, UTC.

## Timeline

| Time (UTC) | Event | Source | Evidence |
|---|---|---|---|
| … | … | … | … |

## Confirm or kill

- Confirms it: …
- Kills it: …

## Handoff block

Exit criteria met (all in-scope logs assessed, every lead sourced, gaps
marked). Evidence carried (file paths, not pasted data). Next skill and why
(forensics for classification / wiki for durable leads / report for the
deliverable). Blockers, if any, recorded — never routed around.
