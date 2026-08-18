#!/usr/bin/env python3
"""Cross-reference MND surname CSVs against the deVries family-tree roster.
Classifies each record KIN / POSSIBLE / NOISE and writes a flagged CSV + markdown summary.
"""
import csv, os, re, collections

VAULT = "/mnt/c/Users/Bayard deVries/Documents/metis-research-vault/05-Raw Data"
OUT_CSV = os.path.join(VAULT, "MND-flagged-20260813.csv")
OUT_MD  = os.path.join(VAULT, "MND-kin-crossref-20260813.md")

FILES = {
 "Spence":  "MND-Spence-20260813.csv",
 "Setter":  "MND-Setter-20260813.csv",
 "Hallett": "MND-Hallett-20260813.csv",
 "Hamilton":"MND-Hamilton-20260813.csv",
 "Lau":     "MND-Lau-20260813.csv",
 "Riggs":   "MND-Riggs-20260813.csv",
}

# --------------------------------------------------------------------------
# ROSTER: documented persons per surname.  (name, dob_year_or_None, approx_flag, relation/line note)
# dob parsed to the birth year shown in roster.md; 'approx' for cXXX / c1880s ranges.
ROSTER = {
 "Spence": [
   ("James Spence Sr", 1753, True,  "maternal 6th-great-grandfather (Spence Sr)"),
   ("James Spence Jr", 1782, True,  "maternal 5th-great-grandfather (Spence Jr)"),
   ("Margaret Peggy Spence", 1795, False, "maternal 5th-great-grandmother (Peggy), wife of Andrew Setter"),
   ("Andrew Spence", 1786, False, "ancestor/collateral (depth 9)"),
   ("George Spence Sr", 1792, False, "ancestor/collateral (depth 9)"),
   ("David Spence", 1824, False, "maternal 3rd-great-grandfather (Spence line B)"),
   ("Joseph Spence", 1826, False, "ancestor/collateral (depth 8)"),
   ("Catherine Spence", 1829, False, "ancestor/collateral (depth 8)"),
   ("John Jake Spence", 1848, False, "ancestor/collateral (depth 7), son of David Spence"),
   ("Ellen Anderson Spence", 1853, False, "ancestor/collateral (depth 7), dau of David Spence"),
   ("Charles David Spence", 1857, False, "ancestor/collateral (depth 7), son of David Spence"),
   ("Jane Spence", 1859, False, "ancestor/collateral (depth 7), dau of David Spence"),
   ("Mary Ann Spence", 1861, False, "maternal 3rd-great-grandmother (Spence), m. Ernest Charles Riggs"),
   ("Harriet Spence", 1863, False, "ancestor/collateral (depth 7), dau of David Spence"),
   ("William Bill Spence", 1866, False, "ancestor/collateral (depth 7), son of David Spence"),
 ],
 "Setter": [
   ("Andrew Setter", 1777, False, "maternal 5th-great-grandfather (Setter)"),
   ("James Setter", 1810, False, "ancestor/collateral (depth 8)"),
   ("Margaret Setter", 1813, False, "ancestor/collateral (depth 8)"),
   ("Isabella Bella Setter", 1816, False, "ancestor/collateral (depth 8)"),
   ("Elizabeth Setter", 1822, False, "ancestor/collateral (depth 8)"),
   ("Ann Setter", 1825, False, "ancestor/collateral (depth 8)"),
   ("Mary Setter", 1830, False, "ancestor/collateral (depth 8)"),
   ("Thomas Alexander Setter", 1831, False, "ancestor/collateral (depth 8)"),
   ("John Setter", 1832, False, "ancestor/collateral (depth 8)"),
   ("Catherine Setter", 1837, False, "ancestor/collateral (depth 8)"),
   ("George Setter", 1815, False, "maternal 4th-great-grandfather (Setter)"),
   ("John James Setter", 1837, False, "ancestor/collateral (depth 7)"),
   ("Caroline Setter", 1840, False, "ancestor/collateral (depth 7)"),
   ("Elizabeth Setter", 1842, False, "ancestor/collateral (depth 7), m. Premier John Norquay"),
   ("Duncan Richard Setter", 1852, False, "ancestor/collateral (depth 7)"),
   ("Colin Campbell Setter", 1854, False, "ancestor/collateral (depth 7)"),
   ("Alexander Hunter Murray Setter", 1858, False, "ancestor/collateral (depth 7)"),
   ("George William Setter", 1861, False, "ancestor/collateral (depth 7)"),
   ("Ellen Madeleine Nellie Setter", 1861, False, "ancestor/collateral (depth 7)"),
   ("Roderick McKenzie Setter", 1856, False, "maternal 3rd-great-grandfather (Setter line A)"),
   ("Alan Setter", 1884, False, "maternal 2nd-great-grandfather (Setter line A)"),
   ("Elwyn Setter", None, False, "ancestor/collateral (depth 5), son of Alan Setter"),
   ("Erma Ann Setter", 1910, False, "ancestor/collateral (depth 5)"),
   ("Clayton N Setter", 1917, False, "ancestor/collateral (depth 5)"),
   ("Doris A Setter", 1912, False, "maternal great-grandmother (Setter)"),
 ],
 "Hallett": [
   ("Catherine Hallett", 1824, False, "maternal 3rd-great-grandmother (Hallett), wife of David Spence"),
 ],
 "Riggs": [
   ("Ernest Charles Riggs", 1859, False, "maternal 4th-great-grandfather (Riggs), husband of Mary Ann Spence"),
   ("Mary Ann Spence Riggs", 1861, False, "Mary Ann Spence as Riggs (wife of Ernest Charles Riggs)"),
   ("Ella Alberta Riggs", 1885, True, "maternal 2nd-great-grandmother (Riggs line B), dau of Ernest Charles & Mary Ann Spence"),
 ],
 "Hamilton": [
   ("Guy Wentworth Hamilton", 1882, False, "maternal great-great-grandfather (Hamilton)"),
   ("Lawrence Donald Hamilton", 1912, False, "maternal great-grandfather (Hamilton)"),
   ("Jean Margaret Hamilton", 1915, False, "ancestor/collateral (depth 5)"),
   ("Madeleine Phyllis Hamilton", 1918, False, "ancestor/collateral (depth 5)"),
   ("William Morrison Hamilton", 1926, False, "ancestor/collateral (depth 5)"),
   ("Vivian Ethel Hamilton", 1930, False, "ancestor/collateral (depth 5)"),
   ("Mavis Irene Hamilton", 1933, False, "maternal grandmother (Hamilton)"),
   ("Harley Hamilton", 1934, False, "ancestor/collateral (depth 4)"),
 ],
 "Lau": [
   # Robert Lau / Gordon Lau: DOB & parents unknown -> cannot confirm any record as KIN.
   ("Robert Lau", None, False, "maternal grandfather (Lau) - DOB/parents unknown"),
   ("Gordon Lau", None, False, "maternal uncle (Lau) - DOB unknown"),
 ],
}

# nickname / variant -> canonical base first name
NICK = {
 "jake":"john", "bill":"william", "bella":"isabella", "nellie":"ellen",
 "peggy":"margaret", "ellen a":"ellen", "ellen a brown":"ellen",
 "ernest c":"ernest", "ernest e":"ernest", "mary a":"mary", "ella b":"ella",
 "ella":"ella", "alexander hunter":"alander", "alexander hunter murray":"alander",
 "george jr":"george", "george william":"george", "thomas alexander":"thomas",
 "james jr":"james", "james sr":"james", "william robert":"william",
 "mary ann":"mary", "margaret":"margaret",
}

def base_first(name):
    """Normalize a first_name to a comparable base token (lowercased, Jr/Sr & suffixes stripped)."""
    n = name.lower().strip()
    n = n.replace("?", "").replace(".", " ").replace(",", " ")
    # strip trailing Sr/Jr and ordinals
    n = re.sub(r"\b(jr|sr|ii|iii|iv)\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    # drop 'or <x>' alternates already handled at family level; here keep whole
    if n in NICK:
        n = NICK[n]
    # take first token as base for compound given names (e.g. 'ellen anderson' -> 'ellen')
    base = n.split()[0] if n.split() else n
    if base in NICK:
        base = NICK[base]
    return base

def parse_dob(s):
    s = s.strip().lower().replace("?", "")
    m = re.search(r"(\d{4})", s)
    return int(m.group(1)) if m else None

def norm_place(p):
    return p.lower().replace("?", "").replace(".", " ").strip()

# --------------------------------------------------------------------------
# Build findings seq-lookup  (- Spence David 1824 High Bluff Manitoba Affidavits  [seq 1908897])
SEQ_RE = re.compile(r"-\s+(\w+)\s+([^\[]+?)\s+\[seq\s+(\d+)\]")
def load_seq_lookup():
    lp = os.path.join(os.path.dirname(VAULT), "..")  # not used
    findings = "/home/bayard_devries/projects/deVries-family-tree/research/metis-db-family-findings.md"
    seq = {}
    for line in open(findings, encoding="utf-8"):
        m = SEQ_RE.search(line)
        if not m: continue
        fam = m.group(1).strip().lower()
        rest = m.group(2).strip()
        s = m.group(3)
        # rest = "first dob place series"
        parts = rest.split()
        # dob is the token that is a 4-digit year or 'unknown'
        first = None; dob=None; place=[]; series=[]
        for i,w in enumerate(parts):
            if re.fullmatch(r"\d{4}|unknown", w):
                dob = w; first = " ".join(parts[:i]); place = parts[i+1:-1]; series=[parts[-1]]
                break
        if first is None:
            first = rest
        key = (base_first(first), norm_place(" ".join(place)), series[0].lower() if series else "")
        seq.setdefault(key, s)
    return seq

SEQ = load_seq_lookup()

# --------------------------------------------------------------------------
# Geography helpers for POSSIBLE vs NOISE on non-named same-surname records
BC_FAR = ("lillooet","cariboo","kootenay","fort macleod","fraser","okanagan","clinton")
def lau_is_noise(fam):
    # every Lau-file row is a phonetic variant (no exact 'Lau'); Robert Lau undocumented
    return True

def hamilton_noise(place):
    p = norm_place(place)
    return any(t in p for t in BC_FAR)

# --------------------------------------------------------------------------
# Classify
rows_out = []
summary = {s:{"total":0,"KIN":0,"POSSIBLE":0,"NOISE":0} for s in FILES}
kin_rows = collections.defaultdict(list)
poss_rows = collections.defaultdict(list)
noise_rows = collections.defaultdict(list)

for sur, fn in FILES.items():
    path = os.path.join(VAULT, fn)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        fieldnames = rdr.fieldnames
        for r in rdr:
            fam = (r["family_name"] or "").strip()
            first = (r["first_name"] or "").strip()
            dob_raw = (r["year_of_birth"] or "").strip()
            place = (r["place_of_application"] or "").strip()
            series = (r["document_series"] or "").strip()
            dob = parse_dob(dob_raw)
            bf = base_first(first)

            summary[sur]["total"] += 1
            match = "NOISE"
            note = ""

            # 1) exact-name match against roster persons of this surname
            cand = None
            for (nm, ry, approx, rel) in ROSTER.get(sur, []):
                if base_first(nm) == bf:
                    cand = (nm, ry, approx, rel); break

            if cand:
                nm, ry, approx, rel = cand
                if ry is None or dob is None:
                    # DOB unknown on one side -> consistent (unknown-tolerant)
                    consistent = True
                else:
                    consistent = abs(ry - dob) <= 3
                if consistent:
                    match = "KIN"
                    note = f"Matches roster: {nm} ({rel}); roster DOB {ry if ry else 'unknown'}, record DOB {dob if dob else 'unknown'}"
                else:
                    match = "POSSIBLE"
                    note = f"Name matches roster {nm} but DOB differs (roster {ry} vs record {dob}); verify"
            else:
                # 2) not a specifically-named roster person of this surname
                if sur == "Lau":
                    match = "NOISE"
                    note = "Phonetic variant of 'Lau' returned by loose MND search; Robert Lau's line undocumented (DOB/parents unknown) - no confirmable link"
                elif sur == "Hamilton":
                    if hamilton_noise(place):
                        match = "NOISE"
                        note = f"Hamilton common Scots name; place '{place}' (BC/AB) outside documented Manitoba Hamilton line - no plausible connection"
                    else:
                        match = "POSSIBLE"
                        note = "Hamilton same surname, Red River MB location; documented Hamilton line (Guy Wentworth 1882+) thinly placed - review as possible kin"
                else:
                    # Spence / Setter / Hallett / Riggs : Métis record, same surname, plausibly the line
                    match = "POSSIBLE"
                    extra = ""
                    if sur == "Spence" and fam.lower() == "spencer":
                        extra = " (Spencer spelling variant)"
                    note = f"Same surname, Métis record, not individually in roster{extra}; plausible extended/collateral kin of the {sur} line - review"

            # attach findings seq ref if available
            seq_key = (bf, norm_place(place), series.lower())
            if seq_key in SEQ:
                note = (note + f" | MND ref seq {SEQ[seq_key]}").strip(" |")

            rows_out.append({
                "family_name": fam, "first_name": first, "year_of_birth": dob_raw,
                "place_of_application": place, "document_series": series,
                "match": match, "notes": note,
            })
            summary[sur][match] += 1
            rec = (fam, first, dob_raw, place, series, note)
            if match == "KIN": kin_rows[sur].append(rec)
            elif match == "POSSIBLE": poss_rows[sur].append(rec)
            else: noise_rows[sur].append(rec)

# --------------------------------------------------------------------------
# Write flagged CSV
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["family_name","first_name","year_of_birth",
        "place_of_application","document_series","match","notes"])
    w.writeheader()
    w.writerows(rows_out)

print("WROTE", OUT_CSV, "rows:", len(rows_out))
tot = {"total":0,"KIN":0,"POSSIBLE":0,"NOISE":0}
for s in FILES:
    print(f"{s:9s} total={summary[s]['total']:4d}  KIN={summary[s]['KIN']:3d}  POSSIBLE={summary[s]['POSSIBLE']:4d}  NOISE={summary[s]['NOISE']:4d}")
    for k in tot: tot[k]+=summary[s][k]
print("ALL     ", tot)

# stash for the markdown builder
import json
json.dump({"summary":summary, "kin":kin_rows, "poss":poss_rows, "noise":noise_rows},
          open("/tmp/mnd_classified.json","w"))
print("KIN samples:")
for s in FILES:
    for rec in kin_rows[s][:3]:
        print("  ", s, rec)
