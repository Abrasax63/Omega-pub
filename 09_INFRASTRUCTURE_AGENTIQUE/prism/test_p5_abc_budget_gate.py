"""P5-ABC-001: refuse fake comparability and missing token telemetry.

All token-counting clients here are mocks. Zero real provider calls. This
does NOT count or measure tokens for an actual released model.
"""
from copy import deepcopy
from types import SimpleNamespace
import unittest

from p5_abc_budget_gate import (
    BudgetGateError,check_live_budget,sdk_token_counter
)
from p5_abc_fair_preflight import preflight


class FakeProvider:
    def __init__(self,counts=200):
        self.calls=[]
        self.counts=counts
        self.generation_calls=0

    def with_options(self,**opts):
        self.opts=opts
        return self

    @property
    def responses(self):
        outer=self
        class InputCount:
            def count(self,**params):
                outer.calls.append(params)
                if params.get("tools")!=[]:
                    raise AssertionError("tools allowed in token preflight")
                return SimpleNamespace(input_tokens=outer.counts)
        class Responses:
            input_tokens=InputCount()
            def create(self,**kwargs):
                outer.generation_calls+=1
                raise AssertionError("generation should never be called")
        return Responses()


class BudgetGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=preflight()

    def test_mock_endpoint_reports_no_generations_and_exact_144_counts(self):
        mock=FakeProvider()
        counter=sdk_token_counter(mock)
        summary=check_live_budget(
            self.packet,counter,model="provider/exact-snapshot-v1",
            total_token_cap=1600,output_token_cap=480)
        self.assertEqual(len(mock.calls),144)
        self.assertEqual(mock.generation_calls,0)
        self.assertEqual(summary["status"],
                         "INPUT_TOKENS_COUNTED_BUT_MODEL_GENERATION_NOT_RUN")
        self.assertEqual(summary["actual_model_generation_calls"],0)
        self.assertEqual(summary["token_counting_endpoint_calls"],144)
        self.assertEqual(summary["real_provider_confirmation"],
                         "caller-dependent_unverified_by_this_code")
        self.assertEqual(summary["tools_allowed"],0)
        self.assertEqual({s["sum_input_tokens"] for s
                          in summary["per_arm_distribution"].values()},
                         {48*200})
        self.assertTrue(all(x["model"]=="provider/exact-snapshot-v1"
                            for x in mock.calls))

    def test_differing_actual_prompt_counts_are_preserved(self):
        values=[]
        def counter(**params):
            value=len(params["input"])
            values.append(value)
            return value
        report=check_live_budget(
            self.packet,counter,model="provider/exact-snapshot-v1",
            total_token_cap=9000,output_token_cap=500)
        self.assertEqual(len(values),144)
        by_arm=report["per_arm_distribution"]
        self.assertNotEqual(by_arm["A"]["sum_input_tokens"],
                            by_arm["B"]["sum_input_tokens"])
        # These are mock character counts, NOT genuine tokenizer outputs.
        self.assertEqual(report["actual_model_generation_calls"],0)

    def test_missing_counts_or_too_small_cap_fail_closed(self):
        for count in (None,True,-1,1.2,"123"):
            with self.subTest(count=count),self.assertRaises(BudgetGateError):
                check_live_budget(
                    self.packet,lambda **p:count,
                    model="provider/exact-snapshot-v1",
                    total_token_cap=2000,output_token_cap=400)
        with self.assertRaises(BudgetGateError):
            check_live_budget(
                self.packet,lambda **p:1700,
                model="provider/exact-snapshot-v1",
                total_token_cap=2000,output_token_cap=400)

    def test_no_api_calls_if_case_packet_has_hidden_answer_or_changed_C_context(self):
        packet=deepcopy(self.packet)
        for row in packet["requests"]:
            if row["arm"]=="C":
                row["request"]["input"]["shared"]["truth"]=True
                break
        provider=FakeProvider()
        with self.assertRaises(BudgetGateError):
            check_live_budget(
                packet,sdk_token_counter(provider),
                model="provider/exact-snapshot-v1",
                total_token_cap=2000,output_token_cap=500)
        self.assertEqual(len(provider.calls),0)

    def test_unspecified_model_caps_or_client_rejected(self):
        for model in ("","TBD","unknown","mock","fake"):
            with self.subTest(model=model),self.assertRaises(BudgetGateError):
                check_live_budget(self.packet,lambda **p:1,model=model,
                                  total_token_cap=1000,output_token_cap=300)
        for budget,output in [(300,300),(0,1),("300",100),(300,0)]:
            with self.subTest(cap=(budget,output)),self.assertRaises(BudgetGateError):
                check_live_budget(
                    self.packet,lambda **p:1,model="provider/exact-snapshot-v1",
                    total_token_cap=budget,output_token_cap=output)
        with self.assertRaises(BudgetGateError):
            sdk_token_counter(object())

    def test_error_response_missing_token_count_cannot_be_silently_accepted(self):
        provider=FakeProvider()
        provider.counts=None
        with self.assertRaises(BudgetGateError):
            check_live_budget(
                self.packet,sdk_token_counter(provider),
                model="provider/exact-snapshot-v1",
                total_token_cap=1000,output_token_cap=300)
        self.assertEqual(provider.generation_calls,0)

if __name__=="__main__":
    unittest.main()
