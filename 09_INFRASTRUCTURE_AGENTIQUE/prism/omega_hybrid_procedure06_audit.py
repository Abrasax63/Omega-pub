"""Fail-closed offline auditor for real OMEGA-PROCEDURE-06 artifacts.

Check hashes, frozen answers, model outputs, graph certificates and costs.
No model calls and no inference of training or autonomous new abilities.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

from incremental_math_library import canonical
from omega_hybrid_procedure06 import (
    ARMS, PROTOCOL, make_manifest, valid_answer, independent_clique_check
)

ALLOWED = ("POINTWISE_PROCEDURE_GAIN_OBSERVED",
           "PRE_REGISTERED_GAIN_NOT_OBSERVED","INDETERMINATE_BUDGET")

def audit(report, supplied_questions, supplied_oracle):
    def fail(reason):
        return {"status":"BLOCKED","reason":reason,
                "new_scientific_skill_certified":False}
    if not isinstance(report,dict) or report.get("protocol")!=PROTOCOL:
        return fail("PROTOCOL_MISMATCH")
    expected_questions,expected_oracle=make_manifest()
    if supplied_questions!=expected_questions or supplied_oracle!=expected_oracle:
        return fail("FROZEN_MANIFEST_CHANGED")
    for source,field in ((supplied_questions,"frozen_question_sha256"),
                         (supplied_oracle,"frozen_oracle_sha256")):
        if sha256(canonical(source).encode()).hexdigest()!=report.get(field):
            return fail("FROZEN_MANIFEST_DIGEST_MISMATCH")
    if report.get("status") not in ALLOWED:
        return fail("NOT_A_COMPLETED_SCIENTIFIC_RUN")
    if report.get("model_calls")!=24 or report.get("model_weights_updated") is not False:
        return fail("MISSING_CALLS_OR_WEIGHTS_CHANGED")
    trials=report.get("trials")
    if not isinstance(trials,list) or len(trials)!=8:
        return fail("WRONG_TRIAL_COUNT")
    truth_index={x["id"]:x for x in supplied_oracle["answers"]}
    metrics={a:{"full_axioms_correct":0,"holds_correct":0,
                "certificate_valid":0,"invalid_format":0,
                "invalid_certificate":0,"abstain":0,"input_tokens":0,
                "output_tokens":0} for a in ARMS}
    observations=[]
    balanced=True
    for question,row in zip(supplied_questions["questions"],trials):
        ident=question["id"]
        if row.get("id")!=ident or ident not in truth_index or set(row.get("arms",{}))!=set(ARMS):
            return fail("MISMATCHED_TRIAL_ID_OR_MISSING_ARM")
        edges=frozenset(map(tuple,question["edges"]))
        truth=truth_index[ident]
        if independent_clique_check(edges)!=truth["holds"]:
            return fail("INDEPENDENT_ORACLE_DISAGREES")
        item={"id":ident,"truth":truth["holds"],"full":{},"certified":{}}
        lengths=[]
        for arm in ARMS:
            entry=row["arms"][arm]
            if not isinstance(entry,dict) or not isinstance(entry.get("raw"),str):
                return fail("MISSING_RAW_REPLY")
            raw=entry["raw"]
            if sha256(raw.encode()).hexdigest()!=entry.get("raw_sha256"):
                return fail("RAW_REPLY_DIGEST_TAMPERED")
            verdict=valid_answer(raw,truth,arm,edges)
            if verdict!=entry.get("verdict"):
                return fail("SCORE_RECOMPUTATION_MISMATCH")
            usage=entry.get("usage")
            if not isinstance(usage,dict) or any(
                type(usage.get(k)) is not int or usage[k]<0 for k in
                ("prompt_tokens","completion_tokens")
            ) or usage["prompt_tokens"]==0:
                return fail("MODEL_TOKEN_ACCOUNTING_MISSING")
            lengths.append(usage["prompt_tokens"])
            for key,field in (("full_axioms_correct","full_axioms_correct"),
                              ("holds_correct","holds_correct")):
                metrics[arm][key]+=int(verdict[field])
            metrics[arm]["certificate_valid"]+=int(verdict["certificate_valid"] is True)
            metrics[arm]["invalid_format"]+=int(verdict["status"]=="INVALID_FORMAT")
            metrics[arm]["invalid_certificate"]+=int(verdict["status"]=="CERTIFICATE_INVALID")
            metrics[arm]["abstain"]+=int(verdict["status"]=="ABSTAIN")
            metrics[arm]["input_tokens"]+=usage["prompt_tokens"]
            metrics[arm]["output_tokens"]+=usage["completion_tokens"]
            item["full"][arm]=bool(verdict["full_axioms_correct"])
            item["certified"][arm]=verdict["certificate_valid"] is True
        if max(lengths)-min(lengths)>.05*max(lengths):
            balanced=False
        observations.append(item)
    actual=report.get("metrics")
    if not isinstance(actual,dict) or set(actual)!=set(ARMS):
        return fail("AGGREGATE_MISSING")
    for arm in ARMS:
        for key,value in metrics[arm].items():
            expected=value if key!="certificate_valid" or arm=="P" else None
            if actual[arm].get(key)!=expected:
                return fail("AGGREGATE_TAMPERED_"+arm+"_"+key)
    if report.get("actual_input_budget_comparable") is not balanced and (
            not balanced or report.get("model_prompt_cost_balanced") is False):
        # One or both guards failed, so the global measure must be false.
        if report.get("actual_input_budget_comparable") is not False:
            return fail("BUDGET_FLAG_TAMPERED")
    p,d,r=(metrics[a]["full_axioms_correct"] for a in ("P","D","R"))
    should_gain=(balanced and report.get("model_prompt_cost_balanced") is True
                 and p>=6 and p-d>=2 and p-r>=2
                 and metrics["P"]["certificate_valid"]>=6
                 and metrics["P"]["invalid_format"]==0)
    if bool(report.get("gain_criterion_met"))!=should_gain:
        return fail("GAIN_FLAG_TAMPERED")
    should_status=("POINTWISE_PROCEDURE_GAIN_OBSERVED" if should_gain else
                   "INDETERMINATE_BUDGET" if not balanced or
                   report.get("model_prompt_cost_balanced") is False else
                   "PRE_REGISTERED_GAIN_NOT_OBSERVED")
    if report["status"]!=should_status:
        return fail("STATUS_NOT_REPRODUCED")
    return {"status":"AUDIT_PASSED_DESCRIPTIVE_ONLY",
            "case_count":len(observations),"metrics_recomputed":metrics,
            "paired":{ "P_minus_D_full":p-d,"P_minus_R_full":p-r,
                "P_better_D":sum(x["full"]["P"] and not x["full"]["D"] for x in observations),
                "D_better_P":sum(x["full"]["D"] and not x["full"]["P"] for x in observations),
                "P_better_R":sum(x["full"]["P"] and not x["full"]["R"] for x in observations),
                "R_better_P":sum(x["full"]["R"] and not x["full"]["P"] for x in observations)},
            "correct_classifications_without_valid_P_certificate":sum(
                x["full"]["P"] and not x["certified"]["P"] for x in observations),
            "input_budget_comparable":balanced,
            "pointwise_gain_condition":should_gain,
            "new_scientific_skill_certified":False,
            "model_weights_trained":False,
            "sample_reuse_prohibits_independent_replication":True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    load=lambda name:json.loads((args.folder/name).read_text(encoding="utf-8"))
    result=audit(load("report.json"),load("model_inputs.json"),
                 load("oracle_only.json"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"reason":result.get("reason")}))
    if result["status"]!="AUDIT_PASSED_DESCRIPTIVE_ONLY":
        raise SystemExit("EVIDENCE_AUDIT_FAILED")

if __name__=="__main__":
    main()
