"""Experimental offline provenance evidence recognition. No code or shell execution.

A positive signal denotes a reported operation, not artifact-byte identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

UNKNOWN = "indéterminé"
LABELS = {"recalcul", "copie"}
TIMESTAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z\s+")
LINK_STEP = re.compile(
    r"\[\d+/\d+\].*?(?:^|[;& ]|&&)(?:/usr/bin/)?(?:cc|gcc|clang)(?:\s|$).+?\s-o\s+(?P<output>\S+)"
)


def lines(log: str) -> list[str]:
    return [TIMESTAMP.sub("", s).strip() for s in log.splitlines()]


def normalize(path: str) -> str:
    return path.lstrip("./")


def fingerprints(log: str, script: str, output: str) -> dict:
    """Parse a tiny, explicit subset of build evidence. No shell execution."""
    if not isinstance(log, str) or not isinstance(script, str) or not output:
        raise ValueError("log, script and output required")
    observed = lines(log)
    target = normalize(output)
    # Anchored recipe describes a transformation, not the produced bytes.
    recipe = bool(re.search(
        r"git\s+archive\s+--format=tar\s+HEAD\s*\)\s*\|\s*gzip\s*>\s*source\.tar\.gz",
        script,
    ))
    arc_cmd = any(
        re.match(r"^\+\s+git\s+archive\s+--format=tar\s+HEAD(?:\s|$)", row)
        for row in observed
    )
    gzip_cmd = any(re.match(r"^\+\s+gzip(?:\s|$)", row) for row in observed)
    archive_hash = any(
        re.match(r"^\+{1,2}\s+sha256sum\s+", row) and row.endswith("/source.tar.gz")
        for row in observed
    )
    archive_use = any(
        "-DFROM_ARCHIVE=" in row and "source.tar.gz" in row for row in observed
    )
    # This guard detects *known* competing commands; it is NOT an exhaustive
    # guarantee of a unique writer and cannot certify provenance alone.
    conflicting_write = any(
        re.match(r"^\+\s+(?:cp|mv|install|tee|truncate|rm)(?:\s|$)", row)
        and "source.tar.gz" in row
        for row in observed
    )
    archive = (
        target == "source.tar.gz"
        and recipe and arc_cmd and gzip_cmd and archive_hash and archive_use
        and not conflicting_write
    )

    cmake_target = "add_executable(" in script or "add_executable (" in script
    link_matches = [
        normalize(m.group("output").strip("'\""))
        for row in observed
        if (m := LINK_STEP.search(row))
    ]
    link = bool(cmake_target and target == "src/curl" and target in link_matches)
    markers = sorted(
        set((["archive-pipeline"] if archive else [])
            + (["ninja-link"] if link else []))
    )
    return {
        "markers": markers,
        "archive": archive,
        "link": link,
        "link_occurrences": len(link_matches),
        "log_sha256": hashlib.sha256(log.encode()).hexdigest(),
        "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
    }


def learn(training: list[dict]) -> dict[str, str]:
    """Choose unambiguous semantic markers from prior annotated cases only."""
    seen: dict[str, set[str]] = {}
    for item in training:
        label = item["expected"]
        if label not in LABELS | {UNKNOWN}:
            raise ValueError("bad training label")
        ev = fingerprints(item["log"], item["script"], item["output"])
        for marker in ev["markers"]:
            seen.setdefault(marker, set()).add(label)
    return {
        marker: next(iter(labels))
        for marker, labels in sorted(seen.items())
        if len(labels) == 1 and next(iter(labels)) in LABELS
    }


def verify(log: str, script: str, output: str, rules: dict[str, str]) -> dict:
    f = fingerprints(log, script, output)
    found = f["markers"]
    verdicts = {rules.get(marker, UNKNOWN) for marker in found}
    answer = verdicts.pop() if len(verdicts) == 1 else UNKNOWN
    if answer not in LABELS:
        answer = UNKNOWN
    return {
        "verdict": answer,
        "features": found,
        "log_sha256": f["log_sha256"],
        "script_sha256": f["script_sha256"],
    }


def fixed(log: str, script: str, output: str) -> str:
    """Strong predeclared classic comparison, identical evidence access."""
    return verify(
        log, script, output,
        {"archive-pipeline": "recalcul", "ninja-link": "recalcul"},
    )["verdict"]


def score(data: list[dict], rules: dict[str, str]) -> dict:
    rows = []
    for item in data:
        got = verify(item["log"], item["script"], item["output"], rules)["verdict"]
        ref = fixed(item["log"], item["script"], item["output"])
        rows.append({
            "id": item["id"], "expected": item["expected"],
            "candidate": got, "fixed": ref,
        })

    def metrics(key):
        return {
            "correct": sum(
                r[key] == r["expected"] and r[key] != UNKNOWN for r in rows
            ),
            "false": sum(
                r[key] != UNKNOWN and r[key] != r["expected"] for r in rows
            ),
            "abstain": sum(r[key] == UNKNOWN for r in rows),
        }

    a, b = metrics("candidate"), metrics("fixed")
    return {
        "rows": rows,
        "candidate": a,
        "fixed": b,
        "recommend_for_review": a["false"] == 0 and a["correct"] > b["correct"],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("train", type=Path)
    p.add_argument("reserved", type=Path)
    args = p.parse_args()
    trained = json.loads(args.train.read_text(encoding="utf-8"))
    heldout = json.loads(args.reserved.read_text(encoding="utf-8"))
    train_ids = {x["id"] for x in trained}
    if train_ids & {x["id"] for x in heldout}:
        raise ValueError("reused training IDs")

    def raw_digest(x):
        return hashlib.sha256(json.dumps(
            {key: x[key] for key in ("log", "script", "output")},
            ensure_ascii=False, sort_keys=True,
        ).encode()).hexdigest()

    if {raw_digest(x) for x in trained} & {raw_digest(x) for x in heldout}:
        raise ValueError("reused observations under different IDs")
    rules = learn(trained)
    result = score(heldout, rules)
    print(json.dumps({"rules": rules, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
