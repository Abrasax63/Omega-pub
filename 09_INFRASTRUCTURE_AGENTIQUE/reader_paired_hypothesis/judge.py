"""Evaluate source fidelity first, then exhaustively check the cited contract."""

import argparse
import hashlib
import itertools
import json
import re
from pathlib import Path

from pilot import CASES, HERE, LLAMA_COMMIT, MAX_TOKENS, MODEL_SHA, SEED
from pilot import messages_for, source_path, view, write_json
from gate import gate


DOMAIN = r"Soit \(X\) un ensemble fini avec \(1\leq |X|\leq 3\) et \(T:X\to X\)."
IDEMPOTENT = r"T\circ T=T"
INVOLUTIVE = r"T\circ T=\operatorname{id}_X"
INJECTIVE = r"\forall x,y\in X,\quad T(x)=T(y)\Longrightarrow x=y."
ROLES = ("premise", "premise", "conclusion")


def baseline(lines):
    domain = next(item["line"] for item in lines if item["text"] == DOMAIN)
    equations = [
        item["line"]
        for before, item, after in zip(lines, lines[1:], lines[2:])
        if before["text"] == r"\[" and after["text"] == r"\]"
    ]
    return [domain, equations[0], equations[-1]]


def finite_oracle(citations):
    domain, law, conclusion = citations
    if domain != DOMAIN or law not in {IDEMPOTENT, INVOLUTIVE} or conclusion != INJECTIVE:
        return {"verdict": "UNSUPPORTED_EXACT_CONTRACT"}

    total = retained = violations = 0
    witness = None
    for n in range(1, 4):
        identity = tuple(range(n))
        for t in itertools.product(identity, repeat=n):
            total += 1
            target = identity if law == INVOLUTIVE else t
            if tuple(t[x] for x in t) != target:
                continue
            retained += 1
            collisions = ((x, y) for x in identity for y in range(x + 1, n) if t[x] == t[y])
            collision = next(collisions, None)
            if collision is not None:
                violations += 1
                if witness is None:
                    witness = {"size": n, "map": list(t), "collision": list(collision)}
    return {
        "verdict": "REFUTED" if witness else "TRUE_ON_FINITE_DOMAIN",
        "maps_examined": total,
        "maps_satisfying_hypothesis": retained,
        "violations": violations,
        "first_counterexample": witness,
    }


def grade_selection(case, visible, selection, expected):
    if len(selection) != 3 or len(set(selection)) != 3:
        return {"status": "NO_VALID_SELECTION", "selected_lines": selection, "success": False}
    by_line = {item["line"]: item for item in visible}
    if any(line not in by_line for line in selection):
        return {"status": "LINE_NOT_OFFERED", "selected_lines": selection, "success": False}

    evidence = [
        {"role": role, "packet_id": by_line[line]["packet"], "line": line, "literal": by_line[line]["text"]}
        for role, line in zip(ROLES, selection)
    ]
    path = source_path(case)
    proposal = {"source_blob": CASES[case], "claims": [
        {"claim_id": "C1", "packet_id": evidence[-1]["packet_id"], "evidence": evidence},
    ]}
    gated = gate(path.read_bytes(), path.as_posix(), proposal, provider="paired-hypothesis-pilot")
    if gated["horn_rules"] or gated["automatic_promotions"]:
        raise ValueError("unexpected automatic promotion")
    if gated["accepted_count"] != 1:
        return {"status": "GATE_REJECTED", "rejected": gated["rejected"],
                "selected_lines": selection, "success": False}

    claim = gated["accepted"][0]
    oracle = finite_oracle([cite["literal"] for cite in claim["evidence"]])
    faithful = selection == expected["lines"]
    target = "TRUE_ON_FINITE_DOMAIN" if expected["true_on_finite_domain"] else "REFUTED"
    return {
        "status": "EVALUATED",
        "selected_lines": selection,
        "role_order_and_source_lines_exact": faithful,
        "claim": claim,
        "oracle": oracle,
        "matches_expected_verdict": oracle["verdict"] == target,
        "success": faithful and oracle["verdict"] == target,
    }


def completion(row):
    if row.get("http_status") != 200 or "transport_error" in row:
        return {"status": "INFRA_FAILURE", "selection": []}
    try:
        response = json.loads(row["raw_response"])
        choice = response["choices"][0]
        reply = choice["message"]["content"].strip()
        tokens = response["usage"]["completion_tokens"]
        if type(tokens) is not int or not 0 < tokens <= MAX_TOKENS:
            raise ValueError("unattested token count")
    except (KeyError, AttributeError, IndexError, ValueError, TypeError):
        return {"status": "NO_ATTESTED_COMPLETION", "selection": []}

    numeric = re.fullmatch(r"[0-9]{1,3}(?:[ \t]*,[ \t]*[0-9]{1,3}){2}", reply)
    return {
        "status": "ATTESTED_COMPLETION",
        "format": "TRIPLE" if numeric else "ABSTAINED" if reply == "NONE" else "INVALID",
        "reply": reply,
        "selection": [int(s) for s in reply.split(",")] if numeric else [],
        "completion_tokens": tokens,
        "finish_reason": choice.get("finish_reason"),
    }


def evaluate(raw_path):
    raw = raw_path.read_bytes()
    record = json.loads(raw)
    ref = json.loads((HERE / "reference.json").read_text(encoding="utf-8"))
    if (record["weights_sha256"], record["llama_cpp_commit"], record["paid_api_calls"]) != (
        MODEL_SHA, LLAMA_COMMIT, 0
    ):
        raise ValueError("unexpected runtime identity")
    if [row["case"] for row in record["rows"]] != list(CASES):
        raise ValueError("one raw record per frozen source is required")

    rows = []
    for row in record["rows"]:
        case = row["case"]
        visible = view(case)
        expected = ref["cases"][case]
        request = row["request"]
        if (
            row["source_blob"] != CASES[case]
            or expected["git_blob"] != CASES[case]
            or request != {"messages": messages_for(visible), "max_tokens": MAX_TOKENS,
                           "temperature": 0, "seed": SEED, "stream": False}
        ):
            raise ValueError(f"{case}: source or inference configuration mismatch")
        result = completion(row)
        rows.append({
            "case": case,
            "expected": expected,
            "completion": result,
            "model": grade_selection(case, visible, result["selection"], expected),
            "position_baseline": grade_selection(case, visible, baseline(visible), expected),
        })

    runs = sum(row["completion"]["status"] == "ATTESTED_COMPLETION" for row in rows)
    model_passes = sum(row["model"]["success"] for row in rows)
    baseline_passes = sum(row["position_baseline"]["success"] for row in rows)
    if runs < len(CASES):
        status = "INDETERMINATE_INCOMPLETE_INFERENCE"
    elif model_passes == len(CASES):
        status = "TWO_CASE_CRITERION_MET"
    else:
        status = "TWO_CASE_CRITERION_NOT_MET"
    return {
        "status": status,
        "inference_responses_attested": runs,
        "model_passes": model_passes,
        "position_baseline_passes": baseline_passes,
        "reference_provenance": ref["reference_provenance"],
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "automatic_certifications": 0,
        "automatic_horn_rules": 0,
        "rows": rows,
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--raw", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    report = evaluate(args.raw)
    write_json(args.output, report)
    for key in ("status", "inference_responses_attested", "model_passes", "position_baseline_passes"):
        print(f"{key}={report[key]}")
    if report["inference_responses_attested"] != len(CASES):
        raise SystemExit(1)
