#!/usr/bin/env python3
"""Reader18: matched Qwen2.5 Instruct Q4_K_M source-line classification pilot.

Six synthetic exact-arithmetic documents; no human-independent labels.
This code cannot certify a theorem or promote a source claim.
"""
from __future__ import annotations

import argparse
import json
import operator
from pathlib import Path
import re
import sys
import time
import traceback
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from selector import build_prompt, candidates_from_baseline, parse_selection, proposal_from_lines
from read import safe_read
from gate import gate

MANIFEST = HERE / "FROZEN_CASES.json"
SPEC = HERE / "CASE_SPEC.json"
MODEL_NAMES = {
    "0p5b": "Qwen2.5-0.5B-Instruct-GGUF Q4_K_M",
    "3b": "Qwen2.5-3B-Instruct-GGUF Q4_K_M",
}
GGUF_SHA256 = {
    "0p5b": "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
LLAMA_CPP_SHA = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
ENDPOINT = "http://127.0.0.1:8091/v1/chat/completions"
MAX_NEW_TOKENS = 64
EXACT_FORMULA = re.compile(
    r"\((\d+) ([+*]) (\d+)\) mod (\d+) = (\d+)\."
)


def oracle_check(ref: dict, spec: dict, raw: bytes) -> None:
    """Independently recompute integer arithmetic, then verify source-role labels.

    Labels are synthetic author-defined roles, never independent human gold.
    """
    lines = raw.decode("utf-8").splitlines()
    if len(lines) != 9 or lines[2] != "## Énoncé":
        raise ValueError("SYNTHETIC_SOURCE_LAYOUT_DRIFT")
    if set(spec["order"]) != {"H", "D", "Q", "R1", "R2"}:
        raise ValueError("SYNTHETIC_ROLE_DRIFT")
    expected_gold = sorted(5 + i for i, name in enumerate(spec["order"])
                           if name in ("R1", "R2"))
    if sorted(ref["conclusion_lines"]) != expected_gold:
        raise ValueError("AUTHOR_GOLD_DIFFERS_FROM_FROZEN_SPEC")
    a, b, m = spec["a"], spec["b"], spec["m"]
    if any(type(z) is not int or z <= 0 for z in (a, b, m)) or m <= 2:
        raise ValueError("INVALID_EXACT_ARITHMETIC_SPEC")
    for i, role in enumerate(spec["order"]):
        source = lines[4+i]
        if role in ("R1", "R2"):
            matched = EXACT_FORMULA.search(source)
            if not matched:
                raise ValueError("GOLD_HAS_NO_CHECKABLE_EQUATION")
            x, op, y, mod, out = matched.groups()
            result = operator.add(int(x), int(y)) if op == "+" else operator.mul(int(x), int(y))
            if int(mod) != m or int(x) != a or int(y) != b or result % m != int(out):
                raise ValueError("GOLD_ARITHMETIC_FALSE")
            if not source.startswith(("Résultat calculé :", "Identité établie :")):
                raise ValueError("GOLD_ROLE_DRIFT")
        elif role == "H" and not source.startswith("Hypothèse à vérifier :"):
            raise ValueError("HYPOTHESIS_ROLE_DRIFT")
        elif role == "D" and not source.startswith("Définition proposée :"):
            raise ValueError("DEFINITION_ROLE_DRIFT")
        elif role == "Q" and not source.startswith("Question ouverte :"):
            raise ValueError("QUESTION_ROLE_DRIFT")


def prepare() -> list[dict]:
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    definitions = json.loads(SPEC.read_text(encoding="utf-8"))["cases"]
    if frozen["status"] != "FROZEN_BEFORE_ANY_MODEL_RUN":
        raise ValueError("NOT_PREREGISTERED")
    if len(frozen["documents"]) != 6 or len(definitions) != 6:
        raise ValueError("SIX_FROZEN_CASES_REQUIRED")
    by_id = {s["id"]: s for s in definitions}
    if len(by_id) != 6 or len({r["id"] for r in frozen["documents"]}) != 6:
        raise ValueError("DUPLICATE_CASES")
    prepared = []
    for ref in frozen["documents"]:
        path = ROOT / ref["path"]
        if not path.resolve().is_relative_to(HERE / "cases"):
            raise ValueError("SOURCE_OUTSIDE_FROZEN_CASE_DIR")
        raw = safe_read(path, ref["blob"])
        oracle_check(ref, by_id[ref["id"]], raw)
        staged, candidates, _ = candidates_from_baseline(raw, path, ref)
        if len(candidates) != 5 or staged["accepted_count"] != 5:
            raise ValueError("CANDIDATE_COVERAGE_DRIFT")
        if [c["line"] for c in candidates] != [5, 6, 7, 8, 9]:
            raise ValueError("CANDIDATE_LINE_DRIFT")
        if not set(ref["conclusion_lines"]).issubset({c["line"] for c in candidates}):
            raise ValueError("GOLD_NOT_OFFERED_TO_BOTH_MODELS")
        prepared.append({"ref": ref, "candidates": candidates, "raw": raw, "source": path})
    return prepared


def metrics(chosen: list[int], gold: list[int]) -> dict:
    predicted, truth = set(chosen), set(gold)
    tp, fp, fn = len(predicted & truth), len(predicted - truth), len(truth - predicted)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def summarize_metrics(records: list[dict]) -> dict:
    tp, fp, fn = (sum(x["metrics"][k] for x in records) for k in ("tp", "fp", "fn"))
    return {
        "n": len(records),
        "tp": tp, "fp": fp, "fn": fn,
        "precision": tp / (tp+fp) if tp+fp else None,
        "recall": tp / (tp+fn) if tp+fn else None,
        "f1": 2*tp / (2*tp+fp+fn) if 2*tp+fp+fn else None,
    }


def messages(candidates: list[dict]) -> list[dict]:
    # Exactly Reader15 messages; Reader14 build_prompt unchanged.
    return [
        {"role": "system", "content": "Choisis seulement des numéros de lignes. Réponds NONE ou une liste d'entiers séparés par des virgules."},
        {"role": "user", "content": build_prompt(candidates)},
    ]


def call_model(chats: list[dict]) -> dict:
    payload = {"messages": chats, "max_tokens": MAX_NEW_TOKENS,
               "temperature": 0, "stream": False}
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=240) as reply:
        response = json.loads(reply.read(150000))
    seconds = round(time.perf_counter() - start, 3)
    choice = response["choices"][0]
    text = choice["message"]["content"]
    if not isinstance(text, str):
        raise ValueError("MODEL_REPLY_NOT_STRING")
    return {"raw_reply": text, "seconds": seconds,
            "usage": response.get("usage"),
            "finish_reason": choice.get("finish_reason"),
            "server_model": response.get("model")}


def source_selection(prepared: dict, chosen: list[int], provider: str) -> dict:
    ref = prepared["ref"]
    gate_result = gate(
        prepared["raw"], str(prepared["source"]),
        proposal_from_lines(ref, prepared["candidates"], chosen),
        provider=provider,
    )
    if (gate_result["rejected_count"] != 0
        or gate_result["accepted_count"] != len(chosen)
        or gate_result["automatic_promotions"] != 0
        or gate_result["horn_rules"]):
        raise ValueError("SOURCE_GATE_OR_PROMOTION_VIOLATION")
    return {
        "selected": chosen,
        "accepted_count": gate_result["accepted_count"],
        "metrics": metrics(chosen, ref["conclusion_lines"]),
        "certifications": 0, "horn_rules": 0,
    }


def one_case(prepared: dict, model_label: str, call=call_model) -> dict:
    ref = prepared["ref"]
    generated = call(messages(prepared["candidates"]))
    chosen, reason = parse_selection(generated["raw_reply"],
                                     {c["line"] for c in prepared["candidates"]})
    record = {
        "id": ref["id"], "blob": ref["blob"], "status": "REJECTED" if reason else "VALID",
        "rejection": reason, "abstained": reason is None and chosen == [],
        "selected": chosen, **generated,
    }
    if reason:
        record["metrics"] = metrics([], ref["conclusion_lines"])
        record["accepted_count"] = 0
    else:
        record.update(source_selection(prepared, chosen, "reader18-"+model_label))
    return record


def controls(prepared: list[dict]) -> dict:
    out = {}
    for name, selector in [
        ("all", lambda p: [c["line"] for c in p["candidates"]]),
        ("first3", lambda p: [c["line"] for c in p["candidates"][:3]]),
        ("none", lambda p: [])]:
        # Select-all is a measurement of candidate coverage, not constrained by
        # MAX_CHOICES=3; use source baselines directly, not proposal_from_lines.
        rows = []
        for p in prepared:
            selected = selector(p)
            if name != "all":
                src = source_selection(p, selected, "reader18-control-"+name)
                m = src["metrics"]
            else:
                m = metrics(selected, p["ref"]["conclusion_lines"])
            rows.append({"id": p["ref"]["id"], "selected": selected, "metrics": m})
        out[name] = {"rows": rows, "aggregate": summarize_metrics(rows)}
    return out


def experiment(mode: str, model_label: str | None = None) -> dict:
    prepared = prepare()
    result = {
        "experiment": "READER18_MATCHED_QWEN25_INSTRUCT_Q4",
        "status": "STARTED",
        "synthetic_author_role_labels": True,
        "independent_human_annotation": False,
        "independent_exact_arithmetic_check": True,
        "six_cases": [p["ref"]["id"] for p in prepared],
        "model_label": model_label,
        "models_sha256": GGUF_SHA256,
        "llama_cpp_sha": LLAMA_CPP_SHA,
        "same_prompt": True, "same_candidates": True,
        "paid_api_calls": 0, "auto_certifications": 0, "auto_horn_rules": 0,
        "controls": controls(prepared),
        "rows": [],
    }
    if mode == "control":
        result["status"] = "SOURCE_CONTROLS_ONLY"
    else:
        for p in prepared:
            result["rows"].append(one_case(p, model_label))
        result["aggregate"] = summarize_metrics(result["rows"])
        result["total_inference_seconds"] = round(sum(x["seconds"] for x in result["rows"]), 3)
        result["abstentions"] = sum(x["abstained"] for x in result["rows"])
        result["rejections"] = sum(x["status"] == "REJECTED" for x in result["rows"])
        result["status"] = "FINISHED_REAL_INFERENCE"
    return result


def compare(control_path: Path, small_path: Path, large_path: Path) -> dict:
    a = json.loads(control_path.read_text(encoding="utf-8"))
    s = json.loads(small_path.read_text(encoding="utf-8"))
    l = json.loads(large_path.read_text(encoding="utf-8"))
    if (a["status"] != "SOURCE_CONTROLS_ONLY" or
        s["status"] != "FINISHED_REAL_INFERENCE" or
        l["status"] != "FINISHED_REAL_INFERENCE" or
        s["six_cases"] != l["six_cases"] or
        s["models_sha256"] != l["models_sha256"]):
        raise ValueError("INCOMPLETE_OR_UNPAIRED_RESULTS")
    baseline = a["controls"]["first3"]["aggregate"]
    small = s["aggregate"]
    large = l["aggregate"]
    return {
        "status": "PAIRED_COMPARISON_READY",
        "scientific_generalization": "NOT_DEMONSTRATED",
        "independent_human_annotation": False,
        "n_cases": 6, "baseline_first3": baseline, "model_0p5b": small,
        "model_3b": large,
        "primary_criterion_passed": large["f1"] > small["f1"] and large["f1"] > baseline["f1"],
        "seconds_0p5b_inference_only": s["total_inference_seconds"],
        "seconds_3b_inference_only": l["total_inference_seconds"],
        "note": "Scores synthetic; not causal size-only, not external holdout, no mathematics certification",
    }


def main() -> None:
    arg = argparse.ArgumentParser()
    arg.add_argument("--mode", choices=("control", "model", "compare"), required=True)
    arg.add_argument("--model-label", choices=("0p5b", "3b"))
    arg.add_argument("--output", type=Path, required=True)
    arg.add_argument("--control", type=Path)
    arg.add_argument("--small", type=Path)
    arg.add_argument("--large", type=Path)
    args = arg.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fail = False
    try:
        if args.mode == "compare":
            if not all((args.control, args.small, args.large)):
                raise ValueError("MISSING_COMPARISON_INPUTS")
            result = compare(args.control, args.small, args.large)
        else:
            if args.mode == "model" and args.model_label is None:
                raise ValueError("MODEL_LABEL_REQUIRED")
            result = experiment(args.mode, args.model_label)
    except Exception:
        fail = True
        result = {"status": "FAILED_NOT_SCIENTIFIC_RESULT", "exception": traceback.format_exc()}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("READER18", args.mode, result["status"], args.output, flush=True)
    if not fail and args.mode == "model":
        for row in result["rows"]:
            print(row["id"], row["status"], repr(row["raw_reply"]), row["selected"], flush=True)
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
