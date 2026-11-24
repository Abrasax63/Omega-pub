import unittest
from capacity01_contract import create,validate,score,question,digest,MODELS,VIEWS

class CapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=create()
    def fixture(self,constant=False):
        pins={a:{"revision":m[1]} for a,m in MODELS.items()}
        records=[]
        for a in MODELS:
            for v in VIEWS:
                for r in self.rows:
                    raw="No" if constant else ("Yes" if r["label"] else "No")
                    p=question(r["packet"],v)
                    records.append(dict(arm=a,view=v,id=r["id"],revision=pins[a]["revision"],prompt=p,prompt_sha256=digest(p),
                        raw=raw,raw_sha256=digest(raw),token_ids=[1],output_tokens=1,input_tokens=20,seconds=0,p_yes=None,p_no=None))
        return pins,records
    def test_corpus(self):
        self.assertEqual(validate(self.rows),dict(examples=32,pairs=16,distinct_graphs=32))
    def test_perfect(self):
        p,r=self.fixture()
        s=score(self.rows,r,p)
        self.assertTrue(s["scores"]["360m"]["adjacency"]["signal"])
        self.assertFalse(s["promotion_authorized"])
    def test_constant(self):
        p,r=self.fixture(True)
        s=score(self.rows,r,p)
        self.assertEqual(s["scores"]["135m"]["edges"]["strict_correct"],16)
        self.assertEqual(s["scores"]["135m"]["edges"]["pairs_both_correct"],0)
        self.assertFalse(s["scores"]["135m"]["edges"]["signal"])
    def test_missing(self):
        p,r=self.fixture()
        with self.assertRaisesRegex(ValueError,"COVERAGE"): score(self.rows,r[:-1],p)
