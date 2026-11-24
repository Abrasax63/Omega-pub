"""ARCH-LOCAL01: finite policy learning on local residual features."""
import argparse,hashlib,itertools as it,json,random,signal,statistics,time
from collections import Counter
from pathlib import Path
import arch_gate01 as gate
import arch_switch01 as prev
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm,CPU,reference
GRID=list(it.product((4,10),(4,8,12),(0,512)))
def cohort(train):
    rng=random.Random(20270111 if train else 20270112)
    for n in ((18,32,64) if train else (16,24,40,56,72)):
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
def solve(n,e,policy):
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
                if isinstance(policy,int) and ((policy==-1 and depth==0) or (policy>=0 and stats["visits"]>=policy)):
                    ans,method=structural(adj,mask,stats)
                    if ans is None and m>=4 and sum((adj[v]&mask).bit_count() for v in bits(mask))<=4*m:
                        ans=eliminate(adj,mask,stats)
                        if ans is not None:method="elimination"
                elif not isinstance(policy,int):
                    sm,em,delay=policy
                    if m>=min(sm,em):
                        ds=sum((adj[v]&mask).bit_count() for v in bits(mask))
                        stats["local_features"]+=1
                        if m>=sm and (ds==2*(m-1) or ds>=.7*m*(m-1)):
                            ans,method=structural(adj,mask,stats)
                        if ans is None and m>=em and stats["visits"]>=delay and ds<=4*m:
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
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(prev.__file__),Path(gate.__file__),Path(core.__file__))}
def key(t):return ",".join(map(str,t))
def train(out):
    signal.signal(signal.SIGPROF,alarm)
    costs={key(t):0. for t in GRID};records=[]
    for j,(n,f,e,h,p) in enumerate(cohort(True)):
        ref,kind=reference(n,f,e,h,p);order=GRID[:];random.Random(20270113+j).shuffle(order)
        rs={key(t):[solve(n,e,t)] for t in order}
        gate.audit(rs,ref)
        for k,r in rs.items():costs[k]+=r[0]["cost"]
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs))
    chosen=min(GRID,key=lambda t:(costs[key(t)],t))
    obj=dict(hashes=hashes(),costs=costs,chosen=chosen,training_runs=len(records)*len(GRID),total_capped_cost=sum(costs.values()),records=records)
    Path(out).write_text(json.dumps(obj,indent=2))
    print("LOCAL_TRAIN",json.dumps({k:v for k,v in obj.items() if k!="records"}),flush=True)
def evaluate(checkpoint,out):
    signal.signal(signal.SIGPROF,alarm)
    ck=json.loads(Path(checkpoint).read_text());assert ck["hashes"]==hashes()
    data=list(cohort(False));assert len(data)==40 and len({(n,e) for n,f,e,h,p in data})==40
    assert not {(n,e) for n,f,e,h,p in data}&{(n,e) for n,f,e,h,p in cohort(True)}
    policies={"always":0,"delay":512,"branch":4097,"root":-1,"fixed_local":(4,8,512),"learned":tuple(ck["chosen"])}
    stats={a:Counter() for a in policies};refs=Counter();paired=Counter();records=[];switch_cases=0;preserved=True
    families={str(f):{a:Counter() for a in policies} for f in range(8)}
    for j,(n,f,e,h,p) in enumerate(data):
        ref,kind=reference(n,f,e,h,p);refs[kind]+=1
        unique=list(dict.fromkeys(policies.values()));rs={t:[] for t in unique}
        for k in range(3):
            order=unique[:];random.Random(20270114+3*j+k).shuffle(order)
            for t in order:rs[t].append(solve(n,e,t))
        gate.audit(rs,ref)
        med={a:statistics.median(r["cost"] for r in rs[t]) for a,t in policies.items()}
        done={a:sum(r["count"] is not None for r in rs[t])>=2 for a,t in policies.items()}
        for a,t in policies.items():
            s=stats[a];family=families[str(f)][a]
            for z in (s,family):
                z["verified"]+=int(ref is not None and done[a]);z["unverified"]+=int(ref is None and done[a]);z["unresolved"]+=int(not done[a]);z["all_cost"]+=med[a]
                if ref is not None:z["verified_cost"]+=med[a]
            for name in ("visits","factor_lookups","structural_probes","elimination_probes","local_features","dispatch_tree","dispatch_elimination","dispatch_multipartite"):s[name]+=rs[t][0]["stats"].get(name,0)
            s["switches"]+=len(rs[t][0]["transitions"])
        if ref is not None:
            if done["delay"] and not done["learned"]:preserved=False
            if done["learned"] and any(r["count"] is not None and r["transitions"] for r in rs[policies["learned"]]):switch_cases+=1
            if all(done[a] for a in ("learned","branch","delay","fixed_local")):
                paired["cases"]+=1
                for a in ("learned","branch","delay","fixed_local"):paired[a]+=med[a]
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results={a:rs[t] for a,t in policies.items()},median_cost=med,completed=done))
        print("LOCAL_CASE",n,f,kind,{a:[done[a],round(med[a],6)] for a in policies},flush=True)
    l=stats["learned"];d=stats["delay"]
    gains={a:1-l["verified_cost"]/stats[a]["verified_cost"] if stats[a]["verified_cost"] else 0 for a in ("delay","fixed_local")}
    passed=l["verified"]>=d["verified"] and (l["unverified"]<=d["unverified"] or l["verified"]>d["verified"]) and all(v>=.15 for v in gains.values()) and paired["learned"]<=1.5*paired["branch"] and switch_cases>0
    result=dict(stats=stats,references=refs,paired=paired,chosen=ck["chosen"],gains=gains,preserved_delay=preserved,switch_verified_cases=switch_cases,primary_pass=passed,families=families,training_cost=ck["total_capped_cost"],records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("LOCAL_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("records","families")}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
