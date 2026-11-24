# ARCH-LOCAL01 — local adaptation useful on verified subset, no learned advantage

Preregistration b6d97c7729e1b36002eb896d5abb0f0a8b00d962.
Implementation c5a7728aac1394f1d64f0f03348cb304ff6cb358.
Successful separate train/evaluate jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45468954345.
Verified CI logs, not independent replay of downloaded artifacts.

24 training graphs, 12 local policies, 288 runs, summed capped
training CPU cost 16.786887859 s. Winner (4,8,512), identical to the
preregistered fixed local control: structural minimum 4 vertices,
elimination minimum 8 vertices, cumulative delay 512 visits.
Structural probe eligibility requires the existing necessary tree
or multipartite edge-count condition. No new solver.

40 fresh graphs up to n=72; 31 independent references (8 bitset,
12 conditioned leaf DP, 7 branching, 4 multipartite formula);
nine reference limits. Three repetitions per distinct policy;
identical policies share measured runs. No referenced count mismatch.

| Policy | Verified | Unverified | Unresolved | Verified capped CPU s | All capped CPU s |
|---|---:|---:|---:|---:|---:|
| Always |31|7|2|0.149061113|2.030031677|
| Delay512 |31|7|2|0.122970677|1.989092822|
| Branch |30|4|6|0.521000000|3.044999251|
| Root only |30|4|6|0.528147907|3.053147634|
| Fixed local = learned |31|6|3|0.102992609|2.173700228|

Primary gate FAIL. Local policy preserves every verified completion
of delay512, reduces verified capped cost 16.25% vs delay512, but
0% vs fixed local and increases all-case cost about 9.28% vs delay512.
One fewer unverified completion, one more unresolved. On 30 jointly
verified completed cases local .03399864s, delay .046971554s,
branch .021s (local 1.62x branch; required <=1.5x).
25 verified cases with successful residual dispatch. First repetition
across all graphs: 4521 switches; 1401 structural probes vs 9697 for
delay512, 5801 elimination probes vs 7075; 10197 local feature
computations; 1405395 factor lookups vs 1608200. Different work units
not interchangeable. Coarse CPU timer; one training repeat per
candidate; same generator/author, not externally blind. No general
speedup, no benefit attributable to training over fixed local control.

Do not tune a new grid against this holdout. Next: freeze this result;
test a structurally different shared-state approach, using bounded
concurrent proposals or a lazy race with a common memo and explicit
cancellation budget, compared to delay512 and fixed local on fresh
problems. This is a proposal, not an executed experiment.
No main change, paid API, neural training or promotion.
