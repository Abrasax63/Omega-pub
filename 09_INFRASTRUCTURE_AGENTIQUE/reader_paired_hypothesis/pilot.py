"""Read two frozen Markdown sources and record one real CPU completion per source."""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from read import run as read_source


CASES = {
    "fiche-a": "8917a6d491304fb975b66632d644a76661c37346",
    "fiche-b": "f24227688b012a67ed89fa09d7e2b151644c7eab",
}
MODEL_SHA = "724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
LLAMA_COMMIT = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
ENDPOINT = "http://127.0.0.1:8091/v1/chat/completions"
MAX_TOKENS = 64
SEED = 19


def source_path(case):
    return HERE / "fixtures" / f"{case}.md"


def view(case):
    source = read_source(source_path(case), CASES[case])
    packets = source["packets"]
    if len(packets) > 10 or source["stats"]["packets_with_display_math"] != 3:
        raise ValueError(f"{case}: unexpected packet coverage")
    return [
        {"line": packet["start_line"] + offset, "text": text, "packet": packet["packet_id"]}
        for packet in packets
        for offset, text in enumerate(packet["source_quote"].splitlines())
        if text.strip()
    ]


def messages_for(lines):
    visible = [[item["line"], item["text"]] for item in lines]
    return [
        {
            "role": "system",
            "content": (
                "Extrais les citations d'une note de mathématiques. Donne trois numéros "
                "séparés par des virgules, dans cet ordre : le domaine de T, la formule "
                "de la loi applicable au régime désigné pour la relation candidate, la "
                "formule de cette relation. Cite les lignes des formules, pas les "
                "délimiteurs LaTeX. Ne juge pas la vérité de la relation. Réponds "
                "seulement par les trois numéros ou NONE si le rattachement est ambigu."
            ),
        },
        {"role": "user", "content": json.dumps(visible, ensure_ascii=False)},
    ]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def infer(output):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    report = {
        "weights_sha256": MODEL_SHA,
        "llama_cpp_commit": LLAMA_COMMIT,
        "rows": [],
        "paid_api_calls": 0,
    }
    for case, blob in CASES.items():
        line_view = view(case)
        messages = messages_for(line_view)
        params = {
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": 0,
            "seed": SEED,
            "stream": False,
        }
        row = {"case": case, "source_blob": blob, "request": params}
        report["rows"].append(row)
        request = urllib.request.Request(
            ENDPOINT, data=json.dumps(params).encode(),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        start = time.monotonic()
        try:
            with opener.open(request, timeout=180) as response:
                row["http_status"] = response.status
                row["raw_response"] = response.read(100_001).decode("utf-8", errors="replace")
                if len(row["raw_response"]) > 100_000:
                    row["transport_error"] = "RESPONSE_SIZE_LIMIT"
        except OSError as error:
            row["transport_error"] = str(error)
        row["elapsed_ms"] = round(1000 * (time.monotonic() - start))
        write_json(output, report)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--raw", type=Path, required=True)
    infer(cli.parse_args().raw)
