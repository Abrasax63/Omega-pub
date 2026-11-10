"""Deterministic, explainable role planner for the Omega adaptive prism.

P1 only plans work. It does not call models, execute tasks, write memory, or
claim that role perspectives are independent agents.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

RCE_DIR = Path(__file__).resolve().parents[1] / "prototype"
if str(RCE_DIR) not in sys.path:
    sys.path.insert(0, str(RCE_DIR))

from rce import ROLE_GUIDANCE  # noqa: E402

VERSION = "0.1.0"
ROLE_ORDER = ("refuter", "formalist", "computational", "bibliographer", "researcher")
MISSION_TYPES = ("mathematical", "exploratory", "documentary", "computational", "general")

DEFAULT_DELIVERABLES = {
    "mathematical": (
        "Énoncer le résultat et ses hypothèses.",
        "Fournir une preuve ou un contre-exemple, ou signaler la lacune décisive.",
    ),
    "documentary": (
        "Donner la conclusion qui s'applique et citer le passage décisif.",
        "Signaler les conflits de sources et les informations nécessaires pour trancher.",
    ),
    "computational": (
        "Donner le résultat et la décision qu'il implique, si une décision est demandée.",
        "Indiquer les données et les étapes qui permettent de refaire le calcul.",
    ),
    "exploratory": (
        "Distinguer les constats des explications possibles.",
        "Proposer une observation ou un test qui départagerait ces explications.",
    ),
    "general": ("Donner une réponse directe et indiquer toute incertitude qui change la conclusion.",),
}

ROLE_QUESTIONS = {
    "refuter": "Quelle hypothèse centrale pourrait être fausse, et quel contre-exemple ou test la réfuterait ?",
    "formalist": "Quelles définitions, hypothèses, quantificateurs et étapes logiques doivent être explicités ?",
    "computational": "Quel calcul, cas fini ou test reproductible pourrait réellement changer le verdict ?",
    "bibliographer": "Quelles sources primaires et objections publiées faut-il vérifier pour établir l'état de l'art ?",
    "researcher": "Quelles sont les pistes concurrentes, les inconnues et le prochain verrou à fort gain d'information ?",
}
FAILURE_CRITERIA = {
    "refuter": "Aucune tentative de réfutation pertinente n'est documentée, ou un contre-exemple valide invalide l'énoncé.",
    "formalist": "Une hypothèse est implicite, une implication n'est pas justifiée ou la conclusion dépasse la portée des prémisses.",
    "computational": "Le calcul n'est pas reproductible, les entrées/sorties manquent ou le test ne discrimine pas les hypothèses.",
    "bibliographer": "Les affirmations bibliographiques ne sont pas reliées à des sources vérifiables ou la recherche est incomplète.",
    "researcher": "Les pistes ne sont pas discriminantes, le verrou n'est pas explicité ou les inconnues sont masquées.",
}
STOP_CONDITIONS = {
    "refuter": "Arrêter après réfutation valide, ou après épuisement documenté des tests pertinents pour le verrou.",
    "formalist": "Arrêter lorsque l'énoncé et ses hypothèses sont stabilisés, ou lorsqu'une lacune précise bloque la preuve.",
    "computational": "Arrêter lorsque le test discriminant est exécuté et vérifié, ou lorsque les données/outils nécessaires manquent.",
    "bibliographer": "Arrêter lorsque les sources primaires pertinentes sont identifiées et les limites de couverture déclarées.",
    "researcher": "Arrêter lorsque le prochain verrou est identifié et qu'une action discriminante est formulée.",
}


class MissionValidationError(ValueError):
    """Raised when a mission does not satisfy the planner input contract."""


def _boolean(mission: dict[str, Any], key: str, default: bool) -> bool:
    value = mission.get(key, default)
    if not isinstance(value, bool):
        raise MissionValidationError(f"'{key}' must be a boolean")
    return value


def _next_action(context: Any) -> dict[str, str]:
    """Choose an action from explicitly supplied evidence about the decision."""
    allowed = {"decision_basis", "blocking_uncertainty", "verification", "verification_effect", "clarification"}
    if not isinstance(context, dict) or context.keys() - allowed:
        raise MissionValidationError("'decision_context' must contain only supported fields")
    if any(not isinstance(value, str) or not value.strip() for value in context.values()):
        raise MissionValidationError("decision context fields must be non-empty strings")
    if ("verification" in context) != ("verification_effect" in context):
        raise MissionValidationError("a verification must state what result could change the decision")
    basis = context.get("decision_basis")
    blocker = context.get("blocking_uncertainty")
    if bool(basis) == bool(blocker):
        raise MissionValidationError("supply exactly one decision basis or blocking uncertainty")

    if basis is not None:
        if "verification" in context or "clarification" in context:
            raise MissionValidationError("a verification or clarification requires a blocking uncertainty")
        return {"action": "answer", "reason": basis.strip()}

    if "verification" in context:
        return {
            "action": "verify", "reason": blocker.strip(),
            "next_step": context["verification"].strip(),
            "decision_effect": context["verification_effect"].strip(),
        }
    if "clarification" in context:
        return {"action": "ask", "reason": blocker.strip(), "next_step": context["clarification"].strip()}
    return {"action": "insufficient_evidence", "reason": blocker.strip()}


def plan_mission(mission: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic plan from an explicit, bounded mission object.

    Required: non-empty 'question' and 'mission_type'. Optional boolean flags:
    requires_proof, requires_computation, requires_literature, exploratory,
    claims_to_test. Type defaults can be overridden explicitly by these flags.
    Optional deliverables replace type defaults without changing role selection.
    An optional decision_context adds a recommended next action without executing it.
    """
    if not isinstance(mission, dict):
        raise MissionValidationError("mission must be an object")
    question = mission.get("question")
    if not isinstance(question, str) or not question.strip():
        raise MissionValidationError("'question' must be a non-empty string")
    mission_type = mission.get("mission_type")
    if not isinstance(mission_type, str) or mission_type not in MISSION_TYPES:
        raise MissionValidationError(f"'mission_type' must be one of {MISSION_TYPES}")

    deliverables = mission.get("deliverables")
    if "deliverables" in mission:
        if (not isinstance(deliverables, list) or not deliverables
                or any(not isinstance(item, str) or not item.strip() for item in deliverables)):
            raise MissionValidationError("'deliverables' must be a non-empty list of non-empty strings")
        deliverables = list(dict.fromkeys(item.strip() for item in deliverables))
        deliverable_source = "mission"
    else:
        deliverables = list(DEFAULT_DELIVERABLES[mission_type])
        deliverable_source = "mission_type"

    defaults = {
        "requires_proof": mission_type == "mathematical",
        "requires_computation": mission_type == "computational",
        "requires_literature": mission_type == "documentary",
        "exploratory": mission_type in ("exploratory", "general"),
        "claims_to_test": True,
    }
    flags = {key: _boolean(mission, key, default) for key, default in defaults.items()}

    active = {"refuter": flags["claims_to_test"]}
    active["formalist"] = flags["requires_proof"]
    active["computational"] = flags["requires_computation"]
    active["bibliographer"] = flags["requires_literature"]
    active["researcher"] = flags["exploratory"]

    reasons = {
        "refuter": (
            "Activé par défaut : toute affirmation à évaluer doit subir une tentative de réfutation."
            if active["refuter"] else
            "Désactivé explicitement : aucune affirmation à tester n'est déclarée dans cette mission."
        ),
        "formalist": (
            "Activé : la mission est déclarée dépendante d'une preuve ou d'une formalisation."
            if active["formalist"] else
            "Désactivé : aucune exigence de preuve/formalisation n'est déclarée."
        ),
        "computational": (
            "Activé : un calcul ou test computationnel est déclaré nécessaire."
            if active["computational"] else
            "Désactivé : aucun calcul discriminant n'est déclaré nécessaire."
        ),
        "bibliographer": (
            "Activé : l'établissement de l'état de l'art ou des sources est requis."
            if active["bibliographer"] else
            "Désactivé : aucune vérification bibliographique n'est demandée."
        ),
        "researcher": (
            "Activé : l'indicateur exploratoire est actif (par type de mission ou déclaration explicite)."
            if active["researcher"] else
            "Désactivé : le routage ne demande pas de cartographie exploratoire."
        ),
    }

    tasks = []
    for role in ROLE_ORDER:
        if active[role]:
            tasks.append({
                "role": role,
                "question": ROLE_QUESTIONS[role],
                "role_guidance": ROLE_GUIDANCE[role],
                "activation_reason": reasons[role],
                "expected_output": {
                    "refuter": "Objections testables, contre-exemples candidats et verdict de réfutation motivé.",
                    "formalist": "Énoncé formel, définitions, hypothèses et chaîne logique avec lacunes signalées.",
                    "computational": "Protocole reproductible, données/code requis et résultats uniquement s'ils sont exécutés.",
                    "bibliographer": "Références primaires vérifiables, travaux contradictoires et limites de couverture.",
                    "researcher": "Carte des pistes concurrentes, inconnues et verrou prioritaire.",
                }[role],
                "failure_criterion": FAILURE_CRITERIA[role],
                "stop_condition": STOP_CONDITIONS[role],
                "execution_status": "not_executed",
                "independence": "role_perspective_only",
            })

    inactive = [
        {"role": role, "reason": reasons[role]}
        for role in ROLE_ORDER if not active[role]
    ]
    mission_context = {
        "question": question.strip(),
        "mission_type": mission_type,
        "flags": flags,
    }
    for field in ("mission_id", "domain", "scope"):
        if field in mission:
            value = mission[field]
            if not isinstance(value, str) or not value.strip():
                raise MissionValidationError(f"'{field}' must be a non-empty string")
            mission_context[field] = value.strip()
    for field in ("exclusions", "known_ids", "constraints"):
        if field in mission:
            value = mission[field]
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                raise MissionValidationError(f"'{field}' must be a list of non-empty strings")
            mission_context[field] = list(dict.fromkeys(item.strip() for item in value))

    plan = {
        "planner": "omega-adaptive-prism",
        "planner_version": VERSION,
        "mission": mission_context,
        "selection_policy": "explicit_rules_v1",
        "deliverables": deliverables,
        "deliverable_source": deliverable_source,
        "tasks": tasks,
        "inactive_roles": inactive,
        "execution_model": {
            "status": "planning_only",
            "agent_principal": "ChatGPT",
            "role_perspectives_are_independent_agents": False,
            "model_calls_performed": 0,
            "memory_writes_performed": 0,
            "scientific_validation_performed": False,
        },
        "global_stop_condition": (
            "Ne pas exécuter une tâche sans contexte et autorisation adaptés. "
            "Arrêter le plan lorsque le verrou prioritaire est traité, réfuté ou déclaré indéterminé ; "
            "ne pas lancer plus de deux nouvelles expériences décisives pour un même verrou."
        ),
    }
    if "decision_context" in mission:
        plan["next_action"] = _next_action(mission["decision_context"])
    return plan
