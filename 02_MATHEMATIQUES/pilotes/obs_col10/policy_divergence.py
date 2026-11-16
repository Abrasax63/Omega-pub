#!/usr/bin/env python3
"""OBS-COL-10: first real *policy-originated* EQ probe choices in Omega pipeline.

This is a fully specified, classical hypothesis-coverage / memory heuristic
(not evidence of a new kind of intelligence). Unlike P1's wrapper in #96,
it CHANGES the candidate EQ word execution order before querying the
black-box system, using the learned hypothesis and past probes only.
No target graph / output or holdout label is a policy input.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "obs_col09_common"
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from common_eq import (
    FIXTURES, SharedWordEquivalenceOracle, run_method,
)
from generate_manifests import generate

POLICIES = ("fixed", "coverage_only", "omega_candidate")
MAX_RESETS, MAX_SYMBOLS = 10000, 50000


def model_probe_features(hypothesis, word):
    """Derived ONLY from the current hypothesis, never from the target.

    No mutation of hypothesis.current_state, no use of true states.
    """
    state = hypothesis.initial_state
    transitions = set()
    changes = 0
    for symbol in word:
        before = getattr(state, "output", None)
        transitions.add((state.state_id, str(symbol)))
        state = state.transitions[symbol]
        after = getattr(state, "output", None)
        changes += int(before != after)
    return len(transitions), changes


def coverage_ranking(hypothesis, words, known_prefixes=(), memory=False):
    """Freeze each round's proposed ordering BEFORE its first true observation.

    Candidate set is identical to the fixed manifest; only order changes.
    """
    known = set(known_prefixes)
    scored = []
    for original_index, word in enumerate(words):
        coverage, flips = model_probe_features(hypothesis, word)
        novelty = 0
        if memory:
            novelty = sum(
                tuple(word[:k]) not in known
                for k in range(1, len(word) + 1)
            )
        # Scale scores by 1000*(length+1) to avoid binary float ties;
        # equivalent to 4*coverage + 2*flips + novelty/(len+1).
        score = (4 * coverage + 2 * flips) * (len(word) + 1) + novelty
        scored.append((-score, len(word), original_index, word))
    return tuple(item[-1] for item in sorted(scored))


class AdaptiveEqOracle(SharedWordEquivalenceOracle):
    """Shared bounded EQ oracle with a test order proposed by a policy.

    Identical observed EQ candidate words, bounded lengths and stopping
    rule as #96, but rank from hypothesis before executing any word.
    """
    def __init__(self, alphabet, sul, words, *, policy):
        if policy not in POLICIES:
            raise ValueError("unknown frozen policy")
        super().__init__(alphabet, sul, words)
        self.policy = policy
        self.known_prefixes = set()
        self.first_proposals = []
        self._digest = hashlib.sha256()
        self.policy_differs_from_fixed = False

    def proposed_order(self, hypothesis):
        if self.policy == "fixed":
            return self.words
        return coverage_ranking(
            hypothesis, self.words,
            known_prefixes=self.known_prefixes,
            memory=(self.policy == "omega_candidate"),
        )

    def order_digest(self):
        return self._digest.hexdigest()

    def find_cex(self, hypothesis):
        self.rounds += 1
        ordered = self.proposed_order(hypothesis)
        if len(ordered) != len(self.words) or set(ordered) != set(self.words):
            raise AssertionError("EQ policy changed candidate universe")
        if ordered != self.words:
            self.policy_differs_from_fixed = True
        head = [tuple(map(str, x)) for x in ordered[:3]]
        self.first_proposals.append(head)
        # All 512 proposed inputs per round hashed before querying the target.
        self._digest.update(
            json.dumps([tuple(map(str, w)) for w in ordered],
                       separators=(",", ":")).encode() + b"\n"
        )
        for word in ordered:
            self.reset_hyp_and_sul(hypothesis)
            self.proposed_words += 1
            for k, symbol in enumerate(word):
                actual = self.sul.step(symbol)
                predicted = hypothesis.step(symbol)
                self.num_steps += 1
                self.known_prefixes.add(tuple(word[:k + 1]))
                if actual != predicted:
                    self.sul.post()
                    self.found_counterexamples += 1
                    return tuple(word[:k + 1])
            self.sul.post()
        self.completed_suites += 1
        return None


def run(manifest_dir):
    """Three calibration models only; no claim of a new blinded holdout."""
    results = []
    for index, (name, sha) in enumerate(FIXTURES):
        for policy in POLICIES:
            algorithm = "Lsharp_P1" if policy == "omega_candidate" else "Lsharp"
            row = run_method(
                index, name, sha, algorithm, manifest_dir,
                oracle_factory=lambda a, s, w, p=policy: AdaptiveEqOracle(
                    a, s, w, policy=p,
                ),
            )
            row["requested_policy"] = policy
            row["no_hidden_target_features_in_policy"] = True
            row["not_a_new_holdout"] = True
            results.append(row)
    changed = [
        name for name, _ in FIXTURES
        if next(x for x in results if x["fixture"] == name
                and x["requested_policy"] == "omega_candidate")["eq_first_proposals"]
        != next(x for x in results if x["fixture"] == name
                and x["requested_policy"] == "fixed")["eq_first_proposals"]
    ]
    return {
        "pilot": "OBS-COL-10", "prereg_commit": "73963b67a35c13645c1a76d45106c9c3e3b27345",
        "calibration_only_public_models": True,
        "policy_divergence_cases": changed,
        "policy_divergence_count": len(changed),
        "omega_policy_is_classical_heuristic": True,
        "omega_p1_selects_probes": False,
        "omega_like_eq_policy_selects_probes": True,
        "new_independent_blind_holdout_executed": False,
        "results": results,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: policy_divergence.py <manifest directory>")
    print(json.dumps(run(sys.argv[1]), ensure_ascii=False, indent=2, default=str))
