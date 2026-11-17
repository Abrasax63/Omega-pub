"""Produce four ACTUAL subprocess computations, two genuine filesystem copies,
and one originless ambiguous output. A separate gold file is never passed to
the inference process.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import uuid

HERE=Path(__file__).resolve().parent
SEED=81223
FOUR_INPUTS=(
    {"seed":43,"values":[2,3,5,7]},
    {"seed":43,"values":[2,3,5,7]},  # same output, DISTINCT process
    {"seed":59,"values":[11,13,17]},
    {"seed":71,"values":[19,23,29]},
)
FILES=("receipt.json","stdout.log","input.json","result.json")


def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf-8")


def checksum(p):
    return sha256(p.read_bytes()).hexdigest()


def generate(raw_dir, gold_file):
    if raw_dir.exists() and any(raw_dir.iterdir()):
        raise ValueError("NONEMPTY_RAW_DESTINATION")
    if gold_file.exists():
        raise ValueError("PREEXISTING_ANSWER_KEY")
    raw_dir.mkdir(parents=True,exist_ok=True)
    work=raw_dir.parent/"private_worker_build"
    if work.exists():
        raise ValueError("PREEXISTING_PRIVATE_BUILD")
    work.mkdir(parents=True)
    handles=[]
    for idx,config in enumerate(FOUR_INPUTS):
        folder=work/str(idx)
        folder.mkdir()
        write_json(folder/"input.json",config)
        eid=uuid.uuid4().hex
        command=[sys.executable,str(HERE/"worker.py"),"--input",
                 str(folder/"input.json"),"--output-dir",str(folder),
                 "--execution-id",eid]
        handle=subprocess.Popen(command,stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,text=True)
        handles.append((idx,eid,folder,handle))
    raw_roots=[]
    for idx,eid,folder,handle in handles:
        stdout,stderr=handle.communicate(timeout=40)
        if handle.returncode:
            raise RuntimeError(f"WORKER_FAILED_{idx}: {stderr[-1000:]}")
        (folder/"stdout.log").write_text(stdout,encoding="utf-8")
        if stderr.strip():
            raise RuntimeError(f"WORKER_STDERR_NONEMPTY_{idx}")
        receipt=json.loads((folder/"receipt.json").read_text())
        if receipt["execution_id"]!=eid or len(stdout.splitlines())!=2:
            raise AssertionError("INCONSISTENT_WORKER_LOG")
        raw_roots.append({"execution_id":eid,"folder":folder,
                          "result_sha":checksum(folder/"result.json"),
                          "pid":receipt["pid"]})
    if len({x["execution_id"] for x in raw_roots})!=4:
        raise AssertionError("REPEATED_EXECUTION_ID")
    if len({x["pid"] for x in raw_roots})!=4:
        raise AssertionError("REUSED_PID_AMONG_PARALLEL_SUBPROCESSES")
    if raw_roots[0]["result_sha"]!=raw_roots[1]["result_sha"]:
        raise AssertionError("EQUAL_INPUT_MUST_PRODUCE_EQUAL_OUTPUT")
    if len({x["result_sha"] for x in raw_roots})!=3:
        raise AssertionError("BAD_RESULT_COLLISION_CONTROL")

    # Aliases are shuffled, and their mapping is written ONLY to the gold.
    instructions=[("EXECUTION",i) for i in range(4)]
    instructions += [("MIRROR",0),("MIRROR",2),("ORPHAN",0)]
    random.Random(SEED).shuffle(instructions)
    dataset=raw_dir/"cases"
    dataset.mkdir()
    gold={"scope":"subprocess_origin_within_one_GitHub_workflow_run",
          "scientific_independence":"INDETERMINATE",
          "expected_execution_count":4,"cases":{},"real_subprocess_ids":[
              r["execution_id"] for r in raw_roots]}
    source_alias={}
    mirror_instructions=[]
    for offset,(role,src_idx) in enumerate(instructions):
        alias=f"packet-{offset:03d}"
        dst=dataset/alias
        dst.mkdir()
        root=raw_roots[src_idx]
        if role=="EXECUTION":
            for filename in FILES:
                shutil.copyfile(root["folder"]/filename,dst/filename)
            source_alias[src_idx]=alias
        elif role=="MIRROR":
            # Copy is deferred until all original aliases have been populated.
            mirror_instructions.append((alias,src_idx))
        elif role=="ORPHAN":
            # The output SHA is shared by TWO independent real child processes.
            shutil.copyfile(root["folder"]/"result.json",dst/"result.json")
        gold["cases"][alias]={
            "role":role,
            "origin_id":root["execution_id"] if role!="ORPHAN" else None,
            "status":"GROUPED" if role!="ORPHAN" else "ABSTAIN",
        }
    for alias,src_idx in mirror_instructions:
        root_src=dataset/source_alias[src_idx]
        dst=dataset/alias
        for filename in FILES:
            shutil.copyfile(root_src/filename,dst/filename)
    # Copy event is actually emitted by the orchestrator AFTER byte copies.
    events=[]
    for alias,src_idx in mirror_instructions:
        origin_alias=source_alias[src_idx]
        src=dataset/origin_alias
        dst=dataset/alias
        expected={filename:checksum(src/filename) for filename in FILES}
        if {filename:checksum(dst/filename) for filename in FILES}!=expected:
            raise AssertionError("MIRROR_DID_NOT_COPY_ORIGIN_BYTES")
        events.append({"event":"copy_bundle",
                       "source_packet":origin_alias,"copied_packet":alias,
                       "sha256_by_file":expected})
    with (raw_dir/"copy_events.jsonl").open("w",encoding="utf-8") as stream:
        for event in events:
            stream.write(json.dumps(event,sort_keys=True)+"\n")
    # Inventory does not contain roles, group mappings, expected count per group,
    # or the gold. The file list is observational and needed for fail-closed IO.
    listing=[]
    for folder in sorted(dataset.iterdir()):
        listing.append({"packet":folder.name,
                        "files":sorted(f.name for f in folder.iterdir())})
    write_json(raw_dir/"inventory.json",{
        "schema":"omega_raw_provenance_v1",
        "study":"controlled_real_subprocesses_not_independent_GitHub_runs",
        "packets":listing,
        "gold_excluded":True,
    })
    if "gold" in str(raw_dir).lower():
        raise AssertionError("GOLD_IN_BLIND_DIRECTORY_NAME")
    # Gold goes to independent artifact/job, not into the raw evidence archive.
    write_json(gold_file,gold)
    # Never print UUID -> role mappings here (public job logs).
    print(json.dumps({"produced_processes":4,"raw_packets":len(listing),
                      "real_file_copies":len(events),
                      "ambiguous_packets":1,
                      "raw_case_files":sum(len(i["files"]) for i in listing),
                      "secret_answer_key_separate":True},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--gold-file",type=Path,required=True)
    args=p.parse_args()
    if args.raw_dir.resolve()==args.gold_file.resolve() or (
        args.raw_dir.resolve() in args.gold_file.resolve().parents):
        raise ValueError("ANSWER_KEY_MUST_NOT_BE_WITHIN_RAW_DIR")
    generate(args.raw_dir,args.gold_file)


if __name__=="__main__":
    main()
