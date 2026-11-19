#!/usr/bin/env python3
"""Safety, source-fidelity and oracle tests for BENCH19; no model inference."""
import unittest

from benchmark import (
    blob, benchmark, controls, exhaustive_oracle, messages, metric, model_case,
    prepare, render, source_gate, aggregate,
)
from selector import parse_selection


class FiniteTruthBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = prepare()

    def test_20_frozen_unique_sources_and_oracle_commitments(self):
        self.assertEqual(len(self.tasks), 20)
        self.assertEqual(len({t["ref"]["blob"] for t in self.tasks}), 20)
        self.assertEqual(sum(len(t["ref"]["oracle_true_lines"]) for t in self.tasks), 41)
        self.assertEqual(sum(t["case"]["kind"] == "affine" for t in self.tasks), 10)
        self.assertEqual(sum(t["case"]["kind"] == "quadratic" for t in self.tasks), 10)

    def test_definition_and_oracle_source_are_exact(self):
        for task in self.tasks:
            self.assertEqual(task["raw"], render(task["case"]))
            self.assertEqual(blob(task["raw"]), task["ref"]["blob"])
            truth = exhaustive_oracle(task["case"])
            self.assertEqual(truth, task["ref"]["truth_by_predicate"])

    def test_no_label_is_leaked_into_candidate_lines(self):
        for task in self.tasks:
            candidates = task["candidates"]
            self.assertEqual(len(candidates), 5)
            self.assertEqual([c["line"] for c in candidates], [9,10,11,12,13])
            for c in candidates:
                self.assertTrue(c["source_text"].startswith("Proposition : "))
                self.assertNotIn("vrai", c["source_text"].lower())
                self.assertNotIn("faux", c["source_text"].lower())

    def test_true_and_false_cases_exist(self):
        zero = next(t for t in self.tasks if t["ref"]["id"] == "BF16")
        five = next(t for t in self.tasks if t["ref"]["id"] == "BF03")
        self.assertEqual(len(zero["ref"]["oracle_true_lines"]), 0)
        self.assertEqual(len(five["ref"]["oracle_true_lines"]), 5)

    def test_mechanical_first3_is_lexical_baseline(self):
        reports = controls(self.tasks)
        self.assertEqual(reports["first3"]["aggregate"],
                         reports["lexical_first3"]["aggregate"])
        self.assertEqual(reports["all5_coverage_only"]["aggregate"]["fn"], 0)
        self.assertEqual(reports["none"]["aggregate"]["tp"], 0)

    def test_strict_rejection_without_silent_repair(self):
        allowed = {9, 10, 11, 12, 13}
        for reply in ("999", "9, 9", "9,10,11,12", "9\n10", "ids: 9", "[9]", ""):
            self.assertIsNotNone(parse_selection(reply, allowed)[1], reply)
        self.assertEqual(parse_selection("NONE", allowed), ([], None))

    def test_mock_source_quarantine_and_no_certification(self):
        task = self.tasks[0]
        selected = task["ref"]["oracle_true_lines"][:3]
        row = model_case(task, "offline-mock", call=lambda dialogue: {
            "raw_reply": ",".join(str(x) for x in selected),
            "seconds": 0.01, "usage": {"prompt_tokens": 77, "completion_tokens": 5},
            "finish_reason": "stop", "server_model": "mock-only",
        })
        self.assertEqual(row["status"], "VALID")
        self.assertEqual(row["selected"], selected)
        self.assertEqual(row["metrics"]["fp"], 0)
        self.assertEqual(row["accepted_count"], len(selected))
        self.assertEqual(source_gate(task, selected, "mock-only"), len(selected))

    def test_none_and_out_of_range_are_safe(self):
        task = self.tasks[0]
        for value, valid in (("NONE", True), ("999", False)):
            out = model_case(task, "offline-mock", call=lambda dialogue, result=value: {
                "raw_reply": result, "seconds": 0.01, "usage": {},
                "finish_reason": "stop", "server_model": "mock-only",
            })
            self.assertEqual(out["status"] == "VALID", valid)
            self.assertEqual(out["accepted_count"], 0)
            self.assertEqual(out["metrics"]["tp"], 0)

    def test_scores_do_not_award_free_precision_for_abstention(self):
        self.assertIsNone(metric([], [9,10])["precision"])
        self.assertEqual(metric([], [9,10])["recall"], 0)
        self.assertIsNone(metric([], [])["f1"])
        self.assertEqual(metric([9,11], [9,10])["tp"], 1)
        self.assertEqual(metric([9,11], [9,10])["fp"], 1)

    def test_prompt_is_deterministic_and_never_includes_truth_mask(self):
        task = self.tasks[0]
        a, b = messages(task), messages(task)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 2)
        self.assertNotIn("oracle_true_lines", a[1]["content"])
        self.assertNotIn("truth_by_predicate", a[1]["content"])
        self.assertIn(task["definition"], a[1]["content"])

    def test_score_aggregation(self):
        rows = [{"metrics": metric([9], [9,10])},
                {"metrics": metric([10], [10])}]
        got = aggregate(rows)
        self.assertEqual((got["tp"], got["fp"], got["fn"]), (2,0,1))
        self.assertAlmostEqual(got["micro_f1"], .8)


if __name__ == "__main__":
    unittest.main()
