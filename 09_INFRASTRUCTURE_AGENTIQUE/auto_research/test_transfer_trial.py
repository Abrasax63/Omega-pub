"""Non-LLM tests for preregistered transfer evaluation contract."""
import copy
from hashlib import sha256
from pathlib import Path
import unittest

from reference import observed_relation, walks_exact
from transfer_trial import (ARMS, CANDIDATE_SHA256, FAMILIES, HORIZONS,
                            REPEATS, SIZES, fingerprint, make_cases, make_graph,
                            validate_and_report)


def fake_payload(cases, candidate_wrong=False, candidate_slow=True):
    from reference import walks_exact
    fake = {
        "source_sha256": CANDIDATE_SHA256,
        "input_sha256": fingerprint([{k: v for k, v in row.items() if k != "projection"}
                                     for row in cases]),
        "source_baselines": {x: "fake-audit-hash-" + x for x in ARMS[1:]},
        "results": [],
    }
    for case in cases:
        actual = walks_exact(case["rows"], case["steps"])
        candidate = actual[:]
        if candidate_wrong and case["case_id"] == cases[0]["case_id"]:
            candidate[0] ^= 1
        vals = {x: actual[:] for x in ARMS}
        vals["qwen3b_frozen"] = candidate
        durations = {arm: [2000 if arm == "qwen3b_frozen" and candidate_slow else 1000]
                     * REPEATS for arm in ARMS}
        fake["results"].append({"case_id": case["case_id"], "values": vals,
                                "samples_ns": durations})
    return fake


class TransferPreregTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = make_cases()

    def test_prereg_case_counts_and_family_coverage(self):
        self.assertEqual(len(self.cases), 80)
        self.assertEqual(sum(c["timed"] for c in self.cases), 64)
        self.assertEqual(set(c["family"] for c in self.cases), set(FAMILIES))
        self.assertEqual(set(c["steps"] for c in self.cases), set(HORIZONS))
        self.assertEqual(set(c["n"] for c in self.cases), set(SIZES))
        self.assertEqual(len({c["case_id"] for c in self.cases}), 80)

    def test_all_input_cases_are_deterministic(self):
        self.assertEqual(self.cases, make_cases())

    def test_projection_matches_direct_observability(self):
        for c in self.cases:
            if c["family"] != "projection":
                continue
            p = c["projection"]
            self.assertEqual(c["rows"], observed_relation(
                p["transition"], p["colors"], p["color_count"]))

    def test_frozen_original_source_hash(self):
        file = Path(__file__).resolve().parent / "frozen_qwen3b_candidate.py"
        self.assertEqual(sha256(file.read_bytes()).hexdigest(), CANDIDATE_SHA256)

    def test_synthetic_negative_comparison_is_not_promotion(self):
        r = validate_and_report(self.cases, fake_payload(self.cases),
                                CANDIDATE_SHA256, "test-image")
        self.assertEqual(r["scientific_verdict"], "NO_DEMONSTRATED_ADVANTAGE")
        self.assertEqual(r["n_timed_cases"], 64)
        self.assertFalse(r["correctness_failures"])
        self.assertFalse(r["delta_failures"])
        self.assertTrue(all(not g["candidate_for_independent_review"]
                            for g in r["strong_classical_gates"].values()))

    def test_synthetic_wrong_answer_cannot_pass(self):
        r = validate_and_report(self.cases,
                                fake_payload(self.cases, candidate_wrong=True),
                                CANDIDATE_SHA256, "test-image")
        self.assertEqual(r["scientific_verdict"], "NO_DEMONSTRATED_ADVANTAGE")
        self.assertTrue(r["correctness_failures"])

    def test_unknown_case_is_rejected(self):
        data = fake_payload(self.cases)
        data["results"][0]["case_id"] = "unregistered"
        with self.assertRaisesRegex(ValueError, "case ID"):
            validate_and_report(self.cases, data, CANDIDATE_SHA256, "test-image")

    def test_missing_arm_rejected(self):
        data = fake_payload(self.cases)
        del data["results"][0]["values"]["square-scan"]
        with self.assertRaisesRegex(ValueError, "arm or sample"):
            validate_and_report(self.cases, data, CANDIDATE_SHA256, "test-image")

    def test_nonpositive_timing_rejected(self):
        data = fake_payload(self.cases)
        data["results"][1]["samples_ns"]["qwen3b_frozen"][0] = 0
        with self.assertRaisesRegex(ValueError, "timing"):
            validate_and_report(self.cases, data, CANDIDATE_SHA256, "test-image")

    def test_changed_input_hash_rejected(self):
        data = fake_payload(self.cases)
        data["input_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "input hash"):
            validate_and_report(self.cases, data, CANDIDATE_SHA256, "test-image")


if __name__ == "__main__":
    unittest.main()
