#!/usr/bin/env python3
"""Reproduction indépendante conditionnelle — V19 C4, L=2.

Convention testée : les trajectoires d'une paire doivent avoir des couleurs égales
aux temps t=0,1, uniquement lorsque les deux états comparés sont distincts.
Les contraintes forcées imposent des couleurs différentes lorsque T(u)=T(v)
ou {T(u),T(v)}={u,v}. Les masques projetés codent les couleurs de 0,1,2,3.

Ce script vérifie le témoin à 9 états puis énumère exhaustivement toutes les
extensions du cycle 0->1->2->3->0 pour N=4,...,8.
Il certifie uniquement cette spécification opérationnelle, pas son équivalence
à la définition primaire de V19.
"""
from itertools import combinations, product

WITNESS = (1, 2, 3, 0, 8, 7, 6, 2, 0)
PAIRS = ((0, 1), (0, 2), (1, 8), (0, 7), (0, 6), (4, 5), (1, 4), (0, 4))
TARGETS = (
    frozenset((0, 7, 8, 15)),
    frozenset((0, 5, 10, 15)),
    frozenset((2, 7, 8, 13)),
    frozenset((1, 6, 9, 14)),
    frozenset((0, 3, 4, 7, 8, 11, 12, 15)),
    frozenset((0, 1, 4, 5, 10, 11, 14, 15)),
    frozenset((4, 5, 6, 7, 8, 9, 10, 11)),
    frozenset((2, 3, 6, 7, 8, 9, 12, 13)),
)

def forced_edges(T):
    return tuple((u, v) for u, v in combinations(range(len(T)), 2)
                 if T[u] == T[v] or {T[u], T[v]} == {u, v})

def coherent(T):
    n = len(T)
    if max(sum(1 for x in T if x == j) for j in range(n)) > 2:
        return False
    adj = [[] for _ in range(n)]
    for u, v in forced_edges(T):
        adj[u].append(v)
        adj[v].append(u)
    colors = [-1] * n
    for s in range(n):
        if colors[s] != -1:
            continue
        colors[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if colors[v] == -1:
                    colors[v] = 1 - colors[u]
                    stack.append(v)
                elif colors[v] == colors[u]:
                    return False
    return True

def canonical_set(S):
    # Rotate the WHOLE shadow simultaneously; do not canonicalize each mask
    # independently, which would destroy correlations among masks.
    def rotate(mask, r):
        return sum(((mask >> i) & 1) << ((i + r) % 4) for i in range(4))
    return min(tuple(sorted(rotate(m, r) for m in S)) for r in range(4))

TARGET_CLASSES = tuple(canonical_set(S) for S in TARGETS)
EXPECTED_CANONICAL_TARGETS = (
    (0, 1, 14, 15),
    (0, 5, 10, 15),
    (1, 4, 11, 14),
    (1, 6, 9, 14),
    (0, 1, 2, 3, 12, 13, 14, 15),
    (0, 1, 4, 5, 10, 11, 14, 15),
    (1, 2, 5, 6, 9, 10, 13, 14),
    (1, 3, 4, 6, 9, 11, 12, 14),
)

def all_shadows(T, equality=True):
    n = len(T)
    edges = forced_edges(T)
    pairs = tuple(combinations(range(n), 2))
    requirements = {}
    for p in pairs:
        x, y = p
        req = []
        for _ in range(2):  # t = 0,1 for L=2
            if x != y:
                req.append((x, y))
            x, y = T[x], T[y]
        requirements[p] = req

    shadows = {p: set() for p in pairs}
    for coloring in product((0, 1), repeat=n):
        if any(coloring[u] == coloring[v] for u, v in edges):
            continue
        mask = sum(coloring[i] << i for i in range(4))
        for p, req in requirements.items():
            if all((coloring[u] == coloring[v]) == equality for u, v in req):
                shadows[p].add(mask)
    return shadows

def has_all_targets(T):
    observed = {canonical_set(S) for S in all_shadows(T).values() if S}
    return all(target in observed for target in TARGET_CLASSES)

def main():
    assert TARGET_CLASSES == EXPECTED_CANONICAL_TARGETS, TARGET_CLASSES
    assert len(set(TARGET_CLASSES)) == 8
    assert coherent(WITNESS)
    raw = all_shadows(WITNESS)
    for p, target in zip(PAIRS, TARGETS):
        assert frozenset(raw[p]) == target, (p, raw[p], target)
    print("WITNESS PASS: 8/8 raw masks match under trajectory equalities.")
    raw_inequality = all_shadows(WITNESS, equality=False)
    inequality_matches = sum(
        frozenset(raw_inequality[p]) == target
        for p, target in zip(PAIRS, TARGETS)
    )
    assert inequality_matches == 1, inequality_matches
    print(f"INEQUALITY VARIANT: {inequality_matches}/8 raw masks match (not 0/8).")
    rows = []
    for n in range(4, 9):
        total = coherent_count = 0
        witness = None
        for tail in product(range(n), repeat=n-4):
            T = (1, 2, 3, 0) + tail
            total += 1
            if not coherent(T):
                continue
            coherent_count += 1
            if has_all_targets(T):
                witness = T
                break
        rows.append((n, total, coherent_count, witness is not None))
        print(f"GLOBAL_ENUM N={n}: total={total}, coherent={coherent_count}, "
              f"witness={witness is not None}")
    assert rows == [
        (4, 1, 1, False),
        (5, 5, 5, False),
        (6, 36, 32, False),
        (7, 343, 263, False),
        (8, 4096, 2695, False),
    ], rows
    print("GLOBAL PASS: no witness for N=4,...,8 under this operational specification.")

if __name__ == "__main__":
    main()
