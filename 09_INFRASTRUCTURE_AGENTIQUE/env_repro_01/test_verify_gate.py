"""No-network nonregression of reproduction-only gate."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_gate import check
from freeze_ranks import get_case


class GateTests(unittest.TestCase):
    def data(self,case,status,runs,failed,body_error=False):
        return json.dumps({
          "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
          "package":case["package"],
          "tests":case["tests"],
          "status":status,
          "tests_run":runs,
          "failed_test_count":failed,
          "failure_in_test_body":body_error,
          "import_or_collection_error":status=="RUNNER_OR_DEPENDENCY_ERROR",
          "test_passed":status=="TEST_PASSED",
          "profile_observed_calls":4,
        }).encode()

    def test_buggy_fail_fixed_pass_is_reproduction_only(self):
        c=get_case("scrapy-2")
        out=check(c,self.data(c,"TEST_FAILED",1,1,True),
                  self.data(c,"TEST_PASSED",1,0),"testsha")
        self.assertEqual(out["status"],"BUGGY_FAIL_FIXED_PASS")
        self.assertTrue(out["ranks_not_computed"])
        self.assertFalse(out["new_holdout_blindness"])

    def test_missing_import_never_counts_as_historical_failure(self):
        c=get_case("pysnooper-2")
        out=check(c,self.data(c,"RUNNER_OR_DEPENDENCY_ERROR",1,1,False),
                  self.data(c,"TEST_PASSED",1,0),"sha")
        self.assertEqual(out["status"],"REPRODUCER_UNCONFIRMED")

    def test_fixed_fail_never_confirms_bug(self):
        c=get_case("scrapy-2")
        out=check(c,self.data(c,"TEST_FAILED",1,1,True),
                  self.data(c,"TEST_FAILED",1,1,True),"sha")
        self.assertFalse(out["historical_bug_reproduced"])

    def test_wrong_case_profile_is_rejected(self):
        a=get_case("scrapy-2")
        b=get_case("pysnooper-2")
        with self.assertRaisesRegex(ValueError,"CASE_OR_TEST_CHANGED"):
            check(a,self.data(b,"TEST_FAILED",1,1,True),
                  self.data(a,"TEST_PASSED",1,0),"sha")


if __name__=="__main__":
    unittest.main()
