"""Search for ambiguity when the first image lies outside both terminals."""
from itertools import combinations, product
from random import Random

from audit_v19_one_read_completions import completion_shadows
from audit_v19_prefix_information import prefix
from test_v19_locality_l_plus_1 import coherent, forced_edges


def main():
    # Two disjoint paths of length two and an unobserved state.
    cycle = (0, 1, 2)
    pair = (7, 8)
    short = ((7, 5, 3), (8, 6, 4))
    base = (1, 2, 0, 3, 4, 3, 4, 5, 6, 0)
    negative = completion_shadows(base, cycle, pair, 2, 4, short)
    assert len(negative) > 1
    tested = informative = ambiguous = 0
    for side, image, unseen in product((3, 4), range(10), range(10)):
        if image in (3, 4):
            continue
        T = list(base)
        T[side], T[9] = image, unseen
        shadows = completion_shadows(tuple(T), cycle, pair, 2, 7 - side, short)
        tested += 1
        informative += bool(shadows)
        ambiguous += len(shadows) > 1
    print("disjoint observation", tested, informative, ambiguous)

    rng = Random(1718)
    checked = 0
    for _ in range(6000):
        T = (1, 2, 0) + tuple(rng.randrange(10) for _ in range(7))
        if not coherent(10, forced_edges(T)):
            continue
        for pair, L in product(combinations(range(10), 2), (2, 3)):
            short = tuple(prefix(T, v, L) for v in pair)
            known = set(cycle).union(*(path[:-1] for path in short))
            terminals = {path[-1] for path in short}
            if len(terminals) != 2 or terminals & known:
                continue
            for read, unread in (tuple(sorted(terminals)), tuple(sorted(terminals, reverse=True))):
                if T[read] in terminals:
                    continue
                checked += 1
                shadows = completion_shadows(T, cycle, pair, L, unread, short)
                if len(shadows) > 1:
                    print("witness", checked, T, pair, L, short, read, unread,
                          [(v, sorted(s)) for s, v in shadows.items()])
                    return
    print("no witness", checked)


if __name__ == "__main__":
    main()
