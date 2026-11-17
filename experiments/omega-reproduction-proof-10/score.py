"""Independent gold-scoped scorer for genuine five-job computational replay.

Does not import infer.py or trust its classifications. Checks actual bytes,
log/receipt bindings, independently recomputed output, and predeclared
negative controls. Does NOT certify independent external scientific review.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random


class ScoreFailure(AssertionError):
    pass


def enforce(condition,message):
    if not condition:
        raise ScoreFailure(message)


def checksum(raw):
    return sha256(raw).hexdigest()


def audit(raw_dir,predictions,gold):
    enforce(gold.get("schema")=="omega_reproduction_proof_10_gold",
            "INVALID_GOLD_SCHEMA")
    enforce(gold.get("expected_jobs")==5, "NOT_FIVE_JOBS")
    enforce(gold.get("scientific_independence")=="INDETERMINATE",
            "INVALID_GOLD_SCIENTIFIC_SCOPE")
    expected=gold.get("expected_by_packet")
    roles=gold.get("role_by_packet")
    enforce(isinstance(expected,dict) and len(expected)==5 and
            isinstance(roles,dict) and len(roles)==5,"INCOMPLETE_GOLD")
    enforce(set(roles.values())==set("ABCDE"),"INVALID_GOLD_VARIANTS")
    enforce(predictions.get("scientific_independence")=="INDETERMINATE" and
            predictions.get("independent_scientific_replication_certified") is False and
            predictions.get("gold_supplied_to_engine") is False,
            "ILLICIT_INDEPENDENCE_CERTIFICATION")
    enforce(predictions.get("anchor_packet")==gold["reference_packet"],
            "CHANGED_REFERENCE_PACKET")
    results=predictions.get("results")
    enforce(isinstance(results,list) and len(results)==5,"WRONG_PACKET_COUNT")
    classified={}
    records={}
    sessions=set()
    for r in results:
        packet=r.get("packet")
        enforce(packet in expected and packet not in classified,
                "UNEXPECTED_OR_DUPLICATE_PACKET")
        classified[packet]=r
        folder=raw_dir/"packets"/packet
        enforce(folder.is_dir(),"MISSING_RAW_PACKET")
        file_set={"inputs.json","dependency.py","worker_source.py",
                  "result.json","receipt.json","stdout.log"}
        enforce({x.name for x in folder.iterdir()}==file_set,"MISSING_RAW_BYTES")
        raws={key:(folder/key).read_bytes() for key in file_set}
        try:
            receipt=json.loads(raws["receipt.json"])
            inputs=json.loads(raws["inputs.json"])
            output=json.loads(raws["result.json"])
            lines=[json.loads(s) for s in raws["stdout.log"].decode().splitlines()]
        except (UnicodeError,TypeError,ValueError) as exc:
            raise ScoreFailure("BAD_BINARY_OR_JSON_EVIDENCE") from exc
        enforce(len(lines)==2 and lines[0].get("phase")=="begin" and
                lines[1].get("phase")=="complete","INCOMPLETE_TRACE")
        for field,filename in (
            ("input_sha256","inputs.json"),("dependency_sha256","dependency.py"),
            ("worker_sha256","worker_source.py"),("result_sha256","result.json")):
            enforce(receipt[field]==checksum(raws[filename]),"BAD_SOURCE_SHA_"+field)
        enforce(inputs["seed"]==receipt["seed"],"SEED_RECEIPT_CONFLICT")
        enforce(output=={
            "algorithm":"finite_sum_with_pseudorandom_checks_v1",
            "total":sum(inputs["values"]),
            "noise":[random.Random(inputs["seed"]+idx).randrange(1000000)
                     for idx in range(8)]},"BAD_INDEPENDENT_RECOMPUTE")
        enforce(receipt["session_uuid"] not in sessions, "DUPLICATE_SESSION_UUID")
        sessions.add(receipt["session_uuid"])
        for field in ("session_uuid","pid","github_run_id",
                      "github_run_attempt","source_sha"):
            enforce(lines[0].get(field)==receipt[field] and
                    lines[1].get(field)==receipt[field],
                    "RAW_TRACE_SOURCE_MISMATCH")
        enforce(lines[1]["result_sha256"]==receipt["result_sha256"] and
                lines[1]["receipt_sha256"]==checksum(raws["receipt.json"]),
                "RAW_TRACE_PAYLOAD_SHA_CONFLICT")
        enforce(receipt["github_run_id"]==gold["source_run_id"] and
                receipt["github_run_attempt"]==gold["source_attempt"] and
                receipt["source_sha"]==gold["source_sha"],
                "GITHUB_WORKFLOW_SCOPE_MISMATCH")
        enforce(isinstance(receipt["environment"].get("python"),str),
                "NO_PYTHON_ENVIRONMENT")
        enforce(r.get("decision")==expected[packet],"WRONG_REPLAY_DECISION")
        enforce(r.get("session_uuid")==receipt["session_uuid"] and
                r.get("result_sha256")==receipt["result_sha256"] and
                r.get("input_sha256")==receipt["input_sha256"] and
                r.get("dependency_sha256")==receipt["dependency_sha256"] and
                r.get("seed")==receipt["seed"] and
                r.get("result_recalculated") is True,
                "PREDICTION_CONTRADICTS_RAW_BYTES")
        records[roles[packet]]={"packet":packet,"receipt":receipt,
                                "input":inputs,"result":output}
    enforce(len(classified)==5 and len(sessions)==5,"MISSING_JOBS_OR_PACKETS")
    a=records["A"]["receipt"]
    b=records["B"]["receipt"]
    c=records["C"]["receipt"]
    d=records["D"]["receipt"]
    e=records["E"]["receipt"]
    keys=("input_sha256","dependency_sha256","worker_sha256","seed",
          "result_sha256","environment")
    enforce(all(a[k]==b[k] for k in keys),"REPLAY_POSITIVE_NOT_IDENTICAL")
    enforce(a["session_uuid"]!=b["session_uuid"],
            "POSITIVES_SHARE_EXECUTION_SESSION")
    enforce(all(a[k]==c[k] for k in ("dependency_sha256","worker_sha256",
                                     "seed","result_sha256")) and
            a["input_sha256"]!=c["input_sha256"],
            "INPUT_COLLISION_CONTROL_BROKEN")
    enforce(all(a[k]==d[k] for k in ("input_sha256","worker_sha256",
                                     "seed","result_sha256")) and
            a["dependency_sha256"]!=d["dependency_sha256"],
            "ACTUAL_DEPENDENCY_DRIFT_CONTROL_BROKEN")
    # inputs.json also contains the seed, hence its SHA MUST change with
    # the seed even when the mathematical values stay identical.
    enforce(records["A"]["input"]["values"]==records["E"]["input"]["values"] and
            all(a[k]==e[k] for k in ("dependency_sha256","worker_sha256")) and
            a["input_sha256"]!=e["input_sha256"] and
            a["seed"]!=e["seed"] and a["result_sha256"]!=e["result_sha256"],
            "SEED_DRIFT_CONTROL_BROKEN")
    enforce(sum(r["decision"]=="SC_REPLAY_CERTIFIED" for r in results)==1,
            "WRONG_POSITIVE_CERTIFICATE_COUNT")
    enforce(sum(r["decision"].startswith("NOT_SC_REPLAY_")
                for r in results)==3,"WRONG_NEGATIVE_CONTROL_COUNT")
    enforce(sum(r["decision"]=="REFERENCE" for r in results)==1,
            "WRONG_REFERENCE_COUNT")
    enforce(predictions.get("replayed_same_conditions")==1 and
            predictions.get("classified_controls")==3 and
            predictions.get("abstentions")==0,
            "INCORRECT_REPORTED_COUNTS")
    return {
        "status":"SC_REPLAY_PIPELINE_VERIFIED",
        "run_scope":"five GitHub matrix jobs in one workflow run",
        "source_run_id":gold["source_run_id"],
        "raw_execution_packets":5,
        "distinct_session_uuids":5,
        "strict_replay_certificates":1,
        "correct_negative_controls":3,
        "same_output_different_inputs_detected":1,
        "same_output_different_actual_python_dependency_detected":1,
        "different_seed_detected":1,
        "wrong_replay_certificates":0,
        "gold_excluded_from_inference":True,
        "scientific_independence":"INDETERMINATE",
        "independent_scientific_replications_proven":0,
        "limitations":"Controlled finite example; same GitHub workflow/infrastructure; not independent research replication",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-dir",type=Path,required=True)
    ap.add_argument("--predictions",type=Path,required=True)
    ap.add_argument("--gold",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=audit(args.raw_dir,json.loads(args.predictions.read_bytes()),
                 json.loads(args.gold.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({**result,"score_sha256":checksum(raw)},sort_keys=True))


if __name__=="__main__":
    main()
