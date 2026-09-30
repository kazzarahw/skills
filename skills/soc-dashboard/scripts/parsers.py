"""Format detection and parsers: security logs -> canonical event dicts.

Canonical keys (all optional except t): t (epoch ms), kind, sev (0-4), out
(success|failure), act, src, sport, dst, dport, proto, sig, cat, tac, user,
host, app, st, ua, msg, bytes, dur, raw.  stdlib only, Python 3.8+.
"""
import csv, io, json, os, re, datetime as dt

SEV_TEXT = {
    "info": 0, "informational": 0, "information": 0, "notice": 1, "low": 1, "minor": 1,
    "medium": 2, "moderate": 2, "warning": 2, "warn": 2, "major": 3, "high": 3, "error": 3,
    "critical": 4, "crit": 4, "severe": 4, "fatal": 4, "emergency": 4, "alert": 4,
}
RAW_MAX = 1200
STATS = {"bad_json": 0, "no_time": 0, "note": []}  # per-file counters, reset by the caller: unparseable records, events without a usable timestamp, assumption notes


# ---------------------------------------------------------------- timestamps
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:[.,](\d+))?\s*(Z|[+-]\d{2}:?\d{2}|[+-]\d{2})?$")
_MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def to_ms(v, default_tz_min=0):
    """Best-effort timestamp -> epoch ms. Accepts epoch s/ms/us/ns, ISO 8601, 'YYYY-MM-DD HH:MM:SS'."""
    if v is None or v == "" or v == "-":
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) or (isinstance(v, str) and re.fullmatch(r"\d+(\.\d+)?", v.strip())):
        x = float(v)
        if x <= 0:
            return None
        if x < 1e11:
            return int(x * 1000)          # seconds
        if x < 1e14:
            return int(x)                 # ms
        if x < 1e17:
            return int(x / 1000)          # us
        return int(x / 1e6)               # ns
    if not isinstance(v, str):
        return None
    m = _ISO.match(v.strip())
    if not m:
        m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})[ T](\d{1,2}):(\d{2}):(\d{2})$", v.strip())
        if m2:  # US style m/d/Y; ambiguous, documented as a caveat
            mo, d, y, H, M, S = map(int, m2.groups())
            return _utc(y, mo, d, H, M, S, 0, default_tz_min)
        return None
    y, mo, d, H, M, S = map(int, m.groups()[:6])
    frac = m.group(7) or "0"
    ms = int((frac + "000")[:3])
    tz = m.group(8)
    off = default_tz_min
    if tz:
        if tz == "Z":
            off = 0
        else:
            sign = -1 if tz[0] == "-" else 1
            digits = tz[1:].replace(":", "")
            off = sign * (int(digits[:2]) * 60 + (int(digits[2:4]) if len(digits) > 2 else 0))
    return _utc(y, mo, d, H, M, S, ms, off)


def _utc(y, mo, d, H, M, S, ms, off_min):
    try:
        t = dt.datetime(y, mo, d, H, M, S, tzinfo=dt.timezone.utc)
    except ValueError:
        return None
    return int(t.timestamp() * 1000) + ms - off_min * 60000


def sev_norm(v, scale=None):
    """Normalise a severity to 0-4 (higher = worse). scale: 'inv3' for Suricata (1=high)."""
    if v is None or v == "":
        return None
    if isinstance(v, str):
        s = v.strip().lower()
        if s in SEV_TEXT:
            return SEV_TEXT[s]
        try:
            v = float(s)
        except ValueError:
            return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if scale == "inv3":
        return {1: 3, 2: 2, 3: 1}.get(int(x), 0)
    if scale == "0-10":
        return 1 if x < 4 else 2 if x < 7 else 3 if x < 9 else 4
    if scale == "0-100":
        return 1 if x < 25 else 2 if x < 50 else 3 if x < 75 else 4
    if x <= 4:
        return int(x)
    return 1 if x < 4 else 2 if x < 7 else 3 if x < 9 else 4 if x <= 10 else (1 if x < 25 else 2 if x < 50 else 3 if x < 75 else 4)


def to_int(v):
    try:
        if v in (None, "", "-", "(empty)"):
            return None
        return int(float(v))
    except (TypeError, ValueError):
        return None


def clean_ip(v):
    if not isinstance(v, str):
        return None
    v = v.strip()
    if v in ("", "-", "::", "(empty)", "0.0.0.0"):
        return None
    if v.startswith("::ffff:") and "." in v:
        v = v[7:]
    return v


def flatten(o, prefix="", out=None, depth=0):
    if out is None:
        out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict) and depth < 5:
                flatten(v, key, out, depth + 1)
            else:
                out[key] = v
    return out


def raw_of(o):
    s = o if isinstance(o, str) else json.dumps(o, separators=(",", ":"), default=str)
    return s if len(s) <= RAW_MAX else s[:RAW_MAX] + "…"


def ev(**kw):
    return {k: v for k, v in kw.items() if v not in (None, "")}


# ---------------------------------------------------------------- detection
def _head(path, n=65536):
    with open(path, "rb") as f:
        return f.read(n).decode("utf-8", "replace")


_SYSLOG = re.compile(r"^(?:<\d+>)?(?:[A-Z][a-z]{2}\s+\d{1,2}\s\d\d:\d\d:\d\d|\d{4}-\d\d-\d\dT[\d:.]+(?:Z|[+-]\d\d:?\d\d)?)\s+\S+\s+[\w./()-]+(?:\[\d+\])?:")


def _classify_record(o):
    if "event_type" in o and ("src_ip" in o or "flow_id" in o or "timestamp" in o):
        return "eve"
    if "id.orig_h" in o or (isinstance(o.get("id"), dict) and "orig_h" in o["id"]) or ("_path" in o and "ts" in o):
        return "zeek_json"
    fl = flatten(o)
    names = " ".join(fl).lower()
    if any(k.lower().endswith(("eventid", "event_id", "event.code")) for k in fl) and any(
            s in names for s in ("targetusername", "winlog", "eventdata", "logontype", "computer")):
        return "winevent"
    return None


def _classify_json(path, is_array):
    seen = 0
    for o in _json_records(path):
        c = _classify_record(o)
        if c:
            return c
        seen += 1
        if seen >= 20:
            break
    return "json_array" if is_array else "ndjson"


def detect(path):
    """Return a format id for a file (see FORMATS)."""
    head = _head(path)
    lines = [l for l in head.splitlines() if l.strip()]
    if not lines:
        return "empty"
    if lines[0].startswith("#separator") or lines[0].startswith("#fields"):
        return "zeek_tsv"
    first = lines[0].lstrip("\ufeff")
    if "CEF:0|" in first:
        return "cef"
    if first.startswith("[") or first.startswith("{"):
        return _classify_json(path, first.startswith("["))
    if sum(1 for l in lines[:30] if _SYSLOG.match(l)) >= max(1, min(len(lines), 30) // 2):
        return "syslog"
    if "," in first or "\t" in first or ";" in first:
        return "csv"
    return "text"


# ---------------------------------------------------------------- readers
def _lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if line.strip():
                yield line


def _json_records(path):
    """Yield dict records from NDJSON or a JSON array; counts bad lines in .bad."""
    bad = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        txt_start = ""
        while True:
            ch = f.read(1)
            if not ch:
                break
            if not ch.isspace():
                txt_start = ch
                break
        f.seek(0)
        if txt_start == "[":
            data = json.load(f)
            for o in data:
                if isinstance(o, dict):
                    yield o
                else:
                    bad += 1
        else:
            for line in f:
                line = line.strip().lstrip("\ufeff")
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    bad += 1
                    continue
                if isinstance(o, dict):
                    yield o
                elif isinstance(o, list):
                    for x in o:
                        if isinstance(x, dict):
                            yield x
                else:
                    bad += 1
    STATS["bad_json"] += bad


# ---------------------------------------------------------------- Suricata EVE
def parse_eve(path, opts):
    for o in _json_records(path):
        et = o.get("event_type")
        if et in ("stats",):
            continue
        t = to_ms(o.get("timestamp"))
        if t is None:
            STATS["no_time"] += 1
            continue
        base = dict(t=t, src=clean_ip(o.get("src_ip")), sport=to_int(o.get("src_port")), dst=clean_ip(o.get("dest_ip")),
                    dport=to_int(o.get("dest_port")), proto=o.get("proto"), app=o.get("app_proto"),
                    host=o.get("host") or o.get("in_iface"), raw=raw_of(o))
        http, dns, tls, fl = o.get("http") or {}, o.get("dns") or {}, o.get("tls") or {}, o.get("flow") or {}
        if et == "alert":
            a = o.get("alert") or {}
            meta = a.get("metadata") or {}
            tac = meta.get("mitre_tactic_name") or meta.get("mitre_tactic_id")
            if isinstance(tac, list):
                tac = tac[0] if tac else None
            msg = None
            if http:
                msg = ((http.get("hostname") or "") + (http.get("url") or "")) or None
            elif dns:
                msg = dns.get("rrname")
            elif tls:
                msg = tls.get("sni")
            yield ev(**base, kind="alert", sev=sev_norm(a.get("severity"), "inv3"), act=a.get("action"), sig=a.get("signature"),
                     cat=a.get("category"), tac=tac, ua=http.get("http_user_agent"), msg=msg, st=str(http.get("status") or "") or None)
        elif et == "flow":
            b = (to_int(fl.get("bytes_toserver")) or 0) + (to_int(fl.get("bytes_toclient")) or 0)
            yield ev(**base, kind="flow", bytes=b, st=fl.get("state"), msg=fl.get("reason"))
        elif et == "dns":
            yield ev(**base, kind="dns", msg=dns.get("rrname"), cat=dns.get("rrtype"), st=dns.get("rcode"))
        elif et in ("http", "http2"):
            yield ev(**base, kind="http", msg=((http.get("hostname") or "") + (http.get("url") or "")) or None,
                     cat=http.get("http_method"), ua=http.get("http_user_agent"), st=str(http.get("status") or "") or None,
                     bytes=to_int(http.get("length")))
        elif et == "tls":
            yield ev(**base, kind="tls", msg=tls.get("sni"), st=tls.get("version"), cat=tls.get("ja3", {}).get("hash") if isinstance(tls.get("ja3"), dict) else None)
        elif et == "anomaly":
            an = o.get("anomaly") or {}
            yield ev(**base, kind="alert", sev=1, sig=f"anomaly: {an.get('event') or an.get('type')}", cat="anomaly")
        else:
            yield ev(**base, kind=et or "event", msg=None)


# ---------------------------------------------------------------- Zeek
def _zeek_unescape(s):
    return s.encode("utf-8", "replace").decode("unicode_escape", "replace") if "\\x" in s else s


def _zeek_records_tsv(path):
    fields, sep, unset, empty, zpath = None, "\t", "-", "(empty)", "log"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            if line.startswith("#"):
                parts = line.split(" ", 1) if line.startswith("#separator") else line.split(sep)
                key = parts[0]
                if key == "#separator" and len(parts) > 1:
                    sep = _zeek_unescape(parts[1])
                elif key == "#unset_field":
                    unset = parts[1]
                elif key == "#empty_field":
                    empty = parts[1]
                elif key == "#path":
                    zpath = parts[1]
                elif key == "#fields":
                    fields = parts[1:]
                continue
            if not fields:
                continue
            vals = line.split(sep)
            rec = {}
            for k, v in zip(fields, vals):
                if v == unset or v == empty:
                    continue
                rec[k] = v
            rec["_path"] = zpath
            yield rec


def parse_zeek(path, opts, tsv=True):
    it = _zeek_records_tsv(path) if tsv else _json_records(path)
    for r in it:
        r = flatten(r) if not tsv else r
        t = to_ms(r.get("ts"))
        if t is None:
            STATS["no_time"] += 1
            continue
        p = r.get("_path")
        if not p:
            p = ("conn" if "conn_state" in r else "dns" if "query" in r else "http" if "uri" in r or "method" in r else
                 "ssl" if "server_name" in r or "cipher" in r else "notice" if "note" in r else "ssh" if "auth_success" in r else
                 "weird" if "name" in r and "id.orig_h" not in r else "files" if "fuid" in r else "event")
        src, dst = clean_ip(r.get("id.orig_h")), clean_ip(r.get("id.resp_h"))
        base = dict(t=t, src=src, sport=to_int(r.get("id.orig_p")), dst=dst, dport=to_int(r.get("id.resp_p")),
                    proto=r.get("proto"), raw=raw_of(r))
        if p == "conn":
            b = (to_int(r.get("orig_bytes")) or 0) + (to_int(r.get("resp_bytes")) or 0)
            yield ev(**base, kind="conn", bytes=b, app=r.get("service"), st=r.get("conn_state"), dur=float(r["duration"]) if r.get("duration") else None,
                     msg=r.get("history"))
        elif p == "dns":
            yield ev(**base, kind="dns", msg=r.get("query"), cat=r.get("qtype_name"), st=r.get("rcode_name"), app="dns")
        elif p == "http":
            yield ev(**base, kind="http", msg=(r.get("host", "") + r.get("uri", "")) or None, cat=r.get("method"), ua=r.get("user_agent"),
                     st=r.get("status_code"), bytes=to_int(r.get("response_body_len")), app="http")
        elif p in ("ssl", "tls"):
            yield ev(**base, kind="tls", msg=r.get("server_name"), st=r.get("version"), app="ssl")
        elif p == "ssh":
            ok = r.get("auth_success")
            yield ev(**base, kind="auth", out="success" if ok in ("T", "true", True) else "failure" if ok in ("F", "false", False) else None,
                     app="ssh", msg=r.get("client"))
        elif p == "notice":
            yield ev(**base, kind="alert", sev=2, sig=r.get("note"), msg=r.get("msg"), cat="zeek notice")
        elif p == "weird":
            yield ev(**base, kind="alert", sev=1, sig=r.get("name"), cat="zeek weird", msg=r.get("addl"))
        else:
            yield ev(**base, kind=p, msg=r.get("name") or r.get("filename") or r.get("mime_type"))


# ---------------------------------------------------------------- syslog / sshd
_SL_HDR = re.compile(r"^(?:<\d+>)?(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d\d:\d\d:\d\d|\d{4}-\d\d-\d\dT[\d:.]+(?:Z|[+-]\d\d:?\d\d)?)\s+(?P<host>\S+)\s+(?P<proc>[\w./() -]+?)(?:\[(?P<pid>\d+)\])?:\s*(?P<msg>.*)$")
_FAIL = re.compile(r"Failed (?P<m>\S+) for (?:invalid user )?(?P<u>\S+) from (?P<ip>\S+) port (?P<p>\d+)")
_ACC = re.compile(r"Accepted (?P<m>\S+) for (?P<u>\S+) from (?P<ip>\S+) port (?P<p>\d+)")
_INV = re.compile(r"Invalid user (?P<u>.*?) from (?P<ip>\S+)(?: port (?P<p>\d+))?")
_PREAUTH = re.compile(r"(?:Connection closed|Disconnected|Connection reset) (?:by|from) (?:authenticating user (?P<u>\S+) )?(?P<ip>\d[\d.]+|[0-9a-fA-F:]+) port (?P<p>\d+)")
_MAXA = re.compile(r"maximum authentication attempts exceeded for (?:invalid user )?(?P<u>\S+) from (?P<ip>\S+) port (?P<p>\d+)")
_NOID = re.compile(r"Did not receive identification string from (?P<ip>\S+)")
_SESS = re.compile(r"session (?P<w>opened|closed) for user (?P<u>\S+?)(?:\(|\s|$)")
_SUDO = re.compile(r"^\s*(?P<u>\S+)\s*:.*?(?:USER=(?P<tu>\S+)\s*;\s*)?COMMAND=(?P<c>.*)$")
_SUDO_FAIL = re.compile(r"(?P<u>\S+)\s*:\s*(?P<n>\d+) incorrect password attempt")


def _syslog_ts(s, opts, mtime):
    if s[0].isdigit():
        return to_ms(s, opts.get("tz_min", 0))
    m = re.match(r"([A-Z][a-z]{2})\s+(\d{1,2})\s(\d\d):(\d\d):(\d\d)", s)
    if not m:
        return None
    mon, d, H, M, S = _MON[m.group(1)], int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
    year = opts.get("year")
    if year is None:
        mt = dt.datetime.fromtimestamp(mtime, dt.timezone.utc)
        year = mt.year
        # log lines from late in the previous year when the file was last written in Jan/Feb
        if mon > mt.month + 1:
            year -= 1
    return _utc(year, mon, d, H, M, S, 0, opts.get("tz_min", 0))


def parse_syslog(path, opts):
    mtime = os.path.getmtime(path)
    yr = opts.get("year") or dt.datetime.fromtimestamp(mtime, dt.timezone.utc).year
    STATS["note"].append(f"{os.path.basename(path)}: syslog lines carry no year or zone; assumed year {yr} ({'from --year' if opts.get('year') else 'from the file modification time'}) and "
                         f"{'UTC' if not opts.get('tz_min') else 'UTC%+d min' % opts['tz_min']}. Times are as logged.")
    for line in _lines(path):
        m = _SL_HDR.match(line)
        if not m:
            continue
        t = _syslog_ts(m.group("ts"), opts, mtime)
        if t is None:
            STATS["no_time"] += 1
            continue
        proc, msg, host = m.group("proc").strip(), m.group("msg"), m.group("host")
        base = dict(t=t, host=host, raw=raw_of(line))
        if proc.startswith("sshd") or "sshd" in proc:
            x = _FAIL.search(msg)
            if x:
                yield ev(**base, kind="auth", out="failure", user=x["u"], src=clean_ip(x["ip"]), sport=to_int(x["p"]), app="ssh", sig="ssh login failed", msg=x["m"], dport=22)
                continue
            x = _ACC.search(msg)
            if x:
                yield ev(**base, kind="auth", out="success", user=x["u"], src=clean_ip(x["ip"]), sport=to_int(x["p"]), app="ssh", sig="ssh login", msg=x["m"], dport=22)
                continue
            x = _INV.search(msg)
            if x:
                yield ev(**base, kind="auth", out="failure", user=x["u"], src=clean_ip(x["ip"]), sport=to_int(x["p"]), app="ssh", sig="ssh invalid user", msg="invalid user", dport=22)
                continue
            x = _MAXA.search(msg)
            if x:
                yield ev(**base, kind="auth", out="failure", sev=2, user=x["u"], src=clean_ip(x["ip"]), sport=to_int(x["p"]), app="ssh", sig="ssh max attempts exceeded", dport=22)
                continue
            x = _NOID.search(msg)
            if x:
                yield ev(**base, kind="auth", src=clean_ip(x["ip"]), app="ssh", sig="ssh no identification", dport=22)
                continue
            x = _SESS.search(msg)
            if x:
                yield ev(**base, kind="session", user=x["u"], app="ssh", sig=f"session {x['w']}", msg=msg[:120])
                continue
            x = _PREAUTH.search(msg)
            if x:
                yield ev(**base, kind="session", user=x["u"], src=clean_ip(x["ip"]), sport=to_int(x["p"]), app="ssh", sig="connection closed", msg=msg[:120], dport=22)
                continue
        elif proc == "sudo":
            x = _SUDO_FAIL.search(msg)
            if x:
                yield ev(**base, kind="priv", out="failure", user=x["u"], sev=2, sig="sudo incorrect password", msg=msg[:160])
                continue
            x = _SUDO.match(msg)
            if x:
                yield ev(**base, kind="priv", user=x["u"], sig="sudo", msg=x["c"][:200], cat=x["tu"] or None)
                continue
        elif proc.startswith("su") and "FAILED" in msg.upper():
            yield ev(**base, kind="priv", out="failure", sev=2, sig="su failed", msg=msg[:160])
            continue
        yield ev(**base, kind="event", sig=proc, msg=msg[:200])


# ---------------------------------------------------------------- Windows events
WIN_IDS = {
    4624: ("logon success", "success"), 4625: ("logon failure", "failure"), 4634: ("logoff", None), 4647: ("user logoff", None),
    4648: ("explicit-credential logon", None), 4672: ("special privileges assigned", None), 4688: ("process created", None),
    4697: ("service installed", None), 4698: ("scheduled task created", None), 4719: ("audit policy changed", None),
    4720: ("account created", None), 4722: ("account enabled", None), 4724: ("password reset", None), 4728: ("added to global group", None),
    4732: ("added to local group", None), 4740: ("account locked out", "failure"), 4756: ("added to universal group", None),
    4768: ("kerberos TGT requested", None), 4769: ("kerberos service ticket", None), 4771: ("kerberos pre-auth failed", "failure"),
    4776: ("NTLM credential validation", None), 1102: ("audit log cleared", None), 7045: ("service installed (System)", None),
}
WIN_LOGON = {2: "interactive", 3: "network", 4: "batch", 5: "service", 7: "unlock", 8: "network cleartext", 9: "new credentials",
             10: "remote interactive (RDP)", 11: "cached interactive"}
WIN_SEV = {4625: 1, 4740: 2, 4771: 1, 1102: 3, 4719: 2, 4697: 2, 7045: 2, 4698: 2, 4720: 1, 4728: 2, 4732: 2, 4756: 2, 4724: 1}


def _first(fl, *names):
    low = {k.lower(): v for k, v in fl.items()}
    for n in names:
        v = low.get(n.lower())
        if v not in (None, "", "-"):
            return v
    for n in names:  # suffix match on dotted keys
        suf = "." + n.lower()
        for k, v in low.items():
            if k.endswith(suf) and v not in (None, "", "-"):
                return v
    return None


def parse_winevent(path, opts):
    for o in _json_records(path):
        fl = flatten(o)
        eid = to_int(_first(fl, "EventID", "event_id", "event.code", "winlog.event_id", "Event.System.EventID"))
        t = to_ms(_first(fl, "@timestamp", "TimeCreated", "SystemTime", "TimeCreated.SystemTime", "timestamp", "Event.System.TimeCreated.SystemTime", "time"))
        if t is None:
            STATS["no_time"] += 1
            continue
        name, out = WIN_IDS.get(eid or 0, (f"event {eid}" if eid else "event", None))
        user = _first(fl, "TargetUserName", "user.name", "SubjectUserName", "AccountName")
        if eid in (4672, 4688, 4697, 4698, 4719, 4720, 4722, 4724, 4728, 4732, 4756, 1102):
            user = _first(fl, "SubjectUserName", "user.name") or user  # the actor, not the object of the change
        ip = clean_ip(_first(fl, "IpAddress", "source.ip", "SourceNetworkAddress", "ClientAddress"))
        lt = to_int(_first(fl, "LogonType"))
        status = _first(fl, "SubStatus", "Status")
        comp = _first(fl, "Computer", "computer_name", "host.name", "Event.System.Computer")
        kind = "auth" if eid in (4624, 4625, 4648, 4768, 4769, 4771, 4776, 4740) else "priv" if eid in (4672, 4720, 4722, 4724, 4728, 4732, 4756) else "event"
        msg = WIN_LOGON.get(lt) if lt else None
        if eid == 4625 and status:
            msg = f"{msg or ''} status {status}".strip()
        if eid == 4688:
            msg = _first(fl, "NewProcessName", "process.executable", "CommandLine", "process.command_line")
        if eid in (4697, 7045):
            msg = _first(fl, "ServiceName", "ImagePath")
        if eid == 4720:
            msg = str(_first(fl, "TargetUserName"))
        if eid in (4728, 4732, 4756):
            msg = f"{_first(fl, 'MemberName', 'MemberSid') or 'member'} \u2192 {_first(fl, 'TargetUserName') or 'group'}"
        yield ev(t=t, kind=kind, out=out, sev=WIN_SEV.get(eid or 0), sig=f"{eid} {name}" if eid else name, user=user, src=ip,
                 sport=to_int(_first(fl, "IpPort", "source.port")), host=comp, app="windows", msg=msg, raw=raw_of(o),
                 dport=3389 if lt == 10 else None, st=str(status) if status else None)


# ---------------------------------------------------------------- CEF
_CEF_HDR = re.compile(r"CEF:(\d)\|((?:\\.|[^|])*)\|((?:\\.|[^|])*)\|((?:\\.|[^|])*)\|((?:\\.|[^|])*)\|((?:\\.|[^|])*)\|((?:\\.|[^|])*)\|(.*)$")
_CEF_KV = re.compile(r"(\w+)=(.*?)(?=\s\w+=|$)")


def parse_cef(path, opts):
    mtime = os.path.getmtime(path)
    for line in _lines(path):
        i = line.find("CEF:")
        m = _CEF_HDR.match(line[i:]) if i >= 0 else None
        if not m:
            continue
        _ver, vendor, product, _dver, _sid, name, sev, ext = m.groups()
        kv = {k: v.replace("\\=", "=").replace("\\\\", "\\") for k, v in _CEF_KV.findall(ext)}
        t = to_ms(kv.get("rt") or kv.get("end") or kv.get("start"))
        if t is None:
            t = _syslog_ts(line[:15], opts, mtime) if i > 0 and re.match(r"[A-Z][a-z]{2}\s", line) else None
        if t is None:
            STATS["no_time"] += 1
            continue
        outcome = (kv.get("outcome") or "").lower()
        yield ev(t=t, kind="alert", sev=sev_norm(sev, "0-10"), sig=name.replace("\\|", "|"), cat=f"{vendor} {product}".strip(),
                 act=kv.get("act"), src=clean_ip(kv.get("src")), sport=to_int(kv.get("spt")), dst=clean_ip(kv.get("dst")),
                 dport=to_int(kv.get("dpt")), proto=kv.get("proto"), user=kv.get("suser") or kv.get("duser"),
                 host=kv.get("dvchost") or kv.get("dhost") or kv.get("shost"), msg=(kv.get("msg") or kv.get("request") or "")[:200] or None,
                 out="success" if outcome in ("success", "succeeded") else "failure" if outcome in ("failure", "failed") else None,
                 bytes=(to_int(kv.get("in")) or 0) + (to_int(kv.get("out")) or 0) or None, raw=raw_of(line))


# ---------------------------------------------------------------- generic (NDJSON / JSON array / CSV)
ALIASES = {
    "t": ["@timestamp", "timestamp", "time", "ts", "_time", "datetime", "date", "event_time", "eventtime", "created_at", "detected_at", "first_seen", "creationtime", "log_time", "occurred_at", "starttime", "start_time", "when"],
    "src": ["sourceipaddress", "client_addr", "client_address", "clientipaddress", "src_address", "src_addr", "sourceaddr", "attackerip", "src_ip", "srcip", "source.ip", "src", "source_ip", "sourceaddress", "source_address", "client_ip", "remote_ip", "remote_addr", "attacker_ip", "src_addr", "id.orig_h", "ipaddress", "sourceip", "c-ip", "clientip", "source"],
    "dst": ["destinationipaddress", "dest_addr", "target_addr", "targetip", "dest_ip", "dst_ip", "dstip", "destination.ip", "dst", "destination_ip", "destinationaddress", "destination_address", "server_ip", "target_ip", "victim_ip", "dst_addr", "id.resp_h", "destinationip", "s-ip", "destination"],
    "sport": ["src_port", "source.port", "sport", "source_port", "srcport", "id.orig_p"],
    "dport": ["dest_port", "dst_port", "destination.port", "dport", "destination_port", "dstport", "id.resp_p", "port"],
    "proto": ["proto", "protocol", "network.transport", "ip_protocol", "transport"],
    "sig": ["detection_name", "eventname", "alertname", "signature", "alert.signature", "rule.name", "rule_name", "rule", "alert_name", "alert", "name", "event.action", "action_name", "title", "kibana.alert.rule.name", "threat_name", "detection", "event_name", "message_type", "description"],
    "cat": ["category", "alert.category", "event.category", "rule.category", "type", "classification", "event.type", "class", "threat.technique.name"],
    "tac": ["tactic", "threat.tactic.name", "mitre_tactic", "mitre.tactic", "mitre_tactic_name", "attack_tactic"],
    "sev": ["severity", "alert.severity", "event.severity", "risk", "priority", "level", "kibana.alert.severity", "risk_score", "threat_level", "severity_level"],
    "act": ["action", "alert.action", "event.outcome_action", "disposition", "verdict", "result_action"],
    "out": ["outcome", "authresult", "logonresult", "event.outcome", "result", "status", "success", "auth_result"],
    "user": ["user", "user.name", "username", "user_name", "account", "targetusername", "account_name", "principal", "suser", "login", "userid", "user_id"],
    "host": ["host", "host.name", "hostname", "computer", "device", "sensor", "agent.name", "observer.name", "source_host", "machine", "asset"],
    "app": ["app_proto", "service", "application", "network.protocol", "app", "protocol_name", "app_name"],
    "msg": ["message", "msg", "details", "detail", "summary", "url", "uri", "request", "event.original", "info", "query", "command", "process.command_line", "commandline"],
    "ua": ["user_agent", "http_user_agent", "user_agent.original", "useragent", "ua", "http.user_agent"],
    "bytes": ["bytes", "total_bytes", "network.bytes", "bytes_total", "size", "length", "sentbytes", "bytes_sent"],
    "kind": ["event_type", "kind", "log_type", "logtype", "sourcetype", "_sourcetype", "dataset", "event.dataset", "type_name"],
}


def _nk(k):
    """Normalise a key for matching: lower case, alphanumerics and dots only ('Detected At' == 'detected_at')."""
    return re.sub(r"[^a-z0-9.]", "", str(k).lower())


_ALIAS_N = {}


def _row_to_event(fl, mapping, sev_scale):
    if not _ALIAS_N:
        for f_, names in ALIASES.items():
            _ALIAS_N[f_] = [_nk(n) for n in names]
    full = {}
    last = {}
    for k, v in fl.items():
        if v in (None, "", "-", "null", "None"):
            continue
        nk = _nk(k)
        full.setdefault(nk, v)
        last.setdefault(nk.rsplit(".", 1)[-1], v)

    def get(field):
        cands = [_nk(mapping[field])] if field in mapping else _ALIAS_N.get(field, [])
        for c in cands:
            if c in full:
                return full[c]
        if field not in mapping:
            for c in cands:          # 'userIdentity.userName' matches the alias 'username'
                if "." not in c and c in last:
                    return last[c]
        return None

    t = to_ms(get("t"))
    if t is None:
        return None
    outv = get("out")
    out = None
    if outv is not None:
        s = str(outv).strip().lower()
        out = "success" if s in ("success", "succeeded", "ok", "true", "t", "1", "allowed", "accepted", "pass") else \
              "failure" if s in ("failure", "failed", "fail", "false", "f", "0", "denied", "rejected", "error", "blocked") else None
    sevv = get("sev")
    sig = get("sig")
    k = get("kind")
    catv = get("cat")
    sevn = sev_norm(sevv, sev_scale)
    kind_default = "auth" if out and get("user") else "alert" if sig is not None and sevn is not None else "event"
    e = ev(t=t, kind=str(k).lower() if k is not None else kind_default, sev=sevn,
           out=out, act=get("act"), src=clean_ip(str(get("src"))) if get("src") is not None else None, sport=to_int(get("sport")),
           dst=clean_ip(str(get("dst"))) if get("dst") is not None else None, dport=to_int(get("dport")),
           proto=get("proto"), sig=str(sig)[:160] if sig is not None else None, cat=str(catv)[:80] if catv is not None else None,
           tac=get("tac"), user=get("user"), host=get("host"), app=get("app"), ua=get("ua"),
           msg=str(get("msg"))[:200] if get("msg") is not None else None, bytes=to_int(get("bytes")))
    return e


def parse_generic(path, opts, fmt):
    mapping = opts.get("map") or {}
    sev_scale = opts.get("sev_scale")
    if fmt == "csv":
        txt = open(path, "r", encoding="utf-8", errors="replace", newline="").read().lstrip("\ufeff")
        try:
            dialect = csv.Sniffer().sniff(txt[:8192], delimiters=",\t;|")
        except csv.Error:
            dialect = csv.excel
        it = csv.DictReader(io.StringIO(txt), dialect=dialect)
        recs = (dict(r) for r in it)
    else:
        recs = _json_records(path)
    hinted = False
    for r in recs:
        fl = flatten(r) if fmt != "csv" else {k: v for k, v in r.items() if k}
        e = _row_to_event(fl, mapping, sev_scale)
        if e is None and not hinted:
            hinted = True
            STATS["note"].append(f"{os.path.basename(path)}: no timestamp column recognised. Columns seen: {', '.join(list(fl)[:30])}. Map the time column with --map t=<column>.")
        if e is None:
            STATS["no_time"] += 1
            continue
        e["raw"] = raw_of(r)
        yield e


FORMATS = {
    "eve": "Suricata EVE JSON", "zeek_tsv": "Zeek TSV log", "zeek_json": "Zeek JSON log", "syslog": "syslog / auth.log (sshd, sudo)",
    "winevent": "Windows Security events (JSON)", "cef": "CEF", "ndjson": "generic JSON lines", "json_array": "generic JSON array",
    "csv": "generic CSV/TSV", "text": "unstructured text", "empty": "empty file",
}


def parse(path, opts=None, fmt=None):
    """Yield canonical events from path. Returns (generator, format_id)."""
    opts = opts or {}
    fmt = fmt or detect(path)
    if fmt == "eve":
        g = parse_eve(path, opts)
    elif fmt == "zeek_tsv":
        g = parse_zeek(path, opts, True)
    elif fmt == "zeek_json":
        g = parse_zeek(path, opts, False)
    elif fmt == "syslog":
        g = parse_syslog(path, opts)
    elif fmt == "winevent":
        g = parse_winevent(path, opts)
    elif fmt == "cef":
        g = parse_cef(path, opts)
    elif fmt in ("ndjson", "json_array", "csv"):
        if fmt == "json_array":  # array of Windows events?
            pass
        g = parse_generic(path, opts, fmt)
    else:
        g = iter(())
    return g, fmt
