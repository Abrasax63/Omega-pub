"""Synthetic consistency witnesses; not real model output."""
import copy
import json
import unittest
import omega_hybrid_exact_sensor as sensor
from proposal_pilot import summarize, PROMPT, SEED, MODEL, REV, digest
from proposal_audit import audit
from hashlib import sha256

class IndependentAuditTests(unittest.TestCase):
    def fixture(self):
        raw=json.dumps({"nodes":["a","b","c"],"edges":[["a","b"],["b","c"]],"triple":["a","b","c"]})
        rows=[{"seed":SEED+i,"raw":raw,"raw_sha256":digest(raw),"prompt_sha256":digest(PROMPT),
               "input_tokens":50,"output_tokens":1,"output_token_ids":[1]} for i in range(32)]
        data=("".join(json.dumps(r)+"\n" for r in rows)).encode()
        report=summarize(rows,sensor)
        report.update(model=MODEL,revision=REV,attempts=32,raw_file_sha256=sha256(data).hexdigest())
        return data,report

    def test_consistent_negative(self):
        raw,r=self.fixture()
        result=audit(raw,r)
        self.assertEqual(result["accepted"],1)
        self.assertFalse(result["training_authorized"])

    def test_tampered_raw(self):
        raw,r=self.fixture()
        with self.assertRaisesRegex(ValueError,"RAW_FILE_DIGEST"):
            audit(raw+b" ",r)

    def test_fake_target(self):
        raw,r=self.fixture()
        r["accepted"][0]["target"]='{"xy":true,"yz":true,"xz":true,"violates":false}'
        with self.assertRaisesRegex(ValueError,"TARGET"):
            audit(raw,r)

    def test_fake_gain(self):
        raw,r=self.fixture()
        r["status"]="EXPLORATORY_PROPOSAL_FEASIBILITY_SIGNAL"
        with self.assertRaisesRegex(ValueError,"VERDICT"):
            audit(raw,r)

    def test_misreported_admission(self):
        raw,r=self.fixture()
        r["accepted"].append(copy.deepcopy(r["accepted"][0]))
        with self.assertRaisesRegex(ValueError,"ACCEPTED_INDEX"):
            audit(raw,r)
