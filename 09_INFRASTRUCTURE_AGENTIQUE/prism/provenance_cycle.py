"""Select one provenance failure to investigate and evaluate a candidate separately."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shlex

from provenance_lab import OPERATIONS, UNKNOWN, classify, load, read_program, signature, synthesize


def fingerprint(case):
    observation = {key: value for key, value in case.items() if key != "expected"}
    return sha256(json.dumps(observation, sort_keys=True).encode()).hexdigest()


def module_signature(command):
    argv = shlex.split(command)
    if len(argv) >= 3 and argv[1] == "-m" and not argv[2].startswith("-"):
        return tuple(argv[:3])
    return None


def propose(training, baseline):
    failures = Counter()
    for case in training:
        actual = classify(case, baseline)
        if actual == case["expected"] or not case.get("complete"):
            continue
        writers = case.get("writers", [])
        if len(writers) != 1:
            continue
        writer = writers[0]
        if writer["exit_code"] != 0 or writer["output"] != case["output"]:
            continue
        key = signature(writer["command"])
        if key:
            failures[key, actual != UNKNOWN] += 1

    counts = Counter()
    for (key, false_confirmation), count in failures.items():
        counts[key] += count * (2 if false_confirmation else 1)

    target = min(counts, key=lambda key: (-counts[key], key)) if counts else None
    patch = {}
    if target:
        if target in baseline:
            # A collided prefix can be narrowed when the command selects a module.
            labels = {}
            for case in training:
                for writer in case.get("writers", []):
                    command = writer["command"]
                    if signature(command) != target or classify(case, baseline) == UNKNOWN:
                        continue
                    module = module_signature(command)
                    if module:
                        labels.setdefault(module, set()).add(case["expected"])
            patch = {key: next(iter(values)) for key, values in labels.items()
                     if len(values) == 1 and values <= OPERATIONS}
        else:
            learned = synthesize(training)
            if target in learned:
                patch = {target: learned[target]}
    return {
        "target": target,
        "failure_counts": [
            {"prefix": key, "false_confirmations": failures[key, True],
             "missed_confirmations": failures[key, False]}
            for key in sorted(counts)
        ],
        "rules": [{"argv_prefix": key, "verdict": label} for key, label in sorted(patch.items())],
        "training_fingerprints": sorted({fingerprint(case) for case in training}),
        "baseline_fingerprint": program_fingerprint(baseline),
    }


def program_fingerprint(rules):
    return sha256(json.dumps(sorted(rules.items())).encode()).hexdigest()


def predict(case, baseline, proposal):
    target = proposal["target"]
    if target is None:
        return classify(case, baseline)
    rules = {tuple(rule["argv_prefix"]): rule["verdict"] for rule in proposal["rules"]}
    # Reuse the lab's evidence checks before inspecting the command.
    marker = classify(case, {tuple(target): "target"})
    if marker != "target":
        return classify(case, baseline)
    return rules.get(tuple(target), rules.get(module_signature(case["writers"][0]["command"]), UNKNOWN))


def metrics(expected, predictions):
    return {
        "false_confirmations": sum(got != UNKNOWN and got != want for want, got in zip(expected, predictions)),
        "correct_confirmations": sum(got == want != UNKNOWN for want, got in zip(expected, predictions)),
        "abstentions": predictions.count(UNKNOWN),
    }


def evaluate_proposal(proposal, baseline, reserved, direct=None):
    if program_fingerprint(baseline) != proposal["baseline_fingerprint"]:
        raise ValueError("Baseline differs from the one used to build the proposal.")
    if not reserved:
        raise ValueError("Reserved cases are required.")
    if set(proposal["training_fingerprints"]).intersection(map(fingerprint, reserved)):
        raise ValueError("An observation appears in both training and reserved cases.")
    expected = [case["expected"] for case in reserved]
    before = [classify(case, baseline) for case in reserved]
    after = [predict(case, baseline, proposal) for case in reserved]
    old, new = metrics(expected, before), metrics(expected, after)
    result = {
        "cases": len(reserved),
        "baseline": old,
        "candidate": new,
        "recommend_for_review": (
            proposal["target"] is not None
            and new["false_confirmations"] == 0
            and (new["correct_confirmations"] > old["correct_confirmations"]
                 or (new["correct_confirmations"] == old["correct_confirmations"]
                     and old["false_confirmations"] > 0))
            and all(got == want for want, prev, got in zip(expected, before, after)
                    if prev == want != UNKNOWN)
        ),
    }
    if direct is not None:
        if len(direct) != len(reserved) or any(label not in OPERATIONS | {UNKNOWN} for label in direct):
            raise ValueError("Provide one valid direct verdict per reserved case, in order.")
        result["direct"] = metrics(expected, direct)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    propose_parser = commands.add_parser("propose")
    propose_parser.add_argument("training", type=Path)
    propose_parser.add_argument("baseline", type=Path)
    propose_parser.add_argument("proposal", type=Path)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("proposal", type=Path)
    check_parser.add_argument("baseline", type=Path)
    check_parser.add_argument("reserved", type=Path)
    check_parser.add_argument("--direct", type=Path)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("proposal", type=Path)
    run_parser.add_argument("baseline", type=Path)
    run_parser.add_argument("observation", type=Path)
    args = parser.parse_args()
    baseline = read_program(args.baseline)
    if args.mode == "propose":
        with args.proposal.open("x", encoding="utf-8") as output:
            json.dump(propose(load(args.training), baseline), output, ensure_ascii=False, indent=2)
    elif args.mode == "run":
        proposal = load(args.proposal)
        if program_fingerprint(baseline) != proposal["baseline_fingerprint"]:
            parser.error("Baseline differs from the one used to build the proposal.")
        print(predict(load(args.observation), baseline, proposal))
    else:
        direct = load(args.direct) if args.direct else None
        result = evaluate_proposal(load(args.proposal), baseline, load(args.reserved), direct)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
