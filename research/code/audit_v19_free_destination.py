from collections import Counter
from itertools import product
from time import perf_counter
from audit_v19_shadow_guard import exhaustive_shadow
from audit_v19_one_read_completions import completion_shadows
from test_v19_locality_l_plus_1 import forced_edges, coherent, event_edges

def main():
    negative = completion_shadows((1,2,0,3,4,3,4,5,6,0),(0,1,2),(7,8),2,4,
                                  ((7,5,3),(8,6,4)))
    assert len(negative)>1
    start=perf_counter()
    for read, unread in ((7,11),(11,7)):
        counts=Counter()
        examples={}
        for a,b in product(range(13),repeat=2):
            T=list((1,2,3,0,5,6,7,12,9,10,11,12,0))
            T[read],T[unread],T[12]=12,a,b
            F=forced_edges(T)
            if not coherent(13,F):
                continue
            shadow=exhaustive_shadow(13,F+event_edges(T,(4,8),3),(0,1,2,3))
            counts[len(shadow)]+=1
            examples.setdefault(len(shadow),tuple(T))
        print(read, sorted(counts.items()), examples)
    print("seconds",round(perf_counter()-start,6))
if __name__=="__main__":
    main()
