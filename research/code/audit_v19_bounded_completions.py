"""Enumerate every compatible endofunction on a fixed labelled carrier."""
from itertools import product

from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges


def enumerate_shadows(n, cycle, paths, side, image):
    known = dict(zip(cycle, cycle[1:] + cycle[:1]))
    for path in paths:
        for u, v in zip(path, path[1:]):
            assert known.setdefault(u, v) == v
    assert paths[side][-1] not in known
    known[paths[side][-1]] = image
    unknown = sorted(set(range(n)) - known.keys())
    counts = {}
    admitted = 0
    pair = tuple(path[0] for path in paths)
    horizon = len(paths[0]) - 1
    for values in product(range(n), repeat=len(unknown)):
        mapping = known | dict(zip(unknown, values))
        T = tuple(mapping[v] for v in range(n))
        forced = forced_edges(T)
        if coherent(n, forced):
            admitted += 1
            shadow = exhaustive_shadow(n, forced + event_edges(T, pair, horizon), cycle)
            counts.setdefault(shadow, T)
    return n ** len(unknown), admitted, counts


def main():
    cases = (
        (10, (0, 1, 2, 3), ((8, 6, 4), (9, 7, 5)), (4, 5)),
        (9, (0, 1, 2), ((7, 5, 3), (8, 6, 4)), (3, 4)),
        (10, (0, 1, 2), ((7, 5, 3), (8, 6, 4)), (3, 4)),
    )
    for n, cycle, paths, images in cases:
        for side, terminal_image in enumerate(images):
            attempts, admitted, shadows = enumerate_shadows(
                n, cycle, paths, side, terminal_image,
            )
            assert frozenset() in shadows
            assert frozenset(range(1 << len(cycle))) in shadows
            print(n, side, attempts, admitted, len(shadows),
                  sorted((len(shadow), T) for shadow, T in shadows.items()))


if __name__ == "__main__":
    main()
