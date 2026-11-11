"""Equal-budget finite identification benchmark against Omega's actual planner.

This is a public synthetic benchmark, NOT an LLM experiment or a blind
generalization test. Both planners know the same observation table; both
receive a hard cap of two binary tests per hidden hypothesis.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
import hashlib
import json
import random

from action_planning_two_step import optimize_policy

FROZEN_SHA256 = "6b7e3f2c7392c61206d7ad86ea86e5a2ad738f94a5e4a4678ea03452da6f2faa"


def make_cases(seed=20261111):
    r = random.Random(seed)
    cases = []
    for k in range(200):
        n = r.randrange(5, 10)
        m = r.randrange(3, 7)
        columns = []
        for j in range(m):
            col = [str(r.randrange(2)) for _ in range(n)]
            if len(set(col)) == 1:
                col[0] = "1" if col[0] == "0" else "0"
            columns.append(col)
        cases.append({"id":f"R{k:03}", "kind":"random",
                      "n":n, "observations":columns})
    for k in range(60):
        base = [[0,0,0,1,1,1],
                [0,1,1,0,0,0],
                [0,0,0,0,1,1]]
        permutation = list(range(6))
        r.shuffle(permutation)
        columns = []
        for original in base:
            flip = r.randrange(2)
            columns.append([str(original[i] ^ flip) for i in permutation])
        r.shuffle(columns)
        cases.append({"id":f"C{k:03}", "kind":"conditional_constructed",
                      "n":6, "observations":columns})
    return cases


def case_digest(cases):
    raw = json.dumps(cases, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def to_omega_case(item):
    return {
        "case_id": "budget-" + item["id"],
        "question": "Identifier une hypothese parmi les candidates.",
        "mission_type": "mathematical",
        "uncertainty": "Une observation est necessaire.",
        "hypotheses": [
            {"id":f"h{i}", "decision":f"d{i}", "weight":1}
            for i in range(item["n"])
        ],
        "checks": [
            {"id":f"c{j}", "action":"verify", "step":f"Tester c{j}",
             "method":"synthetic_binary", "available":True,
             "cost_milli":0, "observations":observations}
            for j, observations in enumerate(item["observations"])
        ]
    }


def fixed_best(item):
    """Independent exhaustive best non-conditional pair, not a strawman."""
    n = item["n"]
    columns = item["observations"]
    scores = []
    for pair in combinations(range(len(columns)), 2):
        signatures = {tuple(columns[j][i] for j in pair) for i in range(n)}
        scores.append((len(signatures), pair))
    return sorted(scores, key=lambda x:(-x[0],x[1]))[0]


def conditional_oracle(item):
    """Independent enumeration of all first tests and branch-specific seconds."""
    n = item["n"]
    columns = item["observations"]
    possibilities = []
    for first in range(len(columns)):
        groups = defaultdict(list)
        for i in range(n):
            groups[columns[first][i]].append(i)
        nonempty_leaves = 0
        for group in groups.values():
            best = max(
                len({columns[second][i] for i in group})
                for second in range(len(columns)) if second != first
            )
            nonempty_leaves += best
        possibilities.append(nonempty_leaves)
    return max(possibilities)


def realized_omega(item, policy):
    """Actually route every possible hidden state through the policy tree."""
    n = item["n"]
    columns = item["observations"]
    good = 0
    steps = 0
    for hidden in range(n):
        still = list(range(n))
        used = set()
        node = policy
        while "check_id" in node:
            check = int(node["check_id"][1:])
            assert check not in used and len(used) < 2
            used.add(check)
            outcome = columns[check][hidden]
            still = [i for i in still if columns[check][i] == outcome]
            node = node["branches"][outcome]
        assert hidden in still
        good += (hidden == min(still))  # deterministic MAP tie breaking
        steps += len(used)
    return good, steps


def run_benchmark():
    cases = make_cases()
    digest = case_digest(cases)
    assert digest == FROZEN_SHA256, (digest, FROZEN_SHA256)
    totals = defaultdict(lambda: {"cases":0, "hidden_states":0,
                                  "direct_correct":0, "fixed_correct":0,
                                  "omega_correct":0, "improved_cases":0,
                                  "omega_checks":0, "oracle_matches":0})
    for item in cases:
        n = item["n"]
        fixed_correct, fixed_pair = fixed_best(item)
        oracle = conditional_oracle(item)
        model = to_omega_case(item)
        omega = optimize_policy(model, max_depth=2, max_cost_milli=0)
        achieved, used = realized_omega(item, omega["policy"])
        assert Fraction(1) - Fraction(omega["expected_decision_risk"]) == Fraction(achieved,n)
        assert achieved == oracle, (item["id"],achieved,oracle)
        assert achieved >= fixed_correct
        # Fixed signatures are the exact number of correct MAP decisions.
        assert fixed_correct == len({
            tuple(item["observations"][j][i] for j in fixed_pair)
            for i in range(n)
        })
        t = totals[item["kind"]]
        t["cases"] += 1
        t["hidden_states"] += n
        t["direct_correct"] += 1  # no checks, all labels distinct
        t["fixed_correct"] += fixed_correct
        t["omega_correct"] += achieved
        t["improved_cases"] += (achieved > fixed_correct)
        t["omega_checks"] += used
        t["oracle_matches"] += 1
    report = {"status":"SYNTHETIC_PUBLIC_NOT_BLIND",
              "model_calls":0, "real_observation_calls":0,
              "seed":20261111, "cases_sha256":digest,
              "max_binary_tests_per_hidden_state":2,
              "objective":"correct classification of hidden unique label, exact uniform prior, tests cost zero",
              "arms":["no-check","globally optimal fixed pair",
                      "Omega optimize_policy depth 2 with conditional second test"],
              "strata":dict(totals)}
    return report


if __name__ == "__main__":
    print(json.dumps(run_benchmark(),ensure_ascii=False,indent=2,sort_keys=True))
