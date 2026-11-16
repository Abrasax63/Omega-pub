"""No-network regression tests; no fixed source from any selected BugsInPy case."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from freeze_ranks import get_case,rank,classify,digest
from oracle import changed_functions,score_ranks,evaluate
from run_tests_profile import function_hook


class CohortTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/"pysnooper").mkdir()
        (self.root/"tests").mkdir()
        (self.root/"pysnooper"/"utils.py").write_text(
            "def unrelated():\n    return False\n"
            "def suspect(x):\n    return True\n",encoding="utf-8")
        (self.root/"tests"/"test_pysnooper.py").write_text(
            "from pysnooper import utils\n"
            "def test_example():\n    assert not utils.unrelated()\n",encoding="utf-8")
        self.case=get_case("pysnooper-2")
    def tearDown(self):
        self.temp.cleanup()

    def profile(self, events=None,status="TEST_FAILED",failures=1):
        return {
          "experiment":"OMEGA-MULTIPROJECT-CALLTRACE-01",
          "package":"pysnooper","tests":self.case["tests"],
          "status":status,
          "failed_call_events":events or [],
          "passed_call_events":[],
          "profile_truncated":False,
          "tests_run":1,"failed_test_count":failures,
          "failure_in_test_body":bool(failures),
          "import_or_collection_error":False,
          "test_passed":not failures,
          "profile_observed_calls":len(events or []),
          "profile_seconds":0.02,
          "fixed_production_accessed":False,
        }
    def fixture_rank(self):
        events=[{"file":"pysnooper/utils.py","firstlineno":3,"function":"suspect"}]
        return rank(self.case,self.root,json.dumps(self.profile(events)).encode())

    def test_exact_three_preregistered_distinct_projects(self):
        from freeze_ranks import HERE
        data=json.loads((HERE/"cases.json").read_text())
        cases=data["cases"]
        self.assertEqual(len(cases),3)
        self.assertEqual({x["id"] for x in cases},
                         {"pysnooper-2","tqdm-9","scrapy-2"})
        self.assertEqual(len({x["project"] for x in cases}),3)

    def test_observed_call_survives_assertion_outside_package(self):
        p=self.root/"pysnooper"/"f.py"
        p.write_text("def mistaken():\n    return True\n")
        loc={}
        exec(compile(p.read_text(),str(p),"exec"),loc)
        observed=[]
        stats={"count":0,"truncated":False}
        prev=sys.getprofile()
        try:
            sys.setprofile(function_hook(self.root,"pysnooper",observed,stats))
            value=loc["mistaken"]()
        finally:
            sys.setprofile(prev)
        with self.assertRaises(AssertionError):
            self.assertFalse(value)
        self.assertEqual(len(observed),1)
        self.assertEqual(observed[0]["function"],"mistaken")

    def test_outside_package_produces_no_events(self):
        observed=[]
        stats={"count":0,"truncated":False}
        prev=sys.getprofile()
        try:
            sys.setprofile(function_hook(self.root,"pysnooper",observed,stats))
            repr(3)
        finally:
            sys.setprofile(prev)
        self.assertEqual(observed,[])

    def test_rank_three_arms_same_targets(self):
        report=self.fixture_rank()
        self.assertEqual(report["status"],"BUGGY_FAIL_WITH_PROFILE_RANKS_FROZEN")
        self.assertEqual(report["mapped_unique_functions"],1)
        self.assertEqual(report["target_count"],2)
        for key in ("rank_a","rank_b_membership","rank_c_recency"):
            self.assertEqual({x[key] for x in report["targets"]},{1,2})
        suspect=next(x for x in report["targets"] if x["function"]=="suspect")
        self.assertEqual(suspect["rank_c_recency"],1)

    def test_no_causal_claim_for_passing_or_import_error(self):
        out=self.profile(status="TEST_PASSED",failures=0)
        self.assertEqual(classify(out),"BUGGY_NOT_REPRODUCED")
        out=self.profile(status="RUNNER_OR_DEPENDENCY_ERROR")
        self.assertEqual(classify(out),"REPRODUCER_UNCONFIRMED")
        out=self.profile(status="TEST_FAILED",failures=1)
        out["profile_truncated"]=True
        self.assertEqual(classify(out),"TRUNCATED_PROFILE")

    def test_tests_nested_in_package_not_candidates(self):
        sub=self.root/"pysnooper"/"tests"
        sub.mkdir()
        (sub/"test_bad.py").write_text("def copied_fixed_test():\n    pass\n")
        report=self.fixture_rank()
        self.assertFalse(any("/tests/" in x["file"] for x in report["targets"]))
        self.assertFalse(any("/tests/" in name for name in report["source_hashes"]))

    def test_oracle_hunk_inside_single_function(self):
        r=self.fixture_rank()
        with tempfile.TemporaryDirectory() as fixed_dir:
            fixed=Path(fixed_dir)
            (fixed/"pysnooper").mkdir()
            (fixed/"pysnooper"/"utils.py").write_text(
                "def unrelated():\n    return False\n"
                "def suspect(x):\n    return False\n",encoding="utf-8")
            oracle=changed_functions(self.root,fixed,r,"pysnooper")
            self.assertEqual(len(oracle["oracle_keys"]),1)
            self.assertEqual(oracle["unresolved_hunks"],[])
            scored=score_ranks(r,oracle)
            self.assertEqual(scored["scores"]["C_last_call"]["best_rank"],1)

    def test_tampered_rank_sha_rejected_before_oracle(self):
        with self.assertRaisesRegex(ValueError,"FROZEN_RANK_DRIFT"):
            evaluate(self.case,b'{}',"0"*64,self.root,self.root,b'{}',b'{}')


if __name__=="__main__":
    unittest.main()
