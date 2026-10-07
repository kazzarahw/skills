---
name: soc-dashboard
description: >-
  Builds a single-file offline HTML security dashboard from log or alert data
  (Suricata, Zeek, auth.log, Windows events, CEF, JSON/CSV exports) with
  cross-filtering and rule-based leads. Use for SOC dashboards, security
  analytics, threat-hunting views, or eyeballing failed logins, sprays, scans,
  beacons, alerts. Leads are never verdicts: conclusions belong in forensics,
  the deliverable in a report, durable findings in a wiki. Not for live SIEM,
  geo maps, or non-security BI charts.
license: Apache-2.0
compatibility: >-
  Python 3.8+ (standard library only) to build; Chromium or Chrome on PATH for
  verification; viewers need a 2023+ browser. No network access anywhere in the
  pipeline.
---

# SOC Dashboard

Turn the user's real security data into one offline HTML file: a single ink on
paper, hairline panels, tracked-caps labels, tall numerals, a dot-matrix hour
map. The bundled scripts do parsing, signal detection, packing and
verification. Your job is the judgment around them: what story the data tells,
which panels earn a place, how findings are worded, and where each lead goes
next.

`<skill-dir>` is this folder. Run commands from the user's data folder and
write outputs there, never inside the skill.

## Workflow

1. **Profile the data.** `python3 <skill-dir>/scripts/soc_dash.py profile FILE...`
   Done when you can say what the data is (alerts, auth, flows, mixed), its
   time window, which fields are populated, and which assumptions the NOTE
   lines state. Quote the NOTE lines (assumed year or zone, sampling, omitted
   lines) into your report later — they are load-bearing caveats, not
   diagnostics. If it parses nothing (exit 1) or coverage looks wrong, read
   `references/data-sources.md`. Fixes: `--format`; syslog `--year`/`--tz`;
   generic JSON/CSV `--map CANON=field` and `--sev-scale`.
2. **Decide the story.** Name the hero dimension (severity for alerts, outcome
   for auth, bytes for flows) and the three questions a reader should answer
   in ten seconds. `profile --json` returns `default_config`, which is already
   a valid `--config` file. When its panels answer your three questions, build
   with the defaults; write a config only to override (`references/panels.md`
   has the schema). Aim for 8-11 panels. A panel that cannot compute what you
   asked becomes a Note documenting the blocker — never substitute a different
   quantity, even disclosed.
3. **Build.** `python3 <skill-dir>/scripts/soc_dash.py build FILE... -o <data-dir>/dashboard.html --title "<specific title>" [--config cfg.json] [--accent '#0000f2']`
   The default title is derived from the file name, so always pass a real one
   ("VPN gateway auth, 21-27 Sep"). Files of different formats merge onto one
   timeline. `--raw none` leaves original log lines out when the user is wary
   of embedding them; state the raw-budget choice in your report (auto keeps
   alert/auth lines while they fit 24 MB).
4. **Verify, then look.** `python3 <skill-dir>/scripts/verify.py <data-dir>/dashboard.html`
   It checks readiness, console errors, CSP, external URLs, hash filters, and
   clicks through signals, filters, search, the drawer and brush-zoom (exit 1
   = a check failed, 2 = no Chromium). Then open the two PNGs it writes and
   inspect them. Fixes: an empty panel usually has a `where` that matches
   nothing (check it in the config); a clipped label needs a shorter panel
   title. Done when every check passes and the screenshots look right. Without
   Chromium, say the render was not checked.
5. **Report and hand off.** Give the file path, what it shows, and the two or
   three leads worth acting on, each with its evidence (counts with cuts,
   times, addresses). Merge signals that describe one incident (a burst and a
   login-after-failures from the same address are one lead). Add the caveats
   that apply: the profile's NOTE lines (assumed year or zone, sampling,
   omitted log lines) and what was not tested (other browsers, the CSV
   download). Delete the PNGs unless the user wants them. Then file each lead
   where it belongs — durable leads to the wiki, candidate incidents toward
   forensics, the numbers as report inputs. Open `assets/handoff-packet.md`
   before composing a packet or slice, and follow `references/handoffs.md`
   for the three shapes.

## Wording findings

Signals are rule-based leads, not verdicts. Say "consistent with a successful
guess" and "confirm whether this login was expected", never "compromised" or
"attacker". Periodic traffic also matches updaters, monitoring and NTP, so
name the benign explanation beside the suspicious one. Quote the rule and the
numbers; each signal's Rule line lets the user audit it. Label anything you
noticed beyond the rules as your own reading. Read `references/wording.md`
before writing any lead: it holds the lead vocabulary
(`observed`/`asserted`, `unverified` default, `probable` at most, never
`confirmed`), the phrasing table, and the anti-patterns.

## Gotchas

- **Severity direction differs by source.** Suricata `alert.severity` 1 is the
  highest of 1-3; the parser maps it onto the shared 0-4 scale (higher is
  worse). For generic files check the profile's severity counts and pass
  `--sev-scale` (`inv3`, `0-10`, `0-100`) when the scale is not obvious — the
  no-hint guess (≤4 taken as 0-4) is wrong for any 1-is-worst source, so
  confirm against the profile before trusting severity panels.
- **Syslog has no year and no timezone.** The year comes from `--year` or the
  file's mtime (brittle on copied files) and the zone is assumed UTC; the
  profile and the dashboard's Data notes say so. Say "times as logged" in the
  report.
- **Log fields are attacker-controlled** (usernames, user-agents, URLs, rule
  text). The template renders display text only with `textContent` builders,
  escapes `<` in the embedded data, and ships a script-hash CSP — and the
  evals prove a hostile `<script>` column renders inert. If you edit
  `assets/template.html`, read `references/design.md` first: no `innerHTML`,
  no inline `on*=` handlers, no `style=` attributes, and re-check the hash
  story, because CSP blocks the forbidden forms silently.
- **One ink.** Severity and outcome are ink lightness, not red/amber/green.
  This overrides any other chart skill's palette for this output. A second hue
  usually means you are encoding something the layout already says. Pick
  `--accent` dark enough for 4.5:1 contrast on paper; `build` refuses lighter
  ones (default `#0000f2`).
- **Counts can be approximate.** Bulk kinds (flow, conn, dns, http, tls) above
  100k events per kind are reservoir-sampled and marked "≈"; alert and auth
  events are kept up to 500k. Original log lines are embedded only while they
  fit a 24 MB budget. Both cases appear in the dashboard's Data notes; repeat
  them in your report.
- **Config replaces, not merges.** Keys present in `--config` replace the
  defaults wholesale (`theme` keys excepted — they merge): giving `panels`
  means supplying the whole list (the worked override in
  `references/panels.md` shows the full shape). Start from `profile --json`
  output and edit that.
- **`where` values are strings.** `{"sev": ["3","4"]}`, never `[3, 4]` —
  numeric literals silently match nothing and the panel renders empty.
- **Do not hardcode ATT&CK.** Tactic names, IDs, and counts change between
  matrix versions (names are renamed, objects revoked). Show a tactic panel
  only when the data carries tactic fields, keyed by ATT&CK ID and displaying
  the pinned dataset version from the source — never a list from memory.
- **The HTML contains the data.** Treat it like the logs: do not upload,
  publish or paste it anywhere unless the user asks.
- **Thresholds live in code; layout lives in config.** Changing a signal
  threshold means copying `soc_dash.py` and `parsers.py` next to the data plus
  `assets/template.html`, pointing the copy at its template
  (`SOC_DASH_TEMPLATE=<data-dir>/template.html`), editing the copy, and saying
  so in the report; do not modify the installed skill.
- **Not covered:** live tailing, GeoIP/threat-intel enrichment (no network),
  maps, SIEM connectors. Say so if asked rather than faking it.

## Resources

- `references/data-sources.md`: read when a format is unfamiliar, profile coverage looks wrong, or you need `--map`. Field maps per format, time handling, severity mapping, ATT&CK note.
- `references/panels.md`: read before changing the default panels or writing `--config`. Hero dimension by data kind, panel types and schema, every signal rule with thresholds.
- `references/design.md`: read when restyling, adding a panel type, or editing the template. Tokens, type, chart rules, CSP constraints, accessibility notes.
- `references/wording.md`: read before writing any lead. Lead vocabulary, grades, phrasing table, anti-patterns.
- `references/handoffs.md`: read when reporting. Lead packet, incident slice, wiki filing, report inputs.
- `scripts/soc_dash.py` (`profile`, `build`), `scripts/verify.py`, `scripts/parsers.py` (imported), `assets/template.html` (copied into every build).
