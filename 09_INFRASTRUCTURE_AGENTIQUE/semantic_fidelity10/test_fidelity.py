import copy
import tempfile
import unittest
from pathlib import Path

from fidelity import (
    ROOT, UnsupportedFormula, git_blob, parse_restricted, source_candidates,
    verify_candidate, run, promote_to_reasoner, interpret_relation,
    independent_interpret_raw
)

MEALY = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/logic_translation_gate08/holdout/BR-MEALY-HELLY-01_BRIQUE.md"
MEALY_SHA = "389957f14632fb253434202a46727ace8688b512"
CAP = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/unseen_math_read07/holdout/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md"
CAP_SHA = "3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7"


def minimal(src="x+2*y<=2*z", heading="Théorème") -> bytes:
    return ("# New card\n## " + heading + "\nLa relation " +
            chr(96) + src + chr(96) + " est proposée.\n").encode()


class Fidelity10Tests(unittest.TestCase):
    def test_finite_semantic_agreement_of_exact_arithmetic(self):
        raw = minimal()
        o = source_candidates(raw, "new.md")
        self.assertEqual(len(o["candidates"]), 1)
        c = o["candidates"][0]
        self.assertEqual(c["ast"]["ops"], ["<="])
        self.assertEqual(c["ast"]["variables"], ["x", "y", "z"])
        self.assertEqual(verify_candidate(raw, c)["finite_valuations_checked"], 125)
        self.assertFalse(c["promotable"])

    def test_direction_and_inequality_are_semantically_distinct(self):
        a = parse_restricted("x<=y")
        b = parse_restricted("x>=y")
        self.assertNotEqual(a, b)
        self.assertTrue(interpret_relation(a, {"x":1,"y":2}))
        self.assertFalse(interpret_relation(b, {"x":1,"y":2}))
        self.assertTrue(independent_interpret_raw("x<=y", {"x":1,"y":2}))

    def test_equality_keeps_exact_values(self):
        a = parse_restricted("a+1=3")
        self.assertTrue(interpret_relation(a, {"a":2}))
        self.assertFalse(interpret_relation(a, {"a":1}))
        self.assertTrue(independent_interpret_raw("a+1=3", {"a":2}))

    def test_more_than_one_ordered_comparison_preserves_orientation(self):
        a = parse_restricted("x<=y<z")
        self.assertEqual(a["ops"], ["<=", "<"])
        self.assertTrue(interpret_relation(a, {"x":1,"y":1,"z":2}))
        self.assertFalse(interpret_relation(a, {"x":2,"y":1,"z":2}))

    def test_calibration_source_syntax_extraction(self):
        self.assertEqual(git_blob(MEALY.read_bytes()), MEALY_SHA)
        a = run(MEALY, MEALY_SHA)
        self.assertTrue(a["checked_all_candidates"])
        self.assertGreaterEqual(len(a["candidates"]), 2)
        self.assertTrue(any("q>=3" in x["literal"] for x in a["candidates"]))
        self.assertEqual(a["horn_rules"], [])
        self.assertEqual(a["automatic_promotions"], 0)

    def test_non_theorem_prohibited(self):
        self.assertEqual(git_blob(CAP.read_bytes()), CAP_SHA)
        out = run(CAP, CAP_SHA)
        self.assertTrue(out["checked_all_candidates"])
        self.assertFalse(any("A_C(ω)" in x["literal"] for x in out["candidates"]))
        self.assertTrue(any(x["reason"] == "OUT_OF_CLAIM_SECTION_OR_UNSAFE"
                            for x in out["abstentions"]))

    def test_proof_and_limit_context_never_promoted(self):
        for heading in ("Preuve", "Limites", "Non-théorème", "Domaine"):
            raw = minimal("x<=y", heading)
            out = source_candidates(raw, "new.md")
            self.assertEqual(len(out["candidates"]), 0)
            self.assertEqual(len(out["abstentions"]), 1)

    def test_unknown_notations_abstain_not_guess(self):
        for formula in ("q(x)=p", "A_C(ω)<=z", "x<=>y",
                        "forall x y", "x/y<=z", "x**2=y",
                        "x ⇒ y", "foo(bar)", "x=\\alpha"):
            raw = minimal(formula)
            out = source_candidates(raw, "new.md")
            self.assertEqual(out["candidates"], [], formula)
            self.assertEqual(len(out["abstentions"]), 1, formula)

    def test_fabricated_span_detected(self):
        raw = minimal()
        item = copy.deepcopy(source_candidates(raw, "new.md")["candidates"][0])
        item["literal"] = "x+2*y<=3*z"
        with self.assertRaisesRegex(ValueError, "SOURCE_QUOTE_NOT_EXACT"):
            verify_candidate(raw, item)

    def test_inverted_ast_operator_detected(self):
        raw = minimal()
        item = copy.deepcopy(source_candidates(raw, "new.md")["candidates"][0])
        item["ast"]["ops"][0] = ">="
        with self.assertRaisesRegex(ValueError, "AST_OR_SECURITY_CONTRACT_TAMPERED"):
            verify_candidate(raw, item)

    def test_missing_domain_not_promoted_even_if_formula_true(self):
        raw = minimal("2<3")
        out = source_candidates(raw, "novel.md")
        self.assertEqual(len(out["candidates"]), 1)
        self.assertEqual(out["candidates"][0]["domain_status"],
                         "NOT_SEMANTICALLY_DERIVED")
        with self.assertRaises(PermissionError):
            promote_to_reasoner(out["candidates"][0])

    def test_source_mutation_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "source.md"
            file.write_bytes(minimal())
            with self.assertRaisesRegex(ValueError, "SOURCE_FINGERPRINT_CHANGED"):
                run(file, "0"*40)
            link = Path(d) / "link.md"
            link.symlink_to(file)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                run(link, git_blob(file.read_bytes()))

    def test_deterministic_and_bounded_computation(self):
        raw = minimal()
        a = source_candidates(raw, "test.md")
        self.assertEqual(a, source_candidates(raw, "test.md"))
        with self.assertRaises(UnsupportedFormula):
            parse_restricted("a+b+c+d+e<5")

    def test_all_outputs_are_candidates_not_horn(self):
        raw = minimal()
        out = source_candidates(raw, "new.md")
        self.assertEqual(out["horn_rules"], [])
        self.assertEqual(out["automatic_promotions"], 0)
        self.assertTrue(all(x["certification"] == "NONE" and
                            x["status"] == "REVIEW_REQUIRED" and
                            not x["promotable"] for x in out["candidates"]))


if __name__ == "__main__":
    unittest.main()
