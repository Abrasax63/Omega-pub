# MEMBERSHIP-SFT01 — negative scientific result, recovered offline
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45387623052.
Freeze/train/infer succeeded. Score failed as anticipated, FileNotFoundError
for stale atomic-predictions.jsonl basename; no regeneration or retraining.
Independent offline recomputation from original ZIPs:
predictions artifact 14916843512, SHA256 archive 36ed8b437d71b440988ed98c100403038d5715619e95e00c33f748ec4c7ceb15,
JSONL d147dfa4c93070de6ae4597f9b87fce1d8a9eba79caeb4fa87dcc0233bc70284;
labels artifact 14917161505, SHA256 archive 91ed3a33fb74d65fee008b351a147c2127b0d21c733b38b81d6b952cb16550b5,
eval SHA256 ba4c154b6bcd571194bf72d4e33c416c42cbac8c5466059383553eea079d9e52 matches freeze.
Weights artifact 14917062672, ZIP SHA256 8762fbde902877df6d95d0006fad93cda0995bdfdef1ab6dcdf06b901e162a94;
all manifest adapter hashes match. 256 updates, 460800 trainable parameters,
L2 change 5.023493830244882, 30452 token exposures, 512 supervised tokens,
141.557 s. Mean online epoch loss .414947 -> .452448.
64 exact labels checked by direct edge membership, 32 pairs, 256 distinct
arm/view/id records, full coverage. Results strict valid/correct/both-pairs:
base edges 55/26/2; base matrix 64/33/1;
LoRA edges 64/32/0; LoRA matrix 64/32/0.
LoRA all 128 answers exactly No. Strict yes/no correct: base edges 21/5,
base matrix 20/13, both LoRA views 0/32. Prefix correct: 30/33/32/32;
prefix pairs 2/1/0/0. Binary argmax correct 30/33/32/32.
Mean conditional P(Yes) change when edge added: -.00451323 (base edges),
-.00004704 (base matrix), -.00419806 (LoRA edges), -.00013895 (LoRA matrix).
Positive contrasts out of 32: 20/14/20/13. All primary thresholds fail.
Status NO_PREREGISTERED_GAIN; two LoRA experiments now show constant
response collapse. No causal attribution to size, data quantity or
optimizer. No retention or autonomous skill acquisition demonstrated.
Archive both adapters as negative references, not teaching checkpoints.
Holdout consumed. Do not repeat SFT with same recipe absent a discriminant.
