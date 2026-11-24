# ARCH-COOP01 — cooperative interleaving with exact shared state
Freeze before implementation. Two resumable workers on the same graph:
A max-degree branching (no dispatch); B fixed local structural/elimination
dispatch (4,8,512 from ARCH-LOCAL01), with its own visit counter for
the delay. Same mathematical recurrence, component and isolated rules,
native elimination width 3. Both use the same graph-local residual mask
key; cache entries are exact completed counts only, tagged by producer.
Suspend after each recursion visit; scheduler gives 32 visits per turn
to alternating workers starting A. B dispatch is synchronous within a
visit, not preempted except CPU timeout. First exact root answer cancels
both; no parallel CPU threads. Compare shared cache vs separate caches
with identical scheduler; include same resumable A-only and B-only
controls and existing synchronous delay512. Shared/global cap 4096
visits total, CPU .5 s per task, no doubled budget; max 4096 memo entries
total, naturally <= visits. Measure cross-worker hits, completed
cross-worker-produced entries used, cancellations, total CPU and visits.
Three shuffled repetitions per graph, median capped CPU cost with .5
failure penalty. 32 fresh graphs, 8 families at n=18,32,48,72 from
ARCH-SWITCH01 generator seed 20270115. Reference from same independent
reference suite. Distinguish unknown references; zero wrong verified
counts; check agreement of completed arms. Primary: shared >= separate
and B-only verified completions, >=15% lower verified capped cost than
separate AND best of A/B/delay, no extra unverified outputs relative to
separate, at least one cross-hit on a verified completed task. Also
report all-case costs and matched completed cases, peak memo entries,
cross hits on unresolved tasks separately. No learning or autonomous
reorganization claim; this is fixed cooperative scheduling. Same
author/generator, no blind external replication. CPU timing coarse.
No main change, API cost, or activation; if primary fails, no promotion.
