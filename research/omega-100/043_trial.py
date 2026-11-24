"""Bounded lexical extension of the two complete 042 forms."""
import importlib
import json
import re
import statistics
import sys
import time
from pathlib import Path

previous = importlib.import_module("042_trial")
WORDS = {word: i for i, word in enumerate(
    ("zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix")
)}
WORDS["une"] = 1
TOKEN = r"(?:[0-9]+|" + "|".join(WORDS) + ")"
PATTERNS = tuple(
    (re.compile(pattern.replace(r"[0-9]+", TOKEN), re.IGNORECASE), groups)
    for pattern, groups in previous.PATTERNS
)


def integer(text):
    return int(text) if text.isascii() and text.isdecimal() else WORDS[text.casefold()]


def route(text):
    for pattern, groups in PATTERNS:
        match = pattern.fullmatch(text)
        if match:
            try:
                pair = [integer(match[group]) for group in groups]
            except ValueError:
                return None
            return pair if previous.valid(pair, 6) else None
    return None


def measure(parser, questions, labels):
    ns = []
    for _ in range(500):
        start = time.perf_counter_ns()
        answers = [parser(q) for q in questions]
        ns.append(time.perf_counter_ns() - start)
    return dict(correct=sum(a is not None and a == b for a, b in zip(answers, labels, strict=True)),
                false=sum(a is not None and a != b for a, b in zip(answers, labels, strict=True)),
                abstentions=sum(a is None and b is None for a, b in zip(answers, labels, strict=True)),
                missed=sum(a is None and b is not None for a, b in zip(answers, labels, strict=True)),
                median_ns=statistics.median(ns))


if __name__ == "__main__":
    questions, labels = (json.loads(Path(p).read_text()) for p in sys.argv[1:])
    results = {"reference": measure(previous.baseline, questions, labels),
               "candidate": measure(route, questions, labels)}
    assert route("Quel état obtient-on après 2 pas en partant de dix ?") is None
    assert route("Quel état obtient-on après 101 pas en partant de un ?") is None
    assert route("Quel état obtient-on après ZÉRO pas en partant de cinq ?") == [5, 0]
    assert [route(q) for q in questions[6:8]] == [previous.baseline(q) for q in questions[6:8]]
    print(json.dumps(results, indent=2))

