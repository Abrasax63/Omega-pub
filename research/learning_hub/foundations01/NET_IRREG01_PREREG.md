# NET-IRREG01 — irregular signed Boolean constraint stress
Freeze before code. 48 fresh random signed 2-CNF instances (n=12,16,20,
32,64,128; eight each, four planted satisfiable, four unplanted; edge
density m/n=0.8,1.2,2,4 for each half). Additional six irregular
positive-OR random graphs n=32,64,128, edge probabilities .15,.35;
no complete-clique or bipartite construction. Seed 20261210.
Each clause forbids exactly one pair; duplicates prohibited; random
polarity independently sampled subject to planting when applicable.
All policies receive identical clauses; target count and count with
x0=1; never provide planted assignment. Use existing exact unary/parity
preprocessing and component decomposition with guarded clique shortcut.
Compare incumbent maximum degree + bounded memo, same without memo,
and new balanced-polarity branching (prefer variables occurring with
both signs, then degree) + memo. Every policy gets same 4096 visits per
count, cache max 4096 entries / 250000 clauses, no guessed counts.
Use fallback after existing min-fill refusal for deployment-style
comparison; additionally force branch counting on all cases to
isolate branching/caching with identical reduced inputs.
Independent reference for n<=20: exhaustive truth-table bitset;
larger: uncompressed min-fill with original cap, if unavailable
independent bounded branching over original clauses, with own 4096
visit cap, direct clause evaluation, no memo or component shortcuts.
If independent reference unavailable, mark unverified even when
policies agree. Report exact verified counts, unresolved and unverified
separately. Compare both count queries. No false forced bits, no
regression on independently verified instances. Promote new branch
order only if verified completion >= incumbent, no more incorrect
or unverified outputs, and >=20% fewer total branch visits on the
intersection of verified completed cases; cache retained only if
measured hits reduce visits, accounting for overhead. Report timings
as descriptive single-run measurements, not universal speedups.
No main changes, no paid API, no claim of neural or autonomous learning.
