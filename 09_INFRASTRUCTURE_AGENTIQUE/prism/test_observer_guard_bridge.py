"""Safety gates and non-regression of Omega's existing planner.

All source partitions are supplied explicitly. These tests cannot certify
a scientific statement, completeness of available probes or source origin.
"""
import json
from itertools import product
import unittest

from planner import MissionValidationError, plan_mission
from observer_guard_bridge import inspect_observer_evidence
from legacy_observer_transfer import partitions, block_count
from legacy_guard_benchmark import run_audit, independent_125


class ObserverGuardBridgeTests(unittest.TestCase):
    MISSION={"question":"Vérifier une hypothèse","mission_type":"mathematical",
             "decision_context":{"blocking_uncertainty":"Preuve absente",
                                 "verification":"Calcul exact",
                                 "verification_effect":"Un témoin réfuterait"}}

    def test_optin_only_no_existing_decision_or_roles_change(self):
        old=plan_mission(self.MISSION)
        self.assertNotIn("observer_audit",old)
        spec={"termination":{
            "current_partition":[0,0,0],
            "selected_probe_partition":[0,0,0],
            "listed_probe_partitions":[[0,0,0],[0,0,1]],
            "declared_exhaustive":False}}
        new=plan_mission({**self.MISSION,"observer_audit":spec})
        self.assertEqual({k:v for k,v in new.items() if k!="observer_audit"},old)
        self.assertEqual(new["observer_audit"]["mode"],"read_only_advisory_opt_in")
        self.assertEqual(new["observer_audit"]["durable_memory_writes_performed"],0)
        self.assertFalse(new["observer_audit"]["source_authenticity_verified"])
        self.assertFalse(new["observer_audit"]["scientific_certificate_issued"])
        self.assertFalse(new["observer_audit"]["planner_decisions_modified"])
        self.assertEqual(
            new["observer_audit"]["termination"]["status"],
            "underinformative_relative_to_listed_probes")
        self.assertEqual(
            new["observer_audit"]["termination"]["candidate_probe_indexes"],[1])
        self.assertEqual(new["next_action"],old["next_action"])

    def test_declared_exhaustiveness_is_not_certification(self):
        x={"current_partition":[0,0,1],
           "selected_probe_partition":[0,0,1],
           "listed_probe_partitions":[[0,0,1]]}
        a=inspect_observer_evidence({"termination":{**x,"declared_exhaustive":False}})
        b=inspect_observer_evidence({"termination":{**x,"declared_exhaustive":True}})
        self.assertEqual(a["termination"]["status"],"closure_unknown")
        self.assertEqual(b["termination"]["status"],
                         "closed_assuming_declared_probe_list")
        self.assertFalse(b["source_authenticity_verified"])
        self.assertFalse(b["scientific_certificate_issued"])
        self.assertTrue(b["termination"]["assumption_only_not_source_certification"])

    def test_nonterminal_probes_do_not_get_false_closure(self):
        result=inspect_observer_evidence({"termination":{
           "current_partition":[0,0,0],
           "selected_probe_partition":[0,0,1],
           "listed_probe_partitions":[[0,0,1]],
           "declared_exhaustive":True}})
        self.assertEqual(result["termination"]["status"],"not_a_fixed_point")

    def test_representation_substitution_only_affects_working_view(self):
        spec={"current_partition":[0,0,1,1],
              "target_partition":[0,1,0,1],"capacity":2}
        a=plan_mission({**self.MISSION,"observer_audit":{"reconfiguration":spec}})
        z=a["observer_audit"]["reconfiguration"]
        self.assertEqual(z["decision"],"replace")
        self.assertEqual((z["current_blocks"],z["target_blocks"],z["joint_blocks"]),
                         (2,2,4))
        self.assertTrue(z["working_representation_only"])
        self.assertFalse(z["durable_evidence_may_be_discarded"])
        self.assertEqual(a["execution_model"]["memory_writes_performed"],0)

    def test_reconfiguration_keep_refine_and_infeasible(self):
        base=(0,0,1,1)
        def decision(target,cap):
            return inspect_observer_evidence({"reconfiguration":{
                "current_partition":list(base),"target_partition":list(target),
                "capacity":cap}})["reconfiguration"]["decision"]
        self.assertEqual(decision(base,2),"keep")
        self.assertEqual(decision((0,1,2,3),2),"infeasible")
        self.assertEqual(decision((0,1,2,2),3),"refine")

    def test_exact_w06_49_cases(self):
        two=[p for p in partitions(4) if block_count(p)==2]
        self.assertEqual(len(two),7)
        scores={}
        for a,b in product(two,repeat=2):
            r=inspect_observer_evidence({"reconfiguration":{
                "current_partition":list(a),"target_partition":list(b),
                "capacity":2}})["reconfiguration"]["decision"]
            scores[r]=scores.get(r,0)+1
        self.assertEqual(scores,{"keep":7,"replace":42})

    def test_malformed_or_untrusted_enumerations_are_rejected(self):
        term={"current_partition":[0,0,0],
              "selected_probe_partition":[0,0,0],
              "listed_probe_partitions":[[0,0,0]],
              "declared_exhaustive":False}
        bads=[
            {},
            {"unknown":term},
            {"termination":None},
            {"termination":{**term,"declared_exhaustive":"yes"}},
            {"termination":{**term,"selected_probe_partition":[0,0,1]}},
            {"termination":{**term,"listed_probe_partitions":[]}},
            {"termination":{**term,"current_partition":[False,0,0]}},
            {"termination":{**term,"current_partition":[-1,0,0]}},
            {"termination":{**term,"listed_probe_partitions":[[0,0]]}},
            {"termination":{**term,"bogus":"extra"}},
            {"reconfiguration":{"current_partition":[0,0],
                                "target_partition":[0,0],
                                "capacity":True}},
            {"reconfiguration":{"current_partition":[0,0],
                                "target_partition":[0,0,0],
                                "capacity":2}},
        ]
        for x in bads:
            with self.subTest(x=x), self.assertRaises(MissionValidationError):
                plan_mission({**self.MISSION,"observer_audit":x})

    def test_legacy_guard_budget_and_full_reference(self):
        z=run_audit()
        s=z["primary"]
        self.assertEqual(s,independent_125())
        self.assertEqual(s["cases"],125)
        self.assertEqual(s["guarded_correct"],125)
        self.assertEqual(s["fixed_both_correct"],125)
        self.assertEqual(s["naive_probe_calls"],125)
        self.assertEqual(s["fixed_both_probe_calls"],250)
        self.assertEqual(s["guarded_second_probes"],125-s["naive_correct"])
        self.assertEqual(s["guarded_probe_calls"],
                         125+s["guarded_second_probes"])
        self.assertTrue(0<s["guarded_second_probes"]<125)
        self.assertLessEqual(s["guarded_probe_calls"],
                             s["fixed_both_probe_calls"])
        print("LEGACY_GUARD_RESULT "+json.dumps(z["primary"],sort_keys=True))


if __name__ == "__main__":
    unittest.main()
