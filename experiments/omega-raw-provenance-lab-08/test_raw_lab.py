"""Fourteen controls for actual child-process generation and fail-closed provenance."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import generate
import infer
import score


class RawProvenanceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.holder=tempfile.TemporaryDirectory()
        cls.base=Path(cls.holder.name)
        cls.raw=cls.base/"raw"
        cls.goldfile=cls.base/"answer-key"/"gold.json"
        generate.generate(cls.raw,cls.goldfile)
        cls.gold=json.loads(cls.goldfile.read_text())
        cls.good=infer.resolve(cls.raw)

    @classmethod
    def tearDownClass(cls):
        cls.holder.cleanup()

    def fresh_copy(self):
        t=tempfile.TemporaryDirectory()
        raw=Path(t.name)/"raw"
        shutil.copytree(self.raw,raw)
        return t,raw

    def root_packets(self):
        return [key for key,v in self.gold["cases"].items()
                if v["role"]=="EXECUTION"]

    def test_01_four_actual_processes_and_seven_packets(self):
        self.assertEqual(self.good["group_count"],4)
        self.assertEqual(len(self.good["results"]),7)
        self.assertEqual(len(self.gold["real_subprocess_ids"]),4)

    def test_02_original_bundles_contain_real_logs_and_receipts(self):
        pids=set()
        for key in self.root_packets():
            d=self.raw/"cases"/key
            self.assertEqual({p.name for p in d.iterdir()},
                             generate.FILES and set(generate.FILES))
            rec=json.loads((d/"receipt.json").read_text())
            lines=[json.loads(s) for s in (d/"stdout.log").read_text().splitlines()]
            self.assertEqual([x["phase"] for x in lines],["begin","complete"])
            self.assertEqual(lines[0]["pid"],rec["pid"])
            pids.add(rec["pid"])
        self.assertEqual(len(pids),4)

    def test_03_distinct_executions_can_have_identical_outputs(self):
        roots=self.root_packets()
        hashes={}
        for key in roots:
            data=(self.raw/"cases"/key/"result.json").read_bytes()
            hashes[key]=infer.sha(data)
        self.assertEqual(len(set(hashes.values())),3)
        twins=[(a,b) for a in roots for b in roots
               if a<b and hashes[a]==hashes[b]]
        self.assertEqual(len(twins),1)
        a,b=twins[0]
        self.assertNotEqual(self.gold["cases"][a]["origin_id"],
                            self.gold["cases"][b]["origin_id"])

    def test_04_genuine_byte_for_byte_mirrors(self):
        events=[json.loads(s) for s in
                (self.raw/"copy_events.jsonl").read_text().splitlines()]
        self.assertEqual(len(events),2)
        for entry in events:
            self.assertEqual(entry["event"],"copy_bundle")
            for f,expected in entry["sha256_by_file"].items():
                first=self.raw/"cases"/entry["source_packet"]/f
                copied=self.raw/"cases"/entry["copied_packet"]/f
                self.assertEqual(first.read_bytes(),copied.read_bytes())
                self.assertEqual(infer.sha(first.read_bytes()),expected)

    def test_05_ambiguous_orphan_abstains(self):
        orphans=[x for x in self.good["results"] if x["status"]=="ABSTAIN"]
        self.assertEqual(len(orphans),1)
        self.assertEqual(orphans[0]["role"],"UNRESOLVED")
        self.assertIsNone(orphans[0]["origin_id"])

    def test_06_inference_does_not_import_answer_key(self):
        self.assertFalse((self.raw/"gold.json").exists())
        self.assertFalse((self.raw/"answer-key").exists())
        self.assertTrue(self.goldfile.exists())
        self.assertFalse(any("gold" in x.name for x in self.raw.rglob("*")
                             if x.is_file()))
        self.assertEqual(self.good["scientific_independence"],"INDETERMINATE")

    def test_07_independent_judge_accepts_correct_blind_predictions(self):
        outcome=score.audit(self.raw,self.good,self.gold)
        self.assertEqual(outcome["status"],"RAW_PROVENANCE_PIPELINE_VERIFIED")
        self.assertEqual(outcome["wrong_links"],0)
        self.assertEqual(outcome["false_scientific_certificates"],0)

    def test_08_tampered_worker_result_rejected(self):
        t,raw=self.fresh_copy()
        try:
            packet=self.root_packets()[0]
            with (raw/"cases"/packet/"result.json").open("ab") as f:
                f.write(b"TAMPER")
            with self.assertRaisesRegex(infer.ProvenanceConflict,
                                         "HASH_CONTRADICTION"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_09_tampered_worker_stdout_rejected(self):
        t,raw=self.fresh_copy()
        try:
            packet=self.root_packets()[0]
            log=raw/"cases"/packet/"stdout.log"
            log.write_text(log.read_text().replace('"phase": "begin"',
                                                   '"phase": "unknown"'))
            with self.assertRaises(infer.ProvenanceConflict):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_10_tampered_receipt_id_rejected(self):
        t,raw=self.fresh_copy()
        try:
            packet=self.root_packets()[0]
            path=raw/"cases"/packet/"receipt.json"
            d=json.loads(path.read_text())
            d["execution_id"]="f"*32
            generate.write_json(path,d)
            with self.assertRaises(infer.ProvenanceConflict):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_11_forged_copy_event_rejected(self):
        t,raw=self.fresh_copy()
        try:
            path=raw/"copy_events.jsonl"
            events=[json.loads(s) for s in path.read_text().splitlines()]
            events[0]["sha256_by_file"]["result.json"]="0"*64
            path.write_text("\n".join(json.dumps(x) for x in events)+"\n")
            with self.assertRaisesRegex(infer.ProvenanceConflict,
                                         "COPY_EVENT_BYTES_MISMATCH"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_12_missing_receipt_abstains_not_invents_origin(self):
        mirrored={e["source_packet"] for e in
                  [json.loads(s) for s in
                   (self.raw/"copy_events.jsonl").read_text().splitlines()]}
        packet=next(x for x in self.root_packets() if x not in mirrored)
        t,raw=self.fresh_copy()
        try:
            (raw/"cases"/packet/"receipt.json").unlink()
            invpath=raw/"inventory.json"
            data=json.loads(invpath.read_text())
            for row in data["packets"]:
                if row["packet"]==packet:
                    row["files"].remove("receipt.json")
            generate.write_json(invpath,data)
            outcome=infer.resolve(raw)
            x=next(x for x in outcome["results"] if x["packet"]==packet)
            self.assertEqual(x["status"],"ABSTAIN")
            self.assertIsNone(x["origin_id"])
        finally:
            t.cleanup()

    def test_13_judge_rejects_wrong_origin_group(self):
        copied=json.loads(json.dumps(self.good))
        entry=next(x for x in copied["results"] if x["status"]=="GROUPED")
        entry["origin_id"]="a"*32
        with self.assertRaises(score.ScoreFailure):
            score.audit(self.raw,copied,self.gold)

    def test_14_judge_rejects_false_scientific_claim(self):
        copied=json.loads(json.dumps(self.good))
        copied["scientific_independence"]="PROVEN_INDEPENDENT"
        copied["scientific_replication_certified"]=True
        with self.assertRaises(score.ScoreFailure):
            score.audit(self.raw,copied,self.gold)


if __name__=="__main__":
    unittest.main()
