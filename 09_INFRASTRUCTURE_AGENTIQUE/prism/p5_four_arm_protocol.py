"""P5 four-arm INPUT protocol; never generates outputs or claims a win.

A direct answer, B five fixed perspectives, C adaptation with a provided
structured context, D self-extraction. C has PRIVILEGED information by design
and is diagnostic, NOT information-parity with A/B/D.
No model calls, grading, third-party holdout or real expense.
"""
import hashlib
import json

from planner import ROLE_ORDER, ROLE_QUESTIONS, plan_mission

ARMS = ("A", "B", "C", "D")
COMMON_DELIVERABLES = (
    "Donner la decision applicable si les preuves le permettent.",
    "Citer les documents decisifs et signaler les contradictions.",
    "Si la decision n'est pas justifiee, indiquer la prochaine action ou s'abstenir.",
)
COMMON_INSTRUCTIONS = (
    "Reponds en francais. N'invente ni fait ni verification effectuee. "
    "N'utilise aucune source non fournie. Respecte le meme plafond de sortie."
)
FORBIDDEN = ("expected", "gold", "reference_answer", "answer_key")


def _check_case(case):
    if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
        raise ValueError("invalid case")
    if not isinstance(case.get("question"), str) or not case["question"].strip():
        raise ValueError("case question required")
    if any(key in case for key in FORBIDDEN):
        raise ValueError("reference answer cannot appear in arm inputs")
    if not isinstance(case.get("documents"), list):
        raise ValueError("documents must be list")
    for doc in case["documents"]:
        if not isinstance(doc, dict) or not all(
            isinstance(doc.get(field), str) and doc[field].strip()
            for field in ("id", "kind", "text")
        ):
            raise ValueError("invalid document")


def _common_case_text(case):
    parts = [case["question"], "Documents fournis :"]
    for doc in sorted(case["documents"], key=lambda d: d["id"]):
        parts.append(f"- [{doc['id']}] ({doc['kind']}) {doc['text']}")
    parts.append("Livrables identiques pour tous les bras :")
    parts.extend(f"- {x}" for x in COMMON_DELIVERABLES)
    return "\n".join(parts)


def build_arm_prompts(case, *, structured_context):
    """Build comparable prompts; extra supplied C context MUST be reported.

    Structured context is external to the documents by explicit design.
    It cannot include a reference answer. The tool does not generate it.
    """
    _check_case(case)
    if not isinstance(structured_context, dict) or not structured_context:
        raise ValueError("independent structured context required for C")
    if any(k in structured_context for k in FORBIDDEN):
        raise ValueError("reference answer in C context")
    if any(not isinstance(k, str) or not isinstance(v, str) or not v.strip()
           for k, v in structured_context.items()):
        raise ValueError("structured context values must be nonempty text")
    base = _common_case_text(case)

    fixed = "\n".join(
        f"- {role}: {ROLE_QUESTIONS[role]}" for role in ROLE_ORDER
    )
    plan = plan_mission({
        "question": case["question"], "mission_type": "documentary",
    })
    selected = "\n".join(
        f"- {role}: {ROLE_QUESTIONS[role]}"
        for role in [task["role"] for task in plan["tasks"]]
    )
    prompts = {
        "A": base + "\n\nStrategie: reponse directe, sans prisme de roles.",
        "B": base + "\n\nPerspectives fixes:\n" + fixed,
        "C": (base + "\n\nContexte structure FOURNI (information "
              "supplementaire, non equitable vis-a-vis des autres bras) :\n"
              + json.dumps(structured_context, ensure_ascii=False,
                           sort_keys=True) +
              "\n\nPerspectives adaptees:\n" + selected),
        "D": (base + "\n\nStrategie d'extraction autonome: reconstruis "
              "d'abord les affirmations et leurs sources, la regle de "
              "priorite, les incertitudes et les verifications disponibles. "
              "Choisis ensuite la prochaine action sans supposer les "
              "informations manquantes."),
    }
    return {arm: {"instructions": COMMON_INSTRUCTIONS, "input": prompt}
            for arm, prompt in prompts.items()}


def make_public_packet(fixtures, supplied_contexts):
    """Create input-only fixtures with cryptographic hashes, NO answers."""
    if not isinstance(fixtures, list) or len(fixtures) == 0:
        raise ValueError("nonempty fixture list required")
    ids = [f["input"]["case_id"] for f in fixtures]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate case ID")
    if set(supplied_contexts) != set(ids):
        raise ValueError("C contexts must cover precisely the supplied cases")
    rows = []
    for fixture in fixtures:
        case = fixture["input"]
        built = build_arm_prompts(
            case, structured_context=supplied_contexts[case["case_id"]]
        )
        for arm in ARMS:
            payload = built[arm]
            payload_bytes = json.dumps(payload, ensure_ascii=False,
                                       sort_keys=True).encode("utf-8")
            rows.append({
                "case_id": case["case_id"], "arm": arm,
                "sha256": hashlib.sha256(payload_bytes).hexdigest(),
                "request": payload,
            })
    return {
        "status": "prompts_only_unexecuted",
        "arms": list(ARMS), "case_count": len(ids),
        "request_count": len(rows), "requests": rows,
        "warnings": [
            "No AI model has been called.",
            "C receives extra prestructured context and is NOT a fair pure routing comparison.",
            "All fixtures are PUBLIC and in-sample: not a hidden holdout.",
            "A/B/D are only prompts, not experimentally measured strategies.",
            "Do not put private keys, real holdouts, ratings, or blind mappings in Git.",
        ],
    }


def public_contexts(fixtures):
    """Intentionally NON-oracular common calibration hint for C.

    This does NOT reveal the official rule, date, or answer. The provider
    must build a separately sourced, frozen context in a genuine pilot.
    """
    return {
        f["input"]["case_id"]: {
            "uncertainty_to_test": "Quelle regle officielle et quelle date de reception sont etablies ?",
            "possible_action": "Verifier la source primaire avant de conclure.",
            "scope": "Documents cites seulement.",
        }
        for f in fixtures
    }
