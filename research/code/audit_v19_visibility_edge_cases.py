#!/usr/bin/env python3
"""Targeted adversarial audit of V19 L+2 visibility edge cases.

Enumerates every endofunction extension in the stated finite domain, finds
the three requested edge cases, and compares global/local shadows for every
P4-both-leaves witness plus one witness of each other type.

This is finite falsification, not a general proof.
"""
from itertools import combinations, product


def forced(T):
    return [(u, v) for u, v in combinations(range(len(T)), 2)
            if T[u] == T[v] or {T[u], T[v]} == {u, v}]


def components(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    comp = [-1] * n
    groups = []
    for root in range(n):
        if comp[root] >= 0:
            continue
        k = len(groups)
        stack = [root]
        comp[root] = k
        group = []
        while stack:
            u = stack.pop()
            group.append(u)
            for v in adj[u]:
                if comp[v] < 0:
                    comp[v] = k
                    stack.append(v)
        groups.append(group)
    return comp, groups, adj


def bipartite(n, edges):
    _, _, adj = components(n, edges)
    color = [-1] * n
    for root in range(n):
        if color[root] >= 0:
            continue
        color[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if color[v] < 0:
                    color[v] = 1 - color[u]
                    stack.append(v)
                elif color[v] == color[u]:
                    return False
    return True


def event_nodes(T, pair, L, q):
    nodes = set(range(q))
    a, b = pair
    for _ in range(L):
        nodes.update((a, b))
        a, b = T[a], T[b]
    return nodes


def local_prefix(T, pair, L, q):
    nodes = set(range(q))
    a, b = pair
    for _ in range(L + 3):
        nodes.update((a, b))
        a, b = T[a], T[b]
    return nodes


def shadow(T, pair, L, q, allowed=None):
    n = len(T)
    allowed = set(range(n)) if allowed is None else set(allowed)
    parent = list(range(n))
    rank = [0] * n
    parity = [0] * n
    inconsistent = False

    def find(x):
        if parent[x] != x:
            root, d = find(parent[x])
            parity[x] ^= d
            parent[x] = root
        return parent[x], parity[x]

    def impose(a, b, d):
        nonlocal inconsistent
        ra, xa = find(a)
        rb, xb = find(b)
        if ra == rb:
            if (xa ^ xb) != d:
                inconsistent = True
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
            xa, xb = xb, xa
        parent[rb] = ra
        parity[rb] = xa ^ xb ^ d
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for a, b in forced(T):
        if a in allowed and b in allowed:
            impose(a, b, 1)

    a, b = pair
    for _ in range(L):
        if a != b:
            if a not in allowed or b not in allowed:
                raise AssertionError("local prefix omitted an event endpoint")
            impose(a, b, 0)
        a, b = T[a], T[b]

    if inconsistent:
        return frozenset()
    roots = [find(i) for i in range(q)]
    return frozenset(
        mask for mask in range(1 << q)
        if all(
            roots[i][0] != roots[j][0]
            or (((mask >> i) & 1) ^ ((mask >> j) & 1))
               == (roots[i][1] ^ roots[j][1])
            for i, j in combinations(range(q), 2)
        )
    )


def compare_witness(T, pair, L, q, prefix, label):
    full = shadow(T, pair, L, q)
    local = shadow(T, pair, L, q, prefix)
    if full != local:
        raise AssertionError({
            "kind": "LOCALITY COUNTEREXAMPLE",
            "case": label, "q": q, "N": len(T), "T": T,
            "L": L, "pair": pair, "prefix": sorted(prefix),
            "global_shadow": sorted(full), "local_shadow": sorted(local),
        })


def run():
    counts = {
        "extensions": 0, "coherent": 0,
        "P4_both_leaves_anchors": 0,
        "fixed_I_exactly_one_visible": 0,
        "equalities_cross_forced_components": 0,
    }
    witnesses = {}
    p4_witnesses = []

    for q in range(3, 7):
        cycle = tuple((i + 1) % q for i in range(q))
        for n in range(q, q + 5):
            for tail in product(range(n), repeat=n - q):
                T = cycle + tail
                counts["extensions"] += 1
                edges = forced(T)
                if not bipartite(n, edges):
                    continue
                counts["coherent"] += 1
                cid, groups, adj = components(n, edges)

                for L in (2, 3, 4, 5):
                    for pair in combinations(range(n), 2):
                        R = event_nodes(T, pair, L, q)
                        P = local_prefix(T, pair, L, q)

                        for group in groups:
                            if len(group) != 4:
                                continue
                            degree = {
                                v: sum(w in group for w in adj[v])
                                for v in group
                            }
                            leaves = [v for v in group if degree[v] == 1]
                            if len(leaves) == 2 and all(v in R for v in leaves):
                                counts["P4_both_leaves_anchors"] += 1
                                p4_witnesses.append(
                                    (q, T, L, pair, P)
                                )

                        for u, v in edges:
                            if (T[u] == u and T[v] == v
                                    and ((u in P) != (v in P))):
                                key = "fixed_I_exactly_one_visible"
                                counts[key] += 1
                                witnesses.setdefault(
                                    key, (q, T, L, pair, P)
                                )

                        a, b = pair
                        for _ in range(L):
                            if a != b and cid[a] != cid[b]:
                                key = "equalities_cross_forced_components"
                                counts[key] += 1
                                witnesses.setdefault(
                                    key, (q, T, L, pair, P)
                                )
                            a, b = T[a], T[b]

    assert counts["extensions"] == 25058, counts
    assert counts["coherent"] == 16986, counts
    for key in (
        "P4_both_leaves_anchors",
        "fixed_I_exactly_one_visible",
        "equalities_cross_forced_components",
    ):
        assert counts[key] > 0, (key, counts)

    # Check every occurrence of the P4/two-anchor case; the other two
    # structurally distinct cases are checked on explicit witnesses.
    for q, T, L, pair, P in p4_witnesses:
        compare_witness(T, pair, L, q, P, "P4_both_leaves_anchors")
    for key, witness in witnesses.items():
        q, T, L, pair, P = witness
        compare_witness(T, pair, L, q, P, key)

    print("COUNTS", counts)
    print("P4 witness comparisons", len(p4_witnesses))
    for key, (q, T, L, pair, P) in witnesses.items():
        print("WITNESS", key, {
            "q": q, "N": len(T), "T": T, "L": L,
            "pair": pair, "visible_prefix": sorted(P),
        })
    print("PASS: no mismatch in all P4/two-anchor witnesses and the two other targeted witnesses.")
    print("PASS: all three adversarial edge cases occurred.")
    print("Scope: finite exact enumeration only; no general theorem or Lean certification.")


if __name__ == "__main__":
    run()
