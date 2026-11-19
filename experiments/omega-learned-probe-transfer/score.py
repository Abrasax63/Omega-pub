"""Evaluate the experimental decisions using the two visible candidate rules."""

import argparse
import hashlib
import re
from pathlib import Path

from pilot import ENGINE, HERE, MEMO_GRAMMAR, SCHEDULE, SOURCE_GRAMMAR, TARGET_SYSTEM, WEIGHTS
from pilot import decode, memo_text, observe, read_json, request_params, save, target_grammar, target_prompt


def measurements(case, word):
    if case == "limit":
        n = word.count("F")
        return int(n % 2 == 0), int(n == 2)
    additive = sequence = 1
    for x in word:
        if x == "F":
            additive = (additive + 2) % 7
            sequence = (sequence + 2) % 7
        else:
            additive = (additive - 1) % 7
            sequence = (-sequence) % 7
    return additive, sequence


def grade(case, text):
    length = 3 if case == "order" else 4
    pattern = rf"(ORDRE|CHARGE)\s+([FG]{{{length}}})\s+([FG]{{{length}}})"
    m = re.fullmatch(pattern, text)
    if m is None:
        return {"status": "ABSTAINED" if text == "NONE" else "FORMAT_INVALID", "success": False}
    factor, left, right = m.groups()
    same_mix = left.count("F") == right.count("F")
    lvals, rvals = measurements(case, left), measurements(case, right)
    equality = [x == y for x, y in zip(lvals, rvals)]
    scope = factor == "ORDRE" and same_mix if case == "order" else factor == "CHARGE" and not same_mix
    return {
        "status": "EVALUATED", "factor": factor, "words": [left, right], "same_mix": same_mix,
        "readouts": [lvals, rvals], "equality_per_candidate": equality,
        "false_order_transfer": case == "limit" and factor == "ORDRE",
        "success": scope and equality[0] != equality[1],
    }


def score(acquired_path, raw_path):
    raw = read_json(raw_path)
    acquired = read_json(acquired_path)
    if raw["acquired"] != acquired or (acquired["weights_sha256"], acquired["llama_cpp_commit"]) != (
        WEIGHTS, ENGINE
    ):
        raise ValueError("acquisition or runtime mismatch")
    if acquired["probe"]["request"].get("grammar") != SOURCE_GRAMMAR:
        raise ValueError("unexpected source decoding contract")
    if acquired["reflection"]["request"].get("grammar") != MEMO_GRAMMAR:
        raise ValueError("unexpected memo decoding contract")
    probe = decode(acquired["probe"], 40)
    reflection = decode(acquired["reflection"], 160)
    if probe and observe(probe["text"]) != acquired["trace"]:
        raise ValueError("source feedback does not replay")
    note = memo_text(reflection)
    tasks = read_json(HERE / "tasks.json")
    if [(r["case"], r["arm"]) for r in raw["targets"]] != list(SCHEDULE):
        raise ValueError("target schedule mismatch")
    rows = []
    for row in raw["targets"]:
        case, arm = row["case"], row["arm"]
        expected_note = note if arm == "MEMO" else "(emplacement neutre)"
        expected = target_prompt(tasks[case], acquired["trace"], expected_note)
        req = row["request"]
        if req != request_params(TARGET_SYSTEM, expected, 64, target_grammar(case)):
            raise ValueError("unfrozen target input or budget")
        answer = decode(row, 64)
        judgement = grade(case, answer["text"]) if answer else {
            "status": "INFRA_FAILURE", "success": False
        }
        rows.append({"case": case, "arm": arm, "answer": answer, "grade": judgement})
    scores = {arm: sum(r["grade"]["success"] for r in rows if r["arm"] == arm)
              for arm in ("MEMO", "SANS_MEMO")}
    actual = int(probe is not None) + int(reflection is not None) + sum(
        r["answer"] is not None for r in rows
    )
    source_success = acquired["trace"].get("isolated_order_effect", False)
    passed = source_success and note and scores["MEMO"] == 2 and scores["MEMO"] > scores["SANS_MEMO"]
    if actual != 6:
        verdict = "INDETERMINATE_INFRASTRUCTURE"
    else:
        verdict = "CRITERION_MET" if passed else "CRITERION_NOT_MET"
    return {
        "verdict": verdict, "real_completions": actual, "scores": scores, "rows": rows,
        "source_trace": acquired["trace"], "memo": note,
        "acquisition_sha256": hashlib.sha256(acquired_path.read_bytes()).hexdigest(),
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquired", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = score(args.acquired, args.raw)
    save(args.output, result)
    for k in ("verdict", "real_completions", "scores"):
        print(f"{k}={result[k]}")
    if result["real_completions"] != 6:
        raise SystemExit(1)
