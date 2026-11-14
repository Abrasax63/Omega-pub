"""Compare global shadows with prefixes ending at L and L-1."""
from itertools import combinations

from audit_v19_lplus1_paths import systems
from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def restricted(T, pair, cycle, edges, last):
    visible = set(cycle)
    for state in pair:
        for _ in range(last + 1):
            visible.add(state)
            state = T[state]
    return tuple(edge for edge in edges if set(edge[:2]) <= visible)


def main():
    cycle = (0, 1, 2)
    mismatches = {0: 0, -1: 0}
    first = None
    cases = 0
    for T in systems():
        F = forced_edges(T)
        assert coherent(len(T), F)
        for pair in combinations(range(len(T)), 2):
            for L in (2, 3, 4, 5):
                full = F + event_edges(T, pair, L)
                exact = exhaustive_shadow(len(T), full, cycle)
                for offset in mismatches:
                    local = restricted(T, pair, cycle, full, L + offset)
                    observed = exhaustive_shadow(len(T), local, cycle)
                    assert guarded_shadow(len(T), local, cycle) == observed
                    if exact != observed:
                        mismatches[offset] += 1
                        if offset == -1 and first is None:
                            first = (T, pair, L, full, local, sorted(exact), sorted(observed))
                cases += 1
    print("cases", cases, "differences", mismatches, "first at L-1", first)
    assert mismatches[0] == 0
    pair, L = (0, 6), 2
    maps = ((1, 2, 0, 4, 3, 0, 3, 5, 6), (1, 2, 0, 3, 4, 0, 3, 5, 6))
    assert all(tuple(T[v] for v in pair) == (1, 3) for T in maps)
    shadows = []
    for T in maps:
        F = forced_edges(T)
        assert coherent(len(T), F)
        shadows.append(sorted(exhaustive_shadow(len(T), F + event_edges(T, pair, L), cycle)))
    assert shadows == [[0, 3, 4, 7], [1, 2, 5, 6]]
    print("identical prefixes through L-1, different exact shadows:", shadows)


if __name__ == "__main__":
    main()
