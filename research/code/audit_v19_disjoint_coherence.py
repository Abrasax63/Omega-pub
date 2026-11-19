"""Falsify a cycle-only coherence certificate using unseen disjoint components."""
from itertools import product
from time import perf_counter
import json
from test_v19_locality_l_plus_1 import forced_edges, event_edges
from audit_v19_shadow_guard import exhaustive_shadow, guarded_shadow

def run(q,k):
    cycle=tuple(range(q)); counts=dict(cases=0,local_false_nonempty=0,global_errors=0)
    seconds=[0.,0.,0.]; witness=None
    for remote in product(range(q,q+k),repeat=k):
        T=tuple(range(1,q))+(0,)+remote
        edges=forced_edges(T)+event_edges(T,(0,1),2)
        local=tuple(e for e in edges if e[0]<q and e[1]<q)
        answers=[]
        for i,(fn,es) in enumerate(((exhaustive_shadow,edges),(guarded_shadow,local),(guarded_shadow,edges))):
            t=perf_counter(); answers.append(fn(q+k,es,cycle)); seconds[i]+=perf_counter()-t
        exact,partial,full=answers
        counts['cases']+=1
        counts['local_false_nonempty']+=bool(partial) and not exact
        counts['global_errors']+=full!=exact
        if partial!=exact and witness is None:
            witness=dict(T=T,local=sorted(partial),exact=sorted(exact))
    assert counts['local_false_nonempty']>0 and counts['global_errors']==0
    return dict(q=q,k=k,**counts,seconds=seconds,first_counterexample=witness)

if __name__=='__main__':
    # First ordered assignment is the preregistered triple-fibre negative control.
    print(json.dumps(run(4,3),sort_keys=True))
    print(json.dumps(run(5,4),sort_keys=True))
