#!/usr/bin/env python3
"""TYPED24: source-first, narrow typed formalization with explicit ambiguity.

Reuses reader_bridge12/read.py, reader_bridge12/gate.py, and
semantic22/checker.py for exact finite calculation. This is deliberately
a NON-LLM grammar adapter and NOT a general natural language translator.
An inference model's favored candidate cannot override ambiguous wording.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import sys
from typing import Any

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
sys.path.insert(0,str(HERE.parent/"semantic22"))
from read import blob as git_blob, packetize, verify_packets
from gate import gate
from checker import FiniteFunction, compute_verdict

SOURCE_CAP=8192
DEFINITION = re.compile(
    r"Soit f : Z/([0-9]{1,2})Z -> Z/([0-9]{1,2})Z, "
    r"f\(x\) = \(([0-9]{1,2})\*x(\^2)? \+ ([0-9]{1,2})\) mod ([0-9]{1,2})\."
)
HEADER = re.compile(r"# Fiche [A-Za-z0-9_-]{1,24}")
EXACT_FIX = re.compile(r"f possède exactement (0|[1-9][0-9]?) (point fixe|points fixes)\.")
AMBIGUOUS_FIX_COUNT = re.compile(r"f possède ([1-9][0-9]?) (point fixe|points fixes)\.")
IMAGE_SIZE = re.compile(r"L'image de f compte exactement (0|[1-9][0-9]?) éléments\.")
DOUBLE_ZERO = re.compile(r"f\(f\(0\)\) = (0|[1-9][0-9]?)\.")
ACCEPTED_SIMPLE={
    "f est injective.":("INJ",None),
    "La fonction f est injective.":("INJ",None),
    "The function f is injective.":("INJ",None),
    "f est surjective.":("SURJ",None),
    "f admet au moins un point fixe.":("FIX_EXISTS",None),
    "Pour tout x, f(f(x)) = x.":("INVOL",None),
    "f est une bijection.":("BIJ",None),
}


def _status(status: str, reason: str, *, blob:str, source_path:str,
            definition=None, alternatives=None, claim_line=None,
            citation=None, extra=None)->dict:
    return {
        "status":status,"reason":reason,
        "source_blob":blob,"source_path":source_path,
        "typed_definition":definition,
        "interpretations":alternatives or [],
        "claim_line":claim_line,
        "source_citation":citation,
        "exact_verification_scope":"FINITE_MODULAR_FUNCTIONS_ONLY",
        "auto_promotions":0,"horn_rules":[],
        "formal_theorems_certified":0,
        **(extra or {}),
    }


def parse_source(raw:bytes,source_path:str)->tuple[dict,dict]:
    if not isinstance(raw,bytes) or len(raw)>SOURCE_CAP:
        raise ValueError("INVALID_SOURCE_SIZE_OR_TYPE")
    if len(raw)<20:
        return {"status":"INDETERMINATE","reason":"TOO_SHORT_FOR_COMPLETE_DOCUMENT"},{}
    try:
        lines=raw.decode("utf8",errors="strict").splitlines()
    except UnicodeDecodeError as e:
        raise ValueError("INVALID_SOURCE_UTF8") from e
    if not lines or not HEADER.fullmatch(lines[0]):
        return {"status":"INDETERMINATE","reason":"UNSUPPORTED_DOCUMENT_HEADER"},{}
    if sum(line=="## Définition" for line in lines)!=1 or sum(line=="## Énoncé" for line in lines)!=1:
        return {"status":"INDETERMINATE","reason":"MISSING_OR_DUPLICATED_SECTIONS"},{}
    di=lines.index("## Définition")
    ci=lines.index("## Énoncé")
    if di>=ci or any(
        line.startswith("#") and i not in (0,di,ci)
        for i,line in enumerate(lines)
    ):
        return {"status":"INDETERMINATE","reason":"UNKNOWN_DOCUMENT_STRUCTURE"},{}
    if any(line.strip() for line in lines[1:di]):
        return {"status":"INDETERMINATE","reason":"EXTRA_TEXT_OUTSIDE_SUPPORTED_SECTIONS"},{}
    decls=[(i+1,line) for i,line in enumerate(lines) if di<i<ci and line.strip()]
    claims=[(i+1,line) for i,line in enumerate(lines) if i>ci and line.strip()]
    if len(decls)>1:
        return {"status":"AMBIGUOUS","reason":"MULTIPLE_SOURCE_DEFINITIONS"},{}
    if len(claims)>1:
        return {"status":"AMBIGUOUS","reason":"MULTIPLE_SOURCE_CLAIMS"},{}
    if len(decls)!=1 or len(claims)!=1:
        return {"status":"INDETERMINATE","reason":"MISSING_DEFINITION_OR_CLAIM"},{}
    if any("\t" in line or len(line)>350 for line in lines):
        return {"status":"INDETERMINATE","reason":"UNSUPPORTED_SOURCE_FORMAT"},{}
    inv=packetize(raw,source_path)
    if verify_packets(raw,inv):
        raise ValueError("SOURCE_SPANS_NOT_REPLAYABLE")
    by_line={i:p for p in inv["packets"] for i in range(p["start_line"],p["end_line"]+1)}
    (dn,dtext),(cn,ctext)=decls[0],claims[0]
    defpacket=by_line.get(dn)
    claimpacket=by_line.get(cn)
    if (not defpacket or not claimpacket
        or defpacket["section_path"][-1]!="Définition"
        or claimpacket["section_path"][-1]!="Énoncé"
        or defpacket["context_status"]=="BLOCKED_SOURCE_CONTEXT"
        or claimpacket["context_status"]=="BLOCKED_SOURCE_CONTEXT"):
        return {"status":"INDETERMINATE","reason":"NOT_IN_ALLOWED_SOURCE_SECTION"},{}
    return {"status":"PARSED_SOURCE","reason":"SOURCE_SPANS_VERIFIED"},{
        "definition_line":dn,"definition_text":dtext,
        "claim_line":cn,"claim_text":ctext,
        "definition_packet":defpacket,"claim_packet":claimpacket,
    }


def parse_definition(text:str)->FiniteFunction|None:
    m=DEFINITION.fullmatch(text)
    if not m:
        return None
    src_n,dest_n,a,squared,b,mod=m.groups()
    # Refuse leading zeros and differing domain / codomain / expression modulus.
    fields=(src_n,dest_n,a,b,mod)
    if any(s!=str(int(s)) for s in fields):
        return None
    if src_n!=dest_n or src_n!=mod:
        return None
    try:
        return FiniteFunction(modulus=int(src_n),a=int(a),b=int(b),
                              square=bool(squared))
    except ValueError:
        return None


def parse_claim(text:str,f:FiniteFunction)->list[dict[str,Any]]:
    """Candidate ASTs; never choose among non-equivalent interpretations."""
    if text in ACCEPTED_SIMPLE:
        kind, n=ACCEPTED_SIMPLE[text]
        return [{"kind":kind,"value":n,"quantifier":"UNAMBIGUOUS"}]
    if text=="f possède un point fixe.":
        return [
            {"kind":"FIX_EXISTS","value":None,"quantifier":"EXISTS_AT_LEAST_ONE"},
            {"kind":"FIX_COUNT","value":1,"quantifier":"EXACTLY_ONE"},
        ]
    m=EXACT_FIX.fullmatch(text)
    if m:
        count=int(m.group(1))
        if m.group(2)!=("point fixe" if count<=1 else "points fixes"):
            return []
        return [{"kind":"FIX_COUNT","value":count,"quantifier":"EXACTLY"}]
    m=AMBIGUOUS_FIX_COUNT.fullmatch(text)
    if m:
        count=int(m.group(1))
        if m.group(2)!=("point fixe" if count==1 else "points fixes"):
            return []
        return [
            {"kind":"FIX_COUNT","value":count,"quantifier":"EXACTLY"},
            {"kind":"FIX_AT_LEAST","value":count,"quantifier":"AT_LEAST"},
        ]
    m=IMAGE_SIZE.fullmatch(text)
    if m:
        return [{"kind":"IMG_SIZE","value":int(m.group(1)),
                 "quantifier":"EXACTLY"}]
    m=DOUBLE_ZERO.fullmatch(text)
    if m:
        number=int(m.group(1))
        # In Z/nZ noncanonical representatives would be semantically distinct
        # from naive integer equality; do not silently normalize here.
        if number>=f.modulus:
            return []
        return [{"kind":"DOUBLE_AT_ZERO","value":number,
                 "quantifier":"MODULAR_CANONICAL_REPRESENTATIVE"}]
    return []


def typed_function(f:FiniteFunction)->dict:
    return {
        "type":"FINITE_MODULAR_MAP",
        "domain":{"kind":"Z_MOD_N","n":f.modulus},
        "codomain":{"kind":"Z_MOD_N","n":f.modulus},
        "expression":{"kind":"SQUARE_PLUS_CONST" if f.square else "AFFINE",
                      "a":f.a,"b":f.b},
        "hypotheses":["2<=n<=64","0<=a,b<n","total_function"],
    }


def verify_interpretation(f:FiniteFunction,claim:dict)->dict:
    kind,value=claim["kind"],claim["value"]
    if kind=="BIJ":
        inj=compute_verdict(f,"INJ",None)
        surj=compute_verdict(f,"SURJ",None)
        return {
            "verdict":"TRUE" if (inj["verdict"]=="TRUE" and surj["verdict"]=="TRUE") else "FALSE",
            "method":"EXHAUSTIVE_MODULAR_ENUMERATION",
            "checks":[inj,surj],
            "table":list(f.trace()),
            "scope":"BOTH_INJECTIVE_AND_SURJECTIVE_FINITE_MAP",
        }
    if kind=="FIX_AT_LEAST":
        trace=f.trace()
        fixes=[i for i,v in enumerate(trace) if i==v]
        return {
            "verdict":"TRUE" if len(fixes)>=value else "FALSE",
            "method":"EXHAUSTIVE_MODULAR_ENUMERATION",
            "table":list(trace),
            "fixed_points":fixes,
            "observed":len(fixes),
            "claimed_minimum":value,
        }
    out=compute_verdict(f,kind,value)
    return {
        "verdict":out["verdict"],
        "method":out["method"],
        "table":out["trace"]["f_x_for_x_0_to_n_minus_1"],
        "detail":out,
    }


def canonical_interpretation_key(x:dict)->tuple:
    return x["kind"],x["value"],x["quantifier"]


def evaluate(raw:bytes,*,expected_blob:str,source_path:str)->dict:
    if not isinstance(source_path,str) or not source_path:
        raise ValueError("MISSING_SOURCE_PATH")
    if git_blob(raw)!=expected_blob:
        raise ValueError("SOURCE_BLOB_MISMATCH")
    preliminary,items=parse_source(raw,source_path)
    if preliminary["status"]!="PARSED_SOURCE":
        return _status(preliminary["status"],preliminary["reason"],
                       blob=expected_blob,source_path=source_path)
    f=parse_definition(items["definition_text"])
    if f is None:
        return _status("INDETERMINATE","UNSUPPORTED_OR_UNTYPED_DEFINITION",
                       blob=expected_blob,source_path=source_path,
                       claim_line=items["claim_line"])
    candidates=parse_claim(items["claim_text"],f)
    if not candidates:
        return _status("INDETERMINATE","UNSUPPORTED_CLAIM_OR_MISSING_HYPOTHESES",
                       blob=expected_blob,source_path=source_path,
                       definition=typed_function(f),claim_line=items["claim_line"])
    alternatives=[
        {
            "typed_claim":candidate,
            "local_calculation":verify_interpretation(f,candidate),
            "citation_line":items["claim_line"],
        }
        for candidate in candidates
    ]
    # Even if all truth values agree for this PARTICULAR f, distinct semantics
    # can disagree on other functions. Equality of verdict != fidelity.
    keys={canonical_interpretation_key(c) for c in candidates}
    if len(keys)!=1:
        return _status("AMBIGUOUS","NON_EQUIVALENT_FORMALIZATIONS",
                       blob=expected_blob,source_path=source_path,
                       definition=typed_function(f),alternatives=alternatives,
                       claim_line=items["claim_line"],
                       citation={"line":items["claim_line"],
                                 "literal":items["claim_text"],
                                 "source_blob":expected_blob})
    model_data={
        "source_blob":expected_blob,
        "claims":[{
            "claim_id":"CTYPED1",
            "packet_id":items["claim_packet"]["packet_id"],
            "evidence":[{
                "role":"conclusion",
                "packet_id":items["claim_packet"]["packet_id"],
                "line":items["claim_line"],
                "literal":items["claim_text"],
            }],
        }],
    }
    guarded=gate(raw,source_path,model_data,provider="typed24-deterministic-no-LLM")
    if (guarded["accepted_count"]!=1 or guarded["rejected_count"]!=0
        or guarded["automatic_promotions"]!=0 or guarded["horn_rules"]):
        return _status("INDETERMINATE","READER12_SOURCE_GATE_REFUSED",
                       blob=expected_blob,source_path=source_path,
                       definition=typed_function(f),alternatives=alternatives,
                       claim_line=items["claim_line"])
    exact=alternatives[0]["local_calculation"]
    return _status(
        "VERIFIED_TRUE" if exact["verdict"]=="TRUE" else "VERIFIED_FALSE",
        "EXACT_SCOPE_ONLY_NOT_GENERAL_SEMANTIC_PROOF",
        blob=expected_blob,source_path=source_path,
        definition=typed_function(f),alternatives=alternatives,
        claim_line=items["claim_line"],
        citation={
            "reader12_status":guarded["accepted"][0]["status"],
            "semantic_fidelity_of_source":guarded["accepted"][0]["semantic_fidelity"],
            "verified_literal":guarded["accepted"][0]["evidence"][0],
        },
    )


def check_external_proposal(result:dict,proposal:dict)->dict:
    """Model-proposed typed claim is untrusted, cannot disambiguate the source."""
    if not isinstance(proposal,dict) or set(proposal)!={"source_blob","claim_line","typed_claim"}:
        return {"accepted":False,"reason":"INVALID_PROPOSAL_SCHEMA"}
    if proposal["source_blob"]!=result["source_blob"] or proposal["claim_line"]!=result["claim_line"]:
        return {"accepted":False,"reason":"PROVENANCE_OR_LINE_MISMATCH"}
    if result["status"] in ("AMBIGUOUS","INDETERMINATE","INVALID_SOURCE"):
        return {"accepted":False,"reason":"SOURCE_NOT_SEMANTICALLY_UNAMBIGUOUS"}
    if result["status"] not in ("VERIFIED_TRUE","VERIFIED_FALSE"):
        return {"accepted":False,"reason":"UNVERIFIED_RESULT"}
    if len(result["interpretations"])!=1 or proposal["typed_claim"]!=result["interpretations"][0]["typed_claim"]:
        return {"accepted":False,"reason":"MODEL_IR_NOT_ENTAILED_BY_EXACT_SOURCE"}
    return {"accepted":True,"reason":"MODEL_IR_MATCHES_TYPED_SOURCE_NOT_A_NEW_THEOREM",
            "auto_promotions":0,"formal_certifications":0}
