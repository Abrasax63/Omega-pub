# ARCH-GATE01 — learn when to switch using feedback
Freeze before implementation. Reuse ARCH-SWITCH01 structural/elimination,
reference and exact recursion unchanged except dispatch predicate. A gated
policy starts in combinatorial mode; at cumulative recursion visits >=
threshold, allows same residual dispatch as dynamic. Return to parent
recursion after exact subproblem; no restart or state loss. Thresholds
0 (always),32,128,512,4097 (never). Native caps 4096 visits, width 3,
0.5 CPU seconds, same across arms. No new solver. Learn threshold from
observed capped CPU cost, not target answers. Train 32 fresh graphs
n=12,24,40,64, eight families as ARCH-SWITCH01, seed 20270107.
For each threshold run two repetitions randomized order, loss mean
capped CPU seconds including probes, failure penalty .5. Select
global threshold minimizing aggregate training loss. Also learn two
thresholds for density <.25 or >=.25, minimizing group loss; fixed
tie favors larger threshold. Record choices, costs, source hashes.
Separate evaluation job: 32 fresh graphs n=18,32,48,64, seed
20270108. Three repetitions shuffled per graph; compare all five
fixed thresholds, root-only, learned global, learned density gate.
No holdout feedback; independent reference from previous engine,
assert no count mismatches, unreferenced outputs separate.
Measure verified completions, unresolved, total median capped cost,
paired completed-case median cost vs branch and always, number of
switches and probe counts; report each fixed threshold retrospectively
(not deployable oracle). Primary: density gate >= always verified
completions, no extra unverified outputs, >=15% lower verified capped
cost than always AND learned global, <=1.5x fixed branch cost on
jointly verified completed cases, >=1 successful residual dispatch
on verified case. Secondary: preserve always-only verified cases;
report whether global policy alone meets cost/completion conditions.
No claim if gate fails; no learning of new solver or unbounded
architecture. Training cost separate. CPU timing coarse, same author
and generator, no external blind. No main change, paid API or promotion.
