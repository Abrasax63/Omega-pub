"""Executed by a real, independent GitHub matrix job via subprocess.

Writes a byte-addressed compute receipt, not an independent science proof.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import sys
import types
import uuid


def digest(data):
    return sha256(data).hexdigest()


def write_json(path, data):
    raw=(json.dumps(data,sort_keys=True,indent=2)+"\n").encode()
    path.write_bytes(raw)
    return digest(raw)


def event(phase, **fields):
    print(json.dumps({"phase":phase,**fields},sort_keys=True),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--packet",type=Path,required=True)
    args=parser.parse_args()
    path=args.packet
    input_raw=(path/"inputs.json").read_bytes()
    dep_raw=(path/"dependency.py").read_bytes()
    worker_raw=Path(__file__).read_bytes()
    inputs=json.loads(input_raw)
    if (type(inputs.get("seed")) is not int or
        not isinstance(inputs.get("values"),list) or
        len(inputs["values"])!=4 or
        any(type(x) is not int for x in inputs["values"])):
        raise ValueError("INVALID_COMPUTE_INPUTS")
    module=types.ModuleType("run_dependency")
    exec(compile(dep_raw.decode("utf-8"),str(path/"dependency.py"),"exec"),
         module.__dict__)
    session=uuid.uuid4().hex
    pid=os.getpid()
    run_id=os.environ.get("GITHUB_RUN_ID","LOCAL")
    attempt=os.environ.get("GITHUB_RUN_ATTEMPT","LOCAL")
    source_sha=os.environ.get("GITHUB_SHA","LOCAL")
    python=sys.version
    environment={"python":python,"implementation":platform.python_implementation(),
                 "system":platform.system(),"machine":platform.machine()}
    event("begin",session_uuid=session,pid=pid,github_run_id=run_id,
          github_run_attempt=attempt,source_sha=source_sha)
    noise=[random.Random(inputs["seed"]+n).randrange(1_000_000)
           for n in range(8)]
    result={"algorithm":"finite_sum_with_pseudorandom_checks_v1",
            "total":module.aggregate(inputs["values"]),
            "noise":noise}
    result_hash=write_json(path/"result.json",result)
    receipt={
        "session_uuid":session,"pid":pid,
        "github_run_id":run_id,"github_run_attempt":attempt,
        "source_sha":source_sha,
        "input_sha256":digest(input_raw),
        "dependency_sha256":digest(dep_raw),
        "worker_sha256":digest(worker_raw),
        "result_sha256":result_hash,
        "seed":inputs["seed"],
        "environment":environment,
    }
    receipt_hash=write_json(path/"receipt.json",receipt)
    event("complete",session_uuid=session,pid=pid,github_run_id=run_id,
          github_run_attempt=attempt,source_sha=source_sha,
          result_sha256=result_hash,receipt_sha256=receipt_hash)


if __name__=="__main__":
    main()
