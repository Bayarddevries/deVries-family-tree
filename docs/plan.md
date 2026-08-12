# Plan & Vision — deVries · Spence Family Tree

> Status: DRAFT — pending review by deepseek agent.

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
- **Phase 2 (next):** Rebuild `site/index.html` as a **full family tree** — direct spine + collapsible sibling/descendant branches at each generation, driven by `data/family-tree.json`. Add the Norquay highlight, David Spence portrait, and photo slots.
- **Phase 3:** Research pass — pin the Setter bridge generations, confirm Doris's birth mother, locate the Setter→Hamilton marriage (likely SK), pull scrip/census. Add descendants of collateral branches where public.
- **Phase 4:** Stories + media — Red River historical context, family photos/stories from Bayard's relatives; wire images into the tree.
- **Phase 5:** Paternal deVries branch (with family input).

## Deliverables
- `data/family-tree.json` — structured data (single source of truth).
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
