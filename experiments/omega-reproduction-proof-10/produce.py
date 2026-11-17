"""Produce a genuine separate-job evidence bundle, preserving full raw bytes."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CASE_SETTINGS={
    "A":([2,3,5,7],4321,False),
    "B":([2,3,5,7],4321,False),
    "C":([1,4,5,7],4321,False),
    "D":([2,3,5,7],4321,True),
    "E":([2,3,5,7],4322,False),
}
EXPECTED_FILES={"inputs.json","dependency.py","worker_source.py",
                "result.json","receipt.json","stdout.log"}


def dump_json(file, value):
    file.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")


def produce(case, out):
    if case not in CASE_SETTINGS:
        raise ValueError("CASE_NOT_PREREGISTERED")
    if out.exists() and any(out.iterdir()):
        raise RuntimeError("DESTINATION_IS_NOT_EMPTY")
    out.mkdir(parents=True,exist_ok=True)
    values,seed,alternative=CASE_SETTINGS[case]
    dump_json(out/"inputs.json",{"values":values,"seed":seed})
    shutil.copyfile(HERE/("computation_variant.py" if alternative
                          else "computation.py"),out/"dependency.py")
    shutil.copyfile(HERE/"worker.py",out/"worker_source.py")
    cmd=[sys.executable,str(out/"worker_source.py"),"--packet",str(out)]
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    if run.returncode!=0:
        raise RuntimeError("COMPUTE_SUBPROCESS_FAILED: "+run.stderr[-1000:])
    if run.stderr.strip():
        raise RuntimeError("NONEMPTY_COMPUTE_STDERR")
    (out/"stdout.log").write_text(run.stdout,encoding="utf-8")
    if {p.name for p in out.iterdir() if p.is_file()}!=EXPECTED_FILES:
        raise RuntimeError("BAD_COMPUTE_OUTPUT_FILES")
    receipt=json.loads((out/"receipt.json").read_bytes())
    result=json.loads((out/"result.json").read_bytes())
    if (receipt["result_sha256"]!=sha256((out/"result.json").read_bytes()).hexdigest()
        or receipt["dependency_sha256"]!=sha256(
            (out/"dependency.py").read_bytes()).hexdigest()
        or receipt["seed"]!=seed
        or result["total"]!=sum(values)):
        raise RuntimeError("COMPUTATION_INTEGRITY_REJECTED")
    print(json.dumps({"case_submitted":case,"separate_subprocess":True,
                      "receipt_sha256":sha256(
                          (out/"receipt.json").read_bytes()).hexdigest(),
                      "result_sha256":receipt["result_sha256"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",required=True,choices=sorted(CASE_SETTINGS))
    ap.add_argument("--out",required=True,type=Path)
    arg=ap.parse_args()
    produce(arg.case,arg.out)


if __name__=="__main__":
    main()
