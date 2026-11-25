"""PROTECT21: bounded displacement feasibility kernel. No model training."""
import math
import numpy as np

def protect(displacement, anchors, sweeps=64, rtol=1e-10):
    d=np.asarray(displacement,dtype=np.float64)
    g=np.asarray(anchors,dtype=np.float64)
    if d.ndim!=1 or g.ndim!=2 or g.shape[1]!=d.size or not np.isfinite(d).all() or not np.isfinite(g).all():
        raise ValueError("INVALID_INPUT")
    if not isinstance(sweeps,int) or sweeps<1 or not math.isfinite(rtol) or not 0<=rtol<=1e-6:
        raise ValueError("INVALID_LIMIT")
    norms=np.linalg.norm(g,axis=1)
    n=float(np.linalg.norm(d))
    if not np.isfinite(norms).all() or not math.isfinite(n): raise ValueError("INVALID_NORM")
    unit=g[norms>0]/norms[norms>0,None]
    tol=rtol*n
    v=d.copy()
    for i in range(sweeps+1):
        if np.all(unit@v<=tol):
            return v,{"sweeps":i,"fallback":False,"norm_ratio":float(np.linalg.norm(v))/n if n else 0.0,
                      "violations_before":int(np.sum(unit@d>tol))}
        if i==sweeps: break
        for a in unit:
            s=float(a@v)
            if s>tol: v-=s*a
    return np.zeros_like(d),{"sweeps":sweeps,"fallback":True,"norm_ratio":0.0,
                            "violations_before":int(np.sum(unit@d>tol))}

def selftest():
    # No conflict, one conflict, opposed anchors and nonorthogonal anchors.
    cases=[([1,2],[[-1,0],[0,-1]],[1,2]),
           ([1,2],[[1,0]],[0,2]),
           ([1,2],[[1,0],[-1,0]],[0,2]),
           ([1,2],[[0,0]],[1,2])]
    for d,g,w in cases:
        v,meta=protect(d,g)
        assert np.allclose(v,w) and not meta["fallback"]
    rng=np.random.default_rng(21)
    for _ in range(100):
        d=rng.normal(size=8);g=rng.normal(size=(4,8))
        v,m=protect(d,g)
        unit=g/np.linalg.norm(g,axis=1)[:,None]
        assert np.all(unit@v<=1e-10*np.linalg.norm(d))
        assert np.linalg.norm(v)<=np.linalg.norm(d)+1e-8
    # Bounded fallback and invalid inputs must fail closed.
    v,m=protect([1,2],[[1,0],[-1,1]],sweeps=1)
    assert m["fallback"] and np.all(v==0)
    for d,g in [([np.nan],[[1]]),([1],[[np.inf]]),([1],[[1,2]])]:
        try: protect(d,g)
        except ValueError: pass
        else: raise AssertionError("invalid input accepted")
    print("PROTECT21_KERNEL_OK: 100 randomized feasibility checks; zero model updates")

if __name__=="__main__": selftest()
