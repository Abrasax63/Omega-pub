"""Actual child-process computation for the raw provenance laboratory."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import sys
import time

def digest(raw):
    return sha256(raw).hexdigest()

def write_json(path, obj):
    raw=(json.dumps(obj,sort_keys=True,indent=2)+"\n").encode()
    path.write_bytes(raw)
    return digest(raw)

def emit(phase, **fields):
    print(json.dumps(dict(phase=phase,**fields),sort_keys=True),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--execution-id",required=True)
    args=parser.parse_args()
    inputs_raw=args.input.read_bytes()
    payload=json.loads(inputs_raw)
    seed=payload["seed"]
    if type(seed) is not int:
        raise ValueError("INVALID_SEED")
    pid=os.getpid()
    rid=os.environ.get("GITHUB_RUN_ID","LOCAL_ONLY")
    attempt=os.environ.get("GITHUB_RUN_ATTEMPT","LOCAL_ONLY")
    sha=os.environ.get("GITHUB_SHA","LOCAL_ONLY")
    job=os.environ.get("GITHUB_JOB","LOCAL_ONLY")
    emit("begin",execution_id=args.execution_id,pid=pid,run_id=rid,
         run_attempt=attempt,commit_sha=sha,job=job)
    rng=random.Random(seed)
    # Same input and seed always produce byte-identical data across real processes.
    result={"method":"finite_deterministic_sum","input_payload":payload["values"],
            "seed":seed,"noise":[rng.randrange(1000000) for _ in range(5)],
            "sum":sum(payload["values"])}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result_sha=write_json(args.output_dir/"result.json",result)
    receipt={
        "execution_id":args.execution_id,"pid":pid,"run_id":rid,
        "run_attempt":attempt,"commit_sha":sha,"job":job,
        "program_sha256":digest(Path(__file__).read_bytes()),
        "input_sha256":digest(inputs_raw),"result_sha256":result_sha,
        "seed":seed,
    }
    (args.output_dir/"input.json").write_bytes(inputs_raw)
    write_json(args.output_dir/"receipt.json",receipt)
    time.sleep(0.15)  # ensure subprocess lifetimes overlap in the actual runner
    emit("complete",execution_id=args.execution_id,pid=pid,
         run_id=rid,result_sha256=result_sha,receipt_sha256=digest(
             (args.output_dir/"receipt.json").read_bytes()))
    return 0

if __name__=="__main__":
    sys.exit(main())
