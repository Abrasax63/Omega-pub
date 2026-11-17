#!/usr/bin/env python3
"""Omega model-output gate: untrusted assertions -> source-anchored quarantine.

Exact citations are a necessary but NOT sufficient condition for semantic
fidelity. Even a fully quoted assertion is never exported to Horn or certified.
"""
from __future__ import annotations
import hashlib
import re
from read import packetize, blob

MAX_CLAIMS = 32
MAX_EVIDENCE = 8
ID = re.compile(r"^C[A-Za-z0-9_-]{0,31}$")
ROLES = {"premise", "conclusion", "limitation"}
INLINE_UNSAFE = re.compile(r"\b(?:preuve|démonstration|proof|réfuté|réfutation|contre[- ]exemple)\b", re.I)
CLAIM_KEYS = {"claim_id", "packet_id", "evidence"}
EVIDENCE_KEYS = {"role", "packet_id", "line", "literal"}


def check_evidence(e: dict, lines: list[str], packets: dict) -> tuple[dict | None, str | None]:
    if not isinstance(e, dict) or set(e) != EVIDENCE_KEYS:
        return None, "INVALID_EVIDENCE_SCHEMA"
    role, packet_id, line, literal = (e.get(k) for k in ("role", "packet_id", "line", "literal"))
    if role not in ROLES or not isinstance(packet_id, str) or packet_id not in packets:
        return None, "UNKNOWN_ROLE_OR_PACKET"
    packet = packets[packet_id]
    if type(line) is not int or not packet["start_line"] <= line <= packet["end_line"]:
        return None, "SOURCE_LINE_NOT_WITHIN_REFERENCED_PACKET"
    if not isinstance(literal, str) or not 6 <= len(literal) <= 500:
        return None, "INVALID_LITERAL"
    source_line = lines[line-1]
    if source_line.count(literal) != 1:
        return None, "UNQUOTED_OR_AMBIGUOUS_LITERAL"
    if role in ("premise", "conclusion") and INLINE_UNSAFE.search(source_line):
        return None, "INLINE_PROOF_REFUTATION_OR_COUNTEREXAMPLE"
    if role in ("premise", "conclusion") and packet["context_status"] == "BLOCKED_SOURCE_CONTEXT":
        return None, "CLAIM_FROM_PROOF_REFUTATION_OR_LIMITS"
    return {
        "role": role, "packet_id": packet_id, "line": line, "literal": literal,
        "source_blob": packet["source_blob"], "source_path": packet["source_path"],
        "literal_sha256": hashlib.sha256(literal.encode("utf-8")).hexdigest(),
        "context_status": packet["context_status"],
    }, None


def gate(raw: bytes, path: str, model_data: dict, *, provider: str = "offline-fixture") -> dict:
    inventory = packetize(raw, path)
    packets = {p["packet_id"]: p for p in inventory["packets"]}
    lines = raw.decode("utf-8").splitlines()
    if not isinstance(model_data, dict) or set(model_data) != {"source_blob", "claims"}:
        raise ValueError("model output must have only source_blob and claims fields")
    if model_data["source_blob"] != blob(raw):
        raise ValueError("model source hash differs from exact source")
    claims = model_data["claims"]
    if not isinstance(claims, list) or len(claims) > MAX_CLAIMS:
        raise ValueError("too many or invalid model claims")
    accepted, rejected = [], []
    seen_ids = set()
    for i, claim in enumerate(claims):
        why = None
        if not isinstance(claim, dict) or set(claim) != CLAIM_KEYS:
            why = "UNSUPPORTED_CLAIM_FIELDS_OR_STATUS_PROMOTION"
        elif not isinstance(claim.get("claim_id"), str) or not ID.fullmatch(claim["claim_id"]):
            why = "INVALID_CLAIM_ID"
        elif claim["claim_id"] in seen_ids:
            why = "DUPLICATE_CLAIM_ID"
        elif claim.get("packet_id") not in packets:
            why = "NONEXISTENT_CLAIM_PACKET"
        elif not isinstance(claim.get("evidence"), list) or not 1 <= len(claim["evidence"]) <= MAX_EVIDENCE:
            why = "MISSING_OR_OVERSIZED_EVIDENCE"
        if why:
            rejected.append({"index": i, "reason": why})
            continue
        seen_ids.add(claim["claim_id"])
        items = []
        for e in claim["evidence"]:
            checked, failure = check_evidence(e, lines, packets)
            if failure:
                why = failure
                break
            items.append(checked)
        if not why and sum(x["role"] == "conclusion" for x in items) != 1:
            why = "EXACTLY_ONE_CONCLUSION_REQUIRED"
        if not why and not any(x["packet_id"] == claim["packet_id"] and
                               x["role"] == "conclusion" for x in items):
            why = "CLAIM_PACKET_MUST_CITE_ITS_CONCLUSION"
        if why:
            rejected.append({"index": i, "claim_id": claim["claim_id"], "reason": why})
            continue
        accepted.append({
            "claim_id": claim["claim_id"],
            "packet_id": claim["packet_id"],
            "source_path": path, "source_blob": blob(raw),
            "evidence": items,
            "status": "QUARANTINE_SOURCE_ANCHORED_UNREVIEWED",
            "semantic_fidelity": "NOT_VERIFIED",
            "hypothesis_scope": "NOT_ESTABLISHED",
            "verdict": "INDETERMINATE",
            "promotable": False,
        })
    return {
        "engine": "OMEGA_READ_TO_QUARANTINE_12",
        "source_path": path, "source_blob": blob(raw),
        "provider": provider,
        "model_responses_trusted": False,
        "accepted": accepted, "rejected": rejected,
        "accepted_count": len(accepted), "rejected_count": len(rejected),
        "horn_rules": [], "automatic_promotions": 0,
        "semantic_verification": "NOT_PERFORMED",
        "integration_mode": "READ_ONLY_QUARANTINE",
    }


def export_to_horn(*args, **kwargs):
    raise PermissionError("INDEPENDENT_SEMANTIC_REVIEW_REQUIRED_BEFORE_ANY_FORMAL_RULE")
