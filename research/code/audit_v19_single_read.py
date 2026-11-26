"""Measure the value of reading either transition first on V19 deferrals."""
from collections import Counter
from itertools import combinations, product

from audit_v19_adaptive_prefix import shadow_if_decidable
from audit_v19_prefix_information import CYCLE, FIXED, PAIR, PERIODIC, prefix
from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def classify(T, cycle, pair, horizon):
    short = tuple(prefix(T, state, horizon) for state in pair)
    if shadow_if_decidable(cycle, short, horizon) is not None:
        return None

    left, right = short
    long_left = left + (T[left[-1]],)
    long_right = right + (T[right[-1]],)
    exact = exhaustive_shadow(
        len(T), forced_edges(T) + event_edges(T, pair, horizon), cycle,
    )
    decisions = (
        shadow_if_decidable(cycle, (long_left, right), horizon),
        shadow_if_decidable(cycle, (left, long_right), horizon),
    )
    assert all(shadow is None or shadow == exact for shadow in decisions)
    assert shadow_if_decidable(cycle, (long_left, long_right), horizon) == exact
    known = set(cycle) | set(left[:-1]) | set(right[:-1])
    missing = tuple(path[-1] not in known for path in short)
    return tuple(shadow is not None for shadow in decisions), left[-1] == right[-1], missing


def main():
    cycle = (0, 1, 2, 3, 4)
    counts = Counter()
    for a, b in combinations(range(7), 2):
        T = (1, 2, 3, 4, 0, 6, 5, a, b)
        assert coherent(len(T), forced_edges(T))
        for pair, horizon in product(combinations(range(len(T)), 2), (2, 3, 4, 5)):
            outcome = classify(T, cycle, pair, horizon)
            if outcome is not None:
                reversed_outcome = classify(T, cycle, pair[::-1], horizon)
                decisions, shared, missing = outcome
                assert reversed_outcome == (decisions[::-1], shared, missing[::-1])
                counts[outcome] += 1
    assert sum(counts.values()) == 70
    for (decisions, shared, missing), count in sorted(counts.items()):
        print(f"decidable={decisions} shared={shared} unknown_images={missing}: {count}")
    for T in (FIXED, PERIODIC):
        print("ambiguity witness:", classify(T, CYCLE, PAIR, 2))


if __name__ == "__main__":
    main()
