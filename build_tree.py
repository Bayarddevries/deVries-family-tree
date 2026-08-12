#!/usr/bin/env python3
"""
build_tree.py — generate site/index.html from data/family-tree.json (schema v2).

Renders a PROPER visual family tree as SVG: couple boxes, spouse joins,
parent→child branch lines, with ancestors at top and Bayard at the bottom.
Plus full-family units, stories & profiles, and sources.

Usage: python3 build_tree.py
"""
import json, os, html as H
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "family-tree.json")))
PEOPLE = {p["id"]: p for p in DATA["people"]}

def load_image(rel):
    p = os.path.join(HERE, "site", "assets", rel)
    if not os.path.exists(p): return None
    with open(p, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
IMG = {"P030": load_image("david-spence.jpg"), "P051": load_image("john-norquay.jpg")}

def esc(s): return H.escape(str(s))

def label(pid):
    p = PEOPLE.get(pid, {})
    yrs = f"{p.get('birth','')}–{p.get('death','')}".strip("–") if (p.get('birth') or p.get('death')) else ""
    star = "★" if p.get("you") else ("◈" if p.get("highlight") else "")
    return (p["name"] + (f" {star}" if star else "") + (f"\n{yrs}" if yrs else "")).strip()

def couple_label(pid1, pid2, yrs1="", yrs2=""):
    n1 = label(pid1); n2 = label(pid2)
    return f"{n1}\n⚭\n{n2}"

# =========================================================
# TREE STRUCTURE — explicit rows (y) and edges (parent->child)
# Each node: id, label, and optional spouse (couple box) or person.
# =========================================================
# node_id -> (row, box_text, kind, [child_node_ids])
NODES = {}
def add(node_id, row, text, kind, children=()):
    NODES[node_id] = {"row": row, "text": text, "kind": kind, "children": list(children)}

ROOT = "n_root"
BR_A1 = "n_a1"; BR_B1 = "n_b1"
BR_A2 = "n_a2"; BR_B2 = "n_b2"
BR_A3 = "n_a3"; BR_B3 = "n_b3"
CONV  = "n_conv"
DORIS = "n_doris"
MAVIS = "n_mavis"
TRACY = "n_tracy"
BAY   = "n_bay"
ASH   = "n_ash"
GROVER= "n_grover"

add(ROOT,  0, couple_label("P001","P002"), "couple", [BR_A1, BR_B1])
add(BR_A1, 1, couple_label("P007","P006"), "couple", [BR_A2])
add(BR_B1, 1, couple_label("P003","P029"), "couple", [BR_B2])
add(BR_A2, 2, couple_label("P010","P018"), "couple", [BR_A3])
add(BR_B2, 2, couple_label("P030","P033"), "couple", [BR_B3])
add(BR_A3, 3, couple_label("P025","P060"), "couple", [CONV])
add(BR_B3, 3, couple_label("P041","P038"), "couple", [CONV])
add(CONV,  4, couple_label("P043","P042"), "couple", [DORIS])
add(DORIS, 5, couple_label("P044","P045"), "couple", [MAVIS])
add(MAVIS, 6, couple_label("P047","P046"), "couple", [TRACY])
add(TRACY, 7, couple_label("P048","P049"), "couple", [BAY, ASH])
add(BAY,   8, couple_label("P050","P088"), "couple", [GROVER])
add(ASH,   8, couple_label("P083","P084"), "couple", [])
add(GROVER,9, label("P089"), "person", [])

# Highlight the "you" couple in the SVG
YOUNODES = {"n_bay"}

# In-law parent branches (drawn as side notes attached to the couple)
SIDENOTES = {
    DORIS: ("Lawrence's parents", couple_label("P061","P062")),
    TRACY: ("Bryon's parents", couple_label("P067","P068")),
}

# =========================================================
# LAYOUT — bottom-up centroid x for a clean tree shape
# =========================================================
ROW_H = 118          # vertical gap between rows
NODE_W = 168         # box width
PERSON_W = 128
ROW_PAD = 26
LEAF_GAP = 24

def width(kind): return PERSON_W if kind in ("person","you") else NODE_W

def compute_layout():
    # Explicit columns: branch A left, branch B right, spine centered (hourglass).
    COL_A = 0
    COL_B = NODE_W + 48
    CENTER = (COL_A + COL_B) / 2
    def colx(col, kind):
        return col - width(kind)/2
    pos = {
        "n_root": colx(CENTER, "couple"),
        "n_a1": colx(COL_A, "couple"), "n_b1": colx(COL_B, "couple"),
        "n_a2": colx(COL_A, "couple"), "n_b2": colx(COL_B, "couple"),
        "n_a3": colx(COL_A, "couple"), "n_b3": colx(COL_B, "couple"),
        "n_conv": colx(CENTER, "couple"),
        "n_doris": colx(CENTER, "couple"),
        "n_mavis": colx(CENTER, "couple"),
        "n_tracy": colx(CENTER, "couple"),
        "n_bay": colx(CENTER - 85, "couple"),
        "n_ash": colx(CENTER + 85, "couple"),
        "n_grover": colx(CENTER - 85, "person"),
    }
    minx = min(pos.values())
    return {k: v - minx for k, v in pos.items()}

def render_svg():
    xs = compute_layout()
    # canvas width
    maxx = max(xs[n] + width(NODES[n]["kind"]) for n in NODES) + ROW_PAD*2
    maxrow = max(nd["row"] for nd in NODES.values())
    Hgt = (maxrow) * ROW_H + ROW_H
    parts = [f'<svg viewBox="-8 -8 {maxx+16} {Hgt+16}" xmlns="http://www.w3.org/2000/svg" class="tree">']
    # connector lines first
    for nid, nd in NODES.items():
        cx = xs[nid] + width(nd["kind"])/2
        top = nd["row"]*ROW_H
        bottom = top + (ROW_H - 14)
        for c in nd["children"]:
            if c not in NODES: continue
            cnd = NODES[c]
            cxc = xs[c] + width(cnd["kind"])/2
            ctop = cnd["row"]*ROW_H
            mid = (bottom + ctop)/2
            parts.append(f'<line x1="{cx:.1f}" y1="{bottom:.1f}" x2="{cx:.1f}" y2="{mid:.1f}" class="el"/>')
            parts.append(f'<line x1="{cx:.1f}" y1="{mid:.1f}" x2="{cxc:.1f}" y2="{mid:.1f}" class="el"/>')
            parts.append(f'<line x1="{cxc:.1f}" y1="{mid:.1f}" x2="{cxc:.1f}" y2="{ctop:.1f}" class="el"/>')
    # boxes
    for nid, nd in NODES.items():
        x = xs[nid]; y = nd["row"]*ROW_H
        w = width(nd["kind"]); h = ROW_H - 14
        cx = x + w/2
        cls = "you" if (nd["kind"]=="you" or nid in YOUNODES) else "metis" if nd["kind"]=="couple" else "person"
        # optional portrait
        img = ""
        if nid in ("BR_B2",):  # David Spence couple -> show his portrait at left
            img = f'<image href="{IMG["P030"]}" x="{x+6}" y="{y+6}" width="30" height="40" preserveAspectRatio="xMidYMid slice" class="pimg"/>'
        parts.append(f'<g class="b {cls}">')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="9"/>')
        if img: parts.append(img)
        lines = nd["text"].split("\n")
        # text y positions
        txt_x = x + (44 if img else 0) + w/2
        if len(lines)==1:
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2+4:.1f}" text-anchor="middle" class="tn">{esc(lines[0])}</text>')
        elif len(lines)==2:
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2-6:.1f}" text-anchor="middle" class="tn">{esc(lines[0])}</text>')
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2+14:.1f}" text-anchor="middle" class="tn">{esc(lines[1])}</text>')
        else:  # name \n ⚭ \n name
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2-12:.1f}" text-anchor="middle" class="tn">{esc(lines[0])}</text>')
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2+6:.1f}" text-anchor="middle" class="amp">⚭</text>')
            parts.append(f'<text x="{cx:.1f}" y="{y+h/2+24:.1f}" text-anchor="middle" class="tn">{esc(lines[2])}</text>')
        parts.append('</g>')
        # spouse join bar for couples (small vertical notch between names is implied by ⚭)
    parts.append('</svg>')
    return "".join(parts)

# =========================================================
# FULL FAMILY UNITS
# =========================================================
DIRECT = {'P006','P010','P025','P043','P030','P038','P042','P044','P046','P048','P050'}
def pn(pid):
    p = PEOPLE.get(pid); 
    if not p: return ""
    span = f" <span class='d'>{p.get('birth','')}–{p.get('death','')}</span>".replace("–","–") if (p.get("birth") or p.get("death")) else ""
    return f"<span class='n'>{esc(p['name'])}{span}</span>"

fam = ['<section class="fam"><h2>Full family (by generation)</h2>']
for u in DATA["unions"]:
    s1,s2 = u["spouse1"], u["spouse2"]
    if s1==s2: continue
    head = f"{PEOPLE[s1]['name']} <span class='amp'>⚭</span> {PEOPLE[s2]['name']}"
    if u.get("note"): head += f" <span class='role'>{esc(u['note'])}</span>"
    items = "".join(f"<li{' class=direct' if k in DIRECT else ''}>{pn(k)}{' <span class=star>★</span>' if PEOPLE[k].get('you') else ''}</li>" for k in u["children"])
    if not items: items='<li class="muted">(no children recorded)</li>'
    fam.append(f'<div class="famunit"><div class="head">{head}</div><ul>{items}</ul></div>')
fam.append('</section>')

# =========================================================
# ENTIRE EXTENDED FAMILY TREE — interactive, all people
# =========================================================
def build_extended():
    un = DATA["unions"]
    by_id = {u["id"]: u for u in un}
    vis_u, vis_p = set(), set()
    parts = []

    def nm(pid): return PEOPLE.get(pid, {}).get("name", "")

    def union_html(u):
        if u["id"] in vis_u: return ""
        vis_u.add(u["id"])
        s1, s2 = u["spouse1"], u["spouse2"]
        head = f"{esc(nm(s1))} <span class='amp'>⚭</span> {esc(nm(s2))}"
        if u.get("note"): head += f" <span class='role'>{esc(u['note'])}</span>"
        kids = []
        for k in u["children"]:
            if k in vis_p:
                kids.append(f"<li class='muted'>{esc(nm(k))} — family shown at its home branch</li>")
                continue
            vis_p.add(k)
            own = [x for x in by_id.values() if x["id"] not in vis_u and k in (x["spouse1"], x["spouse2"])]
            if own:
                inner = "".join(union_html(x) for x in own)
                kids.append(f"<li class='famchild'><details open><summary>{esc(nm(k))} <span class='muted'>▾ family</span></summary>{inner}</details></li>")
            else:
                kids.append(f"<li>{esc(nm(k))}</li>")
        kids_list = ("<ul class='kids'>" + "".join(kids) + "</ul>") if kids else ""
        return f"<div class='eu'><div class='ehead'>{head}</div>{kids_list}</div>"

    child_ppl = {c for u in un for c in u["children"]}
    starts = [u for u in un if u["spouse1"] not in child_ppl and u["spouse2"] not in child_ppl]
    order = {"U16": 0, "U01": 1, "U13": 2, "U14": 3}
    starts.sort(key=lambda u: order.get(u["id"], 9))
    for u in starts:
        parts.append(union_html(u))
    return "".join(parts)

EXTENDED = f'''<section class="extended"><details>
<summary><span class="ext-title">View entire extended family tree</span> <span class="ext-hint">(all {len(DATA["people"])} people, expandable)</span></summary>
<div class="extbody">{build_extended()}</div>
</details></section>'''

# =========================================================
# STORIES & PROFILES
# =========================================================
story_html=[]
if DATA.get("stories"):
    story_html.append('<section class="stories"><h2>Stories &amp; Profiles</h2>')
    for pid in ["P001","P002","P079","P007","P030","P022","P051","P067","P049","P046"]:
        s=DATA["stories"].get(pid)
        if not s: continue
        src=f'<a class="srclink" href="{esc(s["source"])}" target="_blank" rel="noopener">source ↗</a>' if s.get("source") else ""
        story_html.append(f'<details><summary>{esc(s["title"])} <span class="who">· {esc(PEOPLE[pid]["name"])}</span></summary><p>{esc(s["text"])}</p>{src}</details>')
    story_html.append('</section>')

# =========================================================
# PATHS + SOURCES
# =========================================================
paths="".join(f"<li>{esc(p)}</li>" for p in DATA["paths_to_root"])
opens="".join(f"<li>{esc(o)}</li>" for o in DATA["open_items"])
sources=f'''<div class="sources">
<h4>Sources & verification</h4>
<p><em>Red River Ancestry</em>: James Spence (1753), Andrew Setter (1777), George Setter (1815), David Spence (1824), John Norquay (1841).</p>
<p><em>Manitoba Vital Statistics:</em> Alan Setter (b. 22 Oct 1884, reg 1884,005103 — mother Sarah Ann HOWRIE); Allan Setter ⚭ Ella Alberta Riggs (1909, reg 1909,001530); Doris Alberta Setter (b. 1912, reg 1912,004481).</p>
<p><em>FamilySearch</em> (Lawrence Donald Hamilton); <em>Obituaries</em> (Bryon deVries 2019; Mavis Lau 2020; Leonard DeVries 2016); <em>Ancestry DNA tree</em>; family knowledge.</p>
<p>Hobbyist/family-tree data flagged; verify vs scrip, census, parish, vital records. Portraits (David Spence, John Norquay) from redriverancestry.ca — identified by source. Never fabricated. Living people's details not published.</p>
<h4>Open items</h4><ul class="opens">{opens}</ul>
</div>'''

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FAF6EE;color:#2A2220;font-family:'EB Garamond',Georgia,serif;padding:22px 10px 60px;line-height:1.4}
header{text-align:center;margin-bottom:6px}
header h1{font-family:'Cinzel',serif;font-weight:700;font-size:clamp(24px,5vw,38px);color:#8C1F28;margin-bottom:4px}
header p.sub{font-size:clamp(14px,3vw,17px);color:#7A6E66;font-style:italic}
.rule{height:2px;background:linear-gradient(90deg,transparent,#8C1F28,transparent);margin:14px auto;max-width:420px}
.legend{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;font-size:13px;color:#7A6E66;margin:2px 0 14px}
.legend span{display:inline-flex;align-items:center;gap:5px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}.dot.a{background:#7A3B2E}.dot.b{background:#2E5E6E}

svg.tree{display:block;max-width:100%;height:auto;margin:0 auto;background:#FCF8EF;border:1px solid #E3D7C4;border-radius:12px}
.el{stroke:#A99A83;stroke-width:2}
.b rect{stroke:#B9A793;stroke-width:1.3;fill:#FFFDF7}
.b.metis rect{fill:#FBF6EC}
.b.person rect{fill:#F7EFDF;stroke:#C9A24B}
.b.you rect{fill:#FBF1EE;stroke:#8C1F28;stroke-width:2}
.b text{font-family:'EB Garamond',Georgia,serif}
.b .tn{font-size:13px;font-weight:600;fill:#5A3B32}
.b .amp{font-size:16px;fill:#C9A24B}
.b.you .tn{font-size:14px;fill:#8C1F28;font-family:'Cinzel',serif}
.pimg{opacity:.97}

section.fam{max-width:720px;margin:30px auto 0}
section.fam h2,.stories h2,.paths h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;border-bottom:2px solid #C9A24B;padding-bottom:6px;margin-bottom:10px}
.famunit{background:#FFFDF7;border:1px solid #B9A793;border-radius:10px;padding:11px 15px;margin-bottom:9px}
.famunit .head{font-family:'Cinzel',serif;font-size:14px;color:#8C1F28;margin-bottom:5px}
.famunit ul{margin:3px 0 2px 18px;font-size:14px}.famunit li{margin-bottom:3px}
.famunit .direct{color:#8C1F28;font-weight:600}.famunit .muted{color:#B9A793;font-style:italic}
.stories{max-width:720px;margin:30px auto 0}
.stories details{background:#FFFDF7;border:1px solid #B9A793;border-left:4px solid #C9A24B;border-radius:9px;margin-bottom:8px;overflow:hidden}
.stories summary{cursor:pointer;padding:10px 14px;font-family:'Cinzel',serif;font-size:14px;color:#8C1F28;font-weight:600}
.stories summary .who{color:#7A6E66;font-weight:400;font-size:12px}
.stories details p{padding:0 14px 12px;font-size:15px;color:#2A2220;line-height:1.5}
.stories .srclink{display:inline-block;margin:0 0 12px 14px;font-size:13px;color:#8C1F28;text-decoration:none;border:1px solid #C9A24B;padding:3px 10px;border-radius:14px;background:#FBF4F0}
.paths{max-width:720px;margin:26px auto 0}
section.extended{max-width:720px;margin:26px auto 0}
section.extended details{background:#FFFDF7;border:1px solid #B9A793;border-radius:12px}
section.extended>details>summary{cursor:pointer;padding:14px 16px;font-family:'Cinzel',serif;font-size:15px;color:#8C1F28;border-radius:12px;list-style:none}
section.extended>details>summary:hover{background:#FBF4F0}
section.extended .ext-hint{font-family:'EB Garamond',serif;font-weight:400;font-size:13px;color:#7A6E66}
.extbody{padding:4px 16px 16px;border-top:1px solid #E3D7C4}
.eu{background:#FBF6EC;border:1px solid #E3D7C4;border-left:3px solid #C9A24B;border-radius:9px;padding:8px 12px;margin-top:8px}
.eu .ehead{font-family:'Cinzel',serif;font-size:13px;color:#8C1F28;font-weight:600}
.eu .ehead .role{font-family:'EB Garamond',serif;font-weight:400;font-size:11px;color:#7A6E66}
ul.kids{margin:6px 0 2px 20px;font-size:14px}
ul.kids li{margin-bottom:3px}
ul.kids .muted{color:#B9A793;font-style:italic;font-size:12px}
li.famchild>details{background:#FFFDF7;border:1px solid #E3D7C4;border-radius:7px;padding:3px 8px;margin-top:3px}
li.famchild>details>summary{cursor:pointer;font-size:13px;color:#2A2220}
li.famchild>details>summary:hover{color:#8C1F28}
.paths ol{margin-left:20px;font-size:15px}.paths li{margin-bottom:8px}
.sources{max-width:720px;margin:28px auto 0;padding-top:14px;border-top:1px solid #B9A793;font-size:13px;color:#7A6E66}
.sources h4{font-family:'Cinzel',serif;color:#2A2220;margin-bottom:6px;font-size:13px;letter-spacing:1px}
.sources p{margin-bottom:5px}.sources em{color:#8C1F28}
.sources .opens{margin-left:18px;font-size:13px}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(DATA['project']['title'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
<header><h1>{esc(DATA['project']['title'])}</h1><p class="sub">{esc(DATA['project']['focus'])}</p></header>
<div class="rule"></div>
<div class="legend">
  <span><span class="dot a"></span> Spence line A (Setter)</span>
  <span><span class="dot b"></span> Spence line B (Riggs)</span>
  <span>★ you</span>
</div>
{render_svg()}
{EXTENDED}
{''.join(fam)}
{''.join(story_html)}
<div class="paths"><h2>Your two paths to the Métis root</h2><ol>{paths}</ol></div>
{sources}
</body></html>"""

out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out,"w").write(HTML)
print(f"Wrote {out} ({len(HTML)} bytes)")
