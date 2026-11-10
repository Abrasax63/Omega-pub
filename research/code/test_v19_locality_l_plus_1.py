#!/usr/bin/env python3
"""Independent exhaustive test of the L+1 prefix against the global shadow.

Prefix convention: states at times 0,...,L+1 (L+2 states).
No imports from prior V19 scripts.
"""
from itertools import product, combinations


def forced_edges(T):
    return tuple((u, v, 1) for u, v in combinations(range(len(T)), 2)
                 if T[u] == T[v] or {T[u], T[v]} == {u, v})


def coherent(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, p in edges:
        adj[u].append((v, p)); adj[v].append((u, p))
    colors = {}
    for root in range(n):
        if root in colors:
            continue
        colors[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v, p in adj[u]:
                wanted = colors[u] ^ p
                if v not in colors:
                    colors[v] = wanted; stack.append(v)
                elif colors[v] != wanted:
                    return False
    return True


def cycles(T):
    done, found = set(), set()
    for start in range(len(T)):
        if start in done:
            continue
        path, pos, u = [], {}, start
        while u not in pos and u not in done:
            pos[u] = len(path); path.append(u); u = T[u]
        if u in pos:
            cyc = tuple(path[pos[u]:])
            if len(cyc) >= 3:
                k = cyc.index(min(cyc))
                found.add(cyc[k:] + cyc[:k])
        done.update(path)
    return tuple(sorted(found))


def event_edges(T, pair, L):
    a, b = pair
    out = []
    for _ in range(L):
        if a != b:
            out.append((a, b, 0))
        a, b = T[a], T[b]
    return tuple(out)


def visible_l_plus_1(T, pair, L, cycle):
    visible = set(cycle)
    for start in pair:
        u = start
        for _ in range(L + 2):  # exactly times 0,...,L+1
            visible.add(u)
            u = T[u]
    return visible


def projected_shadow(n, constraints, cycle):
    adj = [[] for _ in range(n)]
    for u, v, p in constraints:
        adj[u].append((v, p)); adj[v].append((u, p))
    shadow = set()
    for mask in range(1 << len(cycle)):
        colors = {v: (mask >> i) & 1 for i, v in enumerate(cycle)}
        stack, ok = list(cycle), True
        while stack and ok:
            u = stack.pop()
            for v, p in adj[u]:
                wanted = colors[u] ^ p
                if v in colors:
                    if colors[v] != wanted:
                        ok = False; break
                else:
                    colors[v] = wanted; stack.append(v)
        if ok:
            shadow.add(mask)
    return frozenset(shadow)


def main():
    coherent_by_n = {}
    cycle_maps_by_n = {}
    comparisons_by_n = {}
    total = 0

    for n in range(1, 7):
        coherent_by_n[n] = sum(
            coherent(n, forced_edges(T))
            for T in product(range(n), repeat=n)
        )

    assert coherent_by_n == {1: 1, 2: 4, 3: 23, 4: 191, 5: 2069, 6: 27454}

    for n in range(3, 7):
        cycle_maps = comparisons = 0
        for T in product(range(n), repeat=n):
            F = forced_edges(T)
            if not coherent(n, F):
                continue
            cs = cycles(T)
            if not cs:
                continue
            cycle_maps += 1
            for B in cs:
                for pair in combinations(range(n), 2):
                    for L in (2, 3):
                        E = F + event_edges(T, pair, L)
                        visible = visible_l_plus_1(T, pair, L, B)
                        local = tuple(e for e in E
                                      if e[0] in visible and e[1] in visible)
                        global_shadow = projected_shadow(n, E, B)
                        local_shadow = projected_shadow(n, local, B)
                        comparisons += 1
                        if global_shadow != local_shadow:
                            raise AssertionError({
                                "counterexample": True, "n": n, "T": T,
                                "cycle": B, "pair": pair, "L": L,
                                "global_shadow": sorted(global_shadow),
                                "local_shadow": sorted(local_shadow),
                                "visible_prefix": sorted(visible),
                            })
        cycle_maps_by_n[n] = cycle_maps
        comparisons_by_n[n] = comparisons
        total += comparisons

    assert cycle_maps_by_n == {3: 2, 4: 38, 5: 614, 6: 10384}
    assert comparisons_by_n == {3: 12, 4: 456, 5: 12280, 6: 312720}
    assert total == 325468

    print("L_PLUS_1_EXHAUSTIVE_TEST: PASS")
    print("PREFIX_CONVENTION: times 0,...,L+1")
    print("COHERENT_ENDOFUNCTIONS_BY_N:", coherent_by_n)
    print("COHERENT_CYCLE_MAPS_BY_N:", cycle_maps_by_n)
    print("GLOBAL_LOCAL_COMPARISONS_BY_N:", comparisons_by_n)
    print("GLOBAL_LOCAL_COMPARISONS_TOTAL:", total)
    print("NO_COUNTEREXAMPLE_FOUND")
    print("Scope: n<=6 and L in {2,3}; this does not prove universal L+1 sufficiency.")


if __name__ == "__main__":
    main()
