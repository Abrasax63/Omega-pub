"""Synthesize and evaluate small declarative provenance verifiers offline."""

import argparse
import json
from pathlib import Path
import shlex

UNKNOWN = "indéterminé"
OPERATIONS = {"copie", "recalcul"}


def signature(line):
    """Read a literal argv from the collector's successful process record."""
    try:
        argv = shlex.split(line)
    except ValueError:
        return None
    return tuple(argv[:2] if len(argv) > 1 and argv[1].startswith("-") else argv[:1]) or None


def classify(case, rules):
    if case.get("complete") is not True:
        return UNKNOWN
    writers = case.get("writers")
    if not isinstance(writers, list) or len(writers) != 1:
        return UNKNOWN
    writer = writers[0]
    if writer.get("exit_code") != 0 or writer.get("output") != case["output"]:
        return UNKNOWN
    return rules.get(signature(writer["command"]), UNKNOWN)


def score(cases, rules):
    predicted = [(case["expected"], classify(case, rules)) for case in cases]
    return {
        "false_confirmations": sum(got != UNKNOWN and got != want for want, got in predicted),
        "correct_confirmations": sum(got == want and got != UNKNOWN for want, got in predicted),
        "abstentions": sum(got == UNKNOWN for _, got in predicted),
    }


def synthesize(training):
    observations = {}
    for case in training:
        for writer in case.get("writers", []):
            key = signature(writer["command"])
            if key and case["expected"] in OPERATIONS:
                observations.setdefault(key, set()).add(case["expected"])
    rules = {
        key: next(iter(labels)) for key, labels in observations.items() if len(labels) == 1
    }
    # Remove any rule that yields a false confirmation on the training records.
    for case in training:
        actual = classify(case, rules)
        if actual != UNKNOWN and actual != case["expected"]:
            rules.pop(signature(case["writers"][0]["command"]))
    return rules


def evaluate(candidate, baseline, reserved):
    old = score(reserved, baseline)
    new = score(reserved, candidate)
    accepted = (
        new["false_confirmations"] == 0
        and new["correct_confirmations"] > old["correct_confirmations"]
        and all(
            classify(case, candidate) == case["expected"]
            for case in reserved
            if classify(case, baseline) == case["expected"] != UNKNOWN
        )
    )
    return {"baseline": old, "candidate": new, "recommend_for_review": accepted}


def read_program(path):
    return {tuple(rule["argv_prefix"]): rule["verdict"] for rule in load(path)}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    build = modes.add_parser("build")
    build.add_argument("training", type=Path)
    build.add_argument("candidate", type=Path)
    check = modes.add_parser("check")
    check.add_argument("candidate", type=Path)
    check.add_argument("reserved", type=Path)
    check.add_argument("--baseline", type=Path)
    run = modes.add_parser("run")
    run.add_argument("program", type=Path)
    run.add_argument("case", type=Path)
    args = parser.parse_args()
    if args.mode == "build":
        rules = synthesize(load(args.training))
        with args.candidate.open("x", encoding="utf-8") as output:
            json.dump(
                [{"argv_prefix": key, "verdict": value} for key, value in sorted(rules.items())],
                output, ensure_ascii=False, indent=2,
            )
    elif args.mode == "check":
        baseline = read_program(args.baseline) if args.baseline else {}
        print(json.dumps(evaluate(read_program(args.candidate), baseline, load(args.reserved))))
    else:
        print(classify(load(args.case), read_program(args.program)))


if __name__ == "__main__":
    main()
