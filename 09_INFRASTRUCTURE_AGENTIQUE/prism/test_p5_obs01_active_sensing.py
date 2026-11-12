"""OBS-01: independent exact policies, provenance and adverse observability tests."""
import unittest
from fractions import Fraction
from unittest.mock import patch

import p5_obs01_active_sensing as e

class ObservabilityActiveDecisionTests(unittest.TestCase):
    def setUp(self):
        self.b=frozenset(e.STATES)

    def test_known_phantom_invisible_to_all_endpoint_deltas(self):
        x=e.phantom_counterexample()
        self.assertEqual(x["T"],[0,2,2])
        self.assertEqual(x["pi"],[0,0,1])
        self.assertTrue(x["locally_possible"])
        self.assertEqual(x["prefix_survivor_counts"],[2,1,0])
        self.assertFalse(x["realizable"])
        self.assertTrue(x["endpoint_delta_h_empty_h_1_through_20"])

    def test_exact_end_of_belief_and_one_probe_cannot_diagnose(self):
        self.assertEqual(e.terminal(self.b),("ABSTAIN",Fraction(1,20)))
        for p in e.PROBES:
            subsets=e.branches(self.b,p)
            self.assertEqual(
                {e.terminal(s)[0] for s in subsets.values()},{"ABSTAIN"})
            self.assertLess(e.expected_terminal_after_one(self.b,p),
                            Fraction(1,20))
        self.assertEqual(e.independent_tree_enumeration(self.b,0),
                         Fraction(1,20))
        self.assertEqual(e.independent_tree_enumeration(self.b,1),
                         Fraction(1,20))
        self.assertEqual(e.set_dp(self.b,e.PROBES,1)[1],Fraction(1,20))

    def test_two_probe_complementarity_but_no_unique_omega_benefit(self):
        exact=e.set_dp(self.b,e.PROBES,2)
        self.assertEqual(exact,(("PROBE","U"),Fraction(19,25)))
        self.assertEqual(e.independent_tree_enumeration(self.b,2),
                         Fraction(19,25))
        summary=e.summarize()
        self.assertEqual(summary["bayesian_dp_value_exact"],"19/25")
        for name in ("exact_bayesian_dp","omega_observable_candidate",
                     "fixed_u_then_v"):
            self.assertEqual(summary["policy_results"][name]["mean_net_exact"],
                             "19/25")
        self.assertEqual(summary["policy_results"]["myopic_decision_voi"]["mean_net_exact"],
                         "1/20")
        self.assertEqual(summary["policy_results"]["no_probe"]["mean_net_exact"],
                         "1/20")
        self.assertEqual(summary["policy_results"]["entropy_greedy"]["mean_net_exact"],
                         "-3/25")

    def test_nuisance_has_more_microstate_entropy_but_no_decision_gain(self):
        self.assertAlmostEqual(e.entropy_micro(self.b,"Z"),2.0)
        self.assertAlmostEqual(e.entropy_micro(self.b,"U"),1.0)
        self.assertAlmostEqual(e.entropy_micro(self.b,"V"),1.0)
        for secret in e.STATES:
            result=e.run_one("entropy_greedy",secret)
            self.assertEqual(result["probes"][0],"Z")
            self.assertEqual(result["terminal_decision"],"ABSTAIN")

    def test_every_action_only_reveals_its_own_observation(self):
        for secret in e.STATES:
            x=e.run_one("omega_observable_candidate",secret)
            self.assertEqual(x["probes"],["U","V"])
            self.assertEqual(len(x["observations"]),2)
            self.assertEqual(x["observations"][0]["survivors_before"],16)
            self.assertEqual(x["observations"][0]["survivors_after"],8)
            self.assertEqual(x["observations"][1]["survivors_after"],4)
            self.assertEqual(x["net_reward"],Fraction(19,25))
            self.assertEqual(x["final_survivors"],4)
            self.assertEqual(x["true_target_evaluator_only"],
                             int(x["terminal_decision"][-1]))

    def test_impossible_observations_refused_and_no_repeated_probe(self):
        after_u=e.survivors(self.b,"U",1)
        self.assertEqual(len(after_u),8)
        with self.assertRaises(ValueError):
            e.survivors(after_u,"U",0)
        with self.assertRaises(ValueError):
            e.survivors(after_u,"Z",99)
        with self.assertRaises(ValueError):
            e.survivors(frozenset(),"U",0)
        with self.assertRaises(ValueError):
            e.survivors(after_u,"INVALID",1)
        with self.assertRaises(ValueError):
            e.survivors(after_u,"V","1")

    def test_fully_known_initial_state_needs_no_probe_for_bayesian_policy(self):
        for secret in e.STATES:
            for p in ("exact_bayesian_dp","omega_observable_candidate",
                      "myopic_decision_voi"):
                x=e.run_one(p,secret,initial={secret})
                self.assertEqual(x["probes"],[])
                self.assertEqual(x["net_reward"],Fraction(1))

    def test_16_by_6_exhaustive_rollouts_all_under_budget(self):
        r=e.summarize()
        self.assertEqual(r["world_size"],16)
        self.assertEqual(r["max_probes"],2)
        self.assertEqual(r["paid_api_calls"],0)
        self.assertEqual(r["model_generations"],0)
        self.assertEqual(len(r["policy_results"]),6)
        for p,data in r["policy_results"].items():
            self.assertEqual(len(data["all_state_runs"]),16)
            for run in data["all_state_runs"]:
                self.assertLessEqual(len(run["probes"]),2)
                self.assertEqual(len(set(run["probes"])),len(run["probes"]))
                self.assertIn(run["terminal_decision"],
                              ("ABSTAIN","ANSWER_0","ANSWER_1"))

    def test_candidate_planner_does_not_see_secret_or_answer(self):
        # The planner is a static explainable P1; no true-state field.
        with patch.object(e,"hidden_label",
                          side_effect=AssertionError("label leaked into planning")):
            with patch.object(e,"set_dp",return_value=(("STOP",None),Fraction(1,20))):
                # Run patched choose until terminal evaluation, at which point
                # the evaluator is naturally allowed to consult true label.
                plan_calls=[]
                real=e.plan_mission
                def record(mission):
                    self.assertNotIn("secret",str(mission))
                    self.assertNotIn("true_target",str(mission))
                    plan_calls.append(mission)
                    return real(mission)
                with patch.object(e,"plan_mission",side_effect=record):
                    with self.assertRaises(AssertionError):
                        e.run_one("omega_observable_candidate",e.STATES[0])
                self.assertEqual(len(plan_calls),1)

if __name__=="__main__":
    unittest.main()
