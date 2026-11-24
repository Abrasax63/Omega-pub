"""Run with PYTHONPATH pointing to PR250 prism at e68db2c2ca3f14d113fc15f431fac04d5ee7cb30."""
import itertools
import json
import unittest
import omega_hybrid_exact_sensor as sensor
from teacher import admit

class TeacherTests(unittest.TestCase):
    def test_exhaustive(self):
        nodes = ["a","b","c"]
        pairs = list(itertools.product(nodes, repeat=2))
        count = 0
        for mask in range(512):
            edges = [list(e) for i,e in enumerate(pairs) if mask & (1<<i)]
            for triple in itertools.product(nodes,repeat=3):
                x,y,z = triple
                expected = {"xy":[x,y] in edges,"yz":[y,z] in edges,"xz":[x,z] in edges}
                expected["violates"] = expected["xy"] and expected["yz"] and not expected["xz"]
                row = admit(dict(nodes=nodes,edges=edges,triple=list(triple)),sensor)
                self.assertEqual(json.loads(row["target"]),expected)
                self.assertFalse(row["model_generated"])
                count += 1
        self.assertEqual(count,13824)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            admit(dict(nodes=["a"],edges=[["a","b"]],triple=["a","a","a"]),sensor)

if __name__ == "__main__":
    unittest.main()
