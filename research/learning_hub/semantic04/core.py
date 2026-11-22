"""OMEGA-SEMANTIC-TRANSFER-04: frozen semantic benchmark and one-edit baseline.

No training. Candidate selection sees only visible examples; hidden tests
are scored after ALL candidates are fixed. Model outputs remain archived.
"""
from collections import Counter
from hashlib import sha1, sha256
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "learning_lab"))
import prog_reconstruction_pilot as sandbox

FROZEN_BLOB = "00c48008244f787cfcd38fad278a4ed57452ebe5"
SOURCE_RUN = 45073297901
PROTOCOL = "OMEGA-SEMANTIC-TRANSFER-04"
MAX_EDITS = 120


def frozen_cases():
    raw = (HERE / "HOLDOUT_SEMANTIC_FROZEN.json").read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    if blob != FROZEN_BLOB:
        raise ValueError("SEMANTIC_HOLDOUT_CHANGED")
    doc = json.loads(raw)
    rows = doc.get("source_tasks")
    if (doc.get("schema") != "OMEGA_SEMANTIC04_FROZEN_HOLDOUT"
            or doc.get("source_adapter_run") != SOURCE_RUN
            or not isinstance(rows, list) or len(rows) != 12):
        raise ValueError("SEMANTIC_PROTOCOL_NOT_FROZEN")
    groups = Counter(x["family"] for x in rows)
    if len(groups) != 6 or set(groups.values()) != {2}:
        raise ValueError("WRONG_FAMILY_STRUCTURE")
    if len({x["id"] for x in rows}) != 12:
        raise ValueError("DUPLICATE_EVAL_ID")
    return rows


def public_only(cases):
    """Only input to model inference and selection of a symbolic edit."""
    return [{"id":x["id"], "family":x["family"], "defect":x["defect"],
             "prompt":x["model_prompt"], "broken":x["broken_source"],
             "public":x["public_examples"]} for x in cases]


def allowed(code):
    if not isinstance(code, str) or len(code) > sandbox.MAX_CODE_CHARS:
        return None, "INVALID_FORMAT_OR_SIZE"
    try:
        sandbox.validate_program(code)
    except ValueError as exc:
        return None, "INVALID_SYNTAX_OR_POLICY:" + str(exc)
    return code, "SAFE_PYTHON"


def strict(raw):
    if not isinstance(raw, str) or not raw.strip().startswith("def transform(s):"):
        return None, "NO_EXACT_CODE"
    return allowed(raw.strip())


def permissive(raw):
    code, status = strict(raw)
    if code is not None:
        return code, "STRICT_ACCEPTED"
    if not isinstance(raw, str):
        return None, "NOT_TEXT"
    fence = chr(96) * 3
    blocks = re.findall(re.escape(fence) + r"(?:python)?\s*\n(.*?)" +
                        re.escape(fence), raw, re.S | re.I)
    if blocks:
        if len(blocks) != 1:
            return None, "AMBIGUOUS_FENCES"
        code, status = allowed(blocks[0].strip())
        return code, "FENCED_" + status
    lines = raw.splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("def transform(s):")]
    if len(starts) != 1:
        return None, "NO_UNIQUE_FUNCTION"
    collected = [lines[starts[0]]]
    for line in lines[starts[0] + 1:]:
        if not line.strip() or line[:1].isspace():
            collected.append(line)
        else:
            break
    code, status = allowed("\n".join(collected).strip())
    return code, "EXTRACTED_" + status


# Frozen general-purpose mutation catalogue; no oracle code or family IDs.
EDITS = [
    (" not in ", " in "), (" in ", " not in "),
    (".upper()", ".lower()"), (".lower()", ".upper()"),
    ("s.split('|')", "s.split(':')"), ("s.split(':')", "s.split('|')"),
    ("s.split('|')", "s.split(',')"), ("s.split(',')", "s.split('|')"),
    ("for c in reversed(s):", "for c in s:"),
    ("for c in s:", "for c in reversed(s):"),
    ("c != '0'", "c == '0'"), ("c == '0'", "c != '0'"),
    ("i % 2 == 1", "i % 2 == 0"), ("i % 2 == 0", "i % 2 == 1"),
    ("len(s) - 2", "len(s) - 1"), ("len(s) - 1", "len(s) - 2"),
    ("s[i:i+1]", "s[i:i+2]"), ("s[i:i+2]", "s[i:i+1]"),
    ("str(i + 1)", "str(i)"), ("str(i)", "str(i + 1)"),
]


def candidates(source):
    options, seen = [("unchanged", source)], {source}
    for n, (old, new) in enumerate(EDITS):
        if old in source:
            code = source.replace(old, new, 1)
            if code not in seen:
                options.append(("edit_" + str(n), code))
                seen.add(code)
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if "out.append(" not in line:
            continue
        if i + 1 < len(lines) and lines[i + 1] == line:
            new = lines[:i + 1] + lines[i + 2:]
            label = "remove_duplicate"
        else:
            new = lines[:i + 1] + [line] + lines[i + 1:]
            label = "duplicate_append"
        code = "\n".join(new) + "\n"
        if code not in seen:
            options.append((label, code))
            seen.add(code)
    return options[:MAX_EDITS]


def matches_public(code, public):
    # Deliberately does not accept holdout cases, model messages, or gold.
    results = sandbox.execute_student(code, [x["input"] for x in public])
    return len(results) == len(public) and all(
        a.get("value") == e["output"] for a, e in zip(results, public))


def symbolic(broken, public):
    trials = 0
    for edit, candidate in candidates(broken):
        code, _ = allowed(candidate)
        trials += 1
        if code is not None and matches_public(code, public):
            return {"code": code, "edit": edit, "attempts": trials,
                    "hidden_tests_for_selection": 0}
    return {"code": None, "edit": None, "attempts": trials,
            "hidden_tests_for_selection": 0}


def grade(code, hidden):
    results = (sandbox.execute_student(code, [x["input"] for x in hidden])
               if code is not None else [{"error": "NO_ADMITTED_CODE"} for _ in hidden])
    data = [{"input": e["input"], "expected": e["output"],
             "received": got, "correct": got.get("value") == e["output"]}
            for e, got in zip(hidden, results)]
    n = sum(x["correct"] for x in data)
    return {"correct": n, "total": len(hidden), "all_correct": n == len(hidden),
            "details": data}


def score(cases, predictions):
    if sorted(predictions) != sorted(x["id"] for x in cases):
        raise ValueError("PREDICTION_IDS_INCOMPLETE")
    out = {key: [] for key in ("base", "lora", "symbolic")}
    for row in cases:
        ident = row["id"]
        item = predictions[ident]
        for arm in ("base", "lora"):
            raw = item[arm]["raw"]
            a, sa = strict(raw)
            b, sb = permissive(raw)
            out[arm].append({
                "id": ident, "family": row["family"], "defect": row["defect"],
                "raw": raw, "raw_sha256": sha256(raw.encode()).hexdigest(),
                "strict_valid": a is not None, "strict_status": sa,
                "permissive_valid": b is not None, "permissive_status": sb,
                "strict": grade(a, row["hidden_cases"]),
                "permissive": grade(b, row["hidden_cases"]),
                "prompt_tokens": item[arm]["prompt_tokens"],
                "generated_tokens": item[arm]["generated_tokens"],
                "seconds": item[arm]["seconds"]})
        sym = item["symbolic"]
        out["symbolic"].append({
            "id": ident, "family": row["family"], "defect": row["defect"],
            "edit": sym["edit"], "attempts": sym["attempts"],
            "code": sym["code"],
            "hidden_used_for_selection": sym["hidden_tests_for_selection"],
            "strict": grade(sym["code"], row["hidden_cases"])})
    sums = {}
    for arm, rows in out.items():
        sums[arm] = {}
        for method in (("strict", "permissive") if arm != "symbolic"
                       else ("strict",)):
            sums[arm][method] = {
                "exact_programs": sum(r[method]["all_correct"] for r in rows),
                "cases_correct": sum(r[method]["correct"] for r in rows),
                "programs": len(rows), "cases": sum(r[method]["total"] for r in rows)}
        if arm != "symbolic":
            sums[arm]["strict_valid"] = sum(r["strict_valid"] for r in rows)
            sums[arm]["permissive_valid"] = sum(r["permissive_valid"] for r in rows)
            sums[arm]["tokens_out"] = sum(r["generated_tokens"] for r in rows)
            sums[arm]["seconds"] = round(sum(r["seconds"] for r in rows), 3)
    sums["differences"] = {
        "lora_minus_base_strict":
            sums["lora"]["strict"]["exact_programs"] -
            sums["base"]["strict"]["exact_programs"],
        "lora_minus_base_permissive":
            sums["lora"]["permissive"]["exact_programs"] -
            sums["base"]["permissive"]["exact_programs"],
        "lora_minus_symbolic_strict":
            sums["lora"]["strict"]["exact_programs"] -
            sums["symbolic"]["strict"]["exact_programs"]}
    return {"protocol": PROTOCOL, "status": "OBSERVATIONAL_NOT_GENERALIZATION_PROOF",
            "source_adapter_run": SOURCE_RUN,
            "holdout_git_blob": FROZEN_BLOB,
            "summary": sums, "results": out,
            "new_weight_training": False,
            "holdout_not_sent_to_models": True,
            "holdout_not_used_to_choose_symbolic_edits": True,
            "new_scientific_discovery": False,
            "fresh_semantic_holdout_now_consumed": True}
