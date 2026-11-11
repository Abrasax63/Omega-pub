"""Independent regressions for the pre-registered CERT-001 experiment."""
from collections import defaultdict
from fractions import Fraction
import copy
import json
import unittest

from certification_methods_v01 import (
    cases, truth, run_method, outcome_key, independent_checks, HEADER_NORM,
)
from certificate_aware_selector_v01 import (
    COST, METHODS, MAX_TRIES, fit, fit_certified,
    fit_conditioned, best_fixed, _run_policy, execute_fixed,
    execute_conditioned, execute_legacy, evaluate,
)
from strategic_methods_executable import tasks as prior_cases


class CertificateFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=cases()
        cls.train=[x for x in cls.rows if x["partition"]=="train"]
        cls.holdout=[x for x in cls.rows if x["partition"]=="test"]

    def test_frozen_new_cases_and_nonoverlap_with_pr34(self):
        self.assertEqual((len(self.rows),len(self.train),len(self.holdout)),(48,24,24))
        self.assertEqual(len({t["id"] for t in self.rows}),48)
        self.assertEqual({x["domain"] for x in self.rows},
                         {"math","programming","data","documentation"})
        for domain in ("math","programming","data","documentation"):
            self.assertEqual(sum(x["domain"]==domain for x in self.train),6)
            self.assertEqual(sum(x["domain"]==domain for x in self.holdout),6)
        for kind in {x["kind"] for x in self.rows}:
            old={json.dumps(x["params"],sort_keys=True)
                 for x in prior_cases() if x["kind"]==kind}
            recent=[json.dumps(x["params"],sort_keys=True)
                    for x in self.rows if x["kind"]==kind]
            self.assertEqual(len(recent),len(set(recent)))
            self.assertFalse(old.intersection(recent))
        self.assertEqual(sum(x["simulated_outage"] is not None for x in self.rows),14)

    def test_all_192_executable_method_checks_are_sound(self):
        self.assertEqual(independent_checks(),{"checked_cases":48,"validated_methods":192})
        for task in self.rows:
            for method in METHODS:
                receipt=run_method(task,method)
                self.assertIn(receipt["observation"],("yes","no","unknown"))
                key=outcome_key(receipt)
                if receipt["observation"]!="unknown":
                    self.assertIs(receipt["observation"]=="yes",truth(task))
                    self.assertEqual(key,receipt["observation"])
                if method=="refute":
                    self.assertNotEqual(receipt["observation"],"yes")
                if method==task["simulated_outage"]:
                    self.assertEqual(key,"unknown:outage")

    def test_rfc9110_header_scope_and_outage(self):
        docs=[x for x in self.rows if x["kind"]=="header"]
        self.assertEqual(len(docs),12)
        truth_values=[truth(x) for x in docs]
        self.assertGreater(sum(truth_values),0)
        self.assertLess(sum(truth_values),12)
        assert HEADER_NORM.endswith("13.1.3")
        for task in docs:
            if task["simulated_outage"]=="source":
                self.assertEqual(run_method(task,"source")["observation"],"unknown")
            else:
                self.assertEqual(run_method(task,"source")["observation"]=="yes",truth(task))
            for m in ("formal","compute","refute"):
                self.assertEqual(run_method(task,m)["observation"],"unknown")

    def test_heldout_true_universal_is_not_proven_by_bounded_search(self):
        task=next(x for x in self.holdout if x["id"]=="CERT-MATH-mod-03")
        self.assertTrue(truth(task))
        self.assertEqual(run_method(task,"compute")["observation"],"unknown")
        self.assertEqual(run_method(task,"refute")["observation"],"unknown")
        self.assertEqual(run_method(task,"formal")["observation"],"yes")

    def test_equal_information_conditional_baseline_matches_finite_dp_training(self):
        fitdata=fit(self.train)
        for kind in fitdata["C_certificate"]:
            d=fitdata["D_conditioned"][kind]
            c=fitdata["C_certificate"][kind]
            self.assertEqual(Fraction(c["expected_utility"]),
                             Fraction(d["expected_utility"]),kind)
        self.assertEqual(COST,Fraction(1,20))

    def test_no_test_label_needed_to_fit_certificate_or_strong_baseline(self):
        # Neither certificate fitter nor conditional fitter imports a label
        # oracle; counterfactually reordering examples must change nothing.
        bykind=defaultdict(list)
        for t in self.train:bykind[t["kind"]].append(t)
        for kind,subset in bykind.items():
            a=fit_certified(subset)
            b=fit_certified(list(reversed(subset)))
            self.assertEqual(a,b,kind)
            self.assertEqual(fit_conditioned(subset),
                             fit_conditioned(list(reversed(subset))))
            self.assertEqual(best_fixed(subset),
                             best_fixed(list(reversed(subset))))

    def test_same_budget_sound_answers_and_losses_for_every_strategy(self):
        report=evaluate()
        self.assertEqual(report["train_cases"],24)
        self.assertEqual(report["test_cases"],24)
        self.assertEqual(report["budget"],2)
        self.assertEqual(report["llm_calls"],0)
        self.assertEqual(report["remote_calls_in_replay"],0)
        self.assertEqual(len(report["traces"]),120)
        for arm,counts in report["scores"].items():
            self.assertEqual(counts["cases"],24,arm)
            self.assertEqual(counts["wrong"],0,arm)
            self.assertEqual(counts["correct"]+counts["abstain"],24,arm)
            self.assertLessEqual(counts["calls"],48,arm)
            self.assertEqual(
                Fraction(counts["objective_score"]),
                Fraction(counts["correct"]) - 5*counts["wrong"] - COST*counts["calls"])
        for row in report["traces"]:
            trace=row["trace"]
            self.assertLessEqual(len(trace),2)
            self.assertEqual(len({r["method"] for r in trace}),len(trace))
            if row["answer"] is not None:
                self.assertEqual(row["answer"],row["truth"])
                self.assertEqual(row["answer"],trace[-1]["outcome"])
            else:
                self.assertTrue(not trace or trace[-1]["outcome"].startswith("unknown:"))
        print("CERT001_CI_SUMMARY "+json.dumps({
            "scores":report["scores"],"policies":report["policy_summary"]},
            sort_keys=True,ensure_ascii=False))

    def test_individual_calls_do_not_know_future_outage(self):
        p=fit(self.train)
        target=self.holdout[0]
        kind=target["kind"]
        original_policy=p["C_certificate"][kind]
        altered=copy.deepcopy(target)
        altered["simulated_outage"]=None if target["simulated_outage"] else "formal"
        # Fitting observes only training, not the current task.
        self.assertEqual(p["C_certificate"][kind],original_policy)
        for row in (target,altered):
            answer,trace=_run_policy(row,original_policy,p["training"][kind])
            self.assertLessEqual(len(trace),2)
            if answer is not None:
                self.assertEqual(answer,"yes" if truth(row) else "no")


if __name__=="__main__":
    unittest.main()
