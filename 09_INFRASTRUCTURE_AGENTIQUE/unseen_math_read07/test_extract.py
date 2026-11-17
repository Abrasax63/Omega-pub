import copy
import tempfile
import unittest
from pathlib import Path

from extract import (
    ROOT, git_blob, parse_document, run, verify_literal_citations,
)

CAL = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/cross_domain_math05/source_snapshot/BR-OBS-CAP-01_DYNAMIC_CAPACITY.md"
CAL_BLOB = "5cb676c73d385b557aa5282e9514848383c196bc"


class UnknownMathExtractorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CAL.read_bytes()
        cls.cal = parse_document(cls.raw, CAL.as_posix())

    def test_calibration_source_identity(self):
        self.assertEqual(git_blob(self.raw), CAL_BLOB)
        self.assertEqual(self.cal["source_blob"], CAL_BLOB)

    def test_explicit_premise_and_conclusion_are_quoted(self):
        cs = [c for c in self.cal["candidates"]
              if c["kind"] == "CONDITIONAL_CANDIDATE"]
        self.assertGreaterEqual(len(cs), 2)
        self.assertTrue(any("Cap_A(gω)" in c["consequence_literal"] for c in cs))
        self.assertEqual(verify_literal_citations(self.raw, self.cal), [])

    def test_limits_not_promoted_as_theorems(self):
        lim = [c for c in self.cal["candidates"]
               if c["kind"] == "LIMITATION_LITERAL"]
        self.assertGreaterEqual(len(lim), 3)
        self.assertTrue(all(c["scope"] == "DOCUMENT_LIMIT_ONLY" for c in lim))
        self.assertTrue(all("UNREVIEWED" in c["confidence"] for c in lim))

    def test_contextual_assumption_is_not_lost(self):
        cs = [c for c in self.cal["candidates"]
              if c["kind"] == "CONDITIONAL_CANDIDATE"]
        self.assertTrue(any(c["scope"] == "CONTEXT_REQUIRED" for c in cs))

    def test_no_if_then_no_generated_rule(self):
        raw = b"# math\n## Lemma\nSupposons X sans consequence.\n"
        r = parse_document(raw, "synthetic.md")
        self.assertEqual(r["counts"]["CONDITIONAL_CANDIDATE"], 0)

    def test_nested_if_does_not_inherit_previous_statement(self):
        raw = b"# math\n## Lemma\nSupposons A.\nSi B, alors C.\n"
        r = parse_document(raw, "synthetic.md")
        conditional = [x for x in r["candidates"]
                       if x["kind"] == "CONDITIONAL_CANDIDATE"]
        self.assertEqual(len(conditional), 1)
        self.assertEqual(conditional[0]["scope"], "CONTEXT_REQUIRED")
        self.assertNotIn("Supposons A", conditional[0]["condition_literal"])

    def test_verifier_rejects_fabricated_conclusion(self):
        m = copy.deepcopy(self.cal)
        c = next(x for x in m["candidates"]
                 if x["kind"] == "CONDITIONAL_CANDIDATE")
        c["consequence_literal"] = "impossible theorem from nowhere"
        errors = verify_literal_citations(self.raw, m)
        self.assertTrue(any("INVENTED_CONTENT" in x for x in errors))

    def test_verifier_rejects_fabricated_line(self):
        m = copy.deepcopy(self.cal)
        m["candidates"][0]["start_line"] = 100000
        errors = verify_literal_citations(self.raw, m)
        self.assertTrue(any("BAD_RANGE" in x for x in errors))

    def test_source_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "unknown.md"
            p.write_bytes(self.raw + b"\nTampered\n")
            with self.assertRaisesRegex(ValueError, "source modified"):
                run(p, CAL_BLOB)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "source.md"
            p.write_bytes(self.raw)
            link = Path(d) / "symlink.md"
            link.symlink_to(p)
            with self.assertRaisesRegex(ValueError, "symlink"):
                run(link)

    def test_deterministic_output(self):
        self.assertEqual(self.cal, parse_document(self.raw, CAL.as_posix()))
        self.assertTrue(run(CAL, CAL_BLOB)["cited_output_integrity"])

    def test_invalid_utf8_rejected(self):
        with self.assertRaises(UnicodeDecodeError):
            parse_document(b"\xff", "bad.md")


if __name__ == "__main__":
    unittest.main()
