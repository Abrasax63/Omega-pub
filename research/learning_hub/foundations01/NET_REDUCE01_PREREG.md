# NET-REDUCE01 — exact preprocessing before nonlinear factor elimination
Freeze before implementation. Reuse NET-STRESS01's exact cap (65536
joint configurations) and all 77 original cases, regenerated with
unchanged RNG and iteration order. Add 12 dense structured cases:
n=24,64,128; complete pair XOR with planted bits (2 assignments),
same plus pin (1), same plus inconsistent XOR (0), complete OR=1
(n+1 assignments, irreducible to pins/parity by our local rules).
Independent counts with variable 0 pinned, from enumeration/transfer
on original 75, independent recursive domain propagation + branching
on original 2 dense cases, analytic formulas on new 12.
Compare plain min-fill, unary propagation only, and unary+parity
union-find reduction followed by min-fill on compressed roots.
All three share cap, same relations and exact count/forced-bit semantics.
Substitution of affine-equivalent bits is bijective on remaining root
assignments, preserve multiplicity including isolated variables.
Repeat simplification until no new forced bits or parity relations.
Translate remaining binary allowed assignments to forbidden-pair clauses.
Record original/reduced sizes, exact count, resource abstention, max
planned scope, time including preprocessing and both count queries.
Primary: full reduction agrees with independent reference on every
completed case, never regresses any originally solved case, recovers
both original dense cases and all nine new XOR cases without guessing,
and zero false forced bits. OR controls may still abstain; do not claim
universal dense inference. Compare cost and unary-only ablation; no
promotion as universal policy if overhead on easy cases. Single run
timings descriptive. No main changes, paid API or neural training.
