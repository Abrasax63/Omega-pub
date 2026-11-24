# MEMORY-DAG01 — dependency and recovery stress, safety pass / utility fail

Preregistration 43c035fcabb917c2198b3340a84270c0aa4efb11.
Implementation ed56dffd6dba3f03305c145aa0161d091b0a837a.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45455554784.
Verified CI logs; archive JSON copied from DAG_ARCHIVE log and committed
as MEMORY_DAG01_ARCHIVE.json. No independent replay of downloaded artifact.
Archive digest b019f1f42fc9769347b73f0fece2684840bfd01f6e689282b73ea7707079feb6; journal head 22da8736f34032be996b4f6084ac398a656546cb9511381d506bc18d8bb9c01a.
11 definitions (6 mined flat macros, 5 developer-supplied nested stress
fixtures), 42 evidence records (32 reproduced original exact solutions,
5 positive and 5 negative fixture witnesses). All replayed. Removing
SM as a root preserved it as a dependency of N5. Quarantining SM blocked
SM, N1, N4, N5; rollback to a contaminated manifest rejected.
Eight fault injections rejected: missing dependency, cycle, invalid
primitive, changed evidence, archive tamper, stale head, invalid manifest,
quarantine bypass. Both simulated missing/corrupt live files restored
byte-identically from read-only temporary copy. Safety gate PASS in
sandbox. This is not an independent-provider backup or an adversarial
permission boundary; trusted digests are held by same test process.

| Method | Rare solved/cost | Control solved/cost | Total cost |
|---|---:|---:|---:|
| Primitive |12/2368|12/1895|4263|
| Active only |12/1556|12/2727|4283|
| Dormant lookup + active fallback |12/136|12/3243|3379|

All 24/24 exact. Retrieval cut rare cost by 91.26% vs active,
total cost 21.11% vs active, 20.74% vs primitives. Controls cost
18.92% more than active, exceeding predeclared 10% cap; utility FAIL.
Rare targets are deliberately exact matches of archived definitions
on new primes; this demonstrates retrieval not invention. Control
lookups add overhead; no broad generalization or activation.
The lookup returns the dormant program without persisting a new
active manifest. Quarantine and lookup tests are separate scenarios.
Next test: indexed retrieval with independently measured total cost
including index construction, incremental maintenance and false matches;
then actual research archive audit in read-only mode, external backup
with distinct credentials and restore drill before deployment.
No existing library deletion, main change or paid API.
