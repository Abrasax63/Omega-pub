"""Screen a preregistered EXTERNAL GitHub workflow cohort for log-evidence coverage.

This is an admission/screening step, NOT an origin classifier, provenance attestor,
or independent replication benchmark. Never turns missing logs into positive labels.
Opt-in --github reads public GitHub logs; without it, there is no network access.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from provenance_agent import GitHub

TIME_PREFIX = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
XTRACE = re.compile(r"^\+ (?:cp |install |python3? -c )")
SHA_LINE = re.compile(r"^[a-f0-9]{64}\s+\S.*$")


def screening(log):
    """Necessary condition only; matching output and producer is still unverified."""
    if not isinstance(log, str):
        raise TypeError("expected UTF-8 job log")
    lines = [TIME_PREFIX.sub("", line).strip() for line in log.splitlines()]
    writers = sum(bool(XTRACE.match(line)) for line in lines)
    digests = sum(bool(SHA_LINE.fullmatch(line)) for line in lines)
    return {
        "lines": len(lines),
        "xtrace_candidates": writers,
        "sha256_line_candidates": digests,
        "potentially_eligible": bool(writers and digests),
        "log_sha256": sha256(log.encode("utf-8")).hexdigest(),
        "interpretation": "SCREEN_ONLY_NOT_AN_ATTESTATION",
    }


def screen_cohort(cohort, loader):
    if not isinstance(cohort, list):
        raise ValueError("cohort must be a list")
    rows = []
    for item in cohort:
        repo, run_id = item["repo"], item["run_id"]
        if not isinstance(repo, str) or type(run_id) is not int:
            raise ValueError("bad repo/run")
        for job_id in item["job_ids"]:
            if type(job_id) is not int:
                raise ValueError("bad job id")
            try:
                summary = screening(loader(repo, job_id))
                rows.append({"repo": repo, "run_id": run_id, "job_id": job_id,
                             "status": "log_scanned", **summary})
            except (OSError, ValueError) as error:
                rows.append({"repo": repo, "run_id": run_id, "job_id": job_id,
                             "status": "log_unavailable", "reason": type(error).__name__})
    return {"jobs_requested": len(rows), "jobs_scanned": sum(x["status"] == "log_scanned" for x in rows),
            "candidate_evidence_jobs": sum(x.get("potentially_eligible", False) for x in rows),
            "benchmark_status": "INSUFFICIENT_INDEPENDENT_REFERENCE",
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--github", action="store_true", help="Opt in to read-only GitHub API calls")
    args = parser.parse_args()
    cohort = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not args.github:
        parser.error("No implicit network: add --github to read logs")
    sources = {}

    def read(repo, job_id):
        if repo not in sources:
            sources[repo] = GitHub(repo)
        return sources[repo].log(job_id)

    print(json.dumps(screen_cohort(cohort, read), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
