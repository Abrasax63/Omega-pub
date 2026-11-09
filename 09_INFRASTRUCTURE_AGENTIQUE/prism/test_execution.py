import unittest

from planner import plan_mission
from context import prepare_contexts
from execution import (
    SupervisedExecutionError, start_execution, record_perspective, close_execution,
)


class SupervisedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan_mission({
            "question": "noyau période",
            "mission_type": "mathematical",
            "mission_id": "P3-TEST-01",
        })
        # P3 validates the P2 contract shape; no repository reads are needed here.
        self.bundle = {
            "context_preparer": "omega-adaptive-prism-rce",
            "mission": {"question": "noyau période"},
            "packages": [
                {"role": task["role"]} for task in self.plan["tasks"]
            ],
            "manifest": {"content_hash": "a" * 64},
        }

    def test_starts_without_claiming_execution_or_independence(self):
        run = start_execution(self.plan, self.bundle)
        self.assertEqual(run["run_status"], "open")
        self.assertEqual(run["execution_policy"]["model_calls_performed_by_module"], 0)
        self.assertFalse(run["execution_policy"]["perspectives_are_independent_agents"])
        self.assertTrue(all(p["status"] == "not_executed" for p in run["perspectives"]))

    def test_records_only_explicit_actual_output(self):
        run = start_execution(self.plan, self.bundle)
        role = run["perspectives"][0]["role"]
        record_perspective(run, role, status="completed", output="Contre-test effectué.",
                           evidence_refs=["test:case-1"], limitations=["Même modèle principal"])
        perspective = run["perspectives"][0]
        self.assertEqual(perspective["output"], "Contre-test effectué.")
        self.assertEqual(perspective["independence"], "same_model_role_perspective")
        self.assertEqual(perspective["scientific_validation"], "not_performed")

    def test_completed_requires_output(self):
        run = start_execution(self.plan, self.bundle)
        with self.assertRaises(SupervisedExecutionError):
            record_perspective(run, "refuter", status="completed")

    def test_rejects_unknown_and_duplicate_role_recording(self):
        run = start_execution(self.plan, self.bundle)
        with self.assertRaises(SupervisedExecutionError):
            record_perspective(run, "agent_independant", status="blocked")
        record_perspective(run, "refuter", status="blocked")
        with self.assertRaises(SupervisedExecutionError):
            record_perspective(run, "refuter", status="blocked")

    def test_rejects_mismatched_context_bundle(self):
        bundle = dict(self.bundle)
        bundle["mission"] = {"question": "autre question"}
        with self.assertRaises(SupervisedExecutionError):
            start_execution(self.plan, bundle)

    def test_close_reports_coverage_without_scientific_verdict(self):
        run = start_execution(self.plan, self.bundle)
        record_perspective(run, "refuter", status="blocked", limitations=["Contexte insuffisant"])
        closed = close_execution(run)
        self.assertEqual(closed["coverage"]["blocked"], 1)
        self.assertEqual(closed["coverage"]["not_executed"], 1)
        self.assertEqual(closed["scientific_verdict"], "not_produced")
        self.assertIsNone(closed["synthesis"])
        with self.assertRaises(SupervisedExecutionError):
            record_perspective(closed, "formalist", status="blocked")


if __name__ == "__main__":
    unittest.main()
