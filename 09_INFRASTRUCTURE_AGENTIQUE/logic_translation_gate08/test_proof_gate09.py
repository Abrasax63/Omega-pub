import unittest
from skeleton09 import run, independent_check
from evaluate_proof_gate09 import evaluate, HERE, ENGINE, ENGINE_BLOB
from translate import blob

COMMUTE = HERE / "holdout09/BR-ACC-STATE-COMMUTE-01_BRIQUE.md"
COMMUTE_BLOB = "c4c89930f075983e085da5e38c956f12dc61186e"
CAP = HERE.parent / "unseen_math_read07/holdout/BR-OBS-CAP-02_SUPPORT_VS_WEIGHT.md"
CAP_BLOB = "3b5f4a645de2520e7ddd461ef98dd116d3b5fbd7"


class PosthocProofContextGate(unittest.TestCase):
    def test_new_logic_version_pin(self):
        self.assertEqual(blob(ENGINE.read_bytes()), ENGINE_BLOB)

    def test_proof_section_formulas_are_blocked_not_promoted(self):
        result = run(COMMUTE, COMMUTE_BLOB)
        self.assertTrue(result["citations_valid"])
        self.assertFalse(any(x["section"].lower().startswith("preuve") for x in result["items"]))
        self.assertTrue(any(x["reason"] == "RELATION_IN_NON_THEOREM_OR_LIMIT" and
                            "π(T_u T_a x)" in x["source_quote"] for x in result["blocked"]))
        self.assertTrue(any(x["literal"] == "q(H)=Hbar" for x in result["items"]))

    def test_non_theorem_still_blocked(self):
        res = run(CAP, CAP_BLOB)
        self.assertTrue(any(x["reason"] == "RELATION_IN_NON_THEOREM_OR_LIMIT" and
                            "A_C(ω)" in x.get("literal", "") for x in res["blocked"]))
        self.assertEqual(independent_check(CAP.read_bytes(), res), [])

    def test_same_manual_cohort_is_posthoc_not_new_holdout(self):
        r = evaluate()
        self.assertEqual(r, evaluate())
        self.assertEqual(r["salient_total"], 12)
        self.assertTrue(r["no_proof_candidates"])
        self.assertTrue(r["all_citations_valid"])
        self.assertEqual(r["automatic_horn_rules"], 0)
        self.assertTrue(r["not_independent_holdout"])

    def test_restricted_source_does_not_inject_rules(self):
        res = run(COMMUTE, COMMUTE_BLOB)
        self.assertEqual(res["horn_rules"], [])
        self.assertTrue(all(x["promotable"] is False for x in res["items"]))

if __name__ == "__main__":
    unittest.main()
