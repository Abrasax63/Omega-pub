#!/usr/bin/env python3
"""Omega 08: source-anchored syntax proposal, NOT a proof or Horn rule generator.

The only recognized syntax is a literal one-line 'Si ... alors ...'.
Both sides are UNINTERPRETED_TEXT. Even correctly extracted proposals remain
REVIEW_REQUIRED; there is no path here for automatic rule promotion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # repo root: source at repo/09_INFRASTRUCTURE_AGENTIQUE/.../
ROOT = HERE.parent.parent
START = re.compile(r"^\s*(?:[-*]\s*)?Si\b", re.I)
IF_THEN = re.compile(r"^\s*(?:[-*]\s*)?Si\b\s+(.*?)\s*,?\s*\balors\b\s+(.+?)\s*$", re.I)
HEADING = re.compile(r"^(#{2,3})\s+(.+)$")
NEGATIVE = re.compile(r"non[-‑\s]?théorème|limites?|contre[- ]exemple|hypothèse\s+manquante", re.I)
PROOF = re.compile(r"preuve|démonstration", re.I)
NESTED = re.compile(r"\b(?:si|supposons|sauf si|à moins que)\b", re.I)
RESTRICTION = re.compile(r"\b(?:seulement si|si et seulement si|sinon|sauf|à moins que)\b", re.I)


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def safe_source(path: Path, expected_blob: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked source")
    if len(expected_blob) != 40 or not re.fullmatch(r"[a-f0-9]{40}", expected_blob):
        raise ValueError("missing immutable source SHA")
    if path.stat().st_size > 150000:
        raise ValueError("oversized source")
    data = path.read_bytes()
    if blob(data) != expected_blob:
        raise ValueError("source changed after freeze")
    return data


def propose(raw: bytes, source_path: str) -> dict:
    if len(raw) > 150000:
        raise ValueError("oversized input")
    lines = raw.decode("utf-8").splitlines()
    sha = blob(raw)
    section = "UNSECTIONED"
    output, blocked = [], []
    for i, line in enumerate(lines, 1):
        heading = HEADING.match(line)
        if heading:
            if len(heading.group(1)) == 2:
                section = heading.group(2).strip()
            continue
        if not START.match(line):
            continue
        cause = None
        if NEGATIVE.search(section) or PROOF.search(section):
            cause = "UNSAFE_SECTION"
        matched = IF_THEN.match(line)
        if matched is None:
            cause = cause or "NO_EXPLICIT_SAME_LINE_THEN"
        elif NESTED.search(matched.group(1)) or RESTRICTION.search(line):
            cause = cause or "NESTED_OR_RESTRICTED_CONNECTIVE"
        elif not matched.group(1).strip() or not matched.group(2).strip():
            cause = cause or "EMPTY_CLAUSE"
        elif line.count("alors") > 1:
            cause = cause or "MULTIPLE_THEN"
        if cause is not None:
            blocked.append({
                "line": i, "source_blob": sha, "source_quote": line,
                "section": section, "reason": cause,
                "disposition": "BLOCKED_NO_LOGICAL_NODE",
            })
            continue
        antecedent = matched.group(1)
        consequent = matched.group(2)
        # Exact character indices are independent of unicode normalization.
        a0, a1 = matched.span(1)
        c0, c1 = matched.span(2)
        output.append({
            "id": "P"+str(len(output)+1).zfill(3),
            "source_path": source_path, "source_blob": sha, "line": i,
            "source_quote": line, "section": section,
            "relation": "IMPLICATION_SYNTAX_ONLY",
            "antecedent": {"type": "UNINTERPRETED_TEXT", "literal": antecedent,
                            "char_start": a0, "char_end": a1},
            "consequent": {"type": "UNINTERPRETED_TEXT", "literal": consequent,
                            "char_start": c0, "char_end": c1},
            "status": "REVIEW_REQUIRED",
            "scientific_status": "NOT_FORMALIZED_NOT_CERTIFIED",
            "promotable": False,
        })
    return {
        "engine": "OMEGA_TRANSLATION_GATE_08",
        "epistemic_status": "UNREVIEWED_SYNTAX_PROPOSALS_ONLY",
        "source_path": source_path, "source_blob": sha, "source_lines": len(lines),
        "proposals": output, "blocked": blocked,
        "horn_rules": [], "automatic_promotion_count": 0,
    }


def independently_verify(raw: bytes, result: dict) -> list[str]:
    """Replay exact quotation and logical order without invoking propose()."""
    lines = raw.decode("utf-8").splitlines()
    errors = []
    if result.get("source_blob") != blob(raw):
        errors.append("CORRUPT_SOURCE")
    if result.get("horn_rules") or result.get("automatic_promotion_count") != 0:
        errors.append("UNREVIEWED_PROMOTION")
    seen = set()
    for p in result.get("proposals", []):
        n = p.get("line")
        if type(n) is not int or not 1 <= n <= len(lines):
            errors.append("INVALID_LINE")
            continue
        if (p.get("source_quote") != lines[n-1] or p.get("source_blob") != blob(raw) or
                p.get("promotable") is not False or p.get("status") != "REVIEW_REQUIRED"):
            errors.append("BAD_PROVENANCE_OR_GATE")
        if n in seen:
            errors.append("DUPLICATE_LINE")
        seen.add(n)
        line = lines[n-1]
        parts = []
        for key in ("antecedent", "consequent"):
            part = p.get(key, {})
            lo, hi = part.get("char_start"), part.get("char_end")
            if (type(lo) is not int or type(hi) is not int or
                    not 0 <= lo < hi <= len(line)):
                errors.append("INVALID_CHAR_RANGE")
                parts.append("")
                continue
            exact = line[lo:hi]
            if exact != part.get("literal") or part.get("type") != "UNINTERPRETED_TEXT":
                errors.append("INVENTED_OR_NORMALIZED_TEXT")
            parts.append(exact)
        if len(parts) == 2:
            a, c = parts
            # Verify the connector by inspecting *only* text between the
            # two cited spans. No possibility of reordering.
            if not START.match(line) or not re.search(r"\balors\b", line[
                p["antecedent"]["char_end"]:p["consequent"]["char_start"]], re.I):
                errors.append("INVALID_CONNECTIVE")
            if NESTED.search(a) or RESTRICTION.search(line):
                errors.append("DANGEROUS_OR_NESTED_FORM")
        if NEGATIVE.search(p.get("section", "")) or PROOF.search(p.get("section", "")):
            errors.append("UNSAFE_SECTION_PROMOTION")
    for b in result.get("blocked", []):
        n = b.get("line")
        if type(n) is not int or not 1 <= n <= len(lines):
            errors.append("BLOCKED_INVALID_LINE")
        elif b.get("source_quote") != lines[n-1] or b.get("source_blob") != blob(raw):
            errors.append("BLOCKED_INVENTED_LINE")
        if b.get("disposition") != "BLOCKED_NO_LOGICAL_NODE":
            errors.append("BLOCKED_PROMOTED")
    return errors


def run(path: Path, expected_blob: str) -> dict:
    raw = safe_source(path, expected_blob)
    result = propose(raw, path.as_posix())
    errors = independently_verify(raw, result)
    result["verification_errors"] = errors
    result["literal_integrity_passed"] = not errors
    if errors:
        raise ValueError("certificate of exact syntax failed")
    return result


def export_to_horn(*args, **kwargs):
    """Deliberately impossible: independent human semantic review required."""
    raise PermissionError("UNREVIEWED_TRANSLATION_CANNOT_ENTER_HORN_ENGINE")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--source-blob", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run(args.source, args.source_blob)
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output.resolve()
        if output.is_relative_to(ROOT):
            p.error("report destination must be outside repository")
        output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
