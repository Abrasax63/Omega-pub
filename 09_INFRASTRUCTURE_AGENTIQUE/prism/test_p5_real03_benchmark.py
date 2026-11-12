"""REAL-03 executable preflight tests; no LLM dependency and no gold leakage."""
import unittest
from collections import Counter
from unittest.mock import patch

import p5_real03_benchmark as b
from p5_real03_semantic import extract,PARSER_VERSION

class Real03Tests(unittest.TestCase):
    def test_parser_is_typed_and_catches_old_real02_format_problem(self):
        examples=[
            ("Équipe A","RATE","A"),
            ("Equipe B avec un taux global de succès de 80% (4/5).","RATE","B"),
            ("A","RATE","A"),
            ("Non, elle n'est pas injective.","INJ","NON"),
            ("Oui.","INJ","OUI"),
            ("Réponse finale : 702.","MUL","702"),
            ("19","CRT","19"),
        ]
        for raw,kind,answer in examples:
            got,reason=extract(raw,kind)
            self.assertEqual(got,answer,(raw,kind,reason))
            self.assertNotEqual(reason,"empty")
        rejects=[
            ("Equipe A, mais équipe B gagne","RATE"),
            ("A","CRT"),("Équipe B","MUL"),("Oui, elle n'est pas injective.","INJ"),
            ("Non, elle est injective.","INJ"),("0/5 = 30%","RATE"),
            ("Le calcul donne 2 ou 5","CRT"),("","MUL"),
        ]
        for raw,kind in rejects:
            self.assertIsNone(extract(raw,kind)[0],(raw,kind))
        self.assertEqual(PARSER_VERSION,"REAL03-TYPED-PARSER-V1")

    def test_all_80_math_questions_new_and_unique(self):
        rows=b.universe()
        self.assertEqual(len(rows),80)
        self.assertEqual(len({r["question"] for r in rows}),80)
        self.assertEqual(len({(r["kind"],tuple(r["parameters"]))
                              for r in rows}),80)
        self.assertEqual(Counter(r["kind"] for r in rows),
                         {k:20 for k in b.KINDS})
        for r in rows:
            self.assertEqual(b.reference(r),b.verify_exact(r))
        ca,ev=b.generation_plan()
        self.assertEqual((len(ca),len(ev)),(32,64))
        self.assertFalse({r["id"] for _,r in ca}&{r["id"] for _,r in ev})
        self.assertEqual([ev[i][0] for i in (0,16,32,48)],
                         ["large","small","large","small"])
        for j in range(4):
            self.assertEqual(Counter(r["kind"] for _,r in ev[16*j:16*(j+1)]),
                             {k:4 for k in b.KINDS})

    def test_no_reference_or_hidden_info_reaches_controller(self):
        ca,ev=b.generation_plan()
        labeled=[(r,{"text":"Oui","parsed":"OUI","parse_reason":"binary_explicit"})
                 for _,r in ca]
        selectors=[b.Selector(name,labeled) for name in b.POLICIES]
        view=b.public_view(ev[0][1],{
            "text":"Réponse finale : 42","parsed":"42",
            "parse_reason":"numeric_explicit"})
        self.assertEqual(set(view),{
            "kind","question","model_output","parsed","parse_reason","verify_cost"})
        for unwanted in ("model","phase","gold","reference","correct","id","index"):
            self.assertNotIn(unwanted,view)
        with patch.object(b,"reference",side_effect=AssertionError("gold leak")), \
             patch.object(b,"verify_exact",side_effect=AssertionError("tool leak")):
            for sel in selectors:
                self.assertIn(sel.decide(5,view),("DIRECT","VERIFY","ABSTAIN"))
        with self.assertRaises(ValueError):
            selectors[0].decide(6,{**view,"model_id":"large"})

    def test_alarm_is_observation_driven_and_can_change_decision(self):
        ca,ev=b.generation_plan()
        # Labeled calibration is 32/32 correct. Six observed errors are
        # sufficient to trigger the preregistered alarm, no oracle use.
        high=[(r,{"text":b.reference(r),"parsed":b.reference(r)})
              for _,r in ca]
        policy=b.Selector("omega_candidate",high)
        view=b.public_view(ev[0][1],{
            "text":"Réponse finale : 42","parsed":"42",
            "parse_reason":"numeric_explicit"})
        for t in (2,5,7,10,13,15):
            policy.observe(t,view,False)
        self.assertTrue(policy.active)
        self.assertTrue(any(x["event"]=="alarm_on" for x in policy.alarm_events))
        self.assertEqual(policy.used,6)
        self.assertEqual(len(policy.all_checks),6)
        self.assertEqual(policy._p(view["kind"])!=
                         b.Selector("omega_no_alarm",high)._p(view["kind"]),True)

    def test_equal_budget_and_ablation_with_synthetic_engineering_fixture(self):
        cal,ev=b.generation_plan()
        fake={(model,row["id"]):{
            "text":"A","parsed":"A","parse_reason":"team_explicit"}
            for model,row in cal+ev}
        scores=b.evaluate(cal,ev,fake)
        self.assertEqual(set(scores),set(b.POLICIES))
        for name,x in scores.items():
            self.assertEqual(len(x["trajectory"]),64)
            self.assertLessEqual(x["verified"],24)
            self.assertEqual(x["correct_published"]+
                             x["wrong_published"]+x["abstained"],64)
        self.assertEqual(scores["omega_no_alarm"]["trajectory"],
                         scores["online_beta"]["trajectory"])
        self.assertEqual(scores["abstain"]["abstained"],64)
        with self.assertRaises(ValueError):
            b.evaluate(cal,ev,{})

    def test_preflight_no_api_and_known_model_revisions(self):
        x=b.preflight()
        self.assertEqual(x["questions"],80)
        self.assertEqual(x["actual_generations_planned"],96)
        self.assertEqual((x["calibration"],x["test"]),(32,64))
        self.assertEqual(len(x["cases_sha256"]),64)
        self.assertEqual(x["parser"],PARSER_VERSION)
        self.assertEqual(x["paid_api_calls"],0)
        self.assertFalse(x["private_data_access"])
        for model,revision in b.MODELS.values():
            self.assertEqual(len(revision),40)

if __name__=="__main__":
    unittest.main()
