"""Finite Mealy version space from observations alone, with explicit scope limits.

This prototype exhausts 1-3 states, binary inputs/outputs. Its bounded
hypothesis pool is not an exact oracle or a general learning system.
"""
from __future__ import annotations
import argparse
from collections import deque
from hashlib import sha256
from itertools import product
from pathlib import Path
import json

PREREG_COMMIT = "01521caa4cc19971b1322ca77a3da67b4295ca4f"
ALPHABET = (0, 1)
OUTPUTS = (0, 1)
MAX_STATES = 3
MAX_REPRESENTATIVES = 128
EQ_LENGTH = 10
EQ_LIMIT = 32


def trace(model, word):
    transitions, emissions = model
    state, outputs = 0, []
    for symbol in word:
        outputs.append(emissions[state][symbol])
        state = transitions[state][symbol]
    return tuple(outputs)


def canonical(model):
    """Drop unreachable states and relabel by BFS from initial state zero."""
    transitions, emissions = model
    queue, mapping = deque([0]), {0: 0}
    while queue:
        state = queue.popleft()
        for symbol in ALPHABET:
            nxt = transitions[state][symbol]
            if nxt not in mapping:
                mapping[nxt] = len(mapping)
                queue.append(nxt)
    old_by_new = [None] * len(mapping)
    for old, new in mapping.items():
        old_by_new[new] = old
    return (
        tuple(tuple(mapping[transitions[s][a]] for a in ALPHABET)
              for s in old_by_new),
        tuple(tuple(emissions[s][a] for a in ALPHABET) for s in old_by_new),
    )


def validate_observations(observations):
    """Refuse inconsistent resettable I/O traces before attempting synthesis."""
    records, prefixes = [], {}
    for row in observations:
        word, outputs = tuple(row["inputs"]), tuple(row["outputs"])
        if not word or len(word) != len(outputs):
            raise ValueError("INVALID_OBSERVATION_LENGTH")
        if any(a not in ALPHABET for a in word):
            raise ValueError("NONBINARY_INPUT")
        if any(value not in OUTPUTS for value in outputs):
            raise ValueError("NONBINARY_OUTPUT")
        for end in range(1, len(word) + 1):
            prefix, out = word[:end], outputs[:end]
            if prefix in prefixes and prefixes[prefix] != out:
                raise ValueError("CONTRADICTORY_RESETTABLE_TRACES")
            prefixes[prefix] = out
        records.append((word, outputs))
    if not records:
        raise ValueError("NO_OBSERVATIONS")
    return tuple(records)


def enumerate_consistent_models(records):
    """Exhaust all complete transition/output tables within the 3-state bound."""
    result = set()
    count_by_states = {1: 0, 2: 0, 3: 0}
    for n in range(1, MAX_STATES + 1):
        for flat_t in product(range(n), repeat=n * 2):
            transitions = tuple(tuple(flat_t[2*i:2*i+2]) for i in range(n))
            for flat_o in product(OUTPUTS, repeat=n * 2):
                emissions = tuple(tuple(flat_o[2*i:2*i+2]) for i in range(n))
                model = (transitions, emissions)
                if all(trace(model, word) == expected for word, expected in records):
                    normalized = canonical(model)
                    if normalized not in result:
                        count_by_states[len(normalized[0])] += 1
                        result.add(normalized)
    return sorted(result), count_by_states


def seed_words():
    return [tuple(w) + (0,) * (EQ_LENGTH - 3)
            for w in product(ALPHABET, repeat=3)]


def diversify(models):
    """Keep ≤128 representative predictions, not the entire version space."""
    seeds, classes = seed_words(), {}
    for model in models:
        signature = tuple(trace(model, word) for word in seeds)
        classes.setdefault(signature, model)
    ordered = sorted(classes.items(), key=lambda item: item[0])
    if len(ordered) <= MAX_REPRESENTATIVES:
        representatives = [model for _, model in ordered]
    else:
        indices = [i * (len(ordered) - 1) // (MAX_REPRESENTATIVES - 1)
                   for i in range(MAX_REPRESENTATIVES)]
        representatives = [ordered[i][1] for i in indices]
    return representatives, len(ordered)


def rank_queries(representatives, observations):
    """Rank ten-symbol words by observable disagreement of hypotheses only."""
    already_seen = {tuple(row["inputs"]) for row in observations}
    if len(representatives) < 2:
        return [], []
    scored = []
    for word in product(ALPHABET, repeat=EQ_LENGTH):
        if word in already_seen:
            continue
        votes = {}
        for model in representatives:
            predicted = trace(model, word)
            votes[predicted] = votes.get(predicted, 0) + 1
        if len(votes) < 2:
            continue
        minority_votes = len(representatives) - max(votes.values())
        scored.append((-len(votes), -minority_votes, word))
    scored.sort()
    selected = [word for _, _, word in scored[:EQ_LIMIT]]
    details = [{"word": list(word), "predicted_output_classes": -classes,
                "minority_votes": -minority}
               for classes, minority, word in scored[:EQ_LIMIT]]
    return selected, details


def delayed_marker(pattern):
    """TEST-ONLY source; not passed to synthesis or query ranking."""
    first, second, last = pattern
    transitions, outputs = [[0, 0] for _ in range(3)], [[0, 0] for _ in range(3)]
    transitions[0][first] = 1
    transitions[1][second] = 2
    outputs[2][last] = 1
    return tuple(map(tuple, transitions)), tuple(map(tuple, outputs))


def six_zero_observations():
    return [{"inputs": list(w), "outputs": [0] * len(w)}
            for n in (1, 2) for w in product(ALPHABET, repeat=n)]


def run_experiment():
    observed = six_zero_observations()
    records = validate_observations(observed)
    models, counts = enumerate_consistent_models(records)
    reps, classes = diversify(models)
    schedule, explanations = rank_queries(reps, observed)
    one_state = (((0, 0),), ((0, 0),))
    if one_state not in models:
        raise AssertionError("ONE_STATE_MODEL_MISSING")
    witness = (1, 1, 1) + (0,) * 7
    exists = len({trace(m, witness) for m in models}) > 1
    evaluation = []
    for pattern in product(ALPHABET, repeat=3):
        hidden = delayed_marker(pattern)
        if not all(trace(hidden, w) == out for w, out in records):
            raise AssertionError("TEST_SOURCE_NOT_CONSISTENT_WITH_TRAIN")
        hit = next((index for index, word in enumerate(schedule, start=1)
                    if trace(hidden, word) != trace(one_state, word)), None)
        evaluation.append({"pattern": list(pattern), "first_detection_query": hit,
                           "detected": hit is not None,
                           "paid_symbols_through_detection": hit * EQ_LENGTH
                               if hit is not None else None})
    verified = (any(len(model[0]) == 3 for model in models) and exists
                and len(schedule) <= EQ_LIMIT and bool(schedule)
                and all(x["detected"] for x in evaluation))
    return {
        "experiment": "OMEGA-STATE-SPLIT-01",
        "preregistered_commit": PREREG_COMMIT,
        "mechanism_status": ("STATE_SPLIT_LOCAL_MECHANISM_VERIFIED"
                             if verified else "NOT_VERIFIED"),
        "search_scope": {"max_states": MAX_STATES, "input_alphabet": list(ALPHABET),
                         "output_alphabet": list(OUTPUTS),
                         "exhaustive_within_bound": True},
        "observations": observed, "consistent_canonical_models": len(models),
        "model_count_by_reachable_states": counts,
        "behavioral_seed_signature_classes": classes,
        "representative_count": len(reps),
        "ten_symbol_disagreement_exists": exists,
        "selected_eq_words": explanations,
        "eq_cost_per_query": EQ_LENGTH, "max_paid_symbol_budget": EQ_LIMIT * EQ_LENGTH,
        "proposed_eq_symbol_cost": len(schedule) * EQ_LENGTH,
        "eight_test_only_delayed_markers": evaluation,
        "all_eight_detected": all(x["detected"] for x in evaluation),
        "no_paid_api": True, "main_modified": False, "generalization_proven": False,
        "limitations": [
            "Only binary-output Mealy machines with 1..3 states are enumerated.",
            "A 128-representative sample ranks EQ words, not the full version space.",
            "The 8 delayed-output TEST sources share six zero-output observations.",
            "Hypothesis disagreement is not exact equivalence of an arbitrary real world.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_experiment()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({"experiment": report["experiment"],
                      "status": report["mechanism_status"],
                      "consistent_models": report["consistent_canonical_models"],
                      "representatives": report["representative_count"],
                      "distinct_traces": report["behavioral_seed_signature_classes"],
                      "detected": sum(x["detected"] for x in report["eight_test_only_delayed_markers"]),
                      "report_sha256": sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
