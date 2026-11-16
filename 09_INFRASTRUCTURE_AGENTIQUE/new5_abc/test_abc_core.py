"""Independent tests of prospective A/B/C selection rules, no external fixes."""
import json
from pathlib import Path
import tempfile
import unittest

from abc_core import (_candidate_pool, CASE_IDS, MAX_POOL, MAX_PER_ARM, ARMS,
                      final_model_order, freeze_case, frozen_orders,
                      model_select, extract_llama_cli_id, verify_manifest)

CASE = {"id":"N1", "project":"tqdm", "buggy_sha":"fixed-in-test-buggy",
        "test_id":"tqdm/tests/tests_tqdm.py::test_bool"}
SOURCE = """def algorithm(x):
    if x == 0:
        return None
    return [x]

def other(y):
    if y is None:
        return []
    return [y]
"""
TEST = """from tqdm.tqdm import algorithm
def test_bool():
    assert algorithm(0) is None
"""
TRACE = ('OMEGA_CALL_TRACE_V1=' + json.dumps({
    "schema": "omega-calltrace-v1",
    "files": [{"path":"tqdm.py","total_calls":3,
              "functions":[{"label":"algorithm@1","calls":3}]}]
}))


class PilotABCTests(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory()
        root = Path(self.context.name)
        (root / "tqdm").mkdir()
        (root / "tqdm" / "tqdm.py").write_text(SOURCE)
        self.root = root

    def tearDown(self):
        self.context.cleanup()

    def test_five_cases_unique(self):
        self.assertEqual(len(CASE_IDS), 5)
        self.assertEqual(len(set(CASE_IDS)), 5)

    def test_pool_reproducible_and_cap(self):
        a = _candidate_pool(self.root, "tqdm", [], [])
        b = _candidate_pool(self.root, "tqdm", [], [])
        self.assertEqual(a,b)
        self.assertLessEqual(len(a),MAX_POOL)
        self.assertGreater(len(a),0)

    def test_trace_guides_real_called_function(self):
        row = freeze_case(CASE,self.root,TRACE,TEST)
        self.assertTrue(row["trace_verified"])
        self.assertEqual(row["status"],"TRACE_AVAILABLE")
        self.assertTrue(any(c["trace_score"]>0 and c["function"]=="algorithm"
                            for c in row["candidates"]))
        self.assertLessEqual(len(row["orders"][ARMS[1]]),MAX_PER_ARM)
        self.assertLessEqual(len(row["orders"][ARMS[2]]),12)

    def test_no_trace_must_not_claim_b_or_c(self):
        row = freeze_case(CASE,self.root,"",TEST)
        self.assertFalse(row["trace_verified"])
        self.assertFalse(row["orders"][ARMS[1]])
        self.assertFalse(row["orders"][ARMS[2]])

    def test_model_invalid_id_abstains(self):
        allowed = ["P000","P010"]
        for raw in ("P999", "P000\nP010", "The answer is P000", "import os",
                    "", "P000 " * 900):
            self.assertIsNone(model_select(raw, allowed))
        self.assertEqual(model_select("P010", allowed),"P010")

    def test_valid_qwen_id_with_actual_llama_cli_footer(self):
        for answer in ("P038", "P027", "P058"):
            raw = ("<|im_start|>user\nCandidates:\nP000 file function\n"
                   + "one long echoed prompt ... (truncated)\n"
                   + answer
                   + "\n\n[ Prompt: 40.6 t/s | Generation: 15.9 t/s ]\n\n> \n\nExiting...")
            self.assertEqual(extract_llama_cli_id(raw, [answer]), answer)
            self.assertIsNone(extract_llama_cli_id(raw, ["P999"]))

    def test_cli_parser_rejects_chatter_and_ambiguous_candidates(self):
        candidates=["P010", "P020"]
        sample=("P010\nP020\n\n[ Prompt: 40.6 t/s | Generation: 15.9 t/s ]"
                "\n\n> \n\nExiting...")
        self.assertIsNone(extract_llama_cli_id(sample,candidates))
        self.assertIsNone(extract_llama_cli_id("I choose P010",candidates))
        self.assertIsNone(extract_llama_cli_id("P010\nunaudited output",candidates))
        self.assertIsNone(extract_llama_cli_id(
            "P010\n\n[ Prompt: 40.6 t/s | Generation: 15.9 t/s ]\n> injected data",
            candidates))

    def test_model_cannot_increase_patch_testing_budget(self):
        b=["P001","P002","P003","P004"]
        chosen=final_model_order(b,["P001","P007"],"P007")
        self.assertEqual(chosen,["P007","P001","P002","P003"])
        self.assertEqual(len(chosen),MAX_PER_ARM)
        self.assertEqual(final_model_order(b,["P001"],None),[])

    def test_missing_public_test_fail_closed(self):
        row=freeze_case(CASE,self.root,TRACE,"")
        self.assertEqual(row["status"],"MISSING_PUBLIC_TEST")
        self.assertEqual(row["candidates"],[])

    def test_valid_freeze_requires_five_matching_cases(self):
        candidates=_candidate_pool(self.root,"tqdm")
        orders=frozen_orders(candidates,False)
        one={"id":"N1","buggy_sha":"buggy","candidate_count":len(candidates),
             "fixed_source_seen":False,"candidates":candidates,"orders":orders}
        manifest={"experiment":"OMEGA-NEW5-ABC-01",
                  "cases":[dict(one,id=f"N{i}") for i in range(1,6)]}
        cohort={"experiment":"OMEGA-NEW5-ABC-01",
                "cases":[{"id":f"N{i}","buggy_sha":"buggy"} for i in range(1,6)]}
        self.assertTrue(verify_manifest(manifest,cohort))
        manifest["cases"][2]["fixed_source_seen"]=True
        with self.assertRaisesRegex(ValueError,"invalid blind"):
            verify_manifest(manifest,cohort)


if __name__=="__main__":
    unittest.main()
