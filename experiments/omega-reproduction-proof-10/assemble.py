"""Package five separate job artifacts under opaque names and isolate the gold."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import shutil

from produce import EXPECTED_FILES

LABELS={
    "A":"REFERENCE",
    "B":"SC_REPLAY_CERTIFIED",
    "C":"NOT_SC_REPLAY_INPUT_DRIFT",
    "D":"NOT_SC_REPLAY_DEPENDENCY_DRIFT",
    "E":"NOT_SC_REPLAY_SEED_DRIFT",
}
PACK_SEED=60217


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def stage(stage_dir,raw_dir,gold_file):
    if gold_file.resolve() in raw_dir.resolve().parents or (
            raw_dir.resolve() in gold_file.resolve().parents):
        raise ValueError("GOLD_NOT_SEPARATED")
    if raw_dir.exists() and any(raw_dir.iterdir()):
        raise ValueError("RAW_NOT_EMPTY")
    if gold_file.exists():
        raise ValueError("GOLD_ALREADY_EXISTS")
    source={}
    for case in LABELS:
        folder=stage_dir/f"omega-repro-10-compute-{case}"
        if not folder.is_dir():
            raise ValueError("MISSING_SEPARATE_COMPUTE_JOB_"+case)
        if {x.name for x in folder.iterdir()}!=EXPECTED_FILES:
            raise ValueError("INCOMPLETE_COMPUTE_EVIDENCE_"+case)
        source[case]=folder
    cases=list(LABELS)
    random.Random(PACK_SEED).shuffle(cases)
    packet_names={}
    distinct_sessions=set()
    runs=set()
    shas=set()
    attempts=set()
    for idx,case in enumerate(cases):
        packet=f"packet-{idx:03d}"
        target=raw_dir/"packets"/packet
        target.mkdir(parents=True)
        for name in EXPECTED_FILES:
            shutil.copyfile(source[case]/name,target/name)
        record=json.loads((target/"receipt.json").read_bytes())
        session=record.get("session_uuid")
        if not isinstance(session,str) or session in distinct_sessions:
            raise ValueError("NOT_FIVE_DISTINCT_SESSIONS")
        distinct_sessions.add(session)
        runs.add(record["github_run_id"])
        attempts.add(record["github_run_attempt"])
        shas.add(record["source_sha"])
        packet_names[case]=packet
    if len(distinct_sessions)!=5 or len(runs)!=1 or len(attempts)!=1 or len(shas)!=1:
        raise ValueError("RUN_SCOPE_OR_JOB_SESSIONS_INCONSISTENT")
    dump(raw_dir/"inventory.json",{
        "schema":"omega_reproduction_proof_10",
        "anchor_packet":packet_names["A"],
        "packets":sorted(packet_names.values()),
        "gold_excluded":True,
        "source_type":"five_GitHub_Actions_matrix_job_executions",
    })
    dump(gold_file,{
        "schema":"omega_reproduction_proof_10_gold",
        "expected_by_packet":{packet_names[k]:v for k,v in LABELS.items()},
        "role_by_packet":{packet_names[k]:k for k in LABELS},
        "reference_packet":packet_names["A"],
        "expected_jobs":5,
        "scientific_independence":"INDETERMINATE",
        "run_scope":"single_workflow_five_independent_runner_jobs",
        "source_run_id":next(iter(runs)),
        "source_attempt":next(iter(attempts)),
        "source_sha":next(iter(shas)),
        "job_session_ids":sorted(distinct_sessions),
        "pack_seed":PACK_SEED,
    })
    print(json.dumps({"compute_jobs_observed":5,"packets":5,
                      "reference_alias":packet_names["A"],
                      "distinct_sessions":5,
                      "gold_is_separate":True},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage-dir",type=Path,required=True)
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--gold-file",type=Path,required=True)
    args=p.parse_args()
    stage(args.stage_dir,args.raw_dir,args.gold_file)


if __name__=="__main__":
    main()
