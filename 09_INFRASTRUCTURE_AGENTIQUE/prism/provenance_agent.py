"""Generate and test a bounded verifier for GitHub Actions provenance markers."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

from planner import plan_mission
from rce import build_context

EVENT = re.compile(r"^(COMPUTED|COPIED) ([a-zA-Z0-9_-]+) ")
DIGEST = re.compile(r"^[0-9a-f]{64} +(?:[\w.-]+/)*([\w-]+)\.json$")
TIMESTAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
            raise ValueError("Dépôt GitHub invalide.")
        self.base = "https://api.github.com/repos/" + repository

    def get(self, path):
        request = Request(self.base + path)
        if token := os.environ.get("GH_TOKEN"):
            request.add_unredirected_header("Authorization", "Bearer " + token)
        with urlopen(request, timeout=15) as response:
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError("Réponse GitHub trop volumineuse.")
        return payload

    def jobs(self, run):
        return json.loads(self.get(f"/actions/runs/{run}/jobs?per_page=100"))["jobs"]

    def log(self, job):
        return self.get(f"/actions/jobs/{job}/logs").decode("utf-8")


class JournalBundle:
    """Consume a snapshot supplied by an authorized journal collector."""

    def __init__(self, payload, repository, run):
        if not isinstance(payload, dict) or (
            payload.get("repository"), payload.get("run")
        ) != (repository, run):
            raise ValueError("Le dossier ne correspond pas au dépôt et à l'exécution demandés.")
        self.run = run
        self.records = payload.get("jobs")
        self.logs = payload.get("logs")
        if not isinstance(self.records, list) or not isinstance(self.logs, dict):
            raise ValueError("Dossier de journaux incomplet.")
        if any(
            not isinstance(job, dict) or type(job.get("id")) is not int
            or job.get("run_id") != run or not isinstance(job.get("name"), str)
            for job in self.records
        ):
            raise ValueError("Métadonnées de jobs invalides.")
        ids = {str(job["id"]) for job in self.records}
        if len(ids) != len(self.records) or self.logs.keys() - ids:
            raise ValueError("Journaux orphelins ou jobs en double.")

    def jobs(self, run):
        if run != self.run:
            raise ValueError("Exécution différente de celle du dossier.")
        return self.records

    def log(self, job):
        log = self.logs.get(str(job))
        if not isinstance(log, str):
            raise ValueError("Journal absent du dossier.")
        return log


def evidence(log):
    for line in log.splitlines():
        yield TIMESTAMP.sub("", line)


def verdict(log, item, program):
    lines = list(evidence(log))
    patterns = {"digest": DIGEST, "event": EVENT}
    observed = []
    for line in lines:
        for rule in program:
            match = patterns[rule["signal"]].match(line)
            if match and match[rule["item_group"]] == item:
                if "kind" not in rule or match[1] == rule["kind"]:
                    observed.append(rule["verdict"])
    return observed[0] if len(observed) == 1 else "indéterminé"


def learn():
    # Fixtures distinctes des journaux qui seront examinés.
    fingerprint = "a" * 64 + "  test.json\n"
    fixtures = [
        ("COMPUTED test input=1 {}\n" + fingerprint, "recalcul"),
        ("COPIED test from originals\n" + fingerprint, "copie"),
        (fingerprint, "indéterminé"),
        ("COMPUTED test input=1 {}\nCOPIED test from originals\n", "indéterminé"),
    ]
    attempts = []
    program = [{"signal": "digest", "item_group": 1, "verdict": "recalcul"}]
    for _ in range(2):
        failures = [i for i, (log, expected) in enumerate(fixtures, 1)
                    if verdict(log, "test", program) != expected]
        attempts.append({"programme": program, "tests_en_echec": failures})
        if not failures:
            return program, attempts
        program = [
            {"signal": "event", "item_group": 2, "kind": kind, "verdict": status}
            for kind, status in (("COMPUTED", "recalcul"), ("COPIED", "copie"))
        ]
    raise ValueError("Aucun programme n'a réussi les contrôles.")


def audit(source, run, item, question, root, max_logs=6):
    plan = plan_mission({"question": question, "mission_type": "computational"})
    context = build_context(root, question, "computational")
    jobs = source.jobs(run)
    candidates = [
        job for job in jobs if job.get("run_id") == run
        and job.get("conclusion") == "success"
        and job.get("name", "").casefold().startswith("candidate ")
    ]
    program, attempts = learn()
    results = []
    for job in candidates[:max_logs]:
        try:
            status = verdict(source.log(job["id"]), item, program)
        except (OSError, ValueError) as error:
            results.append({"job": job["id"], "nom": job["name"],
                            "verdict": "indéterminé", "motif": str(error)})
        else:
            results.append({"job": job["id"], "nom": job["name"], "verdict": status})
    return {
        "run": run,
        "resultat": item,
        "plan": plan,
        "contexte_sha256": context["manifest"]["content_hash"],
        "tentatives": attempts,
        "programme": program,
        "jobs_candidats": len(candidates),
        "journaux_consultes": len(results),
        "statut": "évalué" if results and all(
            result["verdict"] != "indéterminé" for result in results
        ) and len(results) == len(candidates) else "indéterminé",
        "verdicts": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository")
    parser.add_argument("run", type=int)
    parser.add_argument("item")
    parser.add_argument("--question", default="Le résultat a-t-il été recalculé ou copié ?")
    parser.add_argument("--bundle", type=Path, help="Dossier JSON fourni par un collecteur autorisé")
    args = parser.parse_args()
    try:
        if args.bundle:
            payload = json.loads(args.bundle.read_text(encoding="utf-8"))
            source = JournalBundle(payload, args.repository, args.run)
        else:
            source = GitHub(args.repository)
        result = audit(source, args.run, args.item, args.question,
                       Path(__file__).resolve().parents[2])
    except (OSError, ValueError, KeyError) as error:
        result = {"statut": "indéterminé", "motif": str(error)}
    result["source"] = "dossier_fourni" if args.bundle else "api_github"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["statut"] == "évalué" else 1


if __name__ == "__main__":
    sys.exit(main())
