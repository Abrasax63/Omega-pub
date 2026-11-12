"""FALSIFY03 tests: real finite witness safety; no LLM in unit tests."""
from copy import deepcopy
import unittest

import p5_falsify03_governance as e


class CertifiedProofGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal,cls.test,cls.count=e.dataset()
        cls.a=cls.test[0]
        cls.b=cls.test[-1]

    def test_full_universe_two_oracles_checked_not_a_fictitious_result(self):
        self.assertEqual(self.count,57344)
        self.assertEqual(len(self.cal),4)
        self.assertEqual(len(self.test),16)
        self.assertEqual(len({x["id"] for x in self.cal+self.test}),20)
        self.assertEqual(sum(r["gold_evaluator_only"]=="A" for r in self.test),8)
        self.assertEqual(sum(r["gold_evaluator_only"]=="B" for r in self.test),8)
        self.assertEqual(e.dataset()[1][0]["id"],self.test[0]["id"])
        self.assertTrue(all(len(r["t"])==4 and len(r["word"])==4 for r in self.test))

    def test_genuine_dual_path_certificate_supported_by_states(self):
        for r in self.cal+self.test:
            cert,t=e.certificate(r)
            self.assertGreaterEqual(t,0)
            self.assertEqual(cert["source_sha256"],e._hash(e.spec(r)))
            self.assertEqual(cert["independent_data_providers"],1)
            self.assertEqual(cert["independent_computation_methods"],2)
            self.assertEqual(e.validate_certificate(r,cert)["status"],e.VALID)
            self.assertEqual(e.governed_answer(r,cert)[0],r["gold_evaluator_only"])

    def test_invalid_task_hash_scope_and_provider_abstain(self):
        cert,_=e.certificate(self.a)
        for field,val in (
            ("source_sha256","0"*64),("scope","N3-L3"),
            ("source","invented_source"),("kind","trusted_unchecked")):
            bad=deepcopy(cert)
            bad[field]=val
            out,reason=e.governed_answer(self.a,bad)
            self.assertEqual(out,"ABSTAIN_INVALID_CERTIFICATE")
            self.assertEqual(reason["status"],"INVALID_OR_STALE_SOURCE")
        out,reason=e.governed_answer(self.a,{"answer":"A"})
        self.assertEqual(out,"ABSTAIN_INVALID_CERTIFICATE")
        self.assertEqual(reason["status"],"INVALID_SCHEMA")

    def test_forged_witness_prefix_final_states_and_boolean_abstain(self):
        cert,_=e.certificate(self.a)
        changes={
            "prefix_counts":[999]*4,
            "final_states":[999],
            "initial_witness_states":[999],
            "is_possible":not cert["is_possible"],
        }
        for key,mutated in changes.items():
            bad=deepcopy(cert)
            bad[key]=mutated
            out,reason=e.governed_answer(self.a,bad)
            self.assertEqual(out,"ABSTAIN_INVALID_CERTIFICATE")
            self.assertEqual(reason["status"],"CONTRADICTORY_OR_INCOMPATIBLE_WITNESS")

    def test_wrong_provenance_count_or_algorithm_abstain(self):
        cert,_=e.certificate(self.b)
        for name,val in (
            ("independent_data_providers",2),
            ("independent_computation_methods",1),
            ("algorithms",["output_from_prompt_only"])):
            bad=deepcopy(cert)
            bad[name]=val
            out,reason=e.governed_answer(self.b,bad)
            self.assertEqual(out,"ABSTAIN_INVALID_CERTIFICATE")
            self.assertEqual(reason["status"],"INVALID_PROVENANCE")

    def test_classical_and_direct_have_identical_model_prompt(self):
        for row in self.cal+self.test:
            self.assertEqual(e._messages(row,"direct"),
                             e._messages(row,"classical_exact"))
            self.assertNotEqual(e._messages(row,"direct"),
                                e._messages(row,"omega_no_memory",cert=e.certificate(row)[0]))
            self.assertNotIn("gold_evaluator_only",str(e._messages(row,"direct")))
            self.assertNotIn("gold_evaluator_only",str(e._messages(row,"omega_no_memory",
                                         cert=e.certificate(row)[0])))

    def test_branches_are_actual_decision_mechanisms_not_renamed_aliases(self):
        # These interventions are software controls, NOT a measured model effect.
        r=self.b
        self.assertEqual(r["gold_evaluator_only"],"B")
        cert,_=e.certificate(r)
        raw_model_response="A"
        gated,_=e.governed_answer(r,cert)
        self.assertEqual(gated,"B")
        self.assertNotEqual(gated,raw_model_response)
        self.assertEqual("A",raw_model_response)  # D has no certificate

    def test_same_proof_is_not_two_independent_data_sources(self):
        for r in (self.a,self.b):
            cert,_=e.certificate(r)
            self.assertEqual(cert["independent_data_providers"],1)
            self.assertEqual(cert["independent_computation_methods"],2)
            self.assertEqual(cert["source"],"explicit_task_spec")
            self.assertEqual(len(cert["prefix_counts"]),4)

    def test_planner_and_model_versions_are_real_sources(self):
        plan=e._plan(self.a)
        self.assertEqual(plan["planner"],"omega-adaptive-prism")
        self.assertEqual(plan["execution_model"]["status"],"planning_only")
        self.assertEqual(plan["next_action"]["action"],"verify")
        self.assertEqual(e.earlier.MODEL_REVISION,
                         "7ae557604adf67be50417f59c2c2f167def9a775")
        self.assertEqual(e.earlier.TOKEN_CAP,512)
        self.assertEqual(len(e.ARMS),5)


if __name__=="__main__":
    unittest.main()
