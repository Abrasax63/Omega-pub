import unittest

from analysis import ARMS, AnalysisInputError, analyze_dataset
from evaluation import DIMENSIONS


def rating(case, output, evaluator, score):
    return {
        "case_id": case, "blind_output_id": output, "evaluator_id": evaluator,
        "scores": {dimension: score for dimension in DIMENSIONS},
        "unsupported_claims": 0, "material_errors": 0,
        "missed_counterexamples": 0, "elapsed_seconds": 10.0,
        "tool_calls": 1, "cost_usd": None,
    }


def fixture():
    ratings, key = [], []
    for case, scores in (
        ("case-01", {"A": 2, "B": 3, "C": 4}),
        ("case-02", {"A": 3, "B": 3, "C": 2}),
    ):
        for arm in ARMS:
            output = case + "-" + arm + "-opaque"
            key.append({"case_id": case, "blind_output_id": output, "arm": arm})
            for evaluator in ("rater-1", "rater-2"):
                ratings.append(rating(case, output, evaluator, scores[arm]))
    return ratings, key


class P5AnalysisTests(unittest.TestCase):
    def test_case_paired_deltas_without_composite(self):
        ratings, key = fixture()
        result = analyze_dataset(ratings, key, expected_case_ids={"case-01", "case-02"})
        self.assertEqual(result["status"], "descriptive_exploratory_only")
        self.assertEqual(len(result["case_results"]), 6)
        row = next(x for x in result["paired_comparisons"]
                   if x["candidate"] == "C" and x["reference"] == "A"
                   and x["dimension"] == "accuracy")
        self.assertEqual(row["paired_case_count"], 2)
        self.assertEqual(row["mean_case_delta"], 0.5)
        self.assertEqual((row["positive_cases"], row["negative_cases"]), (1, 1))
        self.assertNotIn("composite_score", result)

    def test_rejects_missing_blind_key_entry(self):
        ratings, key = fixture()
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(ratings, key[:-1])

    def test_rejects_duplicate_mapping(self):
        ratings, key = fixture()
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(ratings, key + [key[0]])

    def test_rejects_invalid_arm(self):
        ratings, key = fixture()
        key[0] = {**key[0], "arm": "D"}
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(ratings, key)

    def test_rejects_two_outputs_mapped_to_same_arm(self):
        ratings, key = fixture()
        key[1] = {**key[1], "arm": key[0]["arm"]}
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(ratings, key)

    def test_rejects_incomplete_rating_dataset(self):
        ratings, key = fixture()
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(ratings[:-1], key)


if __name__ == "__main__":
    unittest.main()
