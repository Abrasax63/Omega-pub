"""Integrity, safe classification and fail-closed tests for frozen-pool coverage."""
import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from pool_coverage import (
    EXPECTED_POOL_SIZE,EXPECT_PREVIOUS,EXPECTED_REMAINING,
    verify_manifest,classify_test,expand_one,digest,
)

def fixture(case="B2",early_exit=1):
    old={"cases":[{"id":case,"historical_regression_reproduced":True,
                   "verdict":"REPAIR_REFUTED"}]}
    early=[{"id":"R"+str(i).zfill(2),"exit":early_exit,
            "passes_real_regression":False} for i in range(EXPECT_PREVIOUS)]
    summary={"experiment":"OMEGA-TRACE-REPAIR-01",
             "cases":[{"id":case,"status":"REPAIRS_REFUTED_OR_NO_CANDIDATES",
                       "patches_tested":early}]}
    candidates=[
        {"id":"R"+str(i).zfill(2),"path":"tqdm/std.py","rule":"invert-branch",
         "lines":[i+1],"changes":[{"line":i+1,"before":"if flag:","after":"if not flag:"}],
         "source_sha256":"a"*64,"source_before_sha256":"b"*64}
        for i in range(EXPECTED_POOL_SIZE)
    ]
    manifest={"candidate_count":20,"candidates":candidates}
    return old,summary,manifest

class PoolCoverageTests(unittest.TestCase):
    def test_budget_exact(self):
        self.assertEqual(EXPECTED_POOL_SIZE,20)
        self.assertEqual(EXPECT_PREVIOUS,6)
        self.assertEqual(EXPECTED_REMAINING,14)

    def test_verify_exact_frozen_pool_and_historical_pair(self):
        old,summary,pool=fixture()
        early,rows=verify_manifest("B2",old,summary,pool)
        self.assertEqual(len(early),6)
        self.assertEqual(len(rows),20)

    def test_candidate_reorder_refused(self):
        old,summary,pool=fixture()
        pool["candidates"][0],pool["candidates"][1]=pool["candidates"][1],pool["candidates"][0]
        with self.assertRaisesRegex(ValueError,"order"):
            verify_manifest("B2",old,summary,pool)

    def test_missing_positive_history_refused(self):
        old,summary,pool=fixture()
        old["cases"][0]["historical_regression_reproduced"]=False
        with self.assertRaisesRegex(ValueError,"not reproduced"):
            verify_manifest("B2",old,summary,pool)

    def test_candidate_source_line_inventory_refused(self):
        old,summary,pool=fixture()
        pool["candidates"][14]["lines"]=[100,200,300]
        with self.assertRaisesRegex(ValueError,"one or two"):
            verify_manifest("B2",old,summary,pool)

    def test_no_results_misclassified_success(self):
        tests=[
            ({"exit":0,"combined_log":"1 passed"},"TEST_PASSED"),
            ({"exit":1,"combined_log":"FAILED test_foo - AssertionError"},"TEST_FAILED"),
            ({"exit":2,"combined_log":"ERROR collecting test_file.py"},"COLLECTION_OR_PATCH_ERROR"),
            ({"exit":1,"combined_log":"ModuleNotFoundError: xyz"},"COLLECTION_OR_PATCH_ERROR"),
            ({"exit":None,"combined_log":"Timed out"},"ENVIRONMENT_OR_EXECUTION_ERROR"),
            ({"exit":1,"combined_log":"unknown failure"},"UNCLASSIFIED_FAILURE"),
        ]
        for data,expected in tests:
            with self.subTest(expected=expected):
                self.assertEqual(classify_test(data),expected)

    def test_diagnostic_runs_only_rank_seven_to_twenty(self):
        old,summary,pool=fixture()
        with TemporaryDirectory() as temp:
            evidence=Path(temp)
            (evidence/"B2-patches.json").write_text(json.dumps(pool),encoding="utf-8")
            observed=[]
            def stage(work,case,c):
                observed.append(c["id"])
            with patch("pool_coverage.stage_patch",side_effect=stage),patch(
                "pool_coverage.run_docker",return_value={
                  "exit":1,"combined_log":"FAILED test_example - AssertionError"
                }):
                report=expand_one("B2",evidence,evidence,old,summary)
            self.assertEqual(report["executed_new_tests"],14)
            self.assertEqual(observed,["R"+str(i).zfill(2) for i in range(6,20)])
            self.assertEqual(report["verdict"],"NO_REPAIR_IN_PREDEFINED_20_CANDIDATES")
            self.assertEqual(len(list(evidence.glob("B2-expanded-R*.log"))),14)

    def test_late_success_separate_from_negative(self):
        old,summary,pool=fixture()
        with TemporaryDirectory() as temp:
            evidence=Path(temp)
            (evidence/"B2-patches.json").write_text(json.dumps(pool),encoding="utf-8")
            seq=[{"exit":0,"combined_log":"1 passed"}]+[
                {"exit":1,"combined_log":"FAILED example - AssertionError"}]*13
            with patch("pool_coverage.stage_patch"),patch(
                "pool_coverage.run_docker",side_effect=seq):
                report=expand_one("B2",evidence,evidence,old,summary)
            self.assertEqual(report["verdict"],"LATE_SUCCESS_BUDGET_LIMITATION")
            self.assertEqual(report["late_passes"],1)

    def test_environment_error_not_promoted_to_scientific_rejection(self):
        old,summary,pool=fixture()
        with TemporaryDirectory() as temp:
            evidence=Path(temp)
            (evidence/"B2-patches.json").write_text(json.dumps(pool),encoding="utf-8")
            seq=[{"exit":None,"combined_log":"Docker daemon missing"}]+[
                {"exit":1,"combined_log":"FAILED example - AssertionError"}]*13
            with patch("pool_coverage.stage_patch"),patch(
                "pool_coverage.run_docker",side_effect=seq):
                report=expand_one("B2",evidence,evidence,old,summary)
            self.assertEqual(report["verdict"],"INDETERMINATE_EXECUTION")

    def test_hashed_manifest_order_matters(self):
        _,_,pool=fixture()
        before=digest(pool["candidates"])
        pool["candidates"].reverse()
        self.assertNotEqual(before,digest(pool["candidates"]))

if __name__=="__main__":
    unittest.main()
