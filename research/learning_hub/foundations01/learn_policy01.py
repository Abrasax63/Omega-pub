"""LEARN-POLICY01: reward-only persistent control policy, frozen exact engine."""
import argparse,hashlib,itertools as it,json,math,random,time
from collections import Counter
from pathlib import Path
from net_irreg01 import bitset_reference

CAP=4096
BEFORE=(1.,0.,0.,0.,0.)
FIXED={"before":BEFORE,"min_degree":(-1.,0.,0.,0.,0.),"neighbor_degree":(0.,1.,0.,0.,0.)}
def bits(x):
    while x:
        b=x&-x;x^=b;yield b.bit_length()-1
def make_graph(n,edges):
    adj=[0]*n
    for a,b in edges:adj[a]|=1<<b;adj[b]|=1<<a
    return tuple(adj)
def cohort(train):
    rng=random.Random(20261212 if train else 20261213)
    data=[]
    for n in ((12,16,20) if train else (16,20,24,32,48,64)):
        for i in range(8):
            p=(.12,.25,.4,.6)[i%4]
            edges=[]
            for a,b in it.combinations(range(n),2):
                prob=p if train or i<4 or (a<n//2)==(b<n//2) else p/8
                if rng.random()<prob:edges.append((a,b))
            data.append((n,i,tuple(edges)))
    assert len(set(data))==len(data)
    return data
class Budget(Exception):pass
def solve(n,edges,weights):
    adj=make_graph(n,edges);memo={};visits=0;hits=0
    def rec(mask):
        nonlocal visits,hits
        if visits>=CAP:raise Budget
        visits+=1
        if mask in memo:hits+=1;return memo[mask]
        if not mask:return 1
        iso=sum(1<<v for v in bits(mask) if not adj[v]&mask)
        if iso:
            ans=(1<<iso.bit_count())*rec(mask^iso)
        else:
            first=mask&-mask;part=first;front=first
            while front:
                nxt=0
                for v in bits(front):nxt|=adj[v]&mask&~part
                part|=nxt;front=nxt
            if part!=mask:
                ans=rec(part)*rec(mask^part)
            else:
                size=mask.bit_count()
                ds={v:(adj[v]&mask).bit_count() for v in bits(mask)}
                def score(v):
                    ns=adj[v]&mask;d=ds[v]
                    mean=sum(ds[u] for u in bits(ns))/max(1,d*size)
                    internal=sum((adj[u]&ns).bit_count() for u in bits(ns))/max(1,d*(d-1))
                    leaves=sum(ds[u]==1 for u in bits(ns))/max(1,d)
                    f=(d/size,mean,internal,leaves,-v/max(1,n-1))
                    return sum(a*b for a,b in zip(weights,f))
                v=max(ds,key=lambda v:(score(v),-v))
                rem=mask^(1<<v)
                ans=rec(rem)+rec(rem&~adj[v])
        if len(memo)<CAP:memo[mask]=ans
        return ans
    start=time.perf_counter()
    try:ans=rec((1<<n)-1)
    except Budget:ans=None
    return dict(count=ans,visits=visits,hits=hits,seconds=time.perf_counter()-start)
def reference(n,edges):
    if n<=20:
        return bitset_reference(n,[(a,b,0,0) for a,b in edges])[0],"BITSET"
    # Independent literal-branch evaluator: selecting a zero forces
    # all incident neighbors to one. No cache or component factorization.
    adj=make_graph(n,edges);calls=0
    def rec(remaining):
        nonlocal calls
        calls+=1
        if calls>65536:raise Budget
        if not remaining:return 1
        constrained=[v for v in bits(remaining) if adj[v]&remaining]
        if not constrained:return 1<<remaining.bit_count()
        v=constrained[0];rest=remaining^(1<<v)
        return rec(rest)+rec(rest&~adj[v])
    try:return rec((1<<n)-1),"BRANCH"
    except Budget:return None,"REFERENCE_LIMIT"
def train(out):
    data=cohort(True)
    gold=[reference(n,e)[0] for n,i,e in data]
    rng=random.Random(20261214);w=BEFORE;trace=[];all_calls=0
    def reward(candidate):
        nonlocal all_calls
        rs=[solve(n,e,candidate) for n,i,e in data]
        all_calls+=sum(r["visits"] for r in rs)
        # Separate correctness gate, no truth values passed to optimizer.
        assert all(r["count"] is None or r["count"]==g for r,g in zip(rs,gold))
        return sum(r["visits"] if r["count"] is not None else CAP+1 for r in rs)
    loss=reward(w);initial=loss
    for step in range(40):
        candidate=tuple(v+rng.gauss(0,.65) for v in w)
        cost=reward(candidate);accept=cost<loss
        if accept:w,loss=candidate,cost
        trace.append(dict(step=step,candidate=candidate,cost=cost,accepted=accept,incumbent_cost=loss))
    result=dict(weights=w,initial=initial,final=loss,training_visits=all_calls,trace=trace,engine_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(out).write_text(json.dumps(result,indent=2))
    print("LEARN_POLICY_TRAIN",json.dumps({k:v for k,v in result.items() if k!="trace"}),flush=True)
def evaluate(checkpoint,out):
    model=json.loads(Path(checkpoint).read_text())
    assert model["engine_sha256"]==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    w=tuple(model["weights"]);assert len(w)==5 and all(math.isfinite(x) for x in w)
    data=cohort(False)
    assert not {(n,e) for n,i,e in data}&{(n,e) for n,i,e in cohort(True)}
    policies=dict(FIXED,learned=w);stats={a:Counter() for a in policies}
    paired={a:0 for a in policies};transfer={a:0 for a in policies};records=[];refk=Counter();common=0
    for n,i,e in data:
        ref,kind=reference(n,e);refk[kind]+=1
        rs={a:solve(n,e,v) for a,v in policies.items()}
        completed={r["count"] for r in rs.values() if r["count"] is not None}
        assert len(completed)<=1
        for a,r in rs.items():
            s=stats[a];s["cases"]+=1;s["visits"]+=r["visits"];s["seconds"]+=r["seconds"]
            s["verified"]+=int(ref is not None and r["count"] is not None)
            s["unverified"]+=int(ref is None and r["count"] is not None)
            s["unresolved"]+=int(r["count"] is None)
            if ref is not None and r["count"] is not None:assert r["count"]==ref
            records.append(dict(n=n,index=i,arm=a,reference=ref,reference_kind=kind,edges=e,**r))
        if ref is not None and all(r["count"] is not None for r in rs.values()):
            common+=1
            for a,r in rs.items():
                paired[a]+=r["visits"]
                if n>=24:transfer[a]+=r["visits"]
        print("LEARN_POLICY_CASE",n,i,kind,[(a,r["count"] is not None,r["visits"]) for a,r in rs.items()],flush=True)
    # Closed form controls, separate from primary holdout.
    controls=[]
    for n in (16,32,64):
        half=n//2
        for kind,e,ref in (("empty",[],1<<n),("complete",list(it.combinations(range(n),2)),n+1),("bipartite",list(it.product(range(half),range(half,n))),(1<<half)+(1<<(n-half))-1),("disjoint",list(it.combinations(range(half),2))+list(it.combinations(range(half,n),2)),(half+1)*(n-half+1))):
            for a,v in policies.items():
                r=solve(n,e,v);assert r["count"] is None or r["count"]==ref
                controls.append(dict(n=n,kind=kind,arm=a,reference=ref,**r))
    b,l=stats["before"],stats["learned"]
    passed=(l["verified"]>=b["verified"] and l["unverified"]<=b["unverified"] and paired["before"]>0 and paired["learned"]<=.85*paired["before"] and all(paired["learned"]<paired[a] for a in ("min_degree","neighbor_degree")))
    result=dict(stats=stats,reference_kinds=refk,paired_visits=paired,paired_transfer_visits=transfer,common_verified=common,primary_pass=passed,training={k:v for k,v in model.items() if k!="trace"},records=records,controls=controls)
    Path(out).write_text(json.dumps(result,indent=2))
    print("LEARN_POLICY_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("records","controls")}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
