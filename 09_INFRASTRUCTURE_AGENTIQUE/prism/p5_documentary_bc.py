"""Run the public documentary B/C calibration and produce a blind packet."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from secrets import SystemRandom
from time import perf_counter

from p5_dispatch import DispatchLedger
from planner import ROLE_ORDER, ROLE_QUESTIONS, plan_mission

CASE = "P5-PUBLIC-DOC-K17"
EXPERIMENT = "p5-documentary-bc"
QUESTION = """Quel délai faut-il annoncer pour le dossier K-17 ? Cite le passage
décisif et indique l'information manquante. Les documents sont fictifs.

A — Notice v1, § 3 : « Le service répond dans les 10 jours ouvrés suivant
la réception du dossier. »
B — Notice v2, § 3 : « Le service répond dans les 5 jours ouvrés suivant
la réception du dossier. » § 8 : « Cette version s’applique aux dossiers
reçus à partir du 1er octobre inclus. Les dossiers reçus avant cette date
restent soumis à la v1. »
C — Message interne du 4 octobre : « K-17 est en cours. Comme la nouvelle
notice est publiée, comptez 5 jours pour tous les dossiers ouverts. »
La date de réception de K-17 ne figure pas dans le dossier transmis."""
INSTRUCTIONS = ("Réponds en français en 120 mots maximum. Utilise uniquement les documents "
                "fournis. Applique les perspectives indiquées puis donne une réponse unifiée.")


def inputs_by_arm():
    plan = plan_mission({"question": QUESTION, "mission_type": "documentary"})
    roles = {"B": ROLE_ORDER, "C": [task["role"] for task in plan["tasks"]]}
    return {arm: QUESTION + "\n\nPerspectives :\n" + "\n".join(
        f"- {role} : {ROLE_QUESTIONS[role]}" for role in selected
    ) for arm, selected in roles.items()}


def run(directory, client, *, model, token_cap, output_cap, simulated):
    from openai_responses_adapter import build_openai_responses_record

    if not 0 < output_cap < token_cap:
        raise ValueError("require 0 < output cap < total cap per arm")
    root = Path(directory)
    if any((parent / ".git").exists() for parent in root.resolve().parents):
        raise ValueError("keep grading keys and raw runs outside Git checkouts")
    root.mkdir(mode=0o700)  # New path only: an interrupted run cannot be silently replayed.
    inputs = inputs_by_arm()
    order = ["B", "C"]
    SystemRandom().shuffle(order)
    frozen = {
        "mode": "simulation" if simulated else "live", "model": model,
        "instructions": INSTRUCTIONS, "inputs": inputs, "run_order": order,
        "token_cap_per_arm": token_cap, "output_cap_per_arm": output_cap,
    }
    frozen_bytes = (json.dumps(frozen, ensure_ascii=False, indent=2) + "\n").encode()
    (root / "run-private.json").write_bytes(frozen_bytes)
    options = client.with_options(max_retries=0, timeout=30.0).responses
    requests = {
        arm: dict(model=model, instructions=INSTRUCTIONS, input=inputs[arm],
                  tools=[], truncation="disabled")
        for arm in order
    }
    expected = {}
    for arm, request in requests.items():
        count = options.input_tokens.count(**request).input_tokens
        if type(count) is not int or count < 0 or count + output_cap > token_cap:
            raise ValueError("input preflight exceeds token cap or returned invalid count")
        expected[arm] = count

    ledger = DispatchLedger(root / "events.jsonl", EXPERIMENT)
    answers, records = {}, []
    for arm, request in requests.items():
        identity = (EXPERIMENT, CASE, arm, 1, "generate", 1, f"k17-{arm}-1")
        ledger.reserve(identity)
        started_at = datetime.now(timezone.utc).isoformat()
        started = perf_counter()
        response = options.create(**request, max_output_tokens=output_cap, store=False)
        row = build_openai_responses_record(
            response, experiment_id=EXPERIMENT, case_id=CASE, arm=arm, call_id=identity[-1],
            started_at=started_at, elapsed_seconds=perf_counter() - started, tool_calls=None,
            context={"repetition": 1, "operation_id": "generate", "attempt": 1,
                     "requested_model": model,
                     "prompt_sha256": hashlib.sha256((INSTRUCTIONS + "\n" + inputs[arm]).encode()).hexdigest()},
        )
        ledger.finish_payload(identity, row, response.model_dump(mode="json"))
        records.append(row)
        if (row["status"] != "completed" or row["model"] != model
                or row["input_tokens"] != expected[arm] or row["output_tokens"] is None
                or row["output_tokens"] > output_cap or not response.output_text.strip()):
            raise ValueError("response differs from the frozen contract; no grading packet emitted")
        answers[arm] = response.output_text
    ledger.verify_results(records)

    labels = ["B", "C"]
    SystemRandom().shuffle(labels)
    key = dict(zip(("X", "Y"), labels))
    (root / "key-private.json").write_text(json.dumps(key) + "\n", encoding="utf-8")
    packet = {"mode": frozen["mode"], "case": CASE, "responses": {
        label: answers[arm] for label, arm in key.items()
    }}
    (root / "grading.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="new private output directory")
    parser.add_argument("--model", required=True, help="exact, versioned provider model ID")
    parser.add_argument("--token-cap", type=int, required=True, help="total input/output tokens per arm")
    parser.add_argument("--output-cap", type=int, required=True, help="output tokens per arm")
    parser.add_argument("--live", action="store_true", help="allow two preflight and two generation API requests")
    args = parser.parse_args()
    if not args.live or not os.environ.get("OPENAI_API_KEY"):
        parser.error("live generation requires --live and OPENAI_API_KEY; use p5_documentary_bc_test.py for simulation")
    from openai import DefaultHttpxClient, OpenAI

    with OpenAI(base_url="https://api.openai.com/v1", max_retries=0,
                http_client=DefaultHttpxClient(trust_env=False, follow_redirects=False)) as client:
        run(args.directory, client, model=args.model, token_cap=args.token_cap,
            output_cap=args.output_cap, simulated=False)


if __name__ == "__main__":
    main()
