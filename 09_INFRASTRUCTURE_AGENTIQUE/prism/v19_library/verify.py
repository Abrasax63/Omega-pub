"""Compute projected binary shadows with parity union-find over all components."""

from itertools import combinations, product


def shadow(n, constraints, cycle):
    parent = list(range(n))
    xor = [0] * n

    def find(node):
        parity = 0
        while parent[node] != node:
            parity ^= xor[node]
            node = parent[node]
        return node, parity

    for u, v, required in constraints:
        a, pu = find(u)
        b, pv = find(v)
        link = pu ^ pv ^ required
        if a == b:
            if link:
                return frozenset()
        else:
            parent[a], xor[a] = b, link

    roots = [find(v) for v in cycle]
    free = sorted({root for root, _ in roots})
    return frozenset(
        sum((assignment[root] ^ parity) << i for i, (root, parity) in enumerate(roots))
        for values in product((0, 1), repeat=len(free))
        for assignment in (dict(zip(free, values)),)
    )


def search(historical, max_n=6):
    counts = {}
    semantic_difference = None
    for n in range(3, max_n + 1):
        counts[n] = 0
        for T in product(range(n), repeat=n):
            forced = [(u, v, 1) for u, v in combinations(range(n), 2)
                      if T[u] == T[v] or (T[u], T[v]) in ((u, v), (v, u))]
            if not shadow(n, forced, ()):
                continue
            for cycle in historical.cycles(T):
                for pair in combinations(range(n), 2):
                    for L in (2, 3):
                        visible = set(cycle)
                        event = []
                        u, v = pair
                        for t in range(L + 2):
                            visible.update((u, v))
                            if t < L:
                                event.append((u, v, 0))
                            u, v = T[u], T[v]
                        edges = forced + event
                        local = [edge for edge in edges if set(edge[:2]) <= visible]
                        full = shadow(n, edges, cycle)
                        reduced = shadow(n, local, cycle)
                        counts[n] += 1
                        if full != reduced:
                            return counts, dict(T=T, cycle=cycle, pair=pair, L=L,
                                                full=sorted(full), local=sorted(reduced)), semantic_difference
                        if semantic_difference is None:
                            reported = historical.projected_shadow(n, edges, cycle)
                            if reported != full:
                                semantic_difference = dict(
                                    T=T, cycle=cycle, pair=pair, L=L,
                                    historical=sorted(reported), full=sorted(full),
                                )
    return counts, None, semantic_difference
