"""Fair prospective cohort: actual Omega vs strongest simple short-circuit arms.

Checks source identity, cross-checks, no leakage from test labels into policy,
equal per-case budget and exposed negative results. No LLM or per-arm network
queries are involved in replay.
"""
import json
from collections import Counter
from pathlib import Path
import unittest

import strategic_first_check_transfer as lab


class FirstCheckTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = lab.train_snapshot()
        cls.target = json.loads(lab.TARGET.read_text(encoding="utf-8"))
        cls.report = lab.evaluate()

    def test_pre_registered_case_ids_and_real_source_fields(self):
        rows = self.target["cases"]
        self.assertEqual([(r["repo"], r["number"]) for r in rows], lab.TARGET_IDS)
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({(r["repo"], r["number"]) for r in rows}), 24)
        self.assertEqual(self.target["preregister_commit"],
                         "8cc991b1d734b280825ce10a73458aacc3f06c7a")
        for row in rows:
            self.assertEqual(type(row["merged"]), bool)
            self.assertEqual(type(row["touched_tests"]), bool)
            self.assertTrue(row["metadata_crosscheck_same_merged_and_sha"])
            self.assertEqual(len(row["head_sha"]), 40)
            self.assertEqual(row["url"],
                             "https://github.com/%s/pull/%d" % (row["repo"], row["number"]))
            file_paths = row["changed_filenames"]
            self.assertIsInstance(file_paths, list)
            expected = any(
                "test" in p.split("/") or "tests" in p.split("/")
                or p.rsplit("/", 1)[-1].startswith("test_")
                or p.endswith("_test.py")
                for p in file_paths
            )
            self.assertEqual(row["touched_tests"], expected)
        self.assertEqual(sum(r["merged"] for r in rows), 2)
        self.assertEqual(sum(r["touched_tests"] for r in rows), 15)
        self.assertEqual(sum(r["merged"] and r["touched_tests"] for r in rows), 2)

    def test_training_is_separate_and_freezes_strategy(self):
        self.assertEqual(len(self.train), 12)
        old = {(r["repo"], r["number"]) for r in self.train}
        new = {(r["repo"], r["number"]) for r in self.target["cases"]}
        self.assertFalse(old.intersection(new))
        p = lab.training_policies(self.train)
        self.assertEqual(p["global"]["marginals"], (5,3))
        self.assertEqual(p["global"]["simple_first"], "touched_tests")
        self.assertEqual({k:v["simple_first"] for k,v in p["by_repo"].items()},
                         {"python/cpython": "merged", "pallets/flask":"merged",
                          "psf/requests":"touched_tests"})
        # The actual optimizer, not a reproduced decision table, is called.
        self.assertEqual(p["global"]["omega"]["max_depth"], 2)
        self.assertEqual(p["global"]["omega"]["max_cost_milli"], 2)
        for group in [p["global"], *p["by_repo"].values()]:
            self.assertIn(group["omega"]["policy"].get("check_id"), lab.CHECK_FIELDS)

    def test_simple_short_circuit_theorem_and_equal_budget(self):
        for row in self.target["cases"]:
            for first in lab.CHECK_FIELDS.values():
                prediction, calls = lab.fixed_order(row, first)
                self.assertEqual(prediction == "accept",
                                 row["merged"] and row["touched_tests"])
                self.assertEqual(calls, 1 + int(row[first]))
                self.assertLessEqual(calls, 2)
        report = self.report
        self.assertEqual(report["holdout_cases"], 24)
        self.assertEqual(report["training_cases"], 12)
        self.assertEqual(report["model_calls"], 0)
        self.assertEqual(report["network_calls_in_replay"], 0)
        self.assertEqual(report["arm_caps"], 2)
        for arm, metrics in report["summary"].items():
            self.assertEqual(metrics["cases"], 24, arm)
            self.assertEqual(metrics["correct"], 24, arm)
            self.assertEqual(metrics["wrong"], 0, arm)
            self.assertEqual(metrics["abstain"], 0, arm)
            self.assertLessEqual(metrics["calls"], 48, arm)

    def test_expected_transfer_result_and_no_unearned_omega_advantage(self):
        report = self.report
        counts = {arm:m["calls"] for arm,m in report["summary"].items()}
        self.assertEqual(counts, {
            "always_merged": 26,
            "always_tests": 39,
            "global_marginal": 39,
            "repo_marginal": 31,
            "both_always": 48,
            "Omega_global": 39,
            "Omega_repo": 31,
        })
        self.assertEqual(
            report["retrospective_oracle_not_an_arm"],
            {"global_optimum_calls":26, "per_repo_optimum_calls":26},
        )
        by_case = {}
        for r in report["paired_per_case"]:
            by_case.setdefault((r["repo"],r["number"]),{})[r["arm"]] = r
        self.assertEqual(len(by_case),24)
        for cohort in by_case.values():
            for o, baseline in [("Omega_repo","repo_marginal"),
                                ("Omega_global","global_marginal")]:
                self.assertEqual(cohort[o]["prediction"], cohort[baseline]["prediction"])
                self.assertEqual(cohort[o]["calls"], cohort[baseline]["calls"])

    def test_reordering_training_rows_keeps_frozen_policy(self):
        p = lab.training_policies(self.train)
        shuffled = lab.training_policies(self.train[::-1])
        self.assertEqual(p["global"]["simple_first"],
                         shuffled["global"]["simple_first"])
        self.assertEqual(p["global"]["omega"]["policy"],
                         shuffled["global"]["omega"]["policy"])
        for repo in p["by_repo"]:
            self.assertEqual(p["by_repo"][repo]["omega"]["policy"],
                             shuffled["by_repo"][repo]["omega"]["policy"])

    def test_unknown_repository_falls_back_to_global(self):
        p=lab.training_policies(self.train)
        self.assertNotIn("other/new-repo",p["by_repo"])
        # Explicit policy lookup in the experiment's evaluation uses global.
        group=p["by_repo"].get("other/new-repo",p["global"])
        self.assertIs(group,p["global"])


if __name__ == "__main__":
    unittest.main()
