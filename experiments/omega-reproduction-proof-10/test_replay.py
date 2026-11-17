"""14 tests on local ephemeral fixtures, no evaluated GitHub matrix run."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import produce
import assemble
import infer
import score


class ReproductionReplayControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.base=Path(cls.temp.name)
        cls.stage=cls.base/"stage"
        for case in "ABCDE":
            produce.produce(case,cls.stage/f"omega-repro-10-compute-{case}")
        cls.raw=cls.base/"raw"
        cls.goldfile=cls.base/"gold"/"gold.json"
        assemble.stage(cls.stage,cls.raw,cls.goldfile)
        cls.gold=json.loads(cls.goldfile.read_bytes())
        cls.prediction=infer.resolve(cls.raw)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def copy_raw(self):
        t=tempfile.TemporaryDirectory()
        folder=Path(t.name)/"raw"
        shutil.copytree(self.raw,folder)
        return t,folder

    def alias(self,case):
        return next(name for name,role in self.gold["role_by_packet"].items()
                    if role==case)

    def test_01_protocol_and_five_actual_processes(self):
        self.assertEqual(assemble.PACK_SEED,60217)
        self.assertEqual(len(assemble.LABELS),5)
        self.assertEqual(len(self.gold["job_session_ids"]),5)
        self.assertEqual(len(set(self.gold["job_session_ids"])),5)
        self.assertEqual(len(self.prediction["results"]),5)

    def test_02_raw_packet_does_not_contain_gold_or_role(self):
        self.assertFalse((self.raw/"gold.json").exists())
        self.assertFalse((self.raw/"answer-key").exists())
        self.assertEqual(self.prediction["gold_supplied_to_engine"],False)
        for folder in (self.raw/"packets").iterdir():
            self.assertEqual({x.name for x in folder.iterdir()},
                             produce.EXPECTED_FILES)

    def test_03_strict_reference_and_replay_positive(self):
        labels={x["packet"]:x["decision"] for x in self.prediction["results"]}
        self.assertEqual(labels[self.alias("A")],"REFERENCE")
        self.assertEqual(labels[self.alias("B")],"SC_REPLAY_CERTIFIED")
        self.assertEqual(self.prediction["replayed_same_conditions"],1)
        self.assertNotEqual(
            next(x["session_uuid"] for x in self.prediction["results"]
                 if x["packet"]==self.alias("A")),
            next(x["session_uuid"] for x in self.prediction["results"]
                 if x["packet"]==self.alias("B"))
        )

    def test_04_equal_result_sha_different_inputs_rejected(self):
        a=infer.inspect(self.raw/"packets"/self.alias("A"))
        c=infer.inspect(self.raw/"packets"/self.alias("C"))
        self.assertEqual(a["result_sha256"],c["result_sha256"])
        self.assertNotEqual(a["input_sha256"],c["input_sha256"])
        self.assertEqual(infer.classify(a,c),"NOT_SC_REPLAY_INPUT_DRIFT")

    def test_05_equal_result_sha_actual_dependency_drift_rejected(self):
        a=infer.inspect(self.raw/"packets"/self.alias("A"))
        d=infer.inspect(self.raw/"packets"/self.alias("D"))
        self.assertEqual(a["result_sha256"],d["result_sha256"])
        self.assertNotEqual(a["dependency_sha256"],d["dependency_sha256"])
        self.assertNotEqual(
            (self.raw/"packets"/self.alias("A")/"dependency.py").read_bytes(),
            (self.raw/"packets"/self.alias("D")/"dependency.py").read_bytes())
        self.assertEqual(infer.classify(a,d),
                         "NOT_SC_REPLAY_DEPENDENCY_DRIFT")

    def test_06_changed_seed_changed_output(self):
        a=infer.inspect(self.raw/"packets"/self.alias("A"))
        e=infer.inspect(self.raw/"packets"/self.alias("E"))
        self.assertNotEqual(a["seed"],e["seed"])
        self.assertNotEqual(a["result_sha256"],e["result_sha256"])
        self.assertEqual(infer.classify(a,e),"NOT_SC_REPLAY_SEED_DRIFT")

    def test_07_independent_gold_scorer_confirms_all_five(self):
        verdict=score.audit(self.raw,self.prediction,self.gold)
        self.assertEqual(verdict["status"],"SC_REPLAY_PIPELINE_VERIFIED")
        self.assertEqual(verdict["strict_replay_certificates"],1)
        self.assertEqual(verdict["correct_negative_controls"],3)
        self.assertEqual(verdict["wrong_replay_certificates"],0)

    def test_08_json_valid_but_tampered_result_fails(self):
        t,raw=self.copy_raw()
        try:
            folder=raw/"packets"/self.alias("B")
            output=folder/"result.json"
            doc=json.loads(output.read_bytes())
            doc["total"]+=1
            output.write_text(json.dumps(doc,sort_keys=True)+"\n")
            with self.assertRaisesRegex(
                infer.BadEvidence,"FALSE_RECORDED_HASH_result_sha256"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_09_forged_stdout_lifecycle_fails(self):
        t,raw=self.copy_raw()
        try:
            log=raw/"packets"/self.alias("C")/"stdout.log"
            log.write_text(log.read_text().replace('"phase": "complete"',
                                                  '"phase": "fake"'))
            with self.assertRaisesRegex(infer.BadEvidence,
                                         "MISSING_REAL_LOG_LIFECYCLE"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_10_missing_receipt_causes_abstention_not_certification(self):
        t,raw=self.copy_raw()
        try:
            (raw/"packets"/self.alias("B")/"receipt.json").unlink()
            doc=infer.resolve(raw)
            b=next(x for x in doc["results"] if x["packet"]==self.alias("B"))
            self.assertEqual(b["decision"],"ABSTAIN_MISSING_EVIDENCE")
            self.assertEqual(doc["replayed_same_conditions"],0)
        finally:
            t.cleanup()

    def test_11_gold_leak_causes_immediate_failure(self):
        t,raw=self.copy_raw()
        try:
            shutil.copyfile(self.goldfile,raw/"gold.json")
            with self.assertRaisesRegex(infer.BadEvidence,"GOLD_LEAK_IN_RAW"):
                infer.resolve(raw)
        finally:
            t.cleanup()

    def test_12_duplicate_execution_session_cannot_certify(self):
        a=infer.inspect(self.raw/"packets"/self.alias("A"))
        b=copy.deepcopy(a)
        self.assertEqual(infer.classify(a,b),"ABSTAIN_NOT_DISTINCT_EXECUTION")

    def test_13_scorer_refuses_forged_reproduction(self):
        fake=copy.deepcopy(self.prediction)
        entry=next(x for x in fake["results"] if x["packet"]==self.alias("C"))
        entry["decision"]="SC_REPLAY_CERTIFIED"
        with self.assertRaises(score.ScoreFailure):
            score.audit(self.raw,fake,self.gold)

    def test_14_scorer_refuses_independence_claim(self):
        fake=copy.deepcopy(self.prediction)
        fake["scientific_independence"]="PROVEN_INDEPENDENT"
        fake["independent_scientific_replication_certified"]=True
        with self.assertRaises(score.ScoreFailure):
            score.audit(self.raw,fake,self.gold)


if __name__=="__main__":
    unittest.main()
