#!/usr/bin/env python3
"""OMEGA-INTEGRATION-06: immutable source registry + paired small-model ablation.

No source-id-specific rule, no LLM weight update, no certification.
The test oracle is a bounded, domain-specific post hoc filter, not general reasoning.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[1]
SOURCES_FILE = HERE / "SOURCES_FROZEN.json"
QUESTIONS_FILE = HERE / "QUESTIONS_FROZEN.json"
SOURCES_BLOB = "2107a731f92f4062f655eb94f63a8d95600468fe"
QUESTIONS_BLOB = "a6c5a2e438104375cae3aa80c5f533ba5589fda5"
OLD_ENGINE_BLOB = "4e4bf62de81bea0eebe1a7a80562e002698d0cd2"
OLD_ENGINE = BASE / "real_math_scope03" / "engine.py"
KINDS = frozenset(("OUI", "NON", "ABSTENTION"))
LABEL = {"OUI": "YES", "NON": "NO", "ABSTENTION": "ABSTAIN"}
MAX_SOURCE_CHARS = 8000


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def digest(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def frozen_bytes(path: Path, expected_blob: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("pinned input missing or symlinked")
    data = path.read_bytes()
    if git_blob(data) != expected_blob:
        raise ValueError("pinned input blob mismatch: " + str(path))
    return data


def load_registry(manifest_path: Path = SOURCES_FILE, base: Path = BASE,
                  pinned_blob: str | None = SOURCES_BLOB) -> dict:
    """Generic manifest: never dispatch by source_id or by subject."""
    raw = frozen_bytes(manifest_path, pinned_blob) if pinned_blob else manifest_path.read_bytes()
    manifest = json.loads(raw)
    if manifest.get("version") != "omega-source-registry-v1":
        raise ValueError("unsupported manifest version")
    out = {}
    for entry in manifest["sources"]:
        key = entry["source_id"]
        relative = entry["relative_path"]
        parts = PurePosixPath(relative)
        if (not isinstance(relative, str) or not relative or parts.is_absolute()
                or not parts.parts or any(p in ("..", ".", "") for p in parts.parts)
                or "\\" in relative or ":" in relative):
            raise ValueError("unsafe source path")
        target = base.joinpath(*parts.parts)
        # Reject symlinks at any level, even if they eventually resolve within base.
        current = base
        for part in parts.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("symlinked source path")
        if not target.is_file() or not target.resolve().is_relative_to(base.resolve()):
            raise ValueError("source file not found inside allowed base")
        raw_doc = target.read_bytes()
        if git_blob(raw_doc) != entry["git_blob"]:
            raise ValueError("source content not at pinned Git blob")
        if key in out:
            raise ValueError("duplicate source id")
        body = raw_doc.decode("utf-8")
        if not body.strip() or len(body) > MAX_SOURCE_CHARS:
            raise ValueError("invalid or oversized source")
        out[key] = {
            "text": body,
            "path": relative,
            "blob": entry["git_blob"],
            "lines": body.splitlines(),
        }
    if not out:
        raise ValueError("empty source registry")
    return out


def load_questions(path: Path = QUESTIONS_FILE) -> list[dict]:
    data = json.loads(frozen_bytes(path, QUESTIONS_BLOB))
    cases = data["cases"]
    ids = [c["id"] for c in cases]
    if len(cases) != 12 or len(ids) != len(set(ids)):
        raise ValueError("cohort altered")
    if any(c["oracle_kind"] not in ("access", "capacity") for c in cases):
        raise ValueError("unknown oracle kind")
    return cases


def prompts(question: str, source: dict | None) -> str:
    # No answer or oracle metadata supplied to the LLM.
    policy = (
        "Tu réponds à une question mathématique fermée. "
        "Si les informations sont insuffisantes, dis ABSTENTION. "
        "Réponds uniquement par un des mots autorisés, sans justification.\n"
    )
    if source is None:
        memo = "Document fourni: aucun.\n"
    else:
        lines = "\n".join(str(i) + ": " + line for i, line in enumerate(source["lines"], 1))
        memo = ("Document scientifique en lecture seule; les affirmations ne valent "
                "pas preuve générale. Git blob: " + source["blob"] + "\n"
                + lines + "\n")
    return (policy + memo + "QUESTION: " + question
            + "\nOptions autorisées: OUI, NON, ABSTENTION.\nREPONSE:")


def decode(output: str) -> str:
    # llama-cli can echo the prompt, so only inspect AFTER its final response marker.
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    last = clean.rsplit("REPONSE:", 1)[-1].strip()
    if not last:
        return "ABSTENTION"
    words = re.findall(r"(?<!\w)(OUI|NON|ABSTENTION)(?!\w)", last.upper())
    return words[0] if len(words) == 1 else "ABSTENTION"


def llama_choose(cli: Path, model: Path, prompt: str, label: str) -> dict:
    command = [str(cli), "-m", str(model), "-p", prompt,
               "-n", "16", "-c", "3072", "-t", "4", "--temp", "0"]
    start = time.perf_counter()
    rec = {"called": True, "label": label, "prompt_sha256":
           hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
           "prompt_chars": len(prompt)}
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=240)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {**rec, "verdict": "ABSTENTION", "status": "CALL_FAILED",
                "error": type(exc).__name__,
                "seconds": round(time.perf_counter() - start, 3)}
    rec.update({"returncode": proc.returncode,
                "seconds": round(time.perf_counter() - start, 3),
                "raw_sha256": hashlib.sha256(proc.stdout.encode("utf-8")).hexdigest(),
                "raw_tail": proc.stdout[-350:]})
    if proc.returncode:
        return {**rec, "verdict": "ABSTENTION", "status": "CALL_FAILED",
                "stderr_tail": proc.stderr[-350:]}
    answer = decode(proc.stdout)
    return {**rec, "verdict": answer,
            "status": "PARSED" if answer != "ABSTENTION" else "ABSTAIN_OR_INVALID"}


def oracle(case: dict) -> str:
    """Independent finite enumeration; evaluated only AFTER all model choices freeze."""
    if case["oracle_kind"] == "access":
        word = case["word"]
        if not word or len(word) > 8 or any(c not in "01" for c in word):
            raise ValueError("invalid finite access test")
        # Model with two states a -> b -> b, pi(a)=0, pi(b)=1.
        state = "a"
        trace = []
        for _ in range(2 * len(word) + 4):
            trace.append("0" if state == "a" else "1")
            state = "b"
        produced = "".join(trace)
        if case["access_test"] == "start":
            match = produced.startswith(word)
        elif case["access_test"] == "factor":
            match = word in produced
        else:
            raise ValueError("unknown access predicate")
    elif case["oracle_kind"] == "capacity":
        pair = case["multiplicities"]
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("invalid multiplicities")
        options = set()
        witnesses = ("A", "A", "B", "B")
        for bits in range(1 << len(witnesses)):
            selected = [witnesses[i] for i in range(4) if bits & (1 << i)]
            options.add((selected.count("A"), selected.count("B")))
        match = tuple(pair) in options
    else:
        raise ValueError("unknown bounded oracle")
    return "OUI" if match else "NON"


def stats(rows: list[dict], arm: str) -> dict:
    vals = [r["choices"][arm] for r in rows]
    return {
        "correct": sum(v == r["oracle"] for v, r in zip(vals, rows)),
        "false_confident": sum(v != "ABSTENTION" and v != r["oracle"]
                               for v, r in zip(vals, rows)),
        "abstentions": vals.count("ABSTENTION"),
        "answered": len(vals) - vals.count("ABSTENTION"),
        "total": len(vals),
    }


def run(chooser, *, registry=None, cases=None):
    registry = registry if registry is not None else load_registry()
    cases = cases if cases is not None else load_questions()
    if git_blob(OLD_ENGINE.read_bytes()) != OLD_ENGINE_BLOB:
        raise ValueError("historical math engine was unexpectedly modified")
    pending = []
    all_choices = []
    for i, case in enumerate(cases):
        if case["source_id"] not in registry:
            raise ValueError("unrecognized document source: " + case["source_id"])
        source = registry[case["source_id"]]
        if i % 2:
            order = ("memory", "solo")
        else:
            order = ("solo", "memory")
        calls = {}
        for arm in order:
            prompt = prompts(case["question"], source if arm == "memory" else None)
            result = chooser(prompt, arm, case["id"])
            if result.get("verdict") not in KINDS:
                raise ValueError("chooser returned invalid classification")
            calls[arm] = result
        choice = {"solo": calls["solo"]["verdict"], "memory": calls["memory"]["verdict"]}
        all_choices.append({"id": case["id"], **choice})
        pending.append((case, calls, order))
    choices_sha = digest(all_choices)
    print("ALL_MODEL_CHOICES_SHA256_BEFORE_ORACLE=" + choices_sha, flush=True)
    # Strict barrier: oracle has not been invoked on any target case until now.
    rows = []
    for case, calls, order in pending:
        truth = oracle(case)
        memory = calls["memory"]["verdict"]
        solo = calls["solo"]["verdict"]
        rows.append({
            "id": case["id"], "source_id": case["source_id"],
            "oracle": truth, "order": list(order),
            "choices": {
                "solo": solo,
                "memory": memory,
                "solo_checked": solo if solo == truth else "ABSTENTION",
                "memory_checked": memory if memory == truth else "ABSTENTION",
            },
            "calls": calls,
            "finite_oracle_calls": 2,
        })
    metrics = {k: stats(rows, k) for k in
               ("solo", "memory", "solo_checked", "memory_checked")}
    return {
        "experiment": "OMEGA-INTEGRATION-06",
        "status": "EXPLORATORY_TWO_FINITE_MICRODOMAINS",
        "input_blobs": {"registry": SOURCES_BLOB, "questions": QUESTIONS_BLOB},
        "old_engine_blob_unchanged": OLD_ENGINE_BLOB,
        "loaded_source_ids": sorted(registry),
        "source_count": len(registry),
        "calls_attempted": len(pending) * 2,
        "choices_sha256_before_scoring": choices_sha,
        "oracle_checked_after_choices": True,
        "finite_oracle_calls": len(pending) * 2,
        "same_model_and_output_limit": True,
        "same_input_token_usage": False,
        "input_token_parity_confirmed": False,
        "model_weights_changed": False,
        "auto_promotion": False,
        "metrics": metrics,
        "h2_memory_gain_local": (
            metrics["memory"]["correct"] > metrics["solo"]["correct"]
            and metrics["memory"]["false_confident"] <= metrics["solo"]["false_confident"]),
        "h3_finite_oracle_safety_local": (
            metrics["memory_checked"]["false_confident"] == 0
            and metrics["memory_checked"]["answered"] > 0),
        "limitations": [
            "Questions are new but source documents and source schemas are not blind.",
            "Same-author questions on two small finite mathematical examples.",
            "The verifier has a correct executable oracle for this narrow benchmark: NOT general scientific verification.",
            "Post-filtering cannot prove increased model intelligence and could also filter the solo arm.",
            "Memory and solo input-token usage is not equalized; same decode settings are not equal total computation.",
            "No learned weights, no external blind holdout, no generalization certification.",
        ],
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llama-cli", type=Path, required=True)
    parser.add_argument("--model-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.llama_cli.is_file() or not args.model_file.is_file():
        parser.error("missing pinned llama-cli or model file")
    report = run(lambda prompt, arm, case_id: llama_choose(
        args.llama_cli, args.model_file, prompt, case_id + "/" + arm))
    target = args.output.resolve()
    if target.is_relative_to(ROOT):
        parser.error("write report outside checkout; keep source tree immutable")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"experiment": report["experiment"], "metrics": report["metrics"],
                      "choices_sha256_before_scoring": report["choices_sha256_before_scoring"],
                      "source_count": report["source_count"],
                      "h2_memory_gain_local": report["h2_memory_gain_local"],
                      "h3_finite_oracle_safety_local": report["h3_finite_oracle_safety_local"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
