"""OMEGA-HYBRID clinic: diagnose REAL-02 examples and prepare *separate* practice.

Uses existing finite-relation oracle; never certifies prose, edits model weights,
or exposes held-out labels to the model. Four-node practice differs in size
from REAL-02's exposed three-node holdout. No Web, no LLM, no paid API.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

from concept_abstraction_lab import check_axioms
from incremental_math_library import read_ledger
from omega_memory_real02 import NODES, TARGETS, concept_name

PRACTICE_NODES = ("a", "b", "c", "d")
MAX_PRACTICE_MASKS = 1 << (len(PRACTICE_NODES) ** 2)


def parse_edges(value, nodes):
    """Accept only exact edge lists; no implicit repairs or deduplication."""
    if not isinstance(value, list) or len(value) > len(nodes) ** 2:
        return None
    parsed = []
    for edge in value:
        if not isinstance(edge, list) or len(edge) != 2 or any(
            type(v) is not str or v not in nodes for v in edge
        ):
            return None
        parsed.append(tuple(edge))
    if len(set(parsed)) != len(parsed):
        return None
    return frozenset(parsed)


def example_report(edges, defining_axioms, declared_positive):
    rel = parse_edges(edges, NODES)
    if rel is None:
        return {"status": "MALFORMED_EDGES", "declared_positive": declared_positive,
                "actual_holds": None}
    checks = check_axioms(NODES, rel)
    failures = {a: checks[a]["counterexample"] for a in defining_axioms
                if not checks[a]["holds"]}
    actual = not failures
    return {"status": "CORRECT" if actual == declared_positive else
            "COUNTEREXAMPLE_TO_MODEL_CLASSIFICATION",
            "declared_positive": declared_positive, "actual_holds": actual,
            "failed_axioms": sorted(failures),
            "witnesses": failures,
            "property_checks_exact_on_three_nodes": True}


def diagnose_card(card):
    """Disambiguate an OMITTED graph from an actual incorrect graph."""
    result = {"status": "BLOCKED", "semantic_prose_certified": False,
              "weights_trained": False, "scope": "FINITE_RELATIONS_3_NODES"}
    if not isinstance(card, dict):
        return {**result, "reason": "MISSING_CARD"}
    concept = concept_name(card.get("concept"))
    if concept not in TARGETS:
        return {**result, "reason": "OUTSIDE_ORACLE_GRAMMAR"}
    sig = TARGETS[concept]
    axioms = card.get("formal_axioms")
    if not isinstance(axioms, list) or any(type(a) is not str for a in axioms) or \
            len(axioms) != len(sig) or len(set(axioms)) != len(sig) or set(axioms) != set(sig):
        return {**result, "reason": "FORMAL_SIGNATURE_MISMATCH", "concept": concept}
    missing = [field for field in ("positive_edges", "negative_edges")
               if field not in card]
    if missing:
        return {**result, "reason": "MISSING_STRUCTURED_EXAMPLES",
                "concept": concept, "missing_fields": missing,
                "mathematical_examples_evaluated": 0}
    pos = example_report(card["positive_edges"], sig, True)
    neg = example_report(card["negative_edges"], sig, False)
    if pos["status"] == "MALFORMED_EDGES" or neg["status"] == "MALFORMED_EDGES":
        decision = "MALFORMED_STRUCTURED_EXAMPLES"
    elif pos["status"] != "CORRECT" or neg["status"] != "CORRECT":
        decision = "MATHEMATICAL_COUNTEREXAMPLE"
    else:
        decision = "BOUNDED_EXAMPLES_PASS"
    return {**result, "status": "BOUNDED_FORMAL_PASS" if
            decision == "BOUNDED_EXAMPLES_PASS" else "BLOCKED",
            "reason": decision, "concept": concept, "positive": pos,
            "negative": neg, "mathematical_examples_evaluated": 2}


def edges_from_mask(mask, nodes=PRACTICE_NODES):
    pairs = [(x, y) for x in nodes for y in nodes]
    return frozenset(pair for bit, pair in enumerate(pairs) if mask & (1 << bit))


def graph_orbit_key(edges, nodes=PRACTICE_NODES):
    """Deduplicate by *all* permutations, not only textual pair ordering."""
    candidates = []
    for perm in permutations(nodes):
        rename = dict(zip(nodes, perm))
        candidates.append(tuple(sorted((rename[a], rename[b]) for a,b in edges)))
    return min(candidates)


def practice_pack(concept, seed="omega-hybrid-four-node-practice-v1", count_each=2):
    """Generate four-node practice without any three-node REAL-02 cases.

    A distinct model-facing payload and answer key are returned. The caller
    MUST store them separately; only model-facing JSON can go to a solver.
    """
    blocked = {"status": "BLOCKED", "reason": "INVALID_PRACTICE_REQUEST"}
    key = concept_name(concept)
    if key not in TARGETS or type(count_each) is not int or not 1 <= count_each <= 4:
        return blocked
    if not isinstance(seed, str) or not seed:
        return blocked
    sig = TARGETS[key]
    candidates = sorted(range(MAX_PRACTICE_MASKS),
                        key=lambda m: sha256((seed + ":" + str(m)).encode()).digest())
    # For any new label order, a graph from the same isomorphism class
    # is considered a duplicate in this practice set.
    used_orbits = set()
    yes, no = [], []
    for mask in candidates:
        edges = edges_from_mask(mask)
        facts = check_axioms(PRACTICE_NODES, edges)
        truth = all(facts[a]["holds"] for a in sig)
        group = yes if truth else no
        if len(group) >= count_each:
            continue
        orbit = graph_orbit_key(edges)
        if orbit in used_orbits:
            continue
        used_orbits.add(orbit)
        group.append((mask, edges, facts))
        if len(yes) == count_each and len(no) == count_each:
            break
    if len(yes) < count_each or len(no) < count_each:
        return {"status": "BLOCKED", "reason": "NOT_ENOUGH_NONISOMORPHIC_CASES",
                "positive_count": len(yes), "negative_count": len(no)}
    selected = yes + no
    # Sort again independently to prevent answer order from revealing truth.
    selected.sort(key=lambda row: sha256((seed + ":display:" + str(row[0])).encode()).digest())
    prompts, keys = [], []
    for idx,(mask,edges,facts) in enumerate(selected):
        case_id = sha256((seed + ":case:" + str(mask)).encode()).hexdigest()[:16]
        failed = {a: facts[a]["counterexample"] for a in sig if not facts[a]["holds"]}
        prompt = {"case_id": case_id, "nodes": list(PRACTICE_NODES),
                  "edges": [list(e) for e in sorted(edges)],
                  "question": "Does this relation satisfy " + key +
                              "? Give JSON {holds: bool, failed_axioms: list}."}
        answer = {"case_id": case_id, "oracle_holds": not failed,
                  "failed_axioms": sorted(failed), "witnesses": failed,
                  "mask": mask}
        prompts.append(prompt)
        keys.append(answer)
    return {"status": "PRACTICE_ONLY_NOT_HOLDOUT",
            "model_inputs": {"protocol": "4_NODE_PRACTICE_V1",
                             "concept": key, "examples": prompts,
                             "oracle_answer_key_included": False},
            "oracle_only": {"protocol": "4_NODE_PRACTICE_V1",
                            "concept": key, "examples": keys},
            "new_skill_demonstrated": False,
            "heldout_cases_reused": False,
            "semantic_prose_certified": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-ledger", type=Path, required=True)
    ap.add_argument("--diagnosis-out", type=Path, required=True)
    ap.add_argument("--model-inputs-out", type=Path, required=True)
    ap.add_argument("--oracle-out", type=Path, required=True)
    ap.add_argument("--seed", default="omega-hybrid-four-node-practice-v1")
    opts = ap.parse_args()
    destinations = [x.resolve() for x in
                    (opts.diagnosis_out,opts.model_inputs_out,opts.oracle_out)]
    if len(set(destinations)) != 3:
        raise SystemExit("REFUSE_SHARED_MODEL_AND_ORACLE_OUTPUT_PATHS")
    rows = read_ledger(opts.source_ledger)
    cards = [r["interpretation_candidate"] for r in rows
             if r.get("record_type") == "EDUCATIONAL_RESEARCH_CANDIDATE"
             and isinstance(r.get("interpretation_candidate"), dict)]
    if len(cards) != 1:
        raise SystemExit("EXPECT_EXACTLY_ONE_CANDIDATE")
    diagnosis = diagnose_card(cards[0])
    pack = practice_pack(cards[0]["concept"], opts.seed)
    if pack["status"] == "BLOCKED":
        raise SystemExit(pack["reason"])
    for path in destinations:
        path.parent.mkdir(parents=True, exist_ok=True)
    opts.diagnosis_out.write_text(json.dumps(diagnosis,indent=2)+"\n")
    opts.model_inputs_out.write_text(json.dumps(pack["model_inputs"],indent=2)+"\n")
    opts.oracle_out.write_text(json.dumps(pack["oracle_only"],indent=2)+"\n")
    print(json.dumps({"diagnosis":diagnosis["reason"],
                      "practice":pack["status"],"training_performed":False}))


if __name__ == "__main__":
    main()
