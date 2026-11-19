#!/usr/bin/env python3
"""CONCEPT28: frozen NL->Lean concept grounding tested on genuinely NEW cases.

This is a source-linked *recognition* proxy, not theorem formalization.
Rules are in frozen CONCEPT_LEXICON.json; the program never sees the
reference pairing when scoring the two candidate theorem strings.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"proofnet26"))
sys.path.insert(0,str(HERE.parent/"contrast27"))
from runner import fetch_pinned,extract_original_pair
from paired import anonymize_reference

HOLDOUT=HERE/"FROZEN_HOLDOUT.json"
LEX=HERE/"CONCEPT_LEXICON.json"
NEAR=((31,32),(33,34),(35,36),(37,38),(39,41),(42,43))
FAR=((44,180),(45,181),(46,182),(47,183),(48,184),(49,185))
EXPECTED=NEAR+FAR
BANNED_NAMES={"theorem","type","class","prove","show","that","this","with",
              "then","from","have","will","every","exists","such","all","the",
              "for","let","there","which","they","when","where","into","only",
              "are","and","you","its","can","not","has","but","may","any",
              "be","one","two","given"}
SOURCE_COMMIT="b7ca411a2abaa6caf3580192b30d865e5bd10bc4"


def load_lexicon()->dict:
    data=json.loads(LEX.read_text(encoding="utf8"))
    if (data.get("status")!="FROZEN_BEFORE_UNSEEN_CORPUS_READING"
        or data.get("method")!="REGEX_MATH_CONCEPT_LINKS_NL_TO_LEAN_TOKEN_SIGNATURES"
        or data["decision_threshold"]!={"min_best_score":2,"min_margin":2}
        or len(data["keywords"])!=40):
        raise ValueError("SEMANTIC_RULES_CHANGED_AFTER_PRE_REGISTRATION")
    ids=[x["id"] for x in data["keywords"]]
    if len(set(ids))!=40:
        raise ValueError("CONCEPT_ID_DUPLICATE")
    for x in data["keywords"]:
        if (not isinstance(x["weight"],int) or not 1<=x["weight"]<=3
            or not x["nl_patterns"] or not x["lean_patterns"]):
            raise ValueError("MALFORMED_CONCEPT_RULE")
        for pat in x["nl_patterns"]+x["lean_patterns"]:
            re.compile(pat)
    return data


def load_holdout()->dict:
    data=json.loads(HOLDOUT.read_text(encoding="utf8"))
    if (data.get("status")!="FROZEN_BEFORE_EVALUATOR_IMPLEMENTATION"
        or data.get("source_commit")!=SOURCE_COMMIT
        or tuple(map(tuple,data["pairs"]))!=EXPECTED
        or len(data["docs"])!=24 or data["n_new_cases"]!=24
        or len({x["git_blob"] for x in data["docs"]})!=24
        or [x["index"] for x in data["docs"]]!=[v for pair in EXPECTED for v in pair]
        or data.get("negative_independent_equivalence_annotation") is not False):
        raise ValueError("NEW_EXTERNAL_HOLDOUT_TAMPERED")
    return data


def read_original_statement(raw:bytes,ref:dict)->dict:
    """Use unchanged external theorem signature, not any proof body.

    The earlier PROOFNET26 extractor accepted exactly ':= by sorry'.
    Some valid upstream ProofNet-V files contain a *complete proof* instead.
    Permit that format, still hash the ORIGINAL entire Git file and never
    infer or fabricate a new statement.
    """
    try:
        original=extract_original_pair(raw,ref)
        formal=original["reference_lean_theorem_exact"]
        return {
            "informal":original["informal_statement_exact"],
            "code":anonymize_reference(formal),
            "nl_sha256":original["informal_sha256"],
            "lean_sha256":original["reference_lean_sha256"],
            "proof_body_kind":"SORRY_PLACEHOLDER",
        }
    except ValueError as exc:
        if str(exc)!="INCOMPLETE_EXTERNAL_NL_LEAN_PAIR":
            raise
    text=raw.decode("utf8",errors="strict")
    nl_matches=list(re.finditer(r"(?m)^/-Informal Statement[ \t]*\n([\s\S]*?)\n-/$",text))
    declarations=list(re.finditer(r"(?m)^theorem\s+[^\s]+\s",text))
    if len(nl_matches)!=1 or len(declarations)!=1:
        raise ValueError("FULL_PROOF_FALLBACK_NEEDS_UNIQUE_NL_AND_THEOREM")
    start=declarations[0].start()
    stop=text.find(":= by",start)
    if stop<=start or stop-start>20000:
        raise ValueError("NO_PROVEN_THEOREM_HEADER_IN_ORIGINAL_SOURCE")
    declaration=text[start:stop].rstrip()
    tail=text[stop:]
    if len(declaration)<30 or "sorry" in tail or not tail.startswith(":= by"):
        raise ValueError("FULL_PROOF_FALLBACK_NOT_AN_ACTUAL_PROOF_BODY")
    if start<=nl_matches[0].start():
        raise ValueError("SOURCE_THEOREM_PRECEDES_NL")
    # Prefix and signature are original bytes; remove only the proof body.
    source_sig=declaration.strip()
    name=re.match(r"theorem\s+[A-Za-z0-9_']+",source_sig)
    if name is None:
        raise ValueError("CANNOT_REMOVE_THEOREM_IDENTIFIER")
    neutral=("theorem candidate"+source_sig[name.end():]).strip()
    if len(neutral)<30:
        raise ValueError("EMPTY_SEMANTIC_LEAN_SIGNATURE")
    nl=nl_matches[0].group(1)
    if not nl.strip():
        raise ValueError("MISSING_EXTERNAL_NATURAL_LANGUAGE_STATEMENT")
    return {
        "informal":nl,"code":neutral,
        "nl_sha256":hashlib.sha256(nl.encode("utf8")).hexdigest(),
        "lean_sha256":hashlib.sha256(declaration.encode("utf8")).hexdigest(),
        "proof_body_kind":"COMPLETE_ORIGINAL_PROOF_NOT_IN_CANDIDATE",
    }


def read_tasks(*,offline_dir:Path|None=None)->list[dict]:
    load_lexicon()
    snap=load_holdout()
    entries={}
    for ref in snap["docs"]:
        raw=fetch_pinned(ref,cache_dir=offline_dir)
        item=read_original_statement(raw,ref)
        entries[ref["index"]]={
            "index":ref["index"],"nl":item["informal"],
            "code":item["code"],"source_blob":ref["git_blob"],
            "source_url":ref["source_url"],
            "nl_sha256":item["nl_sha256"],
            "lean_original_sha256":item["lean_sha256"],
            "proof_body_kind":item["proof_body_kind"],
        }
    return [
        {
            "pair_number":i+1,"stratum":"NEAR" if i<6 else "FAR",
            "first":entries[a],"second":entries[b],
            "indices":[a,b],
        } for i,(a,b) in enumerate(EXPECTED)
    ]


def matching_lexical_terms(text:str)->set[str]:
    """Naive baseline but with CamelCase splitting to avoid straw-man baselines."""
    separated=re.sub(r"([a-z])([A-Z])",r"\1 \2",text)
    words={x.lower() for x in re.findall(r"[A-Za-z]{4,}",separated)}
    return words-BANNED_NAMES


def baseline_score(nl:str,lean:str)->dict:
    common=sorted(matching_lexical_terms(nl)&matching_lexical_terms(lean))
    return {"score":len(common),"matched_terms":common}


def grounded_score(nl:str,lean:str,lexicon:dict)->dict:
    """All matched concepts must have literal evidence on BOTH sides."""
    found=[]
    cues=[]
    for concept in lexicon["keywords"]:
        original=next((p for p in concept["nl_patterns"]
                       if re.search(p,nl,re.IGNORECASE)),None)
        target=next((p for p in concept["lean_patterns"]
                     if re.search(p,lean)),None)
        if original is not None:
            cues.append(concept["id"])
            if target is not None:
                found.append({
                    "concept":concept["id"],
                    "weight":concept["weight"],
                    "natural_pattern":original,
                    "formal_pattern":target,
                })
    return {
        "score":sum(x["weight"] for x in found),
        "nl_concepts_detected":cues,
        "matches":found,
        "alignment_is_a_theorem_proof":False,
    }


def choose(scores:dict[str,dict],*,mode:str,lexicon:dict)->dict:
    """Symmetric selection; gold reference identity is NOT an input."""
    if set(scores)!={"A","B"}:
        raise ValueError("CANDIDATE_LABELS_WRONG")
    threshold=(lexicon["decision_threshold"] if mode=="typed" else
               {"min_best_score":1,"min_margin":1})
    vals={k:scores[k]["score"] for k in ("A","B")}
    winner="A" if vals["A"]>vals["B"] else "B" if vals["B"]>vals["A"] else "NONE"
    if (winner=="NONE" or
        vals[winner]<threshold["min_best_score"] or
        abs(vals["A"]-vals["B"])<threshold["min_margin"]):
        winner="NONE"
    return {"chosen":winner,"scores":vals,
            "reason":"DISTINCT_EVIDENCE_MARGIN" if winner!="NONE"
                     else "INSUFFICIENT_DISCRIMINATING_EVIDENCE"}


def judge(nl:str,opts:dict[str,str],lex:dict,mode:str)->dict:
    if mode not in ("typed","naive"):
        raise ValueError("UNKNOWN_MATCHING_ALGORITHM")
    fn=(lambda t:grounded_score(nl,t,lex)) if mode=="typed" else (lambda t:baseline_score(nl,t))
    values={label:fn(form) for label,form in opts.items()}
    decision=choose(values,mode=mode,lexicon=lex)
    return {**decision,"evidence":values,
            "is_independent_human_meaning_verification":False}


def one_pair(pair:dict,lexicon:dict)->list[dict]:
    first,second=pair["first"],pair["second"]
    if first["code"]==second["code"]:
        raise ValueError("AMBIGUOUS_SAME_FORMAL_CODE_PAIR")
    outputs=[]
    for datum,wrong in ((first,second),(second,first)):
        for order in (0,1):
            true_is_A=(datum["index"]%2 == 0) ^ (order==1)
            correct="A" if true_is_A else "B"
            options={
                "A":datum["code"] if true_is_A else wrong["code"],
                "B":wrong["code"] if true_is_A else datum["code"],
            }
            if options["A"]==options["B"]:
                raise ValueError("DUPLICATE_CANDIDATE")
            out={
                "index":datum["index"],"decoy_index":wrong["index"],
                "stratum":pair["stratum"],"orientation":order,
                "source_url":datum["source_url"],
                "source_blob":datum["source_blob"],
                "original_nl":datum["nl"],
                "lean_correct_original_reference_sha256":datum["lean_original_sha256"],
                "correct_option_posthoc_only":correct,
                "candidate_option_sha256":{
                    k:hashlib.sha256(c.encode("utf8")).hexdigest() for k,c in options.items()},
                "no_replacement_labels":True,
                "strategies":{},
            }
            for mode in ("naive","typed"):
                guess=judge(datum["nl"],options,lexicon,mode)
                selected=guess["chosen"]
                out["strategies"][mode]={
                    **guess,
                    "source_selected":(
                        datum["index"] if selected==correct else
                        wrong["index"] if selected in ("A","B") else None),
                    "is_original_reference_match":selected==correct,
                }
            outputs.append(out)
    return outputs


def scores(rows:list[dict],mode:str)->dict:
    results=[r["strategies"][mode] for r in rows]
    count=sum(x["chosen"]!="NONE" for x in results)
    correct=sum(x["is_original_reference_match"] for x in results)
    return {
        "presentations":len(rows),
        "accepted":count,
        "original_reference_correct":correct,
        "wrong_source_selected":count-correct,
        "abstentions":len(rows)-count,
        "coverage":round(count/len(rows),5) if rows else 0,
        "precision_on_accepted":round(correct/count,5) if count else None,
        "accuracy_over_all":round(correct/len(rows),5) if rows else 0,
    }


def evaluation(*,offline_dir:Path|None=None)->dict:
    lexicon=load_lexicon()
    groups=read_tasks(offline_dir=offline_dir)
    rows=[]
    for group in groups:
        rows.extend(one_pair(group,lexicon))
    if (len(rows)!=48
        or len({r["index"] for r in rows})!=24
        or sorted(set(r["orientation"] for r in rows))!=[0,1]):
        raise ValueError("CONCEPT28_UNBALANCED_SOURCE_COHORT")
    for group in groups:
        for idx in group["indices"]:
            copies=sorted([r for r in rows if r["index"]==idx],
                          key=lambda x:x["orientation"])
            if len(copies)!=2 or {c["correct_option_posthoc_only"] for c in copies}!={"A","B"}:
                raise ValueError("BALANCING_FAILED")
            for mode in ("naive","typed"):
                x,y=(c["strategies"][mode] for c in copies)
                if x["source_selected"] != y["source_selected"]:
                    raise ValueError("MATCHER_POSITION_BIAS")
    return {
        "status":"COMPLETED_GROUNDED_CONCEPT_EXTERNAL_HOLDOUT",
        "n_original_external_human_theorems":24,
        "n_pairs":12,
        "n_presentations":48,
        "old_proofnet26_or_contrast27_examples_reused":False,
        "generated_formal_theorems":0,
        "trained_parameters":0,
        "model_inference_calls":0,
        "curated_positive_reference":"UPSTREAM_INDEPENDENT_PROOFNET_VERIFIED_PAIR",
        "negative_pairwise_non_equivalence_human_validated":False,
        "is_semantic_formalization_benchmark":False,
        "baseline_first_candidate_accuracy":0.5,
        "all":{
            "naive":scores(rows,"naive"),
            "typed":scores(rows,"typed"),
        },
        "by_stratum":{
            stratum:{
                "naive":scores([r for r in rows if r["stratum"]==stratum],"naive"),
                "typed":scores([r for r in rows if r["stratum"]==stratum],"typed"),
            } for stratum in ("NEAR","FAR")},
        "raw_rows":rows,
        "certifications":0,"horn_rules":[],
        "no_external_human_new_annotations":True,
    }


def markdown(v:dict)->str:
    lines=[
        "# CONCEPT28 — rapprochement conceptuel NL/Lean sur 24 nouveaux problèmes",
        "",
        "## Résultats mécaniques",
        "",
        "Les 24 sources complètes sont étrangères à PROOFNET26 et CONTRAST27.",
        "Source : ProofNet-Verified, Git SHA figés avant lecture des exemples ; "
        "règles de concepts et seuils figés avant implémentation et essai.",
        "",
        "| Difficulté | Méthode | Appariements corrects | Mauvaises sélections | Abstentions | Précision sur sélections |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for mode in ("naive","typed"):
        for subset in ("NEAR","FAR"):
            result=v["by_stratum"][subset][mode]
            lines.append(
                f"| {subset} | {mode} | {result['original_reference_correct']}/{result['presentations']} "
                f"| {result['wrong_source_selected']} | {result['abstentions']} "
                f"| {result['precision_on_accepted']} |"
            )
    lines.extend([
        "",
        "## Interprétation rigoureuse",
        "",
        "Une correspondance de mots spécialisés entre un énoncé et des identifiants "
        "Lean est un **indice typé / lexical** mais n'est PAS une traduction "
        "ou une preuve de fidélité sémantique. Les négatifs sont fabriqués "
        "par désappariement de références distinctes et peuvent ne pas être "
        "mathématiquement indépendants ; ils n'ont pas de validation humaine "
        "d'inequivalence.",
        "",
        "Les deux présentations A/B ne sont pas des observations indépendantes : "
        "la décision du programme est strictement invariante sous permutation "
        "par construction. Le score sur 24 problèmes originaux, et non sur "
        "48 présentations, est l'unité d'évaluation réelle.",
        "",
        "Une amélioration limitée aux paires FAR témoigne d'un **tri de grands "
        "domaines** et pas d'un raisonnement fin. Aucun modèle Qwen n'a été "
        "réexécuté sur ce holdout, de sorte que la comparaison directe avec "
        "CONTRAST27 n'est pas causalement valable.",
        "",
        "Aucune validation Lean locale, aucune règle Horn, aucune certification "
        "de theorem, aucune API payante ni changement de main.",
    ])
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--offline-dir",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--markdown",type=Path,required=True)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    failed=False
    try:
        result=evaluation(offline_dir=args.offline_dir)
    except Exception:
        failed=True
        result={"status":"FAILED_NO_VALID_EXTERNAL_RESULT",
                "error":traceback.format_exc()}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if not failed:
        args.markdown.write_text(markdown(result),encoding="utf8")
    print("CONCEPT28",result["status"],flush=True)
    if failed:
        sys.exit(1)

if __name__=="__main__":
    main()
