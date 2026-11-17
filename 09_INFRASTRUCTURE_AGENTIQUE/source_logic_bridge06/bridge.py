#!/usr/bin/env python3
"""Omega source-logic bridge v0.1 — read-only, generic, fail-closed.

This bridge *does not* derive mathematical semantics from free-form text.
It discovers arbitrary Markdown cards, reads independently authored, unverified
interpretation rules with exact source quotes, and checks Horn consequences.
SUPPORTED means: supported by manually declared source interpretation,
under hypotheses supplied by the caller. Never a new theorem certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES_DIR = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/cross_domain_math05/source_snapshot"
RULES_PATH = HERE / "RULES_FROZEN.json"
RULES_BLOB = "34e32f63beb90e5dd0528148141b650ba8d9d848"
ID = re.compile(r"^(?:BR|OBS)-[A-Z0-9]+(?:-[A-Z0-9]+)+$")
ATOM = re.compile(r"^(?:not:)?[a-z][a-z0-9_]*$")
RULE = re.compile(r"^[a-z][a-z0-9_-]{2,80}$")


class BridgeError(ValueError):
    pass


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def safe_read(path: Path, root: Path, size_limit: int = 150000) -> bytes:
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise BridgeError("source outside controlled directory or missing: " + str(path))
    if path.stat().st_size > size_limit:
        raise BridgeError("source oversized: " + str(path))
    return path.read_bytes()


def discover(root: Path = SOURCES_DIR) -> dict[str, dict]:
    """Generic discovery by first title, never hardcoded brick IDs."""
    if not root.is_dir() or root.is_symlink():
        raise BridgeError("source directory absent or symlinked")
    result = {}
    paths = sorted(root.glob("*.md"))
    if len(paths) > 100:
        raise BridgeError("source count outside budget")
    for path in paths:
        raw = safe_read(path, root)
        text = raw.decode("utf-8")
        first = next((line for line in text.splitlines() if line.strip()), "")
        matched = re.match(r"^#\s+((?:BR|OBS)-[A-Z0-9]+(?:-[A-Z0-9]+)+)\b", first)
        if not matched:
            # Unknown Markdown formats are recognized only as inventory,
            # not silently inferred as scientific claim sources.
            continue
        identifier = matched.group(1)
        if identifier in result:
            raise BridgeError("duplicate source ID: " + identifier)
        sections = [line.lstrip("# ").strip() for line in text.splitlines()
                    if line.startswith("## ")]
        result[identifier] = {
            "id": identifier, "name": path.name,
            "path": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name,
            "blob": git_blob(raw), "title": first,
            "sections": sections, "lines": text.splitlines(),
            "historical_status_text": next(
                (line.strip() for line in text.splitlines()[:12]
                 if "Statut" in line), "non explicite"
            ),
            "epistemic_class": "DOCUMENT_CANDIDATE_UNVERIFIED",
        }
    return result


def validate_rules(raw: dict, documents: dict[str, dict]) -> dict[str, list[dict]]:
    """Reject stale, invented, nonlocal, and ambiguous source references."""
    if not isinstance(raw, dict) or not isinstance(raw.get("rules"), list):
        raise BridgeError("invalid rule manifest")
    indexed: dict[str, list[dict]] = {}
    ids = set()
    for item in raw["rules"]:
        if not isinstance(item, dict):
            raise BridgeError("rule must be object")
        rid, sid, sha = item.get("rule_id"), item.get("source_id"), item.get("source_blob")
        if not isinstance(rid, str) or not RULE.fullmatch(rid) or rid in ids:
            raise BridgeError("duplicate or invalid rule id")
        ids.add(rid)
        if not isinstance(sid, str) or not ID.fullmatch(sid) or sid not in documents:
            raise BridgeError("unknown rule source: " + str(sid))
        if sha != documents[sid]["blob"]:
            raise BridgeError("stale source blob in rule " + rid)
        if item.get("interpretation_status") != "HUMAN_TRANSCRIPTION_UNVERIFIED":
            raise BridgeError("rule must retain unverified status: " + rid)
        pre, conclusion = item.get("premises"), item.get("conclusion")
        if not isinstance(pre, list) or len(pre) > 12 or not all(
            isinstance(p, str) and ATOM.fullmatch(p) and not p.startswith("not:")
            for p in pre
        ) or len(set(pre)) != len(pre):
            raise BridgeError("bad premise schema: " + rid)
        if not pre:
            raise BridgeError("assumption-free promotion not allowed: " + rid)
        if not isinstance(conclusion, str) or not ATOM.fullmatch(conclusion):
            raise BridgeError("invalid consequence: " + rid)
        anchor = item.get("anchor")
        if not isinstance(anchor, str) or len(anchor) < 8 or len(anchor) > 200:
            raise BridgeError("missing exact source quote: " + rid)
        lines = documents[sid]["lines"]
        anchors = [i for i, line in enumerate(lines, 1) if anchor in line]
        if len(anchors) != 1:
            raise BridgeError("anchor absent or ambiguous: " + rid)
        indexed.setdefault(sid, []).append({
            "rule_id": rid, "source_id": sid, "premises": pre,
            "conclusion": conclusion, "source_blob": sha,
            "source_file": documents[sid]["path"],
            "line": anchors[0], "excerpt": lines[anchors[0]-1].strip(),
            "interpretation_status": "HUMAN_TRANSCRIPTION_UNVERIFIED",
        })
    return indexed


def load_bridge(source_root: Path = SOURCES_DIR, rule_path: Path = RULES_PATH,
                expected_rule_blob: str = RULES_BLOB) -> tuple[dict, dict]:
    documents = discover(source_root)
    data = rule_path.read_bytes()
    if git_blob(data) != expected_rule_blob:
        raise BridgeError("interpretation manifest changed or unpinned")
    by_source = validate_rules(json.loads(data.decode("utf-8")), documents)
    return documents, by_source


def compute_closure(facts: list[str], rules: list[dict]) -> tuple[set, dict]:
    known, proofs = set(facts), {}
    # Iterate synchronously so source order has no effect on proof depth.
    for _ in range(len(rules) + 1):
        newly = []
        for rule in sorted(rules, key=lambda r: r["rule_id"]):
            if rule["conclusion"] not in known and set(rule["premises"]) <= known:
                newly.append(rule)
        if not newly:
            return known, proofs
        for rule in newly:
            # In case of multiple witnesses choose lexicographically first.
            proofs.setdefault(rule["conclusion"], rule)
        known.update(rule["conclusion"] for rule in newly)
    raise BridgeError("closure did not converge")


def proof_chain(goal: str, facts: set, proofs: dict) -> list[dict]:
    """Only used edges, in dependency order; fact assertions never count as proof."""
    output = []
    used = set()

    def visit(atom: str):
        if atom in facts:
            return
        if atom not in proofs:
            raise BridgeError("incomplete proof trace: " + atom)
        rule = proofs[atom]
        if rule["rule_id"] in used:
            return
        for p in rule["premises"]:
            visit(p)
        used.add(rule["rule_id"])
        output.append({key: rule[key] for key in (
            "rule_id", "source_id", "premises", "conclusion", "source_blob",
            "source_file", "line", "excerpt", "interpretation_status"
        )})
    visit(goal)
    return output


def assess(query: dict, documents: dict, by_source: dict) -> dict:
    sid, goal, raw_facts = query.get("source_id"), query.get("goal"), query.get("facts")
    if not isinstance(sid, str) or not isinstance(goal, str) or not ATOM.fullmatch(goal) or goal.startswith("not:"):
        raise BridgeError("invalid query identifiers")
    if not isinstance(raw_facts, list) or len(raw_facts) > 24 or not all(
        isinstance(x, str) and ATOM.fullmatch(x) and not x.startswith("not:")
        for x in raw_facts
    ) or len(raw_facts) != len(set(raw_facts)):
        raise BridgeError("invalid query hypotheses")
    if sid not in documents:
        return {"source_id": sid, "goal": goal, "verdict": "ABSTAIN",
                "reason": "SOURCE_NOT_IN_CHECKOUT", "hypotheses": raw_facts,
                "proof": [], "missing_assumptions": []}
    if sid not in by_source:
        return {"source_id": sid, "goal": goal, "verdict": "ABSTAIN",
                "reason": "SOURCE_UNANNOTATED", "hypotheses": raw_facts,
                "proof": [], "missing_assumptions": []}

    rules = by_source[sid]  # independent source boundary; no cross-card inference
    known, proofs = compute_closure(raw_facts, rules)
    positive, negative = goal in proofs, "not:" + goal in proofs
    if positive and negative:
        return {"source_id": sid, "goal": goal, "verdict": "ABSTAIN",
                "reason": "CONFLICTING_ANNOTATED_DERIVATIONS",
                "hypotheses": raw_facts, "proof": [], "missing_assumptions": [],
                "conflicting_rule_ids": [
                    proofs[goal]["rule_id"], proofs["not:" + goal]["rule_id"]
                ]}
    if positive or negative:
        target = goal if positive else "not:" + goal
        chain = proof_chain(target, set(raw_facts), proofs)
        return {"source_id": sid, "goal": goal,
                "verdict": "SUPPORTED" if positive else "CONTRADICTED",
                "reason": "CONDITIONAL_DOCUMENTARY_DERIVATION",
                "hypotheses": raw_facts, "proof": chain, "missing_assumptions": [],
                "scientific_status": "INTERPRETATION_UNVERIFIED_NOT_A_PROOF"}

    # A missing condition is not a negation; show gaps only in applicable
    # direct rules, including already-derived intermediate propositions.
    gaps = [sorted(set(r["premises"]) - known) for r in rules
            if r["conclusion"] in (goal, "not:" + goal)]
    minimum = min(gaps, key=lambda x: (len(x), x)) if gaps else []
    return {"source_id": sid, "goal": goal, "verdict": "ABSTAIN",
            "reason": "INSUFFICIENT_ASSUMPTIONS_OR_UNREPRESENTED_RELATION",
            "hypotheses": raw_facts, "proof": [],
            "missing_assumptions": minimum}


def check_proof(query: dict, answer: dict, documents: dict, by_source: dict) -> bool:
    """An independent replay using only cited rule IDs and source lines."""
    if answer["verdict"] == "ABSTAIN":
        return not answer.get("proof")
    if answer["verdict"] not in ("SUPPORTED", "CONTRADICTED"):
        return False
    sid = query["source_id"]
    available = set(query["facts"])
    target = query["goal"] if answer["verdict"] == "SUPPORTED" else "not:" + query["goal"]
    used = set()
    for step in answer.get("proof", []):
        rules = {r["rule_id"]: r for r in by_source.get(sid, [])}
        rule = rules.get(step.get("rule_id"))
        if not rule or rule["rule_id"] in used or step != rule:
            return False
        if not set(rule["premises"]) <= available:
            return False
        document = documents[sid]
        if document["blob"] != rule["source_blob"]:
            return False
        line = rule["line"]
        if line <= 0 or line > len(document["lines"]) or document["lines"][line-1].strip() != rule["excerpt"]:
            return False
        used.add(rule["rule_id"])
        available.add(rule["conclusion"])
    return bool(used) and target in available and target not in query["facts"]


def inventory(documents: dict, by_source: dict) -> list[dict]:
    return [{
        "id": sid, "path": doc["path"], "blob": doc["blob"],
        "title": doc["title"], "historical_status_text": doc["historical_status_text"],
        "sections": doc["sections"],
        "representation": "ANCHORED_INTERPRETATION_UNVERIFIED" if sid in by_source
                          else "DISCOVERED_DOCUMENT_ONLY",
        "rule_count": len(by_source.get(sid, [])),
    } for sid, doc in sorted(documents.items())]


def run(queries: list[dict], source_root: Path = SOURCES_DIR,
        rule_path: Path = RULES_PATH, expected_blob: str = RULES_BLOB) -> dict:
    documents, by_source = load_bridge(source_root, rule_path, expected_blob)
    answers = []
    for query in queries:
        answer = assess(query, documents, by_source)
        answer["query_id"] = query.get("id")
        answer["certificate_valid"] = check_proof(query, answer, documents, by_source)
        if not answer["certificate_valid"]:
            raise BridgeError("invalid certificate for " + str(query.get("id")))
        answers.append(answer)
    output = {
        "engine": "OMEGA_SOURCE_LOGIC_BRIDGE_06_EXPERIMENTAL",
        "status": "DOCUMENTARY_CONDITIONAL_NOT_SCIENTIFIC_CERTIFICATION",
        "source_count": len(documents),
        "annotated_sources": len(by_source),
        "inventory": inventory(documents, by_source),
        "answers": answers,
    }
    canonical = json.dumps(output, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    output["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return output


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queries", type=Path, required=True, help="JSON {queries:[...]} in a controlled workspace")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    queries = json.loads(args.queries.read_text(encoding="utf-8"))["queries"]
    result = run(queries)
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(ROOT):
            p.error("write output outside repository")
        target.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
