"""Independent evaluator using REST-derived gold kept out of inference.

No import from infer.py. A provider-log URL is a technical source link,
not scientific replication or a claim about provenance of the content.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

class ScoreMismatch(AssertionError):
    pass


def sha(raw):
    return sha256(raw).hexdigest()


def evaluate(raw_dir, predictions, gold):
    if gold.get("experiment")!="OMEGA-CROSS-WORKFLOW-RAW-09":
        raise ScoreMismatch("INVALID_GOLD_SCOPE")
    expected_runs=gold["source_runs"]
    if len(expected_runs)!=5 or len({r["run_id"] for r in expected_runs})!=5:
        raise ScoreMismatch("FIVE_ACTUAL_RUNS_NOT_VERIFIED")
    expected_sha={x["run_id"]:x["head_sha"] for x in expected_runs}
    if expected_sha[44149347157]!=expected_sha[44149424240]:
        raise ScoreMismatch("SAME_COMMIT_CONTROL_MISSING")
    if predictions.get("scientific_independence")!="INDETERMINATE" or             predictions.get("scientific_replication_certified") is not False:
        raise ScoreMismatch("ILLICIT_SCIENTIFIC_INDEPENDENCE_CERTIFICATE")
    if predictions.get("run_attempt_inferred_from_raw") is not False or             predictions.get("head_sha_inferred_from_raw") is not False:
        raise ScoreMismatch("HIDDEN_RUN_FIELDS_INVENTED")
    if predictions.get("archive_packets")!=9:
        raise ScoreMismatch("WRONG_PACKET_COUNT")
    inventory=json.loads((raw_dir/"inventory.json").read_bytes())
    if len(inventory["archive_packets"])!=9 or             len(inventory["log_files"])!=len(gold["logs"]):
        raise ScoreMismatch("BAD_BLIND_INVENTORY")
    if len(gold["artifacts"])!=9:
        raise ScoreMismatch("WRONG_GOLD_ARTIFACT_COUNT")

    for name,truth in gold["logs"].items():
        raw=(raw_dir/"logs"/name).read_bytes()
        if sha(raw)!=truth["sha256"] or len(raw)!=truth["size"]:
            raise ScoreMismatch("LOG_BYTE_OR_SHA_MISMATCH")
    mapped={x.get("packet"):x for x in predictions["results"]}
    if len(mapped)!=9 or set(mapped)!=set(gold["artifacts"]):
        raise ScoreMismatch("MISSING_OR_DUPLICATE_PREDICTIONS")

    wrong_links=0
    links=0
    abstentions=0
    mirror_ok=0
    orphan_ok=0
    positive_ids=set()
    original=[]
    for packet,truth in gold["artifacts"].items():
        pred=mapped[packet]
        envelope=json.loads(
            (raw_dir/"artifacts"/packet/"transport.json").read_bytes())
        raw=(raw_dir/"artifacts"/packet/"archive.zip").read_bytes()
        if sha(raw)!=envelope["zip_sha256"]:
            raise ScoreMismatch("TRANSPORT_BYTES_INVALID")
        expected_artid=truth["artifact_id"]
        if pred.get("artifact_id")!=expected_artid:
            raise ScoreMismatch("TRANSPORT_ARTIFACT_ID_CHANGED")
        if pred.get("zip_sha256")!=sha(raw):
            raise ScoreMismatch("ZIP_SHA_CHANGED")
        if pred.get("artifact_name")!=envelope["artifact_name"]:
            raise ScoreMismatch("TRANSPORT_NAME_CHANGED")
        role=truth["role"]
        if role=="ORPHAN":
            if pred["status"]!="ABSTAIN" or pred.get("run_id") is not None or                     pred["role"]!="UNRESOLVED":
                raise ScoreMismatch("ORPHAN_FALSE_ATTRIBUTION")
            orphan_ok+=1
            abstentions+=1
            continue
        if role=="MIRROR":
            if pred["role"]!="MIRROR_TRANSPORT":
                raise ScoreMismatch("TRANSPORT_MIRROR_NOT_IDENTIFIED")
            mirror_ok+=1
        elif role=="ORIGINAL":
            if pred["role"]!="ORIGINAL_TRANSPORT":
                raise ScoreMismatch("ORIGINAL_MISLABELED")
            original.append((packet,truth,pred))
            positive_ids.add(expected_artid)
        else:
            raise ScoreMismatch("UNKNOWN_ROLE_IN_GOLD")
        if pred["status"]=="LINKED_PROVIDER_LOG":
            links+=1
            if pred.get("run_id")!=truth["origin_run_id"]:
                wrong_links+=1
            if not pred["supporting_logs"] or any(
                    f not in gold["logs"] for f in pred["supporting_logs"]):
                raise ScoreMismatch("LINK_WITHOUT_LOG_SOURCE")
        elif pred["status"]=="ABSTAIN" and pred.get("run_id") is None:
            abstentions+=1
        else:
            raise ScoreMismatch("UNKNOWN_PROVENANCE_VERDICT")
    if len(original)!=7 or len(positive_ids)!=7:
        raise ScoreMismatch("SEVEN_REAL_SOURCE_ARCHIVES_NOT_FOUND")
    # Real GitHub source provider gold, not experimental labels supplied to
    # the inference code, supplies independent origin verification.
    if wrong_links:
        raise ScoreMismatch("FALSE_PROVENANCE_LINKS_DETECTED")
    if mirror_ok!=1 or orphan_ok!=1:
        raise ScoreMismatch("TRANSPORT_CONTROLS_MISSING")
    if not predictions.get("no_paid_api") or predictions.get("main_modified"):
        raise ScoreMismatch("UNSAFE_POLICY_CLAIMS")

    original_linked=[x for _,_,x in original
                     if x["status"]=="LINKED_PROVIDER_LOG"]
    correctly_linked=len(original_linked)
    if correctly_linked!=predictions["certified_artifact_links"]:
        raise ScoreMismatch("INCORRECT_UNIQUE_LINK_COUNT")
    if links!=predictions["linked_packet_count"] or             abstentions!=predictions["abstentions"]:
        raise ScoreMismatch("INCORRECT_REPORTED_COUNTS")

    # Additional source-independent pairwise check. A name-only method
    # would fuse distinct workflow invocations sharing a generic file label.
    pair_names=0
    name_false=0
    name_true=0
    for i in range(len(original)):
        for j in range(i+1,len(original)):
            a=original[i];b=original[j]
            same_name=a[2]["artifact_name"]==b[2]["artifact_name"]
            same_run=a[1]["origin_run_id"]==b[1]["origin_run_id"]
            if same_name:
                pair_names+=1
                if same_run:
                    name_true+=1
                else:
                    name_false+=1

    if correctly_linked==0:
        status="NO_PROVIDER_URL_SIGNAL"
    else:
        status="PROVIDER_LOG_LINKS_VERIFIED"
    return {
        "status":status,
        "origin_scope":"five already known GitHub runs; real ZIPs and job logs",
        "source_runs":len(expected_runs),
        "real_zip_archives":len(original),
        "real_job_logs":len(gold["logs"]),
        "packet_count":len(mapped),
        "linked_real_archives":correctly_linked,
        "unlinked_real_archives":7-correctly_linked,
        "linked_packets_including_transport_mirror":links,
        "correct_origin_links":correctly_linked,
        "wrong_origin_links":wrong_links,
        "transport_mirror_ok":mirror_ok,
        "transport_orphan_abstention_ok":orphan_ok,
        "total_abstentions":abstentions,
        "name_only_same_name_pairs":pair_names,
        "name_only_correct_same_run_pairs":name_true,
        "name_only_wrong_same_run_pairs":name_false,
        "same_head_sha_but_two_runs":[44149347157,44149424240],
        "scientific_independence":"INDETERMINATE",
        "scientific_replication_certified":False,
        "independent_external_workflows_generated_by_this_test":0,
        "gold_isolated_from_inference_job":True,
        "limitation":"provider log URL establishes artifact-to-run, not science or ZIP-only provenance",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--predictions",type=Path,required=True)
    p.add_argument("--gold",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=evaluate(args.raw_dir,
                    json.loads(args.predictions.read_bytes()),
                    json.loads(args.gold.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(b)
    print(json.dumps({**result,"score_sha256":sha(b)},sort_keys=True))


if __name__=="__main__":
    main()
