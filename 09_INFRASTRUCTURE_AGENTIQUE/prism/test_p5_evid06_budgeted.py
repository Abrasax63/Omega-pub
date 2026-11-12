"""P5-EVID-06: no-leak routing and BIRD SQL sentinel regressions.

Synthetic records below are TEST FIXTURES; the workflow uses original LFS
model traces and the actual pinned BIRD SQLite source for primary results.
"""
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import p5_evid06_budgeted_routing as b
import p5_evid06_bird_extra_sql as sql


class RealHistoricalPairRoutingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ids=list(range(1001,1113))+list(b.SENTINELS)
        assert len(ids)==120 and len(set(ids))==120
        cls.maps={kind:{} for kind in ("gold","plain","sql")}
        for i,key in enumerate(ids):
            claim=(
                f"If something were different, it would change for case {key}."
                if i%5==0 else
                f"There are exactly {key%15} heroes in the database."
                if i%5==1 else
                "The most appealing character is popular among readers."
                if i%5==2 else
                "This database has a superhero with blue hair."
            )
            gold=b.LABELS[i%3]
            cls.maps["gold"][key]={
                "claim_id":key,"db_name":"superhero","claim":claim,
                "extra_info":"", "label":gold,
            }
            cls.maps["plain"][key]={"claim_id":key,"verdict":b.LABELS[(i+1)%3]}
            cls.maps["sql"][key]={
                "claim_id":key,"verdict":gold if i%3 else b.LABELS[(i+1)%3],
                "to_input_list":[{"type":"function_call"},
                    {"type":"function_call_output"}] if i%7 else [],
            }
        cls.cal,cls.test,cls.digest=b.prepare(cls.maps)
        cls.prior=b.calibration_model(cls.cal)

    def test_precommitted_hash_split_without_gold(self):
        self.assertEqual(len(self.cal),24)
        self.assertEqual(len(self.test),64)
        self.assertEqual(len(self.digest),64)
        self.assertFalse(set(r["claim_id"] for r in self.cal)&
                         set(r["claim_id"] for r in self.test))
        self.assertEqual({r["db_name"] for r in self.test},{"superhero"})
        self.assertEqual(b.prepare(self.maps)[2],self.digest)

    def test_hidden_sql_result_and_annotation_never_reach_selector(self):
        views=[b.public(r) for r in self.test[:8]]
        self.assertEqual(set(views[0]),{
            "claim_id","claim","extra_info","db_name","no_tools","context","cost"})
        for n in b.DEPLOYABLE:
            c=b.Policy(n,self.prior)
            choices=c.choose(0,views)
            self.assertLessEqual(len(choices),2)
            self.assertEqual(len(choices),len(set(choices)))
            self.assertTrue(all(0<=i<8 for i in choices))
        with self.assertRaises(ValueError):
            b.Policy("context_voi",self.prior).choose(
                0,[dict(v,evaluator_only_label="ENTAILED") for v in views])
        with self.assertRaises(ValueError):
            b.Policy("context_trace_gate",self.prior).choose(
                0,[dict(v,with_sql="CONTRADICTED") for v in views])

    def test_same_information_classical_trace_gate_equals_omega(self):
        _,scores,diag=b.evaluate(self.cal,self.test)
        self.assertEqual(set(scores),set(b.POLICIES))
        self.assertEqual(diag["omega_minus_classical_trace_gate"],0)
        self.assertEqual(diag["omega_vs_classical_action_differences"],0)
        self.assertEqual(scores["context_trace_gate"]["events"],
                         scores["omega_observability_candidate"]["events"])
        for n,r in scores.items():
            self.assertLessEqual(r["routed"],16)
            self.assertEqual(r["correct_published"]+
                r["wrong_published"]+r["abstentions"],64)
            self.assertEqual(len(r["events"]),64)
            self.assertTrue(all(len([e for e in r["events"]
                    if e["round"]==t and e["route"]])<=2 for t in range(8)))
        self.assertEqual(scores["no_purchase"]["routed"],0)
        self.assertEqual(scores["position_first_two"]["routed"],16)
        self.assertEqual(scores["hash_random_two"]["routed"],16)

    def test_purchased_mode_is_a_logged_model_output_not_truth(self):
        r=next(x for x in self.test if x["evaluator_only_tool_trace"]["outputs"]>0)
        p=b.paid_result(r)
        self.assertEqual(p["provider"],"claimdb/claimdb")
        self.assertNotIn("evaluator_only_label",p)
        self.assertNotIn("gold",p)
        self.assertEqual(p["with_sql"],r["with_sql"])
        # A logged function call does not establish a correct SQL proof.
        self.assertIn("same-model-family",p["provenance"])

    def test_no_supervised_learning_from_unpaid_outcomes(self):
        p=b.Policy("omega_observability_candidate",self.prior)
        views=[b.public(r) for r in self.test[:8]]
        with patch.object(b,"gain",side_effect=AssertionError("oracle leaked")):
            p.choose(0,views)
            p.finish(views[0],paid=None)

    def test_context_features_are_syntactic_not_gold(self):
        self.assertEqual(b._context("If all team matches were changed, what would happen?"),"hypothetical")
        self.assertEqual(b._context("This is widely regarded as an ideal league."),"subjective")
        self.assertEqual(b._context("Exactly 17 male superheroes."),"numeric")
        self.assertEqual(b._context("The hero has green eyes."),"other")


class ActualBirdSentinelQueryShapes(unittest.TestCase):
    def setUp(self):
        self.con=sqlite3.connect(":memory:")
        self.con.executescript("""
        CREATE TABLE superhero(id INTEGER,superhero_name TEXT,height_cm INTEGER);
        CREATE TABLE attribute(id INTEGER,attribute_name TEXT);
        CREATE TABLE hero_attribute(hero_id INTEGER,attribute_id INTEGER,attribute_value INTEGER);
        CREATE TABLE superpower(id INTEGER,power_name TEXT);
        CREATE TABLE hero_power(hero_id INTEGER,power_id INTEGER);
        INSERT INTO superhero VALUES(1,'A',210),(2,'B',185),(3,'C',190);
        INSERT INTO attribute VALUES(1,'Speed');
        INSERT INTO hero_attribute VALUES(1,1,50),(2,1,99),(3,1,99);
        INSERT INTO superpower VALUES(1,'Super Strength'),(2,'Invisibility');
        INSERT INTO hero_power VALUES(1,1),(2,1),(2,2),(3,2);
        """)

    def tearDown(self):
        self.con.close()

    def test_all_three_new_queries_are_paired_and_consistent_on_fixture(self):
        for claim_id in sql.SENTINELS:
            entry=sql.SQL[claim_id]
            left=sql._value(self.con,entry["sql_a"])
            right=sql._value(self.con,entry["sql_b"])
            self.assertEqual(left,right,claim_id)
        self.assertFalse(sql._value(self.con,sql.SQL[15601]["sql_a"]))
        self.assertEqual(sql._value(self.con,sql.SQL[15601]["count"],"count"),2)
        self.assertFalse(sql._value(self.con,sql.SQL[3730]["sql_a"]))
        self.assertEqual(sql._value(self.con,sql.SQL[3730]["count"],"count"),1)
        self.assertFalse(sql._value(self.con,sql.SQL[3971]["sql_a"]))

    def test_original_bird_source_hash_is_enforced(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"superhero.sqlite"
            p.write_bytes(b"not the source")
            from p5_evid05_bird_sql import check_source
            with self.assertRaisesRegex(ValueError,"STOP_SOURCE_UNVERIFIED"):
                check_source(p)

    def test_known_source_ids_excluded_from_policy_selection(self):
        self.assertEqual(set(sql.SENTINELS),{15601,3730,3971})
        self.assertTrue(set(sql.SENTINELS)<=set(b.SENTINELS))
        for x in sql.SQL.values():
            self.assertFalse("label_evaluator_only" in str(x))
            self.assertTrue(x["semantics"])
            self.assertNotEqual(x["sql_a"],x["sql_b"])


if __name__=="__main__":
    unittest.main()
