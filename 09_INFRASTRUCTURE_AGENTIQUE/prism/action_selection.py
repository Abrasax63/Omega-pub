"""Experimental, one-step decision-value planner; not a scientific oracle.

Input hypotheses and observation partitions are supplied by the caller.
No evidence is discovered, no action is executed, no model is called.
The policy minimizes expected 0-1 decision loss plus an explicitly supplied
normalized action cost. Exact rational arithmetic avoids tie-rounding.
"""
from collections import defaultdict
from fractions import Fraction

from planner import plan_mission


class EvidenceModelError(ValueError):
    """Invalid finite evidence model."""


def _require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise EvidenceModelError(f"{label} must be nonempty text")


def _validate(case):
    if not isinstance(case, dict):
        raise EvidenceModelError("case must be an object")
    for name in ("case_id", "question", "mission_type", "uncertainty"):
        _require_text(case.get(name), name)
    hypotheses = case.get("hypotheses")
    if not isinstance(hypotheses, list) or not hypotheses:
        raise EvidenceModelError("nonempty hypotheses required")
    ids = set()
    for hyp in hypotheses:
        if not isinstance(hyp, dict):
            raise EvidenceModelError("hypothesis must be an object")
        _require_text(hyp.get("id"), "hypothesis id")
        _require_text(hyp.get("decision"), "hypothesis decision")
        weight = hyp.get("weight")
        if type(weight) is not int or weight <= 0:
            raise EvidenceModelError("hypothesis weight must be a positive integer")
        if hyp["id"] in ids:
            raise EvidenceModelError("duplicate hypothesis id")
        ids.add(hyp["id"])
    checks = case.get("checks")
    if not isinstance(checks, list):
        raise EvidenceModelError("checks must be a list")
    check_ids = set()
    for check in checks:
        if not isinstance(check, dict):
            raise EvidenceModelError("check must be an object")
        for name in ("id", "step", "method"):
            _require_text(check.get(name), "check " + name)
        if check["id"] in check_ids:
            raise EvidenceModelError("duplicate check id")
        check_ids.add(check["id"])
        if check.get("action") not in ("verify", "ask"):
            raise EvidenceModelError("check action must be verify or ask")
        if type(check.get("available")) is not bool:
            raise EvidenceModelError("check availability must be bool")
        cost = check.get("cost_milli")
        if type(cost) is not int or not 0 <= cost <= 1000:
            raise EvidenceModelError("check cost_milli must be integer 0..1000")
        outcomes = check.get("observations")
        if (not isinstance(outcomes, list) or len(outcomes) != len(hypotheses)
                or any(not isinstance(x, str) or not x.strip() for x in outcomes)):
            raise EvidenceModelError("observation needed for every hypothesis")
    return hypotheses, checks


def _bayes_error(hypotheses):
    totals = defaultdict(int)
    for h in hypotheses:
        totals[h["decision"]] += h["weight"]
    return sum(totals.values()) - max(totals.values())


def _posterior_error(hypotheses, observations):
    groups = defaultdict(list)
    for h, obs in zip(hypotheses, observations):
        groups[obs].append(h)
    return sum(_bayes_error(group) for group in groups.values())


def select_action(case):
    """Choose the positive net expected reduction in Bayes decision error.

    Only one-step tests are considered. Costs are stipulated fractions of
    0-1 loss (cost_milli/1000), not measured tokens, seconds or money.
    Equal net values are resolved by lexical check id, independent of order.
    """
    hypotheses, checks = _validate(case)
    total = sum(h["weight"] for h in hypotheses)
    prior = Fraction(_bayes_error(hypotheses), total)
    if prior == 0:
        return {"action": "answer", "chosen_check": None,
                "prior_risk": str(prior), "gain": "0", "net_gain": "0"}
    best = None
    for check in sorted(checks, key=lambda c: c["id"]):
        if not check["available"]:
            continue
        posterior = Fraction(_posterior_error(hypotheses, check["observations"]), total)
        gain = prior - posterior
        net = gain - Fraction(check["cost_milli"], 1000)
        if net > 0 and (best is None or net > best["net"]):
            best = {"check": check, "gain": gain, "net": net}
    if best is None:
        return {"action": "insufficient_evidence", "chosen_check": None,
                "prior_risk": str(prior), "gain": "0", "net_gain": "0"}
    return {"action": best["check"]["action"],
            "chosen_check": best["check"]["id"],
            "method": best["check"]["method"],
            "next_step": best["check"]["step"],
            "prior_risk": str(prior),
            "gain": str(best["gain"]), "net_gain": str(best["net"])}


def plan_with_evidence(case):
    """Bridge the experimental choice into the EXISTING Omega P1 planner."""
    choice = select_action(case)
    context = {}
    if choice["action"] == "answer":
        decisions = {h["decision"] for h in case["hypotheses"]}
        context["decision_basis"] = (
            "Dans le modèle d'hypothèses fourni, une seule décision reste possible : "
            + next(iter(decisions)) + "."
        )
    else:
        context["blocking_uncertainty"] = case["uncertainty"]
        if choice["action"] == "verify":
            context["verification"] = choice["next_step"]
            context["verification_effect"] = (
                "Les résultats simulés de ce contrôle peuvent modifier la décision."
            )
        elif choice["action"] == "ask":
            context["clarification"] = choice["next_step"]
    plan = plan_mission({
        "question": case["question"], "mission_type": case["mission_type"],
        "mission_id": case["case_id"], "decision_context": context,
    })
    if plan["next_action"]["action"] != choice["action"]:
        raise AssertionError("P1 action differs from evidence selection")
    return {"choice": choice, "plan": plan}
