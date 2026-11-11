"""Non-regression and scientific falsification of strategic route information."""
from collections import defaultdict
from fractions import Fraction
import copy
import json
import unittest

from intermediate_evidence_gateway import (
    ACTIONS,SPECIALISTS,cases,run_check,independent_verify,_actual_truth,
    _route_from_payload,ROUTE_TO_SPECIALIST,frozen_audit,
)
from intermediate_evidence_policy import (
    COST,BUDGET,fit,fit_certificate_dp,fit_conditional_enumeration,
    fit_fixed,fit_myopic,execute,evaluate,
)


class InformativeIntermediateEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=cases()
        cls.train=[r for r in cls.data if r["partition"]=="train"]
        cls.test=[r for r in cls.data if r["partition"]=="test"]

    def test_frozen_truth_balance_and_source_schemas(self):
        data=frozen_audit()
        self.assertEqual(len(self.data),64)
        self.assertEqual((len(self.train),len(self.test)),(32,32))
        self.assertEqual({x["id"] for x in self.train}&
                         {x["id"] for x in self.test},set())
        for partition in ("train","test"):
            self.assertEqual((data[partition]["yes"],data[partition]["no"]),(16,16))
            self.assertEqual(len(data[partition]["routes"]),4)
            for r,counts in data[partition]["routes"].items():
                self.assertEqual((counts["yes"],counts["no"],counts["outages"]),(4,4,1))
        self.assertEqual(sum(t["simulated_outage"] for t in self.test),4)

    def test_probe_is_nonconclusive_even_for_truth_balanced_route(self):
        for task in self.data:
            receipt=run_check(task,"probe")
            self.assertIn(receipt["outcome"],ROUTE_TO_SPECIALIST)
            self.assertIsNone(receipt["certificate"])
            self.assertTrue(independent_verify(task,receipt))
            self.assertFalse(receipt["outcome"] in ("yes","no"))
            for action in SPECIALISTS:
                value=run_check(task,action)
                self.assertTrue(independent_verify(task,value))
                if value["outcome"] in ("yes","no"):
                    self.assertEqual(value["outcome"]=="yes",_actual_truth(task))
                elif action!=ROUTE_TO_SPECIALIST[receipt["outcome"]]:
                    self.assertEqual(value["outcome"],"unknown:unsupported")
            self.assertTrue(any(
                run_check(task,a)["outcome"] in ("yes","no") for a in SPECIALISTS)
                or task["simulated_outage"])

    def test_forged_routing_evidence_is_rejected(self):
        task=self.data[0]
        receipt=run_check(task,"probe")
        fake=copy.deepcopy(receipt)
        fake["outcome"]="route:http" if receipt["outcome"]!="route:http" else "route:graph"
        self.assertFalse(independent_verify(task,fake))
        self.assertTrue(independent_verify(task,receipt))
        fake["outcome"]=receipt["outcome"]
        fake["certificate"]={"forged":True}
        self.assertFalse(independent_verify(task,fake))

    def test_certificate_gain_objective_and_matching_strong_baseline_on_train(self):
        a=fit_certificate_dp(self.train)
        b=fit_conditional_enumeration(self.train)
        self.assertEqual(Fraction(a["train_value"]),Fraction(b["train_value"]))
        self.assertEqual(a["policy"]["check_id"],"probe")
        self.assertEqual(b["policy"]["check_id"],"probe")
        self.assertEqual(COST,Fraction(1,50))
        self.assertEqual(BUDGET,2)
        for route,method in ROUTE_TO_SPECIALIST.items():
            self.assertEqual(a["policy"]["branches"][route]["check_id"],method)
            self.assertEqual(b["policy"]["branches"][route]["check_id"],method)

    def test_equal_cost_honest_decisions_no_hidden_truth(self):
        fitted=fit(self.train)
        for task in self.test:
            truth="yes" if _actual_truth(task) else "no"
            settings=[
                (fitted["A_fixed"],True,False),
                (fitted["B_specialists"],True,False),
                (fitted["C_omega"]["policy"],False,True),
                (fitted["D_certificate"]["policy"],False,False),
                (fitted["E_strong_conditional"]["policy"],False,False),
                (fitted["F_myopic"],True,False),
            ]
            for policy,is_fixed,is_legacy in settings:
                actual,trace=execute(task,policy,is_fixed=is_fixed,
                                     is_legacy=is_legacy)
                self.assertLessEqual(len(trace),2)
                self.assertEqual(len({t["action"] for t in trace}),len(trace))
                if actual is not None:
                    self.assertEqual(actual,truth)
                    self.assertIn(trace[-1]["outcome"],("yes","no"))
                    self.assertIsInstance(trace[-1]["certificate"],dict)
                else:
                    self.assertTrue(not trace or trace[-1]["outcome"] not in ("yes","no"))

    def test_order_invariance_on_training(self):
        forward=fit(self.train)
        backward=fit(self.train[::-1])
        for key in forward:
            if key=="C_omega":
                # Policy actions must be stable; different hypothesis IDs
                # may affect model-internal explored state count, not choices.
                self.assertEqual(forward[key]["policy"],backward[key]["policy"])
            else:self.assertEqual(forward[key],backward[key])

    def test_full_report_and_exact_per_case_parity(self):
        report=evaluate()
        self.assertEqual(report["training"],32)
        self.assertEqual(report["testing"],32)
        self.assertEqual(report["budget"],2)
        self.assertEqual(report["model_calls"],0)
        self.assertEqual(report["network_calls_in_replay"],0)
        self.assertEqual(len(report["traces"]),192)
        for name,s in report["scores"].items():
            self.assertEqual(s["cases"],32,name)
            self.assertEqual(s["correct"]+s["abstain"]+s["wrong"],32)
            self.assertEqual(s["wrong"],0)
            self.assertLessEqual(s["calls"],64)
            self.assertEqual(Fraction(s["objective"]),
                             Fraction(s["correct"])-5*s["wrong"]-COST*s["calls"])
        paired=defaultdict(dict)
        for row in report["traces"]:
            paired[row["id"]][row["arm"]]=row
        for case in paired.values():
            c=case["D_certificate"]
            e=case["E_strong_conditional"]
            self.assertEqual((c["decision"],c["trace"]),(e["decision"],e["trace"]))
        self.assertGreater(report["scores"]["D_certificate"]["correct"],
                           report["scores"]["B_specialists"]["correct"])
        self.assertEqual(report["scores"]["D_certificate"]["correct"],28)
        self.assertEqual(report["scores"]["D_certificate"]["calls"],64)
        print("STRAT004_CI_SUMMARY "+json.dumps(
            {"scores":report["scores"],"fit":report["fit_summary"]},
            sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    unittest.main()
