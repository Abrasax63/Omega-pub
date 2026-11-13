"""Find and verify the archived PR #18 calculation through the Omega RCE."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

from rce import build_context, safe_repo_path

REPOSITORY = "https://github.com/Abrasax63/Omega-pub"
CASE = "09_INFRASTRUCTURE_AGENTIQUE/prototype/locality_l_plus_1"
SOURCE = f"{CASE}/SOURCE.md"
RUN, JOB = 42788979270, 129737263482
JOB_URL = f"{REPOSITORY}/actions/runs/{RUN}/job/{JOB}"
COMMIT = "ac1a76e9c01491bd4a1365be6be425d0e26b9d45"
LOG_HASH = "396c30f0e8b3f5aee7caf957534a0c74a31a81608714580515e435d07724f9b1"
SCRIPT_HASH = "b4556e78b12edbd2467eb7166576d4202cfa1cdaa10a3113730a5be5d6487946"
OUTPUT_MARKER = "L_PLUS_1_EXHAUSTIVE_TEST: PASS"
SEARCH_TERMS = {"localite", "l+1", "325", "325468", "468", "18"}


def read_case(root, name):
    path = safe_repo_path(root, f"{CASE}/{name}")
    if path is None:
        raise ValueError(f"Pièce introuvable ou hors du dépôt : {name}")
    return path


def audit(root, question, *, replay=False):
    root = root.resolve()
    try:
        context = build_context(root, question, "computational")
        source = next(
            (item for item in context["candidate_documents"]
             if item["path"] == SOURCE and SEARCH_TERMS.intersection(item["matched_terms"])),
            None,
        )
        if source is None:
            raise ValueError("Fiche du calcul introuvable dans le contexte RCE.")

        report = read_case(root, "SOURCE.md").read_text(encoding="utf-8")
        runs = re.findall(r"^- Exécution : (.+)$", report, re.MULTILINE)
        checkouts = re.findall(r"^- Checkout CI : (.+)$", report, re.MULTILINE)
        if runs != [JOB_URL] or checkouts != [COMMIT]:
            raise ValueError("Le lien du job ou le checkout diffère de la référence épinglée.")

        log = read_case(root, "run.log").read_bytes()
        if sha256(log).hexdigest() != LOG_HASH:
            raise ValueError("L'extrait du journal diffère de celui récupéré pour ce job.")
        script = read_case(root, "check.py").read_bytes()
        if sha256(script).hexdigest() != SCRIPT_HASH:
            raise ValueError("Le script diffère de la version récupérée au checkout CI.")

        output = log.decode("utf-8").split(OUTPUT_MARKER, 1)[1]
        total = int(re.search(r"^GLOBAL_LOCAL_COMPARISONS_TOTAL: (\d+)$", output, re.MULTILINE)[1])
        if replay:
            completed = subprocess.run(
                [sys.executable, "-I", "-"],
                input=script,
                capture_output=True,
                cwd=root,
                timeout=120,
                check=True,
            )
            if completed.stdout != (OUTPUT_MARKER + output).encode():
                raise ValueError("La sortie du rejeu diffère de la sortie L+1 épinglée.")
        return {
            "statut": "raccordé",
            "source_rce": source["path"],
            "contexte_sha256": context["manifest"]["content_hash"],
            "pr": f"{REPOSITORY}/pull/18",
            "job_ci": JOB_URL,
            "checkout_ci": COMMIT,
            "script_sha256": SCRIPT_HASH,
            "comparaisons": total,
            "contre_exemple": False,
            "portee": {"etats_max": 6, "L": [2, 3]},
            "rejeu_local": replay,
        }
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {"statut": "indéterminé", "motif": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    result = audit(args.repo_root, args.question, replay=args.replay)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["statut"] == "raccordé" else 1


if __name__ == "__main__":
    sys.exit(main())
