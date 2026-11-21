"""Persistent quarantine remains separate and matches preregistered pairing tasks."""
import json
from pathlib import Path
import unittest
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"external_memory01"))
from run_external import parse_label
from publisher import load_jsonl
from read_memory import ScientificMemoryReader

class QuarantineImportTests(unittest.TestCase):
    def test_all_24_raw_outputs_preserved_not_certified(self):
        manifest=json.loads((HERE.parent/"external_memory01"/"FROZEN_NEW.json").read_text(encoding="utf8"))
        records=load_jsonl(HERE/"model_quarantine.jsonl")
        self.assertEqual(len(records),24)
        self.assertEqual(len({(r["task_id"],r["cache_mode"]) for r in records}),24)
        gold={t["task"]:(t["id"],t["gold"]) for t in manifest["tasks"]}
        for r in records:
            self.assertIn(r["task_id"],gold)
            self.assertEqual((r["source_id"],r["original_source_pairing_gold"]),gold[r["task_id"]])
            self.assertEqual(r["source_run_id"],44878133828)
            self.assertEqual(r["status"],"QUARANTINED_UNVERIFIED_LLM_OUTPUT")
            self.assertIs(r["lean_proof_compiled"],False)
            self.assertIs(r["scientific_understanding_verified"],False)
            self.assertEqual(r["strictly_parsed_label"],parse_label(r["raw_llm_reply"]))
            self.assertEqual(r["matches_original_source_pairing"],
                             r["strictly_parsed_label"]==r["original_source_pairing_gold"])
        groups={mode:{r["task_id"]:r for r in records if r["cache_mode"]==mode} for mode in ("off","on")}
        self.assertEqual(len(groups["off"]),12)
        self.assertEqual(len(groups["on"]),12)
        self.assertEqual(sum(r["matches_original_source_pairing"] for r in groups["off"].values()),4)
        self.assertEqual(sum(r["matches_original_source_pairing"] for r in groups["on"].values()),3)
        diffs=[t for t in groups["off"] if groups["off"][t]["raw_llm_reply"]!=groups["on"][t]["raw_llm_reply"]]
        self.assertEqual(diffs,["N34"])
        self.assertEqual(groups["off"]["N34"]["raw_llm_reply"],"NONE")
        self.assertEqual(groups["on"]["N34"]["raw_llm_reply"],"A")
        reader=ScientificMemoryReader()
        self.assertEqual(reader.index["n_unverified_llm_predictions"],len(records))
        self.assertEqual(reader.index["llm_predictions_in_verified_memory"],0)

if __name__=="__main__":unittest.main()
