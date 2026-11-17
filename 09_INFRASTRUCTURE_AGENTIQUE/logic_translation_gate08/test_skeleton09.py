import copy
import tempfile
import unittest
from pathlib import Path
from translate import ROOT
from skeleton09 import (
    normalize, independent_check, parse_chain, run, export_to_horn
)

KNOWN_CTRL = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/logic_translation_gate08/holdout/BR-CTRL-01_CERTIFICAT_MEMOIRE_INFINIE.md"
KNOWN_CTRL_SHA = "3d52e5372f2eaecc6c66d960b0601e727325e2b2"
KNOWN_MEALY = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/logic_translation_gate08/holdout/BR-MEALY-HELLY-01_BRIQUE.md"
KNOWN_MEALY_SHA = "389957f14632fb253434202a46727ace8688b512"
KNOWN_CAP = ROOT / "09_INFRASTRUCTURE_AGENTIQUE/unseen_math_read07/holdout/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md"
KNOWN_CAP_SHA = "3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7"


class FormalSkeleton09(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctrl = run(KNOWN_CTRL, KNOWN_CTRL_SHA)
        cls.mealy = run(KNOWN_MEALY, KNOWN_MEALY_SHA)
        cls.cap = run(KNOWN_CAP, KNOWN_CAP_SHA)

    def test_calibration_recovers_literal_biconditional(self):
        self.assertGreaterEqual(self.ctrl["summary"]["biconditional_count"], 1)
        iff = next(x for x in self.ctrl["items"] if x["kind"] == "BICONDITIONAL_SYNTAX")
        self.assertIn("F", iff["parsed"]["left"])
        self.assertIn("un cycle accessible", iff["parsed"]["right"])
        self.assertEqual(iff["parsed"]["connective"].lower(), "si et seulement si")
        self.assertFalse(iff["promotable"])

    def test_calibration_recovers_domain_formulas_without_claim(self):
        relations = [x for x in self.mealy["items"] if x["kind"] == "RELATION_CHAIN_SYNTAX"]
        self.assertTrue(any(r["literal"] == "r_IO=1" for r in relations))
        self.assertTrue(any(r["literal"] == "q>=3" for r in relations))
        self.assertTrue(all(r["status"] == "REVIEW_REQUIRED" for r in relations))

    def test_non_theorem_formula_is_blocked(self):
        self.assertTrue(any(x["reason"] == "RELATION_IN_NON_THEOREM_OR_LIMIT"
                            and "A_C(ω)" in x.get("literal", "")
                            for x in self.cap["blocked"]))
        self.assertFalse(any(x["kind"] == "RELATION_CHAIN_SYNTAX"
                             and "A_C(ω)" in x["literal"] for x in self.cap["items"]))

    def test_positive_theorem_chain_preserves_comparator_order(self):
        found = [x for x in self.cap["items"] if x["kind"] == "RELATION_CHAIN_SYNTAX"
                 and "r_C(ω)" in x["literal"]]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["parsed"]["operators"], ["≤", "≤", "≤"])
        self.assertEqual(independent_check(KNOWN_CAP.read_bytes(), self.cap), [])

    def test_mixed_or_formal_biconditional_code_is_not_treated_as_chain(self):
        for s in ("x <=> y", "x -> y", "x ⇔ y", "a=b;c=d", "a\\b=c"):
            self.assertIsNone(parse_chain(s))

    def test_chains_do_not_infer_inequalities_from_inequalities(self):
        self.assertEqual(parse_chain("alpha≤beta≥gamma"),
                         (["alpha", "beta", "gamma"], ["≤", "≥"]))

    def test_no_horn_export_and_no_proof_claim(self):
        for result in (self.ctrl, self.mealy, self.cap):
            self.assertEqual(result["automatic_promotion_count"], 0)
            self.assertEqual(result["horn_rules"], [])
            self.assertTrue(all(x["epistemic_status"] == "UNINTERPRETED_SYNTAX_NOT_THEOREM"
                                for x in result["items"]))
        with self.assertRaises(PermissionError):
            export_to_horn(self.ctrl["items"])

    def test_inverted_operator_is_caught_by_independent_checker(self):
        bad = copy.deepcopy(self.cap)
        target = next(x for x in bad["items"] if x["kind"] == "RELATION_CHAIN_SYNTAX")
        target["parsed"]["operators"][0] = ">="
        self.assertIn("INVENTED_OR_INVERTED_RELATION",
                      independent_check(KNOWN_CAP.read_bytes(), bad))

    def test_fabricated_quote_is_caught_by_independent_checker(self):
        bad = copy.deepcopy(self.mealy)
        bad["items"][0]["source_quote"] += " invented"
        self.assertIn("FABRICATED_CITATION",
                      independent_check(KNOWN_MEALY.read_bytes(), bad))

    def test_false_promotion_is_caught(self):
        bad = copy.deepcopy(self.ctrl)
        bad["items"][0]["promotable"] = True
        self.assertIn("UNSAFE_PROMOTION",
                      independent_check(KNOWN_CTRL.read_bytes(), bad))

    def test_unknown_source_symlink_and_tamper_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "source.md"
            p.write_bytes(KNOWN_CTRL.read_bytes()+b"\nnew")
            with self.assertRaisesRegex(ValueError, "source changed"):
                run(p, KNOWN_CTRL_SHA)
            link = Path(tmp) / "link.md"
            link.symlink_to(p)
            with self.assertRaisesRegex(ValueError, "symlink"):
                run(link, KNOWN_CTRL_SHA)

    def test_new_synthetic_document_without_source_id_table(self):
        raw = ("# Unknown novel card\n## Théorème\n"
               "Si x, alors y.\n"
               "Les valeurs sont " + chr(96) + "x≤y" + chr(96) + ".\n"
               "La loi est vraie si et seulement si les entrées conviennent.\n").encode()
        r = normalize(raw, "any-name.md")
        self.assertEqual(r["summary"]["relation_chain_count"], 1)
        self.assertEqual(r["summary"]["biconditional_count"], 1)
        self.assertEqual(r["legacy_conditional_count"], 1)
        self.assertEqual(independent_check(raw, r), [])

    def test_outputs_deterministic_and_exactly_replayable(self):
        for path, sha in ((KNOWN_CTRL, KNOWN_CTRL_SHA),
                          (KNOWN_MEALY, KNOWN_MEALY_SHA), (KNOWN_CAP, KNOWN_CAP_SHA)):
            a = run(path, sha)
            self.assertEqual(a, run(path, sha))
            self.assertTrue(a["citations_valid"])


if __name__ == "__main__":
    unittest.main()
