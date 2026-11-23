"""Check conversion of REAL-02 raw predictions; no actual LLM inference."""
import json
import unittest
from omega_hybrid_real02_bridge import score_real02


def model_response(correct):
    return json.dumps({"holds": correct,
                       "failed_axioms": [] if correct else ["reflexive"]})


def report():
    examples=[[["a","a"],["b","b"],["c","c"]],
              [["a","a"],["b","b"],["c","c"],["a","b"],["b","a"]],
              [["a","b"]], []]
    tasks=[]
    for i, edges in enumerate(examples):
        truth=i<2
        tasks.append({"id":i,"edges":edges,"oracle_holds":truth,
                      "arms": {name:{"raw":model_response(truth if name=="M" else not truth),
                                     "usage":{"prompt_tokens":101}}
                               for name in ("D","M","N")}})
    return {"stage":"EVALUATED","bounded_fidelity":
            {"target":"equivalence relation","bounded_pass":True},
            "candidate_id_reloaded":"c1","source":{"source_sha256":"a"*64},
            "memory":{"status":"COMPLETE","tasks":tasks}}


class Real02AdapterTests(unittest.TestCase):
    def test_synthetic_report_rescores_but_proves_no_competence(self):
        result=score_real02(report(),"b"*64)
        self.assertEqual(result["status"],"REAL02_RESCORING_COMPLETE_DESCRIPTIVE_ONLY")
        self.assertEqual(result["score"]["n"],4)
        self.assertEqual(result["score"]["net_gain"]["memory_vs_direct"],4)
        self.assertFalse(result["new_competence_demonstrated"])

    def test_pre_registration_digest_is_required(self):
        self.assertEqual(score_real02(report(),"")["reason"],"MISSING_FROZEN_SPLIT_ID")

    def test_wrong_oracle_report_is_rejected(self):
        r=report(); r["memory"]["tasks"][0]["oracle_holds"]=False
        self.assertEqual(score_real02(r,"b"*64)["reason"],"ORACLE_TRUTH_MISMATCH")

    def test_missing_model_tokens_blocks_comparison(self):
        r=report(); r["memory"]["tasks"][1]["arms"]["M"]["usage"]={}
        self.assertEqual(score_real02(r,"b"*64)["reason"],"RECALCULATION_BLOCKED")

    def test_no_memory_reload_blocks_score(self):
        r=report(); r.pop("candidate_id_reloaded")
        self.assertEqual(score_real02(r,"b"*64)["reason"],"NO_PERSISTED_MEMORY_RELOAD")

    def test_no_fidelity_blocks_score(self):
        r=report(); r["bounded_fidelity"]["bounded_pass"]=False
        self.assertEqual(score_real02(r,"b"*64)["reason"],"BOUNDED_FIDELITY_NOT_VALIDATED")


if __name__=="__main__":unittest.main()
