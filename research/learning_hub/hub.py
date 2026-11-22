"""Omega Learning Hub: consolidate existing audited learning components.

Single read-only admission/evaluation entry point. Reuses V1/V2/V3/
verified_python_training_export. No trainer, browser, paid API, hidden case
replay, source code mutation, or silent PR merging.

Commands:
  python research/learning_hub/hub.py inspect --registry ... 
  python research/learning_hub/hub.py consolidate --registry ... --report ... --output ...
  python research/learning_hub/hub.py verify --registry ... --state ...
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
LEARNING_LAB=HERE.parent/"learning_lab"
sys.path.insert(0,str(LEARNING_LAB))
import verified_python_training_export as exporter  # existing #234 interface

SCHEMA="OMEGA_LEARNING_HUB_STATE_01"
MAX_REGISTRY_BYTES=130_000
MAX_REPORT_BYTES=exporter.MAX_REPORT_BYTES
MAX_SNAPSHOT_BYTES=2_000_000
AUDITED_RUN_ID=45064696523
SOURCE_SHA="436df0d8f542c080cc84443e2971b96fecc41c86"
SOURCE_REPORT_SHA="37871f7dc1a414faf8c4f9784fbb551828a04f0a534cf01c4de5000c27572049"


def require(ok, code):
    if not ok:
        raise ValueError(code)


def digest(data):
    return sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,
                             separators=(",",":")).encode("utf-8")).hexdigest()


def read_json(path,limit):
    path=Path(path)
    require(path.is_file(),"FILE_MISSING")
    require(path.stat().st_size<=limit,"FILE_TOO_LARGE")
    return json.loads(path.read_text(encoding="utf-8"))


def read_source_bytes(path):
    path=Path(path)
    require(path.is_file(),"SOURCE_REPORT_NOT_FOUND")
    require(path.stat().st_size<=MAX_REPORT_BYTES,"SOURCE_REPORT_TOO_LARGE")
    return path.read_bytes()


def validate_registry(registry):
    require(isinstance(registry,dict) and registry.get("schema")=="OMEGA_LEARNING_HUB_01",
            "REGISTRY_SCHEMA_INVALID")
    src=registry.get("source_experiment",{})
    require(src.get("run_id")==AUDITED_RUN_ID,"WRONG_FROZEN_RUN")
    require(src.get("source_commit")==SOURCE_SHA,"WRONG_FROZEN_COMMIT")
    require(src.get("report_sha256")==SOURCE_REPORT_SHA,"WRONG_REPORT_HASH")
    require(src.get("run_url")=="https://github.com/Abrasax63/Omega-pub/actions/runs/"+str(AUDITED_RUN_ID),
            "UNTRUSTED_SOURCE_RUN_URL")
    require(src.get("prior_holdout_consumed") is True,"HOLDOUT_CONSUMPTION_NOT_RECORDED")
    require(registry.get("allow_automatic_model_training") is False,
            "AUTO_TRAINING_NOT_AUTHORIZED")
    require(registry.get("allow_automatic_merge") is False,
            "AUTO_MERGE_NOT_AUTHORIZED")
    require(registry.get("allow_automatic_theorem_certification") is False,
            "AUTO_SCIENCE_PROMOTION_NOT_AUTHORIZED")
    require(registry.get("python_trainer_implemented") is False,
            "TRAINER_IMPLEMENTATION_STATUS_UNKNOWN")
    require(registry.get("external_fresh_holdout_pre_registered") is False,
            "NEW_HOLDOUT_STATUS_UNKNOWN")
    require(registry.get("minimum_distinct_verified_python_families_for_further_training_design")==12,
            "MINIMUM_FAMILY_POLICY_CHANGED")
    require(registry.get("minimum_verified_python_samples_for_further_training_design")==24,
            "MINIMUM_SAMPLE_POLICY_CHANGED")
    components=registry.get("components")
    require(isinstance(components,list) and len(components)>=8,
            "INCOMPLETE_COMPONENT_REGISTRY")
    ids=[r["name"] for r in components if isinstance(r,dict) and "name" in r]
    require(len(ids)==len(components) and len(set(ids))==len(ids),
            "DUPLICATE_OR_INVALID_COMPONENT")
    key={x["name"]:x for x in components}
    require(key.get("lora_trainer",{}).get("accepts_python_repair_samples") is False,
            "MATHEMATICAL_TRAINER_MISREPRESENTED_AS_PYTHON_TRAINER")
    for name in ("python_reconstruction","python_curriculum","python_mastery",
                 "python_verified_export"):
        require(key.get(name,{}).get("available_in_this_branch") is True,
                "REQUIRED_LOCAL_COMPONENT_UNAVAILABLE")
    return registry


def audit_components(registry):
    validate_registry(registry)
    return {
        "runtime_programming_modules_available":4,
        "referenced_external_unmerged_modules":len(registry["components"])-4,
        "training_engine_reuse_status":"REFERENCE_ONLY_DATA_SCHEMA_INCOMPATIBLE",
        "math_science_memory_status":"NOT_MERGED_NOT_SKILL_LEDGER",
        "research_gate_status":"UNMERGED_PROVENANCE_AND_COST_LOGIC_REFERENCE",
        "autonomous_learning_status":"NOT_DEMONSTRATED",
        "consolidation_scope":"PYTHON_VERIFIED_SKILL_CANDIDATES_ONLY",
    }


def chain(events):
    previous="0"*64
    out=[]
    for pos,event in enumerate(events):
        record={"index":pos,"previous_sha256":previous,"event":event["event"],
                "payload":event["payload"]}
        record["sha256"]=digest(record)
        previous=record["sha256"]
        out.append(record)
    return out


def validate_chain(records):
    require(isinstance(records,list) and len(records)==3,"MISSING_LEARNING_EVENTS")
    head="0"*64
    for i,record in enumerate(records):
        require(record["index"]==i and record["previous_sha256"]==head,
                "LEARNING_LEDGER_CHAIN_BROKEN")
        without_digest={k:v for k,v in record.items() if k!="sha256"}
        require(digest(without_digest)==record.get("sha256"),
                "LEARNING_LEDGER_RECORD_TAMPERED")
        head=record["sha256"]
    return head


def gate_admission(candidates,registry):
    require(isinstance(candidates,list),"CANDIDATES_NOT_LIST")
    ids=[x["family_id"] for x in candidates]
    require(len(ids)==len(set(ids)),"DUPLICATE_SKILL_FAMILIES")
    families=len(ids)
    n=len(candidates)
    reasons=[]
    if families < registry["minimum_distinct_verified_python_families_for_further_training_design"]:
        reasons.append("INSUFFICIENT_VERIFIED_SKILL_FAMILIES")
    if n < registry["minimum_verified_python_samples_for_further_training_design"]:
        reasons.append("INSUFFICIENT_VERIFIED_CODE_SAMPLES")
    if not registry["external_fresh_holdout_pre_registered"]:
        reasons.append("NO_INDEPENDENT_FRESH_EVALUATION_COHORT")
    if not registry["python_trainer_implemented"]:
        reasons.append("TRAIN26_MATH_LABEL_CONTRACT_INCOMPATIBLE_WITH_PYTHON")
    if not registry["allow_automatic_model_training"]:
        reasons.append("AUTOMATIC_TRAINING_DISABLED_BY_POLICY")
    # No current plan can authorize training; this is a guarded status.
    return {"status":"TRAINING_NOT_AUTHORIZED",
            "admitted_verified_code_samples":n,
            "distinct_families":families,
            "fail_closed":True,
            "reasons":reasons,
            "recommended_next_action":"GATHER_NEW_VERIFIED_PYTHON_SKILL_FAMILIES",
            "advice_not_execution":True}


def observed_scores(report):
    # Source scores are descriptive; any hidden test was consumed in V3.
    def correct(ep,field):
        value=ep[field]["correct"]
        require(type(value)==int and 0<=value<=40,"BAD_REPORTED_HOLDOUT_SCORE")
        return value
    direct=correct(report["F_direct"],"retained_hidden")
    transfer=correct(report["F_transfer"],"retained_hidden")
    c=correct(report["E_training"],"retained_hidden")
    return {"F_direct_of_40":direct,"F_transfer_of_40":transfer,
            "E_retained_of_40":c,"transfer_delta_out_of_40":transfer-direct,
            "causal_effect_demonstrated":False,
            "weight_update_this_run":False,
            "test_set_available_for_future_blind_eval":False}


def consolidate(report_bytes,registry):
    validate_registry(registry)
    require(len(report_bytes)<=MAX_REPORT_BYTES,"REPORT_BYTES_LIMIT")
    actual=sha256(report_bytes).hexdigest()
    require(actual==registry["source_experiment"]["report_sha256"],
            "V3_SOURCE_REPORT_SHA256_MISMATCH")
    report=json.loads(report_bytes.decode("utf-8"))
    src=registry["source_experiment"]
    result=exporter.export_candidate_dataset(
        report,src["source_commit"],src["run_url"])
    candidates=result["training_candidates"]
    require(len(candidates)==result["manifest"]["admitted_examples"],
            "ADMISSION_COUNT_DISAGREEMENT")
    require(result["manifest"]["weight_training_performed"] is False,
            "ILLEGAL_TRAINING_CLAIM")
    decision=gate_admission(candidates,registry)
    require(decision["status"]=="TRAINING_NOT_AUTHORIZED",
            "UNAUTHORIZED_TRAINING_GATE")
    verify_obs=observed_scores(report)
    entries=[
        {"event":"source_snapshot_inspected",
         "payload":{"run_id":src["run_id"],"git_commit":src["source_commit"],
                    "report_sha256":actual,"prior_holdout_consumed":True}},
        {"event":"programming_skill_candidates_admitted_only_to_quarantine",
         "payload":{"admitted":len(candidates),
                    "distinct_skill_families":decision["distinct_families"],
                    "candidate_hash":digest(candidates),
                    "hidden_oracles_exported":False,
                    "candidate_training_parameters_updated":False}},
        {"event":"training_preparation_gate_evaluated",
         "payload":{"gate_status":decision["status"],"reasons":decision["reasons"],
                    "automatic_training_performed":False}}
    ]
    ledger=chain(entries)
    state={
        "schema":SCHEMA,
        "status":"INTEGRATED_QUARANTINE_ONLY",
        "registry_sha256":digest(registry),
        "provenance":{"source_run":src["run_url"],"source_commit":src["source_commit"],
                      "report_sha256":actual},
        "existing_components":audit_components(registry),
        "previous_experiment_observations":verify_obs,
        "skill_candidates":candidates,
        "candidate_manifest":result["manifest"],
        "training_gate":decision,
        "events":ledger,
        "ledger_head_sha256":ledger[-1]["sha256"],
        "training_started":False,"model_weights_updated":False,
        "main_modified":False,
        "this_is_not_new_learning_evidence":True,
    }
    verify_state(state,registry)
    return state


def verify_state(state,registry):
    validate_registry(registry)
    require(isinstance(state,dict) and state.get("schema")==SCHEMA,
            "HUB_STATE_INVALID")
    require(state.get("registry_sha256")==digest(registry),
            "HUB_REGISTRY_CHANGED")
    require(state.get("training_started") is False and
            state.get("model_weights_updated") is False and
            state.get("main_modified") is False,
            "ILLEGAL_POSTHOC_SUCCESS")
    require(state.get("provenance",{}).get("report_sha256")==SOURCE_REPORT_SHA,
            "UNTRUSTED_SOURCE_REPORT")
    require(state.get("provenance",{}).get("source_commit")==SOURCE_SHA,
            "UNTRUSTED_SOURCE_COMMIT")
    candidates=state.get("skill_candidates")
    require(isinstance(candidates,list) and len(candidates)<=10_000,
            "UNBOUNDED_CANDIDATES")
    for item in candidates:
        require(item.get("record_sha256")==digest(
            {k:v for k,v in item.items() if k!="record_sha256"}),
            "CORRUPT_SKILL_CANDIDATE")
        require(item.get("task")=="PYTHON_REPAIR","NOT_A_VERIFIED_PYTHON_SKILL")
    manifest=state.get("candidate_manifest",{})
    require(manifest.get("records_sha256")==digest(candidates),
            "CANDIDATE_MANIFEST_MISMATCH")
    require(manifest.get("admitted_examples")==len(candidates),
            "MANIFEST_COUNT_MISMATCH")
    expected=gate_admission(candidates,registry)
    require(state.get("training_gate")==expected,
            "TRAINING_GATE_TAMPERED")
    head=validate_chain(state.get("events"))
    require(head==state.get("ledger_head_sha256"),
            "LEDGER_HEAD_MISMATCH")
    ev=state["events"]
    require(ev[0]["payload"]["report_sha256"]==SOURCE_REPORT_SHA,
            "SOURCE_EVENT_REWRITTEN")
    require(ev[1]["payload"]["candidate_hash"]==digest(candidates),
            "SKILL_EVENT_INVALID")
    require(ev[1]["payload"]["admitted"]==len(candidates),
            "SKILL_COUNT_CHANGED")
    require(ev[2]["payload"]["gate_status"]==expected["status"] and
            ev[2]["payload"]["reasons"]==expected["reasons"],
            "GATE_EVENT_CHANGED")
    return True



def verify_persisted_index(index,state,registry):
    """An independently readable durable index of already admitted candidates.

    The index is NOT a new training dataset or a new test. Verify every
    reference and code sample against the full source-derived hub state.
    """
    verify_state(state,registry)
    require(isinstance(index,dict) and
            index.get("schema")=="OMEGA_LEARNING_HUB_PERSISTED_SKILL_INDEX_01",
            "SKILL_INDEX_SCHEMA_INVALID")
    require(index.get("source_v3_commit")==SOURCE_SHA and
            index.get("source_v3_report_sha256")==SOURCE_REPORT_SHA,
            "INDEX_SOURCE_FINGERPRINT_MISMATCH")
    require(index.get("registry_sha256")==state["registry_sha256"],
            "INDEX_REGISTRY_CHANGED")
    require(index.get("candidate_dataset_sha256")==
            state["candidate_manifest"]["records_sha256"],
            "INDEX_DATASET_HASH_MISMATCH")
    require(index.get("ledger_head_sha256")==state["ledger_head_sha256"],
            "INDEX_EVENT_LEDGER_MISMATCH")
    require(index.get("status")=="QUARANTINE_INSUFFICIENT_VERIFIED_DIVERSITY",
            "INDEX_NOT_IN_QUARANTINE")
    require(index.get("training_started") is False and
            index.get("parametric_learning_demonstrated") is False and
            index.get("general_python_competence_certified") is False,
            "INDEX_CLAIMS_UNPROVEN_LEARNING")
    require(index.get("used_hidden_tests_not_available_as_fresh_holdout") is True,
            "INDEX_ATTEMPTS_HOLDOUT_REUSE")
    rows=index.get("verified_candidates")
    require(isinstance(rows,list) and len(rows)==len(state["skill_candidates"]),
            "INDEX_CANDIDATE_COUNT_INVALID")
    by_id={x["family_id"]:x for x in state["skill_candidates"]}
    require(len(by_id)==len(rows),"INDEX_DUPLICATE_SOURCE")
    seen=set()
    for row in rows:
        name=row.get("family_id")
        require(name in by_id and name not in seen,"INDEX_UNKNOWN_OR_DUPLICATE_FAMILY")
        seen.add(name)
        original=by_id[name]
        require(row.get("task")==original["task"]=="PYTHON_REPAIR",
                "INDEX_TASK_NOT_VERIFIED")
        require(row.get("best_code")==original["target"],
                "INDEX_CODE_MISMATCH")
        require(row.get("source_raw_model_sha256")==
                original["admission_evidence"]["model_raw_sha256"],
                "INDEX_MODEL_RAW_HASH_MISMATCH")
        require(row.get("candidate_record_sha256")==original["record_sha256"],
                "INDEX_CANDIDATE_HASH_MISMATCH")
        require(row.get("original_best_attempt")==
                original["original_best_attempt"],"INDEX_ATTEMPT_MISMATCH")
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    inspect=sub.add_parser("inspect")
    inspect.add_argument("--registry",type=Path,default=HERE/"REGISTRY.json")
    consolidate_cmd=sub.add_parser("consolidate")
    consolidate_cmd.add_argument("--registry",type=Path,default=HERE/"REGISTRY.json")
    consolidate_cmd.add_argument("--report",type=Path,required=True)
    consolidate_cmd.add_argument("--output",type=Path,required=True)
    validate=sub.add_parser("verify")
    validate.add_argument("--registry",type=Path,default=HERE/"REGISTRY.json")
    validate.add_argument("--state",type=Path,required=True)
    stable=sub.add_parser("verify-index")
    stable.add_argument("--registry",type=Path,default=HERE/"REGISTRY.json")
    stable.add_argument("--state",type=Path,required=True)
    stable.add_argument("--index",type=Path,default=HERE/"VERIFIED_SKILL_INDEX_2026-11-22.json")
    args=p.parse_args()
    registry=validate_registry(read_json(args.registry,MAX_REGISTRY_BYTES))
    if args.command=="inspect":
        print(json.dumps(audit_components(registry),ensure_ascii=False,indent=2))
    elif args.command=="consolidate":
        state=consolidate(read_source_bytes(args.report),registry)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",
                               encoding="utf-8")
        print(json.dumps({"status":state["status"],
                          "skills":len(state["skill_candidates"]),
                          "gate":state["training_gate"]["status"],
                          "ledger_head":state["ledger_head_sha256"],
                          "train_started":False}))
    elif args.command=="verify":
        state=read_json(args.state,MAX_SNAPSHOT_BYTES)
        verify_state(state,registry)
        print(json.dumps({"integrity":"VERIFIED","status":state["status"],
                          "training_started":False,
                          "candidates":len(state["skill_candidates"])}))
    elif args.command=="verify-index":
        state=read_json(args.state,MAX_SNAPSHOT_BYTES)
        index=read_json(args.index,MAX_SNAPSHOT_BYTES)
        verify_persisted_index(index,state,registry)
        print(json.dumps({"durable_index":"VERIFIED",
                          "entries":len(index["verified_candidates"]),
                          "training_started":False}))


if __name__=="__main__":
    main()
