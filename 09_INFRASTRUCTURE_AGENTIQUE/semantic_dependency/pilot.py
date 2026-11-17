#!/usr/bin/env python3
"""Exploratory declared-dependency retrieval, NOT natural-language understanding.

Only secondary reconciliation notes at immutable, pre-registered blobs are read.
No dependency is certified by this parser. No API, LLM, or repository writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GOLD_PATH = HERE / "GOLD_2026-11-17.json"
SOURCES = {
    "01_RAVI2/RECONCILIATION_SEMANTIQUE_BRIQUES_LOT01_2026-11-09.md":
        "6e74baf2e8d81466bd952243add000dd811aa852",
    "01_RAVI2/RECONCILIATION_SEMANTIQUE_BRIQUES_LOT02_2026-11-09.md":
        "48cdc2dd07e3d68f7ba45e71b5b5336e8fde32c0",
}
SOURCE_COMMIT = "639dc01ca3ea58c61b075adb9a6d860bf41db7bc"
RCE_REF = "b42b861fee12bc4e488e7f1c66e31699fe62541e"
ID_PATTERN = re.compile(r"\b(?:BR|OBS)-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")
HEADER = re.compile(r"^###\s+\d+\.\s+\x60([^\x60]+)\x60", re.MULTILINE)
CARD_ID = re.compile(r"^\s*-\s*ID\s*:\s*\x60?((?:BR|OBS)-[A-Z0-9]+(?:-[A-Z0-9]+)+)", re.MULTILINE)
EDGE_LINE = re.compile(
    r"^\s*-\s*(?:Dépendances?\s+déclarées?|Dépendances)\s*:\s*(.+)$",
    re.IGNORECASE,
)
STOPWORDS = {
    "avec", "dans", "pour", "sans", "chez", "cela", "cette", "comme",
    "comment", "quel", "quelle", "quels", "quelles", "nous", "vous",
    "leur", "leurs", "des", "les", "une", "uns", "sur", "sous",
    "entre", "depuis", "vers", "mais", "donc", "alors", "plus",
    "moins", "etre", "avoir", "faire", "est", "sont", "qui",
    "que", "quoi", "dont", "par", "pas", "non", "oui", "the",
    "and", "for", "with", "from", "this", "that", "into",
    "are", "was", "were", "can", "how", "what",
}
ROLE_TERMS = ("lacune", "piste", "résultat", "conjecture", "littérature", "hypothèse")


def normalize(value: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(c)
    )


def rce_terms(query: str) -> list[str]:
    # Lexical tokenizer of RCE v0.1 (PR #7), limited to this public-note corpus.
    return [t for t in re.findall(r"[a-zA-ZÀ-ÿ0-9_./-]+", normalize(query))
            if len(t) > 1 and t not in STOPWORDS]


def rce_score(query_terms: list[str], content: str, relative_path: str) -> float:
    # RCE v0.1 score_document(query_terms, content, rel, role="researcher").
    haystack, path_text = normalize(content), normalize(relative_path)
    hits = {t for t in query_terms if t in haystack}
    path_hits = {t for t in query_terms if t in path_text}
    score = len(hits) + 2.0 * len(path_hits)
    role_hits = sum(1 for term in ROLE_TERMS if normalize(term) in haystack)
    score += min(role_hits, 5) * 0.35
    if "08_ARCHIVES/" in relative_path:
        score *= 0.55
    return score


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_source(root: Path, rel: str, blob: str) -> str:
    path = root / rel
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"source missing or symlinked: {rel}")
    data = path.read_bytes()
    found = git_blob(data)
    if found != blob:
        raise ValueError(f"source blob changed: {rel}; got {found}, expected {blob}")
    return data.decode("utf-8")


def load_cards(root: Path = ROOT) -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for rel, blob in SOURCES.items():
        text = read_source(root, rel, blob)
        headings = list(HEADER.finditer(text))
        for i, head in enumerate(headings):
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            body = text[head.end():end]
            found = CARD_ID.search(body)
            if found:
                identifier = found.group(1)
            else:
                prefix = head.group(1).split("_", 1)[0]
                identifier = prefix if ID_PATTERN.fullmatch(prefix) else ""
            if not identifier:
                continue
            if identifier in cards:
                raise ValueError(f"duplicate ID in source: {identifier}")
            lineno = text.count("\n", 0, head.start()) + 1
            cards[identifier] = {
                "id": identifier,
                "source_file": rel,
                "source_blob": blob,
                "heading_line": lineno,
                "text": body,
                "heading_text": head.group(1),
                "body_start_line": text.count("\n", 0, head.end()) + 1,
            }
    return cards


def typed_dependencies(card: dict, max_results: int = 3) -> list[dict]:
    """Only outbound declared IDs. Unnamed and ambiguous dependencies abstain."""
    edges: list[dict] = []
    for offset, line in enumerate(card["text"].splitlines()):
        found = EDGE_LINE.match(line)
        if not found:
            continue
        payload = found.group(1)
        norm = normalize(payload)
        if any(phrase in norm for phrase in (
            "aucune", "aucun", "pas de dependance", "n'enonce pas",
            "pas de graphe", "sans dependance", "non declaree",
        )):
            continue
        if any(phrase in norm for phrase in (
            "conceptuel", "illustre", "sans dependance logique",
            "simple analogie",
        )):
            continue
        for target in ID_PATTERN.findall(payload):
            if target == card["id"] or any(x["target"] == target for x in edges):
                continue
            edges.append({
                "target": target,
                "relation": "declared_dependency_unverified",
                "source_file": card["source_file"],
                "source_blob": card["source_blob"],
                "line": card["body_start_line"] + offset,
                "source_commit": SOURCE_COMMIT,
                "resolution": "mentioned_in_secondary_report_only",
            })
    return edges[:max_results]


def lexical_candidates(cards: dict, owner: str, k: int = 3) -> list[str]:
    """Rank other card sections, using RCE v0.1 lexical score. Not an edge."""
    query = f"dépendances de {owner}"
    query_terms = rce_terms(query)
    ranked = [
        (rce_score(query_terms, card["text"], card["source_file"]), identifier)
        for identifier, card in cards.items() if identifier != owner
    ]
    ranked.sort(key=lambda p: (-p[0], p[1]))
    return [identifier for score, identifier in ranked if score > 0][:k]


def metrics(tp: int, fp: int, fn: int) -> dict:
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": (tp / (tp + fp)) if tp + fp else None,
        "recall": (tp / (tp + fn)) if tp + fn else None,
    }


def evaluate(root: Path = ROOT) -> dict:
    cards = load_cards(root)
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    cases = gold["cases"]
    if len(cases) != 14 or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("frozen case count or uniqueness was changed")
    missing = [c["id"] for c in cases if c["id"] not in cards]
    if missing:
        raise ValueError(f"gold IDs not present in source: {missing}")
    counts = {"lex": [0, 0, 0], "typed": [0, 0, 0]}
    rows = []
    for case in cases:
        owner = case["id"]
        expected = set(case["formal"])
        conceptual = set(case["conceptual"])
        lex = lexical_candidates(cards, owner)
        typed_edges = typed_dependencies(cards[owner])
        typed = [e["target"] for e in typed_edges]
        for name, proposals in (("lex", lex), ("typed", typed)):
            proposals_set = set(proposals)
            counts[name][0] += len(proposals_set & expected)
            counts[name][1] += len(proposals_set - expected)
            counts[name][2] += len(expected - proposals_set)
        rows.append({
            "id": owner,
            "expected_formal_from_secondary_notes": sorted(expected),
            "conceptual_not_formal": sorted(conceptual),
            "lexical_candidates_not_assertions": lex,
            "typed_declared_dependencies": typed_edges,
            "lexical_conceptual_confusions": sorted(set(lex) & conceptual),
            "typed_conceptual_confusions": sorted(set(typed) & conceptual),
        })
    lex = metrics(*counts["lex"])
    typed = metrics(*counts["typed"])
    typed_confusions = sum(len(r["typed_conceptual_confusions"]) for r in rows)
    success = (typed["recall"] is not None and lex["recall"] is not None
               and typed["recall"] > lex["recall"]
               and typed["fp"] <= lex["fp"]
               and typed_confusions == 0)
    return {
        "status": "EXPLORATORY_NONBLIND_SECONDARY_ANNOTATIONS",
        "source_commit": SOURCE_COMMIT,
        "lexical_reference_rce_commit": RCE_REF,
        "frozen_gold_version": gold["version"],
        "source_blobs": SOURCES,
        "card_sections_available": len(cards),
        "case_count": len(cases),
        "retrieval_budget_each_method": 3,
        "metrics": {"lex": lex, "typed": typed},
        "pre_registered_local_criterion_met": success,
        "interpretation_limit": (
            "Graph edges express secondary-report declarations, not verified "
            "mathematical entailment; nonblind small corpus, lexical retrieval "
            "is only a candidate ranking; no general semantic ability established."
        ),
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="JSON report outside repository")
    args = parser.parse_args()
    root = args.repo.resolve()
    report = evaluate(root)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output.resolve()
        if target.is_relative_to(root):
            parser.error("output must not overwrite files inside repository")
        target.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
