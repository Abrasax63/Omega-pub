#!/usr/bin/env python3
"""Exhaustive small-model stress test for the V19 locality L+2 lemma.

This is a finite falsification test, not the proof. It fixes a distinguished
3-cycle, enumerates every extension of its transition map up to N=7, retains
exactly the globally coherent forced-constraint graphs, and compares:
  (1) the shadow computed on the full finite system;
  (2) the shadow computed on the cycle plus the two trajectory prefixes
      through time L+2.
No DSU/parity-union code is used.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, product

CYCLE = (1, 2, 0)


def forced_edges(T):
    edges = []
    for u, v in combinations(range(len(T)), 2):
        if T[u] == T[v]:
            edges.append((u, v, "M"))
        elif {T[u], T[v]} == {u, v}:
            edges.append((u, v, "I"))
    return edges


def coherent(T):
    adj = [[] for _ in T]
    for u, v, _ in forced_edges(T):
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
                wanted = 1 - color[u]
                if v in color:
                    if color[v] != wanted:
                        return False
                else:
                    color[v] = wanted
                    stack.append(v)
    return True


def check_component_shapes(T):
    edges = forced_edges(T)
    adj = [[] for _ in T]
    for u, v, _ in edges:
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
        edge_count = sum(1 for u, v, _ in edges
                         if u in component and v in component)
        degrees = [len(adj[u]) for u in component]
        if len(component) > 4 or edge_count != len(component) - 1:
            return False
        if max(degrees, default=0) > 2:
            return False
    return True


def shadow(T, pair, horizon, allowed_nodes=None):
    n = len(T)
    allowed = set(range(n)) if allowed_nodes is None else set(allowed_nodes)
    constraints = []
    for u, v, kind in forced_edges(T):
        if u in allowed and v in allowed:
            constraints.append((u, v, 1))
    a, b = pair
    for _ in range(horizon):
        if a != b:
            if a not in allowed or b not in allowed:
                raise AssertionError("trajectory endpoint missing from local prefix")
            constraints.append((a, b, 0))
        a, b = T[a], T[b]

    adj = {u: [] for u in allowed}
    for u, v, parity in constraints:
        adj[u].append((v, parity))
        adj[v].append((u, parity))

    result = set()
    for mask in range(1 << 3):
        colors = {i: (mask >> i) & 1 for i in range(3)}
        stack = list(range(3))
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
            free = next((u for u in allowed if u not in colors), None)
            if free is None:
                break
            colors[free] = 0
            stack = [free]
        if consistent:
            result.add(mask)
    return result


def local_prefix(T, pair, horizon):
    nodes = {0, 1, 2}
    a, b = pair
    for _ in range(horizon + 3):  # add trajectory states at times 0,...,L+2
        nodes.add(a)
        nodes.add(b)
        a, b = T[a], T[b]
    return nodes


def main():
    expected = {
        3: (1, 1, 6),
        4: (4, 4, 48),
        5: (25, 22, 440),
        6: (216, 164, 4920),
        7: (2401, 1571, 65982),
    }
    totals = {}
    for n in range(3, 8):
        total = coherent_count = comparisons = 0
        for tail in product(range(n), repeat=n - 3):
            T = CYCLE + tail
            total += 1
            if not coherent(T):
                continue
            coherent_count += 1
            if not check_component_shapes(T):
                raise AssertionError(("forced-component counterexample", n, T))
            for horizon in (2, 3):
                for pair in combinations(range(n), 2):
                    prefix = local_prefix(T, pair, horizon)
                    full = shadow(T, pair, horizon)
                    local = shadow(T, pair, horizon, prefix)
                    comparisons += 1
                    if full != local:
                        raise AssertionError({
                            "locality counterexample": {
                                "n": n, "T": T, "horizon": horizon,
                                "pair": pair, "prefix": sorted(prefix),
                                "full_shadow": sorted(full),
                                "local_shadow": sorted(local),
                            }
                        })
        totals[n] = (total, coherent_count, comparisons)
        if totals[n] != expected[n]:
            raise AssertionError(("unexpected enumeration count", n, totals[n]))
    print("PASS — forced components are P1/P2/P3/P4 in every retained system.")
    print("PASS — full and L+2-local shadows agree in every tested case.")
    print("N | extensions | coherent | full/local comparisons")
    for n, values in totals.items():
        print(n, *values, sep=" | ")
    print("TOTAL comparisons:", sum(v[2] for v in totals.values()))


if __name__ == "__main__":
    main()
