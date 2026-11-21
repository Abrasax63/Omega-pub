"""Full witness verdict parity of adaptive compressed representation."""
import unittest
from adaptive_bitset import AdaptiveBitsetRouter
from witness_cache import NaiveExact
from bench_finite import make_cases

class AdaptiveBitsetTests(unittest.TestCase):
    def test_first_call_no_bitset_allocation(self):
        a=AdaptiveBitsetRouter("adaptive-bitset")
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        self.assertEqual(a.check(T,pi,w),NaiveExact().check(T,pi,w))
        self.assertEqual(a.counters()["bitset_prefix_entries"],0)
        self.assertEqual(a.counters()["direct_calls"],1)
    def test_repetition_then_bitset_cache_hit(self):
        a=AdaptiveBitsetRouter("adaptive-bitset")
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        baseline=NaiveExact().check(T,pi,w)
        for _ in range(3):self.assertEqual(a.check(T,pi,w),baseline)
        self.assertEqual(a.counters()["direct_calls"],1)
        self.assertEqual(a.counters()["bitset_calls"],2)
        self.assertGreater(a.counters()["bitset_hits"],0)
    def test_n_8_32_128_512_both_profiles_preserve_verdicts(self):
        for n in (8,32,128,512):
            for profile in ("repeated","unique_systems"):
                cases=make_cases(n,profile)
                a=AdaptiveBitsetRouter("adaptive-bitset")
                direct=NaiveExact()
                for case in cases:
                    self.assertEqual(a.check(*case),direct.check(*case),(n,profile))
                if profile=="unique_systems":
                    self.assertEqual(a.counters()["bitset_prefix_entries"],0)
                    self.assertEqual(a.counters()["bitset_calls"],0)
                    self.assertEqual(a.counters()["direct_calls"],len(cases))
                else:
                    self.assertEqual(a.counters()["direct_calls"],1)
                    self.assertEqual(a.counters()["bitset_calls"],len(cases)-1)
    def test_both_internal_ghosts_rejected(self):
        c=AdaptiveBitsetRouter("adaptive-bitset")
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        self.assertEqual(c.check(T,pi,w).first_empty_length,3)
        self.assertEqual(c.check(T,pi,w).first_empty_length,3)
        T=(0,3,1,3);pi=(0,0,0,1);w=(0,0,0,1)
        self.assertEqual(c.check(T,pi,w).first_empty_length,4)
        self.assertEqual(c.check(T,pi,w).first_empty_length,4)
    def test_unsupported_mode_fails_closed(self):
        for mode in ("llm","automatic","","cached"):
            with self.assertRaises(ValueError):AdaptiveBitsetRouter(mode)
    def test_bounded_tracking(self):
        c=AdaptiveBitsetRouter("adaptive-bitset",max_tracked_systems=2,max_prefixes=4)
        for n in range(2,12):
            T=tuple((i+1)%n for i in range(n))
            pi=tuple(i%2 for i in range(n))
            c.check(T,pi,(0,1))
            c.check(T,pi,(0,1))
        self.assertLessEqual(c.counters()["tracked_systems"],2)
        self.assertLessEqual(c.counters()["bitset_prefix_entries"],4)
        self.assertGreater(c.counters()["tracking_evictions"],0)
if __name__=="__main__":unittest.main()
