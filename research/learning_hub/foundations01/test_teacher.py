"""Run with PYTHONPATH pointing to PR250 prism at e68db2c2ca3f14d113fc15f431fac04d5ee7cb30."""
import itertools
import json
import unittest
import omega_hybrid_exact_sensor as sensor
from teacher import admit
from corpus_gate import identities, motif, quotas, audit_splits
from proposer import collect

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

class CorpusGateTests(unittest.TestCase):
    def setUp(self):
        self.a=dict(nodes=["a","b","c"],edges=[["a","b"],["b","c"]],triple=["a","b","c"])
        self.b=dict(nodes=["x","y","z"],edges=[["y","x"],["z","y"]],triple=["z","y","x"])

    def test_renamed_proposal(self):
        self.assertEqual(identities(self.a),identities(self.b))
        report=collect([json.dumps(self.a),json.dumps(self.b)],sensor)
        self.assertEqual(len(report["accepted"]),1)
        self.assertEqual(report["rejected"][0]["reason"],"DUPLICATE_ISOMORPHIC_TASK")

    def test_graph_key_ignores_triple(self):
        altered=dict(self.a,triple=["c","c","c"])
        self.assertEqual(identities(self.a)[0],identities(altered)[0])
        self.assertNotEqual(identities(self.a)[1],identities(altered)[1])

    def test_all_three_node_graphs(self):
        nodes=["a","b","c"]
        pairs=list(itertools.product(nodes,repeat=2))
        graph_keys=set()
        task_keys=set()
        counts={}
        for mask in range(512):
            edges=[list(e) for i,e in enumerate(pairs) if mask & (1<<i)]
            for triple in itertools.product(nodes,repeat=3):
                packet=dict(nodes=nodes,edges=edges,triple=list(triple))
                g,k=identities(packet)
                graph_keys.add(g)
                task_keys.add(k)
                m=motif(packet)
                counts[m]=counts.get(m,0)+1
        self.assertEqual(len(graph_keys),104)
        self.assertEqual(len(task_keys),2320)
        self.assertEqual(sum(counts.values()),13824)
        self.assertEqual(counts["110"],768)

    def test_quotas(self):
        for size in (256,64,128):
            q=quotas(size)
            self.assertEqual(sum(q.values()),size)
            self.assertEqual(q["110"],size//2)
            self.assertEqual(len(q),8)
            negatives=[n for m,n in q.items() if m!="110"]
            self.assertLessEqual(max(negatives)-min(negatives),1)
        with self.assertRaises(ValueError):
            quotas(13)

    def test_split_overlap_with_new_triple(self):
        # Generate a balanced, unique task list for one split, then leak a
        # renamed graph into dev. Curator must reject despite new triple.
        rows=[]
        seen=set()
        q=quotas(14)
        nodes=["a","b","c"]
        pairs=list(itertools.product(nodes,repeat=2))
        for mask in range(512):
            edges=[list(e) for i,e in enumerate(pairs) if mask & (1<<i)]
            for triple in itertools.product(nodes,repeat=3):
                p=dict(nodes=nodes,edges=edges,triple=list(triple))
                m=motif(p)
                k=identities(p)[1]
                if q[m] and k not in seen:
                    q[m]-=1
                    seen.add(k)
                    rows.append(p)
            if not any(q.values()):
                break
        self.assertEqual(len(rows),14)
        leaked=dict(rows[0],triple=["c","c","c"])
        with self.assertRaisesRegex(ValueError,"GRAPH_OVERLAP"):
            audit_splits(dict(train=rows,dev=[leaked]*14,holdout=rows),
                         dict(train=14,dev=14,holdout=14))

    def test_invalid_packet(self):
        with self.assertRaises(ValueError):
            identities(dict(self.a,edges=[["a","b"],["a","b"]]))

if __name__ == "__main__":
    unittest.main()
