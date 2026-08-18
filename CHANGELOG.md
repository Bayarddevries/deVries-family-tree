# Family Tree Changelog & Issues

> Comprehensive log of changes made to the deVries family tree project.
> Last updated: 2026-08-18
> Next agent: read this file first for project state, open issues, and architecture.

## Project Architecture

### Files
- `build_tree.py` — Main build script. Loads `data/family-tree.json`, applies corrections, runs layout, generates `site/index.html`
- `layout_auto.py` — Generation-layered barycenter + damped centroid relaxation layout algorithm
- `add_circular_view.py` — Post-processing script that adds the Circular (radial) view tab to `site/index.html`
- `export_gedcom.py` — Exports build_tree.PEOPLE/UNIONS to GEDCOM format for Gramps import
- `data/family-tree.json` — Original base data (DO NOT modify — corrections are in build_tree.py)
- `data/family-tree.ged` — Generated GEDCOM export for Gramps

### Build Pipeline
```bash
python3 build_tree.py        # -> generates site/index.html (177KB)
python3 add_circular_view.py # -> adds Circular view tab (now integrated into build_tree.py)
```
`build_tree.py` now automatically calls `add_circular_view.py` as a post-processing step.

### Deployment
- GitHub Pages: https://bayarddevries.github.io/deVries-family-tree/
- Branch: `gh-pages` (built from `site/index.html`)
- Old Netlify sites are deprecated (credit exhaustion)

### Data Structures
- **UNIONS**: `data/family-tree.json` uses `spouse1`/`spouse2` keys; `build_tree.py` does NOT transform these (the layout_auto works with `spouse1`/`spouse2`)
- **TREE dict**: Contains `nodes` (PERS), `fams` (FAMS), `edges` (TEDGES), `lanes`, `pw`, `ph`, `rowh`, `faclass`, `w`, `h`
- **People PIDs**: P001-P159 (base), P92-P128 (additions), P900-P902 (group summaries), P050=Bayard (root)

## Changes Made

### Phase 1: Data Corrections (2026-08-18)

#### Removed non-essential unions from tree layout
- **U22 removed** (Sarah Fowler + Isaac Batt): Sarah stayed in England; Métis line descends from Batt's Cree family, not hers. Sarah Fowler (P96) kept in PEOPLE for People tab.
- **U03 removed** (George Setter + Isabella Kennedy): George remarried Jessie Ellen Campbell; Isabella's children (P020/P021/P022) are non-ancestral collateral. Removing U03 eliminates the duplicate George Setter node. Children kept in PEOPLE but not placed in tree.

#### Collapsed Setter collateral children
- **P902 created**: Summary box for George Setter + Jessie Ellen Campbell's 5 non-ancestral children (P023, P024, P026, P027, P028)
- Added `COLLAPSE_CHILDREN` mechanism in `layout_auto.py` — unlike `COLLAPSE` (which replaces ALL children of a union), this selectively collapses specific children while keeping ancestral ones
- **Impact**: George Setter moved from x=4506 to x=3374 (closer to descendant Roderick at x=3255)

### Phase 2: Organic Earthy Visualization (2026-08-18)

#### CSS Earthy Palette
- Added earthy CSS variables: `--earth-umber`, `--earth-sienna`, `--earth-forest`, `--earth-ochre`, `--earth-terracotta`, `--earth-moss`, `--earth-stone`, `--earth-clay`

#### Family-Line Color Coding
- Created `FAMILY_CLASS` dict in `build_tree.py` mapping each person PID to a family-line CSS class:
  - `fl-setter` (umber) — Line A: James Spence → Peggy → Andrew → George → Roderick → Alan
  - `fl-riggs` (sienna) — Line B: David Spence → Mary Ann → Ernest → Ella
  - `fl-spence` (forest green) — David Spence (MLA) + Catherine Hallett
  - `fl-hamilton` (forest green) — Joseph → John James → Guy → Lawrence → Doris
  - `fl-hallett` (terracotta) — Henry Hallett family
  - `fl-hourie` (moss) — John Hourie + Margaret Bird
  - `fl-king` (ochre) — William King → Thomas Allan → Ethel
  - `fl-devries` (stone) — Gerhard → Leewe → Engbertus
  - `fl-bayard` (crimson) — Central person, pulses gently
  - `fl-grp` (gold) — Collapsed group summary boxes
  - `fl-inlaw` (muted) — Spouses married into tree
  - `fl-stone` (muted) — Default for unclassified

#### Per-Family-Line Pulse Animations
- Added `@keyframes pulseSetter`, `pulseRiggs`, `pulseHamilton`, etc. — each with family-line-specific glow color
- Staggered timing (6-10s duration, different phase offsets) for organic, breathing effect
- Child connectors colored per family line via JavaScript `lineC(pid)` function

#### Marriage Bar Colors
- Changed from purple (`#A99BD9`) to earthy ochre (`#C9A66F`)
- Changed child connector default from `url(#lg)` gradient to earthy brown (`#6B5E52`)

#### Circular View Earthy Colors
- Updated `add_circular_view.py` CSS: replaced neon cyan (`#5af0ff`) and gold (`#f4c95d`) with earthy tones
  - Edges: `#8B7355` (umber) glow, `#FFFFFF` core at reduced opacity
  - Marriage lines: `#D4A853` (gold) dashed
  - Direct line connectors: `#A66E4E` (sienna)
  - Nodes: `#D4B896` stroke, `#9DB4C0` root fill with `#C9A66F` (ochre) accent

### Phase 3: Build Pipeline Integration (2026-08-18)

#### Integrated circular view into build
- Added `subprocess.run([sys.executable, "add_circular_view.py"])` call at end of `build_tree.py`
- Added `import sys` to `build_tree.py`

## Known Bugs / Issues

### 1. FAMILY_LINES Return Bug (FIXED)
- **Description**: `_build_family_lines()` function had a `lines` dict (only with P050) and a `trunk` dict (with all family-line PIDs). The function accidentally returned `lines` instead of `trunk`, causing all family-line classes to default to `fl-stone`.
- **Fix**: Changed `return lines` to `return trunk`, and added `"P050": "bayard"` to the trunk dict.
- **Status**: FIXED

### 2. Layout Convergence: Andrew Setter Gap
- **Description**: Andrew Setter (P007) at x=1826 is ~1548px from his son George Setter (P010) at x=3374. The barycenter + damped relaxation algorithm converges to a local minimum where the barycenter ordering locks Andrew far left.
- **Root cause**: The barycenter ordering places nodes by connectivity, and the overlap resolution constrains movement within neighbor boundaries. The relaxation has already converged at 30-40 iterations — more iterations don't help.
- **Proposed fix**: Seed the relaxation with child centroids instead of compact left-to-right packing. OR accept this as inherent to the barycenter approach and rely on the Circular view for clean visualization.
- **Status**: OPEN — cosmetic issue in traditional view

### 3. Subagent Rate Limit (HTTP 429)
- **Description**: A background subagent trying to explain Gramps' layout approach failed with HTTP 429 (rate limit). Could not retrieve its findings.
- **Status**: OPEN — need to retry the Gramps research separately

### 4. Circular View JS Bug
- **Description**: In `add_circular_view.py` line 123: `downward(ROOT,'P050'||ROOT)` — this is a no-op (truthy string OR), doesn't actually start from root's spouse unions. Should be `downward(ROOT, ROOT)` or just removed.
- **Status**: OPEN — cosmetic, doesn't affect rendering

## Open Questions

1. Should the Circular view become the DEFAULT view (tab 1 instead of after Traditional)?
2. The `radial/build.py` file in `radial/` directory is git-ignored but may contain newer circular layout logic — check if it's been updated.
3. The `--gold` CSS variable (`#D4A853`) is still used for UI buttons — should these also shift to earthy palette?

## File Locations on Disk

- Working dir: `/home/bayard_devries/projects/deVries-family-tree/`
- Build script: `build_tree.py` (1617 lines)
- Layout algorithm: `layout_auto.py` (258 lines, original barycenter)
- Circular view: `add_circular_view.py` (315 lines)
- GEDCOM export: `export_gedcom.py` (lines unknown)
- Output: `site/index.html` (177,730 bytes)
