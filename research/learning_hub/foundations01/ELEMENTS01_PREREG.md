# ELEMENTS-01 — prospective bottleneck localization
Do not train again until identifying which elementary operation is weak.
Frozen pinned SmolLM2-135M-Instruct, no adapter, no oracle/tool access
during generation. Separate diagnostic, not the old or new training holdout.
Membership: 16 fresh paired 4-node directed graphs, seeded 20261128.
For each pair fix names/order, queried ordered distinct edge, other
adjacency bits; toggle only queried edge, giving 16 absent and 16 present.
Use edge list, prompt asks whether specified ordered edge exists.
Logic: all eight Boolean triples once, prompt supplies x-y, y-z, x-z
presence bits and asks whether this triple violates transitivity.
No graph reading required; no worked example, no truth table or formula
provided. This is a diagnostic of the term and local logical combination,
not pure formal logic competence; one positive, seven negative.
Compare free greedy generation (max 8 tokens, strict ASCII 0/1, invalid
counted wrong) with grammar-only greedy single-token binary choice,
same prompt and same base weights. Grammar supplies output alphabet,
never answer. Record probabilities/mass of allowed digits under raw logits,
token IDs, raw text, prompt digest, model revision and wall time.
Primary membership metric: 32 correct, per-class counts, paired both-correct
out of 16; exploratory signal >=24/32 and >=10/16 pairs. Constant baseline
16/32 and 0/16 pairs, uniform independent binary choices expect 16 and 4.
Logic report all 8 predictions, per-class exactness, balanced accuracy.
Signal >=6/8 including positive and >=5/7 negatives. Constant negative
gets 7/8 but fails signal. No statistical independence claim for logic
truth table. If membership weak, prioritize edge reading; if membership
passes but logic weak, prioritize local implication; if both pass under
constraint but free fails, investigate output-interface adaptation rather
than increasing reasoning training. Even both pass does not establish
composition or autonomous learning. No holdout reused, no gradients,
no paid API, no promotion, no main changes, no retry.
