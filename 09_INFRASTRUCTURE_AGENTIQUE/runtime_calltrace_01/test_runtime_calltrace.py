"""No-network tests: call trace survives assertion-only failure and SHA drift fails closed."""
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from profile_test import project_profiler
from profile_rank import locate_event,rank
from compare_oracle import evaluate


class RuntimeTraceUnitTests(unittest.TestCase):
    def test_call_is_captured_even_if_assertion_happens_after_return(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            path=root/"youtube_dl"/"utils.py"
            path.parent.mkdir()
            path.write_text("def wrong():\n    return True\n",encoding="utf-8")
            local={}
            exec(compile(path.read_text(),str(path),"exec"),local)
            observed=[]
            stats={"observed_calls":0,"truncated":False}
            prior=sys.getprofile()
            try:
                sys.setprofile(project_profiler(root,"youtube_dl",observed,stats))
                value=local["wrong"]()
            finally:
                sys.setprofile(prior)
            with self.assertRaises(AssertionError):
                self.assertFalse(value)
            self.assertEqual(len(observed),1)
            self.assertEqual(observed[0]["function"],"wrong")
            self.assertEqual(observed[0]["file"],"youtube_dl/utils.py")
            self.assertFalse(stats["truncated"])

    def test_outside_package_is_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"youtube_dl").mkdir()
            observed=[]
            stats={"observed_calls":0,"truncated":False}
            def external():
                return 1
            prior=sys.getprofile()
            try:
                sys.setprofile(project_profiler(root,"youtube_dl",observed,stats))
                external()
            finally:
                sys.setprofile(prior)
            self.assertEqual(observed,[])

    def test_mapping_with_exact_function_name(self):
        target={"key":"youtube_dl/u.py::m@12","file":"youtube_dl/u.py",
                "line":12,"end_line":18,"function":"m"}
        self.assertEqual(locate_event({"file":"youtube_dl/u.py","firstlineno":12,
                                        "function":"m"},{"youtube_dl/u.py":[target]}),
                         target["key"])

    def test_baseline_source_must_be_the_frozen_one(self):
        with self.assertRaisesRegex(ValueError,"BASELINE_MANIFEST_DRIFT"):
            rank(b"{}",b"{}")

    def test_oracle_must_be_the_frozen_one(self):
        with self.assertRaisesRegex(ValueError,"PROFILE_RANKS_DRIFT"):
            evaluate(b"{}", "0"*64, b"{}")


if __name__=="__main__":
    unittest.main()
