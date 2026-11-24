"""Measure the coverage/safety tradeoff of two bounded French route templates."""
import importlib
import json
import re
import sys
from pathlib import Path

prior = importlib.import_module("043_trial")
token = prior.TOKEN
PATTERNS = (
    (re.compile(rf"Depuis l’État ({token}), effectue ({token}) transitions?\.", re.I), (1, 2)),
    (re.compile(rf"Effectue ({token}) transitions? à partir de l’État ({token})\.", re.I), (2, 1)),
)


def route(text):
    existing = prior.route(text)
    if existing is not None:
        return existing
    for pattern, groups in PATTERNS:
        match = pattern.fullmatch(text)
        if match:
            try:
                result = [prior.integer(match[group]) for group in groups]
            except ValueError:
                return None
            return result if prior.previous.valid(result, 6) else None
    return None


if __name__ == "__main__":
    questions, labels = (json.loads(Path(f).read_text()) for f in sys.argv[1:])
    assert len(questions) == 16 and labels.count(None) == 6
    result = {"reference": prior.measure(prior.route, questions, labels),
              "candidate": prior.measure(route, questions, labels)}
    assert all(route(q) == prior.route(q) for q in questions[6:8])
    assert route(questions[-1]) is None
    print(json.dumps(result, indent=2))

