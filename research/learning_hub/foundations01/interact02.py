"""INTERACT02: outcome-dependent degree expansion, exact black-box oracle."""
import itertools as it
import json,random
from collections import Counter
from pathlib import Path
from interact01 import STATES,apply,random_basis

def monomials(d):
    return [sum(1<<i for i in subset) for k in range(d+1) for subset in it.combinations(range(6),k)]
def features(x,ms):
    return sum(1<<i for i,m in enumerate(ms) if x&m==m)
def interpolate(obs,d):
    ms=monomials(d)
    # Boolean lattice inversion on all low-weight points.
    co=[]
    for m in ms:
        v=obs[m]
        for j,s in enumerate(ms[:len(co)]):
            if s&m==s:v^=co[j]
        co.append(v)
    return ms,co
def predict(model,x):
    ms,co=model
    return apply(co,features(x,ms))
def teachers():
    rng=random.Random(20261129);seen=set()
    for degree in (1,2,3,4):
        for idx in range(24):
            while True:
                ms=monomials(degree)
                co=[rng.randrange(64) if m.bit_count()<=2 else 0 for m in ms]
                if degree>=3:
                    choices=[i for i,m in enumerate(ms) if m.bit_count()==degree]
                    co[rng.choice(choices)]=rng.randrange(1,64)
                elif not any(c for m,c in zip(ms,co) if m.bit_count()==degree):continue
                t=[predict((ms,co),x) for x in STATES]
                if idx%2:
                    p=random_basis(rng);inv={y:x for x,y in enumerate(p)}
                    t=[inv[t[p[x]]] for x in STATES]
                if tuple(t) not in seen:seen.add(tuple(t));break
            yield degree,idx,t
def agent(query,arm,seed):
    rng=random.Random(seed);high=[x for x in STATES if x.bit_count()>=4];rng.shuffle(high)
    obs={};trace=[];checks=[];offset=0
    stages=[(1,6),(2,6),(3,8)] if arm=="adaptive" else [(int(arm[-1]),20)]
    def ask(x):
        assert x not in obs
        obs[x]=query(x)
    for d,k in stages:
        for x in STATES:
            if x.bit_count()<=d and x not in obs:ask(x)
        model=interpolate(obs,d)
        for x in high[offset:offset+k]:
            ask(x);checks.append(x)
        offset+=k
        bad=[x for x,y in obs.items() if predict(model,x)!=y]
        trace.append(dict(degree=d,queries=len(obs),contradictions=bad))
        if not bad:
            return dict(status="CONDITIONAL",degree=d,model=model,queries=len(obs),observations=obs,trace=trace)
    return dict(status="REFUTED",degree=d,model=None,queries=len(obs),observations=obs,trace=trace)
def evaluate(t,r):
    if r["model"] is None:return False,False,None
    pred=[predict(r["model"],x) for x in STATES]
    wrong=sum(a!=b for a,b in zip(t,pred))
    def rollout(a,x):
        out=[]
        for _ in range(5):
            x=a[x];out.append(x)
        return out
    return wrong==0,all(rollout(t,x)==rollout(pred,x) for x in STATES),wrong
def independent_degree(t):
    # independent full-table Möbius transform
    c=t.copy()
    for i in range(6):
        for x in STATES:
            if x>>i&1:c[x]^=c[x^(1<<i)]
    return max((x.bit_count() for x in STATES if c[x]),default=0)
def main(path):
    arms=("fixed1","fixed2","fixed3","adaptive")
    stats={a:{d:Counter() for d in range(1,5)} for a in arms};records=[]
    for degree,idx,t in teachers():
        assert independent_degree(t)==degree
        for arm in arms:
            calls=[]
            def query(x):
                assert x in STATES and x not in calls
                calls.append(x);return t[x]
            r=agent(query,arm,20261130+100*degree+idx)
            assert len(calls)==r["queries"]<=62
            exact,roll,wrong=evaluate(t,r)
            s=stats[arm][degree]
            s["tasks"]+=1;s["exact"]+=int(exact);s["rollout_exact"]+=int(roll)
            s["wrong_candidate"]+=int(wrong is not None and wrong>0)
            s["refuted"]+=int(r["status"]=="REFUTED");s["queries"]+=r["queries"]
            s["degree_"+str(r["degree"])]+=1
            records.append(dict(arm=arm,teacher_degree=degree,index=idx,truth=t,exact=exact,rollout_exact=roll,mismatches=wrong,**r))
    totals={a:{k:sum(c[k] for c in by.values()) for k in sorted(set().union(*(set(c) for c in by.values())))} for a,by in stats.items()}
    a,f=totals["adaptive"],totals["fixed3"]
    savings=1-a["queries"]/f["queries"]
    passed=a["exact"]>=f["exact"] and a["wrong_candidate"]<=f["wrong_candidate"] and savings>=.20
    result=dict(stats=stats,totals=totals,query_savings=savings,primary_pass=passed,records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("INTERACT02_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
