"""Real compute process used by both GitHub workflow A and workflow B."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
import types
import uuid


def digest(data):
    return sha256(data).hexdigest()


def dump(path,obj):
    raw=(json.dumps(obj,sort_keys=True,indent=2)+"\n").encode("utf-8")
    path.write_bytes(raw)
    return digest(raw)


def noise(seed):
    # Fully specified SHA256 protocol, independent of Python's random module.
    return [int(digest(f"{seed}:{i}".encode())[:12],16) for i in range(8)]


def emit(phase,**fields):
    print(json.dumps({"phase":phase,**fields},sort_keys=True),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--packet",type=Path,required=True)
    args=parser.parse_args()
    packet=args.packet
    input_raw=(packet/"inputs.json").read_bytes()
    dep_raw=(packet/"dependency.py").read_bytes()
    worker_raw=Path(__file__).read_bytes()
    inputs=json.loads(input_raw)
    if (type(inputs.get("seed")) is not int or
        type(inputs.get("values")) is not list or
        len(inputs["values"])!=4 or
        any(type(v) is not int for v in inputs["values"])):
        raise ValueError("INVALID_NUMERIC_INPUT")
    mod=types.ModuleType("loaded_dependency")
    exec(compile(dep_raw.decode("utf-8"),str(packet/"dependency.py"),"exec"),
         mod.__dict__)
    session=uuid.uuid4().hex
    context={
        "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "github_run_attempt":os.getenv("GITHUB_RUN_ATTEMPT","LOCAL"),
        "github_workflow":os.getenv("GITHUB_WORKFLOW","LOCAL"),
        "source_sha":os.getenv("GITHUB_SHA","LOCAL"),
        "python_version":platform.python_version(),
        "python_implementation":platform.python_implementation(),
        "system":platform.system(),
        "machine":platform.machine(),
    }
    pid=os.getpid()
    emit("begin",session_uuid=session,pid=pid,**context)
    result={"algorithm":"sha256_finite_sum_v1",
            "total":mod.aggregate(inputs["values"]),
            "noise":noise(inputs["seed"])}
    result_sha=dump(packet/"result.json",result)
    receipt={"session_uuid":session,"pid":pid,"seed":inputs["seed"],
             "input_sha256":digest(input_raw),
             "dependency_sha256":digest(dep_raw),
             "worker_sha256":digest(worker_raw),
             "result_sha256":result_sha,**context}
    receipt_sha=dump(packet/"receipt.json",receipt)
    emit("complete",session_uuid=session,pid=pid,
         result_sha256=result_sha,receipt_sha256=receipt_sha,**context)


if __name__=="__main__":
    main()
