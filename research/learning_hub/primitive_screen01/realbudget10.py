"""REALBUDGET10: verify frozen DEVBASE08 traces; constrain real adaptive plan.
No model weights, no training, no holdout access.
"""
import argparse, json, hashlib
from pathlib import Path
import curriculum06 as c
import trainer07 as t
import loop09 as l
import devbase08 as d
DEV_LABEL_SHA="566397279e96838b119dbac29f0b5c4569331b66d8d01036c289e9faebf34444"
DEV_PRED_SHA="62ee2a83732c2aa38caeb1dde87be449bfb4032e421162bcbee713c5a96b83eb"
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(labels,predictions,result):
    need(sha(labels)==DEV_LABEL_SHA and sha(predictions)==DEV_PRED_SHA,"FROZEN_DEV_HASH")
    rows=json.loads(Path(labels).read_text())
    need(rows==c.build("dev",t.SEED+1),"DEV_REGENERATION")
    records=[json.loads(x) for x in Path(predictions).read_text().splitlines()]
    score=d.score(rows,records);old=json.loads(Path(result).read_text())
    need(old["labels_sha"]==DEV_LABEL_SHA and old["predictions_sha"]==DEV_PRED_SHA and old["revision"]==c.REV,"SOURCE_IDENTITY")
    need(all(score[k]==old[k] for k in score),"RECOMPUTED_SCORE")
    return score
def preflight(labels,predictions,result,out):
    score=audit(labels,predictions,result)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    tr=c.build("train",t.SEED);enc=t.prepare(tok,tr)
    plans={k:c.schedule(tr,k,1234) for k in ("supervised","contrastive")}
    plans["adaptive"],report=l.match(tr,enc,score["dev_pair_errors"])
    budgets={k:t.budget(enc,p) for k,p in plans.items()}
    need(budgets["supervised"]==budgets["contrastive"],"BASE_BUDGET")
    need(len({(b["steps"],b["examples"],b["forward_sequences"],b["padded_positions"]) for b in budgets.values()})==1,"COMPUTE_BUDGET")
    spread={f:(max(b[f] for b in budgets.values())-min(b[f] for b in budgets.values()))/min(b[f] for b in budgets.values()) for f in l.FIELDS}
    need(all(x<=l.TOL for x in spread.values()),"TOKEN_BUDGET")
    # Explicitly distinguish allocation feasibility and an actually different treatment.
    delta=sum(abs(report["achieved"][k]-32) for k in c.KINDS)//2
    obj=dict(status="REAL_DEV_BUDGET_AUDITED",dev_run=45658613634,dev_label_sha=DEV_LABEL_SHA,dev_predictions_sha=DEV_PRED_SHA,dev_scores=score["scores"],dev_pair_errors=score["dev_pair_errors"],budgets=budgets,relative_spread=spread,requested=report["requested"],achieved=report["achieved"],remaining_quota_gap=report["remaining_quota_gap"],reallocated_pairs=delta,nontrivial_allocation=delta>0,plans=plans,training_authorized=False,scope="same-author development fixture; tokenizer-only budget, not measured wall time or learning",remaining_gates=["independently authored sealed exam","full Qwen training runner audit","actual model update and evaluation release"])
    Path(out).write_text(json.dumps(obj,indent=2));print(json.dumps({k:v for k,v in obj.items() if k!="plans"},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for a in ("labels","predictions","result","out"):p.add_argument("--"+a,required=True)
    a=p.parse_args();preflight(a.labels,a.predictions,a.result,a.out)
