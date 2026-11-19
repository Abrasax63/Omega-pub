#!/usr/bin/env python3
"""TYPED24: evaluate precommitted contract cases and third-party OOD snippets.

No LLM or online calls. Uses prior checked readers, source gate and exact
semantic22 arithmetic. Keeps human text separate from controlled scaffolding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
sys.path.insert(0,str(HERE.parent/"semantic22"))
from read import safe_read
from checker import verify_source
from adapter import evaluate, check_external_proposal

FROZEN=HERE/"FROZEN_SOURCES.json"
CONTROL=HERE/"CONTROL_CASES.json"
HUMAN=HERE/"EXTERNAL_UNSEEN.json"
OLD_EXTERNAL=HERE.parent/"external23"/"EXTERNAL_SOURCES.json"
OLD_MATH=HERE.parent/"semantic22"/"FROZEN_ORACLE.json"


def contract_tasks()->list[dict]:
    frozen=json.loads(FROZEN.read_text(encoding="utf8"))
    spec=json.loads(CONTROL.read_text(encoding="utf8"))
    if (frozen["status"]!="FROZEN_BEFORE_IMPLEMENTATION" or
        spec["status"]!="FROZEN_PRE_IMPLEMENTATION"
        or len(frozen["docs"])!=24 or len(spec["cases"])!=24):
        raise ValueError("CONTRACT_DATASET_DRIFT")
    expected={c["id"]:c for c in spec["cases"]}
    if len(expected)!=24 or len({d["id"] for d in frozen["docs"]})!=24:
        raise ValueError("DUPLICATE_CONTRACT_SOURCE")
    tasks=[]
    for d in frozen["docs"]:
        target=ROOT/d["source_path"]
        if target.resolve()!=(HERE/"cases"/(d["id"]+".md")).resolve():
            raise ValueError("SOURCE_PATH_NOT_IN_FROZEN_DIRECTORY")
        raw=safe_read(target,d["git_blob"])
        spec_case=expected[d["id"]]
        if (d["expected_status"]!=spec_case["expected_status"]
            or spec_case["definition"] not in raw.decode("utf8")
            or spec_case["claim"] not in raw.decode("utf8")):
            raise ValueError("PRECOMMITTED_CONTRACT_MISMATCH")
        tasks.append({"ref":d,"raw":raw,"case":spec_case})
    return tasks


def check_contract()->dict:
    tasks=contract_tasks()
    outcomes=[]
    for item in tasks:
        ref=item["ref"]
        result=evaluate(item["raw"],expected_blob=ref["git_blob"],
                        source_path=ref["source_path"])
        expected=ref["expected_status"]
        if result["status"]!=expected:
            raise ValueError(f"CONTRACT_VERDICT_MISMATCH {ref['id']}: {result['status']} != {expected}")
        if result["auto_promotions"] or result["horn_rules"] or result["formal_theorems_certified"]:
            raise ValueError("UNAPPROVED_PROMOTION")
        old=verify_source(item["raw"],expected_blob=ref["git_blob"],
                          source_path=ref["source_path"])
        if old["status"]!="UNSUPPORTED_SOURCE":
            raise ValueError("BASELINE_SEM22_UNEXPECTEDLY_ACCEPTED_REFORMULATION")
        if result["status"] in ("VERIFIED_TRUE","VERIFIED_FALSE"):
            if not result["source_citation"] or result["source_citation"]["reader12_status"]!="QUARANTINE_SOURCE_ANCHORED_UNREVIEWED":
                raise ValueError("MISSING_SOURCE_GATE_QUARANTINE")
            accepted_proposal={
                "source_blob":ref["git_blob"],
                "claim_line":result["claim_line"],
                "typed_claim":result["interpretations"][0]["typed_claim"],
            }
            if not check_external_proposal(result,accepted_proposal)["accepted"]:
                raise ValueError("KNOWN_SOURCE_PROPOSAL_REJECTED")
            forged={**accepted_proposal,"typed_claim":{"kind":"INJ","value":999,"quantifier":"HALLUCINATED"}}
            if check_external_proposal(result,forged)["accepted"]:
                raise ValueError("MODEL_FABRICATED_IR_ACCEPTED")
        if result["status"]=="AMBIGUOUS" and result["interpretations"]:
            p={"source_blob":ref["git_blob"],
               "claim_line":result["claim_line"],
               "typed_claim":result["interpretations"][0]["typed_claim"]}
            if check_external_proposal(result,p)["accepted"]:
                raise ValueError("MODEL_COERCED_AMBIGUOUS_SOURCE")
        outcomes.append({
            "id":ref["id"],"expected_status":expected,
            "adapter_status":result["status"],"reason":result["reason"],
            "baseline_sem22":old["status"],
            "source_blob":ref["git_blob"],"source_path":ref["source_path"],
            "typed_definition":result["typed_definition"],
            "typed_alternatives":result["interpretations"],
            "source_citation":result["source_citation"],
            "automatic_promotions":0,
        })
    return {
        "n_cases":len(outcomes),
        "baseline_sem22_supported":sum(r["baseline_sem22"]!="UNSUPPORTED_SOURCE" for r in outcomes),
        "typed_adapter_verified":sum(r["adapter_status"] in ("VERIFIED_TRUE","VERIFIED_FALSE") for r in outcomes),
        "verified_true":sum(r["adapter_status"]=="VERIFIED_TRUE" for r in outcomes),
        "verified_false":sum(r["adapter_status"]=="VERIFIED_FALSE" for r in outcomes),
        "ambiguous":sum(r["adapter_status"]=="AMBIGUOUS" for r in outcomes),
        "indeterminate":sum(r["adapter_status"]=="INDETERMINATE" for r in outcomes),
        "errors":0,"rows":outcomes,
    }


def external_holdout()->dict:
    snap=json.loads(HUMAN.read_text(encoding="utf8"))
    rows=[]
    if (snap["status"]!="FROZEN_PRE_EVALUATION_NO_ADAPTER_TUNING" or
        len(snap["quotes"])!=6):
        raise ValueError("UNSEEN_EXTERNAL_COHORT_DRIFT")
    if len({s["url"] for s in snap["quotes"]})!=6:
        raise ValueError("EXTERNAL_SOURCES_NOT_DISTINCT")
    for item in snap["quotes"]:
        text=item["exact_quote"]
        raw=text.encode("utf8")
        # Real context / original words only; never synthesize a different
        # finite domain so that unsupported prose appears "correct".
        sha=hashlib.sha1(("blob "+str(len(raw))+"\0").encode("ascii")+raw).hexdigest()
        res=evaluate(raw,expected_blob=sha,source_path=item["url"])
        if res["status"] in ("VERIFIED_TRUE","VERIFIED_FALSE"):
            raise ValueError("UNSUPPORTED_EXTERNAL_TEXT_GIVEN_MATH_VERDICT")
        rows.append({
            "id":item["id"],"source_url":item["url"],
            "original_quote":text,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "status":res["status"],"reason":res["reason"],
            "auto_promotions":res["auto_promotions"],
        })
    return {
        "cohort":"NEW_EXTERNAL_QUOTES_COLLECTED_AFTER_ADAPTER_IMPLEMENTATION_BUT_BEFORE_EVAL",
        "human_annotated_truth":False,
        "n":len(rows),"verified":sum(x["status"].startswith("VERIFIED") for x in rows),
        "safe_abstention":sum(x["status"] not in ("VERIFIED_TRUE","VERIFIED_FALSE") for x in rows),
        "rows":rows,
        "warning":"Short third-party excerpts; no human mathematical truth oracle; cannot measure semantic recall.",
    }


def existing_compatibility()->dict:
    historic=json.loads(OLD_MATH.read_text(encoding="utf8"))
    prior=json.loads(OLD_EXTERNAL.read_text(encoding="utf8"))
    oldmath=0
    for x in historic["docs"]:
        raw=safe_read(ROOT/x["path"],x["blob"])
        res=verify_source(raw,expected_blob=x["blob"],source_path=x["path"])
        truth=[v["line"] for v in res["results"] if v["verdict"]=="TRUE"]
        if (res["status"]!="EVALUATED_FINITE_SCOPE" or not res["all_claims_checked"]
            or truth!=x["oracle_true_lines"]):
            raise ValueError("SEM22_EXACT_REPRODUCIBILITY_REGRESSION")
        oldmath+=len(res["results"])
    if oldmath!=168:
        raise ValueError("SEM22_MISSING_PREDICATES")
    oldsource=[]
    for x in prior["sources"]:
        raw=x["quote"].encode("utf8")
        sha=hashlib.sha1(("blob "+str(len(raw))+"\0").encode("ascii")+raw).hexdigest()
        res=evaluate(raw,expected_blob=sha,source_path=x["source_url"])
        if res["status"] in ("VERIFIED_TRUE","VERIFIED_FALSE"):
            raise ValueError("FORMER_EXTERNAL_TEXT_SILENTLY_PROMOTED")
        oldsource.append(res["status"])
    if len(oldsource)!=12:
        raise ValueError("EXTERNAL23_REGRESSION_SAMPLE_MISSING")
    return {"sem22_exact_math_reverified":oldmath,
            "external23_legacy_refusal_count":len(oldsource),
            "unexpected_certifications":0}


def run()->dict:
    a=check_contract()
    b=external_holdout()
    c=existing_compatibility()
    if a["typed_adapter_verified"]!=13 or a["ambiguous"]!=4 or a["indeterminate"]!=7:
        raise ValueError("PRECOMMITTED_CONTRACT_CLASSIFICATION_ERROR")
    return {
        "status":"TYPED24_LOCAL_CONTRACT_COMPLETED",
        "scientific_scope":"FINITELY_BOUNDED_SOURCE_GRAMMAR_ONLY",
        "contract":a,"new_external":b,"non_regression":c,
        "raw_interpretation_fidelity_on_new_external":"NOT_DEMONSTRATED",
        "semantic_equivalence_for_arbitrary_human_math":"NOT_DEMONSTRATED",
        "automatic_formal_certifications":0,"horn_rules":[],
        "recommendation":"Require independent human adjudication and another untouched external cohort before expanding deployment.",
    }


def render_markdown(report:dict)->str:
    c=report["contract"];e=report["new_external"];n=report["non_regression"]
    lines=[
        "# TYPED24 — Rapport d'interface typée et ambiguïté",
        "",
        "## Périmètre",
        "Adaptateur strict de fonctions finies explicitement typées, "
        "avec lecteur Reader12, quarantaine et calculateur exact SEM22 réutilisés. "
        "Aucun modèle de langage n'a été exécuté dans cette étape.",
        "",
        "## Tests de contrat contrôlés (créés par l'expérimentateur, non aveugles)",
        f"- Sources préenregistrées : {c['n_cases']}",
        f"- Énoncés avec verdict exact : {c['typed_adapter_verified']} (vrais {c['verified_true']}, faux {c['verified_false']})",
        f"- Énoncés ambigus conservés comme ambigus : {c['ambiguous']}",
        f"- Formulations hors du contrat : {c['indeterminate']}",
        f"- Ancien parseur SEM22 seul sur les mêmes sources reformulées : {c['baseline_sem22_supported']}",
        "",
        "L'écart sur ces 24 cas ne mesure PAS la généralisation de l'IA : "
        "il est une comparaison technique sur des documents conçus pour le test.",
        "",
        "## Distinction entre vérité et fidélité",
        "Une ambiguïté est refusée même lorsque deux interprétations ont "
        "le même verdict sur un cas particulier. Un modèle qui choisit "
        "arbitrairement une branche n'a pas le droit de transformer le résultat "
        "en théorème. Les résultats exacts portent seulement sur la "
        "formalisation typée admise.",
        "",
        "## Nouveaux textes de tiers, non adaptés",
        f"- Sources humaines courtes : {e['n']}",
        f"- Vérifiées comme assertions mathématiques complètes : {e['verified']}",
        f"- Abstentions : {e['safe_abstention']}",
        "",
        "Cet échantillon n'a pas d'annotations humaines indépendantes de vérité. "
        "Le taux d'abstention est une mesure de sûreté, pas de compréhension.",
        "",
        "## Compatibilité",
        f"- Vérifications exactes préexistantes recontrôlées : {n['sem22_exact_math_reverified']}",
        f"- Extraits EXT23 maintenus en refus : {n['external23_legacy_refusal_count']}",
        "- Modifications de main, promotions et certifications : aucune",
        "",
        "## Prochaine expérience falsifiable",
        "Faire annoter, par une personne indépendante, le domaine, "
        "les hypothèses et la signification de nouveaux énoncés réels. "
        "Comparer ces annotations à plusieurs propositions de formalisation "
        "indépendantes. Lorsque les lectures divergent, préserver l'ambiguïté "
        "et demander clarification. Ne jamais évaluer l'extension du parseur "
        "sur les exemples qui ont servi à la développer.",
        "",
        "| Source | Vérification |",
        "|---|---|",
    ]
    for row in e["rows"]:
        lines.append(f"| [{row['id']}]({row['source_url']}) | {row['status']} |")
    return "\n".join(lines)+"\n"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path)
    args=p.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fail=False
    try:
        report=run()
    except Exception:
        report={"status":"FAILED_NO_SCIENTIFIC_CONCLUSION",
                "traceback":traceback.format_exc()}
        fail=True
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if args.markdown and not fail:
        args.markdown.write_text(render_markdown(report),encoding="utf8")
    print("TYPED24",report["status"],flush=True)
    if fail:
        sys.exit(1)

if __name__=="__main__":
    main()
