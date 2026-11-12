"""P5-REAL-01: no-provider tests for public split, exact tools and audit budget."""
import unittest
from collections import Counter
from unittest.mock import patch
import p5_real01_feedback as m

class RealFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=m.cases()

    def test_frozen_preflight_split_no_paid_provider(self):
        p=m.preflight()
        self.assertEqual(p["planned_model_generations"],48)
        self.assertEqual(p["model_generations"],0)
        self.assertEqual(p["paid_api_calls"],0)
        self.assertFalse(p["private_holdout_read"])
        self.assertEqual(p["budget"],16)
        self.assertEqual(len(p["public_cases_sha256"]),64)
        self.assertEqual(Counter(x["split"] for x in self.rows),
                         {"evaluation":32,"calibration":16})
        self.assertEqual(Counter(x["stratum"] for x in self.rows),
                         {s:12 for s in m.STRATA})

    def test_exact_reference_and_limited_verifier_are_independent(self):
        resolution=Counter()
        for row in self.rows:
            g=m.gold(row)
            v=m.limited_verifier(row)
            self.assertIn(row["kind"],m.KINDS)
            if v is not None:
                self.assertEqual(v,g)
                resolution[row["stratum"]]+=1
        self.assertEqual(resolution["DATA_SMALL"],12)
        self.assertEqual(resolution["DATA_LARGE"],0)
        self.assertGreater(resolution["CRT_SMALL"],0)

    def test_model_never_receives_reference_or_hidden_split(self):
        for row in self.rows:
            msgs=m.prompt(row)
            self.assertEqual(len(msgs),2)
            self.assertIn(row["question"],msgs[1]["content"])
            self.assertNotIn("gold",str(msgs))
            self.assertNotIn("parameters",str(msgs))
            self.assertNotIn("calibration",str(msgs))
            self.assertNotIn("evaluation",str(msgs))
        self.assertEqual(m.parse("REPONSE=27"),"27")
        self.assertEqual(m.parse("REPONSE=A\nVoici pourquoi"),"A")
        self.assertEqual(m.parse("La réponse est B."),"B")
        self.assertIsNone(m.parse("VALEUR"))
        self.assertIsNone(m.parse("Je ne sais pas."))

    def test_same_public_observations_for_all_policies(self):
        calib=[(r,{"text":"REPONSE=1","parsed":"1"})
               for r in self.rows if r["split"]=="calibration"]
        row=next(r for r in self.rows if r["split"]=="evaluation")
        view=m.public_view(row,{"text":"REPONSE=1","parsed":"1"})
        self.assertEqual(set(view),{
            "id","kind","stratum","question","model_output","parsed","verify_cost"})
        for name in m.POLICIES:
            pol=m.DecisionPolicy(name,calib)
            self.assertIn(pol.choose(view),("DIRECT","VERIFY","ABSTAIN"))
            self.assertEqual(pol.budget_left,16)

    def test_unauthorized_truth_not_accepted_as_feedback(self):
        calib=[(r,{"text":"REPONSE=1","parsed":"1"})
               for r in self.rows if r["split"]=="calibration"]
        policy=m.DecisionPolicy("omega_candidate",calib)
        view=m.public_view(self.rows[-1],{"text":"REPONSE=A","parsed":"A"})
        with self.assertRaises(ValueError):
            policy.observe(view,{"resolved":False,"model_correct":True})
        with self.assertRaises(ValueError):
            policy.observe(view,{"resolved":True,"model_correct":True,
                                 "gold":"A"})

    def test_online_controller_cannot_call_gold_or_limited_tool(self):
        calib=[(r,{"text":"REPONSE=1","parsed":"1"})
               for r in self.rows if r["split"]=="calibration"]
        view=m.public_view(self.rows[-1],{"text":"REPONSE=A","parsed":"A"})
        # Calibration is deliberately labeled and may use exact references.
        # The test forbids reference/tool access only after calibration,
        # while making test-time decisions from public features.
        policies=[m.DecisionPolicy(name,calib) for name in m.POLICIES]
        with patch.object(m,"gold",side_effect=AssertionError("oracle leakage")), \
             patch.object(m,"limited_verifier",side_effect=AssertionError("tool leakage")):
            for p in policies:
                self.assertIn(p.choose(view),("DIRECT","VERIFY","ABSTAIN"))
                p.observe(view, {"resolved": True, "model_correct": False})

    def test_policy_initialization_uses_only_calibration_cases(self):
        outputs = {row["id"]: {"text": "REPONSE=A", "parsed": "A"}
                   for row in self.rows}
        expected = {row["id"] for row in self.rows if row["split"] == "calibration"}
        self.assertEqual(len(expected), 16)
        initialize = m.DecisionPolicy.__init__

        def check_calibration(policy, name, calibration):
            with patch.object(m, "gold", wraps=m.gold) as gold, \
                 patch.object(m, "limited_verifier", wraps=m.limited_verifier) as verifier:
                initialize(policy, name, calibration)
            for tool in (gold, verifier):
                self.assertEqual({call.args[0]["id"] for call in tool.call_args_list},
                                 expected)

        with patch.object(m.DecisionPolicy, "__init__", autospec=True,
                          side_effect=check_calibration) as initialize_spy:
            m.evaluate_policies(self.rows, outputs)
        self.assertEqual(initialize_spy.call_count, len(m.POLICIES))

    def test_evaluation_checks_only_paid_verifications_once(self):
        outputs = {row["id"]: {"text": "REPONSE=A", "parsed": "A"}
                   for row in self.rows}
        for name in ("direct", "abstain", "verify_budget"):
            with self.subTest(policy=name):
                observe = m.DecisionPolicy.observe
                with patch.object(m, "POLICIES", (name,)), \
                     patch.object(m, "limited_verifier", wraps=m.limited_verifier) as verifier, \
                     patch.object(m.DecisionPolicy, "observe", autospec=True,
                                  side_effect=observe) as feedback:
                    result = m.evaluate_policies(self.rows, outputs)[name]

                trajectory = result["trajectory"]
                if name == "verify_budget":
                    actions = ["VERIFY"] * m.BUDGET + ["DIRECT"] * (32 - m.BUDGET)
                else:
                    actions = [name.upper()] * 32
                self.assertEqual([step["action"] for step in trajectory], actions)
                verified_ids = [step["id"] for step in trajectory if step["action"] == "VERIFY"]
                self.assertEqual([call.args[0]["id"] for call in verifier.call_args_list
                                  if call.args[0]["split"] == "evaluation"], verified_ids)
                self.assertEqual([call.args[1]["id"] for call in feedback.call_args_list],
                                 verified_ids)
                if verified_ids:
                    self.assertEqual(result["alarm_log"][-1]["budget_remaining"], 0)

    def test_budget_and_complete_trajectories_with_stub_model_outputs(self):
        # Engineering regression only; these are NOT real model responses.
        fake={r["id"]:{"text":"REPONSE=A","parsed":"A"} for r in self.rows}
        policies=m.evaluate_policies(self.rows,fake)
        self.assertEqual(set(policies),set(m.POLICIES))
        for name,summary in policies.items():
            self.assertEqual(len(summary["trajectory"]),32)
            self.assertLessEqual(summary["verified"],16)
            self.assertEqual(summary["correct_published"]+
                             summary["wrong_published"]+
                             summary["abstained"],32)
        self.assertEqual(policies["abstain"]["abstained"],32)
        self.assertEqual(policies["verify_budget"]["verified"],16)

    def test_reject_incomplete_model_campaign(self):
        with self.assertRaises(ValueError):
            m.evaluate_policies(self.rows,{})

if __name__=="__main__":unittest.main()
