# COMPOSE-LEARN01 — reusable program fragments from synthesis experience
Freeze protocol before implementation. Domain: permutation programs on
Z_p, p odd prime. Five supplied primitives: R(x)=x+1, L(x)=x-1,
M(x)=2x, D(x)=x/2, S swaps 0 and 1. Same immutable composition engine.
Input is entire target finite permutation table, not teacher expression.
No claim of extrapolating unseen input labels. Learn reusable macros:
solve 32 training targets on p=11,13 with primitive-only bidirectional
search, then mine contiguous length 2/3 fragments of recovered programs,
rank by occurrence across distinct solved tasks (tie length then lexical),
keep up to 6, require support >=2; no target generating code passed to
miner. Exclude adjacent inverses, identities and duplicate transformations
on both training primes, including primitive equivalents. Persist macros,
training traces and source hash, reload in separate evaluation job.
Generator: training 16 per prime, 8 repeated-motif compositions
(motif set RSM, SLD, MRS; concatenate 2-3 motifs with random primitive
prefix/suffix), 8 random reduced words length 6..9. Seed 20261228.
Holdout 48 targets, 12 motif and 12 random per p=17,19, seed 20261229;
deduplicate target tables per p, exclude identity. Same author,
synthetic repeated structure favorable to macro mining, not external blind.
All arms use identical exact bidirectional search (smaller frontier,
deterministic order), budget 12000 candidate compositions per task;
each table composition counted once regardless of macro length,
charge precomputing macros (sum lengths) per task; inverse table
construction not counted separately, record runtime descriptively.
Compare primitive-only, learned macros, random static macros (same
length multiset, seeded 20261230, same exclusions). Strong bidirectional
baseline, not naive expression enumeration. Only per-task search
cache, no cross-task precomputed search table, explicit limitation.
Verify each returned expanded primitive program directly on all p
states, separate evaluator; no guess on exhaustion. Record completion,
candidate cost including cap penalty 12001, runtime, expanded primitive
length, macro usage; separate motif and random controls. Primary:
learned >= both comparators on completion, zero invalid programs,
>=15% lower total capped composition cost vs BOTH, no >10% cost
regression on random subgroup vs primitives. Report gain vs primitive
alone even if gate fails. This tests persistent reuse of composed
operators, not new primitive discovery, neural training, general
intelligence or runtime integration. No main change, no paid API.
