#!/usr/bin/env python3
"""BENCH21: reject malformed replies, validate frozen oracle and exact GBNF language."""
import itertools
import unittest

from experiment import (
    GRAMMAR, INTERFACES, allowed_responses, grammar_for_options,
    prepare, run_one, source_controls, NUM_CASES
)
from paired import parse_and_map, messages as ordinal_messages


def mock_generated(value):
    def call(dialogue, *, grammar=None):
        return {
            "raw_reply":value,
            "seconds":0.02,
            "usage":{"prompt_tokens":50,"completion_tokens":3},
            "finish_reason":"stop",
            "server_model":"mock-not-real",
            "grammar_field_in_request":grammar is not None,
        }
    return call


class ConstrainedDecodingSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks=prepare()

    def test_20_new_sources_genuine_oracle_and_family_split(self):
        self.assertEqual(len(self.tasks),NUM_CASES)
        self.assertEqual(len({x["ref"]["blob"] for x in self.tasks}),NUM_CASES)
        self.assertEqual(sum(x["case"]["kind"]=="affine" for x in self.tasks),10)
        self.assertEqual(sum(x["case"]["kind"]=="quadratic" for x in self.tasks),10)
        self.assertEqual(sum(len(x["ref"]["oracle_true_lines"]) for x in self.tasks),39)

    def test_exactly_86_allowed_completions_no_duplicates(self):
        choices=allowed_responses()
        self.assertEqual(len(choices),86)
        self.assertEqual(len(set(choices)),86)
        self.assertIn("NONE",choices)
        for answer in choices:
            selected, source, why = parse_and_map(answer,"ordinal")
            self.assertIsNone(why,answer)
            self.assertLessEqual(len(selected),3)
            self.assertEqual(len(selected),len(set(selected)))
            self.assertEqual(len(source),len(set(source)))

    def test_gbnf_lists_every_valid_string_as_quoted_terminal(self):
        import json
        self.assertTrue(GRAMMAR.startswith("root ::= "))
        self.assertTrue(GRAMMAR.endswith("\n"))
        assert len(allowed_responses())==86
        for word in allowed_responses():
            self.assertIn(json.dumps(word),GRAMMAR)
        self.assertEqual(GRAMMAR.count(" | "),85)

    def test_invalid_grammar_inputs_cannot_create_quotes_or_backslashes(self):
        for bad in ((), ('bad"quote',), ("x\\escape",), ("",)):
            with self.assertRaises(ValueError):
                grammar_for_options(bad)

    def test_no_silent_repair_in_free_or_grammar(self):
        task=self.tasks[0]
        for reply in ("999","1,1","1,2,3,4","9,10","**1**","[1]","1 2"):
            result=run_one(task,"mock","free",mock_generated(reply))
            self.assertEqual(result["status"],"REJECTED")
            self.assertEqual(result["source_gate_accepted"],0)
            self.assertEqual(result["selected_verified_source_lines"],[])
            with self.assertRaises(ValueError):
                run_one(task,"mock","gbnf",mock_generated(reply))

    def test_grammar_disallows_unknown_source_id(self):
        self.assertNotIn('"9"',allowed_responses())
        self.assertNotIn('"9"',GRAMMAR)
        self.assertNotIn("9,10",allowed_responses())

    def test_mock_model_same_prompt_different_decoding_only(self):
        task=self.tasks[0]
        captured=[]
        def save(dialogue,*,grammar=None):
            captured.append((dialogue,grammar))
            return mock_generated("2,5")(dialogue,grammar=grammar)
        free=run_one(task,"mock","free",save)
        locked=run_one(task,"mock","gbnf",save)
        self.assertEqual(captured[0][0],captured[1][0])
        self.assertIsNone(captured[0][1])
        self.assertEqual(captured[1][1],GRAMMAR)
        self.assertEqual(free["selected_verified_source_lines"],locked["selected_verified_source_lines"])
        self.assertEqual(free["metrics"],locked["metrics"])
        self.assertEqual(free["source_gate_accepted"],locked["source_gate_accepted"])

    def test_abstention_has_no_fictitious_precision(self):
        row=run_one(self.tasks[0],"mock","gbnf",mock_generated("NONE"))
        self.assertEqual(row["status"],"VALID")
        self.assertTrue(row["abstained"])
        self.assertIsNone(row["metrics"]["precision"])

    def test_constrained_valid_ids_cite_real_git_lines_only(self):
        row=run_one(self.tasks[0],"mock","gbnf",mock_generated("1,3,5"))
        self.assertEqual(row["status"],"VALID")
        self.assertEqual(row["selected_model_ids"],[1,3,5])
        self.assertEqual(row["selected_verified_source_lines"],[9,11,13])
        self.assertEqual(row["source_gate_accepted"],3)
        self.assertEqual(row["automatic_certifications"],0)
        self.assertEqual(row["horn_rules"],0)

    def test_none_only_proof_grammar_is_literal(self):
        self.assertEqual(grammar_for_options(("NONE",)), 'root ::= "NONE"\n')

    def test_mechanical_controls(self):
        r=source_controls(self.tasks)
        self.assertEqual(r["first3"]["aggregate"]["n"],20)
        self.assertEqual(r["none"]["aggregate"]["tp"],0)
        self.assertEqual(r["all5_coverage_only"]["aggregate"]["fn"],0)

    def test_proposition_text_is_neutral_and_model_never_sees_gold(self):
        for t in self.tasks:
            messages=ordinal_messages(t,"ordinal")
            self.assertNotIn("truth_by_predicate",str(messages))
            self.assertNotIn("oracle_true_lines",str(messages))
            self.assertEqual(len(t["candidates"]),5)
            self.assertTrue(all(c["source_text"].startswith("Proposition : ") for c in t["candidates"]))

    def test_allowed_modes_explicit(self):
        self.assertEqual(INTERFACES,("free","gbnf"))
        with self.assertRaises(ValueError):
            run_one(self.tasks[0],"mock","modified-prompt",mock_generated("1"))


if __name__=="__main__":
    unittest.main()
