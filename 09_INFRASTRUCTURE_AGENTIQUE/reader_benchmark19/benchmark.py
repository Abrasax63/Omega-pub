#!/usr/bin/env python3
"""BENCH19 -- 20 frozen synthetic finite-math truth classification cases.

A model may select source IDs; it cannot create facts, citations, certifications,
or Horn rules. Ground truth is exhaustive finite computation, NOT an external
human annotation and NOT an assessment of real mathematical documents.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import time
import traceback
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from selector import parse_selection, proposal_from_lines
from read import safe_read, packetize, verify_packets, blob
from gate import gate

SPEC = HERE / "CASE_SPEC.json"
FROZEN = HERE / "FROZEN_BENCHMARK.json"
PROMPT = HERE / "PROMPT.txt"
URL = "http://127.0.0.1:8091/v1/chat/completions"
SHA_0P5B = "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"
SHA_3B = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"
LLAMA_SHA = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
KEYS = {"INJ", "FIX", "EVAL2", "EVAL1", "INV"}
MAX_CHOICE = 3
MAX_TOKENS = 64


def render(case: dict) -> bytes:
    kind = case["kind"]
    n, a, b = case["modulus"], case["a"], case["b"]
    if kind not in ("affine", "quadratic"):
        raise ValueError("UNSUPPORTED_FINITE_FAMILY")
    formula = f"({a}*x + {b}) mod {n}" if kind == "affine" else f"({a}*x^2 + {b}) mod {n}"
    texts = {
        "INJ": "Proposition : f est injective.",
        "FIX": "Proposition : f possède au moins un point fixe.",
        "EVAL2": f"Proposition : f(f(0)) = {case['c']}.",
        "EVAL1": f"Proposition : f(1) = {case['d']}.",
        "INV": "Proposition : pour tout x, f(f(x)) = x.",
    }
    if len(case["order"]) != 5 or set(case["order"]) != KEYS:
        raise ValueError("DUPLICATE_OR_MISSING_STATEMENT_KEY")
    source = (
        f"# Fiche {case['id']}\n\n## Données\n\n"
        f"On travaille dans Z/{n}Z. On définit f(x) = {formula}.\n\n"
        f"## Énoncé\n\n"
        + "\n".join(texts[key] for key in case["order"]) + "\n"
    )
    return source.encode("utf-8")


def exhaustive_oracle(case: dict) -> dict:
    n, a, b = case["modulus"], case["a"], case["b"]
    if (any(type(i) is not int for i in (n, a, b, case["c"], case["d"]))
        or not (5 <= n <= 16) or a < 0 or b < 0
        or not (0 <= case["c"] < n and 0 <= case["d"] < n)):
        raise ValueError("INVALID_FINITE_PARAMS")
    def f(x: int) -> int:
        return (a * (x if case["kind"] == "affine" else x*x) + b) % n
    values = [f(x) for x in range(n)]
    truths = {
        "INJ": len(set(values)) == n,
        "FIX": any(v == i for i, v in enumerate(values)),
        "EVAL2": f(f(0)) == case["c"],
        "EVAL1": f(1) == case["d"],
        "INV": all(f(f(i)) == i for i in range(n)),
    }
    return truths


def prepare() -> list[dict]:
    frozen = json.loads(FROZEN.read_text(encoding="utf8"))
    spec = json.loads(SPEC.read_text(encoding="utf8"))
    if frozen["status"] != "FROZEN_BEFORE_MODEL_INFERENCE":
        raise ValueError("MANIFEST_NOT_FROZEN")
    cases = spec["cases"]
    docs = frozen["docs"]
    if len(cases) != 20 or len(docs) != 20:
        raise ValueError("BENCHMARK_CARDINALITY_DRIFT")
    by_id = {case["id"]: case for case in cases}
    if len(by_id) != 20 or len(set(d["id"] for d in docs)) != 20:
        raise ValueError("DUPLICATE_BENCH_ID")
    tasks = []
    for row in docs:
        case = by_id[row["id"]]
        expected_path = HERE / "cases" / (row["id"] + ".md")
        actual_path = ROOT / row["path"]
        if actual_path.resolve() != expected_path.resolve():
            raise ValueError("SOURCE_PATH_DRIFT")
        raw = safe_read(actual_path, row["blob"])
        if raw != render(case):
            raise ValueError("SOURCE_RENDER_DRIFT")
        if blob(raw) != row["blob"]:
            raise ValueError("SOURCE_GIT_BLOB_DRIFT")
        lines = raw.decode("utf8").splitlines()
        if len(lines) != 13 or row["candidate_lines"] != [9, 10, 11, 12, 13]:
            raise ValueError("SOURCE_LINE_NUMBER_DRIFT")
        truth = exhaustive_oracle(case)
        true_lines = [i + 9 for i, key in enumerate(case["order"]) if truth[key]]
        if (sorted(true_lines) != sorted(row["oracle_true_lines"])
            or truth != row["truth_by_predicate"]):
            raise ValueError("FROZEN_ORACLE_MISMATCH")
        inventory = packetize(raw, str(actual_path))
        if verify_packets(raw, inventory):
            raise ValueError("SOURCE_PACKET_PROVENANCE_FAILURE")
        line_map = {i: p for p in inventory["packets"]
                    for i in range(p["start_line"], p["end_line"] + 1)}
        candidates = []
        for n in row["candidate_lines"]:
            p = line_map.get(n)
            if p is None or p["section_path"][-1] != "Énoncé":
                raise ValueError("MISSING_OR_INVALID_PROPOSITION_PACKET")
            candidates.append({
                "line": n,
                "source_text": lines[n-1].strip(),
                "packet_id": p["packet_id"],
                "section": p["section_path"],
            })
        if len(candidates) != 5 or any(
            not c["source_text"].startswith("Proposition : ")
            for c in candidates):
            raise ValueError("LEXICAL_CUE_OR_CANDIDATE_COUNT_DRIFT")
        # Every candidate is source-anchored and passes the unchanged Reader12 gate.
        for candidate in candidates:
            proposal = proposal_from_lines(row, candidates, [candidate["line"]])
            check = gate(raw, str(actual_path), proposal, provider="benchmark19-source-precheck")
            if (check["accepted_count"] != 1 or check["rejected_count"] != 0
                or check["horn_rules"] or check["automatic_promotions"]):
                raise ValueError("SOURCE_GATE_REJECTED_CANDIDATE")
        tasks.append({
            "ref": row, "case": case, "raw": raw, "source": actual_path,
            "candidates": candidates, "definition": lines[4],
        })
    return tasks


def messages(task: dict) -> list[dict]:
    user_prompt = (
        PROMPT.read_text(encoding="utf8").strip()
        + "\nDÉFINITION DE LA FONCTION :\n" + task["definition"]
        + "\nLIGNES CANDIDATES :\n" + json.dumps(
            [{"line": c["line"], "source_text": c["source_text"]}
             for c in task["candidates"]], ensure_ascii=False)
    )
    return [
        {"role": "system", "content": "Vérifie des propositions sur une structure finie. Réponds uniquement avec des numéros offerts ou NONE."},
        {"role": "user", "content": user_prompt},
    ]


def call_model(dialogue: list[dict]) -> dict:
    payload = {"messages": dialogue, "max_tokens": MAX_TOKENS,
               "temperature": 0, "stream": False}
    req = urllib.request.Request(
        URL, data=json.dumps(payload, ensure_ascii=False).encode("utf8"),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as response:
        answer = json.loads(response.read(160000))
    seconds = round(time.perf_counter() - t0, 3)
    choice = answer["choices"][0]
    raw_reply = choice["message"]["content"]
    if not isinstance(raw_reply, str):
        raise ValueError("MODEL_NON_TEXT_RESPONSE")
    return {
        "raw_reply": raw_reply, "seconds": seconds,
        "usage": answer.get("usage"), "finish_reason": choice.get("finish_reason"),
        "server_model": answer.get("model"),
    }


def metric(chosen: list[int], gold: list[int]) -> dict:
    pred, reference = set(chosen), set(gold)
    tp, fp, fn = len(pred & reference), len(pred - reference), len(reference - pred)
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": tp/(tp+fp) if tp+fp else None,
        "recall": tp/(tp+fn) if tp+fn else None,
        "f1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
    }


def aggregate(rows: list[dict]) -> dict:
    tp = sum(x["metrics"]["tp"] for x in rows)
    fp = sum(x["metrics"]["fp"] for x in rows)
    fn = sum(x["metrics"]["fn"] for x in rows)
    return {
        "n": len(rows), "tp": tp, "fp": fp, "fn": fn,
        "precision": tp/(tp+fp) if tp+fp else None,
        "recall": tp/(tp+fn) if tp+fn else None,
        "micro_f1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
    }


def source_gate(task: dict, chosen: list[int], provider: str) -> int:
    gated = gate(task["raw"], str(task["source"]),
                 proposal_from_lines(task["ref"], task["candidates"], chosen),
                 provider=provider)
    if (gated["accepted_count"] != len(chosen)
        or gated["rejected_count"] or gated["automatic_promotions"]
        or gated["horn_rules"]):
        raise ValueError("SOURCE_GATE_OR_AUTO_PROMOTION_VIOLATION")
    return gated["accepted_count"]


def model_case(task: dict, model_label: str, call=call_model) -> dict:
    chats = messages(task)
    response = call(chats)
    chosen, reject = parse_selection(response["raw_reply"],
                                     set(task["ref"]["candidate_lines"]))
    accepted = source_gate(task, chosen, model_label) if reject is None else 0
    return {
        "id": task["ref"]["id"],
        "kind": task["case"]["kind"],
        "source_blob": task["ref"]["blob"],
        "status": "REJECTED" if reject else "VALID",
        "reject_reason": reject,
        "abstained": reject is None and chosen == [],
        "offered": task["ref"]["candidate_lines"],
        "gold_lines": task["ref"]["oracle_true_lines"],
        "selected": chosen,
        "accepted_count": accepted,
        "metrics": metric(chosen, task["ref"]["oracle_true_lines"]),
        "messages": chats,
        **response,
    }


def controls(tasks: list[dict]) -> dict:
    methods = {
        "first3": lambda t: t["ref"]["candidate_lines"][:3],
        "lexical_first3": lambda t: [c["line"] for c in t["candidates"] if c["source_text"].startswith("Proposition : ")][:3],
        "none": lambda t: [],
        "all5_coverage_only": lambda t: t["ref"]["candidate_lines"],
    }
    results = {}
    for method, choose in methods.items():
        rows = []
        for task in tasks:
            selected = choose(task)
            if method != "all5_coverage_only":
                source_gate(task, selected, "benchmark19-control-"+method)
            rows.append({
                "id": task["ref"]["id"], "kind": task["case"]["kind"],
                "selected": selected, "gold_lines": task["ref"]["oracle_true_lines"],
                "metrics": metric(selected, task["ref"]["oracle_true_lines"]),
            })
        results[method] = {"rows": rows, "aggregate": aggregate(rows)}
    if results["first3"]["aggregate"] != results["lexical_first3"]["aggregate"]:
        raise ValueError("LEXICAL_CONTROL_UNEXPECTED_ADVANTAGE")
    return results


def benchmark(mode: str, model_label: str | None) -> dict:
    tasks = prepare()
    report = {
        "experiment": "OMEGA_BENCH19_FINITE_MATH_TRUTH_MATCHED_QWEN",
        "status": "STARTED", "case_count": len(tasks),
        "corpus_type": "SYNTHETIC_NOT_AUTHENTIC_PAPERS",
        "gold_source": "EXHAUSTIVE_ORACLE_WITHOUT_HUMAN_INDEPENDENT_ANNOTATION",
        "independent_human_labels": False,
        "model_sha256": {"0p5b": SHA_0P5B, "3b": SHA_3B},
        "llama_cpp_sha": LLAMA_SHA,
        "model_label": model_label, "max_new_tokens": MAX_TOKENS,
        "n_paid_api": 0, "n_auto_certification": 0, "n_horn_rules": 0,
        "controls": controls(tasks), "rows": [],
    }
    if mode == "control":
        report["status"] = "FROZEN_SOURCE_CONTROLS_VERIFIED"
    else:
        if model_label not in ("0p5b", "3b"):
            raise ValueError("MODEL_LABEL_REQUIRED")
        for task in tasks:
            row = model_case(task, model_label)
            report["rows"].append(row)
            print(row["id"], row["status"], repr(row["raw_reply"]),
                  "selected", row["selected"], flush=True)
        report["aggregate"] = aggregate(report["rows"])
        report["by_family"] = {
            family: aggregate([r for r in report["rows"] if r["kind"] == family])
            for family in ("affine", "quadratic")
        }
        report["abstentions"] = sum(r["abstained"] for r in report["rows"])
        report["rejections"] = sum(r["status"] == "REJECTED" for r in report["rows"])
        report["seconds_inference_only"] = round(sum(r["seconds"] for r in report["rows"]), 3)
        report["status"] = "FINISHED_REAL_INFERENCE"
    return report


def compare(control_file: Path, small_file: Path, large_file: Path) -> dict:
    ctrl = json.loads(control_file.read_text(encoding="utf8"))
    small = json.loads(small_file.read_text(encoding="utf8"))
    large = json.loads(large_file.read_text(encoding="utf8"))
    if not (ctrl["status"] == "FROZEN_SOURCE_CONTROLS_VERIFIED"
            and small["status"] == large["status"] == "FINISHED_REAL_INFERENCE"):
        raise ValueError("INCOMPLETE_BENCHMARK")
    if (small["case_count"] != large["case_count"] or small["case_count"] != 20
        or [r["id"] for r in small["rows"]] != [r["id"] for r in large["rows"]]
        or small["model_sha256"] != large["model_sha256"]):
        raise ValueError("NON_MATCHED_BENCHMARK")
    first = ctrl["controls"]["first3"]["aggregate"]
    a, b = small["aggregate"], large["aggregate"]
    return {
        "status": "MATCHED_BENCHMARK_COMPLETE",
        "n_cases": 20,
        "baseline_first3": first,
        "small_model": a, "large_model": b,
        "small_by_family": small["by_family"],
        "large_by_family": large["by_family"],
        "primary_success": b["micro_f1"] > a["micro_f1"] and b["micro_f1"] > first["micro_f1"],
        "small_rejections": small["rejections"], "large_rejections": large["rejections"],
        "small_abstentions": small["abstentions"], "large_abstentions": large["abstentions"],
        "small_inference_seconds": small["seconds_inference_only"],
        "large_inference_seconds": large["seconds_inference_only"],
        "generalizable_to_real_documents": "NOT_ESTABLISHED",
        "mathematical_certifications": 0,
        "note": "Synthetic oracle truth, not independent human annotation; size-only causality unproven.",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("control", "model", "compare"), required=True)
    ap.add_argument("--model-label", choices=("0p5b", "3b"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--control", type=Path)
    ap.add_argument("--small", type=Path)
    ap.add_argument("--large", type=Path)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    failed = False
    try:
        if args.mode == "compare":
            if not all((args.control, args.small, args.large)):
                raise ValueError("MISSING_COMPARISON_INPUT")
            report = compare(args.control, args.small, args.large)
        else:
            report = benchmark(args.mode, args.model_label)
    except Exception:
        failed = True
        report = {"status": "FAILED_NOT_SCIENTIFIC_RESULT",
                  "exception": traceback.format_exc()}
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n",
                        encoding="utf8")
    print("BENCH19", args.mode, report["status"], flush=True)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
