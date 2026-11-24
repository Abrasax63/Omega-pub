"""Regression tests: no false 'math error' when graph fields were omitted."""
import unittest

from omega_hybrid_example_clinic import (
    diagnose_card, graph_orbit_key, parse_edges, practice_pack,
    PRACTICE_NODES,
)
from concept_abstraction_lab import check_axioms

FORMAL = ("reflexive","symmetric","transitive")


def card():
    return {"concept":"Equivalence Relations",
            "formal_axioms":list(FORMAL),
            "positive_edges":[["a","a"],["b","b"],["c","c"]],
            "negative_edges":[["a","b"]]}


class ClinicTests(unittest.TestCase):
    def test_real02_omission_is_not_misreported_as_invalid_graph(self):
        raw=card()
        raw.pop("positive_edges")
        raw.pop("negative_edges")
        r=diagnose_card(raw)
        self.assertEqual(r["reason"],"MISSING_STRUCTURED_EXAMPLES")
        self.assertEqual(r["mathematical_examples_evaluated"],0)
        self.assertEqual(r["missing_fields"],["positive_edges","negative_edges"])

    def test_bad_formal_signature_is_not_promoted(self):
        v=card();v["formal_axioms"]=["reflexive"]
        self.assertEqual(diagnose_card(v)["reason"],"FORMAL_SIGNATURE_MISMATCH")

    def test_positive_counterexample_reports_exact_witness(self):
        v=card();v["positive_edges"]=[["a","b"]]
        r=diagnose_card(v)
        self.assertEqual(r["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertFalse(r["positive"]["actual_holds"])
        self.assertIn("reflexive",r["positive"]["failed_axioms"])
        self.assertIn("symmetric",r["positive"]["failed_axioms"])
        self.assertFalse(r["semantic_prose_certified"])

    def test_negative_that_is_positive_is_not_called_counterexample(self):
        v=card();v["negative_edges"]=[["a","a"],["b","b"],["c","c"]]
        r=diagnose_card(v)
        self.assertEqual(r["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertTrue(r["negative"]["actual_holds"])

    def test_distinguishes_malformed_graph_from_wrong_math(self):
        v=card();v["positive_edges"]=[["a","a"],["a","a"]]
        r=diagnose_card(v)
        self.assertEqual(r["reason"],"MALFORMED_STRUCTURED_EXAMPLES")
        self.assertEqual(r["positive"]["status"],"MALFORMED_EDGES")

    def test_valid_pair_is_bounded_only(self):
        r=diagnose_card(card())
        self.assertEqual(r["status"],"BOUNDED_FORMAL_PASS")
        self.assertFalse(r["semantic_prose_certified"])
        self.assertFalse(r["weights_trained"])

    def test_malformed_edges_never_silently_repaired(self):
        self.assertIsNone(parse_edges([["a","z"]],("a","b","c")))
        self.assertIsNone(parse_edges([["a","a"],["a","a"]],("a","b","c")))
        self.assertIsNone(parse_edges([("a","b")],("a","b","c")))

    def test_practice_has_hidden_truth_and_different_node_count(self):
        result=practice_pack("Equivalence Relations",seed="regression-fixed-seed")
        self.assertEqual(result["status"],"PRACTICE_ONLY_NOT_HOLDOUT")
        prompts=result["model_inputs"]["examples"]
        keys=result["oracle_only"]["examples"]
        self.assertEqual(len(prompts),4)
        self.assertEqual(len(keys),4)
        self.assertTrue(all(len(p["nodes"])==4 for p in prompts))
        self.assertNotIn("oracle_holds",str(result["model_inputs"]))
        self.assertFalse(result["new_skill_demonstrated"])
        self.assertEqual(sorted(k["oracle_holds"] for k in keys),[False,False,True,True])
        self.assertEqual(len(set(graph_orbit_key(
            frozenset(tuple(edge) for edge in p["edges"]),PRACTICE_NODES
            ) for p in prompts)),4)
        by_id={x["case_id"]:x for x in keys}
        for p in prompts:
            rel=frozenset(tuple(e) for e in p["edges"])
            facts=check_axioms(PRACTICE_NODES,rel)
            self.assertEqual(all(facts[a]["holds"] for a in FORMAL),
                             by_id[p["case_id"]]["oracle_holds"])

    def test_invalid_practice_request_fails_closed(self):
        self.assertEqual(practice_pack("Riemann hypothesis")["status"],"BLOCKED")
        self.assertEqual(practice_pack("equivalence relation",count_each=0)["status"],"BLOCKED")


if __name__=="__main__":
    unittest.main()
