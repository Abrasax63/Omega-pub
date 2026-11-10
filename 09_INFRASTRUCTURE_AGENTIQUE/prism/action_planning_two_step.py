"""Exact finite-horizon action planner on explicitly supplied hypothetical evidence.

This is an experimental two-step extension of Omega P1, NOT an autonomous
research agent. Decisions, probabilities and observation partitions are
stipulated by the caller. No model, tool, or memory is invoked.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache

from action_selection import EvidenceModelError, _validate
from planner import plan_mission


def _decision_error(hypotheses, indices):
    totals = Counter()
    for i in indices:
        h = hypotheses[i]
        totals[h["decision"]] += h["weight"]
    return sum(totals.values()) - max(totals.values())


def optimize_policy(case, *, max_depth=2):
    """Minimize expected decision error plus hypothetical verification costs.

    Expected errors and action costs are expressed as fractions of the
    original total hypothesis mass. A follow-up test can depend on the
    outcome of the first. Reusing a test is forbidden. Only the next
    max_depth checks are optimized; there is no model of evidence reliability.
    """
    hypotheses, checks = _validate(case)
    if type(max_depth) is not int or not 0 <= max_depth <= 2:
        raise EvidenceModelError("max_depth must be 0, 1 or 2")
    indices = tuple(range(len(hypotheses)))
    total_mass = sum(h["weight"] for h in hypotheses)
    available = tuple(sorted(
        (i for i, c in enumerate(checks) if c["available"]),
        key=lambda i: checks[i]["id"],
    ))

    @lru_cache(maxsize=None)
    def solve(state, remaining, depth):
        weight = sum(hypotheses[i]["weight"] for i in state)
        missed = _decision_error(hypotheses, state)
        best = (Fraction(missed), Fraction(0),
                {"action": "answer" if missed == 0 else "insufficient_evidence"})
        best_total = Fraction(missed)
        if depth == 0 or missed == 0:
            return best

        for ci in remaining:  # Lexical ID order; earlier wins equal scores.
            check = checks[ci]
            outcomes = defaultdict(list)
            for i in state:
                outcomes[check["observations"][i]].append(i)
            follow = tuple(i for i in remaining if i != ci)
            branches = {}
            error_mass = Fraction(0)
            downstream_cost_mass = Fraction(0)
            for outcome in sorted(outcomes):
                subset = tuple(outcomes[outcome])
                e, c, branch = solve(subset, follow, depth - 1)
                error_mass += e
                downstream_cost_mass += c
                branches[outcome] = branch
            action_cost_mass = Fraction(weight * check["cost_milli"], 1000)
            candidate_cost_mass = action_cost_mass + downstream_cost_mass
            candidate_total = error_mass + candidate_cost_mass
            if candidate_total < best_total:
                best_total = candidate_total
                best = (
                    error_mass, candidate_cost_mass,
                    {"action": check["action"], "check_id": check["id"],
                     "next_step": check["step"], "method": check["method"],
                     "branches": branches},
                )
        return best

    error_mass, cost_mass, policy = solve(indices, available, max_depth)
    initial_error_mass = Fraction(_decision_error(hypotheses, indices))
    return {
        "case_id": case["case_id"],
        "max_depth": max_depth,
        "action": policy["action"],
        "policy": policy,
        "initial_decision_risk": str(initial_error_mass / total_mass),
        "expected_decision_risk": str(error_mass / total_mass),
        "expected_action_cost": str(cost_mass / total_mass),
        "expected_total_loss": str((error_mass + cost_mass) / total_mass),
        "net_value": str((initial_error_mass - error_mass - cost_mass) / total_mass),
        "model_status": "hypothetical_finite_evidence_only",
    }


def plan_with_two_step_evidence(case):
    """Reuse Omega P1 for the FIRST step, keeping conditional policy separate."""
    result = optimize_policy(case, max_depth=2)
    action = result["action"]
    if action == "answer":
        decisions = {h["decision"] for h in case["hypotheses"]}
        context = {"decision_basis": (
            "Une seule décision est compatible avec les hypothèses fournies : "
            + next(iter(decisions)) + "."
        )}
    else:
        context = {"blocking_uncertainty": case["uncertainty"]}
        if action == "verify":
            context["verification"] = result["policy"]["next_step"]
            context["verification_effect"] = (
                "La politique conditionnelle peut modifier la décision "
                "après un ou deux contrôles dans le modèle fourni."
            )
        elif action == "ask":
            context["clarification"] = result["policy"]["next_step"]
    p1 = plan_mission({
        "question": case["question"],
        "mission_type": case["mission_type"],
        "mission_id": case["case_id"],
        "decision_context": context,
    })
    if p1["next_action"]["action"] != action:
        raise AssertionError("Two-step first action differs from Omega P1 bridge")
    return {"optimization": result, "p1": p1}
