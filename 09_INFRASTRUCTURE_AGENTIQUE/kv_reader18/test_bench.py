"""Offline quality and unchanged-reader controls for scientific KV A/B."""
import hashlib
import json
import unittest
import bench
import paired


class Reader18KVGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared=bench.paired_cases()
    def test_six_unique_frozen_sources_with_one_duplicate(self):
        self.assertEqual(bench.LABELS,("S01","S01_DUP","S02","S03","S04","S05","S06"))
        self.assertEqual(self.prepared[0]["ref"]["blob"],self.prepared[1]["ref"]["blob"])
        self.assertEqual(len({p["ref"]["blob"] for p in self.prepared}),6)
        self.assertEqual(len(self.prepared),7)
    def test_original_reader18_source_and_gold_present(self):
        self.assertTrue(all(len(p["candidates"])==5 for p in self.prepared))
        self.assertTrue(all(len(p["ref"]["conclusion_lines"])==2 for p in self.prepared))
        self.assertEqual([p["ref"]["id"] for p in self.prepared],
                         ["S01","S01","S02","S03","S04","S05","S06"])
    def test_source_parser_source_gate_kept_unchanged(self):
        p=self.prepared[0]
        result=paired.one_case(p,"0p5b",call=lambda m:{
            "raw_reply":"5,7","seconds":0.0,
            "usage":None,"finish_reason":"stop","server_model":"mock"})
        self.assertEqual(result["status"],"VALID")
        self.assertEqual(result["accepted_count"],2)
        self.assertEqual(result["selected"],[5,7])
        self.assertTrue(all(x in [5,6,7,8,9] for x in result["selected"]))
    def test_no_source_claim_from_invalid_number(self):
        p=self.prepared[0]
        result=paired.one_case(p,"0p5b",call=lambda m:{
            "raw_reply":"999","seconds":0.0,
            "usage":None,"finish_reason":"stop","server_model":"mock"})
        self.assertEqual(result["status"],"REJECTED")
        self.assertEqual(result["accepted_count"],0)
    def test_frozen_prompt_builder_remains_original(self):
        a=paired.messages(self.prepared[0]["candidates"])
        self.assertEqual(a[0]["role"],"system")
        self.assertEqual(a[1]["role"],"user")
        self.assertEqual(a[0],paired.messages(self.prepared[-1]["candidates"])[0])
    def test_order_and_single_factor(self):
        self.assertEqual(bench.ORDER,("off","on","on","off"))
        self.assertEqual(bench.MAX_TOKENS,64)
    def test_absent_telemetry_is_absent_not_zero(self):
        self.assertEqual(bench.telemetry({})["cache_n"],None)
        self.assertEqual(bench.telemetry({"timings":{"cache_n":18}})["cache_n"],18)
    def test_failed_telemetry_not_counted_as_gain(self):
        r=self.example_report()
        r["blocks"][0]["rows"][2]["telemetry"]["prompt_n"]=None
        self.assertEqual(bench.summarize(r)["status"],"MEASUREMENT_UNAVAILABLE")
    def example_report(self):
        blocks=[]
        for mode in bench.ORDER:
            rows=[]
            for label,p in zip(bench.LABELS,self.prepared):
                messages=paired.messages(p["candidates"])
                identity=hashlib.sha256(json.dumps(messages,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                record=paired.one_case(p,"0p5b",call=lambda m:{
                    "raw_reply":"NONE","seconds":0.0,"usage":None,
                    "finish_reason":"stop","server_model":"mock"})
                rows.append({
                    **record,"trace_label":label,"rendered_prompt_sha256":identity,
                    "telemetry":{"cache_n":80 if mode=="on" else 0,
                                 "prompt_n":20 if mode=="on" else 100,
                                 "prompt_ms":1.0,"predicted_n":2,"predicted_ms":1.0},
                    "http_completion_seconds":1.0,
                })
            blocks.append({"mode":mode,"rows":rows})
        return {"blocks":blocks}
    def test_instrumented_only_under_positive_reuse(self):
        r=self.example_report()
        s=bench.summarize(r)
        self.assertEqual(s["status"],"PREFIX_REUSE_INSTRUMENTED")
        self.assertEqual(s["by_mode"]["off"]["prompt_n_excluding_first"],1200)
        self.assertEqual(s["by_mode"]["on"]["prompt_n_excluding_first"],240)
        self.assertEqual(s["quality_status"],"PARITY_OF_WEAK_BASELINE")
        self.assertTrue(s["text_and_selection_identity"])
    def test_mismatch_is_explicit(self):
        r=self.example_report()
        row=r["blocks"][1]["rows"][2]
        row["raw_reply"]="999"
        s=bench.summarize(r)
        self.assertEqual(s["quality_status"],"QUALITY_OR_OUTPUT_DIVERGENCE_OBSERVED")
        self.assertEqual(len(s["differences"]),1)
    def test_unchanged_inputs_but_changed_render_detected(self):
        r=self.example_report()
        r["blocks"][1]["rows"][2]["rendered_prompt_sha256"]="different"
        with self.assertRaisesRegex(ValueError,"RENDERED_PROMPT"):
            bench.summarize(r)
    def test_same_scores_not_claimed_proof_of_understanding(self):
        r=self.example_report()
        self.assertEqual(bench.summarize(r)["scientific_generalization"],"NOT_DEMONSTRATED")


if __name__=="__main__": unittest.main()
