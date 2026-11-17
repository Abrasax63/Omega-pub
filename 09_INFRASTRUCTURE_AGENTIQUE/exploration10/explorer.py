#!/usr/bin/env python3
"""Omega Exploration 10: generate/diversify/audit scientific HYPOTHESES.

This module is deliberately NOT a scientific prover or a language model.
It records source-anchored interpretations and proposed falsification tests.
A real prover may later be plugged into the proof lane, but heuristics can
never be auto-promoted to scientific results.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[1]
FROZEN = HERE / "FOLIO_VALIDATION_ROWS31_60.jsonl"
FROZEN_BLOB = "ee571c2aace48bd3bb73b82ce2387ba120d24e4a"
UPSTREAM_BLOB = "06244bd10b37eac73cba7aca6c336e96011ace58"
FROZEN_TRANSLATOR_BLOB = "385aca9258d69c4545df891a31f1c4ae719a82b8"
TRANSLATOR_FILE = BASE / "natural_query08" / "translator.py"

spec = importlib.util.spec_from_file_location("omega_natural_query08_frozen", TRANSLATOR_FILE)
if not spec or not spec.loader:
    raise RuntimeError("unavailable frozen translator")
strict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strict)

STOPWORDS = frozenset(("a","an","the","is","are","of","in","on","to","and","or",
    "be","for","with","if","then","who","that","they","their","as","all",
    "some","there","has","have","can","not","does","do","were","was","it",
    "person","people","someone","anyone","from","by","at","either","both",
    "only","each","every","this","these","those","because","therefore"))
LABELS = {"True": "SUPPORTED", "False": "CONTRADICTED", "Uncertain": "ABSTAIN"}
BUDGET = 4


class EvidenceError(ValueError):
    pass


def gitblob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def sha_json(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
             separators=(",", ":")).encode("utf-8")).hexdigest()


def load_sample() -> list[dict]:
    if not FROZEN.is_file() or FROZEN.is_symlink():
        raise EvidenceError("missing pinned external sample")
    if gitblob(FROZEN.read_bytes()) != FROZEN_BLOB:
        raise EvidenceError("external FOLIO sample changed")
    if gitblob(TRANSLATOR_FILE.read_bytes()) != FROZEN_TRANSLATOR_BLOB:
        raise EvidenceError("frozen Omega translator changed")
    lines = FROZEN.read_text(encoding="utf-8").splitlines()
    if len(lines) != 30:
        raise EvidenceError("sample length changed")
    data = [json.loads(s) for s in lines]
    for row in data:
        if (not isinstance(row.get("premises"), list) or not row["premises"] or
            any(not isinstance(x, str) for x in row["premises"]) or
            not isinstance(row.get("conclusion"), str) or
            row.get("label") not in LABELS):
            raise EvidenceError("invalid benchmark row")
    return data


def key_terms(text: str) -> set[str]:
    return {s for s in re.findall(r"[a-z]+", text.lower())
            if len(s) > 2 and s not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def proposition(question: str, premises: list[str], index: int,
                perspective: str, gap: list[str], score: float) -> dict:
    source = premises[index]
    doc_source = {"premise_index": index, "exact_excerpt": source,
                  "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest()}
    choices = {
        "lexical_parallel": (
            "Vérifier si la relation mentionnée dans la prémisse et la conclusion est la même.",
            "Formaliser séparément la prémisse et la conclusion et chercher un contre-modèle."),
        "missing_bridge": (
            "Chercher une relation intermédiaire manquante entre la question et la prémisse.",
            "Rechercher la définition des notions absentes dans une autre source indépendante."),
        "countermodel_challenge": (
            "Tester la possibilité d'un contre-modèle plutôt que supposer l'implication.",
            "Construire une interprétation où la prémisse est vraie et la conclusion fausse."),
        "negation_check": (
            "Examiner la portée exacte d'une négation, sans en inverser la direction.",
            "Formaliser la portée du quantificateur et tester les deux polarités.")
    }
    hypothesis, test = choices[perspective]
    return {
        "candidate_id": sha_json({"q": question, "index": index,
                                   "perspective": perspective})[:20],
        "perspective": perspective,
        "hypothesis_to_investigate": hypothesis,
        "question": question,
        "source": doc_source,
        "gap_terms": gap[:8], "heuristic_overlap": round(score, 4),
        "discriminating_test": test,
        "test_status": "NOT_EXECUTED",
        "scientific_status": "HYPOTHESIS_UNVERIFIED",
        "semantic_support": "UNDETERMINED",
        "certified": False,
    }


def propose(question: str, premises: list[str], max_candidates=BUDGET) -> list[dict]:
    """Divergent, bounded proposal ensemble; candidates are *not* conclusions."""
    if not 1 <= max_candidates <= 12:
        raise EvidenceError("invalid exploration budget")
    if not isinstance(question, str) or not isinstance(premises, list) or not premises:
        raise EvidenceError("invalid inputs")
    tokens = key_terms(question)
    ranked = sorted(
        ((jaccard(tokens, key_terms(p)), i, p) for i,p in enumerate(premises)),
        key=lambda item: (-item[0], item[1])
    )
    top_score, best_i, best = ranked[0]
    gap = sorted(tokens - set().union(*(key_terms(p) for p in premises)))
    candidates = [
        proposition(question, premises, best_i, "lexical_parallel", gap, top_score),
        proposition(question, premises, best_i, "countermodel_challenge", gap, top_score)
    ]
    if gap:
        candidates.append(proposition(
            question, premises, best_i, "missing_bridge", gap, top_score))
    else:
        secondary_i = ranked[1][1] if len(ranked) > 1 else best_i
        candidates.append(proposition(question, premises, secondary_i,
                                       "missing_bridge", [], ranked[min(1, len(ranked)-1)][0]))
    negated = [(score,i) for score,i,p in ranked
               if re.search(r"\b(?:not|no|neither|never)\b", p, flags=re.IGNORECASE)]
    if negated:
        score,i = negated[0]
        candidates.append(proposition(question, premises, i, "negation_check", gap, score))
    # Preserve independently motivated diversity, no duplicate candidate IDs.
    unique = []
    seen = set()
    for candidate in candidates:
        if candidate["candidate_id"] not in seen:
            seen.add(candidate["candidate_id"])
            unique.append(candidate)
    return unique[:max_candidates]


def critique(candidate: dict, premises: list[str], question: str) -> dict:
    """Independent structural sceptic. It cannot certify semantic relevance."""
    src = candidate.get("source", {})
    i = src.get("premise_index")
    problems=[]
    if type(i) is not int or i < 0 or i >= len(premises):
        problems.append("UNRESOLVED_SOURCE_INDEX")
    elif src.get("exact_excerpt") != premises[i]:
        problems.append("FORGED_OR_MISQUOTED_EXCERPT")
    elif src.get("source_sha256") != hashlib.sha256(premises[i].encode()).hexdigest():
        problems.append("SOURCE_HASH_MISMATCH")
    if candidate.get("question") != question:
        problems.append("QUESTION_CHANGED")
    if candidate.get("scientific_status") != "HYPOTHESIS_UNVERIFIED":
        problems.append("ILLEGAL_STATUS_PROMOTION")
    if candidate.get("certified") is not False:
        problems.append("UNSUPPORTED_CERTIFICATION")
    if candidate.get("test_status") != "NOT_EXECUTED":
        problems.append("UNEXECUTED_TEST_CLAIMED_AS_DONE")
    if not candidate.get("discriminating_test"):
        problems.append("NO_FALSIFIABLE_NEXT_TEST")
    return {
        "accepted_as_hypothesis": len(problems)==0,
        "provenance_integrity": len(problems)==0,
        "errors": problems,
        "semantic_truth_verified": False,
        "scientific_status": "UNDETERMINED" if not problems else "REJECTED_PROVENANCE",
    }


def view_case(question, premises, docs=None, case_id="query"):
    """Single case; source content is data, never instructions."""
    t0=time.perf_counter()
    if docs is None:
        docs = {}
    strict_result = strict.answer_text(question, documents=docs, case_id=case_id)
    raw = propose(question, premises)
    vetted = []
    for candidate in raw:
        review = critique(candidate, premises, question)
        vetted.append({**candidate, "review": review,
                       "source_document_sha256": sha_json(premises)})
    return {
        "id":case_id,
        "question_sha256":hashlib.sha256(question.encode()).hexdigest(),
        "premises_sha256":sha_json(premises),
        "strict_verdict":strict_result["verdict"],
        "strict_translation_status":strict_result["translation_status"],
        "strict_reason":strict_result.get("reason"),
        "hypotheses":vetted,
        "hypotheses_proposed":len(vetted),
        "hypotheses_provenance_valid":sum(x["review"]["accepted_as_hypothesis"] for x in vetted),
        "independent_semantic_tests_executed":0,
        "certified_hypotheses":0,
        "final_scientific_verdict":strict_result["verdict"],
        "new_scientific_answer_from_exploration":False,
        "elapsed_ms":round((time.perf_counter()-t0)*1000,3),
    }


def evaluate_external():
    rows=load_sample()
    start=time.perf_counter()
    unscored=[]
    with tempfile.TemporaryDirectory(prefix="omega-explore10-") as tmp:
        for i,item in enumerate(rows,31):
            case_dir=Path(tmp)/("case-"+str(i))
            case_dir.mkdir()
            case_file=case_dir/("BR-EXT-EXPL-"+str(i)+".md")
            content="# BR-EXT-EXPL-"+str(i)+" — FOLIO unverified evidence\n"
            content+="\n".join(item["premises"])+"\n"
            case_file.write_text(content,encoding="utf-8")
            documents=strict.logic.discover((case_dir,))
            if len(documents)!=1 or list(documents.values())[0]["lines"][1:]!=item["premises"]:
                raise EvidenceError("premises transport changed")
            unscored.append(view_case(item["conclusion"],item["premises"],
                                      documents,case_id="FOLIO-"+str(i)))
    frozen_decisions=sha_json([
        {"id":x["id"],"verdict":x["final_scientific_verdict"],
         "candidates":[c["candidate_id"] for c in x["hypotheses"]]}
        for x in unscored])
    print("PREDICTIONS_AND_HYPOTHESES_BEFORE_GOLD_SHA256="+frozen_decisions,flush=True)
    # Evaluate final scientific outputs only AFTER all proposals are frozen.
    for row,item in zip(unscored,rows):
        row["gold_label"]=item["label"]
        row["reference_verdict"]=LABELS[item["label"]]
        row["scientific_verdict_correct"] = row["final_scientific_verdict"]==LABELS[item["label"]]
    conf=sum(x["final_scientific_verdict"]!="ABSTAIN" for x in unscored)
    baseline=sum(x["reference_verdict"]=="ABSTAIN" for x in unscored)
    valid=sum(x["hypotheses_provenance_valid"] for x in unscored)
    count=sum(x["hypotheses_proposed"] for x in unscored)
    return {
        "experiment":"OMEGA-EXPLORATION-10",
        "status":"EXPLORATION_ONLY_NO_TRANSFER_PROVEN" if conf==0 else
                 "EXPLORATION_WITH_SCIENTIFIC_OUTPUT_REQUIRES_REVIEW",
        "external_upstream":"Yale-LILY/FOLIO 5d7bb84c validation lines 31-60",
        "sample_git_blob":FROZEN_BLOB,
        "upstream_file_git_blob":UPSTREAM_BLOB,
        "translator_git_blob":FROZEN_TRANSLATOR_BLOB,
        "sample_cases":len(unscored),
        "distinct_theories":len(set(sha_json(r["premises"]) for r in rows)),
        "baseline_always_abstain_correct":baseline,
        "scientific_answers":conf,
        "scientific_correct":sum(x["scientific_verdict_correct"] for x in unscored),
        "scientific_false_confident":sum(x["final_scientific_verdict"]!="ABSTAIN" and
                                        not x["scientific_verdict_correct"] for x in unscored),
        "hypotheses_proposed":count,
        "hypotheses_provenance_valid":valid,
        "different_perspectives":dict(Counter(
            c["perspective"] for x in unscored for c in x["hypotheses"])),
        "independent_semantic_tests_executed":0,
        "scientific_hypotheses_certified":0,
        "no_automatic_promotion":True,
        "model_calls":0,
        "predictions_and_hypotheses_sha256_before_gold":frozen_decisions,
        "elapsed_seconds":round(time.perf_counter()-start,3),
        "limitations":[
            "Lexical/structural hypotheses only, not true natural language understanding",
            "Proposed falsification tests are NOT executed, so no true scientific discovery is claimed",
            "Only external rows 31-60; labels from published FOLIO v0.0 are not audited proof",
            "No LLM called and no learning or weight updates",
            "No integration into the hourly autonomous loop or web chat",
        ],
        "rows":unscored
    }


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output",type=Path)
    args=cli.parse_args()
    result=evaluate_external()
    payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        p=args.output.resolve()
        if p.is_relative_to(ROOT):
            cli.error("reports must remain outside checkout")
        p.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")


if __name__=="__main__":
    main()
