"""Independent gold-only scorer. NEVER import the blind inference module."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path


class ScoreFailure(AssertionError):
    pass


def fail_if(condition, code):
    if condition:
        raise ScoreFailure(code)


def audit(raw_dir, prediction, gold):
    expected=gold.get("cases")
    actual=prediction.get("results")
    fail_if(not isinstance(expected,dict) or len(expected)!=7, "BAD_GOLD_COHO RT".replace(" ",""))
    fail_if(not isinstance(actual,list) or len(actual)!=7, "BAD_PREDICTIONS")
    fail_if(prediction.get("scientific_independence")!="INDETERMINATE",
            "FORBIDDEN_SCIENTIFIC_INDEPENDENCE_CLAIM")
    fail_if(prediction.get("scientific_replication_certified") is not False,
            "FALSE_SCIENTIFIC_CERTIFICATION")
    fail_if(prediction.get("run_scope")!=
            "four_separate_subprocesses_of_one_GitHub_Actions_job",
            "MISREPRESENTED_RUN_SCOPE")
    fail_if(gold.get("scientific_independence")!="INDETERMINATE",
            "BAD_GOLD_INDEPENDENCE_STATUS")
    fail_if(gold.get("expected_execution_count")!=4, "BAD_GOLD_ROOT_COUNT")
    expected_roots=gold.get("real_subprocess_ids")
    fail_if(not isinstance(expected_roots,list) or
            len(expected_roots)!=4 or len(set(expected_roots))!=4,
            "ROOT_PROCESS_ID_INCONSISTENT")
    found={}
    for row in actual:
        key=row.get("packet")
        fail_if(key in found or key not in expected,"UNKNOWN_OR_DUPLICATE_PACKET")
        found[key]=row
    fail_if(set(found)!=set(expected), "INCOMPLETE_PACKETS")
    verified=0
    abstained=0
    mirrors=0
    raw_results={}
    pids={}
    for key,truth in sorted(expected.items()):
        pred=found[key]
        files=raw_dir/"cases"/key
        role=truth["role"]
        if role=="ORPHAN":
            fail_if({f.name for f in files.iterdir()}!={"result.json"},
                    "GOLD_ORPHAN_NOT_ORPHAN")
            fail_if(pred["status"]!="ABSTAIN" or
                    pred["origin_id"] is not None or
                    pred["role"]!="UNRESOLVED","ORPHAN_FALSE_ATTRIBUTION")
            abstained+=1
            continue
        fail_if(pred["status"]!="GROUPED" or
                pred["origin_id"]!=truth["origin_id"] or
                pred["role"]!=role,"WRONG_ORIGIN_GROUPING")
        receipt=json.loads((files/"receipt.json").read_text())
        result=(files/"result.json").read_bytes()
        inputs=(files/"input.json").read_bytes()
        text=(files/"stdout.log").read_text()
        lines=[json.loads(s) for s in text.splitlines()]
        fail_if(len(lines)!=2 or lines[0].get("phase")!="begin" or
                lines[1].get("phase")!="complete", "MALFORMED_REAL_LOGS")
        fail_if(receipt.get("execution_id")!=truth["origin_id"] or
                lines[0].get("execution_id")!=truth["origin_id"] or
                lines[1].get("execution_id")!=truth["origin_id"],
                "WORKER_ID_NOT_PROVEN_BY_LOG")
        fail_if(receipt["result_sha256"]!=sha256(result).hexdigest() or
                receipt["input_sha256"]!=sha256(inputs).hexdigest() or
                lines[1].get("receipt_sha256")!=sha256(
                    (files/"receipt.json").read_bytes()).hexdigest(),
                "INPUT_OUTPUT_RECEIPT_SHA_INVALID")
        fail_if(receipt["pid"]!=lines[0]["pid"] or
                receipt["pid"]!=lines[1]["pid"],"PROCESS_PID_NOT_VERIFIED")
        if role=="EXECUTION":
            fail_if(truth["origin_id"] in pids,"DUPLICATE_ROOT_PROCESS")
            pids[truth["origin_id"]]=receipt["pid"]
            raw_results[truth["origin_id"]]=sha256(result).hexdigest()
        else:
            mirrors+=1
        verified+=1
    fail_if(len(pids)!=4 or len(set(pids.values()))!=4,
            "FOUR_DISTINCT_PIDS_NOT_PROVEN")
    fail_if(set(pids)!=set(expected_roots), "ROOT_PROCESS_LABEL_ERROR")
    fail_if(len(set(raw_results.values()))!=3,
            "EXPECTED_SAME_OUTPUT_FROM_TWO_PROCESSES_MISSING")
    same=[(x,y) for x in raw_results for y in raw_results
          if x<y and raw_results[x]==raw_results[y]]
    fail_if(len(same)!=1, "UNEXPECTED_RESULT_DUPLICATE_PATTERN")
    fail_if((raw_dir/"cases"/next(k for k,v in expected.items()
              if v["role"]=="ORPHAN")/"result.json").read_bytes() not in [
              (raw_dir/"cases"/k/"result.json").read_bytes()
              for k,v in expected.items() if v["role"]=="EXECUTION"],
            "ORPHAN_DOES_NOT_MATCH_REAL_RESULT")
    fail_if(verified!=6 or abstained!=1 or mirrors!=2,
            "SCORE_COUNTS_MISMATCH")
    fail_if(prediction.get("group_count")!=4 or
            prediction.get("mirror_count")!=2 or
            prediction.get("abstention_count")!=1,
            "PREDICTED_SUMMARY_COUNTS_WRONG")
    return {
        "status":"RAW_PROVENANCE_PIPELINE_VERIFIED",
        "scientific_independence":"INDETERMINATE",
        "actual_subprocess_executions":len(pids),
        "real_mirrors_verified":mirrors,
        "unresolved_orphan":abstained,
        "unique_origin_groups":4,
        "correctly_grouped_evidence_packets":verified,
        "wrong_links":0,
        "false_scientific_certificates":0,
        "new_heldout_external_runs":0,
        "labels_never_supplied_to_blind_inference_job":True,
        "source_scope":"controlled subprocess file bytes, not standalone workflow runs",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--predictions",type=Path,required=True)
    p.add_argument("--gold",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    score=audit(args.raw_dir,json.loads(args.predictions.read_bytes()),
                json.loads(args.gold.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(score,indent=2,sort_keys=True)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({**score,"score_sha256":sha256(raw).hexdigest()},
                     sort_keys=True))


if __name__=="__main__":
    main()
