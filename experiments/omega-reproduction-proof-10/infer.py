"""Gold-blind verification of deterministic finite-job replay conditions.

A source file's output hash is not sufficient to certify reproducibility.
The proof requires matching input, seed, worker, loaded dependency, Python
environment and a DISTINCT execution session, plus independent recomputation.
No external scientific independence is certified.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import re

EXPECTED_FILES={"inputs.json","dependency.py","worker_source.py",
                "result.json","receipt.json","stdout.log"}
HEX32=re.compile(r"^[0-9a-f]{32}$")


class BadEvidence(RuntimeError):
    pass


def checksum(data):
    return sha256(data).hexdigest()


def independent_numeric_recompute(payload):
    """Do not import or execute the job's recorded Python dependency."""
    values=payload["values"]
    seed=payload["seed"]
    if (type(seed) is not int or type(values) is not list or len(values)!=4 or
        any(type(item) is not int for item in values)):
        raise BadEvidence("INVALID_COMPUTE_INPUT")
    return {"algorithm":"finite_sum_with_pseudorandom_checks_v1",
            "total":sum(values),
            "noise":[random.Random(seed+index).randrange(1000000)
                     for index in range(8)]}


def inspect(folder):
    names={f.name for f in folder.iterdir()}
    if not EXPECTED_FILES<=names:
        return {"status":"ABSTAIN","reason":"INCOMPLETE_RAW_EVIDENCE"}
    if names!=EXPECTED_FILES:
        raise BadEvidence("UNEXPECTED_RAW_FILES")
    b={name:(folder/name).read_bytes() for name in EXPECTED_FILES}
    try:
        receipt=json.loads(b["receipt.json"])
        config=json.loads(b["inputs.json"])
        output=json.loads(b["result.json"])
        log=[json.loads(line) for line in b["stdout.log"].decode("utf-8").splitlines()]
    except (UnicodeError,ValueError,TypeError) as exc:
        raise BadEvidence("MALFORMED_EVIDENCE") from exc
    if len(log)!=2 or [row.get("phase") for row in log]!=["begin","complete"]:
        raise BadEvidence("MISSING_REAL_LOG_LIFECYCLE")
    for name,fn in (
        ("input_sha256","inputs.json"),
        ("dependency_sha256","dependency.py"),
        ("worker_sha256","worker_source.py"),
        ("result_sha256","result.json"),
    ):
        if receipt.get(name)!=checksum(b[fn]):
            raise BadEvidence("FALSE_RECORDED_HASH_"+name)
    if (receipt.get("seed")!=config.get("seed") or
        output!=independent_numeric_recompute(config)):
        raise BadEvidence("INDEPENDENT_RECALCULATION_FAILED")
    uid=receipt.get("session_uuid")
    if type(uid) is not str or not HEX32.fullmatch(uid):
        raise BadEvidence("INVALID_COMPUTE_SESSION")
    if type(receipt.get("pid")) is not int or receipt["pid"]<=0:
        raise BadEvidence("INVALID_PROCESS_PID")
    for name in ("session_uuid","pid","github_run_id",
                 "github_run_attempt","source_sha"):
        if any(ev.get(name)!=receipt.get(name) for ev in log):
            raise BadEvidence("LOG_RECEIPT_CONFLICT_"+name)
    if (log[1].get("result_sha256")!=receipt["result_sha256"] or
        log[1].get("receipt_sha256")!=checksum(b["receipt.json"])):
        raise BadEvidence("LOG_CONTENT_HASH_CONFLICT")
    environment=receipt.get("environment")
    if (type(environment) is not dict or
        not all(isinstance(environment.get(k),str) and environment[k]
                for k in ("python","implementation","system","machine"))):
        return {"status":"ABSTAIN","reason":"MISSING_PYTHON_ENVIRONMENT"}
    if any(not isinstance(receipt.get(k),str) or not receipt[k] for k in
           ("github_run_id","github_run_attempt","source_sha")):
        return {"status":"ABSTAIN","reason":"INCOMPLETE_GITHUB_RUN_CONTEXT"}
    return {"status":"EVIDENCE_VALIDATED",
            "session_uuid":uid,
            "github_run_id":receipt["github_run_id"],
            "github_run_attempt":receipt["github_run_attempt"],
            "source_sha":receipt["source_sha"],
            "environment":environment,
            "seed":receipt["seed"],
            "input_sha256":receipt["input_sha256"],
            "dependency_sha256":receipt["dependency_sha256"],
            "worker_sha256":receipt["worker_sha256"],
            "result_sha256":receipt["result_sha256"],
            "result_recalculated":True}


def classify(reference,candidate):
    if reference["status"]!="EVIDENCE_VALIDATED" or             candidate["status"]!="EVIDENCE_VALIDATED":
        return "ABSTAIN_MISSING_EVIDENCE"
    if candidate["session_uuid"]==reference["session_uuid"]:
        return "ABSTAIN_NOT_DISTINCT_EXECUTION"
    if (candidate["github_run_id"]!=reference["github_run_id"] or
        candidate["github_run_attempt"]!=reference["github_run_attempt"] or
        candidate["source_sha"]!=reference["source_sha"]):
        return "ABSTAIN_DIFFERENT_RUN_SCOPE"
    # A matching result SHA is never, by itself, a replay proof.
    checks=(
        ("worker_sha256","NOT_SC_REPLAY_WORKER_DRIFT"),
        ("dependency_sha256","NOT_SC_REPLAY_DEPENDENCY_DRIFT"),
        ("input_sha256","NOT_SC_REPLAY_INPUT_DRIFT"),
        ("seed","NOT_SC_REPLAY_SEED_DRIFT"),
        ("environment","NOT_SC_REPLAY_ENVIRONMENT_DRIFT"),
        ("result_sha256","NOT_SC_REPLAY_OUTPUT_MISMATCH"),
    )
    for field,decision in checks:
        if candidate[field]!=reference[field]:
            return decision
    return "SC_REPLAY_CERTIFIED"


def resolve(raw_root):
    inventory=json.loads((raw_root/"inventory.json").read_bytes())
    if inventory.get("schema")!="omega_reproduction_proof_10" or             inventory.get("gold_excluded") is not True:
        raise BadEvidence("INVALID_BLIND_DOSSIER")
    names=inventory.get("packets")
    anchor=inventory.get("anchor_packet")
    if (not isinstance(names,list) or len(names)!=5 or
        len(set(names))!=5 or anchor not in names or
        any(not re.fullmatch(r"packet-[0-9]{3}",name) for name in names)):
        raise BadEvidence("UNTRUSTWORTHY_PACKET_INVENTORY")
    if {x.name for x in (raw_root/"packets").iterdir()}!=set(names):
        raise BadEvidence("UNEXPECTED_PACKET_DIRECTORY")
    observations={}
    for name in names:
        folder=raw_root/"packets"/name
        if not folder.is_dir():
            raise BadEvidence("MISSING_PACKET")
        observations[name]=inspect(folder)
    ref=observations[anchor]
    results=[]
    for name in sorted(names):
        evidence=observations[name]
        label=("REFERENCE" if name==anchor and
               ref["status"]=="EVIDENCE_VALIDATED" else
               classify(ref,evidence))
        results.append({"packet":name,"decision":label,
                        "evidence_status":evidence["status"],
                        "reason":evidence.get("reason"),
                        "session_uuid":evidence.get("session_uuid"),
                        "result_sha256":evidence.get("result_sha256"),
                        "input_sha256":evidence.get("input_sha256"),
                        "dependency_sha256":evidence.get("dependency_sha256"),
                        "seed":evidence.get("seed"),
                        "result_recalculated":evidence.get("result_recalculated",False)})
    successes=sum(x["decision"]=="SC_REPLAY_CERTIFIED" for x in results)
    return {
        "experiment":"OMEGA-REPRODUCTION-PROOF-10",
        "status":"TECHNICAL_REPLAY_CLASSES_ASSIGNED",
        "anchor_packet":anchor,
        "raw_packets":len(results),
        "replayed_same_conditions":successes,
        "classified_controls":sum(x["decision"].startswith("NOT_SC_REPLAY_")
                                  for x in results),
        "abstentions":sum(x["decision"].startswith("ABSTAIN") for x in results),
        "scientific_independence":"INDETERMINATE",
        "independent_scientific_replication_certified":False,
        "limit":"same workflow, separate GitHub jobs, shared code and infrastructure",
        "gold_supplied_to_engine":False,
        "results":results,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    doc=resolve(args.raw_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(doc,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(payload)
    print(json.dumps({"status":doc["status"],
                      "replay_count":doc["replayed_same_conditions"],
                      "non_replay_controls":doc["classified_controls"],
                      "abstentions":doc["abstentions"],
                      "scientific_independence":doc["scientific_independence"],
                      "predictions_sha256":checksum(payload)},sort_keys=True))


if __name__=="__main__":
    main()
