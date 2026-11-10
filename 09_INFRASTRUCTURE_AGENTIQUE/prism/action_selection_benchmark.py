"""Public, deterministic synthetic calibration of Omega's next-action policy.

These 24 authored finite models are NOT a hidden holdout or model performance
measurement. Decision labels and predicted observations are hypothetical.
"""
import json
from collections import Counter, defaultdict
from fractions import Fraction

from action_selection import plan_with_evidence, select_action

PATTERNS = (
    "decision_certain", "cheap_verification", "clarification_only",
    "uninformative", "distracting_check", "cost_tradeoff",
)
EXPECTED_ACTIONS = (
    "answer", "verify", "ask", "insufficient_evidence", "ask", "ask",
)

DOMAINS = {
    "mathematical": {
        "mission_type": "mathematical",
        "questions": (
            "Une condition est-elle requise pour le lemme fictif M1 ?",
            "La propriété M2 est-elle universelle dans le modèle fini proposé ?",
            "La borne M3 peut-elle être améliorée dans le modèle proposé ?",
            "L'implication M4 est-elle décidée par les axiomes fournis ?",
            "Quel cas de M5 invalide éventuellement la conclusion ?",
            "Quel test M6 choisir avec un budget de calcul limité ?",
        ),
        "decisions": ("maintenir", "rejeter"),
        "verification": "Énumérer exactement les cas du modèle fictif.",
        "clarification": "Demander l'hypothèse manquante de l'énoncé.",
        "method": "exact_enumeration",
    },
    "documentary": {
        "mission_type": "documentary",
        "questions": (
            "Quelle règle fictive s'applique au dossier D1 ?",
            "Quel délai fictif annoncer pour le dossier D2 ?",
            "Quelle version gouverne le dossier fictif D3 ?",
            "La notice D4 permet-elle une décision ferme ?",
            "La directive fictive D5 prime-t-elle la notice ?",
            "Quel renseignement demander pour le dossier D6 ?",
        ),
        "decisions": ("version_1", "version_2"),
        "verification": "Lire la source primaire datée dans le registre fictif.",
        "clarification": "Demander la date de réception absente.",
        "method": "primary_source_check",
    },
    "computational": {
        "mission_type": "computational",
        "questions": (
            "L'agrégat fictif C1 est-il exploitable ?",
            "Le résultat fictif C2 dépend-il d'un doublon ?",
            "Le calcul fictif C3 respecte-t-il le filtre attendu ?",
            "La variation fictive C4 peut-elle être attribuée ?",
            "Le traitement fictif C5 contient-il une anomalie ?",
            "Quelle vérification choisir pour le calcul fictif C6 ?",
        ),
        "decisions": ("valide", "invalide"),
        "verification": "Recalculer les contrôles sur les données fictives.",
        "clarification": "Demander la définition du périmètre de calcul.",
        "method": "exact_recomputation",
    },
    "exploratory": {
        "mission_type": "exploratory",
        "questions": (
            "Quelle piste fictive E1 mérite d'être poursuivie ?",
            "Quel mécanisme fictif explique l'observation E2 ?",
            "Quel modèle fictif privilégier pour E3 ?",
            "Quel essai fictif départagerait E4 ?",
            "Quelle interprétation fictive d'E5 retenir ?",
            "Quelle expérience E6 a le meilleur intérêt décisionnel ?",
        ),
        "decisions": ("piste_A", "piste_B"),
        "verification": "Exécuter l'expérience discriminante fictive.",
        "clarification": "Demander la contrainte expérimentale manquante.",
        "method": "controlled_test",
    },
}


def make_cases():
    result = []
    for domain, spec in DOMAINS.items():
        for index, pattern in enumerate(PATTERNS):
            certain = pattern == "decision_certain"
            labels = [spec["decisions"][0]] * 4 if certain else [
                spec["decisions"][0], spec["decisions"][0],
                spec["decisions"][1], spec["decisions"][1],
            ]
            verify = {
                "id": "01-verification", "action": "verify",
                "method": spec["method"], "step": spec["verification"],
                "available": True, "cost_milli": 40,
                "observations": ["x", "x", "y", "y"],
            }
            ask = {
                "id": "02-clarification", "action": "ask",
                "method": "request_missing_fact", "step": spec["clarification"],
                "available": True, "cost_milli": 110,
                "observations": ["x", "x", "y", "y"],
            }
            if pattern == "clarification_only":
                verify["available"] = False
                ask["cost_milli"] = 50
            elif pattern == "uninformative":
                verify["observations"] = ["x"] * 4
                ask["available"] = False
            elif pattern == "distracting_check":
                verify["observations"] = ["x", "y", "x", "y"]
                ask["cost_milli"] = 90
            elif pattern == "cost_tradeoff":
                verify["cost_milli"] = 300
                ask["observations"] = ["x", "y", "y", "y"]
                ask["cost_milli"] = 10
            result.append({
                "case_id": f"{domain}-{index + 1:02d}",
                "question": spec["questions"][index],
                "mission_type": spec["mission_type"],
                "uncertainty": "Plusieurs décisions restent possibles dans le modèle fictif.",
                "hypotheses": [
                    {"id": f"h{i}", "decision": label, "weight": 1}
                    for i, label in enumerate(labels)
                ],
                "checks": [verify, ask],
            })
    return result


def _reference_net_gain(case, check):
    """Second path: enumerate outcomes and optimal predictions per outcome."""
    hypotheses = case["hypotheses"]
    total = sum(h["weight"] for h in hypotheses)
    counts = Counter()
    for h in hypotheses:
        counts[h["decision"]] += h["weight"]
    initial_correct = max(counts.values())
    expected_correct = 0
    for outcome in set(check["observations"]):
        tally = Counter()
        for h, seen in zip(hypotheses, check["observations"]):
            if seen == outcome:
                tally[h["decision"]] += h["weight"]
        expected_correct += max(tally.values())
    return Fraction(expected_correct - initial_correct, total) - Fraction(
        check["cost_milli"], 1000
    )


def _reference_choice(case, mode):
    decisions = {h["decision"] for h in case["hypotheses"]}
    if len(decisions) == 1:
        return ("answer", None)
    viable = []
    for check in case["checks"]:
        if check["available"]:
            score = _reference_net_gain(case, check)
            if score > 0:
                viable.append((check, score))
    if not viable:
        return ("insufficient_evidence", None)
    if mode == "best":
        chosen = sorted(viable, key=lambda x: (-x[1], x[0]["id"]))[0][0]
    elif mode == "first_positive":
        chosen = viable[0][0]
    else:
        raise ValueError("unknown mode")
    return chosen["action"], chosen["id"]


def evaluate():
    cases = make_cases()
    counts = Counter()
    detail = []
    for case in cases:
        selection = select_action(case)
        plan = plan_with_evidence(case)["plan"]
        oracle_action, oracle_id = _reference_choice(case, "best")
        baseline_action, baseline_id = _reference_choice(case, "first_positive")
        pattern_index = int(case["case_id"].rsplit("-", 1)[1]) - 1
        expected = EXPECTED_ACTIONS[pattern_index]
        if (selection["action"], selection["chosen_check"]) != (oracle_action, oracle_id):
            raise AssertionError(f"independent reference mismatch: {case['case_id']}")
        if selection["action"] != expected:
            raise AssertionError(f"declared pattern mismatch: {case['case_id']}")
        if plan["next_action"]["action"] != selection["action"]:
            raise AssertionError("P1 bridge mismatch")
        counts["checked"] += 1
        counts["optimizer_matches_reference"] += 1
        if (baseline_action, baseline_id) == (oracle_action, oracle_id):
            counts["first_positive_matches_reference"] += 1
        detail.append({
            "case_id": case["case_id"], "selected": selection["action"],
            "check": selection["chosen_check"], "reference": oracle_action,
            "first_positive": baseline_action,
            "net_gain": selection["net_gain"],
        })
    return {"kind": "synthetic_in_sample_calibration", "cases": len(cases),
            "optimizer_matches_reference": counts["optimizer_matches_reference"],
            "first_positive_matches_reference": counts["first_positive_matches_reference"],
            "disclaimer": "No model calls, no hidden holdout, no demonstrated real-world improvement.",
            "detail": detail}


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
