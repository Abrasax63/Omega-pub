"""Regression and independent exhaustive audit of witness-preserving cache."""
from itertools import product
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/"02_MATHEMATIQUES"/"defauts_recollement"/"sources"))

from witness_cache import NaiveExact,WitnessCache

class GluingCacheTests(unittest.TestCase):
    def test_p2_not_p1_phantom_110(self):
        T=(0,0,2); pi=(0,1,1); w=(1,1,0)
        result=WitnessCache().check(T,pi,w)
        self.assertFalse(result.admissible)
        self.assertEqual(result.first_empty_length,3)
        Q={(pi[x],pi[T[x]]) for x in range(len(T))}
        self.assertTrue(all((w[i],w[i+1]) in Q for i in range(len(w)-1)))

    def test_same_macro_Q_different_W3_not_merged(self):
        A=(0,0,2,2); api=(0,1,1,0)
        B=(1,0,0,1); bpi=(0,1,0,1)
        self.assertEqual({(api[x],api[A[x]]) for x in range(4)},
                         {(bpi[x],bpi[B[x]]) for x in range(4)})
        cache=WitnessCache()
        self.assertFalse(cache.check(A,api,(0,0,1)).admissible)
        self.assertTrue(cache.check(B,bpi,(0,0,1)).admissible)
        self.assertEqual(cache.check(B,bpi,(0,0,1)).observed_trace,(0,0,1))

    def test_deep_obstruction_0001_despite_triples(self):
        # m=2 family in DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md
        T=(0,3,1,3); pi=(0,0,0,1); c=WitnessCache()
        self.assertTrue(c.check(T,pi,(0,0,0)).admissible)
        self.assertTrue(c.check(T,pi,(0,0,1)).admissible)
        v=c.check(T,pi,(0,0,0,1))
        self.assertFalse(v.admissible)
        self.assertEqual(v.first_empty_length,4)

    def test_repeat_reuses_exact_same_certificate(self):
        T=(0,3,1,3);pi=(0,0,0,1);w=(0,0,0,0)
        c=WitnessCache();a=c.check(T,pi,w);before=c.update_steps
        self.assertEqual(a,c.check(T,pi,w))
        self.assertEqual(c.update_steps,before)
        self.assertEqual(c.cache_hits,1)

    def test_mutated_micro_system_invalidates_cache(self):
        T=(0,1,2);p=(0,1,0);w=(0,1)
        c=WitnessCache()
        a=c.check(T,p,w)
        b=c.check((1,1,2),p,w)
        d=c.check(T,(0,0,1),w)
        self.assertNotEqual((a,b,d),(a,a,a))
        self.assertEqual(len([key for key in c.memo if key[2]==w]),3)

    def test_bounded_lru_and_recompute_remain_exact(self):
        c=WitnessCache(max_entries=2)
        T=(0,2,2);p=(0,0,1)
        for w in ((0,),(0,0),(0,0,1),(1,),(1,1),(0,0,1)):
            self.assertEqual(c.check(T,p,w),NaiveExact().check(T,p,w))
        self.assertLessEqual(len(c.memo),2)
        self.assertGreater(c.evictions,0)

    def test_changed_label_or_transition_does_not_share_results(self):
        c=WitnessCache()
        a=c.check((0,0,2),(0,1,1),(1,1,0))
        b=c.check((0,0,2),(0,1,1),(1,1,0))
        self.assertEqual(a,b)
        self.assertFalse(b.admissible)
        self.assertGreater(c.cache_hits,0)

    def test_bad_data_fail_closed(self):
        c=WitnessCache()
        for T,p,w in (([0,1],(0,1),(0,)),((0,1),[0,1],(0,)),
                       ((0,1),(0,1),[0]),((0,3),(0,1),(0,)),
                       ((0,1),(0,),(0,)),((0,1),(0,-1),(0,))):
            with self.assertRaises((TypeError,ValueError)):
                c.check(T,p,w)

    def test_independent_crosscheck_exhaustive_N_leq_4_q2_L_leq_5(self):
        # Two original independent oracles already present on main:
        # direct micro traces and boolean matrix propagation.
        from delta_gluing_audit import words
        from delta_gluing_crosscheck import matrix_accepts
        cache=WitnessCache(max_entries=50000)
        tested=0
        for n in (2,3,4):
            for T in product(range(n),repeat=n):
                for pi in product(range(2),repeat=n):
                    if set(pi)!={0,1}:continue
                    reference={L:words(T,pi,L) for L in range(1,6)}
                    for L in range(1,6):
                        for w in product(range(2),repeat=L):
                            result=cache.check(T,pi,w)
                            expected=w in reference[L]
                            independent=matrix_accepts(T,pi,w)
                            self.assertEqual(result.admissible,expected,(T,pi,w))
                            self.assertEqual(result.admissible,independent,(T,pi,w))
                            if expected:
                                self.assertEqual(result.observed_trace,w)
                                self.assertIsNone(result.first_empty_length)
                            else:
                                self.assertIsNone(result.witness_start)
                                self.assertIsNotNone(result.first_empty_length)
                            tested+=1
        self.assertEqual(tested,232748)

if __name__=="__main__":unittest.main()
