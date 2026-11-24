import unittest
from cost_policy01 import choose_efficient,solve_efficient
from invariant_select01 import choose,solve

class CostPolicyTests(unittest.TestCase):
    def test_entire_rule90_contract(self):
        for n in range(3,16):
            for h in range(7):
                p={"n":n,"h":h}
                m=choose_efficient("rule90_histogram",p)
                self.assertEqual(m,"causal_cone" if n-2*h-3>=2 else "direct")
                self.assertEqual(choose("rule90_histogram",p,m),m)
    def test_other_contracts_unchanged(self):
        for t,n in [("delta_census",5),("global_triple_census",4),("ordered_triple_census",4)]:
            self.assertEqual(choose_efficient(t,{"n":n}),choose(t,{"n":n}))
    def test_invalid_rejected(self):
        for t,p in [("unknown",{}),("rule90_histogram",{"n":True,"h":0}),("rule90_histogram",{"n":16,"h":0}),("rule90_histogram",{"n":8,"h":-1})]:
            with self.assertRaises(ValueError):choose_efficient(t,p)
    def test_exact_boundary(self):
        for n,h in [(3,0),(4,0),(5,0),(7,3),(10,3),(11,3),(15,6)]:
            p={"n":n,"h":h}
            result=solve_efficient("rule90_histogram",p)["outcome"]
            self.assertEqual(result["histogram"],solve("rule90_histogram",p,"direct")["histogram"])
if __name__=="__main__":unittest.main()
