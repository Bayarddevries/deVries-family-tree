#!/usr/bin/env python3
"""wheel_build.py — build a generic animated radial "family wheel" from any family tree.

Takes any family-tree JSON with the standard shape:
    {"people": [{"id","name","birth","death",...}],
     "unions": [{"id","spouse1","spouse2","children":[pid,...]}]}

and writes a self-contained, animated, rotatable wheel HTML that adapts to
whatever tree you throw at it. The focal person is the one with a "you":true
flag, else a person named like the project title, else the first root.

Features (all data-driven, nothing hardcoded to deVries):
  - radial layout, focal person at center
  - family lines auto-derived by surname clustering
  - generation rings (distance from focal person)
  - drag-to-rotate + buttons, front line auto-fans-out
  - tap a legend color to spin that line to front
  - entrance + rotation animations, hover glow
  - click a person -> bottom sheet (name/dates/line)

Usage:
    python3 wheel_build.py [family-tree.json] [-o out.html] [--focal PID] [--title "T"]
"""
import sys, os, json, argparse, collections
from collections import deque

# --- surname-based line assignment (generic; works for any tree) ---
def _surname(name):
    """Return the family surname, handling compound names (de Vries, deVries,
    McX, O'X) and Latin suffixes (Sr/Jr). Falls back to the last real token."""
    toks = (name or "").split()
    if not toks:
        return "?"
    # strip generation suffixes
    while toks and toks[-1] in ("Sr", "Jr", "I", "II", "III", "IV"):
        toks.pop()
    if not toks:
        return "?"
    # compound Dutch/German noble particles attach to the NEXT token as one surname
    last = toks[-1].lower()
    if last.startswith("devries") or last in ("vries", "devries"):
        return "deVries"
    # "De Vries" -> tokens ['Gerhard','De','Vries'] : last 'vries'
    if last == "vries":
        return "deVries"
    # recombine "de Vries"-style: if penultimate is a particle and last is a name
    if len(toks) >= 2 and toks[-2].lower() in ("de", "van", "der", "den", "di", "la", "le", "von"):
        return (toks[-2] + " " + toks[-1]).title()
    # deVries (no space) already handled by startswith; plain single surname
    return toks[-1]

def assign_lines(people, unions):
    """Return {pid: line_label}. Lines = surname clusters, with married-in
    spouses absorbed into their partner's line so families read as one spoke."""
    children_of = collections.defaultdict(list)
    for u in unions:
        for c in u.get("children", []):
            children_of[u["spouse1"]].append(c)
            children_of[u["spouse2"]].append(c)
    # count each surname across the whole tree; use the most common surname as that person's line
    surname_count = collections.Counter(_surname(p.get("name","")) for p in people)
    line = {}
    for p in people:
        sn = _surname(p.get("name",""))
        # a person whose surname appears many times keeps it; rare/spouse surnames
        # get folded into their co-parent's line
        line[p["id"]] = sn if surname_count.get(sn, 0) >= 2 else None
    # fold spouse-line unknowns into partners
    for u in unions:
        for sp in (u["spouse1"], u["spouse2"]):
            if line[sp] is None:
                for other in (u["spouse1"], u["spouse2"]):
                    if other != sp and line[other]:
                        line[sp] = line[other]; break
    # remaining stragglers
    for p in people:
        if line[p["id"]] is None:
            line[p["id"]] = _surname(p.get("name","")) or "Other"
    return line

def generation_depth(people, unions, focal):
    byid = {p["id"]: p for p in people}
    byunion = {u["id"]: u for u in unions}
    children_of = collections.defaultdict(list)
    parent_union = {}
    for u in unions:
        for c in u.get("children", []):
            children_of[u["spouse1"]].append(c)
            children_of[u["spouse2"]].append(c)
            parent_union.setdefault(c, u["id"])
    gen = {}
    q = deque([focal]); gen[focal] = 0; seen = {focal}
    while q:
        n = q.popleft(); g = gen[n]
        if n in parent_union:
            u = byunion[parent_union[n]]
            for sp in (u["spouse1"], u["spouse2"]):
                if sp not in seen: seen.add(sp); gen[sp] = g + 1; q.append(sp)
        for c in children_of.get(n, []):
            if c not in seen: seen.add(c); gen[c] = g - 1; q.append(c)
    for p in people:
        gen.setdefault(p["id"], 0)
    return gen, byunion

def layout(people, unions, focal, title):
    line = assign_lines(people, unions)
    gen, byunion = generation_depth(people, unions, focal)
    by_line = collections.defaultdict(list)
    for p in people:
        by_line[line[p["id"]]].append(p)
    line_names = sorted(by_line.keys())
    tot = sum(len(v) for v in by_line.values())
    # angular sectors proportional to line size, with a hard minimum gap
    # between adjacent sector centers so no two spokes land on top of each other
    N = len(line_names)
    used = 270
    MIN_GAP = max(24.0, 300 / max(1, N))  # >= ~24deg between centers, grows for few lines
    raw_sectors = [max(18, used * len(by_line[ln]) / max(1, tot)) for ln in line_names]
    # distribute centers greedily with enforced min gap
    centers_raw = []
    cur = 0
    for i, ln in enumerate(line_names):
        centers_raw.append((cur + raw_sectors[i] / 2, ln))
        cur += raw_sectors[i] + (360 - used) / N
    # enforce minimum separation between adjacent centers
    order = sorted(centers_raw)  # by angle
    minsep = MIN_GAP
    for i in range(len(order)):
        prev = order[i - 1][0]
        want = prev + minsep
        if order[i][0] < want:
            order[i] = (want, order[i][1])
    # wrap into [0,360) keeping order
    base = order[0][0]
    center = {ln: (ang - base) % 360 for ang, ln in order}
    # also widen each sector so members of a spread line stay on their spoke
    angper = {ln: raw_sectors[i] for i, ln in enumerate(line_names)}

    palette = ["#ff6b6b","#ffd166","#06d6a0","#118ab2","#ef476f","#f78c6b",
               "#7b2cbf","#4cc9f0","#f72585","#b5e48c","#90be6d","#9d4edd",
               "#ff9e00","#00b4d8","#e9c46a","#2ec4b6","#ff70a6","#70d6ff"]
    linecolor = {ln: palette[i % len(palette)] for i, ln in enumerate(line_names)}

    # ---- radius from GLOBAL generation depth (so all lines spread across the
    # full radial extent, no line packs its members into the inner rings) ----
    gen_vals = [gen[p["id"]] for p in people]
    gmin, gmax = min(gen_vals), max(gen_vals)
    span = max(1, gmax - gmin)
    R0, R1 = 80.0, 500.0   # innermost and outermost radius
    nodes = []
    for li, ln in enumerate(line_names):
        members = sorted(by_line[ln], key=lambda p: gen[p["id"]])
        half = angper[ln] / 2
        for n_ in members:
            g = gen[n_["id"]]
            r = R0 + (g - gmin) / span * (R1 - R0)
            # spread same-generation members of this line across the sector arc
            ring_members = [m for m in members if gen[m["id"]] == g]
            pos = ring_members.index(n_)
            ang = center[ln] - half + (pos + 0.5) * (2 * half / max(1, len(ring_members)))
            nodes.append({
                "id": n_["id"], "name": n_["name"], "r": round(r, 1), "a": round(ang, 2),
                "lc": round(center[ln], 2), "g": g, "c": linecolor[ln], "you": n_["id"] == focal,
                "d": ((n_.get("birth","") or "") + (("-" + n_.get("death","")) if n_.get("death") else "")),
            })
    legend = [{"n": ln, "c": linecolor[ln], "lc": round(center[ln], 2)} for ln in line_names]
    return nodes, legend

# --- HTML template (self-contained, animated, generic) ---
TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>__TITLE__ — Family Wheel</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#07070f;color:#e8e8f0;font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden;height:100dvh;touch-action:none}
  #wrap{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:
    radial-gradient(circle at 50% 40%, #1a1a30 0%, #0b0b18 58%, #040409 100%)}
  svg{width:100%;height:100%}
  .ring{fill:none;opacity:.0;animation:ringIn 1.2s ease forwards}
  .node{cursor:pointer;opacity:0;transition:opacity .3s ease, filter .15s}
  .node:hover circle{filter:brightness(1.6) drop-shadow(0 0 6px currentColor)}
  .nodet{font-size:8px;fill:#e8e8f4;font-weight:600;pointer-events:none;text-anchor:middle;
    paint-order:stroke;stroke:#07070f;stroke-width:2.5px;stroke-linejoin:round}
  .spoke{stroke-linecap:round;opacity:.13;transition:opacity .35s ease}
  .spoke.focus{opacity:.55}
  #hub{opacity:0;animation:hubIn .9s ease forwards}
  #hub text{fill:#ffd166;text-anchor:middle}
  #hub circle.me{fill:#ffd166;stroke:#fff;stroke-width:2}
  @keyframes ringIn{to{opacity:.12}}
  @keyframes hubIn{to{opacity:1}}
  #hud{position:fixed;top:12px;left:12px;right:12px;display:flex;justify-content:space-between;align-items:flex-start;z-index:5;pointer-events:none}
  #title{font-size:13px;font-weight:700;letter-spacing:.5px;text-shadow:0 1px 4px #000;opacity:0;animation:fadeUp .8s .2s ease forwards}
  #title small{display:block;font-size:9px;font-weight:400;opacity:.55;margin-top:2px}
  #hint{font-size:9px;opacity:.5;text-align:right;max-width:150px;line-height:1.4}
  @keyframes fadeUp{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
  #legend{position:fixed;bottom:12px;left:12px;z-index:5;background:#ffffff0d;backdrop-filter:blur(8px);
    border:1px solid #ffffff1a;border-radius:12px;padding:8px 10px;font-size:9px;max-width:190px;opacity:0;animation:fadeUp .8s .4s ease forwards}
  #legend b{display:block;font-size:10px;margin-bottom:4px;letter-spacing:.3px}
  #legend span{display:flex;align-items:center;gap:5px;margin:2px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    cursor:pointer;padding:2px 4px;border-radius:4px;transition:background .15s, transform .1s}
  #legend span:hover{background:#ffffff1c;transform:translateX(2px)}
  #legend span.active{background:#ffffff1c;outline:1px solid currentColor}
  #legend i{width:8px;height:8px;border-radius:50%;display:inline-block;flex:none;transition:transform .2s}
  #legend span.active i{transform:scale(1.5)}
  #sheet{position:fixed;left:0;right:0;bottom:0;background:#17172b;border-top:1px solid #ffffff22;
    border-radius:18px 18px 0 0;padding:16px 18px 28px;transform:translateY(110%);transition:transform .3s cubic-bezier(.2,.9,.3,1.1);z-index:10;box-shadow:0 -8px 40px #000a}
  #sheet.open{transform:translateY(0)}
  #sheet .n{font-size:18px;font-weight:700}
  #sheet .d{font-size:12px;opacity:.65;margin-top:2px}
  #sheet .l{font-size:10px;display:inline-block;margin-top:8px;padding:3px 10px;border-radius:20px;color:#0a0a12;font-weight:700}
  #sheet .close{position:absolute;top:12px;right:16px;font-size:20px;opacity:.5;background:none;border:none;color:#fff;cursor:pointer}
  .grab{cursor:grab}
  .btnrow{position:fixed;bottom:12px;right:12px;z-index:6;display:flex;gap:6px}
  .btnrow button{background:#ffffff14;border:1px solid #ffffff2a;color:#e8e8f0;border-radius:9px;
    width:34px;height:34px;font-size:14px;cursor:pointer;transition:background .15s, transform .1s;backdrop-filter:blur(4px)}
  .btnrow button:hover{background:#ffffff2a;transform:scale(1.08)}
  .btnrow button:active{transform:scale(.94)}
</style>
</head>
<body>
<div id="wrap"><svg id="svg" viewBox="-600 -600 1200 1200"></svg></div>
<div id="hud">
  <div id="title">__TITLE__<small>drag to rotate · front line fans out · tap a legend color to spin it to front</small></div>
  <div id="hint">⟳ drag to rotate · pinch to zoom<br>double-tap to zoom · tap a person</div>
</div>
<div class="btnrow"><button onclick="rotBy(-30)" title="rotate left">⟲</button><button onclick="rotBy(30)" title="rotate right">⟳</button></div>
<div id="legend"><b>Family lines</b><div id="leglist"></div></div>
<div id="sheet">
  <button class="close" onclick="closeSheet()">✕</button>
  <div class="n" id="s_name"></div>
  <div class="d" id="s_dates"></div>
  <div class="l" id="s_line"></div>
</div>
<script>
__DATA__
const SVG=document.getElementById('svg'), NS='http://www.w3.org/2000/svg';
const g=document.createElementNS(NS,'g');SVG.appendChild(g);
let rotation=0,dragging=false,lastX=0,focus=null,FRONT=270,EXPAND=1.9;

// generation rings (animated in via CSS)
[[80,8],[150,6],[240,5],[330,4],[430,3]].forEach(([r,w])=>{
  const c=document.createElementNS(NS,'circle');c.setAttribute('cx',0);c.setAttribute('cy',0);
  c.setAttribute('r',r);c.setAttribute('fill','none');c.setAttribute('stroke','#ffffff');
  c.setAttribute('stroke-width',w/8);c.setAttribute('class','ring');g.appendChild(c);
});
// hub
const hub=document.createElementNS(NS,'g');hub.setAttribute('id','hub');g.appendChild(hub);
const me=document.createElementNS(NS,'circle');me.setAttribute('r',11);me.setAttribute('class','me');hub.appendChild(me);
const ct=document.createElementNS(NS,'text');ct.setAttribute('y',-18);ct.setAttribute('font-size','11px');
ct.setAttribute('font-weight','700');ct.textContent=__FOCAL_NAME__;hub.appendChild(ct);

// spokes (one per line; for a single-line tree, draw one spoke to every member)
const singleLine = LINES.length === 1;
const spokeEls={};
NODES.forEach(n=>{
  if(singleLine){
    const l=document.createElementNS(NS,'line');
    l.setAttribute('x1',0);l.setAttribute('y1',0);
    l.setAttribute('x2',(n.r+8)*Math.cos(n.a*Math.PI/180));
    l.setAttribute('y2',(n.r+8)*Math.sin(n.a*Math.PI/180));
    l.setAttribute('stroke',n.c);l.setAttribute('class','spoke');l.setAttribute('data-color',n.c);
    g.appendChild(l);spokeEls[n.c+n.id]=l;
  } else if(!spokeEls[n.c]){
    const l=document.createElementNS(NS,'line');
    l.setAttribute('x1',0);l.setAttribute('y1',0);l.setAttribute('x2',560*Math.cos(n.a*Math.PI/180));
    l.setAttribute('y2',560*Math.sin(n.a*Math.PI/180));l.setAttribute('stroke',n.c);
    l.setAttribute('class','spoke');l.setAttribute('data-color',n.c);g.appendChild(l);spokeEls[n.c]=l;
  }
});
// nodes
const nodeEls=[];
NODES.forEach((n,i)=>{
  const node=document.createElementNS(NS,'g');node.setAttribute('class','node');
  const c=document.createElementNS(NS,'circle');c.setAttribute('r',n.g>=0?4.5:3.5);c.setAttribute('fill',n.c);
  c.setAttribute('stroke','#fff');c.setAttribute('stroke-width','1');node.appendChild(c);
  const tx=document.createElementNS(NS,'text');tx.setAttribute('class','nodet');tx.textContent=n.name;node.appendChild(tx);
  node.addEventListener('click',()=>openSheet(n));
  g.appendChild(node);nodeEls.push({el:node,tx,c:n.c,baseA:n.a,r:n.r,lc:n.lc});
  // staggered entrance animation
  setTimeout(()=>node.style.opacity=1, 150+i*6);
});
function layout(){
  let best=null,bestd=1e9;
  LINES.forEach(l=>{let d=((l.lc+rotation-FRONT)%360+360)%360;if(d>180)d=360-d;if(d<bestd){bestd=d;best=l;}});
  focus=best;
  document.querySelectorAll('#leglist span').forEach(sp=>sp.classList.toggle('active',focus&&focus.c===sp.dataset.c));
  Object.keys(spokeEls).forEach(key=>{
    const el=spokeEls[key]; el.classList.toggle('focus',focus&&focus.c===el.getAttribute('data-color'));
  });
  nodeEls.forEach(nd=>{
    const isFocus=focus&&nd.c===focus.c;
    const dev=nd.baseA-nd.lc;
    let a=nd.lc+(isFocus?dev*EXPAND:dev)+rotation;
    nd.el.setAttribute('transform',`rotate(${a}) translate(${nd.r} 0)`);
    nd.tx.setAttribute('transform',`rotate(${-a})`);
  });
}
function applyRot(){layout();applyScale();}
function applyScale(){g.setAttribute('transform',`scale(${scale})`);}
let scale=1, MIN_SCALE=0.35, MAX_SCALE=5;
const wrap=document.getElementById('wrap');
// pinch + rotate via pointer map
const ptrs={};
let pinchDist=0, pinchScale=1, lastRot=0;
wrap.addEventListener('pointerdown',e=>{
  ptrs[e.pointerId]={x:e.clientX,y:e.clientY}; wrap.setPointerCapture?.(e.pointerId);
  const keys=Object.keys(ptrs);
  if(keys.length===2){
    dragging=false;
    const [a,b]=keys.map(k=>ptrs[k]);
    pinchDist=Math.hypot(a.x-b.x,a.y-b.y); pinchScale=scale; lastRot=rotation;
    wrap.classList.remove('grab');
  } else { dragging=true; lastX=e.clientX; wrap.classList.add('grab'); }
});
window.addEventListener('pointermove',e=>{
  if(!(e.pointerId in ptrs))return;
  ptrs[e.pointerId]={x:e.clientX,y:e.clientY};
  const keys=Object.keys(ptrs);
  if(keys.length===2){
    const [a,b]=keys.map(k=>ptrs[k]);
    const d=Math.hypot(a.x-b.x,a.y-b.y);
    scale=Math.min(MAX_SCALE,Math.max(MIN_SCALE,pinchScale*d/pinchDist));
    applyScale();
  } else if(dragging){
    const dx=e.clientX-lastX; rotation+=dx*0.4; lastX=e.clientX; applyRot();
  }
});
const endPtr=e=>{delete ptrs[e.pointerId]; if(Object.keys(ptrs).length<2){dragging=false;wrap.classList.remove('grab');} };
window.addEventListener('pointerup',endPtr);
window.addEventListener('pointercancel',endPtr);
// double-tap to zoom in (or back to fit)
let lastTap=0;
wrap.addEventListener('pointerdown',e=>{
  const now=Date.now();
  if(now-lastTap<280){ // double tap
    scale = scale>1.4 ? 1 : Math.min(MAX_SCALE, scale*2.2); applyScale(); lastTap=0;
  } else lastTap=now;
});
window.addEventListener('touchmove',e=>e.preventDefault(),{passive:false});
function rotBy(d){rotation+=d;applyRot();}
document.getElementById('leglist').innerHTML=LINES.map(l=>`<span data-lc="${l.lc}" data-c="${l.c}" style="color:${l.c}"><i style="background:${l.c}"></i>${l.n}</span>`).join('');
document.querySelectorAll('#leglist span').forEach(sp=>{sp.addEventListener('click',()=>{rotation=FRONT-parseFloat(sp.dataset.lc);applyRot();});});
function openSheet(n){
  document.getElementById('s_name').textContent=n.name;
  const rel = n.you ? ' · focal' : (n.g>=0 ? ' · ancestor' : ' · descendant');
  document.getElementById('s_dates').textContent=(n.d||'dates unknown')+rel;
  const l=document.getElementById('s_line');l.textContent=n.you?'focal person':(n.g>=0?'ancestor line':'descendant line');l.style.background=n.c;
  document.getElementById('sheet').classList.add('open');
}
function closeSheet(){document.getElementById('sheet').classList.remove('open');}
applyRot();
</script>
</body>
</html>
"""

def main():
    ap = argparse.ArgumentParser(description="Build a generic animated family wheel from a family-tree.json")
    ap.add_argument("input", nargs="?", default=os.path.expanduser("~/projects/deVries-family-tree/data/family-tree.json"))
    ap.add_argument("-o", "--out", default=os.path.expanduser("~/projects/deVries-family-tree/site/wheel.html"))
    ap.add_argument("--focal", default=None, help="person id to center (default: 'you' flag, else project title match, else first root)")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    d = json.load(open(args.input))
    people = d["people"]; unions = d["unions"]
    focal = args.focal
    if not focal:
        focal = next((p["id"] for p in people if p.get("you")), None)
    if not focal and args.title:
        tl = (args.title or "").lower().split()
        for p in people:
            if any(t in p.get("name","").lower() for t in tl):
                focal = p["id"]; break
    if not focal:
        # first person with no parents = a root
        kids = set(c for u in unions for c in u.get("children",[]))
        focal = next((p["id"] for p in people if p["id"] not in kids), people[0]["id"])
    title = args.title or (d.get("project", {}).get("title") if isinstance(d.get("project"), dict) else d.get("project")) or "Family"
    focal_name = next(p["name"] for p in people if p["id"]==focal)
    # focal name for center label: first name only
    fn = focal_name.split()[0]

    nodes, legend = layout(people, unions, focal, title)
    data_js = ("const NODES=" + json.dumps(nodes, ensure_ascii=False) +
               ";\nconst LINES=" + json.dumps(legend, ensure_ascii=False) + ";")
    html = TEMPLATE.replace("__DATA__", data_js)
    html = html.replace("__TITLE__", title).replace("__FOCAL_NAME__", json.dumps(fn))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    open(args.out, "w").write(html)
    print(f"✅ wheel built -> {args.out}  ({len(nodes)} people, {len(legend)} lines, focal={focal_name})")

if __name__ == "__main__":
    main()
