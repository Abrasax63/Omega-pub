# SEPARATOR-EXPLORE01 — late structural discovery, controlled ablations
Freeze before implementation. Reuse SEPARATOR-GATE01 exact engine.
Arms: direct, shared partition, unrestricted factor, bounded (prior
root veto + 16 searches/128 probes + BFS balance filter), open16
(same bounded without veto), open128 (same open16 but 128 searches/
1024 probes), open128_raw (same open128 without balance prefilter,
candidate order by estimated BFS balance). All root search attempts
and deeper searches occur on eligible connected residuals >=16;
no family labels at solver. Charge all search work; global caps
8192 visits/.8 process CPU s; three shuffled repetitions. 32 fresh
graphs same eight families n=24,40,56,72 seed 20270139, references
as before. Primary predesignated open128: >= verified coverage of
direct, partition, unrestricted factor; >=15% lower verified reward
than best direct/partition and all-case reward <= both; no extra
unverified unless higher verified coverage. Secondary: open16
vs bounded isolates veto, open128 vs open16 isolates budget,
open128_raw vs open128 isolates prefilter. Report verified reward,
all reward, coverage, searches, probes, late discoveries after
negative root, structured/control subgroup and fixed oracle headroom.
Secondary exploration success requires >=1 verified completed case
with negative root and later separator, >=15% verified reward
reduction vs bounded, no verified loss. Exhaustive n<=4, dense
negative root, probe caps, exact late discovery fixture using
constructed connected graph with universal apex over chain of
cliques (apex initially prevents separator, deleting it exposes
chain; verify exact using chain transfer +1), cap failure.
No retuning, no family oracle in solver, no learned selector,
same synthetic generator, no external replication, no main change,
paid API, promotion or archive deletion.
