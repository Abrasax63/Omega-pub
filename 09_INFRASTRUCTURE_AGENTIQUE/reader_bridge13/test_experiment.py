#!/usr/bin/env python3
"""Read-only regression tests: no model download, no paid API."""
from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_experiment import (
    GOLD, ROOT, baseline, packet_line_map, process_doc, score, select_packets
)
from read import blob, packetize, safe_read
from gate import gate


class RealModelExperimentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gold = json.loads(GOLD.read_text(encoding="utf-8"))

    def test_reference_immutable_and_two_documents(self):
        self.assertEqual(len(self.gold["documents"]), 2)
        self.assertFalse(self.gold["annotation_status"].startswith("INDEPENDENT"))
        for ref in self.gold["documents"]:
            raw = safe_read(ROOT / ref["path"], ref["blob"])
            self.assertEqual(blob(raw), ref["blob"])
            self.assertGreater(len(raw), 1000)

    def test_baseline_same_gate_and_no_promotions(self):
        for ref in self.gold["documents"]:
            out = process_doc(ref)
            self.assertEqual(out["model"]["status"], "NOT_RUN")
            gate_out = out["baseline"]["gate"]
            self.assertEqual(gate_out["automatic_promotions"], 0)
            self.assertEqual(gate_out["horn_rules"], [])
            self.assertTrue(all(not c["promotable"] for c in gate_out["accepted"]))
            self.assertLessEqual(len(out["packets_shown"]), 10)
            self.assertGreater(len(out["baseline"]["line_metrics"]["gold_conclusions_visible"]), 0)

    def test_fake_citation_refused(self):
        ref = self.gold["documents"][0]
        raw = safe_read(ROOT / ref["path"], ref["blob"])
        packets = select_packets(packetize(raw, ref["path"]))
        p = packets[0]
        proposed = {"source_blob": ref["blob"], "claims": [{
            "claim_id": "CFAKE", "packet_id": p["packet_id"],
            "evidence": [{"role": "conclusion", "packet_id": p["packet_id"],
                          "line": p["start_line"], "literal": "INVENTED_SCIENTIFIC_CONCLUSION"}],
        }]}
        g = gate(raw, ref["path"], proposed)
        self.assertEqual(g["accepted_count"], 0)
        self.assertEqual(g["rejected_count"], 1)

    def test_inline_proof_is_not_conclusion(self):
        ref = self.gold["documents"][0]
        raw = safe_read(ROOT / ref["path"], ref["blob"])
        lines = raw.decode("utf-8").splitlines()
        candidates = packetize(raw, ref["path"])["packets"]
        line = next(n for n, s in enumerate(lines, 1) if s.startswith("La fiche source renvoie"))
        p = next(p for p in candidates if p["start_line"] <= line <= p["end_line"])
        proposed = {"source_blob": ref["blob"], "claims": [{
            "claim_id": "CPROOF", "packet_id": p["packet_id"],
            "evidence": [{"role": "conclusion", "packet_id": p["packet_id"],
                          "line": line, "literal": lines[line - 1][:75]}],
        }]}
        g = gate(raw, ref["path"], proposed)
        self.assertEqual(g["accepted_count"], 0)
        self.assertEqual(g["rejected_count"], 1)


if __name__ == "__main__":
    unittest.main()
