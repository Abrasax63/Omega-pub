import itertools
import unittest
from collections import Counter
import omega_hybrid_exact_sensor as sensor
from proposal02 import allowed,decode,digest,PROMPT,N,SEED,summarize,digits_for
from corpus_gate import identities,motif

class CompactTests(unittest.TestCase):
    def test_all_possible_strings(self):
        keys=set()
        counts=Counter()
        for bits in itertools.product("01",repeat=9):
            for tr in itertools.product("012",repeat=3):
                p=decode("".join(bits+tr))
                keys.add(identities(p)[1])
                counts[motif(p)]+=1
        self.assertEqual(sum(counts.values()),13824)
        self.assertEqual(counts["110"],768)
        self.assertEqual(len(keys),2320)

    def test_reject_invalid(self):
        for raw in ("010001000012 ","010001000013","010001002012","01000100001",""):
            with self.assertRaises(ValueError):
                decode(raw)

    def test_allowed(self):
        self.assertEqual([allowed(i) for i in range(12)],["01"]*9+["012"]*3)
        for i in (-1,12):
            with self.assertRaises(ValueError):
                allowed(i)

    def test_roundtrip(self):
        class Tok:
            def encode(self,s,**kwargs): return [int(s)]
            def decode(self,ids,**kwargs): return "".join(map(str,ids))
        self.assertEqual(digits_for(Tok()),{"0":0,"1":1,"2":2})

    def rows(self):
        return [{"arm":a,"seed":SEED+i,"raw":raw,"raw_sha256":digest(raw),
                 "prompt_sha256":digest(PROMPT),"token_ids":[0]*length,"output_tokens":length,
                 "allowed_mass":[0.5]*12 if a=="G" else [],"input_tokens":100,"seconds":1.0}
                 for a,raw,length in (("F","not valid",3),("G","010001000012",12)) for i in range(N)]

    def test_syntax_not_diversity(self):
        r=summarize(self.rows(),sensor)
        self.assertEqual(r["arms"]["F"]["valid"],0)
        self.assertEqual(r["arms"]["G"]["valid"],16)
        self.assertEqual(r["arms"]["G"]["unique_tasks"],1)
        self.assertEqual(r["arms"]["G"]["motifs"]["110"],1)
        self.assertFalse(r["arms"]["G"]["exploratory_feasibility"])
        self.assertFalse(r["training_authorized"])

    def test_guard_missing_or_tampered(self):
        rows=self.rows()
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            summarize(rows[:-1],sensor)
        rows[-1]["raw"]="altered"
        with self.assertRaisesRegex(ValueError,"DIGEST"):
            summarize(rows,sensor)
