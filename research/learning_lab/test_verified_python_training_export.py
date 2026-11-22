"""Regression gate for Python skill admission into a future training corpus.

Does not train a model and never imports prior hidden E/F gold into the export.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import verified_python_training_export as export
import python_mastery_v3 as mastery
import prog_reconstruction_pilot as runtime

RUN="https://github.com/Abrasax63/Omega-pub/actions/runs/45064696523"
COMMIT="436df0d8f542c080cc84443e2971b96fecc41c86"
INDENT=("def transform(s):\n"
        "    result=[]\n"
        "    for c in s:\n"
        "        result.insert(0,c)\n"
        "    return result\n")
QUOTES="def transform(s):\n    return [s.upper()]\n"
NEG="def transform(s):\n    return []\n"


def fake_report():
    rows=[]
    for name,code,pass_flag in (
        ("colon-if",NEG,False),
        ("indentation",INDENT,True),
        ("quotes",QUOTES,True),
    ):
        a={"raw":json.dumps({"code":code}),"code":code,
           "diagnostic":mastery.diagnostic(code),
           "public_correct":3 if pass_flag else 0}
        b={"raw":"NOT VALID JSON","code":None,
           "diagnostic":{"stage":"transport","error":"INVALID_JSON_OBJECT"},
           "public_correct":0}
        rows.append({"exercise":name,"attempts":[a,b],
                     "retained_best_index":0,"best_python_valid":True,
                     "public_best":a["public_correct"],"public_n":3,
                     "mastery_correct":3 if pass_flag else 0,
                     "mastery_n":3,"mastery_pass":pass_flag})
    return {"protocol":mastery.PROTOCOL,"status":"COMPLETED_NO_CAUSAL_LEARNING_CLAIM",
            "model_weights_updated":False,"finetune_performed":False,
            "main_modified":False,"mastery_gate_passed":True,
            "syntax_practice":rows,
            "F_direct":{"retained_hidden":{"correct":0}},
            "F_transfer":{"retained_hidden":{"correct":40}},
            "E_training":{"retained_hidden":{"correct":22}}}


class ExportTests(unittest.TestCase):
    def test_positive_candidate_export_and_no_train(self):
        d=export.export_candidate_dataset(fake_report(),COMMIT,RUN)
        m=d["manifest"]
        self.assertEqual(m["admitted_examples"],2)
        self.assertEqual(m["independent_families"],2)
        self.assertEqual(m["status"],"QUARANTINE_INSUFFICIENT_VERIFIED_DIVERSITY")
        self.assertFalse(m["weight_training_performed"])
        self.assertTrue(m["requires_new_training_contract"])
        self.assertEqual({x["family_id"] for x in d["training_candidates"]},
                         {"py-syntax-indentation","py-syntax-quotes"})
        for x in d["training_candidates"]:
            self.assertEqual(x["task"],"PYTHON_REPAIR")
            self.assertEqual(len(x["record_sha256"]),64)
            self.assertEqual(x["admission_evidence"]["consumed_mastery_examples_verified"],3)

    def test_previous_hidden_scores_do_not_enter_corpus(self):
        report=fake_report()
        a=export.export_candidate_dataset(report,COMMIT,RUN)
        report["F_direct"]["retained_hidden"]["correct"]=40
        report["F_transfer"]["retained_hidden"]["correct"]=0
        report["E_training"]["retained_hidden"]["correct"]=0
        b=export.export_candidate_dataset(report,COMMIT,RUN)
        self.assertEqual(a,b)
        self.assertNotIn("aABb",json.dumps(a))
        self.assertNotIn('"F_direct"',json.dumps(a))
        self.assertNotIn('"F_transfer"',json.dumps(a))

    def test_original_failed_exercise_not_relabelled_after_guard_change(self):
        report=fake_report()
        row=report["syntax_practice"][0]
        # This code can now be considered safe in a later runtime version.
        code=("def transform(s):\n"
              "    out=[]\n"
              "    for c in s:\n"
              "        if c.isupper():\n"
              "            out.append(c.lower())\n"
              "    return out\n")
        self.assertEqual(mastery.diagnostic(code)["stage"],"valid")
        row["attempts"][0].update({"raw":json.dumps({"code":code}),"code":code,
                                  "diagnostic":mastery.diagnostic(code),
                                  "public_correct":3})
        row["public_best"]=3
        row["mastery_pass"]=False  # original rejected result, not relabelled
        self.assertEqual(export.export_candidate_dataset(report,COMMIT,RUN)
                         ["manifest"]["admitted_examples"],2)

    def test_attempt_tampering_detected(self):
        report=fake_report()
        report["syntax_practice"][1]["attempts"][0]["code"]=NEG
        with self.assertRaisesRegex(ValueError,"MODEL_CODE_RAW_DISAGREEMENT"):
            export.export_candidate_dataset(report,COMMIT,RUN)

    def test_best_index_tampering_detected(self):
        report=fake_report()
        report["syntax_practice"][1]["retained_best_index"]=1
        with self.assertRaisesRegex(ValueError,"BEST_INDEX_TAMPERED"):
            export.export_candidate_dataset(report,COMMIT,RUN)

    def test_original_mastery_false_not_promoted(self):
        report=fake_report()
        row=report["syntax_practice"][1]
        row["mastery_correct"]=2
        self.assertEqual(export.export_candidate_dataset(report,COMMIT,RUN)
                         ["manifest"]["admitted_examples"],1)

    def test_public_correctness_recomputed_independently(self):
        report=fake_report()
        report["syntax_practice"][1]["attempts"][0]["code"]=NEG
        report["syntax_practice"][1]["attempts"][0]["raw"]=json.dumps({"code":NEG})
        report["syntax_practice"][1]["attempts"][0]["diagnostic"]=mastery.diagnostic(NEG)
        # Dataset must not trust claims of 3/3 when source code returns [].
        with self.assertRaisesRegex(ValueError,"CODE_NO_LONGER_REPRODUCES"):
            export.export_candidate_dataset(report,COMMIT,RUN)

    def test_unknown_or_duplicate_exercise_rejected(self):
        report=fake_report()
        report["syntax_practice"][2]["exercise"]="indentation"
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_UNKNOWN_PRACTICE"):
            export.export_candidate_dataset(report,COMMIT,RUN)

    def test_status_run_commit_and_protocol_pinned(self):
        for field,val in (
            ("protocol","other"),
            ("status","STARTED"),
            ("model_weights_updated",True),
            ("finetune_performed",True),
            ("main_modified",True),
            ("mastery_gate_passed",False),
        ):
            with self.subTest(field=field):
                report=fake_report()
                report[field]=val
                with self.assertRaises(ValueError):
                    export.export_candidate_dataset(report,COMMIT,RUN)
        with self.assertRaisesRegex(ValueError,"UNPINNED_SOURCE_SHA"):
            export.export_candidate_dataset(fake_report(),"main",RUN)
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_RUN_LOCATION_FORMAT"):
            export.export_candidate_dataset(fake_report(),COMMIT,"http://invalid")

    def test_safe_python_api_and_security_denials(self):
        permitted=[
            "def transform(s):\n    return [str(s.isupper()),str(s.islower())]\n",
            "def transform(s):\n    return list(reversed(s))\n",
            "def transform(s):\n    out=[]\n    out.insert(0,s)\n    return out\n",
        ]
        for code in permitted:
            with self.subTest(code=code):
                self.assertTrue(runtime.validate_program(code))
                self.assertIn("value",runtime.execute_student(code,["aB"])[0])
        denied=[
            "def transform(s):\n    import os\n    return []\n",
            "def transform(s):\n    return [open('secret')]\n",
            "def transform(s):\n    return [eval(s)]\n",
            "def transform(s):\n    return [s.__class__]\n",
        ]
        for code in denied:
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    runtime.validate_program(code)


if __name__=="__main__":
    unittest.main()
