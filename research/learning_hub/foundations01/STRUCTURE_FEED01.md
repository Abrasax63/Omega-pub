# STRUCTURE-FEED01 — executable mathematical instruments
Purpose: feed Omega with reusable operations, not merely documents.
Three typed contracts in structure_contracts.py, callable via execute:
- kernel_projection: exact rational orthogonal projection onto the kernel
  of any finite matrix, by orthogonalizing its rows. Inspired by Fourier
  Leray projection; no PDE or complex arithmetic claim.
- closure_audit: two distinct state IDs with identical observation but
  different observed future refute a deterministic observed evolution,
  assuming the supplied records are correct and comparable. No witness
  implies only sample consistency, never universal certification.
- periodic_primitive: exact finite cyclic inverse of forward differences,
  with zero mean gauge. Sum of increments must vanish (telescoping);
  cumulative sums then mean subtraction construct the unique solution.
  Discrete analogue of periodic primitive obstruction NS-CERT-E-15.
Projection proof: orthogonal nonzero Gram-Schmidt rows span the original
row space; subtracting each orthogonal component leaves the orthogonal
complement, exactly the kernel. No floating point approximations.
Local six unittest methods passed: 625 single-row projection examples
(including zero mode), 125 dependent-row examples, 19 Fourier closure
witness pairs (m=2..20), 243 five-cycle increment vectors, status and
invalid-input checks. Tests constructed by developer; not unseen autonomous
learning evaluation. Closure samples require hashable observation keys,
trusted state IDs and compatible future values; no claim of verifying
provenance or authenticity.
Next candidates from historical NS tools: divergence-free localization,
relative margin stability, weighted radial compatibility, energy balance;
then transfer to other scientific domains with scope and negative tests.
Registry is a callable experimental library, NOT wired into autonomous
runtime, not a model weight update, not general semantic tool selection.
No main changes; no paid API. CI reproduction configured.
