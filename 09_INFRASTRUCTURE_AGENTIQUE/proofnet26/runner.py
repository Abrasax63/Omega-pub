#!/usr/bin/env python3
"""PROOFNET26: pinned original human-authored math + curated Lean reference.

No content rewriting, source substitution, answer inference, type-checking
claims, or fake human annotations. Two existing frozen A/B frontends are
evaluated in literal and neutral-wrapper modes to diagnose coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"typed24"))
sys.path.insert(0,str(HERE.parent/"dual25"))
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
sys.path.insert(0,str(HERE.parent/"semantic22"))

from read import blob as git_blob, packetize, verify_packets
from adapter import evaluate as formalizer_A
from token_formalizer_b import parse as formalizer_B
from consensus import reconcile
from checker import verify_source

MANIFEST=HERE/"FROZEN_UPSTREAM.json"
SOURCE_REPO="marcusm117/ProofNet-Verified"
SOURCE_COMMIT="b7ca411a2abaa6caf3580192b30d865e5bd10bc4"
SOURCE_PREFIX="proofnet-verified-latest/"
NL_BEGIN="/-Informal Statement\n"
NL_END="\n-/"
NL_COMMENT=re.compile(r"(?m)^/-Informal Statement[ \t]*\n([\s\S]*?)\n-/$")
FORMAL_THEOREM=re.compile(r"(?m)^theorem\s+[\s\S]*?:= by\s*\n\s*sorry\b")
REJECTED={"AMBIGUOUS","INDETERMINATE","INVALID_SOURCE"}
B_REJECTED={"UNSUPPORTED","AMBIGUOUS"}
INDICES=(1,2,3,6,10,22,40,80,120,160,200,240,280,320,350,367)

def manifest()->dict:
    data=json.loads(MANIFEST.read_text(encoding="utf8"))
    if (data.get("status")!="FROZEN_BEFORE_EVALUATION_CODE"
        or data.get("source_repository")!=SOURCE_REPO
        or data.get("source_commit")!=SOURCE_COMMIT
        or data.get("n_cases")!=16
        or tuple(x["index"] for x in data["items"])!=INDICES
        or len({x["git_blob"] for x in data["items"]})!=16):
        raise ValueError("UNREGISTERED_EXTERNAL_COHORT")
    for item in data["items"]:
        number=item["index"]
        expected=f"{SOURCE_PREFIX}proofnet-{number}.lean"
        if (item["path"]!=expected or
            not re.fullmatch(r"[0-9a-f]{40}",item["git_blob"]) or
            item["source_url"]!=f"https://github.com/{SOURCE_REPO}/blob/{SOURCE_COMMIT}/{expected}"):
            raise ValueError("UNPINNED_OR_MISMATCHED_UPSTREAM_PATH")
    return data


def remote_url(item:dict)->str:
    return (f"https://raw.githubusercontent.com/{SOURCE_REPO}/"
            f"{SOURCE_COMMIT}/{item['path']}")


def fetch_pinned(item:dict, *, cache_dir:Path|None=None)->bytes:
    if cache_dir is not None:
        path=cache_dir/(str(item["index"])+".lean")
        if path.exists():
            raw=path.read_bytes()
        else:
            raise ValueError("EXPECTED_PINNED_OFFLINE_CACHE_FILE")
    else:
        url=remote_url(item)
        request=urllib.request.Request(url,headers={
            "User-Agent":"Omega-proofnet26-readonly-verified-source",
            "Accept":"text/plain"
        })
        with urllib.request.urlopen(request,timeout=40) as response:
            raw=response.read(100_001)
    if not isinstance(raw,bytes) or len(raw)>100_000 or len(raw)<40:
        raise ValueError("SOURCE_BYTES_OUT_OF_RANGE")
    if git_blob(raw)!=item["git_blob"]:
        raise ValueError("UPSTREAM_SOURCE_GIT_HASH_MISMATCH")
    return raw


def extract_original_pair(raw:bytes,item:dict)->dict:
    # Exact source is already pinned with Git blob. Require exactly one
    # NL/Lean pair, not an arbitrarily chosen snippet from a search.
    text=raw.decode("utf8",errors="strict")
    nls=list(NL_COMMENT.finditer(text))
    formal=list(FORMAL_THEOREM.finditer(text))
    if len(nls)!=1 or len(formal)!=1:
        raise ValueError("INCOMPLETE_EXTERNAL_NL_LEAN_PAIR")
    nl=nls[0].group(1)
    theorem=formal[0].group(0)
    if (not nl.strip() or len(nl)>10_000 or not theorem.strip()
        or len(theorem)>20_000
        or not text.index(nls[0].group(0))<text.index(theorem)):
        raise ValueError("MISSING_OR_ORDER_REVERSED_MATH_CONTEXT")
    nl_start=text[:nls[0].start(1)].count("\n")+1
    nl_end=text[:nls[0].end(1)].count("\n")+1
    formal_start=text[:formal[0].start()].count("\n")+1
    formal_end=text[:formal[0].end()].count("\n")+1
    # Replay the exact source excerpt by line. Blank lines in the original
    # are preserved, because paragraph structure can affect quantifier scope.
    lines=text.splitlines()
    if ("\n".join(lines[nl_start-1:nl_end]).strip()!=nl.strip()
        or not theorem.strip().startswith("theorem ")
        or not theorem.rstrip().endswith("sorry")):
        raise ValueError("EXTERNAL_QUOTE_SPAN_FAILED_REPLAY")
    packets=packetize(raw,item["source_url"])
    if verify_packets(raw,packets):
        raise ValueError("PINNED_SOURCE_PACKET_INTEGRITY_FAILED")
    return {
        "index":item["index"],"external_source_url":item["source_url"],
        "external_source_sha":item["git_blob"],
        "informal_source_span":[nl_start,nl_end],
        "formal_source_span":[formal_start,formal_end],
        "informal_statement_exact":nl,
        "reference_lean_theorem_exact":theorem,
        "reference_lean_sha256":hashlib.sha256(theorem.encode("utf8")).hexdigest(),
        "informal_sha256":hashlib.sha256(nl.encode("utf8")).hexdigest(),
        "formal_lean_status":"EXTERNALLY_AUDITED_REFERENCE_NOT_COMPILED_BY_OMEGA",
        "human_annotation_status":"PREEXISTING_EXTERNALLY_REVIEWED_HUMAN_PLUS_AI_NOT_TWO_NEW_BLIND_REVIEWERS",
        "original_context_caveat":"The informal statement comes from a curated theorem file; implicit textbook context may exist.",
        "original_source_replayed":True,
        "reader12_packet_count":packets["stats"]["packet_count"],
    }


def _wrapper(nl:str,index:int)->bytes:
    # ZERO invented mathematical definition. Diagnostic ONLY:
    # a null definition section makes syntactic vs semantic refusal explicit.
    text=(f"# Fiche PN{index}\n\n## Définition\n\n"
          f"\n## Énoncé\n\n{nl}\n")
    wrapped=text.encode("utf8")
    if nl not in wrapped.decode("utf8"):
        raise ValueError("ORIGINAL_NL_NOT_PRESERVED_VERBATIM")
    return wrapped


def run_frontends(raw:bytes,*,source_path:str)->dict:
    sha=git_blob(raw)
    A=formalizer_A(raw,expected_blob=sha,source_path=source_path)
    B=formalizer_B(raw,expected_blob=sha,source_path=source_path)
    # Always run the reconciliation gate: shared abstentions are NOT success.
    both=reconcile(A,B,raw=raw,expected_blob=sha,source_path=source_path)
    if (both["human_fidelity_certified"] or both["automatic_certifications"]
        or both["gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"):
        raise ValueError("UNEXPECTED_EXTERNAL_FORMALIZATION_PROMOTION")
    return {
        "A_status":A["status"],"A_reason":A["reason"],
        "B_status":B["status"],"B_reason":B["reason"],
        "comparison_gate":both["gate"],
        "reference_lean_compared":"NO_IR_TO_LEAN_EQUIVALENCE_IMPLEMENTED",
        "human_fidelity_to_reference":"NOT_COMPARABLE_TYPE_SYSTEMS",
    }


def evaluate(*,cache_dir:Path|None=None)->dict:
    m=manifest()
    start=time.perf_counter()
    rows=[]
    for item in m["items"]:
        raw=fetch_pinned(item,cache_dir=cache_dir)
        pairing=extract_original_pair(raw,item)
        original=run_frontends(raw,source_path=item["source_url"])
        nl=pairing["informal_statement_exact"]
        literal=run_frontends(nl.encode("utf8"),
            source_path=item["source_url"]+"#informal-statement-only")
        wrapper=run_frontends(_wrapper(nl,item["index"]),
            source_path=item["source_url"]+"#neutral-diagnostic-wrapper")
        if any(z["comparison_gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"
               for z in (original,literal,wrapper)):
            raise ValueError("EXTERNAL_COVERAGE_NOT_SUPPORTED_BY_FROZEN_PROVENANCE")
        rows.append({
            **pairing,
            "raw_original_file_frontends":original,
            "original_informal_statement_frontends":literal,
            "diagnostic_neutral_wrapper_frontends":wrapper,
            "reference_to_generated_formal_equivalence":"NOT_EVALUABLE_WITH_CURRENT_FINITE_FUNCTION_IR",
            "human_review_independent_of_omega":"EXTERNAL_DATASET_REVIEW_PREEXISTING",
        })
        print("PROOFNET26",item["index"],"source",item["git_blob"],
              "A",literal["A_status"],"B",literal["B_status"],flush=True)
    if len(rows)!=16:
        raise ValueError("MISSING_PINNED_THEOREMS")
    return {
        "status":"EXTERNAL_PROOFNET_AUDIT_COMPLETED",
        "n_original_math_pairs":len(rows),
        "source_sha_upstream_commit":SOURCE_COMMIT,
        "source_repository":SOURCE_REPO,
        "license":"Apache-2.0",
        "full_statement_and_lean_pair_verified":sum(x["original_source_replayed"] for x in rows),
        "raw_original_docs_verified_by_both":sum(
            x["raw_original_file_frontends"]["comparison_gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"
            for x in rows),
        "original_informal_statements_verified":sum(
            x["original_informal_statement_frontends"]["comparison_gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"
            for x in rows),
        "neutral_layout_only_wrapper_verified":sum(
            x["diagnostic_neutral_wrapper_frontends"]["comparison_gate"]=="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"
            for x in rows),
        "external_reference_lean_available":len(rows),
        "model_predictions_produced":0,
        "new_human_annotators":0,
        "new_double_blind_human_annotations":0,
        "proofnet_curated_reference_labeled_by_external_team":True,
        "human_semantic_fidelity_accuracy":"NOT_MEASURABLE_WITH_A_B_TYPE_SYSTEM",
        "semantic_transfer_verified":False,
        "source_reading_integrity":"VERIFIED",
        "no_new_model_training_or_paid_api":True,
        "time_seconds":round(time.perf_counter()-start,3),
        "rows":rows,
        "scientific_restrictions":"0 correct translations cannot be equated with 0 human-faithfulness accuracy: outputs are absent, not wrong formalizations.",
    }


def report_markdown(v:dict)->str:
    lines=[
        "# PROOFNET26 — vraie référence externe en langage mathématique",
        "",
        "## Résultat",
        "",
        f"- Problèmes appariés complets (NL + Lean) et liés au commit original : **{v['n_original_math_pairs']}/16**.",
        f"- Source originale valide avec empreinte Git : **{v['full_statement_and_lean_pair_verified']}/16**.",
        f"- Couverture A+B sur les énoncés informels originaux : **{v['original_informal_statements_verified']}/16**.",
        f"- Couverture après wrapper de disposition *sans aucune hypothèse ajoutée* : **{v['neutral_layout_only_wrapper_verified']}/16**.",
        f"- Références Lean préexistantes disponibles : **{v['external_reference_lean_available']}/16**.",
        "- Revue humaine de ProofNet-Verified : externe préexistante, impliquant des humains et une IA selon les auteurs.",
        "- Annotations humaines nouvelles demandées/obtenues pour Omega : **0**.",
        "- Mesure de fidélité aux intentions originales : **IMPOSSIBLE ici**. A/B ne produisent pas du Lean ; nous n'avons pas le droit de comparer des représentations non comparables.",
        "",
        "## Interprétation",
        "",
        "Le corpus présente des mathématiques universitaires (groupes, analyse, topologie, algèbre, etc.), ",
        "hors de la famille des fonctions finies modulaires acceptée par les parseurs A/B.",
        "Les références Lean ne sont **pas** des preuves exécutées localement par Omega : le projet source affirme les avoir vérifiées, mais notre CI n'exécute pas Lean.",
        "Aucun texte ni hypothèse n'a été réécrit pour le faire accepter.",
        "",
        "**Verdict : échec de couverture hors distribution**, pas de preuve de compréhension ni de score de fidélité. ",
        "Réussite d'ingestion immuable de paires mathématiques humaines complètes.",
        "",
        "## Sources appariées",
        "",
        "| Cas | Texte et Lean original | Couverture A/B |",
        "|---|---|---|",
    ]
    for x in v["rows"]:
        lines.append(
            f"| {x['index']} | [ProofNet-Verified]({x['external_source_url']}) "
            f"| {x['original_informal_statement_frontends']['comparison_gate']} |"
        )
    lines.extend([
        "",
        "## Prochain test utile",
        "",
        "Cibler une **sous-famille extérieure** dont le domaine et les quantificateurs "
        "sont explicitement identifiables, choisir une IR comparable au Lean de référence, "
        "mettre un contrôle de fidélité indépendant des mots de l'énoncé, et mesurer "
        "une couverture non nulle sur un **autre corpus**. Ne pas réutiliser ces 16 pour "
        "réentraîner/ajuster les parseurs puis annoncer une généralisation.",
        "",
        "Aucune modification de \`main\`, aucun service API payant, zéro certificat automatique.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--markdown",type=Path,required=True)
    parser.add_argument("--offline-dir",type=Path)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    failure=False
    try:
        output=evaluate(cache_dir=args.offline_dir)
    except Exception:
        failure=True
        output={"status":"EXPERIMENT_INCOMPLETE_NOT_A_SCIENTIFIC_RESULT",
                "exception":traceback.format_exc()}
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    if not failure:
        args.markdown.write_text(report_markdown(output),encoding="utf8")
    print("PROOFNET26_RESULT",output["status"],flush=True)
    if failure:
        sys.exit(1)


if __name__=="__main__":
    main()
