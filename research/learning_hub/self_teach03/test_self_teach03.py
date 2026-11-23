"""SELF-TEACH-03 offline test: deterministic positive and adversarial controls."""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner
# old format_audit already imported score v1 under 'score'; load our scorer
# by unique fully qualified path, never use a cached other-version score.
import importlib.util
spec=importlib.util.spec_from_file_location("omega_self_teach03_score",HERE/"score.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

EMPTY="def transform(s):\n    return []\n"
TRAIN_L1="""def transform(s):
    out=[]
    n=0
    for c in s:
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            if n % 2 == 0:
                out.append(c.lower())
            else:
                out.append(c.upper())
            n+=1
    return out
"""
TRAIN_L2="""def transform(s):
    out=[]
    for i in range(0,len(s)-1,2):
        out.append(s[i:i+2])
    return out
"""
E1="""def transform(s):
    out=[]
    n=0
    for i in range(len(s)):
        c=s[i]
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z'):
            n+=1
            if n%3==0:
                out.append(str(i)+':'+c.lower())
    return out
"""
E2="""def transform(s):
    out=[]
    n=0
    for i in range(len(s)):
        c=s[i]
        if c.isdigit():
            n+=1
            if n%2==0:
                out.append(str(i)+':'+c)
    return out
"""
E3="""def transform(s):
    out=[]
    for i in range(1,len(s)):
        if s[i]=='!':
            out.append(s[i-1])
    return out
"""


class DummyModel:
    def __init__(self,better=True,escaped=False):
        self.better=better
        self.escaped=escaped
        self.call_log=[]
        self.prompts=[]
    def __call__(self,messages,tokens,tag):
        prompt=messages[-1]["content"]
        self.prompts.append((tag,prompt))
        self.call_log.append({"tag":tag,"cap":tokens,"usage":{}})
        if tag=="train:L1:first":
            code=EMPTY
        elif tag=="train:L2:first":
            code=TRAIN_L2
        elif tag=="train:L1:repair1":
            code=TRAIN_L1 if self.better else EMPTY
        elif tag=="train:L1:repair2":
            code=EMPTY
        elif tag=="train:L1:lesson":
            return json.dumps({"lesson":
                "Count only qualifying characters, distinguish their logical rank from the absolute input index, and check boundaries."})
        elif tag.startswith("B:") and self.better:
            code={"B:Q1":E1,"B:Q2":E2,"B:Q3":E3}[tag]
        else:
            code=EMPTY
        if self.escaped:
            code=code.replace("\n","\\n")
        return json.dumps({"hypothesis":"Test the boundary conditions before finalizing the algorithm.","code":code})


class TestLearningLedger03(unittest.TestCase):
    def test_frozen_data_and_disjoint_families(self):
        t,e=runner.public_data()
        self.assertEqual((len(t),len(e)),(2,3))
        for name,pin in runner.PINS.items():
            raw=(HERE/name).read_bytes()
            self.assertEqual(runner.git_blob(raw),pin)
            self.assertNotEqual(runner.git_blob(raw+b"X"),pin)
        h=runner.frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        self.assertEqual([len(x["hidden_cases"]) for x in h],[6,6,6])
        for a,b in zip(e,h):
            self.assertEqual(a["id"],b["id"])
            self.assertFalse({x["input"] for x in a["public_examples"]}&
                             {x["input"] for x in b["hidden_cases"]})

    def test_positive_oracle_controls(self):
        t,e=runner.public_data()
        for x,src in zip(t,[TRAIN_L1,TRAIN_L2]):
            self.assertTrue(runner.SAFE.validate_program(src))
            self.assertEqual(runner.grade_cases(src,x["development_cases"])["correct"],10)
        h=runner.frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        for x,src in zip(h,[E1,E2,E3]):
            self.assertTrue(runner.SAFE.validate_program(src))
            self.assertEqual(runner.grade_cases(src,x["hidden_cases"])["correct"],6)

    def test_successful_mock_ledger_and_noncausal_evaluation(self):
        fake=DummyModel()
        raw=runner.run(fake)
        self.assertEqual(raw["practice"]["selected_id"],"L1")
        self.assertLess(raw["practice"]["initial_score"],10)
        self.assertEqual(raw["practice"]["best_score"],10)
        self.assertTrue(raw["practice"]["admitted_memory"])
        self.assertEqual(raw["total_llm_calls"],13)
        self.assertEqual(raw["training_trace_head"],runner.verify_trace(raw["training_trace"]))
        events=[x["kind"] for x in raw["training_trace"]]
        self.assertIn("FEEDBACK_OFFERED",events)
        self.assertIn("LESSON_CANDIDATE",events)
        self.assertEqual(events.count("TRAIN_ATTEMPT"),3)
        self.assertFalse(any("EVAL_SEALED" in p for _,p in fake.prompts))
        result=score.grade(raw)
        self.assertEqual(result["B"]["exact"],18)
        self.assertEqual(result["B"]["full"],3)
        self.assertEqual(result["status"],"EXPLORATORY_LESSON_TRANSFER_ONLY")
        self.assertFalse(result["causal_generalization_proven"])
        self.assertEqual(result["training"]["repairs"],1)

    def test_failed_repairs_rolled_back_logged_and_no_memory(self):
        fake=DummyModel(better=False)
        raw=runner.run(fake)
        self.assertFalse(raw["practice"]["admitted_memory"])
        trials=[x["payload"] for x in raw["training_trace"]
                if x["kind"]=="TRAIN_ATTEMPT" and ":repair" in x["payload"]["tag"]]
        self.assertEqual(len(trials),2)
        self.assertTrue(all(x["decision"]=="ROLLBACK_NO_GAIN" for x in trials))
        self.assertEqual(raw["practice"]["best_score"],raw["practice"]["initial_score"])
        result=score.grade(raw)
        self.assertEqual(result["status"],"NO_AUTONOMOUS_LEARNING_GAIN_DEMONSTRATED")
        self.assertEqual(result["B"]["exact"],result["P"]["exact"])

    def test_escaped_line_normalization_retains_safety(self):
        fake=DummyModel(escaped=True)
        raw=runner.run(fake)
        self.assertTrue(raw["practice"]["admitted_memory"])
        result=score.grade(raw)
        self.assertEqual(result["B"]["exact"],18)
        self.assertGreater(result["B"]["format_recovered"],0)
        self.assertEqual(result["B"]["strict_exact"],0)

    def test_unsafe_candidate_not_accepted(self):
        raw=json.dumps({"code":"def transform(s):\\n    return open('secret')"})
        code,status,strict=runner.parse(raw)
        self.assertIsNone(code)
        self.assertTrue(status.startswith("REJECTED"))

    def test_minimal_counterexamples_are_selected_deterministically(self):
        dev={"rows":[
            {"input":"aaa","correct":False,"expected":[],"observed":{"value":[]}},
            {"input":"!","correct":False,"expected":[],"observed":{"value":[]}},
            {"input":"bb","correct":False,"expected":[],"observed":{"value":[]}},
            {"input":"c","correct":False,"expected":[],"observed":{"value":[]}},
            {"input":"x","correct":True,"expected":[],"observed":{"value":[]}},
        ]}
        self.assertEqual([x["input"] for x in runner.feedback_for(dev)],["!","c","bb"])
        self.assertEqual(runner.MAX_FEEDBACK,3)

    def test_tampered_trace_and_raw_output_rejected(self):
        raw=runner.run(DummyModel())
        bad=copy.deepcopy(raw)
        bad["training_trace"][0]["payload"]["development"]["correct"]+=1
        with self.assertRaisesRegex(ValueError,"TRACE_CHAIN_BROKEN"):
            score.grade(bad)
        bad=copy.deepcopy(raw)
        bad["training_trace_head"]="0"*64
        with self.assertRaisesRegex(ValueError,"TRACE_HEAD_MISMATCH"):
            score.grade(bad)
        bad=copy.deepcopy(raw)
        bad["B"][0]["raw"]+="!"
        with self.assertRaisesRegex(ValueError,"MODEL_OUTPUT_CHANGED"):
            score.grade(bad)

    def test_false_memory_and_weights_rejected(self):
        raw=runner.run(DummyModel())
        bad=copy.deepcopy(raw)
        bad["practice"]["admitted_memory"]="unverified"
        with self.assertRaisesRegex(ValueError,"PRACTICE_SUMMARY_MISMATCH"):
            score.grade(bad)
        bad=copy.deepcopy(raw)
        bad["C"]["weight_updates"]=2
        with self.assertRaisesRegex(ValueError,"ILLEGAL_AUTONOMOUS_SIDE_EFFECT"):
            score.grade(bad)

    def test_generator_has_no_sealed_import(self):
        src=(HERE/"runner.py").read_text()
        self.assertNotIn('frozen("EVAL_SEALED_FROZEN.json")',src)
        self.assertNotIn("import score",src)
        self.assertNotIn("from score import",src)


if __name__=="__main__":
    unittest.main()
