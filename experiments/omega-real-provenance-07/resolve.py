"""OMEGA-REAL-PROVENANCE-07 — conservative grouping of real GitHub metadata.

GitHub run attempts can be verified within the trusted pinned REST projections.
The resulting grouping NEVER certifies scientific independence or a reproduced
mathematical result; source archives/logs are NOT inspected here.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

EXPERIMENT = "OMEGA-REAL-PROVENANCE-07"
PREREG = "bc667631fca36fb992c4e26f2d700195f6462def"
HEX_SHA = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceConflict(ValueError):
    pass


def hash_raw(data):
    return sha256(data).hexdigest()


def valid_id(x):
    return type(x) is int and x > 0


def verify_sha(value):
    return isinstance(value, str) and bool(HEX_SHA.fullmatch(value))


def resolve(snapshot):
    """Regroup raw artifact records by verified provider run/attempt metadata.

    No pre-supplied grouping or scientific-independence label is consulted.
    """
    if snapshot.get("repository") != "Abrasax63/Omega-pub":
        raise ProvenanceConflict("UNEXPECTED_REPOSITORY")
    documents = snapshot.get("source_documents")
    if not isinstance(documents, list) or not documents:
        raise ProvenanceConflict("NO_SOURCE_DOCUMENTS")

    run_lookup = {}
    for doc in documents:
        run = doc.get("run") or {}
        rid = run.get("id")
        if not valid_id(rid):
            raise ProvenanceConflict("INVALID_RUN_IDENTIFIER")
        if doc.get("run_api_url") != (
            f"https://api.github.com/repos/{snapshot['repository']}/actions/runs/{rid}"
        ):
            raise ProvenanceConflict("RUN_SOURCE_URL_MISMATCH")
        if doc.get("artifacts_api_url") != doc["run_api_url"] + "/artifacts":
            raise ProvenanceConflict("ARTIFACT_SOURCE_URL_MISMATCH")
        if not verify_sha(run.get("head_sha")):
            raise ProvenanceConflict("BAD_RUN_SHA")
        if run.get("repository") != snapshot["repository"]:
            raise ProvenanceConflict("RUN_REPOSITORY_MISMATCH")
        if rid in run_lookup and run_lookup[rid] != run:
            raise ProvenanceConflict("CONTRADICTORY_RUN_METADATA")
        run_lookup[rid] = run
        arts = doc.get("artifacts")
        if not isinstance(arts, list) or not isinstance(doc.get("artifact_count"), int):
            raise ProvenanceConflict("MISSING_ARTIFACT_LIST")
        if doc["artifact_count"] != len(arts):
            raise ProvenanceConflict("ARTIFACT_LIST_INCOMPLETE")

    artifacts_by_id = {}
    unknown = []
    duplicate_refs = 0
    for doc in documents:
        origin_run = doc["run"]
        for art in doc["artifacts"]:
            aid = art.get("id")
            if not valid_id(aid):
                raise ProvenanceConflict("INVALID_ARTIFACT_ID")
            source = art.get("workflow_run") or {}
            source_id = source.get("id")
            sha = source.get("head_sha")
            if source_id is None or sha is None:
                unknown.append({"artifact_id": aid, "reason": "MISSING_ARTIFACT_PROVENANCE"})
                continue
            if not valid_id(source_id) or source_id != origin_run["id"]:
                raise ProvenanceConflict("ARTIFACT_RUN_ID_CONFLICT")
            if not verify_sha(sha) or sha != origin_run["head_sha"]:
                raise ProvenanceConflict("ARTIFACT_SHA_CONFLICT")
            attempt = origin_run.get("run_attempt")
            if not valid_id(attempt):
                unknown.append({"artifact_id": aid, "reason": "MISSING_RUN_ATTEMPT"})
                continue
            record = {
                "artifact_id": aid, "name": art.get("name"),
                "run_id": source_id, "run_attempt": attempt,
                "head_sha": sha, "repository": origin_run["repository"],
            }
            if aid in artifacts_by_id:
                if artifacts_by_id[aid] != record:
                    raise ProvenanceConflict("DUPLICATE_ARTIFACT_CONFLICT")
                duplicate_refs += 1
                continue
            artifacts_by_id[aid] = record

    groups = {}
    for art in artifacts_by_id.values():
        key = (art["repository"], art["run_id"], art["run_attempt"])
        groups.setdefault(key, []).append(art)
    merged = []
    for (repo, runid, attempt), items in sorted(groups.items()):
        head_set = {i["head_sha"] for i in items}
        if len(head_set) != 1:
            raise ProvenanceConflict("GROUP_SHA_CONFLICT")
        merged.append({
            "repository": repo, "run_id": runid, "run_attempt": attempt,
            "head_sha": next(iter(head_set)),
            "artifact_ids": sorted(i["artifact_id"] for i in items),
            "artifact_names": sorted(i["name"] for i in items),
        })
    repeated_shas = []
    for i,first in enumerate(merged):
        for second in merged[i+1:]:
            if first["head_sha"] == second["head_sha"]:
                repeated_shas.append({
                    "head_sha": first["head_sha"],
                    "distinct_run_ids": sorted((first["run_id"], second["run_id"])),
                })
    return {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG,
        "execution_grouping_status": (
            "VERIFIED_PROVIDER_METADATA" if not unknown else
            "PARTIAL_WITH_ABSTENTIONS"
        ),
        "scientific_independence": "INDETERMINATE",
        "scientific_replication_certified": False,
        "provenance_sources_are_live": False,
        "provider_metadata_trusted": True,
        "run_count_from_source_documents": len(run_lookup),
        "total_artifact_entries": sum(len(x["artifacts"]) for x in documents),
        "verified_distinct_artifact_ids": len(artifacts_by_id),
        "duplicate_manifest_references": duplicate_refs,
        "unverifiable_artifact_references": unknown,
        "verified_attempt_groups": merged,
        "same_commit_but_distinct_run_pairs": repeated_shas,
        "no_paid_api": True, "main_modified": False,
        "limitations": [
            "Pinned projections of public GitHub REST results, not full HTTP JSON.",
            "No ZIP body or job log contents inspected.",
            "Distinct GitHub invocation IDs are not proof of independent scientific calculation.",
            "Known source documents are calibration fixtures, not an unseen holdout.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    result = resolve(json.loads(raw))
    result["source_snapshot_sha256"] = hash_raw(raw)
    content = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(content)
    print(json.dumps({
        "experiment": EXPERIMENT, "status": result["execution_grouping_status"],
        "attempt_groups": len(result["verified_attempt_groups"]),
        "artifact_ids": result["verified_distinct_artifact_ids"],
        "duplicate_refs": result["duplicate_manifest_references"],
        "scientific_independence": result["scientific_independence"],
        "report_sha256": hash_raw(content),
    },sort_keys=True))


if __name__=="__main__":
    main()
