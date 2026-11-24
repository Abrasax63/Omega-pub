"""INTERACT01: bounded black-box intervention and conditional law recovery."""
import itertools as it
import json,random
from collections import Counter
from pathlib import Path
N=6
STATES=tuple(range(1<<N))
MONOMIALS=[0]+[1<<i for i in range(N)]+[(1<<i)|(1<<j) for i,j in it.combinations(range(N),2)]
K=len(MONOMIALS)
assert K==22
FEATURE={x:sum(1<<i for i,m in enumerate(MONOMIALS) if x&m==m) for x in STATES}
def apply(coef,row):
    out=0
    for i,c in enumerate(coef):
        if row>>i&1:out^=c
    return out

def insert(basis,row,y):
    while row:
        k=row.bit_length()-1
        if k not in basis:
            basis[k]=(row,y);return True,True
        r,v=basis[k];row^=r;y^=v
    return False,y==0

def fit(examples):
    basis={}
    for x,y in examples:
        _,ok=insert(basis,FEATURE[x],y)
        if not ok:return None,len(basis),"INCONSISTENT"
    if len(basis)<K:return None,len(basis),"UNDERDETERMINED"
    coef=[]
    for i in range(K):
        row,y=basis[i]
        coef.append(y^apply(coef,row))
    assert all(apply(coef,FEATURE[x])==y for x,y in examples)
    return coef,K,"IDENTIFIED_CONDITIONAL"

def random_basis(rng):
    while True:
        cols=[rng.randrange(1,64) for _ in range(N)]
        mapping=[apply(cols,x) for x in STATES]
        if len(set(mapping))==64:return mapping

def teachers():
    rng=random.Random(20261127);seen=set()
    for kind in ("affine","quadratic","cubic"):
        for idx in range(24):
            while True:
                co=[rng.randrange(64) for _ in range(7)]+([0]*15 if kind=="affine" else [rng.randrange(64) for _ in range(15)])
                if kind!="affine" and not any(co[7:]):continue
                cubic=sum(1<<i for i in rng.sample(range(N),3)) if kind=="cubic" else 0
                value=rng.randrange(1,64) if cubic else 0
                t=[apply(co,FEATURE[x])^(value if cubic and x&cubic==cubic else 0) for x in STATES]
                if idx%2:
                    m=random_basis(rng);inv={v:i for i,v in enumerate(m)}
                    t=[inv[t[m[x]]] for x in STATES]
                if tuple(t) in seen:continue
                seen.add(tuple(t));break
            yield kind,idx,tuple(t)

def agent(query,arm,seed):
    rng=random.Random(seed);order=list(STATES);rng.shuffle(order)
    selected=[];basis={}
    if arm=="fixed":
        selected=[x for x in STATES if x.bit_count()<=2]
    elif arm=="passive":selected=order[:K]
    elif arm=="rank":
        for x in order:
            independent,_=insert(basis,FEATURE[x],0)
            if independent:selected.append(x)
            if len(selected)==K:break
    else:raise ValueError("ARM")
    assert len(selected)==len(set(selected))==K
    observations=[(x,query(x)) for x in selected]
    co,rank,status=fit(observations)
    validation=rng.sample([x for x in STATES if x not in selected],8)
    tests=[(x,query(x)) for x in validation]
    mismatch=[(x,y) for x,y in tests if co is not None and apply(co,FEATURE[x])!=y]
    if mismatch:status="REFUTED"
    candidate=co if status=="IDENTIFIED_CONDITIONAL" else None
    return dict(status=status,rank=rank,observations=observations,validation=tests,
                mismatch=mismatch,coefficients=candidate,query_count=len(observations)+len(tests))

def evaluate(t,r):
    c=r["coefficients"]
    if c is None:return dict(exact=False,rollout_exact=False,mismatches=None)
    pred=[apply(c,FEATURE[x]) for x in STATES]
    mismatch=sum(a!=b for a,b in zip(t,pred))
    def rollout(table,x):
        path=[]
        for _ in range(5):
            x=table[x];path.append(x)
        return path
    return dict(exact=mismatch==0,rollout_exact=all(rollout(t,x)==rollout(pred,x) for x in STATES),mismatches=mismatch)

def main(path):
    stats={arm:{kind:Counter() for kind in ("affine","quadratic","cubic")} for arm in ("rank","passive","fixed")}
    records=[]
    for kind,idx,t in teachers():
        for arm in stats:
            calls=[]
            def query(x):
                assert type(x) is int and x in STATES and x not in calls
                calls.append(x);return t[x]
            r=agent(query,arm,20261128+100*idx+10000*("affine","quadratic","cubic").index(kind))
            assert len(calls)==30
            e=evaluate(t,r);s=stats[arm][kind]
            s["tasks"]+=1;s["exact"]+=int(e["exact"]);s["rollout_exact"]+=int(e["rollout_exact"])
            s["rank_sum"]+=r["rank"];s["conditional"]+=int(r["status"]=="IDENTIFIED_CONDITIONAL")
            s["refuted"]+=int(r["status"]=="REFUTED");s["underdetermined"]+=int(r["status"]=="UNDERDETERMINED")
            s["wrong_candidate"]+=int(r["coefficients"] is not None and not e["exact"])
            records.append(dict(arm=arm,kind=kind,idx=idx,transformed=bool(idx%2),truth_table=t,**r,**e))
    exact=lambda a:sum(stats[a][k]["exact"] for k in ("affine","quadratic"))
    primary=exact("rank")==48 and exact("rank")>=exact("passive")
    promote=primary and stats["rank"]["cubic"]["wrong_candidate"]==0
    result=dict(stats=stats,primary_pass=primary,promote=promote,records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("INTERACT_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
