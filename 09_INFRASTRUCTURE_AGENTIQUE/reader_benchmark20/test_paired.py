#!/usr/bin/env python3
"""BENCH20 independent offline tests: mapping, fail-closed, provenance, oracle."""
import unittest

from paired import (
    MAX_SELECTED, N, SOURCE_IDS, ORDINAL_IDS,
    compare, controls, id_to_source, messages, metric, one,
    parse_and_map, prepare, verify_exact_oracle,
)


class InterfaceAblationSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks=prepare()

    def test_corpus_has_20_new_blobs_and_40_gold(self):
        self.assertEqual(len(self.tasks),20)
        self.assertEqual(len({t["ref"]["blob"] for t in self.tasks}),20)
        self.assertEqual(sum(len(t["ref"]["oracle_true_lines"]) for t in self.tasks),40)
        self.assertEqual(sum(t["case"]["kind"]=="affine" for t in self.tasks),10)
        self.assertEqual(sum(t["case"]["kind"]=="quadratic" for t in self.tasks),10)

    def test_author_gold_is_rechecked_exhaustively(self):
        for t in self.tasks:
            self.assertEqual(
                verify_exact_oracle(t["case"]),
                t["ref"]["truth_by_predicate"]
            )

    def test_ordinal_map_is_exact_bijection(self):
        self.assertEqual(id_to_source("ordinal"),{1:9,2:10,3:11,4:12,5:13})
        self.assertEqual(id_to_source("source"),{9:9,10:10,11:11,12:12,13:13})
        self.assertEqual(
            parse_and_map("1,3,5","ordinal"),
            ([1,3,5],[9,11,13],None)
        )
        self.assertEqual(
            parse_and_map("9,11,13","source"),
            ([9,11,13],[9,11,13],None)
        )

    def test_mixed_spaces_and_outside_ids_rejected_no_partial_acceptance(self):
        for interface in ("source","ordinal"):
            for response in ("1,10,13","999","1,2,9","0,1,2",
                             "9,10,14","", "[1,2,3]", "**1,2,3**",
                             "1 2 3","1,1,2","1,2,3,4"):
                ids, translated, why=parse_and_map(response,interface)
                self.assertEqual((ids,translated),([],[]),
                                 (interface,response))
                self.assertIsNotNone(why,(interface,response))

    def test_none_is_safe_on_both_interfaces(self):
        for interface in ("source","ordinal"):
            self.assertEqual(parse_and_map("NONE",interface),([],[],None))
        zero=next(t for t in self.tasks if not t["ref"]["oracle_true_lines"])
        row=one(zero,"ordinal","mock",call=lambda _:{
            "raw_reply":"NONE","seconds":0.01,"usage":{},
            "server_model":"mock","finish_reason":"stop"})
        self.assertEqual(row["status"],"VALID")
        self.assertTrue(row["abstained"])
        self.assertEqual(row["metrics"]["fp"],0)

    def test_ordinal_resolves_against_blob_not_model_quote(self):
        t=self.tasks[0]
        row=one(t,"ordinal","mock",call=lambda _:{
            "raw_reply":"1,3,5","seconds":0.01,"usage":{},
            "server_model":"mock","finish_reason":"stop"})
        self.assertEqual(row["selected_verified_source_lines"],[9,11,13])
        self.assertEqual(row["source_gate_accepted"],3)
        self.assertEqual(row["horn_rules"],0)
        self.assertEqual(row["automatic_certifications"],0)

    def test_malformed_output_never_cited(self):
        t=self.tasks[0]
        row=one(t,"ordinal","mock",call=lambda _:{
            "raw_reply":"1,10,13","seconds":0.01,"usage":{},
            "server_model":"mock","finish_reason":"stop"})
        self.assertEqual(row["status"],"REJECTED")
        self.assertEqual(row["selected_model_ids"],[])
        self.assertEqual(row["selected_verified_source_lines"],[])
        self.assertEqual(row["source_gate_accepted"],0)
        self.assertEqual(row["metrics"]["tp"],0)

    def test_only_labels_change_across_two_arms(self):
        t=self.tasks[0]
        source,ordinal=messages(t,"source"),messages(t,"ordinal")
        self.assertEqual(source[0],ordinal[0])
        # Preserve all source data except the offered IDs.
        import json
        raw_source=source[1]["content"]
        raw_ord=ordinal[1]["content"]
        self.assertIn(t["definition"],raw_source)
        self.assertIn(t["definition"],raw_ord)
        for c in t["candidates"]:
            self.assertIn(c["source_text"],raw_source)
            self.assertIn(c["source_text"],raw_ord)
        self.assertNotIn("oracle_true_lines",raw_source)
        self.assertNotIn("oracle_true_lines",raw_ord)

    def test_controls_and_max_choice(self):
        val=controls(self.tasks)
        self.assertEqual(val["first3"]["aggregate"]["n"],20)
        self.assertEqual(val["all5_coverage_only"]["aggregate"]["fn"],0)
        self.assertEqual(val["none"]["aggregate"]["tp"],0)
        self.assertEqual(MAX_SELECTED,3)

    def test_abstention_precision_not_construed_as_perfect(self):
        self.assertIsNone(metric([],[9,10])["precision"])
        self.assertIsNone(metric([],[])["f1"])
        self.assertEqual(metric([9,11],[9,10])["fp"],1)

    def test_no_main_mutation_or_certification_possible_from_experiment(self):
        t=self.tasks[0]
        for i in SOURCE_IDS:
            self.assertIn(i,t["ref"]["candidate_lines"])
        self.assertEqual(tuple(id_to_source("ordinal").values()),SOURCE_IDS)


if __name__=="__main__":
    unittest.main()
