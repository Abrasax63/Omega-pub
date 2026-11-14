"""Compare the PR #18 projector with exact full-coloring enumeration."""
from collections import Counter
from itertools import combinations, product
import json
from test_v19_locality_l_plus_1 import (
    coherent, cycles, event_edges, forced_edges, projected_shadow, visible_l_plus_1,
)

counts = Counter()
for n in range(3, 7):
    assignments = tuple(product((0, 1), repeat=n))
    all_assignments = (1 << len(assignments)) - 1
    edges = {
        (u, v, parity): sum(1 << i for i, c in enumerate(assignments)
                            if c[u] ^ c[v] == parity)
        for u, v in combinations(range(n), 2) for parity in (0, 1)
    }

    def solutions(constraints):
        possible = all_assignments
        for u, v, parity in constraints:
            possible &= edges[min(u, v), max(u, v), parity]
        return possible

    for T in product(range(n), repeat=n):
        F = forced_edges(T)
        if not coherent(n, F):
            continue
        for cycle in cycles(T):
            colorings = [
                sum(c[v] << i for i, v in enumerate(cycle)) for c in assignments
            ]

            def shadow(constraints):
                bits = solutions(constraints)
                result = set()
                while bits:
                    bit = bits & -bits
                    result.add(colorings[bit.bit_length() - 1])
                    bits ^= bit
                return result

            for pair in combinations(range(n), 2):
                for L in (2, 3):
                    full = F + event_edges(T, pair, L)
                    V = visible_l_plus_1(T, pair, L, cycle)
                    local = tuple(e for e in full if e[0] in V and e[1] in V)
                    g, l = shadow(full), shadow(local)
                    counts["comparisons"] += 1
                    counts["absolute_global_mismatch"] += g != projected_shadow(n, full, cycle)
                    counts["absolute_local_mismatch"] += l != projected_shadow(n, local, cycle)
                    if g != l:
                        counts["global_local_mismatch"] += 1
                        if counts["global_local_mismatch"] == 1:
                            print(json.dumps(dict(T=T, cycle=cycle, pair=pair, L=L,
                                                  full=full, local=local,
                                                  global_shadow=sorted(g), local_shadow=sorted(l))), flush=True)
assert counts["comparisons"] == 325468
for key in ("absolute_global_mismatch", "absolute_local_mismatch", "global_local_mismatch"):
    counts.setdefault(key, 0)
print(json.dumps(counts, sort_keys=True))
