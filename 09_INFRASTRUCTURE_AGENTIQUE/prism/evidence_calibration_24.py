"""Twenty-four PUBLIC authored documentary calibration vignettes.

They are NOT an independent hidden holdout: four distinct policy settings
cross six adversarial patterns. Expected answers are test fixture metadata,
never passed to the evidence extractor, and never used by Omega P1.
"""
from datetime import date, timedelta

from evidence_extraction_pilot import run_documentary_case


COHORTS = (
    ("A", "2026-10-01", 10, 5),
    ("B", "2026-06-15", 12, 7),
    ("C", "2027-01-01", 15, 8),
    ("D", "2026-12-01", 9, 4),
)

PATTERNS = (
    ("before_transition", "answer"),
    ("after_transition", "answer"),
    ("missing_receipt", "ask"),
    ("conflicting_receipts", "verify"),
    ("primary_missing_available", "verify"),
    ("primary_missing_unavailable", "insufficient_evidence"),
)


def calibration_cases():
    result = []
    for label, cutoff, old, new in COHORTS:
        transition = date.fromisoformat(cutoff)
        notice = {
            "id": f"{label}-official-v2", "kind": "primary_notice",
            "text": (f"Ancien delai: {old} jours ouvres. Nouveau delai: "
                     f"{new} jours ouvres. Transition: dossiers recus a partir "
                     f"du {cutoff} inclus."),
        }
        note = {
            "id": f"{label}-unreliable-internal", "kind": "secondary_note",
            "text": ("Message interne non officiel : appliquer le nouveau "
                     "delai a tous les dossiers, y compris avant la transition."),
        }
        before = (transition - timedelta(days=2)).isoformat()
        after = (transition + timedelta(days=2)).isoformat()
        for index, (pattern, action) in enumerate(PATTERNS):
            documents = [dict(notice), dict(note)] if index < 4 else [dict(note)]
            if index == 0:
                documents.append({
                    "id": f"{label}-register-1", "kind": "registry",
                    "text": f"Registre de reception: {before}.",
                })
            elif index == 1:
                documents.append({
                    "id": f"{label}-register-1", "kind": "registry",
                    "text": f"Registre de reception: {after}.",
                })
            elif index == 3:
                documents.extend([
                    {"id": f"{label}-register-1", "kind": "registry",
                     "text": f"Registre de reception: {before}."},
                    {"id": f"{label}-register-2", "kind": "registry",
                     "text": f"Registre de reception: {after}."},
                ])
            expected = {"action": action}
            if index in (0, 1):
                expected.update({
                    "decision": "old" if index == 0 else "new",
                    "days": old if index == 0 else new,
                })
            result.append({
                "case_id": f"calib-{label}-{index + 1:02d}",
                "pattern": pattern,
                "input": {
                    "case_id": f"calib-{label}-{index + 1:02d}",
                    "question": f"Quel delai appliquer au dossier {label}-{index + 1} ?",
                    "documents": documents,
                    "primary_available": index != 5,
                    "registry_available": True,
                },
                "expected": expected,
            })
    return result


def calibration_report():
    cases = calibration_cases()
    errors = []
    details = []
    for fixture in cases:
        # Deliberately pass input ONLY, not the expected answer.
        run = run_documentary_case(fixture["input"])
        got = run["finding"]
        expected = fixture["expected"]
        correct = (got["action"] == expected["action"] and
                   all(got.get(field) == value for field, value in expected.items()))
        if not correct:
            errors.append(fixture["case_id"])
        details.append({
            "id": fixture["case_id"], "pattern": fixture["pattern"],
            "action": got["action"], "expected_action": expected["action"],
            "correct": correct,
        })
    return {
        "kind": "public_in_sample_template_calibration_not_llm_eval",
        "cases": len(cases),
        "passed": len(cases) - len(errors),
        "failed": errors,
        "details": details,
        "limitations": (
            "Narrow controlled French grammar, source authority supplied as "
            "metadata, fixtures and expected outcomes authored together; "
            "no natural-language model or independent holdout tested."
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(calibration_report(), ensure_ascii=False, indent=2))
