#!/usr/bin/env python3
"""Frozen real-card comparison, with independent finite Rule-90 checkers.

Predictions are generated before manual gold is loaded.
This validates *source-grounded retrieval on three documents*, not novel proofs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from engine import ROOT, evaluate_case, lexical_baseline, verify_sources

HERE = Path(__file__).resolve().parent
INPUT = HERE / "INPUTS_FROZEN.json"
GOLD = HERE / "GOLD_FROZEN.json"
INPUT_SHA = "eddb12ce789f6264d5f4fcd75b2aba1cef6df5c2"
GOLD_SHA = "0765742dd8b531acaf5e694a24420875bd81133c"


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def frozen(path: Path, sha: str) -> dict:
    data = path.read_bytes()
    if git_blob(data) != sha:
        raise ValueError("frozen data mutated: " + path.name)
    return json.loads(data.decode("utf-8"))


def step90(state: int, n: int) -> int:
    # Independently reconstruct linear operator from the cellular automaton.
    value = 0
    for i in range(n):
        left = (state >> ((i-1) % n)) & 1
        right = (state >> ((i+1) % n)) & 1
        value |= (left ^ right) << i
    return value


def gf2_rank(columns: list[int]) -> int:
    pivots = {}
    for c in columns:
        x = c
        while x:
            pivot = x.bit_length()-1
            if pivot in pivots:
                x ^= pivots[pivot]
            else:
                pivots[pivot] = x
                break
    return len(pivots)


def rule90_finite_invariant(n: int, t: int, kind: str) -> int:
    if not 2 <= n <= 32 or not 0 <= t <= 12:
        raise ValueError("finite exact range exceeded")
    columns = []
    for i in range(n):
        state = 1 << i
        for _ in range(t):
            state = step90(state, n)
        columns.append(state)
    rank = gf2_rank(columns)
    return rank if kind == "rank" else n - rank


def majority_uniform_exact(n: int, h: int) -> tuple[bool, list[int]]:
    if not 3 <= n <= 10 or not 0 <= h <= 5:
        raise ValueError("Majority enumeration budget exceeded")
    buckets = [0] * (1 << (h+1))
    for initial in range(1 << n):
        state = initial
        word = 0
        for t in range(h+1):
            local = sum((state >> (idx % n)) & 1 for idx in (-1, 0, 1))
            word |= int(local >= 2) << t
            state = step90(state, n)
        buckets[word] += 1
    return len(set(buckets)) == 1, buckets


def metrics(rows: list[dict], label: str) -> dict:
    correct = sum(r[label] == r["gold"] for r in rows)
    confident_errors = sum(r[label] in ("SUPPORTED", "CONTRADICTED") and r[label] != r["gold"] for r in rows)
    abstained = sum(r[label] == r["gold"] == "ABSTAIN" for r in rows)
    return {"correct": correct, "total": len(rows), "accuracy": correct/len(rows),
            "confident_errors": confident_errors, "correct_abstentions": abstained}


def run() -> dict:
    notes = verify_sources(ROOT)
    inputs = frozen(INPUT, INPUT_SHA)
    # Predictions made without opening or loading the gold annotations.
    predictions = {
        c["id"]: {"engine": evaluate_case(c, notes),
                  "lexical": lexical_baseline(c, notes)}
        for c in inputs["cases"]
    }
    gold = frozen(GOLD, GOLD_SHA)
    marks = {c["id"]: c for c in gold["cases"]}
    if len(inputs["cases"]) != 24 or len(marks) != 24:
        raise ValueError("not 24 frozen questions")
    if set(predictions) != set(marks):
        raise ValueError("case ID mismatch")

    rows = []
    finite_checks = []
    for c in inputs["cases"]:
        desired = marks[c["id"]]
        if desired["source_id"] != c["source_id"]:
            raise ValueError("source mismatch")
        decision = predictions[c["id"]]["engine"]
        evidence = decision.get("evidence")
        cite_ok = True
        if decision["verdict"] in ("SUPPORTED", "CONTRADICTED"):
            note = notes[c["source_id"]]
            cite_ok = (
                isinstance(evidence, dict)
                and evidence.get("source_file") == note["path"]
                and evidence.get("source_blob") == note["blob"]
                and isinstance(evidence.get("line"), int)
                and 0 < evidence["line"] <= len(note["text"].splitlines())
                and evidence.get("excerpt") == note["text"].splitlines()[evidence["line"]-1].strip()
            )
        math_check = None
        observation = decision.get("finite_case", {})
        if observation.get("domain") == "kernel_rank":
            v = rule90_finite_invariant(observation["n"], observation["t"], observation["kind"])
            math_check = {
                "method": "independent_GF2_linear_algebra",
                "exact_value": v,
                "matches_reported_formula": v == observation["expected_formula"],
                "matches_confident_verdict": (observation["claimed"] == v)
                    == (decision["verdict"] == "SUPPORTED"),
            }
            finite_checks.append(math_check)
        elif observation.get("domain") == "majority":
            uniform, buckets = majority_uniform_exact(observation["n"], observation["h"])
            claimed_uni = observation["claimed_uniformity"]
            claimed_ent = observation["claimed_entropy"]
            expected_support = ((claimed_uni == uniform) if claimed_uni is not None else
                                (uniform and claimed_ent == observation["h"]+1))
            math_check = {
                "method": "full_initial_state_majority_enumeration",
                "uniform": uniform, "counts": buckets,
                "matches_document_theorem": uniform,
                "matches_confident_verdict": expected_support == (decision["verdict"] == "SUPPORTED"),
            }
            finite_checks.append(math_check)
        rows.append({
            "id": c["id"], "source_id": c["source_id"], "question": c["question"],
            "gold": desired["verdict"], "gold_reason": desired["rationale"],
            "engine": decision["verdict"],
            "baseline": predictions[c["id"]]["lexical"]["verdict"],
            "reason": decision["reason"], "evidence": evidence,
            "citation_valid": bool(cite_ok), "finite_check": math_check,
        })
    a, b = metrics(rows, "engine"), metrics(rows, "baseline")
    false_decisions = [r["id"] for r in rows if r["engine"] != "ABSTAIN" and r["engine"] != r["gold"]]
    checks_pass = bool(finite_checks) and all(
        f["matches_reported_formula"] and f["matches_confident_verdict"]
        if "matches_reported_formula" in f
        else f["matches_document_theorem"] and f["matches_confident_verdict"]
        for f in finite_checks
    )
    criterion = a["correct"] >= 18 and a["confident_errors"] == 0 and a["correct_abstentions"] >= 4 and checks_pass and a["accuracy"] > b["accuracy"] and all(r["citation_valid"] for r in rows)
    return {
        "status": "NONBLIND_REAL_DOCUMENT_SCOPED_CLAIM_CHECK",
        "source_ids": {k: {"path": v["path"], "blob": v["blob"]} for k, v in notes.items()},
        "frozen_inputs_git_blob": INPUT_SHA, "frozen_gold_git_blob": GOLD_SHA,
        "engine_metrics": a, "lexical_baseline_metrics": b,
        "finite_independent_checks": len(finite_checks), "finite_checks_passed": checks_pass,
        "all_source_citations_valid": all(r["citation_valid"] for r in rows),
        "false_confident_decisions": false_decisions,
        "preregistered_local_criterion_met": criterion,
        "limits": "Three documents, controlled templates, given source IDs, same-author manual gold. Exact finite independent checks cover R90 but not C4; no external referee, theorem proof, natural-language NLU, or scientific certification.",
        "rows": rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = run()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("report must be outside repository")
        dest.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
