# LEARN-POLICY01 — reward-driven acquisition with frozen counting engine
Question: can a persistent policy improve its own branching decisions from
experience, without developer changes after training begins? Task is exact
independent-set counting, equivalent to positive pair-OR constraints.
New isolated sandbox: same immutable bitmask engine for all arms, recurrence
I(G)=I(G-v)+I(G-N[v]), exact component multiplication, isolated vertices,
memoization within each graph, no hand-coded special reductions.
Only a five-dimensional policy vector may change. Features for a vertex:
degree normalized by current graph size, mean neighbor degree normalized,
number of edges within its neighborhood normalized by possible pairs,
number of degree-one neighbors normalized by degree, constant tie preference
for low vertex index normalized by original n. Fixed incumbent max-degree
vector (1,0,0,0,0) with smallest-index tie. Fixed minimum-degree and
max-neighbor-degree controls. No solution method labels supplied in training.
Evolutionary hill-climb: 40 proposals from current vector, seeded Gaussian
mutations, evaluate each on identical 24 training graphs, accept strictly
lower sum of visits (budget failure penalized at 4097); no gold counts
given to optimizer, only scalar cost for completed counts. All results
are separately audited by brute-force bitset on training graphs. Candidate
weights stored, reloaded from JSON for evaluation, no code changes.
Training: n=12,16,20, 8 each, random graphs p=.12,.25,.4,.6 twice,
seed 20261212. Holdout seed 20261213, 48 distinct graphs: n=16,20,24,32,
48,64, 8 each, 4 random density and 4 two-community graphs with weak
cross edges. Different generation seeds, no holdout evaluation during
optimization. Same author and generator, not externally blind.
Compare frozen before/after policy, fixed min-degree, fixed neighbor-degree.
Cap 4096 recursive visits per count; cache <=4096 entries, no guesses.
Independent reference on n<=20 via exhaustive bitset; larger via independent
exact counting by literal branching and unit propagation with 65536 visit
cap (reference limit explicit); additional structured closed-form tests
including empty, complete, bipartite, disjoint cliques. Measure verified
completion, wrong counts, unverified results, paired visits, wall time.
Primary: learned >= incumbent verified completions, zero incorrect counts,
no extra unverified results, >=15% fewer visits on paired verified holdout
and beats both fixed alternatives on same intersection; separately report
training compute and n>=24 transfer. No gain if threshold fails. This is
learning a small control policy within a supplied feature space and solver,
not inventing new mathematical operators, neural training, or proof of
Omega-wide autonomy. No API, no main change, no automatic activation.
