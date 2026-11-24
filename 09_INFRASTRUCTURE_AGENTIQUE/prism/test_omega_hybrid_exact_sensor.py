"""No-LLM tests: Omega exact sensor cannot invent or silently repair data."""
import unittest

from omega_hybrid_exact_sensor import (
    inspect_atom,inspect_relation,validate_relation
)


class ExactSensorTests(unittest.TestCase):
    def test_all_eight_bit_patterns_exhaustive_with_tool(self):
        for mask in range(8):
            edges=[[p,q] for bit,(p,q) in enumerate(
                (("x","y"),("y","z"),("x","z")))
                if mask & (1<<(2-bit))]
            packet={"nodes":["x","y","z"],"edges":edges,"triple":["x","y","z"]}
            r=inspect_atom(packet)
            bits=r["bits"]
            self.assertEqual(bits["xy"],bool(mask&4))
            self.assertEqual(bits["yz"],bool(mask&2))
            self.assertEqual(bits["xz"],bool(mask&1))
            self.assertEqual(r["violates_transitivity_for_this_triple"],mask==6)
            self.assertFalse(r["model_skill_certified"])

    def test_genuine_negative_certificate_reuses_proven_oracle(self):
        p={"nodes":["a","b","c"],"edges":[
            ["a","a"],["b","b"],["c","c"],["a","b"],["b","a"],
            ["b","c"],["c","b"]]}
        r=inspect_relation(p)
        self.assertFalse(r["equivalence"])
        self.assertIn("transitive",r["failed_axioms"])
        bits=r["certificate"]["premises"]
        self.assertEqual(bits,{"xy":True,"yz":True,"xz":False})
        self.assertEqual(r["certificate"]["kind"],"missing_transitive_edge")
        self.assertFalse(r["model_weight_update"])

    def test_positive_partition_complete(self):
        nodes=["a","b","c","d"]
        e=[[x,x] for x in nodes]+[["a","b"],["b","a"],["c","d"],["d","c"]]
        out=inspect_relation({"nodes":nodes,"edges":e})
        self.assertTrue(out["equivalence"])
        self.assertEqual(out["certificate"]["blocks"],[["a","b"],["c","d"]])
        self.assertFalse(out["model_skill_certified"])

    def test_reflexivity_failure_is_not_fake_transitivity_witness(self):
        out=inspect_relation({"nodes":["a","b"],"edges":[]})
        self.assertFalse(out["equivalence"])
        self.assertIn("reflexive",out["failed_axioms"])
        self.assertEqual(out["certificate"]["kind"],"exact_axiom_failures")

    def test_duplicate_edge_rejected_instead_of_deduplicated(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_DIRECTED_EDGE"):
            validate_relation(["a"],[["a","a"],["a","a"]])

    def test_outside_node_is_not_inferred(self):
        with self.assertRaisesRegex(ValueError,"EDGE_ENDPOINT_OUTSIDE_UNIVERSE"):
            validate_relation(["a","b"],[["a","c"]])

    def test_invalid_triple_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_TRIPLE"):
            inspect_atom({"nodes":["a","b"],"edges":[],
                          "triple":["a","b","unknown"]})

    def test_packet_schema_is_strict(self):
        with self.assertRaisesRegex(ValueError,"REQUIRES_EXACT_ATOM_PACKET"):
            inspect_atom({"nodes":["a"],"edges":[],"triple":["a","a","a"],
                          "extra":"secret"})
        with self.assertRaisesRegex(ValueError,"INVALID_NODE_UNIVERSE"):
            validate_relation(["a","a"],[])

if __name__=="__main__":
    unittest.main()
