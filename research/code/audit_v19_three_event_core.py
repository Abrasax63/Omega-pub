"""Find minimal inconsistent triples of actual orbital event equalities."""
from itertools import product,combinations
from time import perf_counter
import json
from test_v19_locality_l_plus_1 import forced_edges,event_edges,coherent
from audit_v19_shadow_guard import exhaustive_shadow,guarded_shadow

def core(T,pair,C):
    F=forced_edges(T);E=event_edges(T,pair,3);n=len(T)
    assert coherent(n,F)
    full=exhaustive_shadow(n,F+E,C)
    deleted=[exhaustive_shadow(n,F+E[:i]+E[i+1:],C) for i in range(3)]
    assert not full and all(deleted)
    return dict(T=T,pair=pair,forced=F,event=E,full_size=len(full),deletion_sizes=list(map(len,deleted)))

def audit():
    C=(0,1,2);queries=cores=skipped=errors=0;first=None;times=[0.,0.]
    for images in product(range(6),repeat=3):
        T=(1,2,0)+images;F=forced_edges(T)
        if not coherent(6,F):skipped+=1;continue
        for pair in combinations(range(6),2):
            E=event_edges(T,pair,3);results=[]
            for i,fn in enumerate((guarded_shadow,exhaustive_shadow)):
                start=perf_counter();results.append(fn(6,F+E,C));times[i]+=perf_counter()-start
            errors+=results[0]!=results[1];queries+=1
            if len(E)==3 and not results[1] and all(coherent(6,F+E[:i]+E[i+1:]) for i in range(3)):
                cores+=1
                if first is None:first=core(T,pair,C)
    assert errors==0 and cores>0
    return dict(systems=216,forced_incoherent_systems_skipped=skipped,queries=queries,minimal_three_event_cores=cores,errors=errors,
                seconds_guard_exhaustive=times,first_certificate=first)
if __name__=='__main__':
    # Negative control: three same-parity event edges along C4 do not conflict.
    T=(1,2,3,0);assert exhaustive_shadow(4,forced_edges(T)+event_edges(T,(0,1),3),tuple(range(4)))
    print(json.dumps(dict(negative_control='C4 coherent',witness=core((1,2,0,1),(3,1),(0,1,2)))),flush=True)
    print(json.dumps(dict(split='reserve',**audit())),flush=True)
