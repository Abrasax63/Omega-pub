"""No-model tests that bad experimental choice structures are rejected."""
import unittest

from p5_active01_design_gate import diagnose,STRONG

class GateTests(unittest.TestCase):
    def data(self):
        # Test fixture only: never pretend these are measured model outputs.
        outcomes={}
        for p in STRONG:
            outcomes[p]={"trajectory":[
                {"round":r,"kind":k,
                 "action":"VERIFY" if k=="INJ" else "ABSTAIN"}
                for r in range(16) for k in ("MUL","CRT","RATE","INJ")
            ]}
        raw=[{"model":model,"split":"test",
              "answer":"A","gold_posthoc_only":"A" if i%2 else "B",
              "confidence":.75}
             for model in ("small","large") for i in range(32)]
        return {"protocol":"P5-ACTIVE-01","policies":outcomes,
                "omega_vs_no_change_action_differences":0,
                "omega_minus_discount":0.0,"raw_model_scores":raw}

    def test_all_strong_policies_verify_same_cheapest_family(self):
        r=diagnose(self.data())
        self.assertEqual(r["design_gate"],"FAIL_NON_DISCRIMINATING")
        self.assertEqual(r["strong_policy_round_decisions_unique"],1)
        self.assertTrue(r["strong_policies_choose_same_every_round"])
        self.assertEqual(r["strong_policy_max_single_family_share"]["omega_candidate"],1)
        self.assertEqual(r["omega_action_differences_vs_ablation"],0)

    def test_more_choices_can_make_gate_pass(self):
        d=self.data()
        policy=d["policies"]["voi_margin"]["trajectory"]
        for x in policy:
            if x["kind"]=="INJ":x["action"]="ABSTAIN"
            if x["kind"]==("MUL","CRT","RATE","INJ")[x["round"]%4]:
                x["action"]="VERIFY"
        r=diagnose(d)
        self.assertEqual(r["design_gate"],"PASS_SELECTION_DIVERSITY")
        self.assertGreater(r["strong_policy_round_decisions_unique"],1)

    def test_reject_incomplete_or_oververified_archive(self):
        d=self.data()
        d["policies"]["voi_online"]["trajectory"].pop()
        with self.assertRaises(ValueError):diagnose(d)
        d=self.data()
        d["policies"]["voi_online"]["trajectory"][0]["action"]="VERIFY"
        with self.assertRaises(ValueError):diagnose(d)

    def test_no_private_model_grading(self):
        d=self.data()
        r=diagnose(d)
        self.assertEqual(r["test_model_diagnostics"]["small"]["test_cases"],32)
        self.assertEqual(r["test_model_diagnostics"]["large"]["correct"],16)
        self.assertEqual(r["conclusion"],"NO_OMEGA_SPECIFIC_ADAPTIVE_GAIN_DEMONSTRATED")

if __name__=="__main__":
    unittest.main()
