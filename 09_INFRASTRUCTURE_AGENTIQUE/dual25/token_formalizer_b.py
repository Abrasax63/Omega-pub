#!/usr/bin/env python3
"""DUAL25 formalizer B: token-stream grammar, independent of TYPED24 parsing.

The parser does not import typed24.adapter, its patterns, its choices or its
verdicts. This is ALGORITHMIC diversity only, not independent human authorship.
Any source outside this narrow grammar receives UNSUPPORTED or AMBIGUOUS.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
sys.path.insert(0,str(HERE.parent/"semantic22"))
from read import blob as git_blob, packetize, verify_packets
from checker import FiniteFunction

MAX_BYTES = 8192
LEX = re.compile(r"\s+|->|[0-9]+|[A-Za-zÀ-ÿ]+|[^\w\s]",re.UNICODE)
NAME = re.compile(r"# Fiche [A-Za-z0-9_-]{1,24}\Z")


class UnsupportedGrammar(Exception):
    pass


def tokens(line:str)->tuple[str,...]:
    if not isinstance(line,str) or not 0<len(line)<=350:
        raise UnsupportedGrammar("EMPTY_OR_OVERSIZED_LINE")
    result=[]
    pos=0
    for m in LEX.finditer(line):
        if pos != m.start():
            raise UnsupportedGrammar("TOKEN_GAP_OR_UNREADABLE_CHARACTER")
        pos=m.end()
        if not m.group().isspace():
            result.append(m.group())
    if pos!=len(line):
        raise UnsupportedGrammar("TOKENIZATION_INCOMPLETE")
    return tuple(result)


class Stream:
    def __init__(self, seq:tuple[str,...]):
        self.words=seq
        self.pos=0

    def consume(self, word:str)->None:
        if self.pos >= len(self.words) or self.words[self.pos]!=word:
            raise UnsupportedGrammar("UNEXPECTED_GRAMMAR_TOKEN")
        self.pos+=1

    def see(self)->str|None:
        return self.words[self.pos] if self.pos<len(self.words) else None

    def natural(self)->int:
        x=self.see()
        if x is None or not x.isascii() or not x.isdigit() or str(int(x))!=x:
            raise UnsupportedGrammar("NONCANONICAL_INTEGER")
        self.pos+=1
        return int(x)

    def finish(self)->None:
        if self.pos!=len(self.words):
            raise UnsupportedGrammar("TRAILING_UNPARSED_CONTENT")


def definition_ir(text:str)->dict:
    p=Stream(tokens(text))
    for t in ("Soit","f",":","Z","/"):
        p.consume(t)
    domain=p.natural()
    for t in ("Z","->","Z","/"):
        p.consume(t)
    codomain=p.natural()
    for t in ("Z",",","f","(","x",")","=","("):
        p.consume(t)
    a=p.natural()
    p.consume("*")
    p.consume("x")
    square=False
    if p.see()=="^":
        p.consume("^")
        p.consume("2")
        square=True
    p.consume("+")
    b=p.natural()
    for t in (")","mod"):
        p.consume(t)
    modulus=p.natural()
    p.consume(".")
    p.finish()
    if domain!=codomain or domain!=modulus:
        raise UnsupportedGrammar("MISSING_EQUAL_FINITE_DOMAIN_AND_CODOMAIN")
    try:
        f=FiniteFunction(modulus=domain,a=a,b=b,square=square)
    except ValueError as err:
        raise UnsupportedGrammar("OUTSIDE_BOUNDED_FINITE_FUNCTIONS") from err
    return {
        "type":"FINITE_MODULAR_MAP",
        "domain":{"kind":"Z_MOD_N","n":f.modulus},
        "codomain":{"kind":"Z_MOD_N","n":f.modulus},
        "expression":{
            "kind":"SQUARE_PLUS_CONST" if f.square else "AFFINE",
            "a":f.a,"b":f.b
        },
        "hypotheses":["2<=n<=64","0<=a,b<n","total_function"],
    }


SIMPLE = {
    ("f","est","injective","."):("INJ",None,"UNAMBIGUOUS"),
    ("La","fonction","f","est","injective","."):("INJ",None,"UNAMBIGUOUS"),
    ("The","function","f","is","injective","."):("INJ",None,"UNAMBIGUOUS"),
    ("f","est","surjective","."):("SURJ",None,"UNAMBIGUOUS"),
    ("f","admet","au","moins","un","point","fixe","."):
        ("FIX_EXISTS",None,"UNAMBIGUOUS"),
    ("Pour","tout","x",",","f","(","f","(","x",")",")","=","x","."):
        ("INVOL",None,"UNAMBIGUOUS"),
    ("f","est","une","bijection","."):("BIJ",None,"UNAMBIGUOUS"),
    # Standard French math usage = existential. A treats this as ambiguous.
    ("f","possède","un","point","fixe","."):
        ("FIX_EXISTS",None,"EXISTS_AT_LEAST_ONE"),
}


def claim_ir(text:str,definition:dict)->dict:
    seq=tokens(text)
    if seq in SIMPLE:
        kind,num,quant=SIMPLE[seq]
        return {"kind":kind,"value":num,"quantifier":quant}
    p=Stream(seq)
    if seq[:3]==("f","possède","exactement"):
        for w in ("f","possède","exactement"):
            p.consume(w)
        amount=p.natural()
        noun=("point","fixe") if amount<=1 else ("points","fixes")
        for w in (*noun,"."):
            p.consume(w)
        p.finish()
        return {"kind":"FIX_COUNT","value":amount,"quantifier":"EXACTLY"}
    if seq[:2]==("f","possède") and len(seq)>=6 and seq[2].isascii() and seq[2].isdigit():
        for w in ("f","possède"):
            p.consume(w)
        amount=p.natural()
        if amount==0:
            raise UnsupportedGrammar("BARE_ZERO_QUANTITY_WITHOUT_EXACTNESS")
        noun=("point","fixe") if amount==1 else ("points","fixes")
        for w in (*noun,"."):
            p.consume(w)
        p.finish()
        # B treats a bare cardinal as exact: *this cannot override A*.
        return {"kind":"FIX_COUNT","value":amount,"quantifier":"EXACTLY"}
    if seq[:5]==("L","'","image","de","f"):
        for w in ("L","'","image","de","f","compte","exactement"):
            p.consume(w)
        amount=p.natural()
        for w in ("éléments","."):
            p.consume(w)
        p.finish()
        return {"kind":"IMG_SIZE","value":amount,"quantifier":"EXACTLY"}
    if seq[:3]==("f","(","f"):
        for w in ("f","(","f","(","0",")",")","="):
            p.consume(w)
        number=p.natural()
        p.consume(".")
        p.finish()
        if number>=definition["domain"]["n"]:
            raise UnsupportedGrammar("NONCANONICAL_MODULAR_REPRESENTATIVE")
        return {
            "kind":"DOUBLE_AT_ZERO","value":number,
            "quantifier":"MODULAR_CANONICAL_REPRESENTATIVE",
        }
    raise UnsupportedGrammar("CLAIM_OUTSIDE_SECOND_TOKEN_GRAMMAR")


def parse(raw:bytes,*,expected_blob:str,source_path:str)->dict:
    if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:
        raise ValueError("UNSAFE_SOURCE_BYTES_OR_SIZE")
    if git_blob(raw)!=expected_blob:
        raise ValueError("SOURCE_BLOB_MISMATCH")
    def outcome(status:str,reason:str,*,claim=None,definition=None,line=None)->dict:
        return {
            "formalizer":"B_INDEPENDENT_TOKEN_GRAMMAR",
            "status":status,"reason":reason,
            "source_blob":expected_blob,"source_path":source_path,
            "typed_definition":definition,"typed_claim":claim,
            "claim_line":line,
            "human_semantic_equivalence":"NOT_ASSESSED",
            "automatic_certifications":0,"horn_rules":[],
        }
    if len(raw)<20:
        return outcome("UNSUPPORTED","SOURCE_TOO_SHORT")
    try:
        lines=raw.decode("utf8",errors="strict").splitlines()
    except UnicodeDecodeError:
        return outcome("UNSUPPORTED","BAD_UTF8")
    if not lines or not NAME.fullmatch(lines[0]):
        return outcome("UNSUPPORTED","DOCUMENT_TITLE_NOT_TYPED")
    if len(lines)<9 or lines[1]!="" or lines[2]!="## Définition" or lines[3]!="":
        return outcome("UNSUPPORTED","DEFINITION_SECTION_MISSING")
    if lines.count("## Définition")!=1 or lines.count("## Énoncé")!=1:
        return outcome("UNSUPPORTED","DUPLICATE_OR_MISSING_SECTIONS")
    split=lines.index("## Énoncé")
    if split<=3 or split+1>=len(lines):
        return outcome("UNSUPPORTED","DOCUMENT_SECTION_LAYOUT")
    if any(x.startswith("#") and i not in (0,2,split) for i,x in enumerate(lines)):
        return outcome("UNSUPPORTED","EXTRA_HEADING_OR_CONTEXT")
    definitions=[(i+1,x) for i,x in enumerate(lines[4:split],4) if x.strip()]
    claims=[(i+1,x) for i,x in enumerate(lines[split+1:],split+1) if x.strip()]
    if len(definitions)>1 or len(claims)>1:
        return outcome("AMBIGUOUS","MULTIPLE_DEFINITIONS_OR_CLAIMS")
    if len(definitions)!=1 or len(claims)!=1:
        return outcome("UNSUPPORTED","INCOMPLETE_FORMALIZATION")
    dline,dtext=definitions[0]
    cline,ctext=claims[0]
    try:
        inventory=packetize(raw,source_path)
        if verify_packets(raw,inventory):
            raise ValueError("PROVENANCE_PACKETS_DIFFER")
        scoped={n:p for p in inventory["packets"]
                for n in range(p["start_line"],p["end_line"]+1)}
        dp,cp=scoped.get(dline),scoped.get(cline)
        if (dp is None or cp is None
            or dp["section_path"][-1]!="Définition"
            or cp["section_path"][-1]!="Énoncé"
            or "BLOCKED" in dp["context_status"]
            or "BLOCKED" in cp["context_status"]):
            return outcome("UNSUPPORTED","UNSCOPED_SOURCE_SPANS")
        definition=definition_ir(dtext)
        claim=claim_ir(ctext,definition)
        return outcome("SINGLE_PROPOSAL","TOKEN_PARSER_EXACT_MATCH",
                       definition=definition,claim=claim,line=cline)
    except UnsupportedGrammar as err:
        return outcome("UNSUPPORTED",str(err))
