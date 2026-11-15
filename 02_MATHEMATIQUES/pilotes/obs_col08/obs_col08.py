#!/usr/bin/env python3
"""OBS-COL-08: measured, finite-budget query decisions across equal baselines.

Omega really selects actions via PR23 + P1 among 8 supplied probe models.
A separate classical arm uses the SAME exact optimizer without P1. This
must NOT be advertised as an improvement specific to Omega. None of the
methods learn an unrestricted automaton grammar: the 40-model catalog is
supplied by the experimenter, while the target index is private to oracle.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
for folder in (
    ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism",
    ROOT / "02_MATHEMATIQUES" / "pilotes" / "obs_col07",
    ROOT / "02_MATHEMATIQUES" / "pilotes" / "obs_col04",
):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
from obs_col07 import truth, generator, all_words
from action_planning_two_step import optimize_policy, plan_with_variable_horizon
from obs_col04 import independent_two_step_oracle

SEED = 20261115
N_CANDIDATES = 40
TARGET_INDICES = (0, 3, 7, 12, 19, 27, 35, 39)
TRAIN_WORDS = tuple(all_words(1, 6))
MAX_QUERIES = 6
MAX_SYMBOLS = 18
HOLDOUT_WORDS = tuple(all_words(8, 10))
ARM_IDS = ("omega", "exact_classical", "greedy", "lexical")


def catalog():
    """Deterministic 40 candidate machines; not generated from hidden target."""
    rng = random.Random(SEED)
    signatures = set()
    models = []
    for _ in range(5000):
        if len(models) == N_CANDIDATES:
            break
        n = rng.randrange(2, 5)
        p = tuple(rng.randrange(n) for _ in range(n))
        r = tuple(rng.randrange(n) for _ in range(n))
        outputs = tuple(rng.randrange(2) for _ in range(n))
        if len(set(outputs)) != 2 or outputs[0] != 0:
            continue
        source = (p, r, outputs)
        signature = tuple(truth(source, w) for w in all_words(0, 7))
        if signature in signatures:
            continue
        signatures.add(signature)
        models.append(source)
    if len(models) != N_CANDIDATES:
        raise AssertionError("failed to generate frozen candidate class")
    return tuple(models)


class Oracle:
    """No information about the hidden source is passed to any planner."""
    def __init__(self, hidden_source):
        self._hidden = hidden_source
        self.training = []
        self.reserved = []

    def ask(self, word):
        if word not in TRAIN_WORDS:
            raise ValueError("not a training query")
        answer = truth(self._hidden, word)
        self.training.append((word, answer))
        return answer

    def evaluate(self, word):
        if word not in HOLDOUT_WORDS:
            raise ValueError("not a reserved word")
        answer = truth(self._hidden, word)
        self.reserved.append(word)
        return answer


def shortlist(models, remaining, used, symbols_left):
    """Classical Gini-based preparation, equal for EVERY comparison arm.

    This is supplied proposal ranking, not an Omega-created hypothesis.
    """
    possible = []
    n = len(remaining)
    for word in TRAIN_WORDS:
        if word in used or len(word) > symbols_left:
            continue
        ones = sum(truth(models[i], word) for i in remaining)
        zeros = n - ones
        if ones and zeros:
            possible.append((-(ones * zeros), len(word), word))
    possible.sort()
    return [w for _, _, w in possible[:8]]


def make_case(models, surviving, words, step_index):
    """All alternatives are hypothetical observations, not secret answers."""
    return {
        "case_id": f"OBS-COL-08-UNLABELED-{step_index}",
        "question": "Which experiment most efficiently distinguishes the surviving models?",
        "mission_type": "mathematical",
        "uncertainty": "Several finite model descriptions remain possible",
        "hypotheses": [{"id": f"candidate-{i:02d}", "decision": f"candidate-{i:02d}",
                        "weight": 1} for i in surviving],
        "checks": [{"id": f"q{j:02d}", "step": f"Reset and observe {word}",
                    "method": "controlled_membership_word", "action": "verify",
                    "available": True, "cost_milli": 5 * len(word),
                    "observations": [str(truth(models[i], word)) for i in surviving]}
                   for j, word in enumerate(words)],
    }


def best_greedy(case):
    """Strong one-step Gini-gain-per-cost baseline, not the full exact policy."""
    scores = []
    for c in case["checks"]:
        responses = Counter(c["observations"])
        a, b = responses.get("0", 0), responses.get("1", 0)
        gain = a * b
        scores.append((Fraction(-gain, c["cost_milli"]), c["cost_milli"], c["id"]))
    return min(scores)[2] if scores else None


def chosen_check(arm, case, budget_symbols):
    """Return real Omega P1's action, or genuine classical alternatives."""
    if arm in ("omega", "exact_classical"):
        budget_milli = 5 * budget_symbols
        if arm == "omega":
            bridge = plan_with_variable_horizon(
                case, max_depth=2, max_cost_milli=budget_milli)
            policy = bridge["optimization"]
            if bridge["p1"]["next_action"]["action"] != policy["action"]:
                raise AssertionError("real P1 diverged from real PR23 optimization")
        else:
            policy = optimize_policy(
                case, max_depth=2, max_cost_milli=budget_milli)
        reference = independent_two_step_oracle(case, budget_milli=budget_milli)
        if Fraction(reference["expected_total_loss"]) != Fraction(policy["expected_total_loss"]):
            raise AssertionError("PR23 disagrees with independent exhaustive 2-step oracle")
        return {
            "check_id": policy["policy"].get("check_id") if policy["action"] == "verify" else None,
            "loss": policy["expected_total_loss"],
            "reference_loss": reference["expected_total_loss"],
            "p1_called": arm == "omega",
            "next_action": policy["action"],
        }
    if arm == "greedy":
        return {"check_id": best_greedy(case), "p1_called": False,
                "next_action": "verify", "loss": None, "reference_loss": None}
    if arm == "lexical":
        return {"check_id": min((c["id"] for c in case["checks"]),
                                 key=lambda ident: case["checks"][int(ident[1:])]["step"].split()[-1]),
                "p1_called": False, "next_action": "verify",
                "loss": None, "reference_loss": None}
    raise ValueError("unknown arm")


def run_arm(models, source, arm):
    oracle = Oracle(source)
    remaining = tuple(range(len(models)))
    used = set()
    total_symbols = 0
    records = []
    for step in range(MAX_QUERIES):
        if len(remaining) <= 1:
            break
        words = shortlist(models, remaining, used, MAX_SYMBOLS - total_symbols)
        if not words:
            break
        case = make_case(models, remaining, words, step)
        selected = chosen_check(arm, case, MAX_SYMBOLS - total_symbols)
        if selected["check_id"] is None:
            records.append({"status": "ABSTAIN", "p1_called": selected["p1_called"],
                            "loss": selected["loss"]})
            break
        index = int(selected["check_id"][1:])
        word = words[index]
        if word in used or total_symbols + len(word) > MAX_SYMBOLS:
            raise AssertionError("invalid repeated or over-budget selection")
        observed = oracle.ask(word)
        updated = tuple(i for i in remaining if truth(models[i], word) == observed)
        records.append({"word": word, "observed": observed,
                        "before": len(remaining), "after": len(updated),
                        "p1_called": selected["p1_called"], "loss": selected["loss"],
                        "reference_loss": selected["reference_loss"]})
        used.add(word)
        total_symbols += len(word)
        remaining = updated
        if not remaining:
            break

    # Holdout opened only AFTER every decision has been taken.
    errors, abstained = 0, 0
    for word in HOLDOUT_WORDS:
        actual = oracle.evaluate(word)
        if not remaining:
            abstained += 1
            continue
        count = sum(truth(models[i], word) for i in remaining)
        predicted = int(count * 2 > len(remaining))  # tie => 0
        errors += predicted != actual

    assert total_symbols <= MAX_SYMBOLS
    assert len(oracle.training) <= MAX_QUERIES
    assert len(oracle.reserved) == len(HOLDOUT_WORDS)
    assert all(truth(models[i], w) == a for i in remaining for w, a in oracle.training)
    return {
        "arm": arm, "queries": len(oracle.training), "symbols": total_symbols,
        "survivors": len(remaining), "version_space_empty_on_training": not bool(remaining),
        "heldout_errors": errors, "heldout_abstentions": abstained,
        "posthoc_status": ("OUT_OF_HORIZON_WARNING" if errors else
                           "MODEL_CLASS_INCOMPATIBLE" if not remaining else
                           "UNIQUE_IN_CATALOG_NOT_CERTIFIED" if len(remaining) == 1 else
                           "AMBIGUOUS_IN_CATALOG"),
        "heldout_total": len(HOLDOUT_WORDS), "p1_calls": sum(x["p1_called"] for x in records),
        "trace": records,
        "scientific_certificate": False, "model_calls": 0,
    }


def one_target(models, index):
    # Outside the experimenters' candidate library only when index == -1.
    source = generator("DELAY9_OOD") if index == -1 else models[index]
    arms = {arm: run_arm(models, source, arm) for arm in ARM_IDS}
    if arms["omega"]["trace"] != [dict(x, p1_called=False)
                                 for x in arms["exact_classical"]["trace"]]:
        # The real P1 path is a provenance difference; chosen words must match.
        ow = [x.get("word") for x in arms["omega"]["trace"]]
        cw = [x.get("word") for x in arms["exact_classical"]["trace"]]
        if ow != cw:
            raise AssertionError("actual Omega choice deviated from identical classical VOI")
    for field in ("queries", "symbols", "survivors", "heldout_errors", "heldout_abstentions"):
        if arms["omega"][field] != arms["exact_classical"][field]:
            raise AssertionError(f"Omega/classical divergence in {field}")
    return {"target_posthoc": "OOD-delay9" if index == -1 else f"candidate-{index:02d}",
            "arms": arms}


def run():
    models = catalog()
    results = [one_target(models, target) for target in (*TARGET_INDICES, -1)]
    return {
        "protocol": "OBS-COL-08", "prereg": "1bb77250eef4eb2bb43b4ed3e0e941c32d290f8f",
        "status": "CLOSED_CATALOG_SYNTHETIC_EXACT_QUERY_SELECTION",
        "candidate_models": len(models), "case_count": len(results),
        "training_queries_max": MAX_QUERIES, "training_symbols_max": MAX_SYMBOLS,
        "reserved_histories": len(HOLDOUT_WORDS),
        "omega_pipeline_selects_actual_probe": True,
        "pr23_selects_probe": True, "p1_alone_selects_probe": False,
        "p1_uses_classical_voi": True, "independent_exact_two_step": True,
        "not_a_TTT_or_Lsharp_implementation": True, "model_calls": 0,
        "no_claim_of_omega_superiority": True,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
