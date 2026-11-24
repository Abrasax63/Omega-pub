# EQUIV-PILOT01 amendment — process supervision and dry-run only
Frozen before dry-run implementation. Add fourth arm D: supervised
blocked-future masks as auxiliary task. A frozen base, B ordinary
binary CE, C same CE + .5 pairwise softplus margin, D same CE + .5
auxiliary mask-token CE. All train arms use identical pairs, views
(edges train, matrix held-out view), paired order, base and adapter
recipe, 192 updates, identical forward token inputs including auxiliary
teacher-forced inputs; B/C auxiliary loss masked to zero. D receives
additional supervised target information intentionally; equal compute
exposure is not equal supervision. Separate mask prompt, no mask
provided at binary evaluation; no answer or trace in binary prompt.
Auxiliary target is two binary strings in supplied future order
separated by slash; verify every bit by testing whether adding the
singleton preserves independence, cross-check blocked oracle. Use
teacher-forced Yes/No plus EOS for binary CE; contrast is logit Yes-No
at first answer position. Normalize CE per supervised token.
No real model training or weight changes here. Dry-run with tiny
random tensors/fixture model only, check masks, causal alignment,
contrast gradient direction, identical tokens and zero auxiliary
gradient for B/C, finite losses, EOS, artifact hashes and no labels
in eval inputs. Freeze fresh retention controls: 16 paired directed
edge tasks and 16 paired Python syntax tasks (64 questions total),
balanced, shuffled, deterministic seed 20270162, oracle edge set
membership and ast.parse; syntax only, not executable programming
skill. Retention score on frozen base and adapters, <=5 percentage
point drop per domain, report floor effects. No claims of retention
until real evaluation. Original primary thresholds unchanged for
C/D vs base, D vs B measured separately, paired success >=20/32
and >=24/32 per class per view; use exact raw Yes/No, binary argmax
diagnostic not substitute. Compare C vs B and D vs B; no post-hoc
choice on holdout. Fresh independent holdout and three seeds before
promotion. No automatic training workflow, no paid API, main
changes or promotion. After dry-run review request explicit GO
for actual weight updates.
