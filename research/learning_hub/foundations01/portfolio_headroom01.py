"""PORTFOLIO-HEADROOM01: compare different exact graph counting engines."""
import itertools as it,json,random,signal,statistics,time,hashlib
from pathlib import Path
from collections import Counter
import learn_policy01 as core
import net_reduce01 as reduce
import net_decomp01 as decomp
CAP=.5
ARMS=("elimination","hybrid","branch","structural")
class Timeout(Exception):pass
def alarm(*args):raise Timeout
def cohort():
    rng=random.Random(20261221)
    for n in (12,16,20,32,48,64):
        for f in range(8):
            pairs=list(it.combinations(range(n),2))
            groups=None
            if f==0:
                e=[(rng.randrange(v),v) for v in range(1,n)]
            elif f==1:
                w=int(n**.5)
                e=[(a,b) for a,b in pairs if ((b-a==1 and a//w==b//w) or b-a==w) and rng.random()>.1]
                e+=rng.sample([p for p in pairs if p not in e],n//4)
            elif f in (2,3,4,7):
                def p(a,b):
                    same=(a<n//2)==(b<n//2)
                    return (.12 if f==2 else .42 if f==3 else (.45 if same else .035) if f==4 else (.03 if same else .4))
                e=[(a,b) for a,b in pairs if rng.random()<p(a,b)]
            elif f==5:
                groups=[list(range(i,n,3)) for i in range(3)]
                e=[(a,b) for a,b in pairs if a%3!=b%3]
            else:
                e=[(rng.randrange(v//(n//4)*(n//4),v),v) for v in range(1,n) if v%(n//4)]
            labels=list(range(n));rng.shuffle(labels)
            e=tuple(sorted({tuple(sorted((labels[a],labels[b]))) for a,b in e}))
            yield n,f,e,None if groups is None else [len(g) for g in groups]
def structural(n,e):
    adj=core.make_graph(n,e)
    remaining=(1<<n)-1;ans=1
    while remaining:
        first=remaining&-remaining;comp=front=first
        while front:
            z=0
            for v in core.bits(front):z|=adj[v]&remaining&~comp
            comp|=z;front=z
        remaining^=comp
        vs=list(core.bits(comp));size=len(vs)
        if sum((adj[v]&comp).bit_count() for v in vs)==2*(size-1):
            # Tree dynamic programming.
            def dp(v,p):
                a=b=1
                for u in core.bits(adj[v]&comp):
                    if u!=p:
                        x,y=dp(u,v);a*=x+y;b*=x
                return a,b
            ans*=sum(dp(vs[0],-1));continue
        # Complete multipartite iff complement is a union of cliques.
        rest=comp;parts=[];ok=True
        while rest:
            v=(rest&-rest).bit_length()-1
            part=comp&~adj[v]
            if part&~rest or any((comp&~adj[u])!=part for u in core.bits(part)):
                ok=False;break
            parts.append(part.bit_count());rest^=part
        if ok:
            ans*=1+sum((1<<s)-1 for s in parts);continue
        # Fall back once on whole input; prior component work is charged.
        return core.solve(n,e,core.BEFORE)["count"]
    return ans
def execute(n,e,arm):
    if arm=="branch":return core.solve(n,e,core.BEFORE)["count"]
    if arm=="structural":return structural(n,e)
    cs=[("or",(a,b),1) for a,b in e]
    if arm=="elimination":r=reduce.count(n,cs,"full")
    elif arm=="hybrid":r=decomp.count(n,cs,"clique")
    else:raise ValueError(arm)
    return r["count"] if r["status"]=="EXACT" else None
def timed(n,e,arm):
    start=time.process_time()
    signal.setitimer(signal.ITIMER_PROF,CAP)
    try:
        value=execute(n,e,arm)
        status="EXACT" if value is not None else "RESOURCE_LIMIT"
    except Timeout:
        value=None;status="CPU_LIMIT"
    finally:signal.setitimer(signal.ITIMER_PROF,0)
    sec=time.process_time()-start
    if sec>CAP:
        value=None;status="CPU_LIMIT"
    return dict(count=value,status=status,seconds=sec,cost=min(sec,CAP) if value is not None else CAP)
def reference(n,f,e,parts):
    if n<=20:return core.reference(n,e)
    if f==5:return 1+sum((1<<s)-1 for s in parts),"MULTIPARTITE_FORMULA"
    if f in (0,6):
        # Independent leaf-removal product DP with unary weights.
        adj=[set() for _ in range(n)]
        for a,b in e:adj[a].add(b);adj[b].add(a)
        z=[1]*n;o=[1]*n;active=set(range(n));total=1
        while active:
            v=min(v for v in active if len(adj[v])<=1)
            if adj[v]:
                u=next(iter(adj[v]));z[u]*=z[v]+o[v];o[u]*=z[v];adj[u].remove(v)
            else:total*=z[v]+o[v]
            active.remove(v);adj[v].clear()
        return total,"LEAF_DP"
    return core.reference(n,e)
def main(path):
    signal.signal(signal.SIGPROF,alarm)
    data=list(cohort());assert len(data)==48 and len({(n,e) for n,f,e,p in data})==48
    stats={a:Counter() for a in ARMS};refs=Counter();records=[];wins=Counter();families={};rep_cost={a:[0.]*3 for a in ARMS};oracle_rep=[0.]*3
    for j,(n,f,e,p) in enumerate(data):
        ref,kind=reference(n,f,e,p);refs[kind]+=1
        rs={a:[] for a in ARMS}
        for k in range(3):
            order=list(ARMS);random.Random(20261222+j*3+k).shuffle(order)
            for a in order:rs[a].append(timed(n,e,a))
        vals={r["count"] for rows in rs.values() for r in rows if r["count"] is not None}
        assert len(vals)<=1,(n,f,vals)
        if ref is not None:assert not vals or vals=={ref},(n,f,ref,vals)
        med={a:statistics.median(r["cost"] for r in rows) for a,rows in rs.items()}
        done={a:sum(r["count"] is not None for r in rows)>=2 for a,rows in rs.items()}
        for a in ARMS:
            s=stats[a];s["verified"]+=int(ref is not None and done[a]);s["unverified"]+=int(ref is None and done[a]);s["unresolved"]+=int(not done[a]);s["all_cost"]+=med[a]
            if ref is not None:
                s["verified_cost"]+=med[a]
                for k,r in enumerate(rs[a]):rep_cost[a][k]+=r["cost"]
        if ref is not None:
            best=min(ARMS,key=lambda a:med[a]);wins[best]+=1
            s=stats.setdefault("oracle",Counter());s["verified"]+=int(done[best]);s["verified_cost"]+=med[best]
            family=families.setdefault(str(f),Counter());family["cases"]+=1;family["oracle"]+=med[best]
            for a in ARMS:family[a]+=med[a]
            for k in range(3):oracle_rep[k]+=min(rs[a][k]["cost"] for a in ARMS)
        records.append(dict(n=n,family=f,edges=e,reference=ref,reference_kind=kind,results=rs,median_cost=med,completed=done))
        print("HEADROOM_CASE",n,f,kind,{a:(done[a],round(med[a],6)) for a in ARMS},flush=True)
    best=min(ARMS,key=lambda a:stats[a]["verified_cost"]);o=stats["oracle"]
    gain=1-o["verified_cost"]/stats[best]["verified_cost"]
    result=dict(stats=stats,reference_kinds=refs,best_fixed=best,oracle_gain=gain,oracle_vs_hybrid=1-o["verified_cost"]/stats["hybrid"]["verified_cost"],wins=wins,families=families,rep_cost=rep_cost,oracle_rep=oracle_rep,primary_pass=gain>=.15 and o["verified"]>=stats[best]["verified"],records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("HEADROOM_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
