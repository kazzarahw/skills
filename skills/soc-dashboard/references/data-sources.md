# Data sources

How each format maps to the shared event schema, and what to do when detection or mapping goes wrong.

## Contents
- The shared schema
- Formats and their maps
- Time handling
- Severity
- Generic JSON/CSV and `--map`
- ATT&CK tactics
- When nothing parses

## The shared schema

Every parser yields events with these keys (all optional except `t`). The dashboard, signals and filters speak only this vocabulary.

| Key | Meaning | Notes |
|---|---|---|
| `t` | epoch ms, UTC | events without a parsable time are dropped |
| `kind` | event class | `alert`, `auth`, `priv`, `session`, `flow`, `conn`, `dns`, `http`, `tls`, `event`, … |
| `sev` | 0 info, 1 low, 2 medium, 3 high, 4 critical | higher is worse, after normalisation |
| `out` | `success` / `failure` | auth-like events |
| `act` | sensor action | `allowed`, `blocked`, … |
| `src`, `dst`, `sport`, `dport`, `proto` | addresses, ports | IPv4-mapped `::ffff:a.b.c.d` becomes `a.b.c.d`; `-`, `::`, `0.0.0.0` become empty |
| `sig` | rule / event name | Suricata signature, `4625 logon failure`, `ssh login failed` |
| `cat`, `tac` | category, ATT&CK tactic | `tac` only when the source carries it |
| `user`, `host`, `app` | account, reporting host, service / app protocol | |
| `st` | state | Zeek `conn_state`, HTTP status, DNS rcode, Windows NTSTATUS |
| `ua`, `msg` | user-agent, short detail | `msg` = URL, query name, SNI, logon type, command |
| `bytes`, `dur` | total bytes, seconds | |

## Formats and their maps

Detection looks at the first 64 KB. Override with `--format {eve,zeek_tsv,zeek_json,syslog,winevent,cef,ndjson,json_array,csv}`.

| Format | Recognised by | Mapping highlights |
|---|---|---|
| **Suricata EVE** | JSON lines with `event_type` plus `src_ip`/`flow_id`/`timestamp` | `alert` → kind alert, `alert.severity` 1-3 inverted (1 = high), `alert.signature`, `category`, `action`, `app_proto`; `alert.metadata.mitre_tactic_name` → `tac` when rules carry it. `flow` → bytes = `bytes_toserver + bytes_toclient`. `dns`, `http`, `tls`, `anomaly` mapped; `stats` skipped. Timestamps look like `2026-09-28T03:14:15.123456+0000`. |
| **Zeek TSV** | first line `#separator` / `#fields` | Header-driven: `#separator \x09`, unset `-`, empty `(empty)`, `ts` is an epoch float. Handles `conn`, `dns`, `http`, `ssl`, `ssh` (auth_success → outcome), `notice` (→ alert, sev 2), `weird` (→ alert, sev 1); other logs become kind = log name. `conn` bytes = `orig_bytes + resp_bytes` (application layer), state in `st`, `service` in `app`. Pass several logs at once and they merge onto one timeline. |
| **Zeek JSON** | `id.orig_h` keys or `_path` + `ts` | Same maps; log type inferred from fields when `_path` is absent. |
| **syslog / auth.log** | lines shaped `Mon dd HH:MM:SS host proc[pid]: …` or ISO-time variants | sshd: `Failed password`, `Accepted …`, `Invalid user`, `maximum authentication attempts`, `Did not receive identification string`, session opened/closed, pre-auth disconnects. `sudo` commands and incorrect-password lines, `su` failures. Everything else keeps kind `event` with the process as `sig`. Other daemons are not parsed beyond that. |
| **Windows Security events** | JSON with `EventID`/`winlog.event_id`/`event.code` plus `TargetUserName`/`EventData`/`LogonType` | 4624 success, 4625 failure (LogonType text and NTSTATUS in `msg`/`st`), 4740 lockout, Kerberos 4768/4769/4771, 4776; privileged events 4672, 4720, 4728/4732/4756, 4697/7045, 4698, 4719, 1102 use the **actor** (`SubjectUserName`) as `user`. `IpAddress` may be `::1`, `127.0.0.1` or `-`; `-` becomes blank, loopback addresses are kept as written (filter them with a search if they drown the source panels). Works on Winlogbeat, raw `Event.System/EventData` JSON, and ECS-flattened exports. |
| **CEF** | `CEF:0\|` anywhere on the first line | Header fields: name → `sig`, vendor/product → `cat`, severity 0-10 → bucketed (0-3 low, 4-6 medium, 7-8 high, 9-10 critical). Extension keys `src dst spt dpt proto suser duser act outcome msg request rt dvchost`. Time from `rt`/`start`/`end`, else the syslog prefix. |
| **Generic JSON lines / JSON array / CSV** | anything else | Field aliases (next sections). |

## Time handling

- Epoch seconds, milliseconds, microseconds and nanoseconds are told apart by magnitude.
- ISO 8601 with `Z`, `+0000`, `+00:00`, or no zone (then `--tz`, default UTC).
- `m/d/Y H:M:S` is read as US order; flag it if the source may be `d/m/Y`.
- Year-less syslog: year from the file's modification time (previous year when the log month is later than the file's month + 1). Zone assumed UTC. Both are assumptions to state in the report.
- The dashboard shows UTC throughout.

## Severity

Normalised to 0-4. Text maps: info → 0, low/notice/minor → 1, medium/moderate/warning → 2, high/major/error → 3, critical/severe/fatal/emergency → 4. Numbers: `--sev-scale inv3` (Suricata), `0-10` (CEF-like), `0-100`; with no hint, values ≤ 4 are taken as already 0-4 and larger ones are bucketed by 0-10 or 0-100 range. That guess is wrong for any source that uses 1 = most severe, so confirm against `profile` output before trusting severity panels.

## Generic JSON/CSV and `--map`

Nested JSON is flattened to dotted keys and matched case-insensitively against aliases, for example:

- `t`: `@timestamp`, `timestamp`, `time`, `ts`, `_time`, `datetime`, `event_time`, `created_at`, …
- `src`: `src_ip`, `source.ip`, `client_ip`, `remote_addr`, `id.orig_h`, `ipaddress`, …; `dst`: `dest_ip`, `destination.ip`, `server_ip`, …
- `sig`: `signature`, `rule.name`, `alert_name`, `event.action`, `title`, `kibana.alert.rule.name`, …
- `sev`: `severity`, `event.severity`, `risk`, `priority`, `level`, `kibana.alert.severity`
- `out`: `outcome`, `event.outcome`, `result`, `status`, `success` (truthy words and 1/0 map to success/failure)
- `user`: `user`, `user.name`, `username`, `account`, `targetusername`

The alias lists are in `scripts/parsers.py` (`ALIASES`). When a needed field is named something else, map it explicitly and re-run `profile`:

```bash
python3 scripts/soc_dash.py profile export.csv --map src=client.addr --map sig=detection_name --map t=first_seen --sev-scale 0-100
```

Without a `kind` field, rows with an outcome and a user become `auth`; everything else is `event`, which selects the generic panel set. If the data is really alerts, map a field to `kind` or set `kind` values to `alert` before building.

## ATT&CK tactics

Tactic names and IDs move between matrix versions. As checked on attack.mitre.org in 2026-09 (v19.2), Enterprise has 15 tactics and TA0005 is named "Stealth" (previously "Defense Evasion"), with "Defense Impairment" TA0112 added. Do not build a fixed tactic list from memory: the dashboard shows a tactic rank only when events carry a tactic field (EVE `alert.metadata.mitre_tactic_name`, a `tactic` column), using whatever names the source wrote.

## When nothing parses

1. `head -c 600 FILE` and compare against the table. Wrapped exports (`{"hits":{"hits":[{"_source":{…}}]}}`, `{"events":[…]}`) need unwrapping first: write the inner records to a JSON-lines file with a few lines of Python, then profile that.
2. Multi-line formats (raw XML event logs, PCAP, `.evtx`) are out of scope. Convert with the platform's own tool (`wevtutil`/`evtx_dump` to JSON, `tshark -T ek` or Zeek/Suricata over the PCAP), then use the result.
3. Compressed files: decompress first (`zcat`).
4. Report what was and was not parsed; the profile prints the count of unparseable JSON records.
