"""Regression tests for Omega hourly capability discovery and isolation."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import route


class HourlyRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=route.read_registry()

    def test_catalogue_has_pinned_provenance(self):
        self.assertTrue(route.validate(self.data))
        self.assertEqual(len(self.data["capabilities"]),7)
        self.assertEqual(len({x["id"] for x in self.data["capabilities"]}),7)

    def test_semantic_refutation_routes_to_symbolic_not_lora(self):
        selected=route.select(self.data,"local_python_semantic_bug")
        self.assertEqual([x["id"] for x in selected["selected_capabilities"]],
                         ["symbolic_semantic_one_edit"])
        self.assertIn("python_lora_syntax_pilot",selected["declined_capabilities"])
        self.assertFalse(selected["actual_execution_performed"])

    def test_no_false_general_learning_inference(self):
        d=self.data
        sym=next(x for x in d["capabilities"] if x["id"]=="symbolic_semantic_one_edit")
        self.assertIn("11/12",sym["measured"])
        lora=next(x for x in d["capabilities"] if x["id"]=="python_lora_syntax_pilot")
        self.assertIn("0/12",lora["scientific_limit"])

    def test_mathematics_preserves_existing_authorized_work(self):
        s=route.select(self.data,"mathematical_proof_or_counterexample")
        self.assertEqual(s["selected_capabilities"][0]["id"],"existing_math_pilot")
        self.assertFalse(any("python" in x["id"] for x in s["selected_capabilities"]))
        self.assertFalse(s["source_availability_verified_this_run"])

    def test_provenance_preserves_existing_authorized_work(self):
        s=route.select(self.data,"provenance_reconciliation")
        self.assertEqual(s["selected_capabilities"][0]["id"],"existing_provenance_lab")

    def test_omega100_is_not_replaced_with_training(self):
        s=route.select(self.data,"omega100_iteration")
        self.assertEqual(s["selected_capabilities"][0]["id"],"existing_omega100")

    def test_syntax_pilot_does_not_become_production(self):
        s=route.select(self.data,"python_syntax_repair_pilot")
        self.assertEqual(s["selected_capabilities"][0]["level"],"EXPERIMENTAL_ONLY")
        self.assertTrue(s["advice_only"])

    def test_training_data_only_uses_hub_and_fastlane(self):
        s=route.select(self.data,"new_training_data_qa")
        self.assertEqual([x["id"] for x in s["selected_capabilities"]],
                         ["fastlane_synthetic_qa","learning_hub_verified_index"])
        self.assertFalse(s["actual_execution_performed"])

    def test_unknown_kind_does_not_force_a_tool(self):
        s=route.select(self.data,"astrophysics_unknown_task")
        self.assertEqual(s["selected_capabilities"],[])
        self.assertEqual(s["applied_rule"],"other")

    def test_rejects_automatic_training_promotion(self):
        for field in ("auto_merge","auto_train","automatic_model_execution",
                      "auto_promote_science","main_modified"):
            with self.subTest(field=field):
                copydoc=copy.deepcopy(self.data)
                copydoc[field]=True
                with self.assertRaisesRegex(ValueError,"UNAUTHORIZED_SIDE_EFFECTS"):
                    route.validate(copydoc)

    def test_rejects_unpinned_or_no_provenance(self):
        doc=copy.deepcopy(self.data)
        doc["capabilities"][1]["ref"]="main"
        with self.assertRaisesRegex(ValueError,"UNPINNED_EXPERIMENTAL_CODE"):
            route.validate(doc)
        doc=copy.deepcopy(self.data)
        doc["capabilities"][1]["evidence_run"]=None
        with self.assertRaisesRegex(ValueError,"NO_REAL_RUN_PROVENANCE"):
            route.validate(doc)

    def test_rejects_science_and_route_guardrail_tampering(self):
        doc=copy.deepcopy(self.data)
        doc["route_rules"][3]["preferred"]=["python_lora_syntax_pilot"]
        doc["route_rules"][3]["reject"]=[]
        with self.assertRaises(ValueError):
            route.validate(doc)
        doc=copy.deepcopy(self.data)
        doc["safe_default"]["mandatory_application_each_hour"]=True
        with self.assertRaisesRegex(ValueError,"UNSAFE_HOURLY_DEFAULTS"):
            route.validate(doc)

    def test_routing_deterministic_and_displays_evidence(self):
        a=route.select(self.data,"local_python_semantic_bug")
        b=route.select(self.data,"local_python_semantic_bug")
        self.assertEqual(a,b)
        self.assertEqual(a["selected_capabilities"][0]["evidence_run"],45074827572)
        self.assertEqual(len(a["registry_sha256"]),64)

if __name__=="__main__":
    unittest.main()
