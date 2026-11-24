import itertools as it, json, math
from collections import Counter
from pathlib import Path

def orbit_key(t,p):
    n=len(t); ans=[]
    for s in it.permutations(range(n)):
        u=tuple(s[t[s.index(j)]] for j in range(n))
        v=tuple(p[s.index(j)] for j in range(n))
        ans.extend([(u,v),(u,tuple(1-x for x in v))])
    return min(ans)

def signature(t,p):
    # Label-invariant quantities: full defect count sequence, all-horizon exactness,
    # and number of spurious length-3 words (not merely endpoints).
    q={(p[i],p[t[i]]) for i in range(len(t))}; power=q; th=t; seen=set(); ds=[]
    while (frozenset(power),th) not in seen:
        seen.add((frozenset(power),th)); actual={(p[i],p[th[i]]) for i in range(len(t))}
        ds.append(len(power-actual)); power={(a,d) for a,b in power for c,d in q if b==c};th=tuple(t[j] for j in th)
    # raw recurrence period need not be intrinsic under arbitrary quotient,
    # but conjugacy preserves the full state pair and its first repetition.
    w={(p[i],p[t[i]],p[t[t[i]]]) for i in range(len(t))}
    m={(a,b,c) for a,b in q for d,c in q if b==d}
    return (tuple(ds),not any(ds),len(m-w))

def dynamics(n):
    reps={}; totals=Counter(); raw=0; failures=0
    for t in it.product(range(n),repeat=n):
        for p in it.product((0,1),repeat=n):
            if len(set(p))!=2:continue
            raw+=1;k=orbit_key(t,p);s=signature(t,p)
            if k not in reps:reps[k]=[signature(*k),0]
            v=reps[k];v[1]+=1;failures+=s!=v[0]
            totals['all_horizon_exact']+=s[1];totals['hidden_internal_defect']+=s[1] and s[2]>0
    weighted=Counter()
    for s,m in reps.values():
        weighted['all_horizon_exact']+=m*s[1];weighted['hidden_internal_defect']+=m*(s[1] and s[2]>0)
    assert totals==weighted and failures==0
    return dict(n=n,raw=raw,orbits=len(reps),saved=raw-len(reps),mismatches=failures,weighted=dict(weighted),direct=dict(totals))

EDGES=list(it.permutations(range(3),2))
def edges(m):return {e for i,e in enumerate(EDGES) if m>>i&1}
def key(m):
    es=edges(m);return min(sum(1<<EDGES.index((s[a],s[b])) for a,b in es) for s in it.permutations(range(3)))
def props(m):
    es=edges(m)
    return (any((a,b) in es and (b,c) in es and (a,c) not in es for a,b,c in it.permutations(range(3))),
            all((a,b) in es for a,b in [(0,1),(1,2)]) and (0,2) not in es)
def graph():
    groups={}
    for m in range(64):groups.setdefault(key(m),[]).append(m)
    global_errors=sum(props(m)[0]!=props(k)[0] for k,g in groups.items() for m in g)
    local_errors=sum(props(m)[1]!=props(k)[1] for k,g in groups.items() for m in g)
    witness=next(dict(rep=k,other=m,rep_edges=sorted(edges(k)),other_edges=sorted(edges(m)),rep_value=props(k)[1],other_value=props(m)[1]) for k,g in groups.items() for m in g if props(k)[1]!=props(m)[1])
    return dict(raw=64,orbits=len(groups),global_errors=global_errors,local_errors=local_errors,witness=witness)

def main():
    out={'dynamics':[dynamics(n) for n in (2,3,4)],'graphs':graph()}
    a=signature((0,0,2,2),(0,1,1,0));b=signature((1,0,0,1),(0,1,0,1))
    def words(t,p):return sorted({(p[i],p[t[i]],p[t[t[i]]]) for i in range(len(t))})
    out['unsafe_coarse_key']={'A':words((0,0,2,2),(0,1,1,0)),'B':words((1,0,0,1),(0,1,0,1)), 'both_delta_empty':a[1] and b[1], 'word_001_A':(0,0,1) in words((0,0,2,2),(0,1,1,0)),'word_001_B':(0,0,1) in words((1,0,0,1),(0,1,0,1))}
    print(json.dumps(out,indent=2));Path(__file__).with_name('results.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
