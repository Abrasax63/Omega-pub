"""Seek indistinguishable completions after either single terminal read."""
from collections import Counter
from itertools import combinations, product

from audit_v19_prefix_information import prefix
from audit_v19_shadow_guard import exhaustive_shadow
from audit_v19_single_read import classify
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def completion_shadows(T, cycle, pair, horizon, unread, short):
    shadows = {}
    for target in range(len(T)):
        candidate = T[:unread] + (target,) + T[unread + 1:]
        assert tuple(prefix(candidate, v, horizon) for v in pair) == short
        forced = forced_edges(candidate)
        if coherent(len(T), forced):
            shadow = exhaustive_shadow(
                len(T), forced + event_edges(candidate, pair, horizon), cycle,
            )
            shadows.setdefault(shadow, target)
    return shadows


def main():
    cycle = (0, 1, 2, 3)
    counts = Counter()
    first = None
    for core, depth in product(((4, 5), (5, 4)), (1, 2, 3)):
        for a, b in combinations(range(6), 2):
            T = (1, 2, 3, 0, *core, a, b) + tuple(range(6, 6 + 2 * (depth - 1)))
            assert coherent(len(T), forced_edges(T))
            for pair, horizon in product(combinations(range(len(T)), 2), range(2, 6)):
                outcome = classify(T, cycle, pair, horizon)
                if outcome is None or outcome[1:] != (False, (True, True)):
                    continue
                short = tuple(prefix(T, v, horizon) for v in pair)
                left, right = (path[-1] for path in short)
                variants = [completion_shadows(T, cycle, pair, horizon, v, short)
                            for v in (right, left)]
                ambiguous = tuple(len(shadows) > 1 for shadows in variants)
                counts[ambiguous] += 1
                if all(ambiguous) and first is None:
                    first = (T, pair, horizon, short,
                             [[(target, sorted(shadow)) for shadow, target in choices.items()]
                              for choices in variants])
    assert sum(counts.values()) == 66
    print("ambiguity after left and right", sorted(counts.items()))
    print("first witness", first)


if __name__ == "__main__":
    main()
