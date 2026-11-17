"""Exact expected-cost decision-tree oracle for a finite, public candidate set.

Bellman numerator: V(S) = min_q (|S|*price(q) + V(S0) + V(S1)).
This is an offline mathematical reference, NOT an adaptive trained policy.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-cost-to-go-04"))
import cost_to_go as previous

s = previous.s
contrast = previous.previous
EXPERIMENT = "OMEGA-EXACT-ORACLE-05"
PREREG_COMMIT = "dc02ab735e314b106868faa49b284fb4e77e4b9b"
POOL_SEED = 57222
INSTANCE_SEED = 57223
POOL_N = 32
TEST_N = 24
N_CANDIDATES = 16
MAX_QUERIES = 12
MAX_STATES = 65536
TARIFFS = ((1, 5), (5, 1))
POLICIES = ("OPTIMUM", "PRICE_AWARE", "BALANCED")


def digest(payload):
    return sha256(json.dumps(payload, separators=(",", ":"),
                             sort_keys=True).encode()).hexdigest()


def fresh_evaluation_pool(space, menu):
    old_pools, _, _, _ = previous.fresh_pools(space, menu)
    prior_pools, _, _ = contrast.partition_models(space, menu)
    exclusions = set(old_pools["train"] + old_pools["test"])
    exclusions |= set(prior_pools["train"] +
                      prior_pools["calib"] + prior_pools["test"])
    exclusions |= {s.canonical(s.delayed_marker(seq))
                   for seq in product(s.ALPHABET, repeat=3)}
    pr145, _ = contrast.a.new_cohort(space)
    pr157_train, pr157_test, _, _ = contrast.old.select_cohorts(space)
    pr158_train, pr158_test, _, _ = contrast.previous.select_new_cohorts(space)
    exclusions |= set(pr145 + pr157_train + pr157_test +
                      pr158_train + pr158_test)
    unique = {}
    for m in sorted(space):
        if len(m[0]) != 3 or not contrast.a.distinguishable(m) or m in exclusions:
            continue
        signature = tuple(s.trace(m, q)[-1] for q in menu)
        if not any(signature) or all(signature):
            continue
        unique.setdefault(signature, m)
    eligible = sorted(unique.values())
    if len(eligible) < POOL_N:
        raise RuntimeError("INSUFFICIENT_NEW_MODELS")
    random.Random(POOL_SEED).shuffle(eligible)
    pool = eligible[:POOL_N]
    assert len(set(pool)) == POOL_N
    assert not (set(pool) & exclusions)
    return pool, len(eligible), len(exclusions)


def build_instances(pool):
    if len(pool) != POOL_N:
        raise ValueError("BAD_POOL")
    rows = []
    for i in range(TEST_N):
        rng = random.Random(INSTANCE_SEED + 2000 + i)
        actual = pool[i]
        distractors = rng.sample([m for m in pool if m != actual], N_CANDIDATES - 1)
        candidates = [actual] + distractors
        rng.shuffle(candidates)
        assert len(set(candidates)) == N_CANDIDATES
        rows.append({"index": i, "hidden": actual,
                     "candidates": candidates, "tariff": TARIFFS[i % 2]})
    return rows


class IndistinguishableError(RuntimeError):
    pass


def code_length_numerator(n):
    """Optimal external path length with n equiprobable leaves, unit-price binary tests.

    For n=1 => 0. For n=2^k+r, 0<=r<2^k:
    sum of leaf depths = k*n + 2*r.
    """
    if n <= 1:
        return 0
    k = n.bit_length() - 1
    return k * n + 2 * (n - (1 << k))


class ExactOracle:
    def __init__(self, words, outputs, prices):
        self.words = tuple(tuple(x) for x in words)
        self.outputs = tuple(tuple(y) for y in outputs)
        self.prices = tuple(prices)
        self.n = len(self.outputs)
        if not 2 <= self.n <= 16:
            raise ValueError("NUMBER_OF_HYPOTHESES_MUST_BE_2_TO_16")
        if not self.words or len(set(self.words)) != len(self.words):
            raise ValueError("DUPLICATE_OR_EMPTY_WORDS")
        if len(self.prices) != len(self.words) or any(
                not isinstance(c, int) or c <= 0 for c in self.prices):
            raise ValueError("INVALID_PRICES")
        if any(len(row) != len(self.words) or any(v not in (0, 1) for v in row)
               for row in self.outputs):
            raise ValueError("INVALID_BINARY_PREDICTIONS")
        signatures = list(self.outputs)
        if len(set(signatures)) != self.n:
            raise IndistinguishableError("DUPLICATE_OBSERVATIONAL_SIGNATURE")
        self.full = (1 << self.n) - 1
        self.masks = []
        for q in range(len(self.words)):
            mask = 0
            for h in range(self.n):
                if self.outputs[h][q] == 1:
                    mask |= 1 << h
            self.masks.append(mask)
        self.optimal = {}
        self.decision = {}
        self.greedy = {}
        self.greedy_decision = {}
        self.cut_cache = {}
        self.lower_cache = {0: 0}

    def cuts(self, mask):
        if mask in self.cut_cache:
            return self.cut_cache[mask]
        # Keep lowest-priced lexicographically-smallest query per equivalent split.
        unique = {}
        for q, full_one in enumerate(self.masks):
            one = mask & full_one
            if not one or one == mask:
                continue
            zero = mask ^ one
            canonical = min(one, zero)
            old = unique.get(canonical)
            if old is None or (self.prices[q], self.words[q]) < (
                    self.prices[old], self.words[old]):
                unique[canonical] = q
        cuts = []
        for q in unique.values():
            one = mask & self.masks[q]
            cuts.append((q, one, mask ^ one))
        cuts.sort(key=lambda x: self.words[x[0]])
        if mask.bit_count() > 1 and not cuts:
            raise IndistinguishableError("NO_SPLITTING_QUERY")
        self.cut_cache[mask] = cuts
        return cuts

    def lb(self, mask):
        if mask in self.lower_cache:
            return self.lower_cache[mask]
        n = mask.bit_count()
        if n <= 1:
            return 0
        # Every descendant-splitting query also splits the superset mask.
        # Hence the least positive split price at this mask lower-bounds
        # every future query on every branch.
        price = min(self.prices[q] for q, _, _ in self.cuts(mask))
        lower = price * code_length_numerator(n)
        self.lower_cache[mask] = lower
        return lower

    def cheap_tree(self, mask):
        if mask in self.greedy:
            return self.greedy[mask]
        if mask.bit_count() == 1:
            self.greedy[mask] = 0
            return 0
        n = mask.bit_count()
        cuts = sorted(self.cuts(mask), key=lambda v: (
            n * self.prices[v[0]] + self.lb(v[1]) + self.lb(v[2]),
            self.words[v[0]]))
        # A valid greedy tree gives a real incumbent upper bound.
        q, a, b = cuts[0]
        value = n * self.prices[q] + self.cheap_tree(a) + self.cheap_tree(b)
        self.greedy[mask] = value
        self.greedy_decision[mask] = q
        return value

    def exact(self, mask):
        if mask in self.optimal:
            return self.optimal[mask]
        if len(self.optimal) >= MAX_STATES:
            raise RuntimeError("RESOURCE_LIMIT_INDETERMINATE")
        n = mask.bit_count()
        if n == 1:
            self.optimal[mask] = 0
            return 0
        # Tighten the feasible incumbent with EXACT solutions of its two
        # children, and materialize a complete witness decision tree.
        # A greedy-only upper bound may have incomplete/locally suboptimal
        # child choices; it must not be treated as a certified Bellman tree.
        self.cheap_tree(mask)
        incumbent = self.greedy_decision[mask]
        ia = mask & self.masks[incumbent]
        ib = mask ^ ia
        upper = (n * self.prices[incumbent] +
                 self.exact(ia) + self.exact(ib))
        cuts = sorted(self.cuts(mask), key=lambda v: (
            n * self.prices[v[0]] + self.lb(v[1]) + self.lb(v[2]),
            self.words[v[0]]))
        for q, a, b in cuts:
            optimistic = n * self.prices[q] + self.lb(a) + self.lb(b)
            if optimistic > upper:
                continue
            if optimistic == upper and self.words[q] >= self.words[incumbent]:
                continue
            first, second = (a, b) if a.bit_count() <= b.bit_count() else (b, a)
            v1 = self.exact(first)
            if n * self.prices[q] + v1 + self.lb(second) > upper:
                continue
            v2 = self.exact(second)
            candidate = n * self.prices[q] + v1 + v2
            if candidate < upper or (
                    candidate == upper and self.words[q] < self.words[incumbent]):
                upper, incumbent = candidate, q
        self.optimal[mask] = upper
        self.decision[mask] = incumbent
        return upper

    def solve(self):
        return self.exact(self.full)

    def oracle_paths(self):
        root = self.solve()
        paths = []
        for hidden_index in range(self.n):
            mask = self.full
            history = []
            cost = 0
            while mask.bit_count() > 1:
                q = self.decision[mask]
                word = self.words[q]
                bit = self.outputs[hidden_index][q]
                nextmask = mask & self.masks[q] if bit else mask & ~self.masks[q]
                if not nextmask or nextmask == mask:
                    raise AssertionError("INVALID_ORACLE_PATH")
                history.append({"word": list(word), "terminal_bit": bit,
                                "before": mask.bit_count(),
                                "after": nextmask.bit_count(),
                                "price": self.prices[q]})
                cost += self.prices[q]
                mask = nextmask
                if len(history) > self.n - 1:
                    raise AssertionError("IMPOSSIBLE_TREE_DEPTH")
            paths.append({"hidden_index": hidden_index,
                          "cost": cost, "queries": len(history),
                          "certified": mask == (1 << hidden_index),
                          "history": history})
        if any(not x["certified"] for x in paths):
            raise AssertionError("ORACLE_FALSE_CERTIFICATE")
        if sum(x["cost"] for x in paths) != root:
            raise AssertionError("ORACLE_BELLMAN_SUM_MISMATCH")
        return paths

    def witness_digest(self):
        return digest({
            "root_numerator": self.solve(),
            "decisions": [(mask, list(self.words[q]), self.optimal[mask])
                          for mask, q in sorted(self.decision.items())],
            "model_signatures": self.outputs,
            "prices": self.prices,
        })


def baseline_paths(candidates, menu, tariff, name):
    """Recompute unchanged #159 selector for each possible hidden model."""
    paths = []
    for h, hidden in enumerate(candidates):
        survivors = list(candidates)
        queried = set()
        log = []
        for _ in range(N_CANDIDATES - 1):
            if len(survivors) == 1:
                break
            options = contrast.propose(survivors, queried, menu, tariff)
            if name not in options:
                raise IndistinguishableError("BASELINE_NO_QUERY")
            word = options[name]
            if word in queried:
                raise AssertionError("BASELINE_REPEATED_QUERY")
            price = contrast.query_price(word, tariff)
            bit = s.trace(hidden, word)[-1]
            left = [x for x in survivors if s.trace(x, word)[-1] == bit]
            if not left or hidden not in left or len(left) >= len(survivors):
                raise AssertionError("INVALID_BASELINE_STATE")
            log.append({"word": list(word), "terminal_bit": bit,
                        "before": len(survivors), "after": len(left), "price": price})
            queried.add(word)
            survivors = left
        paths.append({"hidden_index": h, "cost": sum(e["price"] for e in log),
                      "queries": len(log),
                      "certified": len(survivors) == 1 and survivors[0] == hidden,
                      "history": log})
    return paths


def conduct():
    menu = contrast.menu_words()
    world_space, _ = s.enumerate_consistent_models(
        s.validate_observations(s.six_zero_observations()))
    pool, eligible, exclusions = fresh_evaluation_pool(world_space, menu)
    instances = build_instances(pool)
    trials = []
    for item in instances:
        models = item["candidates"]
        prices = [contrast.query_price(word, item["tariff"]) for word in menu]
        matrix = [[s.trace(model, word)[-1] for word in menu] for model in models]
        solver = ExactOracle(menu, matrix, prices)
        numerator = solver.solve()
        oracle = solver.oracle_paths()
        baseline = baseline_paths(models, menu, item["tariff"], "PRICE_AWARE")
        balanced = baseline_paths(models, menu, item["tariff"], "BALANCED")
        path_sets = {"OPTIMUM": oracle, "PRICE_AWARE": baseline,
                     "BALANCED": balanced}
        if any(not path["certified"] for episodes in path_sets.values()
               for path in episodes):
            raise AssertionError("INVALID_FULL_IDENTIFICATION")
        sums = {name: sum(r["cost"] for r in episodes)
                for name, episodes in path_sets.items()}
        if numerator != sums["OPTIMUM"] or numerator > sums["PRICE_AWARE"]:
            raise AssertionError("OPTIMALITY_VIOLATED_BY_BASELINE")
        if numerator > sums["BALANCED"]:
            raise AssertionError("OPTIMALITY_VIOLATED_BY_BALANCED")
        depths = {name: max(x["queries"] for x in episodes)
                  for name, episodes in path_sets.items()}
        path_budget_ok = all(depth <= MAX_QUERIES for depth in depths.values())
        trials.append({
            "index": item["index"],
            "tariff": list(item["tariff"]),
            "hidden_model": item["hidden"],
            "candidates": models,
            "candidate_digest": digest(models),
            "oracle_numerator": numerator,
            "oracle_root_word": list(solver.words[solver.decision[solver.full]]),
            "solver_state_count": len(solver.optimal),
            "witness_digest": solver.witness_digest(),
            "cost_sums_all_16_worlds": sums,
            "mean_costs_uniform_16": {name: sums[name] / N_CANDIDATES
                                       for name in POLICIES},
            "max_query_depth": depths,
            "budget_12_comparable": path_budget_ok,
            "paths": path_sets,
        })
    headroom = [r["cost_sums_all_16_worlds"]["PRICE_AWARE"] * 10 >=
                r["oracle_numerator"] * 11 for r in trials]
    strictly_over_10 = [r["cost_sums_all_16_worlds"]["PRICE_AWARE"] * 10 >
                        r["oracle_numerator"] * 11 for r in trials]
    all_budget_ok = all(r["budget_12_comparable"] for r in trials)
    primary = (sum(headroom) >= 6 and all_budget_ok and
               all(len(r["paths"]["OPTIMUM"]) == N_CANDIDATES for r in trials))
    near = all(not x for x in strictly_over_10) and all_budget_ok
    status = ("HEADROOM_FOR_IMPROVEMENT" if primary else
              "NEAR_OPTIMUM_IN_THIS_BENCHMARK" if near else
              "MIXED_OR_INDETERMINATE")
    score = {
        "instances": len(trials),
        "hidden_worlds_replayed_per_instance": N_CANDIDATES,
        "mean_optimal_uniform_cost": sum(r["oracle_numerator"] for r in trials)
                                     / (N_CANDIDATES * len(trials)),
        "mean_price_aware_uniform_cost": sum(
            r["cost_sums_all_16_worlds"]["PRICE_AWARE"] for r in trials)
            / (N_CANDIDATES * len(trials)),
        "mean_balanced_uniform_cost": sum(
            r["cost_sums_all_16_worlds"]["BALANCED"] for r in trials)
            / (N_CANDIDATES * len(trials)),
        "instances_at_least_10pct_gap": sum(headroom),
        "instances_strictly_over_10pct_gap": sum(strictly_over_10),
        "budget12_comparable_instances": sum(r["budget_12_comparable"] for r in trials),
        "max_oracle_depth": max(r["max_query_depth"]["OPTIMUM"] for r in trials),
        "max_price_aware_depth": max(r["max_query_depth"]["PRICE_AWARE"] for r in trials),
        "total_oracle_states": sum(r["solver_state_count"] for r in trials),
        "max_gap_cost_uniform": max(
            (r["cost_sums_all_16_worlds"]["PRICE_AWARE"] - r["oracle_numerator"]) /
             N_CANDIDATES for r in trials),
    }
    return {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG_COMMIT,
        "status": status, "source_models": len(world_space),
        "eligible_new_models": eligible, "excluded_previous_models": exclusions,
        "pool_sha256": digest(pool),
        "instances_sha256": digest([x["candidates"] for x in instances]),
        "menu_sha256": digest(menu), "menu_size": len(menu),
        "seeds": [POOL_SEED, INSTANCE_SEED],
        "tariffs": [list(x) for x in TARIFFS],
        "pool_size": len(pool), "new_instances": len(instances),
        "policies": list(POLICIES),
        "prior": "uniform among 16 candidates, not actual unknown-world distribution",
        "horizon": "unbounded exact identification; depth<=12 reported separately",
        "primary": score, "trials": trials,
        "no_paid_api": True, "main_modified": False,
        "no_training": True, "generalization_proven": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    r = conduct()
    raw = (json.dumps(r, sort_keys=True, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment": EXPERIMENT, "status": r["status"],
        "summary": r["primary"], "report_sha256": sha256(raw).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
