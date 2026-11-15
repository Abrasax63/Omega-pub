"""One-shot pre-registered transfer evaluation of frozen Qwen3B code.

Usage (host with Docker): python transfer_trial.py --output transfer-result.json
No LLM is invoked. Negative scientific results are valid completed evaluations.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

SEED = "OMEGA-TRANSFER-01-FROZEN-2026-11-15"
CANDIDATE_SHA256 = "121e09058b41984199ac870b6250882ffa4eddb5a4344b1fb1cd0d674296de5a"
FAMILIES = ("cycle", "empty", "complete", "sparse", "dense", "functional", "bipartite", "projection")
SIZES = (12, 28)
HORIZONS = (0, 1, 5, 64, 192)
REPEATS = 7
ARMS = ("qwen3b_frozen", "square-scan", "square-lowbit", "linear-scan")
STRONG = ("square-scan", "square-lowbit")
IMAGE = "python:3.12-slim"


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def fingerprint(value):
    return sha256(encoded(value)).hexdigest()


def make_graph(family, n):
    # Deterministic, fixed, case-family-specific draws; no tuning on results.
    rng = random.Random(int(sha256(f"{SEED}|{family}|{n}".encode()).hexdigest(), 16))
    all_bits = (1 << n) - 1
    extra = None
    if family == "cycle":
        rows = [1 << ((i + 1) % n) for i in range(n)]
    elif family == "empty":
        rows = [0] * n
    elif family == "complete":
        rows = [all_bits] * n
    elif family in ("sparse", "dense"):
        probability = .08 if family == "sparse" else .65
        rows = [sum(1 << j for j in range(n) if rng.random() < probability)
                for _ in range(n)]
    elif family == "functional":
        rows = [1 << rng.randrange(n) for _ in range(n)]
    elif family == "bipartite":
        half = n // 2
        rows = [sum(1 << j for j in range(n) if (i < half) != (j < half)
                    and rng.random() < .38) for i in range(n)]
    elif family == "projection":
        states = 5 * n
        colors = [i % n for i in range(states)]
        rng.shuffle(colors)
        transition = [rng.randrange(states) for _ in range(states)]
        rows = [0] * n
        for state, next_state in enumerate(transition):
            rows[colors[state]] |= 1 << colors[next_state]
        extra = {"transition": transition, "colors": colors, "color_count": n}
    else:
        raise ValueError("unregistered family")
    return rows, extra


def make_cases():
    cases = []
    for family in FAMILIES:
        for n in SIZES:
            rows, extra = make_graph(family, n)
            for h in HORIZONS:
                cases.append({
                    "case_id": f"{family}-{n}-h{h}",
                    "family": family,
                    "group_id": f"{family}-{n}",
                    "n": n, "steps": h, "rows": rows,
                    "timed": h != 0,
                    "projection": extra,
                })
    assert len(cases) == 80
    return cases


def cpu_ns():
    return time.process_time_ns()


def run_inside():
    """This is the fixed read-only harness; candidate functions never score."""
    work = Path("/work")
    source = (work / "frozen_qwen3b_candidate.py").read_bytes()
    if sha256(source).hexdigest() != CANDIDATE_SHA256:
        raise RuntimeError("frozen model-source hash changed")
    programs = {}
    namespace = {}
    exec(compile(source, "/work/frozen_qwen3b_candidate.py", "exec"), namespace)
    programs["qwen3b_frozen"] = namespace["q_power"]
    variant_ns = {}
    exec(compile((work / "variant_factory.py").read_text(), "variant_factory.py", "exec"),
         variant_ns)
    classical = variant_ns["generate"]()
    for name in ARMS[1:]:
        namespace = {}
        exec(compile(classical[name]["source"], name, "exec"), namespace)
        programs[name] = namespace["q_power"]

    cases = json.loads((work / "cases.json").read_text())
    output = {"source_sha256": CANDIDATE_SHA256,
              "input_sha256": fingerprint(cases),
              "source_baselines": {name: classical[name]["sha256"] for name in ARMS[1:]},
              "measurement_kind": "in-container process_time_ns per call",
              "results": []}
    rng = random.Random(SEED + "|order")
    for case in cases:
        rows = case["rows"]
        h = case["steps"]
        samples = {arm: [] for arm in ARMS}
        values = {}
        for arm in ARMS:
            values[arm] = programs[arm](rows[:], h)  # Warm-up outside measurement
        for _ in range(REPEATS):
            order = list(ARMS)
            rng.shuffle(order)
            for arm in order:
                before = cpu_ns()
                got = programs[arm](rows[:], h)
                duration = cpu_ns() - before
                samples[arm].append(max(1, duration))
                values[arm] = got
        output["results"].append({
            "case_id": case["case_id"],
            "values": values,
            "samples_ns": samples,
        })
    print(json.dumps(output, separators=(",", ":"), sort_keys=True))


def validate_and_report(cases, payload, source_sha, image_digest):
    from gate import digest, evaluate
    from reference import walks_exact, actual_h_relation

    required_ids = {case["case_id"] for case in cases}
    if payload.get("source_sha256") != source_sha:
        raise ValueError("candidate source hash mismatch")
    inputs = [{k: v for k, v in row.items() if k != "projection"} for row in cases]
    if payload.get("input_sha256") != fingerprint(inputs):
        raise ValueError("input hash mismatch")
    result_rows = payload.get("results")
    if not isinstance(result_rows, list) or len(result_rows) != len(cases):
        raise ValueError("missing or duplicate case results")
    observed_ids = [row["case_id"] for row in result_rows]
    if set(observed_ids) != required_ids or len(set(observed_ids)) != len(observed_ids):
        raise ValueError("unexpected, duplicate or missing case ID")
    indexed = {row["case_id"]: row for row in result_rows}
    correctness_failures = []
    delta_failures = []
    case_speeds = []
    manifest_rows = []
    arm_rows = {arm: [] for arm in ARMS}
    for case in cases:
        result = indexed[case["case_id"]]
        predicted = result["values"]
        samples = result["samples_ns"]
        if set(predicted) != set(ARMS) or set(samples) != set(ARMS):
            raise ValueError("missing arm or sample set")
        gold = walks_exact(case["rows"], case["steps"])
        for arm in ARMS:
            got = predicted[arm]
            if got != gold:
                correctness_failures.append({"case_id": case["case_id"], "arm": arm,
                                             "expected": gold, "actual": got})
            durations = samples[arm]
            if len(durations) != REPEATS or any(type(v) is not int or v <= 0 for v in durations):
                raise ValueError("unreliable timing sample count or type")
        if case["projection"] is not None:
            p = case["projection"]
            actual = actual_h_relation(p["transition"], p["colors"], p["color_count"], case["steps"])
            expected_delta = [row & ~seen for row, seen in zip(gold, actual)]
            candidate_delta = [row & ~seen for row, seen in zip(predicted["qwen3b_frozen"], actual)]
            if expected_delta != candidate_delta:
                delta_failures.append(case["case_id"])
        if not case["timed"]:
            continue
        med = {arm: statistics.median(samples[arm]) for arm in ARMS}
        strong_best = min(med[name] for name in STRONG)
        speedup = strong_best / med["qwen3b_frozen"]
        case_speeds.append({"case_id": case["case_id"], "family": case["family"],
                            "n": case["n"], "h": case["steps"],
                            "speedup_over_best_classical": round(speedup, 6),
                            "cpu_ns_medians": med})
        manifest_rows.append({"case_id": case["case_id"], "group_id": case["group_id"],
                              "domain": case["family"], "expected": digest(gold)})
        for arm in ARMS:
            arm_rows[arm].append({"case_id": case["case_id"],
                                  "prediction": digest(predicted[arm]),
                                  "cost": max(1, math.ceil(med[arm] / 1000))})

    family_medians = {
        f: statistics.median(row["speedup_over_best_classical"] for row in case_speeds
                             if row["family"] == f)
        for f in FAMILIES
    }
    positive = sum(v > 1 for v in family_medians.values())
    sign_p = sum(math.comb(8, k) for k in range(positive, 9)) / 256
    geo_mean = math.exp(sum(math.log(x["speedup_over_best_classical"]) for x in case_speeds)
                        / len(case_speeds))
    manifest = {
        "experiment_id": "OMEGA-TRANSFER-01",
        "cost_unit": "median_container_cpu_microseconds",
        "cost_policy": "no_increase",
        "max_cost_per_case": 10_000_000,
        "max_total_cost": len(manifest_rows) * 10_000_000,
        "training_case_ids": ["QWEN3B-GENERATION-TRAINING-PR85"],
        "training_group_ids": ["PR85-ORIGINAL-DEVELOPMENT"],
        "previous_holdout_group_ids": ["PR85-ORIGINAL-RESERVED"],
        "required_domains": list(FAMILIES),
        "holdout": manifest_rows,
    }
    baseline_gate = {}
    for arm in STRONG:
        arms = {
            "baseline": {"source_commit": payload["source_baselines"][arm],
                         "run_url": "UNATTESTED-CI-CPU", "results": arm_rows[arm]},
            "candidate": {"source_commit": source_sha,
                          "run_url": "UNATTESTED-CI-CPU",
                          "results": arm_rows["qwen3b_frozen"]},
        }
        baseline_gate[arm] = evaluate(manifest, {"experiment_id": "OMEGA-TRANSFER-01",
                                                "arms": arms}, digest(manifest))
    exact = len(correctness_failures) == 0 and len(delta_failures) == 0
    prereg_success = (exact and geo_mean >= 1.10
                      and all(v >= 1.05 for v in family_medians.values())
                      and positive >= 7 and sign_p <= .05
                      and all(g["candidate_for_independent_review"]
                              for g in baseline_gate.values()))
    return {
        "experiment_id": "OMEGA-TRANSFER-01",
        "scientific_verdict": "REVIEW_REQUIRED" if prereg_success else "NO_DEMONSTRATED_ADVANTAGE",
        "candidate_source_sha256": source_sha,
        "origin_run": "https://github.com/Abrasax63/Omega-pub/actions/runs/43693684837",
        "frozen_protocol": "TRANSFER_PREREG.md",
        "evaluator_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "image_digest": image_digest,
        "input_sha256": payload["input_sha256"],
        "manifest_sha256": digest(manifest),
        "n_cases_total": len(cases),
        "n_timed_cases": len(case_speeds),
        "repetitions_per_arm_per_case": REPEATS,
        "correctness_failures": correctness_failures,
        "delta_failures": delta_failures,
        "family_median_speedup": family_medians,
        "geometric_mean_speedup": geo_mean,
        "positive_family_count": positive,
        "one_sided_family_sign_test_p": sign_p,
        "strong_classical_gates": baseline_gate,
        "cases": case_speeds,
        "limitations": [
            "Public synthetic case families, not an independently held external corpus.",
            "CPU metrics inside Docker are noisy; one run cannot certify speed.",
            "A successful workflow does not demonstrate a novel algorithm or general intelligence.",
            "Original frozen Qwen3B code cannot be adapted during this experiment.",
        ],
    }


def run_host(outfile):
    root = Path(__file__).resolve().parent
    source = (root / "frozen_qwen3b_candidate.py").read_bytes()
    if sha256(source).hexdigest() != CANDIDATE_SHA256:
        raise ValueError("frozen source changed")
    cases = make_cases()
    inputs = [{k: v for k, v in row.items() if k != "projection"} for row in cases]
    check = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
    if check.returncode:
        raise RuntimeError("Docker is required: fail closed")
    inspect = subprocess.run(["docker", "image", "inspect", IMAGE, "--format",
                              "{{index .RepoDigests 0}}"], capture_output=True, text=True, timeout=10)
    image_digest = inspect.stdout.strip() if inspect.returncode == 0 else "UNVERIFIED_IMAGE"
    with tempfile.TemporaryDirectory(prefix="omega-transfer-") as dirname:
        stage = Path(dirname)
        os.chmod(stage, 0o755)
        for name in ("transfer_trial.py", "variant_factory.py", "frozen_qwen3b_candidate.py"):
            shutil.copyfile(root / name, stage / name)
            os.chmod(stage / name, 0o644)
        (stage / "cases.json").write_text(json.dumps(inputs), encoding="utf-8")
        os.chmod(stage / "cases.json", 0o644)
        command = [
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--user", "65534:65534", "--cap-drop", "ALL", "--security-opt",
            "no-new-privileges", "--pids-limit", "32", "--memory", "512m",
            "--memory-swap", "512m", "--cpus", "1",
            "--mount", f"type=bind,src={stage},dst=/work,readonly",
            IMAGE, "python", "-I", "-B", "/work/transfer_trial.py", "--inside",
        ]
        process = subprocess.run(command, text=True, capture_output=True, timeout=180)
        if process.returncode:
            raise RuntimeError("bounded evaluation failed: " + process.stderr[-1000:])
        if len(process.stdout) > 2_000_000:
            raise ValueError("oversized measured output")
        payload = json.loads(process.stdout)
    report = validate_and_report(cases, payload, CANDIDATE_SHA256, image_digest)
    outfile.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                       encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("cases", "strong_classical_gates")},
                     ensure_ascii=False, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inside", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("transfer-result.json"))
    args = parser.parse_args()
    if args.inside:
        run_inside()
    else:
        run_host(args.output)


if __name__ == "__main__":
    main()
