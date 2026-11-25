"""Compare three strata of one-pair checks on the same applications."""
from itertools import combinations, product
import json
from time import perf_counter_ns

from audit_v19_pivot import priority
from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_amortize import check
from v19_signed import fixed, prepare, signed


def reserve():
    prefix = (1, 2, 3, 0, 5, 4)
    cards = []
    for tail in product(range(6), repeat=4):
        t = prefix + tail
        forced = forced_edges(t)
        if not coherent(len(t), forced):
            continue
        selected = {}
        for pair in combinations(range(len(t)), 2):
            events = event_edges(t, pair, 4)
            if len(events) != 4:
                continue
            row = t, pair, tuple(range(4)), forced, events
            key = "reject" if priority(row) else "positive" if fixed(row) else "pass_negative"
            selected.setdefault(key, row)
            if len(selected) == 3:
                cards.append(selected)
                break
        if len(cards) == 8:
            return cards
    raise AssertionError("insufficient reserve")


def main():
    tick = perf_counter_ns()
    short = ((0, 1, 0), (0, 1, 1), (1, 2, 0), (2, 3, 0))
    assert not signed(prepare(4, ()), short)
    guards = [compare([((0, 0, 3, 4, 2), (2, 3, 4), (0, 1), 2)]), compare(family())]
    assert all(row["new_errors"] == 0 for row in guards)
    cards = reserve()
    results = {k: check([[card[k]] for card in cards])
               for k in ("reject", "pass_negative", "positive")}
    assert [row["positives"] for row in results.values()] == [0, 0, 8]
    print(json.dumps(dict(results=results, guards=guards,
                          elapsed_ns=perf_counter_ns()-tick), indent=2))


if __name__ == "__main__":
    main()
