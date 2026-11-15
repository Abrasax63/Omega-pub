import unittest
from planner import plan_mission, MissionValidationError
from provenance_tool_runner import run_selected_provenance_tool


DOSSIER = {"evidence": [{"id": "source"}, {"id": "result", "derived_from": ["source"]}]}


class ProvenanceToolRoutingTests(unittest.TestCase):
    def test_enabled_tool_executes_and_finds_declared_relation(self):
        plan = plan_mission({"question": "Retracer le résultat", "mission_type": "documentary",
                             "requires_provenance": True})
        self.assertEqual(plan["tools"][0]["name"], "reconstruct_provenance")
        outcome = run_selected_provenance_tool(plan, DOSSIER)
        self.assertTrue(outcome["tool_executed"])
        self.assertEqual(outcome["result"]["relations"][0]["kind"], "declared_dependency")
        self.assertFalse(outcome["scientific_certification"])

    def test_disabled_tool_never_executes(self):
        plan = plan_mission({"question": "Retracer le résultat", "mission_type": "documentary",
                             "requires_provenance": False})
        self.assertEqual(plan["tools"], [])
        self.assertEqual(run_selected_provenance_tool(plan, DOSSIER)["status"], "not_selected")

    def test_default_behavior_unchanged(self):
        plan = plan_mission({"question": "Établir un lemme", "mission_type": "mathematical"})
        self.assertEqual([t["role"] for t in plan["tasks"]], ["refuter", "formalist"])
        self.assertEqual(plan["tools"], [])

    def test_invalid_flag_rejected(self):
        with self.assertRaises(MissionValidationError):
            plan_mission({"question": "Q", "mission_type": "general",
                          "requires_provenance": "yes"})

    def test_missing_parent_is_not_certified(self):
        plan = plan_mission({"question": "Q", "mission_type": "general",
                             "requires_provenance": True})
        outcome = run_selected_provenance_tool(plan, {"evidence": [
            {"id": "result", "derived_from": ["unknown"]}]})
        self.assertEqual(outcome["result"]["status"], "indéterminé")
        self.assertFalse(outcome["scientific_certification"])


if __name__ == "__main__":
    unittest.main()
