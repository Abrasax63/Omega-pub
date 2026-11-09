"""Supervised recording of ChatGPT role perspectives for Omega prism P3.

This module records outputs that have actually been produced by the principal
assistant. It does not call models, spawn agents, execute code, or validate
scientific claims. Each role remains a perspective of the same principal.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

VERSION = "0.1.0"
ALLOWED_STATUSES = {"completed", "blocked", "not_executed"}


class SupervisedExecutionError(ValueError):
    """Raised when a P3 run or recorded perspective violates its contract."""


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def start_execution(plan: dict[str, Any], context_bundle: dict[str, Any]) -> dict[str, Any]:
    """Create an in-memory supervised run from a P1 plan and P2 context bundle."""
    if not isinstance(plan, dict) or plan.get("planner") != "omega-adaptive-prism":
        raise SupervisedExecutionError("plan must be an Omega adaptive prism plan")
    if not isinstance(context_bundle, dict) or context_bundle.get("context_preparer") != "omega-adaptive-prism-rce":
        raise SupervisedExecutionError("context_bundle must be an Omega P2 bundle")
    plan_mission = plan.get("mission")
    bundle_mission = context_bundle.get("mission")
    if not isinstance(plan_mission, dict) or not isinstance(bundle_mission, dict):
        raise SupervisedExecutionError("plan and context bundle must contain mission objects")
    if plan_mission.get("question") != bundle_mission.get("question"):
        raise SupervisedExecutionError("plan and context bundle refer to different questions")
    tasks = plan.get("tasks")
    packages = context_bundle.get("packages")
    if not isinstance(tasks, list) or not isinstance(packages, list):
        raise SupervisedExecutionError("plan.tasks and context_bundle.packages must be lists")
    task_roles = [task.get("role") for task in tasks if isinstance(task, dict)]
    package_roles = [package.get("role") for package in packages if isinstance(package, dict)]
    if len(task_roles) != len(tasks) or len(package_roles) != len(packages):
        raise SupervisedExecutionError("tasks and packages must contain objects")
    if len(set(task_roles)) != len(task_roles) or set(task_roles) != set(package_roles):
        raise SupervisedExecutionError("each planned role must have exactly one matching context package")

    run = {
        "runner": "omega-adaptive-prism-supervised-recorder",
        "runner_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mission": dict(plan_mission),
        "execution_policy": {
            "principal": "ChatGPT",
            "execution_kind": "same_model_role_perspectives",
            "perspectives_are_independent_agents": False,
            "model_calls_performed_by_module": 0,
            "external_agents_spawned": 0,
            "code_execution_performed_by_module": False,
            "scientific_validation_performed": False,
            "memory_writes_performed": 0,
        },
        "perspectives": [
            {
                "role": task["role"],
                "assigned_question": task["question"],
                "activation_reason": task.get("activation_reason"),
                "context_manifest_hash": context_bundle.get("manifest", {}).get("content_hash"),
                "status": "not_executed",
                "output": None,
                "evidence_refs": [],
                "limitations": [],
            }
            for task in tasks
        ],
        "run_status": "open",
    }
    run["manifest"] = {
        "perspective_count": len(run["perspectives"]),
        "content_hash": _canonical_hash(run),
    }
    return run


def record_perspective(
    run: dict[str, Any],
    role: str,
    *,
    status: str,
    output: str | None = None,
    evidence_refs: list[str] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    """Record one explicitly supplied perspective output; never invent one."""
    if not isinstance(run, dict) or run.get("runner") != "omega-adaptive-prism-supervised-recorder":
        raise SupervisedExecutionError("run must be a P3 supervised execution")
    if run.get("run_status") != "open":
        raise SupervisedExecutionError("cannot modify a closed run")
    if status not in ALLOWED_STATUSES:
        raise SupervisedExecutionError(f"status must be one of {sorted(ALLOWED_STATUSES)}")
    if not isinstance(role, str) or not role:
        raise SupervisedExecutionError("role must be a non-empty string")
    perspective = next((item for item in run.get("perspectives", []) if item.get("role") == role), None)
    if perspective is None:
        raise SupervisedExecutionError(f"role is not part of this run: {role}")
    if perspective["status"] != "not_executed":
        raise SupervisedExecutionError(f"role already has a recorded outcome: {role}")
    if status == "completed" and (not isinstance(output, str) or not output.strip()):
        raise SupervisedExecutionError("completed perspectives require their actual non-empty output")
    if status != "completed" and output is not None:
        raise SupervisedExecutionError("blocked/not_executed perspectives cannot carry an output")
    for field, value in (("evidence_refs", evidence_refs), ("limitations", limitations)):
        if value is not None and (
            not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value)
        ):
            raise SupervisedExecutionError(f"{field} must be a list of non-empty strings")
    perspective.update({
        "status": status,
        "output": output.strip() if isinstance(output, str) else None,
        "evidence_refs": list(dict.fromkeys(evidence_refs or [])),
        "limitations": list(dict.fromkeys(limitations or [])),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "recorded_by": "principal_assistant",
        "independence": "same_model_role_perspective",
        "scientific_validation": "not_performed",
    })
    run["manifest"] = {
        "perspective_count": len(run["perspectives"]),
        "content_hash": _canonical_hash({k: v for k, v in run.items() if k != "manifest"}),
    }
    return run


def close_execution(run: dict[str, Any]) -> dict[str, Any]:
    """Close the recorder and report coverage; does not synthesize a verdict."""
    if not isinstance(run, dict) or run.get("runner") != "omega-adaptive-prism-supervised-recorder":
        raise SupervisedExecutionError("run must be a P3 supervised execution")
    if run.get("run_status") != "open":
        raise SupervisedExecutionError("run is already closed")
    statuses = [item.get("status") for item in run.get("perspectives", [])]
    run["run_status"] = "closed"
    run["coverage"] = {
        "completed": statuses.count("completed"),
        "blocked": statuses.count("blocked"),
        "not_executed": statuses.count("not_executed"),
        "all_planned_perspectives_recorded": all(status != "not_executed" for status in statuses),
    }
    run["scientific_verdict"] = "not_produced"
    run["synthesis"] = None
    run["closed_at"] = datetime.now(timezone.utc).isoformat()
    run["manifest"] = {
        "perspective_count": len(run["perspectives"]),
        "content_hash": _canonical_hash({k: v for k, v in run.items() if k != "manifest"}),
    }
    return run
