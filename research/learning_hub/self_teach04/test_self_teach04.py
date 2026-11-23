"""SELF-TEACH-04: offline positive/negative tests; no LLM or paid API."""
from pathlib import Path
from hashlib import sha256
import copy
import json
import sys
import unittest
import importlib.util

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner
spec=importlib.util.spec_from_file_location("omega_self_teach04_score", HERE/"score.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

EMPTY="def transform(s):\n    return []\n"

R1="""def transform(s):
    out=[]
    if len(s)==0:
        return out
    prev=s[0]
    n=1
    for i in range(1,len(s)):
        if s[i]==prev:
            n+=1
        else:
            out.append(prev+":"+str(n))
            prev=s[i]
            n=1
    out.append(prev+":"+str(n))
    return out
"""
R2="""def transform(s):
    out=[]
    cur=""
    for c in s:
        if "0"<=c<="9":
            cur+=c
        else:
            if len(cur)>=2:
                out.append(cur)
            cur=""
    if len(cur)>=2:
        out.append(cur)
    return out
"""
Q1="""def transform(s):
    out=[]
    start=-1
    for i in range(len(s)):
        c=s[i]
        if "A"<=c<="Z":
            if start==-1:
                start=i
        else:
            if start!=-1:
                out.append(str(start)+":"+str(i-start))
                start=-1
    if start!=-1:
        out.append(str(start)+":"+str(len(s)-start))
    return out
"""
Q2="""def transform(s):
    out=[]
    cur=""
    for c in s:
        if c in "aeiouAEIOU":
            cur+=c
        else:
            if len(cur)>=2:
                out.append(cur)
            cur=""
    if len(cur)>=2:
        out.append(cur)
    return out
"""
Q3="""def transform(s):
    out=[]
    start=-1
    for i in range(len(s)):
        if s[i]=="#" or s[i]=="@":
            if start==-1:
                start=i
        else:
            if start!=-1:
                out.append(str(i-1)+":"+str(i-start))
                start=-1
    if start!=-1:
        out.append(str(len(s)-1)+":"+str(len(s)-start))
    return out
"""

class FakeClient:
    def __init__(self,positive=False):
        self.positive=positive
        self.call_log=[]
    def __call__(self,messages,tokens,tag):
        self.call_log.append({"tag":tag,"cap":tokens})
        if tag=="train:R1:first":
            code=EMPTY
        elif tag=="train:R2:first":
            code=R2
        elif tag=="train:R1:repair1":
            code=R1 if self.positive else EMPTY
        elif tag=="train:R1:repair2":
            code=EMPTY
        elif tag=="train:R1:lesson":
            return json.dumps({"lesson":"Track each contiguous run, emit at the first breaking character, and flush a qualifying final run."})
        elif tag.startswith("B:") and self.positive:
            code={"B:Q1":Q1,"B:Q2":Q2,"B:Q3":Q3}[tag]
        else:
            code=EMPTY
        return json.dumps({"hypothesis":"Carry a run state through input and emit at boundaries.","code":code})

class TestSelfTeach04(unittest.TestCase):
    def test_pins_schemas_partitions(self):
        t,e=runner.public_data()
        self.assertEqual((len(t),len(e)),(2,3))
        for name,pin in runner.PINS.items():
            self.assertEqual(runner.git_blob((HERE/name).read_bytes()),pin)
        h=runner.frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        self.assertEqual(len(h),3)
        self.assertEqual([len(x["hidden_cases"]) for x in h],[6,6,6])
        self.assertEqual(len({x["family"] for x in t+e}),5)
        for a,b in zip(e,h):
            self.assertEqual(a["id"],b["id"])
            self.assertFalse({x["input"] for x in a["public_examples"]}&{x["input"] for x in b["hidden_cases"]})

    def test_oracles_nontrivial_and_safe(self):
        t,_=runner.public_data()
        h=runner.frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        for item,src in zip(t,[R1,R2]):
            runner.SAFE.validate_program(src)
            self.assertEqual(runner.grade_cases(src,item["development_cases"])["correct"],10)
        for item,src in zip(h,[Q1,Q2,Q3]):
            runner.SAFE.validate_program(src)
            self.assertEqual(runner.grade_cases(src,item["hidden_cases"])["correct"],6)

    def test_no_memory_reuses_control_instead_of_stochastic_replay(self):
        client=FakeClient()
        raw=runner.run(client)
        self.assertEqual(raw["B_actual_model_calls"],0)
        self.assertTrue(raw["B_alias_of_P_without_memory"])
        self.assertFalse(any(x["tag"].startswith("B:") for x in client.call_log))
        self.assertEqual([x["raw"] for x in raw["P"]],[x["raw"] for x in raw["B"]])
        verdict=score.grade(raw)
        self.assertEqual(verdict["P"]["exact"],verdict["B"]["exact"])
        self.assertEqual(verdict["status"],"NO_AUTONOMOUS_LEARNING_GAIN_DEMONSTRATED")

    def test_positive_mock_proves_software_path_not_actual_learning(self):
        client=FakeClient(positive=True)
        raw=runner.run(client)
        self.assertTrue(raw["practice"]["admitted_memory"])
        self.assertEqual(raw["B_actual_model_calls"],3)
        self.assertFalse(raw["B_alias_of_P_without_memory"])
        self.assertEqual(raw["practice"]["initial_score"],0)
        self.assertEqual(raw["practice"]["best_score"],10)
        verdict=score.grade(raw)
        self.assertEqual(verdict["status"],"EXPLORATORY_LESSON_TRANSFER_ONLY")
        self.assertEqual(verdict["B"]["exact"],18)
        self.assertFalse(verdict["causal_generalization_proven"])

    def test_fake_b_gain_rejected_without_memory(self):
        raw=runner.run(FakeClient())
        bad=copy.deepcopy(raw)
        bad["B"][0]["raw"]="tampered"
        with self.assertRaisesRegex(ValueError,"NO_MEMORY_B_MUST_EQUAL_P"):
            score.grade(bad)

    def test_raw_and_ledger_integrity_checked(self):
        raw=runner.run(FakeClient(positive=True))
        bad=copy.deepcopy(raw)
        bad["training_trace"][0]["payload"]["development"]["correct"]=55
        with self.assertRaisesRegex(ValueError,"TRACE_CHAIN_BROKEN"):
            score.grade(bad)
        bad=copy.deepcopy(raw)
        bad["B"][0]["raw"]+="!"
        with self.assertRaisesRegex(ValueError,"MODEL_OUTPUT_CHANGED"):
            score.grade(bad)

    def test_sealed_not_imported_in_generator(self):
        src=(HERE/"runner.py").read_text()
        self.assertNotIn('frozen("EVAL_SEALED_FROZEN.json")',src)
        self.assertNotIn("import score",src)

if __name__=="__main__":
    unittest.main()
