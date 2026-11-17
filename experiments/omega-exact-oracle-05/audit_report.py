"""Independent structural auditor for a frozen exact-oracle report.

No import of ExactOracle or its Bellman recurrence is used here; tiny
independent brute-force tests in test_exact_oracle.py establish recurrence
correctness separately. Audit reconstructs each paid path from raw machines.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json


def frozen(model):
    return tuple(tuple(tuple(row) for row in block) for block in model)


def terminal_bit(model, word):
    transition, emission = model
    state = 0
    last = None
    for bit in word:
        assert bit in (0,1)
        last = emission[state][bit]
        state = transition[state][bit]
    return last


def audit(d):
    assert d["experiment"] == "OMEGA-EXACT-ORACLE-05"
    assert d["preregistered_commit"] == "dc02ab735e314b106868faa49b284fb4e77e4b9b"
    assert d["seeds"] == [57222, 57223]
    assert d["menu_size"] == 64
    assert d["pool_size"] == 32
    assert d["new_instances"] == 24 and len(d["trials"]) == 24
    assert d["policies"] == ["OPTIMUM","PRICE_AWARE","BALANCED"]
    assert d["tariffs"] == [[1,5],[5,1]]
    assert d["no_training"] and d["no_paid_api"] and not d["main_modified"]
    assert not d["generalization_proven"]
    assert d["eligible_new_models"] >= 32

    # Source-based pool/instance hashes must agree with the original arrays;
    # each trial carries all candidate models, but the 32-member pool itself
    # is not embedded as a separate array (its digest remains provenance).
    checksum = lambda v: sha256(json.dumps(v, separators=(",",":"),
                         sort_keys=True).encode()).hexdigest()
    assert d["instances_sha256"] == checksum(
        [x["candidates"] for x in d["trials"]])
    scores = []
    seen_primary_models = set()
    menu = set()
    for row in d["trials"]:
        i = row["index"]
        assert 0 <= i < 24
        tariff = [1,5] if i % 2 == 0 else [5,1]
        assert row["tariff"] == tariff
        models = row["candidates"]
        assert len(models) == 16 and len({frozen(x) for x in models}) == 16
        assert row["candidate_digest"] == checksum(models)
        secret = frozen(row["hidden_model"])
        assert secret in {frozen(x) for x in models}
        assert secret not in seen_primary_models
        seen_primary_models.add(secret)
        costs = row["cost_sums_all_16_worlds"]
        depths = row["max_query_depth"]
        means = row["mean_costs_uniform_16"]
        assert set(costs) == {"OPTIMUM","PRICE_AWARE","BALANCED"}
        assert all(costs[name] >= 0 for name in costs)
        assert row["oracle_numerator"] == costs["OPTIMUM"]
        assert costs["OPTIMUM"] <= costs["PRICE_AWARE"]
        assert costs["OPTIMUM"] <= costs["BALANCED"]
        assert 16 <= row["solver_state_count"] <= 65536
        assert len(row["witness_digest"]) == 64
        assert all(abs(means[name]-costs[name]/16)<1e-10 for name in costs)
        for policy in ("OPTIMUM","PRICE_AWARE","BALANCED"):
            paths = row["paths"][policy]
            assert len(paths) == 16
            observed_policy = {}
            paid_sum = 0
            max_depth = 0
            for path in paths:
                h = path["hidden_index"]
                assert 0 <= h < 16 and path["certified"]
                assert path["queries"] == len(path["history"]) <= 15
                live = set(range(16))
                questions = set()
                for event in path["history"]:
                    assert event["before"] == len(live)
                    query = tuple(event["word"])
                    assert len(query) == 10 and all(bit in (0,1) for bit in query)
                    assert query not in questions
                    questions.add(query)
                    menu.add(query)
                    assert event["price"] == sum(tariff[bit] for bit in query)
                    assert event["terminal_bit"] == terminal_bit(models[h], query)
                    descendants = {j for j in live
                                   if terminal_bit(models[j], query) ==
                                      event["terminal_bit"]}
                    assert 0 < len(descendants) < len(live)
                    assert event["after"] == len(descendants)
                    state = frozenset(live)
                    if state in observed_policy:
                        assert observed_policy[state] == query
                    else:
                        observed_policy[state] = query
                    live = descendants
                assert live == {h}
                assert path["cost"] == sum(x["price"] for x in path["history"])
                paid_sum += path["cost"]
                max_depth = max(max_depth, len(path["history"]))
            assert paid_sum == costs[policy]
            assert max_depth == depths[policy]
        firsts = {tuple(p["history"][0]["word"]) for p in row["paths"]["OPTIMUM"]}
        assert firsts == {tuple(row["oracle_root_word"])}
        assert row["budget_12_comparable"] == all(depth<=12 for depth in depths.values())
        scores.append(row)
    assert len(seen_primary_models) == 24
    # The menu may contain words not selected by any of the 24 decision trees.
    assert 1 <= len(menu) <= 64

    primary = d["primary"]
    assert primary["instances"] == 24
    assert primary["hidden_worlds_replayed_per_instance"] == 16
    avg = lambda name: sum(row["cost_sums_all_16_worlds"][name]
                           for row in scores) / (24*16)
    assert abs(primary["mean_optimal_uniform_cost"]-avg("OPTIMUM"))<1e-10
    assert abs(primary["mean_price_aware_uniform_cost"]-avg("PRICE_AWARE"))<1e-10
    assert abs(primary["mean_balanced_uniform_cost"]-avg("BALANCED"))<1e-10
    gaps = [row["cost_sums_all_16_worlds"]["PRICE_AWARE"]-
            row["oracle_numerator"] for row in scores]
    at_least = sum(gap*10>=row["oracle_numerator"] for gap,row in zip(gaps,scores))
    over = sum(gap*10>row["oracle_numerator"] for gap,row in zip(gaps,scores))
    count = sum(row["budget_12_comparable"] for row in scores)
    assert primary["instances_at_least_10pct_gap"] == at_least
    assert primary["instances_strictly_over_10pct_gap"] == over
    assert primary["budget12_comparable_instances"] == count
    assert primary["max_oracle_depth"] == max(
        row["max_query_depth"]["OPTIMUM"] for row in scores)
    assert primary["max_price_aware_depth"] == max(
        row["max_query_depth"]["PRICE_AWARE"] for row in scores)
    assert primary["total_oracle_states"] == sum(
        row["solver_state_count"] for row in scores)
    assert abs(primary["max_gap_cost_uniform"]-max(gaps)/16)<1e-10
    if at_least >= 6 and count == 24:
        expected = "HEADROOM_FOR_IMPROVEMENT"
    elif over == 0 and count == 24:
        expected = "NEAR_OPTIMUM_IN_THIS_BENCHMARK"
    else:
        expected = "MIXED_OR_INDETERMINATE"
    assert d["status"] == expected
    return {"status": expected, "uniform_optimum": avg("OPTIMUM"),
            "uniform_price_aware": avg("PRICE_AWARE"),
            "uniform_balanced": avg("BALANCED"),
            "headroom_cases": at_least, "budget12_comparable": count}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    raw = args.report.read_bytes()
    print("AUDITED_REPORT_SHA256", sha256(raw).hexdigest())
    print("INDEPENDENT_AUDIT", json.dumps(audit(json.loads(raw)),sort_keys=True))


if __name__ == "__main__":
    main()
