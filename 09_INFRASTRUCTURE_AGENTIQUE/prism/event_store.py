"""Append-only event ledger conforming to Omega's research-event schema (P4).

Only provenance metadata and content hashes are persisted. Raw mission text,
context documents, and perspective outputs are deliberately excluded.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.2.0"
GENESIS = "0" * 64
ROLE_EVENT_TYPES = {
    "refuter": "review",
    "formalist": "formalization",
    "computational": "computation",
    "bibliographer": "literature_search",
    "researcher": "reasoning",
}


class EventLedgerError(ValueError):
    """Raised when an event or append-only ledger violates its contract."""


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _event_hash(event: dict[str, Any]) -> str:
    return content_hash({key: value for key, value in event.items() if key != "event_hash"})


def _reference(ref_id: str, ref_type: str, digest: str | None = None) -> dict[str, Any]:
    return {
        "ref_id": ref_id,
        "version": None,
        "ref_type": ref_type,
        "uri": None,
        "content_hash": digest,
        "locator": None,
        "epistemic_space": "experimental_internal",
        "scientific_status": None,
        "publication_status": "EXPÉRIMENTAL",
    }


def build_event(
    *,
    mission_id: str,
    event_type: str,
    role: str,
    execution_status: str,
    inputs: list[dict[str, Any]] | None = None,
    outputs: list[dict[str, Any]] | None = None,
    context_manifest: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
    previous_hash: str = GENESIS,
) -> dict[str, Any]:
    allowed_types = {
        "context_retrieval", "literature_search", "reasoning", "computation",
        "simulation", "formalization", "review", "counterexample", "proposal",
        "validation_decision", "publication", "revision",
    }
    if not isinstance(mission_id, str) or not mission_id.strip():
        raise EventLedgerError("mission_id must be non-empty")
    if event_type not in allowed_types:
        raise EventLedgerError("event_type is not allowed by research-event.schema.json")
    if execution_status not in {"completed", "partial", "failed", "not_executed"}:
        raise EventLedgerError("invalid execution_status")
    if not isinstance(previous_hash, str) or len(previous_hash) != 64:
        raise EventLedgerError("previous_hash must be a SHA-256 digest")
    try:
        int(previous_hash, 16)
    except ValueError as exc:
        raise EventLedgerError("previous_hash must be hexadecimal") from exc
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id,
        "actor": {
            "actor_id": "chatgpt-principal",
            "actor_type": "agent",
            "role": role,
            "provider": None,
            "model_or_tool": "ChatGPT principal assistant; exact model version not recorded",
            "version": None,
            "configuration_ref": None,
        },
        "context_manifest": context_manifest,
        "inputs": inputs or [],
        "outputs": outputs or [],
        "epistemic_space": "experimental_internal",
        "execution_status": execution_status,
        "independence": {
            "source": "unknown",
            "method": "dependent",
            "implementation": "not_applicable",
            "data": "dependent",
            "environment": "unknown",
            "agent": "dependent",
            "review": "unknown",
        },
        "limitations": limitations or [],
        "errors": [],
        "supersedes_event_ids": [],
        "privacy_class": "internal",
        "previous_hash": previous_hash,
    }
    event["event_hash"] = _event_hash(event)
    return event


def lifecycle_events(plan: dict[str, Any], context_bundle: dict[str, Any], run: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(plan, dict) or plan.get("planner") != "omega-adaptive-prism":
        raise EventLedgerError("invalid P1 plan")
    if not isinstance(context_bundle, dict) or context_bundle.get("context_preparer") != "omega-adaptive-prism-rce":
        raise EventLedgerError("invalid P2 context bundle")
    if not isinstance(run, dict) or run.get("runner") != "omega-adaptive-prism-supervised-recorder":
        raise EventLedgerError("invalid P3 execution")
    mission = plan.get("mission", {})
    mission_id = mission.get("mission_id") or "mission-" + content_hash(mission)[:16]
    if mission.get("question") != context_bundle.get("mission", {}).get("question"):
        raise EventLedgerError("P1 and P2 mission mismatch")
    if run.get("mission", {}).get("question") != mission.get("question"):
        raise EventLedgerError("P1 and P3 mission mismatch")

    plan_digest = content_hash(plan)
    context_digest = context_bundle.get("manifest", {}).get("content_hash")
    if not isinstance(context_digest, str) or len(context_digest) != 64:
        raise EventLedgerError("P2 context manifest hash is missing or invalid")
    manifest = {
        "manifest_id": "context-" + context_digest[:16],
        "version": str(context_bundle.get("context_preparer_version", "0.1.0")),
        "content_hash": context_digest,
        "retrieved_item_ids": sorted({
            record.get("requested_id")
            for package in context_bundle.get("packages", [])
            for record in package.get("exact_retrievals", [])
            if isinstance(record.get("requested_id"), str)
        }),
    }
    events = []
    events.append(build_event(
        mission_id=mission_id, event_type="reasoning", role="planner",
        execution_status="completed",
        inputs=[_reference("mission-" + content_hash(mission)[:16], "document", content_hash(mission))],
        outputs=[_reference("plan-" + plan_digest[:16], "run", plan_digest)],
        limitations=["Planification uniquement ; aucune tâche scientifique exécutée."],
    ))
    events.append(build_event(
        mission_id=mission_id, event_type="context_retrieval", role="context_engine",
        execution_status="completed",
        inputs=[_reference("plan-" + plan_digest[:16], "run", plan_digest)],
        outputs=[_reference("context-" + context_digest[:16], "context_bundle", context_digest)],
        context_manifest=manifest,
        limitations=list(context_bundle.get("limitations", [])),
    ))
    for item in run.get("perspectives", []):
        role = item.get("role")
        status = item.get("status")
        mapped = status if status in {"completed", "not_executed"} else "partial"
        output = item.get("output")
        outputs = [_reference(
            "output-" + content_hash(output)[:16], "agent_artifact", content_hash(output)
        )] if isinstance(output, str) else []
        events.append(build_event(
            mission_id=mission_id,
            event_type=ROLE_EVENT_TYPES.get(role, "reasoning"),
            role=role or "unknown",
            execution_status=mapped,
            inputs=[_reference("context-" + context_digest[:16], "context_bundle", context_digest)],
            outputs=outputs,
            context_manifest=manifest,
            limitations=list(item.get("limitations", [])) + [
                "Perspective du même agent principal ; aucune indépendance inter-agent revendiquée.",
                "Enregistrement d'activité, pas validation scientifique.",
            ],
        ))
    if run.get("run_status") == "closed":
        events.append(build_event(
            mission_id=mission_id, event_type="review", role="prism_recorder",
            execution_status="completed",
            inputs=[_reference("context-" + context_digest[:16], "context_bundle", context_digest)],
            outputs=[_reference("run-" + content_hash(run)[:16], "run", content_hash(run))],
            context_manifest=manifest,
            limitations=["Clôture administrative ; aucun verdict scientifique ni synthèse automatique."],
        ))
    previous = GENESIS
    for event in events:
        event["previous_hash"] = previous
        event["event_hash"] = _event_hash(event)
        previous = event["event_hash"]
    return events


def verify_events(events: list[dict[str, Any]], *, previous_hash: str = GENESIS) -> dict[str, Any]:
    if not isinstance(events, list):
        raise EventLedgerError("events must be a list")
    expected = previous_hash
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise EventLedgerError(f"event {index} is not an object")
        if event.get("previous_hash") != expected:
            raise EventLedgerError(f"broken hash-chain link at event {index}")
        if event.get("event_hash") != _event_hash(event):
            raise EventLedgerError(f"event hash mismatch at event {index}")
        required = {"event_id", "event_type", "occurred_at", "mission_id", "actor",
                    "inputs", "outputs", "epistemic_space", "execution_status"}
        if not required.issubset(event):
            raise EventLedgerError(f"event {index} misses research-event schema fields")
        if event.get("epistemic_space") != "experimental_internal":
            raise EventLedgerError(f"event {index} has an invalid epistemic space")
        expected = event["event_hash"]
    return {"valid": True, "event_count": len(events), "last_hash": expected}


def append_events(path: Path, events: list[dict[str, Any]]) -> dict[str, Any]:
    """Append a verified batch to JSONL; never truncate or rewrite prior events."""
    path = Path(path)
    if not events:
        raise EventLedgerError("refusing to append an empty event batch")
    if path.exists():
        try:
            existing = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        except (OSError, json.JSONDecodeError) as exc:
            raise EventLedgerError(f"cannot read existing ledger: {exc}") from exc
        if any(not line.strip() for line in path.read_text(encoding="utf-8").splitlines()):
            raise EventLedgerError("blank line in existing ledger")
        expected = verify_events(existing)["last_hash"]
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        expected = GENESIS
    # Re-chain the new batch to the current tail without changing prior lines.
    verify_events(events)  # Reject malformed or tampered source batches before re-chaining.
    chained = []
    previous = expected
    for original in events:
        event = dict(original)
        event["previous_hash"] = previous
        event["event_hash"] = _event_hash(event)
        chained.append(event)
        previous = event["event_hash"]
    state = verify_events(chained, previous_hash=expected)
    rendered = "".join(_canonical(event) + "\\n" for event in chained)
    try:
        with path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(rendered)
            handle.flush()
    except OSError as exc:
        raise EventLedgerError(f"cannot append ledger: {exc}") from exc
    return {"appended": len(events), "last_hash": state["last_hash"], "path": str(path)}


def read_ledger(path: Path) -> dict[str, Any]:
    try:
        events = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
    except (OSError, json.JSONDecodeError) as exc:
        raise EventLedgerError(f"cannot read ledger: {exc}") from exc
    return {"events": events, **verify_events(events)}
