# PORTFOLIO-HEADROOM01 — structural baseline wins; insufficient selector headroom

Preregistration ec84aa8e807e7fbf62da522eb19cc2708dd494dd.
Implementation a48b4d7ae98af43f655b512c5b7ded64a1e42783.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45451839705.
Results verified from CI logs, not independent artifact replay.

48 new labeled graphs, eight families, n=12..64; four engines, three
repetitions, 576 timed solves. 0.5 CPU-second cap, existing internal
visit/scope caps retained. Independent reference available on 40 graphs
(24 bitset, 6 leaf DP, 7 branching, 3 multipartite formula); 8 reference
limits. No observed disagreements on completed results.

| Engine | Verified | Unverified | Unresolved | Verified capped CPU s | All capped CPU s |
|---|---:|---:|---:|---:|---:|
| Elimination |34|2|12|4.045110441|7.136097597|
| Existing hybrid |38|2|8|2.592821676|5.682818896|
| Graph branching |39|0|9|0.615393569|4.615393569|
| Structural + graph branching |39|0|9|0.572003471|4.572003471|
| Retrospective oracle (verified subset only) |39|—|—|0.565719748|—|

Best fixed structural engine reduces verified-subset capped cost by
77.94% relative to existing hybrid and 7.05% relative to graph branching.
Oracle reduces it by only 1.10% relative to best fixed (78.18% vs hybrid).
All engines fail on one independently referenced dense random n=64
case under their respective caps. On two unreferenced cases hybrid
can return a count while graph/structural do not; no certification.
Primary gate FAIL: headroom <15%. Do not train a selector on this
portfolio. Three repetitions give similar capped totals but CPU timer
resolution is coarse: some very fast solves measured zero seconds;
no literal zero-cost interpretation and no precise micro-timing claims.
Dominant 0.5 s penalty for the one verified unsolved case further
compresses potential headroom; descriptive outcome, not universal.
No claim of causality on speed outside this cohort, or deployment.
Structural shortcut is programmed, not learned. Domain only positive
pair OR / independent-set counting, not all algebraic/logical problems.
Next decisive test should use genuinely different problem domains and
a stronger exact algorithm for the common hard case (e.g. separator
decomposition or graph reductions), but avoid training unless prospective
headroom is demonstrated. No main change, API calls or neural training.
