# Plan & Vision — deVries · Spence Family Tree

> Status: ACTIVE — data-model refactored to a person graph (schema v2), build script live. Deepseek review applied (2026-08-12).

## Vision
Build an **expanding, source-backed family tree** for Bayard deVries's Métis lineage, assembled from **all available open-source data, images, stories, and sources**, presented as a clean, readable, mobile-first diagram where every fact is tied to a source and every unverified item is clearly flagged. The tree should keep growing as new records and family knowledge arrive.

## Goals
1. **Complete and correct the direct line** (maternal spine already confirmed).
2. **Expand to a full family view**: siblings, spouses, descendants of each generation (not just the direct line).
3. **Add depth**: images (archival portraits, Ancestry tree photos), stories (Red River era, David Spence's life, the Norquay connection, the Flin Flon migration), and rich source citations.
4. **Start the paternal deVries branch** (needs family input).
5. **Make it maintainable**: JSON single source of truth + readable HTML renderer, so we can keep adding.

## Current confirmed spine
Bayard deVries → Tracy Lau ⚭ Bryon deVries → Robert Lau ⚭ Mavis Hamilton → Doris Setter ⚭ Lawrence D. Hamilton → Allan Setter ⚭ Ella Alberta Riggs → [both Spence roots] → James Spence Sr ⚭ Margaret 'Nestichio' Batt (Métis).

## Build plan
- **Phase 1 (done):** Establish + verify the direct line; scaffold the project; document sources/methodology/gaps.
- **Phase 2 (done):** Data-model refactor to a **person graph** (`data/family-tree.json`, schema v2: unique person IDs, `unions` edges, per-person privacy/metis/highlight fields). **Build script** (`build_tree.py`) generates `site/index.html` from the JSON — single source of truth, no hand-edited HTML, self-contained output.
- **Phase 3 (next):** Research pass — **highest value first**: pull full vital-stats registrations (Allan Setter ⚭ Ella Riggs 1909; Doris Setter birth 1912) to pin the Setter bridge + confirm Doris's mother; then Saskatchewan vital stats for the Setter→Hamilton marriage. Cap collateral branches at name+dates; full detail only on the spine and notable figures (Norquay, David Spence).
- **Phase 4:** Stories + media — Red River historical context, family photos/stories (with consent), wire images into the tree (image fields, base64-embedded at build).
- **Phase 5:** Paternal deVries branch (with family input).

## Deepseek-review guardrails (applied)
- **Data model:** one node per person; a guard warns when adding a person whose ID already exists (endogamy). Never store the same person twice.
- **Endogamy display:** each person rendered once; the second Spence line is shown as a convergence (Allan ⚭ Ella) + the explicit "two paths to the root" list — not redrawn as parallel duplicate cards.
- **Images:** only attach a portrait if the source **identifies** the person; never misidentified or AI-generated likenesses; family photos need consent. Verify licensing (Wikimedia PD-old, LAC, Provincial Archives).
- **Privacy:** keep the repo a **private local artifact** (no remote); never publish living people; gate on the per-person `privacy` field.
- **Accuracy:** every fact needs a source or an explicit "verify" flag; hobbyist data always marked; watch name-collision hazards (multiple James/George Setters, two Halletts).
- **Scope:** collateral branches capped; depth reserved for the spine and notable figures.

## Deliverables
- `data/family-tree.json` — person-graph data (single source of truth).
- `build_tree.py` — JSON → HTML generator.
- `site/index.html` — the readable diagram (mobile-first, self-contained).
- `docs/*` — research log, sources, methodology, gaps.
- Wiki page + research-vault routing for ongoing work.

## Success criteria
- Every person on the tree has a source or an explicit "verify" flag.
- No fabricated facts; hobbyist data always marked.
- Readable on a phone; easy to add new people.
- Living people's details never published.

## Risks / open questions
- Archive access is login/Cloudflare-gated (scrip, census) — need workarounds or user-side pulls.
- The intermediate Setter generations and the Setter→Hamilton marriage are the main gaps.
- Endogamy (the two Spence lines re-converging) can create duplicate/looping entries — renderer must handle it without confusion.
- Scope of "stories": how deep to go (Red River context vs. strictly genealogical) — user preference needed.

## Reviewer questions (for deepseek agent)
1. Is the project structure right for an expanding tree? Any better data model / renderer approach?
2. Are the gaps prioritized correctly? What's the highest-value next research step?
3. How should we handle endogamy (converging lines) in both the data and the display?
4. What's the best way to source images (archival portraits, family photos) legally and accurately?
5. Any risks with scope creep or accuracy we should guard against?
