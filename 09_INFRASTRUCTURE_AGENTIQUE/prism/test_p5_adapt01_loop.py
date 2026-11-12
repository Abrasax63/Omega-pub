"""P5-ADAPT-01 regression tests: no provider, real observable-only feedback."""
import unittest
from unittest.mock import patch
import p5_adapt01_loop as m

class Adapt01Tests(unittest.TestCase):
    def test_preregistered_world_and_reproducibility(self):
        self.assertEqual(m.EXPERIMENT,"P5-ADAPT-01")
        self.assertEqual(m.EPISODES,32)
        self.assertEqual(m.HORIZON,180)
        self.assertEqual(len(m.REGIMES),4)
        for regime in m.REGIMES:
            for seed in (0,1,31):
                first=m.evaluate(regime,seed,"omega_candidate",keep_trace=True)
                second=m.evaluate(regime,seed,"omega_candidate",keep_trace=True)
                self.assertEqual(first,second)
                self.assertEqual(len(first["trace_observed_only"]),m.HORIZON)
                self.assertGreaterEqual(first["pseudo_regret"],0)
                self.assertEqual(
                    first["verifications"]+first["abstentions"]+
                    sum(x["action"]=="DIRECT" for x in first["trace_observed_only"]),
                    m.HORIZON,
                )
                self.assertAlmostEqual(first["verification_cost"],
                                       0.2*first["verifications"])

    def test_policy_never_receives_hidden_regime_or_probabilities(self):
        for name in m.POLICIES:
            p=m.Policy(name)
            # Forbid access to the hidden generator even indirectly.
            with patch.object(m,"_world_probabilities",
                              side_effect=AssertionError("private oracle leak")):
                action=p.choose(0)
                self.assertIn(action,m.ACTIONS)
                p.observe(0,action,0.08 if action=="ABSTAIN" else 1.0)
                self.assertEqual(len(p.all_observed),1)
            self.assertNotIn("regime",vars(p))
            self.assertNotIn("probabilities",vars(p))

    def test_change_detector_responds_to_observed_feedback_only(self):
        p=m.Policy("omega_candidate")
        # Two blocks of outcomes for the same selected action; no oracle.
        for t in range(12):
            p.observe(t,"DIRECT",-2.0 if t<6 else 1.0)
        self.assertEqual(p.alarms,1)
        self.assertEqual(p.mode,"fast")
        self.assertEqual(p.mode_switches,1)
        self.assertEqual(len(p.snapshot),12)
        self.assertEqual(len(p.memory),1)
        self.assertEqual(p.last_event,"change_alarm_start_fast")
        for t in range(12,30):
            p.observe(t,"DIRECT",-2.0)
        self.assertEqual(p.rollbacks,1)
        self.assertEqual(p.mode,"stable")
        self.assertEqual(p.mode_switches,2)
        self.assertEqual(p.last_event,"rollback_to_prechange_checkpoint")
        self.assertEqual(p.history,p.snapshot)
        self.assertEqual(len(p.all_observed),30) # audit trail not rolled back

    def test_rollback_ablation_is_genuine(self):
        p=m.Policy("omega_no_rollback")
        for t in range(12):
            p.observe(t,"DIRECT",-2.0 if t<6 else 1.0)
        for t in range(12,30):
            p.observe(t,"DIRECT",-2.0)
        self.assertEqual(p.alarms,1)
        self.assertEqual(p.rollbacks,0)
        self.assertEqual(p.mode,"stable")
        self.assertEqual(len(p.history),18)
        self.assertEqual(len(p.all_observed),30)

    def test_memory_ablation_does_not_use_archive_for_priors(self):
        p=m.Policy("omega_no_memory")
        for t in range(12):
            p.observe(t,"DIRECT",-2.0 if t<6 else 1.0)
        self.assertEqual(p.mode,"fast")
        self.assertTrue(p.memory)
        # The memory is logged in this ablation, but NEVER fed to choice.
        with patch.object(p,"_memory_prior",
                          side_effect=AssertionError("memory prior leaked")):
            self.assertIn(p.choose(12),m.ACTIONS)

    def test_strong_controls_are_real_distinct_policies(self):
        self.assertEqual(m.Policy("fixed_direct").choose(0),"DIRECT")
        self.assertEqual(m.Policy("fixed_verify").choose(0),"VERIFY")
        self.assertEqual(m.Policy("fixed_abstain").choose(0),"ABSTAIN")
        sample={}
        for name in m.POLICIES:
            result=m.evaluate("abrupt",0,name)
            sample[name]=(result["realized_utility"],result["observed_trace_sha256"])
            self.assertGreaterEqual(result["pseudo_regret"],0)
        self.assertGreater(len(set(sample.values())),3)

    def test_world_is_observed_only_in_evaluator_and_rewards_are_bounded(self):
        self.assertAlmostEqual(m._reward("stationary",0,0,"ABSTAIN"),.08)
        for regime in m.REGIMES:
            for t in (0,44,59,60,90,119,120,135,179):
                rewards=m._expected_rewards(regime,1,t)
                self.assertEqual(set(rewards),set(m.ACTIONS))
                self.assertAlmostEqual(rewards["ABSTAIN"],.08)
                for action in m.ACTIONS:
                    gain=m._reward(regime,1,t,action)
                    self.assertTrue(-2.2<=gain<=1.0)

if __name__=="__main__":
    unittest.main()
