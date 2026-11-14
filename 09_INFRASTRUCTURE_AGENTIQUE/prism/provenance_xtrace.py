"""Evaluate the lab on a controlled Bash xtrace corpus."""

import re
import shlex


def copy_output(argv):
    if len(argv) == 3 and argv[0] == "cp":
        return argv[2]
    if (
        len(argv) == 5 and argv[:2] == ["install", "-m"]
        and re.fullmatch(r"[0-7]{3,4}", argv[2])
        and all(value and not value.startswith("-") for value in argv[3:])
    ):
        return argv[4]
    return None


def extract(log, output, *, recognize_install=True):
    """Read executed commands from the dedicated successful fixture step."""
    writers = []
    unparsed = False
    for line in log.splitlines():
        line = re.sub(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ", "", line)
        if not line.startswith("+ "):
            continue
        command = line[2:]
        if command.lstrip().startswith("#"):
            continue
        try:
            argv = shlex.split(command)
        except ValueError:
            # An unreadable record may conceal a second write to the output.
            unparsed = True
            continue
        if not argv:
            continue
        copy_destination = (
            copy_output(argv) if recognize_install or argv[0] != "install" else None
        )
        writes_output = copy_destination == output or (
            len(argv) == 3 and (
                argv[:2] == ["python3", "-c"] and f'Path("{output}").write_text(' in argv[2]
            )
        )
        if writes_output:
            writers.append({"command": command, "exit_code": 0, "output": output})
    # The controlled step uses errexit. Missing or multiple writes remain ambiguous.
    return {"complete": len(writers) == 1 and not unparsed, "output": output, "writers": writers}


def extract_buildkit_copy(log, output):
    """Recognize a traced cp -av backed by its verbose output and step completion."""
    failed = set()
    pending = {}
    writers = []
    output = output.removeprefix("./")
    for line in log.splitlines():
        line = re.sub(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ", "", line)
        error = re.fullmatch(r"(#\d+) ERROR:.*", line)
        if error:
            failed.add(error[1])
            continue
        done = re.fullmatch(r"(#\d+) DONE [0-9.]+s", line)
        if done:
            writer = pending.pop(done[1], None)
            if writer and not writer["reported"]:
                return {"complete": False, "output": output, "writers": [row for _, row in writers]}
            if writer:
                writers.append((done[1], {"command": writer["command"], "exit_code": 0, "output": output}))
            continue
        event = re.fullmatch(r"(#\d+) [0-9.]+ (.*)", line)
        if not event:
            continue
        step, detail = event.groups()
        if detail.startswith("+ "):
            if not detail.startswith("+ cp -av "):
                continue
            match = re.fullmatch(r"cp -av ([\w./-]+) ([\w./-]+/)", detail[2:])
            if not match:
                continue
            source, directory = (value.removeprefix("./") for value in match.groups())
            filename = source.rsplit("/", 1)[-1]
            if directory + filename != output:
                continue
            if step in pending:
                return {"complete": False, "output": output, "writers": []}
            pending[step] = {
                "command": detail[2:],
                "paths": (source, output),
                "reported": False,
            }
        elif step in pending:
            quoted_paths = re.fullmatch(r"'([\w./-]+)' -> '([\w./-]+)'", detail)
            if quoted_paths:
                observed = tuple(path.removeprefix("./") for path in quoted_paths.groups())
                if observed == pending[step]["paths"]:
                    pending[step]["reported"] = True
    return {
        "complete": len(writers) == 1 and not pending and writers[0][0] not in failed,
        "output": output,
        "writers": [writer for _, writer in writers],
    }


def fixed_verdict(case):
    if not case["complete"]:
        return "indéterminé"
    argv = shlex.split(case["writers"][0]["command"])
    if copy_output(argv) == case["output"] or (
        len(argv) == 4 and argv[:2] == ["cp", "-av"]
        and argv[3].endswith("/")
        and argv[3].removeprefix("./") + argv[2].rsplit("/", 1)[-1] == case["output"]
    ):
        return "copie"
    expression = (
        f'from pathlib import Path; Path("{case["output"]}").write_text('
        'str(sum(i*i for i in range(1,12)))+chr(10))'
    )
    return "recalcul" if argv == ["python3", "-c", expression] else "indéterminé"


def compare(build_log, reserved_log):
    from provenance_lab import classify, evaluate, synthesize

    training = [
        dict(extract(build_log, f"evidence/build-{name}.json"), expected=expected)
        for name, expected in (("a", "recalcul"), ("b", "copie"))
    ]
    reserved = [
        dict(extract(reserved_log, f"evidence/reserved-{name}.json"), expected=expected)
        for name, expected in (("a", "copie"), ("b", "recalcul"), ("c", "indéterminé"))
    ]
    digests = re.findall(r"\b([a-f0-9]{64})  evidence/(?:build|reserved)-[a-c]\.json$", build_log + "\n" + reserved_log, re.M)
    if len(digests) != 5 or len(set(digests)) != 1:
        raise ValueError("Le corpus doit contenir cinq sorties de même empreinte.")
    rules = synthesize(training)
    rows = [
        {"output": case["output"], "expected": case["expected"],
         "fixed": fixed_verdict(case), "learned": classify(case, rules)}
        for case in reserved
    ]
    return {"digest": digests[0], "rows": rows, "versus_abstention": evaluate(rules, {}, reserved)}


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_log", type=Path)
    parser.add_argument("reserved_log", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.build_log.read_text(), args.reserved_log.read_text()),
                     ensure_ascii=False, indent=2))
