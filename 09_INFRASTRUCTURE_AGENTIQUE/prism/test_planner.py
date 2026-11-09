import unittest

from planner import MissionValidationError, plan_mission


class AdaptivePrismPlannerTests(unittest.TestCase):
    def test_mathematical_mission_activates_formalist_and_refuter(self):
        plan = plan_mission({"question": "Établir le lemme", "mission_type": "mathematical"})
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(roles, ["refuter", "formalist"])
        self.assertEqual(plan["execution_model"]["status"], "planning_only")

    def test_exploratory_mission_activates_researcher_and_refuter(self):
        plan = plan_mission({"question": "Explorer les mécanismes", "mission_type": "exploratory"})
        self.assertEqual([t["role"] for t in plan["tasks"]], ["refuter", "researcher"])

    def test_documentary_mission_activates_bibliographer_and_refuter(self):
        plan = plan_mission({"question": "Vérifier les sources primaires", "mission_type": "documentary"})
        self.assertEqual([t["role"] for t in plan["tasks"]], ["refuter", "bibliographer"])

    def test_computational_mission_activates_computational_and_refuter(self):
        plan = plan_mission({"question": "Tester un cas fini", "mission_type": "computational"})
        self.assertEqual([t["role"] for t in plan["tasks"]], ["refuter", "computational"])

    def test_explicit_flags_override_type_defaults(self):
        plan = plan_mission({
            "question": "Étudier une preuve par calcul",
            "mission_type": "mathematical",
            "requires_computation": True,
            "requires_literature": True,
        })
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(roles, ["refuter", "formalist", "computational", "bibliographer"])

    def test_inactive_roles_have_reasons(self):
        plan = plan_mission({
            "question": "Un calcul seulement",
            "mission_type": "computational",
            "claims_to_test": False,
        })
        inactive = {item["role"]: item["reason"] for item in plan["inactive_roles"]}
        self.assertIn("refuter", inactive)
        self.assertIn("bibliographer", inactive)
        self.assertTrue(all(reason for reason in inactive.values()))

    def test_no_duplicate_roles_and_all_tasks_are_unexecuted(self):
        plan = plan_mission({"question": "Question générale", "mission_type": "general"})
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertTrue(all(task["execution_status"] == "not_executed" for task in plan["tasks"]))
        self.assertTrue(all(task["independence"] == "role_perspective_only" for task in plan["tasks"]))

    def test_boolean_flags_are_strictly_validated(self):
        with self.assertRaises(MissionValidationError):
            plan_mission({"question": "Q", "mission_type": "general", "requires_computation": "yes"})

    def test_invalid_missions_are_rejected(self):
        for mission in (None, [], {}, {"question": "", "mission_type": "general"},
                        {"question": "Q", "mission_type": "unknown"}):
            with self.subTest(mission=mission):
                with self.assertRaises(MissionValidationError):
                    plan_mission(mission)


    def test_structured_context_metadata_is_preserved(self):
        plan = plan_mission({
            "question": "Établir le lemme",
            "mission_type": "mathematical",
            "mission_id": "M-17",
            "domain": "dynamique finie",
            "scope": "Cas binaires de longueur 3",
            "exclusions": ["pas de simulation"],
            "known_ids": ["CL-DYN-01", "CL-DYN-02", "CL-DYN-01"],
            "constraints": ["lecture seule"],
        })
        self.assertEqual(plan["mission"]["mission_id"], "M-17")
        self.assertEqual(plan["mission"]["known_ids"], ["CL-DYN-01", "CL-DYN-02"])
        self.assertEqual(plan["mission"]["exclusions"], ["pas de simulation"])

    def test_same_input_produces_same_plan(self):
        mission = {"question": "Question générale", "mission_type": "general"}
        self.assertEqual(plan_mission(mission), plan_mission(mission))


if __name__ == "__main__":
    unittest.main()
