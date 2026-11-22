"""Omega research reflector: grounded alternative structures and conservative redundancy audit.

Preparation/critique only. It does NOT infer mathematical meaning from text,
call a model, prove a thesis, promote a rule, merge or delete any file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata

STATUS = "PROPOSED_UNVERIFIED"
MAX_SOURCE = 200_000
MAX_FILES = 5000


class UnsafeProposal(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def source_anchor(root: Path, source: dict) -> dict:
    """Resolve a unique literal quote in a pinned file, reject stale or unsafe sources."""
    if not isinstance(source, dict):
        raise UnsafeProposal("Missing source")
    rel, pinned, quote = (source.get(key) for key in ("path", "git_blob", "quote"))
    if not isinstance(rel, str) or not rel or rel.startswith("/") or "\\" in rel:
        raise UnsafeProposal("Bad source path")
    if not isinstance(pinned, str) or not re.fullmatch(r"[0-9a-f]{40}", pinned):
        raise UnsafeProposal("Source Git blob must be pinned")
    if not isinstance(quote, str) or len(quote.strip()) < 25:
        raise UnsafeProposal("Missing substantial source quote")
    base = Path(root).resolve()
    path = base / rel
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(base):
        raise UnsafeProposal("Source absent or outside declared root")
    if path.stat().st_size > MAX_SOURCE:
        raise UnsafeProposal("Source exceeds budget")
    raw = path.read_bytes()
    if git_blob(raw) != pinned:
        raise UnsafeProposal("Stale source: Git blob mismatch")
    text = raw.decode("utf-8")
    if text.count(quote) != 1:
        raise UnsafeProposal("Quote is absent or ambiguous, cannot ground interpretation")
    start = text.index(quote)
    return {"path": rel, "git_blob": pinned,
            "start_line": text.count("\n", 0, start) + 1,
            "quote_sha256": sha256(quote.encode("utf-8")),
            "source_semantics_verified": False}


def nonempty(x):
    return isinstance(x, str) and bool(x.strip()) and len(x) <= 3500


def validate_proposal(proposal: dict, roots: dict[str, Path]) -> dict:
    """Validate the falsifiable *contract*, not the scientific truth of its thesis."""
    if not isinstance(proposal, dict) or proposal.get("status") != STATUS:
        raise UnsafeProposal("Proposal must explicitly remain unverified")
    for field in ("id", "source_root", "question", "thesis", "limitations"):
        if not nonempty(proposal.get(field)):
            raise UnsafeProposal("Missing/unsafe proposal field: " + field)
    if not re.fullmatch(r"[A-Z][A-Z0-9-]{5,90}", proposal["id"]):
        raise UnsafeProposal("Invalid proposal id")
    key = proposal["source_root"]
    if key not in roots:
        raise UnsafeProposal("Unknown source root")
    anchor = source_anchor(roots[key], proposal.get("source"))
    reps = proposal.get("representations")
    if not isinstance(reps, list) or len(reps) < 2 or len(reps) > 5:
        raise UnsafeProposal("Need two genuinely specified representations")
    names = set()
    for rep in reps:
        if not isinstance(rep, dict) or not all(nonempty(rep.get(k)) for k in
                                                ("name", "mapping", "preserved", "breaks_on")):
            raise UnsafeProposal("Representation mapping or invariants missing")
        if rep["name"] in names:
            raise UnsafeProposal("Repeated representation")
        names.add(rep["name"])
    plan = proposal.get("test")
    fields = ("premises", "baseline", "prediction", "counterexample",
              "independent_evidence", "metrics", "failure_criteria", "budget")
    if not isinstance(plan, dict) or not all(nonempty(plan.get(k)) for k in fields):
        raise UnsafeProposal("Missing discriminating experiment contract")
    # A proposal cannot attach a proved/supported status by writing a label.
    if any(x in proposal for x in ("proof", "certified", "verified", "adopted")):
        raise UnsafeProposal("No proof or certification promotion in proposal manifest")
    return {"id": proposal["id"], "status": STATUS,
            "anchor": anchor, "representations": len(reps),
            "protocol_sha256": sha256(json.dumps(proposal, sort_keys=True,
                         ensure_ascii=False).encode("utf-8")),
            "scientific_truth_checked": False,
            "needs_independent_semantic_review": True,
            "can_enter_research_inbox": True, "can_enter_executed_ledger": False}


def normalize(text: str) -> set[str]:
    norm = "".join(c for c in unicodedata.normalize("NFKD", text.casefold())
                   if not unicodedata.combining(c))
    return {t for t in re.findall(r"[a-z0-9]+", norm) if len(t) > 3}


def overlap(a: dict, b: dict) -> dict:
    """Only *identical full execution contracts* are exact replays."""
    required = ("source_revision", "input_digest", "oracle_digest",
                "holdout_digest", "metric_definition", "scope", "budget")
    same = all(a.get(k) == b.get(k) and nonempty(a.get(k)) for k in required)
    terms_a, terms_b = normalize(a.get("objective", "")), normalize(b.get("objective", ""))
    similarity = len(terms_a & terms_b) / len(terms_a | terms_b) if terms_a | terms_b else 0.0
    if same and a.get("objective") == b.get("objective"):
        label = "EXACT_SAME_CONTRACT_REVIEW_ONLY"
    elif similarity >= 0.45:
        label = "POTENTIAL_OVERLAP_MANUAL_REVIEW"
    else:
        label = "NO_EVIDENCE_OF_DUPLICATION"
    return {"first": a.get("id"), "second": b.get("id"),
            "relationship": label, "lexical_overlap": round(similarity, 3),
            "automatically_delete": False,
            "automatically_skip_regression": False,
            "reason": "Textual overlap alone does not establish semantic or experimental equivalence"}


def audit_redundancy(roots: dict[str, Path], jobs: list[dict]) -> dict:
    """Inventory read-only duplicate *bytes* and suspiciously overlapping contracts."""
    fingerprints = {}
    for label, root in sorted(roots.items()):
        root = Path(root).resolve()
        if not root.is_dir():
            raise UnsafeProposal("Missing checkout " + label)
        count = 0
        for path in sorted(root.rglob("*.py")):
            count += 1
            if count > MAX_FILES:
                raise UnsafeProposal("Inventory budget exceeded")
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SOURCE:
                continue
            h = sha256(path.read_bytes())
            fingerprints.setdefault(h, []).append(f"{label}:{path.relative_to(root)}")
    duplicates = [sorted(v) for v in fingerprints.values() if len(v) > 1]
    duplicates.sort(key=lambda v: (len(v), v), reverse=True)
    pairs = []
    for i, a in enumerate(jobs):
        for b in jobs[i + 1:]:
            comparison = overlap(a, b)
            if comparison["relationship"] != "NO_EVIDENCE_OF_DUPLICATION":
                pairs.append(comparison)
    return {
        "status": "READ_ONLY_AUDIT_NOT_SEMANTIC_EQUIVALENCE",
        "content_duplicate_groups": len(duplicates),
        "identical_python_file_samples": duplicates[:15],
        "potentially_overlapping_job_pairs": pairs,
        "safe_to_delete_files": [],
        "safe_to_drop_tests": [],
        "requires_human_and_regression_review": True,
        "conclusion": "Identical bytes and similar titles do not prove that branches, tests or scientific hypotheses are redundant."
    }


def run(proposals_file, roots, work_items, destination):
    payload = json.loads(Path(proposals_file).read_text(encoding="utf-8"))
    proposals = payload.get("proposals")
    if not isinstance(proposals, list) or not proposals:
        raise UnsafeProposal("Proposal manifest missing")
    validated = [validate_proposal(p, roots) for p in proposals]
    if len({p["id"] for p in validated}) != len(validated):
        raise UnsafeProposal("Duplicate hypothesis ID")
    jobs = json.loads(Path(work_items).read_text(encoding="utf-8")).get("work_items")
    if not isinstance(jobs, list):
        raise UnsafeProposal("Work-items inventory missing")
    summary = {
        "scientific_claims_certified": 0,
        "grounded_hypothesis_proposals": validated,
        "deduplication": audit_redundancy(roots, jobs),
        "action_policy": {"delete": False, "merge": False, "skip": False,
                          "promote": False, "automatic_semantic_verdict": False},
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--proposals", type=Path, required=True)
    p.add_argument("--work-items", type=Path, required=True)
    p.add_argument("--provenance", type=Path, required=True)
    p.add_argument("--math", type=Path, required=True)
    p.add_argument("--omega100", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    roots = {"provenance": a.provenance, "math": a.math, "omega100": a.omega100}
    result = run(a.proposals, roots, a.work_items, a.output)
    print(json.dumps({"status": "OK", "grounded_proposals": len(result["grounded_hypothesis_proposals"]),
                      "identical_python_groups": result["deduplication"]["content_duplicate_groups"],
                      "overlapping_jobs": len(result["deduplication"]["potentially_overlapping_job_pairs"]),
                      "changes_performed": 0}, ensure_ascii=False))
    

if __name__ == "__main__":
    main()
