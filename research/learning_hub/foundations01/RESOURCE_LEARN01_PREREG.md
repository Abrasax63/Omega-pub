# RESOURCE-LEARN01 — learned resource choice and granularity under matched budgets
Freeze before implementation. Four actions: direct exact local solver,
partition k=2 serial, partition k=2 pool2, partition k=4 pool2.
Use PARALLEL01 frontier identity (top k degree, aggregate identical
residuals), ARCH-LOCAL01 policy fixed (4,8,512). Every action receives
aggregate solver CPU allowance .8s and 8192 visits. For partition,
divide equally by unique tasks (floor visits); unused allowance not
redistributed. Count parent/worker task CPU and reject outputs when
measured per-case total >1s, not a strict OS aggregate CPU quota;
process startup/shutdown recorded separately. Same direct .8s/8192.
One persistent 2-worker pool per dataset run, warm before timed cases,
charge startup separately. If fewer than 2 affinity CPUs, report
and do not claim physical speedup. Three shuffled repetitions per
action per case, identical action runs shared across policies.
Reward per run: wall + .25*CPU + 1s if unresolved; median over repeats.
Learn global best action, and a depth-one decision stump over
n, edge density, mean degree, max degree (thresholds midpoints of
observed distinct values, min 4 cases per child); choose by summed
training median reward, tie deterministic. No label/family/ref
in features or reward. Charge feature extraction at deployment;
fixed comparison policies do not need features. 24 train graphs
n=24,40,64 and 32 fresh test graphs n=20,36,56,72, all eight
families, seeds 20270124/25. Use existing independent references,
plus independent complement-clique enumeration with 500000 call
cap if original reference unavailable (count cliques by enumerating
in increasing order, counting each prefix, no memo), cross-check
when both available. No holdout feedback; persist source hashes and
stump. Primary: learned stump >= verified completions of best
fixed policy (best defined by verified-subset reward retrospectively),
no additional unverified outputs unless more verified completions;
>=15% lower verified-subset summed median reward than best fixed
AND learned global, all-case reward <= learned global; zero
count discrepancy. Report matched completed-case wall, CPU,
coverage and regret vs retrospective per-case oracle. Training
cost recorded. No neural or general autonomy claim. Same synthetic
generator, one machine per job; no guarantee hardware identical
between jobs; report visible topology, quota if accessible.
No main change, paid API, promotion or deletion.
