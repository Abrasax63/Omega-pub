"""Validate completeness and numeric integrity of blinded Omega P5 ratings.

This validator checks structure only. It does not grade answers, infer truth,
unblind arms, compute significance, or certify scientific claims.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

VERSION = "0.2.0"
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


def _finite_nonnegative_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
        and value >= 0
    )


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
    if not _finite_nonnegative_number(record["elapsed_seconds"]):
        raise EvaluationRecordError("elapsed_seconds must be a finite non-negative number")
    if "cost_usd" in record and record["cost_usd"] is not None:
        if not _finite_nonnegative_number(record["cost_usd"]):
            raise EvaluationRecordError("cost_usd must be null or a finite non-negative number")
    if "adjudication" in record:
        raise EvaluationRecordError("adjudication belongs in a separate post-rating record")


def validate_dataset(
    records: list[dict[str, Any]],
    *,
    expected_case_ids: set[str] | None = None,
    expected_outputs_per_case: int = 3,
    minimum_evaluators: int = 2,
) -> dict[str, Any]:
    """Require complete A/B/C-blind-output coverage and balanced independent raters.

    blind_output_id values remain opaque: this function never maps them to A/B/C.
    Each evaluator must rate every blind output for a given case.
    """
    if not isinstance(records, list) or not records:
        raise EvaluationRecordError("records must be a non-empty list")
    if expected_outputs_per_case < 1 or minimum_evaluators < 2:
        raise EvaluationRecordError("expected_outputs_per_case must be >=1 and minimum_evaluators >=2")

    seen: set[tuple[str, str, str]] = set()
    by_case: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for index, record in enumerate(records):
        try:
            validate_record(record)
        except EvaluationRecordError as exc:
            raise EvaluationRecordError(f"record {index}: {exc}") from exc
        key = (record["case_id"], record["blind_output_id"], record["evaluator_id"])
        if key in seen:
            raise EvaluationRecordError(f"duplicate rating: {key}")
        seen.add(key)
        by_case[record["case_id"]][record["blind_output_id"]].add(record["evaluator_id"])

    actual_cases = set(by_case)
    if expected_case_ids is not None and actual_cases != expected_case_ids:
        missing = sorted(expected_case_ids - actual_cases)
        unexpected = sorted(actual_cases - expected_case_ids)
        raise EvaluationRecordError(f"case coverage mismatch; missing={missing}, unexpected={unexpected}")

    outputs_per_case: dict[str, int] = {}
    evaluators_per_case: dict[str, int] = {}
    for case_id, outputs in sorted(by_case.items()):
        if len(outputs) != expected_outputs_per_case:
            raise EvaluationRecordError(
                f"{case_id}: expected {expected_outputs_per_case} blind outputs, got {len(outputs)}"
            )
        evaluator_sets = list(outputs.values())
        common = set.intersection(*evaluator_sets)
        union = set.union(*evaluator_sets)
        if len(common) < minimum_evaluators:
            raise EvaluationRecordError(
                f"{case_id}: at least {minimum_evaluators} evaluators must rate every output"
            )
        if common != union:
            raise EvaluationRecordError(
                f"{case_id}: evaluator coverage is unbalanced across blind outputs"
            )
        outputs_per_case[case_id] = len(outputs)
        evaluators_per_case[case_id] = len(common)

    return {
        "valid": True,
        "record_count": len(records),
        "case_count": len(by_case),
        "blind_outputs_per_case": outputs_per_case,
        "complete_evaluators_per_case": evaluators_per_case,
        "scoring": "human_ratings_only_no_automatic_truth_judgment",
    }
