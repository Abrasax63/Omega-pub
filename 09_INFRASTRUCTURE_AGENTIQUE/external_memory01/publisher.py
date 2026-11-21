#!/usr/bin/env python3
"""Independent, append-only scientific memory ledger from executed run artifacts.

No automatic scientific certification. Accepts ONLY source-integrity results,
bounded exact arithmetic checks, and benchmark measurements. The model's raw
predictions are retained separately in quarantine, never promoted.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

PREV_ZERO="0"*64
ALLOWED={
    ("EXTERNAL_SOURCE_PAIR_PROVENANCE","SOURCE_BYTES_AND_PAIRING_VERIFIED"),
    ("MODEL_BENCHMARK_MEASUREMENT","EMPIRICAL_PAIRED_SOURCE_BENCHMARK"),
    ("EXT01-ARITH-N99","FINITE_ENUMERATION_VERIFIED"),
    ("EXT01-EISENSTEIN-N11","EISENSTEIN_PREMISES_ARITHMETICALLY_VERIFIED"),
}
FORBIDDEN_TRUE=("lean_proof_compiled_locally","semantic_equivalence_certified",
                "universal_theorem_certified","universal_irreducibility_formal_proof_executed",
                "semantic_understanding_certified")


def canonical(data):
    return json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf8")


def digest(data):
    return sha256(canonical(data)).hexdigest()


def load_jsonl(path):
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf8").splitlines(),start=1):
        if not line.strip():
            raise ValueError(f"EMPTY_JSONL_LINE_{n}")
        parsed=json.loads(line)
        if not isinstance(parsed,dict):
            raise ValueError(f"NON_OBJECT_JSONL_LINE_{n}")
        rows.append(parsed)
    return rows


def validate_candidate(row):
    kind=row.get("record_type",row.get("id"))
    status=row.get("status")
    if (kind,status) not in ALLOWED:
        raise ValueError("UNSUPPORTED_CLAIM_OR_SCIENTIFIC_CERTIFICATION")
    if any(row.get(k) is True for k in FORBIDDEN_TRUE):
        raise ValueError("UNVERIFIED_MATH_PROMOTION")
    if kind=="EXTERNAL_SOURCE_PAIR_PROVENANCE":
        if not isinstance(row.get("source_blob"),str) or len(row["source_blob"])!=40:
            raise ValueError("SOURCE_PROVENANCE_MISSING")
        if not row.get("lean_contains_sorry") or row.get("lean_proof_compiled_locally") is not False:
            raise ValueError("FORMAL_PROOF_EXECUTION_IMPLIED")
    elif kind=="EXT01-ARITH-N99":
        if not isinstance(row.get("checked_cases"),int) or row["checked_cases"]<=0 or row.get("universal_theorem_certified") is not False:
            raise ValueError("BOUNDED_CHECK_NOT_EXPLICIT")
    elif kind=="EXT01-EISENSTEIN-N11":
        if row.get("universal_irreducibility_formal_proof_executed") is not False:
            raise ValueError("EISENSTEIN_NOT_SCOPED")
    elif kind=="MODEL_BENCHMARK_MEASUREMENT":
        if row.get("semantic_understanding_certified") is not False:
            raise ValueError("UNSUPPORTED_SEMANTIC_CLAIM")
    return kind


def verify_ledger(records):
    prev=PREV_ZERO
    seen=set()
    for i,row in enumerate(records):
        if row.get("sequence")!=i+1 or row.get("previous_record_sha256")!=prev:
            raise ValueError("LEDGER_CHAIN_OR_SEQUENCE_BROKEN")
        candidate=row.get("observation")
        if not isinstance(candidate,dict):
            raise ValueError("MISSING_OBSERVATION")
        validate_candidate(candidate)
        key=digest(candidate)
        if key in seen:
            raise ValueError("DUPLICATE_VERIFIED_RECORD")
        seen.add(key)
        if row.get("observation_sha256")!=key:
            raise ValueError("OBSERVATION_HASH_MISMATCH")
        envelope={k:row[k] for k in (
            "sequence","previous_record_sha256","observation_sha256","observation","source_run_id")}
        expected=digest(envelope)
        if row.get("record_sha256")!=expected:
            raise ValueError("LEDGER_CONTENT_CHANGED")
        prev=expected
    return {"validated_count":len(records),"head_sha256":prev,
            "chain_verified":True,"unique_hashes_verified":len(seen)}


def append_verified(existing,candidates,run_id):
    if type(run_id) is not int or run_id<=0:
        raise ValueError("SOURCE_RUN_ID_REQUIRED")
    state=verify_ledger(existing)
    seen={x["observation_sha256"] for x in existing}
    chain=list(existing)
    for candidate in candidates:
        validate_candidate(candidate)
        key=digest(candidate)
        if key in seen:
            continue
        seen.add(key)
        envelope={
            "sequence":len(chain)+1,
            "previous_record_sha256":state["head_sha256"],
            "observation_sha256":key,
            "observation":candidate,
            "source_run_id":run_id,
        }
        row={**envelope,"record_sha256":digest(envelope)}
        chain.append(row)
        state["head_sha256"]=row["record_sha256"]
    verify_ledger(chain)
    return chain


def publication_plan(artifact_folder,existing_path,run_id):
    report=json.loads((artifact_folder/"report.json").read_text(encoding="utf8"))
    candidates=load_jsonl(artifact_folder/"verified_candidates.jsonl")
    quarantine=load_jsonl(artifact_folder/"model_quarantine.jsonl")
    if report.get("status")!="FINISHED_WITH_LLM_RESULTS_QUARANTINED":
        raise ValueError("NO_COMPLETED_EXPERIMENT_TO_PUBLISH")
    if report.get("sources",{}).get("count")!=8:
        raise ValueError("EXTERNAL_SOURCE_SET_NOT_COMPLETE")
    if len(report.get("model_evaluation",[]))!=2:
        raise ValueError("OFF_ON_PAIRED_MODEL_RUNS_REQUIRED")
    if len(quarantine)!=24 or len(candidates)!=11:
        raise ValueError("MISSING_OR_EXTRA_PUBLISHABLE_RECORDS")
    if report.get("validated_candidates_count")!=len(candidates) or report.get("quarantine_rows_count")!=len(quarantine):
        raise ValueError("REPORT_AND_RECORD_COUNT_DISAGREE")
    source_ids={r.get("source_id") for r in candidates if r.get("record_type")=="EXTERNAL_SOURCE_PAIR_PROVENANCE"}
    if len(source_ids)!=8:
        raise ValueError("MISSING_EXTERNAL_SOURCE_PROVENANCE")
    for entry in quarantine:
        if entry.get("cache_mode") not in ("off","on") or entry.get("classification_not_a_proof") is not True:
            raise ValueError("UNQUARANTINED_LLM_RESULT")
    recorded_runs={x.get("cache_mode") for x in quarantine}
    if recorded_runs!={"off","on"}:
        raise ValueError("NO_PAIRED_LLM_CONDITIONS")
    if report["comparison"]["compared"]!=12:
        raise ValueError("INVALID_LLM_COMPARISON_COUNT")
    old=load_jsonl(existing_path) if existing_path and existing_path.exists() else []
    merged=append_verified(old,candidates,run_id)
    return {
        "validated_ledger":merged,"quarantine":quarantine,
        "publication_index":{
            **verify_ledger(merged),
            "status":"SOURCE_AND_BOUNDED_MATH_EVIDENCE_ONLY",
            "source_run_id":run_id,
            "n_new_observations":len(merged)-len(old),
            "n_pinned_new_external_documents":8,
            "n_unverified_llm_predictions":len(quarantine),
            "llm_predictions_in_verified_memory":0,
            "lean_proofs_locally_compiled":0,
            "source_report_sha256":sha256((artifact_folder/"report.json").read_bytes()).hexdigest(),
            "scientific_semantic_fidelity":"NOT_VERIFIED",
            "production_main_changed":False,
        }
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-dir",required=True,type=Path)
    ap.add_argument("--existing",type=Path)
    ap.add_argument("--run-id",required=True,type=int)
    ap.add_argument("--output-dir",required=True,type=Path)
    a=ap.parse_args()
    plan=publication_plan(a.artifact_dir,a.existing,a.run_id)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for name,rows in (("verified_ledger.jsonl",plan["validated_ledger"]),
                      ("model_quarantine.jsonl",plan["quarantine"])):
        (a.output_dir/name).write_text(
            "".join(canonical(row).decode("utf8")+"\n" for row in rows),encoding="utf8")
    (a.output_dir/"index.json").write_text(
        json.dumps(plan["publication_index"],ensure_ascii=False,indent=2)+"\n",
        encoding="utf8")
    print("PUBLICATION_CANDIDATES",json.dumps(plan["publication_index"]),flush=True)


if __name__=="__main__":
    main()
