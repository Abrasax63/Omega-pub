# COST-SELECT01 — prospective profitability selection with hard validity
Problem: INVARIANT-SELECT01 exact but R90 cone at N=15,h=6 slower than direct.
Do not learn validity: invariant_select01.choose remains mandatory.
Study only Rule90 profitability; other three typed tasks retain existing
selection, no extrapolated speed claims. Compare valid direct and cone.
Calibration: N in {9,11,13,15}, h=0..6, valid cone cases only.
Holdout: N in {8,10,12,14}, h=0..6 (including wrapped cases).
No shared (N,h). Timing 5 paired repeats per method with deterministic
randomized execution order, median wall-clock including solve and outcome
construction. Exact histograms must match; independent literal circular
list evolution on each holdout domain verifies histogram. Measure full
solve cost, not only representative count. Fixed model fit on calibration
only: ordinary least squares of log(cone/direct) on [1, N-(2h+3),
log(h+1)]; no hyperparameter tuning. Select cone iff predicted ratio<1,
otherwise direct; wrapped cases hard direct, equality width=N hard direct.
Baselines: direct always, valid cone whenever admissible (inc equality),
simple fixed rule cone iff slack>=2, posthoc per-case fastest median
lower reference (not deployable). Freeze model coefficients before
holdout timing. On holdout compare sum of selected measured medians,
regret vs posthoc oracle, number within 10% of fastest, errors/invalid
selection, per-case times. Actually execute learned-selected solve and
verify against independent reference, log measured time separately.
Primary: all results exact, no invalid method, learned aggregate
estimated cost <=1.15*oracle AND <= direct and always-cone aggregate.
If fixed rule matches/beats learned cost within 5%, prefer simplicity
(not evidence of useful learning). Timings one machine, noise and
small task grid, no generalization to other families/CPU. Report all
results incl failures, do not tune on holdout. No paid API or main change.
