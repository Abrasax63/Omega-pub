#!/usr/bin/env python3
"""Source-first *syntax* extraction from an unseen Markdown math card.

No ML, no source-name table, no generated formal rule, and no certification.
A candidate is not a sound logical premise/conclusion until externally reviewed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # adjusted below if needed
ROOT = Path(__file__).resolve().parent.parent.parent
IF = re.compile(r"^\s*(?:-\s*)?(?:si\b|supposons\b)", re.IGNORECASE)
THEN = re.compile(r"\balors\b", re.IGNORECASE)
SECTION = re.compile(r"^##\s+(.*)$")
PROOF = re.compile(r"^\s*(?:\*\*)?(?:preuve|démonstration|remarque|historique)\b", re.IGNORECASE)
IF_WORD = re.compile(r"\b(?:si|supposons)\b", re.IGNORECASE)
BLOCKED = re.compile(r"^(?:#|\s*\*\*Preuve|\s*\*\*Démonstration)", re.IGNORECASE)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def parse_document(raw: bytes, name: str) -> dict:
    """Extract bounded *literal* spans. All fields are substrings of citations."""
    if len(raw) > 150000:
        raise ValueError("source exceeds 150kB safety cap")
    body = raw.decode("utf-8")
    lines = body.splitlines()
    section = "AVANT_SECTIONS"
    candidates: list[dict] = []
    assumed_context = False
    i = 0
    while i < len(lines):
        line = lines[i]
        h = SECTION.match(line)
        if h:
            section = h.group(1)
            assumed_context = False
            i += 1
            continue
        # The 'si' clauses in prose not at the start of a line are not promoted.
        marker = IF.match(line)
        if marker and not PROOF.match(line):
            start = i
            cond = [line]
            then_at = None
            then_match = THEN.search(line)
            if then_match:
                then_at = i
                cond = [line[:then_match.start()]]
            else:
                for j in range(i+1, min(i+11, len(lines))):
                    nextline = lines[j]
                    if SECTION.match(nextline) or nextline.startswith("# ") or PROOF.match(nextline):
                        break
                    if IF.match(nextline):
                        break  # nested/fresh hypothesis: never bind to preceding 'supposons'
                    m = THEN.search(nextline)
                    if m:
                        then_at = j
                        cond = lines[i:j]+[nextline[:m.start()]]
                        break
            if then_at is not None:
                m = THEN.search(lines[then_at])
                assert m is not None
                tail = lines[then_at][m.end():].strip()
                end = then_at
                consequence = tail
                if not consequence:
                    for k in range(then_at+1, min(then_at+5, len(lines))):
                        if SECTION.match(lines[k]) or PROOF.match(lines[k]) or IF.match(lines[k]):
                            break
                        if lines[k].strip():
                            consequence = lines[k].strip()
                            end = k
                            break
                if consequence:
                    quoted = "\n".join(lines[start:end+1])
                    condition = "\n".join(cond).strip()
                    context = "CONTEXT_REQUIRED" if assumed_context else "EXPLICIT_CONNECTIVE_ONLY"
                    candidates.append({
                        "kind": "CONDITIONAL_CANDIDATE",
                        "section": section, "start_line": start+1, "end_line": end+1,
                        "source_quote": quoted, "condition_literal": condition,
                        "consequence_literal": consequence,
                        "scope": context, "confidence": "SYNTAX_ONLY_UNREVIEWED",
                    })
                    i = end+1
                    continue
            # Explicit assumed context not itself a complete logical implication.
            if re.search(r"\bsupposons\b", line, re.I):
                assumed_context = True
        if re.search(r"limites?", section, re.I) and line.lstrip().startswith("- "):
            candidates.append({
                "kind": "LIMITATION_LITERAL", "section": section,
                "start_line": i+1, "end_line": i+1,
                "source_quote": line, "condition_literal": "",
                "consequence_literal": "", "scope": "DOCUMENT_LIMIT_ONLY",
                "confidence": "SYNTAX_ONLY_UNREVIEWED",
            })
        elif re.search(r"hypothèses?|domaine", section, re.I) and line.lstrip().startswith("- "):
            candidates.append({
                "kind": "ASSUMPTION_LITERAL", "section": section,
                "start_line": i+1, "end_line": i+1,
                "source_quote": line, "condition_literal": "",
                "consequence_literal": "", "scope": "DOCUMENT_CONTEXT_ONLY",
                "confidence": "SYNTAX_ONLY_UNREVIEWED",
            })
        i += 1
    sha = git_blob(raw)
    for index, item in enumerate(candidates, 1):
        item["id"] = "E"+str(index).zfill(3)
        item["source_blob"] = sha
        item["source_path"] = name
    return {
        "status": "CANDIDATE_SYNTAX_EXTRACTION_NOT_SEMANTIC_PROOF",
        "source_path": name, "source_blob": sha,
        "source_lines": len(lines),
        "candidates": candidates, "counts": {
            tag: sum(x["kind"] == tag for x in candidates)
            for tag in ("CONDITIONAL_CANDIDATE", "LIMITATION_LITERAL", "ASSUMPTION_LITERAL")
        }
    }


def verify_literal_citations(raw: bytes, result: dict) -> list[str]:
    """Independent replay of citation boundaries, not a theorem reviewer."""
    lines = raw.decode("utf-8").splitlines()
    sha = git_blob(raw)
    problems = []
    if result.get("source_blob") != sha or result.get("source_lines") != len(lines):
        problems.append("SOURCE_IDENTITY_OR_LENGTH")
    for item in result["candidates"]:
        a, b = item["start_line"], item["end_line"]
        if not isinstance(a, int) or not isinstance(b, int) or not 1 <= a <= b <= len(lines):
            problems.append(item["id"]+":BAD_RANGE")
            continue
        original = "\n".join(lines[a-1:b])
        if original != item["source_quote"] or item["source_blob"] != sha:
            problems.append(item["id"]+":FALSE_CITATION")
        if item["kind"] == "CONDITIONAL_CANDIDATE":
            if not IF.match(lines[a-1]) or not THEN.search(original):
                problems.append(item["id"]+":MISSING_CONDITIONAL_MARKERS")
            if not item["condition_literal"] or not item["consequence_literal"]:
                problems.append(item["id"]+":INCOMPLETE_PAIR")
            else:
                # Normalization removes only line breaks and excess spaces.
                flat = " ".join(original.split())
                condition = " ".join(item["condition_literal"].split())
                consequence = " ".join(item["consequence_literal"].split())
                if condition not in flat or consequence not in flat:
                    problems.append(item["id"]+":INVENTED_CONTENT")
                elif flat.index(condition) > flat.index(consequence):
                    problems.append(item["id"]+":INVERTED_DIRECTION")
        elif item["kind"] in ("LIMITATION_LITERAL", "ASSUMPTION_LITERAL"):
            if a != b or not original.lstrip().startswith("- "):
                problems.append(item["id"]+":FALSE_BULLET")
        else:
            problems.append(item["id"]+":UNKNOWN_KIND")
    return problems


def run(path: Path, expected_blob: str | None = None) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked source")
    data = path.read_bytes()
    if expected_blob is not None and git_blob(data) != expected_blob:
        raise ValueError("source modified after pin")
    result = parse_document(data, path.as_posix())
    errors = verify_literal_citations(data, result)
    result["independent_citation_errors"] = errors
    result["cited_output_integrity"] = not errors
    # No endorsement of mathematical truth is possible in this pilot.
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--source-blob", type=str)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run(args.source, args.source_blob)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out = args.output.resolve()
        if out.is_relative_to(ROOT):
            p.error("write report outside repository")
        out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
