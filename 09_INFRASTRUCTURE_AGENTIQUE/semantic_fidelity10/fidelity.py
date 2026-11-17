#!/usr/bin/env python3
"""Omega 10: bounded arithmetic AST proposals, *never* certified theorems.

Only a strict ASCII subset of explicitly backticked scalar comparisons is
supported. Hypotheses from natural language are NOT extracted. Every source
formula stays in a review queue, not the reasoner's Horn database.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HEAD = re.compile(r"^##\s+(.+?)\s*$")
MATH = re.compile(r"(?<!\x60)\x60([^\x60\n]+)\x60(?!\x60)")
COMPARE = re.compile(r"(<=|>=|≤|≥|==|=|<|>)")
ATOMS = re.compile(r"^[A-Za-z0-9_+\-*() \t]+$")
ALLOWED_HEADING = re.compile(r"^(?:Théorème|Enoncé|Énoncé|Lemme|Propriété|Définition)\b", re.I)
UNSAFE_HEADING = re.compile(r"(?:preuve|limites?|non[-‑\s]?théorème|barrière|contre[- ]exemple|réfutation)", re.I)
MAX_BYTES = 150000


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class UnsupportedFormula(ValueError):
    pass


def encode_expr(node: ast.AST, budget: list[int], depth: int = 0) -> dict:
    budget[0] += 1
    if budget[0] > 32 or depth > 12:
        raise UnsupportedFormula("COMPLEXITY_BOUND")
    if isinstance(node, ast.Name):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,23}", node.id) or node.id.startswith("__"):
            raise UnsupportedFormula("UNKNOWN_SYMBOL_TYPE")
        return {"var": node.id}
    if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 100000:
        return {"int": node.value}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return {"unary": "+" if isinstance(node.op, ast.UAdd) else "-",
                "arg": encode_expr(node.operand, budget, depth+1)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        op = "+" if isinstance(node.op, ast.Add) else "-" if isinstance(node.op, ast.Sub) else "*"
        return {"op": op, "left": encode_expr(node.left, budget, depth+1),
                "right": encode_expr(node.right, budget, depth+1)}
    raise UnsupportedFormula("NON_ARITHMETIC_EXPRESSION")


def parse_restricted(code: str) -> dict:
    if len(code) > 150 or not code.isascii():
        raise UnsupportedFormula("NON_ASCII_OR_TOO_LONG")
    pieces = COMPARE.split(code)
    if len(pieces) < 3 or len(pieces) % 2 != 1 or len(pieces) > 9:
        raise UnsupportedFormula("NO_SUPPORTED_COMPARISON")
    expressions, operators = pieces[::2], pieces[1::2]
    if any(not value.strip() or not ATOMS.fullmatch(value) for value in expressions):
        raise UnsupportedFormula("UNSUPPORTED_EXPRESSION_TOKENS")
    out = []
    budget = [0]
    for expr in expressions:
        try:
            parsed = ast.parse(expr.strip(), mode="eval")
        except SyntaxError:
            raise UnsupportedFormula("INVALID_ARITHMETIC_SYNTAX") from None
        out.append(encode_expr(parsed.body, budget))
    normal = {"==": "=", "≤": "<=", "≥": ">="}
    op = [normal.get(x, x) for x in operators]
    symbols = set()
    def gather(t):
        if "var" in t:
            symbols.add(t["var"])
        for field in ("left", "right", "arg"):
            if field in t:
                gather(t[field])
    for term in out:
        gather(term)
    if len(symbols) > 4:
        raise UnsupportedFormula("TOO_MANY_UNTYPED_VARIABLES")
    return {
        "sort_model": "INTEGER_SCALAR_INTERPRETATION_ONLY",
        "terms": out, "ops": op,
        "variables": sorted(symbols),
        "operator_source": operators,
        "meaning": "SYNTAX_FORMALIZED_UNVERIFIED_DOMAIN",
    }


def source_candidates(data: bytes, source_path: str) -> dict:
    if len(data) > MAX_BYTES:
        raise ValueError("source oversized")
    lines = data.decode("utf-8").splitlines()
    sha = git_blob(data)
    section = "UNSECTIONED"
    recognized, abstentions, domain_records = [], [], []
    for line_no, line in enumerate(lines, 1):
        h = HEAD.match(line)
        if h:
            section = h.group(1).strip()
            continue
        if section.lower().startswith(("domaine", "hypothèses")) and line.strip():
            domain_records.append({"line": line_no, "literal": line,
                                   "review_status": "UNINTERPRETED_CONTEXT"})
        unsafe = bool(UNSAFE_HEADING.search(section))
        eligible = bool(ALLOWED_HEADING.match(section)) and not unsafe
        for match in MATH.finditer(line):
            formula = match.group(1)
            entry = {
                "source_blob": sha, "source_path": source_path,
                "line": line_no, "section": section,
                "source_quote": line, "char_start": match.start(1),
                "char_end": match.end(1), "literal": formula
            }
            if not eligible:
                abstentions.append({**entry, "reason": "OUT_OF_CLAIM_SECTION_OR_UNSAFE"})
                continue
            try:
                parsed = parse_restricted(formula)
            except UnsupportedFormula as e:
                abstentions.append({**entry, "reason": str(e)})
                continue
            recognized.append({
                **entry, "kind": "ARITHMETIC_RELATION_AST_CANDIDATE",
                "ast": parsed, "status": "REVIEW_REQUIRED",
                "domain_status": "NOT_SEMANTICALLY_DERIVED",
                "certification": "NONE",
                "promotable": False,
            })
    return {
        "engine": "OMEGA_SEMANTIC_FIDELITY_10_RESTRICTED",
        "source_path": source_path, "source_blob": sha,
        "source_lines": len(lines),
        "candidates": recognized, "abstentions": abstentions,
        "domain_context": domain_records,
        "horn_rules": [], "automatic_promotions": 0,
    }


def interpret_tree(tree: dict, vals: dict[str, int]) -> int:
    if "int" in tree:
        return tree["int"]
    if "var" in tree:
        return vals[tree["var"]]
    if "unary" in tree:
        a = interpret_tree(tree["arg"], vals)
        return a if tree["unary"] == "+" else -a
    x, y = interpret_tree(tree["left"], vals), interpret_tree(tree["right"], vals)
    if tree["op"] == "+":
        return x+y
    if tree["op"] == "-":
        return x-y
    if tree["op"] == "*":
        return x*y
    raise ValueError("unknown AST operator")


def interpret_relation(model: dict, vals: dict[str, int]) -> bool:
    z = [interpret_tree(t, vals) for t in model["terms"]]
    return all({
        "=": a == b, "<": a < b, ">": a > b,
        "<=": a <= b, ">=": a >= b
    }[op] for a,b,op in zip(z,z[1:],model["ops"]))


def independent_interpret_raw(formula: str, vals: dict[str, int]) -> bool:
    """Separate evaluator of original source, NOT using encoded AST.

    Python grammar here is a separate read of the raw source. Only the
    prevalidated small arithmetic language reaches this function.
    """
    piece = COMPARE.split(formula)
    left_right = piece[::2]
    ops = piece[1::2]
    def compute(src):
        node = ast.parse(src.strip(), mode="eval").body
        def visit(n):
            if isinstance(n, ast.Name):
                return vals[n.id]
            if isinstance(n, ast.Constant) and type(n.value) is int:
                return n.value
            if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
                num = visit(n.operand)
                return -num if isinstance(n.op, ast.USub) else num
            if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub, ast.Mult)):
                left, right = visit(n.left), visit(n.right)
                if isinstance(n.op, ast.Add):
                    return left + right
                if isinstance(n.op, ast.Sub):
                    return left - right
                return left * right
            raise ValueError("not permitted to evaluate")
        return visit(node)
    numbers = [compute(p) for p in left_right]
    for i, original_op in enumerate(ops):
        a, b = numbers[i:i+2]
        relation = {
            "=": a == b, "==": a == b, "<": a < b, ">": a > b,
            "<=": a <= b, "≤": a <= b, ">=": a >= b, "≥": a >= b
        }[original_op]
        if not relation:
            return False
    return True


def verify_candidate(raw: bytes, item: dict) -> dict:
    """Bidirectional test: exact citation + bounded finite interpretations.

    This checks operator faithfulness on [-2,2]^n, NOT universal validity
    or unmodeled domain hypotheses.
    """
    lines = raw.decode("utf-8").splitlines()
    n = item.get("line")
    if type(n) is not int or not 1 <= n <= len(lines):
        raise ValueError("SOURCE_LINE_INVALID")
    line = lines[n-1]
    a, b = item.get("char_start"), item.get("char_end")
    if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(line):
        raise ValueError("SOURCE_SPAN_INVALID")
    if item.get("source_blob") != git_blob(raw) or item.get("source_quote") != line or item["literal"] != line[a:b]:
        raise ValueError("SOURCE_QUOTE_NOT_EXACT")
    expected = parse_restricted(item["literal"])
    if item.get("ast") != expected or item.get("promotable") is not False or \
       item.get("status") != "REVIEW_REQUIRED":
        raise ValueError("AST_OR_SECURITY_CONTRACT_TAMPERED")
    vals = expected["variables"]
    trials = 0
    for values in itertools.product((-2,-1,0,1,2), repeat=len(vals)):
        lookup = dict(zip(vals, values))
        if interpret_relation(expected, lookup) != independent_interpret_raw(item["literal"], lookup):
            raise ValueError("COUNTERMODEL_AST_VS_SOURCE")
        trials += 1
    return {"passed": True, "finite_valuations_checked": trials,
            "boundary": "ONLY_BOUNDED_INTERPRETATIONS_AND_EXACT_SYNTAX"}


def run(path: Path, expected_blob: str) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("missing/symlinked/oversized file")
    raw = path.read_bytes()
    if git_blob(raw) != expected_blob:
        raise ValueError("SOURCE_FINGERPRINT_CHANGED")
    result = source_candidates(raw, path.as_posix())
    checks = [verify_candidate(raw, item) for item in result["candidates"]]
    result["verification"] = checks
    result["checked_all_candidates"] = len(checks) == len(result["candidates"]) and all(x["passed"] for x in checks)
    result["total_finite_valuations"] = sum(c["finite_valuations_checked"] for c in checks)
    return result


def promote_to_reasoner(*args, **kwargs):
    raise PermissionError("SCIENTIFIC_SEMANTIC_REVIEW_REQUIRED; NO_AUTOMATIC_HORN_IMPORT")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-blob", type=str, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.dumps(run(args.source, args.source_blob), ensure_ascii=False, indent=2)+"\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            parser.error("write reports outside repository only")
        dest.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
