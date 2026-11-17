"""OMEGA-DISAGREE-01: evidence-consistent local alternative hypothesis EQ selector.

Runs alongside unchanged AALpy L* baselines inherited from PR #140.
Only the ongoing L* hypothesis and already-paid SUL query log inform EQ words.
No hidden truth, BFS exact label, or holdout word enters this selector.
"""
from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-cover-replication-05"))
import replication_lab as r
from mealy_lab import Mealy, digest

c = r.c
b = c.b
EXPERIMENT = "OMEGA-DISAGREE-01"
PREREG = "0019fbb181032944491bcc56a240159da43bb95c"
TARGET = "DISAGREE_EVIDENCE_LEN10"
ARMS = tuple(r.ARMS) + (TARGET,)
REFS = ("RANDOM_LEN10", "COVER_DISTINGUISH_LEN10")
CAPS = (300, 500)
PRIMARY = 500
GENERATORS = ((4, 39104, 16), (5, 39105, 16), (6, 39106, 16))
WORDS = 128
BOOTSTRAP_REPS = 5000
BOOTSTRAP_SEED = 49319


def modified_trace(hypothesis, word, variant=None):
    """Predict using ONLY the hypothesis and one virtual local mutation."""
    state = hypothesis.initial_state
    answers = []
    for symbol in word:
        if variant is not None and state is variant[0] and symbol == variant[1]:
            output = state.output_fun[symbol] if variant[2] is None else variant[2]
            successor = state.transitions[symbol] if variant[3] is None else variant[3]
        else:
            output = state.output_fun[symbol]
            successor = state.transitions[symbol]
        answers.append(output)
        state = successor
    return tuple(answers)


def admissible_variants(hypothesis, completed_queries, max_variants=64):
    """One-change competitors fitting all already observed paid I/O traces."""
    access = b.candidate_access_paths(hypothesis)
    states = [state for state, _ in access]
    observed = [(tuple(row["inputs"]), tuple(row["outputs"]))
                for row in completed_queries
                if not row.get("incomplete_due_to_budget")]
    variants = []
    proposed = 0
    for state in states:
        for symbol in b.ALPHABET:
            current_output = state.output_fun[symbol]
            alternatives = [(state, symbol, value, None)
                            for value in (0, 1, 2) if value != current_output]
            alternatives += [(state, symbol, None, destination)
                             for destination in states
                             if destination is not state.transitions[symbol]]
            for variant in alternatives:
                proposed += 1
                if all(modified_trace(hypothesis, word, variant) == outputs
                       for word, outputs in observed):
                    variants.append(variant)
                    if len(variants) >= max_variants:
                        return variants, proposed
    return variants, proposed


class DisagreementOracle(c.MatchedOracle):
    """Hypothesis-disagreement ranking; fallback to unchanged COVER schedule."""

    def __init__(self, sul, seed):
        super().__init__(sul, "COVER_DISTINGUISH_LEN10", seed)
        self._round_key = None
        self._schedule = []
        self._cursor = 0
        self.admissible_counts = []
        self.proposed_counts = []
        self.fallbacks = 0
        self.disagreement_chosen = 0

    def _build_schedule(self, hypothesis):
        completed = [row for row in self.sul.queries
                     if not row.get("incomplete_due_to_budget")]
        variants, proposals = admissible_variants(hypothesis, completed)
        self.admissible_counts.append(len(variants))
        self.proposed_counts.append(proposals)
        if not variants:
            return []
        pool = set()
        for original in self.generate_cover_schedule(hypothesis):
            original = tuple(original)
            for fill in ((0, 1), (1, 0)):
                word = (original + fill * 10)[:c.EQ_LENGTH]
                pool.add(word)
        for _ in range(128):
            pool.add(tuple(self.rng.choice(b.ALPHABET)
                           for _ in range(c.EQ_LENGTH)))
        previous = {tuple(row["inputs"]) for row in completed
                    if row["phase"] == "EQ"}
        ranking = []
        for word in pool:
            base = modified_trace(hypothesis, word)
            predictions = [modified_trace(hypothesis, word, x)
                           for x in variants]
            diversity = len(set([base] + predictions))
            disagree = sum(p != base for p in predictions)
            ranking.append((-diversity, -disagree, int(word in previous), word))
        ranking.sort()
        return [word for _, _, _, word in ranking[:c.EQ_ROUND_WORDS]]

    def next_word(self, hypothesis):
        key = (self.fingerprint(hypothesis), self.eq_rounds)
        if self._round_key != key:
            self._round_key = key
            self._schedule = self._build_schedule(hypothesis)
            self._cursor = 0
        if self._cursor >= len(self._schedule):
            self.fallbacks += 1
            return super().next_word(hypothesis)
        word = self._schedule[self._cursor]
        self._cursor += 1
        self.disagreement_chosen += 1
        return self.normalize(word)


def disagreement_evaluate(machine, cap, seed, reserved):
    """Use the exact same black-box charging and independent evaluator."""
    sul = b.MeteredBlackBox(machine, cap)
    oracle = DisagreementOracle(sul, seed)
    hypothesis = None
    status = "NO_HYPOTHESIS"
    try:
        hypothesis = c.run_Lstar(list(b.ALPHABET), sul, oracle,
                                  automaton_type="mealy",
                                  cache_and_non_det_check=False,
                                  print_level=0)
        status = "PROVISIONAL_LSTAR_COMPLETED"
    except b.BudgetExhausted:
        hypothesis = oracle.last_candidate
        status = ("BUDGET_INTERRUPTED_WITH_CANDIDATE" if hypothesis is not None
                  else "BUDGET_INTERRUPTED_NO_CANDIDATE")
    if hypothesis is not None:
        for state in hypothesis.states:
            if any(action not in state.transitions or action not in state.output_fun
                   for action in b.ALPHABET):
                raise AssertionError("INCOMPLETE_LSTAR_HYPOTHESIS")
    ledger = sul.summary()
    if ledger["spent_symbols"] > cap:
        raise AssertionError("QUERY_BUDGET_OVERRUN")
    for row in ledger["query_log"]:
        if row["phase"] == "EQ" and not row.get("incomplete_due_to_budget"):
            if len(row["inputs"]) != c.EQ_LENGTH:
                raise AssertionError("EQ_WORD_NOT_TEN")
    if oracle.words_tested != sum(row["phase"] == "EQ"
            and not row.get("incomplete_due_to_budget")
            for row in ledger["query_log"]):
        raise AssertionError("UNACCOUNTED_EQ_WORDS")
    asked = {tuple(row["inputs"]) for row in ledger["query_log"]
             if not row.get("incomplete_due_to_budget")}
    # All truth access is EVALUATION-ONLY, after learning terminated.
    c.audit_truth(machine, ledger)
    equivalence = b.exact_equivalence(machine, hypothesis)
    reserved_score = b.heldout_score(machine, hypothesis, reserved, asked)
    if equivalence["status"] == "EXACT_EQUIVALENT":
        if reserved_score["whole_word_accuracy"] != 1.0:
            raise AssertionError("EQ_AND_TEST_CONFLICT")
    return {"training": {
        "arm": TARGET, "status": status,
        "hypothesis_states": len(hypothesis.states) if hypothesis is not None else None,
        "ledger": ledger, "eq_rounds": oracle.eq_rounds,
        "eq_words_tested": oracle.words_tested,
        "eq_counterexamples": oracle.counterexamples,
        "eq_round_log": oracle.rounds_log,
        "generated_words_count": len(oracle.generated_words),
        "candidate_word_hash": digest(oracle.generated_words),
        "admissible_variants_per_round": oracle.admissible_counts,
        "proposed_variants_per_round": oracle.proposed_counts,
        "fallback_eq_words": oracle.fallbacks,
        "ranked_eq_words": oracle.disagreement_chosen,
    }, "exact_equivalence": equivalence, "reserved": reserved_score}


def fresh_worlds():
    seen = set(r.historical_signatures())
    earlier = r.fresh_worlds()
    for prior in earlier:
        if prior["signature"] in seen:
            raise AssertionError("HISTORICAL_COLLISION")
        seen.add(prior["signature"])
    if len(seen) != 1196:
        raise AssertionError("HISTORICAL_SIGNATURE_DRIFT")
    result = []
    for size, seed, count in GENERATORS:
        rng = random.Random(seed)
        accepted = draws = 0
        while accepted < count:
            draws += 1
            if draws > 300000:
                raise AssertionError("STRUCTURAL_GENERATOR_EXHAUSTION")
            world = Mealy(
                tuple(tuple(rng.randrange(size) for _ in b.ALPHABET)
                      for _ in range(size)),
                tuple(tuple(rng.randrange(3) for _ in b.ALPHABET)
                      for _ in range(size)))
            if len(c.reachable(world)) != size or not c.distinguishable(world):
                continue
            signature = world.signature()
            if signature in seen:
                continue
            seen.add(signature)
            result.append({"name": f"N{size}_{accepted}", "size": size,
                           "index": accepted, "generation_seed": seed,
                           "canonical_signature": signature, "machine": world})
            accepted += 1
    if len(result) != 48 or len(seen) != 1244:
        raise AssertionError("NEW_COHORT_INVALID")
    return result


def reserved_words(size, index):
    rng = random.Random(1090000 + 100 * size + index)
    words = set()
    while len(words) < WORDS:
        words.add(tuple(rng.choice(b.ALPHABET)
                        for _ in range(rng.randint(12, 20))))
    return sorted(words)


def exact_p(wins, losses):
    n = wins + losses
    return sum(comb(n, k) for k in range(wins, n + 1)) / (2 ** n) if n else 1.0


def bootstrap(cases, cap, baseline, seed):
    strata = {n: [x for x in cases if x["size"] == n] for n in (4, 5, 6)}
    if any(len(v) != 16 for v in strata.values()):
        raise AssertionError("WRONG_BOOTSTRAP_STRATA")
    rng = random.Random(seed)
    deltas = []
    for _ in range(BOOTSTRAP_REPS):
        difference = 0
        for size in (4, 5, 6):
            for _ in range(16):
                case = strata[size][rng.randrange(16)]
                rows = case["budgets"][str(cap)]
                difference += int(rows[TARGET]["exact_equivalence"]["status"]
                                  == "EXACT_EQUIVALENT")
                difference -= int(rows[baseline]["exact_equivalence"]["status"]
                                  == "EXACT_EQUIVALENT")
        deltas.append(difference / 48)
    deltas.sort()
    return [deltas[int((BOOTSTRAP_REPS - 1) * .025)],
            deltas[int((BOOTSTRAP_REPS - 1) * .975)]]


def summarize(cases, cap):
    scores = {}
    for arm in ARMS:
        trials = [case["budgets"][str(cap)][arm] for case in cases]
        scores[arm] = {
            "exact": sum(x["exact_equivalence"]["status"] == "EXACT_EQUIVALENT"
                         for x in trials),
            "accuracy": sum(x["reserved"]["whole_word_accuracy"]
                            for x in trials) / 48,
            "symbols_paid": sum(x["training"]["ledger"]["spent_symbols"]
                                for x in trials),
            "budget_interrupted": sum(x["training"]["status"].startswith(
                "BUDGET_INTERRUPTED") for x in trials),
        }
    paired = {}
    pvals = {}
    for reference in REFS:
        wins = losses = 0
        for case in cases:
            rows = case["budgets"][str(cap)]
            target_ok = rows[TARGET]["exact_equivalence"]["status"] == "EXACT_EQUIVALENT"
            ref_ok = rows[reference]["exact_equivalence"]["status"] == "EXACT_EQUIVALENT"
            wins += int(target_ok and not ref_ok)
            losses += int(ref_ok and not target_ok)
        p = exact_p(wins, losses)
        pvals[reference] = p
        paired[reference] = {
            "wins": wins, "losses": losses, "delta_exact": wins - losses,
            "p_one_sided": p,
            "test_accuracy_delta": scores[TARGET]["accuracy"] - scores[reference]["accuracy"],
            "bootstrap95": bootstrap(cases, cap, reference,
                                      BOOTSTRAP_SEED + REFS.index(reference))
        }
    ordered = sorted(pvals.items(), key=lambda z: (z[1], z[0]))
    running = 0.0
    for index, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (len(REFS) - index) * p))
        paired[name]["p_holm"] = running
    for reference, x in paired.items():
        x["strong"] = (x["wins"] > x["losses"] and x["p_holm"] <= .05
                       and x["bootstrap95"][0] > 0
                       and x["test_accuracy_delta"] >= -1e-12)
    return {"budget": cap, "scores": scores, "paired": paired,
            "strong": all(x["strong"] for x in paired.values())}


def conduct():
    if b.version("aalpy") != "1.6.2":
        raise RuntimeError("AALPY_VERSION_MISMATCH")
    cases = []
    for meta in fresh_worlds():
        machine = meta["machine"]
        size = meta["size"]
        idx = meta["index"]
        reserved = reserved_words(size, idx)
        by_budget = {}
        for cap in CAPS:
            by_budget[str(cap)] = {}
            for arm_idx, arm in enumerate(ARMS):
                seed = 1040000 + 1000 * size + 30 * idx + arm_idx
                if arm == TARGET:
                    trial = disagreement_evaluate(machine, cap, seed, reserved)
                else:
                    trial = c.evaluate_one(machine, arm, cap, seed, reserved)
                by_budget[str(cap)][arm] = trial
        cases.append({"name": meta["name"], "size": size, "index": idx,
                      "canonical_signature": meta["canonical_signature"],
                      "generation_seed": meta["generation_seed"],
                      "reserved_words_sha256": digest(reserved),
                      "evaluator_only_truth": {"transitions": machine.transitions,
                                               "outputs": machine.outputs,
                                               "initial_state": 0},
                      "budgets": by_budget})
    primary = summarize(cases, PRIMARY)
    secondary = summarize(cases, CAPS[0])
    return {"experiment": EXPERIMENT, "preregistered_commit": PREREG,
            "status": ("ROBUST_DISAGREEMENT_GAIN" if primary["strong"] else
                       "NO_ROBUST_DISAGREEMENT_GAIN_DEMONSTRATED"),
            "methods": list(ARMS), "budgets": list(CAPS),
            "primary_budget": PRIMARY,
            "same_rng_seed_across_caps": True,
            "eq_word_length": 10, "max_eq_per_round": 32,
            "heldout_evaluator_only": True, "no_paid_api": True,
            "main_modified": False, "generalization_certified": False,
            "cases": cases, "primary": primary, "secondary": secondary}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = conduct()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    args.output.write_bytes(encoded)
    print(json.dumps({"experiment": EXPERIMENT, "status": report["status"],
                      "primary": report["primary"], "secondary": report["secondary"],
                      "sha256": sha256(encoded).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
