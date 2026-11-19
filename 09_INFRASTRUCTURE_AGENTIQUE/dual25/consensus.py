#!/usr/bin/env python3
"""DUAL25: compare typed A/B proposals, never claim human fidelity from consensus.

Trust model: A and B are algorithmically distinct, but they share their author,
the source and the finite exact checker. Therefore this gate can only prove a
LOCAL contract agreement and exact mathematical correctness of that contract.
It cannot certify the original human statement's intended semantics.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"typed24"))
sys.path.insert(0,str(HERE.parent/"semantic22"))
from adapter import evaluate as formalizer_a, check_external_proposal
from token_formalizer_b import parse as formalizer_b
from checker import FiniteFunction, compute_verdict
from read import blob as git_blob


def agreement_key(claim:dict)->tuple:
    """Compare quantifier as part of the AST, not just a truth value."""
    if not isinstance(claim,dict) or set(claim)!={"kind","value","quantifier"}:
        raise ValueError("NONCANONICAL_TYPED_PREDICATE_SCHEMA")
    kind=claim["kind"]
    number=claim["value"]
    quant=claim["quantifier"]
    if (not isinstance(kind,str) or not isinstance(quant,str)
        or (number is not None and type(number) is not int)):
        raise ValueError("INVALID_TYPED_CLAIM_FIELDS")
    return (kind,number,quant)


def exact_from_typed(definition:dict,claim:dict)->str:
    """Common SEM22 arithmetic, independent of the A/B language frontends."""
    if (definition.get("type")!="FINITE_MODULAR_MAP"
        or definition["domain"] != definition["codomain"]
        or definition["domain"]["kind"]!="Z_MOD_N"
        or definition["expression"]["kind"] not in ("AFFINE","SQUARE_PLUS_CONST")):
        raise ValueError("UNSUPPORTED_TYPED_MATH_DOMAIN")
    n=definition["domain"]["n"]
    expr=definition["expression"]
    f=FiniteFunction(n,expr["a"],expr["b"],
                     expr["kind"]=="SQUARE_PLUS_CONST")
    kind,value,_=agreement_key(claim)
    if kind=="BIJ":
        both=(compute_verdict(f,"INJ",None)["verdict"]=="TRUE"
              and compute_verdict(f,"SURJ",None)["verdict"]=="TRUE")
        return "TRUE" if both else "FALSE"
    if kind=="FIX_AT_LEAST":
        if type(value) is not int or value<0:
            raise ValueError("INVALID_POINT_COUNT_MINIMUM")
        count=sum(f.apply(x)==x for x in range(n))
        return "TRUE" if count>=value else "FALSE"
    if kind not in ("INJ","SURJ","FIX_EXISTS","INVOL","IMG_SIZE","FIX_COUNT","DOUBLE_AT_ZERO"):
        raise ValueError("UNKNOWN_TYPED_PREDICATE")
    return compute_verdict(f,kind,value)["verdict"]


def counterinterpretation_witness(alternatives:list[dict])->dict|None:
    """A real counterexample proves non-equivalence, not the correct reading.

    The finite search is deliberately bounded. No witness found never means
    equivalent; return unknown. Statements may differ outside this family.
    """
    if not isinstance(alternatives,list) or len(alternatives)<2:
        return None
    claims=[x["typed_claim"] for x in alternatives]
    for a in claims:
        agreement_key(a)
    for n in range(2,9):
        for square in (False,True):
            for coeff in range(n):
                for const in range(n):
                    definition={
                        "type":"FINITE_MODULAR_MAP",
                        "domain":{"kind":"Z_MOD_N","n":n},
                        "codomain":{"kind":"Z_MOD_N","n":n},
                        "expression":{
                            "kind":"SQUARE_PLUS_CONST" if square else "AFFINE",
                            "a":coeff,"b":const,
                        },
                    }
                    truths=tuple(exact_from_typed(definition,c) for c in claims)
                    if len(set(truths))>1:
                        return {
                            "finding":"FINITE_COUNTEREXAMPLE_TO_EQUIVALENCE",
                            "n":n,"a":coeff,"b":const,"square":square,
                            "interpretation_truths":list(truths),
                            "f_values":[
                                (coeff*(x*x if square else x)+const)%n
                                for x in range(n)
                            ],
                            "does_not_prove_original_author_intent":True,
                        }
    return {
        "finding":"NO_COUNTEREXAMPLE_FOUND_WITHIN_BOUNDED_SEARCH",
        "searched":"n=2..8, affine and quadratic with 0<=a,b<n",
        "equivalence_status":"UNKNOWN",
    }


def reconcile(a:dict,b:dict,*,raw:bytes,expected_blob:str,source_path:str)->dict:
    if git_blob(raw)!=expected_blob:
        raise ValueError("SOURCE_INTEGRITY_FAILURE")
    if any(x.get("source_blob")!=expected_blob or x.get("source_path")!=source_path for x in (a,b)):
        raise ValueError("CROSS_FORMALIZER_SOURCE_DRIFT")
    base={
        "source_blob":expected_blob,"source_path":source_path,
        "A_status":a["status"],"B_status":b["status"],
        "A_typed_definition":a["typed_definition"],
        "B_typed_definition":b["typed_definition"],
        "A_claim_candidates":[x["typed_claim"] for x in a["interpretations"]],
        "B_claim_candidate":b["typed_claim"],
        "A_claim_line":a["claim_line"],"B_claim_line":b["claim_line"],
        "human_intention_gold":"MISSING_INDEPENDENT_ANNOTATION",
        "human_fidelity_certified":False,
        "mechanical_agreement_is_not_human_semantic_equivalence":True,
        "automatic_certifications":0,"horn_rules":[],
    }
    if a["status"]=="AMBIGUOUS" or b["status"]=="AMBIGUOUS":
        return {
            **base,"gate":"WITHHELD_AMBIGUOUS",
            "reason":"SOURCE_OR_FORMALIZATION_HAS_MULTIPLE_VALID_READINGS",
            "non_equivalence_witness":counterinterpretation_witness(a["interpretations"]),
            "ready_for_human_review":True,
        }
    if a["status"] not in ("VERIFIED_TRUE","VERIFIED_FALSE"):
        return {
            **base,"gate":"WITHHELD_UNSUPPORTED",
            "reason":"A_HAS_NO_SINGLE_SOURCE_SUPPORTED_FORMALIZATION",
            "ready_for_human_review":True,
        }
    if b["status"]!="SINGLE_PROPOSAL":
        return {
            **base,"gate":"WITHHELD_ONE_FORMALIZER_ONLY",
            "reason":"B_COULD_NOT_PARSE_SOURCE",
            "ready_for_human_review":True,
        }
    if a["source_citation"] is None or a["source_citation"].get("reader12_status")!="QUARANTINE_SOURCE_ANCHORED_UNREVIEWED":
        return {
            **base,"gate":"WITHHELD_PROVENANCE",
            "reason":"A_NO_VERIFIED_LITERAL_CITATION",
            "ready_for_human_review":True,
        }
    if b["claim_line"]!=a["claim_line"]:
        return {
            **base,"gate":"WITHHELD_SOURCE_SPAN_DISAGREEMENT",
            "reason":"DIFFERENT_LITERAL_LINE_REFERENCES",
            "ready_for_human_review":True,
        }
    if b["typed_definition"]!=a["typed_definition"]:
        return {
            **base,"gate":"WITHHELD_DEFINITION_DISAGREEMENT",
            "reason":"DOMAIN_CODOMAIN_OR_FUNCTION_DIFFER",
            "ready_for_human_review":True,
        }
    if len(a["interpretations"])!=1:
        return {
            **base,"gate":"WITHHELD_AMBIGUOUS",
            "reason":"A_NON_UNIQUE_FORMALIZATION",
            "ready_for_human_review":True,
        }
    Aclaim=a["interpretations"][0]["typed_claim"]
    if agreement_key(Aclaim)!=agreement_key(b["typed_claim"]):
        return {
            **base,"gate":"WITHHELD_CLAIM_DISAGREEMENT",
            "reason":"QUANTIFIER_OR_PREDICATE_DIFFER",
            "ready_for_human_review":True,
        }
    proposal={"source_blob":expected_blob,"claim_line":b["claim_line"],
              "typed_claim":b["typed_claim"]}
    if not check_external_proposal(a,proposal)["accepted"]:
        return {
            **base,"gate":"WITHHELD_FAILED_SOURCE_PROPOSAL",
            "reason":"MODEL_PROPOSAL_NOT_ENTAILED_BY_ORIGINAL_SOURCE",
            "ready_for_human_review":True,
        }
    exact=exact_from_typed(a["typed_definition"],b["typed_claim"])
    if exact != a["interpretations"][0]["local_calculation"]["verdict"]:
        raise ValueError("EXACT_SEM22_CALCULUS_DID_NOT_AGREE")
    if a["status"] != ("VERIFIED_TRUE" if exact=="TRUE" else "VERIFIED_FALSE"):
        raise ValueError("VERDICT_VS_FORMALIZATION_INCONSISTENT")
    return {
        **base,
        "gate":"AGREED_LOCAL_CONTRACT_AWAITING_HUMAN",
        "reason":"STRUCTURALLY_MATCHED_WITH_EXACT_FINITE_VERDICT_ONLY",
        "exact_finite_verdict":exact,
        "source_citation_in_quarantine":a["source_citation"],
        "ready_for_human_review":True,
        "human_fidelity_certified":False,
    }


def inspect(raw:bytes,*,expected_blob:str,source_path:str)->dict:
    a=formalizer_a(raw,expected_blob=expected_blob,source_path=source_path)
    b=formalizer_b(raw,expected_blob=expected_blob,source_path=source_path)
    return reconcile(a,b,raw=raw,expected_blob=expected_blob,source_path=source_path)
