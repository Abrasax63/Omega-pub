import sympy as sp
k=sp.symbols('k')
def Q(r):
    return sp.expand(sum(sp.mobius(d)*k**(r//d) for d in sp.divisors(r)))
def v8_term(n,i):
    return Q(n) if i==0 else sp.expand((k-1)*k**(i-1)*Q(n-i))
for n in range(1,9):
    lhs=sp.expand(sum(v8_term(n,i) for i in range(n)))
    rhs=sp.expand(Q(n)+sum((k-1)*k**(i-1)*Q(n-i) for i in range(1,n)))
    assert sp.expand(lhs-rhs)==0
    print(n, sp.factor(lhs))
