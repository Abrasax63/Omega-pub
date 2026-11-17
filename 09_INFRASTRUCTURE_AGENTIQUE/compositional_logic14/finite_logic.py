#!/usr/bin/env python3
"""Omega 14: safe compositional FOL mini-AST and two finite-model evaluators.

No general FOL theorem prover: this searches structures with <=2 individuals and
<=12 ground atoms. A found countermodel is conditional on the fidelity of the
AST translation, which this module deliberately DOES NOT certify.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re

MAX_DOMAIN=2
MAX_ATOMS=12
MAX_NODES=100
MAX_DEPTH=12
MAX_PREMISES=12
VAR_NAMES=frozenset(("x","y"))
ATOM_NAME=re.compile(r"^[a-z][a-z0-9_]{0,49}$")
CONSTANT_NAME=re.compile(r"^[A-Z][A-Za-z0-9_]{0,49}$")


class LogicError(ValueError):
    pass


def sha(value):
    return hashlib.sha256(json.dumps(
        value,ensure_ascii=False,sort_keys=True,separators=(",",":")
    ).encode("utf-8")).hexdigest()


def validate(ast,variables=frozenset(),metadata=None,level=0):
    """Only strongly typed compositional operators, scope-checked variables.

    Metadata is a shared accumulator for predicates and named constants.
    """
    if metadata is None:
        metadata={"predicates":{},"constants":set(),"nodes":0}
    metadata["nodes"]+=1
    if metadata["nodes"]>MAX_NODES or level>MAX_DEPTH:
        raise LogicError("FORMULA_COMPLEXITY_LIMIT")
    if not isinstance(ast,dict):
        raise LogicError("FORMULA_NOT_OBJECT")
    op=ast.get("op")
    if op=="atom":
        if set(ast)!={"op","pred","args"}:
            raise LogicError("ATOM_FIELDS")
        pred,args=ast["pred"],ast["args"]
        if not isinstance(pred,str) or not ATOM_NAME.fullmatch(pred):
            raise LogicError("INVALID_PREDICATE")
        if not isinstance(args,list) or len(args) not in (1,2):
            raise LogicError("INVALID_ARITY")
        arities=metadata["predicates"]
        if pred in arities and arities[pred]!=len(args):
            raise LogicError("PREDICATE_ARITY_MISMATCH")
        arities[pred]=len(args)
        for term in args:
            if not isinstance(term,str):
                raise LogicError("INVALID_TERM")
            if term in VAR_NAMES:
                if term not in variables:
                    raise LogicError("FREE_VARIABLE")
            elif CONSTANT_NAME.fullmatch(term):
                metadata["constants"].add(term)
            else:
                raise LogicError("TERM_NOT_VARIABLE_OR_CONSTANT")
        return metadata
    if op=="not":
        if set(ast)!={"op","arg"}:
            raise LogicError("NEGATION_FIELDS")
        return validate(ast["arg"],variables,metadata,level+1)
    if op in ("and","or"):
        if set(ast)!={"op","args"} or not isinstance(ast["args"],list):
            raise LogicError("CONNECTIVE_FIELDS")
        if not 2<=len(ast["args"])<=6:
            raise LogicError("CONNECTIVE_ARITY")
        for child in ast["args"]:
            validate(child,variables,metadata,level+1)
        return metadata
    if op=="implies":
        if set(ast)!={"op","if","then"}:
            raise LogicError("IMPLICATION_FIELDS")
        validate(ast["if"],variables,metadata,level+1)
        validate(ast["then"],variables,metadata,level+1)
        return metadata
    if op in ("forall","exists"):
        if set(ast)!={"op","var","body"}:
            raise LogicError("QUANTIFIER_FIELDS")
        var=ast["var"]
        if var not in VAR_NAMES or var in variables:
            raise LogicError("BOUND_VARIABLE_INVALID_OR_SHADOWED")
        return validate(ast["body"],variables|{var},metadata,level+1)
    raise LogicError("UNSUPPORTED_EXPRESSION")


def evaluate(ast,ground,domain,env=None):
    """Solver interpreter, independent of the LLM and its prompt."""
    env=env or {}
    op=ast["op"]
    if op=="atom":
        terms=tuple(env.get(x,x) for x in ast["args"])
        return bool(ground[(ast["pred"],terms)])
    if op=="not":
        return not evaluate(ast["arg"],ground,domain,env)
    if op=="and":
        return all(evaluate(x,ground,domain,env) for x in ast["args"])
    if op=="or":
        return any(evaluate(x,ground,domain,env) for x in ast["args"])
    if op=="implies":
        return not evaluate(ast["if"],ground,domain,env) or evaluate(
            ast["then"],ground,domain,env)
    if op=="forall":
        return all(evaluate(ast["body"],ground,domain,{**env,ast["var"]:v})
                   for v in domain)
    if op=="exists":
        return any(evaluate(ast["body"],ground,domain,{**env,ast["var"]:v})
                   for v in domain)
    raise LogicError("INTERNAL_UNSUPPORTED_OPERATOR")


def verify_independently(ast,truths,domain,bindings=None):
    """Second, structurally independent evaluator for a returned finite witness."""
    bindings=bindings or {}
    tag=ast["op"]
    if tag=="atom":
        k=(ast["pred"],tuple(bindings[x] if x in bindings else x for x in ast["args"]))
        return k in truths
    if tag=="not":
        return verify_independently(ast["arg"],truths,domain,bindings) is False
    if tag=="and":
        results=[verify_independently(x,truths,domain,bindings) for x in ast["args"]]
        return False not in results
    if tag=="or":
        results=[verify_independently(x,truths,domain,bindings) for x in ast["args"]]
        return True in results
    if tag=="implies":
        a=verify_independently(ast["if"],truths,domain,bindings)
        b=verify_independently(ast["then"],truths,domain,bindings)
        return (not a) or b
    if tag=="forall":
        for x in domain:
            nxt=dict(bindings)
            nxt[ast["var"]]=x
            if not verify_independently(ast["body"],truths,domain,nxt):
                return False
        return True
    if tag=="exists":
        for x in domain:
            nxt=dict(bindings)
            nxt[ast["var"]]=x
            if verify_independently(ast["body"],truths,domain,nxt):
                return True
        return False
    raise LogicError("INVALID_REPLAY_NODE")


def finite_counterexample(clauses,goal):
    if not isinstance(clauses,list) or len(clauses)>MAX_PREMISES or goal is None:
        return {"status":"UNDETERMINED","reason":"MISSING_OR_OVERSIZED_FORMULAE"}
    meta={"predicates":{},"constants":set(),"nodes":0}
    try:
        for rule in clauses:
            validate(rule,metadata=meta)
        validate(goal,metadata=meta)
    except LogicError as e:
        return {"status":"UNDETERMINED","reason":"INVALID_AST:"+str(e)}
    constants=sorted(meta["constants"])
    if len(constants)>MAX_DOMAIN or not meta["predicates"]:
        return {"status":"UNDETERMINED","reason":"OUTSIDE_DOMAIN_OR_NO_PREDICATES"}
    total=0
    valid=0
    for size in range(max(len(constants),1),MAX_DOMAIN+1):
        extra=["anonymous"+str(i) for i in range(size-len(constants))]
        domain=constants+extra
        relation_atoms=[
            (name,combination)
            for name,arity in sorted(meta["predicates"].items())
            for combination in itertools.product(domain,repeat=arity)
        ]
        if len(relation_atoms)>MAX_ATOMS:
            return {"status":"UNDETERMINED","reason":"GROUND_ATOM_LIMIT"}
        for bits in itertools.product((False,True),repeat=len(relation_atoms)):
            total+=1
            assignment=dict(zip(relation_atoms,bits))
            if not all(evaluate(rule,assignment,domain) for rule in clauses):
                continue
            valid+=1
            if evaluate(goal,assignment,domain):
                continue
            true_facts={name for name,value in assignment.items() if value}
            # A different interpreter must reproduce premises TRUE and goal FALSE.
            replayed=all(verify_independently(rule,true_facts,domain) for rule in clauses)
            goal_false=not verify_independently(goal,true_facts,domain)
            if not replayed or not goal_false:
                raise LogicError("WITNESS_REPLAY_DISAGREEMENT")
            return {
                "status":"FINITE_WITNESS_REPLAYED",
                "reason":"BOUNDED_FINITE_COUNTERMODEL_CONDITIONAL_ON_AST",
                "domain":domain,"true_atoms":[
                    {"pred":name,"args":list(args)} for name,args in sorted(true_facts)
                ],
                "atoms_in_domain":len(relation_atoms),
                "assignments_examined":total,
                "models_satisfying_premises_seen":valid,
                "premises_replayed":replayed,
                "goal_false_replayed":goal_false,
                "ast_sha256":sha({"premises":clauses,"goal":goal}),
                "semantic_fidelity_of_translation":"UNVERIFIED",
                "scientific_certification":False,
            }
    return {
        "status":"UNDETERMINED",
        "reason":"NO_COUNTEREXAMPLE_WITHIN_FINITE_BOUND",
        "assignments_examined":total,
        "models_satisfying_premises_seen":valid,
        "semantic_fidelity_of_translation":"UNVERIFIED",
        "scientific_certification":False,
    }
