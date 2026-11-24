"""ARCH-GATE01: train a reversible dispatch gate, not a new exact solver."""
import argparse,hashlib,itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import arch_switch01 as prev
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm,CPU,reference
TH=(0,32,128,512,4097)
def cohort(train):
    rng=random.Random(20270107 if train else 20270108)
    for n in ((12,24,40,64) if train else (18,32,48,64)):
        for f in range(8):
            pairs=list(it.combinations(range(n),2));hubs=[];parts=None
            if f==0:e=[(rng.randrange(v),v) for v in range(1,n)]
            elif f==1:
                e=[(v,v+1) for v in range(n-1)]+[(0,n-1)]
                e+=rng.sample([p for p in pairs if p not in e],n//5)
            elif f in (2,3,7):
                def prob(a,b):
                    return .12 if f==2 else .42 if f==3 else (.4 if (a<n//2)==(b<n//2) else .035)
                e=[(a,b) for a,b in pairs if rng.random()<prob(a,b)]
            elif f==4:
                parts=[len(range(i,n,3)) for i in range(3)]
                e=[(a,b) for a,b in pairs if a%3!=b%3]
            else:
                h=1 if f==5 else 2;hubs=list(range(h))
                e=[(rng.randrange(h,v),v) for v in range(h+1,n) if rng.random()<.82]
                e += [(a,b) for a,b in pairs if a<h and (f==5 or rng.random()<.84)]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,[labels[v] for v in hubs],parts
def solve(n,e,threshold):
    adj=core.make_graph(n,e);memo={};stats=Counter();transitions=[]
    def rec(mask,depth):
        if stats["visits"]>=4096:raise Limit
        stats["visits"]+=1
        if mask in memo:
            stats["memo_hits"]+=1;return memo[mask]
        if not mask:return 1
        iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
        if iso:ans=(1<<iso.bit_count())*rec(mask^iso,depth+1)
        else:
            first=mask&-mask;part=front=first
            while front:
                z=0
                for v in bits(front):z|=adj[v]&mask&~part
                part|=z;front=z
            if part!=mask:
                stats["splits"]+=1
                ans=rec(part,depth+1)*rec(mask^part,depth+1)
            else:
                ans=None;method=None;m=mask.bit_count()
                if (threshold==-1 and depth==0) or (threshold>=0 and stats["visits"]>=threshold):
                    ans,method=structural(adj,mask,stats)
                    if ans is None and m>=4 and sum((adj[v]&mask).bit_count() for v in bits(mask))<=4*m:
                        ans=eliminate(adj,mask,stats)
                        if ans is not None:method="elimination"
                if ans is not None:
                    stats["dispatch_"+method]+=1
                    if depth>0:transitions.append(dict(depth=depth,size=m,method=method))
                else:
                    v=max(bits(mask),key=lambda u:((adj[u]&mask).bit_count(),-u))
                    rem=mask^(1<<v)
                    ans=rec(rem,depth+1)+rec(rem&~adj[v],depth+1)
        memo[mask]=ans
        return ans
    start=time.process_time();wall=time.perf_counter()
    signal.setitimer(signal.ITIMER_PROF,CPU)
    try:
        val=rec((1<<n)-1,0)
        status="EXACT" if val is not None else "WIDTH_LIMIT"
    except Limit:
        val=None;status="RESOURCE_LIMIT"
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    if sec>CPU:val=None;status="CPU_LIMIT"
    return dict(count=val,status=status,seconds=sec,wall=time.perf_counter()-wall,
                cost=min(sec,CPU) if val is not None else CPU,stats=dict(stats),transitions=transitions)

def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(prev.__file__),Path(core.__file__))}
def group(n,e):return "dense" if 2*len(e)/(n*(n-1))>=.25 else "sparse"
def audit(rs,ref):
    vals={r["count"] for rows in rs.values() for r in rows if r["count"] is not None}
    assert len(vals)<=1
    if ref is not None:assert not vals or vals=={ref}
def train(out):
    signal.signal(signal.SIGPROF,alarm)
    costs={g:{t:0. for t in TH} for g in ("dense","sparse")};records=[]
    for j,(n,f,e,h,p) in enumerate(cohort(True)):
        ref,kind=reference(n,f,e,h,p);g=group(n,e);rs={t:[] for t in TH}
        for k in range(2):
            order=list(TH);random.Random(20270109+j*2+k).shuffle(order)
            for t in order:rs[t].append(solve(n,e,t))
        audit(rs,ref)
        for t,rows in rs.items():costs[g][t]+=statistics.mean(r["cost"] for r in rows)
        records.append(dict(n=n,family=f,edges=e,group=g,reference=ref,reference_kind=kind,results=rs))
    selected={g:min(TH,key=lambda t:(costs[g][t],-t)) for g in costs}
    global_t=min(TH,key=lambda t:(sum(costs[g][t] for g in costs),-t))
    ck=dict(hashes=hashes(),costs=costs,global_threshold=global_t,density_thresholds=selected,records=records,training_runs=32*5*2)
    Path(out).write_text(json.dumps(ck,indent=2))
    print("GATE_TRAIN",json.dumps({k:v for k,v in ck.items() if k!="records"}),flush=True)
def evaluate(checkpoint,out):
    signal.signal(signal.SIGPROF,alarm)
    ck=json.loads(Path(checkpoint).read_text());assert ck["hashes"]==hashes()
    data=list(cohort(False));assert len(data)==32 and len({(n,e) for n,f,e,h,p in data})==32
    assert not {(n,e) for n,f,e,h,p in data}&{(n,e) for n,f,e,h,p in cohort(True)}
    arms=[str(t) for t in TH]+["root","global","density"]
    stats={a:Counter() for a in arms};refs=Counter();paired=Counter();records=[];preserve=True;switch_cases=0
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=reference(n,f,e,h,p);refs[kind]+=1;g=group(n,e)
        thresholds={str(t):t for t in TH}|{"root":-1,"global":ck["global_threshold"],"density":ck["density_thresholds"][g]}
        # Identical policies share the measured runs; no extra timing lottery.
        unique=sorted(set(thresholds.values()));rs={t:[] for t in unique}
        for k in range(3):
            order=unique[:];random.Random(20270110+3*j+k).shuffle(order)
            for t in order:rs[t].append(solve(n,e,t))
        audit(rs,ref)
        med={a:statistics.median(r["cost"] for r in rs[t]) for a,t in thresholds.items()}
        done={a:sum(r["count"] is not None for r in rs[t])>=2 for a,t in thresholds.items()}
        for a,t in thresholds.items():
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a]);s["all_cost"]+=med[a]
            for name in ("visits","factor_lookups","structural_probes","elimination_probes"):s[name]+=rs[t][0]["stats"].get(name,0)
            s["switches"]+=len(rs[t][0]["transitions"])
            if ref is not None:s["verified_cost"]+=med[a]
        if ref is not None:
            if done["0"] and not done["density"]:preserve=False
            if done["density"] and any(r["count"] is not None and r["transitions"] for r in rs[thresholds["density"]]):switch_cases+=1
            if all(done[a] for a in ("density","global","0","4097")):
                paired["cases"]+=1
                for a in ("density","global","0","4097"):paired[a]+=med[a]
        records.append(dict(n=n,family=f,group=g,edges=e,reference=ref,reference_kind=kind,thresholds=thresholds,results=rs,median_cost=med,completed=done))
        print("GATE_CASE",n,f,kind,{a:[done[a],round(med[a],6)] for a in arms},flush=True)
    d=stats["density"];b=stats["0"];glob=stats["global"]
    gains={a:1-d["verified_cost"]/stats[a]["verified_cost"] if stats[a]["verified_cost"] else 0 for a in ("0","global")}
    gate=d["verified"]>=b["verified"] and d["unverified"]<=b["unverified"] and all(v>=.15 for v in gains.values()) and paired["density"]<=1.5*paired["4097"] and switch_cases>0
    result=dict(stats=stats,references=refs,paired=paired,preserve_always=preserve,switch_verified_cases=switch_cases,gains=gains,primary_pass=gate,global_threshold=ck["global_threshold"],density_thresholds=ck["density_thresholds"],training_costs=ck["costs"],records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("GATE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
