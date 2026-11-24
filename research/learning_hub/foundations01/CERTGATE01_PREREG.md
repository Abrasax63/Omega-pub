# CERTGATE01 — prospective finite-domain validation gate
Isolate validation from neural extraction: exact six-bit signatures only.
Use EXTENSION01 grammar (cost <=5 and <=7), fresh 48 target masks
(12 IN, EXT, FAR, NEAR each), seed 20261206, exclude all 48 prior
EXTENSION01 targets; sample by same recipe, fail closed on overlap.
For each task run active adaptive query selection once up to 64 distinct
motifs: cost5 then cost7 on empty, replay all evidence; after both
grammars empty continue collecting labels in seeded order. Preserve
old policy at prefix16 (singleton and >=4 subsequent consistent checks)
as baseline; report prefixes 16,32,64 of new gate, same evidence.
New gate reports separate statuses: model hypothesis (singleton,
explicit grammar scope; no unconditional certification), ambiguous,
grammar refuted (no cost7 candidate), and finite truth-table certificate
ONLY when all 64 distinct motifs have consistent labels. Certificates
bind domain ID, canonical evidence and truth table by SHA256; verify
by independently rebuilding table and digest. Duplicate identical
evidence adds no coverage, contradictory labels, invalid inputs and
wrong scope fail closed. No certificate for graph extraction, external
oracle truthfulness, compact formula or arbitrary graph size.
Primary: zero false unconditional certificates, all 48 finite tables
exact at 64, zero unconditional certs at 16/32; report conditional
hypotheses actually right/wrong and grammar-refutation counts, query
cost, minimum counterexamples. Mutation tests: duplicate coverage,
missing motif, conflicting duplicate, invalid motif/label, wrong scope,
altered table/digest. Compare exact certificate cost vs old false
acceptances. No neural calls/updates, paid API, promotion or main change.
Fresh tests, no post-hoc threshold changes.
