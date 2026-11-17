import copy
import tempfile
import unittest
from pathlib import Path

from translate import blob, propose, independently_verify, run, export_to_horn, ROOT

CAL = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/unseen_math_read07/holdout_v2/BR-STATE-01_ETATS_PREDICTIFS_REPARATION.md"
CAL_SHA = "b7f79410a589dd8ba62a997860c924593e85a73c"


class TranslationGate08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = CAL.read_bytes()
        cls.result = run(CAL, CAL_SHA)

    def test_calibration_fingerprint_and_exact_conditions(self):
        self.assertEqual(blob(self.raw), CAL_SHA)
        self.assertTrue(self.result["literal_integrity_passed"])
        self.assertGreaterEqual(len(self.result["proposals"]), 1)
        self.assertTrue(any("E" in p["antecedent"]["literal"]
                            and "équivalence" in p["consequent"]["literal"]
                            for p in self.result["proposals"]))

    def test_no_automatic_horn_rule_even_for_an_explicit_conditional(self):
        self.assertEqual(self.result["horn_rules"], [])
        self.assertEqual(self.result["automatic_promotion_count"], 0)
        self.assertTrue(all(p["promotable"] is False
                            and p["status"] == "REVIEW_REQUIRED"
                            for p in self.result["proposals"]))
        with self.assertRaises(PermissionError):
            export_to_horn(self.result["proposals"][0])

    def test_every_char_span_is_exactly_replayable(self):
        self.assertEqual(independently_verify(self.raw, self.result), [])
        for p in self.result["proposals"]:
            original = self.raw.decode("utf-8").splitlines()[p["line"]-1]
            for key in ("antecedent", "consequent"):
                span = p[key]
                self.assertEqual(span["literal"],
                    original[span["char_start"]:span["char_end"]])

    def test_non_theorem_heading_is_blocked(self):
        raw = ("# Any card\n## Non-théorème\n"
               "Si A, alors B.\n").encode("utf-8")
        o = propose(raw, "synthetic.md")
        self.assertEqual(o["proposals"], [])
        self.assertEqual(o["blocked"][0]["reason"], "UNSAFE_SECTION")
        self.assertEqual(independently_verify(raw, o), [])

    def test_limitation_heading_is_blocked(self):
        raw = ("# Any card\n## Limites\n"
               "Si P, alors Q.\n").encode()
        o = propose(raw, "synthetic.md")
        self.assertEqual(len(o["proposals"]), 0)
        self.assertEqual(len(o["blocked"]), 1)

    def test_nested_conditional_is_blocked(self):
        raw = ("# Any card\n## Théorème\n"
               "Si A et si B, alors C.\n").encode()
        o = propose(raw, "synthetic.md")
        self.assertEqual(o["proposals"], [])
        self.assertEqual(o["blocked"][0]["reason"], "NESTED_OR_RESTRICTED_CONNECTIVE")

    def test_iff_not_silently_represented_as_one_way_if(self):
        raw = ("# Any card\n## Théorème\n"
               "Si et seulement si A, alors B.\n").encode()
        o = propose(raw, "synthetic.md")
        self.assertEqual(o["proposals"], [])

    def test_no_explicit_then_is_blocked(self):
        raw = ("# Any card\n## Théorème\n"
               "Si x est entier, la borne est vraie.\n").encode()
        o = propose(raw, "synthetic.md")
        self.assertEqual(len(o["proposals"]), 0)
        self.assertEqual(o["blocked"][0]["reason"], "NO_EXPLICIT_SAME_LINE_THEN")

    def test_one_line_syntax_only_is_not_a_semantic_proof(self):
        raw = ("# Any card\n## Théorème\n"
               "Si A, alors B.\n").encode()
        o = propose(raw, "synthetic.md")
        self.assertEqual(len(o["proposals"]), 1)
        x = o["proposals"][0]
        self.assertEqual(x["antecedent"]["literal"], "A")
        self.assertEqual(x["consequent"]["literal"], "B.")
        self.assertEqual(x["relation"], "IMPLICATION_SYNTAX_ONLY")
        self.assertEqual(independently_verify(raw, o), [])

    def test_fabricated_conclusion_detected_by_independent_replay(self):
        altered = copy.deepcopy(self.result)
        altered["proposals"][0]["consequent"]["literal"] = "toute théorie universelle est vraie"
        self.assertIn("INVENTED_OR_NORMALIZED_TEXT",
                      independently_verify(self.raw, altered))

    def test_unsafe_promotion_detected(self):
        altered = copy.deepcopy(self.result)
        altered["horn_rules"] = [{"name": "unverified"}]
        self.assertIn("UNREVIEWED_PROMOTION", independently_verify(self.raw, altered))

    def test_corrupt_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "card.md"
            p.write_bytes(self.raw+b"\nchanged\n")
            with self.assertRaisesRegex(ValueError, "source changed"):
                run(p, CAL_SHA)

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "s.md"
            p.write_bytes(self.raw)
            q = Path(tmp) / "link.md"
            q.symlink_to(p)
            with self.assertRaisesRegex(ValueError, "symlink"):
                run(q, CAL_SHA)

    def test_source_independent_reproducible(self):
        self.assertEqual(run(CAL, CAL_SHA), run(CAL, CAL_SHA))


if __name__ == "__main__":
    unittest.main()
