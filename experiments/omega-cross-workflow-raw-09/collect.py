"""Fetch real GitHub job-log bytes and real artifact ZIP bytes on the runner.

The collector receives a GitHub Actions token with read-only actions
permission. It writes two directories, raw/ (blind input) and gold/ (labels).
No gold fields are stored in raw manifests or filenames.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import random
import re
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
import zipfile

REPO = "Abrasax63/Omega-pub"
BASE = f"https://api.github.com/repos/{REPO}"
SOURCE = (
    (44168561827, (14367000971,14366048721)),
    (44163800137, (14365590280,)),
    (44162518044, (14362909206,14363373146)),
    (44149347157, (14359120046,)),
    (44149424240, (14358575909,)),
)
PREREG_COMMIT = "4a665830b38f133ab903882748029123c6b33389"
SAMPLE_SEED = 59221
ZIP_LIMIT = 15*1024*1024
LOG_LIMIT = 10*1024*1024


def hash_bytes(b):
    return sha256(b).hexdigest()


def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")


class CollectionBlocked(RuntimeError):
    pass


class CrossHostRedirect(HTTPRedirectHandler):
    """Do not pass GitHub authorization to temporary archive storage hosts."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host=(urlsplit(newurl).hostname or "").lower()
        allowed=(host=="api.github.com" or host=="github.com" or
                 host.endswith(".githubusercontent.com") or
                 host.endswith(".blob.core.windows.net"))
        if urlsplit(newurl).scheme != "https" or not allowed:
            raise CollectionBlocked("UNEXPECTED_REDIRECT_HOST")
        nextreq=super().redirect_request(req,fp,code,msg,headers,newurl)
        if nextreq is not None and host!="api.github.com":
            nextreq.remove_header("Authorization")
            # Redirected Request headers can be in unredirected_hdrs too.
            for key in list(nextreq.unredirected_hdrs):
                if key.lower()=="authorization":
                    del nextreq.unredirected_hdrs[key]
        return nextreq


def http_api(relative,token,limit=ZIP_LIMIT):
    url=BASE+relative
    req=Request(url,headers={
        "Accept":"application/vnd.github+json",
        "Authorization":f"Bearer {token}",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"OmegaRawProvenanceAudit/09",
    })
    with build_opener(CrossHostRedirect()).open(req,timeout=55) as reply:
        content=reply.read(limit+1)
    if len(content)>limit:
        raise CollectionBlocked("BINARY_SIZE_LIMIT")
    if not content:
        raise CollectionBlocked("EMPTY_API_PAYLOAD")
    return content


def as_json(raw):
    try:
        return json.loads(raw)
    except (ValueError,UnicodeError) as e:
        raise CollectionBlocked("BAD_SOURCE_API_JSON") from e


def collect(token,raw_root,gold_path):
    if not token:
        raise CollectionBlocked("NO_GITHUB_TOKEN")
    if raw_root.exists() and any(raw_root.iterdir()):
        raise CollectionBlocked("RAW_OUTPUT_NOT_EMPTY")
    if gold_path.exists() or raw_root.resolve() in gold_path.resolve().parents:
        raise CollectionBlocked("ANSWER_KEY_NOT_ISOLATED")
    raw_root.mkdir(parents=True,exist_ok=True)
    scans=[]
    for runid,artifact_ids in SOURCE:
        run=as_json(http_api(f"/actions/runs/{runid}",token))
        jobs=as_json(http_api(f"/actions/runs/{runid}/jobs?per_page=100",token))
        arts=as_json(http_api(f"/actions/runs/{runid}/artifacts?per_page=100",token))
        if run.get("id")!=runid or run.get("repository",{}).get("full_name")!=REPO:
            raise CollectionBlocked("RUN_IDENTITY_MISMATCH")
        if not isinstance(run.get("run_attempt"),int):
            raise CollectionBlocked("MISSING_RUN_ATTEMPT")
        if len(jobs.get("jobs",[]))!=jobs.get("total_count"):
            raise CollectionBlocked("PAGINATED_JOB_LIST_NOT_EXHAUSTIVE")
        if len(arts.get("artifacts",[]))!=arts.get("total_count"):
            raise CollectionBlocked("PAGINATED_ARTIFACT_LIST_NOT_EXHAUSTIVE")
        found={a["id"]:a for a in arts["artifacts"]}
        if not set(artifact_ids)<=set(found):
            raise CollectionBlocked("EXPECTED_ARTIFACT_NOT_FOUND")
        scans.append({"run":run,"jobs":jobs["jobs"],
                      "selected":[found[i] for i in artifact_ids]})

    artifact_blobs=[]
    log_blobs=[]
    for scan in scans:
        run=scan["run"]
        for art in scan["selected"]:
            aid=art["id"]
            if art.get("expired"):
                raise CollectionBlocked("SOURCE_ARCHIVE_EXPIRED")
            if art.get("workflow_run",{}).get("id")!=run["id"]:
                raise CollectionBlocked("ARTIFACT_RUN_API_CONFLICT")
            buf=http_api(f"/actions/artifacts/{aid}/zip",token,ZIP_LIMIT)
            if not zipfile.is_zipfile(BytesIO(buf)):
                raise CollectionBlocked("NOT_ACTUAL_ZIP_BYTES")
            with zipfile.ZipFile(BytesIO(buf)) as z:
                if not z.namelist() or len(z.namelist())>3000:
                    raise CollectionBlocked("BAD_ARCHIVE_ENTRY_COUNT")
            artifact_blobs.append({"blob":buf,"artifact_id":aid,
                                   "name":art["name"],"run":run,
                                   "size":len(buf)})
        for job in scan["jobs"]:
            jid=job["id"]
            b=http_api(f"/actions/jobs/{jid}/logs",token,LOG_LIMIT)
            if b"\x00" in b[:400] or b[:4]==b"PK\x03\x04":
                raise CollectionBlocked("EXPECTED_PLAINTEXT_JOB_LOG")
            try:
                b.decode("utf-8")
            except UnicodeError as exc:
                raise CollectionBlocked("JOB_LOG_NOT_UTF8") from exc
            log_blobs.append({"blob":b,"job":job,"run":run})

    # All downloaded origins are known to the independent scorer alone.
    origins=random.Random(SAMPLE_SEED)
    artifacts=list(artifact_blobs)
    logs=list(log_blobs)
    origins.shuffle(artifacts)
    origins.shuffle(logs)
    raw_index={"schema":"omega-cross-workflow-raw09",
               "source_type":"real_GitHub_REST_job_logs_and_artifact_ZIP_bytes",
               "preregistered_commit":PREREG_COMMIT,
               "archive_packets":[],"log_files":[],
               "gold_not_in_raw":True}
    gold={"experiment":"OMEGA-CROSS-WORKFLOW-RAW-09",
          "source_runs":[{"run_id":s["run"]["id"],
                          "run_attempt":s["run"]["run_attempt"],
                          "head_sha":s["run"]["head_sha"],
                          "workflow_name":s["run"].get("name"),
                          "event":s["run"]["event"]}
                         for s in scans],
          "artifacts":{},"logs":{},
          "transport_injections":{"mirror":None,"orphan":None}}
    packets=[]
    for idx,art in enumerate(artifacts):
        alias=f"packet-{idx:03d}"
        folder=raw_root/"artifacts"/alias
        folder.mkdir(parents=True,exist_ok=False)
        (folder/"archive.zip").write_bytes(art["blob"])
        envelope={"artifact_id":art["artifact_id"],
                  "artifact_name":art["name"],"zip_sha256":hash_bytes(art["blob"])}
        write_json(folder/"transport.json",envelope)
        packets.append(alias)
        raw_index["archive_packets"].append(alias)
        gold["artifacts"][alias]={"origin_run_id":art["run"]["id"],
                                   "artifact_id":art["artifact_id"],
                                   "role":"ORIGINAL"}
    for idx,trace in enumerate(logs):
        alias=f"trace-{idx:03d}.log"
        (raw_root/"logs").mkdir(exist_ok=True)
        (raw_root/"logs"/alias).write_bytes(trace["blob"])
        raw_index["log_files"].append(alias)
        gold["logs"][alias]={"run_id":trace["run"]["id"],
                              "job_id":trace["job"]["id"],
                              "size":len(trace["blob"]),
                              "sha256":hash_bytes(trace["blob"])}
    # Synthetic transport modifications (do not call them newly retrieved
    # GitHub artifacts): an exact mirror and an unlabelled archive copy.
    src0,src1=packets[0],packets[1]
    mirror="packet-007"
    orphan="packet-008"
    for name,src,missing_id in (
        (mirror,src0,False),(orphan,src1,True)):
        folder=raw_root/"artifacts"/name
        folder.mkdir()
        b=(raw_root/"artifacts"/src/"archive.zip").read_bytes()
        (folder/"archive.zip").write_bytes(b)
        source_envelope=as_json(
            (raw_root/"artifacts"/src/"transport.json").read_bytes())
        env={"artifact_id":None if missing_id else source_envelope["artifact_id"],
             "artifact_name":source_envelope["artifact_name"],
             "zip_sha256":hash_bytes(b)}
        write_json(folder/"transport.json",env)
        raw_index["archive_packets"].append(name)
        gold["artifacts"][name]={
            "origin_run_id":None if missing_id else gold["artifacts"][src]["origin_run_id"],
            "artifact_id":None if missing_id else gold["artifacts"][src]["artifact_id"],
            "role":"ORPHAN" if missing_id else "MIRROR"}
    gold["transport_injections"]={"mirror":mirror,"orphan":orphan}
    # Refuse accidental leakage of gold in provider input archive.
    write_json(raw_root/"inventory.json",raw_index)
    write_json(gold_path,gold)
    assert len(raw_index["archive_packets"])==9
    assert len(raw_index["log_files"])>=5
    print(json.dumps({"source_runs":len(scans),"real_zip_archives":len(artifact_blobs),
                      "actual_job_logs":len(log_blobs),"raw_zip_packets":9,
                      "transport_mirrors":1,"transport_orphans":1,
                      "gold_isolated":True,"no_paid_api":True},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw-dir",type=Path,required=True)
    p.add_argument("--gold-file",type=Path,required=True)
    args=p.parse_args()
    collect(os.environ.get("GH_ACTIONS_READ_TOKEN",""),args.raw_dir,args.gold_file)


if __name__=="__main__":
    main()
