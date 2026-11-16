"""Five no-network non-regressions for PySnooper test-fixture reconstruction."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_fixture import check_fixture,evaluate


def make_tree(root:Path,broken:bool=False):
    (root/"tests"/"mini_toolbox").mkdir(parents=True)
    (root/"tests"/"mini_toolbox"/"__init__.py").write_text(
        "from . import contextlib\n")
    (root/"tests"/"mini_toolbox"/"contextlib.py").write_text(
        "def f():\n    return 42\n" if not broken else "def f():\n    return 99\n")
    (root/"tests"/"test_pysnooper.py").write_text(
        "def test_custom_repr_single():\n    assert True\n")


def profile(status,failed,tests=1):
    return json.dumps({
      "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
      "package":"pysnooper",
      "tests":["tests/test_pysnooper.py::test_custom_repr_single"],
      "status":status,
      "failure_in_test_body":bool(failed),
      "failed_test_count":failed,
      "tests_run":tests,
      "test_passed":not failed,
      "import_or_collection_error":status=="RUNNER_OR_DEPENDENCY_ERROR",
      "profile_observed_calls":2,
    }).encode()


class FixtureUnitTests(unittest.TestCase):
    def setUp(self):
        self.a=tempfile.TemporaryDirectory()
        self.b=tempfile.TemporaryDirectory()
        self.old=Path(self.a.name)
        self.new=Path(self.b.name)
        make_tree(self.old)
        make_tree(self.new)
    def tearDown(self):
        self.a.cleanup()
        self.b.cleanup()
    def test_same_test_tree_is_byte_for_byte(self):
        out=check_fixture(self.old,self.new)
        self.assertTrue(out["same_test_fixture_on_buggy_and_fixed"])
        self.assertEqual(out["file_count"],2)
        self.assertIn("__init__.py",out["files"])
    def test_missing_tree_rejected(self):
        (self.old/"tests"/"mini_toolbox"/"__init__.py").unlink()
        with self.assertRaisesRegex(ValueError,"TEST_FIXTURE_INCOMPLETE"):
            check_fixture(self.old,self.new)
    def test_changed_fixture_byte_rejected(self):
        (self.old/"tests"/"mini_toolbox"/"contextlib.py").write_text("oops\n")
        with self.assertRaisesRegex(ValueError,"TEST_FIXTURE_MISMATCH"):
            check_fixture(self.old,self.new)
    def test_true_buggy_fail_fixed_pass_is_reproduction_not_localization(self):
        out=evaluate(self.old,self.new,profile("TEST_FAILED",1),
                     profile("TEST_PASSED",0))
        self.assertEqual(out["status"],"BUGGY_FAIL_FIXED_PASS")
        self.assertFalse(out["can_credit_localization_gain_to_omega"])
        self.assertTrue(out["pr124_admissible_cases_remain_one_of_three"])
        self.assertFalse(out["new_holdout_blindness"])
    def test_collect_error_is_not_historical_failure(self):
        out=evaluate(self.old,self.new,profile("RUNNER_OR_DEPENDENCY_ERROR",1,0),
                     profile("TEST_PASSED",0))
        self.assertEqual(out["status"],"REPRODUCER_UNCONFIRMED")


if __name__=="__main__":
    unittest.main()
