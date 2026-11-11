"""P5-ABC-001: strictly comparable A/B/C prompt *inputs*, not model outputs.

An old four-arm P5 constructor unfairly gave C privileged structured context.
This alternative builds a common immutable evidence body for every arm.
Only strategy instructions change. This is public calibration data, never a
blind holdout, and never an LLM benchmark without real isolated executions.

Use the already-implemented Omega planner plan_mission; do NOT replace it.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess

from planner import ROLE_ORDER, ROLE_QUESTIONS, plan_mission

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "p5_multidomain_public_cases_2026-11-11.json"
EXPECTED_GIT_BLOB = "3eb87dc5b8851dd30c753cb54e0d03659c62441b"
DATA_COMMIT = "experiment/provenance-equal-budget-2026-11-11"
PREREG_COMMIT = "e7a66ee2275d94ec42473ac306c4d2f430cad4a2"
CONDITIONS = ("intact", "perturbed")
ARMS = ("A", "B", "C")
ORDER_SEED = 20261111
DOMAINS = {"github": "documentary", "http": "documentary",
           "uri": "computational", "python": "computational"}
COMMON_INSTRUCTIONS = (
    "Réponds en français, de façon concise. Justifie ton verdict, distingue "
    "fait vérifié et observation non authentifiée, et indique les incertitudes. "
    "N'invente pas d'accès aux URL, ni de vérification exécutée. "
    "Utilise exclusivement les informations fournies. "
    "La même limite de sortie s'applique aux trois stratégies."
)

# Identical in all arms: substantive task + access to the same documents.
BASE_REQUIREMENTS = (
    "Donne une réponse oui/non seulement si les éléments fournis le justifient.",
    "Si la conclusion n'est pas vérifiable, exprime l'incertitude et la prochaine vérification utile.",
    "Indique quelle observation est décisive et quelles vérifications n'ont pas été faites.",
)

# Forbidden if present as *keys* inside the model-visible payload.
LEAKED_FIELDS = {
    "truth", "gold", "answer_key", "correct_answer", "reference_answer",
    "secondary_note_is_fabricated", "spoof_primary_in_adversarial",
    "is_spoofed", "condition", "expected", "label", "head_sha",
}

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",",":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")

def digest(x):
    return sha256(canonical(x)).hexdigest()

def _assert_no_hidden_fields(obj):
    if isinstance(obj,dict):
        if LEAKED_FIELDS & set(obj):
            raise ValueError("private grading/perturbation field leaked to prompt")
        for child in obj.values():_assert_no_hidden_fields(child)
    elif isinstance(obj,list):
        for child in obj:_assert_no_hidden_fields(child)

def get_rows(path=DATA, *, check_blob=True):
    if check_blob:
        run=subprocess.run(
            ["git","hash-object",str(path)],capture_output=True,text=True)
        if run.returncode!=0 or run.stdout.strip()!=EXPECTED_GIT_BLOB:
            raise ValueError("source dataset does not match preregistered Git blob")
    source=json.loads(Path(path).read_text(encoding="utf-8"))
    if source.get("status")!="PUBLIC_CALIBRATION_NOT_HOLDOUT":
        raise ValueError("wrong source status")
    cases=source.get("cases")
    if not isinstance(cases,list) or len(cases)!=24:
        raise ValueError("24 public cases required")
    if len({r["id"] for r in cases})!=24:
        raise ValueError("duplicate case id")
    domains=Counter(r["domain"] for r in cases)
    if domains!={"github":6,"http":6,"uri":6,"python":6}:
        raise ValueError("changed 4-domain population")
    if sum(r["spoof_primary_in_adversarial"] is True for r in cases)!=8:
        raise ValueError("changed perturbation map")
    if sum(r["secondary_note_claim"] != r["truth"] for r in cases)!=8:
        raise ValueError("changed secondary notes")
    for row in cases:
        required={"id","domain","question","truth","reference",
                  "verification","secondary_note_claim",
                  "secondary_note_is_fabricated",
                  "spoof_primary_in_adversarial"}
        if not required.issubset(row):
            raise ValueError("incomplete source case")
        if not all(type(row[k]) is bool for k in (
            "truth","secondary_note_claim","secondary_note_is_fabricated",
            "spoof_primary_in_adversarial")):
            raise ValueError("invalid label types")
        if not row["secondary_note_is_fabricated"]:
            raise ValueError("cannot quietly treat fabricated note as authentic")
    return cases

def public_evidence(row, condition):
    """The identical model-visible information for ALL A/B/C arms."""
    if condition not in CONDITIONS:
        raise ValueError("unknown calibration condition")
    if row["domain"] not in DOMAINS:
        raise ValueError("unsupported domain")
    claimed=row["truth"]
    if condition=="perturbed" and row["spoof_primary_in_adversarial"]:
        claimed=not claimed
    # A primary "observation" is fabricated for testing. NEVER claim to have
    # fetched the referenced official source here or to authenticate this note.
    shared={
        "question":row["question"],
        "task_domain":row["domain"],
        "mission_type":DOMAINS[row["domain"]],
        "reference_url_not_opened":row["reference"],
        "source_scope":(
            "Exercice de calibration publique : des observations simulées "
            "sont attribuées aux sources ; elles ne sont pas authentifiées. "
            "L'URL n'a pas été consultée par le modèle. "
            "Ne pas traiter l'étiquette « primaire » comme une signature."),
        "observations":[
            {"id":"source_primary_simulated","category":"simulation non authentifiée",
             "claim_text":"Cette affirmation est vraie." if claimed
                          else "Cette affirmation est fausse."},
            {"id":"secondary_note_simulated","category":"note secondaire fictive",
             "claim_text":("Selon une note secondaire, l'affirmation est vraie."
                           if row["secondary_note_claim"] else
                           "Selon une note secondaire, l'affirmation est fausse.")}
        ],
        "common_deliverables":list(BASE_REQUIREMENTS),
    }
    _assert_no_hidden_fields(shared)
    return shared

def _roles_for(row):
    # This only knows the public domain and question shared with A/B.
    selected=plan_mission({
        "question":row["question"],
        "mission_type":DOMAINS[row["domain"]],
    })
    roles=tuple(task["role"] for task in selected["tasks"])
    if not roles or any(role not in ROLE_ORDER for role in roles):
        raise AssertionError("unrecognized adaptive role")
    return roles

def make_prompts(row,condition):
    shared=public_evidence(row,condition)
    plan_roles=_roles_for(row)
    fixed_roles=tuple(ROLE_ORDER)
    # In the visible request only, A/B/C can use the *same* source and
    # information. Different role instructions are the treatment, not data.
    instructions={
        "A":("Réponds directement avec les livrables communs, "
             "sans perspectives spécialisées."),
        "B":"Perspectives fixes : "+ " ; ".join(
            f"{role} : {ROLE_QUESTIONS[role]}" for role in fixed_roles),
        "C":"Perspectives sélectionnées par le Prisme : "+ " ; ".join(
            f"{role} : {ROLE_QUESTIONS[role]}" for role in plan_roles),
    }
    output={}
    for arm in ARMS:
        request={
            "instructions":COMMON_INSTRUCTIONS,
            "input":{
                "shared":shared,
                "strategy":instructions[arm],
            },
        }
        _assert_no_hidden_fields(request)
        output[arm]={"request":request,
                     "prompt_sha256":digest(request),
                     "shared_sha256":digest(shared),
                     "adaptive_roles":list(plan_roles) if arm=="C" else None,
                     "fixed_roles":list(fixed_roles) if arm=="B" else None,
                     "model_calls":0}
    return output

def preflight(public_cases=None):
    cases=public_cases if public_cases is not None else get_rows()
    if len(cases)!=24:
        raise ValueError("frozen public calibration requires 24 tasks")
    requests=[]
    coverage=Counter()
    role_counts=Counter()
    total_toggles=0
    for row in cases:
        for condition in CONDITIONS:
            variants=make_prompts(row,condition)
            shares=[variants[arm]["request"]["input"]["shared"]
                    for arm in ARMS]
            if not (shares[0]==shares[1]==shares[2]):
                raise AssertionError("unequal evidence inputs")
            if len({canonical(share) for share in shares})!=1:
                raise AssertionError("not byte-identical common evidence")
            if len({variants[arm]["shared_sha256"] for arm in ARMS})!=1:
                raise AssertionError("different shared data digest")
            for arm in ARMS:
                item=variants[arm]
                requests.append({
                    "case_id":row["id"],
                    "condition":condition,
                    "domain":row["domain"],
                    "arm":arm,
                    **item,
                })
                coverage[(row["domain"],condition,arm)]+=1
            role_counts[tuple(variants["C"]["adaptive_roles"])]+=1
            if condition=="perturbed" and row["spoof_primary_in_adversarial"]:
                total_toggles+=1
    if len(requests)!=144 or len(coverage)!=4*2*3:
        raise AssertionError("missing frozen cases or arms")
    if any(v!=6 for v in coverage.values()) or total_toggles!=8:
        raise AssertionError("domain or perturbation count drift")
    # Execution order is frozen for synthetic preflight only. Any actual
    # blinded campaign needs a new *private* seed and independent sessions.
    schedule=[]
    for row in cases:
        for condition in CONDITIONS:
            order=list(ARMS)
            local=random.Random(digest(
                {"case":row["id"],"condition":condition,"seed":ORDER_SEED}
            )).shuffle(order)
            schedule.append({"case_id":row["id"],"condition":condition,
                             "arms":order})
    return {
        "status":"PREFLIGHT_ONLY_P5_LIVE_NOT_RUN",
        "source":"PUBLIC_CALIBRATION_NOT_HOLDOUT",
        "frozen_case_blob_sha":EXPECTED_GIT_BLOB,
        "prereg_commit":PREREG_COMMIT,
        "case_count":24,
        "conditions":list(CONDITIONS),
        "arms":list(ARMS),
        "prompt_count":len(requests),
        "real_model_calls":0,
        "human_independent_graders":0,
        "real_token_counts":None,
        "external_holdout_evaluated":False,
        "fair_common_evidence":True,
        "independent_sessions_executed":False,
        "role_counts":{"|".join(k):v for k,v in sorted(role_counts.items())},
        "requests":requests,
        "synthetic_preflight_schedule":schedule,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output")
    opt=parser.parse_args()
    packet=preflight()
    if opt.output:
        Path(opt.output).write_text(json.dumps(
            packet,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
            encoding="utf-8")
    print("OMEGA_P5_ABC_PREFLIGHT "+json.dumps({
        key:packet[key] for key in (
            "status","case_count","conditions","arms","prompt_count",
            "real_model_calls","human_independent_graders",
            "real_token_counts","fair_common_evidence","role_counts",
        )
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
