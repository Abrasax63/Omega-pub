"""COMPOSE-LEARN01: mine reusable operator programs, test across domains."""
import argparse,hashlib,itertools as it,json,random,time
from collections import Counter
from pathlib import Path
OPS=("R","L","M","D","S")
INV={"R":"L","L":"R","M":"D","D":"M","S":"S"}
CAP=12000
def primitive(p,o,x):
    if o=="R":return (x+1)%p
    if o=="L":return (x-1)%p
    if o=="M":return 2*x%p
    if o=="D":return x*pow(2,-1,p)%p
    if o=="S":return 1-x if x in (0,1) else x
    raise ValueError(o)
def evaluate_program(p,word):
    out=[]
    for x in range(p):
        for o in word:x=primitive(p,o,x)
        out.append(x)
    return tuple(out)
def inverse(t):
    a=[0]*len(t)
    for i,v in enumerate(t):a[v]=i
    return tuple(a)
def compose(a,b):
    return tuple(a[x] for x in b)
def reduced(word):
    return all(INV[a]!=b for a,b in zip(word,word[1:]))
def signature(w):
    return tuple(evaluate_program(p,w) for p in (11,13))
def exclusions():
    return {signature(w) for w in ("",*OPS)}
def select_mined(paths):
    counts=Counter()
    for word in paths:
        counts.update({word[i:i+k] for k in (2,3) for i in range(len(word)-k+1) if reduced(word[i:i+k])})
    seen=exclusions();out=[]
    for w,n in sorted(counts.items(),key=lambda z:(-z[1],len(z[0]),z[0])):
        if n<2:break
        sig=signature(w)
        if sig in seen:continue
        seen.add(sig);out.append((w,n))
        if len(out)==6:break
    return out
def static_macros(lengths):
    rng=random.Random(20261230);seen=exclusions();out=[]
    for k in lengths:
        choices=["".join(w) for w in it.product(OPS,repeat=k) if reduced(w) and signature("".join(w)) not in seen]
        w=rng.choice(choices);seen.add(signature(w));out.append(w)
    return out
def target_cohort(train):
    rng=random.Random(20261228 if train else 20261229)
    for p in ((11,13) if train else (17,19)):
        seen={tuple(range(p))}
        for family in ("motif","random"):
            for i in range(8 if train else 12):
                for attempt in range(10000):
                    if family=="motif":
                        w=rng.choice(OPS)+"".join(rng.choice(("RSM","SLD","MRS")) for _ in range(rng.randint(2,3)))+rng.choice(OPS)
                    else:
                        w=""
                        for _ in range(rng.randint(6,9)):
                            w+=rng.choice([o for o in OPS if not w or INV[w[-1]]!=o])
                    target=evaluate_program(p,w)
                    if target not in seen:break
                else:raise RuntimeError("cohort exhausted")
                seen.add(target)
                yield p,family,i,target,w
def search(p,target,macros):
    start=time.process_time()
    identity=tuple(range(p))
    words=list(OPS)+list(macros)
    tables=[evaluate_program(p,w) for w in words]
    backward=[inverse(t) for t in tables]
    cost=sum(map(len,macros))
    # Each frontier is a complete BFS layer. Expand the smaller side.
    forward={identity:()};reverse={target:()}
    front=[identity];back=[target]
    def result(tokens):
        word=None if tokens is None else "".join(tokens)
        if word is not None:assert evaluate_program(p,word)==target
        return dict(word=word,tokens=tokens,cost=cost,seconds=time.process_time()-start,
                    macro_uses=0 if tokens is None else sum(len(w)>1 for w in tokens))
    if identity==target:return result(())
    while front and back:
        left=len(front)<=len(back)
        layer=front if left else back
        own=forward if left else reverse
        other=reverse if left else forward
        next_layer=[]
        for state in layer:
            for word,t in zip(words,tables if left else backward):
                if cost>=CAP:return result(None)
                cost+=1
                v=compose(t,state)
                if v in own:continue
                own[v]=own[state]+(word,) if left else (word,)+own[state]
                if v in other:
                    return result(own[v]+other[v] if left else other[v]+own[v])
                next_layer.append(v)
        if left:front=next_layer
        else:back=next_layer
    return result(None)
def source_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
def train(path):
    traces=[]
    for p,f,i,t,_ in target_cohort(True):
        r=search(p,t,[]);traces.append(dict(p=p,family=f,index=i,target=t,**r))
    paths=[r["word"] for r in traces if r["word"] is not None]
    mined=select_mined(paths)
    ck=dict(source_hash=source_hash(),macros=[w for w,n in mined],support=dict(mined),traces=traces)
    Path(path).write_text(json.dumps(ck,indent=2))
    print("COMPOSE_TRAIN",json.dumps(dict(macros=ck["macros"],support=ck["support"],solved=len(paths),cost=sum(r["cost"] for r in traces))),flush=True)
def evaluate(checkpoint,path):
    ck=json.loads(Path(checkpoint).read_text());assert ck["source_hash"]==source_hash()
    learned=ck["macros"];assert learned==[w for w,n in select_mined([r["word"] for r in ck["traces"] if r["word"] is not None])]
    static=static_macros(list(map(len,learned)))
    arms={"primitive":[],"learned":learned,"random":static}
    stats={a:{f:Counter() for f in ("motif","random")} for a in arms};records=[]
    for p,f,i,t,teacher in target_cohort(False):
        for a,macros in arms.items():
            r=search(p,t,macros);s=stats[a][f];done=r["word"] is not None
            assert not done or evaluate_program(p,r["word"])==t
            s["cases"]+=1;s["solved"]+=int(done);s["capped_cost"]+=r["cost"] if done else CAP+1
            s["seconds"]+=r["seconds"];s["macro_uses"]+=r["macro_uses"];s["expanded_length"]+=len(r["word"]) if done else 0
            records.append(dict(p=p,family=f,index=i,target=t,teacher_word=teacher,arm=a,**r))
        print("COMPOSE_CASE",p,f,i,flush=True)
    totals={a:dict(sum(d.values(),Counter())) for a,d in stats.items()}
    l=totals["learned"];gains={a:1-l["capped_cost"]/totals[a]["capped_cost"] for a in ("primitive","random")}
    random_gain=1-stats["learned"]["random"]["capped_cost"]/stats["primitive"]["random"]["capped_cost"]
    passed=all(l.get("solved",0)>=totals[a].get("solved",0) and gains[a]>=.15 for a in gains) and random_gain>=-.10
    result=dict(stats=stats,totals=totals,learned_macros=learned,random_macros=static,gains=gains,random_subgroup_gain=random_gain,primary_pass=passed,records=records)
    Path(path).write_text(json.dumps(result,indent=2))
    print("COMPOSE_LEARN_RESULT",json.dumps({k:v for k,v in result.items() if k!="records"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["train","evaluate"]);p.add_argument("--out",required=True);p.add_argument("--checkpoint");a=p.parse_args()
    if a.mode=="train":train(a.out)
    else:evaluate(a.checkpoint,a.out)
