"""Auditable raw-log transfer probe. No external actions, no API, no promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from provenance_cycle import predict, program_fingerprint
from provenance_lab import UNKNOWN, load, read_program
from provenance_xtrace import extract, extract_buildkit_copy, fixed_verdict

# Job IDs, targets and sample membership were frozen before reading the B logs.
# Hashes below are SHA256 of decoded GitHub connector text re-encoded as UTF-8.
COHORT_B = {
    "C3": ("curl/curl", 132705913199, "source.tar.gz", "75f232165ae3490fed42650e3e1f8cd0b64dac6c517b1a45bbbd86add08c3722"),
    "C4": ("curl/curl", 132705914296, "src/curl", "b61b073c9b72a7eafadcd308e703b7a2c494bef2a72122273ca3b3f088fa5e1e"),
    "D3": ("docker/build-push-action", 132413316807, "localhost:5000/name/app:latest", "bb7d09877f44e036503e014480673bff3098ca4f18bf876dadf1fa1dc7e06467"),
    "D4": ("docker/build-push-action", 132413316717, "/tmp/buildx-build", "d7e0f403529cdb0d69462f657eb5eb538992c229c1e45bb90c3c1a5033c5818d"),
}


def inspect(log: str, output: str, proposal: dict, baseline: dict) -> dict:
    """Compare unchanged extractors on exactly the same full job text.

    A positive parser 'complete' indicates only local extractor completeness;
    it cannot establish global uniqueness of file writers.
    """
    candidates = [extract(log, output), extract_buildkit_copy(log, output)]
    usable = [p for p in candidates if p.get("complete") is True]
    if len(usable) > 1 and usable[0]["writers"] != usable[1]["writers"]:
        return {"learned": UNKNOWN, "fixed": UNKNOWN, "parser": "conflict"}
    if not usable:
        return {"learned": UNKNOWN, "fixed": UNKNOWN, "parser": "unsupported"}
    case = usable[0]
    return {
        "learned": predict(case, baseline, proposal),
        "fixed": fixed_verdict(case),
        "parser": "bash" if usable[0] is candidates[0] else "buildkit",
    }


def run(root: Path, proposal_file: Path, baseline_file: Path) -> dict:
    proposal = load(proposal_file)
    baseline = read_program(baseline_file)
    if program_fingerprint(baseline) != proposal["baseline_fingerprint"]:
        raise ValueError("Frozen baseline mismatch")
    rows = []
    for case_id, (repo, job_id, output, sha) in COHORT_B.items():
        raw = (root / f"{case_id}.log").read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f"{case_id}: downloaded log differs from frozen UTF-8 snapshot")
        log = raw.decode("utf-8")
        verdicts = inspect(log, output, proposal, baseline)
        rows.append({"id": case_id, "repo": repo, "job_id": job_id,
                     "output": output, "sha256_raw": sha,
                     "pieces_read_each": 1, **verdicts})
    return {"scope": "raw-log parser coverage only; independent oracle pending",
            "candidate_sha256": hashlib.sha256(proposal_file.read_bytes()).hexdigest(),
            "cases": rows,
            "determinate_learned": sum(row["learned"] != UNKNOWN for row in rows),
            "determinate_fixed": sum(row["fixed"] != UNKNOWN for row in rows),
            "promotion_allowed": False}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("logdir", type=Path)
    p.add_argument("proposal", type=Path)
    p.add_argument("baseline", type=Path)
    args = p.parse_args()
    print(json.dumps(run(args.logdir, args.proposal, args.baseline), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
