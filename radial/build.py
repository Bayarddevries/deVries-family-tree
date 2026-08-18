#!/usr/bin/env python3
"""Build the circular/radial family-tree page from the real family data.

Reads ../data/family-tree.json, inlines it, and emits a self-contained
index.html with a deterministic union-aware radial layout:
  * root (Bayard) at the exact center
  * each generation on a concentric ring (r = depth * RING)
  * each COUPLE (union) gets one angular sector, split between the two spouses
    so married partners sit side-by-side and never overlap
  * sector width proportional to each branch's leaf count (leaf-weighted)
  * glowing cyan dendrogram aesthetic matching Bayard's reference image
  * mobile-first rotate / pinch-zoom / scroll / tap-to-open detail
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "family-tree.json")
OUT = os.path.join(HERE, "index.html")

# Load base data from family-tree.json
with open(SRC) as f:
    data = json.load(f)

# Add the verified extra people + unions (King line, deeper Hallett/Parenteau,
# Hourie/Oltrop lines, Hamilton collaterals) that the traditional tree includes.
# Without these, the radial view is missing the entire King line (Thomas Allan
# King + Catherine Clark -> Ethel Rose King -> Guy Hamilton + Ethel -> ... -> Bayard).
PEOPLE = {p["id"]: p for p in data["people"]}
UNIONS = list(data["unions"])

PEOPLE.setdefault("P92", {"id":"P92","name":"James Morwick","birth":"c1778","death":"1865","metis":False,"privacy":"deceased",
  "note":"Jane Morwick's father (c.1778-1865), Kirkwall, Orkney."})
PEOPLE.setdefault("P93", {"id":"P93","name":"Sarah Sabiston","birth":"1800","death":"1872","metis":False,"privacy":"deceased",
  "note":"Jane Morwick's mother (1800-1872)."})
PEOPLE.setdefault("P96", {"id":"P96","name":"Sarah Fowler","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Isaac Batt's English wife. The Metis line descends from Batt's Cree family, not her."})
UNIONS += [{"id":"U20","spouse1":"P92","spouse2":"P93","children":["P029"]}]
UNIONS += [{"id":"U22","spouse1":"P079","spouse2":"P96","children":[]}]

# Round 2
for pid, p in {"P97":{"name":"Leewe de Vries","birth":"1862","death":"1926","note":"Gerhard de Vries's father."},
  "P98":{"name":"Trienje Pommer","birth":"1863","death":"1937","note":"Gerhard de Vries's mother."},
  "P99":{"name":"John James Hamilton","birth":"1856","death":"1913","note":"Guy Wentworth Hamilton's father."},
  "P100":{"name":"Jane Buchanan","birth":"1859","death":"1931","note":"Guy Wentworth Hamilton's mother."},
  "P101":{"name":"Thomas Allan King","birth":"1864","death":"1954","note":"Ethel Rose King's father; Ontario settler."},
  "P102":{"name":"Catherine Ann Clark","birth":"1867","death":"1956","note":"Ethel Rose King's mother."},
  "P103":{"name":"Harmon Miles Riggs","birth":"1834","death":"1874","note":"Ernest Charles Riggs's father."},
  "P104":{"name":"Amelia Williams","birth":"","death":"","note":"Ernest Charles Riggs's mother."}}.items():
  PEOPLE.setdefault(pid, {"id":pid,"name":p["name"],"birth":p["birth"],"death":p["death"],"metis":False,"privacy":"deceased","note":p.get("note","")})
UNIONS += [{"id":"U23","spouse1":"P97","spouse2":"P98","children":["P067"]},
  {"id":"U24","spouse1":"P99","spouse2":"P100","children":["P061"]},
  {"id":"U25","spouse1":"P101","spouse2":"P102","children":["P062"]},
  {"id":"U26","spouse1":"P103","spouse2":"P104","children":["P041"]}]

# Round 3
for pid, p in {"P105":{"name":"Engbertus de Vries","birth":"1839","death":"","note":"Leewe de Vries's father."},
  "P106":{"name":"Maria Geerds Meinders","birth":"1836","death":"1872","note":"Leewe de Vries's mother."},
  "P107":{"name":"David J. Riggs Jr","birth":"1804","death":"1850","note":"Harmon Miles Riggs's father."},
  "P108":{"name":"Catherine M. Hendricks","birth":"","death":"","note":"Harmon Miles Riggs's mother."},
  "P109":{"name":"William King","birth":"1817","death":"1898","note":"Thomas Allan King's father."},
  "P110":{"name":"Sarah Burke","birth":"1829","death":"1909","note":"Thomas Allan King's mother."}}.items():
  PEOPLE.setdefault(pid, {"id":pid,"name":p["name"],"birth":p["birth"],"death":p["death"],"metis":False,"privacy":"deceased","note":p.get("note","")})
UNIONS += [{"id":"U27","spouse1":"P105","spouse2":"P106","children":["P97"]},
  {"id":"U28","spouse1":"P107","spouse2":"P108","children":["P103"]},
  {"id":"U29","spouse1":"P109","spouse2":"P110","children":["P101"]}]

# Round 4
for pid, p in {"P111":{"name":"Joseph Hamilton","birth":"1821","death":"1889","note":"John James Hamilton's father."},
  "P112":{"name":"Mary Busby","birth":"1831","death":"1921","note":"John James Hamilton's mother."},
  "P113":{"name":"John Hamilton","birth":"1791","death":"1857","note":"Joseph Hamilton's father; Irish immigrant."},
  "P114":{"name":"Eleanor Jane Preston","birth":"1798","death":"1884","note":"Joseph Hamilton's mother."},
  "P115":{"name":"John Buchanan","birth":"1829","death":"1909","note":"Jane Buchanan's father."},
  "P116":{"name":"Isabella Watson","birth":"1837","death":"1917","note":"Jane Buchanan's mother."}}.items():
  PEOPLE.setdefault(pid, {"id":pid,"name":p["name"],"birth":p["birth"],"death":p["death"],"metis":False,"privacy":"deceased","note":p.get("note","")})
UNIONS += [{"id":"U30","spouse1":"P113","spouse2":"P114","children":["P111"]},
  {"id":"U31","spouse1":"P111","spouse2":"P112","children":["P99"]},
  {"id":"U32","spouse1":"P115","spouse2":"P116","children":["P100"]}]

# Parenteau correction
PEOPLE.setdefault("P117", {"id":"P117","name":"Philip Hourie","birth":"1833","death":"1914","metis":False,"privacy":"deceased","note":"Sarah Ann Hourie's father."})
PEOPLE.setdefault("P118", {"id":"P118","name":"Euphemia Cook Halcro","birth":"1839","death":"1917","metis":False,"privacy":"deceased","note":"Sarah Ann Hourie's mother."})
PEOPLE.setdefault("P119", {"id":"P119","name":"John Hourie","birth":"1779","death":"1857","metis":False,"privacy":"deceased","note":"Philip Hourie's father; Orkney HBC man."})
PEOPLE.setdefault("P120", {"id":"P120","name":"Margaret Bird","birth":"1787","death":"1847","metis":False,"privacy":"deceased","note":"Shoshoni adopted by Chief Factor James Curtis Bird."})
UNIONS += [{"id":"U33","spouse1":"P117","spouse2":"P118","children":["P060"]},
  {"id":"U34","spouse1":"P119","spouse2":"P120","children":["P117"]}]

# Hallett deeper
PEOPLE.setdefault("P121", {"id":"P121","name":"Henry Hallett Jr","birth":"1799","death":"1871","metis":False,"privacy":"deceased","note":"Father of Catherine Hallett."})
PEOPLE.setdefault("P122", {"id":"P122","name":"Catherine Parenteau","birth":"c1799","death":"1857","metis":True,"privacy":"deceased","note":"Mother of Catherine Hallett."})
PEOPLE.setdefault("P123", {"id":"P123","name":"Jean Baptiste Parenteau","birth":"","death":"","metis":False,"privacy":"deceased","note":"Catherine Parenteau's father, from Quebec."})
PEOPLE.setdefault("P124", {"id":"P124","name":"Unknown (Parenteau)","birth":"","death":"","metis":False,"privacy":"deceased","note":"Catherine Parenteau's mother."})
UNIONS += [{"id":"U35","spouse1":"P121","spouse2":"P122","children":["P033"]},
  {"id":"U36","spouse1":"P123","spouse2":"P124","children":["P122"]}]

# Hallett patriarch
PEOPLE.setdefault("P125", {"id":"P125","name":"Henry Hallett Sr","birth":"1773","death":"1844","metis":False,"privacy":"deceased","note":"Hallett patriarch, father of Henry Jr."})
PEOPLE.setdefault("P126", {"id":"P126","name":"Catherine Crise (Cree)","birth":"","death":"","metis":True,"privacy":"deceased","note":"Henry Hallett Sr's wife."})
PEOPLE.setdefault("P127", {"id":"P127","name":"William Peter Hallett","birth":"c1811","death":"1873","metis":True,"privacy":"deceased","note":"Buffalo-hunt captain, Henry Jr's younger brother."})
PEOPLE.setdefault("P128", {"id":"P128","name":"Maria Pruden","birth":"1813","death":"1883","metis":True,"privacy":"deceased","note":"Wife of William Peter Hallett."})
UNIONS += [{"id":"U37","spouse1":"P125","spouse2":"P126","children":["P121","P127"]},
  {"id":"U38","spouse1":"P127","spouse2":"P128","children":[]}]

# Collateral spouses
PEOPLE.setdefault("P129", {"id":"P129","name":"George Brown","birth":"1853","death":"1936","metis":False,"privacy":"deceased","note":"Ellen Spence's husband."})
PEOPLE.setdefault("P130", {"id":"P130","name":"Peter Henry Wishart","birth":"1862","death":"1936","metis":False,"privacy":"deceased","note":"Harriet Spence's husband."})
PEOPLE.setdefault("P131", {"id":"P131","name":"William Folster","birth":"","death":"","metis":False,"privacy":"deceased","note":"Jane Spence's husband."})
PEOPLE.setdefault("P132", {"id":"P132","name":"Jemima Hourie","birth":"","death":"","metis":True,"privacy":"deceased","note":"Wife of Colin Campbell Setter. Sarah Ann's sister."})
UNIONS += [{"id":"U42","spouse1":"P024","spouse2":"P132","children":[]},
  {"id":"U43","spouse1":"P035","spouse2":"P129","children":[]},
  {"id":"U44","spouse1":"P039","spouse2":"P130","children":[]},
  {"id":"U45","spouse1":"P037","spouse2":"P131","children":[]}]

# Fix Catherine Parenteau's note (corrected from Joseph V Parenteau)
PEOPLE["P122"]["note"] = "Catherine Hallett's mother (c.1799-1857, Metis). Father = Jean Baptiste Parenteau (from Quebec)."

data = {"people": list(PEOPLE.values()), "unions": UNIONS}

data_json = json.dumps(data, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>Circular Family Tree</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
  :root{
    --bg:#04060a; --grid:#c2681e; --line:#5af0ff; --line2:#0e7490;
    --node:#eafdff; --root:#9dfbff; --gold:#f4c95d; --txt:#dbe9ee; --muted:#7c8a93;
  }
  html,body{height:100%}
  body{background:radial-gradient(120% 120% at 50% 50%, #0a1018 0%, var(--bg) 70%);
    color:var(--txt);font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden;touch-action:none}
  #svg{position:fixed;inset:0;width:100%;height:100%;display:block;cursor:grab}
  #svg:active{cursor:grabbing}
  /* edges: glow layer (wide soft cyan) + core layer (thin bright white) */
  .edge{fill:none;stroke-linecap:round}
  .edge.glow{stroke:var(--line);stroke-width:3.2;opacity:.85;filter:url(#glow)}
  .edge.core{stroke:#ffffff;stroke-width:1.4;opacity:1}
  .edge.glow.mar{stroke:var(--gold);stroke-width:2;opacity:.4;stroke-dasharray:4 4;filter:none}
  .edge.core.mar{stroke:var(--gold);stroke-width:.7;opacity:.4;stroke-dasharray:4 4}
  .edge.glow.direct{stroke:var(--gold);stroke-width:4;opacity:1}
  .edge.core.direct{stroke:#fffbe6;stroke-width:2;opacity:1}
  .edge.glow.dim{opacity:.12}
  .edge.core.dim{opacity:.12}
  .node{fill:none;stroke:var(--node);stroke-width:2.2}
  .node.dim{opacity:.3}
  .node.direct{stroke:var(--gold)}
  .node.root{fill:var(--root);stroke:var(--root);filter:url(#glowW)}
  .node-dot{fill:var(--node)}
  .lbl{fill:var(--txt);font-size:9px;font-family:'Segoe UI',system-ui,sans-serif;
    paint-order:stroke;stroke:#04060a;stroke-width:2.4px;stroke-linejoin:round;
    pointer-events:none;user-select:none}
  .lbl.direct{fill:var(--gold);font-weight:600}
  .lbl.dim{opacity:.28}
  #top{position:fixed;top:0;left:0;right:0;padding:12px 14px 6px;z-index:10;
    pointer-events:none;display:flex;justify-content:space-between;align-items:flex-start}
  #title{font-size:14px;letter-spacing:.4px;color:var(--txt);text-shadow:0 0 8px #000}
  #title b{color:var(--gold);font-weight:700}
  #hint{font-size:11px;color:var(--muted);margin-top:2px}
  .ctrls{position:fixed;right:12px;bottom:18px;display:flex;flex-direction:column;gap:8px;z-index:10}
  .btn{width:42px;height:42px;border-radius:50%;border:1px solid #1c3340;background:rgba(8,18,24,.82);
    color:var(--line);font-size:18px;font-weight:700;cursor:pointer;backdrop-filter:blur(6px);
    display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(0,0,0,.5)}
  .btn:active{transform:scale(.92)}
  .toggles{position:fixed;left:12px;bottom:18px;display:flex;flex-direction:column;gap:6px;z-index:10}
  .tg{font-size:11px;color:var(--muted);border:1px solid #1c3340;background:rgba(8,18,24,.82);
    padding:7px 11px;border-radius:20px;cursor:pointer;backdrop-filter:blur(6px);user-select:none}
  .tg.on{color:var(--gold);border-color:#5a4a22}
  #backdrop{position:fixed;inset:0;background:rgba(0,0,0,.55);opacity:0;pointer-events:none;
    transition:opacity .25s;z-index:20}
  #backdrop.show{opacity:1;pointer-events:auto}
  #sheet{position:fixed;left:0;right:0;bottom:0;max-height:72vh;background:#0c151c;
    border-radius:22px 22px 0 0;border-top:1px solid #1c3340;transform:translateY(105%);
    transition:transform .3s cubic-bezier(.2,.9,.25,1);z-index:30;overflow-y:auto;padding:12px 20px 30px}
  #sheet.open{transform:translateY(0)}
  .handle{width:44px;height:4px;border-radius:2px;background:#1c3340;margin:0 auto 12px}
  .sname{font-size:19px;font-weight:700;color:var(--txt)}
  .smeta{font-size:12px;color:var(--muted);font-style:italic;margin-top:3px}
  .snote{font-size:14px;line-height:1.5;color:var(--txt);margin-top:12px}
  .stitle{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);
    margin:14px 0 6px;font-weight:700}
  .chip{display:inline-block;background:#13212b;border:1px solid #1c3340;border-radius:14px;
    padding:4px 11px;font-size:12.5px;color:var(--txt);margin:0 5px 5px 0;cursor:pointer}
  .chip.you{border-color:var(--gold);color:var(--gold)}
  .close{position:absolute;top:14px;right:16px;background:none;border:none;color:var(--muted);
    font-size:20px;cursor:pointer}
  .badge{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.5px;padding:2px 7px;
    border-radius:10px;margin-left:6px;vertical-align:middle}
  .badge.m{background:#1d3323;color:#7bd89b;border:1px solid #2f5e3f}
  .badge.you{background:#3a2e12;color:var(--gold);border:1px solid #5a4a22}
</style>
</head>
<body>
<svg id="svg"><defs>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3.6" result="b1"/>
    <feGaussianBlur stdDeviation="6.5" result="b2"/>
    <feMerge>
      <feMergeNode in="b2"/>
      <feMergeNode in="b1"/>
      <feMergeNode in="SourceGraphic"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="glowW" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="5" result="b1"/>
    <feGaussianBlur stdDeviation="9" result="b2"/>
    <feMerge>
      <feMergeNode in="b2"/>
      <feMergeNode in="b1"/>
      <feMergeNode in="SourceGraphic"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs></svg>

<div id="top">
  <div>
    <div id="title"><b>Circular Family Tree</b> · deVries · Spence</div>
    <div id="hint">drag to rotate · pinch or scroll to zoom · tap a person</div>
  </div>
</div>
<div class="toggles">
  <div class="tg on" id="tgLabels">names</div>
  <div class="tg" id="tgDirect">direct line</div>
</div>
<div class="ctrls">
  <div class="btn" id="zin">+</div>
  <div class="btn" id="zout">&minus;</div>
  <div class="btn" id="zreset">⟳</div>
  <div class="btn" id="zfit">⤢</div>
</div>
<div id="backdrop"></div>
<div id="sheet">
  <div class="handle"></div>
  <button class="close" id="sheetclose">✕</button>
  <div id="sheetbody"></div>
</div>

<script>
const DATA = __DATA__;
const ROOT = (DATA.people.find(p=>p.you)||DATA.people[0]).id;
const byId = {}; DATA.people.forEach(p=>byId[p.id]=p);
const RING = 60;
const NODE_R = 5.0;
const TWO_PI = Math.PI*2;

// ---- parent map + union maps ----
const parentsOf = {};                 // child -> [parent ids]
const childUnionOf = {};              // person -> union where they are a child
const spouseUnionOf = {};             // person -> list of unions where they are a spouse
DATA.unions.forEach(u=>{
  const pars=[u.spouse1,u.spouse2].filter(Boolean);
  (u.children||[]).forEach(c=>{ parentsOf[c]=pars.slice(); });
  (u.children||[]).forEach(c=>{ if(!childUnionOf[c]) childUnionOf[c]=u; });
  pars.forEach(s=>{ (spouseUnionOf[s]=spouseUnionOf[s]||[]).push(u); });
});

// ---- ancestor set + generation depth (BFS from ROOT upward) ----
const anc=new Set([ROOT]); const depth={[ROOT]:0}; const q=[ROOT];
while(q.length){ const c=q.shift(); const d=depth[c];
  (parentsOf[c]||[]).forEach(p=>{ if(byId[p]&&!(p in depth)){depth[p]=d+1;anc.add(p);q.push(p);} });
}

// ---- leaf weight under a person (unique deepest ancestors upward) ----
const leafMemo={};
function leavesUnder(pid){
  if(pid in leafMemo) return leafMemo[pid];
  const u=childUnionOf[pid];
  if(!u){ leafMemo[pid]=1; return 1; }            // no known parents -> a leaf
  let s=0;
  [u.spouse1,u.spouse2].forEach(sp=>{ if(sp&&byId[sp]) s+=leavesUnder(sp); });
  leafMemo[pid]=Math.max(1,s); return leafMemo[pid];
}

// ---- union-aware recursive layout ----
const pos={}; pos[ROOT]={x:0,y:0,r:0,a:0,d:0};
const placed=new Set([ROOT]);
const seenU=new Set();
function layoutUnion(u,a0,a1){
  if(!u||seenU.has(u.id)) return; seenU.add(u.id);
  const s1=u.spouse1, s2=u.spouse2;
  const w1=(s1&&byId[s1])?leavesUnder(s1):0;
  const w2=(s2&&byId[s2])?leavesUnder(s2):0;
  const tot=w1+w2||1;
  const aMid=a0+(a1-a0)*(w1/tot);
  if(s1&&byId[s1]&&!placed.has(s1)){
    const a=(a0+aMid)/2, d=depth[s1]|0;
    pos[s1]={x:d*RING*Math.cos(a), y:d*RING*Math.sin(a), r:d*RING, a, d};
    placed.add(s1);
  }
  if(s2&&byId[s2]&&!placed.has(s2)){
    const a=(aMid+a1)/2, d=depth[s2]|0;
    pos[s2]={x:d*RING*Math.cos(a), y:d*RING*Math.sin(a), r:d*RING, a, d};
    placed.add(s2);
  }
  if(s1&&byId[s1]&&childUnionOf[s1]&&!seenU.has(childUnionOf[s1].id)) layoutUnion(childUnionOf[s1], a0, aMid);
  if(s2&&byId[s2]&&childUnionOf[s2]&&!seenU.has(childUnionOf[s2].id)) layoutUnion(childUnionOf[s2], aMid, a1);
}
const rootUnion=childUnionOf[ROOT];
layoutUnion(rootUnion, -Math.PI/2, -Math.PI/2+TWO_PI);

// place any ancestors not reached (orphan branches) around the rim
let orphanStart=-Math.PI/2;
anc.forEach(id=>{ if(!placed.has(id)){ const d=depth[id]|0, a=orphanStart;
  pos[id]={x:d*RING*Math.cos(a), y:d*RING*Math.sin(a), r:d*RING, a, d}; placed.add(id); orphanStart+=0.2; } });

// direct spine: paths ROOT -> P001 (James Spence Sr) and ROOT -> P002 (Margaret Batt)
const directIds=new Set([ROOT]);
function downward(id, target){
  if(id===target){directIds.add(id);return true;}
  let found=false;
  (spouseUnionOf[id]||[]).forEach(u=>{
    (u.children||[]).forEach(c=>{ if(byId[c]&&downward(c,target)){directIds.add(id);found=true;} });
  });
  return found;
}
downward(ROOT,'P001'); downward(ROOT,'P002');

// ---- edges: child -> each parent (lineage) + spouse arc (marriage) ----
const edges=[];
anc.forEach(c=>{
  (parentsOf[c]||[]).forEach(p=>{ if(anc.has(p)) edges.push({c,p,type:'line'}); });
});
DATA.unions.forEach(u=>{
  const s1=u.spouse1,s2=u.spouse2;
  if(s1&&s2&&anc.has(s1)&&anc.has(s2)) edges.push({c:s1,p:s2,type:'mar'});
});

// ---- render ----
const svg=document.getElementById('svg');
const maxDepth=Math.max(...Object.values(depth));
const VB=(maxDepth*RING+80);
svg.setAttribute('viewBox', `${-VB} ${-VB} ${VB*2} ${VB*2}`);
const gGrid=document.createElementNS('http://www.w3.org/2000/svg','g');
const gEdges=document.createElementNS('http://www.w3.org/2000/svg','g');
const gNodes=document.createElementNS('http://www.w3.org/2000/svg','g');
const gLabels=document.createElementNS('http://www.w3.org/2000/svg','g');
svg.appendChild(gGrid); svg.appendChild(gEdges); svg.appendChild(gNodes); svg.appendChild(gLabels);

// faint orange concentric rings + spokes (non-rotating)
for(let d=1;d<=maxDepth;d++){
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx',0);c.setAttribute('cy',0);c.setAttribute('r',d*RING);
  c.setAttribute('fill','none');c.setAttribute('stroke','var(--grid)');
  c.setAttribute('stroke-opacity','0.10');c.setAttribute('stroke-width','1');
  gGrid.appendChild(c);
}
for(let i=0;i<24;i++){ const a=i/24*TWO_PI;
  const l=document.createElementNS('http://www.w3.org/2000/svg','line');
  l.setAttribute('x1',0);l.setAttribute('y1',0);
  l.setAttribute('x2',(maxDepth*RING+40)*Math.cos(a));l.setAttribute('y2',(maxDepth*RING+40)*Math.sin(a));
  l.setAttribute('stroke','var(--grid)');l.setAttribute('stroke-opacity','0.06');l.setAttribute('stroke-width','1');
  gGrid.appendChild(l);
}

edges.forEach(e=>{
  const C=pos[e.c], P=pos[e.p]; if(!C||!P) return;
  const isD=(e.type!=='mar') && directIds.has(e.c)&&directIds.has(e.p);
  const d = (e.type==='mar')
    ? `M ${C.x} ${C.y} L ${P.x} ${P.y}`
    : (()=>{ const rm=(C.r+P.r)/2, ctrlx=rm*Math.cos(C.a), ctrly=rm*Math.sin(C.a);
             return `M ${C.x} ${C.y} Q ${ctrlx} ${ctrly} ${P.x} ${P.y}`; })();
  // glow layer (wide, soft) + core layer (thin, bright white-ish)
  const glow=document.createElementNS('http://www.w3.org/2000/svg','path');
  glow.setAttribute('d',d);
  glow.setAttribute('class','edge glow'+(e.type==='mar'?' mar':'')+(isD?' direct':''));
  glow.setAttribute('filter','url(#glow)');
  const core=document.createElementNS('http://www.w3.org/2000/svg','path');
  core.setAttribute('d',d);
  core.setAttribute('class','edge core'+(e.type==='mar'?' mar':'')+(isD?' direct':''));
  gEdges.appendChild(glow); gEdges.appendChild(core);
});

anc.forEach(id=>{
  const p=pos[id]; const person=byId[id];
  const g=document.createElementNS('http://www.w3.org/2000/svg','g');
  g.dataset.id=id; g.style.cursor='pointer';
  const isRoot=id===ROOT, isDirect=directIds.has(id);
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);
  c.setAttribute('r',isRoot?9:NODE_R);
  c.setAttribute('class','node'+(isRoot?' root':(isDirect?' direct':'')));
  c.setAttribute('filter', isRoot?'url(#glowW)':'url(#glow)');
  g.appendChild(c);
  // bright solid core dot (white center of the glowing ring)
  const core=document.createElementNS('http://www.w3.org/2000/svg','circle');
  core.setAttribute('cx',p.x);core.setAttribute('cy',p.y);
  core.setAttribute('r',isRoot?4.5:2.4);
  core.setAttribute('fill', isRoot?'#ffffff':'#eaffff');
  core.setAttribute('stroke','none');
  core.setAttribute('filter','url(#glow)');
  g.appendChild(core);
  // invisible hit area so the whole node (not just the thin stroke) is tappable
  const hit=document.createElementNS('http://www.w3.org/2000/svg','circle');
  hit.setAttribute('cx',p.x);hit.setAttribute('cy',p.y);
  hit.setAttribute('r',isRoot?14:11);
  hit.setAttribute('fill','transparent');
  hit.setAttribute('stroke','none');
  hit.style.cursor='pointer';
  g.appendChild(hit);
  // robust tap detection: pointerdown on node -> pointerup near same spot = tap
  let downX=null, downY=null;
  g.addEventListener('pointerdown',e=>{ downX=e.clientX; downY=e.clientY; });
  g.addEventListener('pointerup',e=>{
    if(downX===null) return;
    const moved=Math.hypot(e.clientX-downX, e.clientY-downY);
    downX=downY=null;
    if(moved<8){ e.stopPropagation(); openSheet(id); }
  });
  gNodes.appendChild(g);
  const t=document.createElementNS('http://www.w3.org/2000/svg','text');
  t.setAttribute('x',p.x + (Math.cos(p.a)>=0?8:-8));
  t.setAttribute('y',p.y+3);
  t.setAttribute('text-anchor', Math.cos(p.a)>=0?'start':'end');
  t.setAttribute('class','lbl'+(isDirect?' direct':''));
  const nm=person.name.split(/[ ]+/);
  t.textContent=(nm[0]||'')+(nm.length>1?(' '+nm[nm.length-1]):'');
  gLabels.appendChild(t);
});

// ---- transform / interaction ----
let rot=0, zoom=1;
function apply(){
  const t=`rotate(${rot}) scale(${zoom})`;
  gEdges.setAttribute('transform',t); gNodes.setAttribute('transform',t); gLabels.setAttribute('transform',t);
  gLabels.querySelectorAll('text').forEach(t0=>{
    const x=+t0.getAttribute('x'), y=+t0.getAttribute('y');
    t0.setAttribute('transform',`rotate(${-rot} ${x} ${y})`);
  });
}
apply();
function fit(){ const vw=window.innerWidth, vh=window.innerHeight;
  zoom=Math.min(vw,vh)/((maxDepth*RING+90)*2)*0.94; zoom=Math.max(zoom,0.2); rot=0; apply(); }
function zoomAt(f){ zoom=Math.min(6,Math.max(0.2,zoom*f)); apply(); }

const ptrs=new Map(); let lastAng=null;
function centerAng(ev){ const r=svg.getBoundingClientRect();
  return Math.atan2(ev.clientY-(r.top+r.height/2), ev.clientX-(r.left+r.width/2)); }
svg.addEventListener('pointerdown',e=>{ ptrs.set(e.pointerId,[e.clientX,e.clientY]);
  if(ptrs.size===1) lastAng=centerAng(e); });
svg.addEventListener('pointermove',e=>{
  if(!ptrs.has(e.pointerId))return; ptrs.set(e.pointerId,[e.clientX,e.clientY]);
  if(ptrs.size===1&&lastAng!==null){
    const a=centerAng(e); let d=a-lastAng; if(d>Math.PI)d-=TWO_PI; if(d<-Math.PI)d+=TWO_PI;
    rot+=d*180/Math.PI; lastAng=a; apply();
  } else if(ptrs.size===2){
    const v=[...ptrs.values()]; const dist=Math.hypot(v[0][0]-v[1][0],v[0][1]-v[1][1]);
    if(zoom._pd) zoomAt(dist/zoom._pd); zoom._pd=dist;
  }
});
function endP(e){ ptrs.delete(e.pointerId); if(ptrs.size<2)zoom._pd=null; if(ptrs.size===0)lastAng=null; }
svg.addEventListener('pointerup',endP); svg.addEventListener('pointercancel',endP);
svg.addEventListener('wheel',e=>{e.preventDefault();zoomAt(Math.exp(-e.deltaY*0.0015));},{passive:false});
let lastTap=0;
svg.addEventListener('touchend',e=>{ if(e.changedTouches.length!==1)return;
  const n=Date.now(); if(n-lastTap<320){zoomAt(1.4);lastTap=0;} else lastTap=n; },{passive:true});
svg.addEventListener('dblclick',()=>zoomAt(1.4));

document.getElementById('zin').onclick=()=>zoomAt(1.35);
document.getElementById('zout').onclick=()=>zoomAt(1/1.35);
document.getElementById('zreset').onclick=()=>{rot=0;apply();};
document.getElementById('zfit').onclick=fit;

let labelsOn=true, directOn=false;
const tgL=document.getElementById('tgLabels'), tgD=document.getElementById('tgDirect');
tgL.onclick=()=>{ labelsOn=!labelsOn; tgL.classList.toggle('on',labelsOn);
  gLabels.style.display=labelsOn?'':'none'; };
tgD.onclick=()=>{ directOn=!directOn; tgD.classList.toggle('on',directOn);
  gEdges.querySelectorAll('.edge').forEach(p=>{ if(!p.classList.contains('direct')) p.classList.toggle('dim',directOn); });
  gNodes.querySelectorAll('.node:not(.root):not(.direct)').forEach(p=>p.classList.toggle('dim',directOn));
  gLabels.querySelectorAll('.lbl:not(.direct)').forEach(p=>p.classList.toggle('dim',directOn)); };

// ---- detail sheet ----
const backdrop=document.getElementById('backdrop'), sheet=document.getElementById('sheet');
function openSheet(id){
  const p=byId[id]; if(!p)return;
  let h=`<div class="sname">${esc(p.name)}`;
  if(p.you)h+=`<span class="badge you">YOU</span>`;
  if(p.metis)h+=`<span class="badge m">MÉTIS</span>`;
  h+=`</div>`;
  const yrs=[]; if(p.birth)yrs.push('b. '+p.birth); if(p.death)yrs.push('d. '+p.death);
  if(yrs.length)h+=`<div class="smeta">${yrs.join(' · ')}</div>`;
  if(p.note||p.notes)h+=`<div class="snote">${esc(p.note||p.notes)}</div>`;
  const pars=(parentsOf[id]||[]).filter(x=>byId[x]);
  const kids=DATA.unions.filter(u=>(u.spouse1===id||u.spouse2===id)).flatMap(u=>u.children||[]).filter(x=>byId[x]);
  if(pars.length){ h+=`<div class="stitle">Parents</div>`; h+=pars.map(x=>`<span class="chip" data-id="${x}">${esc(byId[x].name)}</span>`).join(''); }
  if(kids.length){ h+=`<div class="stitle">Children</div>`; h+=kids.map(x=>`<span class="chip" data-id="${x}">${esc(byId[x].name)}</span>`).join(''); }
  document.getElementById('sheetbody').innerHTML=h;
  document.getElementById('sheetbody').querySelectorAll('.chip').forEach(c=>c.onclick=()=>openSheet(c.dataset.id));
  backdrop.classList.add('show'); sheet.classList.add('open');
}
function closeSheet(){ backdrop.classList.remove('show'); sheet.classList.remove('open'); }
document.getElementById('sheetclose').onclick=closeSheet;
backdrop.onclick=closeSheet;
function esc(s){const d=document.createElement('div');d.textContent=s??'';return d.innerHTML;}
window.addEventListener('resize',()=>{ if(zoom<=0.01)fit(); });
fit();
</script>
</body>
</html>
"""

HTML = HTML.replace("__DATA__", data_json)
with open(OUT, "w") as f:
    f.write(HTML)

# python-side stats for confirmation
_root = next((p["id"] for p in data["people"] if p.get("you")), data["people"][0]["id"])
_pby = {p["id"]: p for p in data["people"]}
_po = {}
for u in data["unions"]:
    for c in u.get("children", []):
        _po.setdefault(c, []).extend([x for x in (u["spouse1"], u["spouse2"]) if x])
_anc = {_root}
_q = [_root]
while _q:
    c = _q.pop()
    for p in _po.get(c, []):
        if p in _pby and p not in _anc:
            _anc.add(p); _q.append(p)
print("wrote", OUT, len(HTML), "bytes; root=", _root, "; ancestors=", len(_anc))
