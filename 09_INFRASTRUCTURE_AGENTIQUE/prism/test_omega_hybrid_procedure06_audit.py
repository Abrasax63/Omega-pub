"""Offline evidence audit checks; never count mock responses as experiments."""
import copy
import tempfile
from pathlib import Path
import unittest

import omega_hybrid_procedure06 as m
import omega_hybrid_procedure06_audit as audit


class FakeClient:
    def __call__(self,messages,limit):
        txt=messages[-1]["content"]
        is_proc="Apply a mechanical certificate" in txt
        raw=('{"holds":true,"failed_axioms":[],"certificate":{"kind":"partition","blocks":[["v0"],["v1"],["v2"],["v3"],["v4"]]}}'
             if is_proc else '{"holds":true,"failed_axioms":[]}')
        return {"text":raw,"usage":{"prompt_tokens":len(
            (m.SYSTEM+"\n"+txt).split()),"completion_tokens":25},
            "time_s":0.01}


class AuditTests(unittest.TestCase):
    def get_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            return m.run(Path(tmp),"offline",client=FakeClient(),
                         token_counter=lambda s:len(s.split()))

    def test_complete_frozen_fake_run_recalculated(self):
        r=self.get_report()
        q,a=m.make_manifest()
        result=audit.audit(r,q,a)
        self.assertEqual(result["status"],"AUDIT_PASSED_DESCRIPTIVE_ONLY")
        self.assertEqual(result["case_count"],8)
        self.assertFalse(result["new_scientific_skill_certified"])
        self.assertFalse(result["pointwise_gain_condition"])

    def test_tampered_oracle_or_input_is_blocked(self):
        r=self.get_report()
        q,a=m.make_manifest()
        q2=copy.deepcopy(q)
        q2["questions"][0]["edges"]=[]
        self.assertEqual(audit.audit(r,q2,a)["reason"],"FROZEN_MANIFEST_CHANGED")
        a2=copy.deepcopy(a)
        a2["answers"][0]["holds"]=not a2["answers"][0]["holds"]
        self.assertEqual(audit.audit(r,q,a2)["reason"],"FROZEN_MANIFEST_CHANGED")

    def test_tampered_raw_or_score_is_blocked(self):
        r=self.get_report()
        q,a=m.make_manifest()
        x=copy.deepcopy(r)
        x["trials"][0]["arms"]["D"]["raw"]="{}"
        self.assertEqual(audit.audit(x,q,a)["reason"],"RAW_REPLY_DIGEST_TAMPERED")
        x=copy.deepcopy(r)
        x["trials"][0]["arms"]["D"]["verdict"]["full_axioms_correct"]=True
        if r["trials"][0]["arms"]["D"]["verdict"]["full_axioms_correct"]:
            x["trials"][0]["arms"]["D"]["verdict"]["full_axioms_correct"]=False
        self.assertEqual(audit.audit(x,q,a)["reason"],"SCORE_RECOMPUTATION_MISMATCH")

    def test_tampered_aggregate_blocked(self):
        r=self.get_report()
        q,a=m.make_manifest()
        x=copy.deepcopy(r)
        x["metrics"]["P"]["certificate_valid"]=8
        self.assertEqual(audit.audit(x,q,a)["reason"],
                         "AGGREGATE_TAMPERED_P_certificate_valid")


if __name__=="__main__":
    unittest.main()
