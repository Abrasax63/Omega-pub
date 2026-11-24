"""ARCH-COMP01: same Boolean grammar, competing/factorized/fixed designs."""
import json,random,time,statistics
from collections import Counter
from pathlib import Path

STATES=range(64)
ATOMS=(0,1,2,3,4,8,16,32,12,48,5,18,33,10)
K=len(ATOMS)
FEATURE=[sum(1<<i for i,m in enumerate(ATOMS) if x&m==m) for x in STATES]
assert K==14 and len(set(ATOMS))==K

def predict(c,x):
    return (c&FEATURE[x]).bit_count()%2

def independent_degree_support(table):
    a=list(table)
    for i in range(6):
        for x in STATES:
            if x&(1<<i):a[x]^=a[x^(1<<i)]
    return {x for x in STATES if a[x]}

def teachers():
    rng=random.Random(20261201);seen=set()
    for kind,n in (("local",12),("history",24),("mixed",24),("outside",24)):
        for i in range(n):
            while True:
                if kind=="local":
                    c=rng.randrange(16)
                elif kind=="history":
                    c=rng.randrange(1,64)*16+rng.randrange(2)
                elif kind=="mixed":
                    c=rng.randrange(1<<K)
                    if not(c&14 and c&1008 and c&15360):continue
                else:
                    c=rng.randrange(1<<K)
                extra=rng.choice([x for x in STATES if x not in ATOMS]) if kind=="outside" else None
                table=tuple(predict(c,x)^int(extra is not None and x&extra==extra) for x in STATES)
                if table in seen:continue
                seen.add(table);break
            support=independent_degree_support(table)
            expected={m for j,m in enumerate(ATOMS) if c>>j&1}
            if extra is not None:expected.add(extra)
            assert support==expected
            assert (support.issubset(ATOMS))==(kind!="outside")
            yield kind,i,table

def insert(basis,row,y):
    while row:
        k=row.bit_length()-1
        if k not in basis:basis[k]=(row,y);return True,True
        r,v=basis[k];row^=r;y^=v
    return False,y==0

def solution(basis):
    c=0
    for k in sorted(basis):
        r,y=basis[k]
        c|=(y^((r&c).bit_count()%2))<<k
    return c

def interpolate(obs,k):
    # All submonomials of each atom are present in each prefix.
    c=0
    for i,m in sorted(enumerate(ATOMS[:k]),key=lambda z:z[1].bit_count()):
        c|=(obs[m]^predict(c,m))<<i
    assert all(predict(c,m)==obs[m] for m in ATOMS[:k])
    return c

def build_flat():
    # Bit j denotes coefficient assignment j, one precomputed partition per input.
    # Use bytearray instead of constructing the huge integer one bit at a time.
    masks=[]
    for row in FEATURE:
        data=bytearray((1<<K)//8)
        for c in range(1<<K):
            if (c&row).bit_count()%2:data[c>>3]|=1<<(c&7)
        masks.append(int.from_bytes(data,"little"))
    return masks,(1<<(1<<K))-1

def learn(oracle,arm,seed,flat=None):
    rng=random.Random(seed);order=list(STATES);rng.shuffle(order)
    high=[x for x in STATES if x.bit_count()>=3];rng.shuffle(high)
    obs={};trace=[];work=0
    def ask(x):
        assert x not in obs
        obs[x]=oracle(x)
        return obs[x]
    def result(c,reason):
        return dict(candidate=c,status="CONDITIONAL" if c is not None else "REFUTED",
                    queries=len(obs),observations=list(obs.items()),trace=trace,
                    abstract_selection_checks=work,reason=reason)
    if arm in ("progressive","fixed"):
        stages=[(4,3),(10,3),(14,8)] if arm=="progressive" else [(14,8)]
        offset=0
        for k,n in stages:
            for x in ATOMS[:k]:
                if x not in obs:ask(x)
            c=interpolate(obs,k)
            for x in high[offset:offset+n]:
                if x not in obs:ask(x)
            offset+=n
            bad=[x for x,y in obs.items() if predict(c,x)!=y]
            trace.append(dict(size=k,contradictions=bad))
            if not bad:return result(c,"VALIDATION_AGREES")
        return result(None,"CONTRADICTION")
    if arm=="flat":
        masks,space=flat
        while space.bit_count()>1:
            total=space.bit_count();best=-1;chosen=None
            for x in order:
                if x in obs:continue
                work+=1
                yes=(space&masks[x]).bit_count()
                score=min(yes,total-yes)
                if score>best:best=score;chosen=x
            assert best>0
            y=ask(chosen)
            space&=masks[chosen] if y else ~masks[chosen]
        assert space.bit_count()==1
        c=space.bit_length()-1
    elif arm=="network":
        basis={}
        # Nonzero residual row yields a balanced split of the affine space;
        # this is exactly the first max-information tie in the flat policy.
        for x in order:
            row=FEATURE[x];work+=1
            residual=row
            while residual:
                k=residual.bit_length()-1
                if k not in basis:break
                residual^=basis[k][0]
            if not residual:continue
            y=ask(x);new,ok=insert(basis,row,y)
            assert new and ok
            if len(basis)==K:break
        assert len(basis)==K
        c=solution(basis)
    else:raise ValueError("UNKNOWN_ARM")
    assert len(obs)==K and all(predict(c,x)==y for x,y in obs.items())
    checks=rng.sample([x for x in STATES if x not in obs],8)
    for x in checks:ask(x)
    bad=[x for x,y in obs.items() if predict(c,x)!=y]
    trace.append(dict(size=K,contradictions=bad))
    return result(None if bad else c,"CONTRADICTION" if bad else "VALIDATION_AGREES")

def main(out):
    data=list(teachers());arms=("progressive","flat","network","fixed")
    stats={a:{k:Counter() for k in ("local","history","mixed","outside")} for a in arms}
    timings={a:[] for a in arms};init_times=[];records=[]
    for rep in range(3):
        start=time.process_time();flat=build_flat();init=time.process_time()-start;init_times.append(init)
        trial={};order=list(arms);random.Random(20261202+rep).shuffle(order)
        for arm in order:
            start=time.process_time();results=[]
            for j,(kind,i,t) in enumerate(data):
                calls=[]
                def oracle(x):
                    assert type(x) is int and x in STATES and x not in calls
                    calls.append(x);return t[x]
                r=learn(oracle,arm,20261203+j,flat)
                assert len(calls)==r["queries"]<=(28 if arm=="progressive" else 22)
                results.append(r)
            timings[arm].append(time.process_time()-start+(init if arm=="flat" else 0))
            trial[arm]=results
        assert all(a["observations"]==b["observations"] and a["candidate"]==b["candidate"]
                   for a,b in zip(trial["flat"],trial["network"]))
        if rep==0:
            first=trial
            for arm,results in trial.items():
                for (kind,i,t),r in zip(data,results):
                    c=r["candidate"];wrong=None if c is None else sum(predict(c,x)!=t[x] for x in STATES)
                    s=stats[arm][kind]
                    s["tasks"]+=1;s["exact"]+=int(wrong==0)
                    s["wrong_candidate"]+=int(wrong is not None and wrong>0)
                    s["refuted"]+=int(c is None);s["queries"]+=r["queries"]
                    s["abstract_selection_checks"]+=r["abstract_selection_checks"]
                    records.append(dict(arm=arm,kind=kind,index=i,truth=t,mismatches=wrong,**r))
        else:assert trial==first
    totals={a:{k:sum(v[k] for v in d.values()) for k in sorted(set().union(*(set(v) for v in d.values())))} for a,d in stats.items()}
    med={a:statistics.median(v) for a,v in timings.items()}
    n=totals["network"]
    safety=n["wrong_candidate"]<=min(totals[a]["wrong_candidate"] for a in ("flat","fixed"))
    quality=n["exact"]==60
    cost=all(n["queries"]<=.8*totals[a]["queries"] or med["network"]<=.8*med[a] for a in ("flat","fixed"))
    # To meet the preregistered gate, one shared metric must beat both.
    cost=(all(n["queries"]<=.8*totals[a]["queries"] for a in ("flat","fixed")) or
          all(med["network"]<=.8*med[a] for a in ("flat","fixed")))
    result=dict(stats=stats,totals=totals,cpu_seconds=timings,median_cpu_seconds=med,flat_init_seconds=init_times,
                flat_network_trace_parity=True,quality=quality,safety=safety,cost=cost,primary_pass=quality and safety and cost,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("ARCH_COMP_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
