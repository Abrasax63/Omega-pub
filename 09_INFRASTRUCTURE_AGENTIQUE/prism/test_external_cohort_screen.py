"""Tests for the frozen external-log screening adapter; all examples synthetic."""
import unittest

from external_cohort_screen import screening, screen_cohort


H = "a" * 64


class ExternalCohortScreenTests(unittest.TestCase):
    def test_no_usable_evidence(self):
        result = screening("Run compile\nTests passed\n")
        self.assertFalse(result["potentially_eligible"])
        self.assertEqual(result["xtrace_candidates"], 0)
        self.assertEqual(result["sha256_line_candidates"], 0)

    def test_digest_alone_not_enough(self):
        result = screening(H + "  output.json\n")
        self.assertEqual(result["sha256_line_candidates"], 1)
        self.assertFalse(result["potentially_eligible"])

    def test_writer_alone_not_enough(self):
        result = screening("+ cp input output\n")
        self.assertEqual(result["xtrace_candidates"], 1)
        self.assertFalse(result["potentially_eligible"])

    def test_two_independent_signals_only_admit_for_review(self):
        result = screening("+ cp input output\n" + H + "  output\n")
        self.assertTrue(result["potentially_eligible"])
        self.assertEqual(result["interpretation"], "SCREEN_ONLY_NOT_AN_ATTESTATION")

    def test_prefixed_github_log(self):
        log = ("2026-11-13T19:09:30.0000000Z + cp a b\n"
               + "2026-11-13T19:09:30.0000000Z " + H + "  b\n")
        result = screening(log)
        self.assertEqual((result["xtrace_candidates"],result["sha256_line_candidates"]),(1,1))

    def test_missing_log_is_not_positive(self):
        calls = []
        cohort = [{"repo":"example/open", "run_id":8,"job_ids":[11,12]}]
        def reader(repo, job):
            calls.append(job)
            if job == 11:
                return H + "  target\n"
            raise OSError("unavailable")
        result = screen_cohort(cohort,reader)
        self.assertEqual(calls,[11,12])
        self.assertEqual(result["candidate_evidence_jobs"],0)
        self.assertEqual(result["benchmark_status"], "INSUFFICIENT_INDEPENDENT_REFERENCE")
        self.assertEqual(result["rows"][1]["status"],"log_unavailable")

    def test_empty_jobs_does_not_create_observations(self):
        result = screen_cohort([{"repo":"example/open","run_id":1,"job_ids":[]}],
                               lambda *_: self.fail("must not read"))
        self.assertEqual(result["jobs_requested"],0)

    def test_invalid_or_malformed_inputs(self):
        with self.assertRaises(TypeError):
            screening(None)
        with self.assertRaises(ValueError):
            screen_cohort({},lambda *_:"")
        with self.assertRaises(ValueError):
            screen_cohort([{"repo":"x","run_id":1,"job_ids":["oops"]}],lambda *_:"")


if __name__ == "__main__":
    unittest.main()
