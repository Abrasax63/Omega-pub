"""Compare reuse of a V19 brick with a direct solver on the same missions."""
from hashlib import sha256
from itertools import combinations
import json
from time import perf_counter

from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges

BRICKS = {
    "OBS-V19-LPLUS1-AUDIT": "bounded_locality",
    "OBS-V19-SHADOW-GUARD": "global_binary_parity_projection",
}
MISSION = "global_binary_parity_projection"


def direct_shadow(n, constraints, cycle):
    return frozenset(
        sum(((mask >> v) & 1) << i for i, v in enumerate(cycle))
        for mask in range(1 << n)
        if all(((mask >> u) ^ (mask >> v)) & 1 == parity
               for u, v, parity in constraints)
    )


def choose_brick(catalog, mission):
    return next((key for key, scope in catalog.items() if scope == mission), None)


def missions():
    cycle = (0, 1, 2, 3)
    # One C4, two fixed points, two leaves at distinct periodic destinations.
    for destinations in combinations(range(6), 2):
        T = (1, 2, 3, 0, 4, 5) + destinations
        forced = forced_edges(T)
        assert coherent(len(T), forced)
        for pair in combinations(range(len(T)), 2):
            for horizon in (2, 3, 4):
                yield len(T), forced + event_edges(T, pair, horizon), cycle


def solve(cases, catalog):
    start = perf_counter()
    brick = choose_brick(catalog, MISSION)
    projector = guarded_shadow if brick == "OBS-V19-SHADOW-GUARD" else direct_shadow
    outputs = [projector(*case) for case in cases]
    return brick, outputs, perf_counter() - start


def main():
    cases = list(missions())
    # Each arm receives the same cases and may invoke one projector per case.
    # The oracle runs only after both arms have returned their masks.
    arms = [solve(cases, catalog) for catalog in ({}, BRICKS)]
    oracle = [exhaustive_shadow(*case) for case in cases]
    print("missions", len(cases), "empty shadows", sum(not masks for masks in oracle))
    print("mask digest", sha256(json.dumps([sorted(x) for x in oracle]).encode()).hexdigest())
    for brick, outputs, elapsed in arms:
        errors = sum(actual != expected for actual, expected in zip(outputs, oracle))
        print(brick, "errors", errors, "seconds", round(elapsed, 6))
        assert errors == 0
    assert arms[0][0] is None and arms[1][0] == "OBS-V19-SHADOW-GUARD"


if __name__ == "__main__":
    main()
