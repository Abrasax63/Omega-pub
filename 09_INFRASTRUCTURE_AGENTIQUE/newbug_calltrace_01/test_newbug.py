"""Regression tests for youtube-dl-2 frozen candidate ranks and oracle gates."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from rank_new import OFFICIAL_TEST,rank,sha
from oracle_new import evaluate


def fixture(root:Path,good=False):
    (root/"youtube_dl").mkdir()
    (root/"test").mkdir()
    (root/"youtube_dl"/"utils.py").write_text(
        "def find_result(x):\n    return "+("True" if good else "False")+"\n",
        encoding="utf-8")
    (root/"test"/"test_InfoExtractor.py").write_text(
        "from youtube_dl import utils\n"
        "class TestInfoExtractor:\n"
        "    def test_parse_mpd_formats(self):\n"
        "        assert utils.find_result('test')\n",encoding="utf-8")


def profile(test_passed=False,func="find_result"):
    return {
       "experiment":"OMEGA-RUNTIME-CALLTRACE-01",
       "target_test":OFFICIAL_TEST,
       "project_source_root":"youtube_dl",
       "fixed_production_accessed":False,
       "observed_calls":1,
       "test_count":1,"tests_run":1,
       "test_passed":test_passed,
       "failures":0 if test_passed else 1,
       "errors":0,
       "truncated":False,
       "profiled_seconds":0.01,
       "events":[{"file":"youtube_dl/utils.py","firstlineno":1,
                  "function":func}],
    }


class NewBugTests(unittest.TestCase):
    def test_exact_official_command_frozen(self):
        self.assertEqual(OFFICIAL_TEST,
                         "test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats")

    def test_fail_and_profile_changes_rank_not_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            fixture(root)
            manifest=rank(root,json.dumps(profile()).encode())
            self.assertEqual(manifest["status"],"BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN")
            self.assertEqual(manifest["target_count"],1)
            self.assertEqual(manifest["mapped_functions"],1)
            self.assertEqual(manifest["targets"][0]["rank_a"],1)
            self.assertEqual(manifest["targets"][0]["rank_b"],1)
            self.assertFalse(manifest["production_fixed_accessed"])
            self.assertTrue(manifest["valid_profile_gate"])

    def test_passing_profile_is_negative_control_not_buggy_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            fixture(root)
            manifest=rank(root,json.dumps(profile(test_passed=True)).encode())
            self.assertEqual(manifest["status"],"REPRODUCER_UNCONFIRMED")
            self.assertFalse(manifest["valid_profile_gate"])

    def test_unmapped_events_do_not_fabricate_signal(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            fixture(root)
            p=profile(func="absent")
            p["events"][0]["firstlineno"]=50
            manifest=rank(root,json.dumps(p).encode())
            self.assertEqual(manifest["status"],"NO_USABLE_CALL_EVENTS")
            self.assertEqual(manifest["unmapped_events"],1)
            self.assertEqual(manifest["top_a"],manifest["top_b"])

    def test_wrong_test_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            fixture(root)
            p=profile()
            p["target_test"]="test.unrelated.test_x"
            with self.assertRaisesRegex(ValueError,"WRONG_PROFILE_OR_TEST"):
                rank(root,json.dumps(p).encode())

    def test_oracle_requires_frozen_manifest_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            fixture(root)
            with self.assertRaisesRegex(ValueError,"FROZEN_RANK_DRIFT"):
                evaluate(b"{}","0"*64,root,root,b"{}",b"{}")

    def test_source_diff_oracle_with_passing_control(self):
        with tempfile.TemporaryDirectory() as b,tempfile.TemporaryDirectory() as f:
            bug=Path(b)
            fixed=Path(f)
            fixture(bug)
            fixture(fixed,good=True)
            raw=json.dumps(profile(),sort_keys=True).encode()
            data=rank(bug,raw)
            encoded=json.dumps(data,sort_keys=True).encode()
            passing=json.dumps(profile(test_passed=True)).encode()
            result=evaluate(encoded,sha(encoded),bug,fixed,passing,raw)
            self.assertTrue(result["historical_reproduction_confirmed"])
            self.assertEqual(len(result["oracle"]["oracle_target_keys"]),1)
            self.assertEqual(result["status"],"NO_DIFFERENCE")
            self.assertTrue(result["passing_fixed_calls_not_used_for_ranking"])
            self.assertGreaterEqual(result["unique_name_file_pairs_in_both_profiles"],1)
            self.assertFalse(result["independent_generalization_demonstrated"])


if __name__=="__main__":
    unittest.main()
