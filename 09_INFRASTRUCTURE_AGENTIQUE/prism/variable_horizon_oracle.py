"""Independent exhaustive small-policy verifier for the variable-horizon Omega experiment.

Enumerates contingent decision trees explicitly; DOES NOT use optimize_policy,
its cache, recursion recurrence, or priority rules. Intended for <=3 checks.
Larger parity constructions use direct combinatorial certificates instead.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product

from action_selection import _validate
from action_planning_two_step import optimize_policy
from action_planning_challenge import make_challenge_cases, make_seeded_stress_cases


def _stop_error(hypotheses, ids):
    decision_weight = Counter()
    for i in ids:
        decision_weight[hypotheses[i]["decision"]] += hypotheses[i]["weight"]
    return sum(decision_weight.values()) - max(decision_weight.values())


def enumerate_policies(case, *, depth, max_cost_milli=4000):
    """Brute force all conditional policies including STOP on every branch.

    Each yielded candidate is a (classification-miss-mass, cost-mass,
    expected-check-mass, root-check-ID) tuple. This is intentionally
    unoptimized and should only be applied to tiny trees.
    """
    hypotheses, checks = _validate(case)
    if len(checks) > 3:
        raise ValueError("independent enumerator restricted to <=3 checks")
    total_weight = sum(h["weight"] for h in hypotheses)
    ordered = tuple(sorted(
        (i for i, c in enumerate(checks) if c["available"]),
        key=lambda i: checks[i]["id"],
    ))
    def walk(indices, rest, steps, budget):
        mass = sum(hypotheses[i]["weight"] for i in indices)
        yield (Fraction(_stop_error(hypotheses, indices)),
               Fraction(0), Fraction(0), None)
        if steps <= 0:
            return
        for ci in rest:
            check = checks[ci]
            if check["cost_milli"] > budget:
                continue
            separated = defaultdict(list)
            for i in indices:
                separated[check["observations"][i]].append(i)
            options = [
                list(walk(tuple(separated[out]), tuple(x for x in rest if x != ci),
                          steps - 1, budget - check["cost_milli"]))
                for out in sorted(separated)
            ]
            for choice in product(*options):
                missed = sum((item[0] for item in choice), Fraction(0))
                cost = Fraction(mass * check["cost_milli"], 1000) + sum(
                    (item[1] for item in choice), Fraction(0))
                count = Fraction(mass) + sum(
                    (item[2] for item in choice), Fraction(0))
                yield (missed, cost, count, check["id"])
    return min(
        walk(tuple(range(len(hypotheses))), ordered, depth, max_cost_milli),
        key=lambda x: (x[0] + x[1], x[3] is not None, x[3] or ""),
    ), total_weight


def evaluate_independent_oracle(cases):
    stats = Counter()
    snapshots = []
    for case in cases:
        for depth in (0, 1, 2, 3):
            oracle, mass = enumerate_policies(case, depth=depth)
            optimized = optimize_policy(case, max_depth=depth)
            expected_loss = (oracle[0] + oracle[1]) / mass
            if Fraction(optimized["expected_total_loss"]) != expected_loss:
                raise AssertionError(f"{case['case_id']} depth={depth}: loss mismatch")
            if Fraction(optimized["expected_steps"]) != oracle[2] / mass:
                raise AssertionError(f"{case['case_id']} depth={depth}: step mismatch")
            if optimized["policy"].get("check_id") != oracle[3]:
                raise AssertionError(f"{case['case_id']} depth={depth}: first check mismatch")
            stats["exact_matches"] += 1
        one = optimize_policy(case, max_depth=1)
        two = optimize_policy(case, max_depth=2)
        three = optimize_policy(case, max_depth=3)
        stats["cases"] += 1
        if Fraction(three["expected_total_loss"]) < Fraction(two["expected_total_loss"]):
            stats["depth3_better_than2"] += 1
        if Fraction(two["expected_total_loss"]) < Fraction(one["expected_total_loss"]):
            stats["depth2_better_than1"] += 1
        if case["case_id"].startswith("next-"):
            snapshots.append({
                "case": case["case_id"],
                "depth1": one["expected_total_loss"],
                "depth2": two["expected_total_loss"],
                "depth3": three["expected_total_loss"],
                "first_action": three["action"],
            })
    return {"statistics": dict(stats), "authored_examples": snapshots,
            "kind": "exact_synthetic_public_no_model_or_real_world_claim"}


def main():
    import json
    cases = make_challenge_cases() + make_seeded_stress_cases()
    print(json.dumps(evaluate_independent_oracle(cases),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
