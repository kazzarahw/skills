#!/usr/bin/env python3
"""verify.py - render a built dashboard in headless Chromium and check that it works.

  verify.py dashboard.html [--shots DIR] [--wide 1440x2400] [--narrow 390x3200]

Checks: page reached data-ready (no data-error), no console errors, panel count, a filter
round-trip through the URL hash (a matching filter narrows the table; an impossible search
empties it without errors), and that no external URLs are referenced. Writes screenshots at
desktop and phone width so you can LOOK at the result (view the PNGs before declaring done).
Exit codes: 0 all checks passed, 1 a check failed or the file is missing, 2 no Chromium/Chrome found
(put it on PATH or set CHROME=/path). stdlib only.
"""
import argparse, base64, json, os, re, shutil, struct, subprocess, sys, tempfile, urllib.parse, zlib


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "microsoft-edge"):
        p = shutil.which(n)
        if p:
            return p
    return None


def run(chrome, url, extra, timeout=90):
    cmd = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--enable-logging=stderr", "--v=0",
           "--virtual-time-budget=9000", "--user-data-dir=" + tempfile.mkdtemp(prefix="socv-")] + extra + [url]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout, p.stderr


def console_errors(stderr):
    out = []
    for l in stderr.splitlines():
        if "CONSOLE" in l and re.search(r"(Uncaught|Error|error|Refused|blocked|Failed)", l):
            out.append(l.strip()[:300])
    return out


def attr(dom, name):
    m = re.search(r'<html[^>]*\s%s="([^"]*)"' % re.escape(name), dom)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("--shots", help="directory for screenshots (default: next to the HTML)")
    ap.add_argument("--wide", default="1440x2400")
    ap.add_argument("--narrow", default="390x3200")
    a = ap.parse_args()
    path = os.path.abspath(a.html)
    if not os.path.exists(path):
        sys.exit(f"not found: {path}")
    chrome = find_chrome()
    if not chrome:
        print("SKIP: no Chromium/Chrome found (set CHROME=/path). Open the file in a browser and check: panels render, no console errors, click a bar to filter.")
        sys.exit(2)
    base = "file://" + path
    shots = a.shots or os.path.dirname(path)
    os.makedirs(shots, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    results, ok = [], True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        results.append(("PASS" if cond else "FAIL", name, detail))

    dom, err = run(chrome, base, ["--dump-dom", "--window-size=1440,2400"])
    check("ready flag set", attr(dom, "data-ready") == "1", f"data-error={attr(dom, 'data-error')}" if attr(dom, "data-error") else "")
    check("no console errors", not console_errors(err), "; ".join(console_errors(err)[:3]))
    nsec = len(re.findall(r"<section", dom))
    check("panels rendered", nsec >= 4, f"{nsec} sections")
    total = int(attr(dom, "data-total") or 0)
    matches0 = int(attr(dom, "data-matches") or -1)
    check("table shows events", matches0 > 0 and matches0 == total, f"{matches0} of {total}")
    html = open(path, encoding="utf-8", errors="replace").read()
    body = re.sub(r'<script type="application/json".*?</script>', "", html, flags=re.S)
    ext = sorted({u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', body)} | {u for u in re.findall(r"url\((https?://[^)]+)\)", body)})
    check("no external resources", not ext, ", ".join(ext[:3]))
    check("CSP present", 'http-equiv="Content-Security-Policy"' in html)
    check("no inline handlers / innerHTML", not re.search(r"\son[a-z]+=|\.innerHTML|insertAdjacentHTML|document\.write", body), "")

    # filter round-trip via hash: pick the first src in the data if any
    m = re.search(r'<script type="application/json" id="soc-data">(.*?)</script>', html, re.S)
    if m:
        blob = zlib.decompress(base64.b64decode(json.loads(m.group(1))["b64"]))
        d = json.loads(blob[4:4 + struct.unpack("<I", blob[:4])[0]].decode("utf-8"))
        pick = None
        for f in ("src", "user", "sig"):
            if d["str"].get(f):
                pick = (f, d["str"][f][0])
                break
        if pick:
            dom2, err2 = run(chrome, base + "#f." + pick[0] + "=" + urllib.parse.quote(pick[1], safe=""), ["--dump-dom"])
            n2 = int(attr(dom2, "data-matches") or -1)
            check(f"hash filter {pick[0]} narrows view", 0 < n2 < total, f"{n2} of {total}; errors={console_errors(err2)[:1]}")
        dom3, err3 = run(chrome, base + "#q=zzzz-no-such-thing-zzzz", ["--dump-dom"])
        check("empty search is handled", attr(dom3, "data-matches") == "0" and attr(dom3, "data-error") is None and not console_errors(err3))

    # interaction test: a copy without the CSP meta plus a driver script that clicks through the UI
    drv = r"""<script>
(function(){var R={},root=document.documentElement;function q(s){return document.querySelector(s)}function qa(s){return document.querySelectorAll(s)}
function mt(){return +root.getAttribute('data-matches')}
function step(i){var S=[
 function(){var b=q('.sig button.btn');R.signalButton=!!b;if(b)b.click()},
 function(){R.focusNarrows=mt()<+root.getAttribute('data-total');R.chipAfterFocus=qa('.chip').length>0;var r=[].slice.call(qa('.act button')).filter(function(x){return /reset/i.test(x.textContent)})[0];if(r)r.click()},
 function(){R.resetRestores=mt()===+root.getAttribute('data-total')&&qa('.chip').length===0;var r=q('.rk');R.rankRow=!!r;if(r)r.click()},
 function(){R.rankFilters=qa('.chip').length>0;var c=q('.chip');if(c)c.click()},
 function(){R.chipRemoves=qa('.chip').length===0;var i=q('.search input');i.value='zzz-nothing-matches-zzz';i.dispatchEvent(new Event('input',{bubbles:true}))},
 function(){R.searchFilters=mt()===0;var i=q('.search input');i.value='';i.dispatchEvent(new Event('input',{bubbles:true}))},
 function(){R.searchClears=mt()===+root.getAttribute('data-total');var r=q('tr.r');R.tableRow=!!r;if(r)r.click()},
 function(){var d=q('aside.drawer');R.drawerOpens=!!d&&d.classList.contains('open');document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))},
 function(){R.drawerCloses=!q('aside.drawer.open');var s=q('svg[role="img"]');R.timelineSvg=!!s;if(s){var r=s.getBoundingClientRect(),y=r.top+r.height/2;
   function ev(t,x){s.dispatchEvent(new PointerEvent(t,{clientX:r.left+x*r.width,clientY:y,pointerId:1,bubbles:true}))}ev('pointerdown',.35);ev('pointermove',.5);ev('pointerup',.55)}},
 function(){R.brushZooms=mt()<+root.getAttribute('data-total')&&qa('.chip').length>0&&location.hash.indexOf('t=')>=0;var r=[].slice.call(qa('.act button')).filter(function(x){return /reset/i.test(x.textContent)})[0];if(r)r.click()},
 function(){R.finalReset=mt()===+root.getAttribute('data-total');root.setAttribute('data-ui',JSON.stringify(R))}];
 if(i<S.length){try{S[i]()}catch(e){R['error'+i]=String(e)}setTimeout(function(){step(i+1)},350)}}
var w=setInterval(function(){if(root.getAttribute('data-ready')==='1'){clearInterval(w);step(0)}},100)})();
</script>"""
    tmp = os.path.join(tempfile.mkdtemp(prefix="socui-"), "ui.html")
    open(tmp, "w", encoding="utf-8").write(re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', "", html).replace("</body>", drv + "</body>"))
    dom4, err4 = run(chrome, "file://" + tmp, ["--dump-dom", "--window-size=1440,2400", "--virtual-time-budget=20000"])
    mu = re.search(r'data-ui="([^"]*)"', dom4)
    if mu:
        ui = json.loads(mu.group(1).replace("&quot;", '"'))
        for k in ("signalButton", "focusNarrows", "chipAfterFocus", "resetRestores", "rankRow", "rankFilters", "chipRemoves", "searchFilters", "searchClears", "tableRow", "drawerOpens", "drawerCloses", "timelineSvg", "brushZooms", "finalReset"):
            if k == "signalButton" and ui.get(k) is False:
                results.append(("INFO", "ui: no signals panel button (data has no signals)", ""))
                continue
            if k in ("focusNarrows", "chipAfterFocus", "resetRestores") and not ui.get("signalButton"):
                continue
            check("ui: " + k, ui.get(k) is True)
        errs = [k for k in ui if k.startswith("error")]
        check("ui: no exceptions", not errs, "; ".join(f"{k}={ui[k]}" for k in errs))
        check("ui: no console errors during clicks", not console_errors(err4), "; ".join(console_errors(err4)[:2]))
    else:
        check("interaction test ran", False, "driver did not finish; is the page ready?")

    for label, size in (("wide", a.wide), ("narrow", a.narrow)):
        out = os.path.join(shots, f"{stem}.{label}.png")
        run(chrome, base, ["--screenshot=" + out, "--window-size=" + size.replace("x", ",")])
        check(f"screenshot {label}", os.path.exists(out) and os.path.getsize(out) > 5000, out)

    for status, name, detail in results:
        print(f"{status}  {name}" + (f"  - {detail}" if detail else ""))
    print("\nNow open the PNGs and look: overlapping labels, clipped text, empty panels, unreadable contrast.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
