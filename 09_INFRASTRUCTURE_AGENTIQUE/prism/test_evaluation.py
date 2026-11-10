import math
import unittest

from evaluation import (
    DIMENSIONS, EvaluationRecordError, validate_dataset, validate_record,
)


def valid_record(case="case-01", output="opaque-A", evaluator="reviewer-1"):
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


def complete_dataset():
    return [
        valid_record(output=output, evaluator=evaluator)
        for output in ("opaque-A", "opaque-B", "opaque-C")
        for evaluator in ("reviewer-1", "reviewer-2")
    ]


class EvaluationValidationTests(unittest.TestCase):
    def test_accepts_valid_blinded_record(self):
        validate_record(valid_record())

    def test_rejects_non_object_record(self):
        for value in (None, [], "record", 7):
            with self.subTest(value=value), self.assertRaises(EvaluationRecordError):
                validate_record(value)

    def test_rejects_blank_identifiers(self):
        for field in ("case_id", "blind_output_id", "evaluator_id"):
            record = valid_record()
            record[field] = "  "
            with self.subTest(field=field), self.assertRaises(EvaluationRecordError):
                validate_record(record)

    def test_rejects_missing_dimension_and_out_of_range_score(self):
        record = valid_record()
        del record["scores"]["accuracy"]
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)
        record = valid_record()
        record["scores"]["accuracy"] = 5
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)

    def test_rejects_extra_score_dimension(self):
        record = valid_record()
        record["scores"]["extra"] = 3
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)

    def test_rejects_boolean_as_numeric_score_or_count(self):
        record = valid_record()
        record["scores"]["accuracy"] = True
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)
        for field in ("unsupported_claims", "material_errors", "missed_counterexamples", "tool_calls"):
            record = valid_record()
            record[field] = True
            with self.subTest(field=field), self.assertRaises(EvaluationRecordError):
                validate_record(record)

    def test_rejects_negative_and_non_integer_counts(self):
        for value in (-1, 1.5, "2"):
            record = valid_record()
            record["tool_calls"] = value
            with self.subTest(value=value), self.assertRaises(EvaluationRecordError):
                validate_record(record)

    def test_rejects_non_finite_elapsed_and_cost(self):
        for value in (math.nan, math.inf, -math.inf):
            record = valid_record()
            record["elapsed_seconds"] = value
            with self.assertRaises(EvaluationRecordError):
                validate_record(record)
            record = valid_record()
            record["cost_usd"] = value
            with self.assertRaises(EvaluationRecordError):
                validate_record(record)

    def test_rejects_negative_or_wrong_type_elapsed_and_cost(self):
        for field, value in (
            ("elapsed_seconds", -0.1),
            ("elapsed_seconds", "12"),
            ("elapsed_seconds", True),
            ("cost_usd", -0.1),
            ("cost_usd", "0.5"),
            ("cost_usd", True),
        ):
            record = valid_record()
            record[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(EvaluationRecordError):
                validate_record(record)

    def test_rejects_duplicate_evaluator_rating(self):
        records = complete_dataset()
        records.append(records[0].copy())
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(records)

    def test_accepts_complete_three_arm_blinded_dataset(self):
        result = validate_dataset(
            complete_dataset(),
            expected_case_ids={"case-01"},
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["blind_outputs_per_case"], {"case-01": 3})
        self.assertEqual(result["complete_evaluators_per_case"], {"case-01": 2})

    def test_accepts_permuted_complete_dataset(self):
        records = list(reversed(complete_dataset()))
        result = validate_dataset(records, expected_case_ids={"case-01"})
        self.assertTrue(result["valid"])

    def test_rejects_single_evaluator(self):
        records = [
            valid_record(output=output, evaluator="reviewer-1")
            for output in ("opaque-A", "opaque-B", "opaque-C")
        ]
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(records)

    def test_rejects_missing_third_arm(self):
        records = [
            valid_record(output=output, evaluator=evaluator)
            for output in ("opaque-A", "opaque-B")
            for evaluator in ("reviewer-1", "reviewer-2")
        ]
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(records)

    def test_rejects_unbalanced_reviewer_coverage(self):
        records = complete_dataset()
        records = [
            row for row in records
            if not (row["blind_output_id"] == "opaque-C" and row["evaluator_id"] == "reviewer-2")
        ]
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(records)

    def test_rejects_missing_expected_case(self):
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(complete_dataset(), expected_case_ids={"case-01", "case-02"})

    def test_rejects_unexpected_case(self):
        records = complete_dataset()
        records.extend([
            valid_record(case="case-extra", output=output, evaluator=evaluator)
            for output in ("opaque-A", "opaque-B", "opaque-C")
            for evaluator in ("reviewer-1", "reviewer-2")
        ])
        with self.assertRaises(EvaluationRecordError):
            validate_dataset(records, expected_case_ids={"case-01"})

    def test_rejects_empty_or_wrong_type_dataset(self):
        for records in ([], None, {}, "records"):
            with self.subTest(records=records), self.assertRaises(EvaluationRecordError):
                validate_dataset(records)

    def test_rejects_invalid_expected_case_ids(self):
        for expected in (["case-01"], {" "}, {1}):
            with self.subTest(expected=expected), self.assertRaises(EvaluationRecordError):
                validate_dataset(complete_dataset(), expected_case_ids=expected)

    def test_rejects_invalid_coverage_parameters(self):
        for kwargs in (
            {"expected_outputs_per_case": 0},
            {"expected_outputs_per_case": True},
            {"expected_outputs_per_case": 3.0},
            {"minimum_evaluators": 1},
            {"minimum_evaluators": True},
            {"minimum_evaluators": 2.5},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(EvaluationRecordError):
                validate_dataset(complete_dataset(), **kwargs)

    def test_adjudication_cannot_be_mixed_into_initial_blind_rating(self):
        record = valid_record()
        record["adjudication"] = "opaque-A is correct"
        with self.assertRaises(EvaluationRecordError):
            validate_record(record)


if __name__ == "__main__":
    unittest.main()
