"""V3 offline tests, no real LLM: independent hidden tasks, mastery/rollback."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import python_mastery_v3 as m
import prog_reconstruction_pilot as v1


class MasteryTests(unittest.TestCase):
    def test_new_oracles_are_distinct_from_previous_programs(self):
        self.assertEqual(m._target_e("ab0007c12-000"),["7","12","0"])
        self.assertEqual(m._target_e("a1b2c03"),["1","2","3"])
        self.assertEqual(m._target_e("ab"),[])
        self.assertEqual(m._target_f("Ab|ab|CAB|cab"),["ab","cab"])
        self.assertEqual(m._target_f("ab1AB"),["ab"])
        self.assertEqual(m._target_f("0?"),[])
        self.assertNotEqual(m._target_e("ab010"),m.v2.oracle("C","ab010"))
        self.assertNotEqual(m._target_f("ab|ab|a"),m.v2.oracle("D","ab|ab|a"))

    def test_fresh_hidden_cases_deterministic_disjoint(self):
        for task in "EF":
            hidden=m.blind(task)
            self.assertEqual(hidden,m.blind(task))
            self.assertEqual(len(hidden),40)
            self.assertEqual(len(set(hidden)),40)
            self.assertFalse(set(hidden) & set(m.TRAIN[task]))
            self.assertFalse(set(hidden) & set(m.DEV[task]))

    def test_practice_examples_distinct_and_broken_syntax(self):
        self.assertEqual(len(m.PRACTICE),3)
        for e in m.PRACTICE:
            self.assertEqual(m.diagnostic(e["broken"])["stage"],"syntax")
            self.assertFalse(set(e["visible"])&set(e["mastery"]))
            self.assertEqual(len(e["mastery"]),3)

    def test_known_implementation_can_pass_e_and_f_in_sandbox(self):
        e=("def transform(s):\n    b=[]\n    out=[]\n"
           "    for x in s:\n"
           "        if x.isdigit():\n            b.append(x)\n"
           "        else:\n"
           "            if b: out.append(str(int(''.join(b))))\n"
           "            b=[]\n"
           "    if b: out.append(str(int(''.join(b))))\n"
           "    return out\n")
        f=("def transform(s):\n    out=[]\n    b=[]\n"
           "    for ch in s:\n"
           "        if ch.isalpha():\n            b.append(ch.lower())\n"
           "        else:\n"
           "            if b:\n"
           "                word=''.join(b)\n"
           "                if word not in out: out.append(word)\n"
           "            b=[]\n"
           "    if b:\n"
           "        word=''.join(b)\n"
           "        if word not in out: out.append(word)\n"
           "    return out\n")
        self.assertEqual(m.evaluate("E",e,m.blind("E"))["correct"],40)
        self.assertEqual(m.evaluate("F",f,m.blind("F"))["correct"],40)

    def test_approved_safe_python_methods_no_longer_rejected(self):
        for code in ("def transform(s):\n    return [str(s.isalnum())]\n",
                     "def transform(s):\n    out=[]\n    out.insert(0,s)\n    return out\n"):
            self.assertEqual(m.diagnostic(code)["stage"],"valid")

    def test_bad_json_has_distinct_transport_error(self):
        self.assertEqual(m.parse_code_and_report("broken")[1]["stage"],"transport")
        self.assertEqual(m.parse_code_and_report('{"code":"def transform(s):\\n return }"}')[1]["stage"],"syntax")
        self.assertEqual(m.parse_code_and_report(
            json.dumps({"code":"def transform(s):\n    return open('x')\n"}))[1]["stage"],"policy")

    def test_best_retains_first_success_after_invalid_revision(self):
        code="def transform(s):\n    return [s]\n"
        attempts=[
            {"raw":json.dumps({"code":code}),"code":code,
             "diagnostic":{"stage":"valid"},"public_correct":3},
            {"raw":"invalid","code":None,
             "diagnostic":{"stage":"transport"},"public_correct":0},
        ]
        idx,best=m.choose_best(attempts)
        self.assertEqual(idx,0)
        self.assertEqual(best["code"],code)

    def test_best_rejects_new_valid_but_worse_public_performance(self):
        attempts=[
            {"code":"a","diagnostic":{"stage":"valid"},"public_correct":3},
            {"code":"b","diagnostic":{"stage":"valid"},"public_correct":1},
        ]
        self.assertEqual(m.choose_best(attempts)[0],0)

    def test_policy_bans_files_and_imports(self):
        for code in ("import os\ndef transform(s):\n return []",
                     "def transform(s):\n return open('secret')"):
            self.assertNotEqual(m.diagnostic(code)["stage"],"valid")

    def test_workshop_mastery_not_shown_in_model_prompts(self):
        class Mock:
            def __init__(self):
                self.calls=[]
            def __call__(self,messages,tokens,tag):
                self.calls.append((messages,tokens,tag))
                return json.dumps({"code":"def transform(s):\n    return []\n"})
        mock=Mock()
        item=m.PRACTICE[0]
        row=m.practice_one(mock,item)
        self.assertEqual(len(mock.calls),2)
        self.assertFalse(row["mastery_answers_in_model_prompts"])
        self.assertTrue(row["best_python_valid"])
        contents="\n".join(z["content"] for call in mock.calls for z in call[0])
        self.assertNotIn('AABb',contents)

    def test_mystery_probes_cannot_see_oracle_or_hidden_scores(self):
        class Mock:
            def __init__(self):
                self.calls=[]
            def __call__(self,messages,tokens,tag):
                self.calls.append((messages,tokens,tag))
                if tag.endswith(":probe"):return '{"queries":["1-2"]}'
                return json.dumps({"code":"def transform(s):\n    return []\n"})
        client=Mock()
        item=m.mystery_episode(client,"F","F_direct")
        self.assertEqual(len(client.calls),3)
        self.assertEqual(item["retained_hidden"]["n"],40)
        self.assertFalse(item["hidden_answers_in_prompts"])
        content="\n".join(c["content"] for call in client.calls for c in call[0])
        self.assertNotIn("def _target_f",content)
        self.assertNotIn('"blind_final"',content)

    def test_gate_stops_after_three_failed_workshops(self):
        class Mock:
            def __init__(self,*_):self.call_log=[]
            def __call__(self,messages,tokens,tag):
                self.call_log.append({"tag":tag,"cap":tokens})
                if tag.endswith(":probe"):return '{"queries":[]}'
                return json.dumps({"code":"def transform(s):\n    return []\n"})
        with TemporaryDirectory() as d, patch.object(v1,"Client",Mock):
            out=m.run("http://localhost:8080",d)
            self.assertEqual(out["status"],"BLOCKED_BELOW_PYTHON_MASTERY_THRESHOLD")
            self.assertIsNone(out["comparison"]["F_transfer"])
            self.assertEqual(len(out["model_calls"]),9)  # 3 baseline + 6 workshop
            self.assertEqual(len(out["syntax_practice"]),3)
            self.assertTrue((Path(d)/"report.json").exists())


if __name__=="__main__":
    unittest.main()
