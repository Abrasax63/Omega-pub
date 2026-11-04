import numpy as np, json, math
from pathlib import Path
OUT=Path('/mnt/data/qpred_20261020/Q_PREDICTIVE_HIDDEN_CHECKS_2026-10-20.json')

def ptrace_E(psi,d):
    A=psi.reshape(d,d)
    return A@A.conj().T

def bell(d,m,n):
    w=np.exp(2j*np.pi/d)
    v=np.zeros(d*d,dtype=complex)
    for j in range(d):
        v[j*d+((j+n)%d)] = w**(m*j)/np.sqrt(d)
    return v

def bell_basis(d):
    return np.stack([bell(d,m,n) for m in range(d) for n in range(d)],axis=1)

def swap(d):
    U=np.zeros((d*d,d*d),complex)
    for a in range(d):
        for b in range(d):
            U[b*d+a,a*d+b]=1
    return U

checks=[]
max_err=0.0
for d in range(2,11):
    B=bell_basis(d)
    gram=B.conj().T@B
    err_orth=float(np.max(np.abs(gram-np.eye(d*d))))
    red_err=0.0
    for k in range(d*d):
        rho=ptrace_E(B[:,k],d)
        red_err=max(red_err,float(np.max(np.abs(rho-np.eye(d)/d))))
    # decoder B^† maps Bell column k to computational basis k=(m,n)
    Udec=B.conj().T
    decode_err=float(np.max(np.abs(Udec@B-np.eye(d*d))))
    # product family |0,n>, SWAP -> |n,0>
    S=swap(d)
    prod_err=0.0
    for n in range(d):
        v=np.zeros(d*d,complex); v[n]=1 # |0,n> index 0*d+n
        target=np.zeros(d*d,complex); target[n*d+0]=1
        prod_err=max(prod_err,float(np.max(np.abs(S@v-target))))
    # Bell two-stage continuation: Udec -> |m,n>; measuring S gives m; reset S=0; SWAP -> |n,0>
    # Check computational labels produced by Udec exactly.
    checks.append({'d':d,'bell_states':d*d,'product_labels':d,'orthogonality_error':err_orth,
                   'same_reduced_state_error':red_err,'decoder_error':decode_err,'product_swap_error':prod_err,
                   'ambient_upper_bound':d*d,'product_environment_upper_bound':d})
    max_err=max(max_err,err_orth,red_err,decode_err,prod_err)

# Continuum predictive inequivalence for d=2 product hidden states |0>_S⊗|psi(theta)>_E, swap then Z measurement.
# p0(theta)=cos^2(theta), giving infinitely many distinct response laws on theta in [0,pi/2].
thetas=np.linspace(0,np.pi/2,1001)
ps=np.cos(thetas)**2
strict_monotone=bool(np.all(np.diff(ps)<0))
# A dense sample demonstrates distinct values; analytic derivative is -sin(2theta), strictly negative on interior.
unique_sample=len(np.unique(np.round(ps,14)))

out={
  'date':'2026-10-20',
  'experiment_1_product_and_correlated_perfect_predictive_labels':{
    'dimensions_checked':[2,3,4,5,6,7,8,9,10],
    'cases':checks,
    'max_numerical_error':max_err,
    'pass':max_err<1e-10,
    'analytic_bounds':{
      'product_cut':'N_perfect <= d_E because perfect discrimination requires pairwise orthogonal hidden environment supports; achieved by |0>_S|n>_E and SWAP when d_S=d_E=d.',
      'correlated_equal_dimension':'N_perfect <= d^2 by ambient Hilbert dimension; achieved by the d^2 generalized Bell states with common reduced I/d and one common Bell-decoder + system measurement/reset + SWAP + system measurement continuation.'
    }
  },
  'experiment_2_raw_predictive_class_count_is_not_dimension_bounded':{
    'dimension':2,
    'family':'|0>_S tensor (cos(theta)|0>+sin(theta)|1>)_E, theta in [0,pi/2]',
    'continuation':'SWAP then computational-basis measurement on S',
    'response':'P(0|theta)=cos(theta)^2',
    'sample_points':len(thetas),
    'sample_unique_probabilities':unique_sample,
    'strictly_monotone_sample':strict_monotone,
    'analytic_conclusion':'Uncountably many predictive equivalence classes already with d_E=2; therefore cardinality of predictive classes is not a finite-memory dimension measure. Perfect distinguishability number is the operational finite-dimensional invariant used instead.',
    'pass':strict_monotone and unique_sample==len(thetas)
  },
  'verdict':{
    'construction':'PASS',
    'original_G_cardinality_metric':'REFUTED_AS_DIMENSION_MEASURE',
    'corrected_operational_invariant':'N_perfect = maximum pairwise perfectly future-distinguishable histories sharing the same instantaneous reduced state',
    'product_exact':'d for d_S=d_E=d',
    'correlation_assisted_exact':'d^2 for d_S=d_E=d and local reduced I/d',
    'novelty_hint':'Components are classical/known (generalized Bell basis/dense coding, temporal dimension witnesses, process tensors); candidate value is as an internal bridge and exact specialization, not a new general quantum-memory principle.'
  }
}
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False))
print(json.dumps(out['verdict'],indent=2,ensure_ascii=False))
print('maxerr',max_err,'unique',unique_sample)