"""OMEGA-CONTEXTUAL-BANDIT-02: priced observation-only contextual learning.

Frozen experimental contract: PREREG_2026-11-17.md, prior to implementation.
No LLM fine-tuning, no hidden-world access by selectors, no paid API.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-three-policy-bandit-01"))
import pilot as old

s = old.s
a = old.previous
PREREG_COMMIT = "10f94b228d1806f9576dda9078be226d8bba07a6"
EXPERIMENT = "OMEGA-CONTEXTUAL-BANDIT-02"
COHORT_SEED = 55117
GLOBAL_SEED = 55118
CONTEXT_SEED = 55119
TRAIN_N = 48
HOLDOUT_N = 24
MAX_QUERIES = 8
EPSILON = 0.15
POLICIES = ("ACTIVE", "COST_AWARE", "GLOBAL", "CONTEXTUAL")
DECISIONS = ("ACTIVE", "COST_AWARE")
TARIFFS = ((1, 4), (4, 1))


def world_digest(worlds):
    return sha256(json.dumps(worlds, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def select_new_cohorts(space):
    """No score-based filtering. The previous experiments' machines are excluded."""
    prior_train, prior_test, _, _ = old.select_cohorts(space)
    pr145, _ = a.new_cohort(space)
    pr143 = {s.canonical(s.delayed_marker(seq))
             for seq in product(s.ALPHABET, repeat=3)}
    excluded = pr143 | set(pr145) | set(prior_train) | set(prior_test)
    candidates = sorted(model for model in space
                        if len(model[0]) == 3 and a.distinguishable(model)
                        and model not in excluded)
    if len(candidates) < TRAIN_N + HOLDOUT_N:
        raise RuntimeError("INSUFFICIENT_ELIGIBLE_WORLDS")
    random.Random(COHORT_SEED).shuffle(candidates)
    train = candidates[:TRAIN_N]
    test = candidates[TRAIN_N:TRAIN_N + HOLDOUT_N]
    assert len(set(train + test)) == TRAIN_N + HOLDOUT_N
    assert not set(train + test) & excluded
    return train, test, len(candidates), len(excluded)


def price(word, tariff):
    if len(word) != s.EQ_LENGTH:
        raise ValueError("NONSTANDARD_QUERY_LENGTH")
    if tariff not in TARIFFS:
        raise ValueError("UNKNOWN_TARIFF")
    return sum(tariff[b] for b in word)


def context_key(tariff, size):
    return ("ZERO_CHEAP" if tariff == TARIFFS[0] else "ONE_CHEAP") + (
        "_LARGE" if size >= 64 else "_SMALL")


def candidate_choices(remaining, known, tariff):
    """Two proposals from observed hypotheses only, never the hidden model."""
    reps, _ = s.diversify(remaining)
    ranked, _ = s.rank_queries(reps, known)
    if not ranked:
        return {}
    already = {tuple(row["inputs"]) for row in known}
    active = ranked[0]
    options = set(ranked[:8]) | set(s.seed_words())
    scored = []
    for word in options:
        if word in already:
            continue
        votes = {}
        for model in reps:
            output = s.trace(model, word)
            votes[output] = votes.get(output, 0) + 1
        if len(votes) < 2:
            continue
        minority = len(reps) - max(votes.values())
        cost = price(word, tariff)
        scored.append((-minority / cost, -len(votes) / cost,
                       cost, word))
    if not scored:
        return {"ACTIVE": active}
    scored.sort()
    return {"ACTIVE": active, "COST_AWARE": scored[0][-1]}


class MeanBandit:
    """Observed-reward mean bandit; contextual mode stores separate cells."""
    def __init__(self, contextual):
        self.contextual = contextual
        self.global_counts = {k: 0 for k in DECISIONS}
        self.global_totals = {k: 0.0 for k in DECISIONS}
        self.cell_counts = {}
        self.cell_totals = {}

    def snapshot(self):
        return {
            "contextual": self.contextual,
            "global_counts": dict(self.global_counts),
            "global_totals": dict(self.global_totals),
            "cell_counts": {k: dict(v) for k, v in sorted(self.cell_counts.items())},
            "cell_totals": {k: dict(v) for k, v in sorted(self.cell_totals.items())},
        }

    def estimate(self, option, cell):
        if self.contextual and cell in self.cell_counts:
            n = self.cell_counts[cell][option]
            if n:
                return self.cell_totals[cell][option] / n
        n = self.global_counts[option]
        return self.global_totals[option] / n if n else 0.0

    def choose(self, choices, cell, training, rng):
        actions = tuple(sorted(choices))
        if not actions:
            raise ValueError("NO_CHOICES")
        if len(actions) == 1:
            return actions[0]
        if training:
            unseen = [k for k in actions
                      if (self.cell_counts.get(cell, {}).get(k, 0) == 0
                          if self.contextual else self.global_counts[k] == 0)]
            if unseen:
                return unseen[0]
            if rng.random() < EPSILON:
                return rng.choice(actions)
        return max(actions, key=lambda k: (self.estimate(k, cell),
                                           k == "COST_AWARE"))

    def observe(self, action, cell, reward):
        if action not in DECISIONS:
            raise ValueError("INVALID_ACTION")
        self.global_counts[action] += 1
        self.global_totals[action] += reward
        if self.contextual:
            if cell not in self.cell_counts:
                self.cell_counts[cell] = {k: 0 for k in DECISIONS}
                self.cell_totals[cell] = {k: 0.0 for k in DECISIONS}
            self.cell_counts[cell][action] += 1
            self.cell_totals[cell][action] += reward


def run_episode(arm, world, observations, space, tariff,
                bandit=None, training=False, rng=None):
    if arm not in POLICIES:
        raise ValueError("UNKNOWN_POLICY")
    if training and arm not in ("GLOBAL", "CONTEXTUAL"):
        raise ValueError("UNSUPPORTED_TRAINING_ARM")
    if arm in ("GLOBAL", "CONTEXTUAL") and bandit is None:
        raise ValueError("MISSING_BANDIT")
    if rng is None:
        rng = random.Random(GLOBAL_SEED)
    known = [{"inputs": list(x["inputs"]), "outputs": list(x["outputs"])}
             for x in observations]
    remaining = list(space)
    log = []
    status = "BUDGET_EXHAUSTED_UNDETECTED"
    for step in range(MAX_QUERIES):
        options = candidate_choices(remaining, known, tariff)
        if not options:
            status = "NO_IDENTIFIABLE_QUERY"
            break
        cell = context_key(tariff, len(remaining))
        if arm in ("ACTIVE", "COST_AWARE"):
            if arm not in options:
                status = "NO_IDENTIFIABLE_QUERY"
                break
            action = arm
        else:
            action = bandit.choose(options, cell, training, rng)
        word = options[action]
        if any(tuple(x["inputs"]) == word for x in known):
            raise AssertionError("REPAID_OBSERVATION")
        paid = price(word, tariff)
        before = len(remaining)
        # The selector has no access to 'world'; it enters only the paid simulator.
        outputs = a.paid_query(world, word)
        survivors = [candidate for candidate in remaining
                     if s.trace(candidate, word) == outputs]
        # Auditor uses the truth only after the paid response exists.
        if not survivors or world not in survivors:
            raise AssertionError("INVALID_PAID_OUTPUT_OR_MODEL_POOL")
        if outputs != s.trace(world, word):
            raise AssertionError("SIMULATOR_MISMATCH")
        after = len(survivors)
        detected = outputs != s.trace(a.BASE, word)
        reward = 4.0 * int(detected) + 2 * (before - after) / before - paid / 10
        equivalent = len(set(options.values())) == 1
        if training and not equivalent:
            bandit.observe(action, cell, reward)
        log.append({
            "step": step, "context": cell, "choice": action,
            "available_actions": sorted(options),
            "same_candidate": equivalent,
            "word": list(word), "outputs": list(outputs),
            "before": before, "after": after,
            "detected": detected, "paid": paid,
            "reward_training": reward if training else None,
            "updated_model": bool(training and not equivalent),
        })
        known.append({"inputs": list(word), "outputs": list(outputs)})
        remaining = survivors
        if detected:
            status = "DETECTED_VERIFIED_DIVERGENCE"
            break
    return {
        "arm": arm, "tariff": list(tariff), "status": status,
        "detected": status == "DETECTED_VERIFIED_DIVERGENCE",
        "false_certificate": False,
        "queries_paid": len(log),
        "cost_paid": sum(x["paid"] for x in log),
        "log": log,
    }


def summarize(trials):
    return {
        name: {
            "detected": sum(item["arms"][name]["detected"] for item in trials),
            "false_certificates": sum(item["arms"][name]["false_certificate"]
                                       for item in trials),
            "total_cost": sum(item["arms"][name]["cost_paid"] for item in trials),
            "mean_cost": sum(item["arms"][name]["cost_paid"] for item in trials)
                         / len(trials),
            "mean_queries": sum(item["arms"][name]["queries_paid"] for item in trials)
                            / len(trials),
        } for name in POLICIES
    }


def conduct():
    observations = s.six_zero_observations()
    space, _ = s.enumerate_consistent_models(s.validate_observations(observations))
    train, test, eligible, excluded = select_new_cohorts(space)
    global_policy = MeanBandit(contextual=False)
    contextual_policy = MeanBandit(contextual=True)
    rng_global, rng_context = random.Random(GLOBAL_SEED), random.Random(CONTEXT_SEED)
    trained = []
    for index, world in enumerate(train):
        tariff = TARIFFS[index % 2]
        arms = {
            "GLOBAL": run_episode("GLOBAL", world, observations, space,
                                   tariff, global_policy, True, rng_global),
            "CONTEXTUAL": run_episode("CONTEXTUAL", world, observations, space,
                                      tariff, contextual_policy, True, rng_context),
        }
        trained.append({"index": index, "model": world, "tariff": list(tariff),
                        "arms": arms})
    frozen_global, frozen_context = (global_policy.snapshot(),
                                      contextual_policy.snapshot())
    evaluated = []
    for index, world in enumerate(test):
        tariff = TARIFFS[index % 2]
        arms = {
            "ACTIVE": run_episode("ACTIVE", world, observations, space, tariff),
            "COST_AWARE": run_episode("COST_AWARE", world, observations, space, tariff),
            "GLOBAL": run_episode("GLOBAL", world, observations, space, tariff,
                                   global_policy),
            "CONTEXTUAL": run_episode("CONTEXTUAL", world, observations, space,
                                      tariff, contextual_policy),
        }
        evaluated.append({"index": index, "model": world, "tariff": list(tariff),
                          "arms": arms})
    if global_policy.snapshot() != frozen_global or contextual_policy.snapshot() != frozen_context:
        raise AssertionError("TEST_LEAK_INTO_WEIGHTS")
    scores = summarize(evaluated)
    contender = scores["CONTEXTUAL"]
    gain = (contender["detected"] == HOLDOUT_N
            and contender["false_certificates"] == 0
            and all(contender["mean_cost"] < scores[x]["mean_cost"]
                    for x in ("ACTIVE", "COST_AWARE", "GLOBAL"))
            and contender["mean_queries"] <= min(
                scores[x]["mean_queries"] for x in ("ACTIVE", "COST_AWARE", "GLOBAL")))
    paired = {}
    for name in ("ACTIVE", "COST_AWARE", "GLOBAL"):
        diffs = [row["arms"]["CONTEXTUAL"]["cost_paid"] -
                 row["arms"][name]["cost_paid"] for row in evaluated]
        paired[name] = {
            "wins": sum(v < 0 for v in diffs),
            "losses": sum(v > 0 for v in diffs),
            "ties": sum(v == 0 for v in diffs),
            "total_difference": sum(diffs),
        }
    return {
        "experiment": EXPERIMENT, "preregistered_commit": PREREG_COMMIT,
        "status": ("DESCRIPTIVE_CONTEXTUAL_GAIN" if gain else
                   "NO_CONTEXTUAL_ADVANTAGE_DEMONSTRATED"),
        "seeds": [COHORT_SEED, GLOBAL_SEED, CONTEXT_SEED],
        "training_n": TRAIN_N, "holdout_n": HOLDOUT_N,
        "eligible_after_exclusions": eligible,
        "excluded_prior_models": excluded, "source_model_count": len(space),
        "train_sha256": world_digest(train),
        "holdout_sha256": world_digest(test),
        "frozen_global": frozen_global,
        "frozen_contextual": frozen_context,
        "tariffs": [list(t) for t in TARIFFS], "max_queries": MAX_QUERIES,
        "policies": list(POLICIES),
        "train_runs": trained, "holdout_runs": evaluated,
        "summary": scores, "paired": paired,
        "no_paid_api": True, "main_modified": False,
        "generalization_proven": False,
        "limitations": [
            "This is a finite three-state synthetic laboratory, not general scientific reasoning.",
            "Observational contextual selection is not deep reinforcement learning.",
            "Equal query caps do not equalize CPU effort or observed data.",
            "One frozen holdout cannot establish a general improvement.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = conduct()
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({"experiment": EXPERIMENT, "status": report["status"],
                      "summary": report["summary"], "paired": report["paired"],
                      "digest": sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
