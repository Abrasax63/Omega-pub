"""Contrastive finite-state context laboratory. Frozen protocol: PREREG commit 0501760.

A Mealy hidden system is identified among sixteen candidates from paid,
resettable LAST-BIT-only probes. Selectors never receive hidden system data.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-contextual-bandit-02"))
import contextual_lab as previous

s = previous.s
a = previous.a
old = previous.old
EXPERIMENT = "OMEGA-CONTEXT-CONTRAST-03"
PREREG_COMMIT = "05017609751aeae1a3d181e9ef6eefc000d833e4"
MENU_SEED = 55221
POOL_SEED = 55222
INSTANCE_SEED = 55223
GLOBAL_SEED = 55224
CONTEXT_SEED = 55225
POOL_SIZES = (64, 32, 32)
N_CANDIDATES = 16
TRAIN_N, CALIB_N, HOLDOUT_N = 48, 24, 24
MAX_QUERIES = 12
EPSILON = 0.2
TARIFFS = ((1, 5), (5, 1))
ACTIONS = ("BALANCED", "PRICE_AWARE")
POLICIES = ("BALANCED", "PRICE_AWARE", "GLOBAL", "CONTEXTUAL")


def digest(value):
    return sha256(json.dumps(value, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def menu_words():
    seeds = s.seed_words()
    remaining = sorted(set(product(s.ALPHABET, repeat=10)) - set(seeds))
    chosen = random.Random(MENU_SEED).sample(remaining, 56)
    words = tuple(seeds + chosen)
    assert len(words) == 64 and len(set(words)) == 64
    return words


def partition_models(space, menu):
    """Eligibility and exclusions are policy-score free."""
    historical = {s.canonical(s.delayed_marker(p))
                  for p in product(s.ALPHABET, repeat=3)}
    pr145, _ = a.new_cohort(space)
    pr157_train, pr157_test, _, _ = old.select_cohorts(space)
    pr158_train, pr158_test, _, _ = previous.select_new_cohorts(space)
    excluded = (historical | set(pr145) | set(pr157_train) |
                set(pr157_test) | set(pr158_train) | set(pr158_test))
    unique = {}
    for world in sorted(space):
        if len(world[0]) != 3 or not a.distinguishable(world) or world in excluded:
            continue
        signature = tuple(s.trace(world, word)[-1] for word in menu)
        if not any(signature) or all(signature):
            continue
        unique.setdefault(signature, world)
    eligible = sorted(unique.values())
    if len(eligible) < sum(POOL_SIZES):
        raise RuntimeError("INSUFFICIENT_NEW_MODELS")
    random.Random(POOL_SEED).shuffle(eligible)
    n_train, n_calib, n_test = POOL_SIZES
    train = eligible[:n_train]
    calib = eligible[n_train:n_train+n_calib]
    test = eligible[n_train+n_calib:n_train+n_calib+n_test]
    if len(set(train + calib + test)) != sum(POOL_SIZES):
        raise AssertionError("COHORT_LEAK")
    return {"train": train, "calib": calib, "test": test}, len(eligible), len(excluded)


def build_instances(pool, count, offset):
    """Hidden world is secret to the policy, but available to test-only simulator."""
    if count > len(pool) or len(pool) < N_CANDIDATES:
        raise RuntimeError("INVALID_POOL_SIZE")
    result = []
    for index in range(count):
        rng = random.Random(INSTANCE_SEED + offset + index)
        hidden = pool[index]
        distractors = rng.sample([m for m in pool if m != hidden],
                                 N_CANDIDATES - 1)
        candidates = [hidden] + distractors
        rng.shuffle(candidates)
        assert len(candidates) == len(set(candidates)) == N_CANDIDATES
        result.append({"index": index, "hidden": hidden,
                       "candidates": candidates, "tariff": TARIFFS[index % 2]})
    return result


def query_price(word, tariff):
    if len(word) != 10 or tariff not in TARIFFS:
        raise ValueError("INVALID_PRICED_QUERY")
    return sum(tariff[x] for x in word)


def context_key(tariff, n):
    return ("ZERO_CHEAP" if tariff == TARIFFS[0] else "ONE_CHEAP") + (
        "_LARGE" if n >= 8 else "_SMALL")


def paid_last_bit(hidden, word):
    """Only this environment function can inspect the hidden model."""
    return s.trace(hidden, word)[-1]


def propose(candidates, queried, menu, tariff):
    """Rank binary last-bit splits from the *observed* consistent hypotheses."""
    if len(candidates) <= 1:
        return {}
    records = []
    for word in menu:
        if word in queried:
            continue
        zeros = sum(s.trace(model, word)[-1] == 0 for model in candidates)
        ones = len(candidates) - zeros
        if zeros == 0 or ones == 0:
            continue
        strength = zeros * ones
        cost = query_price(word, tariff)
        records.append((word, strength, cost))
    if not records:
        return {}
    balanced = min(records, key=lambda row: (-row[1], row[0]))[0]
    aware = min(records,
                key=lambda row: (-Fraction(row[1], row[2]), row[0]))[0]
    return {"BALANCED": balanced, "PRICE_AWARE": aware}


class RewardBandit:
    """Epsilon-greedy sample mean of observed rewards only, with optional cells."""
    def __init__(self, contextual):
        self.contextual = contextual
        self.counts = {action: 0 for action in ACTIONS}
        self.totals = {action: 0.0 for action in ACTIONS}
        self.cell_counts = {}
        self.cell_totals = {}

    def snapshot(self):
        return {
            "contextual": self.contextual,
            "counts": dict(self.counts),
            "totals": dict(self.totals),
            "cell_counts": {k: dict(v) for k, v in sorted(self.cell_counts.items())},
            "cell_totals": {k: dict(v) for k, v in sorted(self.cell_totals.items())},
        }

    def value(self, action, cell):
        if self.contextual and cell in self.cell_counts:
            n = self.cell_counts[cell][action]
            if n:
                return self.cell_totals[cell][action] / n
        n = self.counts[action]
        return self.totals[action] / n if n else 0.0

    def choose(self, choices, cell, learning, rng):
        if not choices:
            raise ValueError("NO_AVAILABLE_CHOICE")
        possibilities = tuple(sorted(choices))
        if len(possibilities) == 1:
            return possibilities[0]
        if learning:
            if self.contextual:
                unseen = [x for x in possibilities if
                          self.cell_counts.get(cell, {}).get(x, 0) == 0]
            else:
                unseen = [x for x in possibilities if self.counts[x] == 0]
            if unseen:
                return unseen[0]
            if rng.random() < EPSILON:
                return rng.choice(possibilities)
        return max(possibilities, key=lambda x: (self.value(x, cell),
                                                x == "PRICE_AWARE"))

    def observe(self, action, cell, reward):
        self.counts[action] += 1
        self.totals[action] += reward
        if self.contextual:
            self.cell_counts.setdefault(cell, {a: 0 for a in ACTIONS})
            self.cell_totals.setdefault(cell, {a: 0.0 for a in ACTIONS})
            self.cell_counts[cell][action] += 1
            self.cell_totals[cell][action] += reward


def episode(policy, instance, menu, learner=None, learning=False, rng=None):
    if policy not in POLICIES:
        raise ValueError("INVALID_POLICY")
    if learning and policy not in ("GLOBAL", "CONTEXTUAL"):
        raise ValueError("UNSUPPORTED_TRAINING_POLICY")
    if policy in ("GLOBAL", "CONTEXTUAL") and learner is None:
        raise ValueError("LEARNER_REQUIRED")
    if rng is None:
        rng = random.Random(GLOBAL_SEED)
    candidates = list(instance["candidates"])
    known_queries = set()
    log = []
    status = "BUDGET_EXHAUSTED_UNRESOLVED"
    tariff = instance["tariff"]
    if len(candidates) != N_CANDIDATES or len(set(candidates)) != N_CANDIDATES:
        raise AssertionError("BAD_STARTING_CANDIDATE_SET")
    for step in range(MAX_QUERIES):
        if len(candidates) == 1:
            status = "VERIFIED_IDENTIFICATION"
            break
        options = propose(candidates, known_queries, menu, tariff)
        if not options:
            status = "NO_SPLITTING_PROBE"
            break
        cell = context_key(tariff, len(candidates))
        if policy in ACTIONS:
            action = policy
        else:
            action = learner.choose(options, cell, learning, rng)
        word = options[action]
        if word in known_queries:
            raise AssertionError("DUPLICATE_PAID_QUERY")
        paid = query_price(word, tariff)
        before = len(candidates)
        # The only pre-observation call receiving the hidden truth:
        observed = paid_last_bit(instance["hidden"], word)
        surviving = [model for model in candidates
                     if s.trace(model, word)[-1] == observed]
        # Test-only independent audit, *after* actual observation:
        if not surviving or instance["hidden"] not in surviving:
            raise AssertionError("INCONSISTENT_PAID_OBSERVATION")
        if observed != s.trace(instance["hidden"], word)[-1]:
            raise AssertionError("SIMULATOR_OUTPUT_MISMATCH")
        after = len(surviving)
        identified = after == 1
        equivalent = options["BALANCED"] == options["PRICE_AWARE"]
        reward = (4 * int(identified) +
                  2 * (before - after) / before - paid / 20)
        updated = bool(learning and not equivalent)
        if updated:
            learner.observe(action, cell, reward)
        log.append({
            "index": step, "context": cell, "choice": action,
            "proposals_differ": not equivalent,
            "candidate_words": {name: list(w) for name, w in options.items()},
            "word": list(word), "observed": observed,
            "before": before, "after": after,
            "paid": paid, "reward_training": reward if learning else None,
            "updated": updated,
        })
        known_queries.add(word)
        candidates = surviving
        if identified:
            status = "VERIFIED_IDENTIFICATION"
            break
    return {
        "policy": policy, "status": status,
        "certified": status == "VERIFIED_IDENTIFICATION",
        "false_certificates": 0,
        "queries_paid": len(log), "cost_paid": sum(x["paid"] for x in log),
        "remaining": len(candidates), "log": log,
    }


def calibration_stage(instances, menu):
    rows = []
    initial_difference = {"ZERO_CHEAP": 0, "ONE_CHEAP": 0}
    wins = {"BALANCED": 0, "PRICE_AWARE": 0}
    both_resolved = 0
    for item in instances:
        proposals = propose(item["candidates"], set(), menu, item["tariff"])
        tariff_name = ("ZERO_CHEAP" if item["tariff"] == TARIFFS[0] else
                       "ONE_CHEAP")
        different = (len(proposals) == 2 and
                     proposals["BALANCED"] != proposals["PRICE_AWARE"] and
                     query_price(proposals["BALANCED"], item["tariff"]) !=
                     query_price(proposals["PRICE_AWARE"], item["tariff"]))
        if different:
            initial_difference[tariff_name] += 1
        arms = {name: episode(name, item, menu) for name in ACTIONS}
        if all(arms[name]["certified"] for name in ACTIONS):
            both_resolved += 1
            a_cost, b_cost = arms["BALANCED"]["cost_paid"], arms["PRICE_AWARE"]["cost_paid"]
            if a_cost < b_cost:
                wins["BALANCED"] += 1
            elif b_cost < a_cost:
                wins["PRICE_AWARE"] += 1
        rows.append({"index": item["index"], "tariff": list(item["tariff"]),
                     "hidden": item["hidden"], "candidates": item["candidates"],
                     "initial_options_different_price": different, "arms": arms})
    passed = (initial_difference["ZERO_CHEAP"] >= 6 and
              initial_difference["ONE_CHEAP"] >= 6 and
              wins["BALANCED"] >= 1 and wins["PRICE_AWARE"] >= 1)
    return {
        "gate": "INFORMATIVE_CALIBRATION" if passed else "UNINFORMATIVE_CONTEXTS",
        "initial_price_disagreements": initial_difference,
        "paired_wins_both_certified": wins,
        "both_certified": both_resolved,
        "runs": rows,
    }


def summarize(runs):
    return {
        name: {
            "certified": sum(row["arms"][name]["certified"] for row in runs),
            "false_certificates": sum(row["arms"][name]["false_certificates"]
                                       for row in runs),
            "total_cost": sum(row["arms"][name]["cost_paid"] for row in runs),
            "mean_cost": sum(row["arms"][name]["cost_paid"] for row in runs) / len(runs),
            "mean_queries": sum(row["arms"][name]["queries_paid"]
                                for row in runs) / len(runs),
        } for name in POLICIES
    }


def conduct(calibration_only=False):
    menu = menu_words()
    records = s.validate_observations(s.six_zero_observations())
    space, _ = s.enumerate_consistent_models(records)
    pools, eligible, exclusions = partition_models(space, menu)
    calib = build_instances(pools["calib"], CALIB_N, 1000)
    calibr = calibration_stage(calib, menu)
    base = {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG_COMMIT,
        "mode": "calibration" if calibration_only else "full",
        "source_model_count": len(space),
        "eligible_after_exclusions": eligible,
        "excluded_prior_models": exclusions,
        "pool_digests": {k: digest(v) for k, v in pools.items()},
        "pool_sizes": dict(zip(("train", "calib", "test"), POOL_SIZES)),
        "menu_sha256": digest(menu), "menu_size": len(menu),
        "seeds": [MENU_SEED, POOL_SEED, INSTANCE_SEED, GLOBAL_SEED, CONTEXT_SEED],
        "calibration": calibr,
        "full_train_runs": [], "holdout_runs": [],
        "frozen_global": None, "frozen_contextual": None,
        "summary": None, "paired": None,
        "no_paid_api": True, "main_modified": False,
        "generalization_proven": False,
        "limitations": [
            "Sixteen candidates are drawn from finite synthetic three-state machines.",
            "Only one output bit from each resettable ten-input probe is observed.",
            "Calibration worlds are not held-out scientific validation.",
            "Training trajectories and their total costs can differ across learned arms.",
            "Equal held-out episode caps do not equalize CPU effort or proven generalization.",
        ],
    }
    if calibration_only or calibr["gate"] != "INFORMATIVE_CALIBRATION":
        base["status"] = ("CALIBRATION_ONLY" if calibration_only else
                          "UNINFORMATIVE_CONTEXTS_NO_HOLDOUT")
        return base
    train = build_instances(pools["train"], TRAIN_N, 0)
    test = build_instances(pools["test"], HOLDOUT_N, 2000)
    global_policy = RewardBandit(contextual=False)
    context_policy = RewardBandit(contextual=True)
    rng_g, rng_c = random.Random(GLOBAL_SEED), random.Random(CONTEXT_SEED)
    for item in train:
        arms = {
            "GLOBAL": episode("GLOBAL", item, menu, global_policy, True, rng_g),
            "CONTEXTUAL": episode("CONTEXTUAL", item, menu, context_policy, True, rng_c),
        }
        base["full_train_runs"].append({
            "index": item["index"], "tariff": list(item["tariff"]),
            "hidden": item["hidden"], "candidates": item["candidates"], "arms": arms})
    frozen_g, frozen_c = global_policy.snapshot(), context_policy.snapshot()
    base["frozen_global"], base["frozen_contextual"] = frozen_g, frozen_c
    for item in test:
        arms = {
            "BALANCED": episode("BALANCED", item, menu),
            "PRICE_AWARE": episode("PRICE_AWARE", item, menu),
            "GLOBAL": episode("GLOBAL", item, menu, global_policy),
            "CONTEXTUAL": episode("CONTEXTUAL", item, menu, context_policy),
        }
        base["holdout_runs"].append({
            "index": item["index"], "tariff": list(item["tariff"]),
            "hidden": item["hidden"], "candidates": item["candidates"], "arms": arms})
    if global_policy.snapshot() != frozen_g or context_policy.snapshot() != frozen_c:
        raise AssertionError("UNFROZEN_HOLDOUT_WEIGHTS")
    scores = summarize(base["holdout_runs"])
    base["summary"] = scores
    contender = scores["CONTEXTUAL"]
    passed = (contender["certified"] == HOLDOUT_N and
              contender["false_certificates"] == 0 and
              all(contender["mean_cost"] < scores[name]["mean_cost"]
                  for name in ("BALANCED", "PRICE_AWARE", "GLOBAL")) and
              contender["mean_queries"] <= min(
                  scores[name]["mean_queries"] for name in ("BALANCED", "PRICE_AWARE", "GLOBAL")))
    base["status"] = ("DESCRIPTIVE_CONTEXTUAL_GAIN" if passed else
                      "NO_CONTEXTUAL_GAIN_DEMONSTRATED")
    base["paired"] = {}
    for ref in ("BALANCED", "PRICE_AWARE", "GLOBAL"):
        diffs = [row["arms"]["CONTEXTUAL"]["cost_paid"] -
                 row["arms"][ref]["cost_paid"] for row in base["holdout_runs"]]
        base["paired"][ref] = {
            "wins": sum(d < 0 for d in diffs), "losses": sum(d > 0 for d in diffs),
            "ties": sum(d == 0 for d in diffs), "cost_difference": sum(diffs),
        }
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["calibration", "full"], required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = conduct(calibration_only=(args.mode == "calibration"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    args.output.write_bytes(data)
    print(json.dumps({
        "experiment": EXPERIMENT,
        "mode": args.mode, "status": report["status"],
        "calibration": {key: report["calibration"][key] for key in
                        ("gate", "initial_price_disagreements",
                         "paired_wins_both_certified", "both_certified")},
        "summary": report["summary"], "paired": report["paired"],
        "report_sha256": sha256(data).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
