"""End-to-end open-weight model code proposal and independently scored Docker replay.

No paid LLM service; no secret is given to model or candidate. The limited,
ephemeral test is NOT a blind external benchmark or an intelligence claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import sys

from gate import digest, evaluate
from model_proposal import generate_with_llama
from reference import observed_relation, walks_exact, actual_h_relation
from runner import graph_case
from sandbox_runner import IMAGE, docker_available, execute
from variant_factory import generate

TRAIN_SEEDS = (1101, 1102, 1103)
BASELINE_STRONG = "square-scan"
BASELINE_STRONG_ALTERNATE = "square-lowbit"
BASELINE_WEAK = "linear-scan"
MAX_COST_PER_CASE_US = 15_000_000


def score(source, cases):
    scores = []
    for case in cases:
        q = observed_relation(case["transition"], case["colors"], case["color_count"])
        expected = walks_exact(q, case["steps"])
        actual = actual_h_relation(case["transition"], case["colors"], case["color_count"], case["steps"])
        got, cost = execute(source, q, case["steps"])
        correct = got == expected
        scores.append({
            "case_id": str(case["seed"]),
            "group_id": case["group_id"],
            "expected": digest(expected),
            "prediction": digest(got),
            "correct": correct,
            "counterexample": {"rows": q, "steps": case["steps"],
                               "expected": expected, "actual": got} if not correct else None,
            "delta_correct": [a & ~b for a, b in zip(expected, actual)] ==
                             [a & ~b for a, b in zip(got, actual)],
            "cost": cost,
        })
    return scores


def arm(rows, name, program_sha, run_url="UNATTESTED-GITHUB-ACTIONS-RUN"):
    return {
        "source_commit": name + ":" + program_sha,
        "run_url": run_url,
        "results": [{"case_id": x["case_id"], "prediction": x["prediction"],
                     "cost": x["cost"]} for x in rows],
    }


def make_manifest(cases):
    return {
        "experiment_id": "OMEGA-OPEN-MODEL-01",
        "cost_unit": "host_monotonic_docker_wall_microseconds",
        "cost_policy": "no_increase",
        "max_cost_per_case": MAX_COST_PER_CASE_US,
        "max_total_cost": MAX_COST_PER_CASE_US * len(cases),
        "training_case_ids": [str(x) for x in TRAIN_SEEDS],
        "training_group_ids": ["source-seed-" + str(x) for x in TRAIN_SEEDS],
        "previous_holdout_group_ids": [],
        "required_domains": ["finite-observability"],
        "holdout": [],
    }


def evaluate_against(baseline_name, baseline_rows, winner_rows, manifest, candidate_sha, baseline_sha):
    observations = {
        "experiment_id": manifest["experiment_id"],
        "arms": {
            "baseline": arm(baseline_rows, baseline_name, baseline_sha),
            "candidate": arm(winner_rows, "open-model", candidate_sha),
        },
    }
    return evaluate(manifest, observations, digest(manifest))


def run(llama_cli, model_file, model_label):
    if not docker_available():
        raise RuntimeError("Docker is required; no unisolated fallback")
    candidates = generate()
    train = [graph_case(x) for x in TRAIN_SEEDS]

    # Frozen *before* model inference, and not passed to the model or candidate.
    private_seeds = [secrets.randbits(48) for _ in range(3)]
    reserved = [graph_case(x) for x in private_seeds]
    manifest = make_manifest(reserved)
    manifest["holdout"] = [
        {"case_id": str(x["seed"]), "group_id": x["group_id"],
         "domain": "finite-observability",
         "expected": digest(walks_exact(
             observed_relation(x["transition"], x["colors"], x["color_count"]),
             x["steps"]))}
        for x in reserved
    ]
    initial_commitment = digest(manifest)
    print("FROZEN_BEFORE_MODEL_INFERENCE_SHA256=" + initial_commitment, flush=True)
    print("MODEL_HAS_NO_ACCESS_TO_RESERVED_CASES", flush=True)

    attempts = []
    valid = []
    seen_semantic = {}
    training_feedback = None
    for variant in (0, 1):
        source, meta = generate_with_llama(llama_cli, model_file, variant,
                                           feedback=training_feedback)
        if source is None:
            meta["status"] = "MODEL_PROPOSAL_REJECTED_AT_PARSE"
            training_feedback = ("Your previous answer did not contain an allowed complete "
                                 "Python function. Include only def q_power(rows, steps). "
                                 "Use exact Boolean matrix multiplication, not shifts/XOR.")
            attempts.append(meta)
            continue
        sem = meta["semantic_sha256"]
        if sem in seen_semantic:
            meta["status"] = "DUPLICATE_SOURCE_NOT_REEXECUTED"
            meta["duplicate_of_variant"] = seen_semantic[sem]
            attempts.append(meta)
            continue
        seen_semantic[sem] = variant
        try:
            train_results = score(source, train)
            meta["training_correct"] = all(r["correct"] and r["delta_correct"] for r in train_results)
            meta["training_wall_us"] = sum(r["cost"] for r in train_results)
            meta["status"] = "TRAINING_CORRECT" if meta["training_correct"] else "TRAINING_INCORRECT"
            if meta["training_correct"]:
                valid.append(meta)
                training_feedback = None
            else:
                failing = next((r["counterexample"] for r in train_results
                                if not r["correct"]), None)
                training_feedback = ("Your previous code failed a PUBLIC training example. "
                                     "Replace its logic, do not just rename variables. "
                                     + json.dumps(failing, separators=(",", ":"))
                                     + " Previous code: " + source)
        except (RuntimeError, ValueError, TimeoutError) as exc:
            meta["status"] = "TRAINING_EXECUTION_REJECTED"
            meta["failure"] = str(exc)[:300]
            training_feedback = ("Your previous code crashed on PUBLIC training data: "
                                 + str(exc)[:250] + ". Previous code: " + source
                                 + ". Use Boolean OR for path composition, not XOR.")
        attempts.append(meta)

    # The model is invoked for real even if it produces no valid programs. Fail
    # closed: do not substitute a hand-coded algorithm and label it model-created.
    result = {
        "status": "NO_VALID_MODEL_CANDIDATE",
        "model": model_label,
        "model_file_sha256": hashlib.sha256(Path(model_file).read_bytes()).hexdigest(),
        "sandbox_image": IMAGE,
        "manifest_sha256": initial_commitment,
        "model_invocations": len(attempts),
        "attempts": attempts,
        "distinct_programs": len(seen_semantic),
        "holdout_opened": False,
        "limits": [
            "Public task and model prompts; private holdout is generated within this run, not sealed by an external custodian",
            "Docker reduces risk but shares the host kernel",
            "Only two candidate prompts; sample too small for statistical claims",
            "Measured Docker wall time includes startup noise; not proof of computational superiority",
            "A valid generated program is not proof of Omega-specific intelligence",
        ],
    }
    if not valid:
        return result

    # Selected strictly by correct training outcomes + training-only speed.
    champion = min(valid, key=lambda x: (x["training_wall_us"], x["source_sha256"]))
    winner = champion["source"]
    winner_rows = score(winner, reserved)
    if not all(x["delta_correct"] for x in winner_rows):
        raise RuntimeError("independent Δ_h comparison failed")
    comparisons = {}
    for label in (BASELINE_WEAK, BASELINE_STRONG, BASELINE_STRONG_ALTERNATE):
        baseline_source = candidates[label]["source"]
        baseline_rows = score(baseline_source, reserved)
        comparisons[label] = evaluate_against(
            label, baseline_rows, winner_rows, manifest,
            champion["source_sha256"], candidates[label]["sha256"])
    result.update({
        "status": "MODEL_CANDIDATE_EVALUATED",
        "holdout_opened": True,
        "winner_variant": champion["variant"],
        "winner_sha256": champion["source_sha256"],
        "holdout_cases": len(reserved),
        "correct_on_holdout": sum(x["correct"] for x in winner_rows),
        "delta_exact_matches": sum(x["delta_correct"] for x in winner_rows),
        "baselines": comparisons,
        "strong_baseline_passed": (
            comparisons[BASELINE_STRONG]["candidate_for_independent_review"]
            and comparisons[BASELINE_STRONG_ALTERNATE]["candidate_for_independent_review"]
            and champion["source_sha256"] not in (
                candidates[BASELINE_STRONG]["sha256"],
                candidates[BASELINE_STRONG_ALTERNATE]["sha256"],
            )
        ),
        "candidate_equals_classical_source": champion["source_sha256"] in (
            candidates[BASELINE_STRONG]["sha256"],
            candidates[BASELINE_STRONG_ALTERNATE]["sha256"],
        ),
        "scientific_status": "INDETERMINATE_NOT_INDEPENDENTLY_CERTIFIED",
        "withheld_manifest_after_evaluation": manifest,
    })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--model-file", required=True)
    parser.add_argument("--output", type=Path, default=Path("model-result.json"))
    parser.add_argument("--model-label", required=True)
    args = parser.parse_args()
    report = run(args.llama_cli, args.model_file, args.model_label)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("attempts", "withheld_manifest_after_evaluation")},
                     indent=2, ensure_ascii=False, sort_keys=True))
    if not any(a["model_call_returncode"] == 0 for a in report["attempts"]):
        sys.exit("INFRA_MODEL_INFERENCE_FAILED: no successful llama-cli call")


if __name__ == "__main__":
    main()
