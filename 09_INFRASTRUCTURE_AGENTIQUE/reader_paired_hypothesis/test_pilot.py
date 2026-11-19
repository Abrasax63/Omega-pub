import json
import unittest

from judge import baseline, completion, grade_selection
from pilot import CASES, HERE, messages_for, source_path, view


class PairedHypothesisTest(unittest.TestCase):
    def setUp(self):
        self.ref = json.loads((HERE / "reference.json").read_text())["cases"]

    def test_pair_has_one_prose_difference_and_all_target_lines_are_visible(self):
        a, b = [source_path(case).read_text().splitlines() for case in CASES]
        self.assertEqual(len(a), len(b))
        self.assertEqual([i for i, (x, y) in enumerate(zip(a, b), 1) if x != y], [19])
        for case in CASES:
            visible = {line for line, _ in json.loads(messages_for(view(case))[1]["content"])}
            self.assertTrue({3, 9, 14, 19, 21} <= visible)
            self.assertEqual(self.ref[case]["git_blob"], CASES[case])

    def test_oracle_agrees_with_the_reference_for_both_laws(self):
        verdicts = []
        for case in CASES:
            expected = self.ref[case]
            graded = grade_selection(case, view(case), expected["lines"], expected)
            self.assertTrue(graded["success"])
            self.assertEqual(graded["claim"]["verdict"], "INDETERMINATE")
            self.assertFalse(graded["claim"]["promotable"])
            verdicts.append(graded["oracle"])
        self.assertEqual([v["maps_examined"] for v in verdicts], [32, 32])
        self.assertEqual([v["maps_satisfying_hypothesis"] for v in verdicts], [7, 14])
        self.assertEqual([v["violations"] for v in verdicts], [0, 11])
        self.assertEqual(verdicts[1]["first_counterexample"],
                         {"size": 2, "map": [0, 0], "collision": [0, 1]})

    def test_exact_but_wrong_context_fails(self):
        case = "fiche-a"
        visible = view(case)
        selection = baseline(visible)
        self.assertEqual(selection, [3, 9, 21])
        graded = grade_selection(case, visible, selection, self.ref[case])
        self.assertEqual(graded["status"], "EVALUATED")
        self.assertEqual(graded["oracle"]["verdict"], "REFUTED")
        self.assertFalse(graded["success"])
        self.assertFalse(grade_selection(case, visible, [3, 99, 21], self.ref[case])["success"])

    def test_response_format_and_infrastructure_are_distinct(self):
        def response(text):
            return {"http_status": 200, "raw_response": json.dumps({
                "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
                "usage": {"completion_tokens": 3},
            })}

        self.assertEqual(completion(response("3, 14, 21"))["selection"], [3, 14, 21])
        self.assertEqual(completion(response("NONE"))["format"], "ABSTAINED")
        self.assertEqual(completion(response("Les numéros sont 3, 14, 21"))["format"], "INVALID")
        self.assertEqual(completion({"transport_error": "timeout"})["status"], "INFRA_FAILURE")
