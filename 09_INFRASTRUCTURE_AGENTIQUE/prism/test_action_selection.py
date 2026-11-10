import copy
import unittest
from collections import Counter

from action_selection import EvidenceModelError, plan_with_evidence, select_action
from action_selection_benchmark import evaluate, make_cases, _reference_choice


class NextActionValueTests(unittest.TestCase):
    def test_all_24_public_cases_and_separate_reference(self):
        report = evaluate()
        self.assertEqual(report["cases"], 24)
        self.assertEqual(report["optimizer_matches_reference"], 24)
        self.assertEqual(report["first_positive_matches_reference"], 20)
        self.assertEqual(Counter(row["selected"] for row in report["detail"]), {
            "answer": 4, "verify": 4, "ask": 12,
            "insufficient_evidence": 4,
        })
        print("SYNTHETIC NEXT ACTION: 24/24 exact-reference matches; "
              "first-positive control 20/24; zero model calls.")

    def test_p1_records_no_execution_or_scientific_validation(self):
        for case in make_cases():
            result = plan_with_evidence(case)
            execution = result["plan"]["execution_model"]
            self.assertEqual(execution["model_calls_performed"], 0)
            self.assertFalse(execution["scientific_validation_performed"])
            self.assertEqual(execution["status"], "planning_only")
            self.assertEqual(result["plan"]["mission"]["mission_id"], case["case_id"])

    def test_counterfactual_availability_changes_the_decision(self):
        original = next(c for c in make_cases() if c["case_id"] == "mathematical-02")
        altered = copy.deepcopy(original)
        altered["checks"][0]["available"] = False
        self.assertEqual(select_action(original)["action"], "verify")
        self.assertEqual(select_action(altered)["action"], "ask")

    def test_counterfactual_absent_clarification_forces_abstention(self):
        case = next(c for c in make_cases() if c["case_id"] == "documentary-03")
        self.assertEqual(select_action(case)["action"], "ask")
        case["checks"][1]["available"] = False
        self.assertEqual(select_action(case)["action"], "insufficient_evidence")

    def test_counterfactual_shared_decision_changes_to_answer(self):
        case = next(c for c in make_cases() if c["case_id"] == "computational-04")
        self.assertEqual(select_action(case)["action"], "insufficient_evidence")
        for h in case["hypotheses"]:
            h["decision"] = "valide"
        self.assertEqual(select_action(case)["action"], "answer")

    def test_hypothesis_and_check_order_do_not_change_choice(self):
        for case in make_cases():
            expected = select_action(case)
            reordered = copy.deepcopy(case)
            reordered["hypotheses"].reverse()
            for check in reordered["checks"]:
                check["observations"].reverse()
            reordered["checks"].reverse()
            self.assertEqual(select_action(reordered), expected)

    def test_uninformative_zero_cost_is_not_chosen(self):
        case = next(c for c in make_cases() if c["case_id"] == "exploratory-04")
        case["checks"][0]["cost_milli"] = 0
        self.assertEqual(select_action(case)["action"], "insufficient_evidence")

    def test_cost_tradeoff_prefers_partial_cheap_clarification(self):
        case = next(c for c in make_cases() if c["case_id"] == "mathematical-06")
        result = select_action(case)
        self.assertEqual((result["action"], result["chosen_check"]),
                         ("ask", "02-clarification"))
        self.assertEqual(result["net_gain"], "6/25")
        self.assertEqual(_reference_choice(case, "first_positive"),
                         ("verify", "01-verification"))

    def test_reject_malformed_models(self):
        base = make_cases()[1]
        cases = []
        missing = copy.deepcopy(base); del missing["hypotheses"]
        cases.append(missing)
        wrong = copy.deepcopy(base); wrong["hypotheses"][0]["weight"] = True
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["hypotheses"][1]["id"] = "h0"
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][0]["cost_milli"] = True
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][0]["cost_milli"] = -1
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][0]["available"] = "yes"
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][0]["action"] = "execute"
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][0]["observations"].pop()
        cases.append(wrong)
        wrong = copy.deepcopy(base); wrong["checks"][1]["id"] = "01-verification"
        cases.append(wrong)
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(EvidenceModelError):
                    select_action(case)


    def test_cost_change_reverses_preferred_action(self):
        case = next(c for c in make_cases() if c["case_id"] == "mathematical-06")
        self.assertEqual(select_action(case)["action"], "ask")
        case["checks"][1]["cost_milli"] = 100
        self.assertEqual(select_action(case)["action"], "verify")

    def test_two_stage_information_can_defeat_one_step_greedy(self):
        # Both measurements alone keep one A and one B in each outcome
        # class. Jointly, their outcome pairs identify all hypotheses.
        case = copy.deepcopy(make_cases()[1])
        for i, h in enumerate(case["hypotheses"]):
            h["decision"] = "A" if i < 2 else "B"
        case["checks"][0]["observations"] = ["x", "y", "x", "y"]
        case["checks"][0]["cost_milli"] = 1
        case["checks"][1]["observations"] = ["x", "y", "y", "x"]
        case["checks"][1]["cost_milli"] = 1
        self.assertEqual(select_action(case)["action"], "insufficient_evidence")
        pairs = list(zip(case["checks"][0]["observations"],
                         case["checks"][1]["observations"]))
        self.assertEqual(len(set(pairs)), len(case["hypotheses"]))
        self.assertEqual(_reference_choice(case, "best"),
                         ("insufficient_evidence", None))
        # One-step abstention here is a documented limitation, not success
        # of a multi-step optimizer: the two inexpensive tests together
        # would identify the right decision.


if __name__ == "__main__":
    unittest.main()
