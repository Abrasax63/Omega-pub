"""Admission gate: V3 model-generated Python corrections -> quarantined SFT candidates.

Deliberately NOT a trainer. It links the established Omega Python mastery
experiment to TRAIN25/26-style frozen corpus practices, without importing
their mathematical training labels or exposing any holdout program answers.

The model-generated target is admitted only if it was selected by the frozen
original V3 evaluator, correctly parsed from the model's RAW output, Python
safe, correct on all public examples and previously evaluated mastery probes.
Mastery inputs are used as a *consumed validation set*; they are never
included in the candidate's train prompt, exported labels or future holdout.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import prog_reconstruction_pilot as v1
import python_mastery_v3 as v3

SCHEMA="OMEGA_PY_SKILL_ADMISSION_V1"
MIN_INDEPENDENT_FAMILIES=12
MAX_REPORT_BYTES=4_000_000
SHA_PATTERN=re.compile(r"^[a-f0-9]{40}$")
RUN_PATTERN=re.compile(r"^https://github\.com/Abrasax63/Omega-pub/actions/runs/[0-9]+$")
FROZEN_PROTOCOL=v3.PROTOCOL


def stable_sha(obj):
    return sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,
                             separators=(",",":")).encode()).hexdigest()


def require(test,message):
    if not test:
        raise ValueError(message)


def check_source(report,run_url,sha):
    require(isinstance(report,dict),"REPORT_NOT_OBJECT")
    require(report.get("protocol")==FROZEN_PROTOCOL,"WRONG_PROTOCOL")
    require(report.get("status")=="COMPLETED_NO_CAUSAL_LEARNING_CLAIM",
            "INCOMPLETE_EXPERIMENT")
    require(report.get("mastery_gate_passed") is True,"MASTERY_GATE_NOT_PASS")
    require(report.get("model_weights_updated") is False,"UNKNOWN_WEIGHT_UPDATES")
    require(report.get("finetune_performed") is False,"UNKNOWN_FINETUNING")
    require(report.get("main_modified") is False,"UNEXPECTED_MAIN_MODIFICATION")
    require(bool(SHA_PATTERN.fullmatch(sha)),"UNPINNED_SOURCE_SHA")
    require(bool(RUN_PATTERN.fullmatch(run_url)),"UNVERIFIED_RUN_LOCATION_FORMAT")
    require(isinstance(report.get("syntax_practice"),list),"MISSING_PRACTICE_ROWS")
    return True


def candidate_from_practice(row,exercise,run_url,sha):
    require(row.get("exercise")==exercise["id"],"PRACTICE_NAME_MISMATCH")
    attempts=row.get("attempts")
    require(isinstance(attempts,list) and len(attempts)==2,"INVALID_ATTEMPT_COUNT")
    for att in attempts:
        require(isinstance(att,dict) and isinstance(att.get("raw"),str),
                "RAW_ATTEMPT_MISSING")
        got=v1.parse_code(att["raw"])
        require(got==att.get("code"),"MODEL_CODE_RAW_DISAGREEMENT")
    expected_idx,chosen=v3.choose_best(attempts)
    require(row.get("retained_best_index")==expected_idx,"BEST_INDEX_TAMPERED")
    # Admission relies on the *original* V3 run's recorded decision, never
    # relabels failures after later changes to the evaluator's allowlist.
    if not (row.get("mastery_pass") is True and
            row.get("best_python_valid") is True and
            row.get("public_best")==row.get("public_n")==len(exercise["visible"]) and
            row.get("mastery_correct")==row.get("mastery_n")==len(exercise["mastery"])):
        return None
    code=chosen["code"]
    require(isinstance(code,str),"NO_ORIGINAL_BEST_CODE")
    require(chosen.get("diagnostic",{}).get("stage")=="valid",
            "ORIGINAL_BEST_CODE_NOT_VALID")
    # Re-execution is an integrity check on consumed development and
    # mastery inputs, not an independent scientific experiment.
    for inputs in (exercise["visible"],exercise["mastery"]):
        outputs=v1.execute_student(code,inputs)
        expected=[exercise["oracle"](s) for s in inputs]
        require(all(p.get("value")==x for p,x in zip(outputs,expected)),
                "CODE_NO_LONGER_REPRODUCES_RECORDED_EXAMPLES")
    exposed=[{"input":s,"output":exercise["oracle"](s)}
             for s in exercise["visible"]]
    # The course prompt includes ONLY already public training demonstrations.
    prompt=("TASK=PYTHON_REPAIR\n"
            "Behavior: "+exercise["goal"]+"\n"
            "Original broken source:\n"+exercise["broken"]+
            "\nVisible examples:\n"+json.dumps(exposed,ensure_ascii=False)+
            "\nReturn a complete Python def transform(s) as source, "
            "without imports or external side effects.")
    fields={"family_id":"py-syntax-"+exercise["id"],
            "task":"PYTHON_REPAIR",
            "prompt":prompt,"target":code,
            "source_run_url":run_url,"source_commit":sha,
            "original_best_attempt":expected_idx,
            "admission_evidence":{
                "model_raw_sha256":sha256(chosen["raw"].encode()).hexdigest(),
                "public_examples_verified":len(exercise["visible"]),
                "consumed_mastery_examples_verified":len(exercise["mastery"]),
                "source_original_mastery_pass":True,
                "independent_new_holdout":False,
                "code_compilable_and_policy_valid":True,
            }}
    fields["record_sha256"]=stable_sha(fields)
    return fields


def export_candidate_dataset(report,source_commit,source_run):
    check_source(report,source_run,source_commit)
    spec={x["id"]:x for x in v3.PRACTICE}
    entries=[]
    seen=set()
    for row in report["syntax_practice"]:
        require(isinstance(row,dict),"PRACTICE_ROW_INVALID")
        name=row.get("exercise")
        require(name in spec and name not in seen,"DUPLICATE_OR_UNKNOWN_PRACTICE")
        seen.add(name)
        candidate=candidate_from_practice(row,spec[name],source_run,source_commit)
        if candidate:
            entries.append(candidate)
    require(seen==set(spec),"INCOMPLETE_WORKSHOP_SET")
    families={x["family_id"] for x in entries}
    eligible=len(families)>=MIN_INDEPENDENT_FAMILIES
    # Crucially the old E/F program scores are *never* inspected, copied,
    # or encoded in prompt and target. The old mastery cases are consumed
    # for admission and must NEVER become a new blinded evaluation.
    manifest={
        "schema":SCHEMA,
        "source_protocol":FROZEN_PROTOCOL,
        "source_run_url":source_run,
        "source_commit":source_commit,
        "admitted_examples":len(entries),
        "independent_families":len(families),
        "minimum_independent_families":MIN_INDEPENDENT_FAMILIES,
        "status":"READY_FOR_SEPARATE_PRE_REGISTERED_TRAINING" if eligible
                 else "QUARANTINE_INSUFFICIENT_VERIFIED_DIVERSITY",
        "weight_training_performed":False,
        "automatic_promotion_to_main":False,
        "source_report_original_holdout_reused_as_train":False,
        "new_independent_holdout_verified":False,
        "consumed_groups_do_not_reuse_as_future_holdout":
            ["OMEGA-PY-MASTERY-03:course:"+x["id"] for x in v3.PRACTICE]+
            ["OMEGA-PY-MASTERY-03:E","OMEGA-PY-MASTERY-03:F"],
        "compatible_with_train26_labels":False,
        "requires_new_training_contract":True,
        "training_data_are_model_proposals_verified_by_bounded_tests":True,
        "notes":"Static admission/packaging only. TRAIN26 expects mathematical EXPR labels. "
                "Never silently feed these Python code samples into its existing trainer.",
    }
    manifest["records_sha256"]=stable_sha(entries)
    return {"manifest":manifest,"training_candidates":entries}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--source-run",required=True)
    p.add_argument("--source-commit",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    require(args.report.is_file(),"REPORT_MISSING")
    require(args.report.stat().st_size<=MAX_REPORT_BYTES,"REPORT_TOO_LARGE")
    source=json.loads(args.report.read_text(encoding="utf-8"))
    obj=export_candidate_dataset(source,args.source_commit,args.source_run)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({"status":obj["manifest"]["status"],
                      "accepted":obj["manifest"]["admitted_examples"],
                      "training_started":False,
                      "source_sha256":sha256(args.report.read_bytes()).hexdigest(),
                      "candidate_digest":obj["manifest"]["records_sha256"]}))


if __name__=="__main__":
    main()
