"""Tests for wiring, never pretend these constitute a real model run."""
import copy
import unittest
from unittest.mock import patch

from integrated_cycle import ROOT, integrated_cycle, template_trial, model_trial, known_prior_sources
from event_store import verify_events, EventLedgerError


class IntegratedCycleTests(unittest.TestCase):
    def test_plan_runs_read_only_and_does_not_claim_agents(self):
        report = integrated_cycle("plan", root=ROOT)
        self.assertIsNone(report["experiment"])
        self.assertTrue(report["provenance_validation"]["valid"])
        self.assertEqual(report["p3"]["coverage"]["completed"], 0)
        self.assertGreater(report["context"]["package_count"], 0)
        self.assertFalse(report["promotion_to_core"])
        self.assertFalse(report["main_modified"])

    def test_one_actual_computational_perspective_is_recorded(self):
        stub = {
            "status": "SYNTHETIC_UNIT_TEST_ONLY",
            "decision": "REJECTED",
            "gain_of_autonomous_intelligence_demonstrated": False,
        }
        with patch("integrated_cycle.template_trial", return_value=stub):
            report = integrated_cycle("templates", root=ROOT, inputs={"synthetic": True})
        self.assertEqual(report["p3"]["coverage"]["completed"], 1)
        self.assertEqual(report["p3"]["coverage"]["not_executed"],
                         report["context"]["package_count"] - 1)
        self.assertEqual(report["experiment"]["status"], "SYNTHETIC_UNIT_TEST_ONLY")
        self.assertTrue(report["provenance_validation"]["valid"])

    def test_forged_provenance_event_is_rejected(self):
        report = integrated_cycle("plan", root=ROOT)
        events = copy.deepcopy(report["events"])
        events[0]["mission_id"] = "tampered"
        with self.assertRaises(EventLedgerError):
            verify_events(events)

    def test_unknown_mode_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown mode"):
            integrated_cycle("pretend")

    def test_real_model_requires_model_and_cli(self):
        with self.assertRaisesRegex(ValueError, "requires both"):
            integrated_cycle("model")

    def test_cross_run_reuse_is_rejected_even_if_fast(self):
        known_sha = known_prior_sources()[0]["source_sha256"]
        fake = {
            "status": "MODEL_CANDIDATE_EVALUATED",
            "attempts": [{"model_call_returncode": 0}],
            "winner_sha256": known_sha,
            "strong_baseline_passed": True,
            "candidate_equals_classical_source": False,
        }
        with patch("integrated_cycle.run_open_model", return_value=fake):
            verdict = model_trial("FAKE_TEST_ONLY", "FAKE_TEST_ONLY", "unit-test")
        self.assertEqual(verdict["decision"], "REJECTED")
        self.assertTrue(verdict["known_historical_duplicate"])
        self.assertIn("KNOWN_HISTORICAL_SOURCE_REUSED", verdict["rejection_reasons"])
        self.assertFalse(verdict["promotion_to_core"])

    def test_unknown_source_does_not_certify_novelty(self):
        fake = {
            "status": "MODEL_CANDIDATE_EVALUATED",
            "attempts": [{"model_call_returncode": 0}],
            "winner_sha256": "f" * 64,
            "strong_baseline_passed": True,
            "candidate_equals_classical_source": False,
        }
        with patch("integrated_cycle.run_open_model", return_value=fake):
            verdict = model_trial("FAKE_TEST_ONLY", "FAKE_TEST_ONLY", "unit-test")
        self.assertEqual(verdict["decision"], "REVIEW_REQUIRED")
        self.assertEqual(verdict["source_novelty"], "UNVERIFIED_GLOBAL_NOVELTY")
        self.assertFalse(verdict["gain_of_autonomous_intelligence_demonstrated"])

    def test_training_holdout_overlap_is_fatal(self):
        bad = {"seed_development": [1101], "seed_reserved": [1101]}
        with self.assertRaisesRegex(ValueError, "overlap"):
            template_trial(bad)


if __name__ == "__main__":
    unittest.main()
