"""Minimal derived fixtures from *real* REAL-02 artifacts, no quoted text.

Source runs: 45118912669, 45119536096, archived artifacts
14793460094 and 14792897432. Not independent holdouts.
"""
import unittest

from omega_hybrid_example_clinic import diagnose_card

BASE = {"concept":"Equivalence Relations",
        "formal_axioms":["reflexive","symmetric","transitive"]}


class ArchivedReal02Forensics(unittest.TestCase):
    def test_run_45118912669_missing_c_loop_is_math_failure(self):
        card={**BASE,
              "positive_edges":[["a","a"],["b","b"],["a","b"],["b","a"]],
              "negative_edges":[["a","b"],["b","a"]]}
        outcome=diagnose_card(card)
        self.assertEqual(outcome["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertEqual(outcome["positive"]["witnesses"]["reflexive"],["c","c"])
        self.assertEqual(outcome["negative"]["status"],"CORRECT")
        self.assertEqual(outcome["mathematical_examples_evaluated"],2)

    def test_run_45119536096_graphs_missing_is_not_math_failure(self):
        outcome=diagnose_card(BASE)
        self.assertEqual(outcome["reason"],"MISSING_STRUCTURED_EXAMPLES")
        self.assertEqual(outcome["mathematical_examples_evaluated"],0)


if __name__=="__main__": unittest.main()
