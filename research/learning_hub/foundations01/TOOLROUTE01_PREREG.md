# TOOLROUTE01 — prospective end-to-end bounded tool selection
Goal: learn a router from short task descriptions, execute exact existing
contracts, independently verify outputs. No LLM, no new neural weight
training. All inputs have identical structured payload fields (vector,
rows, samples); router receives text only. Adapters supplied by developer.
Five classes: projection, closure audit, periodic inverse, composition
(project onto supplied zero-sum kernel then periodic inverse), unsupported
(abstain). Compare multinomial Naive Bayes with Laplace smoothing (alpha=1,
uniform priors, lowercase Unicode word tokens), a predeclared keyword
baseline (count matching distinct keywords; abstain on tie), and oracle
route. Training 8 distinct text templates/class; holdout 8 other templates
per class, including negation/conflicting keyword and missing-observation
requests. French descriptions; template-level split, no holdout tuning.
For each holdout template generate 3 exact rational payloads, common schema,
fresh deterministic seed 20261124. 120 tasks, 24/class. Report both route
and execution accuracy (strict route plus verified result), unsupported
false dispatch, wrong-route outcomes, composition success. Reference
projection via independent rank-one formula; cycle via reverse cumulative
construction, closure via all-pairs witness check; composition applies
independent projection then inverse. Verify closure witness IDs and
status, not arbitrary witness ordering. Model and baseline same payload
and adapters; oracle not deployable. Primary learned >=90% total exact,
>=90% composition and zero unsupported dispatch; compare keyword, no
promotion unless learned beats simple by >=5 percentage points and
primary passes. Exact oracle 120/120 required or harness invalid.
Small curated text test not natural language generality or autonomous
skill discovery. No paid API/main modification. Record all failures.
