"""Independent post-run audit for OMEGA-ATOMIC-TUTOR-07.

Reconstructs truth by component cliques, independently verifies positive
partitions and negative atomic-edge witnesses, checks all serialized raw
outputs and feedback. Does not call any LLM or promote scientific claims.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from incremental_math_library import canonical
from omega_hybrid_tutor07 import (
    ARMS, AXIOMS, MODEL_SHA, NODES, PROTOCOL, SEED, TRAIN_NODES,
    independent_oracle, make_holdout, make_training, teacher_feedback
)

STATUSES=("POINTWISE_CONTEXT_TRANSFER_OBSERVED",
          "REGISTERED_CONTEXT_GAIN_NOT_OBSERVED","INDETERMINATE_BUDGET")

def verify_certificate(nodes,edges,holds,cert):
    e=set(edges)
    if not isinstance(cert,dict):
        return False
    if holds:
        if set(cert)!={"kind","blocks"} or cert.get("kind")!="partition":
            return False
        blocks=cert.get("blocks")
        if not isinstance(blocks,list) or not blocks:return False
        flat=[]
        for block in blocks:
            if not isinstance(block,list) or not block or any(
                type(n) is not str or n not in nodes for n in block):
                return False
            flat+=block
        if len(flat)!=len(nodes) or set(flat)!=set(nodes):
            return False
        return {(a,b) for block in blocks for a in block for b in block}==e
    if set(cert)!={"kind","triple","premises"} or cert.get("kind")!="missing_transitive_edge":
        return False
    triple=cert.get("triple")
    premises=cert.get("premises")
    if not isinstance(triple,list) or len(triple)!=3 or any(
            type(x) is not str or x not in nodes for x in triple):
        return False
    if not isinstance(premises,dict) or set(premises)!={"xy","yz","xz"} or any(
            type(premises[k]) is not bool for k in ("xy","yz","xz")):
        return False
    a,b,c=triple
    truth={"xy":(a,b) in e,"yz":(b,c) in e,"xz":(a,c) in e}
    return premises==truth and truth=={"xy":True,"yz":True,"xz":False}


def independently_score(raw,nodes,edges):
    truth=independent_oracle(nodes,edges)
    bad={"status":"INVALID","boolean_correct":False,"axioms_correct":False,
         "certificate_correct":False,"atomic_bits_correct":False,
         "fully_certified":False}
    if not isinstance(raw,str):return bad
    try:o=json.loads(raw.strip())
    except (TypeError,ValueError):return bad
    if o=={"abstain":True}:return {**bad,"status":"ABSTAIN"}
    if not isinstance(o,dict) or set(o)!={"holds","failed_axioms","certificate"} or type(o["holds"]) is not bool:
        return bad
    fails=o["failed_axioms"]
    if not isinstance(fails,list) or any(type(x) is not str or x not in AXIOMS for x in fails) or (
       len(fails)!=len(set(fails))) or o["holds"] != (len(fails)==0):
        return bad
    b=o["holds"]==truth
    a=b and set(fails)==(set() if truth else {"transitive"})
    c=verify_certificate(nodes,edges,o["holds"],o["certificate"])
    atomic=c
    cert=o["certificate"]
    if (not o["holds"] and isinstance(cert,dict) and
        set(cert)=={"kind","triple","premises"} and cert.get("kind")=="missing_transitive_edge"):
        triple=cert.get("triple")
        p=cert.get("premises")
        if isinstance(triple,list) and len(triple)==3 and all(
            type(x) is str and x in nodes for x in triple
        ) and isinstance(p,dict) and set(p)=={"xy","yz","xz"} and all(
            type(p[k]) is bool for k in ("xy","yz","xz")
        ):
            x,y,z=triple
            atomic=p=={"xy":(x,y) in edges,"yz":(y,z) in edges,"xz":(x,z) in edges}
    return {"status":"ANSWER","boolean_correct":b,"axioms_correct":a,
            "certificate_correct":c,"atomic_bits_correct":atomic,
            "fully_certified":a and c}


def audit(report,q,a):
    def blocked(reason):
        return {"status":"BLOCKED","reason":reason,
                "certified_new_skills":0}
    if not isinstance(report,dict) or report.get("protocol")!=PROTOCOL:
        return blocked("PROTOCOL_INVALID")
    expected_q,expected_a=make_holdout()
    if q!=expected_q or a!=expected_a:
        return blocked("FROZEN_MANIFEST_CONTENT_MISMATCH")
    if report.get("input_manifest_sha256")!=sha256(canonical(q).encode()).hexdigest() or (
        report.get("oracle_manifest_sha256")!=sha256(canonical(a).encode()).hexdigest()):
        return blocked("FROZEN_MANIFEST_DIGEST_MISMATCH")
    if report.get("model_weights_sha256_expected")!=MODEL_SHA or (
        report.get("model_weights_updated") is not False):
        return blocked("MODEL_IDENTITY_OR_UPDATE_INCONSISTENT")
    if report.get("status") not in STATUSES:
        return blocked("REAL_EXPERIMENT_NOT_COMPLETE")
    if (report.get("train_calls"),report.get("note_calls"),
        report.get("evaluation_calls"))!=(4,2,24):
        return blocked("INCOMPLETE_MODEL_CALLS")
    training=report.get("training")
    if not isinstance(training,dict) or set(training)!={"G","T"}:
        return blocked("TRAINING_ARM_MISSING")
    for arm in ("G","T"):
        rows=training[arm].get("traces")
        if not isinstance(rows,list) or len(rows)!=2:
            return blocked("TRAINING_LOG_INCOMPLETE")
        for logged,task in zip(rows,make_training()):
            if logged.get("training_id")!=task["id"]:
                return blocked("TRAINING_CASE_MISMATCH")
            ans=logged.get("output",{})
            raw=ans.get("raw")
            if not isinstance(raw,str) or ans.get("raw_sha256")!=sha256(raw.encode()).hexdigest():
                return blocked("TRAINING_RAW_TAMPERED")
            if logged.get("feedback")!=teacher_feedback(task,raw,arm):
                return blocked("TRAINING_FEEDBACK_TAMPERED")
        note=training[arm].get("note",{}).get("output",{})
        raw=note.get("raw")
        if not isinstance(raw,str) or note.get("raw_sha256")!=sha256(raw.encode()).hexdigest():
            return blocked("TRANSFER_NOTE_TAMPERED")
    if not isinstance(report.get("evaluation"),list) or len(report["evaluation"])!=8:
        return blocked("HOLDOUT_INCOMPLETE")
    calculated={arm:{"n":8,"boolean_correct":0,"axioms_correct":0,
            "certificate_correct":0,"fully_certified":0,"invalid":0,
            "abstain":0,"prompt_tokens":0,"completion_tokens":0,
            "model_seconds":0.0,"positive_certified":0,"negative_certified":0}
            for arm in ARMS}
    ids={x["id"]:x for x in a["answers"]}
    all_balanced=True
    for question,row in zip(q["questions"],report["evaluation"]):
        if row.get("id")!=question["id"] or set(row.get("arms",{}))!=set(ARMS):
            return blocked("HOLDOUT_CASE_OR_ARMS_CHANGED")
        nodes=tuple(question["nodes"])
        edges=frozenset(map(tuple,question["edges"]))
        truth=independent_oracle(nodes,edges)
        if truth!=ids[question["id"]]["holds"]:
            return blocked("ALTERNATIVE_ORACLE_DISAGREES")
        tokens=[]
        for arm in ARMS:
            ans=row["arms"][arm]
            raw=ans.get("raw")
            if not isinstance(raw,str) or ans.get("raw_sha256")!=sha256(raw.encode()).hexdigest():
                return blocked("RAW_GENERATION_TAMPERED")
            score=independently_score(raw,nodes,edges)
            # No acceptance of the original scorer's unverified decision.
            if score!=ans.get("score"):
                return blocked("SCORING_DISAGREEMENT_"+arm)
            usage=ans.get("usage",{})
            pt=usage.get("prompt_tokens");ct=usage.get("completion_tokens")
            if type(pt) is not int or pt<=0 or type(ct) is not int or ct<0:
                return blocked("TOKEN_ACCOUNTING_MISSING")
            tokens.append(pt)
            m=calculated[arm]
            for field in ("boolean_correct","axioms_correct","certificate_correct",
                          "fully_certified"):
                m[field]+=int(score[field])
            m["invalid"]+=int(score["status"]=="INVALID")
            m["abstain"]+=int(score["status"]=="ABSTAIN")
            m["prompt_tokens"]+=pt;m["completion_tokens"]+=ct
            m["model_seconds"]+=ans.get("time_s",0)
            if score["fully_certified"]:
                m["positive_certified" if truth else "negative_certified"]+=1
        if max(tokens)-min(tokens) > .05*max(tokens):
            all_balanced=False
    declared=report.get("metrics",{})
    for arm in ARMS:
        computed=calculated[arm]
        for key in ("n","boolean_correct","axioms_correct","certificate_correct",
                    "fully_certified","invalid","abstain","prompt_tokens","completion_tokens"):
            if computed[key]!=declared.get(arm,{}).get(key):
                return blocked("AGGREGATE_MISMATCH_"+arm+"_"+key)
    if all_balanced is False and report.get("actual_eval_prompts_balanced") is not False:
        return blocked("BALANCE_FLAG_FALSIFIED")
    T=calculated["T"];G=calculated["G"];D=calculated["D"]
    gain=(all_balanced and report.get("actual_eval_prompts_balanced") is True
          and T["fully_certified"]>=6 and T["positive_certified"]>=3
          and T["negative_certified"]>=3
          and T["fully_certified"]-G["fully_certified"]>=2
          and T["fully_certified"]-D["fully_certified"]>=2
          and T["invalid"]==0)
    if report.get("registered_gain")!=bool(gain):
        return blocked("GAIN_THRESHOLD_FALSIFIED")
    status="POINTWISE_CONTEXT_TRANSFER_OBSERVED" if gain else (
       "INDETERMINATE_BUDGET" if not report["actual_eval_prompts_balanced"] else
       "REGISTERED_CONTEXT_GAIN_NOT_OBSERVED")
    if report["status"]!=status:
        return blocked("EPIS_TEMIC_STATUS_INCONSISTENT")
    return {"status":"EXTERNAL_RESCORING_PASSED_DESCRIPTIVE_ONLY",
            "metrics":calculated,
            "T_minus_D_fully_certified":T["fully_certified"]-D["fully_certified"],
            "T_minus_G_fully_certified":T["fully_certified"]-G["fully_certified"],
            "threshold_met":bool(gain),
            "input_budget_comparable":all_balanced,
            "certified_new_skills":0,
            "statistical_significance":False,
            "weights_updated":False}


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    load=lambda filename:json.loads((args.folder/filename).read_text(encoding="utf-8"))
    result=audit(load("report.json"),load("model_inputs.json"),load("oracle_only.json"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"reason":result.get("reason"),
                      "new_scientific_competences":0}))
    if result["status"]!="EXTERNAL_RESCORING_PASSED_DESCRIPTIVE_ONLY":
        raise SystemExit("SCIENTIFIC_EVIDENCE_AUDIT_BLOCKED")

if __name__=="__main__":main()
