"""MEMORY-ARCH01: finite contextual equivalence, exact associative lookup."""
import itertools as it,json,random,time
from collections import Counter,defaultdict
from pathlib import Path
import compose_learn01 as c
import memory_dag01 as dag
from memory_prune01 import digest,require
ARMS=("scan","index","global_merge","context_quotient")
def signature(p,w):
    # Independent direct operations, no reliance on a previous domain.
    return tuple(c.evaluate_program(p,w))
def rank(entry):
    key,w=entry
    return len(w),w,key
def library(a):
    defs=a["definitions"];rows={}
    for k in range(1,5):
        for word in it.product(c.OPS,repeat=k):
            w="".join(word)
            if c.reduced(w):
                rows["flat:"+w]=w
                rows["variant:"+w+"RL"]=w+"RL"
    for k in defs:rows["archive:"+k]=dag.expand(defs,k)
    return rows
def eligible(rows,a,q):
    blocked=dag.blocked(a["definitions"],q)
    return {k:w for k,w in rows.items() if not(k.startswith("archive:") and k[8:] in blocked)}
def build(p,rows,mode):
    buckets=defaultdict(list);cost=0
    for k,w in rows.items():
        buckets[signature(p,w)].append((k,w));cost+=p*len(w)
    canonical={t:min(es,key=rank) for t,es in buckets.items()}
    if mode=="context_quotient":
        # Canonical index plus reversible membership. Keep all source rows.
        reverse={k:t for t,es in buckets.items() for k,w in es}
    else:reverse={}
    return dict(buckets=dict(buckets),canonical=canonical,reverse=reverse,
                primitive=cost,signature_entries=len(rows)*p,classes=len(buckets),members=len(rows))
def reference(p,rows):
    # Exhaustive independent evaluator, kept outside measured architecture cost.
    out={}
    for k,w in rows.items():
        vals=[]
        for x in range(p):
            for op in w:
                if op=="R":x=(x+1)%p
                elif op=="L":x=(x-1)%p
                elif op=="M":x=(x*2)%p
                elif op=="D":x=(x+p if x%2 else x)//2
                elif op=="S":x=1-x if x<2 else x
                else:raise ValueError(op)
            vals.append(x)
        t=tuple(vals);e=(k,w)
        if t not in out or rank(e)<rank(out[t]):out[t]=e
    return out
def queries(p,rows,prev,rng):
    ref=reference(p,rows);pool=sorted(ref)
    hits=rng.sample(pool,min(20,len(pool)));used=set(hits)
    split=set()
    if prev is not None:
        old=defaultdict(set)
        for w in rows.values():old[signature(prev,w)].add(signature(p,w))
        split=set().union(*(s for s in old.values() if len(s)>1)) if old else set()
    candidates=sorted(split-used);changed=rng.sample(candidates,min(10,len(candidates)))
    used.update(changed)
    fills=rng.sample(sorted(set(pool)-used),min(10-len(changed),len(set(pool)-used)))
    neg=[];seen=set()
    # Bounded negative generation; on small domains enumerate if necessary.
    for _ in range(10000):
        t=list(range(p));rng.shuffle(t);t=tuple(t)
        if t not in ref and t not in seen:
            neg.append(t);seen.add(t)
            if len(neg)==10:break
    if p<=7 and len(neg)<10:
        for t in it.permutations(range(p)):
            if t not in ref and t not in seen:
                neg.append(t);seen.add(t)
                if len(neg)==10:break
    return [(t,"hit") for t in hits]+[(t,"split") for t in changed]+[(t,"fill") for t in fills]+[(t,"negative") for t in neg],ref
def scan(p,rows,t):
    candidates=[];cost=checks=0
    for k,w in rows.items():
        cost+=p*len(w);checks+=p
        if signature(p,w)==t:candidates.append((k,w))
    return min(candidates,key=rank) if candidates else None,cost,checks
def main(path):
    old=json.loads(Path(__file__).with_name("MEMORY_DAG01_ARCHIVE.json").read_text())
    a=old["archive"];dag.verify(a,old["anchor"],old["journal"],old["head"])
    anchor=digest(a);rows=library(a)
    stats={k:Counter() for k in ARMS};records=[];cache={k:{} for k in ARMS if k!="scan"}
    global0=build(5,rows,"index")
    reps={k:w for k,w in global0["canonical"].values()}
    stats["global_merge"]["primitive"]+=global0["primitive"]
    stats["global_merge"]["signature_units"]+=global0["signature_entries"]
    stats["global_merge"]["global_classes"]=len(reps)
    contexts=[(5,[]),(7,[]),(11,["SM"]),(17,["SM"]),(5,[])]
    rng=random.Random(20270104);prev=None
    for i,(p,q) in enumerate(contexts):
        current=eligible(rows,a,q)
        qs,ref=queries(p,current,prev,rng);prev=p
        rct=Counter(kind for t,kind in qs);details={"context":i,"p":p,"quarantine":q,"queries":dict(rct),"eligible":len(current),"classes":len(ref),"arms":{}}
        for arm in ARMS:
            start=time.perf_counter();s=Counter();idx=None
            if arm!="scan":
                ck=(p,tuple(q))
                source=current if arm!="global_merge" else {k:w for k,w in reps.items() if k in current}
                if ck not in cache[arm]:
                    idx=build(p,source,arm);cache[arm][ck]=idx
                    s["rebuilds"]+=1;s["primitive"]+=idx["primitive"];s["build_primitive"]+=idx["primitive"]
                    s["signature_units"]+=idx["signature_entries"]
                else:idx=cache[arm][ck];s["reuse"]+=1
                s["class_entries"]=idx["classes"];s["member_entries"]=idx["members"]
                s["reverse_entries"]=len(idx["reverse"])
            for t,kind in qs:
                if arm=="scan":
                    found,cost,checks=scan(p,current,t);s["primitive"]+=cost;s["query_primitive"]+=cost;s["signature_units"]+=checks
                else:
                    s["signature_units"]+=p
                    if arm=="index":
                        es=idx["buckets"].get(t,());found=min(es,key=rank) if es else None
                    else:found=idx["canonical"].get(t)
                expected=ref.get(t);s["queries"]+=1
                if found:
                    require(found[0] in current and current[found[0]]==found[1])
                    require(signature(p,found[1])==t)
                s["false_miss"]+=int(expected is not None and found is None)
                s["false_match"]+=int(expected is None and found is not None)
                s["noncanonical"]+=int(found is not None and expected is not None and found!=expected)
                s["exact"]+=int(found==expected)
                records.append(dict(context=i,p=p,kind=kind,arm=arm,target=t,expected=expected,found=found))
            s["seconds"]=time.perf_counter()-start
            stats[arm].update(s);details["arms"][arm]=dict(s)
            if arm!="global_merge":require(s["false_miss"]==s["false_match"]==s["noncanonical"]==0)
        require(digest(a)==anchor)
        dag.verify(a,old["anchor"],old["journal"],old["head"])
        print("MEMARCH_CONTEXT",json.dumps(details),flush=True)
    gain=1-stats["context_quotient"]["primitive"]/stats["scan"]["primitive"]
    # An exact associative bucket and a canonical quotient produce the same
    # canonical answer; D stores an additional reverse membership map.
    require(stats["global_merge"]["false_miss"]>0)
    require(stats["index"]["exact"]==stats["context_quotient"]["exact"])
    result=dict(library_entries=len(rows),archive_evidence=len(a["evidence"]),archive_digest=anchor,
                stats=stats,gain=gain,safety_pass=True,utility_pass=gain>=.15,records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("MEMARCH_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
