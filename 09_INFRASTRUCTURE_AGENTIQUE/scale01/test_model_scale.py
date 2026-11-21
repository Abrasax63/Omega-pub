"""Offline model-scale protocol: frozen sources, independent quality controls."""
from hashlib import sha256
import json
import unittest
import model_scale as m

class ModelScalingTests(unittest.TestCase):
    def fake_report(self):
        blocks=[]
        for idx,mode in enumerate(m.ORDER):
            stages=[]
            for count in m.STAGES:
                rows=[]
                for pos in range(count):
                    item=m.paired.prepare()[pos%6]
                    msgs=m.paired.messages(item["candidates"])
                    digest=sha256(json.dumps(msgs,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
                    rows.append({
                        "id":item["ref"]["id"],
                        "source_id":item["ref"]["id"],
                        "source_blob":item["ref"]["blob"],
                        "prompt_sha256":digest,
                        "request_index":pos,
                        "raw_reply":"NONE",
                        "status":"VALID",
                        "rejection":None,
                        "selected":[],
                        "accepted_count":0,
                        "abstained":True,
                        "metrics":m.paired.metrics([],item["ref"]["conclusion_lines"]),
                        "native":{"prompt_n":10 if mode=="on" else 100,
                                  "cache_n":90 if mode=="on" else 0,
                                  "prompt_ms":1,"predicted_n":1,"predicted_ms":1},
                        "completion_seconds":0.2,
                    })
                stages.append({
                    "documents_processed":count,"wall_seconds":count*0.2,
                    "server_peak_rss_kib":1000000,"rows":rows
                })
            blocks.append({
                "mode":mode,"stages":stages,
                "server_peak_rss_kib":1100000,
                "total_block_wall_seconds":sum(s["wall_seconds"] for s in stages)+1,
                "server_startup_seconds":1
            })
        return {"blocks":blocks}

    def test_modes_and_tiers_are_frozen(self):
        self.assertEqual(m.STAGES,(6,12,24))
        self.assertEqual(m.ORDER,("off","on","on","off"))
        self.assertEqual(set(m.MODEL_VERSIONS),{"0p5b","3b"})
        self.assertEqual(m.EXPECTED_ENGINE,m.paired.LLAMA_CPP_SHA)
    def test_frozen_reader_prepare(self):
        items=m.paired.prepare()
        self.assertEqual(len(items),6)
        self.assertEqual({z["ref"]["id"] for z in items},
                         {"S01","S02","S03","S04","S05","S06"})
    def test_rss_parser_self(self):
        import os
        v=m.proc_peak_rss_kib(os.getpid())
        self.assertIsInstance(v,int)
        self.assertGreater(v,0)
    def test_all_gates_same_no_false_quality_promotion(self):
        s=m.aggregate(self.fake_report())
        self.assertEqual(s["status"],"PREFIX_REUSE_INSTRUMENTED")
        self.assertEqual(s["quality_status"],"LOCAL_TEXT_AND_SOURCE_GATE_PARITY")
        self.assertEqual(s["matched_comparisons"],84)
        self.assertFalse(s["human_quality_verified"])
        self.assertFalse(s["training_parameters_increased"])
        self.assertFalse(s["unique_documents_increased"])
    def test_changed_reply_reported(self):
        fake=self.fake_report()
        fake["blocks"][1]["stages"][2]["rows"][0]["raw_reply"]="5"
        s=m.aggregate(fake)
        self.assertEqual(s["quality_status"],"DIVERGENCE_OBSERVED")
        self.assertEqual(len(s["divergences"]),1)
    def test_changed_prompt_rejected(self):
        fake=self.fake_report()
        fake["blocks"][1]["stages"][1]["rows"][0]["prompt_sha256"]="different"
        with self.assertRaisesRegex(ValueError,"SCIENTIFIC_INPUT"):
            m.aggregate(fake)
    def test_missing_timing_not_imputed(self):
        fake=self.fake_report()
        fake["blocks"][1]["stages"][1]["rows"][0]["native"]["cache_n"]=None
        self.assertEqual(m.aggregate(fake)["status"],"MEASUREMENT_UNAVAILABLE")
    def test_incomplete_block_not_treated_as_success(self):
        fake=self.fake_report()
        fake["blocks"][0]["stages"].pop()
        self.assertEqual(m.aggregate(fake)["status"],"INCOMPLETE_BLOCKS")
if __name__=="__main__":unittest.main()
