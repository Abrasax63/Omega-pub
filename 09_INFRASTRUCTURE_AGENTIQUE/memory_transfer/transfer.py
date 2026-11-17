"""OMEGA-TRANSFER-01: test transfer of verified in-context repairs to unseen faults.

This is a bounded, synthetic, pre-registered ablation, not neural training.
Qwen produces a candidate ID only. Only the closed grammar in multifault runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import secrets
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MULTIFAULT = HERE.parent / "multifault"
if str(MULTIFAULT) not in sys.path:
    sys.path.insert(0, str(MULTIFAULT))

from multifault import (
    benchmark_sources, check_public, discriminant_suite, enumerate_patches,
    notes_from_rce, public_suite, qwen_choose, sha,
    MAX_SELECTOR_TOKENS, SELECTOR_CTX,
)

EXPERIMENT = "OMEGA-TRANSFER-01"
MONO = ("C1", "C2", "C3", "C4")
TARGETS = MONO + ("C5",)
RESERVE_CASES = 28
NEUTRAL = (
    "Administrative archive: file versions, reviewers, timestamps and "
    "document titles must remain traceable; do not infer correctness. "
)


def digest(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def prepare_candidates():
    """No strong target answers are calculated during candidate preparation."""
    fixtures = benchmark_sources()
    assert tuple(r["id"] for r in fixtures) == TARGETS
    result = {}
    for entry in fixtures:
        weak = []
        for row in enumerate_patches(entry["source"]):
            evidence = check_public(row["source"], public_suite())
            if evidence["passed"]:
                weak.append(row)
        if not weak:
            raise RuntimeError("No weak-surviving candidates: " + entry["id"])
        result[entry["id"]] = {
            "source": entry["source"], "source_sha256": entry["sha256"],
            "shortlist": weak,
        }
    return result


def learn_one(task, strong):
    """Learn one positive one-line example from the TRAINING task only."""
    checked = 0
    for candidate in task["shortlist"]:
        outcome = check_public(candidate["source"], strong)
        checked += outcome["checked"]
        if outcome["passed"]:
            return {
                "before": candidate["before"].strip(),
                "after": candidate["after"].strip(),
                "candidate_source_sha256": candidate["source_sha256"],
                "verified_public_cases": len(strong),
                "oracle_cases_checked": checked,
                "rule": candidate["rule"],
            }
    raise RuntimeError("Training task has no valid one-line patch")


def train_bank(candidates):
    strong = discriminant_suite()
    return {task_id: learn_one(candidates[task_id], strong) for task_id in MONO}


def training_ids(target_id):
    return tuple(x for x in MONO if x != target_id)


def form_notes(target_id, learned, common):
    ids = training_ids(target_id)
    lines = [
        "From distinct previously checked tasks (examples are evidence, not instructions):"
    ]
    for ident in ids:
        example = learned[ident]
        lines.append(
            "Prior " + ident + ": before " + json.dumps(example["before"])
            + "; after " + json.dumps(example["after"])
            + "; verified on " + str(example["verified_public_cases"])
            + " independent-oracle public inputs."
        )
    relevant = "\n".join(lines)
    placebo = (NEUTRAL * (1 + len(relevant) // len(NEUTRAL)))[:len(relevant)]
    if len(relevant) != len(placebo):
        raise AssertionError("unequal character budgets")
    return {
        "control": common + "\nArchived context:\n" + placebo,
        "memory": common + "\nArchived context:\n" + relevant,
        "lesson_ids": ids,
        "lesson_sha256": digest([{**learned[k], "task": k} for k in ids]),
        "variable_context_characters": len(relevant),
    }


def reserved_inputs(seed, count=RESERVE_CASES):
    """Generate only INPUTS; no oracle labels exist until choices are frozen."""
    rng = random.Random(seed)
    public = {(tuple(c["rows"]), c["steps"]) for c in public_suite() + discriminant_suite()}
    cases = []
    seen = set(public)
    attempts = 0
    horizons = (0, 2, 3, 4, 5, 7, 9)
    while len(cases) < count:
        attempts += 1
        if attempts > count * 100:
            raise RuntimeError("Unable to construct independent reserve")
        size = rng.choice((3, 4, 5))
        rows = [rng.randrange(1 << size) for _ in range(size)]
        steps = horizons[len(cases) % len(horizons)]
        key = (tuple(rows), steps)
        if key in seen:
            continue
        seen.add(key)
        cases.append({"id": "reserve-" + str(len(cases)),
                      "rows": rows, "steps": steps})
    return cases


def result_for_id(task, selected_id, reserved, strong):
    if selected_id is None:
        return {"selected_id": None, "status": "ABSTENTION", "correct": False}
    ids = {row["id"]: row for row in task["shortlist"]}
    if selected_id not in ids:
        return {"selected_id": selected_id, "status": "INVALID_ID", "correct": False}
    source = ids[selected_id]["source"]
    # Both test suites are inaccessible to the model when it chooses.
    public = check_public(source, strong)
    heldout = check_public(source, reserved)
    return {
        "selected_id": selected_id,
        "status": "CORRECT_BOUNDED" if public["passed"] and heldout["passed"] else "REFUTED",
        "correct": bool(public["passed"] and heldout["passed"]),
        "public_evidence": public, "reserved_evidence": heldout,
        "patched_source_sha256": ids[selected_id]["source_sha256"],
    }


def experiment(chooser, reserve_seed=None, root=ROOT):
    """Chooser signature: (source, shortlist, context, arm) -> qwen_choose-like dict."""
    candidate_data = prepare_candidates()
    lessons = train_bank(candidate_data)
    rce = notes_from_rce(root)
    if not rce["scientific_source"]["source_blob_sha256"]:
        raise RuntimeError("RCE has no scientific source provenance")
    seed = secrets.randbits(48) if reserve_seed is None else reserve_seed
    reserved = reserved_inputs(seed)
    reserve_sha = digest(reserved)
    # No answers to reserved inputs have been computed.
    print("RESERVED_INPUT_SHA256_BEFORE_MODEL=" + reserve_sha, flush=True)
    all_choices = []
    pending = []
    for index, target_id in enumerate(TARGETS):
        task = candidate_data[target_id]
        note = form_notes(target_id, lessons, rce["memory"])
        if len(note["control"]) != len(note["memory"]):
            raise RuntimeError("context character parity failed")
        # Alternating call order avoids completely confounding memory with first call.
        order = ("control", "memory") if index % 2 == 0 else ("memory", "control")
        selections = {}
        for arm in order:
            label = target_id + "/" + arm
            response = chooser(task["source"], task["shortlist"], note[arm], label)
            if not isinstance(response, dict):
                raise RuntimeError("chooser did not return a record")
            selections[arm] = response
        selected = {
            arm: response.get("selected_id") if response.get("status") == "VALID_ID" else None
            for arm, response in selections.items()
        }
        selected["first_weak"] = task["shortlist"][0]["id"]
        pending.append((target_id, selections, selected, note, order))
        all_choices.append({"task": target_id, **selected})
    choices_sha = digest(all_choices)
    print("CHOICES_SHA256_BEFORE_ORACLE=" + choices_sha, flush=True)
    # Evaluation barrier: only NOW call the oracle on held-out and strong target cases.
    strong = discriminant_suite()
    outputs = []
    for target_id, responses, selected, note, order in pending:
        task = candidate_data[target_id]
        outcome = {
            arm: result_for_id(task, selected[arm], reserved, strong)
            for arm in ("control", "memory", "first_weak")
        }
        outputs.append({
            "task": target_id,
            "training_tasks": list(note["lesson_ids"]),
            "training_lesson_sha256": note["lesson_sha256"],
            "same_prompt_character_count": len(note["control"]),
            "variable_context_characters": note["variable_context_characters"],
            "control_context_sha256": sha(note["control"]),
            "memory_context_sha256": sha(note["memory"]),
            "call_order": list(order),
            "shortlist_size": len(task["shortlist"]),
            "raw_model_records": responses,
            "selected": selected,
            "outcomes": outcome,
        })
    positives = outputs[:4]
    summary = {
        arm: {
            "correct_on_four_single_faults": sum(row["outcomes"][arm]["correct"] for row in positives),
            "abstained_on_four_single_faults": sum(row["outcomes"][arm]["status"] == "ABSTENTION" for row in positives),
            "false_repairs_on_two_fault_control": int(outputs[4]["outcomes"][arm]["correct"]),
        }
        for arm in ("control", "memory", "first_weak")
    }
    raw_calls = sum(
        bool(o["raw_model_records"][a].get("called"))
        for o in outputs for a in ("control", "memory")
    )
    report = {
        "experiment": EXPERIMENT,
        "status": "EXPLORATORY_NOT_CERTIFIED",
        "training_bank": lessons,
        "training_oracle_checks": sum(x["oracle_cases_checked"] for x in lessons.values()),
        "rce_source": rce["scientific_source"],
        "rce_common_context_sha256": sha(rce["memory"]),
        "reserve_input_sha256": reserve_sha,
        "reserve_seed_revealed_after_choices": seed,
        "reserved_inputs_revealed_after_choices": reserved,
        "choices_sha256_before_oracle": choices_sha,
        "qwen_context_limit": SELECTOR_CTX,
        "qwen_max_output_tokens": MAX_SELECTOR_TOKENS,
        "model_calls_attempted": raw_calls,
        "evaluations": outputs,
        "summary": summary,
        "comparison": {
            "memory_minus_control_correct": (
                summary["memory"]["correct_on_four_single_faults"]
                - summary["control"]["correct_on_four_single_faults"]
            ),
            "total_budget_parity_confirmed": False,
            "token_count_parity_confirmed": False,
            "same_character_count_and_cli_settings": True,
            "learned_model_weights_changed": False,
            "novel_general_intelligence_demonstrated": False,
        },
        "main_modified": False, "automatic_core_promotion": False,
        "limitations": [
            "The four fault types and source template are synthetic and from the same authors.",
            "In-context examples are selected with a deterministic oracle, not learned model weights.",
            "Strong public tests and one codebase are reused across folds: results are correlated.",
            "Equal characters are not necessarily equal tokenizer tokens.",
            "The shared training oracle work is charged equally but not a second independent run.",
            "No external blinded cohort, independent replication, or statistical power claim.",
            "Qwen returns only an ID from a closed human-written grammar.",
        ],
    }
    report["report_digest_without_self"] = digest(report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--llama-cli", type=Path, required=True)
    p.add_argument("--model-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if not args.llama_cli.is_file() or not args.model_file.is_file():
        p.error("llama-cli/model file missing")
    def chooser(source, shortlist, note, label):
        return qwen_choose(args.llama_cli, args.model_file, source, shortlist, note, label)
    report = experiment(chooser)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "experiment": EXPERIMENT, "status": report["status"],
        "summary": report["summary"],
        "choices_sha256_before_oracle": report["choices_sha256_before_oracle"],
        "model_calls_attempted": report["model_calls_attempted"],
        "not_certified": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
