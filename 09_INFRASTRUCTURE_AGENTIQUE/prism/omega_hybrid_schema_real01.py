"""One-shot *diagnostic* Qwen CPU run for two missing REAL-02 graph fields.

This uses the self-chosen concept and formal axioms from the archived
REAL-02 run (45119536096), NOT a fresh independent acquisition experiment.
No sources are reread, no oracle answers supplied, no model weights changed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from omega_hybrid_schema_retry import schema_retry

ARCHIVED_RUN = 45119536096
ARCHIVED_ARTIFACT = 14792897432
ARCHIVED_CANDIDATE_JSONL_SHA256 = (
    "04fe0bd95fdf92e390b94a1a7f2238f5134b85f0a488e3e0809f22e500db5137"
)
MODEL_SHA256 = "9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
# These values are copied from the model's own original REAL-02 card.
SOURCE_CARD_MINIMUM = {
    "concept": "Equivalence Relations",
    "formal_axioms": ["reflexive", "symmetric", "transitive"],
}


def examine(callback):
    before = dict(SOURCE_CARD_MINIMUM)
    result = schema_retry(before, callback)
    return {
        "experiment": "OMEGA-HYBRID-SCHEMA-REAL-01",
        "evidence_source_run": ARCHIVED_RUN,
        "evidence_artifact": ARCHIVED_ARTIFACT,
        "evidence_candidate_jsonl_sha256": ARCHIVED_CANDIDATE_JSONL_SHA256,
        "model_weights_sha256_required": MODEL_SHA256,
        "original_model_card_fields_reused": sorted(before.keys()),
        "original_two_graph_fields_missing": True,
        "source_semantic_fidelity_certified": False,
        "exposed_previous_case_not_a_holdout": True,
        "benchmark_of_new_competence": False,
        "model_weights_updated": False,
        "scientific_claims_certified": 0,
        "schema_repair": result,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server", default="http://127.0.0.1:8080")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    from real_abstraction_trial import RealClient
    client = RealClient(args.server)
    try:
        report = examine(client)
    except Exception as exc:
        # Never claim a scientific result after an unhandled problem.
        report = {"experiment": "OMEGA-HYBRID-SCHEMA-REAL-01",
                  "status": "RUNNER_FAILURE", "error_type": type(exc).__name__,
                  "scientific_claims_certified": 0}
    report["actual_model_calls"] = client.calls
    report["model_call_count"] = len(client.calls)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({"model_call_count":report["model_call_count"],
                      "schema_retry_status":report.get("schema_repair",{}).get("status"),
                      "schema_retry_reason":report.get("schema_repair",{}).get("reason"),
                      "scientific_claims_certified":0}))
    if report.get("status") == "RUNNER_FAILURE" or report["model_call_count"] > 1:
        raise SystemExit("EXPERIMENT_RUNNER_FAILED_CLOSED")


if __name__ == "__main__":
    main()
