#!/usr/bin/env python3
"""Export processed family tree data to GEDCOM for Gramps import.

Uses build_tree.py's processed PEOPLE/UNIONS (159 people, 41 unions)
after all inline additions (P92-P157) have been applied.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Import processed data from build_tree.py (this also runs the build)
import build_tree
PEOPLE = build_tree.PEOPLE   # dict: pid -> {name, birth, death, ...}
UNIONS = build_tree.UNIONS   # list of {id, spouse1, spouse2, children}

lines = [
    "0 HEAD",
    "1 SOUR deVries-Lau Family Tree",
    "1 GEDC",
    "2 VERS 5.5.1",
    "2 FORM Lineage-Linked",
    "1 CHAR UTF-8",
]

# Person gender heuristic
import re as _re
def guess_sex(name, pid):
    # Use known male/female names in the tree
    male_names = {"James","Andrew","George","John","Roderick","Alan","Lawrence","Duncan","Colin","Alexander","Guy","John James","Thomas","William","Joseph","David","Henry","Philip","John Hourie","William","John Buchanan","John Hamilton","John Oltrop","Jan","John James","Antoine","John","John","John James","William","John","John","Joseph","John","John","William","George","Peter","John"}
    female_names = {"Isabella","Ellen","Jane","Mary","Sarah","Catherine","Ethel","Doris","Mavis","Tracy","Bayard","Paula","Jessie","Isabella","Jane","Catherine","Ellen","Jane","Mary","Ellen","Sarah","Euphemia","Isabella","Charlotte","Esther","Antoinette","Anne","Jane","Margaret","Isabella","Jemima","Maria","Charlotte","Esther","Anne","Jane","Isabella","Euphemia","Sarah","Antje","Jane","Ellen","Jane","Mary","Catherine","Ellen","Jane","Harriet","Mary","Jane","Caroline","Elizabeth","Ellen","Charlotte","Ellen"}
    first = name.split()[0] if name.split() else ""
    if first in male_names: return "M"
    if first in female_names: return "F"
    # Heuristic: names ending in 'a' tend female, 'o'/'s' tend male
    if first.endswith("a") or first in ("Jane","Mary","Ellen","Sarah","Catherine","Isabella","Euphemia","Charlotte","Esther","Anne","Jemima","Maria","Antje"):
        return "F"
    return "U"  # unknown

# Emit persons
for pid in sorted(PEOPLE.keys()):
    p = PEOPLE[pid]
    name = p.get("name", "")
    lines.append(f"0 @I{pid}@ INDI")
    lines.append(f"1 NAME {name}")
    sex = guess_sex(name, pid)
    if sex in ("M", "F"):
        lines.append(f"1 SEX {sex}")
    b = p.get("birth", "")
    if b:
        lines.append(f"1 BIRT")
        lines.append(f"2 DATE ABT {b}")
    d = p.get("death", "")
    if d:
        lines.append(f"1 DEAT")
        lines.append(f"2 DATE ABT {d}")
    note = p.get("note", "")
    if note:
        note = _re.sub(r'\n', ' ', note)[:200]
        lines.append(f"1 NOTE {note}")

# Emit families
for u in UNIONS:
    lines.append(f"0 @F{u['id']}@ FAM")
    lines.append(f"1 HUSB @I{u['spouse1']}@")
    lines.append(f"1 WIFE @I{u['spouse2']}@")
    for cid in u.get("children", []):
        lines.append(f"1 CHIL @I{cid}@")

lines.append("0 TRLR")

gedcom_path = os.path.join(HERE, "data", "family-tree.ged")
with open(gedcom_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote {len(lines)} lines to {gedcom_path}")
print(f"  {len(PEOPLE)} individuals, {len(UNIONS)} families")
