import unittest
from collections import Counter
from elements01 import tasks,summarize,digest

class ElementsTests(unittest.TestCase):
    def rows(self,value=None):
        return [dict(arm=a,id=r["id"],raw=str(r["truth"] if value is None else value),
            raw_sha256=digest(str(r["truth"] if value is None else value)),
            prompt_sha256=digest(r["prompt"]),token_ids=[0],allowed_mass=0.4)
            for a in ("free","binary") for r in tasks()]
    def test_tasks(self):
        t=tasks()
        self.assertEqual(len(t),40)
        self.assertEqual(Counter(r["truth"] for r in t if r["kind"]=="membership"),{0:16,1:16})
        self.assertEqual(Counter(r["truth"] for r in t if r["kind"]=="logic"),{0:7,1:1})
        self.assertEqual(t,tasks())
    def test_perfect(self):
        s=summarize(tasks(),self.rows())
        for a in s["arms"].values():
            self.assertTrue(a["membership"]["signal"])
            self.assertTrue(a["logic"]["signal"])
    def test_constant(self):
        s=summarize(tasks(),self.rows(0))
        self.assertEqual(s["arms"]["binary"]["membership"]["correct"],16)
        self.assertEqual(s["arms"]["binary"]["logic"]["correct"],7)
        self.assertFalse(s["arms"]["binary"]["logic"]["signal"])
        self.assertFalse(s["arms"]["binary"]["membership"]["signal"])
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,"COVERAGE"):
            summarize(tasks(),self.rows()[:-1])
