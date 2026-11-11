"""External measured-solver benchmark for Omega (ASlib MAXSAT-PMS-2016).

Authoritative data are fetched from the immutable GitHub commit, verified
against each Git blob SHA and parsed with the standard library. The published
10 CV folds are used; none of the training parameters is computed from the
held-out fold. Runtimes are *historical external measurements*, not actual
re-executions of MaxSAT solvers.

Research status: historical public cross-validation, not blind, not SOTA.
Data source: coseal/aslib_data (GPLv3), not redistributed by this script.
"""
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import urllib.request

from action_planning_two_step import optimize_policy

UPSTREAM_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
REMOTE = ("https://raw.githubusercontent.com/coseal/aslib_data/"
          + UPSTREAM_COMMIT + "/MAXSAT-PMS-2016/")
BLOBS = {
    "feature_values.arff": "ef97a20a998cba9002d8c0f930ae310c4a2d7010",
    "algorithm_runs.arff": "7be2ed941a53def90d1c79aef34de0e26df1b1ad",
    "cv.arff": "0a2fb78356a0cccf06a1d9482531c5bfe1ba6990",
    "feature_costs.arff": "d4d0ac15240d41bdab6cb5c47b88b612cec815be",
    "description.txt": "b09e4355e9e7602b7ee3f489ead7d60803b2d835",
}
PENALTY=18000.0
CUTOFF=1800.0
OMEGA_MAX_HYPOTHESES=64
K_VALUES=(1,5,15)
METHODS=("SBS","KNN1","KNN5","KNN15","KNN5_small","OMEGA_finite_v0","VBS_oracle")


def git_blob_sha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def load_source(name, cache_dir=None):
    if name not in BLOBS:
        raise ValueError("not a locked source")
    if cache_dir is not None:
        p=Path(cache_dir)/name
        if p.exists():
            data=p.read_bytes()
        else:
            data=urllib.request.urlopen(REMOTE+name,timeout=45).read()
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data)
    else:
        data=urllib.request.urlopen(REMOTE+name,timeout=45).read()
    if git_blob_sha(data)!=BLOBS[name]:
        raise ValueError("upstream Git blob hash mismatch: "+name)
    return data.decode("utf-8")


def read_arff(raw):
    attrs=[]
    rows=[]
    in_data=False
    for line in raw.splitlines():
        s=line.strip()
        if not s or s.startswith("%"):
            continue
        if s.upper()=="@DATA":
            in_data=True
            continue
        if not in_data:
            if s.upper().startswith("@ATTRIBUTE "):
                attrs.append(s.split(None,2)[1].strip("'\""))
        else:
            row=next(csv.reader([s],skipinitialspace=True,quotechar="'"))
            if len(row)!=len(attrs):
                raise ValueError("ARFF width mismatch "+str((len(row),len(attrs))))
            rows.append(dict(zip(attrs,row)))
    if not attrs or not rows:
        raise ValueError("ARFF missing attributes or rows")
    return attrs,rows


def parse_data(texts):
    attrs,feats=read_arff(texts["feature_values.arff"])
    assert attrs[:2]==["instance_id","repetition"]
    features={}
    for r in feats:
        key=r["instance_id"]
        if key in features:
            raise ValueError("duplicate feature repetition: "+key)
        features[key]=tuple(
            None if r[a] in ("?","") else float(r[a]) for a in attrs[2:])
    if len(attrs)!=39:
        raise ValueError("37 features expected")

    _,raw=read_arff(texts["algorithm_runs.arff"])
    runs=defaultdict(dict)
    statuses=Counter()
    repetitions=set()
    algorithms=set()
    for row in raw:
        instance=row["instance_id"]
        algo=row["algorithm"]
        rep=int(row["repetition"])
        repetitions.add(rep)
        if algo in runs[instance]:
            raise ValueError("repeated algorithm run requires median: "+instance)
        cost=float(row["PAR10"])
        status=row["runstatus"]
        if not (math.isfinite(cost) and cost>=0):
            raise ValueError("invalid PAR10")
        if status=="ok" and cost>=PENALTY:
            raise ValueError("ok run at timeout penalty")
        if status!="ok" and cost!=PENALTY:
            raise ValueError("non-ok with unexpected penalty")
        runs[instance][algo]=(cost,status)
        statuses[status]+=1
        algorithms.add(algo)
    if repetitions!={1}:
        raise ValueError("this predefined dataset requires unique repetitions")

    _,raw=read_arff(texts["cv.arff"])
    folds={}
    for row in raw:
        key=row["instance_id"]
        if key in folds:raise ValueError("duplicate official fold entry")
        folds[key]=int(row["fold"])
    _,raw=read_arff(texts["feature_costs.arff"])
    costs={}
    for row in raw:
        key=row["instance_id"]
        if key in costs:raise ValueError("duplicate feature cost")
        costs[key]=(None if row["base"]=="?" else float(row["base"]))

    all_sets={"features":set(features),"runs":set(runs),
              "cv":set(folds),"costs":set(costs)}
    if len(set.union(*all_sets.values())) != len(set.intersection(*all_sets.values())):
        raise ValueError("ASlib source joins are not exhaustive")
    instances=sorted(features)
    if len(instances)!=601 or len(algorithms)!=19:
        raise ValueError("ASlib instance count or algorithm count drift")
    if len(raw)!=601 or any(len(runs[i])!=19 for i in instances):
        raise ValueError("incomplete solver matrix")
    if sorted(set(folds.values()))!=list(range(1,11)):
        raise ValueError("official folds 1..10 missing")
    for name,values in all_sets.items():
        if len(values)!=601:raise ValueError("join mismatch "+name)
    if any(x is None or not math.isfinite(x) or x<0 for x in costs.values()):
        raise ValueError("unexpected missing feature cost")
    if any(any(x is None or not math.isfinite(x) for x in features[i])
           for i in instances):
        raise ValueError("unexpected missing feature values")

    return {
        "ids":instances,"features":features,"runs":runs,
        "folds":folds,"costs":costs,"algorithms":tuple(sorted(algorithms)),
        "quality":{"n_instances":len(instances),"n_algorithms":len(algorithms),
                   "n_features":len(attrs)-2,"n_runs":sum(len(x) for x in runs.values()),
                   "statuses":dict(statuses),
                   "fold_counts":dict(sorted(Counter(folds.values()).items()))}
    }


def _best_algo(ids,d,method="mean"):
    """Only train rows. For singleton, also delivers that row's measured best."""
    if not ids:raise ValueError("empty training group")
    algos=d["algorithms"]
    return min(algos,key=lambda a:(
        statistics.fmean(d["runs"][i][a][0] for i in ids),a))


def train_normalizer(train_ids, data):
    raw=[data["features"][i] for i in train_ids]
    n=len(raw[0])
    med=[statistics.median(x[j] for x in raw) for j in range(n)]
    mean=[statistics.fmean(x[j] for x in raw) for j in range(n)]
    std=[statistics.pstdev(x[j] for x in raw) or 1.0 for j in range(n)]
    return med,mean,std


def normalize(features,normalizer):
    med,mean,std=normalizer
    if len(features)!=len(mean):raise ValueError("feature length mismatch")
    return tuple(max(-10.0,min(10.0,((med[j] if v is None else v)-mean[j])/std[j]))
                 for j,v in enumerate(features))


def select_knn(train_ids,test_id,data,vectors,k,used_features=37):
    test=vectors[test_id]
    neighbors=sorted(
        ((math.fsum((test[j]-vectors[i][j])**2 for j in range(used_features)),i)
         for i in train_ids),
        key=lambda z:(z[0],z[1]))[:k]
    return _best_algo([x[1] for x in neighbors],data)


def fit_omega(train_ids,data,med):
    if len(train_ids)<OMEGA_MAX_HYPOTHESES:
        raise ValueError("insufficient external train cases")
    train_ids=sorted(train_ids)
    n=len(train_ids)
    rep=[train_ids[(i*(n-1))//(OMEGA_MAX_HYPOTHESES-1)]
         for i in range(OMEGA_MAX_HYPOTHESES)]
    assert len(set(rep))==OMEGA_MAX_HYPOTHESES
    model={
        "case_id":"ASLIB-PMS-2016",
        "question":"Choose the best measured MaxSAT solver",
        "mission_type":"computational",
        "uncertainty":"Unknown optimal algorithm",
        "hypotheses":[{"id":"H"+str(j),"decision":_best_algo([i],data),
                       "weight":1} for j,i in enumerate(rep)],
        "checks":[{
            "id":"f_"+str(j+1),"step":"Inspect f_"+str(j+1),
            "method":"recorded_feature","action":"verify",
            "cost_milli":1,"available":True,
            "observations":[
                "low" if data["features"][i][j]<=med[j] else "high"
                for i in rep]
        } for j in range(8)],
    }
    fit=optimize_policy(model,max_depth=3,max_cost_milli=3)
    return {"model":fit,"representatives":rep,"medians":med}


def predict_omega(test_id,fit,data,sbs):
    node=fit["model"]["policy"]
    candidates=fit["representatives"]
    visited=[]
    while node.get("check_id") and len(visited)<3:
        fid=node["check_id"]
        index=int(fid.removeprefix("f_"))-1
        if not 0<=index<8 or index in visited:
            raise AssertionError("invalid Omega feature action")
        visited.append(index)
        val=("low" if data["features"][test_id][index]<=fit["medians"][index]
             else "high")
        candidates=[i for i in candidates if
                    ("low" if data["features"][i][index]<=fit["medians"][index]
                     else "high")==val]
        node=node.get("branches",{}).get(val,{})
        if not candidates:break
    return (_best_algo(candidates,data) if candidates else sbs),visited


def score_measurement(instance,algo,data,use_features):
    cost,status=data["runs"][instance][algo]
    extra=data["costs"][instance] if use_features else 0.0
    return cost+extra,status=="ok",cost,extra


def evaluate(data):
    ledger=[]
    fold_summary=[]
    for fold in range(1,11):
        train=[i for i in data["ids"] if data["folds"][i]!=fold]
        test=[i for i in data["ids"] if data["folds"][i]==fold]
        if len(train)<64 or not test:
            raise ValueError("bad CV")
        sbs=_best_algo(train,data)
        norm=train_normalizer(train,data)
        vectors={i:normalize(data["features"][i],norm)
                 for i in train+test}
        omega=fit_omega(train,data,norm[0])
        per_fold=defaultdict(list)
        for instance in test:
            predictions={
                "SBS":(sbs,False),
                "KNN1":(select_knn(train,instance,data,vectors,1),True),
                "KNN5":(select_knn(train,instance,data,vectors,5),True),
                "KNN15":(select_knn(train,instance,data,vectors,15),True),
                "KNN5_small":(select_knn(train,instance,data,vectors,5,8),True),
                "VBS_oracle":(_best_algo([instance],data),False),
            }
            omega_choice,checks=predict_omega(instance,omega,data,sbs)
            predictions["OMEGA_finite_v0"]=(omega_choice,bool(checks))
            for name in METHODS:
                algo,uses_features=predictions[name]
                total,solved,par10,extra=score_measurement(instance,algo,data,uses_features)
                rec={"fold":fold,"instance":instance,"policy":name,
                     "selected_solver":algo,"PAR10":par10,
                     "feature_cost":extra,"total_PAR10_plus_features":total,
                     "solved":solved}
                ledger.append(rec)
                per_fold[name].append(rec)
        fold_summary.append({
            "fold":fold,"n_test":len(test),"sbs_solver":sbs,
            "metrics":{name:metrics(per_fold[name]) for name in METHODS},
            "omega_first":omega["model"]["policy"].get("check_id"),
        })
    totals=defaultdict(list)
    for r in ledger:totals[r["policy"]].append(r)
    return {
        "status":"EXTERNAL_HISTORICAL_MEASUREMENTS_CV_NOT_BLIND",
        "preregister_commit":"b2c03f48b7acb9c7a33f98978863ec712416ade1",
        "source_commit":UPSTREAM_COMMIT,
        "data_quality":data["quality"],
        "policy_type_note":"OMEGA_finite_v0 bridges 0-1 risk to PAR10; not an algorithm-selection state-of-the-art implementation",
        "official_cv_folds":10,
        "model_calls":0,"external_solver_executions":0,
        "summaries":{name:metrics(totals[name]) for name in METHODS},
        "folds":fold_summary,
        "ledger":ledger,
    }


def metrics(rows):
    n=len(rows)
    return {"n":n,"mean_PAR10_plus_features":round(statistics.fmean(
                 r["total_PAR10_plus_features"] for r in rows),6),
            "median_PAR10_plus_features":round(statistics.median(
                 r["total_PAR10_plus_features"] for r in rows),6),
            "solved":sum(r["solved"] for r in rows),
            "solved_rate":round(sum(r["solved"] for r in rows)/n,6),
            "mean_feature_cost":round(statistics.fmean(r["feature_cost"]
                                                       for r in rows),6)}


def run(cache_dir=None):
    texts={name:load_source(name,cache_dir) for name in BLOBS}
    data=parse_data(texts)
    return evaluate(data)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--cache-dir",default=None)
    ap.add_argument("--json-output",default=None)
    opts=ap.parse_args()
    result=run(opts.cache_dir)
    if opts.json_output:
        Path(opts.json_output).write_text(
            json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False),
            encoding="utf-8")
    # Redacted stdout: no large per-instance ledger, but full ledger saved.
    print("OMEGA_ASLIB_EXTERNAL_RESULT "+json.dumps({
        "source_commit":result["source_commit"],
        "data_quality":result["data_quality"],
        "summaries":result["summaries"],
        "official_cv_folds":result["official_cv_folds"],
        "external_solver_executions":result["external_solver_executions"],
        "status":result["status"],
    },sort_keys=True,ensure_ascii=False))
