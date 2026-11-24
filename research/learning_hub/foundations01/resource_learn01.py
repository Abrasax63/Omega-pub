"""RESOURCE-LEARN01: budget matched granularity and worker allocation."""
import argparse,hashlib,itertools as it,json,random,signal,statistics,time,os,multiprocessing as mp
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import arch_local01 as local
import parallel01 as par
import arch_switch01 as prev
import arch_gate01 as gate
from arch_switch01 import core,bits,structural,eliminate,Limit,alarm,reference
ARMS=("direct","serial2","pool2","pool4")
# pool4 denotes four conditioning vertices, NOT four workers.
def cohort(train):
    rng=random.Random(20270124 if train else 20270125)
    for n in ((24,40,64) if train else (20,36,56,72)):
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
def solve(n,e,policy,cap,budget):
    adj=core.make_graph(n,e);memo={};stats=Counter();transitions=[]
    def rec(mask,depth):
        if stats["visits"]>=cap:raise Limit
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
    signal.setitimer(signal.ITIMER_PROF,budget)
    try:
        val=rec((1<<n)-1,0)
        status="EXACT" if val is not None else "WIDTH_LIMIT"
    except Limit:
        val=None;status="RESOURCE_LIMIT"
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    if sec>budget:val=None;status="budget_LIMIT"
    return dict(count=val,status=status,seconds=sec,wall=time.perf_counter()-wall,
                cost=min(sec,budget) if val is not None else budget,stats=dict(stats),transitions=transitions)



def frontier(n,e,k):
    adj=core.make_graph(n,e)
    selected=sorted(range(n),key=lambda v:(-adj[v].bit_count(),v))[:k]
    root=(1<<n)-1;fixed=sum(1<<v for v in selected);weights=Counter()
    for b in range(1<<len(selected)):
        chosen=[v for i,v in enumerate(selected) if b>>i&1]
        if any(adj[u]>>v&1 for u,v in it.combinations(chosen,2)):continue
        residual=root&~fixed
        for v in chosen:residual&=~adj[v]
        weights[residual]+=1
    return weights
def task(arg):
    n,e,mask,cap,budget=arg
    cpu=time.process_time()
    m,ee=par.induced(n,e,mask);r=solve(m,ee,(4,8,512),cap,budget)
    return dict(mask=mask,count=r["count"],cpu=time.process_time()-cpu,visits=r["stats"].get("visits",0),pid=os.getpid())
def action(n,e,a,pool):
    wall=time.perf_counter();cpu=time.process_time();rows=[]
    if a=="direct":
        r=solve(n,e,(4,8,512),8192,.8);val=r["count"];visits=r["stats"].get("visits",0)
    else:
        w=frontier(n,e,4 if a=="pool4" else 2)
        args=[(n,e,m,8192//len(w),.8/len(w)) for m in sorted(w,key=lambda m:(-m.bit_count(),m))]
        if a=="serial2":rows=[task(x) for x in args]
        else:rows=[f.result() for f in as_completed([pool.submit(task,x) for x in args])]
        val=par.combine(w,rows);visits=sum(r["visits"] for r in rows)
    c=time.process_time()-cpu+(sum(r["cpu"] for r in rows) if a.startswith("pool") else 0)
    t=time.perf_counter()-wall
    assert visits<=8192
    if c>1:val=None
    return dict(count=val,wall=t,cpu=c,visits=visits,tasks=len(rows),reward=t+.25*c+(1 if val is None else 0))
def ping(_):return os.getpid()
def stronger_reference(n,f,e,h,p):
    ref,kind=reference(n,f,e,h,p)
    # independent enumeration of all cliques of the complement.
    adj=core.make_graph(n,e);calls=0
    def rec(mask):
        nonlocal calls
        calls+=1
        if calls>500000:raise Limit
        total=1
        while mask:
            b=mask&-mask;mask^=b;v=b.bit_length()-1
            total+=rec(mask&~adj[v])
        return total
    try:val=rec((1<<n)-1)
    except Limit:return ref,kind
    assert ref is None or ref==val
    return val,kind if ref is not None else "COMPLEMENT_CLIQUES"
def features(n,e):
    d=[0]*n
    for a,b in e:d[a]+=1;d[b]+=1
    return [n,2*len(e)/(n*(n-1)),2*len(e)/n,max(d)]
def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(local.__file__),Path(par.__file__),Path(prev.__file__),Path(core.__file__))}
def collect(train):
    signal.signal(signal.SIGPROF,alarm);data=list(cohort(train))
    assert len(data)==(24 if train else 32)
    rows=[];hw=par.machine()
    start=time.perf_counter();cpu=time.process_time();child=par.child_cpu()
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context("fork"),initializer=par.init) as pool:
        list(pool.map(ping,range(4)))
        warm_wall=time.perf_counter()-start
        for j,(n,f,e,h,p) in enumerate(data):
            ref,kind=stronger_reference(n,f,e,h,p);rs={a:[] for a in ARMS}
            t=time.perf_counter();c=time.process_time();x=features(n,e)
            feature_wall=time.perf_counter()-t;feature_cpu=time.process_time()-c
            for k in range(3):
                order=list(ARMS);random.Random(20270126+1000*int(train)+3*j+k).shuffle(order)
                for a in order:rs[a].append(action(n,e,a,pool))
            gate.audit(rs,ref)
            med={a:{k:statistics.median(r[k] for r in rr) for k in ("wall","cpu","reward")} for a,rr in rs.items()}
            done={a:sum(r["count"] is not None for r in rr)>=2 for a,rr in rs.items()}
            rows.append(dict(n=n,family=f,edges=e,features=x,feature_wall=feature_wall,feature_cpu=feature_cpu,reference=ref,reference_kind=kind,results=rs,med=med,done=done))
            print("RESOURCE_CASE",int(train),n,f,kind,{a:[done[a],round(med[a]["reward"],6)] for a in ARMS},flush=True)
    # Includes reference generation and all benchmark work, not pure overhead.
    meta=dict(machine=hw,pool_warmup_wall=warm_wall,collection_wall=time.perf_counter()-start,collection_cpu=time.process_time()-cpu+par.child_cpu()-child)
    return rows,meta
def loss(rows,a):return sum(r["med"][a]["reward"] for r in rows)
def best(rows):return min(ARMS,key=lambda a:(loss(rows,a),a))
def train(out):
    rows,meta=collect(True);g=best(rows);candidates=[]
    for i in range(4):
        vs=sorted({r["features"][i] for r in rows})
        for a,b in zip(vs,vs[1:]):
            t=(a+b)/2;left=[r for r in rows if r["features"][i]<=t];right=[r for r in rows if r["features"][i]>t]
            if min(len(left),len(right))<4:continue
            l,r=best(left),best(right)
            candidates.append((loss(left,l)+loss(right,r),i,t,l,r))
    obj=dict(hashes=hashes(),global_action=g,stump=min(candidates),global_loss=loss(rows,g),fixed_losses={a:loss(rows,a) for a in ARMS},training_runs=len(rows)*len(ARMS)*3,meta=meta,records=rows)
    Path(out).write_text(json.dumps(obj,indent=2));print("RESOURCE_TRAIN",json.dumps({k:v for k,v in obj.items() if k!="records"}),flush=True)
def evaluate(ckpath,out):
    ck=json.loads(Path(ckpath).read_text());assert ck["hashes"]==hashes()
    rows,meta=collect(False);assert not {(r["n"],tuple(map(tuple,r["edges"]))) for r in rows}&{(r["n"],tuple(map(tuple,r["edges"]))) for r in ck["records"]}
    stats={a:Counter() for a in (*ARMS,"global","stump","oracle")};paired=Counter();refs=Counter();_,i,t,l,r=ck["stump"]
    for row in rows:
        refs[row["reference_kind"]]+=1;has=row["reference"] is not None
        choices={a:a for a in ARMS}
        choices.update({"global":ck["global_action"],"stump":l if row["features"][i]<=t else r,"oracle":min(ARMS,key=lambda a:row["med"][a]["reward"])})
        for a,c in choices.items():
            s=stats[a];done=row["done"][c];m=row["med"][c];fw=row["feature_wall"] if a=="stump" else 0;fc=row["feature_cpu"] if a=="stump" else 0
            s["verified"]+=int(has and done);s["unverified"]+=int(not has and done);s["unresolved"]+=int(not done)
            s["reward"]+=m["reward"]+fw+.25*fc;s["wall"]+=m["wall"]+fw;s["cpu"]+=m["cpu"]+fc;s["choose_"+c]+=1
            if has:s["verified_reward"]+=m["reward"]+fw+.25*fc
            if has and all(row["done"].values()):
                paired[a+"_wall"]+=m["wall"]+fw;paired[a+"_cpu"]+=m["cpu"]+fc
        paired["cases"]+=int(has and all(row["done"].values()))
        row["choices"]=choices
    b=min(ARMS,key=lambda a:stats[a]["verified_reward"]);s=stats["stump"];base=stats[b];g=stats["global"]
    gains={a:1-s["verified_reward"]/stats[a]["verified_reward"] for a in (b,"global")}
    passed=s["verified"]>=base["verified"] and (s["unverified"]<=base["unverified"] or s["verified"]>base["verified"]) and all(v>=.15 for v in gains.values()) and s["reward"]<=g["reward"]
    result=dict(stats=stats,paired=paired,references=refs,best_fixed=b,gains=gains,primary_pass=passed,global_action=ck["global_action"],stump=ck["stump"],meta=meta,records=rows)
    Path(out).write_text(json.dumps(result,indent=2));print("RESOURCE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
