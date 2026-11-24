"""Independent arithmetic/contract audit for EQUIV-REAL01, no model calls."""
import argparse, collections, hashlib, itertools, json, math, random
from pathlib import Path
import equiv_pilot_freeze as pilot
import equiv_process01 as proc
ARMS=("base","ordinary","contrast","process")
SEED=20270160
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def require(ok,why):
    if not ok:raise ValueError(why)
def truth(p):
    e={frozenset(x) for x in p["edges"]}
    def ext(k):
        s=set(p[k]);f=p["future"]
        return {frozenset(c) for j in range(len(f)+1) for c in itertools.combinations(f,j)
                if not any(z<=s|set(c) for z in e)}
    return ext("a")==ext("b")
def audit(train,labels,retention,records,adapters=None):
    require(len(train)==192 and len(labels)==64 and len(retention)==64,"dataset sizes")
    require(all(truth(x["packet"])==x["label"] for x in labels+train),"exact oracle")
    require(retention==proc.retention(),"retention generator mismatch")
    require(len({x["id"] for x in labels+retention})==128,"id collision")
    groups={}
    for r in labels:
        for v in ("edges","matrix"):
            groups["equiv",v,r["id"]]=(r,pilot.question(r["packet"],v))
    for r in retention:groups["retention","direct",r["id"]]=(r,r["question"])
    expected={(a,)+k for a in ARMS for k in groups}
    actual={(r["arm"],r["task"],r["view"],r["id"]) for r in records}
    require(len(records)==len(expected)==768 and actual==expected,"missing/duplicate predictions")
    results={a:{} for a in ARMS};hits={};binary={};prob={};raws={}
    for r in records:
        row,q=groups[r["task"],r["view"],r["id"]]
        require(r["prompt_sha256"]==hashlib.sha256(q.encode()).hexdigest(),"prompt mismatch")
        require(type(r["raw"])==str and type(r["ids"])==list and len(r["ids"])<=8 and all(type(x)==int and x>=0 for x in r["ids"]),"prediction format")
        p=r["p_yes_binary"];require(type(p) in (int,float) and math.isfinite(p) and 0<=p<=1,"probability")
        if "input_tokens" in r:require(type(r["input_tokens"])==int and 0<r["input_tokens"]<=1016,"input length")
        a=r["arm"];v=r["view"] if r["task"]=="equiv" else row["domain"];i=row["id"];k=(a,v,i)
        hits[k]=r["raw"]==("Yes" if row["label"] else "No")
        binary[k]=(p>.5)==row["label"];prob[k]=p;raws[k]=r["raw"]
    views={"edges":labels,"matrix":labels,"edge":[x for x in retention if x["domain"]=="edge"],"syntax":[x for x in retention if x["domain"]=="syntax"]}
    for a in ARMS:
        for v,rows in views.items():
            pairs=collections.defaultdict(list)
            for r in rows:pairs[r["pair"]].append(r)
            require(all(len(p)==2 and {x["label"] for x in p}=={True,False} for p in pairs.values()),"pair balance")
            ks=[(a,v,r["id"]) for r in rows]
            contrasts=[]
            for pair in pairs.values():
                pos,neg=sorted(pair,key=lambda r:not r["label"])
                contrasts.append(prob[a,v,pos["id"]]-prob[a,v,neg["id"]])
            s={"n":len(rows),"strict":sum(hits[k] for k in ks),"binary":sum(binary[k] for k in ks),
              "valid":sum(raws[k] in ("Yes","No") for k in ks),
              "correct_yes":sum(hits[a,v,r["id"]] for r in rows if r["label"]),
              "correct_no":sum(hits[a,v,r["id"]] for r in rows if not r["label"]),
              "binary_yes_predictions":sum(prob[k]>.5 for k in ks),"binary_ties":sum(prob[k]==.5 for k in ks),
              "pairs_both":sum(all(hits[a,v,r["id"]] for r in p) for p in pairs.values()),
              "binary_pairs_both":sum(all(binary[a,v,r["id"]] for r in p) for p in pairs.values()),
              "positive_contrasts":sum(d>0 for d in contrasts),"mean_contrast":sum(contrasts)/len(contrasts),
              "raw_counts":dict(collections.Counter(raws[k] for k in ks))}
            for b in ("base","ordinary"):
                s["vs_"+b]={"gained":sum(hits[a,v,r["id"]] and not hits[b,v,r["id"]] for r in rows),
                "lost":sum(hits[b,v,r["id"]] and not hits[a,v,r["id"]] for r in rows)}
            results[a][v]=s
        results[a]["both_views_strict"]=sum(hits[a,"edges",r["id"]] and hits[a,"matrix",r["id"]] for r in labels)
    verdict={}
    for a in ARMS[1:]:
        g={}
        for v in ("edges","matrix"):
            s=results[a][v];b=results["base"][v]
            g[v]=s["strict"]>=48 and s["strict"]-b["strict"]>=7 and s["pairs_both"]>=20 and min(s["correct_yes"],s["correct_no"])>=24
        for v in ("edge","syntax"):
            s=results[a][v];b=results["base"][v]
            g["retention_"+v]=s["strict"]>=b["strict"]-.05*s["n"]
        verdict[a]={"gates":g,"pass_all":all(g.values()),"delta_vs_ordinary":{v:results[a][v]["strict"]-results["ordinary"][v]["strict"] for v in ("edges","matrix")},"pair_delta_vs_ordinary":{v:results[a][v]["pairs_both"]-results["ordinary"][v]["pairs_both"] for v in ("edges","matrix")}}
    pair_names=sorted({r["pair"] for r in train});require(len(pair_names)==96,"train pair count")
    rng=random.Random(SEED);order=[]
    for _ in range(2):
        ids=list(range(96));rng.shuffle(ids);order.extend(pair_names[i] for i in ids)
    exposure=hashlib.sha256(json.dumps(order).encode()).hexdigest()
    checked=None
    if adapters is not None:
        ms=[]
        for a in ARMS[1:]:
            d=Path(adapters)/("real-adapter-"+a);m=read(d/"manifest.json")
            require(m["kind"]=="real" and m["arm"]==a and m["model"]==pilot.MODEL and m["revision"]==pilot.REV and m["seed"]==SEED and m["updates"]==192 and m["exposure_sha256"]==exposure,"manifest "+a)
            require(len(m["losses"])==192 and all(math.isfinite(x) for x in m["losses"]) and math.isfinite(m["delta_L2"]) and m["delta_L2"]>0 and m["base_frozen"] is True,"weight or loss record")
            files={p.name:sha(p) for p in (d/"adapter").iterdir() if p.is_file()}
            require("adapter_model.safetensors" in files and files==m["adapter_hashes"],"adapter digest "+a)
            require(0<m["input_tokens"]<=m["padded_tokens"] and 0<m["supervised_tokens"]<=m["input_tokens"],"token counts")
            ms.append({k:m[k] for k in ("arm","input_tokens","padded_tokens","supervised_tokens","delta_L2","adapter_hashes","seconds")})
        require(len({(m["input_tokens"],m["padded_tokens"]) for m in ms})==1,"unequal exposure")
        checked=ms
    return dict(scores=results,verdict=verdict,expected_exposure=exposure,checked_adapter_manifests=checked,promotion_authorized=False)
def fixture():
    rows,_=pilot.generate();labels=rows["holdout"];ret=proc.retention();rec=[]
    for a in ARMS:
        for r in labels+ret:
            vlist=("edges","matrix") if "packet" in r else ("direct",)
            for v in vlist:
                q=pilot.question(r["packet"],v) if "packet" in r else r["question"]
                yes=True if a=="base" else r["label"]
                rec.append(dict(arm=a,task="equiv" if "packet" in r else "retention",view=v,id=r["id"],raw="Yes" if yes else "No",p_yes_binary=float(yes),ids=[1],prompt_sha256=hashlib.sha256(q.encode()).hexdigest()))
    s=audit(rows["train"],labels,ret,rec)
    require(s["scores"]["base"]["edges"]["binary"]==32 and s["scores"]["base"]["edges"]["pairs_both"]==0 and s["scores"]["process"]["both_views_strict"]==64 and all(v["pass_all"] for v in s["verdict"].values()),"fixture score")
    rejected=0
    for bad in (rec[:-1],rec[:-1]+[rec[0]], [dict(rec[0],prompt_sha256="bad")]+rec[1:], [dict(rec[0],p_yes_binary=float("nan"))]+rec[1:]):
        try:audit(rows["train"],labels,ret,bad)
        except ValueError:rejected+=1
        else:raise AssertionError("bad prediction accepted")
    print("POSTAUDIT_FIXTURE",json.dumps(dict(rows=len(rec),rejected=rejected,expected_exposure=s["expected_exposure"],synthetic_only=True)),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--fixture",action="store_true");p.add_argument("--train");p.add_argument("--labels");p.add_argument("--retention");p.add_argument("--predictions",nargs="+");p.add_argument("--adapters");p.add_argument("--out");a=p.parse_args()
    if a.fixture:fixture()
    else:
        for f,k in ((a.train,"train"),(a.labels,"labels")):require(sha(f)==proc.EXPECTED[k],"frozen input hash")
        require(sha(a.retention)=="47550736816876c27aad82078fac73818a45a1a3c6a21026d9f7e8790820bf91","retention hash")
        s=audit(read(a.train),read(a.labels),read(a.retention),[r for f in a.predictions for r in read(f)],a.adapters)
        Path(a.out).write_text(json.dumps(s,indent=2));print("POSTAUDIT_REAL",json.dumps(s),flush=True)
