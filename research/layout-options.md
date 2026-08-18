# Family Tree Layout — Options Analysis

Context: deVries·Spence family tree, single-file HTML app, GitHub Pages, mobile-first.
Current state: **157 people / 42 unions**, hand-rolled SVG layout (lines are node-position-based so
connectors are correct, but the hand-placed columnar layout makes families overlap/cross as members
are added — e.g. the Brown and deVries families are visually "mixed up").

HARD CONSTRAINT: the tree has **converging ancestor lines** (two Spence lines meet at the
Alan Setter ⚭ Ella Riggs marriage). Any layout must render both lines flowing into that one marriage
without crashing or dropping a component.

GOAL: a layout that handles **adding new members without breaking the links**.

## History (why this matters)
- Hand-rolled generation-lane layout: rejected ~6 times by the user (invisible/broken connectors,
  marriage bars through boxes, scrambled couples). The current renderer derives line positions from
  actual node positions, fixing connector correctness, but the *placement* is still hand-tuned.
- BALKAN FamilyTree JS (purpose-built genealogy lib): adopted 2026-08-12, then abandoned — it
  crashes or silently drops a component on **converging lines** (pedigree collapse). The only
  workaround is cutting one person's parent link for layout only, which hides the convergence.

## Option 1 — Automatic layered (Sugiyama-style) layout, hand-rolled
- Algorithm: assign each person a generation layer (row); order nodes within layers to minimise
  edge crossings (barycenter heuristic); place couples adjacent, children on rails below. Handle
  the two converging roots as a proper DAG (both lines allowed to merge at the marriage node).
- Rows = generation depth (children below parents, spouses same row, in-law families one row above
  their marriage) — already the project's data model. Child-wrapping compacts wide families.
- Pros: fully automatic — adding a person just re-runs the layout, links always recompute, no
  manual placement. No new dependency. Correct connectors guaranteed (node-based).
- Cons: hardest to implement well; classic layered look may differ from the "bracket" tree the user
  likes; implementation risk (but algorithm is well-documented).

## Option 2 — Purpose-built genealogy library (revisit BALKAN / try family-chart)
- BALKAN FamilyTree JS was already tried; it renders the classic descendant chart with robust
  connectors and built-in pan/zoom/search, but has the convergence (pedigree collapse) limit with a
  hacky parent-link-cut workaround.
- Pros: proven, battle-tested connectors; adding members = add nodes; handles pan/zoom/search for
  free. No layout bugs to maintain.
- Cons: previously abandoned for the convergence crash; the workaround hides the visual convergence
  (may not satisfy "show both Spence lines meeting"); ~414KB lib to inline; less control over the
  exact look. Convergence is a real risk we already hit.

## Option 3 — Focused "ego-tree" view (render a sub-tree, not all 157 at once)
- Instead of one giant canvas, render a focused view around a selected person (their ancestors +
  descendants, a few generations), expandable by tapping. Re-render only that sub-tree.
- Pros: never over-crowded regardless of total size; adding members never breaks a sub-tree layout
  (only a small graph each time); ideal on a phone. Simple per-subtree layout.
- Cons: loses the whole-tree-at-a-glance; different UX (tap to expand); still needs a small layout
  algorithm (but far simpler per sub-tree).

## Option 4 — Harden the current hand-rolled layout
- Apply child-wrapping (stack many children into compact rows), keep node-based connectors, and
  make spacing data-driven so families re-flow on add.
- Pros: preserves current work, incremental, lowest risk to what exists.
- Cons: still hand-rolled and will keep hitting edge cases as it grows; doesn't fundamentally solve
  "automatic layout".

## Key question for the critique
Which option best satisfies: (a) adding members without breaking links, (b) rendering the two
converging Spence lines correctly, (c) mobile-first and single-file, (d) the user's demonstrated
preference for a classic descendant-chart look, and (e) long-term maintainability?
