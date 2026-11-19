#!/usr/bin/env python3
"""A finite, non-executing expression DSL for model-proposed representations.

Never eval or exec model responses. A model proposes numeric letter weights and
a boolean formula over a fixed feature vocabulary. The vocabulary is provided
in the model prompt, limiting any claim of autonomous creativity.
"""
from __future__ import annotations

import json

STATS = (
    "length", "sum", "min_prefix", "max_prefix", "min_suffix",
    "max_suffix", "count_open", "count_close", "first_weight",
    "last_weight", "num_changes",
)
COMPARATORS = frozenset(("eq", "ne", "gt", "ge", "lt", "le"))
LOGICAL = frozenset(("and", "or"))
MAX_NODES = 31
MAX_DEPTH = 8


class InvalidProposal(ValueError):
    pass


def parse_proposal(raw: str) -> dict:
    if not isinstance(raw,str) or len(raw)>6000:
        raise InvalidProposal("RESPONSE_NOT_BOUNDED_TEXT")
    try:
        value=json.loads(raw)
    except (ValueError,TypeError):
        raise InvalidProposal("RESPONSE_NOT_EXACT_JSON")
    if not isinstance(value,dict) or set(value)!={"weights","predicate","idea"}:
        raise InvalidProposal("ROOT_FIELDS_MISMATCH")
    idea=value["idea"]
    weights=value["weights"]
    if not isinstance(idea,str) or not 1<=len(idea)<=500:
        raise InvalidProposal("INVALID_IDEA_TEXT")
    if not isinstance(weights,dict) or set(weights)!={"(",")"} or any(
        type(v) is not int or not -2<=v<=2 for v in weights.values()
    ):
        raise InvalidProposal("INVALID_REPRESENTATION_WEIGHTS")
    count=[0]

    def walk(node,depth,needed):
        if depth>MAX_DEPTH:
            raise InvalidProposal("AST_TOO_DEEP")
        if not isinstance(node,dict):
            raise InvalidProposal("AST_NODE_NOT_OBJECT")
        count[0]+=1
        if count[0]>MAX_NODES:
            raise InvalidProposal("AST_TOO_LARGE")
        if needed=="number":
            if set(node)=={"const"} and type(node["const"]) is int and -100<=node["const"]<=100:
                return
            if set(node)=={"feature"} and node["feature"] in STATS:
                return
            raise InvalidProposal("INVALID_NUMERIC_NODE")
        op=node.get("op")
        if op in COMPARATORS and set(node)=={"op","left","right"}:
            walk(node["left"],depth+1,"number")
            walk(node["right"],depth+1,"number")
            return
        if op in LOGICAL and set(node)=={"op","args"}:
            args=node["args"]
            if not isinstance(args,list) or not 2<=len(args)<=4:
                raise InvalidProposal("INVALID_LOGICAL_ARITY")
            for arg in args:
                walk(arg,depth+1,"bool")
            return
        if op=="not" and set(node)=={"op","arg"}:
            walk(node["arg"],depth+1,"bool")
            return
        raise InvalidProposal("INVALID_BOOLEAN_NODE")
    walk(value["predicate"],0,"bool")
    return value


def characteristics(word: str, weights: dict) -> tuple[dict,int]:
    """Compute each feature explicitly from the proposed numeric mapping."""
    if not isinstance(word,str) or len(word)>128 or any(x not in "()" for x in word):
        raise ValueError("OUTSIDE_BINARY_BRACKET_SCOPE")
    values=[weights[x] for x in word]
    prefixes=[0]
    for v in values:
        prefixes.append(prefixes[-1]+v)
    suffixes=[0]
    for v in reversed(values):
        suffixes.append(suffixes[-1]+v)
    stats={
        "length":len(values),
        "sum":sum(values),
        "min_prefix":min(prefixes),
        "max_prefix":max(prefixes),
        "min_suffix":min(suffixes),
        "max_suffix":max(suffixes),
        "count_open":word.count("("),
        "count_close":word.count(")"),
        "first_weight":values[0] if values else 0,
        "last_weight":values[-1] if values else 0,
        "num_changes":sum(word[i]!=word[i-1] for i in range(1,len(word))),
    }
    # Number of input symbols visited while computing all features; not a
    # comparable instruction or CPU count against the optimized baseline.
    return stats,len(word)


def execute_proposal(proposal: dict, word: str) -> tuple[bool,int]:
    stats,visits=characteristics(word,proposal["weights"])

    def calc(node):
        if "const" in node:
            return node["const"]
        if "feature" in node:
            return stats[node["feature"]]
        op=node["op"]
        if op=="and":
            return all(calc(x) for x in node["args"])
        if op=="or":
            return any(calc(x) for x in node["args"])
        if op=="not":
            return not calc(node["arg"])
        left,right=calc(node["left"]),calc(node["right"])
        if op=="eq":
            return left==right
        if op=="ne":
            return left!=right
        if op=="ge":
            return left>=right
        if op=="gt":
            return left>right
        if op=="le":
            return left<=right
        if op=="lt":
            return left<right
        raise AssertionError("INVALID_ACCEPTED_AST")
    return bool(calc(proposal["predicate"])),visits
