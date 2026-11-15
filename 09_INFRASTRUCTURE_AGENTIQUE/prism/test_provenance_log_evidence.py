import unittest
from provenance_log_evidence import extract


class LogEvidenceTests(unittest.TestCase):
    def test_realistic_job_log_extracts_checkout_and_tests(self):
        log = (
            "2026-11-15T13:32:20.1731354Z HEAD is now at cf7fa4c Merge test\n"
            "2026-11-15T13:32:19.2056147Z Ran 71 tests in 0.025s\n"
            "2026-11-15T13:32:19.2056575Z OK\n"
        )
        result = extract(log, run_id=43719507182, job_id=132828209569,
                         expected_sha="cf7fa4c07bf2bd17de7fe86fcd7a76a42cc1ee3f")
        self.assertTrue(result["checkout_matches_expected"])
        self.assertEqual([o["kind"] for o in result["observations"]],
                         ["checkout", "test_count", "test_ok"])
        self.assertEqual(result["verdict"], "indéterminé")
        self.assertEqual(result["observations"][1]["line"], 2)

    def test_echoed_command_not_treated_as_execution(self):
        log = "2026-11-15T13:32:20Z Run echo 'cp input output'\n"
        self.assertEqual(extract(log, run_id=1, job_id=2)["observations"], [])

    def test_mismatched_checkout_not_accepted(self):
        log = "HEAD is now at abcdef0 Merge\n"
        self.assertFalse(extract(log, run_id=1, job_id=2,
                                 expected_sha="12345678901234567890")["checkout_matches_expected"])

    def test_no_checkout_is_not_verified(self):
        self.assertIsNone(extract("OK\n", run_id=1, job_id=2,
                                  expected_sha="123456789")["checkout_matches_expected"])

    def test_verdict_is_observation_not_certificate(self):
        log = "2026-11-15T13:32:22.8108064Z {'Candidate alpha': 'recalcul', 'Candidate beta': 'copie'}\n"
        result = extract(log, run_id=1, job_id=2)
        self.assertEqual(result["observations"][0]["kind"], "candidate_verdict")
        self.assertEqual(result["verdict"], "indéterminé")


if __name__ == "__main__":
    unittest.main()
