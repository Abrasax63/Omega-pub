"""Append-only, hash-chained event ledger for the Omega adaptive prism P4.

The ledger stores provenance metadata and hashes, not mission text, context
documents, or perspective output bodies. It is an activity log, not scientific
memory and not a certification mechanism.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
GENESIS = "0" * 64
EVENT_TYPES = {
    "mission_planned",
    "context_prepared",
    "perspective_recorded",
    "execution_closed",
}


class EventLedgerError(ValueError):
    """Raised when an event or append-only ledger violates the P4 contract."""


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _event_hash(event: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in event.items() if key != "event_hash"}
    return content_hash(unsigned)


def build_event(event_type: str, payload: dict[str, Any], *, previous_hash: str = GENESIS) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise EventLedgerError(f"unsupported event_type: {event_type}")
    if not isinstance(payload, dict):
        raise EventLedgerError("payload must be an object")
    if not isinstance(previous_hash, str) or len(previous_hash) != 64:
        raise EventLedgerError("previous_hash must be a SHA-256 hex digest")
    try:
        int(previous_hash, 16)
    except ValueError as exc:
        raise EventLedgerError("previous_hash must be hexadecimal") from exc
    # Keep the ledger metadata-only: no raw mission, context, output, or secret material.
    forbidden = {"question", "output", "context", "prompt", "token", "password", "secret", "api_key"}
    if any(str(key).casefold() in forbidden for key in payload):
        raise EventLedgerError("payload contains a prohibited raw-content or secret field")
    try:
        json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise EventLedgerError("payload must be JSON serializable") from exc
    event = {
        "schema": "omega-prism-event",
        "schema_version": VERSION,
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "previous_hash": previous_hash,
    }
    event["event_hash"] = _event_hash(event)
    return event


def lifecycle_events(plan: dict[str, Any], context_bundle: dict[str, Any], run: dict[str, Any]) -> list[dict[str, Any]]:
    """Build metadata-only events for an existing P1/P2/P3 lifecycle."""
    if not isinstance(plan, dict) or plan.get("planner") != "omega-adaptive-prism":
        raise EventLedgerError("invalid P1 plan")
    if not isinstance(context_bundle, dict) or context_bundle.get("context_preparer") != "omega-adaptive-prism-rce":
        raise EventLedgerError("invalid P2 context bundle")
    if not isinstance(run, dict) or run.get("runner") != "omega-adaptive-prism-supervised-recorder":
        raise EventLedgerError("invalid P3 execution")
    mission = plan.get("mission", {})
    if mission.get("question") != context_bundle.get("mission", {}).get("question"):
        raise EventLedgerError("P1 and P2 mission mismatch")
    if run.get("mission", {}).get("question") != mission.get("question"):
        raise EventLedgerError("P1 and P3 mission mismatch")

    mission_id = mission.get("mission_id")
    plan_hash = content_hash(plan)
    context_hash = context_bundle.get("manifest", {}).get("content_hash")
    events = [
        build_event("mission_planned", {
            "mission_id": mission_id,
            "plan_hash": plan_hash,
            "planner_version": plan.get("planner_version"),
            "planned_roles": [task["role"] for task in plan.get("tasks", [])],
        }),
        build_event("context_prepared", {
            "mission_id": mission_id,
            "plan_hash": plan_hash,
            "context_hash": context_hash,
            "package_count": len(context_bundle.get("packages", [])),
            "source_engine": context_bundle.get("source_engine"),
            "mode": context_bundle.get("mode"),
        }),
    ]
    for perspective in run.get("perspectives", []):
        output = perspective.get("output")
        events.append(build_event("perspective_recorded", {
            "mission_id": mission_id,
            "role": perspective.get("role"),
            "status": perspective.get("status"),
            "output_hash": content_hash(output) if isinstance(output, str) else None,
            "evidence_refs": list(perspective.get("evidence_refs", [])),
            "limitations": list(perspective.get("limitations", [])),
            "independence": perspective.get("independence", "same_model_role_perspective"),
            "scientific_validation": perspective.get("scientific_validation", "not_performed"),
        }))
    if run.get("run_status") == "closed":
        events.append(build_event("execution_closed", {
            "mission_id": mission_id,
            "coverage": run.get("coverage", {}),
            "scientific_verdict": run.get("scientific_verdict", "not_produced"),
            "synthesis_present": bool(run.get("synthesis")),
        }))
    # Re-chain the lifecycle as one contiguous batch.
    chained = []
    previous = GENESIS
    for event in events:
        event["previous_hash"] = previous
        event["event_hash"] = _event_hash(event)
        chained.append(event)
        previous = event["event_hash"]
    return chained


def verify_events(events: list[dict[str, Any]], *, previous_hash: str = GENESIS) -> dict[str, Any]:
    if not isinstance(events, list):
        raise EventLedgerError("events must be a list")
    expected = previous_hash
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise EventLedgerError(f"event {index} is not an object")
        if event.get("schema") != "omega-prism-event" or event.get("schema_version") != VERSION:
            raise EventLedgerError(f"event {index} has an unsupported schema")
        if event.get("event_type") not in EVENT_TYPES:
            raise EventLedgerError(f"event {index} has an unsupported type")
        if event.get("previous_hash") != expected:
            raise EventLedgerError(f"broken hash-chain link at event {index}")
        actual = _event_hash(event)
        if event.get("event_hash") != actual:
            raise EventLedgerError(f"event hash mismatch at event {index}")
        expected = actual
    return {"valid": True, "event_count": len(events), "last_hash": expected}


def append_events(path: Path, events: list[dict[str, Any]]) -> dict[str, Any]:
    """Append a verified batch to a JSONL ledger; never truncate or rewrite it."""
    path = Path(path)
    if not events:
        raise EventLedgerError("refusing to append an empty event batch")
    if path.exists():
        if not path.is_file():
            raise EventLedgerError("ledger path exists and is not a regular file")
        existing = []
        try:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    raise EventLedgerError(f"blank line in ledger at line {line_number}")
                existing.append(json.loads(line))
        except (OSError, json.JSONDecodeError) as exc:
            raise EventLedgerError(f"cannot read existing ledger: {exc}") from exc
        state = verify_events(existing)
        expected = state["last_hash"]
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        expected = GENESIS
    state = verify_events(events, previous_hash=expected)
    rendered = "".join(canonical_json(event) + "\n" for event in events)
    try:
        with path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(rendered)
            handle.flush()
    except OSError as exc:
        raise EventLedgerError(f"cannot append ledger: {exc}") from exc
    return {"appended": len(events), "last_hash": state["last_hash"], "path": str(path)}


def read_ledger(path: Path) -> dict[str, Any]:
    path = Path(path)
    try:
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise EventLedgerError(f"cannot read ledger: {exc}") from exc
    state = verify_events(events)
    return {"events": events, **state}
