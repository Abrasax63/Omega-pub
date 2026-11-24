# STRUCTURE01 — local execution, 2026-11-24
Prospective protocol commit 4b06b2a7274bb4876d5e7b63607488ebd9f82cd6.
Local Python 3.13.5, torch 2.10.0+cpu, 2 threads. Source SHA256
a70bd6e538c81a6133e431cf116788e5f6f6fefd6ef3d4dd744a8bd3da9ca383.
Original local result JSON SHA256 488b7b10a8497303b2f62f4eeaac36cd3536919fff4ad853a6b172a01f641fc6.
Six real training runs, 13057 parameters each, 256 optimizer steps each,
4096 generated training examples per seed, twice exposed. Seeds 11,22,33.
Same synthetic test sets across seeds; counts aggregated across predictions
are not independent graph counts. Test sizes are generated node sets, not
necessarily all nodes appear in the input edge list. Vocabulary bounded to 12.
Per-run exact correct / complete pairs, each normal set 256/128, each stress 128/64:
| seed | arm | n8 | n12 | sparse | dense | delta L2 |
|---|---|---|---|---|---|---|
|11|control|132/4|130/2|75/11|65/1|7.7302|
|11|conditioned|256/128|256/128|128/64|128/64|12.4720|
|22|control|137/9|130/2|92/28|64/0|8.4250|
|22|conditioned|256/128|256/128|128/64|128/64|12.0257|
|33|control|135/7|131/3|82/18|66/2|8.1689|
|33|conditioned|256/128|256/128|128/64|128/64|12.4038|
Normal OOD aggregate control 795/1536 (27/768 pairs), conditioned 1536/1536 (768/768 pairs).
Stress aggregate control 444/768, conditioned 768/768.
PREREGISTERED_PASS true for conditioned. This supports a local causal
effect of query conditioning within the matched small architecture,
not superiority over LLMs at equal data budget. No exact lookup feature
is given to either network; exact answers are generated only for training
and scoring. The architecture itself has a task-aligned inductive bias.
No proof of generalization beyond 12 labels, natural language extraction,
compositional reasoning, autonomy or AGI; no promotion. The original
weights and detailed results are local artifacts, not yet uploaded here.
Independent CI replication planned before further composition study.
