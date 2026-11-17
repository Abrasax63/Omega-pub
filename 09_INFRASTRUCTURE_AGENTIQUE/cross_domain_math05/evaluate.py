#!/usr/bin/env python3
"""Cross-domain transfer of untouched Omega math engine to four historical bricks.

Deliberately tests code frozen before the four new source documents were added.
This cannot be interpreted as testing a general-purpose model: source IDs may
not be supported by the prior engine. Independent finite microchecks supplement
the documentary annotations, but DO NOT prove the general source theorems.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = HERE / "INPUTS_FROZEN.json"
GOLD = HERE / "GOLD_FROZEN.json"
INPUT_SHA = "009cbd77bb405785ff74256d722b528683cbcd3f"
GOLD_SHA = "4a8c7e32ec834e1b106004fb3c51837b479022b2"
ENGINE_PATH = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/real_math_scope03/engine.py"
ENGINE_SHA = "4e4bf62de81bea0eebe1a7a80562e002698d0cd2"
SOURCES = {
    "BR-ACC-01": ("BR-ACC-01_CLOTURE_ACCESSIBLE.md", "006a57586ae1e7f100c48d7bc4f159723c2b3352", "Fact(L_E) = L_H"),
    "BR-DESC-01": ("BR-DESC-01_SUFFISANCE_VS_AUTONOMIE.md", "fb584f81bdd285da480df1eafacea75d0ab77c19", "deux catégories"),
    "BR-OBS-CAP-03": ("BR-OBS-CAP-03_FIBER_BOX_TU.md", "e2db670f4f9458a848b7d8719f2a656dbfdab46b", "totalement unimodulaire"),
    "BR-AFFINE-TREE-CORE": ("BR-AFFINE-TREE-CORE_BRIQUE.md", "ff8b35f41aca9de2d362f0bf4852f133527a479d", "minimal par inclusion"),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def pinned_file(path: Path, sha: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing source or symlink: " + str(path))
    data = path.read_bytes()
    if git_blob(data) != sha:
        raise ValueError("source/gold modified after freeze: " + str(path))
    return data


def load_engine_frozen():
    data = pinned_file(ENGINE_PATH, ENGINE_SHA)
    spec = importlib.util.spec_from_file_location("frozen_math_engine_transfer_05", str(ENGINE_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load pinned engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_snapshots() -> dict:
    result = {}
    for source_id, (filename, sha, anchor) in SOURCES.items():
        path = HERE / "source_snapshot" / filename
        body = pinned_file(path, sha).decode("utf-8")
        if anchor not in body:
            raise ValueError("missing source anchor: " + source_id)
        result[source_id] = {
            "file": "source_snapshot/" + filename,
            "historical_git_blob": sha,
            "anchor": anchor,
            "source_character_count": len(body),
        }
    return result


def finite_access_example() -> dict:
    # One total action: a->b->b, pi(a)=0, pi(b)=1, initial E={a}.
    # Observation words suffice because the sole action label is fixed.
    transition = {0: 1, 1: 1}
    results = []
    for length in range(1, 7):
        # Enumerate factors from E words with all lengths <=2*length+2.
        from_E = set()
        for full_length in range(length, 2*length+3):
            state = 0
            observations = []
            for _ in range(full_length):
                observations.append(str(state))
                state = transition[state]
            word = "".join(observations)
            from_E.update(word[i:i+length] for i in range(full_length-length+1))
        from_H = set()
        for start in (0, 1):
            state = start
            observations = []
            for _ in range(length):
                observations.append(str(state))
                state = transition[state]
            from_H.add("".join(observations))
        results.append({
            "length": length, "factors_E": sorted(from_E),
            "words_H": sorted(from_H), "match": from_E == from_H,
        })
    # This exact finite example distinguishes access failure from local closure.
    return {
        "kind": "finite_accessibility_one_action",
        "checked_lengths": 6,
        "all_match": all(row["match"] for row in results),
        "one_symbol_access_defect": "1" in from_H or "1" in results[0]["words_H"],
        "per_length": results,
        "limitation": "finite word horizons 1..6, not a proof of universal language equality",
    }


def finite_fiber_example() -> dict:
    # Four distinct witnesses assigned to one of two local motifs.
    # The selection model assumes witnesses are independent objects.
    assignment = ("A", "A", "B", "B")
    seen = set()
    for selection_bits in range(1 << len(assignment)):
        counts = {"A": 0, "B": 0}
        for i, category in enumerate(assignment):
            if (selection_bits >> i) & 1:
                counts[category] += 1
        seen.add((counts["A"], counts["B"]))
    expected = {(a, b) for a in range(3) for b in range(3)}
    return {
        "kind": "finite_independent_witness_box",
        "witnesses": len(assignment), "subsets_enumerated": 1 << len(assignment),
        "distinct_multiplicity_vectors": len(seen),
        "all_match": seen == expected,
        "limitation": "one constructed finite sigma, not a proof of general total unimodularity",
    }


def summarize(rows: list[dict], arm: str) -> dict:
    correct = sum(r[arm] == r["gold"] for r in rows)
    confident = [r["id"] for r in rows if r[arm] != "ABSTAIN" and r[arm] != r["gold"]]
    ab = sum(r[arm] == "ABSTAIN" for r in rows)
    positive_correct = sum(r[arm] == r["gold"] and r[arm] != "ABSTAIN" for r in rows)
    return {
        "total": len(rows), "correct": correct, "accuracy": correct / len(rows),
        "abstained": ab, "correct_nonabstain": positive_correct,
        "false_confident": confident,
        "correct_abstentions": sum(r[arm] == r["gold"] == "ABSTAIN" for r in rows),
    }


def run() -> dict:
    source_manifest = verify_snapshots()
    frozen_engine = load_engine_frozen()
    input_cases = json.loads(pinned_file(INPUT, INPUT_SHA).decode("utf-8"))["cases"]
    # Crucial: do not load GOLD until after generating all predictions.
    predictions = {}
    for case in input_cases:
        pred = frozen_engine.evaluate_case(case)
        predictions[case["id"]] = pred

    gold = json.loads(pinned_file(GOLD, GOLD_SHA).decode("utf-8"))
    labels = {g["id"]: g for g in gold["cases"]}
    if len(input_cases) != 16 or len(labels) != 16:
        raise ValueError("16-case preregistered cohort changed")
    if {x["id"] for x in input_cases} != set(labels):
        raise ValueError("input-gold ID mismatch")
    rows = []
    for case in input_cases:
        label = labels[case["id"]]
        if label["source_id"] != case["source_id"] or case["source_id"] not in SOURCES:
            raise ValueError("case/source ID mismatch")
        rows.append({
            "id": case["id"], "source_id": case["source_id"],
            "question": case["question"], "gold": label["verdict"],
            "gold_reason": label["reason"],
            "frozen_engine": predictions[case["id"]]["verdict"],
            "engine_reason": predictions[case["id"]]["reason"],
            "abstain_all": "ABSTAIN",
        })
    known_distribution = {tag: sum(r["gold"] == tag for r in rows)
                          for tag in ("SUPPORTED", "CONTRADICTED", "ABSTAIN")}
    if known_distribution != {"SUPPORTED": 6, "CONTRADICTED": 6, "ABSTAIN": 4}:
        raise ValueError("expected distribution drifted")
    frozen = summarize(rows, "frozen_engine")
    baseline = summarize(rows, "abstain_all")
    finite = {"accessible_language": finite_access_example(), "fiber_capacity": finite_fiber_example()}
    microchecks = all(r["all_match"] for r in finite.values())
    criterion = (
        frozen["correct_nonabstain"] >= 8
        and not frozen["false_confident"]
        and frozen["correct"] > baseline["correct"]
        and microchecks
    )
    return {
        "status": "CROSS_DOMAIN_FROZEN_ENGINE_TRANSFER_V05",
        "frozen_engine_git_blob": ENGINE_SHA,
        "source_branch": "migration/ravi2-ccs-public-2026-11-04",
        "source_commit": "2f71a6b8ed03914c0b5d308520d30e0133d9e9ad",
        "source_snapshots": source_manifest,
        "input_git_blob": INPUT_SHA, "gold_git_blob": GOLD_SHA,
        "gold_class_distribution": known_distribution,
        "frozen_engine": frozen, "abstain_all_baseline": baseline,
        "finite_microchecks_passed": microchecks,
        "finite_microchecks": finite,
        "pre_registered_transfer_criterion_met": criterion,
        "unrecognized_source_ids_by_engine": sorted(set(SOURCES) - set(frozen_engine.SOURCE_PATHS)),
        "interpretation": "Unrecognized source IDs are an architectural interface failure, not isolated proof of linguistic inadequacy. Test corpus and documentary gold by the same author; finite microchecks do not certify original theorems.",
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            parser.error("no output inside repository")
        target.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
