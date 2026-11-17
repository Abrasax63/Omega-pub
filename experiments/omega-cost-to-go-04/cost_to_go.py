"""OMEGA-COST-TO-GO-04 — learn from actually observed remaining episode cost.

The cost-to-go learner receives no counterfactual feedback and never sees the
hidden system except through the paid terminal-bit observation interface.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-context-contrast-03"))
import context_contrast as previous

s = previous.s
EXPERIMENT = "OMEGA-COST-TO-GO-04"
PREREG_COMMIT = "df94bba543d5e661005efcb892935dab1ecf6d89"
COHORT_SEED = 56222
INSTANCE_SEED = 56223
IMMEDIATE_SEED = 56224
GLOBAL_SEED = 56225
RETURN_SEED = 56226
TRAIN_N, TEST_N = 48, 24
N_CANDIDATES, MAX_QUERIES = 16, 12
EPSILON = 0.2
UNRESOLVED_PENALTY = 150
ACTIONS = ("BALANCED", "PRICE_AWARE")
POLICIES = ("BALANCED", "PRICE_AWARE", "IMMEDIATE_CONTEXTUAL",
            "RETURN_GLOBAL", "RETURN_CONTEXTUAL")
TARIFFS = ((1, 5), (5, 1))


def digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fresh_pools(space, menu):
    """History exclusions and prospective selection are independent of policy scores."""
    previous_pools, previous_eligible, _ = previous.partition_models(space, menu)
    old_models = set(sum((previous_pools[key] for key in ("train", "calib", "test")), []))
    known = {s.canonical(s.delayed_marker(seq))
             for seq in product(s.ALPHABET, repeat=3)}
    pr145, _ = previous.a.new_cohort(space)
    train157, test157, _, _ = previous.old.select_cohorts(space)
    train158, test158, _, _ = previous.previous.select_new_cohorts(space)
    excluded = known | set(pr145) | set(train157 + test157 + train158 + test158)
    excluded |= old_models
    unique_signatures = {}
    for model in sorted(space):
        if len(model[0]) != 3 or not previous.a.distinguishable(model):
            continue
        if model in excluded:
            continue
        pattern = tuple(s.trace(model, word)[-1] for word in menu)
        if not any(pattern) or all(pattern):
            continue
        unique_signatures.setdefault(pattern, model)
    eligible = sorted(unique_signatures.values())
    if len(eligible) < TRAIN_N + TEST_N:
        raise RuntimeError("INSUFFICIENT_NEW_MODELS")
    random.Random(COHORT_SEED).shuffle(eligible)
    train = eligible[:TRAIN_N]
    test = eligible[TRAIN_N:TRAIN_N + TEST_N]
    if set(train) & set(test) or set(train + test) & excluded:
        raise AssertionError("PRIOR_COHORT_LEAK")
    return {"train": train, "test": test}, len(eligible), len(excluded), previous_eligible


def build_instances(pool, count, offset):
    if len(pool) < N_CANDIDATES or count > len(pool):
        raise ValueError("INVALID_COHORT")
    instances = []
    for i in range(count):
        rng = random.Random(INSTANCE_SEED + offset + i)
        hidden = pool[i]
        other = rng.sample([x for x in pool if x != hidden], N_CANDIDATES - 1)
        options = [hidden] + other
        rng.shuffle(options)
        if len(set(options)) != N_CANDIDATES:
            raise AssertionError("REPEATED_CANDIDATE")
        instances.append({"index": i, "hidden": hidden,
                          "candidates": options, "tariff": TARIFFS[i % 2]})
    return instances


class CostToGo:
    """Observed-action MC return estimates: MINIMIZE total future paid cost."""
    def __init__(self, contextual):
        self.contextual = contextual
        self.counts = {a: 0 for a in ACTIONS}
        self.totals = {a: 0.0 for a in ACTIONS}
        self.cell_counts = {}
        self.cell_totals = {}

    def snapshot(self):
        return {
            "contextual": self.contextual, "counts": dict(self.counts),
            "totals": dict(self.totals),
            "cell_counts": {key: dict(v) for key, v in sorted(self.cell_counts.items())},
            "cell_totals": {key: dict(v) for key, v in sorted(self.cell_totals.items())},
        }

    def estimate(self, action, cell):
        if self.contextual and self.cell_counts.get(cell, {}).get(action, 0):
            return self.cell_totals[cell][action] / self.cell_counts[cell][action]
        if self.counts[action]:
            return self.totals[action] / self.counts[action]
        return 0.0

    def choose(self, available, cell, training, rng):
        actions = tuple(sorted(available))
        if len(actions) == 0:
            raise ValueError("NO_ACTIONS")
        if len(actions) == 1:
            return actions[0]
        if training:
            if self.contextual:
                unexplored = [name for name in actions
                              if not self.cell_counts.get(cell, {}).get(name, 0)]
            else:
                unexplored = [name for name in actions if not self.counts[name]]
            if unexplored:
                return unexplored[0]
            if rng.random() < EPSILON:
                return rng.choice(actions)
        # Explicit fixed tie break. Unknown values revert to zero, an epistemic limitation.
        return min(actions, key=lambda name: (self.estimate(name, cell),
                                               name != "PRICE_AWARE"))

    def observe(self, action, cell, cost_to_go):
        if action not in ACTIONS or cost_to_go < 0:
            raise ValueError("INVALID_OBSERVED_RETURN")
        self.counts[action] += 1
        self.totals[action] += cost_to_go
        if self.contextual:
            self.cell_counts.setdefault(cell, {a: 0 for a in ACTIONS})
            self.cell_totals.setdefault(cell, {a: 0.0 for a in ACTIONS})
            self.cell_counts[cell][action] += 1
            self.cell_totals[cell][action] += cost_to_go


def run_episode(policy, item, menu, learner=None, training=False, rng=None):
    if policy not in POLICIES:
        raise ValueError("UNKNOWN_POLICY")
    if training and policy not in ("IMMEDIATE_CONTEXTUAL", "RETURN_GLOBAL",
                                   "RETURN_CONTEXTUAL"):
        raise ValueError("INVALID_TRAINING_ARM")
    if policy not in ACTIONS and learner is None:
        raise ValueError("MISSING_LEARNER")
    if rng is None:
        rng = random.Random(IMMEDIATE_SEED)
    belief = list(item["candidates"])
    if len(belief) != N_CANDIDATES or len(set(belief)) != N_CANDIDATES:
        raise AssertionError("INVALID_INITIAL_BELIEF")
    if item["hidden"] not in belief:
        raise AssertionError("HIDDEN_MISSING_FROM_BELIEF")
    seen = set()
    log = []
    status = "BUDGET_EXHAUSTED"
    for step in range(MAX_QUERIES):
        if len(belief) == 1:
            status = "VERIFIED_IDENTIFICATION"
            break
        options = previous.propose(belief, seen, menu, item["tariff"])
        if not options:
            status = "NO_SPLITTING_PROBE"
            break
        cell = previous.context_key(item["tariff"], len(belief))
        if policy in ACTIONS:
            action = policy
        else:
            action = learner.choose(options, cell, training, rng)
        word = options[action]
        if word in seen:
            raise AssertionError("DUPLICATE_PAID_QUERY")
        cost = previous.query_price(word, item["tariff"])
        before = len(belief)
        # Only the simulator can inspect the hidden source to answer the paid probe.
        bit = previous.paid_last_bit(item["hidden"], word)
        survivors = [model for model in belief
                     if s.trace(model, word)[-1] == bit]
        # Exact post-payment auditor, not an input to the choice policy.
        if not survivors or item["hidden"] not in survivors:
            raise AssertionError("INCONSISTENT_PAID_OBSERVATION")
        if bit != s.trace(item["hidden"], word)[-1]:
            raise AssertionError("SIMULATOR_OUTPUT_MISMATCH")
        after = len(survivors)
        if after >= before:
            raise AssertionError("USELESS_PAID_PROBE")
        same = options["BALANCED"] == options["PRICE_AWARE"]
        informative = bool(training and policy not in ACTIONS and not same)
        shaped = 4 * int(after == 1) + 2 * (before-after)/before - cost/20
        row = {
            "step": step, "context": cell, "action": action,
            "candidate_words": {k: list(v) for k,v in options.items()},
            "same_proposal": same, "word": list(word), "observed_last_bit": bit,
            "before": before, "after": after, "paid": cost,
            "immediate_reward": shaped if training and policy=="IMMEDIATE_CONTEXTUAL" else None,
            "cost_to_go_target": None, "updated": informative,
        }
        # IMMEDIATE observes only its paid one-step reward, not a future oracle.
        if informative and policy == "IMMEDIATE_CONTEXTUAL":
            learner.observe(action, cell, shaped)
        log.append(row)
        seen.add(word)
        belief = survivors
        if after == 1:
            status = "VERIFIED_IDENTIFICATION"
            break
    unresolved = status != "VERIFIED_IDENTIFICATION"
    # Delayed MC credit: for each paid decision, sum all later actual paid costs.
    if training and policy in ("RETURN_GLOBAL", "RETURN_CONTEXTUAL"):
        later_paid = UNRESOLVED_PENALTY if unresolved else 0
        for row in reversed(log):
            later_paid += row["paid"]
            if row["updated"]:
                row["cost_to_go_target"] = later_paid
                learner.observe(row["action"], row["context"], later_paid)
    result = {
        "policy": policy, "status": status,
        "certified": not unresolved, "false_certificates": 0,
        "queries_paid": len(log),
        "cost_paid": sum(row["paid"] for row in log),
        "remaining_models": len(belief), "log": log,
    }
    if result["queries_paid"] > MAX_QUERIES or result["cost_paid"] > 600:
        raise AssertionError("BUDGET_OVERSPENT")
    if result["certified"] != (len(belief) == 1):
        raise AssertionError("INCORRECT_CERTIFICATE_STATUS")
    return result


def summarize(rows, policies):
    if not rows:
        return {}
    return {
        name: {
            "certified": sum(x["arms"][name]["certified"] for x in rows),
            "false_certificates": sum(x["arms"][name]["false_certificates"] for x in rows),
            "total_cost": sum(x["arms"][name]["cost_paid"] for x in rows),
            "mean_cost": sum(x["arms"][name]["cost_paid"] for x in rows) / len(rows),
            "mean_queries": sum(x["arms"][name]["queries_paid"] for x in rows) / len(rows),
            "total_queries": sum(x["arms"][name]["queries_paid"] for x in rows),
        } for name in policies
    }


def conduct():
    menu = previous.menu_words()
    space, _ = s.enumerate_consistent_models(
        s.validate_observations(s.six_zero_observations()))
    pools, eligible, excluded, earlier_eligible = fresh_pools(space, menu)
    train = build_instances(pools["train"], TRAIN_N, 0)
    test = build_instances(pools["test"], TEST_N, 2000)
    immediate = previous.RewardBandit(contextual=True)
    global_return = CostToGo(contextual=False)
    contextual_return = CostToGo(contextual=True)
    learners = {
        "IMMEDIATE_CONTEXTUAL": immediate,
        "RETURN_GLOBAL": global_return,
        "RETURN_CONTEXTUAL": contextual_return,
    }
    rngs = {
        "IMMEDIATE_CONTEXTUAL": random.Random(IMMEDIATE_SEED),
        "RETURN_GLOBAL": random.Random(GLOBAL_SEED),
        "RETURN_CONTEXTUAL": random.Random(RETURN_SEED),
    }
    train_rows = []
    for item in train:
        arms = {name: run_episode(name, item, menu, learners[name],
                                  training=True, rng=rngs[name])
                for name in learners}
        train_rows.append({"index": item["index"], "model": item["hidden"],
                           "candidates": item["candidates"],
                           "tariff": list(item["tariff"]), "arms": arms})
    frozen = {name: b.snapshot() for name, b in learners.items()}
    evaluated = []
    for item in test:
        arms = {name: run_episode(name, item, menu, learners.get(name),
                                  training=False)
                for name in POLICIES}
        evaluated.append({"index": item["index"], "model": item["hidden"],
                          "candidates": item["candidates"],
                          "tariff": list(item["tariff"]), "arms": arms})
    if any(learners[name].snapshot() != frozen[name] for name in learners):
        raise AssertionError("TEST_LEAK_INTO_TRAINED_WEIGHTS")
    scores = summarize(evaluated, POLICIES)
    candidate = scores["RETURN_CONTEXTUAL"]
    comparable = ("PRICE_AWARE", "IMMEDIATE_CONTEXTUAL", "RETURN_GLOBAL")
    win = (candidate["certified"] == TEST_N and candidate["false_certificates"] == 0
           and all(candidate["mean_cost"] < scores[name]["mean_cost"]
                   for name in comparable)
           and candidate["mean_queries"] <= min(
               scores[name]["mean_queries"] for name in comparable))
    paired = {}
    for name in POLICIES:
        if name == "RETURN_CONTEXTUAL":
            continue
        diffs = [row["arms"]["RETURN_CONTEXTUAL"]["cost_paid"] -
                 row["arms"][name]["cost_paid"] for row in evaluated]
        paired[name] = {
            "wins": sum(v < 0 for v in diffs),
            "losses": sum(v > 0 for v in diffs),
            "ties": sum(v == 0 for v in diffs),
            "total_cost_difference": sum(diffs),
        }
    return {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG_COMMIT,
        "status": "DESCRIPTIVE_RETURN_GAIN" if win else "NO_RETURN_GAIN_DEMONSTRATED",
        "source_model_count": len(space),
        "eligible_new_models": eligible,
        "excluded_history_models": excluded,
        "eligible_in_previous_pr159_before_exclusions": earlier_eligible,
        "seeds": [COHORT_SEED, INSTANCE_SEED,
                  IMMEDIATE_SEED, GLOBAL_SEED, RETURN_SEED],
        "pool_sha256": {k: digest(v) for k,v in pools.items()},
        "train_n": TRAIN_N, "test_n": TEST_N,
        "menu_sha256": digest(menu),
        "menu_size": len(menu),
        "max_queries": MAX_QUERIES,
        "unresolved_penalty_training": UNRESOLVED_PENALTY,
        "tariffs": [list(v) for v in TARIFFS],
        "policies": list(POLICIES),
        "frozen_models": frozen,
        "train_runs": train_rows,
        "holdout_runs": evaluated,
        "train_stats": summarize(train_rows, list(learners)),
        "summary": scores,
        "paired": paired,
        "no_paid_api": True, "main_modified": False,
        "generalization_proven": False,
        "limitations": [
            "Only synthetic finite 3-state Mealy machines; not a language model.",
            "A complete 16-candidate belief is provided; no discovery of candidate models.",
            "Models in TRAIN/TEST are disjoint from every specified prior cohort.",
            "Training spend differs between policies; caps and worlds are equal, actual cost is not.",
            "Prices are artificial symbol weights, not computation or real money.",
            "Single synthetic holdout, 24 cases, with no statistical generalization.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = conduct()
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment": EXPERIMENT, "status": report["status"],
        "training": report["train_stats"],
        "summary": report["summary"], "paired": report["paired"],
        "frozen_counts": {k: v["counts"] for k,v in report["frozen_models"].items()},
        "report_sha256": sha256(raw).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
