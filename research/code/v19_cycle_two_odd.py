"""Compare the first color contradiction on disjoint periodic orbits."""
from collections import Counter
from functools import reduce
from math import lcm
import json
from operator import and_
from time import perf_counter

from audit_v19_shadow_guard import compare, family
from test_v19_locality_l_plus_1 import coherent, event_edges, forced_edges
from v19_branch_five import masks


def mapping(p, q, leaves):
    return tuple(range(1,p)) + (0,) + tuple(range(p+1,p+q)) + (p,) + ((0,p) if leaves else ())


def main():
    start = perf_counter()
    guards = [compare([((0,0,3,4,2),(2,3,4),(0,1),2)]), compare(family())]
    assert all(not g["new_errors"] for g in guards)
    cases = [(2,q) for q in range(3,12)] + [(3,4),(3,5)]
    totals, costs = Counter(), Counter()
    banks = {p+q+k for p,q in cases for k in (0,2)}
    oracles = {n: masks(n) for n in sorted(banks)}
    for p,q in cases:
        limit = lcm(p,q)
        expected = q+1 if p==2 and q%2 else None
        for leaves in (False,True):
            t = mapping(p,q,leaves)
            forced = forced_edges(t)
            assert coherent(len(t),forced)
            universe,bits = oracles[len(t)]
            base = reduce(and_,(bits[e] for e in forced),universe)
            for a in range(p):
                for b in range(p,p+q):
                    e = event_edges(t,(a,b),limit)
                    tick = perf_counter()
                    ref = next((i for i in range(1,limit+1)
                                if not coherent(len(t),forced+e[:i])),None)
                    costs["parity"] += perf_counter()-tick
                    tick = perf_counter()
                    state = base
                    exact = None
                    for i,row in enumerate(e,1):
                        state &= bits[row]
                        if not state:
                            exact=i
                            break
                    costs["oracle"] += perf_counter()-tick
                    assert expected == ref == exact, (p,q,leaves,a,b,expected,ref,exact)
                    totals["all"] += 1
                    totals["adverse" if p!=2 else "even" if q%2==0 else "odd"] += 1
    print(json.dumps(dict(totals=totals,costs=costs,guards=guards,
                          seconds=perf_counter()-start),indent=2))


if __name__ == "__main__":
    main()
