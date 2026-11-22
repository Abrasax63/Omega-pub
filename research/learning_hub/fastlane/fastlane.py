"""Omega accelerated curriculum: reuse verified SFT01 *training* families.

Generate fresh *semantic-error* repair exercises cheaply, validate every
candidate in the existing bounded Python sandbox, and export an inspectable
train-only queue. NO old holdout or model score is read; NO model call and NO
automatic training or weights modification.

This is supervised synthetic data engineering, not autonomous learning.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SFT = ROOT.parent / "sft01"
LAB = ROOT.parent.parent / "learning_lab"
sys.path.insert(0, str(SFT))
sys.path.insert(0, str(LAB))
from data_guard import load_train
import prog_reconstruction_pilot as sandbox

SCHEMA = "OMEGA_FASTLANE_CURRICULUM_01"
MAX_PER_FAMILY = 4
MAX_EXAMPLES = 90
MIN_FAMILIES = 12
MIN_EXAMPLES = 24

# These family names denote *consumed* earlier model evaluations. Do not
# feed them to this generator or grade against them.
CONSUMED_HOLDOUTS = (
    "A", "B", "C", "D", "E", "F",
    "unique_digits", "split_colon", "third_index",
    "ord_each", "vowels_up", "reverse_upper_lower",
    "double_vowels", "even_distinct_lower", "pipe_alpha_upper",
    "reverse_nonzero_digits", "overlap_bigrams", "indexed_upper_alpha",
)

def ordered_mutations(gold):
    """Fixed generic fault grammar, never optimized using hidden results."""
    options = []
    seen = {gold}
    def add(label, val):
        if val != gold and val not in seen:
            seen.add(val)
            options.append((label, val))
    replacements = [
        (".lower()", ".upper()", "case_upper"),
        (".upper()", ".lower()", "case_lower"),
        (".isdigit()", ".isalpha()", "digit_vs_letter"),
        (".isalpha()", ".isdigit()", "letter_vs_digit"),
        (".isupper()", ".islower()", "upper_vs_lower"),
        (".islower()", ".isupper()", "lower_vs_upper"),
        ("i % 2 == 0", "i % 2 == 1", "parity_odd"),
        ("i % 2 == 1", "i % 2 == 0", "parity_even"),
        ("for c in s:", "for c in reversed(s):", "reverse_iteration"),
        ("for c in reversed(s):", "for c in s:", "forward_iteration"),
        ("enumerate(s)", "enumerate(reversed(s))", "reverse_enumerate"),
        ("c.lower() == 'a'", "c.lower() == 'b'", "wrong_literal"),
        ("c != '|'", "c == '|'", "wrong_pipe_comparison"),
        ("c != ' '", "c == ' '", "wrong_space_comparison"),
        ("'X' + c", "'Y' + c", "wrong_prefix"),
        ("c + '!'", "c + '?'", "wrong_suffix"),
        ("c in '!?'", "c not in '!?'", "inverted_punctuation"),
        ("c not in out", "c in out", "inverted_membership"),
        ("c.lower() not in out", "c.lower() in out", "inverted_lower_membership"),
        ("out.append(c)", "out.append(c.upper())", "append_upper_instead"),
        ("out.append(c)", "out.append(c.lower())", "append_lower_instead"),
        ("out.append(c)", "out.append(c + '!')", "append_suffix_instead"),
        ("out.append(c.lower())", "out.append(c)", "forget_normalize"),
        ("out.append(c.upper())", "out.append(c)", "forget_upper"),
    ]
    for old, new, label in replacements:
        if old in gold:
            add(label, gold.replace(old, new, 1))

    # A generic semantic mistake: reverse the output insertion order.
    for i, line in enumerate(gold.splitlines()):
        m = re.fullmatch(r"(\s*)out\.append\((.*)\)", line)
        if m:
            changed = gold.splitlines()
            changed[i] = m.group(1) + "out.insert(0, " + m.group(2) + ")"
            add("output_order", "\n".join(changed) + "\n")

    lines = gold.splitlines()
    for i, line in enumerate(lines):
        m = re.fullmatch(r"(\s*)if (.+):", line)
        if m:
            amended = lines[:]
            amended[i] = m.group(1) + "if not (" + m.group(2) + "):"
            add("invert_condition", "\n".join(amended) + "\n")

    for i in range(len(lines)-1):
        if lines[i] == lines[i+1] and "out.append(" in lines[i]:
            add("forget_duplicate_append", "\n".join(lines[:i+1] + lines[i+2:]) + "\n")
    return options


def public_from_prompt(prompt):
    mark = "Observed examples: "
    tail = "\nReturn ONLY"
    if mark not in prompt:
        raise ValueError("NO_PUBLIC_EXAMPLES_IN_ORIGINAL_TRAINING_PROMPT")
    return json.loads(prompt.split(mark, 1)[1].split(tail, 1)[0])


def run_cases(code, samples):
    return sandbox.execute_student(code, [x["input"] for x in samples])


def verified(code, samples):
    got = run_cases(code, samples)
    return len(got) == len(samples) and all(
        g.get("value") == x["expected"] for g,x in zip(got, samples))


def produce():
    source = load_train()  # from SFT01 TRAIN_FROZEN only, not any holdout.
    groups = {}
    for item in source:
        if item["provenance"] != "CURATED_SYNTHETIC_GOLD_NOT_MODEL_DISCOVERED":
            continue
        groups.setdefault(item["family"], item)
    if len(groups) != 20:
        raise ValueError("SOURCE_TRAINING_FAMILY_COUNT_UNEXPECTED")
    if any(k in CONSUMED_HOLDOUTS for k in groups):
        raise ValueError("SFT01_TRAINING_SOURCE_CROSSES_CONSUMED_HOLDOUT")
    selected = []
    rejected = Counter()
    family_counts = Counter()
    original_fingerprints = set()

    for family, row in sorted(groups.items()):
        gold = row["target"]
        sandbox.validate_program(gold)
        public = public_from_prompt(row["prompt"])
        checks = row["verification_cases"]
        if not verified(gold, public) or not verified(gold, checks):
            raise ValueError("PREVIOUS_TRAIN_REFERENCE_NO_LONGER_REPRODUCIBLE_"+family)
        gold_hash = sha256(gold.encode()).hexdigest()
        original_fingerprints.add(gold_hash)
        for defect, bad in ordered_mutations(gold):
            if family_counts[family] >= MAX_PER_FAMILY:
                break
            if len(selected) >= MAX_EXAMPLES:
                break
            try:
                sandbox.validate_program(bad)
            except ValueError:
                rejected["INVALID_AST_OR_SYNTAX"] += 1
                continue
            if not verified(bad, public):
                # Ensure the exercise is discriminating using visible
                # examples, not merely an error on old hidden inputs.
                bad_output = run_cases(bad, public)
                if len(bad_output) != len(public) or not all(
                        isinstance(x.get("value"), list) for x in bad_output):
                    rejected["BAD_MUTANT_OUTPUT"] += 1
                    continue
            else:
                rejected["NO_VISIBLE_SEMANTIC_DIFFERENCE"] += 1
                continue
            # Fresh verification checks are PREVIOUS TRAINING QA cases,
            # not a novel/independent holdout. Distinguish explicitly.
            if verified(bad, checks):
                rejected["NO_ADDITIONAL_FAILURE"] += 1
                continue
            prompt = (
                "TASK=PYTHON_REPAIR\n"
                "Repair this Python function. It already compiles but its "
                "logic is wrong. Preserve its observable input/output behavior. "
                "Return ONLY complete Python def transform(s), no Markdown.\n"
                "BROKEN SOURCE:\n" + bad +
                "\nVISIBLE OBSERVATIONS:\n" +
                json.dumps(public, ensure_ascii=False) + "\n"
            )
            training_record = {
                "id": "FAST01-"+family+"-"+defect,
                "family": family, "fault": defect,
                "source_kind": "SYNTHETIC_SEMANTIC_MUTATION_OF_PREVIOUS_SFT_TRAIN",
                "teacher_code_provenance": "CURATED_REFERENCE_NOT_MODEL_PROPOSAL",
                "prompt": prompt, "target": gold,
                "previous_train_public_examples": public,
                "previous_train_qa_checks_used_for_admission": len(checks),
                "target_sha256": gold_hash,
                "broken_sha256": sha256(bad.encode()).hexdigest(),
                "all_previous_holdouts_consumed": True,
                "new_generalization_demonstrated": False,
            }
            selected.append(training_record)
            family_counts[family] += 1
    if not selected:
        raise ValueError("NO_VALIDATED_SEMANTIC_MUTATIONS")
    if len(set(x["id"] for x in selected)) != len(selected):
        raise ValueError("DUPLICATE_SYNTHETIC_SKILL")
    dataset = {
        "schema": SCHEMA,
        "status": "TRAINING_CANDIDATES_ONLY",
        "prior_source": "OMEGA-PY-SFT-01 TRAIN_FROZEN",
        "families": len(family_counts),
        "examples": len(selected),
        "max_per_family": MAX_PER_FAMILY,
        "families_banned_as_previously_evaluated": list(CONSUMED_HOLDOUTS),
        "train_only_no_independent_holdout": True,
        "old_training_examples_recombined": True,
        "different_program_families_not_demonstrated": True,
        "model_generated_new_targets": 0,
        "inference_calls": 0,
        "training_updates": 0,
        "requires_fresh_preregistered_evaluation": True,
        "rejections": dict(sorted(rejected.items())),
        "training_samples": selected,
    }
    dataset["dataset_sha256"] = sha256(json.dumps(selected, sort_keys=True,
                      ensure_ascii=False).encode()).hexdigest()
    return dataset


def promotion_gate(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("WRONG_SCHEMA")
    reasons = []
    if data["families"] < MIN_FAMILIES:
        reasons.append("TOO_FEW_FAMILIES")
    if data["examples"] < MIN_EXAMPLES:
        reasons.append("TOO_FEW_EXAMPLES")
    reasons.extend(["NO_FRESH_INDEPENDENT_HOLDOUT",
                    "NO_SEMANTIC04_RESULT_REVIEW",
                    "NO_AUTO_TRAINING_PERMISSION"])
    return {
        "status": "DATA_READY_FOR_HUMAN_REVIEW_NOT_FOR_AUTO_TRAINING",
        "families": data["families"], "examples": data["examples"],
        "blocked": True, "block_reasons": reasons,
        "recommended_next_action": "FREEZE_NEW_EVALUATION_THEN_REUSE_SFT01_TRAINER",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = produce()
    data["gate"] = promotion_gate(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps({"status": data["status"], "verified": data["examples"],
        "families": data["families"], "rejections": data["rejections"],
        "training_started": False, "gate": data["gate"]["status"]}))


if __name__ == "__main__":
    main()
