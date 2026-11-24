# REORG01 — reversible direct probe and partition on one exact ledger
Freeze before implementation. Same local specialist policy (4,8,512),
global original graph masks, same exact recurrence and fixed four-vertex
frontier from RESOURCE-POOL01. Resumable workers preserve stacks and
exact completed memo. One global visit ledger 8192 and process CPU cap
.8s, all construction/selection included, no multicore. Delay based
on worker-local visits as before. Direct baseline; partition-only
round robin 64 visits per leaf; hybrid fixed: direct 256 visits then
if unfinished try partition for <=1024 additional visits, resume
direct if partition incomplete. Shared memo keyed by original mask
with producer tag; cache hits across workers and duplicate completions
checked; partial results never published. Fixed private-cache hybrid
same schedule as ablation. Adaptive hybrid: at 256 visits switch only
if memo hit fraction <.25 and current residual size >=8; otherwise
continue direct; if switched, same bounded 1024 visit partition trial
then resume direct. This is hand-coded progress gating, not learning.
No restart of direct. Suspended leaf states discarded on fallback,
their exact results retained in shared arm, abandoned visits charged.
Compare direct native also (same nominal caps, descriptive; generator
uses original masks instead of induced relabeling). 32 fresh graphs
n=20,36,56,72 eight prior families seed 20270129. Three randomized
repetitions; independent stronger_reference. Objective reward =
wall + .25*CPU + 1 if unresolved, sum per-case medians.
Primary adaptive hybrid >= verified completions of direct and
partition, >=15% lower verified reward than both, <= their best
all-case reward, no extra unverified outputs unless additional
verified coverage, at least one actual switch on verified task.
Secondary shared fixed vs private fixed: >=15% lower verified reward
without verified completion loss; cross-producer hits required.
Report direct fallback counts, partition successes, exact retained
memo hits, duplicate work, all cost, matched cases, retrospective
oracle. Selftests exhaustive n<=4 all resumable arms, forced switch
and fallback on deterministic graph with small probe/trial, same
answer as brute force; cap exhaustion no partial output; shared vs
private identical exact answer. No main change, paid API, promotion,
new neural training. Same author/generator, no external blind.
