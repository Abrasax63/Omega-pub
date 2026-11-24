"""Offline recovery of scores from frozen MEMBERSHIP-SFT01 artifacts.
No LLM, gradient, regeneration or change to preregistered metrics.
"""
import argparse
import json
from pathlib import Path
from membership_sft_contract import read_frozen,score_pair,sha

def recover(labels,predictions,eval_sha,predictions_sha):
    rows=read_frozen(labels,eval_sha,"eval")
    if sha(predictions)!=predictions_sha:
        raise ValueError("PREDICTIONS_DIGEST")
    records=[json.loads(s) for s in Path(predictions).read_text().splitlines()]
    report=score_pair(rows,records)
    report.update(eval_sha256=eval_sha,predictions_sha256=predictions_sha,
                  recovery="OFFLINE_SCORE_ONLY_NO_REGENERATION")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("labels","predictions","eval-sha","predictions-sha","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    report=recover(a.labels,a.predictions,a.eval_sha,a.predictions_sha)
    with Path(a.out).open("x") as f: json.dump(report,f,indent=2)
    print(report["status"],json.dumps(report["comparisons"]))
    for arm,views in report["scores"].items():
        for view,s in views.items(): print(arm,view,s["correct"],s["pairs_both_correct"])
