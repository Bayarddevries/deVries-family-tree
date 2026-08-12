#!/usr/bin/env python3
"""
build_tree.py — generate site/index.html from data/family-tree.json (schema v2).

Renders a TRADITIONAL branching family tree (nested CSS tree with branch
connectors), plus full-family units, ancestor paths, and sources.
Output is self-contained (inline CSS, no external JS fetch) and mobile-first.

Usage: python3 build_tree.py
"""
import json, os, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "family-tree.json")))
PEOPLE = {p["id"]: p for p in DATA["people"]}

def esc(s): return H.escape(str(s))

def pn(pid):
    p = PEOPLE.get(pid)
    if not p: return ""
    span = ""
    if p.get("birth") or p.get("death"):
        span = f" <span class='d'>{p.get('birth','')}–{p.get('death','')}</span>".replace("–","–")
    return f"<span class='n'>{esc(p['name'])}{span}</span>"

def card(pid, role="", note=None, metis_badge=True):
    p = PEOPLE.get(pid, {})
    cls = "node" + (" you" if p.get("you") else "")
    stars = ' <span class="star">★</span>' if p.get("you") else (' <span class="star">◈</span>' if p.get("highlight") else '')
    badge = ' <span class="m">MÉTIS</span>' if (metis_badge and (p.get("metis") or (p.get("you")))) else ''
    note_html = f"<div class='role'>{esc(note or p.get('note',''))}</div>" if (note or p.get("note")) else ""
    return f'<div class="{cls}">{pn(pid)}{stars}{badge}{note_html}</div>'

def couple(pid1, pid2, note=None):
    amp = '<span class="amp">⚭</span>'
    return f'<div class="couple">{card(pid1)}{amp}{card(pid2)}{f"<div class=role>{esc(note)}</div>" if note else ""}</div>'

def li(cards, children_html=None):
    kids = f"<ul>{children_html}</ul>" if children_html else ""
    return f"<li>{cards}{kids}</li>"

# =========================================================
# TRADITIONAL TREE — nested <ul> with branch connectors
# =========================================================
tree = []
# Root
tree.append(li(couple("P001","P002","⚑ Métis root · James Spence Sr & Margaret 'Nestichio' Batt")))

# Two Spence branches (siblings under the root)
tree.append("<li><div class='branchlabel'>The two Spence lines</div><ul>")

# Branch A — Setter line
branchA = li(
    couple("P007","P006","Spence line A"),
    li(
        couple("P010","P018","George Setter · also m. Jessie Campbell 1824–1912"),
        li(
            couple("P025","P060","Roderick McKenzie Setter · m. Sarah Ann Howrie 1879"),
            li(card("P043", note="Alan Setter → line A", metis_badge=False))
        )
    )
)
tree.append(branchA)

# Branch B — Spence/Riggs line
branchB = li(
    couple("P003","P029","Spence line B"),
    li(
        couple("P030","P033","David Spence, MLA"),
        li(
            couple("P041","P038","Ernest Riggs · Mary Ann Spence"),
            li(card("P042", note="Ella Alberta Riggs → line B", metis_badge=False))
        )
    )
)
tree.append(branchB)

tree.append("</ul></li>")

# Convergence — marriage of the two branches
tree.append(li(couple("P043","P042","★ The two lines converge · Alan Setter ⚭ Ella Riggs, m. 31 Mar 1909, Portage la Prairie")))

# Hamilton branch — Lawrence's parents (before the Doris+Lawrence couple)
tree.append(li(couple("P061","P062","Hamilton branch · Lawrence's parents · Guy Wentworth Hamilton ⚭ Ethel Rose King")))

# deVries branch — Bryon's parents (before the Tracy+Bryon couple)
tree.append(li(couple("P067","P068","deVries branch · Bryon's parents · Gerhard De Vries ⚭ Geeske Oltrop (Ochre River MB, Dutch/Friesland)")))

# Trunk down to Bayard
trunk = li(
    couple("P044","P045","Doris A. Setter ⚭ Lawrence D. Hamilton"),
    li(
        couple("P047","P046","Robert Lau · Mavis Irene Hamilton"),
        li(
            couple("P048","P049","Tracy Diane Lau · Bryon deVries"),
            li(card("P050"))
        )
    )
)
tree.append(trunk)

tree_html = f'<div class="treeroot">{""}</div><ul class="tree">{"".join(tree)}</ul>'

# =========================================================
# FULL FAMILY UNITS
# =========================================================
DIRECT = {'P006','P010','P025','P043','P030','P038','P042','P044','P046','P048','P050'}
fam = ['<section class="fam"><h2>Full family (by generation)</h2>']
for u in DATA["unions"]:
    s1, s2 = u["spouse1"], u["spouse2"]
    if s1 == s2: continue
    head = f"{PEOPLE[s1]['name']} <span class='amp'>⚭</span> {PEOPLE[s2]['name']}"
    if u.get("note"): head += f" <span class='role'>{esc(u['note'])}</span>"
    items = "".join(
        f"<li{' class=direct' if k in DIRECT else ''}>{pn(k)}{' <span class=star>★</span>' if PEOPLE[k].get('you') else ''}</li>"
        for k in u["children"])
    if not items: items = '<li class="muted">(no children recorded)</li>'
    fam.append(f'<div class="famunit"><div class="head">{head}</div><ul>{items}</ul></div>')
fam.append('</section>')

# =========================================================
# STORIES & PROFILES
# =========================================================
story_html = []
if DATA.get("stories"):
    story_html.append('<section class="stories"><h2>Stories &amp; Profiles</h2>')
    # order: oldest-first by generation depth (compute via unions is complex; use fixed order)
    order = ["P001","P002","P007","P030","P022","P051","P067","P049","P046"]
    for pid in order:
        s = DATA["stories"].get(pid)
        if not s: continue
        name = PEOPLE[pid]["name"]
        story_html.append(f'<details><summary>{esc(s["title"])} <span class="who">· {esc(name)}</span></summary><p>{esc(s["text"])}</p></details>')
    story_html.append('</section>')

# =========================================================
# PATHS + SOURCES
# =========================================================
paths = "".join(f"<li>{esc(p)}</li>" for p in DATA["paths_to_root"])
opens = "".join(f"<li>{esc(o)}</li>" for o in DATA["open_items"])
sources = f'''<div class="sources">
<h4>Sources & verification</h4>
<p><em>Red River Ancestry</em>: James Spence (1753), Andrew Setter (1777), George Setter (1815), David Spence (1824).</p>
<p><em>Manitoba Vital Statistics:</em> Alan Setter (b. 22 Oct 1884, Portage la Prairie RM, reg 1884,005103 — mother Sarah Ann HOWRIE); Allan Setter ⚭ Ella Alberta Riggs (31 Mar 1909, reg 1909,001530); Doris Alberta Setter (b. 24 Dec 1912, reg 1912,004481).</p>
<p><em>Ancestry DNA tree</em> (family screenshots, Aug 2026) · family knowledge.</p>
<p>Hobbyist/family-tree data is flagged and should be verified against scrip, census, parish, and vital records. Never fabricated. Living people's details not published.</p>
<h4>Open items</h4><ul class="opens">{opens}</ul>
</div>'''

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FAF6EE;color:#2A2220;font-family:'EB Garamond',Georgia,serif;padding:22px 14px 60px;line-height:1.4}
header{text-align:center;margin-bottom:6px}
header h1{font-family:'Cinzel',serif;font-weight:700;font-size:clamp(24px,5vw,38px);color:#8C1F28;margin-bottom:4px}
header p.sub{font-size:clamp(14px,3vw,17px);color:#7A6E66;font-style:italic}
.rule{height:2px;background:linear-gradient(90deg,transparent,#8C1F28,transparent);margin:16px auto;max-width:420px}
.legend{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;font-size:13px;color:#7A6E66;margin:2px 0 18px}
.legend span{display:inline-flex;align-items:center;gap:5px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}.dot.a{background:#7A3B2E}.dot.b{background:#2E5E6E}

/* Traditional tree */
.tree, .tree ul{list-style:none;padding:0;margin:0;position:relative}
.tree{padding-left:20px}
.tree li{position:relative;margin:10px 0 10px 22px;padding-left:22px}
/* horizontal branch to node */
.tree li::before{content:'';position:absolute;left:-22px;top:50%;width:22px;height:2px;background:#B9A793}
/* vertical trunk from this node down through its children */
.tree li::after{content:'';position:absolute;left:-22px;top:50%;bottom:-10px;width:2px;background:#B9A793}
.tree li:last-child::after{height:0}
/* vertical line from parent node down to first child rail */
.tree > li::before{background:#B9A793}
.tree > li::after{display:none}

.node{display:inline-block;background:#FFFDF7;border:1px solid #B9A793;border-left:4px solid #C9A24B;border-radius:9px;padding:7px 12px;box-shadow:0 2px 5px rgba(0,0,0,.05);font-size:clamp(13px,3.4vw,15px)}
.node .n{font-family:'Cinzel',serif;font-weight:600;color:#8C1F28}
.node .d{color:#7A6E66;font-size:.82em;font-weight:500}
.node .star{color:#C9A24B}
.node.you{border-color:#8C1F28;border-left-width:4px;border-left-color:#8C1F28;background:#FBF4F0}
.node .m{display:inline-block;background:#C9A24B;color:#fff;font-size:9px;font-family:'Cinzel',serif;letter-spacing:1px;padding:1px 6px;border-radius:8px;vertical-align:middle;margin-left:4px}
.node .role{font-size:12px;color:#7A6E66;font-style:italic;margin-top:2px;max-width:230px}
.couple{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.couple .amp{color:#C9A24B;font-weight:700;font-size:16px}
.branchlabel{font-family:'Cinzel',serif;font-size:11px;letter-spacing:1.5px;color:#7A6E66;margin:4px 0 2px}
.treeroot{text-align:center;font-family:'Cinzel',serif;font-size:12px;color:#7A6E66;margin-bottom:8px;letter-spacing:1px}

section.fam{max-width:720px;margin:34px auto 0}
section.fam h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;border-bottom:2px solid #C9A24B;padding-bottom:6px;margin-bottom:10px}
.famunit{background:#FFFDF7;border:1px solid #B9A793;border-radius:10px;padding:11px 15px;margin-bottom:9px}
.famunit .head{font-family:'Cinzel',serif;font-size:14px;color:#8C1F28;margin-bottom:5px}
.famunit ul{margin:3px 0 2px 18px;font-size:14px}
.famunit li{margin-bottom:3px}
.famunit .direct{color:#8C1F28;font-weight:600}
.famunit .muted{color:#B9A793;font-style:italic}
.paths{max-width:720px;margin:26px auto 0}
.stories{max-width:720px;margin:30px auto 0}
.stories h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;border-bottom:2px solid #C9A24B;padding-bottom:6px;margin-bottom:10px}
.stories details{background:#FFFDF7;border:1px solid #B9A793;border-left:4px solid #C9A24B;border-radius:9px;margin-bottom:8px;overflow:hidden}
.stories summary{cursor:pointer;padding:10px 14px;font-family:'Cinzel',serif;font-size:14px;color:#8C1F28;font-weight:600}
.stories summary .who{color:#7A6E66;font-weight:400;font-size:12px}
.stories details p{padding:0 14px 12px;font-size:15px;color:#2A2220;line-height:1.5}
.paths h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;border-bottom:2px solid #C9A24B;padding-bottom:6px;margin-bottom:10px}
.paths ol{margin-left:20px;font-size:15px}.paths li{margin-bottom:8px}
.sources{max-width:720px;margin:28px auto 0;padding-top:14px;border-top:1px solid #B9A793;font-size:13px;color:#7A6E66}
.sources h4{font-family:'Cinzel',serif;color:#2A2220;margin-bottom:6px;font-size:13px;letter-spacing:1px}
.sources p{margin-bottom:5px}.sources em{color:#8C1F28}
.sources .opens{margin-left:18px;font-size:13px}
@media(max-width:520px){.tree{padding-left:14px}.tree li{margin-left:16px;padding-left:16px}.tree li::before{left:-16px;width:16px}.tree li::after{left:-16px}.node .role{max-width:190px}}
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
  <span>★ you · ◈ notable</span>
</div>
{tree_html}
{''.join(fam)}
{''.join(story_html)}
<div class="paths"><h2>Your two paths to the Métis root</h2><ol>{paths}</ol></div>
{sources}
</body></html>"""

out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(HTML)
print(f"Wrote {out} ({len(HTML)} bytes, {len(PEOPLE)} people, {len(DATA['unions'])} unions)")
