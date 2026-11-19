"""Acquire a model-written memo and compare independent target completions."""

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENDPOINT = "http://127.0.0.1:8091/v1/chat/completions"
WEIGHTS = "724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
ENGINE = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
SCHEDULE = (("order", "MEMO"), ("order", "SANS_MEMO"),
            ("limit", "SANS_MEMO"), ("limit", "MEMO"))
TARGET_SYSTEM = (
    "Résous le problème courant. Format unique : ORDRE MOT1 MOT2 si tu varies "
    "l'ordre à composition constante, CHARGE MOT1 MOT2 si tu varies la composition, "
    "ou NONE. Les mots contiennent F et G seulement. Une note d'un autre problème "
    "peut figurer dans le contexte. Évalue sa pertinence pour le problème courant."
)


def read_json(path):
    return json.loads(path.read_bytes())


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def complete(system, prompt, cap):
    params = {
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": cap, "temperature": 0, "seed": 19, "stream": False,
    }
    request = urllib.request.Request(
        ENDPOINT, data=json.dumps(params, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    start = time.monotonic()
    row = {"request": params}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=180) as response:
            row["http_status"] = response.status
            row["raw"] = response.read(100_001).decode("utf-8", errors="replace")
            if len(row["raw"]) > 100_000:
                row["error"] = "RESPONSE_SIZE_LIMIT"
    except OSError as err:
        row["error"] = str(err)
    row["elapsed_ms"] = round((time.monotonic() - start) * 1000)
    return row


def decode(row, cap):
    if row.get("http_status") != 200 or "error" in row:
        return None
    try:
        data = json.loads(row["raw"])
        choice = data["choices"][0]
        text = choice["message"]["content"]
        usage = data["usage"]
        if not isinstance(text, str) or not 0 < usage["completion_tokens"] <= cap:
            return None
        return {"text": text.strip(), "usage": usage, "finish": choice["finish_reason"]}
    except (KeyError, ValueError, IndexError, TypeError):
        return None


def plant(word):
    signal = 0
    for command in word:
        signal = (signal + 1 if command == "A" else 2 * signal) % 5
    return signal


def observe(reply):
    match = re.fullmatch(r"(SAME|DIFFERENT)\s+([AB]{2,5})\s+([AB]{2,5})", reply)
    if match is None:
        return {"status": "INVALID_PROBE", "experiments": 0}
    prediction, left, right = match.groups()
    values = [plant(left), plant(right)]
    actual = "SAME" if values[0] == values[1] else "DIFFERENT"
    return {
        "status": "OBSERVED", "prediction": prediction, "words": [left, right],
        "outputs": values, "observed": actual, "experiments": 2,
        "prediction_refuted": prediction != actual,
        "isolated_order_effect": left.count("A") == right.count("A")
        and left.count("B") == right.count("B") and actual == "DIFFERENT",
    }


def acquire(output):
    probe = complete(
        "Tu conçois une expérience. Format exact : SAME MOT1 MOT2 ou DIFFERENT MOT1 MOT2.",
        "Un appareil audio affiche un entier final après une suite de commandes A et B. "
        "Il repart de zéro pour chaque mot. Tu ne connais pas ses règles. Tu as deux "
        "essais de longueur 2 à 5 et veux tester si réordonner les mêmes commandes peut "
        "modifier l'affichage. Choisis les deux suites et prédis si leurs sorties "
        "seront identiques (SAME) ou différentes (DIFFERENT).",
        40,
    )
    answer = decode(probe, 40)
    trace = observe(answer["text"]) if answer else {"status": "INFRA_FAILURE", "experiments": 0}
    result = {"weights_sha256": WEIGHTS, "llama_cpp_commit": ENGINE, "probe": probe, "trace": trace}
    save(output, result)
    result["reflection"] = complete(
        "Écris une note autonome en français. Une phrase sur la méthode. Une sur sa "
        "limite. Une sur le prochain essai quand la méthode ne distingue rien. "
        "Ne transforme pas une absence d'effet observé en preuve générale.",
        "Voici le relevé des essais que tu as choisis sur l'appareil audio. "
        "Quels tests conseillerais-tu sur un autre problème, à partir des observations ?\n"
        + json.dumps(trace, ensure_ascii=False),
        160,
    )
    save(output, result)


def target_prompt(task, trace, note):
    return ("Relevé commun d'un ancien problème audio : " + json.dumps(trace, ensure_ascii=False)
            + "\nNote facultative : " + note + "\nProblème courant : " + task)


def transfer(acquired, output):
    acquisition = read_json(acquired)
    reflection = decode(acquisition["reflection"], 160)
    note = reflection["text"] if reflection else ""
    tasks = read_json(HERE / "tasks.json")
    result = {"acquired": acquisition, "budget": {"cap": 64, "n_ctx": 4096}, "targets": []}
    for case, arm in SCHEDULE:
        annotation = note if arm == "MEMO" else "(emplacement neutre)"
        row = complete(TARGET_SYSTEM, target_prompt(tasks[case], acquisition["trace"], annotation), 64)
        result["targets"].append({"case": case, "arm": arm, **row})
        save(output, result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("acquire", "transfer"))
    parser.add_argument("--acquired", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.phase == "acquire":
        acquire(args.acquired)
    else:
        transfer(args.acquired, args.output)
