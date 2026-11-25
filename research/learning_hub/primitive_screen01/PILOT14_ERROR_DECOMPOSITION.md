# PILOT14 — error decomposition and paired comparison, 25 November 2026
Source: run 45662119374, artifacts 15045861860 (base), 15045909969 (supervised), 15047277068 (contrastive), 15047856395 (adaptive), 15048321608 (results).
Local audit this intervention: actual ZIP SHA256 values match GitHub metadata, prediction file SHA256 matches each manifest, all 1024 prediction IDs unique within arm, complete coverage, and all prompt hashes match locally regenerated TRANSFER13 prompts and oracle. No adapter weights available to audit. Counts below are post-hoc diagnostics, not altered primary scores.
## Selection (64 each)
| Error / success | Base | Supervised | Contrastive | Adaptive |
|---|---:|---:|---:|---:|
| Correct | 4 | 1 | 18 | 20 |
| Wrong single word present in list | 13 | 5 | 32 | 33 |
| Entire list copied | 13 | 3 | 0 | 0 |
| Multiple input words, not whole list | 13 | 11 | 13 | 9 |
| Other | 21 | 44 | 1 | 2 |
## Reversal (64 each)
| Error / success | Base | Supervised | Contrastive | Adaptive |
|---|---:|---:|---:|---:|
| Correct | 15 | 0 | 25 | 23 |
| Original list copied | 23 | 7 | 17 | 20 |
| Other permutation of input | 10 | 0 | 17 | 8 |
| Missing/extra/repeated words or other | 16 | 57 | 5 | 13 |
Membership: stripping at most one trailing period yields 37/30/44/47 correct respectively, so improvement survives this secondary format adjustment. Copy 44/17/62/63 strict.
## Paired transitions
Unit = a pair of related questions, success iff both answers correct. On 128 pairs, adaptive vs base: 36 newly successful, 3 lost. Contrastive vs base: 37 gained, 7 lost. Adaptive vs contrastive: 13 gained, 10 lost. Exploratory exact two-sided sign/McNemar binomial p values on discordant pairs: 3.61e-8, 5.30e-6, 0.678 respectively. These assume independent pair-level observations, do not model training seed variation or correct multiple comparisons, and are descriptive/exploratory only. Adaptive selection follows frozen pair-count rule, not demonstrated superiority.
## Implications
Selection is largely wrong-position retrieval, reversal often identity-copy or wrong permutation. Do not treat these as merely formatting failures. A prospective discriminant after CUMULATIVE18: balanced positional swaps (selection) and identity-vs-reversed foil (reversal), preserving vocabulary and budgets; compare against generic contrastive control and evaluate fresh paired sets. No new training launched; no release or promotion. Independent curator and second seed remain outstanding.