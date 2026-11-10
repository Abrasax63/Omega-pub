"""OpenAI Responses API usage adapter (no network calls).

Accepts an already-returned SDK response or mapping and converts only
provider-reported usage into the shared Omega telemetry contract.
"""
from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable

from telemetry import CONTEXT_FIELDS, SCHEMA_VERSION, TelemetryRecordError, validate_call_record


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        result = dump()
        if isinstance(result, dict):
            return result
    raise TypeError("response must be a mapping or expose model_dump()")


def build_openai_responses_record(
    response: Any,
    *,
    experiment_id: str,
    case_id: str,
    arm: str,
    call_id: str,
    started_at: str,
    elapsed_seconds: float,
    tool_calls: int | None = None,
    context: dict[str, Any] | None = None,
    result_validation_status: str = "not_assessed",
) -> dict[str, Any]:
    """Build one telemetry record from an OpenAI Responses API response."""
    if context is not None and (not isinstance(context, dict) or context.keys() - CONTEXT_FIELDS):
        raise TelemetryRecordError("invalid telemetry context fields")
    payload = _as_mapping(response)
    usage = payload.get("usage")
    if usage is not None and not isinstance(usage, dict):
        raise TelemetryRecordError("provider usage must be an object or null")
    usage = usage or {}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    details = usage.get("input_tokens_details")
    if details is not None and not isinstance(details, dict):
        raise TelemetryRecordError("input_tokens_details must be an object or null")
    cached_tokens = (details or {}).get("cached_tokens")
    reported = any(value is not None for value in (input_tokens, output_tokens, cached_tokens))
    provider_status = payload.get("status")
    status_map = {
        "completed": "completed", "failed": "failed", "incomplete": "interrupted",
        "cancelled": "interrupted", "queued": "pending", "in_progress": "pending",
    }
    if provider_status is not None and (
        not isinstance(provider_status, str) or provider_status not in status_map
    ):
        raise TelemetryRecordError("unrecognized provider response status")
    record = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": experiment_id,
        "case_id": case_id,
        "arm": arm,
        "call_id": call_id,
        "provider": "openai",
        "model": payload.get("model"),
        "model_version": None,
        "provider_response_id": payload.get("id"),
        "provider_request_id": getattr(response, "_request_id", None),
        "started_at": started_at,
        "elapsed_seconds": elapsed_seconds,
        "status": status_map.get(provider_status, "unknown"),
        "input_tokens": input_tokens if reported else None,
        "output_tokens": output_tokens if reported else None,
        "cached_input_tokens": cached_tokens if reported else None,
        "token_usage_source": "provider_response" if reported else "unavailable",
        "cost_usd": None,
        "cost_source": "unavailable",
        "tool_calls": tool_calls,
        "result_validation_status": result_validation_status,
        **(context or {}),
    }
    validate_call_record(record)
    return record


def measure_call(call: Callable[[], Any]) -> tuple[Any, str, float]:
    """Run a supplied callable and return (response, UTC start, elapsed seconds).

    This helper measures wall-clock duration only. It does not call a provider
    itself and deliberately leaves token extraction to the response adapter.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    started = perf_counter()
    response = call()
    elapsed = perf_counter() - started
    return response, started_at, elapsed
