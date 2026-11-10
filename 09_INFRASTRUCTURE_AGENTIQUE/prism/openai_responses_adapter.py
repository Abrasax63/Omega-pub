"""OpenAI Responses API usage adapter (no network calls).

Accepts an already-returned SDK response or mapping and converts only
provider-reported usage into the shared Omega telemetry contract.
"""
from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable

from telemetry import SCHEMA_VERSION, validate_call_record


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
    tool_calls: int = 0,
    result_validation_status: str = "not_assessed",
) -> dict[str, Any]:
    """Build one telemetry record from an OpenAI Responses API response."""
    payload = _as_mapping(response)
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        usage = {}

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    details = usage.get("input_tokens_details")
    cached_tokens = details.get("cached_tokens") if isinstance(details, dict) else None

    reported = (
        isinstance(input_tokens, int) and not isinstance(input_tokens, bool)
        and isinstance(output_tokens, int) and not isinstance(output_tokens, bool)
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": experiment_id,
        "case_id": case_id,
        "arm": arm,
        "call_id": call_id,
        "provider": "openai",
        "model": payload.get("model") or "unknown",
        "model_version": None,
        "provider_request_id": payload.get("id"),
        "started_at": started_at,
        "elapsed_seconds": elapsed_seconds,
        "status": "completed",
        "input_tokens": input_tokens if reported else None,
        "output_tokens": output_tokens if reported else None,
        "cached_input_tokens": cached_tokens if reported else None,
        "token_usage_source": "provider_response" if reported else "unavailable",
        "cost_usd": None,
        "cost_source": "unavailable",
        "tool_calls": tool_calls,
        "result_validation_status": result_validation_status,
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
