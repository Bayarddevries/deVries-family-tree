# deVries · Spence Family Tree

An expanding, source-backed family tree for **Bayard deVries**, tracing his Métis lineage back to the Spence family of Red River (Winnipeg), with all available open-source data, images, stories, and sources.

**Owner:** Bayard deVries · **Focus:** Métis lineage, Red River → Winnipeg (with a Flin Flon migration)

---

## Vision

Build an **expanding family tree** assembled from all available open-source records — genealogical indexes, census, scrip, parish registers, archival photos, and family oral history — presented as a clean, readable, mobile-first diagram, with every fact tied to a source and clearly marked for verification.

## Current status

The **direct maternal line** is confirmed end-to-end (see tree below). The tree is now being expanded into a full family view (siblings, spouses, descendants of each generation) and a paternal deVries branch.

```
Bayard deVries
└─ Tracy Diane Lau ⚭ Bryon deVries        (parents)
   └─ Robert Lau ⚭ Mavis Hamilton          (maternal grandparents)
      └─ Doris Alberta Setter ⚭ Lawrence D. Hamilton
         └─ Allan Setter ⚭ Ella Alberta Riggs   ← two Spence lines converge here
            ├─ (Setter)  George Setter → Andrew Setter ⚭ Margaret 'Peggy' Spence
            └─ (Riggs)   Ernest C. Riggs ⚭ Mary Ann Spence → David Spence (MLA) + Catherine Hallett
               ⚑ Métis root: James Spence Sr (c1753-1795) ⚭ Margaret 'Nestichio' Batt (1757-1829)
```

## Key insight

Both Spence branches descend from the **same root**: James Spence Sr + Margaret 'Nestichio' Batt. The two lines re-converge at Allan Setter + Ella Alberta Riggs — a common Red River Métis endogamy pattern. Notable connections: **David Spence** (Manitoba MLA, 1870-74) and **Premier John Norquay** (Manitoba's first Métis premier, via Elizabeth Setter).

## Repository structure

```
deVries-family-tree/
├── README.md            ← you are here
├── data/
│   └── family-tree.json ← single source of truth (edit this to grow the tree)
├── docs/
│   ├── plan.md          ← vision + build plan (reviewed by deepseek agent)
│   ├── research-log.md  ← chronological research notes
│   ├── sources.md       ← all sources, with links + verification status
│   ├── methodology.md   ← how we research and verify
│   └── gaps.md          ← open items / to-verify
└── site/
    └── index.html       ← the family tree diagram (deliverable)
```

## How to grow the tree

1. Edit `data/family-tree.json` to add people/generations.
2. Update the visual tree (`site/index.html`).
3. Log the change + source in `docs/research-log.md`.
4. Verify against primary records (scrip, census, parish, vital stats) before final publication.
5. Commit to git.

## Guardrails

- **Never fabricate** a name, date, marriage, or family link. Only report what a source actually shows, with the source cited.
- Hobbyist/family-tree data (redriverancestry, Ancestry, WikiTree) = "verify against primary records," never confirmed.
- Never publish living people's details.
- App/tree dates that conflict with archives are flagged, not silently preferred.
