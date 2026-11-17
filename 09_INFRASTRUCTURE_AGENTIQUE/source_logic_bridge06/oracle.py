"""Independent finite Boolean-model audit of manually encoded rules.

Unlike the bridge's forward chaining, this checker enumerates every valuation.
This is independent for *logical consistency* only; it cannot establish that a
human-encoded rule faithfully captures the mathematical source document.
"""
from __future__ import annotations

from itertools import product


def signed_atom(value: str) -> tuple[str, bool]:
    return (value[4:], False) if value.startswith("not:") else (value, True)


def exact_boolean_verdict(query: dict, rules: list[dict]) -> dict:
    facts = set(query["facts"])
    goal = query["goal"]
    universe = facts | {goal}
    for rule in rules:
        universe.update(rule["premises"])
        universe.add(signed_atom(rule["conclusion"])[0])
    atoms = sorted(universe)
    if len(atoms) > 15:
        raise ValueError("exhaustive model bound exceeded")
    models = 0
    true_goal = 0
    false_goal = 0
    witness_true = None
    witness_false = None
    for bits in product((False, True), repeat=len(atoms)):
        m = dict(zip(atoms, bits))
        if not all(m[atom] for atom in facts):
            continue
        accepted = True
        for rule in rules:
            if all(m[atom] for atom in rule["premises"]):
                target, sign = signed_atom(rule["conclusion"])
                if m[target] != sign:
                    accepted = False
                    break
        if not accepted:
            continue
        models += 1
        if m[goal]:
            true_goal += 1
            if witness_true is None:
                witness_true = {a: v for a, v in m.items()}
        else:
            false_goal += 1
            if witness_false is None:
                witness_false = {a: v for a, v in m.items()}
    if models == 0:
        verdict = "ABSTAIN"
        reason = "no_consistent_model"
    elif true_goal == models:
        verdict = "SUPPORTED"
        reason = "all_models_goal_true"
    elif false_goal == models:
        verdict = "CONTRADICTED"
        reason = "all_models_goal_false"
    else:
        verdict = "ABSTAIN"
        reason = "both_goal_values_possible"
    return {
        "verdict": verdict, "reason": reason,
        "models": models, "goal_true_models": true_goal,
        "goal_false_models": false_goal,
        "witness_goal_true": witness_true, "witness_goal_false": witness_false,
        "atoms": len(atoms),
    }
