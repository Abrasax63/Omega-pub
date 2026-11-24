# COMPOSITION01 — results from CI
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45402569813
Artifact 14924271795; ZIP SHA256 866102f8fefaa169fc2a099ea01cfbe64b96eb39ab8f8f82cb69dc66d30d2671.
Nine training runs. All three recreated STRUCTURE01 checkpoints match
original weight file hashes. Frozen: joint 3072/3072, retention 1536/1536,
all eight motifs correct, member delta zero. Fine-tune seeds 11 and 22:
joint 768/1024 each, retention 256/512 each, all positive-path motifs
110 and 111 wrong. Seed33 both perfect. Scratch each joint 768/1024,
retention diagnostic 256/512. Totals finetune 2560/3072, 1024/1536;
scratch 2304/3072, 768/1536. Preregistered composition+retention only
passes all seeds for frozen. Evidence from CI logs, not independent
artifact audit yet. The modular decomposition is supplied by humans.
Retention by freezing is expected; not proof of shared-weight
continual learning. Next: stress the original weights without updates.
