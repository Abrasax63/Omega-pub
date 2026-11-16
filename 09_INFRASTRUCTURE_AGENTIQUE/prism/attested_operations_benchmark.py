"""Controlled prospective provenance intervention, precommitted four-case oracle.

Run this only with real GitHub Actions-generated evidence and a genuine Sigstore
bundle. Predictions are computed BEFORE the pre-registered labels are consulted.
NOT an independent external scientific holdout; these are built-by-us cases.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from attested_evidence_bridge import select_with_attested_artifact
from lineage_adapter import digest_from_log
from provenance_selection import Piece, select_verdict
from provenance_xtrace import extract, fixed_verdict
from slsa_attestation_pilot import file_sha256

UNKNOWN = "indéterminé"


def predict_case(raw_log, artifact, output, *, bundle, trusted_root,
                 repository, repository_id, signer_workflow, source_commit,
                 verifier=None):
    """Return two comparable copy/recompute predictions and separate trust costs."""
    artifact = Path(artifact)
    job = "controlled-builder"
    label = "raw-production-xtrace"
    xtrace = extract(raw_log, output)
    operation = fixed_verdict(xtrace)
    stated_digest = digest_from_log(raw_log, output)
    record = {
        "job": job, "output": output,
        "complete": xtrace["complete"], "success": True,
        "operation": operation, "artifact_sha256": stated_digest,
    }
    pieces = [Piece(label, "execution", job, output)]
    # The reference uses precisely one shared raw log observation.
    baseline = select_verdict(pieces, lambda _: record,
                              job=job, output=output, budget=1)
    # This is the same existing selector plus a separately charged signature
    # verification. No attempt to recategorize untraced writers.
    candidate = select_with_attested_artifact(
        pieces, lambda _: record, job=job, output=output, budget=1,
        artifact=artifact, bundle=bundle, trusted_root=trusted_root,
        repository=repository, repository_id=repository_id,
        signer_workflow=signer_workflow, source_commit=source_commit,
        verifier=verifier,
    )
    return {
        "output": output,
        "artifact_sha256": file_sha256(artifact),
        "hash_matches_raw_log": stated_digest == file_sha256(artifact),
        "parser_observed_writer": xtrace["complete"],
        "baseline_label": baseline["verdict"],
        "baseline_log_reads": len(baseline["pieces_lues"]),
        "candidate_label": candidate["operation_from_untrusted_log"],
        "candidate_log_reads": candidate["log_read_count"],
        "candidate_signature_checks": candidate["signature_verification_attempts"],
        "build_provenance": candidate["signed_build_provenance"],
        "scientific_verdict": candidate["scientific_verdict"],
        "routing": candidate["routing"],
    }


def score_predictions(predictions, frozen_manifest):
    """Apply frozen controlled labels AFTER all predictions have been produced."""
    if not isinstance(frozen_manifest, dict) or frozen_manifest.get("version") != 1:
        raise ValueError("unexpected frozen manifest version")
    cases = frozen_manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != 4:
        raise ValueError("expected exactly four preregistered interventions")
    by_path = {c["file"]: c for c in cases}
    if len(by_path) != len(cases) or set(by_path) != {p["output"] for p in predictions}:
        raise ValueError("case mismatch: fail closed")
    rows = []
    for p in predictions:
        expected = by_path[p["output"]]["expected"]
        rows.append({**p, "case_id": by_path[p["output"]]["id"],
                     "expected_operation_from_precommitted_plan": expected,
                     "baseline_correct": p["baseline_label"] == expected,
                     "candidate_correct": p["candidate_label"] == expected})
    correct_baseline = sum(int(x["baseline_correct"]) for x in rows)
    correct_candidate = sum(int(x["candidate_correct"]) for x in rows)
    return {
        "scope": "CONTROLLED_CONSTRUCTED_ACTUAL_GITHUB_EXECUTION_NOT_EXTERNAL_HOLDOUT",
        "status": "TECHNICAL_INTEGRATION_REPLAY",
        "total": len(rows),
        "baseline_correct": correct_baseline,
        "candidate_correct": correct_candidate,
        "baseline_abstentions": sum(x["baseline_label"] == UNKNOWN for x in rows),
        "candidate_abstentions": sum(x["candidate_label"] == UNKNOWN for x in rows),
        "candidate_verified_signatures": sum(
            x["build_provenance"] == "VERIFIED_BUILD_ONLY" for x in rows
        ),
        "baseline_log_reads": sum(x["baseline_log_reads"] for x in rows),
        "candidate_log_reads": sum(x["candidate_log_reads"] for x in rows),
        "candidate_signature_checks": sum(x["candidate_signature_checks"] for x in rows),
        "scientific_certifications": sum(
            x["scientific_verdict"] != "INDETERMINATE" for x in rows
        ),
        "hash_mismatches": sum(not x["hash_matches_raw_log"] for x in rows),
        "scientific_gain_demonstrated": False,
        "selection_accuracy_gain": correct_candidate - correct_baseline,
        "oracle_independence": "NOT_ESTABLISHED_CONTROLLED_PLAN_ONLY",
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--signer-workflow", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # The outputs are read only from fixed paths; expected labels are not passed
    # to the classifier. Manifest labels enter *only* in score_predictions.
    frozen = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected_paths = [x["file"] for x in frozen["cases"]]
    raw_log = args.log.read_text(encoding="utf-8")
    predictions = [
        predict_case(raw_log, Path(path), path, bundle=args.bundle,
                     trusted_root=args.trusted_root, repository=args.repo,
                     repository_id=args.repo_id,
                     signer_workflow=args.signer_workflow,
                     source_commit=args.commit)
        for path in expected_paths
    ]
    report = score_predictions(predictions, frozen)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # A negative result is valid. Fail only on broken experimental integrity.
    integrity_ok = (
        report["total"] == 4 and report["candidate_verified_signatures"] == 4
        and report["scientific_certifications"] == 0
        and report["candidate_log_reads"] == report["baseline_log_reads"] == 4
        and report["hash_mismatches"] == 0
    )
    return 0 if integrity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
