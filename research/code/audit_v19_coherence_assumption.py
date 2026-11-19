from collections import Counter
from itertools import product
from time import perf_counter
from audit_v19_free_certificate import full_shadow_certificate, check_controls
from audit_v19_shadow_guard import exhaustive_shadow
from test_v19_locality_l_plus_1 import forced_edges, coherent, event_edges

def main():
    check_controls()
    start=perf_counter()
    for read,unread in ((6,9),(9,6)):
        counts=Counter()
        witnesses={}
        for a,b,c in product(range(12),repeat=3):
            T=list((1,2,3,0,5,6,10,8,9,10,0,0))
            T[read],T[unread],T[10],T[11]=10,a,b,c
            F=forced_edges(T)
            constraints=F+event_edges(T,(4,7),2)
            if coherent(12,F):
                assert full_shadow_certificate(12,constraints,(0,1,2,3))
                size=16
            else:
                size=0
            counts[size]+=1
            if size not in witnesses:
                exact=exhaustive_shadow(12,constraints,(0,1,2,3))
                assert len(exact)==size
                witnesses[size]=tuple(T)
        assert set(counts)=={0,16}
        print(read,dict(counts),"witnesses",witnesses)
    print("seconds",round(perf_counter()-start,6))
if __name__=="__main__":
    main()
