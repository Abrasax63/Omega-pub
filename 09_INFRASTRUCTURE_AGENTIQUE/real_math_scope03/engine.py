#!/usr/bin/env python3
"""Strict scoped claim checker for three pinned real Omega math documents.

NOT free-form semantic understanding; unknown phrasing => ABSTAIN.
Never reads GOLD_FROZEN.json.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PATHS = {
    "BR-R90-01": ("02_MATHEMATIQUES/temps_regle90/BR-R90-01_NOYAUX_PERIODES.md",
                  "478ca7c518ed1368a0bf35deb5f9be160bba581d"),
    "BR-R90-02": ("02_MATHEMATIQUES/temps_regle90/BR-R90-02_MAJORITY_WALSH.md",
                  "0a9f6bab0b91a93f8fcc831c39a988171c169eb5"),
    "PILOTE-EXT-C4-L2-2026-11-04":
        ("02_MATHEMATIQUES/defauts_recollement/PILOTE_EXTRACTION_C4_L2_2026-11-04.md",
         "874e284aedadcffb2d7b18055709ba880002586d"),
}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def verify_sources(root: Path = ROOT) -> dict:
    notes = {}
    for identifier, (path, sha) in SOURCE_PATHS.items():
        file = root / path
        if not file.is_file() or file.is_symlink():
            raise ValueError("missing or symlinked real source: " + path)
        data = file.read_bytes()
        if git_blob(data) != sha:
            raise ValueError("pinned real source changed: " + path)
        body = data.decode("utf-8")
        if identifier == "BR-R90-01":
            anchors = (r"\dim\ker(A_N^t)=\min(2t,2^a)", r"\operatorname{rang}(A_N^t)=N-\min(2t,2^a)")
        elif identifier == "BR-R90-02":
            anchors = (r"N\geq 2h+3", r"H(W_h)=H_2(W_h)=h+1")
        else:
            anchors = ("Minimalité N=9", "Certification Lean", "NON RÉALISÉE", "C4O-07")
        for anchor in anchors:
            if anchor not in body:
                raise ValueError("theorem anchor not found in " + path + ": " + anchor)
        notes[identifier] = {"text": body, "path": path, "blob": sha}
    return notes


def find_int(patterns: tuple[str, ...], question: str) -> int | None:
    for p in patterns:
        match = re.search(p, question, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def last_number(q: str) -> int | None:
    values = re.findall(r"\d+", q)
    return int(values[-1]) if values else None


def citation(note: dict, anchor: str) -> dict:
    lines = note["text"].splitlines()
    for i, line in enumerate(lines, 1):
        if anchor in line:
            return {"source_file": note["path"], "source_blob": note["blob"],
                    "line": i, "excerpt": line.strip(), "status": "experimental_source"}
    raise ValueError("missing anchor")


def judgement(verdict: str, reason: str, note: dict | None = None, anchor: str | None = None, oracle_inputs=None) -> dict:
    out = {"verdict": verdict, "reason": reason}
    if note is not None and anchor is not None:
        out["evidence"] = citation(note, anchor)
    if oracle_inputs is not None:
        out["finite_case"] = oracle_inputs
    return out


def rule90(case: dict, note: dict) -> dict:
    q = case["question"].casefold()
    n = find_int((r"\bN\s*=\s*(\d+)", r"\bN\s+vaut\s+(\d+)", r"\b(\d+)\s+sites"), q)
    t = find_int((r"\bt\s*=\s*(\d+)", r"\bt\s+vaut\s+(\d+)"), q)
    if n is None or t is None or n < 2 or t < 0:
        return judgement("ABSTAIN", "missing or invalid N/t under real theorem")
    is_rank = bool(re.search(r"\brang\b", q))
    is_kernel = bool(re.search(r"noyau|dim\s*ker", q))
    if is_rank == is_kernel:
        return judgement("ABSTAIN", "unknown or ambiguous requested invariant")
    candidate = last_number(q)
    if candidate is None:
        return judgement("ABSTAIN", "no expected integer extracted")
    lowbit = n & -n
    exact = n - min(2*t, lowbit) if is_rank else min(2*t, lowbit)
    anchor = r"\operatorname{rang}(A_N^t)=N-\min(2t,2^a)" if is_rank else r"\dim\ker(A_N^t)=\min(2t,2^a)"
    verdict = "SUPPORTED" if candidate == exact else "CONTRADICTED"
    return judgement(verdict, "document formula evaluated for N and t; expected " + str(exact),
                     note, anchor, {"domain": "kernel_rank", "n": n, "t": t, "kind": "rank" if is_rank else "kernel",
                                    "claimed": candidate, "expected_formula": exact})


def majority(case: dict, note: dict) -> dict:
    q = case["question"].casefold()
    n = find_int((r"\bN\s*=\s*(\d+)",), q)
    h = find_int((r"\bh\s*=\s*(\d+)",), q)
    if n is None or h is None or n < 3 or h < 0:
        return judgement("ABSTAIN", "unresolved N/h or invalid domain")
    if n < 2*h+3:
        return judgement("ABSTAIN", "condition sufficient only; converse not asserted",
                         note, r"N\geq 2h+3")
    negative_uniform = bool(re.search(r"n.est pas uniforme", q))
    if "uniforme" in q:
        claimed = not negative_uniform
        actual = True
        ok = claimed == actual
    elif any(x in q for x in ("h(w_h)", "h_2(w_h)", "entropie")):
        claimed = last_number(q)
        if claimed is None:
            return judgement("ABSTAIN", "missing entropy value")
        ok = claimed == h+1
    else:
        return judgement("ABSTAIN", "unrecognized Majority-Walsh claim")
    return judgement("SUPPORTED" if ok else "CONTRADICTED",
                     "sufficient condition N >= 2h+3 holds; result from source",
                     note, r"H(W_h)=H_2(W_h)=h+1",
                     {"domain": "majority", "n": n, "h": h,
                      "claimed_uniformity": claimed if "uniforme" in q else None,
                      "claimed_entropy": claimed if "uniforme" not in q else None})


def c4(case: dict, note: dict) -> dict:
    q = case["question"].casefold()
    if "c5" in q or "l=3" in q or "seul motif" in q or "sans la définition v19" in q:
        return judgement("ABSTAIN", "scope differs from the eight-class C4/L2 V19(2) experiment")
    if "v19(2)" not in q or "c4" not in q or not re.search(r"l\s*=\s*2", q):
        return judgement("ABSTAIN", "missing complete V19(2), C4, L=2 scope")
    if "lean" in q and ("certifi" in q or "formali" in q):
        return judgement("CONTRADICTED", "source explicitly reports no Lean certification",
                         note, "Certification Lean")
    if ("huit états suffisent" in q or "8 états suffisent" in q):
        return judgement("CONTRADICTED", "no simultaneous witness with <= 8 states under the scoped contract",
                         note, "Absence de témoin pour N=4,…,8")
    if ("aucun témoin simultané à huit états" in q or "aucun témoin simultané à 8 états" in q):
        return judgement("SUPPORTED", "exhaustive 4..8 reported in scoped source",
                         note, "Absence de témoin pour N=4,…,8")
    if (("minimum" in q and ("9 états" in q or "neuf états" in q))
        or ("témoin simultané" in q and ("neuf états" in q or "9 états" in q))):
        return judgement("SUPPORTED", "scoped reported nine-state witness and minimum",
                         note, "Minimalité N=9")
    return judgement("ABSTAIN", "not identified as a scoped source claim")


def evaluate_case(case: dict, notes: dict | None = None) -> dict:
    notes = notes if notes is not None else verify_sources()
    identifier = case.get("source_id")
    if identifier not in notes:
        return judgement("ABSTAIN", "source identifier missing or unsupported")
    note = notes[identifier]
    if identifier == "BR-R90-01":
        return rule90(case, note)
    if identifier == "BR-R90-02":
        return majority(case, note)
    return c4(case, note)


def lexical_baseline(case: dict, notes: dict) -> dict:
    """Deliberately weak documentary co-occurrence baseline, not a solver."""
    q = case["question"].casefold()
    key = case.get("source_id")
    if key not in notes:
        return {"verdict": "ABSTAIN"}
    tests = ("noyau", "rang", "dim ker") if key == "BR-R90-01" else (
        ("uniforme", "h(w_h)", "h_2(w_h)", "entropie")
        if key == "BR-R90-02" else ("témoin", "minimum", "états", "lean"))
    return {"verdict": "SUPPORTED" if any(term in q for term in tests) else "ABSTAIN"}
