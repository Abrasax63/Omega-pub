"""Verify that REAL-01 metadata and verdicts are not overstated."""
import json
import unittest

from omega_hybrid_schema_real01 import examine, ARCHIVED_RUN, ARCHIVED_ARTIFACT


class SchemaReal01Tests(unittest.TestCase):
    def test_single_mock_reply_diagnostic_only(self):
        invocations=[]
        def model(messages, tokens):
            invocations.append((messages,tokens))
            return {"text":json.dumps({
                "positive_edges":[["a","a"],["b","b"],["c","c"]],
                "negative_edges":[["a","b"]]})}
        r=examine(model)
        self.assertEqual(len(invocations),1)
        self.assertEqual(r["schema_repair"]["status"],"BOUNDED_GRAPH_PASS_QUARANTINE_ONLY")
        self.assertFalse(r["benchmark_of_new_competence"])
        self.assertTrue(r["exposed_previous_case_not_a_holdout"])
        self.assertFalse(r["model_weights_updated"])
        self.assertEqual(r["scientific_claims_certified"],0)
        self.assertEqual(r["evidence_source_run"],ARCHIVED_RUN)
        self.assertEqual(r["evidence_artifact"],ARCHIVED_ARTIFACT)

    def test_an_incorrect_graph_is_preserved_as_negative(self):
        r=examine(lambda *_: {"text":json.dumps({
            "positive_edges":[["a","b"]],"negative_edges":[["a","b"]]})})
        self.assertEqual(r["schema_repair"]["status"],"QUARANTINE")
        self.assertEqual(r["schema_repair"]["reason"],"MATHEMATICAL_COUNTEREXAMPLE")
        self.assertFalse(r["benchmark_of_new_competence"])


if __name__=="__main__":unittest.main()
