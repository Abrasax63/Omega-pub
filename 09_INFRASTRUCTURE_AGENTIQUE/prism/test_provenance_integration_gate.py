"""Synthetic non-regression tests. Not a real GitHub provenance validation."""
import unittest
from provenance_integration_gate import assess_evidence, UNKNOWN


def piece(run, artifact):
    return {"run_id": run, "artifact_id": artifact,
            "source_uri": "https://github.com/example/repo/actions/runs/" + run,
            "verified_execution": True, "sha256": "same-content"}


class ProvenanceGateTests(unittest.TestCase):
    def test_mirror_not_independent(self):
        result = assess_evidence({"scientific_status": "EXPÉRIMENTAL",
                                  "evidence": [piece("100", "a"), piece("100", "b")]})
        self.assertEqual(result["verdict"], "same_execution")

    def test_distinct_runs_not_automatically_independent(self):
        result = assess_evidence({"scientific_status": "CALCUL EXACT",
                                  "evidence": [piece("100", "a"), piece("101", "b")]})
        self.assertEqual(result["verdict"], UNKNOWN)
        self.assertEqual(result["reason"], "independence_not_attested")

    def test_missing_origin_abstains(self):
        result = assess_evidence({"scientific_status": "DÉMONTRÉ",
                                  "evidence": [{"artifact_id": "a"}]})
        self.assertEqual(result["reason"], "unresolved_origin")

    def test_unverified_execution_abstains(self):
        item = piece("100", "a")
        item["verified_execution"] = False
        self.assertEqual(assess_evidence({"scientific_status": "DÉMONTRÉ",
                                          "evidence": [item]})["verdict"], UNKNOWN)

    def test_attested_runs_still_not_certified(self):
        result = assess_evidence({"scientific_status": "EXPÉRIMENTAL",
                                  "evidence": [piece("100", "a"), piece("101", "b")],
                                  "independence_attested": True,
                                  "independence_evidence_uri": "https://example.org/audit"})
        self.assertEqual(result["verdict"], "distinct_attested_runs")
        self.assertEqual(result["reason"], "attested_not_certified")


if __name__ == "__main__":
    unittest.main()
