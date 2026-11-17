"""Gold-blind cross-workflow linker using real ZIP bytes and raw job logs.

Only explicit upload-artifact download URLs link an artifact transport ID to a
GitHub run ID. Equal archive bytes, filenames, or commit SHAs are never
assumed to mean a shared process origin.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import zipfile

EXPERIMENT="OMEGA-CROSS-WORKFLOW-RAW-09"
URL_PATTERN=re.compile(
    r"https://github\.com/Abrasax63/Omega-pub/actions/runs/([0-9]{4,})/artifacts/([0-9]{4,})",
    re.IGNORECASE,
)
HEX64=re.compile(r"^[0-9a-f]{64}$")


class LinkConflict(RuntimeError):
    pass


def hash_bytes(data):
    return sha256(data).hexdigest()


def infer_links_from_logs(raw_root):
    index=json.loads((raw_root/"inventory.json").read_bytes())
    if index.get("schema")!="omega-cross-workflow-raw09" or             index.get("gold_not_in_raw") is not True:
        raise LinkConflict("INVALID_RAW_INVENTORY")
    if index.get("source_type")!="real_GitHub_REST_job_logs_and_artifact_ZIP_bytes":
        raise LinkConflict("INVALID_RAW_SOURCE_TYPE")
    expected_logs=index.get("log_files")
    if not isinstance(expected_logs,list) or len(set(expected_logs))!=len(expected_logs):
        raise LinkConflict("INVALID_RAW_LOG_LIST")
    actual_logs={x.name for x in (raw_root/"logs").iterdir() if x.is_file()}
    if set(expected_logs)!=actual_logs:
        raise LinkConflict("LOG_INVENTORY_MISMATCH")
    links={}
    evidence={}
    for filename in expected_logs:
        if not re.fullmatch(r"trace-[0-9]{3}\.log",filename):
            raise LinkConflict("UNSAFE_LOG_NAME")
        data=(raw_root/"logs"/filename).read_bytes()
        try:
            decoded=data.decode("utf-8")
        except UnicodeError as exc:
            raise LinkConflict("NON_UTF8_LOG") from exc
        for line in decoded.splitlines():
            # These text markers are printed by actions/upload-artifact.
            # Other URLs occurring elsewhere in code snippets or readme
            # cannot independently certify provenance.
            if not ("artifact" in line.lower() and
                    ("download url" in line.lower() or
                     "can be downloaded at" in line.lower())):
                continue
            for match in URL_PATTERN.finditer(line):
                runid=int(match.group(1)); aid=int(match.group(2))
                if aid in links and links[aid]!=runid:
                    raise LinkConflict("CONFLICTING_LOG_RUN_IDS")
                links[aid]=runid
                evidence.setdefault(aid,set()).add(filename)
    return index,links,evidence


def verify_archive(path):
    raw=path.read_bytes()
    if not zipfile.is_zipfile(BytesIO(raw)):
        raise LinkConflict("INVALID_ARCHIVE_ZIP")
    try:
        with zipfile.ZipFile(BytesIO(raw)) as z:
            paths=z.namelist()
            if not paths or len(paths)>3000:
                raise LinkConflict("EMPTY_OR_EXCESSIVE_ZIP")
            if any(p.startswith("/") or ".." in Path(p).parts for p in paths):
                raise LinkConflict("UNSAFE_ZIP_MEMBER_PATH")
            if z.testzip() is not None:
                raise LinkConflict("ZIP_BAD_CRC")
    except (zipfile.BadZipFile,EOFError) as exc:
        raise LinkConflict("CORRUPT_ZIP") from exc
    return hash_bytes(raw)


def resolve(raw_root):
    index, links, evidence=infer_links_from_logs(raw_root)
    names=index.get("archive_packets")
    if (not isinstance(names,list) or len(names)!=9 or
        len(set(names))!=len(names)):
        raise LinkConflict("UNEXPECTED_PACKET_COUNT")
    if {x.name for x in (raw_root/"artifacts").iterdir()}!=set(names):
        raise LinkConflict("PACKET_DIRECTORY_MISMATCH")
    results=[]
    seen={}
    for packet in names:
        if not re.fullmatch(r"packet-[0-9]{3}",packet):
            raise LinkConflict("UNSAFE_PACKET_NAME")
        folder=raw_root/"artifacts"/packet
        if {x.name for x in folder.iterdir()}!={"archive.zip","transport.json"}:
            raise LinkConflict("PACKET_FILES_INVALID")
        envelope=json.loads((folder/"transport.json").read_bytes())
        expected_hash=envelope.get("zip_sha256")
        if not isinstance(expected_hash,str) or not HEX64.fullmatch(expected_hash):
            raise LinkConflict("INVALID_TRANSPORT_DIGEST")
        actual_hash=verify_archive(folder/"archive.zip")
        if expected_hash!=actual_hash:
            raise LinkConflict("TRANSPORT_DIGEST_MISMATCH")
        aid=envelope.get("artifact_id")
        name=envelope.get("artifact_name")
        if name is not None and not isinstance(name,str):
            raise LinkConflict("INVALID_TRANSPORT_NAME")
        if aid is None:
            results.append({"packet":packet,"status":"ABSTAIN",
                            "run_id":None,"artifact_id":None,
                            "role":"UNRESOLVED", "reason":"NO_TRANSPORT_ARTIFACT_ID",
                            "zip_sha256":actual_hash,"artifact_name":name,
                            "supporting_logs":[]})
            continue
        if type(aid) is not int or aid<=0:
            raise LinkConflict("INVALID_TRANSPORT_ARTIFACT_ID")
        if aid in seen:
            previous=seen[aid]
            if (previous["zip_sha256"]!=actual_hash or
                previous["artifact_name"]!=name):
                raise LinkConflict("CONTRADICTORY_MIRROR_BYTES")
            role="MIRROR_TRANSPORT"
        else:
            role="ORIGINAL_TRANSPORT"
        if aid not in links:
            results.append({"packet":packet,"status":"ABSTAIN",
                            "run_id":None,"artifact_id":aid,
                            "role":role,"reason":"NO_PROVIDER_LOG_URL",
                            "zip_sha256":actual_hash,"artifact_name":name,
                            "supporting_logs":[]})
        else:
            results.append({"packet":packet,"status":"LINKED_PROVIDER_LOG",
                            "run_id":links[aid],"artifact_id":aid,
                            "role":role,"reason":"EXPLICIT_UPLOAD_LOG_URL",
                            "zip_sha256":actual_hash,"artifact_name":name,
                            "supporting_logs":sorted(evidence[aid])})
        if aid not in seen:
            seen[aid]=results[-1]
    known=[x for x in results if x["status"]=="LINKED_PROVIDER_LOG"]
    return {"experiment":EXPERIMENT,
            "status":"LINKED_WITH_PROVIDER_LOGS" if known else
                     "NO_PROVIDER_URL_SIGNAL",
            "archive_packets":len(results),
            "actual_log_files_scanned":len(index["log_files"]),
            "identified_artifact_ids":len(links),
            "certified_artifact_links":len(
                {x["artifact_id"] for x in known if x["artifact_id"] is not None}),
            "linked_packet_count":len(known),
            "linked_distinct_runs":len(set(x["run_id"] for x in known)),
            "transport_mirror_count":sum(x["role"]=="MIRROR_TRANSPORT"
                                           for x in results),
            "abstentions":sum(x["status"]=="ABSTAIN" for x in results),
            "scientific_independence":"INDETERMINATE",
            "scientific_replication_certified":False,
            "run_attempt_inferred_from_raw":False,
            "head_sha_inferred_from_raw":False,
            "no_paid_api":True,"main_modified":False,
            "link_rule":"explicit_actions_upload_artifact_URL_in_actual_job_log",
            "results":sorted(results,key=lambda x:x["packet"])}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=resolve(args.raw_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({"status":result["status"],
                      "link_count":result["certified_artifact_links"],
                      "linked_distinct_runs":result["linked_distinct_runs"],
                      "abstentions":result["abstentions"],
                      "scientific_independence":result["scientific_independence"],
                      "report_sha256":hash_bytes(raw)},sort_keys=True))


if __name__=="__main__":
    main()
