import copy
import unittest

from public_source_pilot import SOURCES, run_pilot
from action_planning_two_step import plan_with_variable_horizon


class PublicSourceRehearsalTests(unittest.TestCase):
    def test_eight_real_source_questions_are_cited_and_rehearsed(self):
        outcome = run_pilot()
        self.assertEqual(outcome["cases"], 8)
        self.assertEqual(outcome["runnable_cross_checks"], 4)
        self.assertEqual(outcome["source_check_selected"], 8)
        self.assertTrue(all(r["source"].startswith("https://") for r in outcome["results"]))
        self.assertEqual({r["ground_truth"] for r in outcome["results"]}, {"yes", "no"})
        self.assertTrue(all(r["risk_after_primary_source"] == "0" for r in outcome["results"]))
        print("PUBLIC-SOURCE REHEARSAL: 8/8 source-check selections, "
              "4 executable fact cross-checks; NOT model or blind evaluation")

    def test_absent_primary_source_causes_justified_abstention(self):
        row = SOURCES[0]
        case = {
            "case_id": row["id"], "question": row["question"],
            "mission_type": "documentary", "uncertainty": "Source indisponible.",
            "hypotheses": [
                {"id": "y", "decision": "yes", "weight": 1},
                {"id": "n", "decision": "no", "weight": 1},
            ],
            "checks": [
                {"id": "secondary", "action": "verify", "method": "summary",
                 "step": "Consulter un resume", "available": True,
                 "cost_milli": 5, "observations": ["unknown", "unknown"]},
                {"id": "primary", "action": "verify", "method": "source",
                 "step": "Consulter la source officielle", "available": False,
                 "cost_milli": 20, "observations": ["yes", "no"]},
            ],
        }
        self.assertEqual(plan_with_variable_horizon(case, max_depth=4)["optimization"]["action"],
                         "insufficient_evidence")
        case["checks"][1]["available"] = True
        self.assertEqual(plan_with_variable_horizon(case, max_depth=4)["optimization"]["action"],
                         "verify")


if __name__ == "__main__":
    unittest.main()
