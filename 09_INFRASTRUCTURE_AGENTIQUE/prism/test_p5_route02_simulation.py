"""No model tests for P5 ROUTE-02, including adversarial controls."""
import copy
import unittest

from p5_route02_simulation import (
    N_EPISODES, N_CASES, REGIMES, POLICIES, BUDGET,
    PUBLIC_FIELDS, STATUS, episode, choose, expected_score_hundredths,
    _best_by_dp, _best_by_enumeration, _measures, run
)

class RoutingExperimentTests(unittest.TestCase):
    def test_hidden_labels_separated_and_reproducible(self):
        for regime in REGIMES:
            for episode_index in (0,1,25,127):
                visible,hidden=episode(regime,episode_index)
                visible_again,hidden_again=episode(regime,episode_index)
                self.assertEqual(visible,visible_again)
                self.assertEqual(hidden,hidden_again)
                self.assertEqual(len(visible),N_CASES)
                self.assertEqual(set(hidden),{p["id"] for p in visible})
                for row in visible:
                    self.assertEqual(set(row),PUBLIC_FIELDS)
                    self.assertEqual(row["mission_type"],"general")
                    self.assertNotIn("fault",str(row))
                    self.assertNotIn("truth",str(row))

    def test_omega_candidate_equals_strong_exact_baseline_for_every_episode(self):
        differences_to_fixed=0
        for regime in REGIMES:
            for i in range(N_EPISODES):
                visible,hidden=episode(regime,i)
                a=choose("omega_candidate",visible)
                b=choose("exact_knapsack",visible)
                self.assertEqual(a,b)
                self.assertEqual(a,_best_by_dp(visible))
                self.assertEqual(b,_best_by_enumeration(
                    visible,expected_score_hundredths))
                metrics=_measures(visible,hidden,a)
                self.assertLessEqual(metrics["cost_units"],BUDGET)
                self.assertEqual(len(a),len(set(a)))
                if a!=choose("fixed",visible):
                    differences_to_fixed+=1
        self.assertGreater(differences_to_fixed,0)

    def test_every_policy_honors_budget(self):
        for i in range(0,N_EPISODES,7):
            visible,hidden=episode("shifted",i)
            for p in POLICIES:
                if p=="hindsight_oracle":continue
                selected=choose(p,visible)
                self.assertLessEqual(_measures(
                    visible,hidden,selected)["cost_units"],BUDGET)

    def test_hidden_outcome_leak_is_rejected(self):
        visible,hidden=episode("calibrated",2)
        contaminated=copy.deepcopy(visible)
        contaminated[0]["is_fault"]=hidden[contaminated[0]["id"]]
        for name in ("exact_knapsack","omega_candidate","ratio"):
            with self.subTest(name=name),self.assertRaises(ValueError):
                choose(name,contaminated)
        bad=copy.deepcopy(visible)
        bad[0]["mission_type"]="computational"
        with self.assertRaises(ValueError):
            choose("omega_candidate",bad)
        bad=copy.deepcopy(visible)
        bad[0]["risk_percent"]=101
        with self.assertRaises(ValueError):
            choose("omega_candidate",bad)

    def test_hindsight_is_not_exposed_to_candidate_policies(self):
        public,_=episode("calibrated",0)
        with self.assertRaises(ValueError):
            choose("hindsight_oracle",public)

    def test_full_study_is_repeatable_and_falsifies_unique_claim(self):
        data=run()
        again=run()
        self.assertEqual(data["public_input_digest"],again["public_input_digest"])
        self.assertEqual(data["status"],STATUS)
        self.assertEqual(data["paid_api_calls"],0)
        self.assertEqual(data["model_generations"],0)
        self.assertFalse(data["private_data_used"])
        for regime in REGIMES:
            group=data["results"][regime]
            self.assertEqual(len(group["episodes"]),N_EPISODES)
            self.assertEqual(
                group["policy_totals"]["omega_candidate"],
                group["policy_totals"]["exact_knapsack"])
            pair=group["paired_comparisons_vs_omega"]["exact_knapsack"]
            self.assertEqual(pair,{"wins":0,"ties":N_EPISODES,"losses":0})
            self.assertEqual(
                group["policy_totals"]["none"]["realized_net_hundredths"],0)

if __name__=="__main__":unittest.main()
