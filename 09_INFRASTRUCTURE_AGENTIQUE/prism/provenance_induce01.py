"""P5-INDUCE-01: synthesize a bounded build rule from earlier command records.

No shell commands are executed. This establishes reported command evidence only,
not artifact-byte identity or successful completion of each internal command.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shlex
from pathlib import Path

STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z?\s+")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ENV = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=.*$")
DANGER = {";", "&&", "||", "|", ">", ">>", "<", "<<", "&"}
FIXED = {"tool": "go", "verb": "build", "flag": "-o", "verdict": "construction_signalée"}


def parse_line(line: str) -> dict | None:
    clean = ANSI.sub("", STAMP.sub("", line).strip())
    if clean.startswith("+ "):
        clean = clean[2:]
    if not clean or clean.startswith(("#", "[command]", "Run ")):
        return None
    if any(mark in clean for mark in (chr(96), "$" + "(", "$" + "{", "\r")):
        return None
    try:
        tokens = shlex.split(clean)
    except ValueError:
        return None
    while tokens and ENV.fullmatch(tokens[0]):
        tokens.pop(0)
    if len(tokens) < 4 or any(x in DANGER for x in tokens):
        return None
    if any(mark in clean for mark in ("&&", "||", ";", "|", " > ", " < ")):
        return None
    tool, verb = tokens[:2]
    # Console reporters and text-only commands are never artifact producers.
    if tool in {"echo", "printf", "cat", "grep", "sed", "awk"}:
        return None
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,30}", tool):
        return None
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,30}", verb):
        return None
    positions = [i for i, x in enumerate(tokens) if x == "-o"]
    if len(positions) != 1 or positions[0] + 1 >= len(tokens):
        return None
    output = tokens[positions[0] + 1]
    if (not output or output.startswith("-") or output in ("/dev/null", "NUL")
        or output.endswith("/") or not re.fullmatch(r"[A-Za-z0-9_./+-]{1,240}", output)):
        return None
    return {"tool": tool, "verb": verb, "flag": "-o", "output": output}


def extract(log: str) -> list[dict]:
    if not isinstance(log, str):
        raise TypeError("log must be text")
    seen, records = set(), []
    for line in log.splitlines():
        rec = parse_line(line)
        if rec:
            key = (rec["tool"], rec["verb"], rec["flag"], rec["output"])
            if key not in seen:
                records.append(rec)
                seen.add(key)
    return records


def construct(training: list[dict]) -> dict:
    evidence = []
    for item in training:
        if item.get("expected") != "construction_signalée":
            raise ValueError("training requires annotated command evidence")
        matching = [rec for rec in extract(item["log"]) if rec["output"] == item["output"]]
        if len(matching) != 1:
            raise ValueError("training command not uniquely evidenced")
        evidence.append(matching[0])
    if not evidence:
        raise ValueError("empty training")
    signatures = {(rec["tool"], rec["verb"], rec["flag"]) for rec in evidence}
    if len(signatures) != 1:
        raise ValueError("incompatible training signatures")
    tool, verb, flag = next(iter(signatures))
    return {
        "tool": tool, "verb": verb, "flag": flag,
        "verdict": "construction_signalée",
        "training_log_sha256": sorted({
            hashlib.sha256(t["log"].encode("utf-8")).hexdigest() for t in training
        }),
        "scope": "reported-command-only",
    }


def predict(log: str, rule: dict) -> list[dict]:
    return [
        {"output": rec["output"], "verdict": rule["verdict"]}
        for rec in extract(log)
        if all(rec[k] == rule[k] for k in ("tool", "verb", "flag"))
    ]


def compare(logs: dict[str, str], candidate: dict) -> dict:
    cases = []
    for case_id, log in logs.items():
        learned = predict(log, candidate)
        fixed = predict(log, FIXED)
        cases.append({
            "case": case_id,
            "log_sha256_utf8": hashlib.sha256(log.encode("utf-8")).hexdigest(),
            "candidate": learned, "fixed": fixed,
            "agreement": learned == fixed,
        })
    return {
        "candidate_rule": candidate, "fixed_rule": FIXED, "cases": cases,
        "candidate_jobs_positive": sum(bool(c["candidate"]) for c in cases),
        "fixed_jobs_positive": sum(bool(c["fixed"]) for c in cases),
        "candidate_advantage_jobs": sum(
            bool(c["candidate"]) and not c["fixed"] for c in cases),
        "artifact_integrity_proven": False, "recommend_for_core": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("training_json", type=Path)
    p.add_argument("logdir", type=Path)
    p.add_argument("manifest_json", type=Path)
    args = p.parse_args()
    training = json.loads(args.training_json.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest_json.read_text(encoding="utf-8"))
    rule = construct(training)
    seen = {hashlib.sha256(x["log"].encode("utf-8")).hexdigest() for x in training}
    logs = {}
    for item in manifest:
        raw = (args.logdir / (item["id"] + ".log")).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != item["sha256_utf8"]:
            raise ValueError("held-out log hash mismatch: " + item["id"])
        if sha in seen:
            raise ValueError("training log reused: " + item["id"])
        logs[item["id"]] = raw.decode("utf-8")
    print(json.dumps(compare(logs, rule), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
