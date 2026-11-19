#!/usr/bin/env python3
"""Finite, typed interpreter for untrusted LLM mathematics. Never eval/exec."""
from __future__ import annotations
import ast
import math


class InvalidExpression(ValueError):
    pass


DOMAIN_NAMES={
    "modular_orbit":frozenset(("start","target","step","modulus")),
    "closed_interval_overlap":frozenset(("a","b","c","d")),
}
FUNCS=frozenset(("gcd","min","max"))
ALLOWED=(
    ast.Expression,ast.Name,ast.Load,ast.Constant,
    ast.BinOp,ast.Add,ast.Sub,ast.Mod,ast.BoolOp,ast.And,ast.Or,
    ast.UnaryOp,ast.Not,ast.USub,ast.UAdd,
    ast.Compare,ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,
    ast.Call,
)


def parse_raw_reply(raw:str,domain:str):
    """Returns None only for exact abstention; otherwise validated AST."""
    if domain=="unsupported":
        if raw=="ABSTAIN":
            return None
        raise InvalidExpression("UNSUPPORTED_FAMILY_MUST_ABSTAIN")
    if domain not in DOMAIN_NAMES:
        raise InvalidExpression("UNKNOWN_DOMAIN")
    if not isinstance(raw,str) or not 0<len(raw)<=400:
        raise InvalidExpression("EMPTY_OR_OVERSIZED_RAW_REPLY")
    if raw=="ABSTAIN":
        return None
    if any(c in raw for c in ("\n","\r","#",";","\x00")):
        raise InvalidExpression("MULTILINE_OR_COMMENT")
    if not raw.startswith("EXPR: "):
        raise InvalidExpression("NOT_EXACT_PREFIX_OR_MARKDOWN")
    expression=raw[6:]
    try:
        node=ast.parse(expression,mode="eval")
    except (ValueError,SyntaxError,TypeError):
        raise InvalidExpression("PARSER_REJECTED") from None
    nodes=list(ast.walk(node))
    if len(nodes)>80 or any(not isinstance(n,ALLOWED) for n in nodes):
        raise InvalidExpression("UNSAFE_OR_OVERCOMPLEX_AST")
    names=DOMAIN_NAMES[domain]
    for n in nodes:
        if isinstance(n,ast.Constant) and (type(n.value)!=int or not 0<=n.value<=64):
            raise InvalidExpression("FORBIDDEN_LITERAL")
        if isinstance(n,ast.Name) and n.id not in names|FUNCS:
            raise InvalidExpression("FORBIDDEN_VARIABLE_OR_FUNCTION")
        if isinstance(n,ast.Call) and (
            not isinstance(n.func,ast.Name)
            or n.func.id not in FUNCS or len(n.args)!=2 or n.keywords
        ):
            raise InvalidExpression("FORBIDDEN_FUNCTION_INVOCATION")
        if isinstance(n,ast.Compare) and (
            len(n.ops)!=1 or len(n.comparators)!=1
        ):
            raise InvalidExpression("CHAINED_COMPARISONS_FORBIDDEN")
    return node


def interpret(tree,case:dict,domain:str)->bool:
    if domain not in DOMAIN_NAMES:
        raise InvalidExpression("UNREGISTERED_DOMAIN")
    variables={name:case[name] for name in DOMAIN_NAMES[domain]}
    if any(type(v)!=int or abs(v)>64 for v in variables.values()):
        raise InvalidExpression("INPUT_OUT_OF_SCOPE")
    counter=[0]

    def numeric(x):
        if type(x)!=int or not -4096<=x<=4096:
            raise InvalidExpression("NONINT_OR_HUGE_NUMBER")
        return x

    def visit(n,depth=0):
        counter[0]+=1
        if counter[0]>128 or depth>22:
            raise InvalidExpression("COST_LIMIT")
        if isinstance(n,ast.Expression):
            return visit(n.body,depth+1)
        if isinstance(n,ast.Constant):
            return numeric(n.value)
        if isinstance(n,ast.Name):
            if n.id not in variables:
                raise InvalidExpression("FUNCTION_AS_VALUE")
            return numeric(variables[n.id])
        if isinstance(n,ast.UnaryOp):
            v=visit(n.operand,depth+1)
            if isinstance(n.op,ast.Not):
                if type(v)!=bool:raise InvalidExpression("NOT_NEEDS_BOOLEAN")
                return not v
            v=numeric(v)
            if isinstance(n.op,ast.USub):return numeric(-v)
            if isinstance(n.op,ast.UAdd):return v
        if isinstance(n,ast.BinOp):
            a=numeric(visit(n.left,depth+1))
            b=numeric(visit(n.right,depth+1))
            if isinstance(n.op,ast.Add):return numeric(a+b)
            if isinstance(n.op,ast.Sub):return numeric(a-b)
            if isinstance(n.op,ast.Mod):
                if b==0:raise InvalidExpression("MODULO_BY_ZERO")
                return numeric(a%b)
        if isinstance(n,ast.Call):
            a=numeric(visit(n.args[0],depth+1))
            b=numeric(visit(n.args[1],depth+1))
            fn=n.func.id
            if fn=="gcd":return numeric(math.gcd(a,b))
            if fn=="min":return min(a,b)
            if fn=="max":return max(a,b)
        if isinstance(n,ast.Compare):
            a=numeric(visit(n.left,depth+1))
            b=numeric(visit(n.comparators[0],depth+1))
            op=n.ops[0]
            if isinstance(op,ast.Eq):return a==b
            if isinstance(op,ast.NotEq):return a!=b
            if isinstance(op,ast.Lt):return a<b
            if isinstance(op,ast.LtE):return a<=b
            if isinstance(op,ast.Gt):return a>b
            if isinstance(op,ast.GtE):return a>=b
        if isinstance(n,ast.BoolOp):
            values=[visit(x,depth+1) for x in n.values]
            if any(type(x)!=bool for x in values):
                raise InvalidExpression("BOOLEAN_OPERAND_NOT_BOOL")
            if isinstance(n.op,ast.And):return all(values)
            if isinstance(n.op,ast.Or):return any(values)
        raise InvalidExpression("FORBIDDEN_EVALUATION_NODE")

    value=visit(tree)
    if type(value)!=bool:
        raise InvalidExpression("MUST_RETURN_BOOLEAN")
    return value


def check_on_cases(raw:str,domain:str,cases:list[dict],*,max_witnesses=1)->dict:
    """Safe finite check, with a single exact witness or abstention status."""
    try:
        tree=parse_raw_reply(raw,domain)
    except InvalidExpression as err:
        return {"status":"PARSE_REJECTED","error":str(err),"checked":0,
                "correct":0,"wrong":0,"counterexample":None}
    if tree is None:
        return {"status":"ABSTAIN","error":None,"checked":0,
                "correct":0,"wrong":0,"counterexample":None}
    if domain=="unsupported":
        raise AssertionError("UNSUPPORTED_DOMAIN_HAS_TREE")
    expected_key="reachable" if domain=="modular_orbit" else "overlap"
    correct=wrong=0
    first=None
    for c in cases:
        try:
            observed=interpret(tree,c,domain)
        except InvalidExpression as err:
            return {"status":"EVALUATION_REJECTED","error":str(err),
                    "checked":correct+wrong,"correct":correct,"wrong":wrong,
                    "counterexample":None}
        truth=c[expected_key]
        if type(truth)!=bool:raise AssertionError("SOURCE_GOLD_BAD")
        if observed==truth:correct+=1
        else:
            wrong+=1
            if first is None and max_witnesses:
                first={"id":c["id"],"inputs":{k:v for k,v in c.items()
                    if k not in ("reachable","overlap","id")},
                    "expected":truth,"observed":observed}
    return {
        "status":"MATCHES_FINITE_CASES" if wrong==0 else "FALSIFIED",
        "error":None,"checked":len(cases),"correct":correct,"wrong":wrong,
        "counterexample":first,
    }
