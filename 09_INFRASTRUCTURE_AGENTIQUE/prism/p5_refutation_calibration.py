"""Exact certificate and routing comparison on the public P5V2-ADV-001 case."""
from itertools import product
import json
from math import factorial
from pathlib import Path

from planner import ROLE_ORDER, plan_mission

CASE_ID = "P5V2-ADV-001"
OBSERVED = (1, 2, 3)


def verdict_certificate(injective, noninjective):
    """Check two candidate tables on a shared, consecutively labelled domain."""
    size = len(injective)
    if size < 4 or len(noninjective) != size:
        return False
    if any(table[:3] != OBSERVED or any(type(y) is not int or not 0 <= y < size for y in table)
           for table in (injective, noninjective)):
        return False
    return len(set(injective)) == size and len(set(noninjective)) < size


def audit():
    path = Path(__file__).resolve().parents[1] / "evaluation/holdout_v0_2/cases.jsonl"
    case = next(row for row in map(json.loads, path.read_text(encoding="utf-8").splitlines())
                if row["case_id"] == CASE_ID)
    mission = {"question": case["prompt"], "mission_type": "mathematical"}
    def active(plan):
        return [task["role"] for task in plan["tasks"]]

    fixed = list(ROLE_ORDER)
    adaptive = active(plan_mission(mission))
    adaptive_computation = active(plan_mission({**mission, "requires_computation": True}))

    sizes = []
    for size in range(4, 8):
        total = positive = 0
        for tail in product(range(size), repeat=size - len(OBSERVED)):
            total += 1
            positive += len(set(OBSERVED + tail)) == size
        if total != size ** (size - 3) or positive != factorial(size - 3):
            raise AssertionError("enumeration disagrees with the counting argument")
        sizes.append({"size": size, "total": total, "injective": positive,
                      "noninjective": total - positive})

    positive = (1, 2, 3, 0)
    negative = (1, 2, 3, 1)
    if not verdict_certificate(positive, negative):
        raise AssertionError("valid witness pair rejected")
    invalid = (
        (positive, positive),                   # no collision
        (positive, (1, 2, 3, 4)),               # image outside domain
        (positive, (1, 2, 1, 1)),               # contradicts the observations
        (positive, (1, 2, 3, 1, 1)),            # different domains
        ((1, 2, 3, False), negative),          # a boolean is not a state label
    )
    if any(verdict_certificate(*pair) for pair in invalid):
        raise AssertionError("invalid witness pair accepted")
    return {
        "case_id": CASE_ID,
        "scope": "public calibration, exact witnesses and routing only",
        "fixed_B": fixed,
        "adaptive_C_mathematical_default": adaptive,
        "adaptive_C_explicit_computation": adaptive_computation,
        "witnesses": {"injective": positive, "noninjective": negative},
        "extensions_by_size": sizes,
        "invalid_witness_pairs_rejected": len(invalid),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
