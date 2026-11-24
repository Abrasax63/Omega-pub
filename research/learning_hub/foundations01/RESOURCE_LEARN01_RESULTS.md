# RESOURCE-LEARN01 — resource selection learned, transfer gate fails

Preregistration df8f8aca22bf8bb247029f6f77ba481569e38a3b.
Implementation 7758b24dd23406fb0c76c771d9709d38ff6e956b.
Successful train and independent evaluation CI:
https://github.com/Abrasax63/Omega-pub/actions/runs/45473059030.
Results inspected in CI logs; no independent artifact replay.

24 training graphs, 288 runs, frozen stump based on maximum degree:
<=22: condition four vertices, use two worker processes (pool4);
>22: condition two vertices, serial (serial2).
Global training winner: condition two vertices, two workers (pool2).
Training loss 2.594192 stump vs 3.011476 global (13.86% lower).
Training collection 15.2493 wall seconds, 16.8820 aggregate CPU
including references and all benchmark runs, not just learning.
Both jobs report 4 logical CPUs, 2 visible core IDs; quota unknown.

32 fresh test graphs; 24 independent references including one
additional complement-clique enumeration result; 8 reference limits.
No incorrect completed counts detected. Three repeats per action.
Identical aggregate solver allowance .8 CPU s and 8192 visits, divided
equally among frontier tasks; unused allowances not reassigned.
Reject outputs above measured total CPU 1s; not a hard OS global cap.
Warm pool startup recorded separately, .045s on evaluation; actual
policy deployment overhead not independently replayed.

| Strategy | Verified | Unverified | Unresolved | Wall s | CPU s | Loss all | Loss verified subset |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct |24|6|2|1.848443|1.842391|4.309180|0.260114|
| Partition 2 serial |23|6|3|1.247295|1.239857|4.557479|1.189241|
| Partition 2, 2 workers (global) |23|6|3|0.895395|1.266765|4.212624|1.193787|
| Partition 4, 2 workers |22|4|6|0.289316|0.450524|6.401983|2.124428|
| Learned stump |23|4|5|0.354014|0.500657|5.479059|1.201382|
| Retrospective per-case oracle |24|6|2|0.519604|0.626002|2.676108|0.254218|

Loss = wall + .25*CPU + 1s per unresolved, summed per-case medians;
not elapsed runtime. Lower is better. Stump selects partition4 on 21
cases, serial2 on 11. Relative to best verified fixed direct, it loses
one verified completion, verified loss +361.87%; +0.64% vs learned
global, all-case loss +30.06% vs global. Primary FAIL.
On 22 jointly verified completed cases stump wall .020620s vs direct
.010404s; CPU .024256 vs .007372. Apparent overall lower wall/CPU is
confounded by failures and unused per-task budget. Oracle is only a
retrospective diagnostic: verified loss improvement over direct ~2.27%,
although all-case loss has headroom; cannot deploy oracle.
No general learning gain, no autonomous resource management certified.

Next falsifiable change: budget redistribution with direct fallback
or bounded probing under a shared aggregate ledger. Test whether
partition loses because one hard residual exhausts its equal share
while easy tasks return unused allowance. Keep fixed direct as strong
control; compare static equal shares, size-weighted shares, and
reallocation on fresh tasks. Do not increase budget or retune holdout.
No main change, paid API, deletion, or activation.
