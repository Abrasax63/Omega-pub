"""Decide four-event inclusion-minimal contradictions on a coherent forced system."""
from collections import Counter
from itertools import product
from time import perf_counter
import json

from pivot import family, priority, certify
from test_v19_locality_l_plus_1 import forced_edges, event_edges


def signed_core(case):
    transformation, _, _, forced, events = case
    adjacency = [[] for _ in transformation]
    for a,b,p in forced:
        adjacency[a].append((b,p))
        adjacency[b].append((a,p))
    root = [-1] * len(adjacency)
    offset = [0] * len(adjacency)
    for i in range(len(adjacency)):
        if root[i] >= 0:
            continue
        root[i] = i
        stack = [i]
        while stack:
            a = stack.pop()
            for b,p in adjacency[a]:
                if root[b] == -1:
                    root[b] = i
                    offset[b] = offset[a] ^ p
                    stack.append(b)
                elif offset[b] != offset[a] ^ p:
                    raise ValueError('Forced constraints must be coherent')
    degree = Counter()
    seen = set()
    total = 0
    for a,b,p in events:
        u,v = root[a],root[b]
        edge = frozenset((u,v))
        if u == v or edge in seen:
            return False
        seen.add(edge)
        degree[u] += 1
        degree[v] += 1
        total ^= offset[a] ^ offset[b] ^ p
    return bool(total and len(seen)==4 and len(degree)==4 and all(d==2 for d in degree.values()))


def control(transformation, pair, wanted):
    case = (transformation, pair, (0,1,2,3), forced_edges(transformation),
            event_edges(transformation,pair,4))
    assert bool(certify(case)) == signed_core(case) == wanted


def audit(n,q):
    stats=dict(n=n,q=q,total=0,positive=0,fixed_projection_calls=0,
               oracle_projection_calls=0,candidate_errors=0,fixed_errors=0,
               fixed_seconds=0.,candidate_seconds=0.,oracle_seconds=0.)
    for case in family(n,q):
        t=perf_counter()
        screened=priority(case)==0
        fixed=screened and bool(certify(case))
        stats['fixed_seconds']+=perf_counter()-t
        t=perf_counter()
        candidate=signed_core(case)
        stats['candidate_seconds']+=perf_counter()-t
        t=perf_counter()
        exact=bool(certify(case))
        stats['oracle_seconds']+=perf_counter()-t
        stats['total']+=1
        stats['positive']+=exact
        stats['fixed_projection_calls']+=5*screened
        stats['oracle_projection_calls']+=5
        stats['candidate_errors']+=candidate!=exact
        stats['fixed_errors']+=fixed!=exact
    assert not stats['candidate_errors'] and not stats['fixed_errors']
    return stats


if __name__=='__main__':
    control((1,2,3,0),(0,1),False)
    control((1,2,3,0,0),(0,4),True)
    for n,q in [(7,5),(7,6),(8,5)]:
        print(json.dumps(audit(n,q),sort_keys=True),flush=True)
