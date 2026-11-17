import copy
import tempfile
import unittest
from pathlib import Path

from extract import git_blob, ROOT
from structure_v2 import extract_structures, verify_structure_output, run

CAL = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/unseen_math_read07/holdout/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md"
CAL_BLOB = "3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7"


class MathStructureV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CAL.read_bytes()
        cls.report = extract_structures(cls.raw, CAL.as_posix())

    def test_calibration_identity_and_type_coverage(self):
        self.assertEqual(git_blob(self.raw), CAL_BLOB)
        counts = self.report["counts"]
        self.assertEqual(counts["THEOREM_STATEMENT_LITERAL"], 1)
        self.assertEqual(counts["NON_THEOREM_WARNING"], 1)
        self.assertGreaterEqual(counts["DEFINITION_LITERAL"], 2)
        self.assertGreaterEqual(counts["LIMITATION_LITERAL"], 1)

    def test_non_theorem_is_not_treated_as_theorem(self):
        blocked = [x for x in self.report["items"] if x["kind"] == "NON_THEOREM_WARNING"]
        self.assertEqual(len(blocked), 1)
        self.assertIn("A_C(ω) ≤ Cap(ω)", blocked[0]["source_quote"])
        positive = [x for x in self.report["items"]
                    if x["kind"] == "THEOREM_STATEMENT_LITERAL"]
        self.assertEqual(len(positive), 1)
        self.assertIn("r_C(ω) ≤ μ_T(ω)", positive[0]["source_quote"])
        self.assertNotIn("A_C(ω) ≤ Cap(ω)", positive[0]["source_quote"])

    def test_no_proof_claimed_and_literal_citations(self):
        self.assertEqual(verify_structure_output(self.raw, self.report), [])
        self.assertTrue(all(x["scientific_status"] == "CANDIDATE_UNREVIEWED_NOT_A_PROOF"
                            for x in self.report["items"]))

    def test_deliberate_fake_citation_rejected(self):
        altered = copy.deepcopy(self.report)
        altered["items"][0]["source_quote"] += "\nInvented conclusion"
        self.assertTrue(any("INVENTED_CITATION" in e for e in
                            verify_structure_output(self.raw, altered)))

    def test_negative_heading_never_promoted_even_with_formula(self):
        raw = ("# New math\n## Non-théorème\n"
               "On ne peut pas conclure\n\nQ≤R.\n").encode("utf-8")
        output = extract_structures(raw, "fresh.md")
        self.assertEqual(output["counts"]["THEOREM_STATEMENT_LITERAL"], 0)
        self.assertEqual(output["counts"]["NON_THEOREM_WARNING"], 1)
        self.assertEqual(verify_structure_output(raw, output), [])

    def test_unrecognized_prose_not_made_a_theorem(self):
        raw = b"# New math\n## Discussion\nA theorem is believed true.\n"
        output = extract_structures(raw, "fresh.md")
        self.assertEqual(output["counts"]["THEOREM_STATEMENT_LITERAL"], 0)

    def test_source_modification_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            altered = Path(d) / "source.md"
            altered.write_bytes(self.raw + b"\nModified\n")
            with self.assertRaisesRegex(ValueError, "changed after freeze"):
                run(altered, CAL_BLOB)
            link = Path(d) / "link.md"
            link.symlink_to(altered)
            with self.assertRaisesRegex(ValueError, "symlink"):
                run(link)

    def test_determinism_and_calibration_integrity(self):
        self.assertEqual(self.report, extract_structures(self.raw, CAL.as_posix()))
        self.assertTrue(run(CAL, CAL_BLOB)["citations_valid"])


if __name__ == "__main__":
    unittest.main()
