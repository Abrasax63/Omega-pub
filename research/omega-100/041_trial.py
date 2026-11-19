"""Compare exact scanning, neural selection and exact checking of proposals."""
import importlib
import json
import statistics
import sys
import time
from hashlib import sha256
from pathlib import Path

pilot = importlib.import_module("040_selector_trial")


def oracle(card):
    start, steps = card["query"]
    value = start
    for _ in range(steps):
        value = card["transitions"][value]
    return {i for i, claim in enumerate(card["claims"], 1) if claim == [start, steps, value]}


def exact(card, indices):
    start, steps = card["query"]
    value = pilot.apply_power(card["transitions"], start, steps)
    return {i for i in indices if card["claims"][i - 1] == [start, steps, value]}


def timed(cards, choices):
    samples = []
    for _ in range(500):
        start = time.perf_counter_ns()
        result = [exact(card, indices) for card, indices in zip(cards, choices, strict=True)]
        samples.append(time.perf_counter_ns() - start)
    return result, statistics.median(samples)


def run(cards, with_model):
    all_indices = [range(1, len(card["claims"]) + 1) for card in cards]
    expected = [oracle(card) for card in cards]
    assert len(cards) == 8 and sum(not e for e in expected) == 2
    full, full_ns = timed(cards, all_indices)
    assert full == expected
    metrics = {}

    def record(name, outputs, statuses):
        rows = [pilot.score(selected, truth, status, len(card["claims"]))
                for card, selected, truth, status in zip(cards, outputs, expected, statuses, strict=True)]
        metrics[name] = {key: sum(r[key] for r in rows) for key in rows[0]}

    record("exact", full, ["selection" if chosen else "abstention" for chosen in full])
    data = {"metrics": metrics, "reference_scan_ns": full_ns, "reference_lines": sum(map(len, all_indices))}
    if with_model:
        predictions = [pilot.infer(card) for card in cards]
        chosen = [pair[0] for pair in predictions]
        reports = [pair[1] for pair in predictions]
        statuses = [r["status"] for r in reports]
        checked, checked_ns = timed(cards, chosen)
        checked_status = [
            status if status in ("format_rejection", "inference_error")
            else "selection" if output else "abstention"
            for status, output in zip(statuses, checked, strict=True)
        ]
        record("model", chosen, statuses)
        record("guarded", checked, checked_status)
        data.update(
            candidate_checks_ns=checked_ns,
            candidate_lines=sum(map(len, chosen)),
            inference_seconds=sum(report["seconds"] for report in reports),
            tokens={key: sum(r["usage"].get(key, 0) for r in reports)
                    for key in ("prompt_tokens", "completion_tokens")},
        )
    return data


if __name__ == "__main__":
    raw = Path(sys.argv[1]).read_bytes()
    result = run(json.loads(raw), "--model" in sys.argv[2:])
    print(json.dumps({"input_sha256": sha256(raw).hexdigest(), **result}, indent=2))

