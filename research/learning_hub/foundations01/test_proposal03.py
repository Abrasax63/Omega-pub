import unittest
from collections import Counter
import omega_hybrid_exact_sensor as sensor
from proposal03 import desired,prompt,summarize,digest,SEED,N

class TargetedTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for i in range(N):
            seed=SEED+i
            for arm in ("N","T"):
                target=desired(seed) if arm=="T" else "000"
                raw=list("000000000")
                for idx,v in zip((1,5,2),target):
                    raw[idx]=v
                raw="".join(raw)
                rows.append(dict(arm=arm,seed=seed,raw=raw,raw_sha256=digest(raw),
                     prompt_sha256=digest(prompt(arm,seed)),token_ids=[0]*9,allowed_mass=[0.5]*9,
                     input_tokens=100,seconds=1))
        return rows
    def test_balanced_and_neutral_blind(self):
        self.assertEqual(set(Counter(desired(SEED+i) for i in range(N)).values()),{4})
        self.assertEqual(len(set(prompt("N",SEED+i) for i in range(N))),1)
        self.assertEqual(len(set(prompt("T",SEED+i) for i in range(N))),8)
    def test_perfect_target_and_constant_neutral(self):
        r=summarize(self.fixture(),sensor)
        self.assertEqual(r["arms"]["N"]["exact"],4)
        self.assertEqual(r["arms"]["T"]["exact"],32)
        self.assertEqual(r["arms"]["T"]["violations"],4)
        self.assertEqual(r["paired"],dict(both=4,N_only=0,T_only=28,neither=0))
        self.assertTrue(r["exploratory_feasibility"])
        self.assertFalse(r["training_authorized"])
    def test_constant_not_learning(self):
        rows=self.fixture()
        for r in rows:
            r["raw"]="000000000"
            r["raw_sha256"]=digest(r["raw"])
        self.assertFalse(summarize(rows,sensor)["exploratory_feasibility"])
    def test_invalid_trace(self):
        rows=self.fixture()
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            summarize(rows[:-1],sensor)
        rows[0]["raw"]="111111111"
        with self.assertRaisesRegex(ValueError,"DIGEST"):
            summarize(rows,sensor)
