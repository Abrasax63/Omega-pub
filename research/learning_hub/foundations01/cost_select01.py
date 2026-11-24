"""COST-SELECT01: learn cost only, never override the validity gate."""
import json,math,random,statistics,time
from collections import Counter
from pathlib import Path
from invariant_select01 import choose,solve,digest

def features(n,h):return [1.,float(n-2*h-3),math.log(h+1)]
def fit(rows):
    x=[features(r["n"],r["h"]) for r in rows]
    y=[math.log(r["times"]["causal_cone"]/r["times"]["direct"]) for r in rows]
    a=[[sum(v[i]*v[j] for v in x) for j in range(3)]+[sum(v[i]*z for v,z in zip(x,y))] for i in range(3)]
    for i in range(3):
        p=max(range(i,3),key=lambda j:abs(a[j][i]));a[i],a[p]=a[p],a[i]
        if abs(a[i][i])<1e-12:raise ValueError("SINGULAR")
        d=a[i][i];a[i]=[v/d for v in a[i]]
        for j in range(3):
            if j!=i:
                d=a[j][i];a[j]=[u-d*v for u,v in zip(a[j],a[i])]
    return [v[-1] for v in a]

def select(n,h,beta):
    p={"n":n,"h":h}
    valid=choose("rule90_histogram",p)
    if valid=="direct" or n==2*h+3:return "direct"
    method="causal_cone" if sum(a*b for a,b in zip(features(n,h),beta))<0 else "direct"
    return choose("rule90_histogram",p,method)

def timed(n,h,phase):
    p={"n":n,"h":h};valid=choose("rule90_histogram",p)
    methods=["direct"]+([valid] if valid!="direct" else [])
    samples={m:[] for m in methods};hist=None
    rng=random.Random(20261124+100*n+h+10000*phase)
    for _ in range(5):
        order=list(methods);rng.shuffle(order)
        for m in order:
            t=time.perf_counter_ns();r=solve("rule90_histogram",p,m);dt=(time.perf_counter_ns()-t)/1e9
            if hist is not None and r["histogram"]!=hist:raise ValueError("MISMATCH")
            hist=r["histogram"];samples[m].append(dt)
    return dict(n=n,h=h,samples=samples,times={m:statistics.median(v) for m,v in samples.items()},hist=hist)

def independent(n,h):
    counts=Counter()
    for mask in range(1<<n):
        x=[(mask>>i)&1 for i in range(n)];w=0
        for _ in range(h+1):
            w=2*w+int(x[-1]+x[0]+x[1]>=2)
            x=[x[(i-1)%n]^x[(i+1)%n] for i in range(n)]
        counts[str(w)]+=1
    return dict(counts)

def main(out):
    calibration=[timed(n,h,0) for n in (9,11,13,15) for h in range(7) if n>=2*h+3]
    beta=fit(calibration)
    frozen=dict(features=["intercept","slack","log(h+1)"],beta=beta,calibration_cases=[(r["n"],r["h"]) for r in calibration])
    print("COST_MODEL_FROZEN",json.dumps(frozen),flush=True)
    rows=[];sums=Counter();near=Counter()
    for n in (8,10,12,14):
        for h in range(7):
            r=timed(n,h,1);ts=r["times"];best=min(ts.values());p={"n":n,"h":h}
            methods={"direct":"direct","always_valid":choose("rule90_histogram",p),
                     "simple":"causal_cone" if n-2*h-3>=2 else "direct",
                     "learned":select(n,h,beta),"oracle":min(ts,key=ts.get)}
            for arm,m in methods.items():
                choose("rule90_histogram",p,m)
                sums[arm]+=ts[m];near[arm]+=int(ts[m]<=1.1*best)
            t=time.perf_counter_ns();selected=solve("rule90_histogram",p,methods["learned"]);elapsed=(time.perf_counter_ns()-t)/1e9
            gold=independent(n,h)
            if selected["histogram"]!=gold or r["hist"]!=gold:raise ValueError("INDEPENDENT_MISMATCH")
            r.update(methods=methods,selected_seconds=elapsed,exact=True);rows.append(r)
            print("COST_CASE",n,h,methods,ts,flush=True)
    primary=sums["learned"]<=1.15*sums["oracle"] and sums["learned"]<=min(sums["direct"],sums["always_valid"])
    preferred="simple" if sums["simple"]<=1.05*sums["learned"] else "learned" if primary else "no_promotion"
    result=dict(frozen=frozen,calibration=calibration,holdout=rows,aggregate_seconds=dict(sums),
                regret={k:v/sums["oracle"] for k,v in sums.items()},within_10_percent=dict(near),
                exact_cases=len(rows),unsafe_choices=0,primary_pass=primary,preferred=preferred)
    Path(out).write_text(json.dumps(result,indent=2))
    print("COST_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("calibration","holdout")}),flush=True)

if __name__=="__main__":
    import sys
    main(sys.argv[1])
