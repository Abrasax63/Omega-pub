"""Independent regression, falsification and budget checks for STRAT-002."""
from collections import Counter
from fractions import Fraction
import copy
import unittest

from strategic_methods_executable import METHODS, tasks, oracle, run_method, _euler_theorem, _euler_dfs
from strategic_method_selection import execute_order, execute_omega, evaluate, fit, fit_omega, best_fixed


class StrategyMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=tasks()
        cls.train=[t for t in cls.cases if t["partition"]=="train"]
        cls.held=[t for t in cls.cases if t["partition"]=="test"]

    def test_four_domains_and_no_overlapping_instances(self):
        self.assertEqual(len(self.cases),32)
        self.assertEqual(len(self.train),len(self.held))
        self.assertEqual(len(self.train),16)
        self.assertEqual(len({x["id"] for x in self.cases}),32)
        for domain in ("math","programming","data","documentation"):
            rows=[x for x in self.cases if x["domain"]==domain]
            self.assertEqual(len(rows),8)
            self.assertEqual(sum(x["partition"]=="train" for x in rows),4)
            self.assertEqual(sum(x["partition"]=="test" for x in rows),4)
        self.assertEqual(sum(oracle(x) for x in self.cases),16)

    def test_executable_methods_never_assert_unsupported_truth(self):
        for task in self.cases:
            truth="yes" if oracle(task) else "no"
            for method in METHODS:
                with self.subTest(task=task["id"],method=method):
                    result=run_method(task,method)
                    self.assertIn(result["observation"],("yes","no","unknown"))
                    self.assertIsInstance(result["certificate"],str)
                    self.assertTrue(result["certificate"])
                    if result["observation"]!="unknown":
                        self.assertEqual(result["observation"],truth)
                    if method=="refute":
                        self.assertNotEqual(result["observation"],"yes")
                    if task["simulated_outage"]==method:
                        self.assertEqual(result["observation"],"unknown")

    def test_mathematical_oracle_independent_paths_and_simpson_exact(self):
        for task in self.cases:
            if task["kind"]=="euler":
                self.assertEqual(_euler_theorem(task["params"]["edges"]),
                                 _euler_dfs(task["params"]["edges"]))
            if task["kind"]=="ratio":
                a,b=task["params"]["a"],task["params"]["b"]
                self.assertEqual(a[0]*b[1]>b[0]*a[1],Fraction(*a)>Fraction(*b))
        # True Simpson reversal and a non-reversal checked by exact fractions.
        for i,expected in ((1,True),(3,False),(5,True),(7,False)):
            d=next(x for x in self.cases if x["id"]=="D"+str(i))
            self.assertIs(oracle(d),expected)

    def test_training_only_and_equal_budget(self):
        fitdata=fit(self.train)
        self.assertEqual(len(fitdata["domain"]),4)
        self.assertEqual(len(fitdata["kind"]),7)
        for task in self.held:
            for order in (fitdata["global"],fitdata["domain"][task["domain"]],
                          fitdata["kind"][task["kind"]]):
                answer,trace=execute_order(task,order)
                self.assertLessEqual(len(trace),2)
                self.assertEqual(len({x["method"] for x in trace}),len(trace))
                if answer is not None:
                    self.assertEqual(answer, "yes" if oracle(task) else "no")
            answer,trace=execute_omega(task,fitdata["omega"][task["domain"]])
            self.assertLessEqual(len(trace),2)
            self.assertEqual(len({x["method"] for x in trace}),len(trace))
            if answer is not None:
                self.assertEqual(answer, "yes" if oracle(task) else "no")

    def test_method_change_after_unavailable_check_and_negative_truth(self):
        case=next(x for x in self.cases if x["id"]=="P5")
        result,trace=execute_order(case,("compute","source"))
        self.assertEqual(result,"yes")
        self.assertEqual([x["observation"] for x in trace],["unknown","yes"])
        # A fruitless search cannot establish a universal mathematical true.
        true_mod=next(x for x in self.cases if x["id"]=="M4")
        self.assertEqual(run_method(true_mod,"refute")["observation"],"unknown")
        self.assertEqual(run_method(true_mod,"formal")["observation"],"yes")

    def test_invariance_to_train_instance_order(self):
        a=fit(self.train)
        b=fit(list(reversed(self.train)))
        self.assertEqual(a["global"],b["global"])
        self.assertEqual(a["domain"],b["domain"])
        self.assertEqual(a["kind"],b["kind"])
        for domain in a["omega"]:
            self.assertEqual(a["omega"][domain]["policy"],
                             b["omega"][domain]["policy"])

    def test_no_score_from_posterior_without_actual_certificate(self):
        case=next(x for x in self.cases if x["id"]=="S4")
        # A source outage on a documentary question cannot be replaced by
        # a guessed label from prior outcomes.
        policy=fit_omega([x for x in self.train if x["domain"]=="documentation"],"test")
        answer,trace=execute_omega(case,policy)
        self.assertIsNone(answer)
        self.assertTrue(all(x["observation"]=="unknown" for x in trace))

    def test_summary_reproduces_conclusive_evidence_only(self):
        result=evaluate()
        self.assertEqual(result["status"],"PUBLIC_CONSTRUCTED_CALIBRATION_SYNTHETIC_OUTAGES")
        self.assertEqual(result["training_instances"],16)
        self.assertEqual(result["test_instances"],16)
        self.assertEqual(result["model_calls"],0)
        self.assertEqual(result["live_source_calls_in_replay"],0)
        for arm,s in result["summary"].items():
            self.assertEqual(s["cases"],16,arm)
            self.assertEqual(s["correct"]+s["wrong"]+s["abstain"],16)
            self.assertLessEqual(s["calls"],32)
            self.assertEqual(s["wrong"],0)
        self.assertEqual(len(result["records"]),80)
        import json
        print("STRAT002_CI_SUMMARY "+json.dumps({"summary":result["summary"],"fit":result["fit"]},
                                                sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    unittest.main()
