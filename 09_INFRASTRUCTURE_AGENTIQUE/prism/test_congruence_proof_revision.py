"""CONG-001: adversarial congruence, proof revocation and no explosion.

Baseline ATMS enumerates models; Omega experiment uses generalized CRT.
Every active certificate is independently checked over all 60 residues.
"""
from copy import deepcopy
from itertools import combinations
from math import gcd
import json
import unittest

from congruence_proof_revision import (
    ProofLabels,PATH,crt,symbolic_kind,finite_kind,models,
    independently_verify_proof,validate_scenario,check,replay
)


class CongruenceRevisionTests(unittest.TestCase):
    def test_pairwise_crt_and_refutation_with_unknown_distinguished(self):
        even={"r":0,"m":2}
        odd={"r":1,"m":2}
        self.assertIsNone(crt([even,odd]))
        self.assertEqual(symbolic_kind([even,odd],even),
                         "inconsistent_environment")
        self.assertEqual(symbolic_kind([even],odd),"refuted")
        self.assertEqual(symbolic_kind([even],{"r":0,"m":4}),
                         "undetermined")
        self.assertEqual(symbolic_kind([{"r":8,"m":12}],{"r":2,"m":3}),
                         "entailed")

    def test_generalized_crt_matches_finite_semantics_on_small_catalog(self):
        pool=[{"r":r,"m":m} for m in (2,3,4,5,6,10,12)
              for r in range(min(m,3))]
        queries=[{"r":r,"m":m} for m in (2,3,4,5,6,10,12)
                 for r in range(min(m,2))]
        for size in (0,1,2):
            source=((),) if size==0 else combinations(pool,size)
            for subset in source:
                for q in queries:
                    self.assertEqual(symbolic_kind(subset,q),
                                     finite_kind(subset,q),
                                     (subset,q))

    def test_multiple_proofs_survive_one_retraction(self):
        data=json.loads(PATH.read_text(encoding="utf-8"))
        s=data["scenarios"][0]
        engine=ProofLabels(s["premises"],s["queries"],"symbolic")
        first=engine.evaluate(0,{"A","B"})
        self.assertEqual(first["q1"]["status"],"entailed")
        self.assertIn(["A"],first["q1"]["proofs"])
        self.assertIn(["B"],first["q1"]["proofs"])
        second=engine.evaluate(1,{"B"})
        self.assertEqual(second["q1"]["status"],"entailed")
        self.assertIn(["B"],second["q1"]["proofs"])
        self.assertNotIn(["A"],second["q1"]["proofs"])
        self.assertEqual(engine.history[0]["results"]["q1"]["status"],"entailed")
        self.assertEqual(engine.evaluate(2,set())["q1"]["status"],"undetermined")

    def test_contradiction_no_logical_explosion_and_recover(self):
        premises={"E":{"r":0,"m":2},"O":{"r":1,"m":2}}
        qs={"e":{"r":0,"m":2},"o":{"r":1,"m":2},
            "unrelated":{"r":4,"m":5}}
        engine=ProofLabels(premises,qs,"symbolic")
        contradiction=engine.evaluate(0,{"E","O"})
        for v in contradiction.values():
            self.assertEqual(v["status"],"inconsistent_environment")
            self.assertEqual(v["proofs"],[])
            self.assertEqual(v["conflicts"],[["E","O"]])
        restored=engine.evaluate(1,{"E"})
        self.assertEqual(restored["e"]["status"],"entailed")
        self.assertEqual(restored["o"]["status"],"refuted")
        self.assertEqual(restored["unrelated"]["status"],"undetermined")

    def test_forged_and_stale_certificates_rejected_independently(self):
        premises={"a":{"r":0,"m":2},"b":{"r":1,"m":2}}
        q={"r":0,"m":2}
        self.assertTrue(independently_verify_proof(premises,q,{"a"},
                                                 "entailed",["a"]))
        self.assertFalse(independently_verify_proof(premises,q,{"b"},
                                                  "entailed",["b"]))
        self.assertFalse(independently_verify_proof(premises,q,set(),
                                                  "entailed",["a"]))
        self.assertFalse(independently_verify_proof(premises,q,{"a","b"},
                                                  "entailed",["a"]))
        self.assertFalse(independently_verify_proof(premises,q,{"a"},
                                                  "entailed",["unknown"]))
        self.assertFalse(independently_verify_proof(premises,q,{"a"},
                                                  "entailed",["a","a"]))

    def test_bad_events_and_moduli_rejected(self):
        bad=[{"r":0,"m":0},{"r":1,"m":7},{"r":2,"m":2},
             {"r":True,"m":2},{"r":0,"m":False}]
        for item in bad:
            with self.subTest(item=item),self.assertRaises(ValueError):
                check(item)
        original=json.loads(PATH.read_text(encoding="utf-8"))["scenarios"][0]
        s=deepcopy(original)
        s["events"].append({"op":"activate","id":"NEVER_DEFINED"})
        with self.assertRaises(ValueError):validate_scenario(s)
        s=deepcopy(original)
        s["events"].insert(0,{"op":"activate","id":"A"})
        with self.assertRaises(ValueError):validate_scenario(s)

    def test_supports_order_invariant(self):
        s=json.loads(PATH.read_text(encoding="utf-8"))["scenarios"][2]
        a=ProofLabels(s["premises"],s["queries"],"symbolic")
        b=ProofLabels(dict(reversed(list(s["premises"].items()))),
                      s["queries"],"symbolic")
        self.assertEqual(a.labels,b.labels)

    def test_all_frozen_revisions_including_heldout(self):
        z=replay()
        self.assertEqual(z["scenario_count"],4)
        self.assertEqual(z["states"],50)
        self.assertEqual(sum(x["status"]=="PUBLIC_CONSTRUCTED_MODULAR_PROOF_MAINTENANCE"
                             for x in [z]),1)
        self.assertTrue(z["ATMS_symbolic_omega_paired_identical"])
        self.assertTrue(z["independent_60_residue_oracle_validated"])
        self.assertEqual(z["model_calls"],0)
        for event in z["results"]:
            self.assertEqual(event["omega"],event["baseline"])
            self.assertTrue(all(event["truth"][q]==r["status"]
                                for q,r in event["omega"].items()))
        self.assertEqual(sum(v["judgments"] for v in z["summaries"].values()),
                         len(z["results"][:24])*5+len(z["results"][24:])*6)
        print("CONG001_CI_SUMMARY "+json.dumps({
            "summaries":z["summaries"],"states":z["states"],
            "matched_atms_baseline":True,
        },ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    unittest.main()
