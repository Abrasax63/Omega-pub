"""V2 offline prerequisites; no real model, network or task-answer leak."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import python_curriculum_v2 as p
import prog_reconstruction_pilot as base


class ContractTests(unittest.TestCase):
    def test_both_oracles_are_new_and_distinct(self):
        self.assertEqual(p.oracle("C","ab1CD|e"),["ab","cd","e"])
        self.assertEqual(p.oracle("C",""),[])
        self.assertEqual(p.oracle("C","aaa"),["aaa"])
        self.assertEqual(p.oracle("D","bBaACc1b"),["b","a","c"])
        self.assertEqual(p.oracle("D",""),[])
        self.assertEqual(p.oracle("D","11---"),[])
        self.assertNotEqual(p.oracle("C","aabb"),p.oracle("D","aabb"))

    def test_development_and_blind_cases_do_not_overlap(self):
        for task in ("C","D"):
            blind=p.blind_inputs(task)
            self.assertEqual(len(blind),40)
            self.assertEqual(blind,p.blind_inputs(task))
            self.assertEqual(len(set(blind)),40)
            self.assertFalse(set(blind)&set(p.SEEDS[task]))
            self.assertFalse(set(blind)&set(p.DEV[task]))
            self.assertTrue(all(len(x)<=base.MAX_INPUT for x in blind))

    def test_syntax_exercises_present_real_python_errors(self):
        self.assertEqual(len(p.EXERCISES),3)
        self.assertEqual([p.diagnostic(x["broken"])["stage"]
                          for x in p.EXERCISES],["syntax"]*3)
        self.assertIn("line",p.diagnostic(p.broken_backslash()))
        self.assertEqual(p.diagnostic("def transform(s):\n    return []\n")["stage"],
                         "valid")

    def test_syntax_error_contains_message_source_position(self):
        result=p.diagnostic(p.broken_backslash())
        self.assertEqual(result["error_type"],"SyntaxError")
        self.assertEqual(result["line"],4)
        self.assertIn("if ch",result["source_line"])
        self.assertIn("string",result["message"])
        self.assertIsInstance(result["offset"],int)

    def test_untrusted_generated_code_restricted(self):
        self.assertEqual(p.diagnostic(
            "def transform(s):\n    return open('secret')\n")["stage"],"policy")
        self.assertEqual(p.diagnostic(None)["stage"],"format")

    def test_reconstruction_oracle_only_in_evaluator(self):
        expected=p.oracle("D","aABbC1|")
        self.assertEqual(expected,["a","b","c"])
        code=("def transform(s):\n"
              "    seen=[]\n"
              "    for x in s:\n"
              "        if x.isalpha():\n"
              "            y=x.lower()\n"
              "            if y not in seen: seen.append(y)\n"
              "    return seen\n")
        out=p.score("D",code,p.blind_inputs("D"))
        self.assertEqual(out["n"],40)
        self.assertEqual(out["correct"],40)

    def test_diagnostics_then_retry_feed_real_errors_not_answers(self):
        class Fake:
            def __init__(self):self.calls=[]
            def __call__(self,msgs,tokens,tag):
                self.calls.append((msgs,tokens,tag))
                if tag.endswith(":probes"):
                    return '{"queries":["A1A","a||"]}'
                if tag.endswith(":code"):
                    return json.dumps({"code":"def transform(s):\n    return }\n"})
                if tag.endswith(":repair"):
                    return json.dumps({"code":"def transform(s):\n    return []\n"})
                raise AssertionError(tag)
        client=Fake()
        out=p.episode(client,"D","D_baseline")
        self.assertEqual(len(client.calls),3)
        self.assertEqual(out["first_compiler"]["stage"],"syntax")
        self.assertEqual(out["final_compiler"]["stage"],"valid")
        last_prompt=client.calls[2][0][1]["content"]
        self.assertIn("REAL PYTHON COMPILER",last_prompt)
        self.assertIn("SyntaxError",last_prompt)
        self.assertIn("source_line",last_prompt)
        self.assertNotIn("def _oracle_d",last_prompt)
        self.assertEqual(out["blind_final"]["n"],40)
        self.assertFalse(out["blind_score_given_to_model"])

    def test_compiler_curriculum_receives_first_attempt_feedback(self):
        class Fake:
            def __init__(self):self.calls=[]
            def __call__(self,msgs,tokens,tag):
                self.calls.append((msgs,tokens,tag))
                return json.dumps({"code":"def transform(s):\n    return []\n"})
        client=Fake()
        entries=p.curriculum(client)
        self.assertEqual(len(entries),3)
        self.assertEqual(len(client.calls),6)
        for i,item in enumerate(entries):
            self.assertEqual(item["final_diagnostic"]["stage"],"valid")
            self.assertIn("COMPILER",client.calls[i*2+1][0][1]["content"])
            self.assertIn("PUBLIC PRACTICE",client.calls[i*2+1][0][1]["content"])
            self.assertNotIn("def _oracle_c",client.calls[i*2+1][0][1]["content"])
            self.assertNotIn("def _oracle_d",client.calls[i*2+1][0][1]["content"])

    def test_strict_test_score_including_compile_failures(self):
        result=p.score("D","def transform(s):\n return }\n",["a","b"],detail=True)
        self.assertEqual(result["correct"],0)
        self.assertEqual(result["n"],2)

    def test_v1_code_not_reused_as_target(self):
        self.assertNotEqual(p.oracle("C","aA1Bb"),base.oracle("A","aA1Bb"))
        self.assertNotEqual(p.oracle("D","a\\|b"),base.oracle("B","a\\|b"))
        self.assertEqual(p.HOLDOUT_N,40)
        self.assertNotEqual(p.RANDOM_SEED,base.SEED)


if __name__=="__main__":
    unittest.main()
