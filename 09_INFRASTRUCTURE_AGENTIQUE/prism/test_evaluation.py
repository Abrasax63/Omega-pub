import unittest

from evaluation import (
    DIMENSIONS, EvaluationRecordError, validate_dataset, validate_record,
)


def valid_record(case="case-01", output="opaque-01", evaluator="reviewer-1"):
    return {
        "case_id": case,
        "blind_output_id": output,
        "evaluator_id": evaluator,
        "scores": {dimension: 3 for dimension in DIMENSIONS},
        "unsupported_claims": 0,
        "material_errors": 0,
        "missed_counterexamples": 1,
        "elapsed_seconds": 12.5,
        "tool_calls": 2,
        "cost_usd": None,
    }


class EvaluationValidationTests(unittest.TestCase):
    def test_accepts_valid_blinded_record(self):
        validate_record(valid_record())

    def test_rejects_missing_dimension_and_out_of_range_score(self):
        record = valid_record()
        del record["scores"]["accuracy"]
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)
        record = valid_record()
        record["scores"]["accuracy"] = 5
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)

    def test_rejects_boolean_as_numeric_score_or_count(self):
        record = valid_record()
        record["scores"]["accuracy"] = True
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)
        record = valid_record()
        record["tool_calls"] = True
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)

    def test_rejects_duplicate_evaluator_rating(self):
        with self.assertRaises(EvaluationRecordError):
            validate_dataset([valid_record(), valid_record()])

    def test_accepts_multiple_blind_outputs_and_reviewers(self):
        records = [
            valid_record(output="opaque-A", evaluator="reviewer-1"),
            valid_record(output="opaque-A", evaluator="reviewer-2"),
            valid_record(output="opaque-B", evaluator="reviewer-1"),
            valid_record(output="opaque-B", evaluator="reviewer-2"),
        ]
        result = validate_dataset(records)
        self.assertTrue(result["valid"])
        self.assertEqual(result["case_count"], 1)
        self.assertEqual(result["blind_outputs_per_case"]["case-01"], 2)
        self.assertEqual(result["scoring"], "human_ratings_only_no_automatic_truth_judgment")

    def test_adjudication_cannot_be_mixed_into_initial_blind_rating(self):
        record = valid_record()
        record["adjudication"] = "A is correct"
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)


if __name__ == "__main__":
    unittest.main()
