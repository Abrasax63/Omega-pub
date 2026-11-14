"""Check exact global and L+1 shadows on decorated functional graphs."""
from itertools import combinations, product

from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow
from test_v19_locality_l_plus_1 import (
    coherent, event_edges, forced_edges, visible_l_plus_1,
)


def systems():
    # C3, disjoint C2 or two fixed points, and two tails of length two.
    for core in ((4, 3), (3, 4)):
        for a, b in combinations(range(5), 2):
            yield (1, 2, 0, *core, a, b, 5, 6)


def main():
    pairs = total = empty = 0
    cycle = (0, 1, 2)
    for T in systems():
        forced = forced_edges(T)
        assert coherent(len(T), forced)
        for pair, horizon in product(combinations(range(len(T)), 2), (2, 3, 4, 5)):
            full = forced + event_edges(T, pair, horizon)
            visible = visible_l_plus_1(T, pair, horizon, cycle)
            local = tuple(e for e in full if e[0] in visible and e[1] in visible)
            exact = exhaustive_shadow(len(T), full, cycle)
            exact_local = exhaustive_shadow(len(T), local, cycle)
            assert exact == exact_local, (T, pair, horizon, exact, exact_local)
            for edges in (full, local):
                assert guarded_shadow(len(T), edges, cycle) == exact
                total += 1
            pairs += 1
            empty += not exact
    print(f"comparisons={pairs} guarded_projections={total} empty_shadows={empty}")


if __name__ == "__main__":
    main()
