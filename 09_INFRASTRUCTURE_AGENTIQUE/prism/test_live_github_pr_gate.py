"""Reproduce the preregistered live-GitHub PR-gate pilot from frozen observations.

Runs Omega's *actual* finite evidence planner against 12 public external
source outcomes. No model call, independent human review, or secret holdout.
The external connector was queried at collection time; this test must NOT
silently substitute fabricated data or request a moving external state.
"""
import json
from pathlib import Path
import unittest
from action_planning_two_step import optimize_policy

OBSERVATIONS = Path(__file__).with_name("live_github_pr_gate_observations_2026-11-11.json")


def finite_case():
    hypotheses = [
        {"id": "neither", "decision": "reject", "weight": 1},
        {"id": "tests_only", "decision": "reject", "weight": 1},
        {"id": "merged_only", "decision": "reject", "weight": 1},
        {"id": "both", "decision": "accept", "weight": 1},
    ]
    checks = [
        {"id": "00-merged", "action": "verify", "step": "Read GitHub PR metadata",
         "method": "github_get_pr_info", "cost_milli": 5, "available": True,
         "observations": ["no", "no", "yes", "yes"]},
        {"id": "01-tests", "action": "verify", "step": "Read changed PR filenames",
         "method": "github_list_pr_changed_filenames",
         "cost_milli": 5, "available": True,
         "observations": ["no", "yes", "no", "yes"]},
    ]
    return {"case_id": "live-pr-gate", "question": "Merged and touches tests?",
            "mission_type": "mathematical",
            "uncertainty": "Actual external PR status and file paths are unknown",
            "hypotheses": hypotheses, "checks": checks}


def execute_policy(policy, row, case):
    remaining = list(range(len(case["hypotheses"])))
    visited = []
    node = policy
    while "check_id" in node:
        check = next(c for c in case["checks"] if c["id"] == node["check_id"])
        assert check["id"] not in visited
        visited.append(check["id"])
        real = "yes" if (row["merged"] if check["id"] == "00-merged"
                         else row["touched_tests"]) else "no"
        remaining = [i for i in remaining if check["observations"][i] == real]
        node = node["branches"][real]
    decisions = {case["hypotheses"][i]["decision"] for i in remaining}
    assert len(decisions) == 1, "Policy stopped with ambiguous decision"
    return decisions.pop(), len(visited)


class LiveSourcePRGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
        cls.case = finite_case()
        cls.policy = optimize_policy(cls.case, max_depth=2, max_cost_milli=10)

    def test_policy_is_conditional_and_budgeted(self):
        policy = self.policy["policy"]
        self.assertEqual(policy["check_id"], "00-merged")
        self.assertEqual(policy["branches"]["no"]["action"], "answer")
        self.assertEqual(policy["branches"]["yes"]["check_id"], "01-tests")
        self.assertEqual(self.policy["expected_total_loss"], "3/400")
        self.assertEqual(self.policy["max_cost_milli"], 10)

    def test_frozen_real_source_outcomes_and_equal_call_ceiling(self):
        rows = self.snapshot["cases"]
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({(r["repo"], r["number"]) for r in rows}), 12)
        observed = []
        for row in rows:
            decision, calls = execute_policy(self.policy["policy"], row, self.case)
            self.assertEqual(decision == "accept", row["ground_truth"])
            self.assertEqual(decision == "accept", row["adaptive_prediction"])
            self.assertEqual(calls, row["adaptive_calls"])
            self.assertLessEqual(calls, row["fixed_calls"])
            self.assertTrue(row["independent_metadata_read_agreed"])
            observed.append((row, decision, calls))
        summary = self.snapshot["summary"]
        self.assertEqual(summary["merged"], sum(r["merged"] for r in rows))
        self.assertEqual(summary["truth_positive"], sum(r["ground_truth"] for r in rows))
        self.assertEqual(summary["direct_correct"],
                         sum(not r["ground_truth"] for r in rows))
        self.assertEqual(summary["fixed_correct"],
                         sum(r["fixed_prediction"] == r["ground_truth"] for r in rows))
        self.assertEqual(summary["adaptive_correct"],
                         sum(d == ("accept" if r["ground_truth"] else "reject")
                             for r,d,_ in observed))
        self.assertEqual(summary["adaptive_calls"], sum(c for _,_,c in observed))
        self.assertEqual(summary["fixed_calls"], 2*len(rows))
        self.assertEqual((summary["merged"], summary["truth_positive"]), (5,1))
        self.assertEqual((summary["direct_correct"], summary["fixed_correct"],
                          summary["adaptive_correct"]), (11,12,12))
        self.assertEqual((summary["fixed_calls"], summary["adaptive_calls"]), (24,17))

    def test_negative_case_without_merge_must_not_request_files(self):
        for row in self.snapshot["cases"]:
            decision, calls = execute_policy(self.policy["policy"], row, self.case)
            if not row["merged"]:
                self.assertEqual((decision, calls), ("reject", 1))


if __name__ == "__main__":
    unittest.main()
