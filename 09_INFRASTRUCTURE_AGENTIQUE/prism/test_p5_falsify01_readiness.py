"""Tests for P5 FALSIFY-01. Fixtures DO NOT constitute experimental results."""
from copy import deepcopy
from pathlib import Path
import unittest

import p5_falsify01_readiness as m

ROOT=Path(__file__).resolve().parents[2]

class FiveArmReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audited=m.audit(ROOT)

    def test_actual_p1_plans_and_never_executes_model(self):
        data=self.audited
        self.assertEqual(data["actual_P1_execution_model"]["status"],"planning_only")
        self.assertEqual(data["actual_P1_execution_model"]["model_calls_performed"],0)
        self.assertEqual(data["actual_P1_next_action"]["action"],"verify")
        self.assertEqual(data["actual_P1_execution_model"]["memory_writes_performed"],0)

    def test_actual_p2_context_and_p3_recorder_not_execution(self):
        data=self.audited
        if data["actual_P2_error"] is None:
            self.assertEqual(data["actual_P2_execution_model"]["status"],
                             "context_preparation_only")
            self.assertEqual(data["actual_P2_execution_model"]["model_calls_performed"],0)
            self.assertEqual(data["actual_P2_execution_model"]["memory_writes_performed"],0)
            self.assertGreaterEqual(
                data["actual_P2_manifest"]["search_calls"],1)
            self.assertEqual(data["actual_P3_execution_policy"]["model_calls_performed_by_module"],0)
            self.assertEqual(data["actual_P3_scientific_verdict"],"not_produced")
            self.assertGreater(data["actual_P3_coverage"]["not_executed"],0)
        else:
            self.assertIsNone(data["actual_P3_execution_policy"])

    def test_five_genuine_arms_not_ready_until_actual_causal_interventions(self):
        x=self.audited
        self.assertEqual(x["readiness"],"NOT_READY")
        self.assertEqual(x["status"],"PRE_REGISTERED_5_ARM_EXECUTION_NOT_READY")
        self.assertEqual(len(x["required_arms"]),5)
        self.assertTrue(all(not x["pass"] for x in x["gates"].values()))
        self.assertFalse(x["arms_have_genuine_5_way_results"])
        self.assertEqual(x["model_inference_now"],0)
        self.assertEqual(x["new_genuine_evaluation_tasks_scored"],0)
        self.assertEqual(len(x["pre_registration_sha256"]),64)

    def test_finite_observability_has_real_counterexample_not_only_a_log(self):
        x=self.audited["observability_phantom_test"]
        self.assertTrue(x["locally_possible"])
        self.assertFalse(x["realizable"])
        self.assertEqual(x["prefix_survivor_counts"],[2,1,0])
        self.assertEqual(self.audited["observability_survivor_filter_positive_test"][
            "possible_states_after_U_equals_1"],8)

    def example(self,arm,action="STOP",label="ABSTAIN"):
        return {
            "arm":arm,"task_id":"FRESH-HIDDEN-TASK-001",
            "model_calls":1,"model_sha":"4ad58f489cb57b0c2cf934e5df12345678901234",
            "actual_action":action,"final_answer":label,
            "memory_reads":2 if arm!="omega_no_memory" else 0,
            "observability_filter_calls":1 if arm!="omega_no_observability" else 0,
            "provenance_evidence":[{"ref":"VERIFIABLE-SOURCE"}],
            "execution_kind":"REAL_TOOL_AND_MODEL_CALLS",
            "tokens_total":120,"tool_calls":2,
        }

    def test_causal_ablation_must_change_action_not_just_flags(self):
        no_memory=self.example("omega_no_memory")
        full=self.example("omega_full")
        same=m.ablation_pair_certification(no_memory,full,"memory")
        self.assertEqual(same["status"],
                         "NON_IDENTIFIABLE_SAME_ACTION_AND_DECISION")
        full["actual_action"]="VERIFY_INDEPENDENT_SOURCE"
        changed=m.ablation_pair_certification(no_memory,full,"memory")
        self.assertEqual(changed["status"],
                         "PASS_CAUSAL_MECHANISM_ACTIVATION_AND_ACTION_DIVERGENCE")
        no_obs=self.example("omega_no_observability")
        changed=m.ablation_pair_certification(no_obs,full,"observability")
        self.assertEqual(changed["status"],
                         "PASS_CAUSAL_MECHANISM_ACTIVATION_AND_ACTION_DIVERGENCE")

    def test_ablation_rejects_fake_or_decorative_flags(self):
        full=self.example("omega_full")
        old=self.example("omega_no_memory")
        old["memory_reads"]=1
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")
        old=self.example("omega_no_memory")
        old["execution_kind"]="SIMULATED_MODEL"
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")
        old=self.example("omega_no_memory")
        old["model_calls"]=0
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")
        old=self.example("omega_no_memory")
        old["model_sha"]="unversioned"
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")

    def test_no_gold_or_hidden_source_labels_in_policy_trace(self):
        bad=self.example("omega_full")
        bad["evaluator_only_label"]="ENTAILED"
        with self.assertRaises(ValueError):
            m._recorded_decision(bad)
        bad=self.example("omega_full")
        bad["memory_reads"]=0
        with self.assertRaises(ValueError):
            m._recorded_decision(bad)
        bad=self.example("omega_no_observability")
        bad["observability_filter_calls"]=1
        with self.assertRaises(ValueError):
            m._recorded_decision(bad)

    def test_different_model_or_task_cannot_count_as_ablation(self):
        old=self.example("omega_no_memory")
        full=self.example("omega_full","VERIFY","ENTAILED")
        full["model_sha"]="3"*40
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")
        full=self.example("omega_full","VERIFY","ENTAILED")
        full["task_id"]="DIFFERENT-TASK"
        with self.assertRaises(ValueError):
            m.ablation_pair_certification(old,full,"memory")

    def test_more_budget_not_an_adaptive_result(self):
        x=self.audited
        self.assertFalse(x["gates"]["GATE_RESOURCE_PARITY"]["pass"])
        self.assertFalse(x["gates"]["GATE_NEW_BLINDED_TASKS"]["pass"])
        self.assertFalse(x["gates"]["GATE_INDEPENDENT_SEMANTIC_REVIEW"]["pass"])
        self.assertIn("not a performed falsification",
                      " ".join(x["restrictions"]).lower())

if __name__=="__main__":
    unittest.main()
