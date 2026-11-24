# PROPOSAL-01 — actual result, 24 November 2026
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45381176801, success
technically. Artifact https://github.com/Abrasax63/Omega-pub/actions/runs/45381176801/artifacts/14913971815.
Source commit 8bbca688c551d653505095dbed2f7e46f40a7d22.
32 real SmolLM2-135M-Instruct calls, 2304 input tokens, 5388 output tokens,
153.613 s summed inference. 26/32 reached 192-token cap.
0/32 strict JSON, 0 admitted, no graph/motif diversity measured.
Rejections: 27 expecting value, 4 extra data, 1 unterminated string.
Independent local reanalysis of original ZIP: all 32 raw/prompt hashes,
seeds, token counts, raw file digest, parse errors and reported rejection
counts match. Scanning every opening brace with JSONDecoder.raw_decode
found complete JSON objects in 7 of 32 outputs, but zero objects with
exactly the required nodes/edges/triple keys. This relaxed diagnostic
does not change the preregistered score. ZIP SHA256:
7486ec450fe1c2e2cc7dfa049a55447205f1e4eabb3856cc126ffb56872c2cac
raw.jsonl SHA256:
bc93c1fe72c42617ccf9107c1ef950a0f98fef23a72b15e873f9a2711763a41b
Verdict PROPOSAL_FEASIBILITY_NOT_DEMONSTRATED. Cannot distinguish mathematical
generation skill from failure to communicate under this contract; simple
JSON extraction cannot recover any exact-schema object. Zero gradients,
zero admitted training examples, no holdout consumed. Do not train on these
outputs or count a replay as independent. No automatic promotion.
Next diagnostic: compact representation with and without grammar-only
constraints. The grammar supplies syntax, not graph edges, queried triple
or correctness labels. Report intrinsic and scaffolded abilities separately.
