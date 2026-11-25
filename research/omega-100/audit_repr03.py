"""Rescore the public REPR03 archive without running the model or CI workflow."""
import argparse
import ast
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
from textwrap import dedent
from time import perf_counter
from zipfile import ZipFile

ARCHIVE = "42fcb4d03cb135b4a38aab407d1e09abd5e3a23846cf90e35f57c3d311220a78"
REV = "ee72e5415c002e8fc0566a191a07c0b2b708875a"
MODES = ("extract_full", "copy_row", "member_row")


def development_source(workflow):
    start = workflow.index("          import argparse,")
    end = workflow.index("\n          PY", start)
    nodes = ast.parse(dedent(workflow[start:end]))
    needed = {"dump", "sha", "canonical", "oracle", "fixture"}
    imports = [node for node in nodes.body if isinstance(node, ast.Import)]
    generator = [node for node in nodes.body if isinstance(node, ast.FunctionDef) and node.name in needed]
    scope = {"NPAIRS": 32}
    exec(compile(ast.Module(body=imports + generator, type_ignores=[]), "public fixture", "exec"), scope)
    return scope["fixture"](20261124)


def prompt(packet, mode, outgoing):
    source, target = packet["query"]
    if mode == "member_row":
        data = {"target": target, "list": outgoing}
        prefix = "Is target in the list? Answer exactly Yes or No. "
    else:
        edges = [tuple(edge) for edge in packet["edges"]]
        all_rows = {node: sorted(b for a, b in edges if a == node) for node in packet["nodes"]}
        data = {"source": source, "outgoing": all_rows if mode == "extract_full" else {source: outgoing}}
        prefix = "Find the outgoing list for source. Copy exactly that list as a JSON array of node names. Output only the array. "
    return prefix + json.dumps(data, sort_keys=True, separators=(",", ":"))


def key(packet):
    edges = set(map(tuple, packet["edges"]))
    return min(tuple((a, b) in edges for a in order for b in order)
               for order in permutations(packet["nodes"]))


def verify(rows, records):
    by_id = {row["id"]: row for row in rows}
    assert len(by_id) == len({key(row["packet"]) for row in rows}) == 64
    groups = defaultdict(list)
    for row in rows:
        groups[row["pair"]].append(row)
    assert len(groups) == 32
    for pair in groups.values():
        before, after = sorted(pair, key=lambda row: row["gold"])
        p, q = before["packet"], after["packet"]
        edges = set(map(tuple, p["edges"]))
        assert p["query"] == q["query"] and p["nodes"] == q["nodes"]
        assert set(map(tuple, q["edges"])) == edges | {tuple(p["query"])}
        assert tuple(p["query"]) not in edges

    stats = {mode: Counter() for mode in MODES}
    hits = {mode: {} for mode in MODES}
    exact = {mode: {} for mode in MODES if mode != "member_row"}
    for rec in records:
        mode, rid, raw = rec["mode"], rec["id"], rec["raw"]
        assert rid not in hits[mode] and rec["revision"] == REV
        packet = by_id[rid]["packet"]
        a, target = packet["query"]
        outgoing = sorted(y for x, y in packet["edges"] if x == a)
        gold = target in outgoing
        assert gold == by_id[rid]["gold"]
        assert sha256(prompt(packet, mode, outgoing).encode()).hexdigest() == rec["prompt_sha256"]
        limit = 8 if mode == "member_row" else 32
        assert 0 < rec["input_tokens"] <= 352 and 0 <= rec["output_tokens"] <= limit
        stats[mode].update({"input_tokens": rec["input_tokens"], "output_tokens": rec["output_tokens"]})
        if mode == "member_row":
            pred = {"Yes": True, "No": False}.get(raw)
        else:
            try:
                parsed = json.loads(raw)
            except ValueError:
                parsed = None
            valid = isinstance(parsed, list) and all(type(x) is str and x in packet["nodes"] for x in parsed)
            valid = valid and len(parsed) == len(set(parsed))
            pred = target in parsed if valid else None
            exact[mode][rid] = valid and set(parsed) == set(outgoing)
        hit = pred == gold
        hits[mode][rid] = hit
        stats[mode].update({"valid": int(pred is not None), "correct": int(hit),
                            "yes_correct": int(gold and hit), "no_correct": int(not gold and hit),
                            "wrong_nonabstained": int(pred is not None and not hit),
                            "abstained": int(pred is None)})
    for mode in MODES:
        assert set(hits[mode]) == set(by_id)
        stats[mode]["pairs_both_correct"] = sum(all(hits[mode][row["id"]] for row in pair)
                                                for pair in groups.values())
        if mode in exact:
            stats[mode]["exact_rows"] = sum(exact[mode].values())
            stats[mode]["exact_pairs"] = sum(all(exact[mode][row["id"]] for row in pair)
                                             for pair in groups.values())
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    start = perf_counter()
    assert sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE
    with ZipFile(args.archive) as archive:
        data = archive.read("predictions.jsonl")
        archived = json.loads(archive.read("result.json"))
    assert sha256(data).hexdigest() == archived["predictions_sha256"]
    records = [json.loads(line) for line in data.splitlines()]
    rows = development_source(args.workflow.read_text())
    scores = verify(rows, records)
    for record in (records[:-1], records + [records[0]]):
        try:
            verify(rows, record)
        except AssertionError:
            continue
        raise AssertionError("Incomplete or duplicated trace accepted")
    for mode, result in scores.items():
        assert all(archived["scores"][mode][k] == v for k, v in result.items() if not k.endswith("_tokens"))
    assert sum(result["input_tokens"] for result in scores.values()) == archived["input_tokens"]
    assert sum(result["output_tokens"] for result in scores.values()) == archived["output_tokens"]
    print(json.dumps(dict(scores=scores, generations=len(records), audit_seconds=perf_counter()-start,
                          run_seconds=archived["elapsed_seconds"], archive_sha256=ARCHIVE,
                          predictions_sha256=archived["predictions_sha256"]), indent=2))


if __name__ == "__main__":
    main()
