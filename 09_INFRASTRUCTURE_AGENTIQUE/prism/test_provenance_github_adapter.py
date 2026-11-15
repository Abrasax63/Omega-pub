import unittest
from provenance_github_adapter import inspect


class GitHubAdapterTests(unittest.TestCase):
    def setUp(self):
        self.run = {"id": 43719507182, "head_sha": "1ec26219d5f2df91175d4783535cb2b1580d3f8a",
                    "html_url": "https://github.com/Abrasax63/Omega-pub/actions/runs/43719507182",
                    "status": "completed", "conclusion": "success"}
        self.jobs = {"jobs": [
            {"id": 132828209569, "run_id": 43719507182, "status": "completed", "conclusion": "success"},
            {"id": 132828209806, "run_id": 43719507182, "status": "completed", "conclusion": "success"},
        ]}

    def test_distinct_jobs_same_run_are_not_independent(self):
        self.assertEqual(inspect(self.run, self.jobs)["verdict"], "same_execution")

    def test_mismatched_job_run_abstains(self):
        self.jobs["jobs"][1]["run_id"] = 999
        self.assertEqual(inspect(self.run, self.jobs)["reason"], "job_run_mismatch")

    def test_failed_job_does_not_attest_execution(self):
        self.jobs["jobs"][0]["conclusion"] = "failure"
        self.assertEqual(inspect(self.run, self.jobs)["reason"], "execution_not_verified")

    def test_no_jobs_abstains(self):
        self.assertEqual(inspect(self.run, {"jobs": []})["reason"], "missing_evidence")


if __name__ == "__main__":
    unittest.main()
