#!/usr/bin/env python3
"""
build_tree.py — generate site/index.html from data/family-tree.json (schema v2).

One source of truth: the JSON. This script renders the readable, mobile-first
tree (crimson/cream exhibit aesthetic) with:
  1. The direct line (two Spence branches converging into the spine).
  2. Full family units (couple + children) per generation.
  3. Ancestor paths to root.
  4. Open items + sources footer.

Usage: python3 build_tree.py
Output: site/index.html (self-contained, inline CSS; no external JS fetch).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data", "family-tree.json")))
PEOPLE = {p["id"]: p for p in DATA["people"]}
UNIONS = DATA["unions"]

def pname(pid):
    p = PEOPLE[pid]
    return f"{p['name']} <span class='dates'>{p.get('birth','')}&ndash;{p.get('death','')}</span>".replace("&ndash;", "–") if p.get("birth") or p.get("death") else p["name"]

def metis(pid):
    return PEOPLE[pid].get("metis")

def couple_card(sp1, sp2, you=False, note=None):
    met = (metis(sp1) or metis(sp2)) and not you
    metis_badge = '<span class="metis-badge">MÉTIS</span>' if met else ''
    sp = '<div class="spouse-link">' \
         f'<div><h3>{pname(sp1)}</h3><p class="note">{PEOPLE[sp1].get("note","")}</p></div>' \
         '<span class="amp">&amp;</span>' \
         f'<div><h3>{pname(sp2)}</h3><p class="note">{PEOPLE[sp2].get("note","")}</p></div>' \
         '</div>' + metis_badge
    return f'<div class="card {"you" if you else "metis" if met else ""}">{sp}{f"<p class=note>{note}</p>" if note else ""}</div>'

def person_card(pid, highlight=False):
    p = PEOPLE[pid]
    met = metis(pid)
    cls = "card " + ("you" if p.get("you") else "metis" if met else "")
    star = '★' if p.get("you") else ('◈' if p.get("highlight") else '')
    return (f'<div class="{cls}"><h3>{pname(pid)}{" "+star if star else ""}</h3>'
            f'<p class="note">{p.get("note","")}</p></div>')

# ---------- HTML ----------
css = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FAF6EE;color:#2A2220;font-family:'EB Garamond',Georgia,serif;padding:24px 16px 60px;line-height:1.45}
header{text-align:center;margin-bottom:8px}
header h1{font-family:'Cinzel',serif;font-weight:700;font-size:clamp(24px,5vw,40px);color:#8C1F28;margin-bottom:4px}
header p.sub{font-size:clamp(14px,3vw,17px);color:#7A6E66;font-style:italic}
.rule{height:2px;background:linear-gradient(90deg,transparent,#8C1F28,transparent);margin:18px auto;max-width:420px}
.legend{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;font-size:13px;color:#7A6E66;margin:4px 0 18px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.dot.a{background:#7A3B2E}.dot.b{background:#2E5E6E}
.branch-label{font-family:'Cinzel',serif;font-size:12px;letter-spacing:1.5px;color:#7A6E66;text-align:center;margin:20px 0 8px}
.branch-label .pill{display:inline-block;padding:3px 12px;border-radius:12px;background:#F0E8DB;color:#2A2220}
.branch-label.a .pill{border-left:4px solid #7A3B2E}
.branch-label.b .pill{border-left:4px solid #2E5E6E}
.tree{max-width:660px;margin:0 auto}
.gen{display:flex;gap:14px;justify-content:center;align-items:stretch}
.gen .couple{flex:0 1 300px;min-width:0}
.gen.two .couple{flex:0 1 245px}
.card{background:#FFFDF7;border:1px solid #B9A793;border-radius:10px;padding:12px 14px;box-shadow:0 2px 6px rgba(0,0,0,.05);margin-bottom:6px}
.spouse-link{display:flex;align-items:center;gap:8px}
.spouse-link .amp{color:#C9A24B;font-weight:600}
.card h3{font-family:'Cinzel',serif;font-size:clamp(13px,3.4vw,16px);font-weight:600;line-height:1.2;color:#8C1F28}
.card h3 .dates{color:#7A6E66;font-size:.85em;font-weight:500}
.card .note{font-size:clamp(12px,3vw,14px);color:#7A6E66;margin-top:3px;font-style:italic}
.card.you{border:2px solid #8C1F28;background:#FBF4F0}
.card.you h3{color:#6E141C}
.card.metis{border-left:4px solid #C9A24B}
.metis-badge{display:inline-block;background:#C9A24B;color:#fff;font-size:10px;font-family:'Cinzel',serif;letter-spacing:1px;padding:1px 7px;border-radius:9px;margin-top:5px}
.down{text-align:center;color:#8C1F28;font-size:18px;line-height:1;margin:2px 0}
.converge{width:100%;height:44px;position:relative;margin:0}
.converge::before,.converge::after{content:'';position:absolute;width:2px;background:#B9A793;top:0;bottom:0}
.converge::before{left:25%}.converge::after{right:25%}
.converge .horiz{position:absolute;height:2px;background:#B9A793;left:25%;right:25%;top:50%}
.converge .drop{position:absolute;left:50%;top:50%;width:2px;height:50%;background:#B9A793}
.gen-title{text-align:center;font-family:'Cinzel',serif;font-size:11px;letter-spacing:1.5px;color:#7A6E66;margin:6px 0 8px;text-transform:uppercase}
section.fam{max-width:660px;margin:30px auto 0}
section.fam h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;margin-bottom:10px;border-bottom:2px solid #C9A24B;padding-bottom:6px}
.famunit{background:#FFFDF7;border:1px solid #B9A793;border-radius:10px;padding:12px 16px;margin-bottom:10px}
.famunit .head{font-family:'Cinzel',serif;font-size:14px;color:#8C1F28;margin-bottom:6px}
.famunit ul{margin:4px 0 2px 18px;font-size:14px}
.famunit li{margin-bottom:3px}
.famunit .direct{color:#8C1F28;font-weight:600}
.bridge{background:#EFE3D0;color:#8a6a2f;font-size:13px;padding:6px 12px;border-radius:8px;text-align:center;margin:4px 0;font-style:italic}
.paths{max-width:660px;margin:24px auto 0}
.paths h2{font-family:'Cinzel',serif;font-size:18px;color:#8C1F28;border-bottom:2px solid #C9A24B;padding-bottom:6px;margin-bottom:10px}
.paths ol{margin-left:20px;font-size:15px}
.paths li{margin-bottom:8px}
.sources{max-width:660px;margin:26px auto 0;padding-top:14px;border-top:1px solid #B9A793;font-size:13px;color:#7A6E66}
.sources h4{font-family:'Cinzel',serif;color:#2A2220;margin-bottom:6px;font-size:13px;letter-spacing:1px}
.sources p{margin-bottom:5px}
.sources em{color:#8C1F28}
@media(max-width:520px){.gen{flex-direction:column;align-items:center}.gen.two .couple{flex:1 1 100%;width:100%}.converge::before{left:50%}.converge::after{display:none}.converge .horiz{left:50%;right:50%}}
"""

# ---- Direct line (hourglass) ----
tree_html = []
# Root
tree_html.append('<div class="tree">')
tree_html.append('<div class="branch-label"><span class="pill">⚑ Métis root</span></div>')
tree_html.append('<div class="gen"><div class="couple">' + couple_card("P001","P002") + '</div></div>')
tree_html.append('<div class="down">↓</div>')

# Branch A (left) + Branch B (right), side by side
tree_html.append('<div class="gen two">')
# Branch A
tree_html.append('<div class="couple">')
tree_html.append('<div class="branch-label a"><span class="pill">Spence line A</span></div>')
tree_html.append(couple_card("P007","P006"))
tree_html.append('<div class="down">↓</div>')
tree_html.append(person_card("P010", highlight=True))
tree_html.append('<div class="down">↓</div>')
tree_html.append('<div class="bridge">… bridge to Allan Setter (to pin)</div>')
tree_html.append('</div>')
# Branch B
tree_html.append('<div class="couple">')
tree_html.append('<div class="branch-label b"><span class="pill">Spence line B</span></div>')
tree_html.append(couple_card("P003","P029"))
tree_html.append('<div class="down">↓</div>')
tree_html.append(couple_card("P030","P033"))
tree_html.append('<div class="down">↓</div>')
tree_html.append(couple_card("P041","P038"))
tree_html.append('</div>')
tree_html.append('</div>')

# Convergence
tree_html.append('<div class="gen-title">The two Spence lines converge here</div>')
tree_html.append('<div class="converge"><div class="horiz"></div><div class="drop"></div></div>')
tree_html.append('<div class="gen"><div class="couple">' + couple_card("P043","P042", note="married 31 Mar 1909, Portage la Prairie") + '</div></div>')
tree_html.append('<div class="down">↓</div>')

# Spine down to Bayard
tree_html.append('<div class="gen"><div class="couple">' + couple_card("P044","P045") + '</div></div>')
tree_html.append('<div class="down">↓</div>')
tree_html.append('<div class="gen"><div class="couple">' + couple_card("P047","P046") + '</div></div>')
tree_html.append('<div class="down">↓</div>')
tree_html.append('<div class="gen"><div class="couple">' + couple_card("P048","P049") + '</div></div>')
tree_html.append('<div class="down">↓</div>')
tree_html.append('<div class="gen"><div class="couple">' + person_card("P050") + '</div></div>')
tree_html.append('</div>')

# ---- Full family units ----
fam = []
fam.append('<section class="fam"><h2>Full family (by generation)</h2>')
by_parent = {}
for u in UNIONS:
    s1, s2 = u["spouse1"], u["spouse2"]
    if s1 == s2:
        continue
    kids = u["children"]
    head = f"{PEOPLE[s1]['name']} <span style='color:#C9A24B'>⚭</span> {PEOPLE[s2]['name']}"
    items = "".join(f"<li{' class=direct' if k in ('P006','P010','P030','P038','P042','P043','P044','P046','P048','P050') else ''}>{pname(k)}"
                    f"{' <span style=color:#C9A24B>★</span>' if PEOPLE[k].get('you') else ''}</li>" for k in kids)
    if not items:
        items = '<li style="color:#B9A793">(no children recorded)</li>'
    fam.append(f'<div class="famunit"><div class="head">{head}</div><ul>{items}</ul></div>')
fam.append('</section>')

# ---- Paths to root ----
paths = "".join(f"<li>{p}</li>" for p in DATA["paths_to_root"])
paths_html = f'<div class="paths"><h2>Your two paths to the Métis root</h2><ol>{paths}</ol></div>'

# ---- Open items + sources ----
opens = "".join(f"<li>{o}</li>" for o in DATA["open_items"])
sources_html = f'''<div class="sources">
<h4>Sources & verification</h4>
<p><em>Red River Ancestry</em> (redriverancestry.ca): James Spence (1753), Andrew Setter (1777), George Setter (1815), James Spence (c1780), David Spence (1824).</p>
<p><em>Manitoba Vital Statistics Index:</em> Allan Setter ⚭ Ella Alberta Riggs (31 Mar 1909, reg 1909,001530); Doris Alberta Setter (b. 24 Dec 1912, reg 1912,004481).</p>
<p><em>Ancestry DNA tree</em> (family screenshots, Aug 2026) · family knowledge.</p>
<p>Hobbyist/family-tree data is flagged and should be verified against scrip, census, and parish records. Never fabricated; living people's details not published.</p>
<h4>Open items</h4><ul style="margin-left:18px;font-size:13px">{opens}</ul>
</div>'''

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{DATA['project']['title']}</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body>
<header><h1>{DATA['project']['title']}</h1><p class="sub">{DATA['project']['focus']}</p></header>
<div class="rule"></div>
<div class="legend">
  <span><span class="dot a"></span> Spence line A</span>
  <span><span class="dot b"></span> Spence line B</span>
  <span>★ = you &nbsp;·&nbsp; ◈ = notable</span>
</div>
{''.join(tree_html)}
{''.join(fam)}
{paths_html}
{sources_html}
</body></html>"""

out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(html)
print(f"Wrote {out} ({len(html)} bytes, {len(PEOPLE)} people, {len(UNIONS)} unions)")
