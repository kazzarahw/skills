#!/usr/bin/env python3
"""soc_dash.py - turn security logs into one self-contained interactive HTML dashboard.

  soc_dash.py profile FILE...            what is in the data (formats, fields, time range, suggested panels)
  soc_dash.py build   FILE... -o out.html [--config cfg.json] [--title T] [--accent '#0000f2']

stdlib only (Python 3.8+). Run with --help on either subcommand for options.
"""
import argparse, array, base64, collections, hashlib, ipaddress, json, os, random, re, struct, sys, zlib, datetime as dt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parsers as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")

STR_FIELDS = ["kind", "act", "src", "dst", "proto", "sig", "cat", "tac", "user", "host", "app", "st", "ua", "msg", "out"]
NUM_FIELDS = ["t", "sev", "sport", "dport", "bytes"]
BULK = {"flow", "conn", "dns", "http", "tls", "ssl", "files", "fileinfo", "smb", "dhcp", "rdp", "ssh_flow"}
RAW_KINDS_DEFAULT = {"alert", "auth", "priv", "session", "event", "notice"}
RESERVOIR = 100000
MAX_MAIN = 500000
RAW_BUDGET = 24_000_000   # uncompressed bytes of original log lines we are willing to embed

PRIVATE = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16", "fc00::/7", "fe80::/10", "::1/128", "100.64.0.0/10")]
_pub_cache = {}


def is_public(ip):
    if ip is None:
        return None
    r = _pub_cache.get(ip)
    if r is None:
        try:
            a = ipaddress.ip_address(ip)
            r = not any(a in n for n in PRIVATE) and not a.is_multicast and not a.is_unspecified
        except ValueError:
            r = None
        _pub_cache[ip] = r
    return r


# ------------------------------------------------------------------ columns
class Columns:
    def __init__(self):
        self.n = 0
        self.num = {k: [] for k in NUM_FIELDS}
        self.dic = {k: {} for k in STR_FIELDS}       # value -> idx
        self.vals = {k: [] for k in STR_FIELDS}      # idx -> value
        self.idx = {k: [] for k in STR_FIELDS}
        self.raw = []
        self.raw_bytes = 0

    def add(self, e, keep_raw):
        for k in NUM_FIELDS:
            v = e.get(k)
            self.num[k].append(-1 if v is None else v)
        for k in STR_FIELDS:
            v = e.get(k)
            if v is None:
                self.idx[k].append(-1)
            else:
                v = str(v)
                d = self.dic[k]
                i = d.get(v)
                if i is None:
                    i = d[v] = len(self.vals[k])
                    self.vals[k].append(v)
                self.idx[k].append(i)
        r = e.get("raw") if keep_raw and self.raw_bytes < 2 * RAW_BUDGET else None   # stop accumulating; all-or-nothing is decided in to_payload
        if r:
            self.raw_bytes += len(r)
        self.raw.append(r or "")
        self.n += 1

    def sort_by_time(self):
        order = sorted(range(self.n), key=self.num["t"].__getitem__)
        for k in NUM_FIELDS:
            a = self.num[k]
            self.num[k] = [a[i] for i in order]
        for k in STR_FIELDS:
            a = self.idx[k]
            self.idx[k] = [a[i] for i in order]
        self.raw = [self.raw[i] for i in order]


def collect(files, opts, fmt_override=None, max_main=MAX_MAIN, raw_mode="auto"):
    """Parse all files into Columns; bulk kinds are reservoir-sampled. Returns (cols, meta)."""
    rng = random.Random(1337)
    cols = Columns()
    seen = collections.Counter()
    reservoirs = {}
    main_kept = 0
    skipped_time = 0
    formats = []
    per_file = []
    main_stride_drop = 0
    notes = []
    for path in files:
        if not os.path.isfile(path):
            sys.exit(f"not found: {path}")
        if not os.access(path, os.R_OK):
            sys.exit(f"not readable: {path}")
        P.STATS["bad_json"] = 0
        P.STATS["no_time"] = 0
        P.STATS["note"] = []
        gen, fmt = P.parse(path, opts, fmt_override)
        n_ok = 0
        for e in gen:
            n_ok += 1
            k = e.get("kind", "event")
            seen[k] += 1
            if k in BULK:
                res = reservoirs.setdefault(k, [])
                if raw_mode != "all":
                    e.pop("raw", None)
                if len(res) < RESERVOIR:
                    res.append(e)
                else:
                    j = rng.randint(0, seen[k] - 1)
                    if j < RESERVOIR:
                        res[j] = e
            else:
                if main_kept >= max_main:
                    main_stride_drop += 1
                    continue
                keep = raw_mode == "all" or (raw_mode == "auto" and k in RAW_KINDS_DEFAULT)
                cols.add(e, keep)
                main_kept += 1
        formats.append(fmt)
        bn = os.path.basename(path)
        per_file.append({"file": bn, "format": fmt, "label": P.FORMATS.get(fmt, fmt), "events": n_ok, "bad_records": P.STATS["bad_json"], "no_time": P.STATS["no_time"]})
        notes.extend(P.STATS["note"])
        if P.STATS["no_time"]:
            notes.append(f"{bn}: {P.STATS['no_time']:,} records had no parsable timestamp and were left out.")
        if P.STATS["bad_json"]:
            notes.append(f"{bn}: {P.STATS['bad_json']:,} lines were not valid JSON and were skipped.")
        if fmt in ("text", "empty"):
            notes.append(f"{bn}: format not recognised; nothing parsed (see references/data-sources.md).")
    kept = collections.Counter()
    for k, res in reservoirs.items():
        for e in res:
            cols.add(e, raw_mode == "all")
        kept[k] = len(res)
    for k in seen:
        if k not in BULK:
            kept[k] = seen[k]
    cols.sort_by_time()
    weights = {}
    # weights: seen / kept for bulk kinds (1.0 otherwise)
    for k in seen:
        if k in BULK and kept[k]:
            weights[k] = round(seen[k] / kept[k], 4)
    samp = [f"{k} \u00d7{v:.1f}" for k, v in weights.items() if v > 1]
    if samp:
        notes.append("Bulk event kinds were sampled (" + ", ".join(samp) + "); their counts are scaled and marked \u2248.")
    if main_stride_drop:
        notes.append(f"{main_stride_drop:,} alert/auth events beyond the {max_main:,}-event cap were left out (latest in file order).")
    meta = {"files": per_file, "seen": dict(seen), "weights": weights, "truncated_main": main_stride_drop, "notes": notes,
            "events_embedded": cols.n, "events_seen": sum(seen.values())}
    return cols, meta


# ------------------------------------------------------------------ helpers
def fmt_dur(ms):
    s = ms / 1000
    if s < 90:
        return f"{s:.0f} s"
    if s < 5400:
        return f"{s / 60:.0f} min"
    if s < 172800:
        return f"{s / 3600:.1f} h".replace(".0 h", " h")
    return f"{s / 86400:.1f} d"


def fmt_bytes(b):
    for u in ('B', 'KB', 'MB', 'GB', 'TB'):
        if b < 1000 or u == 'TB':
            return f"{b:.0f} {u}" if u == 'B' else f"{b:.1f} {u}"
        b /= 1000


def fmt_ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def decode(cols, k):
    v = cols.vals[k]
    return [v[i] if i >= 0 else None for i in cols.idx[k]]


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return 0 if not n else xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


# ------------------------------------------------------------------ signals
def compute_signals(cols, weights):
    """Transparent, rule-based signals. Every signal carries its rule and evidence; none asserts compromise."""
    n = cols.n
    if n == 0:
        return []
    t = cols.num["t"]
    kind, src, dst, sig, user, out, act = (decode(cols, k) for k in ("kind", "src", "dst", "sig", "user", "out", "act"))
    dport = cols.num["dport"]
    sev = cols.num["sev"]
    sigs = []
    t_min, t_max = t[0], t[-1]

    # 1. bursts of alert/auth activity
    sig_idx = [i for i in range(n) if kind[i] in ("alert", "auth")]
    if len(sig_idx) >= 50 and t_max > t_min:
        span = t_max - t_min
        target = span / 200
        width = next((w for w in (60e3, 300e3, 900e3, 3600e3, 10800e3, 21600e3, 86400e3) if w >= target), 86400e3)
        base = (t_min // width) * width
        b = collections.Counter(int((t[i] - base) // width) for i in sig_idx)
        nb = int((t_max - base) // width) + 1
        counts = [b.get(j, 0) for j in range(nb)]
        med = median(counts)
        mad = median([abs(c - med) for c in counts]) * 1.4826
        thr = max(20, med + 8 * mad, 4 * med)
        flagged = [j for j, c in enumerate(counts) if c >= thr]
        groups = []
        for j in flagged:
            if groups and j - groups[-1][-1] <= 1:
                groups[-1].append(j)
            else:
                groups.append([j])
        ranked = sorted(groups, key=lambda g: -sum(counts[j] for j in g))[:3]
        for g in ranked:
            lo, hi = base + g[0] * width, base + (g[-1] + 1) * width
            ids = [i for i in sig_idx if lo <= t[i] < hi]
            tot = len(ids)
            ts_ = collections.Counter(src[i] for i in ids if src[i])
            tg = collections.Counter(sig[i] for i in ids if sig[i])
            body = f"{tot:,} alert/auth events in {fmt_dur(hi - lo)}, {tot / max(1, med * len(g)):.1f}× the typical bucket."
            filters = {}
            if ts_:
                s0, c0 = ts_.most_common(1)[0]
                body += f" {c0 / tot:.0%} came from {s0}."
                if c0 / tot >= 0.5:
                    filters["src"] = [s0]
            if tg:
                s1, c1 = tg.most_common(1)[0]
                body += f" Top rule: {s1} ({c1 / tot:.0%})."
            sigs.append(dict(id=f"burst-{g[0]}", lvl="med", title=f"Burst at {fmt_ts(lo)[5:16]} UTC", body=body, t0=lo, t1=hi, n=tot, filters=filters,
                             rule=f"{fmt_dur(width)} buckets of alert+auth events; flagged when ≥ max(20, median+8·MAD, 4×median) (median {med:.0f})."))

    # 2. periodic (beacon-like) traffic per src→dst:port
    pairs = collections.defaultdict(list)
    for i in range(n):
        if dst[i] and src[i] and kind[i] in ("alert", "conn", "flow", "http", "tls"):
            pairs[(src[i], dst[i], dport[i])].append(i)
    found = []
    for key, ids in pairs.items():
        if len(ids) < 12:
            continue
        ts_ = [t[i] for i in ids]
        gaps = [b - a for a, b in zip(ts_, ts_[1:]) if b > a]
        if len(gaps) < 11:
            continue
        m = median(gaps)
        if m < 1000 or m > 6 * 3600e3:
            continue
        within = sum(1 for g in gaps if abs(g - m) <= 0.25 * m) / len(gaps)
        if within >= 0.8 and (ts_[-1] - ts_[0]) >= 10 * m:
            top_sev = max((sev[i] for i in ids), default=-1)
            found.append((len(ids) * within, key, ids, m, within, ts_[0], ts_[-1], top_sev))
    found.sort(key=lambda x: -x[0])
    for _, key, ids, m, within, t0, t1, top_sev in found[:3]:
        s_, d_, p_ = key
        names = collections.Counter(sig[i] for i in ids if sig[i])
        nm = names.most_common(1)[0][0] if names else None
        lvl = "high" if top_sev >= 3 else "med"
        sigs.append(dict(id=f"periodic-{s_}-{d_}-{p_}", lvl=lvl, title=f"Periodic traffic {s_} → {d_}" + (f":{p_}" if p_ and p_ > 0 else ""),
                         body=f"{len(ids):,} events about every {fmt_dur(m)} for {fmt_dur(t1 - t0)}; {within:.0%} of gaps within ±25% of the median." +
                              (f" Rule: {nm}." if nm else "") + " Timing regularity is consistent with beaconing or automation; updaters, monitoring and NTP look the same, so check the destination.",
                         t0=t0, t1=t1 + 1, n=len(ids), filters={"src": [s_], "dst": [d_]},
                         rule="≥12 events for one src→dst:port with median gap 1 s–6 h; ≥80% of gaps within ±25% of the median; span ≥10 gaps."))

    # 3. auth: a burst of failures from one source, then a success (or a spray/brute force with no success)
    by_src = collections.defaultdict(list)
    for i in range(n):
        if kind[i] == "auth" and src[i] and out[i]:
            by_src[src[i]].append(i)
    follow_by_user = collections.defaultdict(list)
    for i in range(n):
        if kind[i] == "priv" and user[i]:
            follow_by_user[user[i]].append(i)
    msg = decode(cols, "msg")

    def describe(i):
        return " ".join(x for x in (sig[i], msg[i]) if x)[:70]

    for s_, ids in by_src.items():
        fails = [i for i in ids if out[i] == "failure"]
        if len(fails) < 10:
            continue
        bursts, cur = [], [fails[0]]
        for f in fails[1:]:
            if t[f] - t[cur[-1]] <= 600e3:
                cur.append(f)
            else:
                bursts.append(cur)
                cur = [f]
        bursts.append(cur)
        bursts = [b for b in bursts if len(b) >= 10]
        if not bursts:
            continue
        b = max(bursts, key=len)
        bt0, bt1 = t[b[0]], t[b[-1]]
        users_b = collections.Counter(user[i] for i in b if user[i])
        pub = is_public(s_)
        succ = next((i for i in ids if out[i] == "success" and bt0 <= t[i] <= bt1 + 1800e3), None)
        who = f"{len(users_b)} account name{'s' if len(users_b) != 1 else ''}"
        if succ is not None:
            u = user[succ]
            follow = [p for p in follow_by_user.get(u, []) if 0 <= t[p] - t[succ] <= 600e3] if u else []
            extra = ""
            if follow:
                seen_d = []
                for p in follow:
                    d = describe(p)
                    if d not in seen_d:
                        seen_d.append(d)
                extra = f" Within 10 min the same account then: {'; '.join(seen_d[:4])}."
            sigs.append(dict(id=f"brute-success-{s_}", lvl="high", title=f"Login succeeded after {len(b):,} failures from {s_}",
                             body=f"{s_} ({'public' if pub else 'internal'}) made {len(b):,} failed attempts in {fmt_dur(bt1 - bt0)} against {who}, then logged in as {u or 'an account'} at {fmt_ts(t[succ])} UTC, {fmt_dur(max(0, t[succ] - bt1))} after its last failure.{extra} Consistent with a successful guess; confirm whether this login was expected.",
                             t0=bt0, t1=t[succ] + 1, n=len(b) + 1, filters={"src": [s_]},
                             rule="≥10 failures from one source with gaps ≤10 min, followed by a success from the same source before the burst ends or within 30 min after."))
        elif len(users_b) >= 15:
            sigs.append(dict(id=f"spray-{s_}", lvl="med", title=f"One source tried {len(users_b)} accounts: {s_}",
                             body=f"{len(b):,} failures across {who} in {fmt_dur(bt1 - bt0)} (top: {', '.join(u for u, _ in users_b.most_common(3))}). Pattern of password spraying or username guessing; no success from this source.",
                             t0=bt0, t1=bt1 + 1, n=len(b), filters={"src": [s_]},
                             rule="≥10 failures from one source (gaps ≤10 min) across ≥15 distinct accounts, no success."))
        elif len(b) >= 20:
            sigs.append(dict(id=f"brute-{s_}", lvl="med", title=f"Repeated failed logins from {s_}",
                             body=f"{len(b):,} failures in {fmt_dur(bt1 - bt0)} against {', '.join(list(users_b)[:3]) or who}. No success from this source in the data.",
                             t0=bt0, t1=bt1 + 1, n=len(b), filters={"src": [s_]},
                             rule="≥20 failures from one source (gaps ≤10 min) against <15 accounts, no success."))
    # privileged changes (Windows): account creation and group-membership additions
    chg = [i for i in range(n) if sig[i] and sig[i][:4] in ("4720", "4728", "4732", "4756")]
    if chg:
        lines = [f"{fmt_ts(t[i])[5:16]} {user[i] or '?'}: {sig[i][5:]} ({msg[i]})" if msg[i] else f"{fmt_ts(t[i])[5:16]} {user[i] or '?'}: {sig[i][5:]}" for i in chg[:3]]
        sigs.append(dict(id="priv-change", lvl="med", title=f"{len(chg)} account or privileged-group change{'s' if len(chg) != 1 else ''}",
                         body="; ".join(lines) + ("; …" if len(chg) > 3 else "") + ". Confirm each was an approved change.",
                         t0=t[chg[0]], t1=t[chg[-1]] + 1, n=len(chg), filters={"sig": sorted({sig[i] for i in chg})},
                         rule="Windows events 4720 (account created), 4728/4732/4756 (member added to a group)."))
    # 4. scans: many ports/hosts from one source in 10 minutes
    win = collections.defaultdict(lambda: [set(), set(), 0, None])
    for i in range(n):
        if src[i] and dst[i] and kind[i] in ("alert", "conn", "flow"):
            w = win[(src[i], int(t[i] // 600e3))]
            w[0].add(dport[i]); w[1].add(dst[i]); w[2] += 1
            if w[3] is None:
                w[3] = i
    scan = collections.defaultdict(lambda: [0, 0, 0, None, None])
    for (s_, bk), (ports, hosts, cnt, _first) in win.items():
        if cnt >= 30 and (len(ports) >= 15 or len(hosts) >= 25):
            r = scan[s_]
            r[0] = max(r[0], len(ports)); r[1] = max(r[1], len(hosts)); r[2] += cnt
            lo_, hi_ = bk * 600e3, (bk + 1) * 600e3
            r[3] = lo_ if r[3] is None else min(r[3], lo_)
            r[4] = hi_ if r[4] is None else max(r[4], hi_)
    for s_, (np_, nh, cnt, lo_, hi_) in sorted(scan.items(), key=lambda kv: -kv[1][2])[:3]:
        sigs.append(dict(id=f"scan-{s_}", lvl="med", title=f"Scan-like activity from {s_}",
                         body=f"{cnt:,} events touching up to {np_} ports and {nh} hosts within single 10-minute windows.",
                         t0=lo_, t1=hi_, n=cnt, filters={"src": [s_]},
                         rule="≥30 events from one source in a 10-min window touching ≥15 distinct ports or ≥25 distinct hosts."))
    # 4b. one src->dst pair carrying a large share of all bytes
    nbytes = cols.num["bytes"]
    tot_b, pair_b, pair_i = 0.0, collections.Counter(), collections.defaultdict(list)
    for i in range(n):
        if nbytes[i] > 0:
            w = weights.get(kind[i], 1.0)
            tot_b += nbytes[i] * w
            if src[i] and dst[i]:
                pair_b[(src[i], dst[i])] += nbytes[i] * w
                pair_i[(src[i], dst[i])].append(i)
    if tot_b >= 50e6 and pair_b:
        (s_, d_), pb = pair_b.most_common(1)[0]
        if pb >= 100e6 and pb / tot_b >= 0.15:
            ids = pair_i[(s_, d_)]
            sigs.append(dict(id=f"transfer-{s_}-{d_}", lvl="med", title=f"Large transfer {s_} → {d_}",
                             body=f"{fmt_bytes(pb)} moved between these two addresses in {len(ids):,} connections, {pb / tot_b:.0%} of all {fmt_bytes(tot_b)} in the data. Check whether {d_} is an expected destination (backup, sync, update) for {s_}.",
                             t0=t[ids[0]], t1=t[ids[-1]] + 1, n=len(ids), filters={"src": [s_], "dst": [d_]},
                             rule="One src→dst pair accounts for ≥15% of all bytes and ≥100 MB."))
    # 5. audit log cleared
    for i in range(n):
        if sig[i] and sig[i].startswith("1102"):
            sigs.append(dict(id=f"audit-cleared-{i}", lvl="high", title="Windows audit log cleared", body=f"Event 1102 at {fmt_ts(t[i])} UTC. Clearing the Security log removes evidence; confirm it was an approved action.",
                             t0=t[i], t1=t[i] + 1, n=1, filters={"sig": [sig[i]]}, rule="Event ID 1102 present."))
            break
    # 6. detect-only sensor
    n_alert = sum(1 for i in range(n) if kind[i] == "alert" and act[i])
    if n_alert >= 20 and not any(act[i] in ("blocked", "drop", "dropped", "reject", "rejected", "deny", "denied") for i in range(n) if kind[i] == "alert"):
        sigs.append(dict(id="detect-only", lvl="info", title="No alert was blocked",
                         body=f"All {n_alert:,} alerts carry an allowed/alert-only action, so the sensor appears to be in detection mode. High-severity hits were not stopped inline.",
                         t0=t_min, t1=t_max + 1, n=n_alert, filters={}, rule="Every alert with an action field has a non-blocking action."))
    order = {"high": 0, "med": 1, "info": 2}
    sigs.sort(key=lambda s: (order[s["lvl"]], -s["n"]))
    return sigs[:12]


# ------------------------------------------------------------------ profile
def profile(cols, meta):
    n = cols.n
    kinds = collections.Counter(decode(cols, "kind"))
    cov = {}
    for k in STR_FIELDS:
        c = sum(1 for i in cols.idx[k] if i >= 0)
        cov[k] = c
    for k in NUM_FIELDS:
        cov[k] = sum(1 for v in cols.num[k] if v >= 0)
    top = {}
    for k in ("kind", "sev", "out", "act", "sig", "cat", "tac", "src", "dst", "user", "app", "st", "host", "ua"):
        if k == "sev":
            c = collections.Counter(cols.num["sev"][i] for i in range(n) if cols.num["sev"][i] >= 0)
            top[k] = [(str(a), b) for a, b in c.most_common(5)]
        else:
            c = collections.Counter(cols.idx[k])
            c.pop(-1, None)
            top[k] = [(cols.vals[k][a], b) for a, b in c.most_common(5)]
    uniq = {k: len(cols.vals[k]) for k in STR_FIELDS}
    pub_src = sum(1 for v in cols.vals["src"] if is_public(v))
    return dict(n=n, kinds=dict(kinds), coverage_pct={k: round(100 * v / n, 1) if n else 0 for k, v in cov.items()}, unique=uniq,
                top=top, public_src=pub_src, t0=cols.num["t"][0] if n else None, t1=cols.num["t"][-1] if n else None)


def suggest_profile(prof):
    n = max(1, prof["n"])
    k = prof["kinds"]
    cov = prof["coverage_pct"]
    alert, auth = k.get("alert", 0) / n, (k.get("auth", 0) + k.get("priv", 0) + k.get("session", 0)) / n
    flowish = (k.get("flow", 0) + k.get("conn", 0)) / n
    if alert >= 0.25:
        return "alerts"
    if auth >= 0.4:
        return "auth"
    if flowish >= 0.4 and alert < 0.1:
        return "flows"
    if cov.get("sig", 0) > 50 and cov.get("sev", 0) > 30:
        return "alerts"
    if cov.get("out", 0) > 50 and cov.get("user", 0) > 30:
        return "auth"
    return "mixed"


def default_config(prof, kind_profile):
    """Panels chosen from the data; the agent should review and edit this (see references/panels.md)."""
    cov, uniq, kinds = prof["coverage_pct"], prof["unique"], prof["kinds"]
    has = lambda f, pct=8, u=2: cov.get(f, 0) >= pct and uniq.get(f, 99) >= u  # noqa: E731
    panels = []
    if kind_profile == "alerts":
        where = {"kind": ["alert"]}
        panels.append({"type": "kpis", "items": [
            {"label": "Alerts", "agg": "count", "where": where},
            {"label": "High + critical", "agg": "count", "where": {**where, "sev": ["3", "4"]}},
            {"label": "Distinct sources", "agg": "uniq", "field": "src", "where": where},
            {"label": "Distinct targets", "agg": "uniq", "field": "dst", "where": where},
            {"label": "Rules fired", "agg": "uniq", "field": "sig", "where": where}]})
        panels.append({"type": "signals"})
        panels.append({"type": "timeline", "title": "Alerts over time", "by": "sev", "where": where, "w": 12})
        right = [{"type": "heat", "title": "When alerts fire", "where": where}]
        if has("cat"):
            right.append({"type": "rank", "title": "Category", "field": "cat", "where": where, "limit": 6})
        panels.append({"type": "rank", "title": "Rules", "field": "sig", "where": where, "w": 8, "limit": 12})
        panels.append({"type": "stack", "w": 4, "panels": right})
        if has("src"):
            panels.append({"type": "rank", "title": "Sources", "field": "src", "where": where, "w": 4})
        if has("dst"):
            panels.append({"type": "rank", "title": "Targets", "field": "dst", "where": where, "w": 4})
        if has("dport"):
            panels.append({"type": "rank", "title": "Destination ports", "field": "dport", "where": where, "w": 4})
        if has("tac"):
            panels.append({"type": "rank", "title": "ATT&CK tactic", "field": "tac", "where": where, "w": 4})
        if has("ua", 3):
            panels.append({"type": "rank", "title": "HTTP user-agents", "field": "ua", "where": where, "w": 4})
        panels.append({"type": "table", "title": "Events", "where": where, "columns": ["t", "sev", "sig", "src", "dst", "dport", "act"]})
        hero = "sev"
    elif kind_profile == "auth":
        where = {"kind": ["auth"]}
        panels.append({"type": "kpis", "items": [
            {"label": "Failed", "agg": "count", "where": {**where, "out": ["failure"]}},
            {"label": "Succeeded", "agg": "count", "where": {**where, "out": ["success"]}},
            {"label": "Sources with failures", "agg": "uniq", "field": "src", "where": {**where, "out": ["failure"]}},
            {"label": "Accounts targeted", "agg": "uniq", "field": "user", "where": {**where, "out": ["failure"]}}]})
        panels.append({"type": "signals"})
        panels.append({"type": "timeline", "title": "Logins over time", "by": "out", "where": where, "w": 12})
        panels.append({"type": "rank", "title": "Sources of failures", "field": "src", "where": {**where, "out": ["failure"]}, "w": 4})
        panels.append({"type": "rank", "title": "Accounts targeted", "field": "user", "where": {**where, "out": ["failure"]}, "w": 4})
        panels.append({"type": "rank", "title": "Successful logins by account", "field": "user", "where": {**where, "out": ["success"]}, "w": 4})
        panels.append({"type": "heat", "title": "When logins happen", "where": where, "w": 4})
        if has("msg"):
            panels.append({"type": "rank", "title": "Method / detail", "field": "msg", "where": where, "w": 4})
        if has("host"):
            panels.append({"type": "rank", "title": "Host", "field": "host", "where": where, "w": 4})
        panels.append({"type": "table", "title": "Events", "columns": ["t", "out", "user", "src", "sig", "msg", "host"]})
        hero = "out"
    elif kind_profile == "flows":
        where = {"kind": [k for k in ("conn", "flow") if kinds.get(k)] or ["conn"]}
        panels.append({"type": "kpis", "items": [
            {"label": "Connections", "agg": "count", "where": where},
            {"label": "Traffic", "agg": "sum", "field": "bytes", "where": where, "unit": "bytes"},
            {"label": "Distinct sources", "agg": "uniq", "field": "src", "where": where},
            {"label": "Distinct destinations", "agg": "uniq", "field": "dst", "where": where}]})
        panels.append({"type": "signals"})
        panels.append({"type": "timeline", "title": "Traffic over time", "by": "app" if has("app", 20, 2) else "kind", "value": "bytes", "where": where, "w": 12})
        panels.append({"type": "rank", "title": "Destinations by bytes", "field": "dst", "value": "bytes", "where": where, "w": 4})
        panels.append({"type": "rank", "title": "Sources by bytes", "field": "src", "value": "bytes", "where": where, "w": 4})
        panels.append({"type": "rank", "title": "Destination ports", "field": "dport", "where": where, "w": 4})
        if has("app", 20):
            panels.append({"type": "rank", "title": "Service", "field": "app", "where": where, "w": 4})
        if has("st", 20):
            panels.append({"type": "rank", "title": "Connection state", "field": "st", "where": where, "w": 4})
        panels.append({"type": "heat", "title": "When traffic flows", "where": where, "w": 4})
        panels.append({"type": "table", "title": "Connections", "where": where, "columns": ["t", "src", "dst", "dport", "app", "st", "bytes"]})
        hero = "bytes"
    else:
        panels.append({"type": "kpis", "items": [{"label": "Events", "agg": "count"}, {"label": "Distinct sources", "agg": "uniq", "field": "src"}, {"label": "Distinct targets", "agg": "uniq", "field": "dst"}]})
        panels.append({"type": "signals"})
        panels.append({"type": "timeline", "title": "Events over time", "by": "kind", "w": 12})
        for f, title in (("kind", "Event kind"), ("sig", "Rule / event"), ("src", "Sources"), ("dst", "Targets"), ("user", "Accounts")):
            if has(f):
                panels.append({"type": "rank", "title": title, "field": f, "w": 4})
        panels.append({"type": "heat", "title": "Activity by hour", "w": 4})
        panels.append({"type": "table", "title": "Events", "columns": ["t", "kind", "sig", "src", "dst", "user"]})
        hero = "kind"
    return {"profile": kind_profile, "hero": hero, "panels": panels}


def drop_absent_kinds(panels, kinds):
    """A default panel must never filter on an event kind that is not in the data (it would render empty)."""
    def fix(w):
        if not w or "kind" not in w:
            return w
        present = [k for k in w["kind"] if kinds.get(k)]
        w = dict(w)
        if present:
            w["kind"] = present
        else:
            w.pop("kind")
        return w or None
    out = []
    for p in panels:
        p = dict(p)
        if "where" in p:
            nw = fix(p["where"])
            if nw:
                p["where"] = nw
            else:
                p.pop("where")
        if p.get("type") == "kpis":
            p["items"] = [dict(i, **({"where": fix(i["where"])} if fix(i.get("where")) else {})) if "where" in i else i for i in p["items"]]
            for i in p["items"]:
                if i.get("where") is None:
                    i.pop("where", None)
        if p.get("type") == "stack":
            p["panels"] = drop_absent_kinds(p["panels"], kinds)
        out.append(p)
    return out


# ------------------------------------------------------------------ build
def to_payload(cols, meta, signals):
    """Pack into one deflate-compressed blob: [u32 json_len][json][pad to 8][typed-array columns].

    JSON holds dictionaries, raw lines (only if they fit RAW_BUDGET), meta, signals and the column layout;
    the numeric/index columns are raw little-endian typed arrays. The page inflates it with DecompressionStream.
    """
    arrays, layout, off = [], [], 0

    def put(name, typ, data):
        nonlocal off
        a = array.array("d" if typ == "f64" else "i", data)
        if sys.byteorder == "big":
            a.byteswap()
        raw = a.tobytes()
        pad = (-len(raw)) % 8
        layout.append({"k": name, "type": typ, "off": off, "len": len(a)})
        arrays.append(raw + b"\0" * pad)
        off += len(raw) + pad

    put("t", "f64", cols.num["t"])
    put("bytes", "f64", cols.num["bytes"])
    for k in ("sev", "sport", "dport"):
        put(k, "i32", cols.num[k])
    strs = {}
    for k in STR_FIELDS:
        if cols.vals[k]:
            strs[k] = cols.vals[k]
            put("s:" + k, "i32", cols.idx[k])
    keep_raw = any(cols.raw) and cols.raw_bytes <= RAW_BUDGET
    meta = dict(meta, raw="kept" if keep_raw else ("omitted: original lines exceed the embed budget; use --raw all to force" if any(cols.raw) else "none"))
    if any(cols.raw) and not keep_raw:
        meta["notes"] = list(meta.get("notes", [])) + ["Original log lines are not embedded (they exceed the size budget); the detail drawer shows parsed fields only. Search the source file by time and address."]
    head = json.dumps({"n": cols.n, "layout": layout, "str": strs, "raw": cols.raw if keep_raw else None, "meta": meta, "signals": signals},
                      separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    hdr = struct.pack("<I", len(head)) + head
    hdr += b"\0" * ((-len(hdr)) % 8)
    blob = zlib.compress(hdr + b"".join(arrays), 9)
    return {"b64": base64.b64encode(blob).decode("ascii"), "n": cols.n}


def js_json(obj):
    """JSON safe to embed in <script type=application/json>: no '<' (kills </script> and <!--) and no U+2028/9."""
    s = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return s.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace(">", "\\u003e").replace("&", "\\u0026")


def assemble(payload, cfg):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    m = re.search(r"<script id=\"soc-app\">(.*?)</script>", tpl, re.S)
    st = re.search(r"<style id=\"soc-style\">(.*?)</style>", tpl, re.S)
    if not m or not st:
        sys.exit("template.html is missing <script id=\"soc-app\"> or <style id=\"soc-style\">")
    h_js = base64.b64encode(hashlib.sha256(m.group(1).encode("utf-8")).digest()).decode()
    h_css = base64.b64encode(hashlib.sha256(st.group(1).encode("utf-8")).digest()).decode()
    csp = f"default-src 'none'; script-src 'sha256-{h_js}'; style-src 'sha256-{h_css}'; img-src data:; base-uri 'none'; form-action 'none'"
    out = tpl.replace("__CSP__", csp)
    out = out.replace("<!--__CFG__-->", f'<script type="application/json" id="soc-cfg">{js_json(cfg)}</script>')
    out = out.replace("<!--__DATA__-->", f'<script type="application/json" id="soc-data">{js_json(payload)}</script>')
    out = out.replace("__TITLE__", (cfg.get("title") or "Security dashboard").replace("<", "").replace(">", "").replace("&", "and")[:120])
    return out


def contrast(hex_a, hex_b):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a, b = sorted((lum(hex_a), lum(hex_b)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def parse_tz(s):
    if not s:
        return 0
    m = re.fullmatch(r"([+-])(\d{1,2}):?(\d{2})?", s.strip())
    if not m:
        sys.exit(f"--tz must look like +02:00 or -0500, got {s!r}")
    return (-1 if m.group(1) == "-" else 1) * (int(m.group(2)) * 60 + int(m.group(3) or 0))


def common_args(ap):
    ap.add_argument("files", nargs="+")
    ap.add_argument("--format", choices=sorted(P.FORMATS), help="force a format instead of auto-detecting")
    ap.add_argument("--year", type=int, help="year for year-less syslog timestamps (default: file mtime year)")
    ap.add_argument("--tz", help="UTC offset of timestamps that carry none, e.g. -05:00 (default UTC)")
    ap.add_argument("--map", action="append", default=[], metavar="CANON=field", help="generic JSON/CSV only (ignored by eve/zeek/syslog/winevent/cef): map a canonical field to a source field, e.g. --map src=client.addr (repeatable)")
    ap.add_argument("--sev-scale", choices=["inv3", "0-10", "0-100"], help="numeric severity scale when the source is ambiguous (inv3: 1=highest of 3)")


def opts_from(a):
    mp = {}
    for kv in a.map:
        if "=" not in kv:
            sys.exit(f"--map expects CANON=field, got {kv!r}")
        k, v = kv.split("=", 1)
        mp[k] = v
    return {"year": a.year, "tz_min": parse_tz(a.tz), "map": mp, "sev_scale": a.sev_scale}


def cmd_profile(a):
    cols, meta = collect(a.files, opts_from(a), a.format)
    prof = profile(cols, meta)
    kp = suggest_profile(prof)
    if a.json:
        print(json.dumps({"meta": meta, "profile": prof, "suggested_profile": kp, "default_config": default_config(prof, kp)}, indent=1, default=str))
        return
    w = print
    w("FILES")
    for f in meta["files"]:
        w(f"  {f['file']}: {f['label']} - {f['events']:,} events parsed" + (f", {f['bad_records']} unparseable records skipped" if f["bad_records"] else ""))
    if not prof["n"]:
        w("\nNo events parsed. Check the format with --format or map fields with --map (see references/data-sources.md).")
        for n_ in meta["notes"]:
            w("NOTE  " + n_)
        sys.exit(1)
    w(f"\nTIME  {fmt_ts(prof['t0'])} → {fmt_ts(prof['t1'])} UTC  ({fmt_dur(prof['t1'] - prof['t0'])})")
    w(f"EVENTS  {meta['events_seen']:,} seen, {prof['n']:,} embedded" + (f"  (sampled kinds: {', '.join(f'{k} ×{v}' for k, v in meta['weights'].items() if v > 1)})" if any(v > 1 for v in meta["weights"].values()) else ""))
    w("KINDS  " + ", ".join(f"{k} {v:,}" for k, v in sorted(prof["kinds"].items(), key=lambda kv: -kv[1])))
    w("\nFIELD COVERAGE (% of events) and distinct values")
    for k in NUM_FIELDS[1:] + STR_FIELDS[1:]:
        c = prof["coverage_pct"].get(k, 0)
        if c:
            u = prof["unique"].get(k)
            tv = ", ".join(f"{v}({c2})" for v, c2 in prof["top"].get(k, [])[:3]) if k in prof["top"] else ""
            w(f"  {k:6} {c:5.1f}%  " + (f"{u:>7,} distinct  " if u else " " * 18) + (tv[:90]))
    for n_ in meta["notes"]:
        w("NOTE  " + n_)
    w(f"\nPUBLIC SOURCES  {prof['public_src']:,} of {prof['unique']['src']:,} distinct source addresses")
    w(f"SUGGESTED PROFILE  {kp}  (hero dimension: {default_config(prof, kp)['hero']})")
    w("Panels: " + ", ".join(p.get("title") or p["type"] for p in default_config(prof, kp)["panels"]))
    w("\nNext: edit panels if the story calls for it (references/panels.md), then build. Use --json for the full default config.")


def cmd_build(a):
    opts = opts_from(a)
    cols, meta = collect(a.files, opts, a.format, raw_mode=a.raw)
    if not cols.n:
        sys.exit("No events parsed; run `profile` and see references/data-sources.md.")
    prof = profile(cols, meta)
    kp = suggest_profile(prof)
    cfg = default_config(prof, kp)
    cfg["panels"] = drop_absent_kinds(cfg["panels"], prof["kinds"])
    if a.config:
        user = json.load(open(a.config, encoding="utf-8"))
        cfg.update({k: v for k, v in user.items() if k != "theme"})
        cfg["theme"] = {**cfg.get("theme", {}), **user.get("theme", {})}
    if a.title:
        cfg["title"] = a.title
    cfg.setdefault("title", "Security dashboard")
    cfg.setdefault("theme", {})
    if a.accent:
        cfg["theme"]["accent"] = a.accent
    accent = cfg["theme"].get("accent", "#0000f2")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        sys.exit("theme.accent must be a #rrggbb hex color")
    cr = contrast(accent, "#f4f4f2")
    if cr < 4.5:
        sys.exit(f"theme.accent {accent} has only {cr:.1f}:1 contrast on the paper color (#f4f4f2); pick a darker ink (>= 4.5:1), e.g. #0000f2, #00635d, #8a1c2b, #1f2937")
    cfg["sources"] = [f["file"] for f in meta["files"]]
    cfg["built"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    signals = compute_signals(cols, meta["weights"])
    html = assemble(to_payload(cols, meta, signals), cfg)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(a.out)
    print(f"wrote {a.out}  ({size / 1e6:.1f} MB)  profile={cfg['profile']}  events embedded {cols.n:,} of {meta['events_seen']:,} seen  signals={len(signals)}")
    for s in signals:
        print(f"  [{s['lvl']:4}] {s['title']}")
    if meta["truncated_main"]:
        print(f"WARNING: {meta['truncated_main']:,} alert/auth events past the {MAX_MAIN:,} cap were dropped (file order); say so in your summary.", file=sys.stderr)
    if any(v > 1 for v in meta["weights"].values()):
        print("NOTE: bulk kinds were sampled (" + ", ".join(f"{k} ×{v}" for k, v in meta["weights"].items() if v > 1) + "); the dashboard scales their counts and marks them approximate.", file=sys.stderr)
    if size > 40e6:
        print("WARNING: output is large; consider --raw none or fewer bulk kinds.", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("profile", help="summarise what the data contains and suggest panels")
    common_args(p1)
    p1.add_argument("--json", action="store_true", help="emit full JSON incl. the default panel config")
    p2 = sub.add_parser("build", help="write the dashboard HTML")
    common_args(p2)
    p2.add_argument("-o", "--out", default="dashboard.html", help="output HTML path; relative paths resolve against the current directory, so give <data-dir>/dashboard.html")
    p2.add_argument("--config", help="JSON file overriding title/theme/panels (see references/panels.md)")
    p2.add_argument("--title", help="page headline (default: derived from the file name, so pass a specific one)")
    p2.add_argument("--accent", help="ink color, #rrggbb (default #0000f2)")
    p2.add_argument("--raw", choices=["auto", "all", "none"], default="auto", help="keep original log lines for the detail drawer: auto = alerts/auth only")
    a = ap.parse_args()
    (cmd_profile if a.cmd == "profile" else cmd_build)(a)


if __name__ == "__main__":
    main()
