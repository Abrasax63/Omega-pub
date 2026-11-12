"""P5 ACTIVE-01: explicit, cheap audit that a verification benchmark is discriminating.

Reads a PUBLIC completed output report; does not fit parameters or change any
predicted labels. If all VOI methods verify the same cheapest domain, an
apparent comparison of 'adaptive' and 'nonadaptive' policies is not credible.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

STRONG=("voi_static","voi_online","voi_discount","voi_margin",
        "omega_candidate","omega_no_change")
FAIL_FAMILY_SHARE=.875  # pre-announced 14/16 same-domain gate
STATUS="EXPLORATORY_DESIGN_AUDIT_NOT_A_NEW_MODEL_EXPERIMENT"

def diagnose(report):
    if report.get("protocol")!="P5-ACTIVE-01":
        raise ValueError("not an ACTIVE-01 report")
    policies=report["policies"]
    counts={}
    decisions={}
    for name in STRONG:
        rows=policies[name]["trajectory"]
        if len(rows)!=64:
            raise ValueError("must have all 64 evaluation candidate records")
        selected=[]
        for t in range(16):
            chosen=[x for x in rows if x["round"]==t and x["action"]=="VERIFY"]
            if len(chosen)>1:
                raise ValueError("a round oververified")
            selected.append(chosen[0]["kind"] if chosen else "NONE")
        counts[name]=dict(Counter(selected))
        decisions[name]=selected
    biased={name:(max(Counter(seq).values())/len(seq))
            for name,seq in decisions.items()}
    unique_patterns=len({tuple(x) for x in decisions.values()})
    alarm_diff=report["omega_vs_no_change_action_differences"]
    by_model={}
    for model in ("small","large"):
        rows=[r for r in report["raw_model_scores"]
              if r["model"]==model and r["split"]=="test"]
        if len(rows)!=32:
            raise ValueError("incomplete model data")
        correct=[r["answer"]==r["gold_posthoc_only"] for r in rows]
        brier=sum((float(r["confidence"])-int(y))**2
                  for r,y in zip(rows,correct))/len(rows)
        by_model[model]={
            "test_cases":len(rows),"correct":sum(correct),
            "reported_confidence_mean":round(sum(
                r["confidence"] for r in rows)/len(rows),6),
            "brier_over_constrained_choice":round(brier,6),
            "answer_counts":dict(Counter(r["answer"] for r in rows)),
        }
    # Non-discriminability is a limit of the benchmark, NOT a verdict on all
    # possible Omega adaptivity; no alarm / no different action is a separate
    # direct falsification of this particular new controller.
    nondiscriminating=(
        min(biased.values())>=FAIL_FAMILY_SHARE or unique_patterns==1)
    return {
        "status":STATUS,
        "strong_policy_verification_families":counts,
        "strong_policy_round_decisions_unique":unique_patterns,
        "strong_policy_max_single_family_share":{
            k:round(v,5) for k,v in biased.items()},
        "strong_policies_choose_same_every_round":unique_patterns==1,
        "design_gate":"FAIL_NON_DISCRIMINATING" if nondiscriminating
                      else "PASS_SELECTION_DIVERSITY",
        "omega_action_differences_vs_ablation":alarm_diff,
        "omega_utility_minus_discount":report["omega_minus_discount"],
        "model_scores_are_not_calibrated_probabilities":True,
        "test_model_diagnostics":by_model,
        "conclusion":"NO_OMEGA_SPECIFIC_ADAPTIVE_GAIN_DEMONSTRATED",
        "next_benchmark_conditions":[
            "Show substantive variation in policy verification choices before expensive model scoring",
            "Report chosen-feedback selection bias, never expose unchosen labels",
            "Use classical paid-observation bandit and Bayesian VOI controls",
            "Cost and task value must not make one domain universally dominant",
            "If only chosen verifications reveal truth, retain an exploratory policy for identifiability",
            "Score predictive confidence calibration separately from expected rewards",
            "Do not claim gains from hindsight-selected protocols or parsers",
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--report",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    result=diagnose(json.loads(args.report.read_text(encoding="utf-8")))
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,
                     ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print("ACTIVE01_GATE",json.dumps(result,sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
