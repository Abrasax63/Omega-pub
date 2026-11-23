"""Omega hybrid-learning evidence gate and adaptive practice planner.

A non-LLM, fail-closed bridge for the existing PR #231 educational ledger and
REAL-02 finite-relations oracle. Does not train weights, fetch the Web, change
main, or certify scientific claims. Run experiments elsewhere; feed back raw
outputs and source snapshots for an inspectable decision.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
from typing import Any

ARMS = ("D", "M", "N")  # direct / verified memory / neutral control
MAX_TASKS = 200


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def checksum(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def source_gate(record: dict, snapshots: list[dict]) -> dict:
    """Check exact quote against a snapshot and its *ledger-recorded* digest.

    Authenticity of the snapshot is NOT independently established; this checks
    internal correspondence only. A quote is never proof of semantic fidelity.
    """
    card = record.get("interpretation_candidate")
    metadata = record.get("sources", [])
    result = {"status": "QUARANTINE", "reason": "INVALID_CANDIDATE",
              "authenticity": "NOT_INDEPENDENTLY_RETRIEVED"}
    if not isinstance(card, dict) or not isinstance(metadata, list):
        return result
    quote, page = card.get("exact_quote"), card.get("source_page_id")
    kind = card.get("source_kind", "web")  # legacy records cite Wikipedia
    if not isinstance(quote, str) or len(quote.strip()) < 20:
        result["reason"] = "QUOTE_MISSING_OR_TOO_SHORT"
        return result
    if type(page) is not int or kind not in ("web", "primary"):
        result["reason"] = "INVALID_SOURCE_ID_OR_KIND"
        return result
    candidates = [s for s in metadata if isinstance(s, dict)
                  and s.get("page_id") == page
                  and s.get("source_kind", "web") == kind]
    if len(candidates) != 1:
        result["reason"] = "SOURCE_METADATA_NOT_UNIQUE"
        return result
    meta = candidates[0]
    matched = [s for s in snapshots if isinstance(s, dict)
               and s.get("source_kind") == kind
               and s.get("page_id") == page
               and s.get("revision_id") == meta.get("revision_id")]
    if len(matched) != 1:
        result["reason"] = "SNAPSHOT_MISSING_OR_AMBIGUOUS"
        return result
    snap = matched[0]
    excerpt = snap.get("excerpt")
    if not isinstance(excerpt, str) or not isinstance(meta.get("excerpt_sha256"), str):
        result["reason"] = "SNAPSHOT_BYTES_NOT_AVAILABLE"
        return result
    if checksum(excerpt) != meta["excerpt_sha256"]:
        result["reason"] = "SOURCE_DIGEST_MISMATCH"
        return result
    if quote not in excerpt:
        result["reason"] = "QUOTE_NOT_IN_DECLARED_SOURCE"
        return result
    result.update(status="SNAPSHOT_QUOTE_MATCH", reason="PASS",
                  source_kind=kind, page_id=page,
                  revision_id=meta.get("revision_id"),
                  excerpt_sha256=meta["excerpt_sha256"])
    return result


def bounded_gate(record: dict, gate: dict, oracle=None) -> dict:
    """Existing exact oracle for a finite, FIXED grammar; prose is unverified."""
    out = {"status": "NOT_VERIFIED", "free_text_semantics": "NOT_VERIFIED",
           "new_theorem_certified": False}
    if gate.get("status") != "SNAPSHOT_QUOTE_MATCH":
        out["reason"] = "SOURCE_GATE_FAILED"
        return out
    card = record.get("interpretation_candidate") or {}
    # Import the existing contract, not a second competing relation oracle.
    from omega_memory_real02 import TARGETS, concept_name, is_example
    name = concept_name(card.get("concept"))
    if name is None:
        out["reason"] = "OUTSIDE_FINITE_ORACLE_GRAMMAR"
        return out
    expected = TARGETS[name]
    observed = card.get("formal_axioms")
    if not isinstance(observed, list) or len(observed) != len(expected) or \
            any(type(a) is not str for a in observed) or \
            len(set(observed)) != len(expected) or set(observed) != set(expected):
        out["reason"] = "FORMAL_SIGNATURE_MISMATCH"
        return out
    checker = oracle if oracle is not None else is_example
    if not checker(card.get("positive_edges"), expected, True):
        out["reason"] = "POSITIVE_EXAMPLE_INVALID"
        return out
    if not checker(card.get("negative_edges"), expected, False):
        out["reason"] = "NEGATIVE_EXAMPLE_INVALID"
        return out
    out.update(status="BOUNDED_FORMAL_PASS", reason="PASS", concept=name,
               required_axioms=list(expected),
               scope="FINITE_RELATIONS_ONLY")
    return out


def parse_prediction(raw: str, axioms: tuple[str, ...]) -> tuple[str, bool | None]:
    """No post-hoc JSON repair. Invalid and explicit abstention are distinct."""
    if not isinstance(raw, str):
        return "INVALID", None
    try:
        obj = json.loads(raw.strip())
    except (ValueError, TypeError):
        return "INVALID", None
    if not isinstance(obj, dict):
        return "INVALID", None
    if obj.get("abstain") is True:
        return ("ABSTAIN", None) if set(obj) == {"abstain"} else ("INVALID", None)
    if set(obj) != {"holds", "failed_axioms"} or type(obj["holds"]) is not bool:
        return "INVALID", None
    failed = obj["failed_axioms"]
    if not isinstance(failed, list) or any(type(a) is not str for a in failed) \
            or len(failed) != len(set(failed)) or any(a not in axioms for a in failed) \
            or obj["holds"] != (len(failed) == 0):
        return "INVALID", None
    return "ANSWER", obj["holds"]


def evaluate_holdout(packet: dict, axioms: tuple[str, ...], oracle=None) -> dict:
    """Score blind *reported* model outputs; compute truth using local oracle.

    A manifest saying the answers were hidden is not proof of blindness.
    The code deliberately never passes oracle truths into any model prompt.
    """
    block = {"status": "BLOCKED", "reason": "INVALID_OR_UNFROZEN_HOLDOUT"}
    if packet.get("protocol_frozen") is not True or packet.get("source_disjoint") is not True:
        return block
    trials = packet.get("trials")
    if not isinstance(trials, list) or not 1 <= len(trials) <= MAX_TASKS:
        return block
    # The oracle depends on a finite exact check, never on a model's self-grade.
    if oracle is None:
        from concept_abstraction_lab import check_axioms
        def oracle(edges):
            nodes = ("a", "b", "c")
            pairs = [tuple(e) for e in edges]
            if len(set(pairs)) != len(pairs) or any(
                len(p) != 2 or p[0] not in nodes or p[1] not in nodes for p in pairs
            ):
                raise ValueError("INVALID_RELATION")
            facts = check_axioms(nodes, frozenset(pairs))
            return all(facts[a]["holds"] for a in axioms)
    seen_ids, seen_relations = set(), set()
    stats = {arm: {"correct": 0, "wrong": 0, "abstain": 0, "invalid": 0}
             for arm in ARMS}
    rows = []
    for t in trials:
        if not isinstance(t, dict) or not isinstance(t.get("id"), str) or \
                not t["id"] or t["id"] in seen_ids:
            return {"status": "BLOCKED", "reason": "DUPLICATE_OR_INVALID_CASE_ID"}
        seen_ids.add(t["id"])
        edges = t.get("edges")
        if not isinstance(edges, list):
            return {"status": "BLOCKED", "reason": "MISSING_RELATION"}
        try:
            relation_key = canonical(sorted(edges))
            truth = oracle(edges)
            if type(truth) is not bool:
                raise ValueError("NON_BOOLEAN_ORACLE")
        except (TypeError, ValueError, KeyError, IndexError):
            return {"status": "BLOCKED", "reason": "ORACLE_OR_RELATION_INVALID"}
        if relation_key in seen_relations:
            return {"status": "BLOCKED", "reason": "DUPLICATE_RELATION"}
        seen_relations.add(relation_key)
        outputs, token_counts = t.get("outputs"), t.get("prompt_tokens")
        if not isinstance(outputs, dict) or set(outputs) != set(ARMS) or \
                not isinstance(token_counts, dict) or set(token_counts) != set(ARMS) or \
                any(type(token_counts[a]) is not int or token_counts[a] <= 0 for a in ARMS):
            return {"status": "BLOCKED", "reason": "MISSING_ARM_OR_TOKEN_COUNTS"}
        if (max(token_counts.values()) - min(token_counts.values())) / max(token_counts.values()) > .05:
            return {"status": "BLOCKED", "reason": "TOKEN_BUDGET_IMBALANCE"}
        statuses = {}
        for arm in ARMS:
            category, answer = parse_prediction(outputs[arm], axioms)
            outcome = "invalid" if category == "INVALID" else (
                "abstain" if category == "ABSTAIN" else
                "correct" if answer == truth else "wrong")
            stats[arm][outcome] += 1
            statuses[arm] = outcome
        rows.append({"case_id": t["id"], "outcomes": statuses,
                     "oracle_boolean_truth": truth})
    score = {arm: stats[arm]["correct"] for arm in ARMS}
    gain = {"memory_vs_direct": score["M"] - score["D"],
            "memory_vs_neutral": score["M"] - score["N"]}
    # This is a directional, *descriptive* test only, not a p-value or certification.
    return {"status": "SCORED_DESCRIPTIVE_ONLY", "n": len(rows),
            "metrics": stats, "net_gain": gain, "cases": rows,
            "blindness": "DECLARED_NOT_INDEPENDENTLY_AUDITED",
            "weight_update": False, "statistical_gain_proven": False}


def next_action(source: dict, bounded: dict, evaluation: dict | None = None) -> dict:
    """Explicit deterministic planner, not an LLM with self-awareness."""
    if source.get("status") != "SNAPSHOT_QUOTE_MATCH":
        action, reason = "RESEARCH", "SOURCE_OR_ATTRIBUTION_UNTRUSTED"
    elif bounded.get("status") != "BOUNDED_FORMAL_PASS":
        action, reason = "REVISE_REPRESENTATION", "BOUNDED_SEMANTICS_NOT_PASSED"
    elif not evaluation or evaluation.get("status") != "SCORED_DESCRIPTIVE_ONLY":
        action, reason = "PRACTICE", "TRANSFER_UNMEASURED"
    elif evaluation["net_gain"]["memory_vs_direct"] <= 0 or \
            evaluation["net_gain"]["memory_vs_neutral"] <= 0:
        action, reason = "PRACTICE", "NO_OBSERVED_MEMORY_ADVANTAGE"
    else:
        action, reason = "CHALLENGE", "PRELIMINARY_GAIN_NEEDS_INDEPENDENT_REPLICATION"
    return {"action": action, "reason": reason, "planner": "DETERMINISTIC_RULES_V1"}


def select_exercise(pool: list[dict], previous: list[dict], mode="adaptive", seed=0) -> dict:
    """Compare policies without generating test-set answers for the model."""
    if mode not in ("progressive", "adaptive", "random"):
        raise ValueError("UNKNOWN_POLICY")
    done = {x["exercise_id"] for x in previous if x.get("exercise_id")}
    choices = [x for x in pool if x.get("id") not in done]
    if not choices or len({x.get("id") for x in pool}) != len(pool):
        raise ValueError("NO_UNIQUE_UNSEEN_EXERCISES")
    if any(type(x.get("difficulty")) is not int or not 1 <= x["difficulty"] <= 5
           or not isinstance(x.get("id"), str) for x in choices):
        raise ValueError("INVALID_DIFFICULTY_OR_ID")
    if mode == "random":
        picked = random.Random(seed).choice(sorted(choices, key=lambda x: x["id"]))
    elif mode == "progressive":
        picked = min(choices, key=lambda x: (x["difficulty"], x["id"]))
    else:
        recent = [x for x in previous if x.get("result") in ("correct", "wrong")][-8:]
        rate = sum(x["result"] == "correct" for x in recent) / len(recent) if recent else .5
        target = max(1, min(5, round(1 + 4 * rate)))
        picked = min(choices, key=lambda x: (abs(x["difficulty"]-target), x["id"]))
    return {"exercise_id": picked["id"], "difficulty": picked["difficulty"],
            "policy": mode, "selection_is_model_learning": False}


def inspect_ledger(ledger_path: Path, snapshots: list[dict], episode_path: Path | None = None):
    """Consume the existing tamper-evident ledger, not a parallel fact store."""
    from incremental_math_library import read_ledger, append_candidate, digest
    source_records = read_ledger(ledger_path)  # raises if chain has been altered
    reports = []
    for row in source_records:
        if row.get("record_type") != "EDUCATIONAL_RESEARCH_CANDIDATE":
            continue
        s = source_gate(row, snapshots)
        f = bounded_gate(row, s)
        decision = next_action(s, f)
        report = {"candidate_id": row.get("candidate_id"), "source": s,
                  "bounded": f, "decision": decision,
                  "model_new_skill_demonstrated": False,
                  "semantic_fidelity_certified": False}
        reports.append(report)
        if episode_path is not None:
            episode = {"record_type": "LEARNING_EPISODE",
                       "candidate_id": digest({"learning_gate_v1": report}),
                       "source_candidate_id": row.get("candidate_id"),
                       "learning_gate_v1": report, "publication_level": "QUARANTINE_ONLY",
                       "model_weights_updated": False}
            append_candidate(episode_path, episode)
    return {"status": "AUDITED_NOT_TRAINED", "records": len(reports),
            "reports": reports, "training_performed": False,
            "scientific_claims_certified": 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True,
                   help="Existing PR 231 source candidate JSONL")
    p.add_argument("--snapshots", type=Path, required=True,
                   help="JSON list of immutable source snapshots with excerpts")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--episode-ledger", type=Path,
                   help="Optional append-only quarantined episodes, NEVER certified memory")
    args = p.parse_args()
    snapshots = json.loads(args.snapshots.read_text(encoding="utf-8"))
    if not isinstance(snapshots, list):
        raise ValueError("SNAPSHOTS_MUST_BE_LIST")
    result = inspect_ledger(args.ledger, snapshots, args.episode_ledger)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(canonical({"status": result["status"], "records": result["records"]}))


if __name__ == "__main__":
    main()
