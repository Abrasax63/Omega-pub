"""Opt-in read-only bridge to recovered finite observer guards.

Only finite partitions *explicitly supplied by the caller* are examined.
No model retrieval, source verification, hidden oracle, answer-certification,
plan rewrites, role changes, tool calls, or durable-memory mutations.

Original functions are imported unchanged from legacy_observer_transfer.py.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from legacy_observer_transfer import (
    canonicalize, reconfiguration_gate, terminal_probe_guard,
)


# Bounded input: the recovered refinement predicate compares all pairs of
# states. Unbounded user-provided arrays could turn a read-only audit into
# an excessive quadratic computation. This does NOT imply scientific validity.
MAX_STATES = 64
MAX_LISTED_PROBES = 64


class ObserverAuditValidationError(ValueError):
    """Missing or malformed declarative observer evidence."""


def _fields(obj: Any, *, required: set[str], allowed: set[str], label: str) -> dict:
    if not isinstance(obj, dict):
        raise ObserverAuditValidationError(f"{label} must be an object")
    if set(obj) - allowed:
        raise ObserverAuditValidationError(f"{label} contains unknown fields")
    if required - set(obj):
        raise ObserverAuditValidationError(f"{label} misses required fields")
    return obj


def _partition(raw: Any, label: str) -> tuple[int, ...]:
    if not isinstance(raw, list) or not raw:
        raise ObserverAuditValidationError(f"{label} must be a non-empty array")
    if len(raw) > MAX_STATES:
        raise ObserverAuditValidationError(
            f"{label} exceeds safe finite audit bound ({MAX_STATES} states)")
    if any(type(item) is not int or item < 0 for item in raw):
        raise ObserverAuditValidationError(
            f"{label} must contain only nonnegative integer block labels")
    return canonicalize(raw)


def _termination(payload: Any) -> dict[str, Any]:
    data = _fields(
        payload,
        required={"current_partition", "selected_probe_partition",
                  "listed_probe_partitions", "declared_exhaustive"},
        allowed={"current_partition", "selected_probe_partition",
                 "listed_probe_partitions", "declared_exhaustive"},
        label="termination",
    )
    current = _partition(data["current_partition"], "current_partition")
    selected = _partition(data["selected_probe_partition"],
                          "selected_probe_partition")
    raw_available = data["listed_probe_partitions"]
    if not isinstance(raw_available, list) or not raw_available:
        raise ObserverAuditValidationError("listed_probe_partitions must be nonempty")
    if len(raw_available) > MAX_LISTED_PROBES:
        raise ObserverAuditValidationError(
            f"listed_probe_partitions exceeds safe bound ({MAX_LISTED_PROBES})")
    available = tuple(_partition(q, f"listed_probe_partitions[{i}]")
                      for i, q in enumerate(raw_available))
    if type(data["declared_exhaustive"]) is not bool:
        raise ObserverAuditValidationError("declared_exhaustive must be boolean")
    if any(len(q) != len(current) for q in (selected, *available)):
        raise ObserverAuditValidationError("probe partitions have different universes")
    if selected not in available:
        raise ObserverAuditValidationError(
            "selected_probe_partition must occur in listed_probe_partitions")
    reported = terminal_probe_guard(current, selected, available)
    source_status = reported["status"]
    if source_status == "underinformative":
        status = "underinformative_relative_to_listed_probes"
    elif source_status == "not_terminal":
        status = "not_a_fixed_point"
    elif data["declared_exhaustive"]:
        status = "closed_assuming_declared_probe_list"
    else:
        status = "closure_unknown"
    return {
        "status": status,
        "candidate_probe_indexes": list(reported["candidate_probe_indexes"]),
        "declared_exhaustive": data["declared_exhaustive"],
        "assumption_only_not_source_certification": True,
        "indicates_additional_distinction": source_status == "underinformative",
        "description": (
            "Only relative to caller-supplied finite probe models; "
            "availability, model completeness and authenticity not verified."
        ),
    }


def _reconfiguration(payload: Any) -> dict[str, Any]:
    data = _fields(
        payload,
        required={"current_partition", "target_partition", "capacity"},
        allowed={"current_partition", "target_partition", "capacity"},
        label="reconfiguration",
    )
    current = _partition(data["current_partition"], "current_partition")
    target = _partition(data["target_partition"], "target_partition")
    capacity = data["capacity"]
    if type(capacity) is not int or capacity <= 0:
        raise ObserverAuditValidationError("capacity must be a positive integer")
    if len(current) != len(target):
        raise ObserverAuditValidationError("representation universes differ")
    original = reconfiguration_gate(current, target, capacity)
    return {
        **asdict(original),
        "working_representation_only": True,
        "durable_evidence_may_be_discarded": False,
        "description": "Diagnostic on exact supplied partitions, not task-outcome proof.",
    }


def inspect_observer_evidence(spec: Any) -> dict[str, Any]:
    """Return advice; explicitly cannot certify correctness or take actions.

    The caller controls the meaning and completeness of probe models. This
    interface must never be used as a provenance authentication mechanism.
    """
    if not isinstance(spec, dict) or not spec:
        raise ObserverAuditValidationError("observer_audit must be a nonempty object")
    if set(spec) - {"termination", "reconfiguration"}:
        raise ObserverAuditValidationError("observer_audit contains unsupported fields")
    out: dict[str, Any] = {
        "mode": "read_only_advisory_opt_in",
        "source_authenticity_verified": False,
        "scientific_certificate_issued": False,
        "durable_memory_writes_performed": 0,
        "model_calls_performed": 0,
        "planner_decisions_modified": False,
    }
    if "termination" in spec:
        out["termination"] = _termination(spec["termination"])
    if "reconfiguration" in spec:
        out["reconfiguration"] = _reconfiguration(spec["reconfiguration"])
    return out
