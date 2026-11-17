"""OMEGA-PROVENANCE-ORACLE-06: exact adaptive provenance certificates.

SYNTHETIC lab only. Four artifact identities, fifteen possible set partitions,
six binary paid same_execution_origin probes, threshold >=3 distinct origins.
An exact Bellman decision policy is compared with three frozen heuristics.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random

EXPERIMENT = "OMEGA-PROVENANCE-ORACLE-06"
PREREG_COMMIT = "ce03dc1af00af9521a3ca7ddc80993d2718d5091"
QUESTION_PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
ACTIONS = ("EXACT_VERDICT_ORACLE", "CHEAP_FIRST",
           "PARTITION_SPLIT_PER_COST", "DECISION_GAIN_PER_COST")
COST_SEED_BASE = 58301
CALIBRATION_CASES = tuple(range(12))
HOLDOUT_CASES = tuple(range(100, 124))
THRESHOLD = 3


def sha_obj(obj):
    return sha256(json.dumps(obj, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def canonical_partitions():
    """Restricted-growth strings, each Bell(4) partition exactly once."""
    rows = [(0,)]
    for _ in range(3):
        rows = [part + (next_class,)
                for part in rows
                for next_class in range(max(part) + 2)]
    result = tuple(sorted(rows))
    assert len(result) == 15 and len(set(result)) == 15
    return result


PARTITIONS = canonical_partitions()


def distinct_origins(partition):
    return len(set(partition))


def certified_goal(partition):
    return distinct_origins(partition) >= THRESHOLD


def priced_questions(index):
    if not isinstance(index, int) or index < 0:
        raise ValueError("INVALID_SCENARIO_INDEX")
    rng = random.Random(COST_SEED_BASE + index)
    return tuple(rng.randint(1, 12) for _ in QUESTION_PAIRS)


def paid_same_execution_origin(hidden, question):
    """Idealized paid retrieval of a trustworthy source-origin comparison."""
    i, j = question
    return int(hidden[i] == hidden[j])


class Unresolved(RuntimeError):
    pass


class ProvenanceOracle:
    def __init__(self, partitions=PARTITIONS, pairs=QUESTION_PAIRS, costs=None):
        self.partitions = tuple(tuple(row) for row in partitions)
        self.pairs = tuple(tuple(q) for q in pairs)
        self.costs = tuple(costs if costs is not None else [1] * len(self.pairs))
        if not 2 <= len(self.partitions) <= 15:
            raise ValueError("BAD_NUMBER_OF_HYPOTHESES")
        if len(set(self.partitions)) != len(self.partitions):
            raise ValueError("DUPLICATE_HYPOTHESIS")
        if not self.pairs or len(set(self.pairs)) != len(self.pairs):
            raise ValueError("DUPLICATE_OR_EMPTY_QUERIES")
        if any(len(x) != 4 or x[0] != 0 or any(
                k > max(x[:i]) + 1 for i, k in enumerate(x) if i)
                for x in self.partitions):
            raise ValueError("NOT_CANONICAL_PARTITIONS")
        if any(len(p) != 2 or not 0 <= p[0] < p[1] < 4 for p in self.pairs):
            raise ValueError("INVALID_PAIR")
        if len(self.costs) != len(self.pairs) or any(
                type(v) is not int or v <= 0 for v in self.costs):
            raise ValueError("INVALID_PRICE")
        self.n = len(self.partitions)
        self.full_mask = (1 << self.n) - 1
        self.truth = tuple(certified_goal(x) for x in self.partitions)
        self.ones = []
        for p in self.pairs:
            mask = 0
            for idx, world in enumerate(self.partitions):
                if world[p[0]] == world[p[1]]:
                    mask |= 1 << idx
            self.ones.append(mask)
        self.values = {}
        self.decisions = {}
        self.cut_cache = {}

    def ids(self, mask):
        return [i for i in range(self.n) if mask & (1 << i)]

    def unanimous(self, mask):
        if not mask:
            raise AssertionError("EMPTY_BELIEF")
        ids = self.ids(mask)
        return all(self.truth[i] == self.truth[ids[0]] for i in ids)

    def cuts(self, mask):
        if mask not in self.cut_cache:
            options = []
            for q, ones in enumerate(self.ones):
                branch1 = mask & ones
                if branch1 and branch1 != mask:
                    options.append((q, mask ^ branch1, branch1))
            self.cut_cache[mask] = tuple(options)
        return self.cut_cache[mask]

    def value(self, mask):
        if mask in self.values:
            return self.values[mask]
        if self.unanimous(mask):
            self.values[mask] = 0
            return 0
        choices = self.cuts(mask)
        if not choices:
            raise Unresolved("UNRESOLVED_NOT_CERTIFIED")
        n = mask.bit_count()
        rated = []
        for q, zero, one in choices:
            total = (n * self.costs[q] +
                     self.value(zero) + self.value(one))
            rated.append((total, self.pairs[q], q))
        best_cost, _, best_q = min(rated)
        self.values[mask] = best_cost
        self.decisions[mask] = best_q
        return best_cost

    def solve(self):
        return self.value(self.full_mask)

    def greedy_query(self, policy, mask):
        cuts = self.cuts(mask)
        if not cuts:
            raise Unresolved("UNRESOLVED_NOT_CERTIFIED")
        if policy == "CHEAP_FIRST":
            return min(cuts, key=lambda v: (self.costs[v[0]],
                                             self.pairs[v[0]]))[0]
        n = mask.bit_count()
        def split_ratio(v):
            q, zero, one = v
            return Fraction(zero.bit_count() * one.bit_count(),
                            self.costs[q])
        if policy == "PARTITION_SPLIT_PER_COST":
            return min(cuts, key=lambda v: (-split_ratio(v), self.pairs[v[0]]))[0]
        if policy == "DECISION_GAIN_PER_COST":
            pos = sum(self.truth[i] for i in self.ids(mask))
            neg = n - pos
            def impurity_gain(v):
                q, zero, one = v
                a = zero.bit_count()
                b = one.bit_count()
                pos_a = sum(self.truth[i] for i in self.ids(zero))
                pos_b = sum(self.truth[i] for i in self.ids(one))
                # Proportional to the expected Gini decrease. Multiplicative
                # factor 2/n is the same across candidate questions.
                gain = (Fraction(pos * neg, n) -
                        Fraction(pos_a * (a - pos_a), a) -
                        Fraction(pos_b * (b - pos_b), b))
                if gain < 0:
                    raise AssertionError("IMPURITY_CANNOT_INCREASE")
                return gain / self.costs[q]
            rated = [(impurity_gain(v), v) for v in cuts]
            max_gain = max(gain for gain, _ in rated)
            if max_gain == 0:
                return min(cuts, key=lambda v: (-split_ratio(v),
                                                self.pairs[v[0]]))[0]
            return min((v for gain,v in rated if gain == max_gain),
                       key=lambda v: self.pairs[v[0]])[0]
        raise ValueError("UNKNOWN_POLICY")

    def episode(self, hidden_index, policy, paid_probe=None):
        if not 0 <= hidden_index < self.n:
            raise ValueError("INVALID_HIDDEN_WORLD")
        if policy not in ACTIONS:
            raise ValueError("UNKNOWN_POLICY")
        hidden = self.partitions[hidden_index]
        if policy == "EXACT_VERDICT_ORACLE":
            self.solve()
        paid = paid_probe or paid_same_execution_origin
        mask = self.full_mask
        visited = set()
        history = []
        while not self.unanimous(mask):
            if policy == "EXACT_VERDICT_ORACLE":
                q = self.decisions[mask]
            else:
                q = self.greedy_query(policy, mask)
            if q in visited:
                raise AssertionError("REPEATED_PAID_PROBE")
            visited.add(q)
            before = self.ids(mask)
            observed = paid(hidden, self.pairs[q])
            # The simulator truth is checked only AFTER the paid response.
            if type(observed) is not int or observed not in (0, 1):
                raise AssertionError("INVALID_PAID_ORIGIN_RESPONSE")
            if observed != paid_same_execution_origin(hidden, self.pairs[q]):
                raise AssertionError("FORGED_PAID_ORIGIN_RESPONSE")
            next_mask = mask & self.ones[q] if observed else mask & ~self.ones[q]
            if not next_mask or next_mask == mask:
                raise AssertionError("INCONSISTENT_PAID_ORIGIN_RESPONSE")
            if not next_mask & (1 << hidden_index):
                raise AssertionError("TRUE_WORLD_LOST_AFTER_PAYMENT")
            history.append({
                "question": list(self.pairs[q]),
                "answer_same_origin": observed,
                "price_paid": self.costs[q],
                "belief_before": before,
                "belief_after": self.ids(next_mask),
            })
            mask = next_mask
            if len(history) > len(self.pairs):
                raise AssertionError("TOO_MANY_PROBES")
        verdict = self.truth[self.ids(mask)[0]]
        if verdict != certified_goal(hidden):
            raise AssertionError("FALSE_PROVENANCE_CERTIFICATE")
        return {
            "hidden_index": hidden_index,
            "status": "CERTIFIED",
            "verdict_at_least_three_origins": verdict,
            "actual_distinct_origins": distinct_origins(hidden),
            "total_price": sum(row["price_paid"] for row in history),
            "queries_paid": len(history),
            "remaining_hypotheses": self.ids(mask),
            "log": history,
        }

    def all_paths(self, policy):
        return [self.episode(index, policy) for index in range(self.n)]


def evaluate(index):
    costs = priced_questions(index)
    model = ProvenanceOracle(costs=costs)
    optimal = model.solve()
    paths = {name: model.all_paths(name) for name in ACTIONS}
    sums = {name: sum(row["total_price"] for row in episodes)
            for name, episodes in paths.items()}
    if sums["EXACT_VERDICT_ORACLE"] != optimal:
        raise AssertionError("BELLMan_PATH_COST_MISMATCH")
    if any(optimal > sums[name] for name in ACTIONS):
        raise AssertionError("ALLEGED_OPTIMUM_COST_MORE_THAN_BASELINE")
    if any(row["status"] != "CERTIFIED"
           for episodes in paths.values() for row in episodes):
        raise AssertionError("NONCERTIFIED_PATH")
    depths = {name: max(row["queries_paid"] for row in episodes)
              for name, episodes in paths.items()}
    return {
        "index": index, "pair_costs": list(costs),
        "partitions_sha256": sha_obj(PARTITIONS),
        "optimal_cost_numerator": optimal,
        "optimal_first_question": list(
            model.pairs[model.decisions[model.full_mask]]),
        "states_evaluated": len(model.values),
        "cost_sums_all_15_partitions": sums,
        "uniform_expected_cost": {name: sums[name] / len(PARTITIONS)
                                  for name in ACTIONS},
        "max_probe_depth": depths,
        "paths": paths,
    }


def summarize(rows):
    bests = [min(row["cost_sums_all_15_partitions"][name] for name in
                 ACTIONS if name != "EXACT_VERDICT_ORACLE") for row in rows]
    opts = [row["optimal_cost_numerator"] for row in rows]
    gaps = [best - opt for best,opt in zip(bests, opts)]
    at_least = sum(10*gap >= opt for gap,opt in zip(gaps,opts))
    greater = sum(10*gap > opt for gap,opt in zip(gaps,opts))
    if at_least >= 6:
        status = "MEASURABLE_PROVENANCE_HEADROOM"
    elif greater == 0:
        status = "NEAR_BEST_BASELINE_IN_THIS_SYNTHETIC_BENCHMARK"
    else:
        status = "MIXED_HEADROOM"
    summary = {
        "cases": len(rows), "worlds_per_case": len(PARTITIONS),
        "cost_mean_uniform": {
            name: sum(row["cost_sums_all_15_partitions"][name]
                      for row in rows) / (len(PARTITIONS)*len(rows))
            for name in ACTIONS
        },
        "best_baseline_mean_uniform": sum(bests)/(len(PARTITIONS)*len(rows)),
        "headroom_at_least_10pct": at_least,
        "headroom_strictly_over_10pct": greater,
        "mean_headroom_to_best_baseline": sum(gaps)/(len(PARTITIONS)*len(rows)),
        "max_headroom_to_best_baseline": max(gaps)/len(PARTITIONS),
        "max_probes_across_all_trajectories": max(
            max(row["max_probe_depth"].values()) for row in rows),
        "total_bellman_states": sum(row["states_evaluated"] for row in rows),
    }
    return status, summary


def conduct(mode):
    if mode not in ("calibration", "holdout"):
        raise ValueError("UNKNOWN_MODE")
    ids = CALIBRATION_CASES if mode == "calibration" else HOLDOUT_CASES
    rows = [evaluate(index) for index in ids]
    status, summary = summarize(rows)
    return {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG_COMMIT,
        "mode": mode, "status": status,
        "target": "at least 3 independent origin runs among 4 evidence items",
        "world_type": "synthetic Bell(4) partitions, uniform prior",
        "partitions": [list(x) for x in PARTITIONS],
        "partition_sha256": sha_obj(PARTITIONS),
        "questions": [list(x) for x in QUESTION_PAIRS],
        "cost_seed_formula": "58301+index; six randint(1,12)",
        "case_ids": list(ids),
        "benchmark_identity": sha_obj({"partitions": PARTITIONS,
                                      "questions": QUESTION_PAIRS,
                                      "case_ids": ids,
                                      "costs": [priced_questions(i) for i in ids]}),
        "policies": list(ACTIONS), "summary": summary,
        "trials": rows, "no_paid_api": True, "main_modified": False,
        "trained_policies": False, "actual_github_provenance_verified": False,
        "generalization_proven": False,
        "limitations": [
            "Synthetic origin equivalence partitions; not raw GitHub logs.",
            "All six pairwise origin checks are assumed perfectly reliable.",
            "Uniform prior is not a measured frequency of duplicate proofs.",
            "The measured costs are synthetic audit efforts, not compute or cash.",
            "Heldout cost vectors are new but the fifteen partition structures are shared.",
            "Exact oracle CPU cost is not normalized with heuristic CPU costs.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("calibration","holdout"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = conduct(args.mode)
    raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment": EXPERIMENT, "mode": args.mode,
        "status": report["status"], "summary": report["summary"],
        "report_sha256": sha256(raw).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
