"""Blind, conservative reconstruction from raw file bytes, NOT gold labels.

This module receives only the raw-evidence directory. It has no connector,
network, oracle, or gold-file access and must abstain on an orphaned output.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
FILE_SET={"receipt.json","stdout.log","input.json","result.json"}
HEX32=re.compile(r"^[0-9a-f]{32}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")


class ProvenanceConflict(RuntimeError):
    pass


def sha(raw):
    return sha256(raw).hexdigest()


def load_json(p):
    return json.loads(p.read_bytes())


def verify_packet(folder):
    names={p.name for p in folder.iterdir() if p.is_file()}
    if names=={"result.json"}:
        # A content hash is insufficient to assign an origin even with only
        # one matching known result; two different processes can make same bytes.
        return None, "ABSTAIN", "ORIGIN_RECEIPT_AND_LOG_MISSING"
    if names!=FILE_SET:
        return None, "ABSTAIN", "INCOMPLETE_EVIDENCE_BUNDLE"
    raws={name:(folder/name).read_bytes() for name in FILE_SET}
    try:
        receipt=json.loads(raws["receipt.json"])
        data=json.loads(raws["input.json"])
        result=json.loads(raws["result.json"])
        lines=[json.loads(line) for line in
               raws["stdout.log"].decode("utf-8").splitlines()]
    except (ValueError,UnicodeError,TypeError) as error:
        raise ProvenanceConflict("UNPARSABLE_RAW_PACKET") from error
    if len(lines)!=2 or [ev.get("phase") for ev in lines]!=["begin","complete"]:
        raise ProvenanceConflict("LOG_LIFECYCLE_INCONSISTENT")
    eid=receipt.get("execution_id")
    if not isinstance(eid,str) or not HEX32.fullmatch(eid):
        raise ProvenanceConflict("BAD_EXECUTION_ID")
    if not isinstance(receipt.get("pid"),int) or receipt["pid"]<=0:
        raise ProvenanceConflict("BAD_PROCESS_ID")
    if data.get("seed")!=receipt.get("seed"):
        raise ProvenanceConflict("INPUT_SEED_MISMATCH")
    if (sha(raws["input.json"])!=receipt.get("input_sha256") or
        sha(raws["result.json"])!=receipt.get("result_sha256")):
        raise ProvenanceConflict("HASH_CONTRADICTION")
    if sha((HERE/"worker.py").read_bytes())!=receipt.get("program_sha256"):
        raise ProvenanceConflict("WORKER_PROGRAM_SHA_CONTRADICTION")
    begin, end=lines
    for name in ("execution_id","pid","run_id"):
        if begin.get(name)!=receipt.get(name) or end.get(name)!=receipt.get(name):
            raise ProvenanceConflict("LOG_RECEIPT_ID_CONTRADICTION")
    for name in ("run_attempt","commit_sha","job"):
        if name not in receipt or begin.get(name)!=receipt.get(name):
            return None,"ABSTAIN","RECEIPT_RUN_METADATA_MISSING"
    if end.get("result_sha256")!=receipt.get("result_sha256"):
        raise ProvenanceConflict("LOG_OUTPUT_HASH_CONTRADICTION")
    if end.get("receipt_sha256")!=sha(raws["receipt.json"]):
        raise ProvenanceConflict("LOG_RECEIPT_HASH_CONTRADICTION")
    if not isinstance(receipt["run_id"],str) or not receipt["run_id"]:
        return None,"ABSTAIN","RUN_ID_MISSING"
    if not isinstance(receipt["run_attempt"],str) or not receipt["run_attempt"]:
        return None,"ABSTAIN","RUN_ATTEMPT_MISSING"
    # Metadata does not cryptographically prove independent scientific work.
    return eid,"GROUPED","MATCHED_LOG_RECEIPT_AND_BYTES"


def resolve(raw_dir):
    inventory=load_json(raw_dir/"inventory.json")
    if (inventory.get("schema")!="omega_raw_provenance_v1" or
        inventory.get("gold_excluded") is not True):
        raise ProvenanceConflict("UNTRUSTED_INVENTORY")
    declarations=inventory.get("packets")
    if not isinstance(declarations,list) or not declarations:
        raise ProvenanceConflict("EMPTY_INVENTORY")
    ids=[x["packet"] for x in declarations]
    if len(set(ids))!=len(ids):
        raise ProvenanceConflict("DUPLICATE_PACKET_ALIAS")
    outputs={}
    source_files={}
    for item in declarations:
        alias=item["packet"]
        if not re.fullmatch(r"packet-[0-9]{3}",alias):
            raise ProvenanceConflict("UNSAFE_PACKET_ALIAS")
        folder=raw_dir/"cases"/alias
        if not folder.is_dir():
            raise ProvenanceConflict("MISSING_DECLARED_PACKET_DIRECTORY")
        names={p.name for p in folder.iterdir()}
        if names!=set(item["files"]):
            raise ProvenanceConflict("INVENTORY_CONTENT_CONTRADICTION")
        origin,status,reason=verify_packet(folder)
        outputs[alias]={"packet":alias,"status":status,
                        "origin_id":origin,"reason":reason,"role":"EXECUTION"}
        source_files[alias]={
            x:sha((folder/x).read_bytes()) for x in names}
    # Reconstruct copy relation from actual file hash + copy log; a matching
    # result hash alone can NEVER establish a mirror.
    event_file=raw_dir/"copy_events.jsonl"
    events=[json.loads(x) for x in event_file.read_text().splitlines() if x.strip()]
    copied=set()
    for event in events:
        if event.get("event")!="copy_bundle":
            raise ProvenanceConflict("BAD_COPY_EVENT")
        src=event.get("source_packet");dst=event.get("copied_packet")
        if src not in outputs or dst not in outputs or src==dst or dst in copied:
            raise ProvenanceConflict("INVALID_COPY_EDGE")
        copied.add(dst)
        if (source_files[src]!=source_files[dst] or
            source_files[src]!=event.get("sha256_by_file") or
            set(source_files[src])!=FILE_SET):
            raise ProvenanceConflict("COPY_EVENT_BYTES_MISMATCH")
        if outputs[src]["status"]!="GROUPED" or outputs[dst]["status"]!="GROUPED":
            raise ProvenanceConflict("UNCERTIFIED_COPY_SOURCE")
        if outputs[src]["origin_id"]!=outputs[dst]["origin_id"]:
            raise ProvenanceConflict("COPY_SOURCE_ORIGIN_CONFLICT")
        outputs[dst]["role"]="MIRROR"
        outputs[dst]["reason"]="VERIFIED_ACTUAL_FILE_COPY"
    # A repeated root execution-id with no verifiable copy event is suspicious
    # even though a self-attested receipt would look consistent.
    originals={}
    for alias,record in outputs.items():
        if record["status"]!="GROUPED":
            continue
        origin=record["origin_id"]
        if record["role"]=="MIRROR":
            continue
        if origin in originals:
            raise ProvenanceConflict("UNEXPLAINED_DUPLICATE_EXECUTION_RECEIPT")
        originals[origin]=alias
    for alias,record in outputs.items():
        if record["status"]=="GROUPED" and record["role"]=="MIRROR":
            if record["origin_id"] not in originals:
                raise ProvenanceConflict("MIRROR_WITHOUT_ORIGINAL")
        if record["status"]=="ABSTAIN":
            record["role"]="UNRESOLVED"
    result={
        "experiment":"OMEGA-RAW-PROVENANCE-LAB-08",
        "run_scope":"four_separate_subprocesses_of_one_GitHub_Actions_job",
        "provenance_status":"PROCEDURAL_GROUPING_FROM_RAW_BYTES",
        "scientific_independence":"INDETERMINATE",
        "scientific_replication_certified":False,
        "results":sorted(outputs.values(),key=lambda x:x["packet"]),
        "group_count":len(originals),
        "mirror_count":sum(x["role"]=="MIRROR" for x in outputs.values()),
        "abstention_count":sum(x["status"]=="ABSTAIN" for x in outputs.values()),
        "false_independence_claims":0,
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--raw-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=resolve(args.raw_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({"group_count":result["group_count"],
                      "mirror_count":result["mirror_count"],
                      "abstention_count":result["abstention_count"],
                      "scientific_independence":result["scientific_independence"],
                      "report_sha256":sha(raw)},sort_keys=True))


if __name__=="__main__":
    main()
