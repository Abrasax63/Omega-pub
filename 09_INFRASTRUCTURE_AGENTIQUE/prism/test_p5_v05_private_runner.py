"""P5V05 candidate private execution fail-closed tests. NO actual provider calls.

All fixture cases live in TemporaryDirectory; they are deliberately *not*
the real private cases. The real answer file is not imported or read here.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from p5_v05_private_runner import (
    ARMS,REPS,EXP,EXPECTED_COUNTS,build_triplet,
    validate_inputs,private_schedule,preflight,execute
)


def dummy_case(typ,num):
    return {
        "case_id":f"P5V05-{typ}-{num:02d}",
        "mission_type":{
            "FORMAL":"mathematical","CRT":"computational",
            "DOC":"documentary","DATA":"computational"}[typ],
        "question":f"Question fictive non secrète {typ}-{num} ?",
        "documents":[{"id":"DOC-1","kind":"exemple","text":"Constat fictif."}],
    }

def write_dummy(folder):
    cases=[dummy_case(typ,i) for typ in EXPECTED_COUNTS
           for i in range(1,EXPECTED_COUNTS[typ]+1)]
    raw={"protocol":"P5V05_CANDIDATE_PRIVATE",
         "status":"candidate_not_independently_vetted",
         "created":"2026-11-11","cases":cases}
    inputs=folder/"dummy_inputs.json"
    inputs.write_text(json.dumps(raw,sort_keys=True,indent=2)+"\n",
                      encoding="utf-8")
    manifest={"protocol":"P5V05_CANDIDATE",
              "status":"PRIVATE_CANDIDATE_NOT_BLIND_NOT_INDEPENDENTLY_VETTED",
              "case_count":16,"expected_arms":["A","B","C"],
              "expected_repetitions":2,"expected_generations":96,
              "prompt_only_sha256":sha256(inputs.read_bytes()).hexdigest()}
    path=folder/"dummy_manifest.json"
    path.write_text(json.dumps(manifest),encoding="utf-8")
    return cases,inputs,path,manifest


def rate_card(model="provider/explicit-test-model"):
    return {
        "model":model,"currency":"USD","processing_mode":"standard",
        "input_usd_per_million":"1.00","output_usd_per_million":"5.00",
        "source_url":"https://platform.openai.com/pricing",
        "checked_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
    }


class FakeOpenAI:
    def __init__(self):
        self.generations=0
        self.counts=0
        self.last_options=[]

    def with_options(self,**opts):
        self.last_options.append(opts)
        return self

    @property
    def responses(self):
        outer=self
        class Count:
            def count(self,**params):
                if params["tools"]!=[]:raise AssertionError("tools not prohibited")
                outer.counts+=1
                return SimpleNamespace(input_tokens=350)
        class Responses:
            input_tokens=Count()
            def create(self,**params):
                if params["tools"]!=[] or params["store"] is not False:
                    raise AssertionError("incorrect provider request")
                if params["truncation"]!="disabled":
                    raise AssertionError("prompt truncation hides information")
                outer.generations+=1
                return SimpleNamespace(
                    status="completed",model=params["model"],
                    id=f"mock-response-{outer.generations}",
                    output_text="Réponse simulée, pas une preuve de qualité.",
                    usage=SimpleNamespace(input_tokens=350,output_tokens=40))
        return Responses()


class P5V05PrivateRunnerTests(unittest.TestCase):
    def test_pairwise_information_parity_with_actual_planner(self):
        with tempfile.TemporaryDirectory() as d:
            cases,src,mf,manifest=write_dummy(Path(d))
            loaded,grounded=validate_inputs(src,mf)
            self.assertEqual(grounded["prompt_only_sha256"],
                             manifest["prompt_only_sha256"])
            self.assertEqual(len(loaded),16)
            packet=preflight(loaded,grounded)
            self.assertEqual(packet["status"],"PREFLIGHT_ONLY")
            self.assertEqual(packet["provider_generations"],0)
            self.assertEqual(packet["required_generations"],96)
            self.assertFalse(packet["independently_vetted"])
            for case in loaded:
                abc=build_triplet(case)
                self.assertEqual(set(abc),set(ARMS))
                self.assertEqual(
                    abc["A"]["input"]["shared"],
                    abc["B"]["input"]["shared"])
                self.assertEqual(
                    abc["B"]["input"]["shared"],
                    abc["C"]["input"]["shared"])
                self.assertNotEqual(abc["B"]["input"]["strategy"],
                                    abc["C"]["input"]["strategy"])

    def test_schedule_has_isolated_repetitions_and_full_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            cases,_,_,_=write_dummy(Path(d))
            a=private_schedule(cases,20261111)
            b=private_schedule(cases,20261111)
            self.assertEqual(a,b)
            self.assertEqual(len(a),96)
            self.assertEqual(len({(x["case_id"],x["repetition"],x["arm"])
                                  for x in a}),96)
            for i in range(0,len(a),3):
                chunk=a[i:i+3]
                self.assertEqual(len({x["case_id"] for x in chunk}),1)
                self.assertEqual(len({x["repetition"] for x in chunk}),1)
                self.assertEqual({x["arm"] for x in chunk},set(ARMS))

    def test_full_96_mock_generations_durable_and_no_replay(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,_,_,manifest=write_dummy(folder)
            client=FakeOpenAI()
            output=folder/"private-outputs"
            summary=execute(
                cases,manifest,client=client,
                model="provider/explicit-test-model",
                total_token_cap=1024,
                output_token_cap=400,
                max_generation_calls=96,
                allow_billable_api=True,
                output_dir=output,pricing=rate_card(),
                max_estimated_usd="1.00",seed=20261111)
            self.assertEqual(summary["status"],"RUN_UNGRADED")
            self.assertEqual(summary["provider_generations"],96)
            self.assertEqual(summary["measured_input_tokens"],96*350)
            self.assertEqual(summary["measured_output_tokens"],96*40)
            self.assertEqual(client.generations,96)
            self.assertEqual(summary["per_arm"]["A"]["generations"],32)
            self.assertEqual(summary["per_arm"]["B"]["generations"],32)
            self.assertEqual(summary["per_arm"]["C"]["generations"],32)
            self.assertEqual(summary["cost_status"],
                             "ESTIMATED_FROM_MODEL_TOKENS_NOT_BILLED_USD")
            self.assertIsNone(summary["billed_usd"])
            self.assertAlmostEqual(float(summary["estimated_model_usd"]),0.0528)
            self.assertEqual(client.counts,96)
            self.assertTrue((output/"dispatch_events.jsonl").exists())
            self.assertEqual(len(list(output.glob("*.json"))),98)
            # 96 per-call durable payloads plus start + summary.
            with self.assertRaises(FileExistsError):
                execute(cases,manifest,client=client,
                        model="provider/explicit-test-model",
                        total_token_cap=1024,output_token_cap=400,
                        max_generation_calls=96,allow_billable_api=True,
                        output_dir=output,pricing=rate_card(),
                max_estimated_usd="1.00",seed=20261111)
            self.assertEqual(client.generations,96)

    def test_missing_caps_or_provider_refused_before_any_generation(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,_,_,manifest=write_dummy(folder)
            client=FakeOpenAI()
            opts={"model":"provider/explicit-test-model",
                  "total_token_cap":1000,"output_token_cap":300,
                  "max_generation_calls":96,"allow_billable_api":True,
                  "output_dir":folder/"never-created",
                  "pricing":rate_card(),"max_estimated_usd":"1.00"}
            for mutation in (
                {"allow_billable_api":False},{"max_generation_calls":95},
                {"model":None},{"output_token_cap":1200},
                {"total_token_cap":None},
                {"pricing":None},{"max_estimated_usd":None},
                {"client":object()},
            ):
                with self.subTest(mutation=mutation),self.assertRaises(
                    (ValueError,TypeError)):
                    execute(cases,manifest,client=mutation.pop("client",client),
                            **{**opts,**mutation})
            self.assertEqual(client.generations,0)
            self.assertEqual(client.counts,0)

    def test_insufficient_budget_for_any_one_prompt_aborts_before_generations(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,_,_,manifest=write_dummy(folder)
            client=FakeOpenAI()
            with self.assertRaises(RuntimeError):
                execute(cases,manifest,client=client,
                        model="provider/explicit-test-model",
                        total_token_cap=500,output_token_cap=200,
                        max_generation_calls=96,allow_billable_api=True,
                        output_dir=folder/"blocked",
                        pricing=rate_card(),max_estimated_usd="1.00",seed=123)
            self.assertEqual(client.generations,0)
            self.assertFalse((folder/"blocked").exists())

    def test_usd_budget_rejection_prevents_all_generations(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,_,_,manifest=write_dummy(folder)
            client=FakeOpenAI()
            with self.assertRaises(ValueError):
                execute(cases,manifest,client=client,
                        model="provider/explicit-test-model",
                        total_token_cap=1024,output_token_cap=400,
                        max_generation_calls=96,allow_billable_api=True,
                        output_dir=folder/"blocked-money",
                        pricing=rate_card(),max_estimated_usd="0.22",seed=123)
            self.assertEqual(client.generations,0)
            self.assertEqual(client.counts,96)
            self.assertFalse((folder/"blocked-money").exists())

    def test_usd_pricing_mismatch_fails_before_counting_or_generation(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,_,_,manifest=write_dummy(folder)
            client=FakeOpenAI()
            with self.assertRaises(ValueError):
                execute(cases,manifest,client=client,
                        model="provider/explicit-test-model",
                        total_token_cap=1024,output_token_cap=400,
                        max_generation_calls=96,allow_billable_api=True,
                        output_dir=folder/"blocked-model",
                        pricing=rate_card("wrong-model"),
                        max_estimated_usd="1.00",seed=123)
            self.assertEqual(client.generations,0)
            self.assertEqual(client.counts,0)

    def test_input_hash_breaks_on_single_character_change_and_rejects_hidden_keys(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            cases,src,mf,_=write_dummy(folder)
            raw=json.loads(src.read_text())
            raw["cases"][0]["question"]+=" perturbation"
            src.write_text(json.dumps(raw),encoding="utf-8")
            with self.assertRaises(ValueError):validate_inputs(src,mf)
            cases[0]["gold"]=True
            with self.assertRaises(ValueError):build_triplet(cases[0])
            # More direct validation is performed when loading the file.

if __name__=="__main__":
    unittest.main()
