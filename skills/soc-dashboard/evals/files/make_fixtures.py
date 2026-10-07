#!/usr/bin/env python3
"""make_fixtures.py - generate small, deterministic, format-true fixtures with planted findings.

Usage: python3 make_fixtures.py OUTDIR

Writes eve.json, auth.log, conn.log, winevents.json. Every headline figure used
in evals/evals.json is derived from the constants below; the generator prints
them so expectations stay in sync. Timestamps are fixed (September 2026);
auth.log relies on file-mtime year, so regenerate any time in 2026+ (or pass
--year explicitly when profiling).
"""
import datetime as dt
import json
import os
import sys

BASE = dt.datetime(2026, 9, 21, 0, 0, 0, tzinfo=dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S.123456+0000")


def eve_alert(t, sig, sev, src, dst, dport=80, cat="Potentially Bad Traffic",
              action="allowed", extra=None):
    o = {"timestamp": iso(t), "event_type": "alert", "src_ip": src,
         "src_port": 40000 + (hash(sig + src) % 20000), "dest_ip": dst,
         "dest_port": dport, "proto": "TCP", "flow_id": 1000 + hash(str(t)) % 999999,
         "alert": {"action": action, "signature": sig, "category": cat, "severity": sev}}
    if extra:
        o.update(extra)
    return o


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)

    # --- eve.json: 128 alerts, 15 severity-1 (=high) -------------------------
    eve = []
    t = BASE
    # background: 80 alerts, sev 2/3 mix, spread over 3 days
    sigs = ["ET MALWARE Possible Trojan", "ET SCAN Nmap Scripting",
            "ET POLICY Outbound Connection", "ET INFO Observed DNS over HTTPS"]
    for i in range(80):
        t += dt.timedelta(minutes=53)
        eve.append(eve_alert(t, sigs[i % 4], 2 if i % 3 else 3,
                             f"198.51.100.{10 + i % 40}", f"203.0.113.{20 + i % 30}",
                             dport=[80, 443, 53, 25][i % 4]))
    # beacon: 15 sev-1 alerts, 10.20.2.77 -> 103.75.201.9:5985, every 300 s
    bt = BASE + dt.timedelta(hours=30)
    for i in range(15):
        bt += dt.timedelta(seconds=300)
        eve.append(eve_alert(bt, "ET CNC Beacon Likely", 1, "10.20.2.77",
                             "103.75.201.9", dport=5985, cat="Command and Control"))
    # scan: 32 sev-2 alerts from 185.220.101.47 across 18 ports in ~5 minutes,
    # aligned inside one clock-aligned 10-minute bucket
    st_epoch = ((int((BASE + dt.timedelta(hours=50)).timestamp()) // 600) + 1) * 600 + 60
    st = dt.datetime.fromtimestamp(st_epoch, tz=dt.timezone.utc)
    for i in range(32):
        eve.append(eve_alert(st + dt.timedelta(seconds=10 * i), "ET SCAN Port Sweep", 2,
                             "185.220.101.47", "203.0.113.7", dport=1000 + i % 18))
    # hostile strings: must render inert
    eve.append(eve_alert(BASE + dt.timedelta(hours=60), "ET POLICY HTTP Request", 3,
                         "198.51.100.99", "203.0.113.9",
                         extra={"http": {"hostname": "example.com",
                                         "url": "/?q=<script>alert('dns')</script>",
                                         "http_user_agent": "<img src=x onerror=alert(1)>",
                                         "status": 200}}))
    with open(os.path.join(out, "eve.json"), "w") as f:
        for o in eve:
            f.write(json.dumps(o) + "\n")
    n_alerts = len(eve)
    n_sev1 = sum(1 for o in eve if (o.get("alert") or {}).get("severity") == 1)

    # --- auth.log: 69 failed logins (8 invalid-user + 1 hostile + 60 brute-force),
    # then a deploy success + sudo --------------------------------------------
    lines = []
    at = BASE.replace(hour=2)
    # background noise: 8 invalid-user failures from two other sources
    for i in range(8):
        at += dt.timedelta(minutes=7)
        ip = "45.148.10.5" if i % 2 else "45.148.10.9"
        lines.append(f"Sep 21 {at:%H:%M:%S} gateway sshd[101]: Failed password for invalid user test{i} from {ip} port 5123{i} ssh2")
    # hostile username: must render inert
    lines.append("Sep 21 03:58:11 gateway sshd[101]: Failed password for invalid user <script>alert(3)</script> from 45.148.10.5 port 51239 ssh2")
    # brute force: 60 failures from 61.177.172.14 over ~24 min
    ft = BASE.replace(hour=4)
    users = ["root", "admin", "deploy", "oracle", "postgres"]
    for i in range(60):
        ft += dt.timedelta(seconds=24)
        lines.append(f"Sep 21 {ft:%H:%M:%S} gateway sshd[101]: Failed password for {users[i % 5]} from 61.177.172.14 port 600{i % 90 + 10} ssh2")
    # success 6 min later, then sudo within 10 min
    st_ = ft + dt.timedelta(minutes=6)
    lines.append(f"Sep 21 {st_:%H:%M:%S} gateway sshd[101]: Accepted password for deploy from 61.177.172.14 port 60111 ssh2")
    lines.append(f"Sep 21 {st_:%H:%M:%S} gateway sshd[101]: session opened for user deploy by (uid=0)")
    ut = st_ + dt.timedelta(minutes=4)
    lines.append(f"Sep 21 {ut:%H:%M:%S} gateway sudo: deploy : TTY=pts/0 ; PWD=/home/deploy ; USER=root ; COMMAND=/usr/bin/systemctl restart app")
    with open(os.path.join(out, "auth.log"), "w") as f:
        f.write("\n".join(lines) + "\n")
    n_failed = 69  # 8 invalid-user + 1 hostile + 60 password failures

    # --- conn.log: 163 conns; 110 MB pair; 35-conn sweep ----------------------
    zh = ["#separator \\x09", "#set_separator\t,",
          "#empty_field\t(empty)", "#unset_field\t-",
          "#path\tconn", "#open\t2026-09-21-00-00-00",
          "#fields\tts\tuid\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tservice\tduration\torig_bytes\tresp_bytes\tconn_state",
          "#types\ttime\tstring\taddr\tport\taddr\tport\tenum\tstring\tinterval\tcount\tcount\tstring"]
    rows = []
    ct = BASE
    for i in range(120):  # background, ~2 MB total
        ct += dt.timedelta(minutes=36)
        rows.append((ct.timestamp(), f"C{i}", f"10.0.0.{5 + i % 50}", 50000 + i,
                     f"93.184.216.{10 + i % 20}", 443, "tcp", "ssl", "1.2",
                     9000 + i * 37, 8000 + i * 41, "SF"))
    # large transfer: 8 conns, 10.0.0.8 -> 185.199.109.15, 110 MB total
    mt = BASE + dt.timedelta(hours=40)
    for i in range(8):
        rows.append(((mt + dt.timedelta(minutes=11 * i)).timestamp(), f"T{i}",
                     "10.0.0.8", 51000 + i, "185.199.109.15", 443, "tcp", "ssl",
                     "600.0", 12_000_000, 1_750_000, "SF"))
    # sweep: 35 conns from 45.9.148.22 across 20 ports in ~9 minutes,
    # aligned inside one clock-aligned 10-minute bucket
    sw_epoch = ((int((BASE + dt.timedelta(hours=55)).timestamp()) // 600) + 1) * 600 + 30
    sw = dt.datetime.fromtimestamp(sw_epoch, tz=dt.timezone.utc)
    for i in range(35):
        rows.append((int((sw + dt.timedelta(seconds=15 * i)).timestamp()), f"S{i}",
                     "45.9.148.22", 52000 + i, "203.0.113.44", 2000 + i % 20,
                     "tcp", "-", "0.1", 60, 40, "S0"))
    with open(os.path.join(out, "conn.log"), "w") as f:
        f.write("\n".join(zh) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    n_conns = len(rows)

    # --- winevents.json: 36 failed logons; brute-success + persistence + 1102 -
    win = []
    wt = BASE + dt.timedelta(days=1, hours=1)
    # spray-shaped burst: 30 × 4625 from 91.240.118.172 across 18 accounts
    for i in range(30):
        wt += dt.timedelta(seconds=38)
        win.append({"EventID": 4625, "@timestamp": iso(wt),
                    "TargetUserName": f"user{i % 18:02d}", "IpAddress": "91.240.118.172",
                    "LogonType": 3, "SubStatus": "0xC000006D", "Computer": "DC01"})
    # success: helpdesk RDP from the spray source, 4 min after last failure
    ok = wt + dt.timedelta(minutes=4)
    win.append({"EventID": 4624, "@timestamp": iso(ok), "TargetUserName": "helpdesk",
                "IpAddress": "91.240.118.172", "LogonType": 10, "Computer": "DC01"})
    # persistence within 10 min: account created + added to Administrators
    win.append({"EventID": 4720, "@timestamp": iso(ok + dt.timedelta(minutes=2)),
                "TargetUserName": "support_tmp", "SubjectUserName": "helpdesk",
                "Computer": "DC01"})
    win.append({"EventID": 4728, "@timestamp": iso(ok + dt.timedelta(minutes=3)),
                "MemberName": "support_tmp", "TargetUserName": "Administrators",
                "SubjectUserName": "helpdesk", "Computer": "DC01"})
    # audit log cleared 20 min later
    win.append({"EventID": 1102, "@timestamp": iso(ok + dt.timedelta(minutes=23)),
                "SubjectUserName": "support_tmp", "Computer": "DC01"})
    # background failures from elsewhere (separate burst, no success: no lead)
    bt = ok + dt.timedelta(minutes=60)
    for i in range(6):
        bt += dt.timedelta(minutes=9)
        win.append({"EventID": 4625, "@timestamp": iso(bt),
                    "TargetUserName": f"svc{i}", "IpAddress": "10.0.0.21",
                    "LogonType": 3, "Computer": "DC01"})
    # routine logons (must not become leads)
    for i in range(10):
        win.append({"EventID": 4624, "@timestamp": iso(BASE + dt.timedelta(hours=i * 5)),
                    "TargetUserName": "alice", "IpAddress": "10.0.0.31",
                    "LogonType": 2, "Computer": "WS07"})
    with open(os.path.join(out, "winevents.json"), "w") as f:
        for o in win:
            f.write(json.dumps(o) + "\n")
    n_fail = sum(1 for o in win if o["EventID"] == 4625)

    print(f"eve.json: alerts={n_alerts} sev1(high)={n_sev1}")
    print(f"auth.log: failed-logins={n_failed}")
    print(f"conn.log: connections={n_conns}")
    print(f"winevents.json: failed-logons={n_fail}")


if __name__ == "__main__":
    main()
