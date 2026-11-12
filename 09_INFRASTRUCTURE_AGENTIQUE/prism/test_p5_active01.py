"""P5 ACTIVE-01: hostile controls for hidden labels, choices and real-score input."""
import unittest
from collections import Counter
from unittest.mock import patch
import p5_active01 as p

class ActiveVerificationTests(unittest.TestCase):
    def setUp(self):
        self.cal,self.batches=p.plan()
        self.fake={(m,r["id"]):{
            "answer":"A" if r["index"]%3 else "B",
            "confidence":.66 if r["index"]%2 else .91,
            "margin":1.3,"logit_a":-1.1,"logit_b":-2.0,
            "input_tokens":40,"method":"TEST_STUB_NOT_REAL_MODEL",
            "token_id_a":32,"token_id_b":33,
        } for m,r in self.cal+[q for batch in self.batches for q in batch]}
        self.labeled=[(r,self.fake[(m,r["id"])]) for m,r in self.cal]

    def test_unique_80_truths_and_two_exact_proofs(self):
        universe=p.universe()
        self.assertEqual(len(universe),80)
        self.assertEqual(len({r["question"] for r in universe}),80)
        self.assertEqual(len({(r["kind"],tuple(r["parameters"]))
                              for r in universe}),80)
        self.assertEqual(Counter(r["kind"] for r in universe),
                         {k:20 for k in p.KINDS})
        for r in universe:
            self.assertEqual(p.gold(r),p.verify_exact(r))
            self.assertEqual(p.gold(r),"A" if r["index"]%2==0 else "B")

    def test_disjoint_calibration_and_eval_four_way_batches(self):
        self.assertEqual(len(self.cal),32)
        self.assertEqual(len(self.batches),16)
        self.assertEqual(sum(len(x) for x in self.batches),64)
        self.assertEqual({m for m,_ in self.batches[0]},{"large"})
        self.assertEqual({m for m,_ in self.batches[4]},{"small"})
        self.assertEqual({m for m,_ in self.batches[8]},{"large"})
        self.assertEqual({m for m,_ in self.batches[12]},{"small"})
        self.assertFalse({r["id"] for _,r in self.cal}&{
            r["id"] for batch in self.batches for _,r in batch})
        for batch in self.batches:
            self.assertEqual({r["kind"] for _,r in batch},set(p.KINDS))
        self.assertEqual(p.preflight()["real_model_forwards"],96)

    def test_decisions_never_call_math_oracle_or_see_model_or_phase(self):
        views=[p.public(r,self.fake[(m,r["id"])])
               for m,r in self.batches[0]]
        self.assertEqual(set(views[0]),{
            "kind","question","answer","confidence","margin","cost"})
        policies=[p.Policy(name,self.labeled) for name in p.DEPLOYABLE]
        with patch.object(p,"gold",
                          side_effect=AssertionError("hidden oracle leaked")), \
             patch.object(p,"verify_exact",
                          side_effect=AssertionError("unpaid verifier leaked")):
            for policy in policies:
                dec=policy.choose(0,views)
                self.assertLessEqual(dec["actions"].count("VERIFY"),1)
        contaminated=[dict(v) for v in views]
        contaminated[0]["gold"]="A"
        with self.assertRaises(ValueError):
            policies[0].choose(0,contaminated)
        contaminated=[dict(v) for v in views]
        contaminated[0]["model_id"]="large"
        with self.assertRaises(ValueError):
            policies[0].choose(0,contaminated)

    def test_paid_feedback_is_single_and_append_only(self):
        policy=p.Policy("omega_candidate",self.labeled)
        views=[p.public(r,self.fake[(m,r["id"])])
               for m,r in self.batches[0]]
        policy.observe(0,views[0],False)
        self.assertEqual(policy.used,1)
        self.assertEqual(len(policy.seen),1)
        self.assertEqual(policy.feedback[views[0]["kind"]],[0])
        with self.assertRaises(ValueError):
            policy.observe(0,views[1],True)
        with self.assertRaises(ValueError):
            policy.observe(1,views[1],1)
        self.assertEqual(policy.used,1)
        for i in range(1,16):
            policy.observe(i,views[i%4],bool(i%2))
        self.assertEqual(policy.used,16)
        with self.assertRaises(AssertionError):
            policy.observe(16,views[0],False)

    def test_constrained_model_reply_is_label_not_parser(self):
        self.assertEqual(p.model_prompt(self.cal[0][1])[0]["role"],"system")
        for kind in p.KINDS:
            row=p.make_case(kind,0)
            msgs=p.model_prompt(row)
            self.assertIn("A = Vrai",msgs[1]["content"])
            self.assertIn("B = Faux",msgs[1]["content"])
            self.assertNotIn(p.gold(row)+" est la bonne réponse",str(msgs))
        self.assertEqual(p.PROTOCOL,"P5-ACTIVE-01")

    def test_controller_has_real_competing_verification_choices(self):
        selected_by_policy={}
        views=[p.public(r,self.fake[(m,r["id"])])
               for m,r in self.batches[0]]
        for name in p.DEPLOYABLE:
            decision=p.Policy(name,self.labeled).choose(0,views)
            self.assertLessEqual(sum(a=="VERIFY" for a in decision["actions"]),1)
            selected_by_policy[name]=decision["chosen"]
        self.assertIsNone(selected_by_policy["none"])
        self.assertEqual(selected_by_policy["fixed_first"],0)
        self.assertNotEqual(selected_by_policy["round_robin"],None)
        self.assertGreater(len(set(selected_by_policy.values())),1)

    def test_all_policies_same_round_budget_and_no_free_labels(self):
        scores=p.evaluate(self.cal,self.batches,self.fake)
        self.assertEqual(set(scores),set(p.POLICIES))
        self.assertEqual(scores["voi_online"]["trajectory"],
                         scores["omega_no_change"]["trajectory"])
        for name in p.DEPLOYABLE:
            s=scores[name]
            self.assertEqual(len(s["trajectory"]),64)
            self.assertLessEqual(s["verified"],16)
            self.assertEqual(s["correct_published"]+
                             s["wrong_published"]+s["abstained"],64)
            self.assertEqual(s["verified"],len(s["observed_feedback"]))
            for t in range(16):
                self.assertLessEqual(sum(e["action"]=="VERIFY"
                    for e in s["trajectory"] if e["round"]==t),1)
        self.assertTrue(scores["hindsight_oracle"]["nondeployable"])

    def test_missing_real_inference_is_not_an_experiment(self):
        with self.assertRaises(ValueError):
            p.evaluate(self.cal,self.batches,{})
        with self.assertRaises(ValueError):
            p.evaluate(self.cal,self.batches,{
                k:v for i,(k,v) in enumerate(self.fake.items()) if i>0})

if __name__=="__main__":
    unittest.main()
