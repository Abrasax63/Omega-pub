"""Post-inference audit for ATOMIC-SFT-PILOT01. Standard library only.

Run on frozen labels and predictions AFTER inference. Independent of original
scorer. Does not change preregistered thresholds or authorize promotion.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import re

def require(ok,msg):
    if not ok:
        raise ValueError(msg)

def truth(p):
    a,b,c=p["triple"]
    es={tuple(e) for e in p["edges"]}
    bits=[(a,b) in es,(b,c) in es,(a,c) in es]
    return "".join(str(int(x)) for x in bits+[bits[0] and bits[1] and not bits[2]])

def graph_key(p):
    es={tuple(e) for e in p["edges"]}
    return len(p["nodes"]),min("".join(str(int((a,b) in es)) for a in order for b in order)
                                for order in permutations(p["nodes"]))

def summarize(labels,predictions):
    require(len(labels)==64 and len({r["id"] for r in labels})==64,"LABEL_COUNT")
    require(Counter(len(r["packet"]["nodes"]) for r in labels)=={5:32,6:32},"SIZE_COUNTS")
    require(len({graph_key(r["packet"]) for r in labels})==64,"DUPLICATE_GRAPH")
    gold={r["id"]:truth(r["packet"]) for r in labels}
    sizes={r["id"]:len(r["packet"]["nodes"]) for r in labels}
    for r in labels:
        require(len(set(r["packet"]["triple"]))==3,"TRIPLE")
        require(r["label"]==dict(zip(("xy","yz","xz","violates"),[c=="1" for c in gold[r["id"]]])),"LABEL")
    expected={m:(32 if m=="110" else 6 if m in ("000","001") else 4)
              for m in (format(i,"03b") for i in range(8))}
    require(Counter(g[:3] for g in gold.values())==expected,"MOTIF_COUNTS")
    keys={(a,v,i) for a in ("base","lora") for v in ("edges","matrix") for i in gold}
    require(len(predictions)==len(keys) and {(r["arm"],r["view"],r["id"]) for r in predictions}==keys,"PREDICTION_COVERAGE")
    records={(r["arm"],r["view"],r["id"]):r for r in predictions}
    out={}
    all_joint={}
    for arm in ("base","lora"):
        out[arm]={}
        for view in ("edges","matrix"):
            groups={}
            outputs=Counter()
            joint={}
            for i,g in gold.items():
                r=records[arm,view,i]
                raw=r["raw"]
                require(isinstance(raw,str) and len(r["token_ids"])==r["output_tokens"] and 0<=r["output_tokens"]<=16,"TOKEN_TRACE")
                valid=re.fullmatch("[01]{4}",raw) is not None
                reading=valid and raw[:3]==g[:3]
                decision=valid and raw[3]==g[3]
                consistent=valid and (raw[3]=="1")==(raw[:3]=="110")
                joint[i]=reading and decision
                outputs[raw if valid else "INVALID"]+=1
                for name in ("all",g[:3],"size"+str(sizes[i]),"positive" if g[3]=="1" else "negative"):
                    c=groups.setdefault(name,Counter())
                    for k,v in (("n",1),("valid",valid),("reading",reading),("decision",decision),
                                ("consistent",consistent),("joint",joint[i])):
                        c[k]+=int(v)
            totals=groups["all"]
            macro=sum(groups[m]["joint"]/groups[m]["n"] for m in expected)/8
            out[arm][view]={"groups":{k:dict(v) for k,v in groups.items()},"outputs":dict(outputs),
                           "macro_motif_joint":macro,"joint_given_valid":totals["joint"]/totals["valid"] if totals["valid"] else None,
                           "joint_minus_best_constant":totals["joint"]-32}
            all_joint[arm,view]=joint
        out[arm]["same_graph_correct_both_views"]=sum(all_joint[arm,"edges"][i] and all_joint[arm,"matrix"][i] for i in gold)
    paired={}
    for view in ("edges","matrix"):
        b=all_joint["base",view];a=all_joint["lora",view]
        paired[view]={k:0 for k in ("both","base_only","lora_only","neither")}
        for i in gold:
            paired[view]["both" if b[i] and a[i] else "base_only" if b[i] else "lora_only" if a[i] else "neither"]+=1
    edge=out["lora"]["edges"]["groups"];base=out["base"]["edges"]["groups"]
    gain=edge["all"]["joint"]-base["all"]["joint"]
    return {"scores":out,"paired":paired,"strongest_constant_joint":32,
            "uniform_consistent_expected_joint":8,"preregistered_signal":gain>=7 and all(edge[c]["joint"]>base[c]["joint"] for c in ("positive","negative")),
            "promotion_authorized":False,"autonomous_learning_demonstrated":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--labels",type=Path,required=True)
    p.add_argument("--labels-sha",required=True)
    p.add_argument("--predictions",type=Path,required=True)
    p.add_argument("--predictions-sha",required=True)
    a=p.parse_args()
    raw=a.labels.read_bytes();pred=a.predictions.read_bytes()
    require(sha256(raw).hexdigest()==a.labels_sha,"LABEL_DIGEST")
    require(sha256(pred).hexdigest()==a.predictions_sha,"PREDICTION_DIGEST")
    print(json.dumps(summarize(json.loads(raw),[json.loads(x) for x in pred.splitlines()]),indent=2))

if __name__=="__main__":
    main()
