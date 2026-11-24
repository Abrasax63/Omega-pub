# NET-STRESS01 — exact nonlinear factor-network stress
Preregistration 865d3babc7aa66e7a5617ffe2583bed68fc0c79d.
Implementation f707a0e4487d83c4bd4778b4c5f75916bdac243c.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45441178982.
Artifact 14944005487; GitHub-reported ZIP digest
52b68e20b6cc25bad07c90a19661aec112c27cc6bd63265768136c3339e978b3.
Results verified in CI logs, not independent replay of ZIP.

77 cases, exact count and count with variable 0 pinned to 1,
including 75 independently counted cases (exhaustive or row transfer)
and two dense cap stresses. Min-fill: 75 exact completed, 39 UNSAT,
21 forced-bit results, two RESOURCE_LIMIT. Fixed numerical ordering:
71 exact completed, 37 UNSAT, 19 forced-bit results, six RESOURCE_LIMIT.
No discrepancies on completed cases. 36 trivial opposite-pin
contradictions plus three nonlocal parity-cycle contradictions.
All three nonlocal contradictions at n=8,32,128 rejected by both
orderings. Pairwise satisfiability does not imply global satisfiability.

Min-fill maximum planned intermediate scope cardinality on completed
cases is 2048 configurations, fixed maximum 65536. This metric counts
the joint bucket scope before summation, not actual allocation or
total memory. Cap checks scope before enumeration; does not bound
aggregate RAM, integer bit length, runtime or input size.
n=128 paths: scope cardinality 4, width 1; ~30–32 ms min-fill,
~21 ms fixed. n=128 rings: cardinality 8, width 2; ~32 ms min-fill,
~21–27 ms fixed. n=64 grids (4 cases): min-fill width 10,
2048 configurations, ~41–43 ms, all completed; fixed reached
resource cap on all four. Dense complete n=18 and 24: both
stop at planned width 17 and 23 respectively, before enumerating
2^18 or 2^24 joint configurations. Dense examples use mixed AND/XOR
and may be easy for stronger constraint propagation; cap is a
limitation of this implementation, not a hardness result.
Min-fill is a heuristic, not a proof of optimal treewidth.
Exact inference from supplied factors, not discovery of factors
or autonomous learning. References share local relation semantics
but independently calculate global counts. One timing run, no
general speed claim. Preregistered checks pass.
Next falsifiable step: add propagation and affine-component
elimination before min-fill, with independent small brute-force
reference, dense structured and irreducible controls, same cap
and measured end-to-end cost. No silent promotion on unsupported
counts; retain simple ordering on cases without benefit.
No main changes, paid API, or autonomous runtime activation.
