"""Conservative documentary evidence extraction for an Omega P5 calibration.

This recognises a DECLARED narrow French template, not general natural
language. Source kind/availability are trusted metadata supplied by caller.
Never infer an answer from a secondary message; fail closed on ambiguity.
No external lookup, model call, or certification is performed.
"""
from datetime import date
import re

from planner import plan_mission


class EvidenceExtractionError(ValueError):
    pass


POLICY = re.compile(
    r"Ancien delai: ([0-9]{1,2}) jours ouvres\. "
    r"Nouveau delai: ([0-9]{1,2}) jours ouvres\. "
    r"Transition: dossiers recus a partir du ([0-9]{4}-[0-9]{2}-[0-9]{2}) inclus\."
)
RECEIPT = re.compile(r"Registre de reception: ([0-9]{4}-[0-9]{2}-[0-9]{2})\.")


def _parse_date(raw):
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise EvidenceExtractionError("invalid calendar date") from exc


def _nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise EvidenceExtractionError(label + " must be nonempty text")
    return value


def _validate(case):
    if not isinstance(case, dict):
        raise EvidenceExtractionError("case must be an object")
    for key in ("case_id", "question"):
        _nonempty(case.get(key), key)
    for key in ("primary_available", "registry_available"):
        if type(case.get(key)) is not bool:
            raise EvidenceExtractionError(key + " must be boolean")
    documents = case.get("documents")
    if not isinstance(documents, list):
        raise EvidenceExtractionError("documents must be a list")
    ids = set()
    for doc in documents:
        if not isinstance(doc, dict):
            raise EvidenceExtractionError("document must be object")
        ident = _nonempty(doc.get("id"), "document id")
        _nonempty(doc.get("text"), "document text")
        if ident in ids:
            raise EvidenceExtractionError("duplicate document id")
        ids.add(ident)
        if doc.get("kind") not in ("primary_notice", "registry", "secondary_note"):
            raise EvidenceExtractionError("unrecognised source kind")
    return documents


def interpret_evidence(case):
    """Return an action plus a grounded decision if and only if justified."""
    documents = _validate(case)
    notices = [x for x in documents if x["kind"] == "primary_notice"]
    registers = [x for x in documents if x["kind"] == "registry"]
    notices.sort(key=lambda doc: doc["id"])
    registers.sort(key=lambda doc: doc["id"])

    if not notices:
        if case["primary_available"]:
            return {"action": "verify", "reason": "Notice officielle absente.",
                    "next_step": "Consulter la notice officielle dans le registre.",
                    "evidence_refs": []}
        return {"action": "insufficient_evidence",
                "reason": "Notice officielle absente et source inaccessible.",
                "evidence_refs": []}

    notice_rules = []
    for doc in notices:
        match = POLICY.fullmatch(doc["text"])
        if not match:
            return {"action": "insufficient_evidence",
                    "reason": "Format de notice non reconnu; aucune regle applicable verifiable.",
                    "evidence_refs": [doc["id"]]}
        old, new, raw_date = match.groups()
        notice_rules.append((int(old), int(new), _parse_date(raw_date)))
    if len(set(notice_rules)) != 1:
        return {"action": "verify",
                "reason": "Deux notices officielles incompatibles.",
                "next_step": "Verifier la version officielle applicable aupres du registre.",
                "evidence_refs": [n["id"] for n in notices]}
    old, new, transition = notice_rules[0]
    if old <= 0 or new <= 0:
        return {"action": "insufficient_evidence",
                "reason": "Delai non positif; controle humain necessaire.",
                "evidence_refs": [n["id"] for n in notices]}

    receipts = []
    for doc in registers:
        m = RECEIPT.fullmatch(doc["text"])
        if not m:
            if case["registry_available"]:
                return {"action": "verify", "reason": "Entree de registre non interpretable.",
                        "next_step": "Verifier la date de reception dans le registre.",
                        "evidence_refs": [doc["id"]]}
            return {"action": "insufficient_evidence",
                    "reason": "Entree du registre non interpretable, source indisponible.",
                    "evidence_refs": [doc["id"]]}
        receipts.append(_parse_date(m.group(1)))
    refs = [n["id"] for n in notices] + [r["id"] for r in registers]
    if len(set(receipts)) > 1:
        if case["registry_available"]:
            return {"action": "verify", "reason": "Dates de reception contradictoires.",
                    "next_step": "Comparer les entrees originales du registre.",
                    "evidence_refs": refs}
        return {"action": "insufficient_evidence",
                "reason": "Dates contradictoires et registre indisponible.",
                "evidence_refs": refs}
    if not receipts:
        return {"action": "ask",
                "reason": "La date de reception manque dans le dossier.",
                "next_step": "Quelle est la date de reception du dossier ?",
                "evidence_refs": refs}
    decision = "old" if receipts[0] < transition else "new"
    return {
        "action": "answer", "reason": "Source officielle et date coherentement etablies.",
        "decision": decision, "days": old if decision == "old" else new,
        "receipt": receipts[0].isoformat(), "threshold": transition.isoformat(),
        "evidence_refs": refs,
    }


def run_documentary_case(case):
    """Bridge extracted uncertainty to the EXISTING deterministic Omega P1."""
    finding = interpret_evidence(case)
    if finding["action"] == "answer":
        context = {"decision_basis": finding["reason"]}
    else:
        context = {"blocking_uncertainty": finding["reason"]}
        if finding["action"] == "verify":
            context["verification"] = finding["next_step"]
            context["verification_effect"] = (
                "La source primaire ou la date peut changer le delai applicable."
            )
        if finding["action"] == "ask":
            context["clarification"] = finding["next_step"]
    plan = plan_mission({
        "question": case["question"], "mission_type": "documentary",
        "mission_id": case["case_id"], "decision_context": context,
        "deliverables": [
            "Indiquer la decision applicable ou la raison de suspendre le verdict.",
            "Citer les documents decisifs et signaler les contradictions.",
        ],
    })
    if plan["next_action"]["action"] != finding["action"]:
        raise AssertionError("Omega P1 bridge changed the extracted next action")
    return {"finding": finding, "p1": plan}
