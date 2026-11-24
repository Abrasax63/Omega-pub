# RESOURCE-POOL01 — reusable budget without restarting residual computations
Freeze before implementation. Same exact local solver as RESOURCE-LEARN01
(4,8,512), made resumable by yielding after each recursive visit,
retaining stack and memo. Same global 8192 visit cap and .8 process CPU
seconds for every arm (single process, includes task construction and
scheduler; reject overrun; no strict OS aggregate quota). Four fixed
conditioning vertices; identical deduplicated frontier and weights
in partition arms; no shared internal memo across leaves.
Compare direct resumable, direct original (same caps), static equal
visit shares, static size-weighted shares proportional to residual
size+1 (largest remainder allocation, deterministic), pooled dynamic
round-robin 64-visit slices, and sequential pooled (one leaf at a
time, largest residual first). Static shares apply to visits only;
CPU globally shared in all arms, not independent per-leaf timers.
Pooled visits may be spent on any unfinished leaf; no restart. Charge
all work, record unused static allocations, unfinished leaf states,
resumptions, visit totals, CPU, wall, no partial root answer.
32 new graphs n=20,36,56,72, eight previous families seed 20270127.
Three randomized repetitions. Independent stronger_reference from
RESOURCE-LEARN01. Reward wall+.25*CPU+1 if unresolved (median).
Primary: round robin >= equal and weighted verified completions,
at least one verified recovery where both static arms fail, >=15%
lower verified reward than best static AND no greater all-case reward;
no added unverified outputs unless more verified completions.
Report comparison to direct, sequential pooled and per-case oracle,
jointly verified matched costs. To claim scheduling benefit beyond
pooled budget alone, round robin must beat sequential pooled by 15%
on verified reward with no coverage loss; separate secondary gate.
Controls: exhaustive frontier identity n<=4 via PARALLEL01 tests,
resumable exact counts against brute-force for all n<=4 graphs;
suspension at quantum1 vs64 identical exact result and visit count
on deterministic test; budget exhausted rejects partial results.
Same generator/author, no external blind. No neural training,
parallel execution, automatic promotion, main change, paid API.
