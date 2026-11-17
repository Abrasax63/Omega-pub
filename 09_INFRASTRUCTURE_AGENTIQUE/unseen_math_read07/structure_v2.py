#!/usr/bin/env python3
"""Generic structural Markdown math extractor; all results are unreviewed quotes."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from extract import ROOT, git_blob, parse_document

HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
PROOF = re.compile(r"^\s*(?:\*\*)?\s*(?:Preuve|Démonstration)\b", re.I)
NON_THEOREM = re.compile(r"non[-‑\s]?théorème", re.I)
THEOREM = re.compile(r"^\s*(?:théorème|énoncé|propriété|lemme|corollaire)\b", re.I)
DEFINE = re.compile(r"^\s*(?:définition|notations?)\b", re.I)
LIMIT = re.compile(r"^\s*(?:limites?|réserves?|précautions?)\b", re.I)
CAUTION = re.compile(
    r"(?:ne\s+peut\s+pas\s+conclure|n[’']est\s+pas\s+certifi[ée]|"
    r"ne\s+doit\s+pas|ne\s+constitue\s+pas|"
    r"n[’']est\s+pas\b|hypothèse\s+supplémentaire)", re.I
)


def headings(lines):
    result = []
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            result.append({"line": i, "level": len(m.group(1)), "heading": m.group(2)})
    return result


def blocks(lines):
    result, active = [], None
    for node in headings(lines):
        if node["level"] == 2:
            if active is not None:
                active["end"] = node["line"]-1
                result.append(active)
            active = {"heading": node["heading"], "start": node["line"],
                      "end": len(lines)-1, "subheads": []}
        elif active is not None:
            active["subheads"].append(node)
    if active is not None:
        result.append(active)
    return result


def extract_structures(raw: bytes, path: str) -> dict:
    if len(raw) > 150000:
        raise ValueError("source exceeds 150kB")
    lines = raw.decode("utf-8").splitlines()
    sha, items = git_blob(raw), []

    def emit(kind, section, a, b, scope):
        while a <= b and not lines[a].strip():
            a += 1
        while b >= a and not lines[b].strip():
            b -= 1
        if a > b:
            return
        quote = "\n".join(lines[a:b+1])
        if len(quote) > 7000:
            return
        items.append({
            "kind": kind, "section": section, "start_line": a+1,
            "end_line": b+1, "source_quote": quote, "source_blob": sha,
            "source_path": path, "scope": scope,
            "scientific_status": "CANDIDATE_UNREVIEWED_NOT_A_PROOF"
        })

    for sec in blocks(lines):
        h, a, b = sec["heading"], sec["start"], sec["end"]
        if NON_THEOREM.search(h):
            emit("NON_THEOREM_WARNING", h, a+1, b, "BLOCKED_INFERENCE_NOT_NEGATION_PROOF")
        elif THEOREM.match(h):
            end = next((j-1 for j in range(a+1,b+1) if PROOF.match(lines[j])), b)
            emit("THEOREM_STATEMENT_LITERAL", h, a+1, end, "HEADING_ONLY_NO_FORMAL_PROOF")
        elif DEFINE.match(h):
            emit("DEFINITION_LITERAL", h, a+1, b, "DEFINITION_SECTION_ONLY")
        elif LIMIT.match(h):
            emit("LIMITATION_LITERAL", h, a+1, b, "LIMITATION_SECTION_ONLY")
        else:
            for idx, sub in enumerate(sec["subheads"]):
                if re.search(r"multiplicit[ée]|poids|support|définition", sub["heading"], re.I):
                    next_end = sec["subheads"][idx+1]["line"]-1 if idx+1 < len(sec["subheads"]) else b
                    emit("DEFINITION_LITERAL", h+" > "+sub["heading"],
                         sub["line"]+1, next_end, "SUBHEADING_ONLY")

        for j in range(a+1, b+1):
            if CAUTION.search(lines[j]) and not PROOF.match(lines[j]):
                emit("LIMITATION_LITERAL", h, j, j, "EXPLICIT_CAUTION_TEXT_ONLY")

    for i, item in enumerate(items, 1):
        item["id"] = f"S{i:03d}"
    old = parse_document(raw, path)
    return {
        "status": "MARKDOWN_STRUCTURE_CANDIDATES_NOT_MATH_SEMANTICS",
        "source_path": path, "source_blob": sha, "source_lines": len(lines),
        "items": items,
        "legacy_explicit_conditionals": old["counts"]["CONDITIONAL_CANDIDATE"],
        "counts": {k: sum(x["kind"] == k for x in items)
                   for k in ("THEOREM_STATEMENT_LITERAL", "NON_THEOREM_WARNING",
                             "DEFINITION_LITERAL", "LIMITATION_LITERAL")}
    }


def verify_structure_output(raw: bytes, output: dict) -> list[str]:
    """Independent literal-range replay and structural type check."""
    lines = raw.decode("utf-8").splitlines()
    sec = blocks(lines)
    errors = []
    if output["source_blob"] != git_blob(raw) or output["source_lines"] != len(lines):
        errors.append("DOCUMENT_FINGERPRINT_MISMATCH")
    for item in output["items"]:
        a, b = item["start_line"], item["end_line"]
        if not isinstance(a, int) or not isinstance(b, int) or not 1 <= a <= b <= len(lines):
            errors.append(item["id"]+":BAD_SPAN")
            continue
        if "\n".join(lines[a-1:b]) != item["source_quote"] or item["source_blob"] != git_blob(raw):
            errors.append(item["id"]+":INVENTED_CITATION")
        parent = next((s for s in sec if s["start"] < a and b-1 <= s["end"]), None)
        if parent is None:
            errors.append(item["id"]+":MISSING_SECTION")
            continue
        k, head = item["kind"], parent["heading"]
        if k == "THEOREM_STATEMENT_LITERAL":
            if NON_THEOREM.search(head) or not THEOREM.match(head):
                errors.append(item["id"]+":FALSE_THEOREM_PROMOTION")
            if any(PROOF.match(t) for t in lines[a-1:b]):
                errors.append(item["id"]+":PROOF_INCLUDED")
        elif k == "NON_THEOREM_WARNING":
            if not NON_THEOREM.search(head):
                errors.append(item["id"]+":FALSE_WARNING")
        elif k == "DEFINITION_LITERAL":
            if not (DEFINE.match(head) or
                    any(n["line"] < a and re.search(r"multiplicit[ée]|poids|support|définition",
                                                  n["heading"], re.I) for n in parent["subheads"])):
                errors.append(item["id"]+":FALSE_DEFINITION")
        elif k == "LIMITATION_LITERAL":
            if not (LIMIT.match(head) or any(CAUTION.search(t) for t in lines[a-1:b])):
                errors.append(item["id"]+":FALSE_LIMITATION")
        else:
            errors.append(item["id"]+":UNKNOWN_TYPE")
    return errors


def run(path: Path, expected_blob: str | None = None) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked input")
    raw = path.read_bytes()
    if expected_blob is not None and git_blob(raw) != expected_blob:
        raise ValueError("heldout source changed after freeze")
    result = extract_structures(raw, path.as_posix())
    result["verification_errors"] = verify_structure_output(raw, result)
    result["citations_valid"] = not result["verification_errors"]
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--source-blob", type=str)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run(args.source, args.source_blob)
    data = json.dumps(report, indent=2, ensure_ascii=False)+"\n"
    if args.output:
        dest = args.output.resolve()
        if dest.is_relative_to(ROOT):
            p.error("report outside repository only")
        dest.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
