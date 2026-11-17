"""Prepare and execute a real cross-workflow numerical experiment packet."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CASES={
    "A": ([2,3,5,7],4321,False),
    "B": ([2,3,5,7],4321,False),
    "C": ([1,4,5,7],4321,False),
    "D": ([2,3,5,7],4321,True),
    "E": ([2,3,5,7],4322,False),
}
FILES={"inputs.json","worker_source.py","dependency.py","result.json",
       "receipt.json","stdout.log"}


def save_json(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")


def produce(case,folder):
    if case not in CASES:
        raise ValueError("UNPREREGISTERED_CASE")
    if folder.exists() and any(folder.iterdir()):
        raise ValueError("REUSED_EXPERIMENT_OUTPUT")
    folder.mkdir(parents=True,exist_ok=True)
    values,seed,alt=CASES[case]
    save_json(folder/"inputs.json",{"values":values,"seed":seed})
    shutil.copyfile(HERE/("algorithms_variant.py" if alt else "algorithms.py"),
                    folder/"dependency.py")
    shutil.copyfile(HERE/"worker.py",folder/"worker_source.py")
    result=subprocess.run([sys.executable,str(folder/"worker_source.py"),
                           "--packet",str(folder)],
                          capture_output=True,text=True,timeout=40)
    if result.returncode or result.stderr.strip():
        raise RuntimeError("ACTUAL_JOB_SUBPROCESS_FAILED:"+result.stderr[-1000:])
    (folder/"stdout.log").write_text(result.stdout)
    if {p.name for p in folder.iterdir()}!=FILES:
        raise RuntimeError("NOT_SIX_RAW_PROOF_FILES")
    receipt=json.loads((folder/"receipt.json").read_bytes())
    if receipt["seed"]!=seed or receipt["result_sha256"]!=sha256(
            (folder/"result.json").read_bytes()).hexdigest():
        raise RuntimeError("INVALID_PRODUCED_RECEIPT")
    print(json.dumps({
        "actual_compute_child_process":True,
        "github_run_id":receipt["github_run_id"],
        "github_workflow":receipt["github_workflow"],
        "python_version":receipt["python_version"],
        "result_sha256":receipt["result_sha256"],
        "six_raw_files":True
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case",required=True,choices=sorted(CASES))
    ap.add_argument("--out",type=Path,required=True)
    x=ap.parse_args()
    produce(x.case,x.out)


if __name__=="__main__":
    main()
