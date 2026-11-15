"""Bounded Qwen 3B code optimization from a strong Boolean-power baseline.

This stage uses only synthetic DEVELOPMENT cases. An independent later CI job
builds the held-out NetworkX graphs; this program neither imports them nor
reads the external evaluator. No LLM execution is relabelled as discovery.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import tempfile
import os

from model_proposal import extract_candidate, semantic_fingerprint
from reference import walks_exact

CALLS = 3
TOKENS_PER_CALL = 800
MODEL_HASH = "724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
TRAINING_SEEDS = (207, 401, 607, 809, 1009, 1229)
TRAINING_WIDTHS = (16, 22, 31, 47, 59, 64)
TRAINING_HORIZONS = (0, 1, 31, 127, 511)
BASELINE_EXAMPLE = """def classical_reference(rows, steps):
    n = len(rows)
    result = [1 << i for i in range(n)]
    base = rows[:]
    while steps:
        if steps & 1:
            new = []
            for mask in result:
                out = 0
                while mask:
                    bit = mask & -mask
                    out |= base[bit.bit_length() - 1]
                    mask -= bit
                new.append(out)
            result = new
        steps >>= 1
        if steps:
            new = []
            for mask in base:
                out = 0
                while mask:
                    bit = mask & -mask
                    out |= base[bit.bit_length() - 1]
                    mask -= bit
                new.append(out)
            base = new
    return result
"""
HARNESS = r"""
import json
import time
from pathlib import Path

scope = {}
exec(compile(Path('/work/candidate.py').read_text(), '/work/candidate.py', 'exec'), scope)
fn = scope['q_power']
cases = json.loads(Path('/work/cases.json').read_text())
outputs = []
for case in cases:
    rows, h = case['rows'], case['h']
    times = []
    got = fn(rows[:], h)
    for _ in range(5):
        start = time.process_time_ns()
        for unused in range(6):
            got = fn(rows[:], h)
        times.append(max(1, time.process_time_ns() - start))
    times.sort()
    outputs.append({'id':case['id'], 'answer':got, 'median_ns_6calls':times[2]})
print(json.dumps(outputs, separators=(',', ':')))
"""


def make_training():
    out = []
    for seed, width in zip(TRAINING_SEEDS, TRAINING_WIDTHS):
        rng = random.Random(seed)
        # Random mixed sparsity; not any of the NetworkX graph files.
        p = .035 + .11 * (seed % 5)
        rows = [sum(1 << j for j in range(width) if rng.random() < p)
                for _ in range(width)]
        for h in TRAINING_HORIZONS:
            out.append({'id': f'dev-{seed}-h{h}', 'rows': rows, 'h': h})
    return out


def prompt_for(attempt, feedback):
    objectives = (
        "Improve bit iteration and reduce allocations.",
        "Try an alternative composition that is faster on sparse and dense graphs.",
        "Optimize both repeated squaring and multiplication without changing meaning.",
    )
    prompt = ("<|im_start|>system\nYou are a Python optimization engineer. "
              "Return a single complete Python function, no imports, no markdown, "
              "no other text. Never use external APIs or file access.\n<|im_end|>\n"
              "<|im_start|>user\nImprove this already strong classic logarithmic-time "
              "Boolean adjacency matrix exponentiation. "
              "You MUST maintain exact-length walks, steps=0 identity, arbitrary graph width, "
              "and exponentiation by squaring (do not loop once per step). "
              "Write only def q_power(rows, steps): as a single function. "
              "You may use while, for, lists, bit operations, bit_length(), append(), "
              "range, len, enumerate. No imports, globals, helpers, classes or recursion. "
              "Here is the correct strong baseline named classical_reference:\n"
              + BASELINE_EXAMPLE
              + "\nOptimization focus: " + objectives[attempt] + "\n")
    if feedback:
        prompt += ("Public DEVELOPMENT-only feedback from the previous attempt; "
                   "the final evaluation corpus has not been examined:\n"
                   + feedback[:1500] + "\n")
    return prompt + "<|im_end|>\n<|im_start|>assistant\n"


def model_call(cli, weights, attempt, feedback):
    command = [str(cli), "-m", str(weights), "-p", prompt_for(attempt, feedback),
               "-n", str(TOKENS_PER_CALL), "-c", "4096", "-t", "4", "--temp", "0.20",
               "--seed", str(302 + attempt)]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=270)
    meta = {"attempt": attempt, "model_exit": proc.returncode,
            "stdout_sha256": sha256(proc.stdout.encode()).hexdigest(),
            "stdout_size": len(proc.stdout), "stderr_tail": proc.stderr[-200:] if proc.returncode else ""}
    if proc.returncode:
        meta["status"] = "MODEL_CALL_ERROR"
        return None, meta
    try:
        source = extract_candidate(proc.stdout)
        meta["source_sha256"] = sha256(source.encode()).hexdigest()
        meta["semantic_sha256"] = semantic_fingerprint(source)
        meta["source"] = source
        return source, meta
    except (ValueError, SyntaxError) as exc:
        meta["status"] = "INVALID_GENERATED_SOURCE"
        meta["failure"] = str(exc)
        return None, meta


def training_run(source, cases):
    with tempfile.TemporaryDirectory(prefix="omega-opt02-dev-") as td:
        folder = Path(td)
        # TemporaryDirectory defaults to 0700. The non-root Docker process
        # cannot traverse it even when the mounted files are mode 0644.
        os.chmod(folder, 0o755)
        (folder / "candidate.py").write_text(source)
        (folder / "cases.json").write_text(json.dumps(cases))
        (folder / "harness.py").write_text(HARNESS)
        for path in folder.iterdir():
            os.chmod(path, 0o644)
        proc = subprocess.run([
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--pids-limit", "32", "--memory", "256m", "--cpus", "1",
            "--user", "65534:65534", "--mount", f"type=bind,src={folder},dst=/work,readonly",
            "python:3.12-slim", "python", "-I", "-B", "/work/harness.py",
        ], text=True, capture_output=True, timeout=110)
        if proc.returncode:
            raise RuntimeError("candidate development crash: " + proc.stderr[-350:])
        if len(proc.stdout) > 180000:
            raise ValueError("oversized training result")
        output = json.loads(proc.stdout)
    if not isinstance(output, list) or len(output) != len(cases):
        raise ValueError("missing training results")
    score = 0
    errors = []
    for source_case, reply in zip(cases, output):
        if reply.get("id") != source_case["id"]:
            raise ValueError("training order or case mismatch")
        expected = walks_exact(source_case["rows"], source_case["h"])
        if reply.get("answer") != expected:
            errors.append({"id": source_case["id"], "expected": expected,
                           "actual": reply.get("answer")})
        elapsed = reply.get("median_ns_6calls")
        if type(elapsed) is not int or elapsed < 1:
            raise ValueError("invalid training CPU metric")
        score += elapsed
    return {"n_training": len(cases), "errors": len(errors),
            "first_counterexample": errors[0] if errors else None,
            "median_cpu_ns_total": score}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--model-file", required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("opt02-produced"))
    args = parser.parse_args()
    if sha256(Path(args.model_file).read_bytes()).hexdigest() != MODEL_HASH:
        raise ValueError("model weights differ from frozen SHA-256")
    import subprocess as sp
    if sp.run(["docker", "info"], capture_output=True, timeout=10).returncode:
        raise RuntimeError("Docker required, no unsafe fallback")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    dev = make_training()
    results = []
    qualified = []
    seen = {}
    feedback = None
    for attempt in range(CALLS):
        source, meta = model_call(args.llama_cli, args.model_file, attempt, feedback)
        if source is None:
            feedback = "Your prior output did not provide a complete allowed q_power function."
            results.append(meta)
            continue
        code_hash = meta["semantic_sha256"]
        if code_hash in seen:
            meta.update(status="DUPLICATE_NOT_RETESTED", duplicate_of=seen[code_hash])
            results.append(meta)
            continue
        seen[code_hash] = attempt
        try:
            measurements = training_run(source, dev)
            meta["training"] = measurements
            if measurements["errors"]:
                meta["status"] = "INCORRECT_DEVELOPMENT"
                feedback = "Counterexample: " + json.dumps(
                    measurements["first_counterexample"], separators=(",", ":"))[:1200]
            else:
                meta["status"] = "QUALIFIED_DEVELOPMENT"
                qualified.append(meta)
                feedback = None
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            meta["status"] = "CRASHED_OR_INVALID_DEVELOPMENT"
            meta["failure"] = str(exc)[:450]
            feedback = meta["failure"]
        results.append(meta)
    winner = min(qualified, key=lambda x: (
        x["training"]["median_cpu_ns_total"], x["semantic_sha256"])) if qualified else None
    if winner:
        (args.output_dir / "champion.py").write_text(winner["source"], encoding="utf-8")
    report = {
        "status": "CHAMPION_READY_FOR_SEPARATE_EVALUATOR" if winner else "NO_VALID_CANDIDATE",
        "model": "Qwen2.5-Coder-3B-Instruct-GGUF Q4_K_M",
        "model_weight_sha256": MODEL_HASH,
        "model_attempts": len(results),
        "distinct_ast_programs": len(seen),
        "training_case_count": len(dev),
        "input_development_sha256": sha256(json.dumps(dev, sort_keys=True).encode()).hexdigest(),
        "attempts": results,
        "winner_source_sha256": winner["source_sha256"] if winner else None,
        "winner_semantic_sha256": winner["semantic_sha256"] if winner else None,
        "external_corpus_opened": False,
        "description": "CPU selection on public synthetic development only; no external evaluation seen",
    }
    (args.output_dir / "generation.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="attempts"}, indent=2))
    if not any(row["model_exit"] == 0 for row in results):
        raise RuntimeError("zero successful model inference calls")


if __name__ == "__main__":
    main()
