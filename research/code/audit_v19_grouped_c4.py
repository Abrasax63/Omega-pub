"""Exhaust all completions jointly of two fixed disjoint paths and a C4."""
from itertools import product
from time import perf_counter
from audit_v19_one_read_completions import completion_shadows
from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges

CYCLE = (0, 1, 2, 3)

def census(n, L):
    one_read, two_reads = {}, {}
    observations = 0
    witnesses = {}
    paths = (tuple(range(4, 5 + L)), tuple(range(5 + L, 6 + 2*L)))
    pair = tuple(path[0] for path in paths)
    fixed = {0: 1, 1: 2, 2: 3, 3: 0}
    for path in paths:
        fixed.update(zip(path, path[1:]))
    ends = tuple(path[-1] for path in paths)
    unknown = tuple(v for v in range(n) if v not in fixed)
    for images in product(range(n), repeat=len(unknown)):
        transitions = fixed | dict(zip(unknown, images))
        T = tuple(transitions[v] for v in range(n))
        F = forced_edges(T)
        if not coherent(n, F):
            continue
        readers = tuple((a, b) for a, b in (ends, ends[::-1]) if T[a] not in ends)
        if not readers:
            continue
        shadow = exhaustive_shadow(n, F + event_edges(T, pair, L), CYCLE)
        for read, unread in readers:
            observations += 1
            key = (pair, L, paths, read, T[read])
            for groups, k, label in ((one_read, key, "one"),
                                     (two_reads, (*key, T[unread]), "two")):
                values = groups.setdefault(k, {})
                values.setdefault(shadow, T)
                if len(values) > 1 and label not in witnesses:
                    witnesses[label] = (k, [(sorted(s), t) for s, t in values.items()])
    print(n, observations, len(one_read), sum(len(v)>1 for v in one_read.values()),
          len(two_reads), sum(len(v)>1 for v in two_reads.values()), witnesses)

if __name__ == "__main__":
    T = (1, 2, 0, 3, 4, 3, 4, 5, 6, 0)
    negative = completion_shadows(T, (0, 1, 2), (7, 8), 2, 4, ((7, 5, 3), (8, 6, 4)))
    assert len(negative) > 1
    print("negative", sorted(map(sorted, negative)))
    start = perf_counter()
    for n, L in ((10, 2), (11, 2)):
        census(n, L)
    print("seconds", round(perf_counter() - start, 3))
