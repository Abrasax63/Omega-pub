#!/usr/bin/env python3
"""OMEGA-NATURAL-QUERY-08: conservative French text -> typed query -> cited verifier.

This is a *bounded grammar bridge*, not unrestricted language understanding.
No model API, weights, network or per-source executable dispatch.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import time
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[1]
CATALOG = HERE / "SOURCE_CATALOG_FROZEN.json"
COHORT = HERE / "CASES_FROZEN.json"

spec = importlib.util.spec_from_file_location(
    "omega_source_to_proof_07", BASE / "source_to_proof07" / "pipeline.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("source-to-proof07 dependency missing")
logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic)

ATOM = r"[a-z][a-z0-9_]*"
BACKTICK = chr(96)
QUOTED = re.escape(BACKTICK) + ATOM + re.escape(BACKTICK)
HORN_FORMS = [
    ("HORN_SACHANT", re.compile(
        r"^Sachant (?P<facts>.+?), peut-on déduire (?P<goal>" + QUOTED + r") \?$")),
    ("HORN_AVEC_ETABLIR", re.compile(
        r"^Avec (?P<facts>.+?), peut-on établir (?P<goal>" + QUOTED + r") \?$")),
    ("HORN_AVEC_DEDUIRE", re.compile(
        r"^Avec (?P<facts>.+?), peut-on déduire (?P<goal>" + QUOTED + r") \?$")),
    ("HORN_AVEC_EVALUER", re.compile(
        r"^Avec (?P<facts>.+?), est-ce que (?P<goal>" + QUOTED + r") est démontrable \?$")),
    ("HORN_SACHANT_VRAIS", re.compile(
        r"^Sachant que (?P<facts>.+?) sont vrais, peut-on en déduire (?P<goal>" + QUOTED + r") \?$")),
    ("HORN_ACQUIS", re.compile(
        r"^Si (?P<facts>.+?) sont acquis, est-ce que (?P<goal>" + QUOTED + r") suit \?$")),
]
CAPACITY_FORM = re.compile(
    r"^(?:Nous avons|On dispose de) (?P<inventory>.+?)"
    r" ; (?P<scope>.+?)\. (?P<request>.+?) \?$"
)
INDEPENDENCE = frozenset((
    "chacun est sélectionnable indépendamment",
    "chaque témoin est sélectionnable indépendamment",
))
CAPACITY_QUESTION = re.compile(
    r"^(?:Peut-on choisir|Est-il possible de choisir) (?P<counts>.+)$"
)
INVENTORY_ITEM = re.compile(r"^(?P<count>[0-9]+) (?P<unit>témoin|témoins) (?P<motif>[A-Z])$")
REQUEST_ITEM = re.compile(r"^(?P<count>[0-9]+) (?P<motif>[A-Z])$")
VALID = frozenset(("SUPPORTED", "CONTRADICTED", "ABSTAIN"))


class TranslationError(ValueError):
    pass


def json_sha(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def load_catalog(path=CATALOG, roots=None):
    """Require a pinned source manifest; new IDs work by adding DATA, not CODE."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != "source_catalog08-v1" or not isinstance(data.get("sources"), list):
        raise TranslationError("invalid source catalog version")
    documents = logic.discover(roots if roots is not None
                               else (logic.SOURCES, HERE))
    selected = {}
    for entry in data["sources"]:
        if not isinstance(entry, dict):
            raise TranslationError("bad source manifest entry")
        sid, expected_blob, relative = (
            entry.get("source_id"), entry.get("source_blob"), entry.get("source_path")
        )
        if not all(isinstance(v, str) and v for v in (sid, expected_blob, relative)):
            raise TranslationError("incomplete source record")
        if not re.fullmatch(r"[0-9a-f]{40}", expected_blob):
            raise TranslationError("invalid expected blob SHA")
        if relative.startswith("/") or "\\" in relative or ".." in Path(relative).parts:
            raise TranslationError("unsafe catalog path")
        doc = documents.get(sid)
        if doc is None:
            raise TranslationError("source absent from repository: " + sid)
        if doc["blob"] != expected_blob:
            raise TranslationError("source blob mismatch: " + sid)
        if doc["path"] != (BASE.name + "/" + relative):
            raise TranslationError("source ID / path mismatch: " + sid)
        if sid in selected:
            raise TranslationError("duplicate source ID in catalog")
        selected[sid] = doc
    if not selected:
        raise TranslationError("no permitted scientific sources")
    return selected


def parse_atoms(fragment):
    """Never infer unstated atoms, synonyms or implicit hypotheses."""
    fragment = fragment.removesuffix(" seulement")
    fragment = re.sub(r" et ", ", ", fragment)
    chunks = fragment.split(", ")
    values = []
    for chunk in chunks:
        if not re.fullmatch(QUOTED, chunk):
            return None
        value = chunk[1:-1]
        if value in values:
            return None
        values.append(value)
    return values if 0 < len(values) <= 12 else None


def parse_horn(text):
    for identifier, pattern in HORN_FORMS:
        match = pattern.fullmatch(text)
        if match:
            facts = parse_atoms(match.group("facts"))
            if facts is None:
                return None
            return {
                "kind": "horn", "facts": facts,
                "goal": match.group("goal")[1:-1],
                "grammar": identifier,
                "fragments": {
                    "facts": match.group("facts"),
                    "goal": match.group("goal"),
                },
            }
    return None


def parse_items(value, item_pattern, inventory=False):
    chunks = value.split(" et ")
    if not 1 <= len(chunks) <= 6:
        return None
    result = {}
    for part in chunks:
        match = item_pattern.fullmatch(part)
        if not match:
            return None
        count = int(match.group("count"))
        motif = match.group("motif")
        if count > 12 or motif in result:
            return None
        if inventory:
            if (count == 1 and match.group("unit") != "témoin") or (
                count != 1 and match.group("unit") != "témoins"
            ):
                return None
        result[motif] = count
    return result


def parse_capacity(text):
    m = CAPACITY_FORM.fullmatch(text)
    if not m:
        return None
    if m.group("scope") not in INDEPENDENCE:
        return None
    request = CAPACITY_QUESTION.fullmatch(m.group("request"))
    if request is None:
        return None
    available = parse_items(m.group("inventory"), INVENTORY_ITEM, inventory=True)
    desired = parse_items(request.group("counts"), REQUEST_ITEM)
    if available is None or desired is None or sum(available.values()) > 12:
        return None
    witnesses = [motif for motif, count in available.items() for _ in range(count)]
    return {
        "kind": "capacity", "independent_selection": True,
        "witness_motifs": witnesses, "requested": desired,
        "grammar": "CAPACITY_TWO_SENTENCE",
        "fragments": {
            "inventory": m.group("inventory"), "scope": m.group("scope"),
            "requested": request.group("counts"),
        },
    }


def retrieve_source(typed, documents):
    """Source selection uses source *content* and uniqueness, never an ID mapping."""
    if typed["kind"] == "horn":
        goal = typed["goal"]
        candidates = [
            doc for doc in documents.values()
            if any(rule["conclusion"] in (goal, "not:" + goal)
                   for rule in logic.extract_horn(doc))
        ]
    else:
        candidates = [
            doc for doc in documents.values() if len(logic.extract_bound(doc)) == 3
        ]
    if len(candidates) != 1:
        return None, "SOURCE_AMBIGUOUS" if candidates else "NO_APPLICABLE_SOURCE", len(candidates)
    return candidates[0], "UNIQUE_PINNED_SOURCE", 1


def answer_text(text, documents=None, case_id="query"):
    """One user string -> typed query -> original proof engine -> audited result."""
    started = time.perf_counter()
    if not isinstance(text, str):
        raise TranslationError("text must be a string")
    clean = unicodedata.normalize("NFC", text).strip()
    if len(clean) > 600 or not clean or "\n" in clean or "\r" in clean:
        raise TranslationError("input invalid or oversized")
    docs = documents if documents is not None else load_catalog()
    def refused(reason, translation_status="ABSTAIN_OUTSIDE_GRAMMAR", candidates=0):
        return {
            "id": case_id, "verdict": "ABSTAIN", "reason": reason,
            "translation_status": translation_status,
            "source_id": None, "typed_query": None,
            "certificate_valid": True, "source_candidates": candidates,
            "input_sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest(),
            "source_documents_scanned": len(docs),
            "input_chars": len(clean), "elapsed_ms": round(1000*(time.perf_counter()-started), 3),
            "scientific_status": "NO_CLAIM",
        }

    candidates = [c for c in (parse_horn(clean), parse_capacity(clean)) if c is not None]
    if len(candidates) != 1:
        return refused("AMBIGUOUS_OR_UNSUPPORTED_NATURAL_LANGUAGE")
    typed = candidates[0]
    source, source_status, source_count = retrieve_source(typed, docs)
    if source is None:
        return refused(source_status, "ABSTAIN_SOURCE_SELECTION", source_count)

    query = {k: value for k, value in typed.items()
             if k not in ("grammar", "fragments")}
    query.update({"id": case_id, "source_id": source["id"],
                  "expected_source_blob": source["blob"]})
    # Independent engine evaluates only the trusted *typed* request.
    result = logic.answer(query, docs)
    if result["verdict"] not in VALID or not result["certificate_valid"]:
        return refused("PROOF_GATE_FAILED", "ABSTAIN_PROOF_GATE")
    return {
        "id": case_id, "verdict": result["verdict"],
        "reason": result.get("reason"), "source_id": source["id"],
        "source_blob": source["blob"], "source_candidates": source_count,
        "translation_status": "EXACT_GRAMMAR_TRANSLATED",
        "translation_grammar": typed["grammar"],
        "source_selection_status": source_status,
        "typed_query": query, "input_fragments": typed["fragments"],
        "proof_result": result,
        "certificate_valid": True,
        "input_sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest(),
        "input_chars": len(clean), "source_documents_scanned": len(docs),
        "elapsed_ms": round(1000*(time.perf_counter()-started), 3),
        "scientific_status": "CONTROLLED_NL_TO_VERIFIED_INSTANCE_ONLY",
    }


def run_frozen(cases, documents=None):
    docs = documents if documents is not None else load_catalog()
    # A strict information barrier: do not provide a gold field to translation.
    inputs = [{"id": row["id"], "text": row["text"]} for row in cases]
    rows = [answer_text(row["text"], docs, case_id=row["id"]) for row in inputs]
    frozen_choices = [{
        "id": row["id"], "verdict": row["verdict"], "source_id": row["source_id"],
        "translation_status": row["translation_status"]
    } for row in rows]
    prediction_sha = json_sha(frozen_choices)
    for output, source_case in zip(rows, cases):
        gold = source_case["gold"]
        output["expected"] = gold
        output["matched_verdict"] = output["verdict"] == gold["verdict"]
        output["matched_source"] = output["source_id"] == gold["source_id"]
    return {
        "experiment": "OMEGA-NATURAL-QUERY-08",
        "status": "POSTHOC_H06_GRAMMAR_REPAIR_NOT_BLIND",
        "original_unchanged_run": "https://github.com/Abrasax63/Omega-pub/actions/runs/44138024001",
        "posthoc_only": True,
        "cases": len(cases),
        "decisions_sha256_before_gold": prediction_sha,
        "inputs_sha256": json_sha(inputs),
        "correct": sum(x["matched_verdict"] for x in rows),
        "source_selection_correct": sum(x["matched_source"] for x in rows),
        "answered": sum(x["verdict"] != "ABSTAIN" for x in rows),
        "translated": sum(x["typed_query"] is not None for x in rows),
        "abstained": sum(x["verdict"] == "ABSTAIN" for x in rows),
        "false_confident": sum(x["verdict"] != "ABSTAIN" and not x["matched_verdict"] for x in rows),
        "invalid_certificates": sum(not x["certificate_valid"] for x in rows),
        "all_abstain_baseline_correct": sum(x["gold"]["verdict"] == "ABSTAIN" for x in cases),
        "model_weights_changed": False, "model_api_calls": 0, "auto_promotion": False,
        "limitations": [
            "Exact French grammar and backtick identifiers, NOT general natural-language understanding",
            "Three pre-pinned sources, two synthetic and one historical with known formula",
            "20 same-author examples, not independent or blind",
            "No neural model, no semantic theorem extraction from arbitrary texts",
            "Scientific validity of historical source is not independently re-proven",
            "The source-to-proof engine #153 remains experimental, separate from main",
        ], "rows": rows,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    choice = cli.add_mutually_exclusive_group(required=True)
    choice.add_argument("--text", help="French question, grammar-gated")
    choice.add_argument("--query", type=Path, help="JSON object with text only")
    choice.add_argument("--frozen", action="store_true", help="evaluate preregistered cohort")
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    if args.frozen:
        cases = json.loads(COHORT.read_text(encoding="utf-8"))["cases"]
        report = run_frozen(cases)
    elif args.query:
        obj = json.loads(args.query.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or "gold" in obj or "expected" in obj:
            cli.error("query must be an object without gold/expected labels")
        report = answer_text(obj["text"], case_id=obj.get("id", "query"))
    else:
        report = answer_text(args.text)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        destination = args.output.resolve()
        if destination.is_relative_to(ROOT):
            cli.error("write reports outside repository")
        destination.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
