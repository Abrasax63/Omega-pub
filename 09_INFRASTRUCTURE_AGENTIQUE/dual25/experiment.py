#!/usr/bin/env python3
"""DUAL25 -- replay two algorithmically distinct formalizers on pinned inputs.

This is NOT a human-reviewed autoformalization benchmark. Its blind review
packet intentionally omits machine interpretations and the author's known
labels; there is no independent human annotation yet.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
sys.path.insert(0,str(HERE.parent/"typed24"))
sys.path.insert(0,str(HERE.parent/"semantic22"))
from read import blob as git_blob, safe_read
from checker import verify_source
from consensus import inspect

MANIFEST = HERE / "FROZEN_INPUTS.json"
SOURCES = HERE.parent / "typed24" / "FROZEN_SOURCES.json"
CONTROL = HERE.parent / "typed24" / "CONTROL_CASES.json"
EXTERNAL_NEW = HERE.parent / "typed24" / "EXTERNAL_UNSEEN.json"
EXTERNAL_OLD = HERE.parent / "external23" / "EXTERNAL_SOURCES.json"
MATHEMATICS = HERE.parent / "semantic22" / "FROZEN_ORACLE.json"
TEMPLATE = HERE / "HUMAN_ANNOTATION_TEMPLATE.json"


def read_manifest() -> dict:
    frozen=json.loads(MANIFEST.read_text(encoding="utf8"))
    source_specs=[
        ("case_manifest_blob",SOURCES),
        ("case_spec_blob",CONTROL),
        ("external_six_blob",EXTERNAL_NEW),
        ("external_twelve_blob",EXTERNAL_OLD),
    ]
    if (frozen["status"]!="FROZEN_BEFORE_SECOND_FORMALIZER_CODE"
        or frozen["n_controls"]!=24 or frozen["n_short_external"]!=18
        or frozen["independent_human_annotation_status"]!="NONE_COLLECTED"):
        raise ValueError("UNREGISTERED_DATASET_OR_HUMAN_LABELS")
    for key,file in source_specs:
        if git_blob(file.read_bytes())!=frozen[key]:
            raise ValueError("SOURCE_MANIFEST_TAMPERED_"+key)
    return frozen


def controlled()->tuple[list[dict],list[dict]]:
    frozen=read_manifest()
    controls=json.loads(CONTROL.read_text(encoding="utf8"))["cases"]
    expected={x["id"]:x for x in controls}
    if len(expected)!=24 or len(frozen["documents"])!=24:
        raise ValueError("CONTRACT_CASE_COUNT_MISMATCH")
    rows=[]
    review=[]
    for item in frozen["documents"]:
        original=expected[item["id"]]
        source=ROOT/item["path"]
        if source.resolve()!=(HERE.parent/"typed24"/"cases"/(item["id"]+".md")).resolve():
            raise ValueError("DOC_NOT_ON_FROZEN_PATH")
        raw=safe_read(source,item["blob"])
        result=inspect(raw,expected_blob=item["blob"],source_path=item["path"])
        if (result["automatic_certifications"]!=0 or result["horn_rules"]
            or result["human_fidelity_certified"]):
            raise ValueError("FALSE_CERTIFICATION_FROM_FORMALIZER_AGREEMENT")
        rows.append({
            "id":item["id"],
            "source_path":item["path"],
            "source_blob":item["blob"],
            "status":result["gate"],
            "A_status":result["A_status"],
            "B_status":result["B_status"],
            "A_candidates":result["A_claim_candidates"],
            "B_candidate":result["B_claim_candidate"],
            "A_definition":result["A_typed_definition"],
            "B_definition":result["B_typed_definition"],
            "A_claim_line":result["A_claim_line"],
            "B_claim_line":result["B_claim_line"],
            "exact_finite_verdict":result.get("exact_finite_verdict"),
            "counterinterpretation_witness":result.get("non_equivalence_witness"),
            "machine_agreement":result["gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN",
            "human_fidelity_verified":False,
            "human_reviewer_status":"NOT_COLLECTED",
        })
        # BLIND WITHIN THIS PACKET. This input is publicly visible in the
        # repository, so a motivated reviewer can find the author's labels.
        review.append({
            "id":item["id"],
            "kind":"AUTHOR_DESIGNED_MATH_CONTRACT_NOT_NEW_HUMAN_SOURCE",
            "source_file":item["path"],
            "source_git_blob":item["blob"],
            "source_text_original":raw.decode("utf8"),
            "context_completeness":"COMPLETE_SYNTHETIC_CARD",
            "recommended_review_questions":[
                "Identify the domain/codomain without assuming implicit conditions.",
                "Is the claim a complete proposition or genuinely ambiguous?",
                "Record every plausible typed interpretation and justify with source quote.",
                "Do not look at formalizers' output or author labels before your review.",
            ],
        })
    return rows,review


def external()->tuple[list[dict],list[dict]]:
    read_manifest()
    newest=json.loads(EXTERNAL_NEW.read_text(encoding="utf8"))["quotes"]
    previous=json.loads(EXTERNAL_OLD.read_text(encoding="utf8"))["sources"]
    if len(newest)!=6 or len(previous)!=12:
        raise ValueError("EXTERNAL_SNIPPET_SET_CHANGED")
    entries=[{
        "id":x["id"],"text":x["exact_quote"],
        "url":x["url"],"group":"SIX_NEW_EXTERNAL_SOURCES"
    } for x in newest] + [{
        "id":x["id"],"text":x["quote"],
        "url":x["source_url"],"group":"TWELVE_OLDER_EXTERNAL_SOURCES"
    } for x in previous]
    out=[]
    blind=[]
    for x in entries:
        raw=x["text"].encode("utf8")
        sha=git_blob(raw)
        result=inspect(raw,expected_blob=sha,source_path=x["url"])
        if result["gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN":
            raise ValueError("UNSUPPORTED_THIRD_PARTY_EXCERPT_UNEXPECTEDLY_DECIDED")
        out.append({
            "id":x["id"],"url":x["url"],"group":x["group"],
            "source_text_sha256":hashlib.sha256(raw).hexdigest(),
            "status":result["gate"],"A_status":result["A_status"],
            "B_status":result["B_status"],
            "human_fidelity_verified":False,
        })
        blind.append({
            "id":x["id"],"kind":"THIRD_PARTY_SHORT_QUOTE_WITHOUT_COMPLETE_CONTEXT",
            "source_url":x["url"],
            "literal_quote":x["text"],
            "quote_sha256":hashlib.sha256(raw).hexdigest(),
            "context_completeness":"INCOMPLETE_SHORT_EXCERPT",
            "recommended_review_questions":[
                "Is there enough original context to determine the intended theorem?",
                "If not, mark CONTEXT_INSUFFICIENT; never infer missing hypotheses.",
                "Do not substitute an invented finite domain or finite modulus.",
            ],
        })
    return out,blind


def check_sem22_legacy()->int:
    historic=json.loads(MATHEMATICS.read_text(encoding="utf8"))["docs"]
    verified=0
    for entry in historic:
        raw=safe_read(ROOT/entry["path"],entry["blob"])
        report=verify_source(raw,expected_blob=entry["blob"],source_path=entry["path"])
        if (report["status"]!="EVALUATED_FINITE_SCOPE"
            or not report["all_claims_checked"]
            or [r["line"] for r in report["results"] if r["verdict"]=="TRUE"]
               != entry["oracle_true_lines"]):
            raise ValueError("REGRESSION_IN_EXACT_SEM22_VERIFIER")
        verified+=len(report["results"])
    if verified!=168:
        raise ValueError("SEM22_EXPECTED_168_INVARIANTS")
    return verified


def review_packet(controls:list[dict],external:list[dict])->dict:
    packet={
        "status":"BLIND_WITHIN_PACKET_ONLY_NOT_PRIVATE_DATASET",
        "authors_of_test_cases":"OMEGA_TEST_GENERATION_NOT_INDEPENDENT",
        "human_annotation_status":"PENDING_NOT_PERFORMED",
        "reviewer_identity":"NOT_ASSIGNED",
        "source_count":len(controls)+len(external),
        "labels_and_machine_proposals_excluded":True,
        "warning":"The source repo is public and independent blind review is not guaranteed; use independent new full documents for actual faithfulness scoring.",
        "items":controls+external,
    }
    if packet["source_count"]!=42:
        raise ValueError("BLIND_REVIEW_PACKET_IS_NOT_COMPLETE")
    return packet


def run()->tuple[dict,dict]:
    contracts,rc=controlled()
    public,re=external()
    exact=check_sem22_legacy()
    gate_count=Counter(x["status"] for x in contracts)
    witnesses=[x for x in contracts if x["counterinterpretation_witness"]
               and x["counterinterpretation_witness"]["finding"]=="FINITE_COUNTEREXAMPLE_TO_EQUIVALENCE"]
    # Existing TYPED24 A has 13 unambiguous exact cases; a discrepancy
    # is a regression or a causal finding, not silently a success.
    if (len(contracts)!=24 or len(public)!=18
        or gate_count["AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"]>13):
        raise ValueError("PREEXISTING_CONTRACT_IS_OUT_OF_SCOPE")
    status={
        "status":"DUAL25_MECHANICAL_ABLATION_COMPLETED",
        "formalizers":[
            {"id":"A","algorithm":"TYPED24_FIXED_REGEX_AND_SOURCE_PATTERNS",
             "author_independent":False},
            {"id":"B","algorithm":"FRESH_TOKEN_STREAM_GRAMMAR",
             "author_independent":False},
        ],
        "source_controlled_contracts":24,
        "machine_agreement_count":gate_count["AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"],
        "machine_agreement_ratio_on_author_cases":
            round(gate_count["AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"]/24,6),
        "withheld_cases":24-gate_count["AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"],
        "gate_status_counts":dict(gate_count),
        "discriminating_interpretation_witnesses":len(witnesses),
        "external_short_sources":len(public),
        "external_claims_verified":sum(x["status"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN" for x in public),
        "external_safe_refusals":sum(x["status"]!="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN" for x in public),
        "sem22_original_exact_claims_rechecked":exact,
        "independent_human_reference_status":"PENDING_NO_HUMAN_GOLD",
        "can_measure_fidelity_to_real_human_intent":False,
        "causal_conclusion":"NO_REAL_LANGUAGE_SEMANTIC_TRANSFER_ESTABLISHED",
        "automatic_formal_certifications":0,
        "horn_rules":[],
        "controlled_case_details":contracts,
        "external_details":public,
        "next_test":"Independent blind annotation of new, complete, human-authored problems; compare unmodified A and B before tuning.",
    }
    return status,review_packet(rc,re)


def markdown_report(out:dict)->str:
    c=out["gate_status_counts"]
    return "\n".join([
        "# DUAL25 — deux formaliseurs et fidélité sémantique",
        "",
        "Expérience mécanique, pas un benchmark humain de fidélité. "
        "Même auteur / mêmes sources entre les deux voies ; le consensus ne "
        "certifie pas le sens de l'énoncé.",
        "",
        f"- Cas contrôlés réutilisés : {out['source_controlled_contracts']}",
        f"- Accord structurel avec calcul exact : {out['machine_agreement_count']}/24",
        f"- Cas retenus pour désaccord, ambiguïté ou hors langage : {out['withheld_cases']}/24",
        f"- Contre-exemples d'interprétations distinctes : {out['discriminating_interpretation_witnesses']}",
        f"- Courts extraits externes (anciennes sources, non un nouveau holdout) : {out['external_short_sources']}",
        f"- Extraits externes réellement vérifiés : {out['external_claims_verified']}",
        f"- Régressions SEM22 contrôlées : {out['sem22_original_exact_claims_rechecked']} propositions",
        "- Annotations humaines indépendantes : **absentes**",
        "",
        "## Lecture des résultats",
        "",
        "Les accords signifient uniquement une concordance d'AST locale entre "
        "un parseur à patrons et un parseur par jetons, avec exactitude arithmétique "
        "dans Z/nZ. La fidélité à l'intention humaine est indéterminée.",
        "",
        "Les désaccords sont archivés comme de **nouvelles hypothèses** ; un "
        "contre-exemple fini prouve la non-équivalence de deux lectures mais "
        "ne permet pas de choisir celle que l'auteur voulait.",
        "",
        "## Validation humaine encore nécessaire",
        "",
        "Le paquet \`HUMAN_REVIEW_PACKET.json\` masque les réponses attendues et "
        "les analyses des parseurs **à l'intérieur du paquet**. Le dépôt "
        "étant public, l'aveuglement réel devra être organisé par un réviseur "
        "indépendant, sur des textes complets et non vus, avec annotation "
        "domaine/hypothèses/quantificateurs et justification des lectures.",
        "",
        f"Répartition : {c}",
        "",
        "**Interdictions :** ni preuve Lean, ni règle Horn, ni mise à jour "
        "automatique de la mémoire scientifique, ni modification de main.",
        "",
    ])+"\n"


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--review-packet",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    for output in (args.report,args.review_packet,args.markdown):
        output.parent.mkdir(parents=True,exist_ok=True)
    failed=False
    try:
        out,packet=run()
    except Exception:
        failed=True
        out={"status":"EXPERIMENT_FAILED_NOT_A_SCIENTIFIC_RESULT",
             "traceback":traceback.format_exc()}
        packet={"status":"NO_HUMAN_REVIEW_PACKAGE_DUE_TO_FAILED_EXPERIMENT"}
    args.report.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    args.review_packet.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if not failed:
        args.markdown.write_text(markdown_report(out),encoding="utf8")
    print("DUAL25",out["status"],flush=True)
    if failed:
        sys.exit(1)


if __name__=="__main__":
    main()
