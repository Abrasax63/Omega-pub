"""OMEGA-ASLIB-002: externally measured, cost-sensitive transfer to WPMS.

Preregistered before looking at target PAR10:
- baseline SBS / KNN5 / KNN15, same 37 features and official CV folds
- greedy cost-sensitive depth-1 and depth-2 trees
- exact depth-2 lookahead over the same train-fold median thresholds
- non-admissible VBS oracle

The cost-sensitive depth-2 learner is an *experimental tree-search adapter*,
NOT the existing Omega optimize_policy or a new general-purpose orchestrator.
No solver execution/LLM is performed: historical upstream measured runtimes.
"""
import argparse
from collections import defaultdict, Counter
from functools import lru_cache
import json
import math
from pathlib import Path
import statistics
import urllib.request

from aslib_external_benchmark import (
    git_blob_sha, read_arff, train_normalizer, normalize, select_knn,
    _best_algo, score_measurement, metrics,
)

SOURCE_COMMIT="551b22beef8df17de59286b4822ef720e0aa4d6f"
BASE=("https://raw.githubusercontent.com/coseal/aslib_data/"+SOURCE_COMMIT+
      "/MAXSAT-WPMS-2016/")
SHA={
    "algorithm_runs.arff":"45aec3038b4304714c8047ad79ff0171c59dc5c8",
    "feature_values.arff":"4684f66e4111ce1dbef69e68a14367ce93293853",
    "feature_costs.arff":"2e7b9bdbacab04a87b1ab4766c5841a47eae08e7",
    "cv.arff":"a81207d105555c96a7278ee915f3ff3bd93377b2",
    "description.txt":"a7693da4fdaf433e3f2c0107adabca9592e9b7a8",
}
EXPECTED_CASES=630
EXPECTED_SOLVERS=18
EXPECTED_FEATURES=37
POLICIES=("SBS","KNN5","KNN15","TREE_greedy1",
          "TREE_greedy2","OMEGA_cost_lookahead2","VBS_oracle")


def load_source(name,cache=None):
    if name not in SHA:raise ValueError("unknown source")
    p=Path(cache)/name if cache else None
    if p and p.is_file():
        raw=p.read_bytes()
    else:
        with urllib.request.urlopen(BASE+name,timeout=45) as resp:raw=resp.read()
        if p:
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(raw)
    if git_blob_sha(raw)!=SHA[name]:
        raise ValueError("Git source blob mismatch: "+name)
    return raw.decode("utf-8")


def validate_description(text):
    for token in ("scenario_id: MAXSAT-WPMS-2016",
                  "- PAR10","maximize:","false",
                  "performance_type:","runtime",
                  "algorithm_cutoff_time: 1800",
                  "number_of_feature_steps: 1",
                  "    base:"):
        if token not in text:raise ValueError("scenario metadata mismatch: "+token)


def parse(texts):
    validate_description(texts["description.txt"])
    attrs,feat=read_arff(texts["feature_values.arff"])
    if attrs[:2]!=["instance_id","repetition"] or len(attrs)-2!=EXPECTED_FEATURES:
        raise ValueError("feature schema mismatch")
    features={}
    repetitions=set()
    for r in feat:
        id=r["instance_id"]
        rep=int(r["repetition"])
        repetitions.add(rep)
        if id in features:raise ValueError("duplicate feature id")
        features[id]=tuple(None if r[k]=="?" else float(r[k])
                           for k in attrs[2:])
    if repetitions!={1}:raise ValueError("unsupported feature repetitions")
    _,rows=read_arff(texts["cv.arff"])
    cv={}
    for r in rows:
        id=r["instance_id"]
        if id in cv:raise ValueError("duplicate official fold")
        cv[id]=int(r["fold"])
        if int(r["repetition"])!=1:raise ValueError("fold repetition")
    _,rows=read_arff(texts["feature_costs.arff"])
    costs={}
    for r in rows:
        id=r["instance_id"]
        if id in costs:raise ValueError("duplicate cost")
        costs[id]=None if r["base"]=="?" else float(r["base"])
        if int(r["repetition"])!=1:raise ValueError("cost repetition")
    _,rows=read_arff(texts["algorithm_runs.arff"])
    runs=defaultdict(dict)
    statuses=Counter()
    algos=set()
    for r in rows:
        id,algo=r["instance_id"],r["algorithm"]
        if int(r["repetition"])!=1:raise ValueError("run repetition")
        if algo in runs[id]:raise ValueError("duplicate (instance, solver)")
        value=float(r["PAR10"]);status=r["runstatus"]
        if not math.isfinite(value) or value<0:raise ValueError("invalid PAR10")
        if (status=="ok" and value>=18000) or (status!="ok" and value!=18000):
            raise ValueError("PAR10/runstatus contradiction")
        runs[id][algo]=(value,status)
        statuses[status]+=1;algos.add(algo)
    all_ids=[set(features),set(runs),set(cv),set(costs)]
    if len(set.union(*all_ids))!=len(set.intersection(*all_ids)):
        raise ValueError("incomplete external join")
    ids=sorted(features)
    algos=tuple(sorted(algos))
    if len(ids)!=EXPECTED_CASES or len(algos)!=EXPECTED_SOLVERS:
        raise ValueError("unexpected external population")
    if any(len(runs[i])!=len(algos) for i in ids):
        raise ValueError("incomplete runtime matrix")
    if sorted(set(cv.values()))!=list(range(1,11)):
        raise ValueError("official fold schema mismatch")
    for id in ids:
        if costs[id] is None or not math.isfinite(costs[id]) or costs[id]<0:
            raise ValueError("invalid base cost")
        if any(x is None or not math.isfinite(x) for x in features[id]):
            raise ValueError("invalid or missing features")
    return {"ids":ids,"features":features,"runs":runs,"folds":cv,
            "costs":costs,"algorithms":algos,
            "quality":{"instances":len(ids),"algorithms":len(algos),
                       "features":EXPECTED_FEATURES,"measurements":sum(map(len,runs.values())),
                       "statuses":dict(sorted(statuses.items())),
                       "official_folds":dict(sorted(Counter(cv.values()).items()))}}


def train_medians(train_ids,vectors):
    return tuple(statistics.median(vectors[id][j] for id in train_ids)
                 for j in range(len(next(iter(vectors.values())))))


def tree_fit(train_ids, data, vectors, thresholds,*,mode="lookahead",depth=2):
    """All costs and split thresholds are train-only.

    Greedy chooses best immediate split, then separately greedily refines.
    Lookahead searches the optimal root with independently optimal child
    splits for the *same* finite candidate medians, max depth 2.
    """
    if not train_ids:raise ValueError("no training records")
    ids=tuple(sorted(train_ids));d=len(thresholds)
    algos=data["algorithms"]
    runtime={id:tuple(data["runs"][id][a][0] for a in algos) for id in ids}
    bins={id:tuple(vectors[id][j]<=thresholds[j] for j in range(d))
          for id in ids}

    @lru_cache(None)
    def leaf(items):
        if not items:raise AssertionError("empty leaf")
        totals=[0.]*len(algos)
        for id in items:
            for j,value in enumerate(runtime[id]):
                totals[j]+=value
        best=min(range(len(algos)),key=lambda j:(totals[j],algos[j]))
        return totals[best],{"action":"solve","solver":algos[best]}

    @lru_cache(None)
    def split_children(items,j):
        left=tuple(i for i in items if bins[i][j])
        right=tuple(i for i in items if not bins[i][j])
        return left,right

    @lru_cache(None)
    def best_depth1(items):
        incumbent,node=leaf(items)
        for j in range(d):
            left,right=split_children(items,j)
            if not left or not right:continue
            left_loss,l_node=leaf(left)
            right_loss,r_node=leaf(right)
            score=left_loss+right_loss
            if score<incumbent-1e-9:
                incumbent=score
                node={"action":"split","feature":j,"threshold":thresholds[j],
                      "yes":l_node,"no":r_node}
        return incumbent,node

    if depth==1:return best_depth1(ids)
    if depth!=2 or mode not in ("greedy","lookahead"):
        raise ValueError("unsupported tree specification")
    if mode=="lookahead":
        best_cost,best_node=leaf(ids)
        for j in range(d):
            left,right=split_children(ids,j)
            if not left or not right:continue
            a,lnode=best_depth1(left)
            b,rnode=best_depth1(right)
            cost=a+b
            if cost<best_cost-1e-9:
                best_cost=cost
                best_node={"action":"split","feature":j,
                           "threshold":thresholds[j],"yes":lnode,"no":rnode}
        return best_cost,best_node
    _,root=best_depth1(ids)
    if root["action"]=="solve":
        return leaf(ids)
    j=root["feature"]
    left,right=split_children(ids,j)
    a,lnode=best_depth1(left)
    b,rnode=best_depth1(right)
    return a+b,{"action":"split","feature":j,"threshold":thresholds[j],
                "yes":lnode,"no":rnode}


def tree_predict(row,node):
    while node["action"]=="split":
        j=node["feature"]
        node=node["yes"] if row[j]<=node["threshold"] else node["no"]
    if node["action"]!="solve":raise AssertionError("unsupported tree leaf")
    return node["solver"]


def evaluate(data):
    output=[]
    fold_report=[]
    for fold in range(1,11):
        train=[id for id in data["ids"] if data["folds"][id]!=fold]
        test=[id for id in data["ids"] if data["folds"][id]==fold]
        normalizer=train_normalizer(train,data)
        vectors={id:normalize(data["features"][id],normalizer)
                 for id in train+test}
        thresholds=train_medians(train,vectors)
        sbs=_best_algo(train,data)
        loss1,t1=tree_fit(train,data,vectors,thresholds,depth=1)
        lossg,tg=tree_fit(train,data,vectors,thresholds,mode="greedy",depth=2)
        losso,to=tree_fit(train,data,vectors,thresholds,mode="lookahead",depth=2)
        if losso>lossg+1e-6:
            raise AssertionError("lookahead worse than greedy ON TRAIN")
        per_fold=defaultdict(list)
        for id in test:
            choice={
                "SBS":(sbs,False),
                "KNN5":(select_knn(train,id,data,vectors,5),True),
                "KNN15":(select_knn(train,id,data,vectors,15),True),
                "TREE_greedy1":(tree_predict(vectors[id],t1),True),
                "TREE_greedy2":(tree_predict(vectors[id],tg),True),
                "OMEGA_cost_lookahead2":(tree_predict(vectors[id],to),True),
                "VBS_oracle":(_best_algo([id],data),False)}
            for name in POLICIES:
                algo,uses=choice[name]
                tot,solved,par10,extra=score_measurement(id,algo,data,uses)
                record={"fold":fold,"instance":id,"arm":name,
                        "selected_solver":algo,"PAR10":par10,
                        "feature_cost":extra,"total":tot,"solved":solved}
                output.append(record)
                per_fold[name].append(record)
        fold_report.append({
            "fold":fold,"n_test":len(test),
            "train_loss":{"TREE_greedy1":loss1,"TREE_greedy2":lossg,
                          "OMEGA_cost_lookahead2":losso},
            "tree_root_features":{"greedy1":t1.get("feature"),
                                  "greedy2":tg.get("feature"),
                                  "lookahead2":to.get("feature")},
            "metrics":{name:metrics_renamed(per_fold[name]) for name in POLICIES}
        })
    grouped=defaultdict(list)
    for rec in output:grouped[rec["arm"]].append(rec)
    return {"status":"EXTERNAL_HISTORICAL_COST_SENSITIVE_TRANSFER_NOT_BLIND",
            "preregister_commit":"30331b960d91d23642628dee8713e09a10f9b30c",
            "source_commit":SOURCE_COMMIT,
            "data_quality":data["quality"],
            "official_folds":len(fold_report),
            "external_solver_executions":0,
            "llm_calls":0,
            "model_type":"cost_sensitive_binary_tree_adapter_not_original_omega",
            "scores":{name:metrics_renamed(grouped[name]) for name in POLICIES},
            "folds":fold_report,"ledger":output}


def metrics_renamed(rows):
    return {"n":len(rows),
            "mean_PAR10_plus_features":round(statistics.fmean(r["total"] for r in rows),6),
            "median_PAR10_plus_features":round(statistics.median(r["total"] for r in rows),6),
            "solved":sum(r["solved"] for r in rows),
            "solved_rate":round(sum(r["solved"] for r in rows)/len(rows),6),
            "mean_feature_cost":round(statistics.fmean(r["feature_cost"] for r in rows),6)}


def run(cache=None):
    inputs={name:load_source(name,cache) for name in SHA}
    return evaluate(parse(inputs))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--cache-dir",default=None)
    ap.add_argument("--json-output",default=None)
    args=ap.parse_args()
    result=run(args.cache_dir)
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result,indent=2,
            ensure_ascii=False,sort_keys=True),encoding="utf-8")
    print("ASLIB_WPMS_TRANSFER_RESULT "+json.dumps({
        "status":result["status"],
        "preregister_commit":result["preregister_commit"],
        "data_quality":result["data_quality"],
        "scores":result["scores"],
        "train_loss_check":"lookahead <= greedy across each fold",
        "external_solver_executions":0,
    },ensure_ascii=False,sort_keys=True))
