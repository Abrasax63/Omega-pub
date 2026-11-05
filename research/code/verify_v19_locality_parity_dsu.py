#!/usr/bin/env python3
"""Independent finite stress test of V19 locality using parity union-find.

This implementation is intentionally separate from
verify_v19_locality_exhaustive_small.py: constraints are accumulated with a
parity disjoint-set structure, not graph-colouring propagation.

Scope: distinguished cycles C_q, 3 <= q <= 6; N=q,...,q+3;
horizons L=2,3,4,5; every endofunction extension and every initial pair.
This is a finite falsification test, not a proof for arbitrary q, L, N.
"""
from __future__ import annotations

from itertools import combinations, product


def forced_edges(T):
    return [
        (u, v)
        for u, v in combinations(range(len(T)), 2)
        if T[u] == T[v] or {T[u], T[v]} == {u, v}
    ]


def coherent(T):
    adj = [[] for _ in T]
    for u, v in forced_edges(T):
        adj[u].append(v)
        adj[v].append(u)
    color = {}
    for root in range(len(T)):
        if root in color:
            continue
        color[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v in color:
                    if color[v] == color[u]:
                        return False
                else:
                    color[v] = 1 - color[u]
                    stack.append(v)
    return True


def component_shapes_ok(T):
    edges = forced_edges(T)
    adj = [[] for _ in T]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = set()
    for root in range(len(T)):
        if root in seen:
            continue
        stack = [root]
        seen.add(root)
        component = []
        while stack:
            u = stack.pop()
            component.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        edge_count = sum(u in component and v in component for u, v in edges)
        if (
            len(component) > 4
            or edge_count != len(component) - 1
            or max(len(adj[u]) for u in component) > 2
        ):
            return False
    return True


def shadow_dsu(T, pair, horizon, cycle_size, allowed_nodes=None):
    """Return all cycle colour masks extending the parity constraints."""
    n = len(T)
    allowed = set(range(n)) if allowed_nodes is None else set(allowed_nodes)
    parent = list(range(n))
    rank = [0] * n
    xor_to_parent = [0] * n
    inconsistent = False

    def find(x):
        if parent[x] != x:
            root, parity = find(parent[x])
            xor_to_parent[x] ^= parity
            parent[x] = root
        return parent[x], xor_to_parent[x]

    def impose(u, v, parity):
        nonlocal inconsistent
        ru, xu = find(u)
        rv, xv = find(v)
        if ru == rv:
            if (xu ^ xv) != parity:
                inconsistent = True
            return
        if rank[ru] < rank[rv]:
            ru, rv = rv, ru
            xu, xv = xv, xu
        parent[rv] = ru
        xor_to_parent[rv] = xu ^ xv ^ parity
        if rank[ru] == rank[rv]:
            rank[ru] += 1

    # Forced inequalities have parity 1.
    for u, v in forced_edges(T):
        if u in allowed and v in allowed:
            impose(u, v, 1)

    # The bad-event equalities have parity 0.
    a, b = pair
    for _ in range(horizon):
        if a != b:
            if a not in allowed or b not in allowed:
                raise AssertionError("local prefix omitted a bad-event endpoint")
            impose(a, b, 0)
        a, b = T[a], T[b]

    if inconsistent:
        return frozenset()

    cycle_relations = [find(i) for i in range(cycle_size)]
    return frozenset(
        mask
        for mask in range(1 << cycle_size)
        if all(
            cycle_relations[i][0] != cycle_relations[j][0]
            or (((mask >> i) & 1) ^ ((mask >> j) & 1))
            == (cycle_relations[i][1] ^ cycle_relations[j][1])
            for i, j in combinations(range(cycle_size), 2)
        )
    )


def local_prefix(T, pair, horizon, cycle_size):
    nodes = set(range(cycle_size))
    a, b = pair
    # Include exactly the trajectory states at times 0,...,L+2.
    for _ in range(horizon + 3):
        nodes.update((a, b))
        a, b = T[a], T[b]
    return nodes


EXPECTED = {
    3: [(3, 1, 1, 12), (4, 4, 4, 96), (5, 25, 22, 880), (6, 216, 164, 9840)],
    4: [(4, 1, 1, 24), (5, 5, 5, 200), (6, 36, 32, 1920), (7, 343, 263, 22092)],
    5: [(5, 1, 1, 40), (6, 6, 6, 360), (7, 49, 44, 3696), (8, 512, 398, 44576)],
    6: [(6, 1, 1, 60), (7, 7, 7, 588), (8, 64, 58, 6496), (9, 729, 575, 82800)],
}


def run_cycle(cycle_size):
    cycle = tuple((i + 1) % cycle_size for i in range(cycle_size))
    rows = []
    for n in range(cycle_size, cycle_size + 4):
        extensions = coherent_systems = comparisons = 0
        for tail in product(range(n), repeat=n - cycle_size):
            T = cycle + tail
            extensions += 1
            if not coherent(T):
                continue
            coherent_systems += 1
            if not component_shapes_ok(T):
                raise AssertionError({
                    "kind": "forced-component counterexample",
                    "cycle_size": cycle_size, "n": n, "T": T,
                })
            for horizon in (2, 3, 4, 5):
                for pair in combinations(range(n), 2):
                    prefix = local_prefix(T, pair, horizon, cycle_size)
                    full = shadow_dsu(T, pair, horizon, cycle_size)
                    local = shadow_dsu(T, pair, horizon, cycle_size, prefix)
                    comparisons += 1
                    if full != local:
                        raise AssertionError({
                            "kind": "locality counterexample",
                            "cycle_size": cycle_size, "n": n, "T": T,
                            "horizon": horizon, "pair": pair,
                            "prefix": sorted(prefix),
                            "full_shadow": sorted(full),
                            "local_shadow": sorted(local),
                        })
        row = (n, extensions, coherent_systems, comparisons)
        rows.append(row)
    if rows != EXPECTED[cycle_size]:
        raise AssertionError(("unexpected enumeration counts", cycle_size, rows))
    return rows


def main():
    all_comparisons = 0
    all_extensions = 0
    all_coherent = 0
    print("q | N | extensions | coherent | global/local comparisons")
    for q in range(3, 7):
        for n, extensions, coherent_systems, comparisons in run_cycle(q):
            print(q, n, extensions, coherent_systems, comparisons, sep=" | ")
            all_extensions += extensions
            all_coherent += coherent_systems
            all_comparisons += comparisons
    assert all_extensions == 3040
    assert all_coherent == 2182
    assert all_comparisons == 173680
    print("PASS — all retained forced graphs have components P1/P2/P3/P4.")
    print("PASS — no global/local shadow divergence in the tested finite range.")
    print("TOTAL extensions:", all_extensions)
    print("TOTAL coherent systems:", all_coherent)
    print("TOTAL comparisons:", all_comparisons)


if __name__ == "__main__":
    main()
