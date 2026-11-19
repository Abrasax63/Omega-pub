#!/usr/bin/env python3
"""Omega SEM22 -- exact, source-bound, read-only verifier of modular functions.

This is a CLOSED-LANGUAGE, finite exhaustive evaluator, not a general theorem
prover. It parses untrusted Markdown SOURCE instead of trusting a model's
answer or a benchmark's hidden oracle. Unknown constructions ABSTAIN.
No dynamic eval/exec, no LLM, no imports of frozen dataset labels.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

MAX_BYTES = 8192
MIN_MODULUS = 2
MAX_MODULUS = 64
MAX_CANDIDATES = 32

# Full matches, no fuzzy keyword detection or natural-language interpretation.
HEADER = re.compile(r"# Fiche ([A-Za-z0-9_-]{1,24})")
DEFINITION = re.compile(
    r"On travaille dans Z/([0-9]{1,2})Z\. On définit f\(x\) = "
    r"\(([0-9]{1,2})\*x(?:(\^2))? \+ ([0-9]{1,2})\) mod ([0-9]{1,2})\."
)
SIMPLE_CLAIMS = {
    "Proposition : f est injective.": "INJ",
    "Proposition : f est surjective.": "SURJ",
    "Proposition : f possède au moins un point fixe.": "FIX_EXISTS",
    "Proposition : pour tout x, f(f(x)) = x.": "INVOL",
}
PARAMETER_CLAIMS = (
    (re.compile(r"Proposition : l'image de f contient exactement ([0-9]{1,2}) éléments\."), "IMG_SIZE"),
    (re.compile(r"Proposition : f possède exactement ([0-9]{1,2}) (point fixe|points fixes)\."), "FIX_COUNT"),
    (re.compile(r"Proposition : f\(f\(0\)\) = ([0-9]{1,2})\."), "DOUBLE_AT_ZERO"),
)


@dataclass(frozen=True)
class FiniteFunction:
    modulus: int
    a: int
    b: int
    square: bool

    def __post_init__(self):
        if (type(self.modulus) is not int
            or type(self.a) is not int
            or type(self.b) is not int
            or not (MIN_MODULUS <= self.modulus <= MAX_MODULUS)
            or not (0 <= self.a < self.modulus and 0 <= self.b < self.modulus)):
            raise ValueError("UNSUPPORTED_FINITE_DEFINITION")

    def apply(self, x: int) -> int:
        # No eval(), sympy symbolic assumptions or float arithmetic.
        v = x*x if self.square else x
        return (self.a*v + self.b) % self.modulus

    def trace(self) -> tuple[int, ...]:
        return tuple(self.apply(i) for i in range(self.modulus))


def decode_source(raw: bytes) -> tuple[list[str], FiniteFunction]:
    if not isinstance(raw, bytes) or not (16 <= len(raw) <= MAX_BYTES):
        raise ValueError("SOURCE_SIZE_OR_TYPE_INVALID")
    try:
        text = raw.decode("utf8", errors="strict")
    except UnicodeDecodeError as e:
        raise ValueError("SOURCE_ENCODING_INVALID") from e
    lines = text.splitlines()
    if len(lines) < 9 or not HEADER.fullmatch(lines[0]):
        raise ValueError("UNKNOWN_SOURCE_LAYOUT")
    if (lines[1:4] != ["", "## Données", ""]
        or lines[5:8] != ["", "## Énoncé", ""]):
        raise ValueError("UNKNOWN_SOURCE_LAYOUT")
    d = DEFINITION.fullmatch(lines[4])
    if not d:
        raise ValueError("UNSUPPORTED_FUNCTION_SYNTAX")
    m, a, square, b, end_m = d.groups()
    if m != end_m:
        raise ValueError("INCONSISTENT_MODULI")
    f = FiniteFunction(int(m), int(a), int(b), bool(square))
    if len(lines) > MAX_CANDIDATES + 8:
        raise ValueError("TOO_MANY_CANDIDATE_LINES")
    return lines, f


def parse_predicate(text: str) -> tuple[str, int | None, str | None]:
    if text in SIMPLE_CLAIMS:
        return SIMPLE_CLAIMS[text], None, None
    for pattern, kind in PARAMETER_CLAIMS:
        m = pattern.fullmatch(text)
        if m:
            value = int(m.group(1))
            if kind == "FIX_COUNT":
                expected_plural = "point fixe" if value <= 1 else "points fixes"
                if m.group(2) != expected_plural:
                    return "UNSUPPORTED", None, "UNEXPECTED_SINGULAR_PLURAL"
            return kind, value, None
    return "UNSUPPORTED", None, "UNSUPPORTED_CLAIM_LANGUAGE"


def compute_verdict(f: FiniteFunction, kind: str, number: int | None) -> dict[str, Any]:
    vals = f.trace()
    n = f.modulus
    image = sorted(set(vals))
    missing = [i for i in range(n) if i not in image]
    fixed = [x for x,v in enumerate(vals) if x == v]
    collision = next(
        ((i,j,vals[i]) for i in range(n) for j in range(i+1,n)
         if vals[i] == vals[j]),
        None,
    )
    non_invol = next(
        ((i, f.apply(f.apply(i))) for i in range(n)
         if f.apply(f.apply(i)) != i),
        None,
    )
    observed = None
    expected = None
    witness: dict[str, Any] = {}
    if kind in ("INJ", "SURJ"):
        truth = collision is None if kind == "INJ" else not missing
        witness = ({"collision_x_y_image": list(collision)}
                   if kind == "INJ" and collision is not None else
                   {"missing_values": missing}
                   if kind == "SURJ" and missing else
                   {"image_values": image})
    elif kind == "FIX_EXISTS":
        truth = bool(fixed)
        witness = {"fixed_points": fixed}
    elif kind == "INVOL":
        truth = non_invol is None
        witness = ({"counterexample_x_and_f2x": list(non_invol)}
                   if non_invol else {"all_x_checked": n})
    elif kind == "IMG_SIZE":
        truth = len(image) == number
        observed, expected = len(image), number
        witness = {"image_values": image}
    elif kind == "FIX_COUNT":
        truth = len(fixed) == number
        observed, expected = len(fixed), number
        witness = {"fixed_points": fixed}
    elif kind == "DOUBLE_AT_ZERO":
        observed, expected = f.apply(f.apply(0)), number
        truth = observed == expected
        witness = {"f_0": f.apply(0), "f2_0": observed}
    else:
        raise ValueError("CHECKER_UNSUPPORTED_INTERNAL_KIND")
    return {
        "verdict": "TRUE" if truth else "FALSE",
        "method": "EXHAUSTIVE_MODULAR_ENUMERATION",
        "hypotheses": {
            "domain": f"Z/{n}Z", "codomain": f"Z/{n}Z",
            "a": f.a, "b": f.b, "square": f.square,
        },
        "trace": {"f_x_for_x_0_to_n_minus_1": list(vals)},
        "predicate": kind,
        "observed": observed, "claimed": expected,
        "witness": witness,
        "formal_theorem_certified": False,
        "generalizes_outside_finite_scope": False,
    }


def verify_source(raw: bytes, *, expected_blob: str, source_path: str) -> dict[str, Any]:
    # Integrity failure is an error, NOT an unchecked success.
    if not isinstance(expected_blob,str) or not re.fullmatch(r"[0-9a-f]{40}", expected_blob):
        raise ValueError("INVALID_EXPECTED_GIT_BLOB")
    actual = "blob " + str(len(raw)) + "\0"
    sha = hashlib.sha1(actual.encode("ascii") + raw).hexdigest()
    if sha != expected_blob:
        raise ValueError("SOURCE_BLOB_MISMATCH")
    if not isinstance(source_path,str) or not source_path:
        raise ValueError("SOURCE_PATH_REQUIRED")
    try:
        lines, f = decode_source(raw)
    except ValueError as e:
        return {
            "status": "UNSUPPORTED_SOURCE",
            "reason": str(e),
            "source_blob": expected_blob, "source_path": source_path,
            "results": [],
            "all_claims_checked": False,
            "auto_promotions": 0, "horn_rules": [], "theorems_certified": 0,
        }
    rows=[]
    for line_number in range(9,len(lines)+1):
        phrase = lines[line_number-1]
        kind, number, failure = parse_predicate(phrase)
        base = {
            "line":line_number,
            "literal":phrase,
            "source_blob":expected_blob,
            "source_path":source_path,
            "literal_sha256":hashlib.sha256(phrase.encode("utf8")).hexdigest(),
            "verification_scope":"FINITE_FUNCTIONS_SUPPORTED_LANGUAGE_ONLY",
        }
        if failure is not None:
            detail={"verdict":"INDETERMINATE","reason":failure,"formal_theorem_certified":False}
        else:
            detail=compute_verdict(f,kind,number)
        rows.append({**base, **detail})
    return {
        "status":"EVALUATED_FINITE_SCOPE",
        "source_blob":expected_blob,"source_path":source_path,
        "definition":lines[4],
        "function_table":list(f.trace()),
        "results":rows,
        "all_claims_checked":all(r["verdict"]!="INDETERMINATE" for r in rows),
        "auto_promotions":0,"horn_rules":[],"theorems_certified":0,
    }


def select_verified(
    evaluation: dict, requested_lines: list[int], *, require_true: bool=True
)->dict[str, Any]:
    """Reject unknown IDs, falsities and abstentions; source-bound choices only."""
    by_line = {item["line"]:item for item in evaluation.get("results",[])}
    if (not isinstance(requested_lines,list) or len(requested_lines)>3
        or any(type(x) is not int for x in requested_lines)
        or len(requested_lines)!=len(set(requested_lines))
        or not set(requested_lines).issubset(by_line)):
        raise ValueError("BAD_REQUESTED_SOURCE_LINES")
    accepted=[]; rejected=[]
    for line in requested_lines:
        result=by_line[line]
        if result["verdict"] == "TRUE":
            accepted.append(line)
        else:
            rejected.append({"line":line,"reason":result["verdict"]})
    return {
        "selected_true_lines": accepted,
        "suppressed":rejected,
        "source_blob":evaluation["source_blob"],
        "unverified_claims_promoted":0,
        "theorems_certified":0,
        "horn_rules":[],
    }
