"""No-LLM tests for ATOM-08 independent artifact auditing."""
import copy
import tempfile
from pathlib import Path
import unittest

import omega_hybrid_atom08 as atom
import omega_hybrid_atom08_audit as audit

class FakeClient:
    def __call__(self,messages,max_tokens):
        s=messages[-1]["content"]
        output=('{"violates":false}' if "Given ONLY these three verified" in s else
                '{"xy":false,"yz":false,"xz":false}')
        return {"text":output,"usage":{"prompt_tokens":len(s.split())+10,
                "completion_tokens":10},"time_s":0.04}

class IndependentAtomicAuditorTests(unittest.TestCase):
    def fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            return atom.run(Path(tmp),"offline",client=FakeClient())

    def test_can_recompute_incomplete_model_with_no_false_certification(self):
        report=self.fixture()
        q,a=atom.make_manifest()
        r=audit.audit(report,q,a)
        self.assertEqual(r["status"],"EXTERNAL_ATOM08_AUDIT_PASSED")
        self.assertFalse(r["logic_gate"])
        self.assertFalse(r["reading_gate"])
        self.assertEqual(r["metrics"]["LOGIC"]["correct"],7)
        self.assertEqual(r["reported_new_model_skills"],0)

    def test_forged_truth_or_prompt_rejected(self):
        report=self.fixture();q,a=atom.make_manifest()
        fake=copy.deepcopy(q);fake["graphs"][0]["edges"]=[]
        self.assertEqual(audit.audit(report,fake,a)["reason"],"MANIFEST_CHANGED")
        fake=copy.deepcopy(report)
        fake["graph_trials"][0]["arms"]["LIST"]["prompt_sha256"]="0"*64
        self.assertEqual(audit.audit(fake,q,a)["reason"],"MODEL_PROMPT_MODIFIED")

    def test_forged_raw_score_is_rejected(self):
        report=self.fixture();q,a=atom.make_manifest()
        fake=copy.deepcopy(report)
        fake["graph_trials"][0]["arms"]["MATRIX"]["raw"]='{"xy":true,"yz":true,"xz":true}'
        self.assertEqual(audit.audit(fake,q,a)["reason"],"RAW_REPLY_MODIFIED")
        fake=copy.deepcopy(report)
        fake["metrics"]["LOGIC"]["correct"]=8
        self.assertEqual(audit.audit(fake,q,a)["reason"],"AGGREGATE_CORRUPTED_LOGIC_correct")

    def test_boolean_truth_table_forgery_rejected(self):
        report=self.fixture();q,a=atom.make_manifest()
        fake=copy.deepcopy(report)
        fake["logic_trials"][0]["output"]["score"]["correct"]=True
        if report["logic_trials"][0]["output"]["score"]["correct"]:
            fake["logic_trials"][0]["output"]["score"]["correct"]=False
        self.assertEqual(audit.audit(fake,q,a)["reason"],"LOGIC_SCORE_TAMPERED")

if __name__=="__main__":
    unittest.main()
