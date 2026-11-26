"""Measure one-read certificates when two distinct terminal images are unknown."""
from collections import Counter
from itertools import combinations, product

from audit_v19_prefix_information import CYCLE, FIXED, PAIR, PERIODIC
from audit_v19_single_read import classify
from test_v19_locality_l_plus_1 import coherent, forced_edges


def main():
    for witness in (FIXED, PERIODIC):
        assert classify(witness, CYCLE, PAIR, 2) == (
            (False, False), False, (True, True),
        )

    cycle = (0, 1, 2, 3)
    counts = Counter()
    for core, depth in product(((4, 5), (5, 4)), (1, 2, 3)):
        for a, b in combinations(range(6), 2):
            T = (1, 2, 3, 0, *core, a, b) + tuple(range(6, 6 + 2 * (depth - 1)))
            assert coherent(len(T), forced_edges(T))
            for pair, horizon in product(combinations(range(len(T)), 2), range(2, 6)):
                outcome = classify(T, cycle, pair, horizon)
                if outcome is None:
                    continue
                decisions, shared, unknown = outcome
                if shared or unknown != (True, True):
                    continue
                assert classify(T, cycle, pair[::-1], horizon) == (
                    decisions[::-1], False, (True, True),
                )
                counts[decisions] += 1

    total = sum(counts.values())
    assert total > 0
    print("decision counts", sorted(counts.items()))
    for side, name in enumerate(("left", "right")):
        saved = sum(count for decisions, count in counts.items() if decisions[side])
        print(name, "reads", 2 * total - saved, "round trips", 2 * total - saved)
    print("batch reads", 2 * total, "batch round trips", total)


if __name__ == "__main__":
    main()
