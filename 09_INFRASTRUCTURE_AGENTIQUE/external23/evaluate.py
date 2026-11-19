#!/usr/bin/env python3
"""EXT23 -- reproducible out-of-distribution test of independent math wording.

The original third-party phrases are not rewritten. This audits coverage and
fail-closed semantics, NOT the truth or correctness of third-party theorems.
The 'transplanted' context is synthetic and tests only claim-language parsing,
not the meaning of the original external source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "semantic22"))
from checker import parse_predicate, verify_source, select_verified

FROZEN = HERE / "EXTERNAL_SOURCES.json"
EXPECTED_N = 12


def blob(raw: bytes) -> str:
    return hashlib.sha1(("blob " + str(len(raw)) + "\0").encode("ascii") + raw).hexdigest()


def transplant(short_original_quote: str, ident: str) -> bytes:
    """Preserve the EXTERNAL claim verbatim; inject only controlled test scaffolding.

    Never interpret the external speaker's statement *as if* it were originally
    about the synthetic Z/12Z example: its semantic context is NOT carried over.
    """
    if "\n" in short_original_quote or "\r" in short_original_quote:
        raise ValueError("MULTILINE_SOURCE_NOT_SUPPORTED_IN_TRANSPLANT")
    if not re.fullmatch(r"EX[0-9]{2}", ident):
        raise ValueError("INVALID_EXTERNAL_ID")
    return (
        f"# Fiche {ident}\n\n"
        "## Données\n\n"
        "On travaille dans Z/12Z. On définit f(x) = (3*x + 1) mod 12.\n\n"
        "## Énoncé\n\n"
        + short_original_quote + "\n"
    ).encode("utf8")


def read_frozen() -> list[dict]:
    snap = json.loads(FROZEN.read_text(encoding="utf8"))
    sources = snap["sources"]
    if (snap["status"] != "FROZEN_BEFORE_EVALUATION_CODE"
        or snap["selection"] != "NON_BLIND_CONVENIENCE_SAMPLE"
        or len(sources) != EXPECTED_N
        or len({s["id"] for s in sources}) != EXPECTED_N):
        raise ValueError("EXTERNAL_CORPUS_DRIFT")
    for s in sources:
        if (not re.fullmatch(r"EX[0-9]{2}", s["id"])
            or not s["source_url"].startswith("https://")
            or not isinstance(s["quote"], str)
            or not 8 <= len(s["quote"]) <= 512
            or "\n" in s["quote"]
            or not s["source_type"] in (
                "mathstackexchange_post",
                "mathstackexchange_answer",
                "wikipedia_fr_article"
            )):
            raise ValueError("UNSAFE_OR_MISSING_EXTERNAL_SOURCE")
    return sources


def evaluate() -> dict:
    sources = read_frozen()
    rows=[]
    for src in sources:
        quoted = src["quote"]
        raw = quoted.encode("utf8")
        hashed = blob(raw)
        # Original raw quotation, not a synthetic well-formed SEM22 file.
        raw_verdict = verify_source(
            raw, expected_blob=hashed, source_path=src["source_url"]
        )
        category, value, why = parse_predicate(quoted)
        # Separate *syntax-only* experiment with a known, in-scope definition.
        wrapper = transplant(quoted, src["id"])
        wrapper_verdict = verify_source(
            wrapper, expected_blob=blob(wrapper), source_path="fixtures/" + src["id"] + ".md"
        )
        if len(wrapper_verdict["results"]) != 1:
            raise ValueError("EXPECTED_ONE_EXACT_EXTERNAL_QUOTE_IN_WRAPPER")
        row = wrapper_verdict["results"][0]
        filtering = select_verified(wrapper_verdict, [9])
        if raw_verdict["results"] or raw_verdict["status"] != "UNSUPPORTED_SOURCE":
            raise ValueError("RAW_EXTERNAL_CLAIM_UNEXPECTEDLY_PARSED")
        if category != "UNSUPPORTED" or value is not None or why is None:
            raise ValueError("EXTERNAL_QUOTE_UNEXPECTEDLY_SUPPORTED")
        if (row["literal"] != quoted or row["verdict"] != "INDETERMINATE"
            or filtering["selected_true_lines"] or len(filtering["suppressed"]) != 1
            or wrapper_verdict["auto_promotions"] != 0
            or wrapper_verdict["theorems_certified"] != 0 or wrapper_verdict["horn_rules"]):
            raise ValueError("UNSAFE_EXTERNAL_QUOTE_PROMOTION")
        rows.append({
            "id":src["id"],
            "source_type":src["source_type"],
            "source_url":src["source_url"],
            "original_quote":quoted,
            "quote_sha256":hashlib.sha256(raw).hexdigest(),
            "category_from_preregistered_source_record":src["category"],
            "raw_document_status":raw_verdict["status"],
            "raw_document_reason":raw_verdict["reason"],
            "claim_parser_status":"UNSUPPORTED",
            "claim_parser_reason":why,
            "lexical_transplant_only_status":row["verdict"],
            "lexical_transplant_reason":row["reason"],
            "verdict_on_original_claim":"NOT_ATTEMPTED",
            "mathematical_truth_of_original_claim":"NOT_INDEPENDENTLY_ANNOTATED",
            "claim_automatically_promoted":False,
        })
    eligible_supported = sum(
        r["claim_parser_status"] == "SUPPORTED" for r in rows
    )
    n_raw_abstentions = sum(
        r["raw_document_status"] == "UNSUPPORTED_SOURCE" for r in rows
    )
    return {
        "status":"EXTERNAL_TEXT_AUDIT_COMPLETED",
        "corpus_kind":"SHORT_GENUINE_THIRD_PARTY_QUOTES_NON_BLIND_CONVENIENCE",
        "source_count":len(rows),
        "number_external_sources_with_links":sum(bool(r["source_url"]) for r in rows),
        "supported_external_claim_count":eligible_supported,
        "raw_source_abstentions":n_raw_abstentions,
        "claim_transplant_abstentions":sum(
            r["lexical_transplant_only_status"] == "INDETERMINATE" for r in rows
        ),
        "unsafe_true_or_false_predictions":0,
        "automatic_promotions":0,
        "formal_certifications":0,
        "horn_rules":[],
        "semantic_generalization_demonstrated":False,
        "warning":"No independent ground-truth or human annotation, and the transplant deliberately changes source context. Safety-only test, NOT math-verification accuracy.",
        "rows":rows,
    }


def markdown_report(report:dict)->str:
    lines=[
        "# EXT23 — audit externe de langage mathématique",
        "",
        "Étude de 12 courts extraits de sources humaines préexistantes, "
        "sélectionnés et figés avant le code du benchmark, mais **non aveugles**.",
        "",
        f"- Sources reliées : {report['number_external_sources_with_links']}/{report['source_count']}",
        f"- Sources externes complètes reconnues comme documents SEM22 : {report['source_count'] - report['raw_source_abstentions']}/{report['source_count']}",
        f"- Énoncés externes évaluables dans le langage strict : {report['supported_external_claim_count']}/{report['source_count']}",
        f"- Abstentions sur propositions externes isolées : {report['claim_transplant_abstentions']}/{report['source_count']}",
        f"- Verdicts scientifiques non justifiés : {report['unsafe_true_or_false_predictions']}",
        "",
        "**Verdict : cette expérience montre l'échec de couverture linguistique "
        "hors du format interne, accompagné d'abstentions sûres. Elle ne démontre "
        "aucune capacité à vérifier ces énoncés mathématiques externes.**",
        "",
        "Les fragments testés sont conservés *sans modification* avec leur URL et "
        "empreinte SHA256. Le test de « transplantation » ajoute un contexte "
        "synthétique uniquement pour isoler le comportement lexical et ne doit "
        "jamais être interprété comme un vrai contrôle de la signification de "
        "l'énoncé source.",
        "",
        "| ID | Catégorie | Source | Document brut | Phrase seule |",
        "|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['id']} | {row['category_from_preregistered_source_record']} "
            f"| [voir]({row['source_url']}) | {row['raw_document_status']} "
            f"| {row['lexical_transplant_only_status']} |"
        )
    lines.extend([
        "",
        "## Prochaine expérience décisive",
        "",
        "Créer un **adaptateur typé**, qui extrait d'un document authentique "
        "les seules formules finies explicitement bornées et leurs hypothèses. "
        "Séparer l'extraction et la preuve par calcul exact, rejeter les domaines "
        "ambigus et garder le vérificateur source SEM22 inchangé. "
        "Évaluer cet adaptateur sur **d'autres textes indépendants, non utilisés "
        "pour son développement**, avec un corrigé humain séparé.",
        "",
        "Ni cette expérience ni la cohorte synthétique SEM22 ne prouvent une "
        "intelligence mathématique générale ou une amélioration du LLM.",
    ])
    return "\n".join(lines) + "\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    args=p.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    failure=False
    try:
        report=evaluate()
    except Exception:
        failure=True
        report={"status":"AUDIT_FAILED_NOT_SCIENTIFIC_RESULT",
                "exception":traceback.format_exc()}
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    if args.markdown and not failure:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown_report(report),encoding="utf8")
    print("EXT23",report["status"],flush=True)
    if failure:
        sys.exit(1)


if __name__=="__main__":
    main()
