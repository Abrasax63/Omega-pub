# ATOMIC-SFT-PILOT-01 — verified outcome, 24 November 2026
Workflow https://github.com/Abrasax63/Omega-pub/actions/runs/45384124691
all four jobs completed successfully. Source commit 09dd7154fc5509645a29e0be435fc49dcc63751f.
Training: 256 updates, 460800 trainable adapter parameters, L2 delta
6.931451327871569, 42610 token exposures, 1280 supervised target tokens.
Evaluation: 64 distinct unseen graphs (32 each sizes 5 and 6), 2 views,
2 models, 256 generations. Original archive artifacts:
- weights 14914893686
- labels 14914763444
- predictions 14915463293
- score 14916330825
Independent local Python audit of downloaded original ZIPs checked SHA256
against GitHub metadata, eval label digest against freeze manifest,
recomputed all 64 truth labels by edge membership and graph identities
by lexicographic adjacency over all permutations, checked 64 distinct
graph keys and all 256 prediction records. No missing IDs per arm/view.
Predictions SHA256 72acc9f7d9ceb0210c28554597a4559e58ed274a61779cd2a931fe3486ce9d5c.
Labels SHA256 489a32cf84079164faf6461ac284526d01e2425b92cb6af64dcb80d65af942ec.
Per view, base valid/reading/decision/consistent/joint = 0/0/0/0/0.
LoRA = 64/32/32/64/32. All 128 LoRA generations are literally 1101.
Paired joint both 0, base only 0, LoRA only 32, neither 32 each view.
Macro motif joint 1/8, positive joint 32/32, negative 0/32. Same 32
graphs correct in both views, explained entirely by constant response.
Output tokens per view base 1024 vs LoRA 320. CPU inference seconds
base edges 76.136, matrix 74.607; LoRA edges 40.525, matrix 39.347.
Verdict NO_PREREGISTERED_GAIN: strict formatting learned in this task,
no demonstrated graph-dependent reasoning or transfer. Constant shortcut.
Do not promote adapter or use it as an autonomous teacher. Preserve as
negative reference and format-adaptation checkpoint. Original holdout
now consumed and cannot be used as independent evidence. No main changes.
