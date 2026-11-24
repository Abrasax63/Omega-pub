# TOOLROUTE01 — negative end-to-end benchmark
Protocol e32db8bb976cb65e08d89bab039c836a8437d870; implementation
ba8796d3d669b98c9494dd1c6795ee84381b67de.
CI run https://github.com/Abrasax63/Omega-pub/actions/runs/45430676314
completed successfully, scientific primary failed. Artifact 14938098679
downloaded; ZIP SHA256 verified locally:
f67c290a8d2acb8fc53a2e8cf6aaf3f8c2e00a53a71912538c100e721d276adc.
Locally recomputed exact counts and confusion pairs from 360 records
(not an independent re-verification of every mathematical output).
40 training and 40 disjoint holdout text templates; 3 payloads per
holdout template, so 120 tasks but only 40 distinct routing decisions
per arm. Developer-supplied common data envelope, adapters, labels
and composition recipe; no LLM or neural weight training.
Learned NB 63/120 (52.5%), keyword 69/120 (57.5%), oracle 120/120.
Learned class scores projection 12/24, closure 15/24, inverse 18/24,
compose 12/24, unsupported 6/24. Keyword 15,18,12,9,15 respectively.
Learned false dispatch 18/24 unsupported; keyword 9/24.
12/24 composition requests misrouted to inversion only.
Negation failure: "Sans correction du vecteur, tenter seulement la
primitive des écarts" -> compose, should inverse.
Scope failure: "Calculer la primitive analytique de sin x sur la droite
réelle" -> inverse, should abstain.
Unsupported general theorem requests also misrouted.
No promotion of either selector. All 120 oracle outputs independently
verified in CI, showing execution works when route supplied, not
autonomous semantic selection. The unsupported class is scored by
intended abstention; shared synthetic payloads are not authentic data
for unsupported tasks. This is a bounded curated benchmark, not
evidence about general language comprehension.
Next: separate proposal and typed semantic validation, represent
required outputs, forbidden operations, domain and composition order;
test on fresh independently authored templates and out-of-scope tasks.
Compare with existing simple baseline, avoid training on this holdout
then reusing it as evidence. Do not add more instruments until
selection safety and composition improve. No main change, no paid API,
no runtime activation.
