"""Offline falsification for actual Omega cycle from frozen input to memory."""
from tempfile import TemporaryDirectory
from pathlib import Path
import json
import unittest

import cycle


class OmegaCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(cycle.MANIFEST.read_text(encoding="utf-8"))
        cls.prepared=cycle.check_pinned_sources(cls.manifest)

    def make_book(self):
        folder=TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        return cycle.ScientificMemory(Path(folder.name)/"memory.jsonl")

    def fake_call(self,chosen):
        def provide(messages,mode):
            return ({
                "raw_reply":chosen,"seconds":0.001,
                "usage":None,"finish_reason":"mock",
                "server_model":"UNIT_TEST_NO_REAL_LLM"
            },{
                "native":{"prompt_n":25,"cache_n":0},
                "completion_http_seconds":0.001,
                "mock_not_real_model":True
            })
        return provide

    def test_frozen_original_math_document_git_blob(self):
        self.assertEqual(self.manifest["source"]["git_blob"],
                         "0d449a5911b7364d03b5557b24afc3dfc6eef292")
        self.assertEqual(len(self.prepared),6)
        self.assertEqual(self.prepared[0]["ref"]["id"],"S01")

    def test_end_to_end_exact_route_and_provenance(self):
        book=self.make_book()
        result=cycle.run_exact(self.manifest,book)
        self.assertEqual(result["status"],"EXACT_AND_INDEPENDENT_GATES_PASS")
        self.assertEqual(len(result["rows"]),5)
        self.assertEqual([x["admissible"] for x in result["rows"]],
                         [False,True,False,True,False])
        self.assertEqual(result["routing_counters"]["direct_calls"],3)
        self.assertEqual(result["routing_counters"]["bitset_calls"],2)
        self.assertGreater(result["routing_counters"]["bitset_hits"],0)
        self.assertEqual(book.index()["unique_records"],4)
        self.assertEqual(book.index()["revisits"],1)
        self.assertEqual(book.validate_replay()["verified_events"],5)

    def test_direct_exact_oracles_ghost_and_deep_failure(self):
        examples={
            "110":((0,0,2),(0,1,1),(1,1,0),3),
            "0001":((0,3,1,3),(0,0,0,1),(0,0,0,1),4)
        }
        for T,pi,w,fail_at in examples.values():
            result=cycle.verify_finite_question(T,pi,w)
            self.assertFalse(result["admissible"])
            self.assertEqual(result["first_empty_length"],fail_at)
            self.assertEqual(result["all_initial_witnesses"],())

    def test_reader_scientific_gate_and_nonpromotion(self):
        book=self.make_book()
        out=cycle.classify_readers(self.prepared,self.manifest,book,
                                   "off",self.fake_call("5,7"))
        self.assertEqual(len(out["rows"]),6)
        self.assertEqual(out["all_certifications"],0)
        self.assertTrue(all(x["status"]=="VALID" for x in out["rows"]))
        self.assertTrue(all(x["accepted_count"]==2 for x in out["rows"]))
        self.assertTrue(all(x["policy"]=="CONSERVATIVE_OFF" for x in out["rows"]))
        self.assertEqual(book.index()["unique_records"],6)
        self.assertTrue(book.validate_replay()["event_hashes_checked"])

    def test_parse_rejection_is_not_masked(self):
        book=self.make_book()
        out=cycle.classify_readers(self.prepared,self.manifest,book,
                                   "off",self.fake_call("La réponse est 5."))
        self.assertEqual(len(out["rows"]),6)
        self.assertTrue(all(x["status"]=="REJECTED" for x in out["rows"]))
        self.assertTrue(all(x["accepted_count"]==0 for x in out["rows"]))
        self.assertTrue(book.validate_replay()["event_hashes_checked"])

    def test_cache_parity_mock_and_difference_detection(self):
        book=self.make_book()
        off=cycle.classify_readers(self.prepared,self.manifest,book,
                                   "off",self.fake_call("NONE"))
        on=cycle.classify_readers(self.prepared,self.manifest,book,
                                  "on",self.fake_call("NONE"))
        self.assertEqual(cycle.compare_modes(off,on)["status"],
                         "LOCAL_TEXT_AND_SELECTION_PARITY")
        self.assertEqual(cycle.compare_modes(off,on)["cases_compared"],6)
        on["rows"][0]["raw_reply"]="5,7"
        self.assertEqual(cycle.compare_modes(off,on)["status"],
                         "DIVERGENCE_OBSERVED")
        self.assertEqual(len(cycle.compare_modes(off,on)["divergences"]),1)

    def test_nonmatching_sources_cannot_be_compared(self):
        book=self.make_book()
        off=cycle.classify_readers(self.prepared,self.manifest,book,
                                   "off",self.fake_call("NONE"))
        on=cycle.classify_readers(self.prepared,self.manifest,book,
                                  "on",self.fake_call("NONE"))
        on["rows"][0]["prompt_sha256"]="changed"
        with self.assertRaisesRegex(ValueError,"SCIENTIFIC_SOURCE_OR_MESSAGES"):
            cycle.compare_modes(off,on)

    def test_memory_is_append_only_and_tamper_evident_locally(self):
        book=self.make_book()
        key="exact:4"
        event_id,is_new=book.remember(key,{"status":"CALCUL_EXACT_VERIFIE","a":1})
        self.assertTrue(is_new)
        self.assertEqual(book.remember(key,{"status":"changed"})[0],event_id)
        self.assertEqual(book.validate_replay()["revisits"],1)
        text=book.path.read_text(encoding="utf-8")
        book.path.write_text(text.replace('"a":1','"a":2'),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"HASH_OR_DUPLICATE"):
            book.validate_replay()

    def test_file_source_drift_is_rejected(self):
        manifest=json.loads(json.dumps(self.manifest))
        manifest["source"]["git_blob"]="f"*40
        with self.assertRaisesRegex(ValueError,"MATHEMATICAL_SOURCE_DRIFT"):
            cycle.check_pinned_sources(manifest)

    def test_input_expectation_drift_fails_before_memory_promotion(self):
        manifest=json.loads(json.dumps(self.manifest))
        manifest["exact_questions"][0]["expected_admissible"]=True
        book=self.make_book()
        with self.assertRaisesRegex(ValueError,"EXPECTATION_VIOLATED"):
            cycle.run_exact(manifest,book)

    def test_actual_model_requires_source_report_sha_and_real_process(self):
        self.assertEqual(
            self.manifest["scale01_profile"]["report_sha256"],
            "f6f1fae5cae5c79a6c0145496f5f2456311ba76f3b8b7ce22bd3a7a464a34996")
        self.assertEqual(self.manifest["model_label"],"0p5b")
        self.assertTrue(self.manifest["scale01_profile"]["artifact_id"]>0)


if __name__=="__main__":
    unittest.main()
