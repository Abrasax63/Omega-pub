"""Independent outcome recount from the IMMUTABLE OBS04 derived artifact.

No reading of model outputs beyond the recorded paired verdicts;
no imports from the first evaluator; no fitted parameters or source labels
can be changed. Descriptive after-run stratification was preregistered.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from pathlib import Path
import argparse
import json

LABELS={"ENTAILED","CONTRADICTED","NOT ENOUGH INFO"}

def audit(report):
    assert report["protocol"]=="P5-OBS-04"
    assert report["sources"]["sql"]["sha256"]==(
        "e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100")
    assert report["sources"]["gold"]["count"]==1000
    assert report["sources"]["no_tools"]["count"]==1000
    assert report["sources"]["sql"]["count"]==1000
    rows=report["case_audit"]
    if len(rows)!=1000 or len({x["claim_id"] for x in rows})!=1000:
        raise ValueError("missing, duplicate or invalid 1,000 paired verdicts")
    truth_groups=defaultdict(list)
    category_counts=Counter()
    k=Counter()
    for x in rows:
        gold,plain,sql=x["gold"],x["no_tools"],x["sql_tools"]
        if {gold,plain,sql}-LABELS:
            raise ValueError("unknown verdict, potential parser interpolation")
        agreement=(plain==sql)
        if agreement==x["disagrees"]:
            raise AssertionError("disagreement annotation flipped")
        truth_groups[gold].append(x)
        if plain==gold and sql==gold:k["both_correct"]+=1
        elif plain!=gold and sql!=gold and agreement:k["both_wrong_agree"]+=1
        elif plain!=gold and sql!=gold:k["both_wrong_disagree"]+=1
        elif plain==gold:k["plain_only_correct"]+=1
        else:k["sql_only_correct"]+=1
        if agreement:
            category_counts[sql]+=1
        if x["logged_sql_tool_outputs"]>x["logged_sql_tool_calls"]:
            raise AssertionError("output count exceeds call count")
    if sum(k.values())!=1000:
        raise AssertionError("contingency partition not complete")
    assert k["both_correct"]==291
    assert k["both_wrong_agree"]==17
    assert k["both_wrong_disagree"]==90
    assert k["plain_only_correct"]==66
    assert k["sql_only_correct"]==536
    rows_for_policies={}
    scores={
        "no_tools":[],
        "sql_tools":[],
        "agree_or_abstain":[],
        "sql_trace_gate":[],
        "reject_all":[],
    }
    stratified={}
    for label,sub in sorted(truth_groups.items()):
        agreeing=[r for r in sub if not r["disagrees"]]
        correct=sum(r["sql_tools"]==label for r in agreeing)
        stratified[label]={
            "total":len(sub),
            "consensus_published":len(agreeing),
            "consensus_correct":correct,
            "consensus_wrong":len(agreeing)-correct,
            "consensus_coverage":round(len(agreeing)/len(sub),6),
            "consensus_risk_on_published":round(
                (len(agreeing)-correct)/len(agreeing),6) if agreeing else None,
            "plain_correct":sum(r["no_tools"]==label for r in sub),
            "sql_correct":sum(r["sql_tools"]==label for r in sub),
        }
    for x in rows:
        choices={
            "no_tools":x["no_tools"],
            "sql_tools":x["sql_tools"],
            "agree_or_abstain":x["sql_tools"] if not x["disagrees"] else None,
            "sql_trace_gate":x["sql_tools"] if x["logged_sql_tool_outputs"]>0 else None,
            "reject_all":None,
        }
        for policy,prediction in choices.items():
            g=x["gold"]
            scores[policy].append(0.05 if prediction is None else
                1 if prediction==g else -2)
    for name,points in scores.items():
        prior=report["model_policies"][name]["total_utility"]
        if abs(sum(points)-prior)>1e-6:
            raise AssertionError(f"independent net-score mismatch {name}")
        rows_for_policies[name]={
            "total_utility":round(sum(points),6),
            "fully_independent_recount":True,
        }
    if sum(v["consensus_published"] for v in stratified.values())!=308:
        raise AssertionError("consensus coverage wrong")
    if sum(v["consensus_wrong"] for v in stratified.values())!=17:
        raise AssertionError("consensus errors wrong")
    return {
        "status":"INDEPENDENT_RECOUNT_OF_REAL_PAIRED_MODEL_TRACES",
        "paired_cases":1000,
        "contingency":dict(k),
        "consensus_prediction_labels":dict(category_counts),
        "by_gold_label":stratified,
        "model_source_independent":False,
        "database_golds_reexecuted":False,
        "experiments_are_prompt_and_tools_confounded":True,
        "all_metrics_exploratory_public_test":True,
        "policy_utility_crosscheck":rows_for_policies,
        "interpretation":"High consensus selective precision is predominantly driven "
                         "by agreement on NOT ENOUGH INFO; not broad verification "
                         "of entailed or contradicted claims.",
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    data=json.loads(args.source.read_text(encoding="utf-8"))
    result=audit(data)
    args.output.write_text(json.dumps(result,ensure_ascii=False,
                  sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("P5_OBS04_INDEPENDENT_STRATIFIED_AUDIT",
          json.dumps(result,sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
