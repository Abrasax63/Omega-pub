"""Check admissibility of staggered and synchronous crossings."""
from itertools import product
from time import perf_counter
from audit_v19_prefix_information import prefix
from test_v19_locality_l_plus_1 import coherent, forced_edges

def check(paths):
    n = 10
    cycle = tuple(range(4))
    fixed = dict(zip(cycle, (1, 2, 3, 0)))
    for path in paths:
        for a, b in zip(path, path[1:]):
            assert fixed.setdefault(a, b) == b
    ends = tuple(p[-1] for p in paths)
    admissible = consistent = observations = 0
    free = [v for v in range(n) if v not in fixed]
    for images in product(range(n), repeat=len(free)):
        T = fixed | dict(zip(free, images))
        T = tuple(T[v] for v in range(n))
        assert tuple(prefix(T, p[0], 2) for p in paths) == paths
        if not coherent(n, forced_edges(T)):
            continue
        consistent += 1
        if len(set(ends)) != 2 or set(ends) & fixed.keys():
            continue
        admissible += 1
        observations += sum(T[v] not in ends for v in ends)
    return n**len(free), consistent, admissible, observations

if __name__ == "__main__":
    start = perf_counter()
    staggered = check(((4, 5, 6), (7, 4, 5)))
    synchronous = check(((4, 6, 7), (5, 6, 7)))
    disjoint = check(((4, 5, 6), (7, 8, 9)))
    print("staggered", staggered, "synchronous", synchronous, "disjoint", disjoint)
    assert staggered[1] and synchronous[1] and disjoint[3]
    assert staggered[2] == synchronous[2] == 0
    print("seconds", round(perf_counter()-start, 6))
