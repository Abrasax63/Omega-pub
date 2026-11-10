import json
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analysis import ARMS, AnalysisInputError, analyze_dataset, analyze_files
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
        for index, arm in enumerate(ARMS):
            output = case + "-opaque-" + str(index)
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

    def test_synthetic_frozen_file_round_trip_and_order_invariance(self):
        ratings, key = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notes = root / "synthetic.jsonl"
            key_path = root / "key.json"
            output = root / "report.json"
            key_path.write_text(json.dumps({"mappings": key}), encoding="utf-8")
            notes.write_text("".join(json.dumps(row) + "\n" for row in ratings), encoding="utf-8")
            digest = sha256(notes.read_bytes()).hexdigest()
            args = {"expected_case_ids": {"case-01", "case-02"}, "ratings_sha256": digest}
            result = analyze_files(notes, key_path, output, **args)
            self.assertEqual(result, json.loads(output.read_text(encoding="utf-8")))
            self.assertEqual(result, analyze_files(notes, key_path, output, **args))
            self.assertEqual(analyze_dataset(ratings, key), analyze_dataset(ratings[::-1], key[::-1]))
            deltas = {(r["candidate"], r["reference"]): r["mean_case_delta"]
                      for r in result["paired_comparisons"] if r["dimension"] == "accuracy"}
            self.assertEqual(deltas, {("C", "A"): 0.5, ("C", "B"): 0.0, ("B", "A"): 0.5})
            notes.write_bytes(notes.read_bytes().replace(b'"accuracy": 2', b'"accuracy": 1', 1))
            with patch("analysis.load_blind_key") as load_key:
                with self.assertRaisesRegex(AnalysisInputError, "SHA-256"):
                    analyze_files(notes, key_path, output, **args)
                load_key.assert_not_called()

    def test_rejects_contaminated_or_ambiguous_rating_before_key_access(self):
        ratings, _ = fixture()
        first = json.dumps(ratings[0])
        for line in (first[:-1] + ', "arm": "A"}',
                     first[:-1] + ', "case_id": "case-01"}',
                     first.replace('"rater-1"', '" rater-1"')):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                notes = root / "synthetic.jsonl"
                notes.write_text(line + "\n" + "".join(json.dumps(row) + "\n" for row in ratings[1:]),
                                 encoding="utf-8")
                with patch("analysis.load_blind_key") as load_key:
                    with self.assertRaises(AnalysisInputError):
                        analyze_files(notes, root / "key.json", root / "report.json",
                                      expected_case_ids={"case-01", "case-02"},
                                      ratings_sha256=sha256(notes.read_bytes()).hexdigest())
                    load_key.assert_not_called()

    def test_repeated_blocks_require_unique_arm_repetition_pairs(self):
        ratings, key = fixture()
        repeated_ratings = ratings + [{**row, "blind_output_id": row["blind_output_id"] + "-extra"}
                                      for row in ratings]
        repeated_key = [{**row, "repetition": 1} for row in key] + [
            {**row, "blind_output_id": row["blind_output_id"] + "-extra", "repetition": 2}
            for row in key
        ]
        result = analyze_dataset(repeated_ratings, repeated_key, repetitions=2)
        self.assertEqual(result["paired_comparisons"], analyze_dataset(ratings, key)["paired_comparisons"])
        repeated_key[-1]["repetition"] = 1
        with self.assertRaises(AnalysisInputError):
            analyze_dataset(repeated_ratings, repeated_key, repetitions=2)

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

    def test_file_pipeline_validates_ratings_before_opening_blind_key(self):
        ratings, _ = fixture()
        with tempfile.TemporaryDirectory() as directory:
            ratings_path = Path(directory) / "ratings.jsonl"
            ratings_path.write_text(
                "".join(json.dumps(row) + "\n" for row in ratings[:-1]),
                encoding="utf-8",
            )
            with patch("analysis.load_blind_key") as load_key:
                with self.assertRaises(AnalysisInputError):
                    analyze_files(
                        ratings_path,
                        Path(directory) / "blind_key.json",
                        Path(directory) / "analysis.json",
                        expected_case_ids={"case-01", "case-02"},
                        ratings_sha256=sha256(ratings_path.read_bytes()).hexdigest(),
                    )
                load_key.assert_not_called()


if __name__ == "__main__":
    unittest.main()
