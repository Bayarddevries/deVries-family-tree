#!/usr/bin/env python3
"""layout_auto.py — generation-layered auto-layout for the family tree.

Replaces the hand-authored coordinate section of build_tree.py. Derives every
position and every connector from the union graph, so:

  * rows = generation from Bayard (ancestors up, descendants down)
  * every parent -> child connector spans exactly one generation (no skipping)
  * in-law and converging families connect at their real marriage, as rails
    drawn to the spouse's actual box in the descendant union
  * each generation row is packed compactly, ordered by barycenter so connected
    couples sit adjacent (short rails, no empty gaps)

Returns (PERS, FAMS, TEDGES) in the same shape build_tree.py's renderer expects:
  PERS  : [{id,pid,x,y,w,h,you}]
  FAMS  : [{u,s1,s2,s1x,s2x,x,y,children:[(child_nid, child_cx)]}]
  TEDGES: []  (convergence/in-law handled by the parent->child rails)
"""
from collections import defaultdict, deque

P_W, P_H = 116, 54
GAP2 = 16          # gap between spouses (marriage bar spans this)
ROW_H = 140
GAP_BOX = 36       # horizontal gap between units in a row
BAYARD = "P050"


def auto_layout(UNIONS, PEOPLE, box_w=None, p_w=P_W, p_h=P_H, row_h=ROW_H,
                gap2=GAP2, gap_box=GAP_BOX, collapse=None, collapse_children=None):
    by_union = {u["id"]: u for u in UNIONS}
    collapse = collapse or {}
    collapse_children = collapse_children or {}  # {union_id: [child_pid,...] -> collapse into summary_pid}
    if box_w is None:
        box_w = lambda pid: 210 if PEOPLE.get(pid, {}).get("group") else p_w
    eff_children = {u["id"]: ([collapse[u["id"]]] if u["id"] in collapse
                               else list(u.get("children", [])))
                    for u in UNIONS}
    # For unions in collapse_children, replace listed children with their summary pid
    for uid, spec in collapse_children.items():
        if uid in eff_children:
            children = eff_children[uid]
            # Remove listed children and add summary pid
            eff_children[uid] = [c for c in children if c not in spec[0]] + [spec[1]]

    # ---- parent-of / spouse-of maps ----
    parent_union_of = {}              # pid -> the union where pid is a child
    for u in UNIONS:
        for c in eff_children[u["id"]]:
            parent_union_of[c] = u["id"]
    spouse_of = defaultdict(list)     # pid -> unions where pid is a spouse
    for u in UNIONS:
        spouse_of[u["spouse1"]].append(u["id"])
        spouse_of[u["spouse2"]].append(u["id"])

    # ---- generation layering from Bayard (gens grow downward) ----
    pgen, ugen = {}, {}
    dq = deque([BAYARD]); seen = {BAYARD}; pgen[BAYARD] = 0
    NEG = -10 ** 9
    while dq:
        p = dq.popleft(); g = pgen[p]
        if p in parent_union_of:                      # p is a child -> its parents
            u = parent_union_of[p]
            ugen[u] = max(ugen.get(u, NEG), g + 1)
            for sp in (by_union[u]["spouse1"], by_union[u]["spouse2"]):
                pgen[sp] = max(pgen.get(sp, NEG), g + 1)
                if sp not in seen: seen.add(sp); dq.append(sp)
        for u in spouse_of[p]:                        # p is a spouse -> marriages + kids
            ugen[u] = max(ugen.get(u, NEG), g)
            for sp in (by_union[u]["spouse1"], by_union[u]["spouse2"]):
                pgen[sp] = max(pgen.get(sp, NEG), g)
                if sp not in seen: seen.add(sp); dq.append(sp)
            for c in eff_children[u]:
                pgen[c] = max(pgen.get(c, NEG), g - 1)
                if c not in seen: seen.add(c); dq.append(c)
    for u in UNIONS:                                  # stragglers (safety)
        ugen.setdefault(u["id"], 0)
        for sp in (u["spouse1"], u["spouse2"]): pgen.setdefault(sp, 0)
        for c in eff_children[u["id"]]: pgen.setdefault(c, ugen[u["id"]] - 1)
    max_gen = max(ugen.values())
    y_of = lambda g: (max_gen - g) * row_h

    def leaf_children(u):
        return [c for c in eff_children[u]
                if not any(c in (v["spouse1"], v["spouse2"])
                           for v in UNIONS if v["id"] != u)]

    # ---- units: one per couple + one per leaf box; connected by parent<->child ----
    unit_of_couple = {}
    for u in UNIONS:
        unit_of_couple[u["id"]] = {"kind": "couple", "key": ("c", u["id"]),
                                   "row": ugen[u["id"]], "w": 2 * p_w + gap2,
                                   "neighbors": set()}
    unit_of_leaf = {}
    for u in UNIONS:
        for c in leaf_children(u["id"]):
            unit_of_leaf[(u["id"], c)] = {"kind": "leaf", "key": ("l", u["id"], c),
                                          "row": ugen[u["id"]] - 1, "w": box_w(c),
                                          "neighbors": set()}
    def _link(a, b):
        a["neighbors"].add(id(b)); b["neighbors"].add(id(a))
    for uid, unit in unit_of_couple.items():
        uu = by_union[uid]
        for sp in (uu["spouse1"], uu["spouse2"]):
            if sp in parent_union_of and parent_union_of[sp] != uid:
                _link(unit, unit_of_couple[parent_union_of[sp]])
        for c in eff_children[uid]:
            target = next((v for v in spouse_of[c] if v != uid), None)
            if target and target in unit_of_couple:
                _link(unit, unit_of_couple[target])
            elif (uid, c) in unit_of_leaf:
                _link(unit, unit_of_leaf[(uid, c)])

    # ---- barycenter ordering within each generation row ----
    byrow = defaultdict(list)
    for unit in list(unit_of_couple.values()) + list(unit_of_leaf.values()):
        byrow[unit["row"]].append(unit)
    def _positions():
        return {id(un): i for g in sorted(byrow) for i, un in enumerate(byrow[g])}
    def _sort_row(g):
        pos = _positions()
        def bary(un):
            ns = [pos[n] for n in un["neighbors"] if n in pos]
            return (sum(ns) / len(ns)) if ns else 1e9
        byrow[g].sort(key=lambda un: (bary(un), un["key"]))
    for _ in range(10):
        for g in sorted(byrow): _sort_row(g)          # top-down
        for g in sorted(byrow, reverse=True): _sort_row(g)   # bottom-up

    # ---- compact x assignment: each row centered in the widest row's span ----
    maxw = max(sum(un["w"] for un in byrow[g]) + gap_box * (len(byrow[g]) - 1)
               for g in byrow)
    x_of = {}
    for g in sorted(byrow):
        roww = sum(un["w"] for un in byrow[g]) + gap_box * (len(byrow[g]) - 1)
        xcur = (maxw - roww) / 2
        for un in byrow[g]:
            x_of[id(un)] = xcur + un["w"] / 2
            xcur += un["w"] + gap_box

    # ---- parent bar centering relaxation ----
    # Each parent bar (couple unit) is shifted toward the mean x of its children.
    # Children who are spouses already sit at their spouse-union bar, so this
    # pulls the parent toward the child's actual position. Damped iteration
    # with overlap constraints prevents collisions. Bidirectional passes (top-down
    # then bottom-up) let convergence propagate through the full tree.
    # Increased from 20->30 iterations and 0.4->0.45 damping to drive ancestral
    # branches (King, Spence line A) closer to their descendants' positions.
    _ITER = 30
    _DAMP = 0.45
    for _relax in range(_ITER):
        for g in sorted(byrow, reverse=True):  # top-down pass
            units = byrow[g]
            ideal = {}
            for un in units:
                if un["kind"] != "couple":
                    continue
                uid_c = un["key"][1]
                child_xs = []
                for c in eff_children[uid_c]:
                    target = next((v for v in spouse_of[c] if v != uid_c), None)
                    if target and target in unit_of_couple:
                        child_xs.append(x_of[id(unit_of_couple[target])])
                    elif (uid_c, c) in unit_of_leaf:
                        child_xs.append(x_of[id(unit_of_leaf[(uid_c, c)])])
                if child_xs:
                    ideal[id(un)] = sum(child_xs) / len(child_xs)
            if not ideal:
                continue
            ordered = sorted(units, key=lambda un: x_of[id(un)])
            for i, un in enumerate(ordered):
                if id(un) not in ideal:
                    continue
                tgt = ideal[id(un)]; cur = x_of[id(un)]
                delta = (tgt - cur) * _DAMP
                left = -1e9
                if i > 0:
                    left = x_of[id(ordered[i-1])] + ordered[i-1]["w"] / 2 + 4
                right = 1e9
                if i < len(ordered) - 1:
                    right = x_of[id(ordered[i+1])] - ordered[i+1]["w"] / 2 - 4
                x_of[id(un)] = max(min(cur + delta, right), left)
        for g in sorted(byrow):  # bottom-up pass
            units = byrow[g]
            ideal = {}
            for un in units:
                if un["kind"] != "couple":
                    continue
                uid_c = un["key"][1]
                child_xs = []
                for c in eff_children[uid_c]:
                    target = next((v for v in spouse_of[c] if v != uid_c), None)
                    if target and target in unit_of_couple:
                        child_xs.append(x_of[id(unit_of_couple[target])])
                    elif (uid_c, c) in unit_of_leaf:
                        child_xs.append(x_of[id(unit_of_leaf[(uid_c, c)])])
                if child_xs:
                    ideal[id(un)] = sum(child_xs) / len(child_xs)
            if not ideal:
                continue
            ordered = sorted(units, key=lambda un: x_of[id(un)])
            for i, un in enumerate(ordered):
                if id(un) not in ideal:
                    continue
                tgt = ideal[id(un)]; cur = x_of[id(un)]
                delta = (tgt - cur) * _DAMP
                left = -1e9
                if i > 0:
                    left = x_of[id(ordered[i-1])] + ordered[i-1]["w"] / 2 + 4
                right = 1e9
                if i < len(ordered) - 1:
                    right = x_of[id(ordered[i+1])] - ordered[i+1]["w"] / 2 - 4
                x_of[id(un)] = max(min(cur + delta, right), left)

    # ---- final overlap resolution: sweep rows, shift right ----
    for g in sorted(byrow):
        ordered = sorted(byrow[g], key=lambda un: x_of[id(un)])
        for i in range(1, len(ordered)):
            prev_right = x_of[id(ordered[i - 1])] + ordered[i - 1]["w"] / 2
            cur_left = x_of[id(ordered[i])] - ordered[i]["w"] / 2
            if cur_left < prev_right + 4:
                shift = prev_right + 4 - cur_left
                for j in range(i, len(ordered)):
                    x_of[id(ordered[j])] += shift

    # ---- place boxes ----
    PERS, FAMS = [], []
    boxid_for = {}                    # (uid, pid) -> nid
    leafbox_for = defaultdict(dict)   # uid -> {pid: nid}
    def person(pid, cx, y, w=None):
        nid = "b" + str(len(PERS))
        PERS.append({"id": nid, "pid": pid, "x": round(cx - (w or p_w) / 2, 1),
                     "y": int(y), "w": w or p_w, "h": p_h, "you": pid == BAYARD})
        return nid
    def place_couple(u, cx):
        uu = by_union[u]; y = y_of(ugen[u])
        n1 = person(uu["spouse1"], cx - (p_w + gap2) / 2, y)
        n2 = person(uu["spouse2"], cx + (p_w + gap2) / 2, y)
        boxid_for[(u, uu["spouse1"])] = n1
        boxid_for[(u, uu["spouse2"])] = n2
        FAMS.append({"u": u, "s1": n1, "s2": n2,
                     "s1x": cx - gap2 / 2, "s2x": cx + gap2 / 2,
                     "x": cx, "y": y, "children": []})
    for uid, unit in unit_of_couple.items():
        place_couple(uid, x_of[id(unit)])
    for (uid, pid), unit in unit_of_leaf.items():
        y = y_of(ugen[uid] - 1); w = box_w(pid)
        nid = person(pid, x_of[id(unit)], y, w)
        leafbox_for[uid][pid] = nid

    # ---- parent->child connectors (from actual box positions) ----
    bybox = {n["id"]: n for n in PERS}
    fam_by_u = {f["u"]: f for f in FAMS}
    for u in UNIONS:
        fam = fam_by_u[u["id"]]; kids = []
        for c in eff_children[u["id"]]:
            target = next((v for v in spouse_of[c] if v != u["id"]), None)
            nid = None
            if target and (target, c) in boxid_for:
                nid = boxid_for[(target, c)]
            elif c in leafbox_for.get(u["id"], {}):
                nid = leafbox_for[u["id"]][c]
            if nid:
                nb = bybox[nid]
                kids.append((nid, round(nb["x"] + nb["w"] / 2, 1)))
        fam["children"] = kids

    return PERS, FAMS, []
