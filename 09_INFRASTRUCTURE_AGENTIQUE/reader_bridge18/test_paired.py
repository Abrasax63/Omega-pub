#!/usr/bin/env python3
"""Reader18 regression and safety controls; no model downloads."""
import unittest
from paired import prepare, metrics, controls, one_case, messages
from selector import parse_selection


class MatchedModelExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = prepare()

    def test_sources_are_frozen_and_gold_visible(self):
        self.assertEqual(len(self.cases), 6)
        self.assertEqual(len({c["ref"]["blob"] for c in self.cases}), 6)
        for c in self.cases:
            self.assertEqual(len(c["candidates"]), 5)
            self.assertEqual(len(c["ref"]["conclusion_lines"]), 2)
            offered = {x["line"] for x in c["candidates"]}
            self.assertTrue(set(c["ref"]["conclusion_lines"]).issubset(offered))

    def test_controls_have_consistent_denominators(self):
        values = controls(self.cases)
        self.assertEqual(values["all"]["aggregate"]["tp"], 12)
        self.assertEqual(values["all"]["aggregate"]["fp"], 18)
        self.assertEqual(values["none"]["aggregate"]["tp"], 0)
        self.assertEqual(values["none"]["aggregate"]["fn"], 12)
        self.assertIsNone(values["none"]["aggregate"]["precision"])
        self.assertEqual(values["first3"]["aggregate"]["n"], 6)

    def test_rejected_arbitrary_and_duplicate_ids(self):
        allow = {5, 6, 7, 8, 9}
        for reply in ("999", "5,5", "5,6,7,8", "5\n6", "**5**", "note: 5", ""):
            self.assertIsNotNone(parse_selection(reply, allow)[1], reply)
        self.assertEqual(parse_selection("NONE", allow), ([], None))

    def test_mock_valid_selection_reconstructed_and_quarantined(self):
        p = self.cases[0]
        chosen = p["ref"]["conclusion_lines"]
        row = one_case(p, "3b", call=lambda chats: {
            "raw_reply": ",".join(map(str, chosen)),
            "seconds": 0.01, "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            "finish_reason": "stop", "server_model": "fake-only",
        })
        self.assertEqual(row["status"], "VALID")
        self.assertEqual(row["metrics"]["tp"], 2)
        self.assertEqual(row["metrics"]["fp"], 0)
        self.assertEqual(row["accepted_count"], 2)
        self.assertEqual(row["certifications"], 0)
        self.assertEqual(row["horn_rules"], 0)

    def test_mock_abstention_and_malformed_outputs(self):
        p = self.cases[1]
        for reply, status in (("NONE", "VALID"), ("999", "REJECTED"), ("1,2,3", "REJECTED")):
            row = one_case(p, "0p5b", call=lambda chats, answer=reply: {
                "raw_reply": answer, "seconds": 0.01, "usage": None,
                "finish_reason": "stop", "server_model": "fake-only",
            })
            self.assertEqual(row["status"], status)
            self.assertEqual(row["selected"], [])
            self.assertEqual(row["accepted_count"], 0)
            self.assertEqual(row["metrics"]["tp"], 0)

    def test_exact_scoring_not_accuracy_of_unreviewed_math(self):
        self.assertIsNone(metrics([], [5, 8])["precision"])
        self.assertEqual(metrics([5, 7], [5, 8])["tp"], 1)
        self.assertEqual(metrics([5, 7], [5, 8])["fp"], 1)
        self.assertEqual(metrics([5, 7], [5, 8])["fn"], 1)
        self.assertAlmostEqual(metrics([5, 7], [5, 8])["f1"], 0.5)

    def test_matched_messages_are_deterministic(self):
        p = self.cases[0]["candidates"]
        self.assertEqual(messages(p), messages(p))
        self.assertEqual(len(messages(p)), 2)
        self.assertIn("numéros", messages(p)[0]["content"])


if __name__ == "__main__":
    unittest.main()
