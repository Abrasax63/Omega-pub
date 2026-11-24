"""MEMORY-PRUNE01: reversible activation, integrity checks and no deletion."""
import argparse,copy,hashlib,json,random
from pathlib import Path
from collections import Counter
import compose_learn01 as c
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(c.__file__))}
def require(ok):
    if not ok:raise ValueError("integrity")
def revision(journal,active,reason):
    body=dict(index=len(journal),previous=journal[-1]["hash"] if journal else None,active=list(active),reason=reason)
    journal.append(dict(body,hash=digest(body)))
def verify(archive,anchor,journal):
    require(digest(archive)==anchor)
    defs=archive["definitions"]
    for k,v in defs.items():
        require(k==digest(v) and len(v["word"]) in (2,3) and all(x in c.OPS for x in v["word"]))
    for s in archive["solutions"]:
        require(tuple(s["target"])==c.evaluate_program(s["p"],s["word"]))
    require(len(archive["solutions"])==32 and bool(journal))
    for i,r in enumerate(journal):
        body={k:v for k,v in r.items() if k!="hash"}
        require(r["hash"]==digest(body) and r["index"]==i and r["previous"]==(journal[i-1]["hash"] if i else None))
        require(len(set(r["active"]))==len(r["active"]) and all(k in defs for k in r["active"]))
def rollback(journal,index):
    require(type(index) is int and 0<=index<len(journal))
    revision(journal,journal[index]["active"],"rollback:"+str(index))
def cohort(primes,count,seed,exclude=()):
    rng=random.Random(seed)
    for p in primes:
        seen={tuple(range(p))}|{tuple(t) for q,t in exclude if q==p}
        for f in ("motif","random"):
            for i in range(count):
                for _ in range(10000):
                    if f=="motif":
                        w=rng.choice(c.OPS)+"".join(rng.choice(("RSM","SLD","MRS")) for _ in range(rng.randint(2,3)))+rng.choice(c.OPS)
                    else:
                        w=""
                        for _ in range(rng.randint(6,9)):
                            w+=rng.choice([o for o in c.OPS if not w or c.INV[w[-1]]!=o])
                    t=c.evaluate_program(p,w)
                    if t not in seen:break
                else:raise RuntimeError("cohort exhausted")
                seen.add(t);yield p,f,i,t
def words(archive,active):
    return [archive["definitions"][k]["word"] for k in active]
def trial(data,macros):
    results=[]
    for p,f,i,t in data:
        r=c.search(p,t,macros)
        require(r["word"] is None or c.evaluate_program(p,r["word"])==t)
        results.append(dict(p=p,family=f,index=i,target=t,**r))
    return results
def totals(rs):
    return dict(solved=sum(r["word"] is not None for r in rs),
                cost=sum(r["cost"] if r["word"] is not None else c.CAP+1 for r in rs),
                seconds=sum(r["seconds"] for r in rs))
def stable(rs):return [(r["word"],r["cost"]) for r in rs]
def adversarial(archive,anchor,journal):
    tests={}
    def check(name,mutate):
        a,j=copy.deepcopy(archive),copy.deepcopy(journal)
        try:mutate(a,j);verify(a,anchor,j)
        except ValueError:tests[name]=True
        else:tests[name]=False
    key=next(iter(archive["definitions"]))
    check("altered_definition",lambda a,j:a["definitions"][key].update(word="RRR"))
    check("missing_reference",lambda a,j:revision(j,["0"*64],"bad"))
    check("historical_tamper",lambda a,j:j[0].update(reason="changed"))
    check("duplicate_active",lambda a,j:revision(j,[key,key],"bad"))
    check("altered_solution",lambda a,j:a["solutions"][0].update(word=""))
    def wrong_parent(a,j):
        revision(j,[key],"bad");j[-1]["previous"]="0"*64
        j[-1]["hash"]=digest({k:v for k,v in j[-1].items() if k!="hash"})
    check("wrong_parent",wrong_parent)
    try:rollback(copy.deepcopy(journal),len(journal)+1)
    except ValueError:tests["unknown_revision"]=True
    else:tests["unknown_revision"]=False
    require(all(tests.values()))
    return tests
def train(path):
    original=list(c.target_cohort(True))
    solved=[]
    for p,f,i,t,_ in original:
        r=c.search(p,t,[]);require(r["word"] is not None)
        solved.append(dict(p=p,target=t,word=r["word"]))
    mined=c.select_mined([r["word"] for r in solved])
    defs={}
    for w,support in mined:
        obj=dict(word=w,support=support);defs[digest(obj)]=obj
    archive=dict(definitions=defs,solutions=solved);anchor=digest(archive)
    full=list(defs);journal=[];revision(journal,full,"initial");verify(archive,anchor,journal)
    data=list(cohort((13,17),6,20261231,[(r["p"],r["target"]) for r in solved]))
    active=full[:];base=trial(data,words(archive,full));current=totals(base)
    trace=[];overhead=current["cost"];evaluations=1
    while active:
        options=[]
        for k in active:
            nxt=[x for x in active if x!=k]
            rs=trial(data,words(archive,nxt));m=totals(rs)
            overhead+=m["cost"];evaluations+=1
            options.append((m["cost"],defs[k]["word"],k,nxt,m))
        eligible=[o for o in options if o[4]["solved"]>=current["solved"] and o[0]<current["cost"]]
        if not eligible:break
        cost,w,k,active,current=min(eligible,key=lambda o:(o[0],o[1]))
        revision(journal,active,"deactivate:"+w);verify(archive,anchor,journal)
        trace.append(dict(removed=w,**current))
    selected_index=len(journal)-1
    empty=totals(trial(data,[]));overhead+=empty["cost"];evaluations+=1
    rollback(journal,0);verify(archive,anchor,journal)
    require(journal[-1]["active"]==full and stable(trial(data,words(archive,full)))==stable(base))
    rollback(journal,selected_index);verify(archive,anchor,journal)
    require(journal[-1]["active"]==active)
    tests=adversarial(archive,anchor,journal)
    obj=dict(hashes=hashes(),archive=archive,anchor=anchor,journal=journal,journal_head=journal[-1]["hash"],selected=active,trace=trace,tests=tests,calibration_full=totals(base),calibration_selected=current,calibration_empty=empty,calibration_cost=overhead,calibration_evaluations=evaluations)
    Path(path).write_text(json.dumps(obj,indent=2))
    print("PRUNE_TRAIN",json.dumps({k:v for k,v in obj.items() if k not in ("archive","journal","selected")}|{"full":words(archive,full),"active":words(archive,active)}),flush=True)
def evaluate(checkpoint,path):
    ck=json.loads(Path(checkpoint).read_text());require(ck["hashes"]==hashes())
    archive=ck["archive"];journal=ck["journal"];verify(archive,ck["anchor"],journal)
    require(journal[-1]["hash"]==ck["journal_head"] and journal[-1]["active"]==ck["selected"])
    full=journal[0]["active"];active=ck["selected"]
    rng=random.Random(20270102);sample=rng.sample(full,len(active));sample=[k for k in full if k in sample]
    arms={"full":words(archive,full),"selected":words(archive,active),"primitive":[],"random_subset":words(archive,sample)}
    data=list(cohort((23,29),12,20270101));require(len(data)==48)
    stats={};records=[]
    for a,macro in arms.items():
        rs=trial(data,macro);stats[a]=totals(rs)
        stats[a]["random_cost"]=totals([r for r in rs if r["family"]=="random"])["cost"]
        records.extend(dict(arm=a,**r) for r in rs)
    s,f,p=(stats[a] for a in ("selected","full","primitive"))
    gain=1-s["cost"]/f["cost"]
    gate=s["solved"]>=max(f["solved"],p["solved"]) and gain>=.15 and s["cost"]<=p["cost"] and s["random_cost"]<=1.1*p["random_cost"]
    result=dict(stats=stats,arms=arms,archive_digest=ck["anchor"],journal_head=ck["journal_head"],replayed_solutions=len(archive["solutions"]),safety_pass=all(ck["tests"].values()),tests=ck["tests"],utility_pass=gate,gain_vs_full=gain,records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("PRUNE_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
