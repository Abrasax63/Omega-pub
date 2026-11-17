"""Compare an early decision at L with an unconditional read at L+1."""
from itertools import combinations, product
from time import perf_counter

from audit_v19_prefix_information import CYCLE, FIXED, PAIR, PERIODIC, prefix
from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def shadow_if_decidable(cycle, paths, horizon):
    """Return None if the known edges do not certify the shadow."""
    image = dict(zip(cycle, cycle[1:] + cycle[:1]))
    for path in paths:
        for u, v in zip(path, path[1:]):
            if image.setdefault(u, v) != v:
                raise ValueError("inconsistent trajectories")

    nodes = sorted(image)
    indices = {v: i for i, v in enumerate(nodes)}
    constraints = [
        (indices[u], indices[v], 1)
        for u, v in combinations(nodes, 2)
        if image[u] == image[v] or {image[u], image[v]} == {u, v}
    ]
    constraints.extend(
        (indices[u], indices[v], 0)
        for u, v in zip(*(path[:horizon] for path in paths)) if u != v
    )
    shadow = guarded_shadow(len(nodes), constraints, tuple(indices[v] for v in cycle))
    needed = {image[v] for v in set(cycle).union(*(path[:horizon] for path in paths))}
    if shadow and not needed <= image.keys():
        return None
    return shadow


def main():
    for T, size in ((FIXED, 0), (PERIODIC, 8)):
        assert shadow_if_decidable(CYCLE, tuple(prefix(T, v, 2) for v in PAIR), 2) is None
        assert len(shadow_if_decidable(CYCLE, tuple(prefix(T, v, 3) for v in PAIR), 2)) == size

    cycle = (0, 1, 2, 3, 4)
    cases = early = early_empty = 0
    fixed_seconds = adaptive_seconds = 0.0
    for a, b in combinations(range(7), 2):
        T = (1, 2, 3, 4, 0, 6, 5, a, b)
        forced = forced_edges(T)
        assert coherent(len(T), forced)
        for pair, L in product(combinations(range(len(T)), 2), (2, 3, 4, 5)):
            short = tuple(prefix(T, v, L) for v in pair)
            long = tuple(prefix(T, v, L + 1) for v in pair)
            start = perf_counter()
            fixed = shadow_if_decidable(cycle, long, L)
            fixed_seconds += perf_counter() - start
            start = perf_counter()
            adaptive = shadow_if_decidable(cycle, short, L)
            if adaptive is None:
                adaptive = shadow_if_decidable(cycle, long, L)
            else:
                early += 1
                early_empty += not adaptive
            adaptive_seconds += perf_counter() - start
            oracle = exhaustive_shadow(len(T), forced + event_edges(T, pair, L), cycle)
            assert fixed == adaptive == oracle, (T, pair, L)
            cases += 1
    print(f"cases={cases} early={early} early_empty={early_empty} fallback={cases-early}")
    print(f"fixed_seconds={fixed_seconds:.6f} adaptive_seconds={adaptive_seconds:.6f}")


if __name__ == "__main__":
    main()
