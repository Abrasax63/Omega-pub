"""NET-IRREG01: fresh signed constraint stress with independent references."""
import itertools as it
import json,random,time
from collections import Counter
from pathlib import Path
from net_reduce01 import reduce,count as base_count
from net_stress01 import eliminate,CAP
from net_decomp01 import forbidden,clauses_from
LIMIT=4096
CACHE_SLOTS=250000
class Budget(Exception):pass

def branch_count(n,cs,clique,cache=True,order='degree'):
    memo={};slots=0;stats=Counter()
    def restrict(cl,l):
        return tuple(tuple(x for x in c if x!=-l) for c in cl if l not in c)
    def rec(active,cl):
        nonlocal slots
        stats["visits"]+=1
        if stats["visits"]>LIMIT:raise Budget()
        while True:
            if any(not c for c in cl):return 0
            unit=next((c[0] for c in cl if len(c)==1),None)
            if unit is None:break
            active=active-{abs(unit)};cl=restrict(cl,unit)
            stats["units"]+=1
        cl=tuple(sorted(set(cl)))
        used={abs(x) for c in cl for x in c}
        assert used<=active
        multiplier=1<<(len(active)-len(used))
        if not cl:return multiplier
        if cache and cl in memo:
            stats["hits"]+=1
            return multiplier*memo[cl]
        adj={v:set() for v in used}
        signs={v:set() for v in used}
        for a,b in cl:
            adj[abs(a)].add(abs(b));adj[abs(b)].add(abs(a))
            signs[abs(a)].add(a>0);signs[abs(b)].add(b>0)
        left=set(used);components=[]
        while left:
            stack=[min(left)];part=set(stack);left-=part
            while stack:
                v=stack.pop();new=adj[v]&left
                part|=new;left-=new;stack.extend(new)
            components.append(part)
        if len(components)>1:
            stats["splits"]+=1
            value=1
            for part in components:
                value*=rec(part,tuple(c for c in cl if abs(c[0]) in part))
                if not value:break
        elif clique and len(cl)==len(used)*(len(used)-1)//2 and all(len(s)==1 for s in signs.values()) and all(len(a)==len(used)-1 for a in adj.values()):
            stats["cliques"]+=1
            value=len(used)+1
        else:
            v=min(used,key=lambda x:(-(len(signs[x])==2) if order=='balanced' else 0,-len(adj[x]),x))
            value=rec(used-{v},restrict(cl,v))+rec(used-{v},restrict(cl,-v))
        if cache and len(memo)<LIMIT and slots+len(cl)<=CACHE_SLOTS:
            memo[cl]=value;slots+=len(cl)
        return multiplier*value
    try:
        v=rec(set(range(1,n+1)),clauses_from(cs))
        return dict(status="EXACT",count=v,stats=dict(stats),cache_slots=slots,cache_entries=len(memo))
    except Budget:
        return dict(status="RESOURCE_LIMIT",count=None,stats=dict(stats),cache_slots=slots,cache_entries=len(memo))

def generate():
    rng=random.Random(20261210)
    for n in (12,16,20,32,64,128):
        for planted in (True,False):
            for ratio in (.8,1.2,2,4):
                h=[rng.randrange(2) for _ in range(n)]
                edges=rng.sample(list(it.combinations(range(n),2)),round(n*ratio))
                raw=[]
                for a,b in edges:
                    options=list(it.product((0,1),repeat=2))
                    if planted:options.remove((h[a],h[b]))
                    t=rng.choice(options);raw.append((a,b,*t))
                yield n,"planted" if planted else "unplanted",ratio,raw
    for n in (32,64,128):
        for p in (.15,.35):
            raw=[(a,b,0,0) for a,b in it.combinations(range(n),2) if rng.random()<p]
            yield n,"random_or",p,raw

def signed(raw):
    return tuple((a+1 if u==0 else -(a+1),b+1 if v==0 else -(b+1)) for a,b,u,v in raw)

def bitset_reference(n,raw):
    nb=(1<<n)//8;full=(1<<(1<<n))-1
    masks=[]
    for i in range(n):
        if i<3:data=bytes([sum(1<<k for k in range(8) if k>>i&1)])*nb
        else:
            b=1<<(i-3);data=(bytes(b)+bytes([255])*b)*(nb//(2*b))
        masks.append(int.from_bytes(data,"little"))
    valid=full
    for a,b,u,v in raw:
        aa=masks[a] if u else full^masks[a]
        bb=masks[b] if v else full^masks[b]
        valid&=full^(aa&bb)
    return valid.bit_count(),(valid&masks[0]).bit_count()

def independent_branch(n,raw,pin):
    # Independent direct clauses, no parity contraction, memo or components.
    clauses=signed(raw)+(((1,),) if pin else ())
    visits=0
    def rec(cl,left):
        nonlocal visits
        visits+=1
        if visits>LIMIT:raise Budget
        while True:
            if any(not c for c in cl):return 0
            if not cl:return 1<<left
            unit=next((c[0] for c in cl if len(c)==1),None)
            if unit is None:break
            cl=tuple(tuple(v for v in c if v!=-unit) for c in cl if unit not in c)
            left-=1
        v=min(abs(x) for c in cl for x in c)
        a=tuple(tuple(x for x in c if x!=-v) for c in cl if v not in c)
        b=tuple(tuple(x for x in c if x!=v) for c in cl if -v not in c)
        return rec(a,left-1)+rec(b,left-1)
    try:return rec(clauses,n),visits
    except Budget:return None,visits

def reference(n,raw,cs):
    if n<=20:return bitset_reference(n,raw),"EXHAUSTIVE_BITSET"
    a=eliminate(n,cs,"minfill")
    b=eliminate(n,cs+[("pin",(0,),1)],"minfill") if a["status"]=="EXACT" else None
    if b and b["status"]=="EXACT":return (a["count"],b["count"]),"UNCOMPRESSED_ELIMINATION"
    a,_=independent_branch(n,raw,False)
    if a is None:return None,"REFERENCE_LIMIT"
    b,_=independent_branch(n,raw,True)
    return ((a,b),"INDEPENDENT_BRANCH") if b is not None else (None,"REFERENCE_LIMIT")

def reduced_branch(m,rs,arm):
    if m is None:return dict(status="EXACT",count=0,stats={},cache_entries=0,cache_slots=0)
    if m==0:return dict(status="EXACT",count=1,stats={},cache_entries=0,cache_slots=0)
    return branch_count(m,rs,True,cache=arm!="nocache",order="balanced" if arm=="balanced" else "degree")

def paired(n,cs,arm):
    start=time.perf_counter()
    outputs=[]
    for pin in (False,True):
        constraints=cs+([("pin",(0,),1)] if pin else [])
        m,rs,_=reduce(n,constraints,True)
        r=reduced_branch(m,rs,arm)
        assert r["stats"].get("visits",0)<=LIMIT+1 and r["cache_entries"]<=LIMIT and r["cache_slots"]<=CACHE_SLOTS
        outputs.append(r)
        if r["status"]!="EXACT":break
    a=outputs[0];b=outputs[1] if len(outputs)>1 else None
    counts=(a["count"],b["count"]) if b is not None and b["status"]=="EXACT" else None
    if counts is not None:assert 0<=counts[1]<=counts[0]
    return dict(counts=counts,visits=sum(r["stats"].get("visits",0) for r in outputs),hits=sum(r["stats"].get("hits",0) for r in outputs),seconds=time.perf_counter()-start,outputs=outputs)

def pipeline(n,cs,branch):
    a=base_count(n,cs,"full")
    b=base_count(n,cs+[("pin",(0,),1)],"full") if a["status"]=="EXACT" else None
    if b is not None and b["status"]=="EXACT":
        return (a["count"],b["count"]),False
    # Same reduced problem and same exact search; reuse forced-branch result.
    return branch["counts"],True

def main(out):
    arms=("degree","nocache","balanced");stats={a:Counter() for a in arms};records=[]
    pairvis={a:0 for a in arms};cachevis={a:0 for a in ("degree","nocache")}
    refcounts=Counter()
    for n,kind,param,raw in generate():
        cs=[forbidden(a,b,(u,v)) for a,b,u,v in raw]
        ref,refkind=reference(n,raw,cs);refcounts[refkind]+=1
        current={}
        # Compute identical base once: pipeline result per arm reuses it.
        a=base_count(n,cs,"full")
        b=base_count(n,cs+[("pin",(0,),1)],"full") if a["status"]=="EXACT" else None
        base=(a["count"],b["count"]) if b is not None and b["status"]=="EXACT" else None
        if ref is not None and base is not None:assert base==ref
        for arm in arms:
            r=paired(n,cs,arm);current[arm]=r
            pipe=base if base is not None else r["counts"]
            s=stats[arm];s["cases"]+=1;s["visits"]+=r["visits"];s["hits"]+=r["hits"];s["seconds"]+=r["seconds"]
            s["branch_verified"]+=int(ref is not None and r["counts"] is not None)
            s["branch_unverified"]+=int(ref is None and r["counts"] is not None)
            s["branch_unresolved"]+=int(r["counts"] is None)
            s["pipeline_verified"]+=int(ref is not None and pipe is not None)
            s["pipeline_unverified"]+=int(ref is None and pipe is not None)
            s["pipeline_unresolved"]+=int(pipe is None)
            s["pipeline_fallback"]+=int(base is None)
            if ref is not None:
                if r["counts"] is not None:assert r["counts"]==ref,(n,kind,param,arm,r["counts"],ref)
                if pipe is not None:assert pipe==ref
            records.append(dict(n=n,kind=kind,param=param,clauses=raw,reference=ref,reference_kind=refkind,arm=arm,base=base,pipeline=pipe,**r))
        completed=[r["counts"] for r in current.values() if r["counts"] is not None]
        assert len(set(completed))<=1
        if ref is not None and all(current[a]["counts"] is not None for a in ("degree","balanced")):
            for a in ("degree","balanced"):pairvis[a]+=current[a]["visits"]
        if ref is not None and all(current[a]["counts"] is not None for a in cachevis):
            for a in cachevis:cachevis[a]+=current[a]["visits"]
        print("IRREG_CASE",n,kind,param,refkind,"base",base is not None,[(a,current[a]["counts"] is not None,current[a]["visits"],current[a]["hits"]) for a in arms],flush=True)
    d,b=stats["degree"],stats["balanced"]
    passed=(b["branch_verified"]>=d["branch_verified"] and b["branch_unverified"]<=d["branch_unverified"] and pairvis["balanced"]<=.8*pairvis["degree"] and pairvis["degree"]>0)
    cache_gain=stats["degree"]["hits"]>0 and cachevis["degree"]<cachevis["nocache"]
    result=dict(stats=stats,reference_counts=refcounts,paired_verified_visits=pairvis,cache_paired_visits=cachevis,primary_pass=passed,cache_gain=cache_gain,records=records)
    Path(out).write_text(json.dumps(result,indent=2))
    print("NET_IRREG_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
