"""Adapt GitHub Actions run/job metadata to the conservative provenance gate.

The input must be raw GitHub REST JSON snapshots, not hand-written verdicts.
This checks identity and successful completion only, NOT independence or logs.
"""
import argparse
import json
from pathlib import Path

from provenance_integration_gate import assess_evidence


def inspect(run, jobs):
    if not isinstance(jobs, dict) or not isinstance(jobs.get("jobs"), list):
        return {"verdict": "indéterminé", "reason": "missing_jobs"}
    if not run.get("id") or not run.get("head_sha") or not run.get("html_url"):
        return {"verdict": "indéterminé", "reason": "missing_run_identity"}
    evidence = []
    for job in jobs["jobs"]:
        if job.get("run_id") != run["id"] or not job.get("id"):
            return {"verdict": "indéterminé", "reason": "job_run_mismatch"}
        evidence.append({
            "run_id": str(run["id"]),
            "artifact_id": str(job["id"]),
            "source_uri": job.get("html_url") or run["html_url"],
            "verified_execution": (
                run.get("status") == "completed"
                and run.get("conclusion") == "success"
                and job.get("status") == "completed"
                and job.get("conclusion") == "success"
            ),
        })
    result = assess_evidence({"scientific_status": "INDÉTERMINÉ", "evidence": evidence})
    result["head_sha"] = run["head_sha"]
    result["job_count"] = len(evidence)
    result["limitation"] = "Job metadata alone cannot establish causal independence or inspect logs."
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_json", type=Path)
    parser.add_argument("jobs_json", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(json.loads(args.run_json.read_text()),
                             json.loads(args.jobs_json.read_text())),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
