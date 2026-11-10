"""Independent public challenge: 24 NEW authored cases + 96 seeded stress cases.

Important: these cases are NOT a blinded human evaluation or hidden holdout.
A brute-force oracle enumerates every first test and every contingent second
test, independently of the optimizer's dynamic programming implementation.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from random import Random
import json

from action_selection import _validate, select_action
from action_planning_two_step import optimize_policy, plan_with_two_step_evidence


DOMAINS = (
    ("mathematical", "M", ("prouvee", "refutee")),
    ("documentary", "D", ("version_1", "version_2")),
    ("computational", "C", ("valid", "invalid")),
    ("exploratory", "E", ("hypothesis_A", "hypothesis_B")),
)


def _check(id_, action, observations, cost, *, available=True):
    return {
        "id": id_, "action": action, "step": "Contrôler " + id_,
        "method": "hypothetical_observation", "available": available,
        "cost_milli": cost, "observations": list(observations),
    }


def make_challenge_cases():
    all_cases = []
    for mission, letter, labels in DOMAINS:
        a, b = labels
        for pattern in range(6):
            if pattern == 1:  # Conditional tests are different in x vs y.
                decisions = [a, a, b, a, b, b]
                checks = [
                    _check("01-group", "verify", "xxxyyy", 15),
                    _check("02-local-x", "verify", "ppqppp", 70),
                    _check("03-local-y", "ask", "rrrrss", 70),
                ]
            else:
                decisions = [a, a, b, b] if pattern != 4 else [a] * 4
                if pattern == 0:  # Two zero-standalone-value tests complement.
                    checks = [
                        _check("01-parity", "verify", "xyxy", 10),
                        _check("02-offset", "ask", "xyyx", 10),
                    ]
                elif pattern == 2:
                    checks = [
                        _check("01-distractor", "ask", "xyxy", 10),
                        _check("02-decisive", "verify", "xxyy", 45),
                    ]
                elif pattern == 3:
                    checks = [
                        _check("01-uninformative", "verify", "xyxy", 10),
                        _check("02-uninformative", "ask", "xyxy", 30),
                    ]
                elif pattern == 4:
                    checks = [_check("01-redundant", "ask", "xxyy", 10)]
                else:  # Complementary but jointly too costly.
                    checks = [
                        _check("01-expensive", "verify", "xyxy", 300),
                        _check("02-expensive", "ask", "xyyx", 300),
                    ]
            all_cases.append({
                "case_id": f"next-{letter}-{pattern + 1:02d}",
                "question": f"Décider le problème fictif {letter}-{pattern + 1}.",
                "mission_type": mission,
                "uncertainty": "Le modèle admet plusieurs conclusions distinctes.",
                "hypotheses": [
                    {"id": f"h{i}", "decision": decision, "weight": 1}
                    for i, decision in enumerate(decisions)
                ],
                "checks": checks,
            })
    return all_cases


def make_seeded_stress_cases(count=96):
    rng = Random(20261110)
    cases = []
    for k in range(count):
        mission, letter, labels = DOMAINS[k % len(DOMAINS)]
        n = rng.randint(4, 7)
        decisions = [rng.choice(labels) for _ in range(n)]
        checks = []
        for j in range(3):
            checks.append(_check(
                f"{j + 1:02d}-test", "verify" if j % 2 == 0 else "ask",
                [rng.choice("xyz") for _ in range(n)],
                rng.randint(10, 350), available=rng.random() >= .15,
            ))
        cases.append({
            "case_id": f"stress-{letter}-{k:03d}",
            "question": f"Choix fictif pré-généré {letter}-{k}.",
            "mission_type": mission,
            "uncertainty": "Décision incertaine dans le modèle pondéré.",
            "hypotheses": [
                {"id": f"h{i}", "decision": d, "weight": rng.randint(1, 3)}
                for i, d in enumerate(decisions)
            ],
            "checks": checks,
        })
    return cases


def _bayes_missed(hypotheses, indices):
    counts = Counter()
    for i in indices:
        h = hypotheses[i]
        counts[h["decision"]] += h["weight"]
    return sum(counts.values()) - max(counts.values())


def _split(indices, check):
    groups = defaultdict(list)
    for i in indices:
        groups[check["observations"][i]].append(i)
    return [(name, tuple(groups[name])) for name in sorted(groups)]


def exhaustive_policy_reference(case, *, depth):
    """Enumerate EVERY first test and contingent second choice, no recursion.

    The reference does not call the optimizer, share its dynamic program
    or rely on its action-selection rules, except input validation.
    """
    if type(depth) is not int or depth not in (1, 2):
        raise ValueError("depth must be 1 or 2")
    hypotheses, checks = _validate(case)
    indices = tuple(range(len(hypotheses)))
    total = sum(h["weight"] for h in hypotheses)
    initial = Fraction(_bayes_missed(hypotheses, indices))
    best = initial
    best_check = None
    best_branches = {}
    available = sorted(
        (i for i, c in enumerate(checks) if c["available"]),
        key=lambda i: checks[i]["id"],
    )
    for first in available:
        partitions = _split(indices, checks[first])
        choices = [None] + [
            j for j in available if j != first
        ] if depth == 2 else [None]
        # Full enumeration of the Cartesian product of outcome-contingent plans.
        for followups in product(choices, repeat=len(partitions)):
            cost = Fraction(total * checks[first]["cost_milli"], 1000)
            error = 0
            branches = {}
            for (outcome, subset), second in zip(partitions, followups):
                if second is None:
                    error += _bayes_missed(hypotheses, subset)
                    branches[outcome] = None
                else:
                    branch_mass = sum(hypotheses[i]["weight"] for i in subset)
                    cost += Fraction(branch_mass * checks[second]["cost_milli"], 1000)
                    error += sum(
                        _bayes_missed(hypotheses, piece)
                        for _, piece in _split(subset, checks[second])
                    )
                    branches[outcome] = checks[second]["id"]
            total_loss = Fraction(error) + cost
            if total_loss < best:  # stopping wins ties; IDs iterate lexical.
                best = total_loss
                best_check = first
                best_branches = branches
    action = ("answer" if initial == 0 else "insufficient_evidence") if best_check is None else checks[best_check]["action"]
    return {
        "action": action,
        "check_id": None if best_check is None else checks[best_check]["id"],
        "objective": str(best / total),
        "branches": best_branches,
    }


def assess(cases):
    totals = Counter()
    examples = []
    for case in cases:
        one = optimize_policy(case, max_depth=1)
        two = optimize_policy(case, max_depth=2)
        reference_one = exhaustive_policy_reference(case, depth=1)
        reference_two = exhaustive_policy_reference(case, depth=2)
        expected_one = select_action(case)
        if one["expected_total_loss"] != reference_one["objective"]:
            raise AssertionError("one-step independent oracle mismatch: " + case["case_id"])
        if two["expected_total_loss"] != reference_two["objective"]:
            raise AssertionError("two-step independent oracle mismatch: " + case["case_id"])
        if one["action"] != reference_one["action"] or two["action"] != reference_two["action"]:
            raise AssertionError("first-action disagreement: " + case["case_id"])
        first_id = two["policy"].get("check_id")
        if first_id != reference_two["check_id"]:
            raise AssertionError("first-check disagreement: " + case["case_id"])
        if one["action"] != expected_one["action"]:
            raise AssertionError("legacy one-step disagreement: " + case["case_id"])
        if one["policy"].get("check_id") != expected_one["chosen_check"]:
            raise AssertionError("legacy one-step check disagreement: " + case["case_id"])
        if Fraction(two["expected_total_loss"]) > Fraction(one["expected_total_loss"]):
            raise AssertionError("deeper planning has higher loss: " + case["case_id"])
        gain = Fraction(one["expected_total_loss"]) - Fraction(two["expected_total_loss"])
        totals["cases"] += 1
        totals["oracle_agreements"] += 1
        if gain > 0:
            totals["two_step_better"] += 1
        else:
            totals["equal"] += 1
        if one["action"] == "insufficient_evidence" and two["action"] in ("verify", "ask"):
            totals["rescued_abstentions"] += 1
        if two["action"] in ("verify", "ask"):
            result = plan_with_two_step_evidence(case)
            if result["p1"]["next_action"]["action"] != two["action"]:
                raise AssertionError("P1 mismatch")
        if case["case_id"].startswith("next-"):
            examples.append({
                "id": case["case_id"], "one": one["action"],
                "two": two["action"], "first": first_id,
                "one_loss": one["expected_total_loss"],
                "two_loss": two["expected_total_loss"],
                "improvement": str(gain),
            })
    return {**totals, "examples": examples}


def evaluate():
    challenge = assess(make_challenge_cases())
    stress = assess(make_seeded_stress_cases())
    return {
        "kind": "public_synthetic_nonblind_exact_policy_comparison",
        "challenge": challenge, "stress": {k: v for k, v in stress.items() if k != "examples"},
        "limits": ("Models and costs are hypothetical. These scenarios do not measure "
                   "quality on real research tasks, model reliability, latency or euros."),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
