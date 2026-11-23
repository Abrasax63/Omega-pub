"""No LLM calls: independent auditor tests for OMEGA-TUTOR-07."""
import copy
import tempfile
from pathlib import Path
import unittest

import omega_hybrid_tutor07 as t
import omega_hybrid_tutor07_audit as a


class FakeModel:
    def __call__(self,messages,limit):
        prompt=messages[-1]["content"]
        if "Formulate an actionable procedure" in prompt:
            raw='{"rule":"Check every directed premise and every missing edge; for a positive claim match a complete partition."}'
        else:
            raw='{"holds":false,"failed_axioms":["transitive"],"certificate":{"kind":"missing_transitive_edge","triple":["a","b","c"],"premises":{"xy":true,"yz":true,"xz":false}}}'
        return {"text":raw,"usage":{"prompt_tokens":len(
             (t.SYSTEM+"\n"+prompt).split()),"completion_tokens":25},
             "time_s":0.02}


class AuditTests(unittest.TestCase):
    def fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            return t.run(Path(tmp),"offline",client=FakeModel(),
                         token_counter=lambda s:len(s.split()))

    def test_complete_fake_run_recalculates_without_learning_claim(self):
        r=self.fixture()
        q,o=t.make_holdout()
        report=a.audit(r,q,o)
        self.assertEqual(report["status"],"EXTERNAL_RESCORING_PASSED_DESCRIPTIVE_ONLY")
        self.assertFalse(report["threshold_met"])
        self.assertEqual(report["certified_new_skills"],0)
        self.assertFalse(report["weights_updated"])

    def test_manifests_and_raw_replies_cannot_be_replaced(self):
        r=self.fixture();q,o=t.make_holdout()
        altered=copy.deepcopy(q)
        altered["questions"][0]["edges"]=[]
        self.assertEqual(a.audit(r,altered,o)["reason"],"FROZEN_MANIFEST_CONTENT_MISMATCH")
        altered=copy.deepcopy(r)
        altered["evaluation"][0]["arms"]["D"]["raw"]='{"abstain":true}'
        self.assertEqual(a.audit(altered,q,o)["reason"],"RAW_GENERATION_TAMPERED")

    def test_training_feedback_and_note_must_match_exact_source(self):
        r=self.fixture();q,o=t.make_holdout()
        altered=copy.deepcopy(r)
        altered["training"]["T"]["traces"][0]["feedback"]="A plausible rule."
        self.assertEqual(a.audit(altered,q,o)["reason"],"TRAINING_FEEDBACK_TAMPERED")
        altered=copy.deepcopy(r)
        altered["training"]["T"]["note"]["output"]["raw"]='{"rule":"fake"}'
        self.assertEqual(a.audit(altered,q,o)["reason"],"TRANSFER_NOTE_TAMPERED")

    def test_forged_success_and_metrics_are_blocked(self):
        r=self.fixture();q,o=t.make_holdout()
        altered=copy.deepcopy(r)
        altered["registered_gain"]=True
        self.assertEqual(a.audit(altered,q,o)["reason"],"GAIN_THRESHOLD_FALSIFIED")
        altered=copy.deepcopy(r)
        altered["metrics"]["T"]["fully_certified"]=8
        self.assertEqual(a.audit(altered,q,o)["reason"],
                         "AGGREGATE_MISMATCH_T_fully_certified")

    def test_wrong_atomic_memberships_fail_external_checker(self):
        nodes=t.TRAIN_NODES
        graph=frozenset(map(tuple,t.make_training()[0]["edges"]))
        triple=t.exact_counterexample(nodes,graph)
        base={"holds":False,"failed_axioms":["transitive"],
              "certificate":{"kind":"missing_transitive_edge","triple":triple,
                             "premises":{"xy":True,"yz":True,"xz":False}}}
        import json
        self.assertTrue(a.independently_score(json.dumps(base),nodes,graph)["fully_certified"])
        base["certificate"]["premises"]["xz"]=True
        self.assertFalse(a.independently_score(json.dumps(base),nodes,graph)["fully_certified"])


if __name__=="__main__":
    unittest.main()
