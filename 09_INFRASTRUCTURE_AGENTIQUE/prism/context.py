"""Role-specific, provenance-preserving context preparation for Omega prism P2.

This module reuses the existing read-only MCP gateway functions. It does not
execute role tasks, call models, write memory, or validate scientific claims.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GATEWAY_DIR = HERE.parent / "gateway"
if str(GATEWAY_DIR) not in sys.path:
    sys.path.insert(0, str(GATEWAY_DIR))

import server as gateway  # noqa: E402

VERSION = "0.1.0"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{1,80}$")


class ContextPreparationError(ValueError):
    """Raised when a plan or context request violates the P2 contract."""


def _validate_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(plan, dict) or plan.get("planner") != "omega-adaptive-prism":
        raise ContextPreparationError("plan must be an Omega adaptive prism plan")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        raise ContextPreparationError("plan.tasks must be a list")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ContextPreparationError("each plan task must be an object")
        role = task.get("role")
        if role not in gateway.rce.ROLE_GUIDANCE:
            raise ContextPreparationError(f"unknown RCE role: {role!r}")
        if role in seen:
            raise ContextPreparationError(f"duplicate role in plan: {role}")
        seen.add(role)
        if not isinstance(task.get("question"), str) or not task["question"].strip():
            raise ContextPreparationError(f"task {role} has no question")
    return tasks


def _known_ids(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContextPreparationError("mission.known_ids must be a list of exact IDs")
    result = []
    for identifier in value:
        if not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier):
            raise ContextPreparationError(f"invalid exact ID: {identifier!r}")
        if identifier not in result:
            result.append(identifier)
    return result


def prepare_contexts(
    root: Path,
    plan: dict[str, Any],
    *,
    max_documents: int = 12,
) -> dict[str, Any]:
    """Prepare one RCE context package per planned role, without task execution.

    Search is performed once per role. Exact retrieval is performed for IDs
    explicitly supplied in mission.known_ids and IDs surfaced by the search.
    Semantic candidates remain candidates; pending migrations remain pending.
    """
    tasks = _validate_plan(plan)
    if isinstance(max_documents, bool) or not isinstance(max_documents, int) or not 1 <= max_documents <= 30:
        raise ContextPreparationError("max_documents must be an integer from 1 to 30")
    mission = plan.get("mission")
    if not isinstance(mission, dict):
        raise ContextPreparationError("plan.mission must be an object")
    question = mission.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ContextPreparationError("plan.mission.question must be a non-empty string")
    known_ids = _known_ids(mission.get("known_ids"))

    packages = []
    for task in tasks:
        role = task["role"]
        search_question = f"{question.strip()}\n{task['question'].strip()}"
        search_result = gateway.memory_search(root, {
            "question": search_question,
            "role": role,
            "max_documents": max_documents,
        })

        discovered_ids = []
        for field in ("registered_results", "pending_migration_items"):
            for item in search_result.get(field, []):
                identifier = item.get("id")
                if isinstance(identifier, str) and ID_PATTERN.fullmatch(identifier) and identifier not in discovered_ids:
                    discovered_ids.append(identifier)

        exact_ids = list(dict.fromkeys(known_ids + discovered_ids))
        exact_records = []
        for identifier in exact_ids:
            exact_records.append({
                "requested_id": identifier,
                "retrieval": gateway.memory_get(root, {"id": identifier}),
            })

        package = {
            "role": role,
            "assigned_question": task["question"],
            "activation_reason": task.get("activation_reason"),
            "role_guidance": task.get("role_guidance", gateway.rce.ROLE_GUIDANCE[role]),
            "search_query": search_question,
            "search_context": search_result,
            "exact_retrievals": exact_records,
            "retrieval_policy": {
                "explicit_ids_first": known_ids,
                "exact_ids_retrieved": exact_ids,
                "semantic_candidates_are_not_dependencies": True,
                "scientific_validation_performed": False,
            },
            "execution_status": "not_executed",
            "perspective_independence": "same_principal_role_perspective",
        }
        packages.append(package)

    bundle = {
        "context_preparer": "omega-adaptive-prism-rce",
        "context_preparer_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mission": {
            **{key: mission[key] for key in ("mission_id", "domain", "scope", "exclusions", "constraints")
               if key in mission},
            "question": question.strip(),
            "mission_type": mission.get("mission_type"),
            "known_ids": known_ids,
        },
        "source_engine": "existing_read_only_rce_gateway",
        "repository_root_name": root.name,
        "mode": "read_only_local_checkout",
        "packages": packages,
        "limitations": [
            "Recherche lexicale locale uniquement ; aucune recherche sémantique ou externe.",
            "Seuls les fichiers présents dans ce checkout sont accessibles.",
            "Les documents candidats ne sont pas des dépendances scientifiques établies.",
            "Les entrées d'index et fiches récupérées ne sont pas revalidées scientifiquement.",
            "Aucun rôle n'a été exécuté ; aucun modèle n'a été appelé.",
        ],
        "execution_model": {
            "status": "context_preparation_only",
            "model_calls_performed": 0,
            "role_tasks_executed": 0,
            "memory_writes_performed": 0,
            "scientific_validation_performed": False,
        },
    }
    canonical = json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    bundle["manifest"] = {
        "content_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "package_count": len(packages),
        "search_calls": len(packages),
        "exact_retrieval_calls": sum(len(p["exact_retrievals"]) for p in packages),
    }
    return bundle
