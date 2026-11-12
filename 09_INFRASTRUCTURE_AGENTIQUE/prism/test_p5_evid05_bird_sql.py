"""EVID-05 correctness, SQL safety and provenance fail-closed tests.

The tiny in-memory database is a TEST FIXTURE, not the authentic BIRD data.
Authentic BIRD checks are performed by the separate pinned-download CI stage.
"""
import json
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import p5_evid05_bird_sql as e

class RealSourceWitnessTests(unittest.TestCase):
    def setUp(self):
        self.conn=sqlite3.connect(":memory:")
        self.conn.executescript("""
          CREATE TABLE gender(id INTEGER,gender TEXT);
          CREATE TABLE colour(id INTEGER,colour TEXT);
          CREATE TABLE race(id INTEGER,race TEXT);
          CREATE TABLE publisher(id INTEGER,publisher_name TEXT);
          CREATE TABLE superhero(
             id INTEGER,superhero_name TEXT,full_name TEXT,gender_id INTEGER,
             hair_colour_id INTEGER,race_id INTEGER,publisher_id INTEGER,
             height_cm INTEGER);
          INSERT INTO gender VALUES(1,'Male'),(2,'Female');
          INSERT INTO colour VALUES(1,'Blue'),(2,'Black');
          INSERT INTO race VALUES(1,'Mutant'),(2,'Human');
          INSERT INTO publisher VALUES(1,'Other'),(2,'Marvel Comics');
          INSERT INTO superhero VALUES(10,'Blue Man','Testman',1,1,1,2,186);
          INSERT INTO superhero VALUES(11,'A Hero','Testwoman',2,2,2,2,170);
          INSERT INTO superhero VALUES(12,'Tall Human','Tall Human',1,2,2,1,185);
        """)

    def tearDown(self):
        self.conn.close()

    def test_hand_selected_exact_source_claims_are_frozen(self):
        rows=e._load_claims(e.FROZEN)
        self.assertEqual([r["claim_id"] for r in rows],list(e.CLAIM_IDS))
        self.assertTrue(all(r["db_name"]=="superhero" for r in rows))
        self.assertEqual(len({r["claim_id"] for r in rows}),5)
        self.assertEqual(rows[0]["label_evaluator_only"],"ENTAILED")
        self.assertEqual(rows[-1]["label_evaluator_only"],"NOT ENOUGH INFO")

    def test_each_two_independent_sql_formulations_agree_on_test_fixture(self):
        for claim_id in (4267,4179,4324,3930):
            x=e._exercise(self.conn,e.SQL[claim_id])
            self.assertTrue(x["two_methods_agree"],(claim_id,x))
        self.assertTrue(e._exercise(self.conn,e.SQL[4267])["method_join"])
        self.assertFalse(e._exercise(self.conn,e.SQL[4179])["method_join"])
        self.assertTrue(e._exercise(self.conn,e.SQL[3930])["method_join"])
        self.assertEqual(len(e._exercise(self.conn,e.SQL[3930])["supporting_rows_top3"]),1)
        self.assertFalse(e._exercise(self.conn,e.SQL[4324])["method_join"])
        self.assertEqual(e._exercise(self.conn,e.SQL[4324])["reported_count"],1)

    def test_publisher_source_convention_differs_from_natural_missingness(self):
        natural=e._exercise(self.conn,e.SQL[4179])
        annotation=e._exercise(self.conn,e.PUB_4179)
        self.assertFalse(natural["method_join"])
        self.assertTrue(annotation["method_join"])
        actions=e._interpret(4179,natural,annotation)
        self.assertEqual(actions["omega_provenance_gate"],
                         "ABSTAIN_SEMANTIC_CONVENTION")
        self.assertEqual(actions["two_sql_agreement"],"ENTAILED")

    def test_compound_and_counterfactual_abstain(self):
        counter=e._exercise(self.conn,e.SQL[3930])
        self.assertEqual(e._interpret(3930,counter)["omega_provenance_gate"],
                         "CONTRADICTED")
        false_counter=dict(counter,method_join=False,method_subquery=False,
                           supporting_rows_top3=[],two_methods_agree=True)
        self.assertEqual(e._interpret(3930,false_counter)["omega_provenance_gate"],
                         "ABSTAIN_UNTESTED_CAUSAL_HAIR_CLAUSE")
        self.assertEqual(e._interpret(4419,None)["omega_provenance_gate"],
                         "ABSTAIN_MISSING_OBSERVABLE_COUNTERFACTUAL")

    def test_source_fingerprint_must_precede_claim_verdict(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"superhero.sqlite"
            p.write_bytes(b"SQLite format 3\0"+"invalid".encode())
            with self.assertRaisesRegex(ValueError,"STOP_SOURCE_UNVERIFIED"):
                e.check_source(p)
        self.assertEqual(len(e.DB_SHA256),64)
        self.assertEqual(len(e.DB_GIT_BLOB),40)

    def test_no_unsafe_sql_or_label_leakage(self):
        for sql in ("SELECT 1","SELECT 1; SELECT 2","PRAGMA table_info(hero)",
                    "UPDATE superhero SET id=0","SELECT COUNT(*) FROM superhero;"):
            with self.assertRaises(ValueError):
                e._query(self.conn,sql,"bool")
        with self.assertRaises(ValueError):
            e._query(self.conn,"SELECT COUNT(*) FROM superhero","bool")
        with self.assertRaises(ValueError):
            e._query(self.conn,"SELECT NULL FROM superhero LIMIT 1","bool")
        self.assertNotIn("label_evaluator_only",str(e.SQL))
        self.assertNotIn("ClaimDB",str(e.SQL))

    def test_methods_conflict_if_simulated_requires_abstention(self):
        p=e._exercise(self.conn,e.SQL[4267])
        wrong=dict(p,method_subquery=False,two_methods_agree=False)
        result=e._interpret(4267,wrong)
        self.assertEqual(result["omega_provenance_gate"],"ABSTAIN_METHOD_CONFLICT")
        self.assertEqual(result["two_sql_agreement"],"ABSTAIN_METHOD_CONFLICT")

if __name__=="__main__":
    unittest.main()
