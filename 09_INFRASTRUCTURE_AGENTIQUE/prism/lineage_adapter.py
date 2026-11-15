"""Offline bridge from Omega JournalBundle to a conservative lineage pilot.

No HTTP requests, code execution, scientific certification, or mutation.
The GitHub job identities and raw logs are assertions of the input snapshot;
this adapter DOES NOT authenticate the snapshot or prevent forged traces.
"""
from __future__ import annotations

import re
import shlex

from provenance_agent import JournalBundle
from provenance_selection import Piece, select_verdict
from provenance_xtrace import extract, fixed_verdict
from lineage_pilot import UNKNOWN, DISTINCT, assess

STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
DIGEST = re.compile(r"([a-f0-9]{64})\s+(.+)")


def digest_from_log(log, path):
    """Require a unique non-conflicting checksum printed for the exact path."""
    hashes = set()
    for line in log.splitlines():
        match = DIGEST.fullmatch(STAMP.sub("", line).strip())
        if match and match[2] == path:
            hashes.add(match[1])
    return next(iter(hashes)) if len(hashes) == 1 else None


def source_of_copy(command, destination):
    """Extract only the two audited cp/install argv shapes from xtrace."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return None
    if len(argv) == 3 and argv[0] == "cp" and argv[2] == destination:
        return argv[1] if not argv[1].startswith("-") else None
    if (len(argv) == 5 and argv[:2] == ["install", "-m"]
            and re.fullmatch(r"[0-7]{3,4}", argv[2]) and argv[4] == destination):
        return argv[3] if not argv[3].startswith("-") else None
    return None


def compare_pair(snapshot, pair, *, budget=2):
    """Compare with Omega's existing selection, at identical raw job-log reads.

    pair: [{"job_id": integer, "path": "exact/relative/path"}, ...] of size 2.
    One job log = one charged read. Intra-job parent lookups reuse that log.
    Existing selection answers copy/recompute, not lineage: its *conservative*
    translation can only call two matching recomputations distinct.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("invalid budget")
    if not isinstance(pair, list) or len(pair) != 2 or not all(
        isinstance(x, dict) and type(x.get("job_id")) is int
        and isinstance(x.get("path"), str) and x["path"]
        for x in pair
    ):
        raise ValueError("two (job_id, path) outputs required")
    reads = list(dict.fromkeys(x["job_id"] for x in pair))
    report = {"lineage": UNKNOWN, "selector_translation": UNKNOWN,
              "reads_charged_each": len(reads) if len(reads) <= budget else 0,
              "requested_reads": len(reads), "same_log_budget": True,
              "provenance_status": "DECLARED_SNAPSHOT_NOT_AUTHENTICATED",
              "limitations": "selector recognizes copy/recompute, not proof independence"}
    if len(reads) > budget:
        report["reason"] = "budget_exceeded"
        return report
    if not isinstance(snapshot, dict) or type(snapshot.get("run")) is not int:
        report["reason"] = "invalid_snapshot"
        return report
    try:
        # Reuse the actual read-only collector's snapshot validation.
        source = JournalBundle(snapshot, snapshot["repository"], snapshot["run"])
        jobs = {job["id"]: job for job in source.jobs(snapshot["run"])}
        if any(i not in jobs or jobs[i].get("conclusion") != "success" for i in reads):
            raise ValueError("unverified or unsuccessful job")
        logs = {i: source.log(i) for i in reads}
    except (KeyError, TypeError, ValueError, OSError) as exc:
        report["reason"] = type(exc).__name__ + ": " + str(exc)
        return report

    def describe(job_id, path):
        log = logs[job_id]
        evidence = extract(log, path)
        operation = fixed_verdict(evidence)
        return evidence, operation, digest_from_log(log, path)

    # Existing Omega selector; same log snapshot, same raw job-log read set.
    operations, hashes = [], []
    for job_id, path in [(x["job_id"], x["path"]) for x in pair]:
        evidence, operation, digest = describe(job_id, path)
        piece = Piece(name=str(job_id), kind="execution", job=str(job_id), output=path)
        chosen = select_verdict(
            [piece],
            lambda _: {"job": str(job_id), "output": path,
                       "complete": evidence["complete"], "success": True,
                       "operation": operation},
            job=str(job_id), output=path, budget=1,
        )
        operations.append(chosen["verdict"])
        hashes.append(digest)
    if all(op == "recalcul" for op in operations) and hashes[0] and hashes[0] == hashes[1]:
        report["selector_translation"] = DISTINCT

    nodes, active = {}, set()

    def materialize(job_id, path):
        label = f"job:{job_id}:{path}"
        if label in nodes:
            return label
        if label in active:
            raise ValueError("cyclic lineage")
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError("unsafe path")
        active.add(label)
        try:
            evidence, operation, checksum = describe(job_id, path)
            if not evidence["complete"] or len(evidence["writers"]) != 1 or not checksum:
                raise ValueError("incomplete output evidence")
            command = evidence["writers"][0]["command"]
            if operation == "recalcul":
                node = {"id": label, "kind": "recompute", "parents": [],
                        "run_id": label, "result_digest": checksum, "attested": True}
            elif operation == "copie":
                parent_path = source_of_copy(command, path)
                if not parent_path or parent_path == path:
                    raise ValueError("unresolvable source")
                parent_id = materialize(job_id, parent_path)
                if nodes[parent_id]["result_digest"] != checksum:
                    raise ValueError("copy checksum differs from parent")
                node = {"id": label, "kind": "copy", "parents": [parent_id],
                        "run_id": label, "result_digest": checksum, "attested": True}
            else:
                raise ValueError("unknown writer or multi-writer")
            # attested=True here means syntax-checked *declared log*, NOT source trust.
            nodes[label] = node
            return label
        finally:
            active.remove(label)

    try:
        out = [materialize(x["job_id"], x["path"]) for x in pair]
        report["lineage"] = assess({"nodes": list(nodes.values()), "outputs": out})
    except (ValueError, RecursionError) as exc:
        report["reason"] = str(exc)
    return report


def main():
    """Replay supplied evidence offline; no network or asynchronous jobs."""
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='Existing JournalBundle JSON with jobs and logs')
    parser.add_argument('pairs', type=Path, help='List of {case_id, outputs:[{job_id,path},...] }')
    parser.add_argument('--budget', type=int, default=2, help='Maximum distinct job logs per pair')
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    pairs = json.loads(args.pairs.read_text(encoding='utf-8'))
    if not isinstance(pairs, list):
        parser.error('pairs must be a list')
    rows = [dict(case_id=item['case_id'], **compare_pair(snapshot, item['outputs'], budget=args.budget))
            for item in pairs]
    print(json.dumps({'rows': rows, 'scientific_status': 'NOT_CERTIFIED',
                      'provenance_status': 'DECLARED_SNAPSHOT_NOT_AUTHENTICATED'},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
