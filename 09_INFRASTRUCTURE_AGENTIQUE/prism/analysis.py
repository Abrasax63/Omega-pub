"""Descriptive, case-paired analysis for Omega P5 ratings.

The blind key is supplied separately and only after ratings are frozen.
No significance tests, composite score, truth judgment, or certification is produced.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from evaluation import DIMENSIONS, EvaluationRecordError, validate_dataset

ARMS = ("A", "B", "C")
COUNTS = ("unsupported_claims", "material_errors", "missed_counterexamples")


class AnalysisInputError(ValueError):
    """Raised when ratings or the separately held blind key are inconsistent."""


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                raise AnalysisInputError("blank JSONL line at " + str(line_number))
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AnalysisInputError("invalid JSON at line " + str(line_number)) from exc
            if not isinstance(value, dict):
                raise AnalysisInputError("line " + str(line_number) + " must be an object")
            rows.append(value)
    if not rows:
        raise AnalysisInputError("ratings file is empty")
    return rows


def load_blind_key(path: str | Path) -> list[dict[str, str]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisInputError("cannot read blind key") from exc
    mappings = payload.get("mappings") if isinstance(payload, dict) else None
    if not isinstance(mappings, list):
        raise AnalysisInputError("blind key must contain a mappings array")
    return mappings


def _validate_blind_key(ratings, mappings):
    expected = {(row["case_id"], row["blind_output_id"]) for row in ratings}
    result = {}
    for index, row in enumerate(mappings):
        if not isinstance(row, dict) or set(row) != {"case_id", "blind_output_id", "arm"}:
            raise AnalysisInputError("invalid blind-key mapping at index " + str(index))
        case_id, output_id, arm = row["case_id"], row["blind_output_id"], row["arm"]
        if not all(isinstance(x, str) and x.strip() for x in (case_id, output_id, arm)):
            raise AnalysisInputError("empty/non-string blind-key value")
        if arm not in ARMS:
            raise AnalysisInputError("invalid arm: " + str(arm))
        key = (case_id, output_id)
        if key in result:
            raise AnalysisInputError("duplicate blind-key mapping: " + str(key))
        result[key] = arm
    if set(result) != expected:
        raise AnalysisInputError("blind-key coverage does not exactly match rated outputs")
    by_case = defaultdict(set)
    for (case_id, _), arm in result.items():
        if arm in by_case[case_id]:
            raise AnalysisInputError(case_id + ": an arm maps to multiple outputs")
        by_case[case_id].add(arm)
    for case_id, arms in by_case.items():
        if arms != set(ARMS):
            raise AnalysisInputError(case_id + ": expected exactly A/B/C")
    return result


def analyze_dataset(ratings, blind_key, *, expected_case_ids=None):
    """Validate, unblind, and report descriptive case-paired comparisons."""
    try:
        validation = validate_dataset(ratings, expected_case_ids=expected_case_ids)
    except EvaluationRecordError as exc:
        raise AnalysisInputError(str(exc)) from exc
    mapping = _validate_blind_key(ratings, blind_key)
    grouped = defaultdict(list)
    for row in ratings:
        grouped[(row["case_id"], mapping[(row["case_id"], row["blind_output_id"])])].append(row)

    case_ids = sorted({row["case_id"] for row in ratings})
    case_results = []
    for case_id in case_ids:
        for arm in ARMS:
            rows = grouped[(case_id, arm)]
            case_results.append({
                "case_id": case_id,
                "arm": arm,
                "evaluator_count": len(rows),
                "dimension_means": {
                    dim: mean(row["scores"][dim] for row in rows) for dim in DIMENSIONS
                },
                "dimension_ranges": {
                    dim: {
                        "min": min(row["scores"][dim] for row in rows),
                        "max": max(row["scores"][dim] for row in rows),
                    } for dim in DIMENSIONS
                },
                "rater_reported_count_means": {
                    field: mean(row[field] for row in rows) for field in COUNTS
                },
                "rater_disagreement": {
                    dim: max(row["scores"][dim] for row in rows)
                    - min(row["scores"][dim] for row in rows)
                    for dim in DIMENSIONS
                },
            })

    by_case_arm = {(row["case_id"], row["arm"]): row for row in case_results}
    comparisons = []
    for candidate, reference in (("C", "A"), ("C", "B"), ("B", "A")):
        for dimension in DIMENSIONS:
            deltas = [
                by_case_arm[(case_id, candidate)]["dimension_means"][dimension]
                - by_case_arm[(case_id, reference)]["dimension_means"][dimension]
                for case_id in case_ids
            ]
            comparisons.append({
                "candidate": candidate,
                "reference": reference,
                "dimension": dimension,
                "paired_case_count": len(deltas),
                "mean_case_delta": mean(deltas),
                "min_case_delta": min(deltas),
                "max_case_delta": max(deltas),
                "positive_cases": sum(delta > 0 for delta in deltas),
                "tie_cases": sum(delta == 0 for delta in deltas),
                "negative_cases": sum(delta < 0 for delta in deltas),
            })

    return {
        "analysis_version": "0.1.0",
        "status": "descriptive_exploratory_only",
        "validation": validation,
        "case_results": case_results,
        "paired_comparisons": comparisons,
        "limitations": [
            "No statistical significance or population-level inference is computed.",
            "No composite score or post-hoc weighting is used.",
            "Rater-reported error counts are descriptive, not ground truth.",
            "The blind key is applied only after ratings are frozen.",
            "This tool cannot establish evaluator independence, blinding integrity, or scientific truth.",
        ],
    }


def analyze_files(ratings_path, blind_key_path, output_path, *, expected_case_ids=None):
    result = analyze_dataset(
        load_jsonl(ratings_path),
        load_blind_key(blind_key_path),
        expected_case_ids=expected_case_ids,
    )
    Path(output_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
