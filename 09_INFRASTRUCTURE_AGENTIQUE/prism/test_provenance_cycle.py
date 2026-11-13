import unittest

from provenance_cycle import evaluate_proposal, propose
from test_provenance_lab import UNKNOWN, case


class CycleTests(unittest.TestCase):
    def test_prioritizes_false_confirmation_and_narrows_module(self):
        baseline = {("python", "-m"): "recalcul"}
        training = [
            case("cp src result.json", "copie"),
            case("python -m square 11", "recalcul"),
            case("python -m republish src", "copie"),
        ]
        proposal = propose(training, baseline)
        self.assertEqual(proposal["target"], ("python", "-m"))
        reserved = [
            case("python -m square 23", "recalcul"),
            case("python -m republish archived", "copie"),
            case("python -m missing x", UNKNOWN),
        ]
        self.assertTrue(evaluate_proposal(proposal, baseline, reserved)["recommend_for_review"])

    def test_rejects_narrow_rule_that_still_generalizes_incorrectly(self):
        baseline = {("python", "-m"): "recalcul"}
        proposal = propose([case("python -m calc a", "copie")], baseline)
        result = evaluate_proposal(proposal, baseline, [case("python -m calc b", "recalcul")])
        self.assertFalse(result["recommend_for_review"])

    def test_rejects_reused_observation_even_when_relabelled(self):
        training = [case("cp src result.json", "copie")]
        with self.assertRaisesRegex(ValueError, "both training and reserved"):
            evaluate_proposal(propose(training, {}), {}, [dict(training[0], expected=UNKNOWN)])

    def test_stops_when_no_writer_supports_a_candidate(self):
        training = [case("cp src result.json", "copie", complete=False)]
        proposal = propose(training, {})
        self.assertIsNone(proposal["target"])
        result = evaluate_proposal(proposal, {}, [case("cp other result.json", UNKNOWN, complete=False)])
        self.assertFalse(result["recommend_for_review"])

    def test_no_regression_when_abstention_would_erase_correct_verdict(self):
        baseline = {("cp",): "copie"}
        proposal = propose([case("cp invalid result.json", UNKNOWN)], baseline)
        reserved = [case("cp actual result.json", "copie"), case("cp other result.json", UNKNOWN)]
        self.assertFalse(evaluate_proposal(proposal, baseline, reserved)["recommend_for_review"])
