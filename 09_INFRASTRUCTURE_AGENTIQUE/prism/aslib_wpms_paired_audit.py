"""Post-result, non-tuned paired diagnostics of the frozen WPMS transfer.

This script does NOT fit any strategy or change scores. Its input is the
complete per-instance ledger produced by the preregistered evaluation.
"""
import argparse
from collections import defaultdict
import json
import statistics

N=630
ARMS=("SBS","KNN5","KNN15","TREE_greedy1",
      "TREE_greedy2","OMEGA_cost_lookahead2","VBS_oracle")


def paired_audit(report):
    groups=defaultdict(dict)
    for row in report["ledger"]:
        name=row["instance"]
        arm=row["arm"]
        if arm in groups[name]:
            raise AssertionError("duplicated (instance,arm)")
        groups[name][arm]=row
    if len(groups)!=N or any(set(v)!=set(ARMS) for v in groups.values()):
        raise AssertionError("incomplete external predictions")
    differences=defaultdict(list)
    pair_names=[
        ("OMEGA_cost_lookahead2","TREE_greedy2"),
        ("OMEGA_cost_lookahead2","KNN5"),
        ("OMEGA_cost_lookahead2","SBS"),
        ("TREE_greedy2","TREE_greedy1"),
        ("KNN5","SBS")]
    for key,records in sorted(groups.items()):
        if len({r["fold"] for r in records.values()})!=1:
            raise AssertionError("test fold disagreement")
        baseline=records["VBS_oracle"]
        for name,entry in records.items():
            if name!="VBS_oracle" and baseline["PAR10"]>entry["PAR10"]+1e-9:
                raise AssertionError("oracle worse than a run on an instance")
        for pair in pair_names:
            a,b=pair
            v=records[a]["total"]-records[b]["total"]
            differences[pair].append((records[a]["fold"],v,
                                      records[a]["selected_solver"]!=records[b]["selected_solver"]))
    result={}
    for pair,items in differences.items():
        label=pair[0]+" minus "+pair[1]
        vals=[x[1] for x in items]
        fs=sorted(set(x[0] for x in items))
        result[label]={
            "mean_paired_difference_seconds":round(statistics.fmean(vals),6),
            "median_difference_seconds":round(statistics.median(vals),6),
            "selected_solver_diff_instances":sum(x[2] for x in items),
            "cases_better":sum(x<-1e-9 for x in vals),
            "cases_worse":sum(x>1e-9 for x in vals),
            "cases_equal":sum(abs(x)<=1e-9 for x in vals),
            "mean_delta_by_fold":{
                str(f):round(statistics.fmean(x[1] for x in items if x[0]==f),6)
                for f in fs},
        }
    by_arm=defaultdict(list)
    for records in groups.values():
        for arm,r in records.items():by_arm[arm].append(r["feature_cost"])
    feature_arms=("KNN5","KNN15","TREE_greedy1","TREE_greedy2",
                  "OMEGA_cost_lookahead2")
    if any(len(by_arm[name])!=N for name in ARMS):
        raise AssertionError("missing arm")
    for records in groups.values():
        cost=[records[a]["feature_cost"] for a in feature_arms]
        if max(cost)-min(cost)>1e-12:
            raise AssertionError("unequal feature cost")
        if records["SBS"]["feature_cost"]!=0 or records["VBS_oracle"]["feature_cost"]!=0:
            raise AssertionError("incorrect SBS/VBS feature charge")
    for f in report["folds"]:
        c=f["train_loss"]
        if c["OMEGA_cost_lookahead2"]>c["TREE_greedy2"]+1e-6:
            raise AssertionError("lookahead train objective not optimized")
    return {"status":"POST_RESULT_PAIRED_DIAGNOSTIC_NO_POLICY_TUNING",
            "n":N,"paired_results":result,
            "all_feature_arms_pay_exact_same_base_cost":True,
            "all_folds_lookahead_train_loss_at_most_greedy":True}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("ledger_file")
    args=ap.parse_args()
    data=json.loads(open(args.ledger_file,encoding="utf-8").read())
    print("ASLIB_WPMS_PAIRED_AUDIT "+json.dumps(paired_audit(data),
                                                ensure_ascii=False,sort_keys=True))
