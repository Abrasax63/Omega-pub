#!/usr/bin/env python3
"""Omega 09: uninterpreted mathematical iff and comparison-chain syntax.

Produces exact source-anchored fragments with a mandatory review gate.
No mathematical semantics, proof certification or Horn promotion.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from translate import ROOT, blob, safe_source, propose

HEAD = re.compile(r"^##\s+(.+?)\s*$")
CODE = re.compile(r"(?<!\x60)\x60([^\x60\n]+)\x60(?!\x60)")
OPS = re.compile(r"(<=|>=|≤|≥|≠|=|<|>)")
IFF = re.compile(r"\bsi\s+et\s+seulement\s+si\b", re.I)
NEGATIVE = re.compile(r"non[-‑\s]?théorème|limites?|contre[- ]exemple|barrière\s+de\s+généralisation", re.I)
PROOF = re.compile(r"^\s*\*\*(?:preuve|démonstration)\b", re.I)


def parse_chain(literal: str):
    if any(token in literal for token in ("<=>", "⇔", "→", "->", "\\", "⇒", "\n", chr(96))):
        return None
    pieces = OPS.split(literal)
    if len(pieces) < 3 or len(pieces) % 2 == 0:
        return None
    terms, operators = [p.strip() for p in pieces[::2]], pieces[1::2]
    if not all(terms) or len(terms) > 8 or len(literal) > 300:
        return None
    if any(";" in term or ":" in term or "\t" in term for term in terms):
        return None
    return terms, operators


def trim(line, lo, hi):
    while lo < hi and line[lo].isspace():
        lo += 1
    while hi > lo and line[hi-1].isspace():
        hi -= 1
    return lo, hi


def normalize(raw: bytes, source: str) -> dict:
    if len(raw) > 150000:
        raise ValueError("source too long")
    lines = raw.decode("utf-8").splitlines()
    section = "UNSECTIONED"
    items, blocked = [], []
    sha = blob(raw)

    def emit(kind, n, line, a, b, details):
        items.append({
            "id": "N"+str(len(items)+1).zfill(3),
            "kind": kind, "source_blob": sha, "source_path": source,
            "line": n, "source_quote": line,
            "section": section, "char_start": a, "char_end": b,
            "literal": line[a:b], "parsed": details,
            "status": "REVIEW_REQUIRED",
            "epistemic_status": "UNINTERPRETED_SYNTAX_NOT_THEOREM",
            "promotable": False,
        })

    old = propose(raw, source)
    for i, line in enumerate(lines, 1):
        h = HEAD.match(line)
        if h:
            section = h.group(1).strip()
            continue
        unsafe = bool(NEGATIVE.search(section)) or bool(PROOF.match(line))
        iffs = list(IFF.finditer(line))
        if len(iffs) == 1:
            m = iffs[0]
            a0, a1 = trim(line, 0, m.start())
            c0, c1 = trim(line, m.end(), len(line))
            if a1 > a0 and c1 > c0 and len(line) <= 600 and not unsafe:
                emit("BICONDITIONAL_SYNTAX", i, line, a0, c1, {
                    "left": line[a0:a1], "right": line[c0:c1],
                    "left_span": [a0, a1], "right_span": [c0, c1],
                    "connective_span": [m.start(), m.end()],
                    "connective": line[m.start():m.end()]
                })
            else:
                blocked.append({"line": i, "reason": "IFF_UNSAFE_OR_INCOMPLETE",
                                "source_quote": line, "source_blob": sha})
        elif len(iffs) > 1:
            blocked.append({"line": i, "reason": "MULTIPLE_BICONDITIONALS",
                            "source_quote": line, "source_blob": sha})
        for m in CODE.finditer(line):
            result = parse_chain(m.group(1))
            if result is None:
                continue
            terms, operators = result
            if unsafe:
                blocked.append({"line": i, "reason": "RELATION_IN_NON_THEOREM_OR_LIMIT",
                                "source_quote": line, "source_blob": sha,
                                "literal": m.group(1)})
                continue
            emit("RELATION_CHAIN_SYNTAX", i, line, m.start(1), m.end(1), {
                "terms": terms, "operators": operators,
                "parse": "SYNTACTIC_ORDER_ONLY",
            })
    return {
        "engine": "OMEGA_FORMAL_SKELETON_09",
        "source_blob": sha, "source_path": source,
        "items": items, "blocked": blocked,
        "legacy_conditional_count": len(old["proposals"]),
        "legacy_conditional_blocked": len(old["blocked"]),
        "horn_rules": [], "automatic_promotion_count": 0,
        "summary": {
            "typed_syntax_candidates": len(items),
            "biconditional_count": sum(x["kind"] == "BICONDITIONAL_SYNTAX" for x in items),
            "relation_chain_count": sum(x["kind"] == "RELATION_CHAIN_SYNTAX" for x in items),
            "blocked": len(blocked),
        },
    }


def independent_check(raw: bytes, output: dict) -> list[str]:
    """Replay source spans/relations independently of normalization function."""
    lines = raw.decode("utf-8").splitlines()
    issues = []
    if output.get("source_blob") != blob(raw) or output.get("horn_rules") or \
       output.get("automatic_promotion_count") != 0:
        issues.append("DOCUMENT_OR_GATE_FAILURE")
    for item in output.get("items", []):
        idx = item.get("line")
        if type(idx) is not int or not 1 <= idx <= len(lines):
            issues.append("BAD_LINE")
            continue
        line = lines[idx-1]
        a, b = item.get("char_start"), item.get("char_end")
        if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(line):
            issues.append("BAD_SPAN")
            continue
        if item.get("source_quote") != line or item.get("literal") != line[a:b] or \
           item.get("source_blob") != blob(raw):
            issues.append("FABRICATED_CITATION")
        if item.get("status") != "REVIEW_REQUIRED" or item.get("promotable") is not False:
            issues.append("UNSAFE_PROMOTION")
        heading = "UNSECTIONED"
        for preceding in lines[:idx-1]:
            m = HEAD.match(preceding)
            if m:
                heading = m.group(1).strip()
        if NEGATIVE.search(heading) or PROOF.match(line):
            issues.append("UNSAFE_CONTEXT")
        kind, parsed = item.get("kind"), item.get("parsed", {})
        if kind == "RELATION_CHAIN_SYNTAX":
            if not (a > 0 and b < len(line) and line[a-1] == chr(96) and line[b] == chr(96)):
                issues.append("NOT_EXACT_QUOTED_FORMULA")
            portions = OPS.split(line[a:b])
            if len(portions) < 3 or len(portions) % 2 == 0:
                issues.append("BAD_CHAIN")
            elif (parsed.get("terms") != [v.strip() for v in portions[::2]] or
                  parsed.get("operators") != portions[1::2] or
                  not all(v.strip() for v in portions[::2])):
                issues.append("INVENTED_OR_INVERTED_RELATION")
            if any(x in line[a:b] for x in ("<=>", "⇔", "→", "->")):
                issues.append("AMBIGUOUS_FORMULA")
        elif kind == "BICONDITIONAL_SYNTAX":
            ls, rs, cs = (parsed.get("left_span"), parsed.get("right_span"),
                          parsed.get("connective_span"))
            if not all(isinstance(v, list) and len(v) == 2 for v in (ls, rs, cs)):
                issues.append("BAD_IFF_SPANS")
                continue
            if not (a == ls[0] and ls[1] <= cs[0] < cs[1] <= rs[0] and b == rs[1]):
                issues.append("BAD_IFF_ORDER")
                continue
            if (line[ls[0]:ls[1]] != parsed.get("left") or
                line[rs[0]:rs[1]] != parsed.get("right") or
                line[cs[0]:cs[1]] != parsed.get("connective") or
                not IFF.fullmatch(parsed.get("connective", ""))):
                issues.append("INVENTED_IFF_CLAUSE")
        else:
            issues.append("UNKNOWN_KIND")
    for x in output.get("blocked", []):
        n = x.get("line")
        if type(n) is not int or not 1 <= n <= len(lines) or \
           x.get("source_quote") != lines[n-1] or x.get("source_blob") != blob(raw):
            issues.append("INVENTED_BLOCKER")
    return issues


def run(path: Path, expected_blob: str) -> dict:
    data = safe_source(path, expected_blob)
    out = normalize(data, path.as_posix())
    out["verification_errors"] = independent_check(data, out)
    out["citations_valid"] = not out["verification_errors"]
    if out["verification_errors"]:
        raise ValueError("independent syntax certificate invalid")
    return out


def export_to_horn(*args, **kwargs):
    raise PermissionError("UNREVIEWED_MATHEMATICAL_SKELETON_CANNOT_BE_CERTIFIED")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-blob", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.source, args.source_blob)
    data = json.dumps(report, ensure_ascii=False, indent=2)+"\n"
    if args.output:
        output = args.output.resolve()
        if output.is_relative_to(ROOT):
            parser.error("report outside repository")
        output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
