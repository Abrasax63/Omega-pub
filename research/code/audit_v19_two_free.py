from collections import Counter
from itertools import product
from time import perf_counter
from audit_v19_free_certificate import full_shadow_certificate, check_controls
from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import forced_edges, coherent, event_edges

def main():
    check_controls()
    start=perf_counter()
    groups={}
    counts=Counter()
    for read,unread in ((6,9),(9,6)):
        shadows=set()
        for a,b,c in product(range(12),repeat=3):
            T=list((1,2,3,0,5,6,10,8,9,10,0,0))
            T[read],T[unread],T[10],T[11]=10,a,b,c
            F=forced_edges(T)
            counts["assignments"]+=1
            if not coherent(12,F):
                continue
            constraints=F+event_edges(T,(4,7),2)
            cert=full_shadow_certificate(12,constraints,(0,1,2,3))
            if cert:
                shadow=frozenset(range(16))
                counts["full_certificate"]+=1
            else:
                shadow=exhaustive_shadow(12,constraints,(0,1,2,3))
                counts["oracle_fallback"]+=1
            counts["coherent"]+=1
            if counts["coherent"] % 97==0:
                exact=exhaustive_shadow(12,constraints,(0,1,2,3))
                assert exact==shadow
                counts["independent_rechecks"]+=1
            shadows.add(shadow)
            if len(shadows)>1:
                print("counterexample",read,T,sorted(map(sorted,shadows)))
                return
        groups[read]=sorted(map(len,shadows))
    print(dict(counts),"groups",groups,"seconds",round(perf_counter()-start,6))
if __name__=="__main__":
    main()
