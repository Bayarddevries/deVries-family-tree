# Methodology — deVries · Spence

How this family tree is researched and verified.

## 1. Intake (anchor data)
Capture what the family already knows: the known line (name → parent → grandparent), surnames, communities, and the branch-key questions (mother's first name, birth years, maternal grandfather's full name, and where the target surname enters).

## 2. Build the confirmed generations from family knowledge
Lay out the known line before any research, so searches target the right gap.

## 3. Run the source sequence (ordered by value/minute)
1. **redriverancestry.ca** family pages (richest, but hobbyist — treat as a map, flag "verify").
2. **Manitoba vital stats index** (vitalstats.gov.mb.ca) — births/marriages/deaths; the birth DetailView exposes the mother's **maiden name** (the key to finding where a surname entered).
3. **LAC Métis scrip records** — names, relationships, locations; the backbone for Métis trees.
4. **HBCA biographical sheets** (manitoba.ca).
5. **Census** (1901/1911/1921/1926) via FamilySearch — households and children.
6. **Parish registers / SHSB** — the deep-dig referral.

## 4. Bridge the generations
- A missing link is usually found either in a record (marriage, birth-with-mother's-maiden-name) **or by family memory**, which often beats the archives.
- When a marriage "in the surname" is absent, the surname likely entered via a **maiden name** (e.g. Doris was born a **Setter**, married a Hamilton).

## 5. Verify
- Every fact gets a source. Hobbyist data is marked "verify against primary records."
- Discrepancies between app and archive are flagged, not silently resolved.
- Nothing is published for living people without consent.

## 6. Maintain
- Single source of truth: `data/family-tree.json`.
- Every change logged in `docs/research-log.md`.
- Deliverable: `site/index.html` (readable diagram, mobile-first).
