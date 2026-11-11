"""Post-result audit of information value, paired actions, and upper bound.

All diagnostics are computed after STRAT-004 was frozen and scored. This is
not an additional prospective arm, a trained model, or a new claim of
generalization.
"""
from collections import defaultdict
from fractions import Fraction
import json

from intermediate_evidence_gateway import (
    cases, run_check, ROUTE_TO_SPECIALIST, _actual_truth,
)
from intermediate_evidence_policy import evaluate


def audit():
    report=evaluate()
    holdout=[t for t in cases() if t["partition"]=="test"]
    groups=defaultdict(lambda:{"n":0,"yes":0,"no":0,"outages":0})
    for task in holdout:
        route=run_check(task,"probe")["outcome"]
        g=groups[route]
        g["n"]+=1
        g["yes" if _actual_truth(task) else "no"]+=1
        g["outages"]+=int(task["simulated_outage"])
    all_yes=sum(g["yes"] for g in groups.values())
    total=sum(g["n"] for g in groups.values())
    prior=Fraction(all_yes,total)
    posterior={key:Fraction(g["yes"],g["n"]) for key,g in groups.items()}
    if any(p!=prior for p in posterior.values()):
        raise AssertionError("probe leaks answer information")
    by_case=defaultdict(dict)
    for row in report["traces"]:
        by_case[row["id"]][row["arm"]]=row
    pairs=[]
    for case_id,arms in sorted(by_case.items()):
        entries=[arms[a] for a in
                 ("C_omega","D_certificate","E_strong_conditional")]
        pairs.append({
            "case":case_id,
            "same_certified_answer":len({r["decision"] for r in entries})==1,
            "same_actions_and_outcomes":(
                [r["trace"] for r in entries].count(entries[0]["trace"])==3),
        })
    status=report["scores"]
    return {
        "status":"POST_RESULT_THEORY_AUDIT_ONLY",
        "answer_prior":str(prior),
        "route_conditional_answer_probability":
            {k:str(v) for k,v in sorted(posterior.items())},
        "probe_immediate_answer_information_bits":"0",
        "route_statistics":dict(sorted(groups.items())),
        "n_unavoidable_simulated_outages":sum(g["outages"] for g in groups.values()),
        "best_adaptive_certifications":status["D_certificate"]["correct"],
        "best_fixed_certifications":status["B_specialists"]["correct"],
        "absolute_certification_gain":
            status["D_certificate"]["correct"]-status["B_specialists"]["correct"],
        "paired_C_D_E_identical":all(
            r["same_certified_answer"] and r["same_actions_and_outcomes"]
            for r in pairs),
        "fixed_max_route_coverage_under_two_exclusive_specialists":14,
        "test_total":total,
        "scored_cases":pairs,
        "generalization_outside_sealed_envelopes":"NOT_ESTABLISHED",
    }


if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,indent=2,sort_keys=True))
