"""Versioned-source advisory may alter ONLY the optional diagnostic output.

The actual historical experiment revalidates Git trees and blobs itself.
This planner bridge does NOT validate authenticity or semantic truth.
"""
import copy
import unittest

from planner import MissionValidationError,plan_mission
from versioned_evidence_planner_bridge import (
    MAX_CLAIMS,MAX_CHANGED_PATHS,MAX_DEPENDENCIES_PER_CLAIM,MAX_PATH_CHARS,
    audit_reported_source_change,
)


class VersionedSourcePlannerTests(unittest.TestCase):
    base={
        "question":"Les sources de la preuve ont-elles été modifiées ?",
        "mission_type":"documentary",
        "decision_context":{
            "blocking_uncertainty":"Une assertion dépend de fichiers révisés",
            "verification":"Contrôler les empreintes à la révision cible",
            "verification_effect":"Réémettre ou suspendre les certificats concernés",
        },
    }
    before="a"*40
    after="b"*40
    good={
        "previous_commit":before,
        "target_commit":after,
        "changed_paths":["proofs/proposition.py"],
        "declared_diff_complete":False,
        "claims":[
            {"id":"T1","dependencies":["proofs/proposition.py","docs/definition.md"]},
            {"id":"T2","dependencies":["docs/other.md"]},
        ],
    }

    def test_absent_flag_leaves_entire_existing_plan_unchanged(self):
        plan=plan_mission(self.base)
        self.assertNotIn("source_revision_audit",plan)
        actual=plan_mission({**self.base,"source_revision_audit":self.good})
        self.assertEqual({k:v for k,v in actual.items()
                          if k!="source_revision_audit"},plan)
        result=actual["source_revision_audit"]
        self.assertEqual(result["claim_ids_needing_revalidation"],["T1"])
        self.assertEqual(result["claim_ids_without_reported_change"],["T2"])
        self.assertFalse(result["source_metadata_authentication_performed"])
        self.assertEqual(result["source_content_verifications_performed"],0)
        self.assertFalse(result["scientific_certificate_issued"])
        self.assertFalse(result["unaffected_claims_certified_as_current"])
        self.assertFalse(result["historical_certificates_modified"])
        self.assertEqual(result["durable_memory_writes_performed"],0)
        self.assertEqual(actual["next_action"],plan["next_action"])

    def test_claimed_complete_diff_never_authenticates_document_or_truth(self):
        declared=copy.deepcopy(self.good)
        declared["declared_diff_complete"]=True
        report=audit_reported_source_change(declared)
        self.assertTrue(report["metadata_completeness_declared"])
        self.assertFalse(report["source_metadata_authentication_performed"])
        self.assertFalse(report["unaffected_claims_certified_as_current"])
        self.assertFalse(report["scientific_certificate_issued"])

    def test_no_change_manifest_means_no_automatic_certification(self):
        spec=copy.deepcopy(self.good)
        spec["changed_paths"]=[]
        spec["previous_commit"]=self.after
        report=audit_reported_source_change(spec)
        self.assertEqual(report["claim_ids_needing_revalidation"],[])
        self.assertEqual(report["claim_ids_without_reported_change"],["T1","T2"])
        self.assertFalse(report["source_metadata_authentication_performed"])

    def test_strict_input_fail_closed(self):
        bads=[
            None,{},{"unknown":True},
            {**self.good,"previous_commit":"HEAD"},
            {**self.good,"previous_commit":"A"*40},
            {**self.good,"declared_diff_complete":"yes"},
            {**self.good,"changed_paths":["../proofs/evil.py"]},
            {**self.good,"changed_paths":["/absolute/path"]},
            {**self.good,"changed_paths":["tests\\escape.py"]},
            {**self.good,"changed_paths":["a//b"]},
            {**self.good,"changed_paths":["control\nchar"]},
            {**self.good,"changed_paths":["p.py","p.py"]},
            {**self.good,"changed_paths":["a"*513]},
            {**self.good,"changed_paths":["foo.py"]*257},
            {**self.good,"target_commit":self.before},
            {**self.good,"claims":[]},
            {**self.good,"claims":[{"id":"T1","dependencies":["x"]}]*257},
            {**self.good,"claims":[{"id":"T1","dependencies":["x"]},
                                   {"id":"T1","dependencies":["y"]}]},
            {**self.good,"claims":[{"id":"T1","dependencies":[]}]},
            {**self.good,"claims":[{"id":"T1","dependencies":["x"]*17}]},
            {**self.good,"claims":[{"id":"T1","dependencies":["x","x"]}]},
            {**self.good,"claims":[{"id":"T1","dependencies":["x"],"other":9}]},
        ]
        for spec in bads:
            with self.subTest(spec=str(spec)[:90]):
                with self.assertRaises(MissionValidationError):
                    plan_mission({**self.base,"source_revision_audit":spec})

    def test_validation_caps_are_explicit_and_not_truth_guarantees(self):
        self.assertEqual(MAX_CLAIMS,256)
        self.assertEqual(MAX_CHANGED_PATHS,256)
        self.assertEqual(MAX_DEPENDENCIES_PER_CLAIM,16)
        self.assertEqual(MAX_PATH_CHARS,512)


if __name__=="__main__":
    unittest.main()
