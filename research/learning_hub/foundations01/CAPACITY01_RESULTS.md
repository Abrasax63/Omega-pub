# CAPACITY01 — verified negative result
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45391097316, all jobs
green, 65 offline tests. Frozen model revisions 135M ee72e5415c002e8fc0566a191a07c0b2b708875a,
360M a10cc1512eabd3dde888204e902eca88bddb4951.
Independent local audit of original ZIPs 14919695469,14919965079,14918432942:
archive digests match metadata, both prediction JSONL digests match score,
32 labels recomputed via edge membership, all 128 predictions present,
raw/prompt hashes match. Strict correct/pairs: 135M edges 14/32,2/16;
135M adjacency 16/32,0/16; 360M both views 16/32,0/16.
360M all 64 responses Yes; 135M adjacency all Yes.
Inference seconds (includes first-token diagnostic) 135M edges 22.00,
adjacency 18.29; 360M edges 40.29, adjacency 35.45.
No arm met preregistered threshold. NO_FEASIBILITY_SIGNAL. No size-only
causal conclusion, no proof these models cannot learn, no autonomous
learning, no promotion. Holdout consumed.
