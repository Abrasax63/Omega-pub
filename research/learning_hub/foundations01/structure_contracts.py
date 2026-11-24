"""Exact finite rational instruments, not a PDE solver or neural training."""
from fractions import Fraction as F


def rational(x):
    if type(x) not in (int, F):
        raise ValueError('EXACT_RATIONAL_REQUIRED')
    return F(x)


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('DIMENSION')
    return sum((x*y for x,y in zip(a,b)), F(0))


def project_kernel(rows, vector):
    """Orthogonal projection onto kernel of a finite rational matrix.
    Exact Gram-Schmidt on row space, skipping dependent rows.
    """
    v = tuple(map(rational, vector))
    if not v:
        raise ValueError('EMPTY_VECTOR')
    basis = []
    for row in rows:
        w = tuple(map(rational, row))
        if len(w) != len(v):
            raise ValueError('DIMENSION')
        for b in basis:
            c = dot(w,b)/dot(b,b)
            w = tuple(x-c*y for x,y in zip(w,b))
        if any(w):
            basis.append(w)
    u = v
    for b in basis:
        c = dot(u,b)/dot(b,b)
        u = tuple(x-c*y for x,y in zip(u,b))
    return u


def closure_audit(samples):
    """Records (state_id, observation, observed_derivative_or_successor).
    A witness refutes deterministic closure on the given observation.
    Without a witness only consistency on supplied samples is claimed.
    """
    seen = {}
    ids = set()
    count = 0
    for ident, obs, future in samples:
        if ident in ids:
            raise ValueError('DUPLICATE_STATE_ID')
        ids.add(ident)
        count += 1
        if obs in seen and seen[obs][1] != future:
            return dict(status='REFUTED', witness=(seen[obs][0],ident), checked=count)
        seen[obs] = (ident,future)
    return dict(status='CONSISTENT_ON_SAMPLES' if count else 'NO_EVIDENCE', checked=count)


def periodic_primitive(increments):
    """Exact discrete cycle inverse: g[i+1]-g[i]=f[i], mean(g)=0.
    Discrete analogue of periodic primitive obstruction, not PDE inversion.
    """
    f = tuple(map(rational, increments))
    if not f:
        raise ValueError('EMPTY_CYCLE')
    if sum(f):
        return dict(status='INCOMPATIBLE', obstruction=sum(f))
    g = [F(0)]
    for x in f[:-1]:
        g.append(g[-1]+x)
    avg = sum(g)/len(g)
    return dict(status='SOLVED', primitive=tuple(x-avg for x in g))

REGISTRY = {
    'kernel_projection': {'function': project_kernel, 'scope': 'finite rational Euclidean row constraints', 'source': 'Leray projection analogy; exact row-space proof'},
    'closure_audit': {'function': closure_audit, 'scope': 'finite samples with fixed observation and future semantics', 'source': 'Delta_h recollement and Fourier low-mode counterexamples'},
    'periodic_primitive': {'function': periodic_primitive, 'scope': 'finite rational cyclic differences', 'source': 'discrete analogue of NS-CERT-E-15'},
}


def execute(operation, *args):
    if operation not in REGISTRY:
        raise ValueError('UNKNOWN_CONTRACT')
    return REGISTRY[operation]['function'](*args)
