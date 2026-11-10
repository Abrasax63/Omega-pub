#!/usr/bin/env python3
"""Independent finite audit of the V19 forced-graph and L+2 locality lemmas.

No imports from the V19 production/audit scripts. All maps T:[n]->[n]
are enumerated directly; shadows are computed by explicit XOR propagation.
"""
from itertools import product, combinations
from collections import Counter


def forced_edges(T):
    return tuple((u, v, 1) for u, v in combinations(range(len(T)), 2)
                 if T[u] == T[v] or {T[u], T[v]} == {u, v})


def components_and_coherence(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v, parity in edges:
        adjacency[u].append((v, parity))
        adjacency[v].append((u, parity))
    color = {}
    components = []
    for start in range(n):
        if start in color:
            continue
        color[start] = 0
        stack = [start]
        vertices = []
        coherent = True
        while stack:
            u = stack.pop()
            vertices.append(u)
            for v, parity in adjacency[u]:
                wanted = color[u] ^ parity
                if v not in color:
                    color[v] = wanted
                    stack.append(v)
                elif color[v] != wanted:
                    coherent = False
        components.append((tuple(vertices), coherent, adjacency))
    return components


def classify_forced_graph(n, T, edges):
    components = components_and_coherence(n, edges)
    if not all(ok for _, ok, _ in components):
        return False, None
    sizes = Counter()
    for vertices, _, adjacency in components:
        V = set(vertices)
        degrees = [sum(v in V for v, _ in adjacency[u]) for u in vertices]
        edge_count = sum(degrees) // 2
        # Connected component must be a path, including the singleton P1.
        assert len(vertices) <= 4
        assert max(degrees, default=0) <= 2
        assert edge_count == len(vertices) - 1
        sizes[len(vertices)] += 1

        internal = [(u, v) for u, v, _ in edges if u in V and v in V]
        I = [(u, v) for u, v in internal if {T[u], T[v]} == {u, v}]
        M = [(u, v) for u, v in internal if T[u] == T[v]]
        assert len(I) <= 1
        assert len(I) + len(M) == len(internal)
        if len(vertices) >= 3:
            assert len(I) == 1
            assert len(M) == len(vertices) - 2
    return True, sizes


def find_cycles(T):
    n = len(T)
    finished = set()
    cycles = set()
    for start in range(n):
        if start in finished:
            continue
        path = []
        position = {}
        u = start
        while u not in position and u not in finished:
            position[u] = len(path)
            path.append(u)
            u = T[u]
        if u in position:
            cycle = tuple(path[position[u]:])
            if len(cycle) >= 3:
                k = cycle.index(min(cycle))
                cycles.add(cycle[k:] + cycle[:k])
        finished.update(path)
    return tuple(sorted(cycles))


def event_equalities(T, pair, horizon):
    a, b = pair
    edges = []
    for _ in range(horizon):
        if a != b:
            edges.append((a, b, 0))
        a, b = T[a], T[b]
    return tuple(edges)


def prefix_vertices(T, pair, horizon, cycle):
    visible = set(cycle)
    # Includes times 0,...,L+2 (L+3 listed states).
    for start in pair:
        u = start
        for _ in range(horizon + 3):
            visible.add(u)
            u = T[u]
    return visible


def projected_shadow(n, constraints, cycle):
    adjacency = [[] for _ in range(n)]
    for u, v, parity in constraints:
        adjacency[u].append((v, parity))
        adjacency[v].append((u, parity))
    result = set()
    for mask in range(1 << len(cycle)):
        colors = {u: (mask >> i) & 1 for i, u in enumerate(cycle)}
        stack = list(cycle)
        consistent = True
        while stack and consistent:
            u = stack.pop()
            for v, parity in adjacency[u]:
                wanted = colors[u] ^ parity
                if v in colors:
                    if colors[v] != wanted:
                        consistent = False
                        break
                else:
                    colors[v] = wanted
                    stack.append(v)
        if consistent:
            result.add(mask)
    return frozenset(result)


def main():
    coherent_total = 0
    coherent_by_n = {}
    path_sizes = Counter()
    locality_maps = {}
    locality_cases = {}

    # Structural theorem: every coherent forced graph is a disjoint union
    # of P1-P4 components.
    for n in range(1, 7):
        coherent_n = 0
        for T in product(range(n), repeat=n):
            edges = forced_edges(T)
            coherent, sizes = classify_forced_graph(n, T, edges)
            if coherent:
                coherent_n += 1
                path_sizes.update(sizes)
        coherent_total += coherent_n
        coherent_by_n[n] = coherent_n

    assert coherent_total == 29742
    assert coherent_by_n == {1: 1, 2: 4, 3: 23, 4: 191, 5: 2069, 6: 27454}
    assert set(path_sizes) == {1, 2, 3, 4}

    # Locality theorem: for all coherent maps n<=6, every cycle q>=3,
    # every unordered pair, and horizons L=2,3, global and L+2-prefix
    # projections agree.
    for n in range(3, 7):
        maps_with_cycle = 0
        cases = 0
        for T in product(range(n), repeat=n):
            forced = forced_edges(T)
            if not all(ok for _, ok, _ in components_and_coherence(n, forced)):
                continue
            cycles = find_cycles(T)
            if not cycles:
                continue
            maps_with_cycle += 1
            for cycle in cycles:
                for pair in combinations(range(n), 2):
                    for horizon in (2, 3):
                        event = event_equalities(T, pair, horizon)
                        global_constraints = forced + event
                        visible = prefix_vertices(T, pair, horizon, cycle)
                        local_constraints = tuple(
                            edge for edge in global_constraints
                            if edge[0] in visible and edge[1] in visible
                        )
                        global_shadow = projected_shadow(n, global_constraints, cycle)
                        local_shadow = projected_shadow(n, local_constraints, cycle)
                        assert global_shadow == local_shadow, (
                            "L+2 counterexample", n, T, cycle, pair, horizon,
                            global_shadow, local_shadow, visible
                        )
                        cases += 1
        locality_maps[n] = maps_with_cycle
        locality_cases[n] = cases

    assert locality_maps == {3: 2, 4: 38, 5: 614, 6: 10384}
    assert locality_cases == {3: 12, 4: 456, 5: 12280, 6: 312720}

    print("FORCED_GRAPH_P1_P4: PASS")
    print("COHERENT_ENDOFUNCTIONS_BY_N: " + repr(coherent_by_n))
    print("COHERENT_ENDOFUNCTIONS_TOTAL: 29742")
    print("COMPONENT_SIZES_P1_P4: " + repr(dict(sorted(path_sizes.items()))))
    print("LOCALITY_L_PLUS_2: PASS")
    print("COHERENT_MAPS_WITH_CYCLE_BY_N: " + repr(locality_maps))
    print("GLOBAL_LOCAL_CASES_BY_N: " + repr(locality_cases))
    print("GLOBAL_LOCAL_CASES_TOTAL: 325468")
    print("NO_COUNTEREXAMPLE_FOUND")
    print("Scope: exhaustive finite checks for n<=6, horizons L=2,3;")
    print("not a substitute for the structural proof or a general theorem.")


if __name__ == "__main__":
    main()
