"""Check the structure of V19 forced-inequality graphs."""
from collections import Counter
from itertools import product
import json
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import forced_edges, coherent


def criterion(t):
    return max(Counter(t).values()) <= 2 and sum(u == v for u,v in enumerate(t)) <= 2


def oracle(n, edges):
    return any(all(c[u] != c[v] for u,v,_ in edges) for c in product((0,1), repeat=n))


def component_shape(n, edges):
    adjacency = [set() for _ in range(n)]
    for u,v,_ in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    unseen = set(range(n))
    lengths = []
    while unseen:
        todo = [unseen.pop()]
        connected = set()
        while todo:
            u = todo.pop()
            connected.add(u)
            todo.extend(adjacency[u] & unseen)
            unseen.difference_update(adjacency[u])
        assert max(len(adjacency[u]) for u in connected) <= 2
        assert sum(len(adjacency[u]) for u in connected) == 2*(len(connected)-1)
        lengths.append(len(connected)-1)
    return lengths


def main():
    start = perf_counter()
    for t in ((0,0,0),(0,1,2)):
        assert not criterion(t) and not oracle(len(t), forced_edges(t))
    sharp = (1,0,0,1)
    assert criterion(sharp) and oracle(4,forced_edges(sharp)) and component_shape(4,forced_edges(sharp)) == [3]
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(g["new_errors"] == 0 for g in guards)
    out = {}
    costs = [0.,0.,0.]
    for n in range(1,7):
        ts = list(product(range(n),repeat=n))
        fs = [forced_edges(t) for t in ts]
        tick = perf_counter()
        gold = [oracle(n,edges) for edges in fs]
        costs[0] += perf_counter()-tick
        tick = perf_counter()
        fixed = [coherent(n,edges) for edges in fs]
        costs[1] += perf_counter()-tick
        tick = perf_counter()
        candidate = list(map(criterion,ts))
        costs[2] += perf_counter()-tick
        for t,a,b,c in zip(ts,gold,fixed,candidate,strict=True):
            assert a == b == c, (t,a,b,c)
        components = Counter(length for edges,yes in zip(fs,gold,strict=True) if yes for length in component_shape(n,edges))
        assert max(components) <= 3
        out[n] = dict(maps=len(ts),coherent=sum(gold),components=components)
    print(json.dumps(dict(families=out, costs=costs, errors=[0,0], guards=guards,
                          seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
