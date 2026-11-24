import unittest
from atomic_curriculum import create
from atomic_sft_audit import summarize,truth

class SupplementalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=create(231,"eval")
    def predictions(self):
        return [dict(arm=a,view=v,id=r["id"],raw=truth(r["packet"]) if a=="lora" else "1101",
                     token_ids=[0]*4,output_tokens=4)
                for a in ("base","lora") for v in ("edges","matrix") for r in self.rows]
    def test_constant_vs_perfect(self):
        r=summarize(self.rows,self.predictions())
        self.assertEqual(r["scores"]["base"]["edges"]["groups"]["all"]["joint"],32)
        self.assertEqual(r["scores"]["base"]["edges"]["macro_motif_joint"],0.125)
        self.assertEqual(r["scores"]["lora"]["same_graph_correct_both_views"],64)
        self.assertTrue(r["preregistered_signal"])
        self.assertFalse(r["promotion_authorized"])
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,"PREDICTION_COVERAGE"):
            summarize(self.rows,self.predictions()[:-1])
    def test_all_constant(self):
        p=self.predictions()
        for r in p:r["raw"]="1101"
        self.assertFalse(summarize(self.rows,p)["preregistered_signal"])
