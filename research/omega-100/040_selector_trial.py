"""Compare a local selector with a fixed rule on finite-map cards."""
import argparse
import json
import re
import time
import urllib.request
from hashlib import sha256
from itertools import product
from pathlib import Path
from unittest import TestCase

PORT = 18091
MAX_CHOICES = 3
MAX_TOKENS = 64
TIMELIMIT = 90


def apply_power(mapping, start, steps):
    """Exact oracle, independent of the selector's text and choices."""
    jump = tuple(mapping)
    while steps:
        if steps & 1:
            start = jump[start]
        jump = tuple(jump[i] for i in jump)
        steps >>= 1
    return start


def correct_lines(card):
    start, steps = card["query"]
    value = apply_power(card["transitions"], start, steps)
    return {
        i for i, triple in enumerate(card["claims"], 1)
        if triple == [start, steps, value]
    }


def messages(card):
    pairs = ", ".join(f"{i} -> {v}" for i, v in enumerate(card["transitions"]))
    start, steps = card["query"]
    lines = "\n".join(
        f"{i}. T^{k}({source}) = {target}"
        for i, (source, k, target) in enumerate(card["claims"], 1)
    )
    question = (
        f"Application T: {pairs}. T^k signifie k applications successives de T.\n"
        f"Question: quelle est la valeur de T^{steps}({start}) ?\n"
        "Choisis uniquement les lignes qui donnent la vraie valeur pour cette question exacte. "
        "Les lignes répondant à une autre question sont hors sujet.\n"
        f"{lines}\n"
        "Réponds uniquement par un à trois numéros séparés par des virgules, "
        "ou NONE si aucune ligne ne convient."
    )
    return [
        {"role": "system", "content": "Tu sélectionnes des assertions mathématiques candidates."},
        {"role": "user", "content": question},
    ]


def parse(reply, count):
    reply = reply.strip()
    if reply == "NONE":
        return set()
    if not re.fullmatch(r"[1-9][0-9]*(?:[ \t]*,[ \t]*[1-9][0-9]*){0,2}", reply):
        raise ValueError("invalid_format")
    chosen = {int(value) for value in reply.split(",")}
    if len(chosen) != reply.count(",") + 1 or max(chosen) > count:
        raise ValueError("duplicate_or_out_of_range")
    return chosen


def infer(card):
    request = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/v1/chat/completions",
        data=json.dumps({
            "messages": messages(card), "temperature": 0, "seed": 42,
            "max_tokens": MAX_TOKENS, "stream": False,
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    raw = None
    usage = {}
    try:
        with urllib.request.urlopen(request, timeout=TIMELIMIT) as response:
            result = json.load(response)
        raw = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})
        if raw is None:
            raise ValueError("missing_content")
        chosen = parse(raw, len(card["claims"]))
        status = "selection" if chosen else "abstention"
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        chosen = set()
        status = "format_rejection" if raw is not None else "inference_error"
        return chosen, {
            "status": status, "raw": raw, "usage": usage,
            "seconds": time.perf_counter() - start, "error": type(error).__name__,
        }
    return chosen, {
        "status": status, "raw": raw, "usage": usage,
        "seconds": time.perf_counter() - start,
    }


def score(chosen, truth, status, count):
    return {
        "tp": len(chosen & truth), "fp": len(chosen - truth),
        "fn": len(truth - chosen), "tn": count - len(chosen | truth),
        "correct_abstention": int(status == "abstention" and not truth),
        "abstention": int(status == "abstention"),
        "format_rejection": int(status == "format_rejection"),
        "inference_error": int(status == "inference_error"),
    }


def run(cards, use_model):
    # Complete the reference arm before the first inference.
    reference = []
    for card in cards:
        start = time.perf_counter_ns()
        selected = set(range(1, min(MAX_CHOICES, len(card["claims"])) + 1))
        reference.append((selected, time.perf_counter_ns() - start))
    predictions = [infer(card) for card in cards] if use_model else []
    rows = []
    for i, (card, (selected, latency)) in enumerate(zip(cards, reference)):
        truth = correct_lines(card)
        count = len(card["claims"])
        row = {
            "id": card["id"], "oracle_positive_count": len(truth),
            "reference": {**score(selected, truth, "selection", count), "ns": latency},
        }
        if use_model:
            chosen, report = predictions[i]
            row["model"] = {
                **score(chosen, truth, report["status"], count), **report,
            }
        rows.append(row)
    return rows


class PilotControls(TestCase):
    def test_oracle_matches_direct_iteration(self):
        for size in (1, 2, 3):
            for mapping in product(range(size), repeat=size):
                for start in range(size):
                    direct = start
                    for steps in range(18):
                        self.assertEqual(apply_power(mapping, start, steps), direct)
                        direct = mapping[direct]

    def test_invalid_and_duplicate_ids_are_rejected(self):
        for reply in ("999", "1,1", "1,2,3,4", "1 and 2", "NONE\n1"):
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                parse(reply, 6)
        self.assertEqual(parse("2, 6", 6), {2, 6})
        self.assertEqual(parse("NONE", 6), set())


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--inputs", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    cli.add_argument("--model", action="store_true")
    args = cli.parse_args()
    raw = args.inputs.read_bytes()
    rows = run(json.loads(raw), args.model)
    public_keys = (
        "tp", "fp", "fn", "tn", "correct_abstention", "abstention",
        "format_rejection", "inference_error",
    )
    summary = {
        "input_sha256": sha256(raw).hexdigest(),
        "mode": "real_local_inference" if args.model else "reference_only",
        "cards": len(rows),
        "oracle_positive": sum(row["oracle_positive_count"] for row in rows),
    }
    for arm in ("reference", "model") if args.model else ("reference",):
        summary[arm] = {key: sum(row[arm][key] for row in rows) for key in public_keys}
    if args.model:
        for key in ("prompt_tokens", "completion_tokens"):
            summary["model"][key] = sum(row["model"]["usage"].get(key, 0) for row in rows)
        summary["model"]["seconds"] = round(sum(row["model"]["seconds"] for row in rows), 6)
    summary["reference"]["ns"] = sum(row["reference"]["ns"] for row in rows)
    args.output.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

