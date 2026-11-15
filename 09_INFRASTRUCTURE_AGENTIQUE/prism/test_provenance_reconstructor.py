import unittest
from provenance_reconstructor import reconstruct_provenance


class ReconstructorTests(unittest.TestCase):
    def test_declared_parent_reconstructed_but_not_certified(self):
        result = reconstruct_provenance({"evidence": [
            {"id": "a"}, {"id": "b", "derived_from": ["a"]},
        ]})
        self.assertEqual(result["relations"][0]["kind"], "declared_dependency")
        self.assertFalse(result["scientific_certification"])

    def test_matching_hash_not_mistaken_for_shared_run(self):
        result = reconstruct_provenance({"evidence": [
            {"id": "a", "sha256": "digest"}, {"id": "b", "sha256": "digest"},
        ]})
        self.assertEqual([r["kind"] for r in result["relations"]], ["same_content_digest"])

    def test_missing_parent_abstains(self):
        result = reconstruct_provenance({"evidence": [{"id": "b", "derived_from": ["missing"]}]})
        self.assertEqual(result["status"], "indéterminé")

    def test_no_evidence_no_certification(self):
        result = reconstruct_provenance({})
        self.assertEqual(result["relations"], [])
        self.assertFalse(result["scientific_certification"])


if __name__ == "__main__":
    unittest.main()
