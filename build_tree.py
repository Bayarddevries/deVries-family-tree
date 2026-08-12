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
# FULL EXTENDED TREE LAYOUT (all unions, all people)
# classic columnar descendant chart: two lineage trunks (Setter line A,
# Spence/Riggs line B) converging into the central spine down to Bayard.
# Hand-placed column slots -> real tree silhouette with clear columns.
# =========================================================
P_W, P_H = 116, 54                 # person box
GAP2 = 16                          # gap between spouses (marriage bar spans this)
ROW_H = 140
LEAF_GAP = 8                       # gap between leaf siblings on a rail

by_union = {u["id"]: u for u in UNIONS}

def spouse_unions(pid):
    return [u for u in UNIONS if pid in (u["spouse1"], u["spouse2"])]

PERS, FAMS, TEDGES = [], [], []

def add_person(pid, x, y, you=False):
    nid = "b" + str(len(PERS))
    PERS.append({"id": nid, "pid": pid, "x": round(x, 1), "y": y,
                 "w": P_W, "h": P_H, "you": you})
    return nid

def add_couple(u_id, x, row, you=False):
    u = by_union[u_id]
    n1 = add_person(u["spouse1"], x - P_W - GAP2/2, row*ROW_H, you and u["spouse1"] == "P050")
    n2 = add_person(u["spouse2"], x + GAP2/2, row*ROW_H, you and u["spouse2"] == "P050")
    fam = {"u": u_id, "s1": n1, "s2": n2,
           "s1x": x - P_W/2 - GAP2/2, "s2x": x + P_W/2 + GAP2/2,
           "x": x, "y": row*ROW_H, "children": []}
    FAMS.append(fam)
    return fam, n1, n2

def leaf_boxes(u, row, cx):
    """leaf child boxes of union u spread on a rail at row, centered on cx"""
    leaves = [c for c in u["children"]
              if not any(c in (fu["spouse1"], fu["spouse2"]) for fu in UNIONS if fu["id"] != u["id"])]
    if not leaves: return []
    n = len(leaves); total = n*(P_W + LEAF_GAP) - LEAF_GAP
    x0 = cx - total/2
    out = []
    for i, pid in enumerate(leaves):
        bx = x0 + i*(P_W + LEAF_GAP)
        nid = add_person(pid, bx, row*ROW_H)
        out.append((nid, bx + P_W/2))
    return out

# ---- explicit columnar layout (x = canvas center; COL = column pitch) ----
COL = 470
# rows 0-2: the Batt root spine (top center)
f16, isaac_b, _ = add_couple("U16", 0, 0)
f15, marg_b, _  = add_couple("U15", 0, 1)
f01, james_b, nest_b = add_couple("U01", 0, 2)
f16["children"] = [(isaac_b, f15["s1x"])]                # Isaac hangs under Dantzick
f15["children"] = [(marg_b, f01["s2x"])]                 # Margaret hangs under Isaac

# row 3: the two Spence lines split into two columns
f02, andrew_b, peggy_b = add_couple("U02", -COL, 3)
f04, jamesj_b, jane_b  = add_couple("U04",  COL, 3)
# U01's rail drops to Andrew (U02), Peggy (U02) and JamesJr (U04); George Sr is a leaf
george_sr = leaf_boxes(by_union["U01"], 3, 0)          # George Spence Sr leaf at center
f01["children"] = [(andrew_b, f02["s1x"]), (peggy_b, f02["s2x"]), (jamesj_b, f04["s1x"])] + george_sr

# row 4: line A = George's two marriages; line B = David
f03, george_b1, isab_b = add_couple("U03", -COL-230, 4)
f19, george_b2, jess_b = add_couple("U19", -COL+230, 4)
f05, david_b, cath_b   = add_couple("U05",  COL, 4)
f02["children"] = [(george_b1, f03["s1x"]), (george_b2, f19["s1x"])] + leaf_boxes(by_union["U02"], 4, -COL)
f04["children"] = [(david_b, f05["s1x"])] + leaf_boxes(by_union["U04"], 4, COL)

# row 5: line A = Roderick; line B = Ernest; Elizabeth⚭Norquay side branch
f12, rod_b, sarah_b  = add_couple("U12", -COL, 5)
f06, ern_b, mary_b   = add_couple("U06",  COL, 5)
f11, eliz_b, norq_b  = add_couple("U11", -COL*1.9, 5)
f03["children"] = [(eliz_b, f11["s1x"])] + leaf_boxes(by_union["U03"], 5, -COL-230)
f19["children"] = [(rod_b, f12["s1x"])] + leaf_boxes(by_union["U19"], 5, -COL)
f05["children"] = [(mary_b, f06["s2x"])] + leaf_boxes(by_union["U05"], 5, COL)

# row 6: the two lines CONVERGE at Alan⚭Ella; Hamilton in-law column
f07, alan_b, ella_b  = add_couple("U07", 0, 6)
f13, guy_b, ethel_b  = add_couple("U13", COL*2.1, 6)
f12["children"] = [(alan_b, f07["s1x"])]               # line A drops into Alan
f06["children"] = [(ella_b, f07["s2x"])]               # line B drops into Ella
TEDGES.append({"from": "fam_U08", "to": "fam_U13", "up": True})   # Lawrence's parents

# row 7: the trunk: Doris⚭Lawrence; Hamilton leaves beside their column
f08, doris_b, law_b  = add_couple("U08", 0, 7)
f07["children"] = [(doris_b, f08["s1x"])] + leaf_boxes(by_union["U07"], 7, 0)
f13["children"] += leaf_boxes(by_union["U13"], 7, COL*2.1)

# row 8: Mavis⚭Robert; deVries in-law column
f09, mavis_b, rob_b  = add_couple("U09", -220, 8)
f14, ger_b, gees_b   = add_couple("U14", COL*2.1, 8)
f08["children"] = [(mavis_b, f09["s1x"])] + leaf_boxes(by_union["U08"], 8, -220)
TEDGES.append({"from": "fam_U10", "to": "fam_U14", "up": True})   # Bryon's parents

# row 9: Tracy⚭Bryon; deVries leaves in their column
f10, tracy_b, bry_b  = add_couple("U10", 0, 9)
f09["children"] = [(tracy_b, f10["s1x"])] + leaf_boxes(by_union["U09"], 9, -220)
f14["children"] += leaf_boxes(by_union["U14"], 9, COL*2.1)

# row 10: Bayard⚭Paula and Ashley⚭Noel
f17, bay_b, paula_b  = add_couple("U17", -300, 10, you=True)
f18, ash_b, noel_b   = add_couple("U18",  300, 10)
f10["children"] = [(bay_b, f17["s1x"]), (ash_b, f18["s1x"])]

# row 11: the kids
f17["children"] = leaf_boxes(by_union["U17"], 11, -300)
f18["children"] = leaf_boxes(by_union["U18"], 11,  300)

# --- resolve same-row overlaps: sweep by COUPLE UNITS so spouses stay adjacent ---
rows = {}
for n in PERS:
    rows.setdefault(n["y"], []).append(n)
byid_p = {n["id"]: n for n in PERS}
for y, ns in rows.items():
    units, used = [], set()
    for f in FAMS:
        n1, n2 = byid_p[f["s1"]], byid_p[f["s2"]]
        if n1["y"] == y:
            units.append([n1, n2]); used.add(n1["id"]); used.add(n2["id"])
    for n in ns:
        if n["id"] not in used:
            units.append([n])
    units.sort(key=lambda u: min(b["x"] for b in u))
    for i in range(1, len(units)):
        prev_max = max(b["x"] + b["w"] for b in units[i-1])
        cur_min = min(b["x"] for b in units[i])
        if cur_min < prev_max + 10:
            shift = prev_max + 10 - cur_min
            for b in units[i]:
                b["x"] = round(b["x"] + shift, 1)

# ---- generation lane labels ----
bay_depth = 10
def lane_label(d):
    rel = bay_depth - d
    if rel == 0: return "You"
    if rel == 1: return "Parents"
    if rel == 2: return "Grandparents"
    if rel == 3: return "Great-grandparents"
    if rel >= 4: return f"{rel-2}× great-grandparents"
    if rel == -1: return "Children"
    if rel == -2: return "Grandchildren"
    return f"desc {abs(rel)} gen"
TREE_LANES = [{"y": d*ROW_H, "label": lane_label(d)} for d in range(12)]

# shift boxes right to make room for the label column
for n in PERS: n["x"] += 130

# canvas bounds (keep a 130px label gutter on the left)
minx = min(n["x"] for n in PERS)
maxx = max(n["x"] + n["w"] for n in PERS)
maxy = max(n["y"] + n["h"] for n in PERS)
for n in PERS: n["x"] -= (minx - 130)

# recompute family geometry from the FINAL box positions
bybox = {n["id"]: n for n in PERS}
for f in FAMS:
    n1, n2 = bybox[f["s1"]], bybox[f["s2"]]
    f["s1x"] = n1["x"] + P_W/2
    f["s2x"] = n2["x"] + P_W/2
    f["x"] = (f["s1x"] + f["s2x"])/2
    f["y"] = n1["y"]
    f["children"] = [(cid, bybox[cid]["x"] + P_W/2) for cid, _ in f["children"]]
TREE = {"nodes": PERS, "fams": FAMS, "edges": TEDGES, "lanes": TREE_LANES,
        "pw": P_W, "ph": P_H, "rowh": ROW_H,
        "w": int(maxx - minx + 190), "h": int(maxy + 60)}

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
    <div id="wrap">
      <div id="stage">
        <div id="canvas"></div>
      </div>
      <div id="lanes"></div>
      <div class="zbtns">
        <button class="zbtn" id="zin">+</button>
        <button class="zbtn" id="zout">−</button>
        <button class="zbtn" id="zfit">⤢</button>
      </div>
      <div class="hint" id="treehint">drag to pan · pinch or double-tap to zoom · tap a person</div>
    </div>
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
const wrap=document.getElementById('wrap'), stage=document.getElementById('stage'), canvas=document.getElementById('canvas');
let scale=1,tx=40,ty=30,initial=null;
const T=D.tree;
function drawTree(){
  canvas.innerHTML='';
  canvas.style.width=T.w+'px';canvas.style.height=T.h+'px';
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('width',T.w);svg.setAttribute('height',T.h);
  svg.style.position='absolute';svg.style.top='0';svg.style.left='0';svg.style.pointerEvents='none';
  const defs=document.createElementNS('http://www.w3.org/2000/svg','defs');
  defs.innerHTML='<linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A4258"/><stop offset="1" stop-color="#2E2839"/></linearGradient>';
  svg.appendChild(defs);
  const seg=(x1,y1,x2,y2,color,w,dash)=>{
    const l=document.createElementNS('http://www.w3.org/2000/svg','line');
    l.setAttribute('x1',x1);l.setAttribute('y1',y1);l.setAttribute('x2',x2);l.setAttribute('y2',y2);
    l.setAttribute('stroke',color||'url(#lg)');l.setAttribute('stroke-width',w||2.5);
    if(dash)l.setAttribute('stroke-dasharray','5,5');
    svg.appendChild(l);
  };
  // classic structure: marriage bars + child rails (THICK, high-visibility lines)
  const PW=T.pw, PH=T.ph, RH=T.rowh;
  const RAIL='#7A6D96', MAR='#E8B45A';
  const famById={};T.fams.forEach(f=>famById['fam_'+f.u]=f);
  T.fams.forEach(f=>{
    const my=f.y+PH/2;
    seg(f.s1x+PW/2, my, f.s2x-PW/2, my, MAR, 4.5);                 // marriage bar
    const y0=f.y+PH, ry=y0+26;
    seg(f.x, y0, f.x, ry, RAIL, 4);                                // drop from marriage
    if(f.children.length){
      const cxs=f.children.map(c=>c[1]);
      // rail must always span from the marriage drop to every child (even a single child)
      const mn=Math.min(f.x, ...cxs), mx=Math.max(f.x, ...cxs);
      if(mx-mn>3) seg(mn, ry, mx, ry, RAIL, 4);                    // children rail
      const ctop=f.y+RH;
      f.children.forEach(([pid,cx])=>{ seg(cx, ry, cx, ctop, RAIL, 4); });
    }
  });
  // special edges: dashed convergence + in-law stubs (up)
  T.edges.forEach(e=>{
    if(e.dashed){
      const a=nodeById(e.from), fam=famById[e.to];
      if(a&&fam){
        seg(a.x+a.w/2, a.y+a.h, fam.x, fam.y+PH/2, MAR, 3, true);
      }
    }else if(e.up){
      const f1=famById[e.from], f2=famById[e.to];
      if(f1&&f2){
        const x1=f1.x, y1=f1.y, x2=f2.x, y2=f2.y+PH;
        const mid=(y1+y2)/2;
        seg(x1,y1,x1,mid,RAIL,3.5);seg(x1,mid,x2,mid,RAIL,3.5);seg(x2,mid,x2,y2,RAIL,3.5);
      }
    }
  });
  canvas.appendChild(svg);
  renderLanes();
  T.nodes.forEach(n=>{
    const p=people[n.pid];
    if(!p)return;
    const div=document.createElement('div');
    div.className='cnode'+(n.you?' you':'');
    div.style.left=n.x+'px';div.style.top=n.y+'px';div.style.width=n.w+'px';div.style.height=n.h+'px';
    let h='';
    h+=`<div class="n1">${escH(p.name)}</div><div class="years">${escH(yrs(p))}</div>`;
    if(p.metis)h+='<span class="m">MÉTIS</span>';
    div.innerHTML=h;
    if(p.name.length>15)div.classList.add('long');
    div.addEventListener('click',()=>openSheet([n.pid]));
    canvas.appendChild(div);
  });
  applyTransform();
}
function nodeById(id){return T.nodes.find(n=>n.id===id);}
function applyTransform(){
  canvas.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;
  laneEls.forEach(el=>{el.style.top=(ty+el._y*scale)+'px';});
}
// generation lane labels: fixed axis on the left, tracks rows vertically
let laneEls=[];
function renderLanes(){
  const host=document.getElementById('lanes');
  host.innerHTML='';
  laneEls=[];
  (T.lanes||[]).forEach(l=>{
    const d=document.createElement('div');
    d.className='lane';
    d._y=l.y;
    d.textContent=l.label;
    host.appendChild(d);
    laneEls.push(d);
  });
  applyTransform();
}
function fit(){
  const cw=wrap.clientWidth,ch=wrap.clientHeight;
  scale=Math.min(cw/(T.w+40),ch/(T.h+40),1.15);scale=Math.max(scale,.25);
  tx=(cw-T.w*scale)/2;ty=(ch-T.h*scale)/2;applyTransform();
}
function zoomToYou(){
  const n=T.nodes.find(x=>x.you);
  if(!n)return fit();
  const cw=wrap.clientWidth,ch=wrap.clientHeight;
  scale=0.8;
  tx=cw/2-(n.x+n.w/2)*scale;
  ty=ch/2-(n.y+n.h/2)*scale;
  applyTransform();
}
// pan/zoom (pointer events; works for touch + mouse)
function zoomAt(cx, cy, f) {
  const ns = Math.min(5, Math.max(.2, scale * f));
  const k = ns / scale;
  tx = cx - (cx - tx) * k;
  ty = cy - (cy - ty) * k;
  scale = ns;
  applyTransform();
}
const ptrs = new Map();
let dragStart = null;      // single-finger pan anchor {x,y,tx,ty}
let pinchDist = null;      // two-finger pinch distance
let pinchMid = null;

wrap.addEventListener('pointerdown', e => {
  ptrs.set(e.pointerId, [e.clientX, e.clientY]);
  if (ptrs.size === 1) {
    dragStart = { x: e.clientX, y: e.clientY, tx: tx, ty: ty };
  } else if (ptrs.size === 2) {
    const [a, b] = [...ptrs.values()];
    pinchDist = Math.hypot(a[0]-b[0], a[1]-b[1]);
    pinchMid = [(a[0]+b[0])/2, (a[1]+b[1])/2];
    dragStart = null;
  }
});
window.addEventListener('pointermove', e => {
  if (!ptrs.has(e.pointerId)) return;
  ptrs.set(e.pointerId, [e.clientX, e.clientY]);
  if (ptrs.size === 2 && pinchDist) {
    const [a, b] = [...ptrs.values()];
    const d = Math.hypot(a[0]-b[0], a[1]-b[1]);
    const mid = [(a[0]+b[0])/2, (a[1]+b[1])/2];
    if (d > 0) zoomAt(mid[0]-wm(), mid[1]-wh(), d/pinchDist);
    pinchDist = d;
  } else if (ptrs.size === 1 && dragStart) {
    tx = dragStart.tx + (e.clientX - dragStart.x);
    ty = dragStart.ty + (e.clientY - dragStart.y);
    applyTransform();
  }
});
function endPointer(e) {
  ptrs.delete(e.pointerId);
  if (ptrs.size < 2) { pinchDist = null; pinchMid = null; }
  if (ptrs.size === 0) dragStart = null;
}
window.addEventListener('pointerup', endPointer);
window.addEventListener('pointercancel', endPointer);
wrap.addEventListener('wheel', e => {
  e.preventDefault();
  zoomAt(e.clientX-wm(), e.clientY-wh(), Math.exp(-e.deltaY*0.0015));
}, { passive: false });
function wm() { return wrap.getBoundingClientRect().left; }
function wh() { return wrap.getBoundingClientRect().top; }
// double-tap to zoom (touch)
let lastTap = 0;
wrap.addEventListener('touchend', e => {
  if (e.changedTouches.length !== 1) return;
  const now = Date.now();
  if (now - lastTap < 320) {
    const t = e.changedTouches[0];
    zoomAt(t.clientX - wm(), t.clientY - wh(), 1.8);
    lastTap = 0;
  } else lastTap = now;
}, { passive: true });
document.getElementById('zin').onclick=()=>zoomAt(wrap.clientWidth/2,wrap.clientHeight/2,1.35);
document.getElementById('zout').onclick=()=>zoomAt(wrap.clientWidth/2,wrap.clientHeight/2,1/1.35);
document.getElementById('zfit').onclick=fit;
window.addEventListener('resize',()=>{if(scale<=0.01)fit();});

// initial view: center on the "you" family once fonts/layout settle
// initial view: open at a readable zoom on the tree's middle (never fully zoomed out)
function focusMiddle(){
  const cw=wrap.clientWidth,ch=wrap.clientHeight;
  scale=Math.max(Math.min(cw/(T.w+40),ch/(T.h+40)),0.45);
  tx=cw/2-(T.w/2)*scale;
  ty=ch/2-(T.h/2)*scale;
  applyTransform();
}
function settle(){
  const doIt = () => { focusMiddle(); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(()=>setTimeout(doIt,30));
  setTimeout(doIt, 60);
}
settle();

/* ---------- helpers ---------- */
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
    if(tab==='tree')setTimeout(fit,60);
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
drawTree();
"""

HTML = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>{esc(PROJ['title'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head><body>
{APP.replace('[[TITLE]]', esc(PROJ['title'])).replace('[[SUBTITLE]]', esc(PROJ['focus']))}
<script>
const __DATA__ = {json_blob};
{JS.replace('__DATA__', '__DATA__')}
</script>
</body></html>"""

out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(HTML)
print(f"Wrote {out} ({len(HTML)} bytes)")
