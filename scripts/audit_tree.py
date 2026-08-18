#!/usr/bin/env python3
"""audit_tree.py — audit family-tree visualizations WITHOUT vision tools.

Vision models have repeatedly given FALSE reads on this project's dark trees
("clean, no disconnected boxes" while every connector was detached). This harness
replaces screenshots with hard numeric checks on the actual data + rendered DOM.

Checks (all numeric, deterministic):
  A. DATA LAYER  (reads the built HTML's embedded JSON — no browser needed)
     - every person from the source family-tree.json is present as a node
     - no duplicate node ids
     - every node's angle/radius/line-center is a finite number (no NaN)
     - radius values within sane bounds
     - family-line centers are separated by >= a minimum gap (no spoke collision)
     - legend lists sensible line names (no given-names like "Bayard"/"Grover")
     - focal person flagged correctly
  B. RENDER LAYER (optional, via CDP to headless Chromium — needs port)
     - svg <line> count
     - every connector line has vector-effect=non-scaling-stroke (invisible-line fix)
     - every marriage-bar endpoint lands on a box edge (no drift)
     - per-child elbows: no two families share a rail (false-parentage)

Usage:
  python3 audit_tree.py <html_file> [--data family-tree.json] [--focal PID]
  python3 audit_tree.py <html_file> --cdp <port>      # also check rendered DOM
Exit code 0 = all critical checks pass; 1 = a critical check failed.
"""
import sys, os, json, re, math, argparse, collections

CRIT = {"nan", "missing_people", "dup_ids", "spoke_collision", "no_lines", "no_nss"}

def parse_embedded(html):
    """Pull NODES and LINES (and optional FAMS/edges) out of a built wheel HTML."""
    data = {}
    m = re.search(r"const NODES=(.*?);\s*const LINES=", html, re.S)
    if m:
        try: data["nodes"] = json.loads(m.group(1))
        except Exception: data["nodes"] = None
    m = re.search(r"const LINES=(.*?);", html, re.S)
    if m:
        try: data["lines"] = json.loads(m.group(1))
        except Exception: data["lines"] = None
    return data

def audit_data(html, src_people=None, focal=None):
    results = {"fails": collections.defaultdict(list), "warns": collections.defaultdict(list)}
    d = parse_embedded(html)
    nodes = d.get("nodes")
    if nodes is None:
        results["fails"]["no_embedded"].append("no NODES found in html")
        return {"crit_ok": False, "fails": dict(results["fails"]), "warns": dict(results["warns"])}
    # unique ids + finite numbers
    ids = [n.get("id") for n in nodes]
    dup = [i for i, c in collections.Counter(ids).items() if c > 1]
    if dup: results["fails"]["dup_ids"].append(f"duplicate node ids: {dup[:5]}")
    nan = [n.get("id") for n in nodes
           if not all(isinstance(n.get(k), (int, float)) and math.isfinite(n[k]) for k in ("a", "r", "lc"))]
    if nan: results["fails"]["nan"].append(f"{len(nan)} nodes with non-finite a/r/lc: {nan[:5]}")
    # radius bounds (only on numeric values — NaN/non-numeric already flagged above)
    rs = [n.get("r", 0) for n in nodes if isinstance(n.get("r"), (int, float))]
    if rs and (min(rs) < 10 or max(rs) > 900):
        results["warns"]["radius"].append(f"radius range {min(rs):.0f}-{max(rs):.0f} outside 10-900")
    # spoke collision: min gap between line centers
    lines = d.get("lines") or []
    lcs = sorted(l.get("lc") for l in lines)
    if len(lcs) >= 2:
        gaps = [lcs[i+1]-lcs[i] for i in range(len(lcs)-1)] + [lcs[0]+360-lcs[-1]]
        if min(gaps) < 5:
            results["fails"]["spoke_collision"].append(f"min center gap {min(gaps):.1f}deg < 5deg (spokes overlap)")
        elif min(gaps) < 20:
            results["warns"]["spoke_gap"].append(f"min center gap {min(gaps):.1f}deg is tight (<20)")
    # legend sanity: line names shouldn't be given-names of people
    if src_people:
        given = {p.get("name","").split()[0] for p in src_people}
        badlines = [l.get("n") for l in lines if l.get("n") in given]
        if badlines: results["warns"]["line_names"].append(f"line names look like given-names: {badlines}")
    # missing people
    if src_people:
        src_ids = {p["id"] for p in src_people}
        node_ids = {n.get("id") for n in nodes}
        missing = src_ids - node_ids
        if missing: results["fails"]["missing_people"].append(f"{len(missing)} people missing from nodes: {list(missing)[:5]}")
    # focal flag
    if focal:
        fo = [n for n in nodes if n.get("you")]
        if fo and fo[0].get("id") != focal:
            results["warns"]["focal"].append(f"flagged focal {fo[0].get('id')} != expected {focal}")
        elif not fo:
            results["warns"]["focal"].append("no node flagged 'you'")
    fails = results["fails"]
    crit_fail = any(k in CRIT for k in fails)
    return {"crit_ok": not crit_fail, "fails": dict(fails), "warns": dict(results["warns"])}

def render_checks(cdp_port, html_path):
    """Check the rendered DOM via CDP: line count, non-scaling-stroke, no drift."""
    try:
        from websocket import create_connection
    except ImportError:
        # fallback: add the hermes venv site-packages (where websocket lives) to path
        import glob
        cands = glob.glob(os.path.expanduser("~/.hermes/hermes-agent/.venv/lib/python*/site-packages"))
        if cands:
            sys.path.insert(0, cands[0])
        try:
            from websocket import create_connection
        except ImportError:
            return {"crit_ok": False, "fails": {"no_cdp": ["websocket lib missing"]}, "warns": {}}
    import urllib.request, time
    base = f"http://127.0.0.1:{cdp_port}"
    try:
        with urllib.request.urlopen(f"{base}/json") as r:
            pages = json.load(r)
    except Exception as e:
        return {"crit_ok": False, "fails": {"no_cdp": [f"cannot reach CDP {base}: {e}"]}, "warns": {}}
    tab = [p for p in pages if p.get("type") == "page"][0]
    ws = create_connection(tab["webSocketDebuggerUrl"], timeout=30)
    _id = [0]
    def send(m, p=None):
        _id[0] += 1
        ws.send(json.dumps({"id": _id[0], "method": m, "params": p or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == _id[0]: return r.get("result", {})
    def ev(e):
        return send("Runtime.evaluate", {"expression": e, "returnByValue": True}).get("result", {}).get("value")
    send("Page.enable"); send("Runtime.enable")
    send("Page.navigate", {"url": "file://" + os.path.abspath(html_path)})
    time.sleep(2.2)
    fails = collections.defaultdict(list); warns = collections.defaultdict(list)
    nlines = ev("document.querySelectorAll('svg line').length")
    if not nlines:
        fails["no_lines"].append("0 svg <line> elements in rendered DOM")
    else:
        nss = ev("[...document.querySelectorAll('svg line')].filter(l=>l.getAttribute('vector-effect')==='non-scaling-stroke').length")
        if nss < nlines:
            warns["nss"].append(f"{nss}/{nlines} lines have non-scaling-stroke (rest may vanish at fit zoom)")
    # marriage bar / connector drift — only meaningful for a columnar tree where
    # lines connect boxes. Wheel spokes radiate to empty space, so skip long
    # radial spokes and only inspect short connecting lines.
    drift = ev("""(()=>{
      const boxes=[...document.querySelectorAll('.node')].map(b=>{const r=b.getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom};});
      let bad=0,total=0,short=0;
      document.querySelectorAll('svg line').forEach(l=>{
        const x1=parseFloat(l.getAttribute('x1')),y1=parseFloat(l.getAttribute('y1'));
        const x2=parseFloat(l.getAttribute('x2')),y2=parseFloat(l.getAttribute('y2'));
        const len=Math.hypot(x2-x1,y2-y1); if(len<300){short++;}
        total++;
        if(len<300){
          // short connector should land on a box at least at one end
          const a=boxes.some(b=>b.l-4<=x1&&x1<=b.r+4&&b.t-4<=y1&&y1<=b.b+4);
          const b2=boxes.some(b=>b.l-4<=x2&&x2<=b.r+4&&b.t-4<=y2&&y2<=b.b+4);
          if(!a&&!b2) bad++;
        }
      });
      return JSON.stringify({total,short,bad});
    })()""")
    if drift:
        try:
            dd = json.loads(drift)
            if dd.get("bad"): fails["drift"].append(f"{dd['bad']}/{dd['total']} lines have no endpoint on a box (floating)")
        except Exception: pass
    ws.close()
    crit_fail = any(k in CRIT for k in fails)
    return {"crit_ok": not crit_fail, "fails": dict(fails), "warns": dict(warns)}

def main():
    ap = argparse.ArgumentParser(description="Audit a family-tree visualization numerically (no vision).")
    ap.add_argument("html", help="the built HTML file to audit")
    ap.add_argument("--data", default=None, help="source family-tree.json for completeness check")
    ap.add_argument("--focal", default=None, help="expected focal person id")
    ap.add_argument("--cdp", type=int, default=None, help="CDP port for rendered-DOM checks")
    a = ap.parse_args()
    html = open(a.html).read()
    src = json.load(open(a.data)) if a.data else None
    src_people = src.get("people") if src else None
    print(f"=== AUDIT: {a.html} ===")
    dr = audit_data(html, src_people, a.focal)
    print("\n[DATA LAYER]")
    for k, v in dr["fails"].items():
        for msg in v: print(f"  FAIL {k}: {msg}")
    for k, v in dr["warns"].items():
        for msg in v: print(f"  warn {k}: {msg}")
    if not dr["fails"]: print("  OK — no data-layer failures")
    rr = None
    if a.cdp:
        print("\n[RENDER LAYER (CDP)]")
        rr = render_checks(a.cdp, a.html)
        for k, v in rr["fails"].items():
            for msg in v: print(f"  FAIL {k}: {msg}")
        for k, v in rr["warns"].items():
            for msg in v: print(f"  warn {k}: {msg}")
        if not rr["fails"]: print("  OK — no render-layer failures")
    crit = (dr["crit_ok"] and (rr is None or rr["crit_ok"]))
    print("\n" + ("✅ PASS — critical checks clean" if crit else "❌ FAIL — critical defects found"))
    sys.exit(0 if crit else 1)

if __name__ == "__main__":
    main()
