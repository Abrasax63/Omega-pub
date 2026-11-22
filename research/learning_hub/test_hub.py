"""Unit tests for cross-PR Omega learning unification, no new LLM calls."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"learning_lab"))
import hub
import verified_python_training_export as ex
from test_verified_python_training_export import fake_report, RUN, COMMIT


def registry():
    return hub.validate_registry(hub.read_json(HERE/"REGISTRY.json",130_000))


def synthetic_state():
    r=registry()
    # Synthetic positive control: this is NOT the pinned real V3 artifact.
    # consolidate() only accepts the real artifact, verified by SHA.
    source=fake_report()
    output=ex.export_candidate_dataset(source,COMMIT,RUN)
    candidates=output["training_candidates"]
    decision=hub.gate_admission(candidates,r)
    events=hub.chain([
      {"event":"source_snapshot_inspected",
       "payload":{"run_id":hub.AUDITED_RUN_ID,
                  "git_commit":hub.SOURCE_SHA,
                  "report_sha256":hub.SOURCE_REPORT_SHA,
                  "prior_holdout_consumed":True}},
      {"event":"programming_skill_candidates_admitted_only_to_quarantine",
       "payload":{"admitted":len(candidates),
                  "distinct_skill_families":len(candidates),
                  "candidate_hash":hub.digest(candidates),
                  "hidden_oracles_exported":False,
                  "candidate_training_parameters_updated":False}},
      {"event":"training_preparation_gate_evaluated",
       "payload":{"gate_status":decision["status"],
                  "reasons":decision["reasons"],
                  "automatic_training_performed":False}}
    ])
    return {
      "schema":hub.SCHEMA,"status":"INTEGRATED_QUARANTINE_ONLY",
      "registry_sha256":hub.digest(r),
      "provenance":{"source_run":RUN,"source_commit":COMMIT,
                    "report_sha256":hub.SOURCE_REPORT_SHA},
      "existing_components":hub.audit_components(r),
      "previous_experiment_observations":{},
      "skill_candidates":candidates,
      "candidate_manifest":output["manifest"],
      "training_gate":decision,
      "events":events,"ledger_head_sha256":events[-1]["sha256"],
      "training_started":False,"model_weights_updated":False,
      "main_modified":False,"this_is_not_new_learning_evidence":True,
    }


class LearningHubTests(unittest.TestCase):
    def test_registry_audits_all_reused_components(self):
        r=registry()
        self.assertEqual(len(r["components"]),8)
        self.assertEqual(hub.audit_components(r)["runtime_programming_modules_available"],4)
        self.assertEqual(hub.audit_components(r)["referenced_external_unmerged_modules"],4)
        self.assertFalse(r["allow_automatic_model_training"])
        self.assertFalse(r["external_fresh_holdout_pre_registered"])

    def test_train26_incompatible_contract_is_not_mislabeled_python(self):
        r=registry()
        for c in r["components"]:
            if c["name"]=="lora_trainer":
                c["accepts_python_repair_samples"]=True
        with self.assertRaisesRegex(ValueError,"MATHEMATICAL_TRAINER_MISREPRESENTED"):
            hub.validate_registry(r)

    def test_frozen_artifact_pin_cannot_be_replaced(self):
        r=registry()
        r["source_experiment"]["report_sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"WRONG_REPORT_HASH"):
            hub.validate_registry(r)

    def test_unsupported_alternative_report_cannot_enter(self):
        # Fake report has precisely V3 shape, but is not the source run.
        raw=json.dumps(fake_report()).encode()
        with self.assertRaisesRegex(ValueError,"V3_SOURCE_REPORT_SHA256_MISMATCH"):
            hub.consolidate(raw,registry())

    def test_all_gates_remain_closed_even_with_many_samples(self):
        r=registry()
        samples=[{"family_id":"skill-"+str(i)} for i in range(50)]
        gate=hub.gate_admission(samples,r)
        self.assertEqual(gate["status"],"TRAINING_NOT_AUTHORIZED")
        self.assertIn("NO_INDEPENDENT_FRESH_EVALUATION_COHORT",gate["reasons"])
        self.assertIn("TRAIN26_MATH_LABEL_CONTRACT_INCOMPATIBLE_WITH_PYTHON",gate["reasons"])
        self.assertIn("AUTOMATIC_TRAINING_DISABLED_BY_POLICY",gate["reasons"])

    def test_two_verified_examples_do_not_open_training(self):
        s=synthetic_state()
        self.assertEqual(len(s["skill_candidates"]),2)
        self.assertTrue(hub.verify_state(s,registry()))
        self.assertIn("INSUFFICIENT_VERIFIED_SKILL_FAMILIES",s["training_gate"]["reasons"])

    def test_chain_rejects_removed_event(self):
        s=synthetic_state()
        s["events"].pop(1)
        with self.assertRaisesRegex(ValueError,"MISSING_LEARNING_EVENTS"):
            hub.verify_state(s,registry())

    def test_chain_rejects_forged_event(self):
        s=synthetic_state()
        s["events"][1]["payload"]["admitted"]=500
        with self.assertRaisesRegex(ValueError,"LEARNING_LEDGER_RECORD_TAMPERED"):
            hub.verify_state(s,registry())

    def test_tampered_candidate_is_detected(self):
        s=synthetic_state()
        s["skill_candidates"][0]["target"]="def transform(s): return []"
        with self.assertRaisesRegex(ValueError,"CORRUPT_SKILL_CANDIDATE"):
            hub.verify_state(s,registry())

    def test_no_false_model_training_claim(self):
        s=synthetic_state()
        s["model_weights_updated"]=True
        with self.assertRaisesRegex(ValueError,"ILLEGAL_POSTHOC_SUCCESS"):
            hub.verify_state(s,registry())

    def test_duplicate_families_fail(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SKILL_FAMILIES"):
            hub.gate_admission([{"family_id":"a"},{"family_id":"a"}],registry())

    def test_json_roundtrip_preserves_registry_gate_and_events(self):
        s=synthetic_state()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"hub.json"
            p.write_text(json.dumps(s),encoding="utf-8")
            self.assertTrue(hub.verify_state(hub.read_json(p,hub.MAX_SNAPSHOT_BYTES),registry()))

    def test_hub_does_not_load_math_training_gold(self):
        script=(HERE/"hub.py").read_text(encoding="utf-8")
        self.assertNotIn("HOLDOUT_GOLD_EVAL_ONLY.json",script)
        self.assertNotIn("get_peft_model(",script)
        self.assertNotIn("torch.optim.",script)



def synthetic_index(state):
    return {
      "schema":"OMEGA_LEARNING_HUB_PERSISTED_SKILL_INDEX_01",
      "source_v3_commit":hub.SOURCE_SHA,
      "source_v3_report_sha256":hub.SOURCE_REPORT_SHA,
      "registry_sha256":state["registry_sha256"],
      "candidate_dataset_sha256":state["candidate_manifest"]["records_sha256"],
      "ledger_head_sha256":state["ledger_head_sha256"],
      "status":"QUARANTINE_INSUFFICIENT_VERIFIED_DIVERSITY",
      "training_started":False,"parametric_learning_demonstrated":False,
      "general_python_competence_certified":False,
      "used_hidden_tests_not_available_as_fresh_holdout":True,
      "verified_candidates":[{
         "family_id":s["family_id"],"task":s["task"],"best_code":s["target"],
         "source_raw_model_sha256":s["admission_evidence"]["model_raw_sha256"],
         "candidate_record_sha256":s["record_sha256"],
         "original_best_attempt":s["original_best_attempt"],
      } for s in state["skill_candidates"]],
    }


class PersistentIndexTests(unittest.TestCase):
    def test_exact_candidate_index_matches_a_valid_snapshot(self):
        s=synthetic_state()
        self.assertTrue(hub.verify_persisted_index(synthetic_index(s),s,registry()))

    def test_index_rejects_modified_source_code(self):
        s=synthetic_state()
        idx=synthetic_index(s)
        idx["verified_candidates"][0]["best_code"]="def transform(s): return []"
        with self.assertRaisesRegex(ValueError,"INDEX_CODE_MISMATCH"):
            hub.verify_persisted_index(idx,s,registry())

    def test_index_rejects_duplicated_skill_family(self):
        s=synthetic_state()
        idx=synthetic_index(s)
        idx["verified_candidates"][0]=copy.deepcopy(idx["verified_candidates"][1])
        with self.assertRaisesRegex(ValueError,"INDEX_UNKNOWN_OR_DUPLICATE_FAMILY"):
            hub.verify_persisted_index(idx,s,registry())

    def test_index_rejects_model_training_claim(self):
        s=synthetic_state()
        idx=synthetic_index(s)
        idx["parametric_learning_demonstrated"]=True
        with self.assertRaisesRegex(ValueError,"INDEX_CLAIMS_UNPROVEN_LEARNING"):
            hub.verify_persisted_index(idx,s,registry())

    def test_index_rejects_changed_audit_event_head(self):
        s=synthetic_state()
        idx=synthetic_index(s)
        idx["ledger_head_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"INDEX_EVENT_LEDGER_MISMATCH"):
            hub.verify_persisted_index(idx,s,registry())


if __name__=="__main__":
    unittest.main()
