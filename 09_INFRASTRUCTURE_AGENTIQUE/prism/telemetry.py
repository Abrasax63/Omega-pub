"""Validation and conservative aggregation of per-call P5 telemetry.

This module validates measurements supplied by an execution harness. It does
not call providers, infer missing usage, price tokens, measure host resources,
or certify scientific results.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
import math
import re
from typing import Any

VERSION = "0.2.0"
SCHEMA_VERSION = "omega.telemetry.call.v1"
ARMS = {"A", "B", "C"}
STATUSES = {"completed", "failed", "timeout", "interrupted", "pending", "unknown"}
TOKEN_SOURCES = {"provider_response", "provider_export", "unavailable"}
COST_SOURCES = {"provider_reported", "provider_export", "computed_from_rate_card", "unavailable"}
VALIDATION_STATUSES = {"not_assessed", "validated", "rejected", "indeterminate"}

REQUIRED = {
    "schema_version", "experiment_id", "case_id", "arm", "call_id",
    "provider", "model", "started_at", "elapsed_seconds", "status",
    "input_tokens", "output_tokens", "cached_input_tokens",
    "token_usage_source", "cost_usd", "cost_source", "tool_calls",
    "result_validation_status",
}
CONTEXT_FIELDS = {
    "repetition", "attempt", "operation_id", "requested_model", "model_version",
    "prompt_sha256", "prism_config_sha256", "code_commit", "routing_decision_sha256",
    "error_code", "cost_ref",
}
RESOURCE_FIELDS = ("cpu_seconds", "peak_memory_bytes", "io_read_bytes", "io_write_bytes")


class TelemetryRecordError(ValueError):
    """Raised when a telemetry record is incomplete or internally inconsistent."""


def _nonnegative_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and (isinstance(value, int) or math.isfinite(value))
        and value >= 0
    )


def _optional_count(record: dict[str, Any], field: str) -> int | None:
    value = record[field]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TelemetryRecordError(f"{field} must be null or a non-negative integer")
    return value


def validate_call_record(record: dict[str, Any]) -> None:
    """Validate one provider/tool call; missing measurements must remain null."""
    if not isinstance(record, dict):
        raise TelemetryRecordError("record must be an object")
    missing = REQUIRED - set(record)
    if missing:
        raise TelemetryRecordError("missing fields: " + ", ".join(sorted(missing)))
    if record["schema_version"] != SCHEMA_VERSION:
        raise TelemetryRecordError(f"schema_version must be {SCHEMA_VERSION}")

    for field in ("experiment_id", "case_id", "call_id", "provider", "model"):
        value = record[field]
        if field == "model" and value is None:
            continue
        if not isinstance(value, str) or not re.fullmatch(r"[^\s]+", value) or not value.isprintable():
            raise TelemetryRecordError(f"{field} must be a valid identifier")
    if not isinstance(record["arm"], str) or record["arm"] not in ARMS:
        raise TelemetryRecordError("arm must be A, B, or C")
    if not isinstance(record["status"], str) or record["status"] not in STATUSES:
        raise TelemetryRecordError(f"status must be one of {sorted(STATUSES)}")
    if not _nonnegative_number(record["elapsed_seconds"]):
        raise TelemetryRecordError("elapsed_seconds must be finite and non-negative")
    _optional_count(record, "tool_calls")
    for field in ("repetition", "attempt"):
        value = record.get(field)
        if value is not None and (type(value) is not int or value < 1):
            raise TelemetryRecordError(f"{field} must be a positive integer or null")
    if (record.get("operation_id") is None) != (record.get("attempt") is None):
        raise TelemetryRecordError("operation_id and attempt must be supplied together")
    for field in ("prompt_sha256", "prism_config_sha256", "routing_decision_sha256", "code_commit"):
        value = record.get(field)
        pattern = r"[0-9a-f]{40}|[0-9a-f]{64}" if field == "code_commit" else r"[0-9a-f]{64}"
        if value is not None and (not isinstance(value, str) or not re.fullmatch(pattern, value)):
            raise TelemetryRecordError(f"{field} must be a lowercase hexadecimal digest")

    started_at = record["started_at"]
    if not isinstance(started_at, str) or not started_at.strip():
        raise TelemetryRecordError("started_at must be a timezone-aware ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TelemetryRecordError("started_at must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TelemetryRecordError("started_at must include a timezone offset")

    if not isinstance(record["token_usage_source"], str) or record["token_usage_source"] not in TOKEN_SOURCES:
        raise TelemetryRecordError(f"token_usage_source must be one of {sorted(TOKEN_SOURCES)}")
    token_values = {field: _optional_count(record, field) for field in (
        "input_tokens", "output_tokens", "cached_input_tokens"
    )}
    if record["token_usage_source"] == "unavailable" and any(v is not None for v in token_values.values()):
        raise TelemetryRecordError("unavailable token usage must be represented by null counts")
    if record["token_usage_source"] != "unavailable" and (
        token_values["input_tokens"] is None or token_values["output_tokens"] is None
    ):
        raise TelemetryRecordError("reported token usage requires input_tokens and output_tokens")
    cached = token_values["cached_input_tokens"]
    if cached is not None and token_values["input_tokens"] is not None and cached > token_values["input_tokens"]:
        raise TelemetryRecordError("cached_input_tokens cannot exceed input_tokens")

    if not isinstance(record["cost_source"], str) or record["cost_source"] not in COST_SOURCES:
        raise TelemetryRecordError(f"cost_source must be one of {sorted(COST_SOURCES)}")
    cost = record["cost_usd"]
    if cost is not None and not _nonnegative_number(cost):
        raise TelemetryRecordError("cost_usd must be null or finite and non-negative")
    if (record["cost_source"] == "unavailable") != (cost is None):
        raise TelemetryRecordError("cost_usd must be null exactly when cost_source is unavailable")

    if record["cost_source"] == "computed_from_rate_card" and not record.get("cost_ref"):
        raise TelemetryRecordError("a computed cost requires a versioned rate-card reference")

    validation = record["result_validation_status"]
    if not isinstance(validation, str) or validation not in VALIDATION_STATUSES:
        raise TelemetryRecordError(f"result_validation_status must be one of {sorted(VALIDATION_STATUSES)}")
    for field in RESOURCE_FIELDS:
        if field in record and record[field] is not None:
            if not _nonnegative_number(record[field]):
                raise TelemetryRecordError(f"{field} must be null or finite and non-negative")
            if field.endswith("_bytes") and not isinstance(record[field], int):
                raise TelemetryRecordError(f"{field} must be an integer byte count")
    for field in ("provider_request_id", "provider_response_id", "validation_ref", "model_version",
                  "operation_id", "requested_model", "error_code", "cost_ref"):
        if field in record and record[field] is not None:
            if not isinstance(record[field], str) or not record[field].strip():
                raise TelemetryRecordError(f"{field} must be null or a non-empty string")


def summarize_calls(records: list[dict[str, Any]], *, by_execution: bool = False) -> dict[str, Any]:
    """Summarize per arm without treating missing measurements as zero."""
    if not isinstance(records, list) or not records:
        raise TelemetryRecordError("records must be a non-empty list")
    seen: set[tuple[str, str]] = set()
    attempts = set()
    grouped = defaultdict(list)
    for index, record in enumerate(records):
        try:
            validate_call_record(record)
        except TelemetryRecordError as exc:
            raise TelemetryRecordError(f"record {index}: {exc}") from exc
        key = (record["experiment_id"], record["call_id"])
        if key in seen:
            raise TelemetryRecordError(f"duplicate call identity: {key}")
        seen.add(key)
        group = (record["experiment_id"], record["arm"])
        execution = (record["case_id"], record.get("repetition") or 0)
        if record.get("attempt") is not None:
            attempt = (*group, *execution, record["operation_id"], record["attempt"])
            if attempt in attempts:
                raise TelemetryRecordError("duplicate operation attempt")
            attempts.add(attempt)
        grouped[(*group, *execution) if by_execution else group].append(record)

    summaries = []
    for group, rows in sorted(grouped.items()):
        experiment_id, arm = group[:2]
        rows.sort(key=lambda row: row["call_id"])
        def complete_sum(field: str) -> tuple[int | float | None, int]:
            values = [row.get(field) for row in rows]
            missing = sum(value is None for value in values)
            return (None if missing else sum(values), missing)

        tool_total, tool_missing = complete_sum("tool_calls")
        input_total, input_missing = complete_sum("input_tokens")
        output_total, output_missing = complete_sum("output_tokens")
        cached_total, cached_missing = complete_sum("cached_input_tokens")
        cost_total, cost_missing = complete_sum("cost_usd")
        cpu_total, cpu_missing = complete_sum("cpu_seconds")
        read_total, read_missing = complete_sum("io_read_bytes")
        write_total, write_missing = complete_sum("io_write_bytes")
        memory_values = [row.get("peak_memory_bytes") for row in rows]
        memory_missing = sum(value is None for value in memory_values)
        validation_counts = Counter(row["result_validation_status"] for row in rows)
        summaries.append({
            "experiment_id": experiment_id, "arm": arm, "call_count": len(rows),
            "elapsed_seconds_total": sum(row["elapsed_seconds"] for row in rows),
            "tool_calls_total": tool_total, "tool_calls_missing_calls": tool_missing,
            "status_counts": dict(sorted(Counter(row["status"] for row in rows).items())),
            "input_tokens_total": input_total, "input_tokens_missing_calls": input_missing,
            "output_tokens_total": output_total, "output_tokens_missing_calls": output_missing,
            "cached_input_tokens_total": cached_total, "cached_input_tokens_missing_calls": cached_missing,
            "cost_usd_total": cost_total, "cost_missing_calls": cost_missing,
            "cpu_seconds_total": cpu_total, "cpu_missing_calls": cpu_missing,
            "peak_memory_bytes_max": None if memory_missing else max(memory_values),
            "peak_memory_missing_calls": memory_missing,
            "io_read_bytes_total": read_total, "io_read_missing_calls": read_missing,
            "io_write_bytes_total": write_total, "io_write_missing_calls": write_missing,
            "result_validation_status_counts": dict(sorted(validation_counts.items())),
            "token_sources": dict(sorted(Counter(row["token_usage_source"] for row in rows).items())),
            "cost_sources": dict(sorted(Counter(row["cost_source"] for row in rows).items())),
        })
        if by_execution:
            summaries[-1].update(case_id=group[2], repetition=group[3] or None)
    key = "execution_summaries" if by_execution else "arm_summaries"
    return {"schema_version": SCHEMA_VERSION, key: summaries}
