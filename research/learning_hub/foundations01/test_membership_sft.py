import hashlib
import unittest
from membership_curriculum import create
from membership_sft_contract import question,target,score_pair,prefix

class MembershipSFTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows=create(56,"eval")
    def fixture(self,constant=False):
        return [dict(arm=a,view=v,id=r["id"],raw=target(r["label"]) if a=="lora" and not constant else "Yes",
                    token_ids=[1],output_tokens=1,input_tokens=20,seconds=0,p_yes=None,p_no=None,
                    prompt_sha256=hashlib.sha256(question(r["packet"],v).encode()).hexdigest())
                for a in ("base","lora") for v in ("edges","matrix") for r in self.rows]
    def test_perfect(self):
        r=score_pair(self.rows,self.fixture())
        self.assertTrue(r["comparisons"]["edges"]["signal"])
        self.assertEqual(r["scores"]["lora"]["edges"]["pairs_both_correct"],32)
        self.assertFalse(r["promotion_authorized"])
    def test_constant(self):
        r=score_pair(self.rows,self.fixture(True))
        self.assertEqual(r["scores"]["lora"]["edges"]["correct"],32)
        self.assertEqual(r["scores"]["lora"]["edges"]["pairs_both_correct"],0)
        self.assertFalse(r["comparisons"]["edges"]["signal"])
    def test_missing(self):
        with self.assertRaisesRegex(ValueError,"COVERAGE"): score_pair(self.rows,self.fixture()[:-1])
    def test_prefix(self):
        self.assertEqual(prefix("yes, because"),"Yes")
        self.assertIsNone(prefix("Nobody"))
