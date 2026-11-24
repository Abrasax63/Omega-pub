# EQUIV-REAL01 — negative semantic result; cumulative preparation only

Real pilot https://github.com/Abrasax63/Omega-pub/actions/runs/45487222362
all jobs successful; score 138790455020. 192 actual LoRA updates
per arm, 576 total, fixed base revision and seed. Each arm processed
235992 input / 248712 padded tokens; identical exposure digest
93545651464f033f6d60416493150d6195ec0186607e7a49695fe7c6384208f3.
Supervised target tokens 768 ordinary/contrast, 5040 process.
Adapter delta L2 2.8572344 / 2.8555829 / 4.4137079; elapsed train
681.26 / 772.91 / 974.66 s. No main change or paid API.

| Arm | Edges strict / binary | Matrix strict / binary | Edge-view pairs both | Matrix-view pairs both |
|---|---:|---:|---:|---:|
| base |0/32 of 64|0/32 of 64|0/32|0/32|
| ordinary |32/32 of 64|32/32 of 64|0/32|0/32|
| contrast |31/31 of 64|32/32 of 64|0/32|0/32|
| process |33/33 of 64|32/32 of 64|1/32|0/32|

All trained raw outputs valid Yes/No (192/192 each); matrix outputs
all Yes. Strict gains mostly formatting, binary accuracy 64,64,63,65
out of 128. Retention strict edge/syntax base 0/32,8/32; all trained
16/32,16/32; binary 16/32 in each domain for every arm, zero complete
pairs. Retention gates pass formally but floor effects preclude
claiming retention of a demonstrated competence. All primary gates
fail. No adapter eligible for promotion or proven cumulative learning.
No causal attribution to data, size, architecture or duration alone.
Auxiliary trace reconstruction not evaluated directly in REAL01;
process loss decrease cannot establish trace generalization.

Downloaded all eleven original ZIPs, SHA256 checked against artifact
metadata, stored in user Library /Omega/EQUIV-REAL01. Independent
offline replay in ChatGPT container: verified frozen input file hashes,
64 equivalence labels by exhaustive extension enumeration, all 768
prediction counts/class and pair metrics match official JSON, all
three adapter file digests and exposure metadata verified. This is
reanalysis of the same run, not independent training replication.
Retention labels not independently reconstructed in this replay.
Artifact IDs 14964418282,14964915900,14964900842,14964384423,
14963394944,14965102724,14965831946,14965069696,14967206626,
14966531617,14965653557. No private evaluation labels committed.

CUMULATIVE01 conditional prereg 460da12a82442cf6d9bd008ec363e8e867aefe9f;
implementation fb645dfec74678352cd2902bf3c61e012a720640;
freeze CI https://github.com/Abrasax63/Omega-pub/actions/runs/45491463740
success job 138790618924. 96 train, 16 dev, 64 new witness test,
64 equivalence retention examples; 120 graph pairs. Exact singleton
and extension checks, paired shortcut controls, graph isomorphism
dedup, separate artifacts. Synthetic, not independently secret.
Hashes train f0529567538959e472e238d4627bab39c237bf9e4c2fda0e21157ee71bb086bb,
dev abfaf9d01dc4b7dc09b7566c0aec3e9fdf3fe10f8f96793ce3acd24d9a12ba3b,
questions 87e0f2e623d6e13a7be83a30db071d788baa4b42eefe86815ac3163e95f8a988,
labels c48f7249d3947d3fef4b452a88b8106f4d2a2cf7d0be59c25eb561963a9296a1.
No inference or training. Context limits on larger graphs remain
to verify. No claim this new curriculum has produced competence.

Decision NO-GO for consolidating any REAL01 adapter as learned.
Next discriminant: measure blocked-singleton membership, two-mask
reconstruction and equality given explicit masks separately, with
fresh diagnostic data and exact oracle, before deciding whether
more training or architecture change is appropriate. Do not
consume CUMULATIVE01 reserved questions in diagnosis. No further
weight updates without separate approval.
