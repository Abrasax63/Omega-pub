# COMPOSE-LEARN01 — compositional acquisition, negative efficiency result

Preregistration: 31e0ef6181df8092f27ada6ba8f9b9a041d177a9.
Implementation: 335c1792a47d9c5227df52f335cc5cbc12ef06b1.
Successful separate train and evaluation jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45452791074.
Results verified from CI logs, not independently replayed artifacts.

Training: 32/32 targets on p=11,13 solved using primitive-only search,
24461 candidate compositions. Automatically mined six macros:
SM (19 distinct tasks), RS (16), MR (14), MS (14), SR (14), RSM (13).
Random control macros: LD, SD, SM, MR, LM, DSL. Same length multiset.
Checkpoint loaded and source hash checked in evaluation job.

48 held-out full permutation tables on p=17,19, 24 motif-generated
and 24 random-word targets. Every returned program directly evaluated
on all input states, zero mismatches. All three arms solve 48/48.

| Arm | Motif cost | Random cost | Total cost | Macro uses | Expanded primitive length |
|---|---:|---:|---:|---:|---:|
| Primitive only |21930|10500|32430|0|305|
| Learned macros |23738|23251|46989|88|319|
| Random macros |25425|11631|37056|102|331|

Learned increases total candidate composition cost by 44.89% versus
primitive-only and 26.81% versus random macros. Random subgroup cost
increases 121.44% versus primitives; motif subgroup +8.24%.
Primary gate FAIL. Descriptive total CPU times: 0.05137s primitive,
0.07206s learned, 0.05599s random. Single run, short measurements.
Macros shorten some token sequences but increase branching factor;
this is a plausible explanation, not an isolated causal ablation.
The mined compositions are reused across larger prime domains but
no efficiency or completion benefit is demonstrated. Do not promote.

Scope: full target tables supplied; no inference of unknown outputs,
new primitive discovery, neural training, or general intelligence.
Synthetic shared motifs are favorable to mining; no external blind
holdout. Only per-task caching. No main change, no paid API.
Next discriminating test: cost-aware macro selection or context-gated
activation, matched branching budgets, including a strong primitive
baseline and a random macro baseline. Measure oracle headroom before
training. Avoid accumulating macros merely because frequently used.
