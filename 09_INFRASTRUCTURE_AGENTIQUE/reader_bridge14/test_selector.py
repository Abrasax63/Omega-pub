#!/usr/bin/env python3
"""Reader14 safety and comparison tests; do not download or call a real model."""
import json
import sys
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from selector import (
    GOLD, ROOT, MAX_CHOICES, build_prompt, candidates_from_baseline,
    evaluate_document, parse_selection, proposal_from_lines,
)
from read import safe_read
from gate import gate


class LineSelectorContract(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs = json.loads(GOLD.read_text(encoding="utf-8"))["documents"]

    def test_strict_parser_and_no_guessing(self):
        allowed = {12, 21, 35, 43}
        for raw, want in [("NONE", []), ("21", [21]), ("12,43", [12, 43]),
                          ("12, 21,43", [12, 21, 43])]:
            with self.subTest(raw=raw):
                self.assertEqual(parse_selection(raw, allowed), (want, None))
        for raw in ("", "   ", "999", "12,12", "12,13", "12,21,35,43",
                    "```json\n12\n```", "[12]", "Voici: 21", "21;35",
                    "12, 21\nConclusion", "21,.", "001,3"):
            with self.subTest(rejected=raw):
                self.assertIsNotNone(parse_selection(raw, allowed)[1])

    def test_baseline_is_source_pinned_and_gate_non_promotional(self):
        total = 0
        for ref in self.refs:
            source = ROOT / ref["path"]
            raw = safe_read(source, ref["blob"])
            original, candidates, lines = candidates_from_baseline(raw, source, ref)
            total += len(candidates)
            self.assertEqual(original["accepted_count"], len(candidates))
            self.assertEqual(len({x["line"] for x in candidates}), len(candidates))
            self.assertFalse(original["horn_rules"])
            self.assertEqual(original["automatic_promotions"], 0)
            self.assertTrue(all(x["source_text"] in lines[x["line"]-1]
                                for x in candidates))
            self.assertNotIn("999", [str(x["line"]) for x in candidates])
            prompt = build_prompt(candidates)
            self.assertNotIn("REPLACER_PAR_", prompt)
            self.assertNotIn("source_blob", prompt)
        self.assertEqual(total, 8)  # frozen calibration, not a transferable fact

    def test_gated_reconstruction_and_forged_ids(self):
        for ref in self.refs:
            source = ROOT / ref["path"]
            raw = safe_read(source, ref["blob"])
            _, candidates, _ = candidates_from_baseline(raw, source, ref)
            selected = [x["line"] for x in candidates[:MAX_CHOICES]]
            proposal = proposal_from_lines(ref, candidates, selected)
            accepted = gate(raw, str(source), proposal, provider="test")
            self.assertEqual(accepted["accepted_count"], len(selected))
            self.assertFalse(accepted["horn_rules"])
            self.assertEqual(accepted["automatic_promotions"], 0)
            self.assertTrue(all(not c["promotable"] for c in accepted["accepted"]))
            with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_CHOICE"):
                proposal_from_lines(ref, candidates, [999])
            with self.assertRaisesRegex(ValueError, "BAD_CHOICES"):
                proposal_from_lines(ref, candidates, [selected[0], selected[0]])

    def test_model_reply_requires_valid_line_and_never_auto_certifies(self):
        ref = self.refs[0]
        _, candidates, _ = candidates_from_baseline(
            safe_read(ROOT / ref["path"], ref["blob"]), ROOT / ref["path"], ref
        )
        good = str(candidates[0]["line"])
        with patch("selector.infer_selection", return_value={
            "raw_reply": good, "input_tokens": 3, "output_tokens": 2,
            "inference_seconds": 0.01,
        }):
            r = evaluate_document(ref, tokenizer=object(), model=object())
        self.assertEqual(r["model"]["status"], "REPLY_VALID")
        self.assertEqual(r["model"]["selected"], [int(good)])
        self.assertEqual(r["model"]["accepted_count"], 1)
        self.assertIs(r["model"]["semantic_fidelity_verified"], False)
        self.assertIs(r["model"]["mathematical_validity_verified"], False)
        with patch("selector.infer_selection", return_value={
            "raw_reply": "999", "input_tokens": 3, "output_tokens": 2,
            "inference_seconds": 0.01,
        }):
            bad = evaluate_document(ref, tokenizer=object(), model=object())
        self.assertEqual(bad["model"]["status"], "REPLY_REJECTED")
        self.assertNotIn("accepted_count", bad["model"])
        with patch("selector.infer_selection", return_value={
            "raw_reply": "NONE", "input_tokens": 3, "output_tokens": 2,
            "inference_seconds": 0.01,
        }):
            abstained = evaluate_document(ref, tokenizer=object(), model=object())
        self.assertEqual(abstained["model"]["status"], "REPLY_VALID")
        self.assertEqual(abstained["model"]["accepted_count"], 0)


if __name__ == "__main__":
    main(verbosity=2)
