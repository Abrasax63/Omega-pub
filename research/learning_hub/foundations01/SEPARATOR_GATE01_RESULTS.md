# SEPARATOR-GATE01 — bounded discovery works, root veto is too restrictive

Preregistration 974f1a8173aa5a561475fa49b3b86a7a87167d4d.
Implementation 545135393282085d55874cc51293be3f2f1f909b.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45477976033.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 new synthetic graphs, 20 structured and 12 random controls.
27 independent references (20 transfer DP, 5 branch, 2 complement
cliques), 5 reference limits. Three shuffled repetitions.
All arms 27 verified, no count discrepancies. 304 exhaustive
solver checks and positive-root, negative-dense, probe-cap,
fail-closed tests passed. Same nominal CPU and visit caps.

| Arm | Verified | Unverified | Unresolved | All reward | Verified reward | Structured reward | Control verified reward |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct |27|3|2|6.240838|1.240403|.655239|.585164|
| Shared partition |27|3|2|5.894843|1.069980|.536425|.533555|
| Unrestricted factor |27|2|3|6.283803|.944248|.234729|.709519|
| Root only |27|3|2|6.200044|1.185130|.601404|.583726|
| Bounded |27|3|2|6.187525|1.172063|.585353|.586711|

Reward = wall+.25*CPU+1 if unresolved, summed median per case.
Primary FAIL: bounded verified reward -5.51% vs direct but +9.54%
vs partition and +24.13% vs unrestricted factor. Secondary FAIL:
structured gain retention -16.22%; control verified cost about
9.96% above partition. No new verified completions.

First repetition: bounded 120 searches / 553 component probes
vs unrestricted 3542 / 24493 (96.61% / 97.74% reductions);
bounded 100 accepted separators, 368/1101 factor cache hits.
Bounded 16/20 structured positive roots, 0/12 controls positive.
All four family-4 structured roots missed; unrestricted also has
negative root evidence there yet can find separators deeper.
This is a structural detection cross-tab, not a classifier ground
truth. On the n=72 family-4 case unrestricted .078153 reward vs
bounded .414740 and shared partition .340300: root veto excludes
a valuable downstream opportunity. The 16-search cap and prefilter
are confounded with root veto in bounded arm, so isolate them next.
Unrestricted factor costs 56.24% less than partition on structured
subset but 32.98% more on verified controls. Bounded retains exact
coverage but loses the structural advantage. Fixed retrospective
oracle reward .728506 verified vs best fixed unrestricted .944248
(22.85% headroom), all 4.707990 vs partition 5.894843 (20.13%).
Oracle is not deployable; these are cohort-specific upper bounds on
choice among tested runs, not learning evidence.

Next discriminant: replace permanent root veto with a small shared
exploration budget for deeper residuals; isolate search cap, root
veto, and BFS candidate filter in matched ablations; use fresh
structured and negative controls. In particular preserve possibility
of detecting structure that emerges during reduction. No neural
training, main change, paid API, activation or archive deletion.
