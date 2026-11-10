"""Descriptive, case-paired analysis for Omega P5 ratings.

The blind key is supplied separately and only after ratings are frozen.
No significance tests, composite score, truth judgment, or certification is produced.
"""
from __future__ import annotations

import json
from hashlib import sha256
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from evaluation import DIMENSIONS, EvaluationRecordError, validate_dataset

ARMS = ("A", "B", "C")
COUNTS = ("unsupported_claims", "material_errors", "missed_counterexamples")


class AnalysisInputError(ValueError):
    """Raised when ratings or the separately held blind key are inconsistent."""


def _unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise AnalysisInputError("duplicate JSON member: " + name)
        result[name] = value
    return result


def _invalid_constant(value):
    raise AnalysisInputError("invalid JSON constant: " + value)


def _parse_json(data):
    return json.loads(data, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)


def load_jsonl(path: str | Path, *, expected_sha256: str | None = None) -> list[dict[str, Any]]:
    try:
        data = Path(path).read_bytes()
        if expected_sha256 is not None and sha256(data).hexdigest() != expected_sha256:
            raise AnalysisInputError("ratings SHA-256 does not match the frozen file")
        lines = data.decode("utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise AnalysisInputError("cannot read ratings file") from exc
    rows = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            raise AnalysisInputError("blank JSONL line at " + str(line_number))
        try:
            value = _parse_json(line)
        except (ValueError, RecursionError) as exc:
            raise AnalysisInputError("invalid JSON at line " + str(line_number)) from exc
        if not isinstance(value, dict):
            raise AnalysisInputError("line " + str(line_number) + " must be an object")
        rows.append(value)
    if not rows:
        raise AnalysisInputError("ratings file is empty")
    return rows


def load_blind_key(path: str | Path) -> list[dict[str, str]]:
    try:
        payload = _parse_json(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError) as exc:
        raise AnalysisInputError("cannot read blind key") from exc
    mappings = payload.get("mappings") if isinstance(payload, dict) and set(payload) == {"mappings"} else None
    if not isinstance(mappings, list):
        raise AnalysisInputError("blind key must contain a mappings array")
    return mappings


def _validate_blind_key(ratings, mappings, repetitions):
    if not isinstance(mappings, list):
        raise AnalysisInputError("blind key must be a list of mappings")
    expected = {(row["case_id"], row["blind_output_id"]) for row in ratings}
    result = {}
    for index, row in enumerate(mappings):
        if not isinstance(row, dict) or set(row) - {"repetition"} != {"case_id", "blind_output_id", "arm"}:
            raise AnalysisInputError("invalid blind-key mapping at index " + str(index))
        case_id, output_id, arm = row["case_id"], row["blind_output_id"], row["arm"]
        if not all(isinstance(x, str) and x.strip() for x in (case_id, output_id, arm)):
            raise AnalysisInputError("empty/non-string blind-key value")
        if arm not in ARMS:
            raise AnalysisInputError("invalid arm: " + str(arm))
        key = (case_id, output_id)
        if key in result:
            raise AnalysisInputError("duplicate blind-key mapping: " + str(key))
        repetition = row.get("repetition", 1 if repetitions == 1 else None)
        if type(repetition) is not int or not 1 <= repetition <= repetitions:
            raise AnalysisInputError("invalid or missing repetition")
        result[key] = (arm, repetition)
    if set(result) != expected:
        raise AnalysisInputError("blind-key coverage does not exactly match rated outputs")
    by_case = defaultdict(set)
    for (case_id, _), arm_repetition in result.items():
        if arm_repetition in by_case[case_id]:
            raise AnalysisInputError(case_id + ": an arm/repetition maps to multiple outputs")
        by_case[case_id].add(arm_repetition)
    for case_id, arms in by_case.items():
        if arms != {(arm, rep) for arm in ARMS for rep in range(1, repetitions + 1)}:
            raise AnalysisInputError(case_id + ": expected exactly A/B/C")
    return result


def _validate_ratings(ratings, expected_case_ids, repetitions):
    if type(repetitions) is not int or repetitions < 1:
        raise AnalysisInputError("repetitions must be a positive integer")
    try:
        return validate_dataset(
            ratings, expected_case_ids=expected_case_ids,
            expected_outputs_per_case=len(ARMS) * repetitions,
        )
    except EvaluationRecordError as exc:
        raise AnalysisInputError(str(exc)) from exc


def analyze_dataset(ratings, blind_key, *, expected_case_ids=None, repetitions=1):
    """Validate, unblind, and report descriptive case-paired comparisons."""
    validation = _validate_ratings(ratings, expected_case_ids, repetitions)
    mapping = _validate_blind_key(ratings, blind_key, repetitions)
    grouped = defaultdict(list)
    for row in ratings:
        grouped[(row["case_id"], mapping[(row["case_id"], row["blind_output_id"])][0])].append(row)

    case_ids = sorted({row["case_id"] for row in ratings})
    case_results = []
    for case_id in case_ids:
        for arm in ARMS:
            rows = grouped[(case_id, arm)]
            case_results.append({
                "case_id": case_id,
                "arm": arm,
                "evaluator_count": len({row["evaluator_id"] for row in rows}),
                "rating_count": len(rows),
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

    comparisons = []
    for candidate, reference in (("C", "A"), ("C", "B"), ("B", "A")):
        for dimension in DIMENSIONS:
            deltas = [
                mean(Fraction(row["scores"][dimension]) for row in grouped[(case_id, candidate)])
                - mean(Fraction(row["scores"][dimension]) for row in grouped[(case_id, reference)])
                for case_id in case_ids
            ]
            comparisons.append({
                "candidate": candidate,
                "reference": reference,
                "dimension": dimension,
                "paired_case_count": len(deltas),
                "mean_case_delta": float(mean(deltas)),
                "min_case_delta": float(min(deltas)),
                "max_case_delta": float(max(deltas)),
                "positive_cases": sum(delta > 0 for delta in deltas),
                "tie_cases": sum(delta == 0 for delta in deltas),
                "negative_cases": sum(delta < 0 for delta in deltas),
            })

    return {
        "analysis_version": "0.2.0",
        "repetitions_per_arm": repetitions,
        "status": "descriptive_exploratory_only",
        "validation": validation,
        "case_results": case_results,
        "paired_comparisons": comparisons,
        "limitations": [
            "No statistical significance or population-level inference is computed.",
            "No composite score or post-hoc weighting is used.",
            "Rater-reported error counts are descriptive, not ground truth.",
            "File analysis verifies the supplied ratings digest before reading the blind key.",
            "This tool cannot establish evaluator independence, blinding integrity, or scientific truth.",
        ],
    }


def analyze_files(
    ratings_path, blind_key_path, output_path, *,
    expected_case_ids, ratings_sha256, repetitions=1,
):
    if not expected_case_ids or not ratings_sha256:
        raise AnalysisInputError("the frozen case roster and ratings SHA-256 are required")
    # Use the same byte snapshot for digest verification and parsing.
    ratings = load_jsonl(ratings_path, expected_sha256=ratings_sha256)
    _validate_ratings(ratings, expected_case_ids, repetitions)
    destination = Path(output_path)
    for source in (Path(ratings_path), Path(blind_key_path)):
        if destination.resolve() == source.resolve() or (
            destination.exists() and source.exists() and destination.samefile(source)
        ):
            raise AnalysisInputError("output path aliases a protected input")
    blind_key = load_blind_key(blind_key_path)
    result = analyze_dataset(
        ratings, blind_key, expected_case_ids=expected_case_ids, repetitions=repetitions,
    )
    result["ratings_sha256"] = ratings_sha256
    Path(output_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
