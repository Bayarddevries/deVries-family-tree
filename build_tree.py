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

# ---- Remove non-ancestral / duplicate-impact unions ----
# U03: George Setter (P010) + Isabella Kennedy (P018) — George remarried Jessie Ellen
# Campbell (P019) and the Mtis line descends through Jessie (Roderick, Alan, ...).
# Isabella's three children (P020/P021/P022) are non-ancestral collateral and are
# kept in PEOPLE (People tab / Stories) but not placed in the tree. Removing U03
# eliminates the duplicate George Setter node so the ancestral line is a single
# clean trunk. U22 (Sarah Fowler stay-behind) is not added to _extra_unions.
UNIONS = [u for u in UNIONS if u["id"] not in ("U03", "U22")]

# ---- Verified additions (kept here so data/family-tree.json stays untouched) ----
# James Morwick + Sarah Sabiston -> parents of Jane Morwick (corrects the 'Catherine Dungas' error)
# Jan Oltrop + Antje Von Lengen  -> parents of Geeske Oltrop (Ochre River MB, Dutch/German line)
# Sarah Fowler                   -> Isaac Batt's documented English wife (DCB); the Metis line descends from his Cree family
PEOPLE.setdefault("P92", {"id":"P92","name":"James Morwick","birth":"c1778","death":"1865","metis":False,"privacy":"deceased",
  "note":"Jane Morwick's father (c.1778-1865), Kirkwall, Orkney. Confirmed via Red River Ancestry + scrip records. Corrects the earlier 'Catherine Dungas' conflation."})
PEOPLE.setdefault("P93", {"id":"P93","name":"Sarah Sabiston","birth":"1800","death":"1872","metis":False,"privacy":"deceased",
  "note":"Jane Morwick's mother (1800-1872)."})
PEOPLE.setdefault("P94", {"id":"P94","name":"Jan 'John' Oltrop","birth":"1885","death":"1973","metis":False,"privacy":"deceased",
  "note":"Geeske Oltrop's father (1885-1973); Dutch/German line, Ochre River RM, MB."})
PEOPLE.setdefault("P95", {"id":"P95","name":"Antje Von Lengen","birth":"1885","death":"1961","metis":False,"privacy":"deceased",
  "note":"Geeske Oltrop's mother (1885-1961)."})
PEOPLE.setdefault("P96", {"id":"P96","name":"Sarah Fowler","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Isaac Batt's English wife (m. 1761, Stanstead Abbots, England), who stayed in England. The Metis line descends from Batt's Cree family, not her."})
_extra_unions = [
  {"id":"U20","spouse1":"P92","spouse2":"P93","children":["P029"]},
  {"id":"U21","spouse1":"P94","spouse2":"P95","children":["P068"]},
]
for _u in _extra_unions:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Round 2 additions (corroborated across 2+ free sources: FamilySearch, Find a Grave, cemetery register, redriverancestry) ----
# deVries: Leewe de Vries + Trienje Pommer -> parents of Gerhard De Vries (East Frisia, Germany)
# Hamilton: John James Hamilton + Jane Buchanan -> parents of Guy Wentworth Hamilton
# King:    Thomas Allan King + Catherine Ann Clark -> parents of Ethel Rose King
# Riggs:   Harmon Miles Riggs + Amelia Williams -> parents of Ernest Charles Riggs
PEOPLE.setdefault("P97", {"id":"P97","name":"Leewe de Vries","birth":"1862","death":"1926","metis":False,"privacy":"deceased",
  "note":"Gerhard de Vries's father (8 Dec 1862, Dyksterhusen, East Frisia, Germany; d. 4 May 1926, Germany). East Frisian, not Dutch proper."})
PEOPLE.setdefault("P98", {"id":"P98","name":"Trienje Pommer","birth":"1863","death":"1937","metis":False,"privacy":"deceased",
  "note":"Gerhard de Vries's mother (13 Sep 1863, Ditzumerhammrich; d. 17 May 1937, Ste. Rose du Lac, MB)."})
PEOPLE.setdefault("P99", {"id":"P99","name":"John James Hamilton","birth":"1856","death":"1913","metis":False,"privacy":"deceased",
  "note":"Guy Wentworth Hamilton's father (b. 1856, Mornington Twp, Ontario; d. 1913, Tisdale SK). Irish (Co. Mayo) settler line, not Scottish."})
PEOPLE.setdefault("P100", {"id":"P100","name":"Jane Buchanan","birth":"1859","death":"1931","metis":False,"privacy":"deceased",
  "note":"Guy Wentworth Hamilton's mother (1859-1931)."})
PEOPLE.setdefault("P101", {"id":"P101","name":"Thomas Allan King","birth":"1864","death":"1954","metis":False,"privacy":"deceased",
  "note":"Ethel Rose King's father (1864-1954); Ontario (SD&G) settler line."})
PEOPLE.setdefault("P102", {"id":"P102","name":"Catherine Ann Clark","birth":"1867","death":"1956","metis":False,"privacy":"deceased",
  "note":"Ethel Rose King's mother (1867-1956), m. Thomas Allan King 17 Mar 1884."})
PEOPLE.setdefault("P103", {"id":"P103","name":"Harmon Miles Riggs","birth":"1834","death":"1874","metis":False,"privacy":"deceased",
  "note":"Ernest Charles Riggs's father (1834-1874), m. Amelia Williams 11 Nov 1858, Jackson, WI; family migrated US -> Red River."})
PEOPLE.setdefault("P104", {"id":"P104","name":"Amelia Williams","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Ernest Charles Riggs's mother (Amelia Williams), m. Harmon Miles Riggs 1858."})
_extra_unions2 = [
  {"id":"U23","spouse1":"P97","spouse2":"P98","children":["P067"]},
  {"id":"U24","spouse1":"P99","spouse2":"P100","children":["P061"]},
  {"id":"U25","spouse1":"P101","spouse2":"P102","children":["P062"]},
  {"id":"U26","spouse1":"P103","spouse2":"P104","children":["P041"]},
]
for _u in _extra_unions2:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Round 3 additions: one generation deeper (corroborated via FamilySearch / redriverancestry / Find a Grave) ----
# Engbertus de Vries + Maria Meinders  -> parents of Leewe de Vries
# David J. Riggs Jr + Catherine Hendricks -> parents of Harmon Miles Riggs
# William King + Sarah Burke           -> parents of Thomas Allan King
PEOPLE.setdefault("P105", {"id":"P105","name":"Engbertus de Vries","birth":"1839","death":"","metis":False,"privacy":"deceased",
  "note":"Leewe de Vries's father (b. 1839, East Frisia, Germany)."})
PEOPLE.setdefault("P106", {"id":"P106","name":"Maria Geerds Meinders","birth":"1836","death":"1872","metis":False,"privacy":"deceased",
  "note":"Leewe de Vries's mother (1836-1872)."})
PEOPLE.setdefault("P107", {"id":"P107","name":"David J. Riggs Jr","birth":"1804","death":"1850","metis":False,"privacy":"deceased",
  "note":"Harmon Miles Riggs's father (1804-1850); b. Ontario, NY."})
PEOPLE.setdefault("P108", {"id":"P108","name":"Catherine M. Hendricks","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Harmon Miles Riggs's mother (Catherine M. Hendricks)."})
PEOPLE.setdefault("P109", {"id":"P109","name":"William King","birth":"1817","death":"1898","metis":False,"privacy":"deceased",
  "note":"Thomas Allan King's father (1817-1898); Ontario (SD&G) settler line."})
PEOPLE.setdefault("P110", {"id":"P110","name":"Sarah Burke","birth":"1829","death":"1909","metis":False,"privacy":"deceased",
  "note":"Thomas Allan King's mother (1829-1909)."})
_extra_unions3 = [
  {"id":"U27","spouse1":"P105","spouse2":"P106","children":["P97"]},
  {"id":"U28","spouse1":"P107","spouse2":"P108","children":["P103"]},
  {"id":"U29","spouse1":"P109","spouse2":"P110","children":["P101"]},
]
for _u in _extra_unions3:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Round 4 additions: Hamilton line deeper (VERIFIED: FamilySearch + 1871 census + 1848 Christian Guardian marriage notice + Find a Grave) ----
# Joseph Hamilton + Mary Busby      -> parents of John James Hamilton (P99)
# John Hamilton + Eleanor Preston   -> the Irish immigrant generation (Co. Mayo) -> Joseph Hamilton
# John Buchanan + Isabella Watson   -> parents of Jane Buchanan (P100)
PEOPLE.setdefault("P111", {"id":"P111","name":"Joseph Hamilton","birth":"1821","death":"1889","metis":False,"privacy":"deceased",
  "note":"John James Hamilton's father (1821-1889); married Mary Busby 24 Feb 1848, Mornington, Perth Co., Ontario."})
PEOPLE.setdefault("P112", {"id":"P112","name":"Mary Busby","birth":"1831","death":"1921","metis":False,"privacy":"deceased",
  "note":"John James Hamilton's mother (1831-1921)."})
PEOPLE.setdefault("P113", {"id":"P113","name":"John Hamilton","birth":"1791","death":"1857","metis":False,"privacy":"deceased",
  "note":"Joseph Hamilton's father; the Irish immigrant generation from Glenedagh, Co. Mayo, Ireland (1791-1857)."})
PEOPLE.setdefault("P114", {"id":"P114","name":"Eleanor Jane Preston","birth":"1798","death":"1884","metis":False,"privacy":"deceased",
  "note":"Joseph Hamilton's mother (1798-1884)."})
PEOPLE.setdefault("P115", {"id":"P115","name":"John Buchanan","birth":"1829","death":"1909","metis":False,"privacy":"deceased",
  "note":"Jane Buchanan's father (1829/1831-1909), b. Omagh, Co. Tyrone, Ireland; d. Langford/Neepawa, MB."})
PEOPLE.setdefault("P116", {"id":"P116","name":"Isabella Watson","birth":"1837","death":"1917","metis":False,"privacy":"deceased",
  "note":"Jane Buchanan's mother (1837-1917); Scottish parents (James Watson Sr & Elizabeth Linnen)."})
_extra_unions4 = [
  {"id":"U30","spouse1":"P113","spouse2":"P114","children":["P111"]},
  {"id":"U31","spouse1":"P111","spouse2":"P112","children":["P99"]},
  {"id":"U32","spouse1":"P115","spouse2":"P116","children":["P100"]},
]
for _u in _extra_unions4:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# Paula Fleury (maiden name; user correction 2026-08-13) - she is NOT a deVries by birth.
# NOTE: P088 is Paula (Bayard's wife). P050 is Bayard himself - do NOT rename P050.
PEOPLE["P088"]["name"] = "Paula Fleury"

# in-law spouses = people who married INTO the tree (a spouse in a union, but not born into the
# line - i.e. their own parents are not in the tree). These are rendered with a dashed box so a
# married-in spouse like Robert Lau isn't mistaken for a blood Hamilton/Setter/etc.
_born=set(); _ch=True
while _ch:
    _ch=False
    for _u in UNIONS:
        for _c in _u["children"]:
            if _c not in _born: _born.add(_c); _ch=True
INLAW={_s for _u in UNIONS for _s in (_u["spouse1"],_u["spouse2"]) if _s not in _born}

# ---- Hourie line expansion (VERIFIED 2026-08-13: FamilySearch M81J-6D8 + Find a Grave + 1870 Red River census + Red River Ancestry) ----
# Correct Sarah Ann Howrie's dates/spelling; add parents + the Orkney patriarch.
_h=PEOPLE["P060"]; _h["name"]="Sarah Ann Hourie"; _h["birth"]="1860"; _h["death"]="1944"
_h["note"]="also 'Howrie' · wife of Roderick McKenzie Setter (m. 3 Jan 1879, High Bluff) · b. 8 Dec 1860, d. 19 May 1944 · dau. of Philip Hourie + Euphemia Cook Halcro"
PEOPLE.setdefault("P117", {"id":"P117","name":"Philip Hourie","birth":"1833","death":"1914","metis":False,"privacy":"deceased",
  "note":"Sarah Ann Hourie's father (1833-1914)."})
PEOPLE.setdefault("P118", {"id":"P118","name":"Euphemia Cook Halcro","birth":"1839","death":"1917","metis":False,"privacy":"deceased",
  "note":"Sarah Ann Hourie's mother (1839-1917)."})
PEOPLE.setdefault("P119", {"id":"P119","name":"John Hourie","birth":"1779","death":"1857","metis":False,"privacy":"deceased",
  "note":"Philip Hourie's father; the Orkney patriarch from South Ronaldsay (1779-1857), an HBC man. Same Orkney x Indigenous ethnogenesis as the Spence/Setter lines."})
PEOPLE.setdefault("P120", {"id":"P120","name":"Margaret Bird","birth":"1787","death":"1847","metis":False,"privacy":"deceased",
  "note":"Philip Hourie's mother (1787-1847); a Shoshoni / 'Snake' woman adopted by Chief Factor James Curtis Bird. Needs primary confirmation."})
_extra_unions5 = [
  {"id":"U33","spouse1":"P117","spouse2":"P118","children":["P060"]},
  {"id":"U34","spouse1":"P119","spouse2":"P120","children":["P117"]},
]
for _u in _extra_unions5:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Catherine Parenteau + Henry Hallett Jr as nodes (so she is findable in the tree) ----
# Catherine Parenteau was previously only mentioned in Catherine Hallett's (P033) note.
PEOPLE.setdefault("P121", {"id":"P121","name":"Henry Hallett Jr","birth":"1799","death":"1871","metis":False,"privacy":"deceased",
  "note":"Catherine Hallett's father (c.1799-1871); married Catherine Parenteau 18 Oct 1824, St. John's."})
PEOPLE.setdefault("P122", {"id":"P122","name":"Catherine Parenteau","birth":"c1799","death":"1857","metis":True,"privacy":"deceased",
  "note":"Catherine Hallett's mother (c.1799-1857, Metis). Her OWN parents are the tree's #1 open gap - lead: Joseph V. Parenteau + Suzanne Cree (unverified)."})
_extra_unions6 = [
  {"id":"U35","spouse1":"P121","spouse2":"P122","children":["P033"]},
]
for _u in _extra_unions6:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Parenteau parentage corrected (VERIFIED 2026-08-13: Barkwell 'Metis Dictionary of Biography' + Red River Ancestry) ----
# Catherine Parenteau's father was Jean Baptiste Parenteau (from Quebec), NOT Joseph V. Parenteau.
# (Joseph V. Parenteau + Suzanne 'Cree' Richard are a DIFFERENT family - parents of Metis leader Pierre Parenteau.)
_p=PEOPLE["P122"]; _p["note"]="Catherine Hallett's mother (c.1799-1857, Metis). Father = Jean Baptiste Parenteau (from Quebec), confirmed by Barkwell + Red River Ancestry - this corrects the earlier 'Joseph V. Parenteau + Suzanne Cree' lead, which belongs to a different Parenteau family. Mother still unknown."
PEOPLE.setdefault("P123", {"id":"P123","name":"Jean Baptiste Parenteau","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Catherine Parenteau's father, from Quebec. Confirmed by Barkwell's Metis Dictionary of Biography + Red River Ancestry. The earlier 'Joseph V. Parenteau + Suzanne Cree' lead belongs to a different family (parents of Metis leader Pierre Parenteau)."})
PEOPLE.setdefault("P124", {"id":"P124","name":"Unknown (Parenteau)","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Catherine Parenteau's mother - not yet identified."})
_extra_unions7 = [{"id":"U36","spouse1":"P123","spouse2":"P124","children":["P122"]}]
for _u in _extra_unions7:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Hallett collateral: the patriarch + the notable William Peter (VERIFIED 2026-08-13: Barkwell + WikiTree + Red River Ancestry) ----
# William Peter Hallett is Catherine Hallett's UNCLE (younger brother of her father Henry Jr).
# Adding Henry Sr + Catherine Crise as parents of BOTH Henry Jr (P121) and William Peter places him properly.
PEOPLE.setdefault("P125", {"id":"P125","name":"Henry Hallett Sr","birth":"1773","death":"1844","metis":False,"privacy":"deceased",
  "note":"Hallett patriarch (bapt. 15 Apr 1773, Battersea; d. 9 Mar 1844, St John's). Father of Henry Hallett Jr and William Peter Hallett."})
PEOPLE.setdefault("P126", {"id":"P126","name":"Catherine Crise (Cree)","birth":"","death":"","metis":True,"privacy":"deceased",
  "note":"Henry Hallett Sr's wife, mother of Henry Jr. Spelling varies (Crise / Cree / Tenanse) - needs primary confirmation."})
PEOPLE.setdefault("P127", {"id":"P127","name":"William Peter Hallett","birth":"c1811","death":"1873","metis":True,"privacy":"deceased",
  "note":"Catherine Hallett's uncle (Henry Jr's younger brother). Buffalo-hunt captain, leader / Chief Scout of the 49th Rangers (Int'l Boundary Commission 1872-73), opponent of Riel in 1869-70. m. Maria Pruden 6 Sep 1841."})
PEOPLE.setdefault("P128", {"id":"P128","name":"Maria Pruden","birth":"1813","death":"1883","metis":True,"privacy":"deceased",
  "note":"Wife of William Peter Hallett (m. 6 Sep 1841, Grand Rapids / St Andrews)."})
_extra_unions8 = [
  {"id":"U37","spouse1":"P125","spouse2":"P126","children":["P121","P127"]},
  {"id":"U38","spouse1":"P127","spouse2":"P128","children":[]},
]
for _u in _extra_unions8:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Collateral: David Spence's children's spouses + Jemima Hourie (VERIFIED 2026-08-13) ----
# Ellen (P035) m. George Brown; Jane (P037) m. William Folster; Harriet (P039) m. Peter Henry Wishart.
# Colin Campbell Setter (P024) m. Jemima Hourie (Sarah Ann's sister).
PEOPLE.setdefault("P129", {"id":"P129","name":"George Brown","birth":"1853","death":"1936","metis":False,"privacy":"deceased",
  "note":"Ellen Anderson Spence's husband (m. 1873). Son of Henry Brown & Isabella Slater."})
PEOPLE.setdefault("P130", {"id":"P130","name":"Peter Henry Wishart","birth":"1862","death":"1936","metis":False,"privacy":"deceased",
  "note":"Harriet Spence's husband (m. 1887)."})
PEOPLE.setdefault("P131", {"id":"P131","name":"William Folster","birth":"","death":"","metis":False,"privacy":"deceased",
  "note":"Jane Spence's husband (m. 1879). Children not yet confirmed (possible conflation with a St Clements Folster family)."})
PEOPLE.setdefault("P132", {"id":"P132","name":"Jemima Hourie","birth":"","death":"","metis":True,"privacy":"deceased",
  "note":"Wife of Colin Campbell Setter (P024). Sarah Ann Hourie's sister - two Hourie sisters married two Setter brothers."})
_extra_unions9 = [
  {"id":"U43","spouse1":"P035","spouse2":"P129","children":[]},
  {"id":"U45","spouse1":"P037","spouse2":"P131","children":[]},
  {"id":"U44","spouse1":"P039","spouse2":"P130","children":[]},
  {"id":"U42","spouse1":"P024","spouse2":"P132","children":[]},
]
for _u in _extra_unions9:
    if not any(u["id"]==_u["id"] for u in UNIONS): UNIONS.append(_u)

# ---- Collateral children + Hallett siblings (VERIFIED 2026-08-13) ----
# BROWN children (Ellen Anderson Spence + George Brown, U43) - 12, FamilySearch VERIFIED
_brown_kids = [
  ("P133","Archibald George Brown","1877","1937"),("P134","Alexander Brown","1878","1923"),
  ("P135","Daniel David Brown","1880","1956"),("P136","Jane Brown","1882",""),
  ("P137","Richard A. Brown","1884",""),("P138","Ida Brown","1886",""),
  ("P139","Clara M. E. Brown","1889",""),("P140","Margaret Brown","1891",""),
  ("P141","Flora C. Brown","1893","1899"),("P142","Mariam Brown","1895",""),
  ("P143","Lawrence Brown","1898",""),("P144","William Archibald Brown","1899",""),
]
for _pid,_n,_b,_d in _brown_kids:
  PEOPLE.setdefault(_pid, {"id":_pid,"name":_n,"birth":_b,"death":_d,"metis":False,"privacy":"deceased",
    "note":"Child of Ellen Anderson Spence + George Brown."})
for _u in UNIONS:
  if _u["id"]=="U43": _u["children"]=["P133","P134","P135","P136","P137","P138","P139","P140","P141","P142","P143","P144"]

# WISHART children (Harriet Spence + Peter Henry Wishart, U44) - 7, redriverancestry VERIFIED
_wishart_kids = [
  ("P145","Florence Mildred Wishart","1887","","m. George Augustus Langford 1913"),
  ("P146","Henry Allen Wishart","1889","","'Harry' · m. Kathleen Maggie Payne 1920 · WWI 1918"),
  ("P147","Edgar Wolseley Franklin Wishart","1891","","'Ted' · m. Mary Ethel Neilson 1925 · WWI 1918"),
  ("P148","Edna Wishart","1896","","m. Harold 'Bertie' Cleave 1926"),
  ("P149","Ruby Emma Elizabeth Wishart","1897","",""),
  ("P150","Edith Jane Wishart","1900","","m. Thomas Hoy"),
  ("P151","Herbert Charles Wishart","1901","","farmer, Makinak"),
]
for _pid,_n,_b,_d,_nt in _wishart_kids:
  PEOPLE.setdefault(_pid, {"id":_pid,"name":_n,"birth":_b,"death":_d,"metis":False,"privacy":"deceased","note":_nt})
for _u in UNIONS:
  if _u["id"]=="U44": _u["children"]=["P145","P146","P147","P148","P149","P150","P151"]

# Collateral children (12 Brown, 7 Wishart) are KEPT in PEOPLE (People tab / Stories / search)
# but rendered in the TREE as one compact summary node per family. Laying out 12+7 individual
# boxes put them on the same rows as the central trunk (Bayard's parents / Bayard himself),
# where the overlap-resolver crammed them into the trunk's free space and made the tree ugly.
PEOPLE.setdefault("P900", {"id":"P900","name":"George & Ellen Brown","birth":"","death":"","metis":False,"privacy":"deceased","group":True,"kids":12,
  "note":"12 children (each has a full profile in the People tab): Archibald George (1877-1937), Alexander (1878-1923), Daniel David (1880-1956), Jane (1882-), Richard A. (1884-), Ida (1886-), Clara M.E. (1889-), Margaret (1891-), Flora C. (1893-1899), Mariam (1895-), Lawrence (1898-), William Archibald (1899-)."})
PEOPLE.setdefault("P901", {"id":"P901","name":"Peter & Harriet Wishart","birth":"","death":"","metis":False,"privacy":"deceased","group":True,"kids":7,
  "note":"7 children (each has a full profile in the People tab): Florence Mildred (1887-, m. George Augustus Langford 1913), Henry Allen 'Harry' (1889-, m. Kathleen Payne 1920), Edgar Wolseley 'Ted' (1891-, m. Mary Ethel Neilson 1925), Edna (1896-, m. Bertie Cleave 1926), Ruby Emma Elizabeth (1897-), Edith Jane (1900-, m. Thomas Hoy), Herbert Charles (1901-, farmer Makinak)."})
# Collateral children of George Setter + Jessie Ellen Campbell (U19): 5 siblings
# (Duncan, Colin, Alexander, George W, Ellen) that are NOT ancestors of Bayard.
# Collapsed into one summary box so they don't spread the row wide and pull George
# away from his descendant Roderick. All 5 stay in PEOPLE for the People tab.
PEOPLE.setdefault("P902", {"id":"P902","name":"George & Jessie's other children","birth":"","death":"","metis":False,"privacy":"deceased","group":True,"kids":5,
  "note":"5 children of George Setter + Jessie Ellen Campbell (not in Bayard's direct line): Duncan Richard (1848-1930), Colin Campbell (m. Jemima Hourie), Alexander Hunter Murray (1852-), George William (1854-), Ellen Madeleine 'Nellie' (1858-). Each has a full profile in the People tab."})

# HALLETT siblings (children of Henry Hallett Jr + Catherine Parenteau, U35) - corroborated set.
# RECONCILED the two 'Jane' entries (Jane Spence 1839 + Jane Baubee 1841) as one Jane with a note
# (possible source duplicate); held Alfred/John/Cornelius as less-documented (not added as facts).
_hallett_sibs = [
  ("P152","Antoine (Edwin) Hallett","1823","1853",""),("P153","Esther Justine Hallett","1824","1869","m. Klyne"),
  ("P154","Henry Hallett III","1827","1869","'Andrew'"),("P155","Charlotte Hallett","1834","","m. McNabb"),
  ("P156","Jane Hallett","1839","1874","also recorded as 'Jane Baubee' (1841-79) - possible source duplicate"),
  ("P157","Anne Hallett","1846","","m. Bird"),
]
for _pid,_n,_b,_d,_nt in _hallett_sibs:
  PEOPLE.setdefault(_pid, {"id":_pid,"name":_n,"birth":_b,"death":_d,"metis":True,"privacy":"deceased","note":_nt})
for _u in UNIONS:
  if _u["id"]=="U35": _u["children"]=["P033","P152","P153","P154","P155","P156","P157"]

STORIES = DATA.get("stories", {})
# Expanded stories (kept here so data/family-tree.json stays untouched).
STORIES.update({
 "P042": {"title": "Ella Alberta Riggs \u2014 where the two lines meet",
   "text": "Ella (b. c1880s) was the daughter of Ernest C. Riggs and Mary Ann Spence. Through her mother she carries Spence line B: Mary Ann was the daughter of David Spence (M\u00e9tis MLA and Convention of Forty delegate) and Catherine Hallett. Ella married Alan Setter on 31 Mar 1909 at Portage la Prairie (reg. 1909,001530). Because Alan descends from line A (Peggy Spence), Ella is the point where Bayard's two Spence lines converge. Their daughter Doris inherited her mother's middle name, 'Alberta'. [Verify Ella's exact birth year vs vital records.]",
   "source": "vital stats reg. 1909,001530"},
 "P044": {"title": "Doris Alberta Setter \u2014 the bridge to the Hamiltons",
   "text": "Doris (b. 24 Dec 1912, Portage la Prairie; reg. 1912,004481; d. 23 Apr 2006) was the daughter of Alan Setter and Ella Alberta Riggs. On 29 Dec 1932 she married Lawrence Donald Hamilton at Tisdale, Saskatchewan. Their only daughter, Mavis Irene, was born 1 Sep 1933 in Tisdale and became the mother of Bayard's mother, Tracy. Doris is the hinge joining the Setter/Spence family to the Hamilton line.",
   "source": "vital stats regs 1912,004481; SK marriage record 1932"},
 "P045": {"title": "Lawrence Donald Hamilton \u2014 the Flin Flon connection",
   "text": "Lawrence (b. 15 Jun 1912, Tisdale SK; d. 5 Feb 1984, Flin Flon MB) was the son of Guy Wentworth Hamilton and Ethel Rose King. He married Doris Setter in 1932. The family moved to Flin Flon, Manitoba, in 1939 (when Mavis was six), which is how Bayard's maternal line came to Flin Flon. Also recorded as 'Laurence'.",
   "source": "family research; Flin Flon move c.1939"},
 "P043": {"title": "Alan Setter \u2014 Spence line A",
   "text": "Alan (b. 22 Oct 1884, R.M. Portage la Prairie; reg. 1884,005103; d. 1964; also spelled 'Sutter') was the son of Roderick McKenzie Setter and Sarah Ann Howrie. Roderick was the son of George Setter and Jessie Ellen Campbell. Alan's marriage to Ella Alberta Riggs in 1909 is the meeting point of the two Spence lines. He was Bayard's great-grandfather.",
   "source": "vital stats reg. 1884,005103"},
 "P033": {"title": "Catherine Hallett \u2014 wife of the MLA",
   "text": "Catherine Hallett (1824\u20131880) was the daughter of Henry Hallett and Catherine Parenteau. She married David Spence on 15 Feb 1844 at St. John's parish, Red River. In 1876, as a M\u00e9tis family, she and David received M\u00e9tis scrip. Their daughter Mary Ann Spence became the grandmother of Ella Riggs. [Verify the Catherine Hallett death date: 1880 vs 1887.]",
   "source": "parish record 1844; scrip 1876"},
 "P029": {"title": "Jane Morwick \u2014 grandmother of a Premier",
   "text": "Jane Morwick (1794\u20131874) was a widow (n\u00e9e Morwick, previously married into the Norquay family) when she married James Spence Jr. She is the grandmother of Premier John Norquay, Manitoba's first M\u00e9tis Premier, who was raised in the Spence household. Through Jane and James Jr, their son David Spence continued the family's public life in Red River.",
   "source": "family research; Norquay genealogy"},
 "P010": {"title": "George Setter \u2014 the middle bridge",
   "text": "George Setter (1815\u20131899) was the son of Andrew Setter (an Orkney HBC voyageur) and Peggy Spence (a daughter of James Spence Sr and Margaret 'Nestichio' Batt). He married Isabella Kennedy (d. 1846), then Jessie Ellen Campbell. His son Roderick McKenzie Setter (by Jessie) carried line A down to Alan Setter.",
   "source": "redriverancestry.ca; family research"},
 "P007": {"title": "Andrew Setter \u2014 the Orkney voyageur",
   "text": "Andrew Setter (1777\u20131870) was born in Westray, Orkney and joined the Hudson's Bay Company at York Factory in 1800. On 28 Jan 1821 he married Peggy Spence at Beaver Creek, baptised by Rev. John West. Their son George carried the family's M\u00e9tis lineage forward. Andrew's line is the paternal thread that joined the Spence family.",
   "source": "HBC records; Rev. John West baptism 1821"},
 "P019": {"title": "Jessie Ellen Campbell \u2014 second wife, and a key correction",
   "text": "Jessie Ellen Campbell (1824\u20131912) married George Setter after Isabella Kennedy's death in 1846, and was the mother of Roderick McKenzie Setter. The research corrects an earlier assumption: Roderick was Jessie's son, NOT Isabella's. This matters because it pins line A's descent through Jessie. [Line A ancestress = Jessie Ellen Campbell.]",
   "source": "family research; corrected lineage"},
 "P025": {"title": "Roderick McKenzie Setter \u2014 completing line A",
   "text": "Roderick McKenzie Setter (b. 1856) was the son of George Setter and Jessie Ellen Campbell. He married Sarah Ann Howrie, and their son Alan Setter (b. 1884) closed line A end-to-end. Primary records (vital stats reg. 1884,005103) confirm Alan as Roderick and Sarah's son, completing the Spence-to-Setter descent to Bayard.",
   "source": "vital stats reg. 1884,005103"},
})
PROJ = DATA["project"]
PROJ["title"] = "deVries Lau Family Tree"   # user rename (2026-08-13); data/family-tree.json left untouched

# ---- Al Hamilton NHL story (user-confirmed 2026-08-13) ----
STORIES.update({
 "P055": {"title": "Al Hamilton — NHL star from Flin Flon",
   "text": "Alan Guy 'Al' Hamilton (b. 20 Aug 1946, Flin Flon, MB) was a professional hockey player. He played in the NHL for the New York Rangers and Buffalo Sabres, then became captain of the Edmonton Oilers in the WHA. He played for Team Canada in the 1974 Summit Series against the USSR and still holds the Oilers' WHA records for games (455) and points (311). He came from the great Flin Flon hockey generation (alongside Bobby Clarke). Confirmed as Bayard's maternal great-uncle.",
   "source": "hockeydb / Wikipedia / Edmonton Oilers records"},
})

# ---- Hourie line stories (2026-08-13) ----
STORIES.update({
 "P060": {"title": "Two Hourie sisters, two Setter brothers",
   "text": "Sarah Ann Hourie (b. 8 Dec 1860, High Bluff; d. 19 May 1944) married Roderick McKenzie Setter on 3 Jan 1879. Her sister Jemima Hourie had married Roderick's brother Colin Setter a few years earlier (1875), so two Hourie sisters married two Setter brothers and knit the two Red River Metis families together.",
   "source": "Red River Ancestry · FamilySearch M81J-6D8 · Find a Grave #154376026"},
 "P119": {"title": "From Orkney and the Shoshoni to Red River",
   "text": "The Hourie line begins with John Hourie (1779-1857), an HBC man from South Ronaldsay in Orkney, Scotland, and Margaret Bird (1787-1847), a Shoshoni 'Snake' woman adopted by Chief Factor James Curtis Bird. Their union is the same Orkney-and-Indigenous meeting that shaped the Spence and Setter lines, the root of the family's Metis heritage.",
   "source": "Red River Ancestry · FamilySearch (Margaret Bird needs primary confirmation)"},
 "P127": {"title": "Buffalo-hunt captain and the 49th Rangers",
   "text": "William Peter Hallett (c.1811-1873) was a Metis buffalo-hunt captain and the leader / Chief Scout of the 49th Rangers, the scout corps that guided the International Boundary Commission of 1872-73. A prominent figure in Red River, he was an opponent of Riel during the 1869-70 Resistance. He was the younger brother of Henry Hallett Jr, making him Catherine (Hallett) Spence's uncle.",
   "source": "Metis Museum / Barkwell bio · WikiTree · Red River Ancestry"},
})

# ---- Feature 4: new research-backed stories + enhancements (2026-08-12) ----
STORIES.update({
 "P030": {"title": "David Spence — the farmer who helped found Manitoba",
   "text": "David Spence (b. 5 Sep 1824, St. John's parish, Red River; d. 16 Sep 1885) was a Scottish Half-Breed, son of James Spence and Jane Morwick (both Métis; his mother was grandmother of Premier John Norquay). He married Catherine Hallett in 1844. In 1870 he sat in the Convention of Forty as delegate for St. Anne's (Poplar Point), and was elected the first MLA for Poplar Point, serving 1870-74, also as justice of the peace. He farmed on River Lot 62 at Poplar Point. His 1875 half-breed scrip affidavit (LAC RG15 v.1324, claim 2764) records his occupation as 'Farmer' and his claim for 160 acres/$160; scrip was issued to him and Catherine on 2 Oct 1876. He died in 1885 after being accidentally shot by a neighbour. Seven children, including Mary Ann, who married Ernest Riggs.",
   "source": "vital stats + LAC scrip affidavit 2764 (read from scan); Barkwell bio, Metis Museum"},
 "P033": {"title": "Catherine Hallett — wife of the MLA, and her buffalo-hunt kin",
   "text": "Catherine Hallett (1824-1880) was the daughter of Henry Hallett and Catherine Parenteau. She married David Spence in 1844 and was a 'half-breed head of a family' on her 1875 scrip affidavit. Her paternal half-uncle, William Peter Hallett (1811-1873), was a documented buffalo-hunt captain: one of the ten elected 'Captains of the Hunt,' leader of the English-speaking Half-Breed buffalo hunt in the 1860s, and Chief Scout of the '49th Rangers' (1872-73). So the family's documented buffalo-hunt connection runs through Catherine's Hallett kin.",
   "source": "scrip affidavit 2763; Barkwell (Louis Riel Institute) bio of William Peter Hallett"},
 "P038": {"title": "Mary Ann Spence — the hinge to the Riggs line",
   "text": "Mary Ann Spence (b. 8 Aug 1861) was the fifth of David Spence and Catherine Hallett's seven children, recorded in the 1870 census at Poplar Point with her family. She married Ernest Charles Riggs at Portage la Prairie (28 Aug 1887, reg 1887,001844). Their daughter Ella Alberta Riggs (b. 14 Sep 1888) married Allan Setter, converging the two Spence lines and passing the Métis heritage down to Bayard.",
   "source": "1870 census; vital stats reg 1887,001844 & 1888,001992"},
 "P041": {"title": "Ernest Charles Riggs — the American-born farmer of Portage",
   "text": "Ernest Charles Riggs (b. 1860, United States) married Mary Ann Spence at Portage la Prairie in 1887. The 1901 census (Portage la Prairie, District Macdonald, LAC RG31 v.1250-1251) shows the household: Ernest, wife Mary A, and children Ernest E, Ella B (your great-grandmother), Roy O, Eva M, Ray H, Elsa G and Stanley D. He was the son of Harmon M. Riggs and Amelia Williams.",
   "source": "1901 census; vital stats reg 1887,001844"},
})


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

def leaf_grid(u, row, cx, per=6):
    """leaf children of union u wrapped into compact rows of `per`, starting at `row`.
    Keeps wide families narrow so their connector rails don't overlap neighbouring families."""
    leaves = [c for c in u["children"]
              if not any(c in (fu["spouse1"], fu["spouse2"]) for fu in UNIONS if fu["id"] != u["id"])]
    if not leaves: return []
    out = []
    for r_i in range(0, len(leaves), per):
        band = leaves[r_i:r_i+per]
        y = (row + r_i//per)*ROW_H
        total = len(band)*(P_W + LEAF_GAP) - LEAF_GAP
        x0 = cx - total/2
        for i, pid in enumerate(band):
            bx = x0 + i*(P_W + LEAF_GAP)
            out.append((add_person(pid, bx, y), bx + P_W/2))
    return out

def summary_box(pid, row, cx, w=210):
    """one wide leaf box for a collapsed collateral family (children listed in its popup)."""
    nid = add_person(pid, cx - w/2, row*ROW_H)
    PERS[-1]["w"] = w
    return nid, cx

# ---- AUTO-LAYOUT (generation-layered; derives every position + connector from the graph) ----
from layout_auto import auto_layout
# Collateral families with many children render as ONE summary box (P900/P901 group nodes)
# so their child-rails stay short and never merge with neighbouring families' rails.
COLLAPSE = {"U43": "P900", "U44": "P901"}   # union -> summary person (defined above as group)
# U19 (George + Jessie) has Roderick (ancestral) + 5 collateral children.
# Collapse only the non-ancestral children into P902 so George's bar converges
# toward Roderick's position instead of being pulled wide by 5 spread-out siblings.
COLLAPSE_CHILDREN = {
    "U19": (["P023", "P024", "P026", "P027", "P028"], "P902"),
}
PERS, FAMS, TEDGES = auto_layout(UNIONS, PEOPLE, collapse=COLLAPSE,
                                collapse_children=COLLAPSE_CHILDREN)
# (overlap resolver, generation lanes, canvas bounds, and family-geometry recompute follow below)
# ------------------------------------------------------------------------------------------------

# NOTE: overlap resolution is handled inside layout_auto.py.
# for n in PERS:
#     rows.setdefault(n["y"], []).append(n)
# byid_p = {n["id"]: n for n in PERS}
# for y, ns in rows.items():
#     units, used = [], set()
#     for f in FAMS:
#         n1, n2 = byid_p[f["s1"]], byid_p[f["s2"]]
#         if n1["y"] == y:
#             units.append([n1, n2]); used.add(n1["id"]); used.add(n2["id"])
#     for n in ns:
#         if n["id"] not in used:
#             units.append([n])
#     units.sort(key=lambda u: min(b["x"] for b in u))
#     for i in range(1, len(units)):
#         prev_max = max(b["x"] + b["w"] for b in units[i-1])
#         cur_min = min(b["x"] for b in units[i])
#         if cur_min < prev_max + 10:
#             shift = prev_max + 10 - cur_min
#             for b in units[i]:
#                 b["x"] = round(b["x"] + shift, 1)

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

# canvas bounds (no label gutter; the generation sidebar was removed - labels no longer made sense
# once the tree grew to include in-law and converging branches at mixed depths)
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

# ================= VALIDATION (auto-layout integrity) =================
# Fails the build if a person is disconnected or a connector misses its target.
import sys as _sys
def _validate_layout():
    errs, warns = [], []
    spouse_nids = {f["s1"] for f in FAMS} | {f["s2"] for f in FAMS}
    child_nids = {cid for f in FAMS for cid, _ in f["children"]}
    # 1. every union that HAS children in the data must have a populated children rail
    for u in UNIONS:
        if by_union[u["id"]].get("children") and \
           not any(f["u"] == u["id"] and f["children"] for f in FAMS):
            errs.append(f"union {u['id']} has children but no connected rail")
    # 2. no node is orphaned (neither a spouse nor a connected child)
    for n in PERS:
        if n["id"] not in spouse_nids and n["id"] not in child_nids:
            errs.append(f"person {n['pid']} ({n['id']}) is disconnected (neither spouse nor child rail)")
    # 3. connector spans: a child box should sit one generation below its parent family
    byf = {f["u"]: f for f in FAMS}
    for f in FAMS:
        for cid, _ in f["children"]:
            k = bybox[cid]; gap = (k["y"] - f["y"]) / ROW_H
            if gap < 0.5:
                warns.append(f"connector {f['u']}->{k['pid']} spans {gap:.1f} rows (child at/above parent)")
    # 4. no overlapping boxes
    boxes = sorted(PERS, key=lambda n: n["x"])
    for i in range(len(boxes)):
        a = boxes[i]
        for b in boxes[i+1:]:
            if b["x"] >= a["x"] + a["w"] + 1:
                break
            if a["y"] == b["y"] and not (b["x"] >= a["x"] + a["w"] or a["x"] >= b["x"] + b["w"]):
                warns.append(f"overlap {a['pid']} & {b['pid']} at row {a['y']}")
    return errs, warns
ERR, WARN = _validate_layout()
for _w in WARN: print("  WARN:", _w)
if ERR:
    for _e in ERR: print("  ERROR:", _e)
    print(f"  [{len(ERR)} layout ERRORS - see above; aborting write]")
    _sys.exit(1)
print(f"  [layout-ok: {len(PERS)} nodes, {len(FAMS)} unions, {len(WARN)} warnings]")
# ======================================================================

# ---- Family-line classification (for organic colour coding) ----
# Trace from Bayard (P050) upward through two ancestral trunks:
#   Line A (setter):    Andrew+Spence -> George -> Roderick -> Alan
#   Line B (riggs/spence): David Spence -> Mary Ann -> Ernest Riggs -> Ella
#   Hamilton:           Joseph -> John James -> Guy -> Lawrence
#   deVries:            Gerhard -> Leewe
#   Hallett:            Henry Sr -> Henry Jr -> Catherine -> David Spence
#   Hourie:             John Hourie -> Philip -> Sarah Ann
#   King:               William King -> Thomas Allan -> Ethel
# Each person is assigned a CSS class used for the box border accent + a
# soft background tint. Spouses married into a line get the same class as
# their partner. Collateral/unassigned default to 'earth-stone'.
def _build_family_lines():
    """Map each pid to a family-line label by tracing unions from root up."""
    # Define the trunk person for each line (the person where the line enters)
    # Lines traced from Bayard upward; each person inherits the line of the
    # child through whom they enter.
    lines = {}  # pid -> line name
    # Start from Bayard, trace upward through unions
    # Bayard's parents: Lawrence Hamilton (P045) + Doris Setter (P044)
    lines["P050"] = "bayard"   # center / convergence point
    # Trace up through known trunk people
    trunk = {
        "P050": "bayard",   # center / convergence point
        # Line A: Setter line through Peggy Spence -> Andrew -> George -> Roderick -> Alan
        "P006": "setter",     # Peggy Spence (Spence line A matriarch)
        "P007": "setter",     # Andrew Setter (Orkney voyageur)
        "P010": "setter",     # George Setter (middle bridge)
        "P019": "setter",     # Jessie Ellen Campbell (George's 2nd wife)
        "P025": "setter",     # Roderick McKenzie Setter
        "P043": "setter",     # Alan Setter (where the two lines meet)
        # Line A root: James Spence Sr + Margaret Batt
        "P001": "setter",     # James Spence Jr (Peggy's father)
        "P002": "setter",     # Margaret Nestichio Batt (James's partner)
        # Line B: Spence/Riggs line through David Spence -> Mary Ann -> Ernest -> Ella
        "P042": "riggs",      # Ella Alberta Riggs (convergence: meets setter line at Alan)
        "P030": "spence",     # David Spence (MLA)
        "P033": "spence",     # Catherine Hallett (David's wife)
        "P038": "riggs",      # Mary Ann Spence (David's daughter)
        "P041": "riggs",      # Ernest Charles Riggs (Mary Ann's husband)
        # Spence line B root: James Spence Sr + Margaret Batt (U01)
        # (P001 and P002 above already tagged setter - they're the SHARED root of both lines)
        # Hamilton line
        "P045": "hamilton",   # Lawrence Donald Hamilton
        "P044": "hamilton",   # Doris Alberta Setter (married into Hamilton line)
        "P061": "hamilton",   # Guy Wentworth Hamilton
        "P062": "king",       # Ethel Rose King (married into Hamilton)
        "P099": "hamilton",   # John James Hamilton
        "P100": "hamilton",   # Jane Buchanan
        "P111": "hamilton",   # Joseph Hamilton
        "P112": "hamilton",   # Mary Busby
        "P113": "hamilton",   # John Hamilton (Irish immigrant)
        "P114": "hamilton",   # Eleanor Preston
        "P115": "hamilton",   # John Buchanan
        "P116": "hamilton",   # Isabella Watson
        # King line
        "P062": "king",       # Ethel Rose King (also Hamilton)
        "P101": "king",       # Thomas Allan King
        "P102": "king",       # Catherine Ann Clark
        "P103": "riggs",      # Harmon Miles Riggs (Ernest's father)
        "P104": "riggs",      # Amelia Williams
        "P107": "riggs",      # David J. Riggs Jr
        "P108": "riggs",      # Catherine Hendricks
        # deVries line
        "P055": "devries",    # Gerhard de Vries
        "P056": "devries",    # Trientje
        "P067": "devries",    # Gerhard's child
        "P097": "devries",    # Leewe de Vries
        "P098": "devries",    # Trienje Pommer
        "P105": "devries",    # Engbertus de Vries
        "P106": "devries",    # Maria Meinders
        # Hourie line
        "P060": "hourie",     # Sarah Ann Hourie (married into setter line)
        "P117": "hourie",     # Philip Hourie
        "P118": "hourie",     # Euphemia Cook Halcro
        "P119": "hourie",     # John Hourie (Orkney patriarch)
        "P120": "hourie",     # Margaret Bird (Shoshoni)
        # Hallett line
        "P121": "hallett",    # Henry Hallett Jr (Catherine's father)
        "P122": "hallett",    # Catherine Parenteau
        "P125": "hallett",    # Henry Hallett Sr
        "P126": "hallett",    # Catherine Crise (Cree)
        "P127": "hallett",    # William Peter Hallett
        "P128": "hallett",    # Maria Pruden
        "P123": "hallett",    # Jean Baptiste Parenteau
        "P124": "hallett",    # Unknown (Parenteau)
        # Collateral / in-law / unassigned
        "P023": "setter",     # Duncan Ritchie (George's child)
        "P024": "setter",     # Colin Campbell (married Jemima Hourie)
        "P027": "setter",     # Alexander Hunter Murray
        "P052": "inlaw",      # Tracy Diane Lau
        "P053": "inlaw",      # Robert Lau (married in)
        "P058": "inlaw",      # Al Hamilton (Bayard's great-uncle)
    }
    return trunk
FAMILY_LINES = _build_family_lines()
# Map to CSS class names
FAClass = {pid: f"fl-{line}" for pid, line in FAMILY_LINES.items()}
# Add group node classes
for gid in ("P900", "P901", "P902"):
    FAClass[gid] = "fl-grp"
# Build FAMILY_CLASS map for all placed nodes
FAMILY_CLASS = {}
for n in PERS:
    FAMILY_CLASS[n["pid"]] = FAClass.get(n["pid"], "fl-stone")

TREE = {"nodes": PERS, "fams": FAMS, "edges": TEDGES, "lanes": TREE_LANES,
        "pw": P_W, "ph": P_H, "rowh": ROW_H,
        "faclass": FAMILY_CLASS,
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
    (1824, "h", "Cuthbert Grant founds Grantown (later St. François Xavier) at White Horse Plain — a centre of the Métis buffalo-hunt economy where the family's Spence and Setter kin lived."),
    (1840, "h", "The great 1840 summer buffalo hunt: 1,210 Red River carts and 620 hunters leave, returning with meat from ~10,000 buffalo — the world the Red River Métis, including this family, lived in."),
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

# ---- Feature 2: provenance flags (which facts are primary-verified vs inferred) ----
# 'verified' = confirmed by a primary record (census, scrip affidavit, vital-stat registration,
#              HBC/DCB record, will, marriage/birth registration) located in this research.
# 'inferred' = oral tradition / uncorroborated / needs verification.
VERIFIED = {"P001","P002","P003","P006","P007","P010","P025","P029","P030","P033","P034","P035","P036","P037","P038","P039","P040","P041","P042","P043","P044","P051","P060","P079","P92","P93","P96","P97","P98","P99","P100","P101","P102","P103","P104","P105","P106","P107","P108","P109","P110","P111","P112","P113","P114","P115","P116","P117","P118","P119","P121","P122","P123","P125","P127","P128","P129","P130","P131","P132","P133","P134","P135","P136","P137","P138","P139","P140","P141","P142","P143","P144","P145","P146","P147","P148","P149","P150","P151","P152","P153","P154","P155","P156","P157"}
INFERRED = {"P080","P94","P95","P120","P126"}  # Cree matriarch 'Nikawiy' + Oltrop grandparents + Margaret Bird + Catherine Crise (secondary/oral, need primary)

# ---- Map: family places & the lines connecting them (Leaflet, real coordinates) ----
# `core:false` marks far-flung origins (Europe / US) that are reachable by zooming out but
# excluded from the default view so the map centres on the Red River / MB-SK homeland.
MAP_PLACES = [
 {"id":"orkney","name":"Orkney, Scotland","lat":59.048,"lng":-2.969,"core":False,"people":["P001","P007","P119"],
  "note":"Home of the HBC founders: James Spence Sr and Andrew Setter (both Orkney), and John Hourie (South Ronaldsay)."},
 {"id":"york","name":"York Factory","lat":57.003,"lng":-92.302,"core":False,"people":["P001","P007","P079"],
  "note":"HBC post on Hudson Bay where the fur-trade founders worked: James Spence Sr, Andrew Setter (voyageur) and Isaac Batt."},
 {"id":"battersea","name":"Battersea, England","lat":51.461,"lng":-0.160,"core":False,"people":["P125"],
  "note":"Where Henry Hallett Sr was baptised (1773) before coming to Rupert's Land."},
 {"id":"quebec","name":"Montreal, Quebec","lat":45.501,"lng":-73.567,"core":False,"people":["P123"],
  "note":"Origin of Jean Baptiste Parenteau, who came to Red River (father of Catherine Parenteau)."},
 {"id":"mayo","name":"Co. Mayo, Ireland","lat":53.980,"lng":-9.430,"core":False,"people":["P113","P114"],
  "note":"Irish home of John Hamilton + Eleanor Preston, the founders of the Hamilton line (settlers, not Scottish)."},
 {"id":"friesland","name":"Ee, Friesland, Netherlands","lat":53.329,"lng":5.992,"core":False,"people":["P105","P97","P069","P067"],
  "note":"deVries homeland in the Frisian lands (Ee, Netherlands / East Frisia, Germany); the deVries surname comes from here."},
 {"id":"winchester","name":"Winchester Twp, Ontario","lat":44.990,"lng":-75.340,"core":False,"people":["P109","P110","P101"],
  "note":"Stormont, Dundas & Glengarry. Home of William King + Sarah Burke; their son Thomas Allan King was born here (1864)."},
 {"id":"mornington","name":"Mornington, Ontario","lat":43.490,"lng":-80.860,"core":False,"people":["P111","P112","P99"],
  "note":"Perth County. Joseph Hamilton married Mary Busby here (1848); son John James Hamilton born 1856."},
 {"id":"muscatine","name":"Muscatine, Iowa","lat":41.420,"lng":-91.040,"core":False,"people":["P107"],
  "note":"Where David J. Riggs Jr lived (1804-1850); the Riggs line came north from the United States to Red River."},
 {"id":"flinflon","name":"Flin Flon","lat":54.768,"lng":-101.864,"core":True,"people":["P045","P046"],
  "note":"The Hamiltons moved here in 1939, when Mavis was six. This is how the maternal line came to Flin Flon."},
 {"id":"tisdale","name":"Tisdale, SK","lat":52.853,"lng":-104.051,"core":True,"people":["P044","P045","P046"],
  "note":"Doris Setter married Lawrence Hamilton here (1932); their daughter Mavis was born here in 1933."},
 {"id":"neche","name":"Neche, ND","lat":48.980,"lng":-97.550,"core":True,"people":["P062"],
  "note":"Where Ethel Rose King was born (1892); the King family crossed from Ontario through here to Saskatchewan."},
 {"id":"thepas","name":"The Pas","lat":53.826,"lng":-101.254,"core":True,"people":["P079"],
  "note":"Isaac Batt traded and travelled inland near here in the 1760s-70s."},
 {"id":"standrews","name":"St. Andrews","lat":50.270,"lng":-96.979,"core":True,"people":["P010","P025"],
  "note":"Red River parish where the Setter line is recorded in the 1870 census."},
 {"id":"stjohns","name":"St. John's, Red River","lat":49.895,"lng":-97.138,"core":True,"people":["P030","P033","P121","P122"],
  "note":"Red River. David Spence was born here in 1824 and married Catherine Hallett here in 1844; Henry Hallett Jr married Catherine Parenteau here in 1824."},
 {"id":"sfx","name":"St. François Xavier","lat":49.905,"lng":-97.526,"core":True,"people":["P051"],
  "note":"White Horse Plain, the buffalo-hunt community where the family's Norquay kin lived."},
 {"id":"poplar","name":"Poplar Point","lat":50.040,"lng":-98.002,"core":True,"people":["P030","P010","P025"],
  "note":"David Spence's home and his MLA constituency; the Setter family farmed here. Both families in the 1870 census."},
 {"id":"highbluff","name":"High Bluff","lat":49.978,"lng":-98.251,"core":True,"people":["P030","P010","P060"],
  "note":"David Spence applied for Metis scrip here in 1875; George Setter farmed here; Sarah Ann Hourie was born and died here."},
 {"id":"beautifulplains","name":"Beautiful Plains, MB","lat":50.440,"lng":-99.280,"core":True,"people":["P061"],
  "note":"Where Guy Wentworth Hamilton was born (1882), after the Hamilton family moved west from Ontario."},
 {"id":"ochreriver","name":"Ochre River, MB","lat":51.160,"lng":-99.450,"core":True,"people":["P067","P068","P071"],
  "note":"The deVries homestead near Lake Dauphin / Turtle River; Gerhard and Geeske farmed here after coming from Friesland."},
 {"id":"portage","name":"Portage la Prairie","lat":49.973,"lng":-98.290,"core":True,"people":["P041","P038","P043","P042","P044"],
  "note":"Ernest Riggs's farm. Allan Setter married Ella Riggs here (1909); their daughter Doris was born here in 1912."},
]
# migration / connection lines, one colour per family line (legend rendered on the map)
MAP_LINKS = [
 {"id":"spence_setter","label":"Spence & Setter (line A)","color":"#E8B45A",
  "p":["orkney","york","stjohns","standrews","poplar","highbluff","portage"],"dash":False,
  "desc":"Your direct line. James Spence Sr (Orkney) and Margaret 'Nestichio' Batt, the Metis matriarch; through Peggy Spence and Andrew Setter, then the Setters of Red River, ending at Alan Setter."},
 {"id":"spence_riggs","label":"Spence & Riggs (line B)","color":"#C39BD3",
  "p":["orkney","york","stjohns","portage"],"dash":False,
  "desc":"Your direct line. From James Spence Sr through David Spence (the MLA), his daughter Mary Ann Spence who married Ernest Riggs, to Ella Alberta Riggs. Lines A and B meet at the Alan Setter + Ella Riggs marriage."},
 {"id":"batt","label":"Batt (fur trade)","color":"#7A6D96",
  "p":["orkney","york","thepas"],"dash":True,
  "desc":"Isaac Batt, the English HBC fur trader who worked and travelled inland (The Pas) and was the father of Margaret 'Nestichio' Batt."},
 {"id":"hourie","label":"Hourie","color":"#E57373",
  "p":["orkney","stjohns","highbluff"],"dash":True,
  "desc":"John Hourie of Orkney (and a Shoshoni wife); his granddaughter Sarah Ann Hourie married Roderick McKenzie Setter, joining the Hourie and Setter families."},
 {"id":"hallett","label":"Hallett","color":"#F06292",
  "p":["battersea","stjohns"],"dash":True,
  "desc":"Henry Hallett Sr, baptised in Battersea, England, founder of the Red River Hallett family; Catherine Hallett married David Spence."},
 {"id":"parenteau","label":"Parenteau","color":"#BA68C8",
  "p":["quebec","stjohns"],"dash":True,
  "desc":"Jean Baptiste Parenteau, who came from Quebec to Red River; his daughter Catherine Parenteau married Henry Hallett Jr."},
 {"id":"deVries","label":"deVries (Dutch)","color":"#5B8DEF",
  "p":["friesland","ochreriver"],"dash":False,
  "desc":"Your paternal line. The deVries family came from the Frisian lands (Ee, Netherlands / East Frisia) and homesteaded at Ochre River near Lake Dauphin."},
 {"id":"hamilton","label":"Hamilton (Irish)","color":"#6FBF73",
  "p":["mayo","mornington","beautifulplains","tisdale","flinflon"],"dash":False,
  "desc":"Your maternal in-law line. The Hamiltons came from Co. Mayo, Ireland, through Ontario (Mornington) and Beautiful Plains, then west to Tisdale and north to Flin Flon."},
 {"id":"king","label":"King","color":"#4DB6AC",
  "p":["winchester","neche","tisdale"],"dash":True,
  "desc":"Ethel Rose King's family, settlers who came west from Winchester Twp, Ontario, through Neche, North Dakota, into Saskatchewan."},
 {"id":"riggs","label":"Riggs (US)","color":"#FF8A65",
  "p":["muscatine","portage"],"dash":True,
  "desc":"The Riggs line came north from Iowa (David J. Riggs Jr lived in Muscatine) to Red River, where Ernest Riggs farmed at Portage."},
 {"id":"north","label":"Your line (to Flin Flon)","color":"#9CE0F5",
  "p":["portage","tisdale","flinflon"],"dash":False,
  "desc":"The modern move: Doris Setter married Lawrence Hamilton at Tisdale, and the family moved to Flin Flon in 1939, bringing the line from Red River to the north."},
]

# detailed legend + 'how to read' blocks rendered from the links above (injected into the map tab)
def _map_route(ids):
    names = {p["id"]: p["name"] for p in MAP_PLACES}
    return " → ".join(names.get(i, i) for i in ids)
MAP_LEGEND_HTML = '<div class="mlegendfull"><h3>Family lines</h3>' + "".join(
    f'<div class="mlgrow"><i class="sw" style="background:{lk["color"]}{(";height:3px" if lk["dash"] else "")}"></i>'
    f'<div class="mlgtxt"><b>{lk["label"]}</b><span class="mlgroute">{_map_route(lk["p"])}</span>'
    f'<span class="mlgdesc">{lk.get("desc","")}</span></div></div>' for lk in MAP_LINKS) + '</div>'
MAP_ABOUT_HTML = ('<div class="mabout"><h3>How to read this map</h3>'
  '<p>Each red marker is a place where family lived or passed through. Tap one to see who was there. '
  'The coloured lines trace the journey of each <b>family line</b>.</p>'
  '<p>The <b>gold</b> and <b>purple</b> lines are your two direct ancestors (the Spence-Setter and Spence-Riggs lines). '
  'They begin in Orkney and converge at the Alan Setter + Ella Riggs marriage, which is how two separate Spence lines both lead to you.</p>'
  '<p>Solid lines show settlement and the dashed lines show fur-trade or earlier migration. '
  'Distant origins in Europe and the United States sit off the default view, so zoom out to see them.</p></div>')

# =========================================================
# EMBEDDED DATA (for the JS app)
# =========================================================
JS_DATA = {
    "title": PROJ["title"], "subtitle": PROJ["focus"],
    "people": [{"id": p["id"], "name": p["name"], "birth": p.get("birth"), "death": p.get("death"),
                "metis": bool(p.get("metis")), "living": p.get("privacy") == "living",
                "note": p.get("note", ""), "you": bool(p.get("you")),
                "group": bool(p.get("group")), "kids": p.get("kids", 0),
                "inlaw": p["id"] in INLAW,
                "vflag": ("verified" if p["id"] in VERIFIED else ("inferred" if p["id"] in INFERRED else ""))} for p in PEOPLE.values()],
    "unions": [{"id": u["id"], "s1": u["spouse1"], "s2": u["spouse2"],
                "children": u["children"], "note": u.get("note", "")} for u in UNIONS],
    "stories": STORIES,
    "images": IMAGES,
    "tree": TREE,
    "timeline": TIMELINE,
    "paths": DATA["paths_to_root"],
    "open": DATA["open_items"],
    "mapplaces": MAP_PLACES,
    "maplinks": MAP_LINKS,
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

  <section id="view-map" class="view">
    <h2 class="vhead">Where they lived</h2>
    <div class="mapintro">Tap a marker to see the family who lived there. Each coloured line traces one family line's journey, from the fur-trade homeland to the modern north. Key below the map.</div>
    <div id="mapwrap" class="mapwrap"></div>
    [[MAP_ABOUT]]
    [[MAP_LEGEND]]
  </section>
</main>

<nav class="tabbar">
  <button class="tab active" data-tab="tree"><span class="ti">🌳</span><span>Tree</span></button>
  <button class="tab" data-tab="people"><span class="ti">👥</span><span>People</span></button>
  <button class="tab" data-tab="stories"><span class="ti">📖</span><span>Stories</span></button>
  <button class="tab" data-tab="timeline"><span class="ti">🕰</span><span>Timeline</span></button>
  <button class="tab" data-tab="map"><span class="ti">🗺</span><span>Map</span></button>
</nav>

<div id="backdrop"></div>
<div id="sheet">
  <div class="sheet-handle"></div>
  <button class="sheet-close" id="sheetclose">✕</button>
  <div id="sheetbody"></div>
</div>

<button id="commentbtn" class="comment-fab" aria-label="Share a memory or suggest an edit">💬</button>
<div id="commentmodal" class="modal">
  <div class="modal-box">
    <button class="sheet-close" id="commentclose">✕</button>
    <h3>Share a memory or suggest an edit</h3>
    <p class="cmuted">Tell the family something, or flag something that needs correcting. Submitting opens your email app with the message ready to send to the family-tree owner.</p>
    <label class="cfield">Your name <input id="cname" type="text" placeholder="optional"></label>
    <label class="cfield">About whom or where <input id="csubject" type="text" placeholder="e.g. David Spence, or Portage la Prairie"></label>
    <label class="cfield">Your message <textarea id="cmsg" rows="4" placeholder="Write your memory, comment, or correction here..."></textarea></label>
    <div class="cbtns"><button id="ccancel" class="cbtn ghost">Cancel</button><button id="csend" class="cbtn">Send via email</button></div>
  </div>
</div>
"""

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
:root{
  --bg:#14121A;--surface:#1E1A26;--surface2:#272131;--line:#3A3346;
  --txt:#F2E9DC;--muted:#9C8FA9;--crimson:#E0525C;--crimson-d:#8C1F28;
  --gold:#D4A853;--cream:#F5EDE2;
  /* organic earthy palette for family-line colour coding */
  --earth-umber:#7B5A42;--earth-sienna:#A66E4E;--earth-ochre:#C9A66F;
  --earth-forest:#4A6B3F;--earth-moss:#5D7B5D;--earth-terracotta:#B46B4A;
  --earth-stone:#6B5E52;--earth-clay:#9C7A62;}
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
.cnode.inlaw{border-style:dashed;border-color:var(--muted);opacity:.95}
.cnode.inlaw .n1{color:var(--muted);font-style:italic}
.cnode.grp{border-style:dashed;border-color:var(--gold);background:rgba(214,168,83,.08);cursor:zoom-in}
.cnode.grp .n1{color:var(--gold)}
/* organic earthy family-line colour accents + slow pulse */
.cnode.fl-setter{border-left:3px solid var(--earth-umber);box-shadow:0 0 8px rgba(123,90,66,.15)}
.cnode.fl-riggs{border-left:3px solid var(--earth-sienna);box-shadow:0 0 8px rgba(166,110,78,.15)}
.cnode.fl-spence{border-left:3px solid var(--earth-forest);box-shadow:0 0 8px rgba(74,107,63,.15)}
.cnode.fl-hamilton{border-left:3px solid var(--earth-forest);box-shadow:0 0 8px rgba(74,107,63,.15)}
.cnode.fl-king{border-left:3px solid var(--earth-ochre);box-shadow:0 0 8px rgba(201,166,95,.15)}
.cnode.fl-devries{border-left:3px solid var(--earth-stone);box-shadow:0 0 8px rgba(107,94,82,.15)}
.cnode.fl-hallett{border-left:3px solid var(--earth-terracotta);box-shadow:0 0 8px rgba(180,107,74,.15)}
.cnode.fl-hourie{border-left:3px solid var(--earth-moss);box-shadow:0 0 8px rgba(93,123,93,.15)}
.cnode.fl-bayard{border-left:3px solid var(--crimson);box-shadow:0 0 10px rgba(224,82,92,.2)}
.cnode.fl-grp{border-left:3px solid var(--gold);box-shadow:0 0 8px rgba(212,168,83,.15)}
.cnode.fl-inlaw{border-left:3px solid var(--muted);box-shadow:0 0 8px rgba(156,143,169,.15)}
.cnode.fl-stone{border-left:3px solid var(--muted);box-shadow:0 0 8px rgba(156,143,169,.1)}
/* slow organic pulse — each family line pulses in its own colour */
@keyframes pulseSetter{0%,100%{box-shadow:0 0 6px rgba(123,90,66,.1);box-border-color:rgba(123,90,66,.3)}50%{box-shadow:0 0 14px rgba(123,90,66,.25),0 0 24px rgba(123,90,66,.15)}}
@keyframes pulseRiggs{0%,100%{box-shadow:0 0 6px rgba(166,110,78,.1)}50%{box-shadow:0 0 14px rgba(166,110,78,.25),0 0 24px rgba(166,110,78,.15)}}
@keyframes pulseHamilton{0%,100%{box-shadow:0 0 6px rgba(74,107,63,.1)}50%{box-shadow:0 0 14px rgba(74,107,63,.25),0 0 24px rgba(74,107,63,.15)}}
@keyframes pulseSpence{0%,100%{box-shadow:0 0 6px rgba(74,107,63,.1)}50%{box-shadow:0 0 14px rgba(74,107,63,.25),0 0 24px rgba(74,107,63,.15)}}
@keyframes pulseKing{0%,100%{box-shadow:0 0 6px rgba(201,166,95,.1)}50%{box-shadow:0 0 14px rgba(201,166,95,.25),0 0 24px rgba(201,166,95,.15)}}
@keyframes pulseDevries{0%,100%{box-shadow:0 0 6px rgba(107,94,82,.1)}50%{box-shadow:0 0 14px rgba(107,94,82,.25),0 0 24px rgba(107,94,82,.15)}}
@keyframes pulseHallett{0%,100%{box-shadow:0 0 6px rgba(180,107,74,.1)}50%{box-shadow:0 0 14px rgba(180,107,74,.25),0 0 24px rgba(180,107,74,.15)}}
@keyframes pulseHourie{0%,100%{box-shadow:0 0 6px rgba(93,123,93,.1)}50%{box-shadow:0 0 14px rgba(93,123,93,.25),0 0 24px rgba(93,123,93,.15)}}
@keyframes pulseGrp{0%,100%{box-shadow:0 0 6px rgba(212,168,83,.14)}50%{box-shadow:0 0 14px rgba(212,168,83,.25),0 0 24px rgba(212,168,83,.15)}}
@keyframes pulseInlaw{0%,100%{box-shadow:0 0 6px rgba(156,143,169,.1)}50%{box-shadow:0 0 14px rgba(156,143,169,.25),0 0 24px rgba(156,143,169,.15)}}
@keyframes pulseStone{0%,100%{box-shadow:0 0 6px rgba(107,94,82,.1)}50%{box-shadow:0 0 14px rgba(107,94,82,.25),0 0 24px rgba(107,94,82,.15)}}
@keyframes pulseBayard{0%,100%{box-shadow:0 0 8px rgba(224,82,92,.2)}50%{box-shadow:0 0 16px rgba(224,82,92,.35),0 0 28px rgba(224,82,92,.2)}}
.cnode.fl-setter{animation:pulseSetter 8s ease-in-out infinite}
.cnode.fl-riggs{animation:pulseRiggs 9s ease-in-out 0.5s infinite}
.cnode.fl-spence{animation:pulseSpence 8.5s ease-in-out 1s infinite}
.cnode.fl-hamilton{animation:pulseHamilton 8s ease-in-out 0.3s infinite}
.cnode.fl-hallett{animation:pulseHallett 9s ease-in-out 0.8s infinite}
.cnode.fl-hourie{animation:pulseHourie 8.5s ease-in-out 0.2s infinite}
.cnode.fl-king{animation:pulseKing 9s ease-in-out 0.6s infinite}
.cnode.fl-devries{animation:pulseDevries 8s ease-in-out 0.4s infinite}
.cnode.fl-grp{animation:pulseGrp 7s ease-in-out 0.1s infinite}
.cnode.fl-stone{animation:pulseStone 10s ease-in-out 0.7s infinite}
.cnode.fl-inlaw{animation:pulseInlaw 9s ease-in-out 0.9s infinite}
.cnode.fl-bayard{animation:pulseBayard 6s ease-in-out infinite}
.cnode .sp{display:inline-block;margin-top:2px;background:rgba(214,168,83,.14);color:var(--gold);font-size:8px;font-weight:700;letter-spacing:.3px;padding:1px 5px;border-radius:6px}
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

/* map (Leaflet) */
.mapintro{font-size:13.5px;color:var(--muted);line-height:1.5;margin:0 4px 12px}
.mapwrap{position:relative;z-index:0;height:min(72vh,820px);min-height:440px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#16203a}
.mapwrap .leaflet-container{background:#16203a;font-family:'EB Garamond',serif}
.mapwrap .leaflet-popup-content-wrapper{background:var(--surface2);color:var(--cream);border:1px solid var(--gold);border-radius:12px}
.mapwrap .leaflet-popup-content{margin:12px 14px}
.mapwrap .leaflet-popup-tip{background:var(--surface2)}
.leaflet-container a{color:var(--gold)}
.mpop h4{font-family:'Cinzel',serif;color:var(--gold);font-size:15px;margin-bottom:3px}
.mpop p{font-size:12.5px;color:var(--txt);line-height:1.4;margin-bottom:8px}
.mpop .chips{display:flex;flex-wrap:wrap;gap:5px}
.mpop .chip{font-size:11.5px;padding:3px 9px}
.mapidle{color:var(--muted);font-size:14px;padding:14px}
.mlegend{position:absolute;bottom:24px;right:10px;z-index:500;background:rgba(20,26,43,.92);border:1px solid var(--line);border-radius:10px;padding:8px 10px;max-width:210px}
.mlegend .mlrow{display:flex;align-items:center;gap:8px;font-size:11.5px;color:var(--cream);line-height:1.5}
.mlegend .mlrow i{display:inline-block;width:18px;height:4px;border-radius:2px;flex:none}
.mabout{background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:14px 0}
.mabout h3,.mlegendfull h3{font-family:'Cinzel',serif;font-size:13px;letter-spacing:1px;color:var(--gold);margin:0 0 8px;text-transform:uppercase}
.mabout p{font-size:13.5px;color:var(--txt);line-height:1.55;margin:0 0 8px}
.mabout p:last-child{margin-bottom:0}
.mlegendfull{background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.mlgrow{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid var(--line)}
.mlgrow:last-child{border-bottom:none}
.mlgrow .sw{display:inline-block;width:22px;height:5px;border-radius:3px;flex:none;margin-top:6px}
.mlgrow .mlgtxt{flex:1;min-width:0}
.mlgrow .mlgtxt b{display:block;font-family:'Cinzel',serif;font-size:13px;color:var(--cream)}
.mlgrow .mlgroute{display:block;font-size:11.5px;color:var(--gold);margin:1px 0 3px;font-style:italic}
.mlgrow .mlgdesc{display:block;font-size:12.5px;color:var(--txt);line-height:1.45}

/* comments / suggest an edit */
.comment-fab{position:fixed;right:16px;bottom:78px;width:54px;height:54px;border-radius:50%;border:none;background:var(--gold);color:#241a0c;font-size:24px;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.4);z-index:900}
.modal{position:fixed;inset:0;z-index:1000;background:rgba(10,8,16,.66);display:none;align-items:flex-end;justify-content:center}
.modal.open{display:flex}
.modal-box{position:relative;background:var(--surface);border:1px solid var(--line);border-top-left-radius:20px;border-top-right-radius:20px;padding:20px 18px 26px;width:100%;max-width:520px;max-height:88vh;overflow-y:auto}
.modal-box h3{font-family:'Cinzel',serif;color:var(--gold);font-size:18px;margin-bottom:6px}
.cmuted{font-size:13px;color:var(--muted);line-height:1.45;margin-bottom:14px}
.cfield{display:block;margin-bottom:12px;font-size:12.5px;color:var(--muted);font-family:'Cinzel',serif;letter-spacing:.4px}
.cfield input,.cfield textarea{display:block;width:100%;margin-top:5px;background:var(--surface2);border:1px solid var(--line);border-radius:10px;padding:10px 12px;color:var(--cream);font-size:14.5px;font-family:'EB Garamond',serif;resize:vertical}
.cbtn{flex:1;background:var(--gold);color:#241a0c;border:none;border-radius:12px;padding:13px;font-family:'Cinzel',serif;font-size:15px;font-weight:700;cursor:pointer}
.cbtn.ghost{background:var(--surface2);color:var(--muted);border:1px solid var(--line);font-weight:600}
.cbtns{display:flex;gap:10px;margin-top:2px}
.editsuggest{display:block;width:100%;background:var(--surface2);border:1px dashed var(--gold);color:var(--gold);border-radius:12px;padding:11px;margin-bottom:12px;font-size:13.5px;font-family:'Cinzel',serif;cursor:pointer}

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
/* provenance badges */
.pflag{font-size:10px;font-weight:600;letter-spacing:.3px;padding:2px 7px;border-radius:10px;vertical-align:middle;white-space:nowrap}
.vflag{background:#1d3323;color:#7bd89b;border:1px solid #2f5e3f}
.iflag{background:#33291d;color:#e0b96a;border:1px solid #5e4a2f}
/* 'how you're related' path */
.pathchain{display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;line-height:1.4}
.pthchip{background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:3px 10px;font-size:12.5px;color:var(--cream);cursor:pointer}
.pthchip.you{background:var(--gold);color:#241a0c;border-color:var(--gold);font-weight:600}
.pthchip:active{border-color:var(--gold)}
.ptharrow{color:var(--gold);font-size:12px}
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
    l.setAttribute('vector-effect','non-scaling-stroke');  // lines stay thick at ANY zoom (phone fix)
    if(dash)l.setAttribute('stroke-dasharray','5,5');
    svg.appendChild(l);
  };
  // classic structure: marriage bars + INDIVIDUAL parent->child elbows.
  // Each child gets its OWN connector (down from the bar, over, down into the box)
  // so no two families ever share a rail that reads as one shared parent.
  const PW=T.pw, PH=T.ph, RH=T.rowh;
  // organic earthy colours: marriage bars warm gold, child connectors per family-line
  const RAIL='#A99BD9', MAR='#C9A66F';
  // family-line colour lookup (must match CSS fl-* classes)
  const lineColor = {
    'fl-setter':'#7B5A42','fl-riggs':'#A66E4E','fl-spence':'#4A6B3F',
    'fl-hamilton':'#4A6B3F','fl-king':'#C9A66F','fl-devries':'#6B5E52',
    'fl-hallett':'#B46B4A','fl-hourie':'#5D7B5D','fl-bayard':'#E0525C',
    'fl-grp':'#D4A853','fl-inlaw':'#9C8FA9','fl-stone':'#6B5E52'
  };
  function lineC(pid){var c=T.faclass&&T.faclass[pid];return c?lineColor[c]||'#6B5E52':'#6B5E52';}
  const famById={};T.fams.forEach(f=>famById['fam_'+f.u]=f);
  T.fams.forEach(f=>{
    const n1=nodeById(f.s1), n2=nodeById(f.s2);
    if(!n1||!n2)return;
    const c1x=n1.x+n1.w/2, c2x=n2.x+n2.w/2;                 // ACTUAL spouse centers
    const my=f.y+PH/2;
    seg(c1x, my, c2x, my, MAR, 4.5);                        // marriage bar
    const barx=(c1x+c2x)/2, y0=f.y+PH;
    if(f.children.length){
      const kids=f.children.map(c=>nodeById(c[0])).filter(Boolean);
      // stagger the drop from the bar so same-row children don't stack into a rail
      const dropYs=[];
      kids.forEach(k=>{ dropYs.push((y0 + k.y + k.h/2)/2); });
      kids.forEach((k,i)=>{
        const cx=k.x+k.w/2, ky=k.y+k.h/2;
        const midY=dropYs[i];
        var kidColor=lineC(k.pid);
        seg(barx, y0, barx, midY, kidColor, 3.5);             // down from bar (family-line colour)
        seg(barx, midY, cx, midY, kidColor, 3.5);             // over to child x
        seg(cx, midY, cx, ky, kidColor, 3.5);                 // down into child box
      });
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
        const cxF=(f)=>{const a=nodeById(f.s1),b=nodeById(f.s2);return a&&b?(a.x+a.w/2+b.x+b.w/2)/2:f.x;};
        const x1=cxF(f1), x2=cxF(f2);
        const y1=f1.y+PH, y2=f2.y+PH;
        const mid=(y1+y2)/2;
        seg(x1,y1,x1,mid,MAR,3);seg(x1,mid,x2,mid,MAR,3);seg(x2,mid,x2,y2,MAR,3);
      }
    }
  });
  canvas.appendChild(svg);
  T.nodes.forEach(n=>{
    const p=people[n.pid];
    if(!p)return;
    const div=document.createElement('div');
    div.className='cnode'+(n.you?' you':'')+(p.inlaw?' inlaw':'')+(T.faclass&&T.faclass[n.pid]?' '+T.faclass[n.pid]:'');
    div.style.left=n.x+'px';div.style.top=n.y+'px';div.style.width=n.w+'px';div.style.height=n.h+'px';
    let h='';
    if(p.group){
      div.classList.add('grp');
      h+=`<div class="n1">${escH(p.name)}</div><div class="years">${p.kids} children · tap for list</div>`;
    }else{
      h+=`<div class="n1">${escH(p.name)}</div><div class="years">${escH(yrs(p))}</div>`;
    }
    if(p.metis)h+='<span class="m">MÉTIS</span>';
    if(p.inlaw)h+='<span class="sp">⚭ married in</span>';
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
// (generation lane sidebar removed - labels no longer made sense for the grown, multi-branch tree)
let laneEls=[];
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
    if(tab==='map')setTimeout(startMap,60);
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
  card.innerHTML=`<h3>${escH(s.title)}</h3><span class="who">${escH(p.name)}</span> ${vBadge(p)}<p>${escH(s.text)}</p>${src}`;
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

/* ---------- map (Leaflet) ---------- */
const MPLACES={};D.mapplaces.forEach(p=>MPLACES[p.id]=p);
let LEAFLET_MAP=null, mapStarted=false;
function renderMap(){
  const el=document.getElementById('mapwrap');
  if(typeof L==='undefined'){ el.innerHTML='<div class="mapidle">Map tiles need an internet connection.</div>'; return; }
  el.innerHTML='';
  LEAFLET_MAP=L.map(el,{scrollWheelZoom:false}).setView([52.0,-99.5],6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap contributors'}).addTo(LEAFLET_MAP);
  const core=[]; const mlegend=[];
  D.mapplaces.forEach(p=>{
    const chips=p.people.map(id=>`<button class="chip" data-id="${id}">${escH(people[id].name)}</button>`).join('');
    const html=`<div class="mpop"><h4>${escH(p.name)}</h4><p>${escH(p.note||'')}</p><div class="chips">${chips}</div></div>`;
    L.circleMarker([p.lat,p.lng],{radius:11,color:'#D4A853',weight:2,fillColor:'#E0525C',fillOpacity:1})
      .addTo(LEAFLET_MAP).bindPopup(html);
    if(p.core!==false) core.push([p.lat,p.lng]);
  });
  D.maplinks.forEach(lk=>{
    L.polyline(lk.p.map(id=>[MPLACES[id].lat,MPLACES[id].lng]),
      {color:lk.color||'#D4A853',weight:3,opacity:.85,dashArray:lk.dash?'7,6':null}).addTo(LEAFLET_MAP);
    mlegend.push(`<div class="mlrow"><i style="background:${lk.color||'#D4A853'}${lk.dash?';height:2px':''}"></i><span>${escH(lk.label)}</span></div>`);
  });
  // legend for the family lines
  if(mlegend.length){
    const lg=document.createElement('div');lg.className='mlegend';lg.innerHTML=mlegend.join('');
    const c=document.querySelector('.leaflet-bottom.leaflet-left'); (c||LEAFLET_MAP.getContainer()).appendChild(lg);
  }
  // fit to the core Red River / MB-SK places (Europe & US origins are reachable by zooming out)
  LEAFLET_MAP.fitBounds(core,{padding:[22,22]});
}
function startMap(){
  if(mapStarted){ if(LEAFLET_MAP)LEAFLET_MAP.invalidateSize(); return; }
  mapStarted=true; renderMap();
}
// popup chip clicks open the profile sheet (events bubble up from the popup pane)
document.getElementById('mapwrap').addEventListener('click',e=>{
  const c=e.target.closest('.chip'); if(c){openSheet([c.dataset.id]);}
});

/* ---------- comments / suggest an edit ---------- */
const COMMENTS_TO='bayarddevries@gmail.com'; // family-tree owner receives the comments
function openComment(subject){
  if(subject)document.getElementById('csubject').value=subject;
  document.getElementById('commentmodal').classList.add('open');
}
function closeComment(){
  document.getElementById('commentmodal').classList.remove('open');
  document.getElementById('cname').value='';document.getElementById('csubject').value='';document.getElementById('cmsg').value='';
}
document.getElementById('commentbtn').addEventListener('click',()=>openComment());
document.getElementById('commentclose').addEventListener('click',closeComment);
document.getElementById('ccancel').addEventListener('click',closeComment);
document.getElementById('commentmodal').addEventListener('click',e=>{ if(e.target===e.currentTarget) closeComment(); });
document.getElementById('csend').addEventListener('click',()=>{
  const name=document.getElementById('cname').value.trim();
  const subject=document.getElementById('csubject').value.trim();
  const msg=document.getElementById('cmsg').value.trim();
  if(!msg){document.getElementById('cmsg').focus();return;}
  const body=encodeURIComponent('Name: '+(name||'(not given)')+'\nAbout: '+(subject||'(general)')+'\n\n'+msg);
  const sbj=encodeURIComponent('Family tree: '+(subject||'comment'));
  window.location.href='mailto:'+COMMENTS_TO+'?subject='+sbj+'&body='+body;
  document.getElementById('commentmodal').classList.remove('open');
  document.getElementById('cname').value='';document.getElementById('csubject').value='';document.getElementById('cmsg').value='';
});

/* ---------- provenance badge + 'how you're related' path ---------- */
function vBadge(p){
  if(p.vflag==='verified') return '<span class="pflag vflag">✓ primary record</span>';
  if(p.vflag==='inferred') return '<span class="pflag iflag">⚑ oral tradition</span>';
  return '';
}
// Find the ancestor chain from a person up to Bayard (P050). Returns [Bayard,...,person] or null.
function ancestryPath(pid){
  const T='P050';
  if(pid===T) return null;
  const pm={};
  D.unions.forEach(u=>u.children.forEach(c=>{ (pm[c]=pm[c]||[]).push(u.s1,u.s2); }));
  const q=[T], prev={[T]:null}, seen=new Set([T]);
  while(q.length){
    const cur=q.shift();
    for(const par of (pm[cur]||[])){
      if(seen.has(par)) continue;
      seen.add(par); prev[par]=cur; q.push(par);
    }
  }
  if(!(pid in prev)) return null;
  const out=[]; let c=pid;
  while(c!=null){ out.unshift(c); c=prev[c]; }
  return out;
}
function pathBlock(pid){
  const path=ancestryPath(pid);
  if(!path||path.length<2) return '';
  const rev=path.slice().reverse(); // person first, Bayard last
  const chips=rev.map((id,i)=>{
    const pp=people[id];
    const arrow=i<rev.length-1?' <span class="ptharrow">→</span>':'';
    return `<span class="pthchip${pp.you?' you':''}" data-id="${id}">${escH(pp.name)}</span>${arrow}`;
  }).join('');
  return `<div class="srel pathblock"><h4>How you're related</h4><div class="pathchain">${chips}</div></div>`;
}

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
      <div><div class="sname">${escH(p1.name)} <span class="mtag">${p1.metis?'MÉTIS':''}</span> ${vBadge(p1)}</div>
      <div class="smeta">${escH(fmtYears(p1))}</div>
      <div class="sname" style="font-size:16px;margin-top:6px">${escH(p2.name)} <span class="mtag">${p2.metis?'MÉTIS':''}</span> ${vBadge(p2)}</div>
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
      <div><div class="sname">${escH(p.name)} ${p.you?'<span class="mtag">★ you</span>':''}${p.metis?' <span class="mtag">MÉTIS</span>':''} ${vBadge(p)}</div>
      <div class="smeta">${escH(fmtYears(p))}${p.living?' · living':''}</div></div></div>`;
    if(p.note)h+=`<div class="snote">${escH(p.note)}</div>`;
    h+=pathBlock(p.id);
    h+=`<button class="editsuggest" data-name="${escH(p.name)}">✏️ Suggest an edit about this person</button>`;
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
  const c=e.target.closest('.chip,.pthchip');
  if(c){const id=c.dataset.id;openSheet([id]);}
  const es=e.target.closest('.editsuggest');
  if(es){openComment(es.dataset.name);}
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
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>{CSS}</style>
</head><body>
{APP.replace('[[TITLE]]', esc(PROJ['title'])).replace('[[SUBTITLE]]', esc(PROJ['focus']))
     .replace('[[MAP_ABOUT]]', MAP_ABOUT_HTML).replace('[[MAP_LEGEND]]', MAP_LEGEND_HTML)}
<script>
const __DATA__ = {json_blob};
{JS.replace('__DATA__', '__DATA__')}
</script>
</body></html>"""

out = os.path.join(HERE, "site", "index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(HTML)
print(f"Wrote {out} ({len(HTML)} bytes)")
