# ARCH-LOCAL01 — learn local dispatch policy with end-to-end feedback
Freeze before code. Exact recursion, memo, structural and elimination
engines unchanged from ARCH-SWITCH01/ARCH-GATE01, width 3, 4096 visits,
0.5 CPU-second cap. New policy uses residual size m, edge count and
cumulative visits. For structural action, only probe when the already
necessary condition for tree or multipartite is satisfied (edge count
m-1 or degree sum >= .7*m*(m-1)), and m >= learned minimum size.
For elimination, retain original sparse condition and width probe,
require m >= learned minimum size and visits >= learned delay.
Candidate grid: structural minimum m in {4,10}, elimination minimum
m in {4,8,12}, delay in {0,512}, 12 policies. Root and residual
decisions same; branch fallback and parent resume unchanged.
Train on 24 graphs n=18,32,64, eight original families, seed 20270111;
one randomized repetition per candidate (288 solves); objective total
capped CPU cost, tie lexical tuple. Full training cost and choices
recorded, independent correctness audit. No holdout feedback.
Test on 40 fresh graphs n=16,24,40,56,72 seed 20270112, same generator.
Compare learned policy to always, global delay512, fixed branch,
root-only, and fixed local policy (4,8,512), using three shuffled
repetitions and median capped CPU cost (failure .5 seconds).
Independent reference from previous engine; unverified separate.
Primary: >= as many verified completions as delay512, <= its
unverified count OR additional independently verified completions,
>=15% lower verified capped cost vs delay512 and fixed local,
and <=1.5x branch on jointly verified completed cases. Zero
discrepancies, at least one verified residual transition. Report
all-case costs, matched cases, probe and transition counts, chosen
policy, exact per-family results. No promotion if fails. Training
via finite policy search with local structural features, not neural
or counterfactual cost learning; no separate concurrent engines,
no autonomous solver invention. Same author/generator, no external
blind, CPU quantization caveat. No main change or paid API.
