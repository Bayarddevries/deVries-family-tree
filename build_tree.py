#!/usr/bin/env python3
"""
build_tree.py — generate site/index.html from data/family-tree.json (schema v2).

Modern app-shell family tree: dark theme, bottom tab bar
(Tree · People · Stories · Timeline), pan-and-zoom tree canvas,
tap-for-profile bottom sheets, photo-forward. Single self-contained file.

Usage: python3 build_tree.py
"""
import json, os, html as H
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "family-tree.json")))
PEOPLE = {p["id"]: p for p in DATA["people"]}
UNIONS = DATA["unions"]
STORIES = DATA.get("stories", {})
PROJ = DATA["project"]

def load_image(rel):
    p = os.path.join(HERE, "site", "assets", rel)
    if not os.path.exists(p): return None
    with open(p, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

IMAGES = {pid: uri for pid, uri in {
    "P030": load_image("david-spence.jpg"),
    "P051": load_image("john-norquay.jpg"),
}.items() if uri}

def esc(s): return H.escape(str(s))

def yrs(pid):
    p = PEOPLE.get(pid, {})
    b, dd = p.get("birth"), p.get("death")
    if b and dd: return f"{b}–{dd}"
    if b: return f"b. {b}"
    if dd: return f"d. {dd}"
    return ""

# =========================================================
# FAMILYTREE JS LAYOUT MODEL
# The classic descendant chart is rendered by BALKAN FamilyTree JS,
# a purpose-built genealogy library, from parent/partner links.
# The library cannot lay out pedigree collapse (both Spence lines converge
# at Alan + Ella), so Ella's parent links are cut for LAYOUT only; her card
# carries a note naming her parents. The data itself is untouched.
# =========================================================
FEMALE = {"P080","P002","P006","P009","P011","P012","P013","P014","P017","P018","P019","P021","P022","P028","P029","P032","P033","P035","P037","P038","P039","P042","P044","P046","P048","P053","P060","P062","P063","P064","P066","P068","P070","P072","P073","P074","P075","P076","P082","P083","P088","P090"}

def build_ft_nodes():
    by_id = {p["id"]: p for p in DATA["people"]}
    idmap, nodes = {}, []
    def add(pid):
        nid = len(nodes) + 1
        nodes.append({"id": nid, "name": by_id[pid]["name"],
                      "gender": 2 if pid in FEMALE else 1, "pids": [], "ref": pid})
        idmap[pid] = nid
        return nid
    for p in DATA["people"]:
        add(p["id"])
    for u in UNIONS:
        s1, s2 = u["spouse1"], u["spouse2"]
        n1, n2 = idmap[s1], idmap[s2]
        if n2 not in nodes[n1-1]["pids"]: nodes[n1-1]["pids"].append(n2)
        if n1 not in nodes[n2-1]["pids"]: nodes[n2-1]["pids"].append(n1)
        mid = s1 if s1 in FEMALE else s2
        fid = s2 if s1 in FEMALE else s1
        for c in u["children"]:
            nodes[idmap[c]-1]["mid"] = idmap[mid]
            nodes[idmap[c]-1]["fid"] = idmap[fid]
            nodes[idmap[mid]-1]["gender"] = 2
            nodes[idmap[fid]-1]["gender"] = 1
    # Mixed layout on Lawrence + Bryon: renders each in BOTH their birth
    # family (Hamilton / deVries) and their married family (Doris / Tracy),
    # so the in-law sibling families stay in the tree. Ella stays cut (see
    # below) because her two families share an ancestor (James Sr + Batt)
    # and the library's link renderer overflows on that cousin-marriage.
    for pid in ("P045", "P049"):                    # Lawrence, Bryon
        nodes[idmap[pid]-1]["layout"] = 1           # FamilyTree.mixed
    # layout-only cut: Ella's parent links (cousin-marriage); note on her card
    e = nodes[idmap["P042"]-1]
    e.pop("mid", None); e.pop("fid", None)
    e["note"] = "daughter of Ernest Riggs \u26AC Mary Ann Spence (Riggs \u00B7 Spence line)"
    nodes[idmap["P050"]-1]["cssClass"] = "you"     # highlight Bayard
    return nodes

TREE = {"ftNodes": build_ft_nodes()}


# =========================================================
# TIMELINE
# =========================================================
TIMELINE = [
    (1773, "h", "James Spence Sr arrives at York Factory as an HBC labourer."),
    (1776, "h", "Isaac Batt briefly joins rival 'Pedlar' traders under Joseph Frobisher."),
    (1782, "a", "James Spence Sr and Margaret 'Nestichio' Batt become partners at York Factory; their first son James is born."),
    (1791, "a", "Isaac Batt is shot and killed near Manchester House — the first HBC servant killed by Indians in the Saskatchewan area."),
    (1795, "a", "James Spence Sr dies at Buckingham House aged 42, leaving a will naming 'his Indian Wife Nestichio, daughter of the deceased Isaac Batt' and their four children."),
    (1800, "h", "Andrew Setter joins the HBC at York Factory as a labourer."),
    (1812, "h", "Lord Selkirk's first settlers arrive at Red River."),
    (1821, "a", "Peggy Spence marries Andrew Setter at Beaver Creek (28 Jan), baptised/married by Rev. John West."),
    (1824, "a", "David Spence is born at St. John's parish, Red River (5 Sep)."),
    (1844, "a", "David Spence marries Catherine Hallett at St. John's (15 Feb)."),
    (1861, "a", "Mary Ann Spence is born (8 Aug) — the 5th of David and Catherine's seven children."),
    (1869, "h", "The Red River Resistance begins; Métis block the new lieutenant-governor at Pembina."),
    (1870, "a", "David Spence sits in the Convention of Forty (25 Jan–10 Feb); Manitoba enters Confederation; he is elected first MLA for Poplar Point (27 Dec)."),
    (1876, "a", "Métis scrip is issued to David and Catherine Spence (2 Oct)."),
    (1880, "a", "Catherine Hallett Spence dies aged 55."),
    (1885, "a", "David Spence dies (16 Sep) after being accidentally shot by a neighbour; the North-West Resistance ends at Batoche."),
    (1909, "a", "Allan Setter marries Ella Alberta Riggs at Portage la Prairie (31 Mar)."),
    (1912, "a", "Doris Alberta Setter is born (24 Dec, Portage la Prairie); Lawrence Donald Hamilton is born (15 Jun, Tisdale SK)."),
    (1932, "a", "Doris Setter marries Lawrence Hamilton at Tisdale, Saskatchewan (29 Dec)."),
    (1933, "a", "Mavis Irene Hamilton is born (1 Sep, Tisdale)."),
    (1939, "a", "The Hamilton family relocates to Flin Flon when Mavis is six."),
    (1954, "a", "Bryon Edward deVries is born (17 Jul)."),
    (2019, "a", "Bryon deVries dies (13 Oct), remembered as a devoted family man and HR director."),
    (2020, "a", "Mavis Irene Lau dies (26 Aug)."),
]

# =========================================================
# EMBEDDED DATA (for the JS app)
# =========================================================
JS_DATA = {
    "title": PROJ["title"], "subtitle": PROJ["focus"],
    "people": [{"id": p["id"], "name": p["name"], "birth": p.get("birth"), "death": p.get("death"),
                "metis": bool(p.get("metis")), "living": p.get("privacy") == "living",
                "note": p.get("note", ""), "you": bool(p.get("you"))} for p in DATA["people"]],
    "unions": [{"id": u["id"], "s1": u["spouse1"], "s2": u["spouse2"],
                "children": u["children"], "note": u.get("note", "")} for u in UNIONS],
    "stories": STORIES,
    "images": IMAGES,
    "tree": TREE,
    "timeline": TIMELINE,
    "paths": DATA["paths_to_root"],
    "open": DATA["open_items"],
}
json_blob = json.dumps(JS_DATA, ensure_ascii=False).replace("</", "<\\/")

# =========================================================
# APP SHELL (dark, animated, tabbed)
# =========================================================
APP = r"""
<header class="top">
  <div class="brand">[[TITLE]]</div>
  <div class="brand-sub">[[SUBTITLE]]</div>
</header>

<main>
  <section id="view-tree" class="view active">
    <div id="ftree"></div>
    <div class="zbtns">
      <button class="zbtn" id="zin">+</button>
      <button class="zbtn" id="zout">−</button>
      <button class="zbtn" id="zfit">⤲</button>
    </div>
    <div class="hint" id="treehint">drag to pan · pinch or scroll to zoom · tap a person · search top-right</div>
  </section>

  <section id="view-people" class="view">
    <div class="searchbar"><input id="search" type="search" placeholder="Search the family…"></div>
    <div id="peoplegrid" class="grid"></div>
  </section>

  <section id="view-stories" class="view">
    <h2 class="vhead">Stories &amp; Profiles</h2>
    <div id="storylist"></div>
  </section>

  <section id="view-timeline" class="view">
    <h2 class="vhead">Family timeline</h2>
    <div id="timelinelist" class="tlist"></div>
  </section>
</main>

<nav class="tabbar">
  <button class="tab active" data-tab="tree"><span class="ti">🌳</span><span>Tree</span></button>
  <button class="tab" data-tab="people"><span class="ti">👥</span><span>People</span></button>
  <button class="tab" data-tab="stories"><span class="ti">📖</span><span>Stories</span></button>
  <button class="tab" data-tab="timeline"><span class="ti">🕰</span><span>Timeline</span></button>
</nav>

<div id="backdrop"></div>
<div id="sheet">
  <div class="sheet-handle"></div>
  <button class="sheet-close" id="sheetclose">✕</button>
  <div id="sheetbody"></div>
</div>
"""

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#14121A;--surface:#1E1A26;--surface2:#272131;--line:#3A3346;
  --txt:#F2E9DC;--muted:#9C8FA9;--crimson:#E0525C;--crimson-d:#8C1F28;
  --gold:#D4A853;--cream:#F5EDE2;
}
html,body{height:100%}
body{background:radial-gradient(1200px 800px at 70% -10%,#241D2E 0%,var(--bg) 55%);color:var(--txt);
  font-family:'EB Garamond',Georgia,serif;overflow:hidden}
h1,h2,h3,.brand,.tab,.node-name{font-family:'Cinzel',serif}
.top{padding:18px 18px 6px;text-align:center}
.brand{font-size:clamp(19px,4.5vw,27px);font-weight:700;color:var(--cream);letter-spacing:.5px}
.brand::after{content:"";display:block;width:56px;height:2px;background:linear-gradient(90deg,var(--gold),transparent);margin:7px auto 0}
.brand-sub{font-size:12px;color:var(--muted);font-style:italic;margin-top:5px}
main{position:fixed;inset:58px 0 62px;overflow:hidden}
.view{position:absolute;inset:0;overflow-y:auto;padding:14px 16px 30px;display:none;scrollbar-width:thin;scrollbar-color:var(--line) transparent}
.view.active{display:block;animation:fadeUp .35s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.vhead{font-size:17px;color:var(--cream);border-bottom:2px solid var(--gold);padding-bottom:6px;margin-bottom:12px}

/* ---- tree canvas ---- */
#wrap{position:absolute;inset:0;overflow:hidden;touch-action:none;user-select:none;-webkit-user-select:none}
#stage{position:absolute;inset:0;overflow:hidden}
#canvas{position:absolute;top:0;left:0;transform-origin:0 0;will-change:transform}
.cnode{position:absolute;background:linear-gradient(180deg,var(--surface2),var(--surface));
  border:1px solid var(--line);border-radius:12px;padding:7px 9px;text-align:center;cursor:pointer;
  box-shadow:0 6px 18px rgba(0,0,0,.35);transition:transform .15s ease,border-color .15s,box-shadow .15s;
  display:flex;flex-direction:column;justify-content:center}
.cnode:active{transform:scale(.97)}
.cnode.you{border-color:var(--crimson);box-shadow:0 0 0 2px rgba(224,82,92,.25),0 6px 18px rgba(0,0,0,.4)}
.cnode .n1,.cnode .n3{font-family:'Cinzel',serif;font-size:12px;color:var(--cream);line-height:1.2;font-weight:600}
.cnode .n2{font-size:13px;color:var(--gold);line-height:1.15}
.cnode .years{font-size:10px;color:var(--muted);margin-top:2px;font-style:italic}
.cnode.person .n1{font-size:12.5px}
.cnode.long .n1,.cnode.long .n3{font-size:10px}
.cnode.long.person .n1{font-size:11px}
.cnode .m{display:inline-block;background:var(--gold);color:#241D2E;font-size:8px;font-weight:700;
  letter-spacing:1px;padding:1px 5px;border-radius:7px;margin-top:3px;align-self:center}
.lane{position:absolute;left:8px;width:118px;font-family:'Cinzel',serif;font-size:12px;color:var(--muted);
  line-height:1.15;padding-top:4px;letter-spacing:.3px;pointer-events:none}
#lanes{position:absolute;left:0;top:0;width:130px;bottom:0;overflow:hidden;pointer-events:none;
  background:linear-gradient(90deg,rgba(20,18,26,.92) 82%,transparent);z-index:5}
canvas#conn{position:absolute;top:0;left:0;pointer-events:none}
.zbtns{position:absolute;right:12px;bottom:16px;display:flex;flex-direction:column;gap:8px}
.zbtn{width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--surface2);
  color:var(--cream);font-size:19px;font-weight:700;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.4)}
.zbtn:active{transform:scale(.93)}
.hint{position:absolute;left:0;right:0;bottom:8px;text-align:center;font-size:11px;color:var(--muted);pointer-events:none}

/* ---- people grid ---- */
.searchbar{position:sticky;top:0;z-index:5;padding:2px 0 10px;background:linear-gradient(180deg,var(--bg) 70%,transparent)}
.searchbar input{width:100%;padding:12px 16px;border-radius:14px;border:1px solid var(--line);background:var(--surface);
  color:var(--txt);font-size:15px;font-family:inherit;outline:none}
.searchbar input:focus{border-color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:10px;padding-bottom:10px}
.pcard{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 10px;text-align:center;
  cursor:pointer;animation:fadeUp .4s ease both;transition:transform .12s,border-color .12s}
.pcard:active{transform:scale(.96)}
.pcard .ava{width:54px;height:54px;border-radius:50%;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;
  font-family:'Cinzel',serif;font-size:19px;color:var(--cream);background:linear-gradient(135deg,var(--crimson-d),#4A2530);
  border:1px solid var(--crimson-d);overflow:hidden}
.pcard .ava img{width:100%;height:100%;object-fit:cover}
.pcard .pname{font-size:13px;color:var(--cream);line-height:1.25}
.pcard .pyears{font-size:11px;color:var(--muted);font-style:italic;margin-top:2px}
.pcard .mtag{display:inline-block;background:var(--gold);color:#241D2E;font-size:8px;font-weight:700;letter-spacing:1px;padding:1px 5px;border-radius:7px;margin-top:5px}
.pcard .you{color:var(--crimson);font-weight:700}

/* ---- stories ---- */
.scard{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:14px;
  padding:14px 16px;margin-bottom:10px;animation:fadeUp .4s ease both}
.scard h3{font-size:14.5px;color:var(--crimson);margin-bottom:6px}
.scard .who{font-size:12px;color:var(--muted);font-style:italic;margin-bottom:8px;display:block}
.scard p{font-size:15px;line-height:1.5;color:var(--txt)}
.scard .srclink{display:inline-block;margin-top:10px;font-size:13px;color:var(--gold);text-decoration:none;border:1px solid var(--gold);padding:3px 12px;border-radius:14px}
.scard .srclink:active{background:var(--gold);color:#241D2E}

/* ---- timeline ---- */
.tlist{position:relative;padding-left:22px}
.tlist::before{content:"";position:absolute;left:7px;top:4px;bottom:4px;width:2px;background:var(--line)}
.tevent{position:relative;margin-bottom:14px;animation:fadeUp .4s ease both}
.tevent::before{content:"";position:absolute;left:-21px;top:6px;width:11px;height:11px;border-radius:50%;background:var(--gold);border:2px solid var(--bg)}
.tevent.hist::before{background:var(--muted)}
.tevent .yr{font-family:'Cinzel',serif;font-size:13px;color:var(--gold);font-weight:700}
.tevent p{font-size:14px;color:var(--txt);line-height:1.4;margin-top:1px}

/* ---- tab bar ---- */
.tabbar{position:fixed;left:0;right:0;bottom:0;height:62px;display:flex;background:rgba(20,18,26,.92);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-top:1px solid var(--line);z-index:50}
.tab{flex:1;background:none;border:none;color:var(--muted);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;cursor:pointer;font-family:'Cinzel',serif;font-size:10.5px;letter-spacing:.5px;transition:color .2s}
.tab .ti{font-size:19px;line-height:1}
.tab.active{color:var(--gold)}
.tab.active .ti{animation:pop .3s ease}
@keyframes pop{0%{transform:scale(.6)}70%{transform:scale(1.2)}100%{transform:scale(1)}}

/* ---- bottom sheet ---- */
#backdrop{position:fixed;inset:0;background:rgba(0,0,0,.55);opacity:0;pointer-events:none;transition:opacity .28s ease;z-index:60}
#backdrop.show{opacity:1;pointer-events:auto}
#sheet{position:fixed;left:0;right:0;bottom:0;max-height:82vh;background:var(--surface);border-radius:22px 22px 0 0;
  border-top:1px solid var(--line);transform:translateY(105%);transition:transform .32s cubic-bezier(.2,.9,.25,1);z-index:70;
  overflow-y:auto;scrollbar-width:thin;padding:12px 20px 34px}
#sheet.open{transform:translateY(0)}
.sheet-handle{width:44px;height:4px;border-radius:2px;background:var(--line);margin:0 auto 12px}
.sheet-close{position:absolute;top:14px;right:14px;background:none;border:none;color:var(--muted);font-size:19px;cursor:pointer}
.shead{display:flex;gap:14px;align-items:center;margin-bottom:14px}
.shead .sava{width:76px;height:76px;border-radius:16px;overflow:hidden;flex-shrink:0;background:linear-gradient(135deg,var(--crimson-d),#4A2530);
  display:flex;align-items:center;justify-content:center;font-family:'Cinzel',serif;font-size:26px;color:var(--cream);border:1px solid var(--line)}
.shead .sava img{width:100%;height:100%;object-fit:cover}
.shead .sname{font-family:'Cinzel',serif;font-size:19px;color:var(--cream)}
.shead .smeta{font-size:13px;color:var(--muted);font-style:italic;margin-top:3px}
.smeta .mtag{font-style:normal;background:var(--gold);color:#241D2E;font-size:9px;font-weight:700;letter-spacing:1px;padding:2px 7px;border-radius:8px;margin-left:6px}
.snote{font-size:15px;line-height:1.5;color:var(--txt);margin-bottom:12px}
.sstory{background:var(--surface2);border-left:3px solid var(--gold);border-radius:12px;padding:12px 14px;margin-bottom:12px}
.sstory p{font-size:14.5px;line-height:1.5;color:var(--txt)}
.sstory .srclink{display:inline-block;margin-top:8px;font-size:12.5px;color:var(--gold);text-decoration:none;border:1px solid var(--gold);padding:2px 10px;border-radius:12px}
.srel{margin-top:6px}
.srel h4{font-family:'Cinzel',serif;font-size:12px;letter-spacing:1px;color:var(--muted);margin:12px 0 6px;text-transform:uppercase}
.srel .chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:4px 12px;font-size:13px;color:var(--cream);cursor:pointer}
.chip:active{border-color:var(--gold)}
.chip.metis{border-color:var(--gold)}
.chip.you{border-color:var(--crimson);color:var(--crimson)}
"""

JS = r"""
const D = __DATA__;
const people = Object.fromEntries(D.people.map(p=>[p.id,p]));
const P = D.people;
const byName = {};
P.forEach(p=>byName[p.name.toLowerCase()]=p);

/* ---------- tree canvas ---------- */
// ---- FamilyTree JS: classic descendant chart ----
const FT_NODES = D.tree.ftNodes;
var family = new FamilyTree(document.getElementById("ftree"), {
  nodes: FT_NODES,
  nodeBinding: {field_0: "name", field_1: "note"},
  anim: {duration: 0},
  enableSearch: true,
  searchFields: ["name"],
  scaleInitial: 0.5,
  editForm: {readOnly: true},
  nodeTreeMenu: false,
  nodeMouseClick: function(sender, args){
    if(args.node && args.node.ref) openSheet([args.node.ref]);
    return false;
  }
});
document.getElementById('zin').onclick=()=>family.zoomIn();
document.getElementById('zout').onclick=()=>family.zoomOut();
// fit that ignores nodes the layout dropped (NaN coords) - family.fit() NaNs
// because the boundary is computed over those dropped nodes.
function fitGood(){
  const f=family, svg=f.getSvg();
  let minX=1e9,maxX=-1e9,minY=1e9,maxY=-1e9;
  for(const k in f.nodes){ const n=f.nodes[k];
    if(n.x===undefined||isNaN(n.x)||isNaN(n.y))continue;
    if(n.x<minX)minX=n.x; if(n.x+n.w>maxX)maxX=n.x+n.w;
    if(n.y<minY)minY=n.y; if(n.y+n.h>maxY)maxY=n.y+n.h; }
  if(minX===1e9)return;
  const pad=30, W=f.width(), H=f.height();
  const w=maxX-minX, h=maxY-minY;
  const sc=Math.min((W-2*pad)/w,(H-2*pad)/h);
  svg.setAttribute('viewBox',((minX-pad)+' '+(minY-pad)+' '+(w+2*pad)+' '+(h+2*pad)));
}
document.getElementById('zfit').onclick=fitGood;
family.onInit(function(){ try{ fitGood(); }catch(e){} });
setTimeout(function(){ if(!family._initialized){ try{ family.draw(); fitGood(); }catch(e){ console.log('FT kick:', e.message); } } }, 700);

function escH(s){const d=document.createElement('div');d.textContent=s??'';return d.innerHTML;}
function yrs(p){const b=p.birth,dd=p.death;
  if(b&&dd)return b+'–'+dd; if(b)return 'b. '+b; if(dd)return 'd. '+dd; return '';}
function fmtYears(p){return yrs(p);}
function initials(nm){return nm.split(/[\s-]+/).filter(w=>w[0]&&w[0]===w[0].toUpperCase()&&w.length>1).slice(0,2).map(w=>w[0]).join('')||nm.slice(0,2).toUpperCase();}

/* ---------- tabs ---------- */
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    const tab=t.dataset.tab;
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    const v=document.getElementById('view-'+tab);v.classList.add('active');
    if(tab==='tree')setTimeout(()=>{try{family.fit();}catch(e){}},60);
  });
});

/* ---------- people grid ---------- */
const grid=document.getElementById('peoplegrid');
function renderPeople(filter){
  const q=(filter||'').toLowerCase();
  const list=P.filter(p=>!q||p.name.toLowerCase().includes(q)||(p.note||'').toLowerCase().includes(q));
  grid.innerHTML='';
  list.forEach((p,i)=>{
    const c=document.createElement('div');
    c.className='pcard';c.style.animationDelay=(i%20)*0.02+'s';
    const img=D.images[p.id]?`<img src="${D.images[p.id]}" alt="">`:'';
    const metis=p.metis?'<span class="mtag">MÉTIS</span>':'';
    const you=p.you?' <span class="you">★ you</span>':'';
    c.innerHTML=`<div class="ava">${img||escH(initials(p.name))}</div><div class="pname">${escH(p.name)}${you}</div><div class="pyears">${escH(fmtYears(p))}</div>${metis}`;
    c.addEventListener('click',()=>openSheet([p.id]));
    grid.appendChild(c);
  });
}
document.getElementById('search').addEventListener('input',e=>renderPeople(e.target.value));
renderPeople('');

/* ---------- stories ---------- */
const sl=document.getElementById('storylist');
Object.entries(D.stories).forEach(([pid,s],i)=>{
  const p=people[pid];if(!p)return;
  const img=D.images[pid]?'':''; // story cards stay text-forward
  const card=document.createElement('div');
  card.className='scard';card.style.animationDelay=(i%8)*0.05+'s';
  const src=s.source?`<a class="srclink" href="${escH(s.source)}" target="_blank" rel="noopener">source ↗</a>`:'';
  card.innerHTML=`<h3>${escH(s.title)}</h3><span class="who">${escH(p.name)}</span><p>${escH(s.text)}</p>${src}`;
  sl.appendChild(card);
});

/* ---------- timeline ---------- */
const tl=document.getElementById('timelinelist');
D.timeline.forEach(([year,kind,text],i)=>{
  const d=document.createElement('div');
  d.className='tevent'+(kind==='h'?' hist':'');d.style.animationDelay=(i%10)*0.03+'s';
  d.innerHTML=`<div class="yr">${year}</div><p>${escH(text)}</p>`;
  tl.appendChild(d);
});

/* ---------- bottom sheet ---------- */
const sheet=document.getElementById('sheet'),backdrop=document.getElementById('backdrop');
function openSheet(ids){
  const ps=ids.map(id=>people[id]).filter(Boolean);
  const b=document.getElementById('sheetbody');
  if(ps.length===2){
    const [p1,p2]=ps;
    const img1=D.images[p1.id]?`<img src="${D.images[p1.id]}" alt="">`:'';
    const img2=D.images[p2.id]?`<img src="${D.images[p2.id]}" alt="">`:'';
    const u=D.unions.find(x=>(x.s1===p1.id&&x.s2===p2.id)||(x.s1===p2.id&&x.s2===p1.id));
    let h=`<div class="shead">
      <div class="sava">${img1||escH(initials(p1.name))}</div>
      <div><div class="sname">${escH(p1.name)} <span class="mtag">${p1.metis?'MÉTIS':''}</span></div>
      <div class="smeta">${escH(fmtYears(p1))}</div>
      <div class="sname" style="font-size:16px;margin-top:6px">${escH(p2.name)} <span class="mtag">${p2.metis?'MÉTIS':''}</span></div>
      <div class="smeta">${escH(fmtYears(p2))}</div></div></div>`;
    const notes=[p1.note,p2.note].filter(Boolean).map(n=>`<div class="snote">${escH(n)}</div>`).join('');
    h+=notes;
    // union note
    if(u&&u.note)h+=`<div class="snote" style="color:var(--gold)">${escH(u.note)}</div>`;
    // story for either
    [p1,p2].forEach(p=>{
      const s=D.stories[p.id];
      if(s)h+=`<div class="sstory"><p>${escH(s.text)}</p>${s.source?`<a class="srclink" href="${escH(s.source)}" target="_blank" rel="noopener">source ↗</a>`:''}</div>`;
    });
    // relatives
    h+=relativesBlock(u);
    b.innerHTML=h;
  }else{
    const p=ps[0];
    const img=D.images[p.id]?`<img src="${D.images[p.id]}" alt="">`:'';
    let h=`<div class="shead"><div class="sava">${img||escH(initials(p.name))}</div>
      <div><div class="sname">${escH(p.name)} ${p.you?'<span class="mtag">★ you</span>':''}${p.metis?' <span class="mtag">MÉTIS</span>':''}</div>
      <div class="smeta">${escH(fmtYears(p))}${p.living?' · living':''}</div></div></div>`;
    if(p.note)h+=`<div class="snote">${escH(p.note)}</div>`;
    const s=D.stories[p.id];
    if(s)h+=`<div class="sstory"><p>${escH(s.text)}</p>${s.source?`<a class="srclink" href="${escH(s.source)}" target="_blank" rel="noopener">source ↗</a>`:''}</div>`;
    h+=relativesBlock(null,p.id);
    b.innerHTML=h;
  }
  sheet.classList.add('open');backdrop.classList.add('show');
}
function relativesBlock(union,pid){
  const h=[];
  const parents=new Set(),sibs=[],children=[],spouses=[];
  D.unions.forEach(u=>{
    const s1=people[u.s1],s2=people[u.s2];
    if(u.children.includes(pid)){
      parents.add(u.s1);parents.add(u.s2);
      sibs.push(...u.children.filter(c=>c!==pid));
    }
    if(u.s1===pid){spouses.push(u.s2);children.push(...u.children);}
    if(u.s2===pid){spouses.push(u.s1);children.push(...u.children);}
  });
  if(parents.size){
    h.push(`<div class="srel"><h4>Parents</h4><div class="chips">${[...parents].map(id=>chip(id)).join('')}</div></div>`);
  }
  if(spouses.length){
    h.push(`<div class="srel"><h4>Spouse${spouses.length>1?'s':''}</h4><div class="chips">${spouses.map(id=>chip(id)).join('')}</div></div>`);
  }
  if(children.length){
    h.push(`<div class="srel"><h4>Children</h4><div class="chips">${children.map(id=>chip(id)).join('')}</div></div>`);
  }
  if(sibs.length){
    h.push(`<div class="srel"><h4>Siblings</h4><div class="chips">${sibs.map(id=>chip(id)).join('')}</div></div>`);
  }
  return h.join('');
}
function chip(id){
  const p=people[id];if(!p)return'';
  const cls=p.metis?' chip metis':''+(p.you?' chip you':'');
  return `<button class="chip${cls}" data-id="${id}">${escH(p.name)}</button>`;
}
document.getElementById('sheetbody').addEventListener('click',e=>{
  const c=e.target.closest('.chip');
  if(c){const id=c.dataset.id;openSheet([id]);}
});
function closeSheet(){sheet.classList.remove('open');backdrop.classList.remove('show');}
document.getElementById('sheetclose').onclick=closeSheet;
backdrop.addEventListener('click',closeSheet);
"""

HTML = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>{esc(PROJ['title'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style><style>@@FT_CSS@@</style>
</head><body>
{APP.replace('[[TITLE]]', esc(PROJ['title'])).replace('[[SUBTITLE]]', esc(PROJ['focus']))}
<script src="assets/familytree.min.js"></script>
<script>
const __DATA__ = {json_blob};
{JS.replace('__DATA__', '__DATA__')}
</script>
</body></html>"""

FT_CSS = """
#ftree{position:absolute;inset:58px 0 62px;background:var(--bg,#16141c)}
#ftree .node rect{fill:#241D2E!important;stroke:#3a3346!important;stroke-width:1}
#ftree .node text{fill:#F2EBD9!important;font-family:'Cinzel',serif!important}
#ftree .node.you rect{fill:#3A2C1E!important;stroke:#D4A853!important;stroke-width:2.5!important}
#ftree .node.you text{fill:#F5D78E!important}
#ftree .bft-link,#ftree line.link,#ftree path.link{stroke:#7A6D96!important}
#ftree .bft-search{background:transparent!important;border:none!important}
#ftree .bft-search input{background:#16141c!important;color:#F2EBD9!important;border:1px solid #3a3346!important;border-radius:8px!important}
#ftree .bft-button{background:#241D2E!important;color:#F2EBD9!important;border:1px solid #3a3346!important}
#ftree .bft-fill,#ftree .bft-svg{background:var(--bg,#16141c)!important}
"""
HTML = HTML.replace("@@FT_CSS@@", FT_CSS)
FT_LIB = open(os.path.join(HERE, "site", "assets", "familytree.min.js")).read()
HTML = HTML.replace('<script src="assets/familytree.min.js"></script>', "<script>" + FT_LIB + "</script>")
out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(HTML)
print(f"Wrote {out} ({len(HTML)} bytes)")
