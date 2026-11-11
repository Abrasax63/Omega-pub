"""Exact replay of the two possible short-circuit orders for PR #29."""
import json
from pathlib import Path

DATA = Path(__file__).with_name("live_github_pr_gate_observations_2026-11-11.json")


def replay():
    cases = json.loads(DATA.read_text(encoding="utf-8"))["cases"]
    result = {}
    for first, second in [("merged", "touched_tests"), ("touched_tests", "merged")]:
        correct = calls = 0
        for case in cases:
            calls += 1
            verdict = False
            if case[first]:
                calls += 1
                verdict = case[second]
            correct += verdict == case["ground_truth"]
        result[first] = dict(correct=correct, calls=calls, cases=len(cases))
    return result


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
