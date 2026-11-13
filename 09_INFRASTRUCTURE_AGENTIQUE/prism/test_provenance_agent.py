from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from provenance_agent import audit, learn


class ProvenanceAgentTests(unittest.TestCase):
    def test_repair_and_select_logs(self):
        class Source:
            reads = []

            def jobs(self, run):
                return [
                    {"id": job, "name": name, "run_id": run, "conclusion": "success"}
                    for job, name in [(1, "origin"), (2, "Candidate alpha"), (3, "Candidate beta")]
                ]

            def log(self, job):
                self.reads.append(job)
                return {2: "COMPUTED a input=11 {}", 3: "COPIED a from originals"}[job]

        source = Source()
        with TemporaryDirectory() as directory:
            result = audit(source, 10, "a", "Recalcul ou copie ?", Path(directory))
        self.assertEqual(source.reads, [2, 3])
        self.assertEqual([row["verdict"] for row in result["verdicts"]], ["recalcul", "copie"])
        self.assertEqual(result["statut"], "évalué")
        self.assertEqual([row["tests_en_echec"] for row in result["tentatives"]], [[2, 3], []])

    def test_final_program_has_both_events(self):
        program, _ = learn()
        self.assertEqual({rule["kind"] for rule in program}, {"COMPUTED", "COPIED"})

    def test_bundle_run_and_missing_log(self):
        from provenance_agent import JournalBundle

        repo = "owner/repo"
        payload = {
            "repository": repo, "run": 10,
            "jobs": [{"id": 2, "name": "Candidate alpha", "run_id": 10, "conclusion": "success"}],
            "logs": {},
        }
        with self.assertRaises(ValueError):
            JournalBundle(payload, repo, 11)
        source = JournalBundle(payload, repo, 10)
        with TemporaryDirectory() as directory:
            result = audit(source, 10, "a", "Recalcul ou copie ?", Path(directory))
        self.assertEqual(result["statut"], "indéterminé")

    def test_bundle_rejects_orphan_log(self):
        from provenance_agent import JournalBundle

        with self.assertRaises(ValueError):
            JournalBundle(
                {"repository": "owner/repo", "run": 10, "jobs": [], "logs": {"1": "COMPUTED a "}},
                "owner/repo", 10,
            )
