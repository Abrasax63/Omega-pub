from itertools import combinations, product
from time import perf_counter
from audit_v19_prefix_information import FIXED, PERIODIC, CYCLE, PAIR, prefix
from audit_v19_shadow_guard import guarded_shadow, exhaustive_shadow
from test_v19_locality_l_plus_1 import coherent, forced_edges, event_edges

def reconstruct(cycle, paths, horizon):
    if any(len(path) < horizon + 2 for path in paths):
        return None
    image = dict(zip(cycle, cycle[1:] + cycle[:1]))
    for path in paths:
        for u, v in zip(path[:horizon+1], path[1:horizon+2]):
            if image.setdefault(u, v) != v:
                raise ValueError("inconsistent trajectories")
    nodes = sorted(image)
    idx = {v: i for i, v in enumerate(nodes)}
    edges = [(idx[u], idx[v], 1) for u,v in combinations(nodes,2)
             if image[u] == image[v] or {image[u], image[v]} == {u,v}]
    edges.extend((idx[u],idx[v],0) for u,v in zip(*(p[:horizon] for p in paths)) if u != v)
    return guarded_shadow(len(nodes), edges, tuple(idx[v] for v in cycle))

for T, size in ((FIXED,0),(PERIODIC,8)):
    paths = tuple(prefix(T, v, 2) for v in PAIR)
    assert reconstruct(CYCLE,paths,2) is None
    assert len(reconstruct(CYCLE,tuple(prefix(T,v,3) for v in PAIR),2)) == size

cases = empty = 0
candidate_time = oracle_time = 0
B = (0,1,2,3)
for a,b in product(range(7), repeat=2):
    T = (1,2,3,0,5,6,4,a,b)
    F = forced_edges(T)
    if not coherent(len(T),F):
        continue
    for pair,L in product(combinations(range(len(T)),2), (2,3,4)):
        paths = tuple(prefix(T,v,L+1) for v in pair)
        start = perf_counter()
        actual = reconstruct(B,paths,L)
        candidate_time += perf_counter() - start
        edges = F + event_edges(T,pair,L)
        start = perf_counter()
        expected = exhaustive_shadow(len(T),edges,B)
        oracle_time += perf_counter() - start
        assert actual == expected, (T,pair,L)
        cases += 1
        empty += not expected
print(cases, empty, candidate_time, oracle_time)
