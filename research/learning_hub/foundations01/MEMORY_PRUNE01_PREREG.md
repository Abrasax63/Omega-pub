# MEMORY-PRUNE01 — reversible active library selection, no destruction
Freeze protocol before implementation. Reuse unchanged compose_learn01
search, training generator and macro miner. Train six macros from the
same 32 synthesis tasks. Persist all learned definitions, expanded
primitive words and original exact solutions in an immutable
content-hashed archive. Active library is a versioned manifest of
archive IDs, not a separate copy or destructive deletion. Append-only
hash-chained manifest journal; verify archive integrity, complete
definition dependencies (all current macros are flat primitive words),
original solution replay and journal chain on load. Rollback appends
a new manifest matching an earlier revision; never rewrites history.
This detects corruption relative to a trusted digest; not protection
against malicious rewriting of all hashes or storage loss.
Calibration: 24 fresh targets, p=13,17, six motif and six random
per p, seed 20261231. Greedy backward removal from full active set,
evaluate all one-removal alternatives on same calibration; accept
strictly lower total capped composition cost with no regression
in calibration completion, tie lexicographic. Stop at local minimum.
Also evaluate empty as strong baseline but do not use holdout to
choose. Archive remains identical. Replay all 32 stored solution
words after every revision, independent of active macro set; verify
full rollback then restore selected manifest. No physical deletion.
Adversarial tests: altered macro definition, missing referenced ID,
tampered historical journal, duplicate active ID, altered stored
solution, wrong predecessor hash, rollback to unknown revision.
Require all rejected and rollback restores identical active IDs and
search results (word/cost, not timing) on calibration.
Holdout: 48 fresh targets on p=23,29 (12 motif,12 random per p),
seed 20270101; disjoint tables within p. Compare full library,
selected active set, primitive-only, random subset of archived
macros of same size (seed 20270102). Same 12000 composition cap
and direct evaluation of each output; charge macro setup as before.
Primary safety: all original results replay, archive digest identical,
all corruptions rejected, deterministic rollback. Utility gate:
selected >= full and primitive completion, >=15% lower capped cost
vs full, <= primitive total cost, no random subgroup regression >10%
vs primitive. Empty selected set is legitimate but not evidence of
new learned competence; random subset may equal selected. Report
calibration search overhead separately, no holdout tuning. One run,
synthetic tasks, not external blind. No deletion, main change, paid API,
runtime integration or assertion of general autonomous memory.
