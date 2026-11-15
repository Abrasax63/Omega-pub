"""Fail-closed unit tests for the grammar, oracle and provenance. No model."""
import itertools
import unittest
from unittest.mock import patch

from symbolic_neural import (
    ROOT,N_GRAMMAR,grammar,simulate,public_cases,screen,search,verify_rce,
    parse_selection,selector_prompt,qualify,sha,
)
from reference import walks_exact

class SymbolicRepairTests(unittest.TestCase):
    def test_exactly_sixteen_distinct_frozen_candidates(self):
        g=grammar()
        self.assertEqual(len(g),N_GRAMMAR)
        self.assertEqual(len({v["expression"] for v in g}),16)
        self.assertEqual(len({v["id"] for v in g}),16)
        self.assertTrue(any(v["expression"]=="result[i] & (1 << j)" for v in g))

    def test_rce_file_retrieval_is_real_and_sha_bound(self):
        source=verify_rce(ROOT)
        import hashlib
        from pathlib import Path
        self.assertEqual(source["source_sha256"],
                         hashlib.sha256((ROOT/source["source_path"]).read_bytes()).hexdigest())
        self.assertTrue(all(source["tags"].values()))

    def test_correct_grammar_candidate_matches_finite_oracle(self):
        candidate=next(x for x in grammar() if x["expression"]=="result[i] & (1 << j)")
        for n in (1,2,3):
            # 1-state and 2-state exhaustive, 3-state deterministic sample
            graphs=itertools.product(range(1<<n),repeat=n)
            for index,rows in enumerate(graphs):
                if n==3 and index>=150:
                    break
                for h in range(0,6):
                    with self.subTest(n=n,rows=rows,h=h):
                        self.assertEqual(simulate(list(rows),h,candidate),
                                         walks_exact(list(rows),h))

    def test_historical_incorrect_expression_is_refuted(self):
        bad=next(x for x in grammar() if x["expression"]=="rows[j] & (1 << i)")
        result=screen(bad,public_cases())
        self.assertFalse(result["passed"])
        self.assertIsNotNone(result["first_counterexample"])

    def test_search_no_memory_and_rce_have_identical_survivors(self):
        c=public_cases()
        self.assertEqual(len(c),68)
        direct=search(c)
        guided=search(c,True)
        self.assertEqual(direct["num_hypotheses"],16)
        self.assertEqual(guided["num_hypotheses"],16)
        self.assertEqual(direct["survivor_ids"],guided["survivor_ids"])
        self.assertTrue(guided["survivor_ids"])
        self.assertTrue(any("result[i]" in s["expression"] for s in guided["survivors"]))

    def test_grammar_execution_does_not_eval_untrusted_python(self):
        candidate=grammar()[0]
        self.assertIsInstance(simulate([2,1],2,candidate),list)
        with self.assertRaises(ValueError):
            simulate([4,0],2,candidate)

    def test_selector_prompt_contains_only_public_candidates(self):
        g=grammar()
        p=selector_prompt(g[:3])
        self.assertIn("H00",p)
        self.assertNotIn("H10:",p)
        self.assertNotIn("reserved_manifest",p)

    def test_select_id_after_real_cli_truncation(self):
        p=selector_prompt(grammar()[:2])
        raw="llama-cli banner\n> system prompt... (truncated)\nH00\n\n[ Prompt: 40 t/s | Generation: 10 t/s ]\n\n> \nExiting...\n"
        self.assertEqual(parse_selection(raw,p,{"H00","H01"}),"H00")

    def test_invalid_selection_and_echo_are_rejected(self):
        p=selector_prompt(grammar()[:2])
        with self.assertRaisesRegex(ValueError,"boundary"):
            parse_selection("banner\n"+p[:50],p,{"H00","H01"})
        with self.assertRaisesRegex(ValueError,"outside"):
            parse_selection(p+"H15",p,{"H00","H01"})
        with self.assertRaisesRegex(ValueError,"standalone"):
            parse_selection(p+"H00 H01",p,{"H00","H01"})

    def test_no_silent_model_selection_fallback(self):
        from symbolic_neural import qwen_select
        import types
        fake=types.SimpleNamespace(returncode=0,stdout="garbled",stderr="")
        with patch("symbolic_neural.subprocess.run",return_value=fake):
            choice=qwen_select("llama","model",grammar()[:2])
        self.assertEqual(choice["status"],"INVALID_SELECTION")
        self.assertNotIn("selected_id",choice)

    def test_only_shortlist_is_executed_in_sandbox(self):
        # The public DSL interpreter never executes code; after surviving,
        # exactly the shortlisted trusted source is sent through score().
        from symbolic_neural import qualify
        h=next(x for x in grammar() if x["expression"]=="result[i] & (1 << j)")
        with patch("symbolic_neural.score",return_value=[
            {"correct":True,"delta_correct":True}
        ]) as scorer:
            res=qualify([h],[])
        self.assertEqual(scorer.call_count,1)
        self.assertTrue(res[0]["development_correct"])
        self.assertEqual(res[0]["id"],h["id"])

if __name__=="__main__":
    unittest.main()
