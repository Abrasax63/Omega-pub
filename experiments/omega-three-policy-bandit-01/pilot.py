"""Pre-registered three-arm comparison built on the unchanged finite simulator of PR #145.

This is a two-choice epsilon-greedy bandit, not LLM reinforcement learning.
The bandit observes only outcomes of queries it actually paid for.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-state-split-active-02"))
import active_lab as previous

s = previous.s
EXPERIMENT = "OMEGA-THREE-POLICY-BANDIT-01"
PREREG_COMMIT = "8b94886315d463f2e4585ae4576b92f4c2fcfa2e"
COHORT_SEED = 54117
POLICY_SEED = 54118
TRAIN_N = 48
HOLDOUT_N = 24
MAX_QUERIES = 8
COST_PER_QUERY = 10
EPSILON = 0.2
ARMS = ("FIXED", "ACTIVE", "BANDIT")


def canonical_hash(worlds):
    raw = json.dumps(worlds, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def select_cohorts(space):
    """Selection is score-free and excludes every PR #143/#145 test world."""
    old = {s.canonical(s.delayed_marker(p))
           for p in product(s.ALPHABET, repeat=3)}
    prior, _ = previous.new_cohort(space)
    excluded = old | set(prior)
    eligible = sorted(x for x in space
                      if len(x[0]) == 3 and previous.distinguishable(x)
                      and x not in excluded)
    if len(eligible) < TRAIN_N + HOLDOUT_N:
        raise RuntimeError("INSUFFICIENT_ELIGIBLE_WORLDS")
    random.Random(COHORT_SEED).shuffle(eligible)
    train = eligible[:TRAIN_N]
    holdout = eligible[TRAIN_N:TRAIN_N + HOLDOUT_N]
    assert not (set(train) & set(holdout))
    assert not (set(train) & excluded)
    assert not (set(holdout) & excluded)
    return train, holdout, len(eligible), len(prior)


class ObservedBandit:
    """Two action-value estimates, trained exclusively from paid observations."""
    def __init__(self):
        self.counts = {"FIXED": 0, "ACTIVE": 0}
        self.total_reward = {"FIXED": 0.0, "ACTIVE": 0.0}

    def snapshot(self):
        return {"counts": dict(self.counts),
                "total_reward": dict(self.total_reward),
                "mean_reward": {key: (self.total_reward[key] / self.counts[key]
                                     if self.counts[key] else None)
                                for key in self.counts}}

    def choose(self, choices, training, rng):
        choices = tuple(sorted(choices))
        if not choices:
            raise ValueError("NO_QUERY_CHOICE")
        if training:
            unseen = [k for k in choices if self.counts[k] == 0]
            if unseen:
                return unseen[0]
            if rng.random() < EPSILON:
                return rng.choice(choices)
        def value(key):
            n = self.counts[key]
            return self.total_reward[key] / n if n else 0.0
        return max(choices, key=lambda key: (value(key), key == "ACTIVE"))

    def observe(self, chosen, reward):
        assert chosen in self.counts
        self.counts[chosen] += 1
        self.total_reward[chosen] += reward


def alternatives(remaining, known):
    seen = {tuple(x["inputs"]) for x in known}
    fixed = next((x for x in s.seed_words() if x not in seen), None)
    representatives, _ = s.diversify(remaining)
    ranked, _ = s.rank_queries(representatives, known)
    active = ranked[0] if ranked else None
    options = {}
    if fixed is not None:
        options["FIXED"] = fixed
    if active is not None:
        options["ACTIVE"] = active
    return options


def run_episode(arm, hidden, observations, space, bandit=None,
                training=False, rng=None):
    """hidden is used exclusively by the paid simulator and post-answer audit."""
    if arm not in ARMS:
        raise ValueError("UNKNOWN_ARM")
    if training and arm != "BANDIT":
        raise ValueError("ONLY_BANDIT_TRAINS")
    if arm == "BANDIT" and bandit is None:
        raise ValueError("BANDIT_REQUIRED")
    if rng is None:
        rng = random.Random(POLICY_SEED)
    known = [{"inputs": list(o["inputs"]), "outputs": list(o["outputs"])}
             for o in observations]
    remaining = list(space)
    queries = []
    status = "BUDGET_EXHAUSTED_WITHOUT_DETECTION"
    fixed_order = s.seed_words()
    for step in range(MAX_QUERIES):
        if arm == "FIXED":
            kind, word = "FIXED", fixed_order[step]
            choices = ["FIXED"]
        else:
            options = alternatives(remaining, known)
            if not options:
                status = "NO_IDENTIFIABLE_QUERY"
                break
            if arm == "ACTIVE":
                if "ACTIVE" not in options:
                    status = "NO_ACTIVE_DISAGREEMENT"
                    break
                kind, word = "ACTIVE", options["ACTIVE"]
            else:
                kind = bandit.choose(options, training, rng)
                word = options[kind]
            choices = sorted(options)
        if len(word) != COST_PER_QUERY:
            raise AssertionError("INVALID_EQ_WORD_LENGTH")
        if any(tuple(row["inputs"]) == word for row in known):
            raise AssertionError("REPAID_QUERY")
        before = len(remaining)
        # Only the simulator is allowed to consult hidden before this point.
        observed = previous.paid_query(hidden, word)
        surviving = [model for model in remaining
                     if s.trace(model, word) == observed]
        # Independent exact post-observation checks; never shown to the selector.
        if not surviving or hidden not in surviving:
            raise AssertionError("INVALID_MODEL_SET_AFTER_PAID_QUERY")
        if observed != s.trace(hidden, word):
            raise AssertionError("INVALID_SIMULATOR_RESPONSE")
        detected = observed != s.trace(previous.BASE, word)
        after = len(surviving)
        reward = (3.0 * int(detected)
                  + 0.25 * (before - after) / before
                  - 0.25)
        if training:
            bandit.observe(kind, reward)
        queries.append({
            "step": step, "action": kind, "available_actions": choices,
            "word": list(word), "observed_outputs": list(observed),
            "before": before, "after": after,
            "detected": detected, "cost": COST_PER_QUERY,
            "training_reward": reward if training else None,
        })
        known.append({"inputs": list(word), "outputs": list(observed)})
        remaining = surviving
        if detected:
            status = "DETECTED_VERIFIED_DIVERGENCE"
            break
    result = {"arm": arm, "status": status,
              "detected": status == "DETECTED_VERIFIED_DIVERGENCE",
              "false_certificate": False,
              "queries_paid": len(queries),
              "symbols_paid": COST_PER_QUERY * len(queries),
              "last_consistent_models": len(remaining),
              "query_log": queries}
    assert result["symbols_paid"] <= MAX_QUERIES * COST_PER_QUERY
    assert all(row["after"] <= row["before"] and row["after"] > 0
               for row in queries)
    return result


def scores_for(trials):
    return {
        arm: {
            "detected": sum(row["arms"][arm]["detected"] for row in trials),
            "false_certificates": sum(row["arms"][arm]["false_certificate"]
                                      for row in trials),
            "total_paid_symbols": sum(row["arms"][arm]["symbols_paid"]
                                       for row in trials),
            "mean_paid_symbols": (sum(row["arms"][arm]["symbols_paid"]
                                       for row in trials) / len(trials)),
        } for arm in ARMS
    }


def conduct():
    observations = s.six_zero_observations()
    space, _ = s.enumerate_consistent_models(
        s.validate_observations(observations))
    train, holdout, n_eligible, n_prior = select_cohorts(space)
    bandit, rng = ObservedBandit(), random.Random(POLICY_SEED)
    training_runs = []
    for index, hidden in enumerate(train):
        trial = run_episode("BANDIT", hidden, observations, space,
                            bandit=bandit, training=True, rng=rng)
        training_runs.append({"index": index, "model": hidden, "result": trial})
    frozen = bandit.snapshot()
    trials = []
    for index, hidden in enumerate(holdout):
        all_arms = {
            arm: run_episode(arm, hidden, observations, space,
                             bandit=bandit, training=False, rng=rng)
            for arm in ARMS
        }
        trials.append({"index": index, "model": hidden, "arms": all_arms})
    if bandit.snapshot() != frozen:
        raise AssertionError("TEST_LEAK_INTO_POLICY")
    scores = scores_for(trials)
    candidate = scores["BANDIT"]
    gain = (candidate["detected"] == HOLDOUT_N
            and candidate["false_certificates"] == 0
            and all(candidate["mean_paid_symbols"] <
                    scores[ref]["mean_paid_symbols"]
                    for ref in ("FIXED", "ACTIVE")))
    paired = {
        ref: {
            "wins": sum(t["arms"]["BANDIT"]["symbols_paid"] <
                        t["arms"][ref]["symbols_paid"] for t in trials),
            "losses": sum(t["arms"]["BANDIT"]["symbols_paid"] >
                          t["arms"][ref]["symbols_paid"] for t in trials),
            "ties": sum(t["arms"]["BANDIT"]["symbols_paid"] ==
                        t["arms"][ref]["symbols_paid"] for t in trials),
            "total_cost_difference": sum(
                t["arms"]["BANDIT"]["symbols_paid"] -
                t["arms"][ref]["symbols_paid"] for t in trials),
        } for ref in ("FIXED", "ACTIVE")
    }
    return {
        "experiment": EXPERIMENT,
        "preregistered_commit": PREREG_COMMIT,
        "status": ("DESCRIPTIVE_BANDIT_GAIN" if gain
                   else "NO_LEARNED_ADVANTAGE_DEMONSTRATED"),
        "seeds": {"cohort": COHORT_SEED, "policy": POLICY_SEED},
        "cohorts": {
            "train_n": TRAIN_N, "holdout_n": HOLDOUT_N,
            "eligible_after_exclusions": n_eligible,
            "prior_pr145_excluded": n_prior,
            "train_sha256": canonical_hash(train),
            "holdout_sha256": canonical_hash(holdout),
            "pairwise_disjoint": not bool(set(train) & set(holdout)),
        },
        "arms": list(ARMS),
        "max_symbols_per_episode": COST_PER_QUERY * MAX_QUERIES,
        "source_model_count": len(space),
        "training_observations": observations,
        "bandit_frozen": frozen,
        "training_runs": training_runs,
        "holdout_runs": trials,
        "summary": scores,
        "paired_bandit": paired,
        "no_paid_api": True,
        "generalization_proven": False,
        "limitations": [
            "Finite synthetic three-state Mealy machines only.",
            "No LLM weight training, proof reconstruction or autonomous scientific certification.",
            "A two-choice non-contextual bandit is not deep reinforcement learning.",
            "Equal probe-symbol caps do not equalize CPU costs.",
            "Both train and holdout are drawn from the same structural family.",
            "The exact verifier checks paid outputs, not external scientific claims.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = conduct()
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({"experiment": EXPERIMENT,
                      "status": report["status"],
                      "summary": report["summary"],
                      "paired": report["paired_bandit"],
                      "sha256": hashlib.sha256(raw).hexdigest()},
                     sort_keys=True))


if __name__ == "__main__":
    main()
