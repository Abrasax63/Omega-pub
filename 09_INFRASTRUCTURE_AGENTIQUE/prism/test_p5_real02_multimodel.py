"""REAL-02: separation of model outputs, truth, budget and controller feedback."""
import unittest
from collections import Counter
from unittest.mock import patch

import p5_real02_multimodel as p

class Real02Tests(unittest.TestCase):
    def test_oracles_and_unique_unseen_eval_questions(self):
        allrows=p.all_cases()
        self.assertEqual(len(allrows),80)
        self.assertEqual(Counter(x["kind"] for x in allrows),
                         {kind:20 for kind in p.KINDS})
        for r in allrows:
            self.assertEqual(p.reference(r),p.verify_exact(r))
        calib,ev=p.generation_plan()
        self.assertEqual(len(calib),32)
        self.assertEqual(len(ev),64)
        self.assertEqual(len({r["id"] for _,r in ev}),64)
        self.assertFalse({r["id"] for _,r in ev} & {r["id"] for _,r in calib})
        self.assertEqual([m for m,_ in ev[::16]],["large","small","large","small"])
        for phase in range(4):
            block=ev[phase*16:(phase+1)*16]
            self.assertEqual(Counter(r["kind"] for _,r in block),
                             {kind:4 for kind in p.KINDS})
            self.assertEqual(len({m for m,_ in block}),1)

    def test_public_model_inputs_never_contain_answer(self):
        for r in p.all_cases():
            msg=p.prompt(r)
            self.assertEqual(len(msg),2)
            self.assertNotIn(str(p.reference(r))+" = gold",str(msg))
            self.assertNotIn("calibration",str(msg))
            self.assertNotIn("evaluation",str(msg))
            sample={"text":"Bonjour","parsed":None}
            public=p.public_input(r,sample)
            self.assertEqual(set(public),{
                "kind","question","model_output","parsed","verification_cost"})
            self.assertNotIn("id",public)
            self.assertNotIn("model",public)
            self.assertNotIn("index",public)
            self.assertNotIn("phase",public)

    def test_parser_typed_and_rejects_contextual_garbage(self):
        self.assertEqual(p.parse("Réponse : 117.","CRT"),"117")
        self.assertEqual(p.parse("331","MUL"),"331")
        self.assertEqual(p.parse("OUI, la fonction est injective.","INJ"),"OUI")
        self.assertEqual(p.parse("NON","INJ"),"NON")
        self.assertEqual(p.parse("A","RATE"),"A")
        self.assertIsNone(p.parse("B","CRT"))
        self.assertIsNone(p.parse("OUI","RATE"))
        self.assertIsNone(p.parse("Réponse : n'importe laquelle","CRT"))
        self.assertIsNone(p.parse("27","INJ"))

    def test_preflight_free_open_models_and_budget(self):
        x=p.preflight()
        self.assertEqual(x["expected_generations"],96)
        self.assertEqual(x["calibration_generations"],32)
        self.assertEqual(x["evaluation_generations"],64)
        self.assertEqual(x["oracles_agree_on_all"],80)
        self.assertEqual(x["paid_api_calls"],0)
        self.assertFalse(x["private_data_read"])
        self.assertEqual(x["budget"],24)
        self.assertEqual(len(x["public_cases_sha256"]),64)
        self.assertTrue("Qwen2.5-1.5B-Instruct" in p.MODELS["large"][0])

    def test_controller_blind_to_reference_and_model_switch(self):
        cal,ev=p.generation_plan()
        labelled=[(row,{"text":"OUI","parsed":"OUI"}) for model,row in cal]
        policies=[p.Policy(name,labelled) for name in p.POLICIES]
        view=p.public_input(ev[0][1],{"text":"Réponse : 8","parsed":"8"})
        with patch.object(p,"reference",
                          side_effect=AssertionError("reference leak")), \
             patch.object(p,"verify_exact",
                          side_effect=AssertionError("verifier leak")):
            for policy in policies:
                self.assertIn(policy.decide(3,view),("DIRECT","VERIFY","ABSTAIN"))
        bad=dict(view,model_id="large")
        with self.assertRaises(ValueError):
            policies[0].decide(4,bad)

    def test_credit_cannot_be_overdrawn(self):
        cal,ev=p.generation_plan()
        labelled=[(row,{"text":"OUI","parsed":"OUI"}) for model,row in cal]
        policy=p.Policy("omega_candidate",labelled)
        view=p.public_input(ev[0][1],{"text":"15","parsed":"15"})
        self.assertEqual(policy.decide(0,view),"ABSTAIN")
        self.assertIn(policy.decide(2,view),("DIRECT","VERIFY","ABSTAIN"))
        policy.observe_verification(2,view,True)
        with self.assertRaises(AssertionError):
            policy.observe_verification(2,view,False)
        self.assertEqual(policy.verified,1)

    def test_alarm_can_trigger_without_hidden_truth(self):
        cal,ev=p.generation_plan()
        labelled=[(r,{"text":p.reference(r),"parsed":p.reference(r)})
                  for _,r in cal]
        policy=p.Policy("omega_candidate",labelled)
        view=p.public_input(ev[0][1],{"text":"0","parsed":"0"})
        for i in range(6):
            t=2+3*i
            policy.observe_verification(t,view,False)
        self.assertEqual(policy.alarms,[17])
        self.assertTrue(policy.alarm)
        self.assertEqual(len(policy.all_checked),6)
        self.assertEqual(sum(1 for e in policy.log if e["event"]=="alarm_on"),1)

    def test_equal_budget_and_actual_model_required_for_scoring(self):
        cal,ev=p.generation_plan()
        with self.assertRaises(ValueError):
            p.score_policies(cal,ev,{})
        stub={(model,row["id"]):{"text":"0","parsed":"0"}
              for model,row in cal+ev}
        scores=p.score_policies(cal,ev,stub)
        self.assertEqual(set(scores),set(p.POLICIES))
        for name,v in scores.items():
            self.assertEqual(len(v["trajectory"]),64)
            self.assertLessEqual(v["verified"],24)
            self.assertEqual(
                v["correct_published"]+v["wrong_published"]+v["abstained"],64)
        self.assertEqual(scores["online_beta"]["trajectory"],
                         scores["omega_no_alarm"]["trajectory"])
        self.assertEqual(scores["abstain"]["abstained"],64)

if __name__=="__main__":
    unittest.main()
