# PROPOSAL-03 — targeted generation, preregistered before new inference
Question: when syntax and queried triple are fixed, can frozen SmolLM2-135M
choose graph bits to produce a specified logical motif more frequently than
uninformed generation? This is scaffolded task construction, not intrinsic
reasoning or parameter learning. Same pinned backbone and single-digit
constrained decoder as PROPOSAL-02, temperature .8, no top-k/p. Fix A,B,C
distinct as queried triple; model chooses all 9 adjacency bits. No oracle
or examples during decoding. Do not constrain the three relevant edges.

32 paired seeds 20261126+i (i=0..31), each seed assigned desired motif
format(i mod 8, '03b'), exactly four per motif. N neutral prompt asks for
any graph; T targeted prompt additionally describes desired presence of
A->B, B->C, A->C in plain language. N scored against same hidden assigned
motif (not passed to its prompt). Both arms generate nine bits, use same
sampling parameters; measure tokens and CPU separately (prompt lengths
differ). Uniform control U: independent 9 fair bits; expected exact motif
match 1/8, expected four matches/32; use exact Binomial(32,1/8) reference.
N vs T comparison paired by seed, no formal causal inference from small
cohort. Archive raw bits, token IDs, allowed masses, seeds, prompt hashes,
timings and exact model revision. Oracle labels after all generations.
Primary metric exact motif match, secondary match per bit and diversity;
T exploratory threshold >=16/32 and >=8 more successes than N, plus
>=1 match in each of eight motifs. Report the paired contingency counts,
no threshold revisions or retries. U is analytic control, not an LLM.
Even successful targeted construction does not establish autonomous choice
of learning goals: desired motif supplied externally. Diagnostic samples
only, no training or holdout. No paid API, no main changes.
Separate next stage: prospective supervised atomic LoRA feasibility on a
new independent cohort, compare base vs supervised and retain original
FOUNDATIONS-01 three-arm protocol as blocked until genuine proposals meet
its quotas. No substitution of human/oracle examples in self-generated arm.
