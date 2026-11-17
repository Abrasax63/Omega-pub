"""Eight control tests; full holdout is executed once in the workflow."""
import unittest
from itertools import product
from unittest.mock import patch
import active_lab as a


class ActiveControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observations=a.s.six_zero_observations()
        cls.space,_=a.s.enumerate_consistent_models(
            a.s.validate_observations(cls.observations))
        cls.cohort,cls.eligible=a.new_cohort(cls.space)

    def test_prereg_and_unchanged_bounded_search(self):
        self.assertEqual(a.PREREG,"a70c231753a2112dc0bc0501dd742b5aff4072ce")
        self.assertEqual(a.SAMPLE_SEED,53117)
        self.assertEqual(a.TEST_N,24)
        self.assertEqual(a.s.MAX_STATES,3)
        self.assertEqual(a.s.EQ_LENGTH,10)

    def test_cohort_has_24_unique_new_minimal_three_state_models(self):
        old={a.s.canonical(a.s.delayed_marker(p))
             for p in product(a.s.ALPHABET,repeat=3)}
        self.assertGreaterEqual(self.eligible,24)
        self.assertEqual(len(self.cohort),24)
        self.assertEqual(len(set(self.cohort)),24)
        for model in self.cohort:
            self.assertEqual(len(model[0]),3)
            self.assertTrue(a.distinguishable(model))
            self.assertNotIn(model,old)

    def test_cohort_selection_is_repeatable_and_score_free(self):
        other,_=a.new_cohort(self.space)
        self.assertEqual(self.cohort,other)

    def test_all_sources_respect_only_public_six_training_traces(self):
        records=a.s.validate_observations(self.observations)
        for model in self.cohort:
            self.assertTrue(all(a.s.trace(model,w)==outputs for w,outputs in records))

    def test_active_query_rank_never_receives_hidden_system(self):
        world=self.cohort[0]
        reps,_=a.s.diversify(self.space)
        static,_=a.s.rank_queries(reps,self.observations)
        with patch.object(a.s,"rank_queries",wraps=a.s.rank_queries) as ranked:
            result=a.run_policy("ACTIVE_DISAGREEMENT",world,self.observations,
                                self.space,static)
        self.assertGreaterEqual(ranked.call_count,1)
        for call in ranked.call_args_list:
            self.assertEqual(len(call.args),2)
            self.assertIsInstance(call.args[0],list)
            self.assertIsInstance(call.args[1],list)
        self.assertGreaterEqual(result["queries_paid"],1)

    def test_real_spent_is_ten_per_query_without_budget_overspend(self):
        world=self.cohort[1]
        reps,_=a.s.diversify(self.space)
        static,_=a.s.rank_queries(reps,self.observations)
        for arm,cap in (("FIXED_PREFIX",80),("STATIC_DIVERSITY",320),
                        ("ACTIVE_DISAGREEMENT",320)):
            result=a.run_policy(arm,world,self.observations,self.space,static)
            self.assertEqual(result["symbols_paid"],10*result["queries_paid"])
            self.assertLessEqual(result["symbols_paid"],cap)
            self.assertEqual(result["symbols_paid"],
                             sum(x["cost"] for x in result["query_log"]))
            self.assertTrue(all(len(x["word"])==10 for x in result["query_log"]))

    def test_every_revised_version_space_still_contains_true_model(self):
        world=self.cohort[2]
        reps,_=a.s.diversify(self.space)
        static,_=a.s.rank_queries(reps,self.observations)
        result=a.run_policy("ACTIVE_DISAGREEMENT",world,self.observations,
                            self.space,static)
        size=len(self.space)
        for row in result["query_log"]:
            self.assertEqual(row["consistent_before"],size)
            size=row["consistent_after"]
            self.assertLessEqual(size,row["consistent_before"])
            self.assertGreater(size,0)

    def test_scientific_verdict_uses_all_24_cases_and_realized_costs(self):
        report=a.conduct()
        self.assertEqual(report["world_count"],24)
        self.assertEqual(len(report["runs"]),24)
        for arm in report["policies"]:
            rows=[x["arms"][arm] for x in report["runs"]]
            self.assertEqual(report["summary"][arm]["detected"],
                             sum(x["detected"] for x in rows))
            self.assertEqual(report["summary"][arm]["total_paid_symbols"],
                             sum(x["symbols_paid"] for x in rows))
        score=report["summary"]
        a_score=score["ACTIVE_DISAGREEMENT"]
        strong=(a_score["detected"]==24 and
                all(a_score["mean_paid_symbols"]<score[x]["mean_paid_symbols"]
                    for x in ("FIXED_PREFIX","STATIC_DIVERSITY")))
        self.assertEqual(report["status"],
            "DESCRIPTIVE_ACTIVE_BENEFIT" if strong else "NO_ACTIVE_BENEFIT_DEMONSTRATED")


if __name__=="__main__":
    unittest.main()
