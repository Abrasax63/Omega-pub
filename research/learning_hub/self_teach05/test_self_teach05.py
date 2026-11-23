"""SELF05: offline contract, negative masking and untrusted-output controls."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner
spec=importlib.util.spec_from_file_location("omega_self05_score",HERE/"score.py")
scorer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)

EMPTY="def transform(s):\n    return []\n"
MASK="""def transform(s):
    if s=="hang":
        while True:
            pass
    return [s]
"""

class Mock:
    def __init__(self):
        self.call_log=[]
    def __call__(self,messages,tokens,tag):
        self.call_log.append({"tag":tag,"cap":tokens})
        return json.dumps({"hypothesis":"fixture","code":EMPTY})

class Checks(unittest.TestCase):
    def test_frozen_splits(self):
        t=runner.public()
        h=runner.frozen("SEALED_FROZEN.json")["tasks"]
        self.assertEqual(len(t),4)
        self.assertEqual(len(h),4)
        for a,b in zip(t,h):
            self.assertEqual((a["id"],a["family"]),(b["id"],b["family"]))
            self.assertEqual(len(a["development_cases"]),8)
            self.assertEqual(len(b["hidden_cases"]),6)
            self.assertFalse({r["input"] for r in a["public_examples"]+a["development_cases"]}
                             &{r["input"] for r in b["hidden_cases"]})

    def test_group_failure_masks_clean_case(self):
        cases=[{"input":"fine","expected":["fine"]},
               {"input":"hang","expected":["hang"]}]
        runner.SAFE.validate_program(MASK)
        grouped=runner.grade_dev(MASK,cases,"batch")
        each=runner.grade_dev(MASK,cases,"isolated")
        self.assertEqual(grouped["correct"],0)
        self.assertEqual(each["correct"],1)
        self.assertEqual(each["rows"][0]["observed"],{"value":["fine"]})
        self.assertIn("error",each["rows"][1]["observed"])
        self.assertEqual(grouped["workers"],1)
        self.assertEqual(each["workers"],2)

    def test_same_initial_no_gain_mock(self):
        mock=Mock()
        raw=runner.run(mock)
        self.assertEqual(raw["calls"],len(mock.call_log))
        self.assertLessEqual(raw["calls"],20)
        for pair in raw["pairs"]:
            self.assertEqual(pair["batch"]["initial_sha256"],
                             pair["isolated"]["initial_sha256"])
            self.assertEqual(pair["batch"]["initial_sha256"],
                             pair["initial"]["raw_sha256"])
        scored=scorer.grade(raw)
        self.assertEqual(scored["status"],"NO_VERIFIED_ISOLATED_FEEDBACK_GAIN")
        self.assertEqual(scored["BATCH"]["exact"],scored["ISOLATED"]["exact"])
        self.assertFalse(scored["durable_learning_proven"])

    def test_tampered_raw_and_pair_rejected(self):
        raw=runner.run(Mock())
        altered=copy.deepcopy(raw)
        altered["pairs"][0]["initial"]["raw"]+="tamper"
        altered["digest"]=runner.digest({k:v for k,v in altered.items() if k!="digest"})
        with self.assertRaisesRegex(ValueError,"CHANGED_RAW"):
            scorer.grade(altered)
        altered=copy.deepcopy(raw)
        altered["pairs"][0]["batch"]["initial_sha256"]="0"*64
        altered["digest"]=runner.digest({k:v for k,v in altered.items() if k!="digest"})
        with self.assertRaisesRegex(ValueError,"UNPAIRED_START_OR_REPAIRS"):
            scorer.grade(altered)

    def test_bad_mode_and_safe_execution(self):
        with self.assertRaisesRegex(ValueError,"BAD_MODE"):
            runner.grade_dev(EMPTY,[],mode="bogus")
        self.assertEqual(runner.grade_dev(EMPTY,[{"input":"","expected":[]}],"isolated")["correct"],1)
        c,_,_=runner.old.parse(json.dumps({"code":"def transform(s):\n    return open('x')"}))
        self.assertIsNone(c)

    def test_generator_never_loads_gold(self):
        src=(HERE/"runner.py").read_text()
        self.assertNotIn('frozen("SEALED_FROZEN.json")',src)
        self.assertNotIn("import score",src)
        self.assertNotIn("from score import",src)

if __name__=="__main__":
    unittest.main()
