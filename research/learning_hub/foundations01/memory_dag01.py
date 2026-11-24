"""MEMORY-DAG01: exact dependency closure, quarantine and recovery."""
import copy,json,random,tempfile,os
from pathlib import Path
import compose_learn01 as c
from memory_prune01 import digest,require
def expand(defs,key,stack=()):
    require(key in defs and key not in stack)
    d=defs[key];require(bool(d["parts"]))
    out=""
    for kind,v in d["parts"]:
        if kind=="primitive":
            require(v in c.OPS);out+=v
        else:
            require(kind=="ref");out+=expand(defs,v,stack+(key,))
    return out
def closure(defs,roots):
    out=set()
    def visit(k,stack):
        require(k in defs and k not in stack)
        if k in out:return
        for kind,v in defs[k]["parts"]:
            if kind=="ref":visit(v,stack+(k,))
        out.add(k)
    for k in roots:visit(k,())
    return out
def blocked(defs,q):
    require(len(set(q))==len(q) and set(q)<=set(defs))
    return {k for k in defs if closure(defs,[k])&set(q)}
def state(defs,roots,q):
    require(len(set(roots))==len(roots))
    dep=closure(defs,roots);require(not dep&blocked(defs,q))
    return dict(roots=list(roots),quarantine=list(q),closure=sorted(dep))
def append(j,defs,roots,q,reason):
    s=state(defs,roots,q)
    b=dict(index=len(j),previous=j[-1]["hash"] if j else None,state=s,reason=reason)
    j.append(dict(b,hash=digest(b)))
def verify(a,anchor,j,head):
    require(digest(a)==anchor and bool(j) and j[-1]["hash"]==head)
    defs=a["definitions"]
    for k in defs:expand(defs,k)
    for e in a["evidence"]:
        w=e["word"] if e["key"] is None else expand(defs,e["key"])
        actual=list(c.evaluate_program(e["p"],w))
        require((actual==e["target"])==e["equal"])
    for i,r in enumerate(j):
        b={k:v for k,v in r.items() if k!="hash"}
        require(r["hash"]==digest(b) and r["index"]==i and r["previous"]==(j[i-1]["hash"] if i else None))
        s=r["state"];require(s==state(defs,s["roots"],s["quarantine"]))
def quarantine(j,defs,key):
    s=j[-1]["state"];q=sorted(set(s["quarantine"]+[key]))
    b=blocked(defs,q)
    append(j,defs,[r for r in s["roots"] if r not in b],q,"quarantine:"+key)
def rollback(j,defs,index):
    require(type(index) is int and 0<=index<len(j))
    old=j[index]["state"];q=j[-1]["state"]["quarantine"]
    append(j,defs,old["roots"],q,"rollback:"+str(index))
def build():
    ev=[]
    for p,f,i,t,w in c.target_cohort(True):
        r=c.search(p,t,[]);require(r["word"] is not None)
        ev.append(dict(p=p,target=list(t),word=r["word"],key=None,equal=True))
    require(len(ev)==32)
    defs={w:dict(parts=[["primitive",x] for x in w],origin="mined",support=n) for w,n in c.select_mined([e["word"] for e in ev])}
    require(set(defs)=={"SM","RS","MR","MS","SR","RSM"})
    for k,parts in {"N1":["SM","RS"],"N2":["MR","MS"],"N3":["SR","RSM"],"N4":["N1","N2"],"N5":["N4","N3"]}.items():
        defs[k]=dict(parts=[["ref",x] for x in parts],origin="developer_fixture")
    for k in ("N1","N2","N3","N4","N5"):
        t=list(c.evaluate_program(19,expand(defs,k)))
        ev.append(dict(p=19,target=t,word=None,key=k,equal=True))
        t=t[:];t[0],t[1]=t[1],t[0]
        ev.append(dict(p=19,target=t,word=None,key=k,equal=False))
    return dict(definitions=defs,evidence=ev)
def faults(a,anchor,j,head):
    tests={}
    def bad(name,fn,structural=False):
        x,y=copy.deepcopy(a),copy.deepcopy(j)
        try:
            fn(x,y)
            # For structural attacks assume attacker can recompute archive hash;
            # validity must still reject the invalid DAG.
            verify(x,digest(x) if structural else anchor,y,y[-1]["hash"] if structural else head)
        except ValueError:tests[name]=True
        else:tests[name]=False
    bad("missing_dependency",lambda x,y:x["definitions"]["N1"]["parts"].append(["ref","missing"]),True)
    bad("cycle",lambda x,y:x["definitions"]["N1"]["parts"].append(["ref","N5"]),True)
    bad("invalid_primitive",lambda x,y:x["definitions"]["SM"]["parts"].append(["primitive","X"]),True)
    bad("altered_evidence",lambda x,y:x["evidence"][0].update(target=[]),True)
    bad("archive_tamper",lambda x,y:x["definitions"]["SM"].update(support=999))
    bad("stale_head",lambda x,y:y.pop())
    bad("invalid_manifest",lambda x,y:append(y,x["definitions"],["missing"],[],"bad"),True)
    bad("quarantine_bypass",lambda x,y:append(y,x["definitions"],["N5"],["SM"],"bad"),True)
    require(all(tests.values()));return tests
def recovery(a,anchor,j,head):
    payload=json.dumps(dict(archive=a,journal=j),sort_keys=True).encode()
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);backup=root/"backup.json";live=root/"live.json"
        backup.write_bytes(payload);backup.chmod(0o444);live.write_bytes(payload)
        recovered=[]
        for mode in ("corrupt","missing"):
            if mode=="corrupt":live.write_bytes(b"corrupt")
            else:live.unlink()
            live.write_bytes(backup.read_bytes());x=json.loads(live.read_bytes())
            verify(x["archive"],anchor,x["journal"],head)
            require(live.read_bytes()==payload)
            recovered.append(mode)
        return recovered
def test_retrieval(a,active,q):
    defs=a["definitions"];eligible=sorted(set(defs)-set(active)-blocked(defs,q))
    words=[expand(defs,k) for k in active]
    rng=random.Random(20270103);records=[]
    for p in (31,37):
        targets={k:c.evaluate_program(p,expand(defs,k)) for k in eligible}
        # Distinct targets absent from active and primitive library.
        seen={c.evaluate_program(p,w) for w in ["",*c.OPS,*words]}
        rare=[]
        for k,t in targets.items():
            if t not in seen:rare.append(t);seen.add(t)
        require(len(rare)>=6);rare=rare[:6]
        forbidden={c.evaluate_program(p,expand(defs,k)) for k in defs}|seen
        controls=[]
        while len(controls)<6:
            w="".join(rng.choice(c.OPS) for _ in range(8))
            t=c.evaluate_program(p,w)
            if t not in forbidden:
                controls.append(t);forbidden.add(t)
        for family,ts in (("rare",rare),("control",controls)):
            for t in ts:
                p0=c.search(p,t,[]);a0=c.search(p,t,words)
                charge=0;found=None
                for k in eligible:
                    w=expand(defs,k);charge+=len(w)
                    if c.evaluate_program(p,w)==t:
                        found=k;break
                if found is None:
                    r=c.search(p,t,words);v=dict(word=r["word"],cost=r["cost"]+charge)
                else:v=dict(word=expand(defs,found),cost=charge)
                for x in (p0,a0,v):require(x["word"] is None or c.evaluate_program(p,x["word"])==t)
                require((found is not None)==(family=="rare"))
                records.append(dict(p=p,family=family,target=t,reactivated=found,primitive=p0,active=a0,retrieval=v))
    stats={}
    for arm in ("primitive","active","retrieval"):
        for f in ("rare","control","all"):
            rows=[r[arm] for r in records if f=="all" or r["family"]==f]
            stats[arm+"_"+f]=dict(solved=sum(x["word"] is not None for x in rows),cost=sum(x["cost"] if x["word"] is not None else c.CAP+1 for x in rows))
    s=stats["retrieval_all"];b=stats["active_all"];p=stats["primitive_all"]
    gate=s["solved"]>=b["solved"] and s["cost"]<=.85*min(b["cost"],p["cost"]) and stats["retrieval_control"]["cost"]<=1.1*stats["active_control"]["cost"]
    return dict(stats=stats,utility_pass=gate,records=records)
def main(out):
    a=build();anchor=digest(a);defs=a["definitions"];j=[]
    append(j,defs,["SM","SR","N5"],[],"initial")
    require("SM" in j[-1]["state"]["closure"])
    append(j,defs,["SR","N5"],[],"retire SM root")
    require("SM" in j[-1]["state"]["closure"] and "SM" not in j[-1]["state"]["roots"])
    quarantine(j,defs,"SM")
    require(set(j[-1]["state"]["roots"])=={"SR"} and {"SM","N1","N4","N5"}<=blocked(defs,["SM"]))
    try:rollback(j,defs,0)
    except ValueError:pass
    else:raise AssertionError("unsafe rollback")
    # Separate prospective retrieval scenario without quarantine; verify
    # that quarantine excludes dependent definitions in a direct check.
    require("N5" not in set(defs)-blocked(defs,["SM"]))
    head=j[-1]["hash"];verify(a,anchor,j,head)
    tests=faults(a,anchor,j,head);restored=recovery(a,anchor,j,head)
    r=test_retrieval(a,["SM","SR"],[])
    result=dict(anchor=anchor,head=head,archive=a,journal=j,tests=tests,restored=restored,safety_pass=True,**r)
    Path(out).write_text(json.dumps(result,indent=2))
    print("DAG_RESULT",json.dumps({k:v for k,v in result.items() if k not in ("archive","journal","records")}),flush=True)
    print("DAG_ARCHIVE",json.dumps(dict(archive=a,anchor=anchor,journal=j,head=head),separators=(",",":")),flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])
