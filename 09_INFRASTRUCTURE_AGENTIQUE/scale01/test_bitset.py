"""Bitset witness equivalence: all initial states, not just acceptance."""
import sys
from pathlib import Path
from itertools import product
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/"02_MATHEMATIQUES"/"defauts_recollement"/"sources"))
from delta_gluing_audit import words
from delta_gluing_crosscheck import matrix_accepts
from bitset_witness_cache import ExactBitsetWitnessCache
from witness_cache import WitnessCache,NaiveExact,trace


class ExactBitsetTests(unittest.TestCase):
    def test_ghost_110_no_macro_shortcut(self):
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        c=ExactBitsetWitnessCache()
        result=c.check(T,pi,w)
        self.assertFalse(result.admissible)
        self.assertEqual(result.first_empty_length,3)
        self.assertEqual(c.all_initial_witnesses(T,pi,w),())
    def test_deep_0001_obstruction(self):
        T=(0,3,1,3);pi=(0,0,0,1)
        c=ExactBitsetWitnessCache()
        self.assertTrue(c.check(T,pi,(0,0,0)).admissible)
        self.assertTrue(c.check(T,pi,(0,0,1)).admissible)
        self.assertEqual(c.check(T,pi,(0,0,0,1)).first_empty_length,4)
    def test_same_Q_different_W3(self):
        A=(0,0,2,2);api=(0,1,1,0)
        B=(1,0,0,1);bpi=(0,1,0,1)
        c=ExactBitsetWitnessCache()
        self.assertFalse(c.check(A,api,(0,0,1)).admissible)
        self.assertTrue(c.check(B,bpi,(0,0,1)).admissible)
        self.assertEqual(c.all_initial_witnesses(B,bpi,(0,0,1)),(0,))
    def test_full_multiplicity_and_empty_word(self):
        T=(0,0,0,0);pi=(0,0,0,0)
        c=ExactBitsetWitnessCache()
        self.assertEqual(c.all_initial_witnesses(T,pi,()),(0,1,2,3))
        r=c.check(T,pi,(0,0,0,0))
        self.assertEqual(r.survivor_count,4)
        self.assertEqual(c.all_initial_witnesses(T,pi,(0,0,0,0)),(0,1,2,3))
    def test_repeated_cache_hit(self):
        c=ExactBitsetWitnessCache()
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        c.check(T,pi,w)
        count=c.bitset_intersections
        c.check(T,pi,w)
        self.assertEqual(c.bitset_intersections,count)
        self.assertGreater(c.cache_hits,0)
    def test_evict_then_recalculate_exactly(self):
        c=ExactBitsetWitnessCache(max_systems=1,max_prefixes=2)
        A=((0,0,2),(0,1,1))
        B=((0,3,1,3),(0,0,0,1))
        c.check(*A,(1,1,0))
        c.check(*B,(0,0,1))
        result=c.check(*A,(1,1,0))
        self.assertEqual(result.first_empty_length,3)
        self.assertGreater(c.system_evictions,0)
        self.assertLessEqual(len(c.prefixes),2)
    def test_invalid_inputs_rejected(self):
        c=ExactBitsetWitnessCache(max_states=3,max_word_length=3)
        with self.assertRaises(ValueError):c.check((0,0,0,0),(0,0,0,0),(0,))
        with self.assertRaises(ValueError):c.check((0,0,2),(0,1,1),(0,0,0,0))
        with self.assertRaises(ValueError):c.check((0,0,5),(0,1,1),(0,))
        with self.assertRaises(TypeError):c.check([0,0,2],(0,1,1),(0,))
    def test_268336_exhaustive_cross_oracles(self):
        cache=ExactBitsetWitnessCache(max_systems=8,max_prefixes=2048)
        pairs=WitnessCache(max_entries=2048)
        checked=0
        for n in (2,3,4):
            for T in product(range(n),repeat=n):
                for pi in product(range(2),repeat=n):
                    # Include non-surjective observation colourings.
                    expected_words={l:words(T,pi,l) for l in range(1,6)}
                    for length in range(1,6):
                        for w in product(range(2),repeat=length):
                            got=cache.check(T,pi,w)
                            original=pairs.check(T,pi,w)
                            starts=cache.all_initial_witnesses(T,pi,w)
                            exact_starts=tuple(s for s in range(n) if trace(T,pi,s,length)==w)
                            expected=w in expected_words[length]
                            self.assertEqual(got.admissible,expected,(T,pi,w))
                            self.assertEqual(got.admissible,matrix_accepts(T,pi,w),(T,pi,w))
                            self.assertEqual(got.admissible,original.admissible,(T,pi,w))
                            self.assertEqual(starts,exact_starts,(T,pi,w))
                            self.assertEqual(got.survivor_count,len(exact_starts),(T,pi,w))
                            self.assertEqual(got.first_empty_length,original.first_empty_length,(T,pi,w))
                            self.assertEqual(got.witness_start,original.witness_start,(T,pi,w))
                            self.assertEqual(got.observed_trace,original.observed_trace,(T,pi,w))
                            checked+=1
        self.assertEqual(checked,268336)

if __name__=="__main__":unittest.main()
