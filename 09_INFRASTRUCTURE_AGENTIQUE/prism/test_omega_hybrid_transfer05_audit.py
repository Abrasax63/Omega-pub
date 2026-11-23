"""Audit regression: independent clique oracle + frozen evidence receipt."""
import copy
import tempfile
from pathlib import Path
import unittest

from concept_abstraction_lab import check_axioms
import omega_hybrid_transfer05 as model
import omega_hybrid_transfer05_audit as forensic


class FakeClient:
    def __init__(self):self.calls=[]
    def __call__(self,messages,max_tokens):
        self.calls.append(messages)
        user=messages[-1]["content"]
        raw=('{"rule":"Test all required properties for all triples."}'
             if "Formulate one transferable" in user else
             '{"holds":true,"failed_axioms":[]}')
        return {"text":raw,"usage":{"prompt_tokens":len(
             (model.COMMON_SYSTEM+"\n"+user).split()),"completion_tokens":18},
             "time_s":0.01}


class IndependentAuditTests(unittest.TestCase):
    def test_component_clique_oracle_agrees_on_all_64_cases(self):
        for mask in range(64):
            edges=model.relation(mask)
            facts=check_axioms(model.NODES,edges)
            exact=all(facts[a]["holds"] for a in model.AXIOMS)
            self.assertEqual(forensic.clique_oracle(
                [list(p) for p in sorted(edges)]),exact,msg=str(mask))

    def test_independent_oracle_rejects_missing_transitive_shortcut(self):
        nodes=model.NODES
        edges=[[x,x] for x in nodes]+[[nodes[0],nodes[1]],
              [nodes[1],nodes[0]],[nodes[1],nodes[2]],[nodes[2],nodes[1]]]
        self.assertFalse(forensic.clique_oracle(edges))

    def test_complete_mock_report_audits_and_tallies_total_model_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            result=model.run(path,"test",injected_client=FakeClient(),
                             token_counter=lambda x:len(x.split()))
            inp,oracle=model.make_manifest()
            audited=forensic.audit(result,inp,oracle)
            self.assertEqual(audited["status"],
                             "POST_RUN_DOUBLE_ORACLE_AGREES_DESCRIPTIVE_ONLY")
            self.assertEqual(audited["n"],8)
            self.assertEqual(audited["total_cost_including_rule_generation"]["D"]["calls"],8)
            self.assertEqual(audited["total_cost_including_rule_generation"]["G"]["calls"],9)
            self.assertEqual(audited["total_cost_including_rule_generation"]["W"]["calls"],9)
            self.assertEqual(audited["discordant_pairs"]["W_better_than_G"],0)
            self.assertFalse(audited["independently_certified_new_competence"])

    def test_tampered_truth_or_reply_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=model.run(Path(tmp),"test",injected_client=FakeClient(),
                             token_counter=lambda x:len(x.split()))
            inp,oracle=model.make_manifest()
            bad=copy.deepcopy(oracle)
            bad["answers"][0]["holds"]=not bad["answers"][0]["holds"]
            self.assertEqual(forensic.audit(result,inp,bad)["reason"],
                             "FROZEN_MANIFEST_MISMATCH")
            bad=copy.deepcopy(result)
            bad["tasks"][0]["arms"]["D"]["raw"]="not json"
            self.assertEqual(forensic.audit(bad,inp,oracle)["reason"],"SCORE_MISMATCH_D")


if __name__ == "__main__":unittest.main()
