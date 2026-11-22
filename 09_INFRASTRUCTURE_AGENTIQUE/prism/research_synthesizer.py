"""Executable scientific hypothesis synthesis, scoped to finite V19 XOR systems.

A program-search learner selects a conjunction of structural features using
training cases only. Its verdicts are checked against an independent exhaustive
binary-color oracle on disjoint transformation families. This is symbolic,
bounded program synthesis; NOT an LLM, general semantic understanding, a
novel theorem, or an independently blind scientific discovery.

Reuse the actual PR82 forced/event-edge definitions and a pinned research card.
Never write into a repository; only a JSON report outside checked-out sources.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys

from research_reflector import source_anchor

SOURCE = {
    "path": "research/bricks/OBS-V19-SIGNED-CORE_2026-11-19.md",
    "git_blob": "1fdff7076cb769765193b0955bf1863e2b54aaae",
    "quote": "La réserve principale réfute une amélioration générale de coût pour ce candidat tel quel.",
}
FEATURES = (
    "cycle_four_quotient", "odd_signed_cycle", "four_quotient_vertices",
    "distinct_event_edges", "no_collapsed_event_edge", "all_event_edges",
    "even_state_count",
)
MAX_RULE_ATOMS = 3
FAMILY_LIMITS = {
    "TRAIN-C4-C3-N8": 240,
    "TRAIN-C4-C2-N8": 800,
    "RESERVE-C4-C3-N9": 700,
    "RESERVE-C4-C2-N9": 900,
}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"))
                  .encode("utf-8")).hexdigest()


def forced_event_library(math_root):
    """Use the pre-existing orbit-to-constraint translation from PR82."""
    path = Path(math_root) / "research/code"
    if not (path / "test_v19_locality_l_plus_1.py").is_file():
        raise FileNotFoundError("Missing original PR82 source")
    sys.path.insert(0, str(path))
    try:
        from test_v19_locality_l_plus_1 import forced_edges, event_edges, coherent
        return forced_edges, event_edges, coherent
    finally:
        sys.path.pop(0)


def raw_families(group):
    """Fixed train/reserve split by entire transformation family, not by row."""
    if group == "TRAIN-C4-C3-N8":
        for x in range(8):
            yield (1, 2, 3, 0, 5, 6, 4, x)
    elif group == "TRAIN-C4-C2-N8":
        for x, y in product(range(8), repeat=2):
            yield (1, 2, 3, 0, 5, 4, x, y)
    elif group == "RESERVE-C4-C3-N9":
        for x, y in product(range(9), repeat=2):
            yield (1, 2, 3, 0, 5, 6, 4, x, y)
    elif group == "RESERVE-C4-C2-N9":
        for x, y, z in product(range(9), repeat=3):
            yield (1, 2, 3, 0, 5, 4, x, y, z)
    else:
        raise ValueError("Unknown family")


def select_cases(group, forced_edges, event_edges, coherent):
    """Select cases by a deterministic content hash BEFORE looking at labels."""
    rows = []
    for T in raw_families(group):
        forced = tuple(forced_edges(T))
        if not coherent(len(T), forced):
            continue
        for pair in combinations(range(len(T)), 2):
            events = tuple(event_edges(T, pair, 4))
            if len(events) != 4:
                continue
            row = (T, pair, forced, events)
            rows.append((digest([T, pair]), row))
    rows.sort(key=lambda item: item[0])
    return [row for _, row in rows[:FAMILY_LIMITS[group]]]


def exact_minimal_contradiction(n, forced, events):
    """Independent 2^n oracle, no imports from the structural feature learner."""
    if len(events) != 4 or n > 9:
        raise ValueError("Out of independent oracle scope")
    satisfying = []
    for mask in range(1 << n):
        if all((((mask >> a) ^ (mask >> b)) & 1) == p for a, b, p in forced):
            satisfying.append(mask)
    if not satisfying:
        raise ValueError("Incoherent forced system")
    def exists(subset):
        return any(all((((mask >> a) ^ (mask >> b)) & 1) == p
                       for a, b, p in subset) for mask in satisfying)
    return not exists(events) and all(exists(events[:i] + events[i+1:])
                                      for i in range(4))


def structural_features(n, forced, events):
    """Construct unsigned quotient and signed relative XOR potentials."""
    parents, offsets = list(range(n)), [0] * n

    def find(i):
        if parents[i] != i:
            ancestor = parents[i]
            root = find(ancestor)
            offsets[i] ^= offsets[ancestor]
            parents[i] = root
        return parents[i]

    for a, b, sign in forced:
        u, v = find(a), find(b)
        if u == v:
            if offsets[a] ^ offsets[b] != sign:
                raise ValueError("Forced constraints are contradictory")
        else:
            parents[v] = u
            offsets[v] = offsets[a] ^ offsets[b] ^ sign

    collapsed = []
    relative = []
    for a, b, p in events:
        collapsed.append((find(a), find(b)))
        relative.append(offsets[a] ^ offsets[b] ^ p)
    undirected = [tuple(sorted(edge)) for edge in collapsed]
    vertices = {v for edge in collapsed for v in edge}
    no_loops = all(a != b for a, b in collapsed)
    cycle = (len(events) == 4 and len(undirected) == len(set(undirected))
             and len(vertices) == 4 and no_loops
             and all(sum(v in edge for edge in collapsed) == 2
                     for v in vertices))
    return {
        "cycle_four_quotient": cycle,
        "odd_signed_cycle": bool(sum(relative) % 2),
        "four_quotient_vertices": len(vertices) == 4,
        "distinct_event_edges": len(undirected) == len(set(undirected)),
        "no_collapsed_event_edge": no_loops,
        "all_event_edges": len(events) == 4,
        "even_state_count": n % 2 == 0,
    }


def prepared_rows(rows):
    prepared = []
    for T, pair, forced, events in rows:
        truth = exact_minimal_contradiction(len(T), forced, events)
        features = structural_features(len(T), forced, events)
        prepared.append({"T": T, "pair": pair, "forced": forced,
                         "events": events, "truth": truth, "features": features})
    return prepared


def conjunction(row, atoms):
    return all(row["features"][name] for name in atoms)


def tally(rows, predictor):
    counts = Counter()
    for row in rows:
        predicted = bool(predictor(row))
        actual = row["truth"]
        counts[("TP" if actual else "FP") if predicted else
               ("FN" if actual else "TN")] += 1
    return {key: counts[key] for key in ("TP", "FP", "FN", "TN")}


def learn(training):
    """Finite grammar induction, with deterministic tie-breaking and no reserve access."""
    all_rules = [atom for size in range(1, MAX_RULE_ATOMS+1)
                 for atom in combinations(FEATURES, size)]
    scored = []
    for atoms in all_rules:
        scores = tally(training, lambda row: conjunction(row, atoms))
        # Minimize mistakes, then fewer predicates, then lexical determinism.
        loss = scores["FP"] + scores["FN"]
        scored.append((loss, len(atoms), atoms, scores))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    loss, _, chosen, scores = scored[0]
    return {"atoms": chosen, "training_errors": loss,
            "training_metrics": scores, "hypotheses_evaluated": len(all_rules),
            "selection_rule": "min(FP+FN), then fewer predicates, then lexical order"}


def invariance_checks(reserved, rule, max_samples=32):
    """A genuine relabeling must leave predictions and exact truth unchanged."""
    mistakes, count = [], 0
    for i, row in enumerate(reserved[:max_samples]):
        T, pair = row["T"], row["pair"]
        p = list(range(len(T)))
        Random(9101+i).shuffle(p)
        U = [None] * len(T)
        for old, nxt in enumerate(T):
            U[p[old]] = p[nxt]
        transformed_pair = (p[pair[0]], p[pair[1]])
        f = tuple((p[a], p[b], sign) for a, b, sign in row["forced"])
        e = tuple((p[a], p[b], sign) for a, b, sign in row["events"])
        new_truth = exact_minimal_contradiction(len(U), f, e)
        new_features = structural_features(len(U), f, e)
        if row["truth"] != new_truth or conjunction(row, rule) != all(
                new_features[atom] for atom in rule):
            mistakes.append({"T": T, "pair": pair, "renamed_pair": transformed_pair})
        count += 1
    return {"cases": count, "counterexamples": mistakes[:3], "disagreements": len(mistakes)}


def counterfactual_checks(reserved, rule, max_samples=32):
    """Flip exactly one event parity: a different finite constraint problem."""
    violations, decisive, n = [], 0, 0
    for row in (r for r in reserved if r["features"]["cycle_four_quotient"]):
        E = list(row["events"])
        a, b, p = E[0]
        E[0] = (a, b, 1-p)
        flipped = tuple(E)
        truth = exact_minimal_contradiction(len(row["T"]), row["forced"], flipped)
        pred = all(structural_features(len(row["T"]), row["forced"], flipped)[k] for k in rule)
        decisive += truth != row["truth"]
        if pred != truth:
            violations.append({"T": row["T"], "pair": row["pair"],
                               "expected": truth, "predicted": pred})
        n += 1
        if n >= max_samples:
            break
    return {"checked": n, "truth_changed": decisive,
            "disagreements": len(violations), "counterexamples": violations[:3],
            "note": "Parity flips form adjacent abstract XOR systems, not necessarily orbit constraints."}


def experiment(math_root):
    # This exact source was already studied: synthesis is reconstruction, not novelty.
    anchor = source_anchor(Path(math_root), SOURCE)
    forced, events, coherent = forced_event_library(math_root)

    trained = {}
    for name in ("TRAIN-C4-C3-N8", "TRAIN-C4-C2-N8"):
        trained[name] = prepared_rows(select_cases(name, forced, events, coherent))
    training = trained["TRAIN-C4-C3-N8"] + trained["TRAIN-C4-C2-N8"]
    if not any(row["truth"] for row in training) or all(row["truth"] for row in training):
        raise ValueError("Training is not discriminating")
    learned = learn(training)
    frozen_rule = tuple(learned["atoms"])
    frozen_rule_digest = digest(frozen_rule)  # freeze before the reserve is loaded

    reserved = {}
    for name in ("RESERVE-C4-C3-N9", "RESERVE-C4-C2-N9"):
        reserved[name] = prepared_rows(select_cases(name, forced, events, coherent))
    holdout = reserved["RESERVE-C4-C3-N9"] + reserved["RESERVE-C4-C2-N9"]
    if not any(row["truth"] for row in holdout) or all(row["truth"] for row in holdout):
        raise ValueError("Reserve is not discriminating")
    metrics = {
        "always_negative": tally(holdout, lambda _: False),
        "unsigned_quotient_cycle": tally(holdout, lambda r: r["features"]["cycle_four_quotient"]),
        "learned_conjunction": tally(holdout, lambda r: conjunction(r, frozen_rule)),
    }
    unsigned_counterexample = next(({"T": r["T"], "pair": r["pair"],
                                     "expected": r["truth"],
                                     "unsigned_prediction": True}
                                    for r in holdout if r["features"]["cycle_four_quotient"]
                                    and not r["truth"]), None)
    return {
        "status": "FINITE_PROGRAM_SYNTHESIS_TESTED_NOT_NEW_THEOREM",
        "model_type": "finite enumerative conjunction learner, fixed feature vocabulary, no LLM",
        "source_anchor": anchor,
        "training_families": {name: {"rows": len(rows), "positives": sum(r["truth"] for r in rows),
                                     "input_sha256": digest([(r["T"], r["pair"]) for r in rows])}
                              for name, rows in trained.items()},
        "generated_rule": learned,
        "frozen_rule_sha256": frozen_rule_digest,
        "reserve_families": {name: {"rows": len(rows), "positives": sum(r["truth"] for r in rows),
                                   "input_sha256": digest([(r["T"], r["pair"]) for r in rows])}
                             for name, rows in reserved.items()},
        "comparison": metrics,
        "unsigned_baseline_counterexample": unsigned_counterexample,
        "relabeling_invariance": invariance_checks(holdout, frozen_rule),
        "parity_counterfactual": counterfactual_checks(holdout, frozen_rule),
        "fixed_rule_contains_known_mechanism": "cycle_four_quotient" in frozen_rule
            and "odd_signed_cycle" in frozen_rule,
        "scientific_claims_certified": 0,
        "autonomous_semantic_comprehension_demonstrated": False,
        "novelty": "RECONSTRUCTION_OF_A_KNOWN_SOURCE_MECHANISM_IN_A_RESTRICTED_GRAMMAR",
        "limits": "Development-level family-disjoint test; reserve authored by same experimenter, not an external blind holdout. Grammar and oracle are human-coded.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--math", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = experiment(args.math)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False)
                           + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"],
                      "proposed_rule": report["generated_rule"]["atoms"],
                      "reserve_results": report["comparison"],
                      "relabel_invariance": report["relabeling_invariance"]["disagreements"],
                      "counterfactual_disagreements": report["parity_counterfactual"]["disagreements"],
                      "claims_certified": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
