import unittest
from provenance_log_holdout import evaluate


class HoldoutTests(unittest.TestCase):
    def test_two_jobs_one_run_are_not_two_runs(self):
        rows = [{"run_id": "43724979863", "job_id": "132844845630", "log": "Ran 80 tests in 0.025s\\nOK\\n"},
                {"run_id": "43724979863", "job_id": "132844845631", "log": "OK\\n"}]
        result = evaluate(rows)
        self.assertEqual(result["same_run_pairs"], 1)
        self.assertEqual(result["distinct_run_ids"], 1)
        self.assertEqual(result["independent_reproductions"], "indéterminé")

    def test_distinct_run_ids_do_not_prove_independence(self):
        rows = [{"run_id": "43724979863", "job_id": "1", "log": "OK\\n"},
                {"run_id": "43724963194", "job_id": "2", "log": "OK\\n"}]
        result = evaluate(rows)
        self.assertEqual(result["distinct_run_ids"], 2)
        self.assertEqual(result["independent_reproductions"], "indéterminé")

    def test_log_hashes_preserved(self):
        result = evaluate([{"run_id": "1", "job_id": "2", "log": "OK\\n"}])
        self.assertEqual(len(result["log_sha256"][0]), 64)


if __name__ == "__main__":
    unittest.main()
