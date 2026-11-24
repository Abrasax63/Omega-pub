# CAPACITY-01 — prospective model / representation feasibility screen
After two constant-collapse SFT experiments, pause further 135M SFT.
Evaluate fixed SmolLM2-135M-Instruct (ee72e5415c002e8fc0566a191a07c0b2b708875a)
and SmolLM2-360M-Instruct (resolve and freeze full revision of a10cc15 before
first inference, verify resolved config commit), same CPU stack, no gradients.
Reference: https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/commits/main.
Different checkpoints differ beyond parameter count; no causal size claim.
New independent diagnostic 16 paired graphs (8 size5,8 size6); use
membership_curriculum pair invariants, distinct canonical graphs, fresh
seed, no reuse of prior evaluation packets. Two input views:
full list of directed edges (same membership prompt) vs adjacency list
showing all nodes and their outgoing neighbors, with no oracle answer,
no query-specific filtering, same query and exact Yes/No instruction.
32 questions x 2 views x 2 checkpoints = 128 generations, max8 tokens,
greedy, no tools, no answer in prompt, record full prompts and traces.
Exact Yes/No and anchored prefix separately; all invalid wrong.
Compare strict >=24/32 correct, >=10/16 both endpoints, >=10/16 per class
for each checkpoint/view. Also report exact lookup reference 32/32,
16/16 pairs (non-neural, not a learning claim). Conditional probability
contrast if both Yes/No token roundtrips pass. No training; no promotion;
one exploratory sample. A successful arm motivates a new independent
training study; failure motivates a different model family or learning
objective, not automatic repeated tuning. Never change main or use paid APIs.
Implementation/run separate. Fix scoring integration preflight before launch.
