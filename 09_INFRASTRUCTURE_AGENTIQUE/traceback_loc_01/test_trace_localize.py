"""No-network tests for preregistered traceback ranking without any fixed source."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from trace_localize import parse_frames,map_frame,build_manifest,BUGGY_COMMIT


def fixture(root: Path):
    (root/"youtube_dl").mkdir()
    (root/"test").mkdir()
    (root/"youtube_dl"/"a.py").write_text(
        "def helper(x):\n    return x\n",encoding="utf-8")
    (root/"youtube_dl"/"utils.py").write_text(
        "class Downloader:\n"
        "    def run(self, url):\n"
        "        return 1 / 0\n",encoding="utf-8")
    (root/"test"/"test_utils.py").write_text(
        "from youtube_dl import utils\n"
        "def test_foo():\n    utils.helper(1)\n",encoding="utf-8")
    return root


class FrozenTraceTests(unittest.TestCase):
    def test_actual_unittest_frames_reorder_without_touching_fixed(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(Path(d))
            log=('test_foo (test.test_utils.T.test_foo) ... ERROR\n'
                 'Traceback (most recent call last):\n'
                 '  File "/repo/youtube_dl/utils.py", line 3, in run\n'
                 '    return 1 / 0\n'
                 'ZeroDivisionError: division by zero\n'
                 'Ran 1 test in 0.001s\nFAILED (errors=1)\n')
            result=build_manifest(root,log,1)
            self.assertEqual(result["status"],"BUGGY_TRACE_OBSERVED_NOT_YET_ORACLE_VERIFIED")
            self.assertEqual(result["total_targets"],2)
            self.assertEqual(len(result["ordered_unique_mapped_frame_keys"]),1)
            t=next(t for t in result["target_inventory"] if t["function"]=="run")
            self.assertEqual(t["rank_b"],1)
            self.assertEqual(result["test_suite_reported_tests"],[1])
            self.assertFalse(result["fixed_source_accessed"])
            self.assertIsNone(result["actual_repair_correctness"])

    def test_harness_without_target_frames_is_indeterminate(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(Path(d))
            log=('ImportError: No module named unrelated\n'
                 'Ran 0 tests in 0.0s\nFAILED (errors=1)\n')
            result=build_manifest(root,log,1)
            self.assertEqual(result["status"],"REPRODUCER_UNCONFIRMED")
            self.assertEqual(result["ordered_unique_mapped_frame_keys"],[])
            self.assertEqual(result["top_a"],result["top_b"])

    def test_source_with_no_failure_is_not_reproduced(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(Path(d))
            result=build_manifest(root,"Ran 1 test in 0.1s\nOK\n",0)
            self.assertEqual(result["status"],"BUGGY_TEST_SUITE_PASSED")

    def test_traceback_not_in_package_is_not_evidence(self):
        log=('Traceback (most recent call last):\n'
             '  File "/usr/lib/python3.7/unittest/case.py", line 10, in _callTestMethod\n'
             'RuntimeError: broken\n')
        self.assertEqual(parse_frames(log),[])

    def test_frame_without_function_location_has_no_boost(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(Path(d))
            log=('Traceback (most recent call last):\n'
                 '  File "/repo/youtube_dl/utils.py", line 10000, in unknown\n'
                 'ValueError: sample\n'
                 'Ran 1 test in 0.1s\nFAILED (errors=1)\n')
            result=build_manifest(root,log,1)
            self.assertEqual(result["status"],"REPRODUCER_UNCONFIRMED")
            self.assertEqual(len(result["unmapped_package_frames"]),1)
            self.assertEqual(result["top_a"],result["top_b"])

    def test_source_file_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"youtube_dl").mkdir()
            self.assertEqual(build_manifest(root,"",1)["status"],"NO_TEST_SOURCE")


if __name__=="__main__":
    unittest.main()
