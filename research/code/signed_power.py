"""Cross-check on C4 plus a disjoint C2 and two free states."""
from itertools import combinations, product
import json

import signed_core as trial
from test_v19_locality_l_plus_1 import forced_edges, event_edges, coherent


def cases(n,q):
    assert (n,q)==(8,4)
    for tail in product(range(n),repeat=2):
        T=(1,2,3,0,5,4)+tail
        F=forced_edges(T)
        if not coherent(n,F):
            continue
        for pair in combinations(range(n),2):
            E=event_edges(T,pair,4)
            if len(E)==4:
                yield T,pair,(0,1,2,3),F,E


if __name__=='__main__':
    trial.family=cases
    print(json.dumps(trial.audit(8,4),sort_keys=True))
