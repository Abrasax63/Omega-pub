import unittest
from pathlib import Path
import tempfile
import json
from bench_kv import (PREFIX, CASES, ORDER, prompt_for, request_for, parse_content,
                       timing, exact_number, summarize)

class FrozenKVTests(unittest.TestCase):
    def test_order(self):
        self.assertEqual(ORDER,("off","on","on","off"))
    def test_common_prefix_and_distinct_cases(self):
        prompts=[prompt_for(c) for c in CASES]
        self.assertTrue(all(x.startswith(PREFIX) for x in prompts))
        self.assertEqual(len(set(prompts)),6)
        self.assertEqual(prompts[0],prompts[6])
    def test_only_cache_flag_changes(self):
        a=request_for(CASES[0],False);b=request_for(CASES[0],True)
        self.assertEqual({k:v for k,v in a.items() if k!="cache_prompt"},
                         {k:v for k,v in b.items() if k!="cache_prompt"})
        self.assertFalse(a["cache_prompt"]);self.assertTrue(b["cache_prompt"])
    def test_oracle(self):
        self.assertEqual([(a+b)%m for _,m,a,b in CASES],[3,6,10,7,3,10,3])
    def test_number_parser_strict(self):
        self.assertEqual(exact_number("3\n",7),3)
        for text in ("03","3 explanation","-1","100","3 4",""):
            self.assertIsNone(exact_number(text,7))
    def test_missing_timing_does_not_invent(self):
        self.assertIsNone(timing({"content":"3"})["cache_n"])
        self.assertIsNone(timing({"timings":{"cache_n":-1}})["cache_n"])
        self.assertEqual(timing({"timings":{"prompt_n":25}})["prompt_n"],25)
    def test_no_synthetic_json_claim_of_real_measurement(self):
        rep={"sessions":[{"mode":"off","rows":[]},{"mode":"on","rows":[]}]}
        self.assertEqual(summarize(rep)["status"],"INCOMPLETE_BLOCKS")
    def test_invalid_response_fails_closed(self):
        with self.assertRaises(ValueError):parse_content({"choices":[{"text":"3"}]})
    def test_every_case_oracle_in_range(self):
        for _,m,a,b in CASES:self.assertLess((a+b)%m,m)

if __name__=="__main__":unittest.main()
