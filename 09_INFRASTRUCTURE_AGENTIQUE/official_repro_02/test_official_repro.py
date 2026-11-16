"""Tests for canonical BugsInPy-1 single-test harness."""
from pathlib import Path
import sys, tempfile, unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from official_rank import official_rank,TARGET_TEST
from official_oracle import official_evaluate

class OfficialReproTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/"youtube_dl").mkdir()
        (self.root/"test").mkdir()
        (self.root/"youtube_dl"/"utils.py").write_text(
            "def match_str(value):\n    return False\n")
        (self.root/"test"/"test_utils.py").write_text(
            "from youtube_dl import utils\ndef test_match_str():\n"
            "    assert utils.match_str('ok')\n")
    def tearDown(self):
        self.tmp.cleanup()
    def test_target_is_exactly_official(self):
        self.assertEqual(TARGET_TEST,"test.test_utils.TestUtil.test_match_str")
    def test_frame_can_boost_real_function(self):
        log=('Traceback (most recent call last):\n'
             '  File "/repo/youtube_dl/utils.py", line 2, in match_str\n'
             'AssertionError\nRan 1 test in 0.01s\nFAILED (failures=1)\n')
        r=official_rank(self.root,log,1)
        self.assertEqual(r["status"],"BUGGY_TRACE_OBSERVED_NOT_YET_ORACLE_VERIFIED")
        self.assertEqual(len(r["ordered_unique_mapped_frame_keys"]),1)
        self.assertEqual(r["experiment"],"OMEGA-BUGSINPY-OFFICIAL-REPRO-02")
        self.assertFalse(r["fixed_source_accessed"])
    def test_no_fail_is_not_false_success(self):
        r=official_rank(self.root,"Ran 1 test in 0.1s\nOK\n",0)
        self.assertEqual(r["status"],"BUGGY_TEST_SUITE_PASSED")
        self.assertEqual(r["top_a"],r["top_b"])
    def test_bad_commitment_rejected(self):
        with self.assertRaisesRegex(ValueError,"RANK_MANIFEST_DRIFT"):
            official_evaluate(b"{}","0"*64,self.root,self.root,"",1)

if __name__=="__main__":
    unittest.main()
