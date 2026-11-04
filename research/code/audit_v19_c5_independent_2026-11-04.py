#!/usr/bin/env python3
"""Independent direct-coloring audit of V19 C5, L=3.

No DSU/parity-union implementation is used. For each of the 32 possible
cycle colorings, a graph propagation checks whether all forced inequalities
and bad-event equalities can be extended to the remaining states.
"""
from __future__ import annotations
import csv, json, itertools
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CYCLE_T = (1, 2, 3, 4, 0)
PAIR_IN = HERE / "V19_PAIR_WITNESSES_C5O14_2026-10-15.csv"
TRIPLE_IN = HERE / "V19_TRIPLE_WITNESSES_D5_13_2026-10-15.csv"
CLASS_IN = HERE / "V19_ORIENTED14_CLASSES_2026-10-15.csv"
U42_IN = HERE / "V19_UNIVERSAL10_U42_2026-10-15.json"

def transform_mask(mask: int, k: int, reflection: bool = False) -> int:
    sign = -1 if reflection else 1
    out = 0
    for i in range(5):
        j = (sign * i + k) % 5
        if (mask >> i) & 1:
            out |= 1 << j
    return out

def canonical(shadow, dihedral=False):
    return min(
        tuple(sorted(transform_mask(m, k, r) for m in shadow))
        for r in ((False, True) if dihedral else (False,))
        for k in range(5)
    )

def propagate_shadow(nodes, transitions, bad_equalities):
    """Exact projection by trying all cycle colorings and propagating XOR edges."""
    nodes = set(nodes)
    adj = {u: [] for u in nodes}
    defined = set(transitions)
    ordered = sorted(nodes)
    for ix, u in enumerate(ordered):
        if u not in defined:
            continue
        for v in ordered[ix + 1:]:
            if v not in defined:
                continue
            if (transitions[u] == transitions[v]
                    or {transitions[u], transitions[v]} == {u, v}):
                adj[u].append((v, 1))
                adj[v].append((u, 1))
    for u, v in bad_equalities:
        if u != v:
            adj[u].append((v, 0))
            adj[v].append((u, 0))
    result = set()
    for mask in range(32):
        colors = {i: (mask >> i) & 1 for i in range(5)}
        stack = list(range(5))
        consistent = True
        while True:
            while stack and consistent:
                u = stack.pop()
                for v, parity in adj[u]:
                    wanted = colors[u] ^ parity
                    if v in colors:
                        if colors[v] != wanted:
                            consistent = False
                            break
                    else:
                        colors[v] = wanted
                        stack.append(v)
            if not consistent:
                break
            free = next((u for u in nodes if u not in colors), None)
            if free is None:
                break
            colors[free] = 0
            stack = [free]
        if consistent:
            result.add(mask)
    return frozenset(result)

def local_shadow(A, B, F):
    nodes = set(A) | set(B) | set(range(5))
    eqs = [(A[t], B[t]) for t in range(3)]
    return propagate_shadow(nodes, F, eqs)

def global_shadow(T, pair):
    A, B = pair
    a, b = A, B
    eqs = []
    for _ in range(3):
        eqs.append((a, b))
        a, b = T[a], T[b]
    return propagate_shadow(range(len(T)), dict(enumerate(T)), eqs)

def coherent(T):
    n = len(T)
    adj = [[] for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if T[u] == T[v] or {T[u], T[v]} == {u, v}:
                adj[u].append(v)
                adj[v].append(u)
    color = {}
    for s in range(n):
        if s in color:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                want = 1 - color[u]
                if v in color:
                    if color[v] != want:
                        return False
                else:
                    color[v] = want
                    stack.append(v)
    return True

def generate_local_diagrams(depth=5):
    """Canonical first-appearance enumeration of two functional trajectories."""
    out = []
    for a0 in range(6):
        max0 = max(4, a0)
        for b0 in range(max0 + 2):
            F = {i: (i + 1) % 5 for i in range(5)}
            def rec(t, A, B, f, max_label):
                if t == depth:
                    if A[0] != B[0]:
                        out.append((tuple(A), tuple(B), dict(f)))
                    return
                u, v = A[-1], B[-1]
                a_choices = [f[u]] if u in f else range(max_label + 2)
                for an in a_choices:
                    f1 = dict(f)
                    if u not in f1:
                        f1[u] = an
                    max1 = max(max_label, an)
                    b_choices = [f1[v]] if v in f1 else range(max1 + 2)
                    for bn in b_choices:
                        f2 = dict(f1)
                        if v not in f2:
                            f2[v] = bn
                        rec(t + 1, A + [an], B + [bn], f2, max(max1, bn))
            rec(0, [a0], [b0], F, max(max0, b0))
    return out

def equation_shadow(equations):
    parsed = []
    for term in equations.split(";"):
        lhs, rhs = term.strip().split("=")
        a, b = lhs.strip().split("+")
        parsed.append((int(a.strip()[1:]), int(b.strip()[1:]), int(rhs.strip())))
    return frozenset(
        m for m in range(32)
        if all((((m >> i) & 1) ^ ((m >> j) & 1)) == r
               for i, j, r in parsed)
    )

def choose_distinct(targets, by_class, preferred):
    order = sorted(range(len(targets)),
                   key=lambda i: (len(by_class.get(targets[i], [])), i))
    chosen = [None] * len(targets)
    used = set()
    def rec(k):
        if k == len(order):
            return True
        i = order[k]
        options = list(by_class.get(targets[i], []))
        options.sort(key=lambda p: (p != preferred[i], p))
        for p in options:
            if p in used:
                continue
            used.add(p)
            chosen[i] = p
            if rec(k + 1):
                return True
            used.remove(p)
            chosen[i] = None
        return False
    return tuple(chosen) if rec(0) else None

def all_pairs_by_class(T, class_map):
    by = defaultdict(list)
    for x in range(len(T)):
        for y in range(x + 1, len(T)):
            S = global_shadow(T, (x, y))
            if not S or len(S) == 32:
                continue
            by[class_map[canonical(S, False)]].append((x, y))
    return by

def main():
    class_rows = list(csv.DictReader(open(CLASS_IN, newline="", encoding="utf-8")))
    pair_rows = list(csv.DictReader(open(PAIR_IN, newline="", encoding="utf-8")))
    triple_rows = list(csv.DictReader(open(TRIPLE_IN, newline="", encoding="utf-8")))
    u42 = json.loads(U42_IN.read_text(encoding="utf-8"))

    diagrams = generate_local_diagrams(5)
    assert len(diagrams) == 3341
    shadows = [local_shadow(A, B, F) for A, B, F in diagrams]
    proper = [s for s in shadows if 0 < len(s) < 32]
    d5_classes = {canonical(s, True) for s in proper}
    c5_classes = {canonical(s, False) for s in proper}
    assert len(proper) == 510
    assert len(d5_classes) == 13
    assert len(c5_classes) == 14
    assert Counter(map(len, d5_classes)) == Counter({4: 4, 8: 5, 16: 4})
    assert Counter(map(len, c5_classes)) == Counter({4: 4, 8: 6, 16: 4})

    c5_id, d5_id, c5_to_d5 = {}, {}, {}
    for row in class_rows:
        ckey = canonical(equation_shadow(row["canonical_equations"]), False)
        dkey = canonical(equation_shadow(row["canonical_equations"]), True)
        cid, did = row["c5_class_id"], row["d5_class_id"]
        c5_id[ckey], d5_id[dkey], c5_to_d5[cid] = int(cid.split("-")[1]), int(did.split("-")[1]), did
    assert set(c5_id) == c5_classes and set(d5_id) == d5_classes
    d5_groups = defaultdict(set)
    for cid, did in c5_to_d5.items():
        row = next(r for r in class_rows if r["c5_class_id"] == cid)
        d5_groups[did].add(canonical(equation_shadow(row["canonical_equations"]), False))
    assert sorted(len(v) for v in d5_groups.values()) == [1] * 12 + [2]
    split = [did for did, values in d5_groups.items() if len(values) == 2]
    assert split == ["D5-06"]
    assert {r["c5_class_id"] for r in class_rows if r["is_chiral_split_member"] == "yes"} == {"C5O-06", "C5O-09"}

    pair_cache, pair_fixed, pair_repairs = {}, [], []
    for idx, row in enumerate(pair_rows):
        T = tuple(json.loads(row["T"]))
        assert len(T) == int(row["n_states"]) and T[:5] == CYCLE_T and coherent(T)
        targets = [int(row["class_a"].split("-")[1]), int(row["class_b"].split("-")[1])]
        prefs = [tuple(json.loads(row["pair_a"])), tuple(json.loads(row["pair_b"]))]
        for p, target in zip(prefs, targets):
            assert c5_id[canonical(global_shadow(T, p), False)] == target
        if T not in pair_cache:
            pair_cache[T] = all_pairs_by_class(T, c5_id)
        chosen = choose_distinct(targets, pair_cache[T], prefs)
        assert chosen is not None
        if chosen != tuple(prefs):
            pair_repairs.append({"row": idx, "classes": [row["class_a"], row["class_b"]], "old_pairs": prefs, "new_pairs": chosen})
        new = dict(row)
        new["pair_a"], new["pair_b"] = json.dumps(list(chosen[0])), json.dumps(list(chosen[1]))
        pair_fixed.append(new)
        assert chosen[0] != chosen[1]
        for p, target in zip(chosen, targets):
            assert c5_id[canonical(global_shadow(T, p), False)] == target

    triple_cache, triple_fixed, triple_repairs = {}, [], []
    oriented_triples_from_d5 = set()
    for idx, row in enumerate(triple_rows):
        T = tuple(json.loads(row["T"]))
        assert len(T) == int(row["n_states"]) and T[:5] == CYCLE_T and coherent(T)
        cols, pair_cols = ("class_a", "class_b", "class_c"), ("pair_a", "pair_b", "pair_c")
        targets = [int(row[c].split("-")[1]) for c in cols]
        prefs = [tuple(json.loads(row[c])) for c in pair_cols]
        actual_oriented = []
        for p, col in zip(prefs, cols):
            S = global_shadow(T, p)
            assert S and len(S) < 32
            actual_oriented.append(c5_id[canonical(S, False)])
            assert d5_id[canonical(S, True)] == targets[len(actual_oriented)-1]
        oriented_triples_from_d5.add(tuple(sorted(actual_oriented)))
        if T not in triple_cache:
            triple_cache[T] = all_pairs_by_class(T, c5_id)
        d5_by = defaultdict(list)
        for x in range(len(T)):
            for y in range(x + 1, len(T)):
                S = global_shadow(T, (x, y))
                if S and len(S) < 32:
                    d5_by[d5_id[canonical(S, True)]].append((x, y))
        chosen = choose_distinct(targets, d5_by, prefs)
        assert chosen is not None
        if chosen != tuple(prefs):
            triple_repairs.append({"row": idx, "classes": [row[c] for c in cols], "old_pairs": prefs, "new_pairs": chosen})
        new = dict(row)
        for col, p in zip(pair_cols, chosen):
            new[col] = json.dumps(list(p))
        triple_fixed.append(new)
        assert len(set(chosen)) == 3
        for p, target in zip(chosen, targets):
            assert d5_id[canonical(global_shadow(T, p), True)] == target

    assert len(pair_rows) == 105 and len(triple_rows) == 455
    assert len({tuple(sorted((int(r["class_a"].split("-")[1]), int(r["class_b"].split("-")[1])))) for r in pair_rows}) == 105
    assert len({tuple(sorted(int(r[c].split("-")[1]) for c in ("class_a", "class_b", "class_c"))) for r in triple_rows}) == 455

    all_oriented_triples = set(itertools.combinations_with_replacement(range(14), 3))
    missing_oriented = sorted(all_oriented_triples - oriented_triples_from_d5)
    assert len(oriented_triples_from_d5) == 455 and len(missing_oriented) == 105
    assert all(9 in tri for tri in missing_oriented)

    T42 = tuple(u42["T"])
    assert len(T42) == u42["n_states"] == 42 and T42[:5] == CYCLE_T and coherent(T42)
    u42_by, size_counts = defaultdict(list), Counter()
    for x in range(42):
        for y in range(x + 1, 42):
            S = global_shadow(T42, (x, y))
            size_counts[len(S)] += 1
            if S and len(S) < 32:
                u42_by[c5_id[canonical(S, False)]].append((x, y))
    actual_counts = {f"C5O-{i:02d}": len(u42_by[i]) for i in range(14)}
    assert actual_counts == u42["oriented_class_counts"]
    assert min(actual_counts.values()) == u42["minimum_count"] == 10
    assert sum(actual_counts.values()) == 680
    assert size_counts == Counter({16: 500, 8: 140, 4: 40, 32: 40, 0: 141})

    oriented_triples = []
    for tri in sorted(all_oriented_triples):
        chosen, used = [], set()
        for cid in tri:
            p = next(p for p in sorted(u42_by[cid]) if p not in used)
            chosen.append(p)
            used.add(p)
        oriented_triples.append({"class_a": f"C5O-{tri[0]:02d}", "class_b": f"C5O-{tri[1]:02d}",
            "class_c": f"C5O-{tri[2]:02d}", "n_states": 42, "T": json.dumps(list(T42), separators=(",", ":")),
            "pair_a": json.dumps(list(chosen[0])), "pair_b": json.dumps(list(chosen[1])), "pair_c": json.dumps(list(chosen[2]))})
    assert len(oriented_triples) == 560
    for row in oriented_triples:
        ps = [tuple(json.loads(row[c])) for c in ("pair_a", "pair_b", "pair_c")]
        assert len(set(ps)) == 3
        for p, c in zip(ps, ("class_a", "class_b", "class_c")):
            assert c5_id[canonical(global_shadow(T42, p), False)] == int(row[c].split("-")[1])

    def write_csv(path, rows, fields):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    write_csv(HERE / "V19_PAIR_WITNESSES_C5O14_REPAIRED_2026-11-04.csv", pair_fixed, list(pair_fixed[0].keys()))
    write_csv(HERE / "V19_TRIPLE_WITNESSES_D5_13_REPAIRED_2026-11-04.csv", triple_fixed, list(triple_fixed[0].keys()))
    write_csv(HERE / "V19_TRIPLE_WITNESSES_C5O14_U42_2026-11-04.csv", oriented_triples,
              ["class_a","class_b","class_c","n_states","T","pair_a","pair_b","pair_c"])

    report = {"date":"2026-11-04","local_catalogue":{"canonical_diagrams":len(diagrams),"proper_diagrams":len(proper),
        "D5_classes":len(d5_classes),"C5_rotation_classes":len(c5_classes),"unique_chiral_split":split,
        "chiral_C5_classes":["C5O-06","C5O-09"],
        "scope_note":"Local catalogue reproduced; universal reduction to L+2 prefixes relies on primary V19 locality lemma, not re-proved line-by-line here."},
        "archived_pair_witnesses":{"rows":len(pair_rows),"duplicate_pair_rows_repaired":len(pair_repairs),"repairs":pair_repairs},
        "archived_D5_triples":{"rows":len(triple_rows),"duplicate_pair_rows_repaired":len(triple_repairs),"repairs":triple_repairs,
        "orientation_aware_triples_covered":len(oriented_triples_from_d5),"orientation_aware_triples_total":560,
        "orientation_aware_triples_missing":len(missing_oriented),"all_missing_contain_C5O09":True,"missing_oriented_triples":missing_oriented},
        "U42_independent_recheck":{"states":42,"unordered_state_pairs_examined":861,"proper_shadow_pairs":680,
        "shadow_size_counts":dict(size_counts),"oriented_class_counts":actual_counts,"minimum_per_class":min(actual_counts.values()),
        "oriented_triples_constructed":len(oriented_triples),"all_560_oriented_triples_verified":True}}
    (HERE / "AUDIT_V19_C5_INDEPENDENT_2026-11-04.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"local_diagrams":len(diagrams),"proper":len(proper),"D5":len(d5_classes),"C5":len(c5_classes),
        "pair_repairs":len(pair_repairs),"triple_repairs":len(triple_repairs),"U42_counts":actual_counts,
        "U42_oriented_triples":len(oriented_triples),"U42_all_pass":True},ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
