"""Offline validation for SELF-TEACH02: no real LLM or API; deterministic mocks."""
from __future__ import annotations
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner
# self_teach01/format_audit imports its own 'score' earlier in sys.modules;
# load v2's score module by unique name to avoid a cross-version collision.
import importlib.util
spec=importlib.util.spec_from_file_location("omega_self_teach02_score", HERE/"score.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

DIGITS="""def transform(s):
    out = []
    buf = ""
    for ch in s:
        if ch.isdigit():
            buf += ch
        else:
            if buf:
                out.append(buf)
                buf = ""
    if buf:
        out.append(buf)
    return out
"""
REVERSE="""def transform(s):
    out = []
    for field in s.split(' '):
        if field:
            out.append(field[::-1])
    return out
"""
X1="""def transform(s):
    out = []
    buf = ""
    for c in s:
        if c.isalpha():
            buf += c
        elif buf:
            out.append(buf.lower())
            buf = ""
    if buf:
        out.append(buf.lower())
    return out
"""
X2="""def transform(s):
    out = []
    count = 0
    for c in s:
        if c == '#':
            count += 1
        else:
            if count:
                out.append(str(count))
                count = 0
    if count:
        out.append(str(count))
    return out
"""
X3="""def transform(s):
    out = []
    buf = ""
    for c in s:
        if c.isupper():
            buf += c
        else:
            if buf:
                out.append(buf + ':' + str(len(buf)))
                buf = ""
    if buf:
        out.append(buf + ':' + str(len(buf)))
    return out
"""
EMPTY="def transform(s):\n    return []\n"


class FakeModel:
    def __init__(self,correct_repair=True,escape_lines=False):
        self.correct_repair=correct_repair
        self.escape_lines=escape_lines
        self.call_log=[]
        self.prompts=[]
    def __call__(self,messages,tokens,tag):
        prompt=messages[-1]["content"]
        self.prompts.append((tag,prompt))
        self.call_log.append({"tag":tag,"cap":tokens})
        if tag=="train:T1:initial":
            code=EMPTY
        elif tag=="train:T2:initial":
            code=REVERSE
        elif tag.startswith("train:T1:repair"):
            code=DIGITS if self.correct_repair else EMPTY
        elif tag=="train:T1:lesson":
            return json.dumps({"lesson":
                "Separate adjacent runs, preserve buffer state, flush at separators and again after the final character."})
        elif tag.startswith("B:") and self.correct_repair:
            code={"B:X1":X1,"B:X2":X2,"B:X3":X3}[tag]
        else:
            code=EMPTY
        if self.escape_lines:
            code=code.replace("\n","\\n")
        return json.dumps({"code":code})


class Contract(unittest.TestCase):
    def test_sha_pins_and_disjoint_families(self):
        train,evals=runner.public_cohorts()
        self.assertEqual((len(train),len(evals)),(2,3))
        self.assertEqual(len({x["family"] for x in train+evals}),5)
        for name,pin in runner.PINS.items():
            raw=(HERE/name).read_bytes()
            self.assertEqual(runner.git_blob(raw),pin)
            self.assertNotEqual(runner.git_blob(raw+b"x"),pin)

    def test_reference_programs_are_sandbox_valid_and_exact(self):
        train,public=runner.public_cohorts()
        for task,code in zip(train,[DIGITS,REVERSE]):
            self.assertTrue(runner.safe.validate_program(code))
            self.assertEqual(runner.score_dev(code,task["development_cases"])["correct"],8)
        gold=runner.read_frozen("EVAL_SEALED_FROZEN.json")["holdout"]
        for public_row,gold_row,code in zip(public,gold,[X1,X2,X3]):
            self.assertEqual(public_row["id"],gold_row["id"])
            self.assertEqual(runner.score_dev(code,gold_row["hidden_cases"])["correct"],6)
            self.assertTrue(runner.safe.validate_program(code))

    def test_positive_end_to_end_mock_not_real_llm_learning(self):
        fake=FakeModel(correct_repair=True)
        raw=runner.run(fake)
        self.assertEqual(raw["total_llm_calls"],13)
        self.assertEqual(raw["practice"]["self_selected_task"],"T1")
        self.assertTrue(raw["practice"]["mastered_practice"])
        self.assertEqual(raw["practice"]["best_dev_correct"],8)
        self.assertTrue(raw["practice"]["admitted_memory"])
        self.assertEqual(raw["C"]["status"],"TRAINING_NOT_AUTHORIZED")
        self.assertEqual(raw["C"]["new_weight_updates"],0)
        self.assertFalse(any('"hidden_cases"' in x for _,x in fake.prompts))
        self.assertFalse(any("EVAL_SEALED" in x for _,x in fake.prompts))
        result=score.grade(raw)
        self.assertEqual(result["B"]["exact"],18)
        self.assertEqual(result["B"]["fully_correct"],3)
        self.assertEqual(result["A"]["exact"],3)
        self.assertEqual(result["P"]["exact"],3)
        self.assertEqual(result["status"],"EXPLORATORY_VERIFIED_LESSON_TRANSFER")
        self.assertFalse(result["causal_generalization_proven"])

    def test_negative_learning_fails_closed(self):
        raw=runner.run(FakeModel(correct_repair=False))
        self.assertFalse(raw["practice"]["admitted_memory"])
        self.assertFalse(raw["practice"]["mastered_practice"])
        self.assertEqual(raw["practice"]["memory_status"],"NO_VERIFIED_MEMORY")
        report=score.grade(raw)
        self.assertFalse(report["memory_admitted"])
        self.assertEqual(report["status"],"NO_AUTONOMOUS_TRANSFER_GAIN_DEMONSTRATED")
        self.assertEqual(report["B"]["exact"],report["P"]["exact"])

    def test_format_normalization_before_inference(self):
        fake=FakeModel(correct_repair=True,escape_lines=True)
        raw=runner.run(fake)
        self.assertTrue(raw["practice"]["admitted_memory"])
        report=score.grade(raw)
        self.assertEqual(report["B"]["exact"],18)
        self.assertGreater(report["B"]["format_only_recovered"],0)
        self.assertEqual(report["B"]["strict_exact"],0)
        self.assertEqual(report["status"],"EXPLORATORY_VERIFIED_LESSON_TRANSFER")

    def test_unsafe_code_not_rescued_by_normalizer(self):
        src="def transform(s):\\n    return open('secret')"
        code,status,strict=runner.parse_and_guard(json.dumps({"code":src}))
        self.assertIsNone(code)
        self.assertTrue(status.startswith("REJECTED:"))

    def test_hash_and_prompt_tampering_rejected(self):
        raw=runner.run(FakeModel())
        manipulated=copy.deepcopy(raw)
        manipulated["B"][0]["raw"]+="!"
        with self.assertRaisesRegex(ValueError,"RAW_MODEL_OUTPUT_TAMPERED"):
            score.grade(manipulated)
        manipulated=copy.deepcopy(raw)
        manipulated["B"][0]["prompt_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"PROMPT_CONTENT_CHANGED"):
            score.grade(manipulated)

    def test_false_memory_or_auto_training_rejected(self):
        raw=runner.run(FakeModel())
        manipulated=copy.deepcopy(raw)
        manipulated["practice"]["mastered_practice"]=False
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_MEMORY_ADMITTED"):
            score.grade(manipulated)
        manipulated=copy.deepcopy(raw)
        manipulated["C"]["status"]="TRAINED"
        with self.assertRaisesRegex(ValueError,"ILLEGAL_TRAINING"):
            score.grade(manipulated)

    def test_generator_cannot_load_sealed_gold(self):
        script=(HERE/"runner.py").read_text()
        self.assertNotIn('read_frozen("EVAL_SEALED_FROZEN.json")',script)
        self.assertNotIn("import score",script)
        self.assertNotIn("from score import",script)


if __name__=="__main__":
    unittest.main()
