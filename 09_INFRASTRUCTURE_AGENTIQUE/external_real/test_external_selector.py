"""Unit tests for freeze-before-holdout and model-only opaque ID selection."""
import unittest
from unittest.mock import patch
from external_selector import extract_choice, prompt_for_e1, stable_hash, EXPECTED_MODEL_SHA

class ExternalSelectorTests(unittest.TestCase):
    def test_model_weight_identity_is_frozen(self):
        self.assertEqual(len(EXPECTED_MODEL_SHA),64)

    def test_same_payload_same_commitment_hash(self):
        x={"E1":{"deterministic":"P00","qwen":"P01"}}
        self.assertEqual(stable_hash(x),stable_hash(dict(x)))

    def test_prompt_only_public_patch_lines(self):
        r={"case":"E1","shortlist_ids":["P00","P01"],
           "candidates":[
               {"id":"P00","new":"with open(output, 'a') as f:"},
               {"id":"P01","new":"with open(output, 'w') as f:"},
           ]}
        prompt=prompt_for_e1(r)
        self.assertIn("P00:",prompt)
        self.assertIn("P01:",prompt)
        self.assertNotIn("fixed_commit",prompt)
        self.assertNotIn("reserved",prompt)

    def test_model_response_exact_one_id_after_echo(self):
        p="PROMPT\\nSELECTED_ID: "
        self.assertEqual(extract_choice(p+"P00\n",p,{"P00","P01"}),"P00")
        with self.assertRaises(ValueError):
            extract_choice(p+"P99",p,{"P00","P01"})
        with self.assertRaises(ValueError):
            extract_choice(p+"P00 P01",p,{"P00","P01"})
        with self.assertRaises(ValueError):
            extract_choice("CLI banner no boundaries",p,{"P00","P01"})

    def test_truncated_cli_output_boundary(self):
        p="PROMPT"
        v="banner\n> ... (truncated)\nP01\n\n[ Prompt: 50 t/s | Generation: 20 t/s ]\n"
        self.assertEqual(extract_choice(v,p,{"P00","P01"}),"P01")

if __name__=="__main__":
    unittest.main()
