"""LEARN-POLICY02: weak starts, paired mutation/global random controls."""
import argparse,hashlib,itertools as it,json,random,time
from collections import Counter
from pathlib import Path
import learn_policy01 as core
STARTS={"min":(-1.,0.,0.,0.,0.),"neighbor":(0.,1.,0.,0.,0.),"zero":(0.,0.,0.,0.,0.)}
def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(core.__file__))}
def train(out):
    data=core.cohort(True);gold=[core.reference(n,e)[0] for n,i,e in data]
    results={}
    for j,(name,start) in enumerate(STARTS.items()):
        rng=random.Random(20261216+j)
        noise=[tuple(rng.gauss(0,.65) for _ in range(5)) for _ in range(40)]
        for arm in ("hill","random"):
            visits=0;trace=[]
            def reward(w):
                nonlocal visits
                rs=[core.solve(n,e,w) for n,i,e in data]
                assert all(r["count"] is None or r["count"]==g for r,g in zip(rs,gold))
                visits+=sum(r["visits"] for r in rs)
                return sum(r["visits"] if r["count"] is not None else core.CAP+1 for r in rs)
            w=start;initial=loss=reward(w)
            for step,z in enumerate(noise):
                v=tuple(a+b for a,b in zip(w,z)) if arm=="hill" else z
                cost=reward(v);accepted=cost<loss
                if accepted:w,loss=v,cost
                trace.append(dict(step=step,weights=v,cost=cost,accepted=accepted))
            results[name+"_"+arm]=dict(weights=w,initial=initial,final=loss,accepted=sum(r["accepted"] for r in trace),training_visits=visits,trace=trace)
    obj=dict(hashes=hashes(),results=results)
    Path(out).write_text(json.dumps(obj,indent=2))
    print("POLICY02_TRAIN",json.dumps({k:{a:b for a,b in v.items() if a!="trace"} for k,v in results.items()}),flush=True)
def holdout():
    rng=random.Random(20261215)
    for n in (16,20,24,32,48,64):
        for i in range(8):
            p=(.12,.25,.4,.6)[i%4]
            e=tuple((a,b) for a,b in it.combinations(range(n),2) if rng.random()<(p if i<4 or (a<n//2)==(b<n//2) else p/8))
            yield n,i,e
def evaluate(checkpoint,out):
    ck=json.loads(Path(checkpoint).read_text());assert ck["hashes"]==hashes()
    data=list(holdout());assert len({(n,e) for n,i,e in data})==48
    assert not {(n,e) for n,i,e in data}&{(n,e) for n,i,e in core.cohort(True)+core.cohort(False)}
    policies={"strong":core.BEFORE,**{k+"_start":v for k,v in STARTS.items()},**{k:tuple(v["weights"]) for k,v in ck["results"].items()}}
    stats={k:Counter() for k in policies};records=[];refs=Counter()
    comparisons={(k,other):Counter() for k in STARTS for other in ("start","random","strong")}
    for n,i,e in data:
        ref,kind=core.reference(n,e);refs[kind]+=1
        rs={k:core.solve(n,e,w) for k,w in policies.items()}
        assert len({v["count"] for v in rs.values() if v["count"] is not None})<=1
        for k,r in rs.items():
            s=stats[k];s["verified"]+=int(ref is not None and r["count"] is not None);s["unverified"]+=int(ref is None and r["count"] is not None);s["unresolved"]+=int(r["count"] is None);s["visits"]+=r["visits"];s["seconds"]+=r["seconds"]
            if ref is not None and r["count"] is not None:assert r["count"]==ref
            records.append(dict(n=n,index=i,edges=e,reference=ref,reference_kind=kind,arm=k,**r))
        for (k,o),c in comparisons.items():
            a=rs[k+"_hill"];b=rs["strong" if o=="strong" else k+"_"+o]
            if ref is not None and a["count"] is not None and b["count"] is not None:
                c["common"]+=1;c["hill"]+=a["visits"];c["other"]+=b["visits"]
                if n>=24:c["transfer_common"]+=1;c["transfer_hill"]+=a["visits"];c["transfer_other"]+=b["visits"]
        print("POLICY02_CASE",n,i,kind,flush=True)
    decisions={}
    for (k,o),c in comparisons.items():
        a=stats[k+"_hill"];b=stats["strong" if o=="strong" else k+"_"+o]
        reduction=1-c["hill"]/c["other"] if c["other"] else None
        passed=reduction is not None and reduction>=(.20 if o=="start" else .15) and a["verified"]>=b["verified"] and a["unverified"]<=b["unverified"]
        decisions[k+"_"+o]=dict(**c,reduction=reduction,passed=passed)
    gates={o:sum(decisions[k+"_"+o]["passed"] for k in STARTS)>=2 for o in ("start","random","strong")}
    result=dict(stats=stats,references=refs,comparisons=decisions,gates=gates,training={k:{a:b for a,b in v.items() if a!="trace"} for k,v in ck["results"].items()},records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("POLICY02_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
