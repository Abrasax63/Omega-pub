#!/usr/bin/env python3
"""A limited mathematical expression interpreter for an UNTRUSTED model answer.

Never calls eval/exec/compile or imports model-authored source. A small typed
AST expresses a candidate representation; the allowed names/functions are
generic primitives, not a selectable menu of prewritten algorithms.
"""
from __future__ import annotations
import ast

MAX_EXPR=350
MAX_NODES=55
MAX_NUMBER=1023

class UnsupportedExpression(ValueError):
    pass


def rank2(vectors: list[int]) -> int:
    """Rank over GF(2) as generic expression primitive; not reachability API."""
    if not isinstance(vectors,list) or len(vectors)>10 or any(
        type(x) is not int or x<0 or x>MAX_NUMBER for x in vectors
    ):
        raise UnsupportedExpression("RANK_REQUIRES_BOUNDED_INTEGER_LIST")
    arr=list(vectors)
    basis=[]
    for x in arr:
        v=x
        for row in basis:
            v=min(v,v^row)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def parse_expression(raw: str) -> ast.Expression:
    if not isinstance(raw,str) or not raw.strip() or len(raw)>MAX_EXPR:
        raise UnsupportedExpression("EMPTY_OR_OVERSIZED")
    # Python's parser silently discards trailing comments. For a strict
    # untrusted-model contract, reject all such extraneous source bytes.
    if any(ch in raw for ch in ("#", "\\n", "\\r", ";", "\\x00")):
        raise UnsupportedExpression("COMMENT_OR_EXTRA_SYNTAX_FORBIDDEN")
    try:
        tree=ast.parse(raw,mode="eval")
    except (SyntaxError,TypeError,ValueError):
        raise UnsupportedExpression("PARSE_ERROR") from None
    if len(list(ast.walk(tree)))>MAX_NODES:
        raise UnsupportedExpression("COMPLEXITY_LIMIT")
    allowed=(
        ast.Expression,ast.Name,ast.Load,ast.Constant,ast.List,
        ast.BinOp,ast.BitXor,ast.Add,ast.Call,ast.Compare,
        ast.Eq,ast.NotEq,ast.Gt,ast.GtE,ast.Lt,ast.LtE,
        ast.BoolOp,ast.And,ast.Or,ast.UnaryOp,ast.Not,
    )
    if any(not isinstance(node,allowed) for node in ast.walk(tree)):
        raise UnsupportedExpression("UNSAFE_OR_UNSUPPORTED_AST_NODE")
    for node in ast.walk(tree):
        if isinstance(node,ast.Name) and node.id not in (
            "moves","start","target","rank","popcount","len"
        ):
            raise UnsupportedExpression("NAME_NOT_ALLOWED")
        if isinstance(node,ast.Constant) and (
            type(node.value) is not int or not 0<=node.value<=MAX_NUMBER
        ):
            raise UnsupportedExpression("LITERAL_OUT_OF_SCOPE")
        if isinstance(node,ast.Call) and (
            not isinstance(node.func,ast.Name)
            or node.func.id not in ("rank","popcount","len")
            or len(node.args)!=1 or node.keywords
        ):
            raise UnsupportedExpression("INVALID_FUNCTION_CALL")
        if isinstance(node,ast.Compare) and len(node.ops)!=1:
            raise UnsupportedExpression("CHAINED_COMPARISON_FORBIDDEN")
        if isinstance(node,ast.List) and len(node.elts)>8:
            raise UnsupportedExpression("LIST_TOO_LARGE")
    return tree


def interpret(expr: str, *, moves: list[int], start: int, target: int) -> bool:
    root=parse_expression(expr)
    context={"moves":list(moves),"start":start,"target":target}
    operations=[0]

    def eval_node(node, depth=0):
        operations[0]+=1
        if operations[0]>80 or depth>12:
            raise UnsupportedExpression("EVALUATION_DEPTH_OR_BUDGET_LIMIT")
        if isinstance(node,ast.Expression):
            return eval_node(node.body,depth+1)
        if isinstance(node,ast.Name):
            if node.id not in context:
                raise UnsupportedExpression("FUNCTION_NAME_AS_VALUE")
            return context[node.id]
        if isinstance(node,ast.Constant):
            return node.value
        if isinstance(node,ast.List):
            return [eval_node(x,depth+1) for x in node.elts]
        if isinstance(node,ast.BinOp):
            a=eval_node(node.left,depth+1)
            b=eval_node(node.right,depth+1)
            if isinstance(node.op,ast.BitXor):
                if type(a)!=int or type(b)!=int:
                    raise UnsupportedExpression("BITWISE_XOR_REQUIRES_INTS")
                return a^b
            if isinstance(node.op,ast.Add):
                if type(a)==list and type(b)==list and len(a)+len(b)<=10:
                    return a+b
                raise UnsupportedExpression("ADD_ONLY_LIST_CONCAT")
        if isinstance(node,ast.Call):
            a=eval_node(node.args[0],depth+1)
            if node.func.id=="rank":
                return rank2(a)
            if node.func.id=="popcount":
                if type(a)!=int or a<0 or a>MAX_NUMBER:
                    raise UnsupportedExpression("BAD_POPCOUNT_ARGUMENT")
                return a.bit_count()
            if node.func.id=="len":
                if type(a)!=list:
                    raise UnsupportedExpression("BAD_LEN_ARGUMENT")
                return len(a)
        if isinstance(node,ast.Compare):
            a=eval_node(node.left,depth+1)
            b=eval_node(node.comparators[0],depth+1)
            if type(a) not in (int,bool) or type(b) not in (int,bool):
                raise UnsupportedExpression("NONSCALAR_COMPARISON")
            op=node.ops[0]
            if isinstance(op,ast.Eq): return a==b
            if isinstance(op,ast.NotEq): return a!=b
            if isinstance(op,ast.Lt): return a<b
            if isinstance(op,ast.LtE): return a<=b
            if isinstance(op,ast.Gt): return a>b
            if isinstance(op,ast.GtE): return a>=b
        if isinstance(node,ast.BoolOp):
            vals=[eval_node(item,depth+1) for item in node.values]
            if any(type(x) is not bool for x in vals):
                raise UnsupportedExpression("BOOL_OP_REQUIRES_BOOLEANS")
            return all(vals) if isinstance(node.op,ast.And) else any(vals)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Not):
            a=eval_node(node.operand,depth+1)
            if type(a) is not bool:
                raise UnsupportedExpression("NOT_REQUIRES_BOOL")
            return not a
        raise UnsupportedExpression("UNKNOWN_AST_SEMANTICS")

    if type(start)!=int or type(target)!=int or type(moves)!=list:
        raise UnsupportedExpression("INVALID_DOMAIN_TYPES")
    if not all(type(x) is int and 0<=x<=MAX_NUMBER for x in [start,target,*moves]):
        raise UnsupportedExpression("INPUT_OUT_OF_SCOPE")
    ans=eval_node(root)
    if type(ans) is not bool:
        raise UnsupportedExpression("MUST_RETURN_BOOLEAN")
    return ans


def extract_expression(raw_reply: str) -> str:
    """No hidden repairs. The model must produce exactly one EXPR: line."""
    if not isinstance(raw_reply,str) or not raw_reply.strip():
        raise UnsupportedExpression("EMPTY_REPLY")
    lines=raw_reply.strip().splitlines()
    if len(lines)!=1 or not lines[0].startswith("EXPR: "):
        raise UnsupportedExpression("NOT_ONE_EXPRESSION_LINE")
    expression=lines[0][6:].strip()
    parse_expression(expression)
    return expression
