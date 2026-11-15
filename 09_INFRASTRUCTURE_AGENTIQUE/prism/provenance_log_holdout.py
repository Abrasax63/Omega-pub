"""Blind-ish evaluation of previously unseen GitHub Actions logs.

Evidence inputs are raw job logs and GitHub API run/job identities. The
independent oracle is the API run/job relationship, NOT a supplied label.
The checker does not assume that two runs are causally independent.
"""
import argparse
import json
from pathlib import Path

from provenance_log_evidence import extract


def evaluate(entries):
    observations = []
    for entry in entries:
        log = entry["log"]
        result = extract(log, run_id=entry["run_id"], job_id=entry["job_id"],
                         expected_sha=entry.get("checkout_sha"))
        observations.append(result)
    run_ids = [item["run_id"] for item in observations]
    return {
        "jobs": len(observations),
        "distinct_run_ids": len(set(run_ids)),
        "same_run_pairs": sum(run_ids[i] == run_ids[j]
                              for i in range(len(run_ids))
                              for j in range(i + 1, len(run_ids))),
        "log_sha256": [item["raw_log_sha256"] for item in observations],
        "checkout_matches": [item["checkout_matches_expected"] for item in observations],
        "observations": observations,
        "independent_reproductions": "indéterminé",
        "reason": "API run IDs and logs do not prove causal independence",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path, help="JSON with log file paths and API identities")
    args = parser.parse_args()
    rows = json.loads(args.manifest.read_text(encoding="utf-8"))
    for row in rows:
        row["log"] = Path(row.pop("log_file")).read_text(encoding="utf-8")
    print(json.dumps(evaluate(rows), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
