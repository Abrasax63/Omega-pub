"""Check an indistinguishability witness for the V19 prefix through L."""
from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges

CYCLE = (0, 1, 2)
PAIR = (8, 9)
L = 2
FIXED = (1, 2, 0, 3, 4, 0, 3, 4, 6, 7)
PERIODIC = (1, 2, 0, 4, 5, 3, 3, 4, 6, 7)


def prefix(T, state, last):
    path = [state]
    for _ in range(last):
        path.append(T[path[-1]])
    return tuple(path)


def main():
    for state in PAIR:
        assert prefix(FIXED, state, L) == prefix(PERIODIC, state, L)
    assert any(prefix(FIXED, state, L + 1) != prefix(PERIODIC, state, L + 1)
               for state in PAIR)
    for T, expected_size in ((FIXED, 0), (PERIODIC, 8)):
        assert tuple(T[v] for v in CYCLE) == (1, 2, 0)
        forced = forced_edges(T)
        assert coherent(len(T), forced)
        full = forced + event_edges(T, PAIR, L)
        exact = exhaustive_shadow(len(T), full, CYCLE)
        assert guarded_shadow(len(T), full, CYCLE) == exact
        assert len(exact) == expected_size
        visible = set(CYCLE).union(*(prefix(T, state, L) for state in PAIR))
        induced = tuple(edge for edge in full if set(edge[:2]) <= visible)
        assert exhaustive_shadow(len(T), induced, CYCLE) == exact
        print(T, "forced", forced, "exact", sorted(exact))


if __name__ == "__main__":
    main()
