"""Experimental read-only evidence adapter for Omega's finite planner.

The caller supplies a trusted catalog and receipts from the retrieval layer.
The adapter checks consistency with that catalog. A caller that derives a
receipt from untrusted payload labels provides no origin authentication.
"""
from collections import Counter, defaultdict
from fractions import Fraction

from action_planning_two_step import optimize_policy


def _provenance_issue(check, receipt, scopes):
    if receipt is None:
        return "missing_observation"
    if any(receipt.get(k) != check[k] for k in ("origin", "url", "field")):
        return "origin_or_scope_mismatch"
    scope = (receipt.get("version"), receipt.get("published"))
    if scope != (check["version"], check["published"]) or scope not in scopes:
        return "version_or_date_out_of_scope"
    if type(receipt.get("value")) is not bool or not receipt.get("independence"):
        return "incomplete_receipt"
    return None


def _known_values(receipts, quorum):
    values = {}
    conflicts = []
    for field, records in sorted(receipts.items()):
        claims = {r["value"] for r in records}
        if len(claims) > 1:
            conflicts.append(field)
        elif (len({r["independence"] for r in records}) >= quorum
              and any(r["primary"] for r in records)):
            values[field] = claims.pop()
    return values, conflicts


def _compatible(worlds, facts):
    return [w for w in worlds if all(w["values"][k] == v for k, v in facts.items())]


def _risk(worlds):
    if not worlds:
        return None
    mass = Counter()
    for w in worlds:
        mass[w["decision"]] += w["weight"]
    total = sum(mass.values())
    return str(Fraction(total - max(mass.values()), total))


def _next_check(task, worlds, checks, budget, horizon):
    model = {
        "case_id": task["id"], "question": task["question"],
        "mission_type": "documentary", "uncertainty": "Finite evidence model",
        "hypotheses": worlds,
        "checks": [{
            "id": c["id"], "step": "Consult " + c["url"], "method": "receipt",
            "action": "verify", "available": True, "cost_milli": 5 * c["cost"],
            "observations": [str(w["values"][c["field"]]) for w in worlds],
        } for c in checks],
    }
    return optimize_policy(model, max_depth=min(horizon, budget),
                           max_cost_milli=5 * budget)["policy"].get("check_id")


def decide(task, consult, *, budget, horizon=4, verify=True, fixed=False):
    """Use the same finite planner with optional receipt validation and re-planning.

    consult(check_id) supplies one receipt and may return None for unavailable
    evidence. Its origin, time, and independence assertions are trusted inputs.
    The only side effect is the caller's consultation function.
    """
    if type(budget) is not int or not 0 <= budget <= 4:
        raise ValueError("budget must be an integer from 0 to 4")
    checks = {c["id"]: c for c in task["checks"]}
    if len(checks) != len(task["checks"]) or any(c["cost"] != 1 for c in checks.values()):
        raise ValueError("unique unit-cost checks required")
    scopes = {f: set(map(tuple, entries)) for f, entries in task["scopes"].items()}
    receipts = defaultdict(list)
    facts = {}
    trace = []
    while True:
        certified, conflicts = _known_values(receipts, task["quorum"]) if verify else (facts, [])
        provisional = {f: r[0]["value"] for f, r in receipts.items() if f not in conflicts}
        worlds = _compatible(task["worlds"], certified)
        risk = _risk(worlds)
        if trace:
            trace[-1]["risk_after"] = risk
            trace[-1]["conflicts_after"] = conflicts
        if risk == "0":
            return dict(decision=worlds[0]["decision"], reason="determined", risk=risk, trace=trace)
        if not worlds or len(trace) == budget:
            reason = "model_contradicted" if not worlds else "budget_exhausted"
            return dict(decision=None, reason=reason, risk=risk, trace=trace)
        candidates = [checks[k] for k in sorted(checks) if checks[k]["field"] not in conflicts]
        preferred = [c for c in candidates if c["field"] in provisional
                     and c["field"] not in certified]
        if fixed:
            chosen = candidates[0]["id"] if candidates else None
        else:
            chosen = _next_check(task, worlds, candidates, budget - len(trace), horizon)
            # Corroboration is a prerequisite outside the planner's loss model.
            if preferred and _risk(_compatible(task["worlds"], provisional)) == "0":
                chosen = preferred[0]["id"]
        if chosen is None:
            return dict(decision=None, reason="no_useful_check", risk=risk, trace=trace)
        check = checks.pop(chosen)
        receipt = consult(chosen)
        issue = _provenance_issue(check, receipt, scopes[check["field"]]) if verify else (
            "missing_observation" if receipt is None else None)
        trace.append(dict(check=chosen, risk_before=risk, issue=issue, receipt=receipt))
        if issue is None:
            if verify:
                receipts[check["field"]].append({**receipt, "primary": check["primary"]})
            else:
                facts[check["field"]] = receipt["value"]
