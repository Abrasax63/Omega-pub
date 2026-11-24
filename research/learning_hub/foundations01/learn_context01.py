"""LEARN-CONTEXT01: frozen portfolio, learned cost-conditioned selection."""
import argparse,hashlib,itertools as it,json,math,random,statistics,time
from pathlib import Path
from collections import Counter
import learn_policy01 as core
PORTFOLIO={
 "degree":core.BEFORE,"min":(-1.,0.,0.,0.,0.),"neighbor":(0.,1.,0.,0.,0.),"zero":(0.,0.,0.,0.,0.),
 "hill_min":(1.7683436260486438,-0.726986303930904,-1.2171018123370745,1.0048395470450964,0.24130331201118463),
 "hill_neighbor":(1.6093270740999581,-0.3685906503324871,-0.46161511775970643,0.6991108750647762,-0.10381920689782659),
 "hill_zero":(2.098515230791202,-3.13870883513294,0.4305303482989483,0.8346448982601076,0.18600267691140343)}
ARMS=list(PORTFOLIO)
def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(core.__file__))}
def cohort(train):
    rng=random.Random(20261218 if train else 20261219)
    for n in ((12,16,20,24,32,48) if train else (16,20,24,32,48,64)):
        for family in range(8):
            pairs=list(it.combinations(range(n),2))
            if family in (0,1,2,6):
                def prob(a,b):
                    if family==0:return .12
                    if family==1:return .35
                    if family==2:return .38 if (a<n//2)==(b<n//2) else .045
                    return .025 if (a<n//2)==(b<n//2) else .35
                e=[(a,b) for a,b in pairs if rng.random()<prob(a,b)]
            elif family==3:
                e=[(0,1)];deg=[1,1]+[0]*(n-2)
                for v in range(2,n):
                    chosen=set()
                    while len(chosen)<min(2,v):
                        chosen.add(rng.choices(range(v),weights=[d+1 for d in deg[:v]])[0])
                    for u in sorted(chosen):e.append((u,v));deg[u]+=1;deg[v]+=1
            elif family==4:
                xy=[(rng.random(),rng.random()) for _ in range(n)]
                e=[(a,b) for a,b in pairs if math.dist(xy[a],xy[b])<.27]
            elif family==5:
                width=math.ceil(math.sqrt(n))
                e=[(a,b) for a,b in pairs if (b-a==1 and a//width==b//width) or b-a==width]
                e=[p for p in e if rng.random()>.12]
                e+=rng.sample([p for p in pairs if p not in e],max(1,n//5))
            else:
                e=[(a,b) for a,b in pairs if a<2 or rng.random()<.045]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,family,e
def features(n,e):
    adj=core.make_graph(n,e);d=[x.bit_count() for x in adj];mean=statistics.mean(d)
    clustering=[]
    for a,ns in enumerate(adj):
        if d[a]>=2:
            clustering.append(sum((adj[b]&ns).bit_count() for b in core.bits(ns))/(d[a]*(d[a]-1)))
        else:clustering.append(0.)
    return [2*len(e)/(n*(n-1)),statistics.pstdev(d)/max(mean,1e-12),statistics.mean(clustering),d.count(1)/n,max(d)/(n-1),float(n)]
def cost(r):return r["visits"] if r["count"] is not None else core.CAP+1
def run_all(n,e):
    return {a:core.solve(n,e,w) for a,w in PORTFOLIO.items()}
def audit(rs,ref):
    assert len({r["count"] for r in rs.values() if r["count"] is not None})<=1
    if ref is not None:
        assert all(r["count"] is None or r["count"]==ref for r in rs.values())
def train(path):
    rows=[];total_visits=0;refs=Counter()
    for n,f,e in cohort(True):
        rs=run_all(n,e);ref,kind=core.reference(n,e);refs[kind]+=1;audit(rs,ref)
        costs=[cost(rs[a]) for a in ARMS]
        rows.append(dict(features=features(n,e),costs=costs,normalized=[c/min(costs) for c in costs]))
        total_visits+=sum(r["visits"] for r in rs.values())
    cols=list(zip(*(r["features"] for r in rows)))
    mean=[statistics.mean(c) for c in cols];scale=[statistics.pstdev(c) or 1. for c in cols]
    best=min(range(len(ARMS)),key=lambda a:sum(r["costs"][a] for r in rows))
    ck=dict(hashes=hashes(),arms=ARMS,rows=rows,mean=mean,scale=scale,best_fixed=ARMS[best],training_visits=total_visits,refs=refs)
    Path(path).write_text(json.dumps(ck,indent=2))
    print("CONTEXT_TRAIN",json.dumps({k:v for k,v in ck.items() if k!="rows"}),flush=True)
def choose(x,ck,permutation):
    d=[sum(((a-b)/s)**2 for a,b,s in zip(x,row["features"],ck["scale"])) for row in ck["rows"]]
    close=sorted(range(len(d)),key=lambda i:(d[i],i))[:5]
    return ARMS[min(range(len(ARMS)),key=lambda a:sum(ck["rows"][permutation[i]]["normalized"][a] for i in close))]
def evaluate(checkpoint,path):
    ck=json.loads(Path(checkpoint).read_text());assert ck["hashes"]==hashes() and ck["arms"]==ARMS
    data=list(cohort(False));assert len(data)==48 and len({(n,e) for n,f,e in data})==48
    assert not {(n,e) for n,f,e in data}&{(n,e) for n,f,e in cohort(True)}
    identity=list(range(48));perms=[]
    for seed in range(5):
        p=identity.copy();random.Random(20261220+seed).shuffle(p);perms.append(p)
    rngs=[random.Random(20261225+i) for i in range(5)]
    stats={a:Counter() for a in ["degree","best_fixed","learned","oracle"]+[f"random{i}" for i in range(5)]+[f"shuffled{i}" for i in range(5)]}
    portfolio={a:Counter() for a in ARMS};records=[];refk=Counter();selected=Counter()
    for n,f,e in data:
        start=time.perf_counter();x=features(n,e);sel=choose(x,ck,identity);overhead=time.perf_counter()-start
        picked={"degree":"degree","best_fixed":ck["best_fixed"],"learned":sel}
        picked.update({f"random{i}":rng.choice(ARMS) for i,rng in enumerate(rngs)})
        picked.update({f"shuffled{i}":choose(x,ck,p) for i,p in enumerate(perms)})
        rs=run_all(n,e);ref,kind=core.reference(n,e);refk[kind]+=1;audit(rs,ref)
        picked["oracle"]=min(ARMS,key=lambda a:cost(rs[a]))
        selected[sel]+=1
        for a,r in rs.items():
            s=portfolio[a];s["selected_cost_verified"]+=cost(r) if ref is not None else 0
            s["verified"]+=int(ref is not None and r["count"] is not None)
            s["unverified"]+=int(ref is None and r["count"] is not None)
            s["unresolved"]+=int(r["count"] is None)
        for name,a in picked.items():
            r=rs[a];s=stats[name];s["verified"]+=int(ref is not None and r["count"] is not None)
            s["unverified"]+=int(ref is None and r["count"] is not None);s["unresolved"]+=int(r["count"] is None)
            s["total_capped"]+=cost(r);s["verified_capped"]+=cost(r) if ref is not None else 0
            s["verified_large_capped"]+=cost(r) if ref is not None and n>=24 else 0
            s["seconds"]+=r["seconds"]+(overhead if name=="learned" else 0)
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,features=x,picked=picked,portfolio=rs,selection_seconds=overhead))
        print("CONTEXT_CASE",n,f,kind,sel,picked["oracle"],flush=True)
    d,b,l,o=(stats[a] for a in ("degree","best_fixed","learned","oracle"))
    gains={a:1-l["verified_capped"]/stats[a]["verified_capped"] for a in ("degree","best_fixed")}
    headroom=1-o["verified_capped"]/d["verified_capped"]
    passed=all(v>=.15 for v in gains.values()) and l["verified"]>=max(d["verified"],b["verified"]) and l["unverified"]<=d["unverified"] and headroom>=.15
    paired={}
    for a in ("degree","best_fixed"):
        p=[r for r in records if r["reference"] is not None and all(r["portfolio"][r["picked"][k]]["count"] is not None for k in ("learned",a))]
        paired[a]={"cases":len(p),"learned":sum(r["portfolio"][r["picked"]["learned"]]["visits"] for r in p),"other":sum(r["portfolio"][r["picked"][a]]["visits"] for r in p)}
    result=dict(stats=stats,portfolio=portfolio,reference_kinds=refk,selected=selected,best_fixed=ck["best_fixed"],gains=gains,oracle_headroom=headroom,paired=paired,primary_pass=passed,training_visits=ck["training_visits"],records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("CONTEXT_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
