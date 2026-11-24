import json
import unittest
from atomic_eval import exact,render,parse,score,compare_atomic
from corpus_gate import identities,quotas
from itertools import product

class AtomicEvalTests(unittest.TestCase):
    def setUp(self):
        self.p={"nodes":["a","b","c"],"edges":[["a","b"],["b","c"]],"triple":["a","b","c"]}
        self.t={"id":"x","packet":self.p}

    def test_matrix_and_list(self):
        self.assertEqual(exact(self.p),dict(xy=True,yz=True,xz=False,violates=True))
        self.assertIn('"matrix":[[0,1,0],[0,0,1],[0,0,0]]',render(self.p,"matrix"))
        self.assertNotIn('"violates":',render(self.p,"edges"))
        with self.assertRaises(ValueError):
            render(self.p,"unknown")

    def test_strict_booleans(self):
        for raw in ('{"xy":1,"yz":true,"xz":false,"violates":true}',
                    '{"xy":false,"xy":true,"yz":true,"xz":false,"violates":true}',
                    'not json'):
            self.assertIsNone(parse(raw))

    def test_wrong_logic_after_correct_reading(self):
        pred=dict(exact(self.p),violates=False)
        r=score([self.t],{"x":json.dumps(pred)})["groups"]["all"]
        self.assertEqual((r["reading"],r["decision"],r["consistent"],r["joint"]),(1,0,0,0))

    def test_right_decision_wrong_reading(self):
        pred=dict(xy=False,yz=False,xz=False,violates=True)
        r=score([self.t],{"x":json.dumps(pred)})["groups"]["all"]
        self.assertEqual((r["reading"],r["decision"],r["consistent"],r["joint"]),(0,1,0,0))

    def test_missing_and_invalid(self):
        with self.assertRaises(ValueError):
            score([self.t],{})
        r=score([self.t],{"x":"bad"})["groups"]["all"]
        self.assertEqual(r["n"],1)
        self.assertEqual(r["joint"],0)

    def test_balanced_comparison_and_constant_baseline(self):
        # Disposable synthetic fixture, not a real evaluation cohort.
        ns=["a","b","c"]
        pairs=list(product(ns,repeat=2))
        q=quotas(128)
        seen=set()
        rows=[]
        for mask in range(512):
            es=[list(e) for i,e in enumerate(pairs) if mask&(1<<i)]
            for tr in product(ns,repeat=3):
                p=dict(nodes=ns,edges=es,triple=list(tr))
                k=identities(p)[1]
                e=exact(p)
                m="".join(str(int(e[x])) for x in ("xy","yz","xz"))
                if q[m] and k not in seen:
                    q[m]-=1
                    seen.add(k)
                    rows.append(dict(id=str(len(rows)),packet=p))
            if not any(q.values()):
                break
        self.assertEqual(len(rows),128)
        const={r["id"]:'{"xy":false,"yz":false,"xz":false,"violates":false}' for r in rows}
        perfect={r["id"]:json.dumps(exact(r["packet"])) for r in rows}
        out=compare_atomic(rows,dict(base=const,supervised=const,self_generated=perfect))
        self.assertEqual(out["scores"]["base"]["groups"]["all"]["decision"],64)
        self.assertTrue(out["comparisons"]["self_generated"]["atomic_gain"])
        self.assertFalse(out["comparisons"]["supervised"]["atomic_gain"])
        self.assertFalse(out["promotion_authorized"])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            compare_atomic(rows[:-1]+[rows[0]],dict(base=const,supervised=const,self_generated=perfect))
