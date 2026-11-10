"""Finite-horizon action planner for hypothetical, explicit evidence models.

Experimental extension of the PR #23 two-step planner. No evidence is
discovered, no tool is run, and no scientific truth is established.
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


def optimize_policy(case, *, max_depth=2, max_cost_milli=None):
    """Optimize stopping and conditional tests under an optional HARD budget.

    max_depth is the maximum realized tests on any observation path, 0..4.
    max_cost_milli is the maximum sum of check costs on EACH path, 0..4000;
    None means only the depth constraint applies. Costs are hypothetical
    fractions of 0-1 classification loss (not money, latency, token usage).
    A higher max_depth never forces another test, and can stop early.
    Ties prefer stopping, then lexicographically lowest check ID.
    """
    hypotheses, checks = _validate(case)
    if type(max_depth) is not int or not 0 <= max_depth <= 4:
        raise EvidenceModelError("max_depth must be an integer 0..4")
    if max_cost_milli is not None and (
        type(max_cost_milli) is not int or not 0 <= max_cost_milli <= 4000
    ):
        raise EvidenceModelError("max_cost_milli must be None or integer 0..4000")
    if len(checks) > 8 or len(hypotheses) > 64:
        raise EvidenceModelError("finite search supports <=8 checks and <=64 hypotheses")

    indices = tuple(range(len(hypotheses)))
    total_mass = sum(h["weight"] for h in hypotheses)
    available = tuple(sorted(
        (i for i, c in enumerate(checks) if c["available"]),
        key=lambda i: checks[i]["id"],
    ))
    budget = 4000 if max_cost_milli is None else max_cost_milli

    @lru_cache(maxsize=None)
    def solve(state, remaining, depth, available_budget):
        weight = sum(hypotheses[i]["weight"] for i in state)
        missed = _decision_error(hypotheses, state)
        best = (Fraction(missed), Fraction(0), Fraction(0),
                {"action": "answer" if missed == 0 else "insufficient_evidence"})
        best_total = Fraction(missed)
        if depth == 0 or missed == 0:
            return best

        for ci in remaining:
            check = checks[ci]
            cost = check["cost_milli"]
            if cost > available_budget:
                continue
            outcomes = defaultdict(list)
            for i in state:
                outcomes[check["observations"][i]].append(i)
            follow = tuple(i for i in remaining if i != ci)
            branches = {}
            err_mass = Fraction(0)
            cost_mass = Fraction(weight * cost, 1000)
            steps_mass = Fraction(weight)
            for outcome in sorted(outcomes):
                subset = tuple(outcomes[outcome])
                e, c, steps, branch = solve(
                    subset, follow, depth - 1, available_budget - cost
                )
                err_mass += e
                cost_mass += c
                steps_mass += steps
                branches[outcome] = branch
            candidate_total = err_mass + cost_mass
            if candidate_total < best_total:  # no test if tied with stop
                best_total = candidate_total
                best = (err_mass, cost_mass, steps_mass, {
                    "action": check["action"], "check_id": check["id"],
                    "next_step": check["step"], "method": check["method"],
                    "branches": branches,
                })
        return best

    err_mass, cost_mass, steps_mass, policy = solve(
        indices, available, max_depth, budget
    )
    initial = Fraction(_decision_error(hypotheses, indices))
    return {
        "case_id": case["case_id"],
        "max_depth": max_depth,
        "max_cost_milli": max_cost_milli,
        "action": policy["action"],
        "policy": policy,
        "initial_decision_risk": str(initial / total_mass),
        "expected_decision_risk": str(err_mass / total_mass),
        "expected_action_cost": str(cost_mass / total_mass),
        "expected_total_loss": str((err_mass + cost_mass) / total_mass),
        "expected_steps": str(steps_mass / total_mass),
        "net_value": str((initial - err_mass - cost_mass) / total_mass),
        "model_status": "hypothetical_finite_evidence_only",
        "states_explored": solve.cache_info().currsize,
    }


def plan_with_two_step_evidence(case):
    """Keep existing PR #23 P1 bridge and exact two-step behavior."""
    result = optimize_policy(case, max_depth=2)
    return _bridge_to_p1(case, result)


def plan_with_variable_horizon(case, *, max_depth=4, max_cost_milli=None):
    """Provide first P1 action, retaining future branches as a separate plan."""
    result = optimize_policy(
        case, max_depth=max_depth, max_cost_milli=max_cost_milli
    )
    return _bridge_to_p1(case, result)


def _bridge_to_p1(case, result):
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
                "après plusieurs contrôles dans le modèle fourni."
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
        raise AssertionError("Policy first action differs from Omega P1 bridge")
    return {"optimization": result, "p1": p1}
