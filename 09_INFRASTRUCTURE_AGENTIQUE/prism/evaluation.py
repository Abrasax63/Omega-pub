"""Validate blinded human ratings for the Omega prism A/B/C evaluation.

This module validates records only. It does not grade answers, infer truth,
unblind arms, compute significance, or certify scientific claims.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

VERSION = "0.1.0"
DIMENSIONS = (
    "accuracy",
    "justification_sources",
    "falsification",
    "calibration",
    "traceability",
    "disagreement_preservation",
)
REQUIRED = {
    "case_id", "blind_output_id", "evaluator_id", "scores",
    "unsupported_claims", "material_errors", "missed_counterexamples",
    "elapsed_seconds", "tool_calls",
}


class EvaluationRecordError(ValueError):
    """Raised when a blinded evaluation record is incomplete or invalid."""


def validate_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise EvaluationRecordError("record must be an object")
    missing = REQUIRED - set(record)
    if missing:
        raise EvaluationRecordError("missing fields: " + ", ".join(sorted(missing)))
    for field in ("case_id", "blind_output_id", "evaluator_id"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise EvaluationRecordError(f"{field} must be a non-empty string")
    scores = record["scores"]
    if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
        raise EvaluationRecordError("scores must contain exactly the six rubric dimensions")
    for dimension, score in scores.items():
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 4:
            raise EvaluationRecordError(f"{dimension} score must be an integer from 0 to 4")
    for field in ("unsupported_claims", "material_errors", "missed_counterexamples", "tool_calls"):
        value = record[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise EvaluationRecordError(f"{field} must be a non-negative integer")
    elapsed = record["elapsed_seconds"]
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or elapsed < 0:
        raise EvaluationRecordError("elapsed_seconds must be a non-negative number")
    if "cost_usd" in record and record["cost_usd"] is not None:
        cost = record["cost_usd"]
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
            raise EvaluationRecordError("cost_usd must be null or a non-negative number")
    if "adjudication" in record:
        raise EvaluationRecordError("adjudication belongs in a separate post-rating record")


def validate_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(records, list) or not records:
        raise EvaluationRecordError("records must be a non-empty list")
    seen: set[tuple[str, str, str]] = set()
    by_case: dict[str, set[str]] = defaultdict(set)
    for index, record in enumerate(records):
        try:
            validate_record(record)
        except EvaluationRecordError as exc:
            raise EvaluationRecordError(f"record {index}: {exc}") from exc
        key = (record["case_id"], record["blind_output_id"], record["evaluator_id"])
        if key in seen:
            raise EvaluationRecordError(f"duplicate rating: {key}")
        seen.add(key)
        by_case[record["case_id"]].add(record["blind_output_id"])
    return {
        "valid": True,
        "record_count": len(records),
        "case_count": len(by_case),
        "blind_outputs_per_case": {
            case_id: len(output_ids) for case_id, output_ids in sorted(by_case.items())
        },
        "scoring": "human_ratings_only_no_automatic_truth_judgment",
    }
