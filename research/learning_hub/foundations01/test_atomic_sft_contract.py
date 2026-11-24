import unittest
import json
import hashlib
from atomic_curriculum import create
from atomic_sft_contract import question,target,parse_bits,score_pair

class SFTContractTests(unittest.TestCase):
    def test_bits(self):
        self.assertEqual(parse_bits("1101"),dict(xy=True,yz=True,xz=False,violates=True))
        for invalid in ("1101 ","1101\n","111","10102","true"):
            self.assertIsNone(parse_bits(invalid))
    def test_paired_perfect_vs_invalid(self):
        rows=create(91,"eval")
        pred=[]
        for a in ("base","lora"):
            for v in ("edges","matrix"):
                for r in rows:
                    pred.append(dict(arm=a,view=v,id=r["id"],
                        raw=target(r["label"]) if a=="lora" else "bad",
                        input_tokens=10,output_tokens=4,seconds=0,
                        prompt_sha256=hashlib.sha256(question(r["packet"],v).encode()).hexdigest()))
        result=score_pair(rows,pred)
        self.assertEqual(result["comparisons"]["edges"]["joint_delta"],64)
        self.assertEqual(result["status"],"EXPLORATORY_SUPERVISED_GAIN")
        self.assertFalse(result["promotion_authorized"])
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            score_pair(rows,pred[:-1])
    def test_question(self):
        p={"nodes":["A","B","C"],"edges":[["A","B"]],"triple":["A","B","C"]}
        self.assertIn("four bits",question(p,"edges"))
        self.assertIn('"matrix"',question(p,"matrix"))
        self.assertNotIn('"violates":',question(p,"edges"))
