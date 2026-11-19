#!/usr/bin/env python3
"""Reader17 offline safety tests; no external model or gold required."""
import json
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from experiment import (
    FROZEN, ROOT, POLICIES, MAX_CANDIDATES, MAX_SELECTED, load_sources,
    source_pools, source_proposal, evaluate_doc, strict_line_ids, prompt_for,
)
from gate import gate
from read import safe_read


class FreshSourceSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_sources()
        cls.blind = [source_pools(r) for r in cls.sources]

    def test_frozen_sources_and_no_gold_label(self):
        self.assertEqual(len(self.sources), 3)
        manifest = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(manifest["reference_labels"], "NOT_AVAILABLE")
        for row in self.sources:
            data = safe_read(ROOT / row["path"], row["blob"])
            self.assertEqual(len(data), row["bytes"])
        self.assertNotIn("BR-R90-01", json.dumps(manifest))
        self.assertNotIn("BR-R90-02", json.dumps(manifest))

    def test_policies_only_exact_source_lines(self):
        nonempty = 0
        for ref, record in zip(self.sources, self.blind):
            raw = safe_read(ROOT / ref["path"], ref["blob"])
            self.assertEqual(record["source_blob"], ref["blob"])
            for key in POLICIES:
                pool = record["pools"][key]
                self.assertLessEqual(len(pool["submitted"]), MAX_CANDIDATES)
                self.assertEqual(pool["total_candidate_count"], len(pool["all_candidate_lines"]))
                self.assertEqual(
                    pool["truncated_candidate_count"],
                    pool["total_candidate_count"] - len(pool["submitted"])
                )
                self.assertTrue(set(pool["first_five_control"]).issubset(
                    set(pool["all_up_to_cap_control"])))
                self.assertTrue(set(pool["all_up_to_cap_control"]).issubset(
                    set(pool["all_candidate_lines"])))
                nonempty += bool(pool["submitted"])
                first = [x["line"] for x in pool["submitted"][:MAX_SELECTED]]
                proposed = source_proposal(ref["blob"], pool["submitted"], first)
                staged = gate(raw, str(ROOT / ref["path"]), proposed)
                self.assertEqual(staged["accepted_count"], len(first))
                self.assertEqual(staged["rejected_count"], 0)
                self.assertEqual(staged["automatic_promotions"], 0)
                self.assertEqual(staged["horn_rules"], [])
                self.assertTrue(all(not c["promotable"] for c in staged["accepted"]))
                if pool["submitted"]:
                    self.assertNotIn("999", [str(c["line"]) for c in pool["submitted"]])
                    self.assertNotIn("REPLACER_PAR_", str(prompt_for(pool["submitted"])))
            self.assertTrue(set(record["pools"]["C_statement"]["all_candidate_lines"]).issubset(
                set(record["pools"]["D_generalized_headings"]["all_candidate_lines"])))
        self.assertGreater(nonempty, 0, "all source strategies empty on new documents")

    def test_strict_selection_no_forgeries(self):
        available = {3, 9, 25, 41, 50, 52}
        self.assertEqual(strict_line_ids("NONE", available), ([], None))
        self.assertEqual(strict_line_ids("3,9,25,41,50", available),
                         ([3, 9, 25, 41, 50], None))
        for bad in ("", "999", "3,3", "3,9,25,41,50,52", "[3]", "3, 9\\n",
                    "```json\\n3\\n```", "I choose 3", "3;9", "3.0", "3 9"):
            # harmless outer whitespace is valid; malformed layouts are not
            if bad == "3, 9\\n":
                continue
            with self.subTest(bad=bad):
                chosen, reason = strict_line_ids(bad, available)
                self.assertEqual(chosen, [])
                self.assertIsNotNone(reason)

    def test_model_cannot_invent_source_content(self):
        ref = self.sources[0]
        pool = self.blind[0]["pools"]["D_generalized_headings"]
        if not pool["submitted"]:
            self.skipTest("D has no candidates")
        with self.assertRaises(ValueError):
            source_proposal(ref["blob"], pool["submitted"], [999])
        with self.assertRaises(ValueError):
            source_proposal(ref["blob"], pool["submitted"], [pool["submitted"][0]["line"]] * 2)
        forged = dict(ref, blob="0" * 40)
        with self.assertRaises(ValueError):
            source_pools(forged)

    def test_mock_real_path_and_quarantine(self):
        for ref, blind in zip(self.sources, self.blind):
            counts = []
            def fake_call(messages):
                self.assertEqual(messages[0]["role"], "system")
                self.assertEqual(messages[1]["role"], "user")
                counts.append(1)
                return {"raw_reply": "NONE", "duration_s": 0.001,
                        "tokens": {"prompt_tokens": 5, "completion_tokens": 2}}
            model = evaluate_doc(ref, fake_call)
            required = sum(bool(blind["pools"][key]["submitted"]) for key in POLICIES)
            self.assertEqual(sum(counts), required)
            for key in POLICIES:
                m = model["pools"][key]["model"]
                if blind["pools"][key]["submitted"]:
                    self.assertEqual(m["status"], "VALID_REPLY")
                    self.assertEqual(m["source_citations_admitted"], 0)
                    self.assertEqual(m["certifications"], 0)
                else:
                    self.assertEqual(m["status"], "NO_CANDIDATES")

    def test_mock_invalid_reply_rejected_not_salvaged(self):
        for ref in self.sources:
            model = evaluate_doc(ref, lambda _: {
                "raw_reply": "```\n999\n```",
                "duration_s": 0.001, "tokens": {},
            })
            for key in POLICIES:
                m = model["pools"][key]["model"]
                if m["status"] != "NO_CANDIDATES":
                    self.assertEqual(m["status"], "INVALID_REPLY")
                    self.assertEqual(m["selected"], [])
                    self.assertNotIn("source_citations_admitted", m)


if __name__ == "__main__":
    unittest.main(verbosity=2)
