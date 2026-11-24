import itertools as it
import unittest
from fractions import Fraction as F
from structure_contracts import execute, dot

class TestContracts(unittest.TestCase):
    def test_leray_exact(self):
        for k in it.product(range(-2,3),repeat=2):
            for a in it.product(range(-2,3),repeat=2):
                u=execute('kernel_projection',[k],a)
                d=dot(k,k)
                ref=tuple(F(x)-dot(k,a)*y/d for x,y in zip(a,k)) if d else a
                self.assertEqual(u,ref)
                self.assertEqual(dot(k,u),0)
                self.assertEqual(execute('kernel_projection',[k],u),u)
    def test_dependent_constraints(self):
        rows=[(1,1,0),(2,2,0),(0,1,1)]
        for a in it.product(range(-2,3),repeat=3):
            u=execute('kernel_projection',rows,a)
            b=(1,-1,1)
            self.assertEqual(u,tuple(dot(a,b)*x/3 for x in b))
            self.assertTrue(all(dot(r,u)==0 for r in rows))
    def test_fourier_closure(self):
        for m in range(2,21):
            # p=(m+1,1), q=(-m,-1); both high, p+q=(1,0).
            p,q=(m+1,1),(-m,-1)
            a,b=(-1,m+1),(1,-m)
            d=tuple(-dot(a,q)*v-dot(b,p)*w for v,w in zip(b,a))
            u=execute('kernel_projection',[(1,0)],d)
            self.assertEqual(u,(0,-(2*m+1)))
            obs=(0,dot(a,a)+dot(b,b),dot(p,p)*dot(a,a)+dot(q,q)*dot(b,b))
            r=execute('closure_audit',[('plus',obs,u),('minus',obs,tuple(-v for v in u))])
            self.assertEqual(r['status'],'REFUTED')
    def test_closure_limits(self):
        self.assertEqual(execute('closure_audit',[])['status'],'NO_EVIDENCE')
        self.assertEqual(execute('closure_audit',[(0,1,2),(1,1,2)])['status'],'CONSISTENT_ON_SAMPLES')
        with self.assertRaises(ValueError):execute('closure_audit',[(0,1,2),(0,1,3)])
    def test_cycle(self):
        for f in it.product(range(-1,2),repeat=5):
            r=execute('periodic_primitive',f)
            if sum(f):self.assertEqual(r,dict(status='INCOMPATIBLE',obstruction=sum(f)))
            else:
                g=r['primitive'];self.assertEqual(sum(g),0)
                self.assertEqual(tuple(g[(i+1)%5]-g[i] for i in range(5)),f)
    def test_invalid(self):
        for op,args in [('unknown',()),('kernel_projection',([(1,2)],(1,))),('kernel_projection',([], (0.5,))),('periodic_primitive',([],))]:
            with self.assertRaises(ValueError):execute(op,*args)

if __name__=='__main__':unittest.main()
