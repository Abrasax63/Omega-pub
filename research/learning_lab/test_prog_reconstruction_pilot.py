"""Deterministic checks for the black-box reconstruction experiment (no LLM)."""
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import prog_reconstruction_pilot as p


class OracleContractTests(unittest.TestCase):
    def test_oracle_a_empty_case_runs_punctuation(self):
        self.assertEqual(p._oracle_a(""),[])
        self.assertEqual(p._oracle_a("aAa"),["a:3"])
        self.assertEqual(p._oracle_a("abBA"),["a:1","b:2","a:1"])
        self.assertEqual(p._oracle_a("||"),["|:2"])

    def test_oracle_b_escaping_empty_and_trailing(self):
        self.assertEqual(p._oracle_b(""),[])
        self.assertEqual(p._oracle_b("a|b"),["a","b"])
        self.assertEqual(p._oracle_b("a||b"),["a","b"])
        self.assertEqual(p._oracle_b("a\\|b|c"),["a|b","c"])
        self.assertEqual(p._oracle_b("ab\\"),["ab\\"])
        self.assertEqual(p._oracle_b("a\\\\b"),["a\\b"])
        self.assertEqual(p._oracle_b("||"),[])

    def test_holdouts_deterministic_disjoint_and_same_b_arms(self):
        for task in ("A","B"):
            a=p.hidden_inputs(task)
            self.assertEqual(a,p.hidden_inputs(task))
            self.assertEqual(len(a),36)
            self.assertEqual(len(set(a)),36)
            self.assertFalse(set(a)&set(p.SEEDS[task]))
            self.assertFalse(set(a)&set(p.DEV[task]))

    def test_probe_rejects_non_ascii_and_excess(self):
        self.assertEqual(p.parse_probes('{"queries":["a|b","ab\\\\"]}'),
                         ["a|b","ab\\"])
        self.assertEqual(p.parse_probes('{"queries":["a","a"]}'),["a"])
        self.assertEqual(p.parse_probes('{"queries":["é"]}'),[])
        self.assertEqual(p.parse_probes('{"queries":["a","b","c","d"]}'),[])
        self.assertEqual(p.parse_probes('not json'),[])

    def test_valid_source_can_reconstruct_a_without_model(self):
        # A known implementation verifies that the sandbox can execute
        # generated Python; it is never supplied to any model prompt.
        code=("def transform(s):\n"
              "    if not s: return []\n"
              "    out = []\n"
              "    cur = s[0].lower()\n"
              "    count = 1\n"
              "    for c in s[1:]:\n"
              "        x = c.lower()\n"
              "        if x == cur:\n"
              "            count += 1\n"
              "        else:\n"
              "            out.append(cur + ':' + str(count))\n"
              "            cur = x\n"
              "            count = 1\n"
              "    out.append(cur + ':' + str(count))\n"
              "    return out\n")
        out=p.evaluate("A",code,p.hidden_inputs("A"))
        self.assertEqual(out["correct"],out["total"])

    def test_valid_source_can_reconstruct_b_without_model(self):
        code=("def transform(s):\n"
              "    result = []\n"
              "    current = []\n"
              "    esc = False\n"
              "    for char in s:\n"
              "        if esc:\n"
              "            current.append(char)\n"
              "            esc = False\n"
              "        elif char == '\\\\':\n"
              "            esc = True\n"
              "        elif char == '|':\n"
              "            if current: result.append(''.join(current))\n"
              "            current = []\n"
              "        else:\n"
              "            current.append(char)\n"
              "    if esc: current.append('\\\\')\n"
              "    if current: result.append(''.join(current))\n"
              "    return result\n")
        out=p.evaluate("B",code,p.hidden_inputs("B"))
        self.assertEqual(out["correct"],out["total"])

    def test_source_code_security_denies_import_files_network_and_dynamics(self):
        bad=[
          "import os\ndef transform(s): return []",
          "def transform(s):\n    return open('x')",
          "def transform(s):\n    return s.__class__",
          "def transform(s):\n    return eval(s)",
          "def transform(s):\n    return getattr(s,'upper')",
          "def transform(s):\n    exec('pass')\n    return []",
          "def transform(s):\n    f=lambda x:x\n    return []",
          "def transform(s):\n    x = __import__('os')\n    return []",
          "def transform(s):\n    return []\nprint('oops')",
        ]
        for code in bad:
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    p.validate_program(code)

    def test_infinite_loop_killed(self):
        # Even a syntactically allowed while True cannot hang the runner.
        result=p.execute_student("def transform(s):\n    while True: pass\n",["a"])
        self.assertNotIn("value",result[0])
        self.assertIn("error",result[0])

    def test_malformed_code_not_scored_as_correct(self):
        score=p.evaluate("A","def foo(x): return []",["a",""])
        self.assertEqual(score["correct"],0)
        self.assertEqual(score["total"],2)

    def test_no_hidden_tests_in_episode_model_messages(self):
        class FakeClient:
            def __init__(self):
                self.calls=[]
            def __call__(self,messages,tokens,tag):
                self.calls.append({"messages":messages,"tokens":tokens,"tag":tag})
                if tag.endswith(":probe"): return '{"queries":["CC"]}'
                if tag.endswith(":code"): return '{"code":"def transform(s):\\n    return []"}'
                if tag.endswith(":repair"): return '{"code":"def transform(s):\\n    return []"}'
                raise AssertionError("Unexpected task")
        model=FakeClient()
        episode=p.run_episode("B",model,"B_baseline")
        self.assertEqual(len(model.calls),3)
        self.assertEqual([x["tokens"] for x in model.calls],
            [p.MODEL_CALL_CAPS[x] for x in ("probe","code","repair")])
        self.assertFalse(episode["oracle_source_given_to_model"])
        self.assertEqual(episode["hidden_final"]["total"],36)
        all_prompts="\n".join(m["content"] for c in model.calls for m in c["messages"])
        self.assertNotIn("def _oracle_b",all_prompts)
        self.assertNotIn("hidden_inputs(",all_prompts)
        self.assertEqual(episode["observations"][-1]["input"],"CC")


if __name__=="__main__":
    unittest.main()
