"""SCALE01 guardrails for exact state scaling, witness parity and routing."""
import unittest
from exact_router import ExactGluingRouter
from witness_cache import NaiveExact
from bench_finite import make_cases, report

class ExactScalingTests(unittest.TestCase):
    def test_adaptive_first_request_is_direct(self):
        r=ExactGluingRouter("adaptive")
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        self.assertEqual(r.check(T,pi,w),NaiveExact().check(T,pi,w))
        self.assertEqual(r.counters()["direct_calls"],1)
        self.assertEqual(r.counters()["prefix_cache_entries"],0)
        self.assertEqual(r.counters()["cache_hits"],0)
    def test_adaptive_switch_then_reuse(self):
        r=ExactGluingRouter("adaptive")
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        a=r.check(T,pi,w)
        b=r.check(T,pi,w)
        c=r.check(T,pi,w)
        self.assertEqual(a,b)
        self.assertEqual(b,c)
        self.assertEqual(r.counters()["direct_calls"],1)
        self.assertEqual(r.counters()["cached_calls"],2)
        self.assertEqual(r.counters()["cache_hits"],1)
    def test_no_false_reuse_when_system_changes(self):
        r=ExactGluingRouter("adaptive")
        T=(0,0,2);p=(0,1,1);w=(1,1,0)
        first=r.check(T,p,w)
        changed=r.check((0,0,1),p,w)
        self.assertEqual(first,NaiveExact().check(T,p,w))
        self.assertEqual(changed,NaiveExact().check((0,0,1),p,w))
        self.assertEqual(r.counters()["direct_calls"],2)
        self.assertEqual(r.counters()["cache_hits"],0)
    def test_adaptive_system_memory_is_bounded(self):
        r=ExactGluingRouter("adaptive",max_systems=2,max_prefixes=3)
        for n in range(3,15):
            T=tuple((i+1)%n for i in range(n))
            pi=tuple(i%2 for i in range(n))
            for _ in range(3):
                r.check(T,pi,(0,1,0,1))
            self.assertLessEqual(r.counters()["tracked_systems"],2)
            self.assertLessEqual(r.counters()["prefix_cache_entries"],3)
        self.assertGreater(r.counters()["system_evictions"],0)
    def test_counterexample_110_rejected_in_all_modes(self):
        T=(0,0,2);pi=(0,1,1);w=(1,1,0)
        for mode in ("off","on","adaptive"):
            r=ExactGluingRouter(mode)
            result=r.check(T,pi,w)
            self.assertFalse(result.admissible)
            self.assertEqual(result.first_empty_length,3)
    def test_no_repetition_remains_direct(self):
        r=ExactGluingRouter("adaptive")
        for T,pi,word in make_cases(8,"unique_systems"):
            r.check(T,pi,word)
        self.assertEqual(r.counters()["direct_calls"],24)
        self.assertEqual(r.counters()["cached_calls"],0)
    def test_invalid_configuration_fails(self):
        for mode in ("", "automatic","model","llm"):
            with self.assertRaises(ValueError):ExactGluingRouter(mode)
        with self.assertRaises(ValueError):ExactGluingRouter(max_systems=0)
    def test_finite_scale_reports_exact_parity(self):
        r=report()
        self.assertEqual(len(r["runs"]),8)
        self.assertTrue(all(v["all_three_verdicts_and_witnesses_equal"] for v in r["runs"]))
        self.assertTrue(all(v["modes"]["adaptive"]["cache_hits"]==0 for v in r["runs"] if v["profile"]=="unique_systems"))
        self.assertEqual({v["n_states"] for v in r["runs"]},{8,32,128,512})
if __name__=="__main__": unittest.main()
