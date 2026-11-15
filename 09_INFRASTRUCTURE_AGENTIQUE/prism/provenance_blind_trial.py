"""Read-only, frozen GitHub Actions log trial with a separately queried oracle.

The analyzer sees only raw log strings, not API run IDs. The evaluator
compares to GitHub's job/run associations *after* analysis. Never infer
causal independence from distinct run IDs.
"""
import hashlib
import json
import os
import sys
import urllib.request

from provenance_log_evidence import extract

# Precommitted before reading the corresponding job logs for this trial.
HELD_OUT = (
    (43721779828, 132835140939),
    (43720317522, 132830677717),
)


def fetch_json(url, token):
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch_log(url, token):
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def blind_analyze(logs):
    # The analyst has neither job nor run identifiers nor oracle labels.
    # It extracts only line-grounded evidence from the log body.
    return [extract(log, run_id="masked", job_id="masked") for log in logs]


def evaluate(observations, oracle):
    if len(observations) != len(oracle):
        raise ValueError("Oracle cardinality mismatch")
    # No group inference is attempted when explicit log evidence does not
    # prove the identity relation. This is a negative-control baseline.
    n = len(observations)
    pair_count = n * (n - 1) // 2
    same_run_pairs = sum(oracle[i]["run_id"] == oracle[j]["run_id"]
                         for i in range(n) for j in range(i + 1, n))
    return {
        "cases": n,
        "pairs": pair_count,
        "oracle_same_run_pairs": same_run_pairs,
        "predicted_same_run_pairs": 0,
        "abstentions": pair_count,
        "false_confirmations": 0,
        "log_hashes": [row["raw_log_sha256"] for row in observations],
        "log_observation_counts": [len(row["observations"]) for row in observations],
        "scientific_independence": "indéterminé",
        "limitations": "No blinded dependency reconstruction yet; no causal independence inference.",
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: provenance_blind_trial.py OWNER/REPO")
    token = os.environ["GH_TOKEN"]
    repo = sys.argv[1]
    logs, oracle = [], []
    for run_id, job_id in HELD_OUT:
        job = fetch_json(f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}", token)
        if job.get("run_id") != run_id or job.get("conclusion") != "success":
            raise RuntimeError("Holdout oracle mismatch or failed job")
        logs.append(fetch_log(f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs", token))
        oracle.append({"run_id": job["run_id"], "job_id": job["id"]})
    report = evaluate(blind_analyze(logs), oracle)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["false_confirmations"] != 0 or report["cases"] != len(HELD_OUT):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
