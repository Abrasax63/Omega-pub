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
