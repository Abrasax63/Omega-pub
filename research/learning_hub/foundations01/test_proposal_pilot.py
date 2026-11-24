import json
import unittest
import omega_hybrid_exact_sensor as sensor
from proposal_pilot import N, SEED, PROMPT, digest, summarize

def record(raw,i):
    return {"seed":SEED+i,"raw":raw,"raw_sha256":digest(raw),
            "prompt_sha256":digest(PROMPT),"input_tokens":50,
            "output_tokens":1,"output_token_ids":[1]}

class ProposalPilotTests(unittest.TestCase):
    def setUp(self):
        p={"nodes":["a","b","c"],"edges":[["a","b"],["b","c"]],"triple":["a","b","c"]}
        self.rows=[record(json.dumps(p),i) for i in range(N)]

    def test_repeated_valid_tasks_fail_diversity(self):
        r=summarize(self.rows,sensor)
        self.assertEqual(r["accepted_unique"],1)
        self.assertEqual(r["motifs"]["110"],1)
        self.assertEqual(r["rejection_counts"]["DUPLICATE_ISOMORPHIC_TASK"],31)
        self.assertEqual(r["status"],"PROPOSAL_FEASIBILITY_NOT_DEMONSTRATED")
        self.assertFalse(r["training_authorized"])

    def test_invalid_outputs_counted(self):
        rows=[record("not JSON",i) for i in range(N)]
        r=summarize(rows,sensor)
        self.assertEqual(r["accepted_unique"],0)
        self.assertEqual(sum(r["rejection_counts"].values()),N)

    def test_missing_attempt_rejected(self):
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            summarize(self.rows[:-1],sensor)

    def test_modified_raw_rejected(self):
        self.rows[0]["raw"]="changed"
        with self.assertRaisesRegex(ValueError,"DIGEST"):
            summarize(self.rows,sensor)

    def test_excess_tokens_rejected(self):
        self.rows[0]["output_token_ids"]=list(range(193))
        self.rows[0]["output_tokens"]=193
        with self.assertRaisesRegex(ValueError,"TOKEN"):
            summarize(self.rows,sensor)
