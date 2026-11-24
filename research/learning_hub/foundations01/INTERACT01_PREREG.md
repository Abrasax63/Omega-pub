# INTERACT01 — learn a black-box finite dynamical law by intervention
Prospective experiment: an environment accepts state x in F2^6 and returns
the next six-bit state. Agent sees only x,y responses, not hidden law or
class labels. Supplied hypothesis space: vector Boolean polynomials of
degree <=2; no learned language model or automatic invention of grammar.
Compare rank-seeking intervention against uniform sampling without
replacement, exactly 22 distinct queries (1+6+15 coefficients), plus
8 disjoint uniform validation interventions per task. Active picks
randomly among inputs adding an independent feature row, no target
information; passive uses same seeded order without rank filtering.
Fit via GF2 elimination; inconsistent or rank-deficient systems abstain,
never fill missing coefficients arbitrarily. If validation disagrees,
refute; if it agrees, conditional candidate only, not proof of family
membership. Independent evaluator enumerates all 64 states after freeze
and checks 5-step rollouts from all states. Teachers 24 affine, 24
quadratic (at least one nonzero quadratic coefficient), 24 cubic
(nonzero cubic term), with random output coefficients, seed 20261127.
Distinct teacher truth tables; random invertible linear changes of
coordinates for half of each class, so hidden coordinate choice cannot
be relied upon. Compare 72 tasks each arm, exact truth table recovery,
5-step rollout exactness, abstentions, false candidate acceptance
outside grammar, number of queries, rank. Also report active vs fixed
basis-of-weight<=2 design at same budget; fixed basis is a strong
nonadaptive intervention baseline. Primary: active 48/48 in-family
exact, zero false certificates (no unconditional certificate permitted),
active >= passive on exact recovery; any out-of-family candidate
explicitly marked unsafe outside assumed class. No promotion on false
acceptances; no claim of spontaneous discovery, generalization beyond
finite tasks or neural weight update. No paid API, no main change.
