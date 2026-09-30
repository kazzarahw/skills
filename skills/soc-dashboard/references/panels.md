# Panels, signals and config

Choosing what the dashboard shows, and how to override the defaults.

## Contents
- Derive, don't template
- Hero dimension by data kind
- Panel types and config schema
- Signal rules
- Worked override

## Derive, don't template

A dashboard is a few questions answered at a glance, with detail one click away. Before touching config, write the questions for this data, then keep only panels that answer them.

| Data is mostly… | Hero dimension (gets the darkest ink) | Questions to answer | Default panels |
|---|---|---|---|
| **Alerts** (IDS/IPS/EDR; `alert` ≥ 25%) | `sev` | What fired, how bad, from where to where, when did it change? | KPIs (alerts, high+critical, sources, targets, rules), signals, severity timeline, rules, hour map, sources, targets, ports, category, user-agents, table |
| **Auth** (logins; `auth/priv/session` ≥ 40%) | `out` (failure darkest) | Who is being hit, from where, did anything get in, what did it do next? | KPIs (failed, succeeded, sources with failures, accounts targeted), signals, outcome timeline, sources of failures, accounts targeted, successful logins by account, hour map, method, host, table |
| **Flows** (conn/flow ≥ 40%, few alerts) | `bytes` | Who talks to whom, how much, to what service, anything unusual in volume or shape? | KPIs (connections, traffic, sources, destinations), signals, traffic timeline by service, destinations and sources by bytes, ports, service, state, hour map, table |
| **Mixed / unknown** | `kind` | What kinds of events, from whom, when? | events KPIs, signals, kind timeline, kind/rule/source/target/account ranks, hour map, table |

`profile` prints the suggested profile. Override it when you know better: a mixed Suricata file with 15% alerts still deserves the alerts layout if the user cares about alerts (put `"where": {"kind": ["alert"]}` on the panels, as the defaults do).

Rules of thumb:
- Drop a panel if its field has fewer than 2 distinct values or under ~8% coverage (the defaults already do).
- Add a panel only for a question the defaults miss: a rank of `tac` when tactics exist, `host` when several sensors report, a `src>dst` pair rank for lateral movement.
- 8-11 panels. More than that stops being a dashboard.
- Title panels with the noun the reader uses ("Accounts targeted"), not the field name.
- Timeline `by` is the hero dimension or a low-cardinality field (≤ 6 values; the rest fold into "other").

## Panel types and config schema

`--config cfg.json` is merged over the defaults. Keys present **replace** the default: give `panels` and you supply the whole list.

```json
{
  "title": "VPN gateway auth, 21-27 Sep",
  "kicker": "Security analysis · prepared for IR-2041",
  "theme": { "accent": "#0000f2", "mode": "light" },
  "panels": [ ... ]
}
```

`theme.mode` is the initial light/dark choice (`light`, `dark`, or omit for the OS setting); viewers can still toggle, and `#theme=dark` in the URL works. `kicker` is the small line above the title.

Fields usable in `field`, `by`, `where`: `kind sev out act src dst sport dport proto sig cat tac user host app st ua msg`; `src>dst` (any two fields joined with `>`) makes a pair column. `where` maps a field to a list of **strings** (`{"sev": ["3","4"], "kind": ["alert"]}`); an event must match every key.

| `type` | Keys | Notes |
|---|---|---|
| `kpis` | `items: [{label, agg: "count"\|"uniq"\|"sum", field?, where?, unit?}]` | `uniq` counts distinct `field`; `sum` with `field: "bytes"`, `unit: "bytes"` formats as KB/MB/GB (decimal, 1 GB = 10^9 bytes). Each tile carries a sparkline. |
| `signals` | none | The computed leads. Keep it near the top. |
| `timeline` | `title, by, value?: "count"\|"bytes", where?, w` | Stacked bars, bucket size adapts to the visible range, drag to zoom, click a bar to select it. |
| `rank` | `title, field, value?: "count"\|"bytes", where?, w, limit` | Click a row to filter; "show more" reaches 40. Ranks ignore their own field's filter so alternatives stay visible. |
| `heat` | `title, where?, w` | Day × hour dot matrix (weekday × hour when the range exceeds 35 days). Dot area is capped at the 95th percentile when one hour dwarfs the rest, so the normal rhythm stays visible. |
| `table` | `title, columns: [t, sev, sig, src, dst, dport, act, …], where?` | Virtualised, sortable, CSV export, click a row for detail. |
| `stack` | `w, panels: [...]` | Stacks sub-panels in one column so short panels do not leave gaps. |

`w` is the column span out of 12 (`4`, `6`, `8`, `12`); layouts collapse to one column on narrow screens. Panels with a `where` that matches nothing render empty, so check the screenshot.

## Signal rules

Computed in `scripts/soc_dash.py` (`compute_signals`) over the embedded events. Every signal shows its rule and evidence; thresholds are deliberately conservative. When a dataset needs different sensitivity, copy `soc_dash.py` (with `parsers.py` and `../assets/template.html` beside it) next to the data, edit the copy, and say so in the report; do not modify the installed skill.

| Signal | Level | Fires when |
|---|---|---|
| Burst | med | Alert+auth events per clock-aligned bucket (1 min to 1 day, about 200 buckets) ≥ max(20, median + 8·MAD, 4×median). Top 3 by size; names the dominant source and rule. |
| Periodic traffic | high if the events include severity ≥ 3, else med | ≥ 12 events for one src→dst:port with median gap 1 s to 6 h, ≥ 80% of gaps within ±25% of the median, span ≥ 10 gaps. Top 3. |
| Login succeeded after failures | high | ≥ 10 failures from one source (gaps ≤ 10 min) followed by a success from that source before the burst ends or within 30 min after. Notes follow-on privileged events (sudo, 4672, account creation) within 10 min. |
| Spray | med | Such a failure burst across ≥ 15 distinct accounts, no success. |
| Repeated failures | med | ≥ 20 failures in such a burst against < 15 accounts, no success. |
| Scan-like | med | ≥ 30 events from one source in a 10-min window touching ≥ 15 ports or ≥ 25 hosts. |
| Large transfer | med | One src→dst pair carries ≥ 15% of all bytes and ≥ 100 MB. |
| Account / group changes | med | Windows 4720, 4728, 4732, 4756. |
| Audit log cleared | high | Windows 1102. |
| No alert blocked | info | ≥ 20 alerts carry an action and none is blocking. |

Mention a pattern you noticed yourself in the report, labelled as your reading, rather than adding an untested rule on the spot.

## Worked override

An alerts file where only the four worst rules matter and the user wants flows split by sensor:

```json
{
  "title": "Edge IPS, week 38",
  "panels": [
    {"type": "kpis", "items": [
      {"label": "High + critical", "agg": "count", "where": {"sev": ["3","4"]}},
      {"label": "Sensors", "agg": "uniq", "field": "host"}]},
    {"type": "signals"},
    {"type": "timeline", "title": "High + critical over time", "by": "host", "where": {"sev": ["3","4"]}, "w": 12},
    {"type": "rank", "title": "Rules", "field": "sig", "where": {"sev": ["3","4"]}, "w": 6},
    {"type": "rank", "title": "Source → target", "field": "src>dst", "where": {"sev": ["3","4"]}, "w": 6},
    {"type": "table", "title": "High + critical events", "where": {"sev": ["3","4"]}, "columns": ["t","host","sig","src","dst","dport"]}
  ]
}
```
