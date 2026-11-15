import unittest
from provenance_trace_inference import infer_from_trace, evaluate_blind_traces, infer_buildkit_copy


class TraceInferenceTests(unittest.TestCase):
    def test_buildkit_trace_requires_verbose_and_done(self):
        log = ("#22 1.0 + cp -av ./source/file.tar out/\n"
               "#22 1.1 './source/file.tar' -> 'out/file.tar'\n"
               "#22 DONE 1.2s")
        result = infer_buildkit_copy(log, "out/file.tar")
        self.assertEqual(result["relations"][0]["from"], "source/file.tar")
        self.assertEqual(result["relations"][0]["to"], "out/file.tar")
        self.assertFalse(result["scientific_certification"])
        self.assertEqual(infer_buildkit_copy(log.replace("#22 DONE 1.2s", ""),
                                            "out/file.tar")["relations"], [])
        self.assertEqual(infer_buildkit_copy(log.replace("out/file.tar'","out/other.tar'"),
                                            "out/file.tar")["relations"], [])

    def test_hidden_relation_from_raw_trace(self):
        result = infer_from_trace("start\nCOPY source.csv -> result.csv\nend")
        self.assertEqual([(x["from"], x["to"]) for x in result["relations"]],
                         [("source.csv", "result.csv")])
        self.assertEqual(result["relations"][0]["line"], 2)
        self.assertFalse(result["scientific_certification"])

    def test_hash_and_unrelated_messages_cannot_prove_lineage(self):
        self.assertEqual(infer_from_trace("same sha256 abc\nrun=12\n")["relations"], [])

    def test_malformed_line_abstains(self):
        result = infer_from_trace("COPY a ->\nCOPY b -> b")
        self.assertEqual(result["relations"], [])
        self.assertEqual(len(result["errors"]), 2)

    def test_synthetic_blind_oracle_comparison(self):
        cases = [
            {"id": "positive", "raw": "start\nCOPY a -> b\n",
             "oracle": [("a", "b")]},
            {"id": "negative", "raw": "sha256 same\n", "oracle": []},
            {"id": "missing", "raw": "COPY malformed", "oracle": []},
        ]
        report = evaluate_blind_traces(cases)
        self.assertEqual(report["totals"],
                         {"true_positive": 1, "false_positive": 0, "false_negative": 0})
        self.assertEqual(report["real_world_generalization"], "indéterminé")


if __name__ == "__main__":
    unittest.main()
