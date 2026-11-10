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

    def test_explicit_exploratory_flag_can_disable_general_default(self):
        plan = plan_mission({
            "question": "Répondre à une question générale ciblée",
            "mission_type": "general",
            "exploratory": False,
        })
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(roles, ["refuter"])
        inactive = {item["role"]: item["reason"] for item in plan["inactive_roles"]}
        self.assertIn("Désactivé", inactive["researcher"])

    def test_inactive_roles_have_reasons_and_unneeded_roles_are_omitted(self):
        plan = plan_mission({
            "question": "Un calcul seulement",
            "mission_type": "computational",
            "claims_to_test": False,
        })
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(roles, ["computational"])
        inactive = {item["role"]: item["reason"] for item in plan["inactive_roles"]}
        self.assertEqual(set(inactive), {"refuter", "formalist", "bibliographer", "researcher"})
        self.assertTrue(all(reason for reason in inactive.values()))

    def test_no_duplicate_roles_and_all_tasks_are_unexecuted(self):
        plan = plan_mission({"question": "Question générale", "mission_type": "general"})
        roles = [task["role"] for task in plan["tasks"]]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertTrue(all(task["execution_status"] == "not_executed" for task in plan["tasks"]))
        self.assertTrue(all(task["independence"] == "role_perspective_only" for task in plan["tasks"]))

    def test_every_active_role_has_question_failure_and_stop_conditions(self):
        plan = plan_mission({"question": "Établir le résultat sous hypothèses H", "mission_type": "mathematical"})
        self.assertEqual(plan["mission"]["question"], "Établir le résultat sous hypothèses H")
        for task in plan["tasks"]:
            self.assertTrue(task["question"])
            self.assertTrue(task["activation_reason"])
            self.assertTrue(task["failure_criterion"])
            self.assertTrue(task["stop_condition"])

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

    def test_explicit_deliverables_override_defaults_without_changing_roles(self):
        mission = {"question": "Quel délai appliquer ?", "mission_type": "documentary"}
        default = plan_mission(mission)
        custom = plan_mission({**mission, "deliverables": [" Délai. ", "Source.", "Délai."]})
        self.assertEqual(default["deliverable_source"], "mission_type")
        self.assertIn("passage décisif", default["deliverables"][0])
        self.assertEqual(custom["deliverable_source"], "mission")
        self.assertEqual(custom["deliverables"], ["Délai.", "Source."])
        self.assertEqual(default["tasks"], custom["tasks"])
        self.assertEqual(default["inactive_roles"], custom["inactive_roles"])

    def test_invalid_deliverables_are_rejected(self):
        for invalid in (None, "", [], [""], ["ok", 1]):
            with self.subTest(deliverables=invalid):
                with self.assertRaises(MissionValidationError):
                    plan_mission({"question": "Q", "mission_type": "general", "deliverables": invalid})

    def test_next_action_changes_when_the_decisive_date_is_missing(self):
        mission = {"question": "Quelle notice s'applique ?", "mission_type": "documentary"}
        known = plan_mission({**mission, "decision_context": {
            "decision_basis": "La date est attestée et la clause de transition la couvre.",
        }})
        missing = plan_mission({**mission, "decision_context": {
            "blocking_uncertainty": "La date de réception manque.",
            "clarification": "Quelle est la date de réception ?",
        }})
        self.assertEqual(known["next_action"]["action"], "answer")
        self.assertEqual(missing["next_action"]["action"], "ask")
        self.assertEqual(known["tasks"], missing["tasks"])
        self.assertEqual(known["deliverables"], missing["deliverables"])

    def test_next_action_changes_when_comparable_data_become_available(self):
        mission = {"question": "Peut-on attribuer la baisse ?", "mission_type": "exploratory"}
        context = {"blocking_uncertainty": "La comparaison porte sur des populations différentes."}
        absent = plan_mission({**mission, "decision_context": context})
        present = plan_mission({**mission, "decision_context": {
            **context, "verification": "Comparer les deux périodes sur la population commune.",
            "verification_effect": "Une baisse absente à périmètre égal ferait abandonner l’attribution.",
        }})
        self.assertEqual(absent["next_action"]["action"], "insufficient_evidence")
        self.assertEqual(present["next_action"]["action"], "verify")
        self.assertEqual(absent["tasks"], present["tasks"])

    def test_invalid_context_does_not_produce_a_recommendation(self):
        for context in ({}, None, {"decision_basis": "A", "blocking_uncertainty": "B"},
                        {"decision_basis": "A", "verification": "V"},
                        {"blocking_uncertainty": "B", "verification": "  "},
                        {"blocking_uncertainty": "B", "verification": "V"},
                        {"blocking_uncertainty": "B", "unknown": "X"}):
            with self.subTest(context=context):
                with self.assertRaises(MissionValidationError):
                    plan_mission({"question": "Q", "mission_type": "general", "decision_context": context})

    def test_available_verification_precedes_clarification(self):
        plan = plan_mission({"question": "Q", "mission_type": "general", "decision_context": {
            "blocking_uncertainty": "La date manque dans le résumé.",
            "verification": "Lire le registre accessible.",
            "verification_effect": "La date détermine quelle version appliquer.",
            "clarification": "Demander la date.",
        }})
        self.assertEqual(plan["next_action"]["next_step"], "Lire le registre accessible.")

    def test_same_input_produces_same_plan(self):
        mission = {"question": "Question générale", "mission_type": "general"}
        self.assertEqual(plan_mission(mission), plan_mission(mission))


if __name__ == "__main__":
    unittest.main()
