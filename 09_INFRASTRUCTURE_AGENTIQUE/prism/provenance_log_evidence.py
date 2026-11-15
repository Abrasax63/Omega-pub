"""Extract conservative, line-addressed observations from GitHub Actions job logs.

This is a *reader*, not a proof of independent computation. It deliberately
does not treat workflow script echoes as executed commands or infer data lineage.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")
TIMESTAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z ")
CHECKOUT = re.compile(r"^HEAD is now at ([0-9a-f]{7,40})\b")
TESTS = re.compile(r"^Ran (\d+) tests? in ")
VERDICT = re.compile(r"^\{'Candidate alpha': 'recalcul', 'Candidate beta': 'copie'\}$")


def extract(raw, *, run_id, job_id, expected_sha=None):
    lines = raw.splitlines()
    observed = []
    for index, raw_line in enumerate(lines, 1):
        line = ANSI.sub("", TIMESTAMP.sub("", raw_line)).strip()
        match = CHECKOUT.match(line)
        if match:
            observed.append({"kind": "checkout", "value": match.group(1), "line": index})
        match = TESTS.match(line)
        if match:
            observed.append({"kind": "test_count", "value": int(match.group(1)), "line": index})
        if line == "OK":
            observed.append({"kind": "test_ok", "line": index})
        if VERDICT.fullmatch(line):
            observed.append({"kind": "candidate_verdict", "value": line, "line": index})
    checkouts = [e["value"] for e in observed if e["kind"] == "checkout"]
    sha_matches = (expected_sha is None or
                   bool(checkouts) and all(expected_sha.startswith(c) for c in checkouts))
    return {
        "run_id": str(run_id),
        "job_id": str(job_id),
        "raw_log_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "line_count": len(lines),
        "observations": observed,
        "expected_sha": expected_sha,
        "checkout_matches_expected": sha_matches if checkouts else None,
        "verdict": "indéterminé",
        "reason": "log_observations_do_not_prove_independent_reproduction",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--expected-sha")
    args = parser.parse_args()
    raw = args.log.read_text(encoding="utf-8")
    print(json.dumps(extract(raw, run_id=args.run_id, job_id=args.job_id,
                             expected_sha=args.expected_sha), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
