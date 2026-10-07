# Handoffs

Read this when reporting. A dashboard ends in packets for other skills, not in
verdicts. Three shapes, one rule: verification missing → hand off, never write
around it.

## Contents

- [Lead packet (report inputs)](#lead-packet-report-inputs)
- [Incident slice (toward forensics)](#incident-slice-toward-forensics)
- [Durable leads (toward the wiki)](#durable-leads-toward-the-wiki)
- [The handoff block](#the-handoff-block)

## Lead packet (report inputs)

The dashboard is a report *input*, never the deliverable. Hand each lead as:

- Lead ID (`LEAD-01`, own namespace — never finding-ID or CVSS fields),
  provenance label + grade, rule ID with its threshold.
- Evidence trimmed to: log excerpt + timestamp + source file (with line or
  offset where available) + counts with cuts.
- Repeated rule hits merged into one lead; list each source line ("also
  detected by" as hit-count + rule list). Group key: host + service + rule.
- What it is not: what the dashboard did not conclude, what was not tested
  (other browsers, CSV download), and the profile NOTE lines verbatim.
- Redact passwords, tokens, session strings, and PII from excerpts before
  filing, and say that you did (see `references/wording.md`).

## Incident slice (toward forensics)

When merged signals look like one incident (a burst plus a login-after-failures
from the same address), hand a slice — forensics classifies and owns it:

- Candidate incident type only (burst-then-login, spray, sweep, transfer…);
  never an assigned type, severity, or response time.
- Observed scope: affected hosts/services as seen, with counts. No
  impact or loss verdicts.
- Time window: first and last suspicious timestamps, UTC.
- Rows in `Time (UTC) | Event | Source | Evidence` order, chronological.
  Dashboard supplies the slice; reconstruction belongs to forensics.
- IOC-shaped rows as `Type | Value | Context | First-Seen` leads, with
  attribution status Known / Suspected / Unknown — a status, not a verdict.
- What would confirm or kill it, in one line each.

## Durable leads (toward the wiki)

File leads worth keeping with the wiki skill: one `claim` page per lead
(grade capped as in `references/wording.md`), a `timeline` page for the
incident window, a `synthesis` when several pages answer one question. Search
before filing; link the synthesis to its sources; never overwrite a
contradicted page. Carry the negatives, the gaps ("insufficient data found"),
and the rejected candidates — a handoff that drops them is lossy. File the
run itself: fixture, parser version, build command, counts by lead priority.

## The handoff block

Every handoff states: exit criteria met (all in-scope logs assessed, every
lead sourced, gaps marked), a one-paragraph summary, the evidence carried
(file paths, not pasted data), and which skill should take it next and why.
Record blockers instead of routing around them.
