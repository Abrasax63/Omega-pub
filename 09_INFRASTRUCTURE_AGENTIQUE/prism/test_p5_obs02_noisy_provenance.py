"""P5-OBS-02 adversarial reproducibility tests (no new Qwen inference)."""
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

import p5_obs02_noisy_provenance as e

SNAPSHOT = Path(__file__).resolve().with_name("obs02_frozen_qwen96.zlib.b64")

class ObservabilityWithImperfectEvidence(unittest.TestCase):

    def test_16_microstates_priors_exact(self):
        self.assertEqual(len(e.STATES),16)
        for p in (F(1,2), F(3,5)):
            b=e.prior(p)
            self.assertEqual(sum(b),1)
            self.assertEqual(e.prob_correct(b),p)

    def test_shared_sources_must_not_be_counted_twice(self):
        b=e.prior(F(1,2))
        first,_=e.bayes_update(b,"SHARED_B",1)
        duplicate,mass=e.bayes_update(first,"SHARED_A",1)
        self.assertEqual(first,duplicate)
        self.assertEqual(mass,1)
        self.assertEqual(e.prob_correct(first),F(3,4))
        self.assertEqual(e.naive_update(F(3,4),1),F(9,10))
        with self.assertRaisesRegex(ValueError,"no joint microstate witness"):
            e.bayes_update(first,"SHARED_A",0)

    def test_unknown_is_not_a_negative_verdict(self):
        for p in (F(1,2),F(3,5)):
            b=e.prior(p)
            after,mass=e.bayes_update(b,"INDEPENDENT","?")
            self.assertEqual(mass,F(1,4))
            # Full microstate belief changes (M becomes known), but correctness
            # marginal must remain unchanged: UNKNOWN reveals nothing about C.
            self.assertEqual(e.prob_correct(after),p)
            self.assertTrue(all(s[3]==1 for s,w in zip(e.STATES,after) if w))

    def test_independent_policy_trees_versus_bellman_four_domains(self):
        values=((F(1,2),F(943,3200)),(F(3,5),F(31,100)))
        for p,val in values:
            b=e.prior(p)
            self.assertEqual(e.dp(b,e.TOOLS,2)[1],val)
            self.assertEqual(e.independent_tree_value(b,2),val)
        self.assertEqual(e.dp(e.prior(F(0)),e.TOOLS,2)[0][0],"STOP")
        self.assertEqual(e.dp(e.prior(F(1)),e.TOOLS,2)[0][0],"STOP")

    def test_zero_cost_gold_does_not_buy_redundant_second_proof(self):
        old=e.COST["GOLD"]
        try:
            e.COST["GOLD"]=F(0)
            e.dp.cache_clear()
            b=e.prior(F(1,2))
            self.assertEqual(e.dp(b,e.TOOLS,2),(("PROBE","GOLD"),F(1)))
            for _,(post,mass) in e.branches(b,"GOLD").items():
                remainder=tuple(x for x in e.TOOLS if x!="GOLD")
                self.assertEqual(e.dp(post,remainder,1)[0][0],"STOP")
        finally:
            e.COST["GOLD"]=old
            e.dp.cache_clear()

    def test_policy_does_not_query_unpaid_verifiers_or_secret(self):
        c=e.Controller("omega_provenance_candidate",F(1,2))
        with patch.object(e,"tool_output",side_effect=AssertionError("unpaid oracle accessed")):
            self.assertIn(c.choose(),e.TOOLS)
        c.observe("SHARED_B",1)
        self.assertEqual(len(c.observations),1)
        self.assertIn("support_after",c.observations[0])
        self.assertNotIn("secret",str(c.observations))
        with self.assertRaises(ValueError):
            c.observe("SHARED_B",1)
        with self.assertRaises(ValueError):
            c.observe("SHARED_A",0)
        self.assertEqual(len(c.observations),1)

    def test_stable_real_model_snapshot_and_replay(self):
        rows=e._load_public_snapshot(SNAPSHOT)
        self.assertEqual(len(rows),96)
        self.assertEqual(sum(r["split"]=="test" for r in rows),64)
        self.assertEqual(sum(r["split"]=="calibration" for r in rows),32)
        x=e.run(SNAPSHOT)
        self.assertEqual(x["new_LLM_generations"],0)
        self.assertTrue(x["instrument_faults_are_artificial"])
        self.assertTrue(x["same_source_duplicates_add_zero_information"])
        self.assertTrue(x["impossible_same_source_contradiction_refused"])
        self.assertEqual(x["calibration_priors"],{
            "MUL":"3/5","CRT":"1/2","RATE":"1/2","INJ":"1/2"})
        self.assertEqual(len(x["policies"]),8)
        for name,score in x["policies"].items():
            self.assertEqual(len(score["traces"]),64)
            self.assertEqual(score["correct_published"]+
                             score["wrong_published"]+score["abstained"],64)
            self.assertLessEqual(score["checks"],128)
            for path in score["traces"]:
                self.assertLessEqual(len(path["used_tools"]),2)
                self.assertEqual(len(set(path["used_tools"])),len(path["used_tools"]))
        a=x["policies"]["exact_bayes_dp"]
        b=x["policies"]["omega_provenance_candidate"]
        self.assertEqual(a["realized_total_net"],b["realized_total_net"])
        self.assertEqual(a["wrong_published"],b["wrong_published"])
        for left,right in zip(a["traces"],b["traces"]):
            self.assertEqual(left["used_tools"],right["used_tools"])
            self.assertEqual(left["final_decision"],right["final_decision"])

    def test_missing_or_invalid_frozen_source_fails_closed(self):
        with self.assertRaises(Exception):
            e.run(Path(__file__).with_name("file_does_not_exist_obs02.b64"))

if __name__=="__main__":
    unittest.main()
