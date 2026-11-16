"""Regressions for precommitted controlled provenance intervention."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from attested_operations_benchmark import predict_case, score_predictions

COPY="evidence/case-a-copy.json"
HIDDEN="evidence/case-d-hidden.json"

class ReplayedOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home/"evidence").mkdir()
        self.artifact=self.home/COPY
        self.artifact.write_bytes(b"101\n")
        self.digest=hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.bundle=self.home/"bundle.json"
        self.bundle.write_text("not an actual signature")
        self.root=self.home/"trust.json"
        self.root.write_text("not an actual trusted root")

    def predict(self, log, output=COPY, *, signed=True):
        def mock(*args):
            return {"status":"VERIFIED_BUILD_PROVENANCE_ONLY" if signed else "INDETERMINATE",
                    "signature_verified":signed,
                    "artifact_sha256":self.digest}
        return predict_case(log, self.artifact, output, bundle=self.bundle,
                             trusted_root=self.root, repository="Abrasax63/Omega-pub",
                             repository_id=1309584710,
                             signer_workflow="Abrasax63/Omega-pub/.github/workflows/test.yml",
                             source_commit="a"*40, verifier=mock)

    def test_copy_with_signed_bytes_still_not_science(self):
        log="+ cp seed-a evidence/case-a-copy.json\n"+self.digest+"  "+COPY+"\n"
        result=self.predict(log)
        self.assertEqual(result["baseline_label"],"copie")
        self.assertEqual(result["candidate_label"],"copie")
        self.assertEqual(result["build_provenance"],"VERIFIED_BUILD_ONLY")
        self.assertEqual(result["scientific_verdict"],"INDETERMINATE")
        self.assertTrue(result["hash_matches_raw_log"])

    def test_missing_trace_abstains_even_with_valid_signature(self):
        log=self.digest+"  "+COPY+"\n"
        result=self.predict(log)
        self.assertEqual(result["baseline_label"],"indéterminé")
        self.assertEqual(result["candidate_label"],"indéterminé")
        self.assertEqual(result["build_provenance"],"VERIFIED_BUILD_ONLY")
        self.assertEqual(result["routing"],"LINK_LOG_OUTPUT_TO_SIGNED_BYTES")

    def test_bad_signature_no_cryptographic_upgrade(self):
        result=self.predict("+ cp seed-a evidence/case-a-copy.json\n"
                            +self.digest+"  "+COPY+"\n", signed=False)
        self.assertEqual(result["baseline_label"],"copie")
        self.assertEqual(result["build_provenance"],"INDETERMINATE")
        self.assertEqual(result["scientific_verdict"],"INDETERMINATE")

    def test_unmatched_digest_has_no_cross_evidence_agreement(self):
        result=self.predict("+ cp seed-a evidence/case-a-copy.json\n"
                            +"0"*64+"  "+COPY+"\n")
        self.assertFalse(result["hash_matches_raw_log"])
        self.assertEqual(result["routing"],"LINK_LOG_OUTPUT_TO_SIGNED_BYTES")

    def test_fixed_manifest_evaluated_after_prediction(self):
        manifest={"version":1,"cases":[
            {"id":"A","file":"a","expected":"copie"},
            {"id":"B","file":"b","expected":"recalcul"},
            {"id":"C","file":"c","expected":"copie"},
            {"id":"D","file":"d","expected":"copie"}]}
        predictions=[]
        for file,label in [("a","copie"),("b","recalcul"),
                           ("c","copie"),("d","indéterminé")]:
            predictions.append({
                "output":file,"baseline_label":label,"candidate_label":label,
                "baseline_log_reads":1,"candidate_log_reads":1,
                "candidate_signature_checks":1,
                "build_provenance":"VERIFIED_BUILD_ONLY",
                "scientific_verdict":"INDETERMINATE",
                "hash_matches_raw_log":True,
            })
        s=score_predictions(predictions,manifest)
        self.assertEqual((s["baseline_correct"],s["candidate_correct"]),(3,3))
        self.assertEqual((s["baseline_abstentions"],s["candidate_abstentions"]),(1,1))
        self.assertEqual(s["selection_accuracy_gain"],0)
        self.assertFalse(s["scientific_gain_demonstrated"])
        self.assertEqual(s["scientific_certifications"],0)
        with self.assertRaises(ValueError):
            score_predictions(predictions[:-1],manifest)


if __name__=="__main__":
    unittest.main()
