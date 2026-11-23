"""Falsification-oriented tests for the bounded group-error-only fallback."""
from pathlib import Path
import importlib.util
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner

F=runner.fallback
SAFE=runner.SAFE
LOOP="""def transform(s):
    if s=="hang":
        while True:
            pass
    return [s]
"""
VALID="""def transform(s):
    return [s]
"""
LOGIC_ERROR="""def transform(s):
    if s=="bad":
        return [1/0]
    return [s]
"""

class Tests(unittest.TestCase):
    def test_normal_batch_uses_only_one_worker(self):
        calls=[]
        def fake(code,inputs):
            calls.append(inputs)
            return [{"value":[x]} for x in inputs]
        result=F.evaluate(fake,VALID,["one","two"])
        self.assertEqual(result["status"],"BATCH_ACCEPTED")
        self.assertEqual(result["observations"],[{"value":["one"]},{"value":["two"]}])
        self.assertEqual(result["worker_calls"],1)
        self.assertEqual(len(calls),1)
        self.assertFalse(result["triggered"])

    def test_global_error_isolates_only_on_failure(self):
        calls=[]
        def fake(code,inputs):
            calls.append(inputs)
            if len(inputs)>1:
                return [{"error":"SANDBOX_EXIT_-9"} for _ in inputs]
            return [{"value":[inputs[0]]}] if inputs[0]!="hang" else [{"error":"SANDBOX_EXIT_-9"}]
        result=F.evaluate(fake,LOOP,["fine","hang"])
        self.assertEqual(result["status"],"GLOBAL_FAILURE_ISOLATED")
        self.assertTrue(result["triggered"])
        self.assertEqual(result["worker_calls"],3)
        self.assertEqual(result["observations"],[{"value":["fine"]},{"error":"SANDBOX_EXIT_-9"}])
        self.assertEqual(len(calls),3)
        self.assertEqual(result["batch_observations"],[{"error":"SANDBOX_EXIT_-9"}]*2)

    def test_real_sandbox_masks_and_fallback_recovers_good_case(self):
        SAFE.validate_program(LOOP)
        cases=[{"input":"fine","expected":["fine"]},
               {"input":"hang","expected":["hang"]}]
        batch=runner.grade_dev(LOOP,cases,"batch")
        result=runner.grade_dev(LOOP,cases,"conditional")
        self.assertEqual(batch["correct"],0)
        self.assertEqual(result["correct"],1)
        self.assertEqual(result["rows"][0]["observed"],{"value":["fine"]})
        self.assertIn("error",result["rows"][1]["observed"])
        self.assertEqual(result["workers"],3)

    def test_regular_student_exception_does_not_trigger(self):
        SAFE.validate_program(LOGIC_ERROR)
        grouped=F.evaluate(SAFE.execute_student,LOGIC_ERROR,["good","bad"])
        self.assertEqual(grouped["status"],"BATCH_ACCEPTED")
        self.assertEqual(grouped["observations"][0],{"value":["good"]})
        self.assertEqual(grouped["observations"][1],{"error":"ZeroDivisionError"})
        self.assertEqual(grouped["worker_calls"],1)

    def test_unsafe_input_no_execution(self):
        calls=[]
        def fake(code,inputs):
            calls.append(inputs)
            raise AssertionError("NO_EXECUTION")
        out=F.evaluate(fake,None,["x"])
        self.assertEqual(out["status"],"NO_SAFE_CODE")
        self.assertEqual(out["worker_calls"],0)
        self.assertEqual(calls,[])
        with self.assertRaises(ValueError):
            F.evaluate(fake,VALID,["x"],max_isolated_cases=100)

    def test_bound_prevents_expensive_isolation_and_no_false_success(self):
        calls=[]
        def fake(code,inputs):
            calls.append(inputs)
            return [{"error":"SANDBOX_TIMEOUT_OR_INVALID"} for _ in inputs]
        out=F.evaluate(fake,VALID,["x"]*13)
        self.assertEqual(out["status"],"GLOBAL_FAILURE_UNDIAGNOSED_CAP")
        self.assertEqual(len(calls),1)
        self.assertEqual(out["worker_calls"],1)
        self.assertFalse(out["triggered"])
        self.assertTrue(all("error" in row for row in out["observations"]))

    def test_non_global_and_empty_not_isolated(self):
        def fake(code,inputs):
            return [{"error":"ValueError"} for _ in inputs]
        out=F.evaluate(fake,VALID,["x","y"])
        self.assertEqual(out["status"],"BATCH_ACCEPTED")
        self.assertEqual(out["worker_calls"],1)
        out=F.evaluate(fake,VALID,[])
        self.assertEqual(out["status"],"EMPTY_INPUT")
        self.assertEqual(out["worker_calls"],0)

    def test_original_policies_unchanged_and_holdout_not_read(self):
        valid=[{"input":"a","expected":["a"]}]
        self.assertEqual(runner.grade_dev(VALID,valid,"batch")["correct"],1)
        self.assertEqual(runner.grade_dev(VALID,valid,"isolated")["correct"],1)
        self.assertEqual(runner.grade_dev(VALID,valid,"conditional")["correct"],1)
        source=(HERE/"runner.py").read_text()
        fallback_source=(HERE/"conditional_fallback.py").read_text()
        self.assertNotIn('frozen("SEALED_FROZEN.json")',source)
        self.assertNotIn("SEALED_FROZEN.json",fallback_source)
        self.assertNotIn("import score",fallback_source)

if __name__=="__main__":
    unittest.main()
