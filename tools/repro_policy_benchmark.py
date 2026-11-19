"""Deterministic policy comparison; simulated costs, not measured runtime.

The adaptive policy only reuses when an independently supplied equivalence
certificate covers the changed dependency. Without it, it recomputes.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    name: str
    changed: bool
    output_equivalent: bool
    certificate_valid: bool


CASES = (
    Case("unchanged", False, True, False),
    Case("sympy-equivalent-reviewed", True, True, True),
    Case("sympy-equivalent-unreviewed", True, True, False),
    Case("semantic-change", True, False, False),
)


def decide(policy, case):
    if policy == "strict":
        return "recompute" if case.changed else "reuse"
    if policy == "fast":
        return "reuse"
    if policy == "adaptive":
        return "reuse" if not case.changed or (
            case.certificate_valid and case.output_equivalent) else "recompute"
    raise ValueError("unknown policy")


def evaluate(cases=CASES, verify_cost=1, recompute_cost=10):
    if verify_cost < 0 or recompute_cost < 0:
        raise ValueError("costs must be nonnegative")
    result = {}
    for policy in ("strict", "fast", "adaptive"):
        recomputes = wrong_reuses = 0
        for case in cases:
            action = decide(policy, case)
            recomputes += action == "recompute"
            wrong_reuses += action == "reuse" and not case.output_equivalent
        checks = sum(c.changed for c in cases) if policy == "adaptive" else 0
        result[policy] = {"recomputes": recomputes,
                          "wrong_reuses": wrong_reuses,
                          "simulated_cost": recomputes * recompute_cost +
                                            checks * verify_cost}
    return result
