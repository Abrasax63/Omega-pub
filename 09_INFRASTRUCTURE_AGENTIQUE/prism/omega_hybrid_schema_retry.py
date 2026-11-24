"""One strictly bounded schema-only retry for an Omega-generated formal card.

The retry asks the SAME model to supply the missing graph examples; it does
not supply graphs, a proof, or oracle labels. No fake fixes or promotion.
Caller owns the actual LLM process, model version, budget and source isolation.
"""
from __future__ import annotations

from hashlib import sha256
import json

from omega_hybrid_example_clinic import diagnose_card


def schema_retry(card, model_call):
    """Return both raw replies and exact oracle diagnosis, never modify card.

    model_call(messages: list[dict], max_tokens: int) -> {'text': str}
    One call *only* when graph keys are missing and the formal signature is
    already recognized. No retries after malformed or mathematically wrong
    supplied graphs. Caller MUST persist this report, not silently replace.
    """
    before = diagnose_card(card)
    result = {"status": "NO_RETRY", "reason": before["reason"],
              "before": before, "after": None,
              "calls": 0, "original_card_preserved": True,
              "source_semantics_verified": False,
              "weights_updated": False,
              "scientific_claims_certified": 0}
    if before["reason"] != "MISSING_STRUCTURED_EXAMPLES":
        return result
    if not callable(model_call):
        return {**result, "status": "BLOCKED", "reason": "NO_MODEL_CALLBACK"}
    concept, axioms = before["concept"], card["formal_axioms"]
    # The card and its axioms were already chosen by the model, not given by
    # an evaluator. We disclose no correct edge list and no holdout answers.
    instruction = (
        "Complete ONLY the two missing structured illustration fields for "
        "the mathematical concept that you previously selected. "
        "Use nodes a, b, c. Decide the examples YOURSELF. "
        "Return exactly one JSON object with exactly two keys: "
        "positive_edges and negative_edges. Each value must be an array of "
        "distinct [from,to] arrays; endpoints can only be a, b or c. "
        "The first should satisfy the concept, the second should violate it. "
        "Do not quote sources, invent a proof, or change the prior definition. "
        "If you cannot construct both examples, return exactly "
        "{\"abstain\":true}. No surrounding explanation."
    )
    messages = [{"role": "system", "content":
                 "You generate tentative graph examples; every output is checked independently."},
                {"role": "user", "content":
                 instruction + "\nConcept chosen earlier: " + concept +
                 "\nFormal axioms you previously proposed: " + json.dumps(axioms)}]
    try:
        response = model_call(messages, 320)
    except Exception as exc:
        # Distinguish a client failure from a logical failure; do not serialize
        # exception content (it might contain private endpoint/headers).
        return {**result, "status": "BLOCKED",
                "reason": "MODEL_CALL_FAILED", "error_type": type(exc).__name__,
                "calls": 1}
    raw = response.get("text") if isinstance(response, dict) else None
    out = {**result, "calls": 1,
           "raw_output": raw if isinstance(raw, str) else None,
           "raw_output_sha256": sha256(raw.encode()).hexdigest()
                                if isinstance(raw, str) else None}
    if not isinstance(raw, str):
        return {**out, "status": "QUARANTINE", "reason": "NO_RAW_OUTPUT"}
    try:
        parsed = json.loads(raw.strip())
    except ValueError:
        return {**out, "status": "QUARANTINE", "reason": "RETRY_JSON_INVALID"}
    if parsed == {"abstain": True}:
        return {**out, "status": "QUARANTINE", "reason": "MODEL_ABSTAINED"}
    if not isinstance(parsed, dict) or set(parsed) != {"positive_edges", "negative_edges"}:
        return {**out, "status": "QUARANTINE", "reason": "RETRY_SCHEMA_INVALID"}
    revised = {**card, **parsed}
    checked = diagnose_card(revised)
    return {**out, "status": "BOUNDED_GRAPH_PASS_QUARANTINE_ONLY"
            if checked["status"] == "BOUNDED_FORMAL_PASS" else "QUARANTINE",
            "reason": checked["reason"], "after": checked,
            "candidate_addition": parsed if checked["status"] == "BOUNDED_FORMAL_PASS" else None,
            "source_semantics_verified": False,
            "scientific_claims_certified": 0}
