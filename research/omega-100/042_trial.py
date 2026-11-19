"""Evaluate a strict regex router and a local model fallback."""
import argparse
import importlib
import json
import re
import time
import urllib.error
import urllib.request
from hashlib import sha256
from pathlib import Path

pilot = importlib.import_module("040_selector_trial")
PATTERNS = (
    (r"En partant de ([0-9]+), où arrive-t-on après ([0-9]+) étapes? \?", (1, 2)),
    (r"Quel état obtient-on après ([0-9]+) pas en partant de ([0-9]+) \?", (2, 1)),
)


def baseline(question):
    for pattern, groups in PATTERNS:
        match = re.fullmatch(pattern, question, re.IGNORECASE)
        if match:
            return [int(match[group]) for group in groups]
    return None


def valid(route, count):
    return (
        len(route) == 2
        and all(type(value) is int for value in route)
        and 0 <= route[0] < count
        and 0 <= route[1] <= 100
    )


def parse_model(reply, count):
    if reply.strip() == "NONE":
        return None, "abstention"
    match = re.fullmatch(r"([0-9]{1,3})[ \t]*,[ \t]*([0-9]{1,3})", reply.strip())
    if match:
        route = list(map(int, match.groups()))
        if valid(route, count):
            return route, "route"
    return None, "rejected"


def infer(card):
    system = (
        "Extrais l'état de départ et le nombre exact de transitions demandées. "
        "N'effectue aucun calcul d'état final. Réponds uniquement par deux entiers "
        "séparés par une virgule, dans l'ordre départ, nombre de transitions. "
        "Si un champ manque, est vague, ou admet plusieurs lectures, réponds uniquement NONE. "
        f"États autorisés : de 0 à {len(card['transition']) - 1}."
    )
    request = urllib.request.Request(
        "http://127.0.0.1:18091/v1/chat/completions",
        data=json.dumps({
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": card["request"]}],
            "temperature": 0, "seed": 42, "max_tokens": 48, "stream": False,
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    usage = {}
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.load(response)
        reply = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
        route, status = parse_model(reply, len(card["transition"]))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError):
        route, status = None, "inference_error"
    return route, status, time.perf_counter() - start, usage


def score(cards, labels, decisions):
    result = dict(correct_routes=0, false_routes=0, missed_clear=0,
                  correct_abstentions=0, rejections=0, inference_errors=0,
                  final_collisions=0)
    for card, (route, status) in zip(cards, decisions, strict=True):
        expected = labels[card["id"]]
        if route is not None:
            got = pilot.apply_power(card["transition"], *route)
            if expected is not None:
                oracle, count = expected
                for _ in range(count):
                    oracle = card["transition"][oracle]
            if route == expected:
                assert got == oracle
                result["correct_routes"] += 1
            else:
                result["false_routes"] += 1
                if expected is not None and got == oracle:
                    result["final_collisions"] += 1
        elif expected is not None:
            result["missed_clear"] += 1
        elif status == "abstention":
            result["correct_abstentions"] += 1
        result["rejections"] += status == "rejected"
        result["inference_errors"] += status == "inference_error"
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("inputs", type=Path)
    cli.add_argument("annotations", type=Path)
    cli.add_argument("--model", action="store_true")
    a = cli.parse_args()
    raw_inputs, raw_labels = a.inputs.read_bytes(), a.annotations.read_bytes()
    cards, labels = json.loads(raw_inputs), json.loads(raw_labels)
    assert len(cards) == 12 and len(labels) == 12 and list(labels.values()).count(None) == 4
    start = time.perf_counter_ns()
    reference = []
    for card in cards:
        selected = baseline(card["request"])
        assert selected is None or valid(selected, len(card["transition"]))
        reference.append((selected, "abstention" if selected is None else "route"))
    reference_ns = time.perf_counter_ns() - start
    summary = {
        "input_sha256": sha256(raw_inputs).hexdigest(),
        "annotation_sha256": sha256(raw_labels).hexdigest(),
        "reference": score(cards, labels, reference),
        "reference_ns": reference_ns,
    }
    if a.model:
        hybrid, calls = list(reference), []
        for i, (route, _) in enumerate(reference):
            if route is None:
                call = infer(cards[i])
                hybrid[i] = call[:2]
                calls.append(call)
        summary.update(
            hybrid=score(cards, labels, hybrid),
            calls=len(calls),
            client_seconds=sum(call[2] for call in calls),
            tokens={key: sum(call[3].get(key, 0) for call in calls)
                    for key in ("prompt_tokens", "completion_tokens")},
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

