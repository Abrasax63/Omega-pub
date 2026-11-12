"""ADAPT-02 deterministic no-provider adversarial protocol tests."""
import unittest
from unittest.mock import patch
import p5_adapt01_loop as world
import p5_adapt02_calibration as m

class CalibratedAdaptationTests(unittest.TestCase):
    def test_splits_and_frozen_world(self):
        self.assertEqual(set(m.CALIBRATION_SEEDS)&set(m.TEST_SEEDS),set())
        self.assertEqual(len(m.CALIBRATION_SEEDS),32)
        self.assertEqual(len(m.TEST_SEEDS),64)
        self.assertEqual(min(m.TEST_SEEDS),100)
        self.assertEqual(m.HORIZON,180)
        self.assertEqual(m.THRESHOLDS,(.375,.50,.625,.75))
        self.assertEqual(m.REGIMES,world.REGIMES)
        self.assertEqual(m.CHANGE_POINTS["abrupt"],(60,120))
        self.assertEqual(m.CHANGE_POINTS["recurrent"],(45,90,135))

    def test_calibration_never_queries_test_seeds(self):
        original=m.simulate
        seen=[]
        def restricted(regime,seed,name,threshold,trace=False):
            self.assertIn(seed,m.CALIBRATION_SEEDS)
            seen.append((regime,seed,name,threshold))
            return original(regime,seed,name,threshold,trace=trace)
        with patch.object(m,"simulate",side_effect=restricted):
            cal=m.calibrate()
        self.assertEqual(len(seen),len(m.THRESHOLDS)*4*32)
        self.assertIn(cal["threshold"],m.THRESHOLDS)
        self.assertIn(cal["status"],(
            "CALIBRATED_WITH_STATIONARY_GUARDRAIL",
            "CALIBRATION_GUARDRAIL_FAILED_FALLBACK_MAX_THRESHOLD",
        ))
        self.assertEqual(cal["calibration_episode_count"],128)
        for x in cal["candidates"]:
            self.assertEqual(set(x["by_regime"]),set(m.REGIMES))

    def test_frozen_calibration_and_same_seeds_repeat(self):
        a=m.calibrate()
        b=m.calibrate()
        self.assertEqual(a,b)
        for regime in m.REGIMES:
            for name in ("omega_gated","omega_no_gate","sw_ucb"):
                first=m.simulate(regime,100,name,a["threshold"],trace=True)
                second=m.simulate(regime,100,name,a["threshold"],trace=True)
                self.assertEqual(first,second)
                self.assertEqual(first["observed_count"],180)
                self.assertEqual(len(first["observed_trace"]),180)
                self.assertEqual(len(first["observed_trace_sha256"]),64)

    def test_new_policy_does_not_touch_environment_or_hidden_outcomes(self):
        for name in m.CANDIDATES:
            p=m.GatedController(name,.5)
            with patch.object(world,"_world_probabilities",
                              side_effect=AssertionError("hidden oracle leaked")):
                for t in range(12):
                    action=p.choose(t)
                    self.assertIn(action,m.ACTIONS)
                    reward=(.08 if action=="ABSTAIN" else
                            .8 if action=="VERIFY" else 1.0)
                    p.observe(t,action,reward)
            self.assertEqual(len(p.observed),12)
            self.assertFalse(hasattr(p,"regime"))
            self.assertFalse(hasattr(p,"seed"))

    def test_alarm_probation_promote_and_audit_trail_never_erased(self):
        p=m.GatedController("omega_gated",.375)
        for t in range(16):
            # Same action, a sharp change in observed rewards.
            p.observe(t,"DIRECT",-2.0 if t<8 else 1.0)
        self.assertEqual(p.alarms,[15])
        self.assertEqual(p.mode,"probation")
        self.assertEqual((p.incumbent,p.challenger),("VERIFY","ABSTAIN"))
        for t in range(16,36):
            chosen=p.choose(t)
            p.observe(t,chosen,-2.2 if chosen=="VERIFY" else .08)
        self.assertEqual(p.mode,"commit")
        self.assertEqual(p.promotions,1)
        self.assertEqual(p.rejections,0)
        self.assertEqual(p.committed,"ABSTAIN")
        for t in range(36,56):
            p.observe(t,p.choose(t),.08)
        self.assertEqual(p.mode,"stable")
        self.assertEqual(len(p.observed),56)
        self.assertEqual([x[0] for x in p.observed],list(range(56)))

    def test_rejected_candidate_does_not_erase_observations(self):
        p=m.GatedController("omega_gated",.375)
        for t in range(16):
            p.observe(t,"DIRECT",-2.0 if t<8 else 1.0)
        for t in range(16,36):
            action=p.choose(t)
            p.observe(t,action,.8 if action=="VERIFY" else .08)
        self.assertEqual(p.rejections,1)
        self.assertEqual(p.promotions,0)
        self.assertEqual(p.committed,"VERIFY")
        self.assertEqual(len(p.observed),36)
        self.assertEqual(sum(e["event"]=="reject_proposal_keep_history"
                             for e in p.events),1)

    def test_no_gate_commits_without_counterfactual_validation(self):
        p=m.GatedController("omega_no_gate",.375)
        for t in range(16):
            p.observe(t,"DIRECT",-2.0 if t<8 else 1.0)
        self.assertEqual(p.mode,"commit")
        self.assertEqual(p.promotions,1)
        self.assertEqual(p.rejections,0)
        self.assertEqual(len(p.observed),16)
        self.assertEqual(p.commit_left,m.COMMIT_LENGTH)

    def test_ablation_no_memory_uses_shorter_observation_window(self):
        a=m.GatedController("omega_gated",.5)
        b=m.GatedController("omega_no_memory",.5)
        # Data deliberately arranged so short and long memory disagree.
        observed=[]
        for t in range(60):
            action="DIRECT" if t<10 else "VERIFY" if t<25 else "ABSTAIN"
            reward=1.0 if action=="DIRECT" else (
                0.8 if action=="VERIFY" else 0.08)
            observed.append((t,action,reward))
        a.observed=list(observed)
        b.observed=list(observed)
        self.assertEqual(a._alternative("DIRECT"),"VERIFY")
        self.assertEqual(b._alternative("DIRECT"),"VERIFY")
        self.assertEqual(len(a.observed),len(b.observed))

    def test_baselines_and_regret_comparisons_are_not_using_test_labels(self):
        for regime in m.REGIMES:
            a=m.simulate(regime,100,"omega_gated",.5)
            b=m.simulate(regime,100,"sw_ucb",.5)
            self.assertEqual(a["policy"],"omega_gated")
            self.assertEqual(b["policy"],"sw_ucb")
            self.assertTrue(a["regret"]>=0)
            self.assertTrue(b["regret"]>=0)
            self.assertEqual(b["promotions"],None)
            self.assertEqual(a["planner_version"],"0.1.0")

    def test_evaluator_only_change_dates(self):
        self.assertEqual(m._detection([62,122],"abrupt"),[2,2])
        self.assertEqual(m._detection([15,99],"recurrent"),[None,9,None])
        self.assertEqual(m._detection([10,20],"stationary"),[])

if __name__=="__main__":unittest.main()
